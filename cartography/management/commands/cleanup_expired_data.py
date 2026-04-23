"""
Purge les données dépassant leur durée de rétention.
Usage : python manage.py cleanup_expired_data [--dry-run]

Conformité loi 18-07 art. 3 (durée limitée).
"""
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from cartography.models import AuditLog, RightsRequest


class Command(BaseCommand):
    help = "Purge les enregistrements ayant dépassé leur durée de rétention."

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Afficher sans supprimer')

    def handle(self, *args, **options):
        dry = options['dry_run']
        now = timezone.now()

        # Journal d'audit
        audit_days = getattr(settings, 'RETENTION_AUDIT_DAYS', 365)
        audit_cutoff = now - timedelta(days=audit_days)
        old_audit = AuditLog.objects.filter(timestamp__lt=audit_cutoff)
        n_audit = old_audit.count()

        # Demandes d'exercice des droits
        rights_days = getattr(settings, 'RETENTION_RIGHTS_REQUESTS_DAYS', 1095)
        rights_cutoff = now - timedelta(days=rights_days)
        old_rights = RightsRequest.objects.filter(created_at__lt=rights_cutoff)
        n_rights = old_rights.count()

        self.stdout.write(f"Rétention AuditLog : {audit_days} j → {n_audit} entrées à purger (avant {audit_cutoff:%Y-%m-%d})")
        self.stdout.write(f"Rétention RightsRequest : {rights_days} j → {n_rights} entrées à purger (avant {rights_cutoff:%Y-%m-%d})")

        if dry:
            self.stdout.write(self.style.WARNING("DRY RUN — aucune suppression effectuée"))
            return

        if n_audit:
            old_audit.delete()
            self.stdout.write(self.style.SUCCESS(f"✅ {n_audit} entrées AuditLog supprimées"))
        if n_rights:
            old_rights.delete()
            self.stdout.write(self.style.SUCCESS(f"✅ {n_rights} entrées RightsRequest supprimées"))

        if not n_audit and not n_rights:
            self.stdout.write(self.style.SUCCESS("✅ Rien à purger"))
