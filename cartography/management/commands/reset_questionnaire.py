"""
Reset les reponses d'un questionnaire pour qu'un key user le ressaisisse.

Usage :
    python manage.py reset_questionnaire --name "E-DOLÉANCE"
    python manage.py reset_questionnaire --id 23
    python manage.py reset_questionnaire --name "E-DOLÉANCE" --dry-run

Vide :
  - Question.answer            -> ''
  - Question.is_answered       -> False
  - Question.notes             -> ''
  - Question.validation_status -> 'PENDING'
  - Question.validated_by      -> ''
  - Question.validation_comment-> ''
  - Question.auditor_comment   -> ''

Met le Questionnaire.status a NOT_STARTED.
Le contenu (questions, sections, key users, token d'acces) est conserve :
le key user pourra rouvrir son lien et tout ressaisir.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from cartography.models import Questionnaire, Question


class Command(BaseCommand):
    help = "Vide toutes les reponses d'un questionnaire pour ressaisie"

    def add_arguments(self, parser):
        parser.add_argument('--name', help='Nom exact du systeme (system_name)')
        parser.add_argument('--id', type=int, help='ID du questionnaire')
        parser.add_argument('--dry-run', action='store_true',
                            help='N\'effectue aucune modification, affiche seulement')

    def handle(self, *args, **opts):
        if not opts['name'] and not opts['id']:
            raise CommandError('Specifier --name ou --id')

        qs = Questionnaire.objects.all()
        if opts['id']:
            qs = qs.filter(id=opts['id'])
        if opts['name']:
            qs = qs.filter(system_name=opts['name'])

        if not qs.exists():
            raise CommandError('Aucun questionnaire trouve')

        for q in qs:
            self.stdout.write(self.style.WARNING(
                f'\nQuestionnaire : [{q.id}] {q.system_name}  (status actuel : {q.status})'))

            questions = Question.objects.filter(section__questionnaire=q)
            answered = questions.exclude(answer='').count()
            total = questions.count()
            self.stdout.write(f'  {answered}/{total} questions actuellement repondues')

            if opts['dry_run']:
                self.stdout.write(self.style.NOTICE('  [DRY-RUN] aucune modification'))
                continue

            with transaction.atomic():
                updated = questions.update(
                    answer='',
                    is_answered=False,
                    notes='',
                    validation_status='PENDING',
                    validated_by='',
                    validation_comment='',
                    auditor_comment='',
                    auditor_comment_by='',
                )
                q.status = 'NOT_STARTED'
                q.save(update_fields=['status'])

            self.stdout.write(self.style.SUCCESS(
                f'  -> {updated} questions remises a zero, status -> NOT_STARTED'))

        self.stdout.write(self.style.SUCCESS('\nOK termine.'))
