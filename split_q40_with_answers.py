#!/usr/bin/env python3
"""
Split Q40 "Questions Techniques — Tous Systèmes" en 1 questionnaire par système,
avec copie des réponses déjà saisies + sections transverses (Infra/Sécu/Contrats).

Usage :
  python3 split_q40_with_answers.py            # dry-run
  python3 split_q40_with_answers.py --execute  # applique
"""
import os, sys, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import transaction
from cartography.models import Questionnaire, QuestionSection, Question, KeyUserAccess

DRY_RUN = '--execute' not in sys.argv
MASTER_Q_ID = 40

# Section Q40 → questionnaire métier cible (pour copie des métadonnées key users)
SECTION_TO_QUESTIONNAIRE = {
    139: 1, 140: 2, 141: 3, 142: 4, 143: 5, 144: 6, 145: 7, 146: 8, 147: 9,
    148: 10, 149: 11, 150: 12, 151: 13, 152: 14, 153: 15, 154: 16, 155: 17,
    156: 18, 157: 19, 158: 20, 159: 21, 160: 22, 161: 23, 162: 24, 163: 25,
    164: 26, 165: 27, 166: 28, 167: 29, 168: 30, 169: 31, 170: 32, 171: 33,
    172: 34, 173: 35, 174: 36, 175: 37, 176: 38, 177: 39,
}
TRANSVERSE_SECTION_IDS = [178, 179, 180]  # Infra, Sécurité, Contrats éditeurs


def get_section_system_name(section):
    title = section.title
    if '—' in title:
        title = title.split('—', 1)[1].strip()
    return title


def main():
    mode = "DRY-RUN" if DRY_RUN else "EXÉCUTION"
    print("=" * 70)
    print(f"SPLIT Q40 AVEC COPIE DES RÉPONSES — {mode}")
    print("=" * 70)

    master_q = Questionnaire.objects.get(id=MASTER_Q_ID)
    print(f"\nSource : [{master_q.id}] {master_q.system_name} — status={master_q.status}")

    # Réponses déjà présentes dans Q40
    all_answers = Question.objects.filter(section__questionnaire=master_q).exclude(answer='')
    print(f"Réponses présentes dans Q40 : {all_answers.count()}")

    # Charger transverses
    transverse_sections = QuestionSection.objects.filter(id__in=TRANSVERSE_SECTION_IDS).order_by('order')
    print(f"Sections transverses : {transverse_sections.count()}")

    created_q = created_s = created_quest = created_tokens = copied_answers = 0

    with transaction.atomic():
        for section in QuestionSection.objects.filter(questionnaire=master_q).order_by('order'):
            if section.id in TRANSVERSE_SECTION_IDS:
                continue
            if section.id not in SECTION_TO_QUESTIONNAIRE:
                print(f"  ⚠️  Section [{section.id}] '{section.title}' non mappée")
                continue

            source_q = Questionnaire.objects.get(id=SECTION_TO_QUESTIONNAIRE[section.id])
            section_name = get_section_system_name(section)
            questions = list(section.questions.order_by('order'))
            answered_in_section = sum(1 for q in questions if q.answer.strip())
            new_name = f"Questions Techniques — {source_q.system_name}"

            print(f"\n📋 {new_name}")
            print(f"   {len(questions)} questions spécifiques | {answered_in_section} déjà répondues")

            if DRY_RUN:
                created_q += 1
                created_s += 1 + len(TRANSVERSE_SECTION_IDS)
                created_quest += len(questions) + sum(
                    QuestionSection.objects.get(id=tid).questions.count()
                    for tid in TRANSVERSE_SECTION_IDS
                )
                copied_answers += answered_in_section
                continue

            # Création questionnaire
            new_q = Questionnaire.objects.create(
                system=None,
                system_name=new_name,
                phase=source_q.phase,
                priority_in_phase=source_q.priority_in_phase,
                editor=source_q.editor,
                direction=source_q.direction,
                key_users=source_q.key_users,
                key_users_backup=source_q.key_users_backup,
                responsible=source_q.responsible,
                status='IN_PROGRESS' if answered_in_section else 'NOT_STARTED',
            )
            created_q += 1

            # Section spécifique système
            new_section = QuestionSection.objects.create(
                questionnaire=new_q,
                title=f"Questions Techniques — {section_name}",
                order=1,
            )
            created_s += 1

            for q in questions:
                Question.objects.create(
                    section=new_section,
                    number=q.number,
                    text=q.text,
                    order=q.order,
                    answer=q.answer,
                    notes=q.notes or '',
                    is_answered=bool(q.answer.strip()),
                    validation_status=q.validation_status or 'PENDING',
                )
                created_quest += 1
                if q.answer.strip():
                    copied_answers += 1

            # Sections transverses
            section_order = 2
            for ts in transverse_sections:
                new_ts = QuestionSection.objects.create(
                    questionnaire=new_q,
                    title=ts.title,
                    order=section_order,
                )
                created_s += 1
                section_order += 1
                for tq in ts.questions.order_by('order'):
                    Question.objects.create(
                        section=new_ts,
                        number=tq.number,
                        text=tq.text,
                        order=tq.order,
                        answer=tq.answer,
                        notes=tq.notes or '',
                        is_answered=bool(tq.answer.strip()),
                        validation_status=tq.validation_status or 'PENDING',
                    )
                    created_quest += 1
                    if tq.answer.strip():
                        copied_answers += 1

            # Tokens key users
            key_users = [n.strip() for n in (source_q.key_users or '').split(',') if n.strip() and n.strip() not in ('—', 'À désigner')]
            backups = [n.strip() for n in (source_q.key_users_backup or '').split(',') if n.strip() and n.strip() not in ('—', 'À désigner')]
            for ku_name in key_users + backups:
                KeyUserAccess.objects.create(questionnaire=new_q, name=ku_name)
                created_tokens += 1

        if DRY_RUN:
            transaction.set_rollback(True)

    print(f"\n{'=' * 70}")
    print(f"RÉSUMÉ {'(DRY-RUN — rien appliqué)' if DRY_RUN else '(APPLIQUÉ)'}")
    print(f"{'=' * 70}")
    print(f"  Questionnaires créés  : {created_q}")
    print(f"  Sections créées       : {created_s}")
    print(f"  Questions créées      : {created_quest}")
    print(f"  Réponses copiées      : {copied_answers}")
    print(f"  Tokens key users      : {created_tokens}")
    if DRY_RUN:
        print(f"\n⚠️  Rien modifié. Pour appliquer : python3 {sys.argv[0]} --execute")


if __name__ == '__main__':
    main()
