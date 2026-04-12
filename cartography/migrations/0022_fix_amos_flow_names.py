"""
Fix: corriger les noms courts des flux AMOS qui n'ont pas été mis à jour
par la migration 0021 (exécutée avant l'ajout des champs name).
"""
from django.db import migrations


def fix_names(apps, schema_editor):
    DataFlow = apps.get_model('cartography', 'DataFlow')
    System = apps.get_model('cartography', 'System')

    amos = System.objects.get(code='AMOS')
    aims = System.objects.get(code='AIMS')
    sage_fin = System.objects.get(code='SAGE-FIN')

    DataFlow.objects.filter(source=aims, target=amos).update(
        name="Heures de vol, cycles et programme des vols"
    )
    DataFlow.objects.filter(source=amos, target=aims).update(
        name="Prévisions d'immobilisation maintenance"
    )
    DataFlow.objects.filter(source=amos, target=sage_fin).update(
        name="Stock et valorisation des pièces"
    )


class Migration(migrations.Migration):
    dependencies = [
        ('cartography', '0021_update_amos_flows_dmra'),
    ]
    operations = [
        migrations.RunPython(fix_names, migrations.RunPython.noop),
    ]
