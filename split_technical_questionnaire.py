#!/usr/bin/env python3
"""
Script pour éclater le questionnaire "Questions Techniques — Tous Systèmes" (id=40)
en un questionnaire technique par système, avec assignation des key users.

ATTENTION : Ce script ne doit PAS être exécuté sans validation préalable.
Il va créer ~39 nouveaux questionnaires + sections + questions + tokens key users.

Usage :
  1. Lancer en mode dry-run (par défaut) pour voir ce qui sera créé
  2. Lancer avec --execute pour appliquer les changements

  source venv/bin/activate
  DATABASE_URL="sqlite:///$(pwd)/db.sqlite3" python3 split_technical_questionnaire.py          # dry-run
  DATABASE_URL="sqlite:///$(pwd)/db.sqlite3" python3 split_technical_questionnaire.py --execute # appliquer
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
BASE = os.path.dirname(os.path.abspath(__file__))
if 'DATABASE_URL' not in os.environ:
    os.environ['DATABASE_URL'] = f"sqlite:///{os.path.join(BASE, 'db.sqlite3')}"
django.setup()

from cartography.models import (
    Questionnaire, QuestionSection, Question, KeyUserAccess, System
)

DRY_RUN = '--execute' not in sys.argv

MASTER_Q_ID = 40  # "Questions Techniques — Tous Systèmes"

# ────────────────────────────────────────────────────────────────────────
# Mapping : section du Q40 → questionnaire métier existant (pour key users)
# Clé = section_id dans Q40, Valeur = questionnaire_id du système correspondant
# ────────────────────────────────────────────────────────────────────────
SECTION_TO_QUESTIONNAIRE = {
    139: 1,   # SUITE ALTÉA → Q1
    140: 2,   # AIMS → Q2
    141: 3,   # AMOS → Q3
    142: 4,   # RAPID PASSAGERS → Q4
    143: 5,   # SITATEX ONLINE → Q5
    144: 6,   # ACARS / HERMES → Q6
    145: 7,   # SAGE STOCK → Q7
    146: 8,   # ATPCO → Q8
    147: 9,   # BAC (Amadeus) → Q9
    148: 10,  # Dashboards CCO → Q10
    149: 11,  # AGS → Q11
    150: 12,  # Q-PULSE → Q12
    151: 13,  # EUROCONTROL → Q13
    152: 14,  # JET PLANER → Q14
    153: 15,  # WORLD TRACER → Q15
    154: 16,  # SITE WEB → Q16
    155: 17,  # ACCELYA DISTRIBUTION → Q17
    156: 18,  # QLIK SENSE → Q18
    157: 19,  # POWER BI → Q19
    158: 20,  # AIMS Formation PNC/PNT + Conception → Q20
    159: 21,  # SAGE FINANCE → Q21
    160: 22,  # BSP LINK → Q22
    161: 23,  # E-DOLÉANCE → Q23
    162: 24,  # GLPI → Q24
    163: 25,  # HERMES CALL CENTER → Q25
    164: 26,  # OAG / INNOVATA → Q26
    165: 27,  # E-LEARNING E-EXAM PN → Q27
    166: 28,  # ZIMBRA → Q28
    167: 29,  # CONTRÔLE PROGRAMMES PN/AVIONS → Q29
    168: 30,  # DOA MAILING → Q30
    169: 31,  # CALL DOA → Q31
    170: 32,  # SKYBOOK → Q32
    171: 33,  # FLYSMART → Q33
    172: 34,  # PORTAIL AH → Q34
    173: 35,  # EVALCOM → Q35
    174: 36,  # BODET → Q36
    175: 37,  # DATAWINGS → Q37
    176: 38,  # AIMS Formation PNC → Q38
    177: 39,  # AIMS Formation PNT → Q39
    # Sections transverses (pas liées à un système spécifique)
    # 178: Infrastructure (40 questions) → sera ajouté à TOUS les questionnaires techniques
    # 179: Sécurité (41 questions) → sera ajouté à TOUS les questionnaires techniques
    # 180: Contrats éditeurs (42 questions) → sera ajouté à TOUS les questionnaires techniques
}

# Sections transverses à ajouter à chaque questionnaire technique
TRANSVERSE_SECTION_IDS = [178, 179, 180]


def get_section_system_name(section):
    """Extrait un nom propre depuis le titre de section (ex: '1.1 — SUITE ALTÉA (Amadeus)' → 'SUITE ALTÉA')"""
    title = section.title
    # Retirer le numéro de section (ex: "1.1 — ")
    if '—' in title:
        title = title.split('—', 1)[1].strip()
    return title


def main():
    mode = "DRY-RUN (rien ne sera modifié)" if DRY_RUN else "EXÉCUTION RÉELLE"
    print("=" * 70)
    print(f"SPLIT QUESTIONNAIRE TECHNIQUE → 1 PAR SYSTÈME")
    print(f"Mode : {mode}")
    print("=" * 70)

    master_q = Questionnaire.objects.get(id=MASTER_Q_ID)
    master_sections = QuestionSection.objects.filter(questionnaire=master_q).order_by('order')
    print(f"\nQuestionnaire source : [{master_q.id}] {master_q.system_name}")
    print(f"Sections : {master_sections.count()}")
    total_questions = Question.objects.filter(section__questionnaire=master_q).count()
    print(f"Questions totales : {total_questions}")

    # Charger les sections transverses
    transverse_sections = QuestionSection.objects.filter(id__in=TRANSVERSE_SECTION_IDS)
    transverse_questions = {}
    for ts in transverse_sections:
        transverse_questions[ts.id] = list(
            Question.objects.filter(section=ts).order_by('order').values(
                'number', 'text', 'order'
            )
        )
    print(f"\nSections transverses : {len(transverse_sections)}")
    for ts in transverse_sections:
        print(f"  - {ts.title} ({len(transverse_questions[ts.id])} questions)")

    created_questionnaires = 0
    created_sections = 0
    created_questions = 0
    created_tokens = 0

    print(f"\n{'─' * 70}")
    print(f"CRÉATION DES QUESTIONNAIRES TECHNIQUES PAR SYSTÈME")
    print(f"{'─' * 70}")

    for section in master_sections:
        if section.id not in SECTION_TO_QUESTIONNAIRE:
            if section.id in TRANSVERSE_SECTION_IDS:
                continue  # Sections transverses traitées séparément
            print(f"\n⚠️  Section [{section.id}] '{section.title}' — pas de mapping, ignorée")
            continue

        source_q_id = SECTION_TO_QUESTIONNAIRE[section.id]
        source_q = Questionnaire.objects.get(id=source_q_id)
        section_name = get_section_system_name(section)
        questions = list(Question.objects.filter(section=section).order_by('order'))

        new_name = f"Questions Techniques — {source_q.system_name}"
        print(f"\n{'─' * 50}")
        print(f"📋 {new_name}")
        print(f"   Source section : [{section.id}] {section.title}")
        print(f"   Système métier : [{source_q.id}] {source_q.system_name}")
        print(f"   Questions spécifiques : {len(questions)}")
        print(f"   Key User Principal : {source_q.key_users or '—'}")
        print(f"   Key User Backup : {source_q.key_users_backup or '—'}")
        print(f"   Direction : {source_q.direction}")
        print(f"   Phase : {source_q.phase}")

        if not DRY_RUN:
            # 1. Créer le questionnaire technique
            new_q = Questionnaire.objects.create(
                system=None,  # OneToOneField — le système est déjà lié au questionnaire métier
                system_name=new_name,
                phase=source_q.phase,
                priority_in_phase=source_q.priority_in_phase,
                editor=source_q.editor,
                direction=source_q.direction,
                key_users=source_q.key_users,
                key_users_backup=source_q.key_users_backup,
                responsible=source_q.responsible,
                status='NOT_STARTED',
            )
            created_questionnaires += 1

            # 2. Créer la section spécifique au système
            new_section = QuestionSection.objects.create(
                questionnaire=new_q,
                title=f"Questions Techniques — {section_name}",
                order=1,
            )
            created_sections += 1

            # 3. Copier les questions spécifiques
            for q in questions:
                Question.objects.create(
                    section=new_section,
                    number=q.number,
                    text=q.text,
                    order=q.order,
                    answer='',
                    is_answered=False,
                    validation_status='PENDING',
                )
                created_questions += 1

            # 4. Ajouter les sections transverses
            section_order = 2
            for ts_id in TRANSVERSE_SECTION_IDS:
                ts = QuestionSection.objects.get(id=ts_id)
                new_ts = QuestionSection.objects.create(
                    questionnaire=new_q,
                    title=ts.title,
                    order=section_order,
                )
                created_sections += 1
                section_order += 1

                for tq in transverse_questions[ts_id]:
                    Question.objects.create(
                        section=new_ts,
                        number=tq['number'],
                        text=tq['text'],
                        order=tq['order'],
                        answer='',
                        is_answered=False,
                        validation_status='PENDING',
                    )
                    created_questions += 1

            # 5. Créer les tokens key users
            key_user_names = [
                name.strip()
                for name in (source_q.key_users or '').split(',')
                if name.strip() and name.strip() != '—' and name.strip() != 'À désigner'
            ]
            backup_names = [
                name.strip()
                for name in (source_q.key_users_backup or '').split(',')
                if name.strip() and name.strip() != '—' and name.strip() != 'À désigner'
            ]
            all_key_users = key_user_names + backup_names

            for ku_name in all_key_users:
                KeyUserAccess.objects.create(
                    questionnaire=new_q,
                    name=ku_name,
                )
                created_tokens += 1
                print(f"   🔑 Token créé pour : {ku_name}")

        else:
            # Dry-run : juste afficher
            created_questionnaires += 1
            created_sections += 1 + len(TRANSVERSE_SECTION_IDS)
            created_questions += len(questions) + sum(
                len(transverse_questions[ts_id]) for ts_id in TRANSVERSE_SECTION_IDS
            )
            key_user_names = [
                n.strip() for n in (source_q.key_users or '').split(',')
                if n.strip() and n.strip() not in ('—', 'À désigner')
            ]
            backup_names = [
                n.strip() for n in (source_q.key_users_backup or '').split(',')
                if n.strip() and n.strip() not in ('—', 'À désigner')
            ]
            all_ku = key_user_names + backup_names
            created_tokens += len(all_ku)
            for ku in all_ku:
                print(f"   🔑 Token prévu pour : {ku}")

    # ────────────────────────────────────────────────────────────────────
    # RÉSUMÉ
    # ────────────────────────────────────────────────────────────────────
    print(f"\n{'=' * 70}")
    print(f"RÉSUMÉ {'(DRY-RUN)' if DRY_RUN else '(APPLIQUÉ)'}")
    print(f"{'=' * 70}")
    print(f"  Questionnaires créés : {created_questionnaires}")
    print(f"  Sections créées : {created_sections}")
    print(f"  Questions créées : {created_questions}")
    print(f"  Tokens key users créés : {created_tokens}")
    print()

    if DRY_RUN:
        print("⚠️  Rien n'a été modifié. Pour appliquer :")
        print(f"   python3 {sys.argv[0]} --execute")
    else:
        print("✅ Terminé ! Les nouveaux questionnaires techniques sont créés.")
        print("   Vérifiez sur /admin/ ou /kpi/ que tout est correct.")


if __name__ == '__main__':
    main()
