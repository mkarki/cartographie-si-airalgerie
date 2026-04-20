"""
Split du questionnaire technique Q40 "Questions Techniques — Tous Systèmes"
en 1 questionnaire par système, avec :
- Copie des questions spécifiques
- Copie des réponses déjà saisies
- Ajout des sections transverses (Infra, Sécurité, Contrats éditeurs)
- Création des tokens KeyUserAccess pour chaque key user

Réversible : la migration reverse supprime les questionnaires et tokens créés
(identifiés par system_name LIKE "Questions Techniques —%" différent du Q40).
"""
import secrets
from django.db import migrations


MASTER_Q_ID = 40

SECTION_TO_QUESTIONNAIRE = {
    139: 1, 140: 2, 141: 3, 142: 4, 143: 5, 144: 6, 145: 7, 146: 8, 147: 9,
    148: 10, 149: 11, 150: 12, 151: 13, 152: 14, 153: 15, 154: 16, 155: 17,
    156: 18, 157: 19, 158: 20, 159: 21, 160: 22, 161: 23, 162: 24, 163: 25,
    164: 26, 165: 27, 166: 28, 167: 29, 168: 30, 169: 31, 170: 32, 171: 33,
    172: 34, 173: 35, 174: 36, 175: 37, 176: 38, 177: 39,
}
TRANSVERSE_SECTION_IDS = [178, 179, 180]


def get_section_system_name(title):
    if '—' in title:
        title = title.split('—', 1)[1].strip()
    return title


def split_q40(apps, schema_editor):
    Questionnaire = apps.get_model('cartography', 'Questionnaire')
    QuestionSection = apps.get_model('cartography', 'QuestionSection')
    Question = apps.get_model('cartography', 'Question')
    KeyUserAccess = apps.get_model('cartography', 'KeyUserAccess')

    try:
        master_q = Questionnaire.objects.get(id=MASTER_Q_ID)
    except Questionnaire.DoesNotExist:
        print(f"  ⚠️  Q40 introuvable, migration ignorée")
        return

    # Idempotence : si le split est déjà fait, on skippe
    existing_split = Questionnaire.objects.filter(
        system_name__startswith='Questions Techniques —'
    ).exclude(id=MASTER_Q_ID).count()
    if existing_split > 0:
        print(f"  ℹ️  Déjà {existing_split} questionnaires techniques split existants, skip")
        return

    transverse_sections = list(
        QuestionSection.objects.filter(id__in=TRANSVERSE_SECTION_IDS).order_by('order')
    )

    created_q = created_s = created_quest = created_tokens = copied_answers = 0

    for section in QuestionSection.objects.filter(questionnaire=master_q).order_by('order'):
        if section.id in TRANSVERSE_SECTION_IDS:
            continue
        if section.id not in SECTION_TO_QUESTIONNAIRE:
            continue

        source_q_id = SECTION_TO_QUESTIONNAIRE[section.id]
        try:
            source_q = Questionnaire.objects.get(id=source_q_id)
        except Questionnaire.DoesNotExist:
            print(f"  ⚠️  Q{source_q_id} source introuvable, skip section {section.id}")
            continue

        section_name = get_section_system_name(section.title)
        questions = list(Question.objects.filter(section=section).order_by('order'))
        answered = sum(1 for q in questions if (q.answer or '').strip())
        new_name = f"Questions Techniques — {source_q.system_name}"

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
            status='IN_PROGRESS' if answered else 'NOT_STARTED',
        )
        created_q += 1

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
                answer=q.answer or '',
                notes=q.notes or '',
                is_answered=bool((q.answer or '').strip()),
                validation_status=q.validation_status or 'PENDING',
            )
            created_quest += 1
            if (q.answer or '').strip():
                copied_answers += 1

        section_order = 2
        for ts in transverse_sections:
            new_ts = QuestionSection.objects.create(
                questionnaire=new_q,
                title=ts.title,
                order=section_order,
            )
            created_s += 1
            section_order += 1
            for tq in Question.objects.filter(section=ts).order_by('order'):
                Question.objects.create(
                    section=new_ts,
                    number=tq.number,
                    text=tq.text,
                    order=tq.order,
                    answer=tq.answer or '',
                    notes=tq.notes or '',
                    is_answered=bool((tq.answer or '').strip()),
                    validation_status=tq.validation_status or 'PENDING',
                )
                created_quest += 1
                if (tq.answer or '').strip():
                    copied_answers += 1

        key_users = [
            n.strip() for n in (source_q.key_users or '').split(',')
            if n.strip() and n.strip() not in ('—', 'À désigner')
        ]
        backups = [
            n.strip() for n in (source_q.key_users_backup or '').split(',')
            if n.strip() and n.strip() not in ('—', 'À désigner')
        ]
        for ku_name in key_users + backups:
            KeyUserAccess.objects.create(
                questionnaire=new_q,
                name=ku_name,
                token=secrets.token_urlsafe(32),
            )
            created_tokens += 1

    print(f"  ✅ Split Q40: {created_q} questionnaires, {created_s} sections, "
          f"{created_quest} questions, {copied_answers} réponses copiées, "
          f"{created_tokens} tokens")


def reverse_split(apps, schema_editor):
    Questionnaire = apps.get_model('cartography', 'Questionnaire')
    qs = Questionnaire.objects.filter(
        system_name__startswith='Questions Techniques —'
    ).exclude(id=MASTER_Q_ID)
    n = qs.count()
    qs.delete()
    print(f"  ↩️  Supprimé {n} questionnaires techniques split")


class Migration(migrations.Migration):
    dependencies = [
        ('cartography', '0024_update_aims_flows_reunion_doa'),
    ]
    operations = [
        migrations.RunPython(split_q40, reverse_split),
    ]
