#!/usr/bin/env python3
"""
Split du questionnaire [P1#1] SUITE ALTEA AMADEUS en 6 sous-questionnaires
distincts, conformement a la decision de la reunion DRM du 22/04/2026.

Decoupage :
  [P1#1] Alteoa Reservation         <- garde Section A + transverses Q15-17
  [P1#2] Alteoa Ticketing           <- recoit Section B
  [P1#3] Alteoa Inventory           <- recoit Section C
  [P1#4] Alteoa DCS                 <- recoit Section D
  [P1#5] Alteoa RMS                 <- nouveau (noyau metier DRM)
  [P1#6] Amadeus Data Feeds         <- nouveau + Q18 deplacee

Les questionnaires existants AIMS/AMOS/RAPID/SITATEX/ACARS sont decales
de P1#2-6 vers P1#7-11 (priority_in_phase += 5). Leurs questionnaires
techniques associes sont decales aussi.

Le questionnaire [P1#1] technique (id=158) est renomme pour refleter le split.

LOCAL UNIQUEMENT — ne pas executer sur la base de prod sans validation.

Usage :
  source venv/bin/activate
  DATABASE_URL="sqlite:///$(pwd)/db.sqlite3" python3 split_altea_suite.py            # dry-run
  DATABASE_URL="sqlite:///$(pwd)/db.sqlite3" python3 split_altea_suite.py --execute  # appliquer
"""
import os
import sys
import json
import datetime
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
BASE = os.path.dirname(os.path.abspath(__file__))
if 'DATABASE_URL' not in os.environ:
    os.environ['DATABASE_URL'] = f"sqlite:///{os.path.join(BASE, 'db.sqlite3')}"
django.setup()

from django.db import transaction
from cartography.models import Questionnaire, QuestionSection, Question

DRY_RUN = '--execute' not in sys.argv

# ---------------------------------------------------------------------------
# Constantes du split
# ---------------------------------------------------------------------------
SOURCE_QR_ID = 1                  # [P1#1] SUITE ALTEA AMADEUS
SOURCE_TECH_QR_ID = 158           # [P1#1] Questions Techniques — SUITE ALTEA AMADEUS

# Decalage : tous les questionnaires Phase 1 avec priority_in_phase 2..6
# vont passer a 7..11 pour faire de la place aux 5 nouveaux modules Altea.
PRIORITY_SHIFT = {2: 7, 3: 8, 4: 9, 5: 10, 6: 11}

# Metadonnees communes aux 6 modules issus du split
COMMON_META = {
    'editor': 'Amadeus',
    'direction': 'DC – DIVEX / DOS / DRM',
    'responsible': 'BERRABIA Mokrane (DOS) / FAIDI Fouad (DRM)',
    'key_users': 'FAIDI Fouad (DRM), FIALA Zahra (DOS), LOUNAOUCI Nassim (DOS), '
                 'HASBELLAOUI Imen (DOS), GHARBI Mohamed (DOS), NAMOUNI Ali (DOS)',
    'key_users_backup': 'SAFARZITOUN Naim (DRM), TACHTIOUI Omar (DOS), OUNISSI Akli (DOS), '
                        'BELAMINE Ryad (DOS), TOUAHRIA Faiza (DOS), RAHAL Djalal (DOS), '
                        'DAHMANI Koceila (DOS)',
}

# Nouvelles questions pour les 2 modules creesx ex nihilo
RMS_QUESTIONS = [
    ('Q1', 'Quel systeme de Revenue Management est utilise (Alteoa RMS, autre) ? '
           "Comment est-il integre a Alteoa Inventory et a quels modules tiers ?"),
    ('Q2', "Quelles regles de nesting et politiques de classes sont appliquees ? "
           "Qui valide ces parametrages et selon quelle frequence ?"),
    ('Q3', "Comment sont calcules les bid prices ? Sur quels parametres "
           "(saisonnalite, demande historique, evenements, concurrence) ?"),
    ('Q4', "Quels KPI de Revenue Management sont suivis (yield, RASK, load factor, "
           "spill/spoilage) ? A quelle frequence et par qui ?"),
    ('Q5', "Quels sont les irritants operationnels actuels du RMS et les besoins "
           "d'evolution prioritaires (donnees manquantes, latence, perimetre) ?"),
]

