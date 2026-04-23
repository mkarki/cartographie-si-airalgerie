"""
Management command pour charger la table de correspondance matricule → variantes.
Usage :
    python manage.py load_matricules /chemin/vers/correspondance_matricules.json

Le JSON attendu suit le format produit par le script local :
[
    {"matricule": "KU001", "normalized_name": "...", "raw_variants": ["..."], ...},
    ...
]
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand

from cartography.models import MatriculeMap


class Command(BaseCommand):
    help = "Charge la table matricule → variantes depuis un JSON local"

    def add_arguments(self, parser):
        parser.add_argument('json_path', type=str, help='Chemin vers correspondance_matricules.json')
        parser.add_argument('--replace', action='store_true', help='Supprimer les entrées existantes avant insertion')

    def handle(self, *args, **options):
        path = Path(options['json_path'])
        if not path.exists():
            self.stderr.write(self.style.ERROR(f"Fichier introuvable : {path}"))
            return

        with open(path, encoding='utf-8') as f:
            data = json.load(f)

        if options['replace']:
            n = MatriculeMap.objects.all().count()
            MatriculeMap.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Supprimé {n} entrées existantes"))

        created = 0
        updated = 0
        for item in data:
            matricule = item['matricule']
            variants = list(set(
                item.get('raw_variants', []) + [item.get('normalized_name', '')]
            ))
            variants = [v for v in variants if v and len(v) >= 3]

            obj, was_created = MatriculeMap.objects.update_or_create(
                matricule=matricule,
                defaults={'variants': variants},
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"✅ {created} créés, {updated} mis à jour (total {MatriculeMap.objects.count()})"
        ))
