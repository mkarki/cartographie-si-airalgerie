"""
Remet à NOT_STARTED les questionnaires Call DOA, DOA Mailing et E-Exam PN
qui étaient marqués COMPLETED sans aucune réponse.
"""
from django.db import migrations


def reset_empty_questionnaires(apps, schema_editor):
    Questionnaire = apps.get_model('cartography', 'Questionnaire')
    for code in ['CALL-DOA', 'DOA-MAILING', 'EEXAM']:
        qs = Questionnaire.objects.filter(system__code=code, status='COMPLETED')
        for q in qs:
            # Vérifier qu'il n'y a vraiment aucune réponse
            has_answers = q.sections.filter(questions__answer__gt='').exists()
            if not has_answers:
                q.status = 'NOT_STARTED'
                q.save()
                print(f"  RESET {code}: COMPLETED -> NOT_STARTED")
            else:
                print(f"  SKIP {code}: contient des réponses")


def reverse(apps, schema_editor):
    Questionnaire = apps.get_model('cartography', 'Questionnaire')
    for code in ['CALL-DOA', 'DOA-MAILING', 'EEXAM']:
        Questionnaire.objects.filter(system__code=code).update(status='COMPLETED')


class Migration(migrations.Migration):
    dependencies = [
        ('cartography', '0022_fix_amos_flow_names'),
    ]
    operations = [
        migrations.RunPython(reset_empty_questionnaires, reverse),
    ]