FEEDS_QUESTIONS_NEW = [
    ('Q1', "Quels feeds Amadeus sont actuellement actifs (PNR feed, APS, ticket, payment) ? "
           "Avec quelle frequence (quotidien J+1, intraday, temps reel) ?"),
    ('Q2', "Sous quel format les feeds sont-ils livres (EDIFACT TPF, XML, JSON, CSV) ? "
           "Quelle est la profondeur historique fournie a chaque livraison ?"),
    ('Q3', "Comment les feeds sont-ils receptionnes (SFTP push, SFTP pull, API REST) ? "
           "Sur quelle infrastructure (serveur dedie, plateforme partagee) ?"),
    ('Q4', "Le contrat Amadeus actuel inclut-il l'acces a ces feeds, ou un "
           "Change Proposal payant est-il requis ? Pour quels feeds ?"),
    ('Q5', "Quelles donnees personnelles transitent dans les feeds (passagers, "
           "paiements, contacts) ? Quelle politique d'anonymisation ou de "
           "minimisation est appliquee au regard de la loi 18-07 ?"),
    ('Q6', "Quel est le volume quotidien estime (PNR, coupons, transactions) ? "
           "Quelle duree de retention est appliquee ?"),
    ('Q7', "Existe-t-il un plateforme de test Amadeus permettant la fourniture de "
           "donnees anonymisees pour la modelisation et la validation des flux ?"),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def header(title):
    print()
    print('=' * 70)
    print(title)
    print('=' * 70)


def section_by_letter(qr, letter):
    """Recupere la section dont le titre commence par '{letter} — '."""
    return QuestionSection.objects.filter(
        questionnaire=qr, title__startswith=f'{letter} —'
    ).first()


def snapshot_state():
    """Capture l'etat actuel des questionnaires Phase 1 dans un dict."""
    snapshot = []
    for qr in Questionnaire.objects.filter(phase=1).order_by('priority_in_phase', 'id'):
        snapshot.append({
            'id': qr.id,
            'system_name': qr.system_name,
            'phase': qr.phase,
            'priority_in_phase': qr.priority_in_phase,
            'status': qr.status,
            'sections': [
                {
                    'id': s.id,
                    'title': s.title,
                    'order': s.order,
                    'questions': [
                        {'id': q.id, 'number': q.number,
                         'has_answer': bool(q.answer)}
                        for q in s.questions.order_by('order')
                    ],
                }
                for s in qr.sections.order_by('order')
            ],
        })
    return snapshot


# ---------------------------------------------------------------------------
# Etapes
# ---------------------------------------------------------------------------
def shift_priorities():
    """Decale les questionnaires P1#2..6 vers P1#7..11."""
    print('  Decalage des priorites en Phase 1 :')
    # Decaler en ordre decroissant pour eviter collisions sur la contrainte
    # d'unicite (si jamais il y en avait une)
    for old in sorted(PRIORITY_SHIFT.keys(), reverse=True):
        new = PRIORITY_SHIFT[old]
        for qr in Questionnaire.objects.filter(phase=1, priority_in_phase=old):
            print(f"    [{qr.id}] P1#{old} -> P1#{new}  {qr.system_name}")
            if not DRY_RUN:
                qr.priority_in_phase = new
                qr.save(update_fields=['priority_in_phase'])


def rename_p1_1_into_reservation():
    """Renomme [P1#1] SUITE ALTEA AMADEUS -> Alteoa Reservation."""
    qr = Questionnaire.objects.get(id=SOURCE_QR_ID)
    print(f"  [{qr.id}] '{qr.system_name}' -> 'Altéa Réservation'")
    if not DRY_RUN:
        qr.system_name = 'Altéa Réservation'
        qr.save(update_fields=['system_name'])
    return qr


def rename_p1_1_technical():
    """Renomme [P1#1] technique pour refleter qu'il couvre tout le perimetre Altea."""
    try:
        qr = Questionnaire.objects.get(id=SOURCE_TECH_QR_ID)
    except Questionnaire.DoesNotExist:
        print('  Pas de questionnaire technique a renommer.')
        return None
    new_name = 'Questions Techniques — Altéa & Amadeus (transverse)'
    print(f"  [{qr.id}] '{qr.system_name}' -> '{new_name}'")
    if not DRY_RUN:
        qr.system_name = new_name
        qr.save(update_fields=['system_name'])
    return qr


def create_new_module(priority, name):
    """Cree un questionnaire vide pour un module Altea."""
    print(f"  Creation [P1#{priority}] {name}")
    if DRY_RUN:
        return None
    return Questionnaire.objects.create(
        system=None,
        system_name=name,
        phase=1,
        priority_in_phase=priority,
        editor=COMMON_META['editor'],
        direction=COMMON_META['direction'],
        responsible=COMMON_META['responsible'],
        key_users=COMMON_META['key_users'],
        key_users_backup=COMMON_META['key_users_backup'],
        status='NOT_STARTED',
    )


def reparent_section(section, new_qr, new_title=None, new_order=0):
    """Repointe une section vers un autre questionnaire (preserve questions et reponses)."""
    title = new_title or section.title
    print(f"    Re-parente Section [{section.id}] '{section.title}' -> [{new_qr.id if new_qr else '?'}] '{title}' (order={new_order})")
    if DRY_RUN:
        return
    section.questionnaire = new_qr
    section.title = title
    section.order = new_order
    section.save(update_fields=['questionnaire', 'title', 'order'])


def move_question(question, new_section):
    """Repointe une question vers une autre section."""
    print(f"    Q[{question.id}] {question.number} -> Section [{new_section.id if new_section else '?'}]")
    if DRY_RUN:
        return
    question.section = new_section
    question.save(update_fields=['section'])


def add_questions(section, qlist, start_order=1):
    """Ajoute une liste de (number, text) dans la section."""
    for i, (number, text) in enumerate(qlist):
        print(f"    + Q '{number}' : {text[:60]}...")
        if not DRY_RUN:
            Question.objects.create(
                section=section,
                number=number,
                text=text,
                order=start_order + i,
                answer='',
                is_answered=False,
                validation_status='PENDING',
            )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    mode = 'DRY-RUN (rien ne sera modifie)' if DRY_RUN else 'EXECUTION REELLE'
    header(f'SPLIT SUITE ALTEA AMADEUS  -  Mode : {mode}')

    # 1. Verifications prealables
    try:
        src = Questionnaire.objects.get(id=SOURCE_QR_ID)
    except Questionnaire.DoesNotExist:
        sys.exit(f'ERREUR : questionnaire id={SOURCE_QR_ID} introuvable')
    print(f"\nSource : [{src.id}] P{src.phase}#{src.priority_in_phase} {src.system_name}")
    sec_a = section_by_letter(src, 'A')
    sec_b = section_by_letter(src, 'B')
    sec_c = section_by_letter(src, 'C')
    sec_d = section_by_letter(src, 'D')
    sec_e = section_by_letter(src, 'E')
    if not all([sec_a, sec_b, sec_c, sec_d, sec_e]):
        sys.exit('ERREUR : sections A/B/C/D/E manquantes dans la source.')
    q18 = Question.objects.filter(section=sec_e, number='Q18').first()
    if not q18:
        sys.exit("ERREUR : Q18 introuvable dans la section E (sera deplacee vers Amadeus Data Feeds).")
    print(f'  Section A : {sec_a.title} ({sec_a.questions.count()} Q)')
    print(f'  Section B : {sec_b.title} ({sec_b.questions.count()} Q)')
    print(f'  Section C : {sec_c.title} ({sec_c.questions.count()} Q)')
    print(f'  Section D : {sec_d.title} ({sec_d.questions.count()} Q)')
    print(f'  Section E : {sec_e.title} ({sec_e.questions.count()} Q, dont Q18={q18.number})')

    # 2. Snapshot avant modification
    snapshot = snapshot_state()
    if not DRY_RUN:
        backup_path = os.path.join(
            BASE, f'backup_avant_split_altea_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)
        print(f'\n  Snapshot avant-split sauvegarde : {backup_path}')

    # 3. Operations
    try:
        with transaction.atomic():
            header('1. Decalage P1#2..6 -> P1#7..11')
            shift_priorities()

            header('2. Renommer [P1#1] -> Altéa Réservation')
            altea_reservation = rename_p1_1_into_reservation()

            header('3. Renommer [P1#1] technique')
            rename_p1_1_technical()

            header('4. Creation des 5 nouveaux questionnaires P1#2..6')
            altea_ticketing = create_new_module(2, 'Altéa Ticketing')
            altea_inventory = create_new_module(3, 'Altéa Inventory')
            altea_dcs = create_new_module(4, 'Altéa DCS')
            altea_rms = create_new_module(5, 'Altéa RMS')
            amadeus_feeds = create_new_module(6, 'Amadeus Data Feeds')

            header('5. Re-parentage des sections existantes')
            print('  Section A reste sur [P1#1] Altéa Réservation (re-ordre)')
            reparent_section(sec_a, altea_reservation, 'A — Module Réservation', new_order=0)

            print('  Section B -> [P1#2] Altéa Ticketing')
            reparent_section(sec_b, altea_ticketing, 'A — Module Ticketing', new_order=0)

            print('  Section C -> [P1#3] Altéa Inventory')
            reparent_section(sec_c, altea_inventory, 'A — Module Inventory', new_order=0)

            print('  Section D -> [P1#4] Altéa DCS')
            reparent_section(sec_d, altea_dcs, 'A — Module DCS (Departure Control System)', new_order=0)

            print('  Section E reste sur [P1#1] (renommee, sans Q18)')
            reparent_section(sec_e, altea_reservation, 'B — Processus transverses Altéa Réservation', new_order=1)

            header('6. Creation feeds Amadeus + deplacement Q18')
            if not DRY_RUN:
                feeds_section = QuestionSection.objects.create(
                    questionnaire=amadeus_feeds,
                    title='A — Feeds opérationnels Amadeus (PNR / APS / Ticket / Payment)',
                    order=0,
                )
                print(f"    Section creee [{feeds_section.id}] sur [P1#6]")
            else:
                feeds_section = None
                print('    (dry-run) Section A — Feeds operationnels Amadeus')
            move_question(q18, feeds_section)
            print('  Ajout des nouvelles questions sur Amadeus Data Feeds :')
            if feeds_section:
                add_questions(feeds_section, FEEDS_QUESTIONS_NEW, start_order=2)
            else:
                # dry-run : juste afficher
                for i, (n, t) in enumerate(FEEDS_QUESTIONS_NEW, start=2):
                    print(f"    + Q '{n}' : {t[:60]}...")

            header('7. Creation des questions RMS')
            if not DRY_RUN:
                rms_section = QuestionSection.objects.create(
                    questionnaire=altea_rms,
                    title='A — Revenue Management System (RMS)',
                    order=0,
                )
                print(f"    Section creee [{rms_section.id}] sur [P1#5]")
            else:
                rms_section = None
                print('    (dry-run) Section A — Revenue Management System (RMS)')
            if rms_section:
                add_questions(rms_section, RMS_QUESTIONS, start_order=1)
            else:
                for n, t in RMS_QUESTIONS:
                    print(f"    + Q '{n}' : {t[:60]}...")

            if DRY_RUN:
                # Annuler la transaction pour rester en read-only
                raise RuntimeError('__DRY_RUN_ROLLBACK__')

    except RuntimeError as e:
        if str(e) != '__DRY_RUN_ROLLBACK__':
            raise

    # 4. Resume
    header('RESUME')
    if DRY_RUN:
        print('  Mode dry-run — aucune modification appliquee.')
        print('  Pour appliquer reellement :')
        print(f'    python3 {sys.argv[0]} --execute')
    else:
        print('  Split applique.')
        print('  Verifiez sur /admin/ ou /kpi/ que la nouvelle structure est correcte.')
        print('  Backup JSON conserve dans le dossier du script.')


if __name__ == '__main__':
    main()
