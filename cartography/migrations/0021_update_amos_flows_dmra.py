"""
Data migration: corrections flux AMOS suite entretien DMRA 12 avril 2026.

- Supprimer AMOS→SAGE-STOCK, QPULSE→AMOS, AMOS→QPULSE, AMOS→AGS
- Corriger AIMS→AMOS et AMOS→AIMS descriptions
- Créer AMOS→SAGE-FIN (stock et valorisation vers ERP)
"""
from django.db import migrations


def update_amos_flows(apps, schema_editor):
    DataFlow = apps.get_model('cartography', 'DataFlow')
    System = apps.get_model('cartography', 'System')

    amos = System.objects.get(code='AMOS')
    aims = System.objects.get(code='AIMS')

    # Suppressions par source/target
    deletions = [
        ('AMOS', 'SAGE-STOCK'),
        ('QPULSE', 'AMOS'),
        ('AMOS', 'QPULSE'),
        ('AMOS', 'AGS'),
    ]
    for src_code, tgt_code in deletions:
        src = System.objects.get(code=src_code)
        tgt = System.objects.get(code=tgt_code)
        deleted, _ = DataFlow.objects.filter(source=src, target=tgt).delete()
        print(f"  DEL {src_code}→{tgt_code}: {deleted} flux supprimé(s)")

    # Corrections descriptions
    DataFlow.objects.filter(source=aims, target=amos).update(
        description="Heures de vol effectuées, cycles effectués et programme des vols transmis depuis AIMS vers AMOS"
    )
    DataFlow.objects.filter(source=amos, target=aims).update(
        description="Prévisions d'immobilisation de maintenance de la flotte transmises depuis AMOS vers AIMS"
    )

    # Création AMOS → SAGE-FIN
    sage_fin = System.objects.get(code='SAGE-FIN')
    if not DataFlow.objects.filter(source=amos, target=sage_fin).exists():
        DataFlow.objects.create(
            source=amos,
            target=sage_fin,
            description="Stock et valorisation des pièces de rechange transmis depuis AMOS vers le système comptable (ERP)",
            frequency="PERIODIC",
        )


def reverse_amos_flows(apps, schema_editor):
    DataFlow = apps.get_model('cartography', 'DataFlow')
    System = apps.get_model('cartography', 'System')

    amos = System.objects.get(code='AMOS')
    aims = System.objects.get(code='AIMS')
    sage_stock = System.objects.get(code='SAGE-STOCK')
    qpulse = System.objects.get(code='QPULSE')
    ags = System.objects.get(code='AGS')
    sage_fin = System.objects.get(code='SAGE-FIN')

    # Supprimer le nouveau flux
    DataFlow.objects.filter(source=amos, target=sage_fin).delete()

    # Restaurer descriptions originales
    DataFlow.objects.filter(source=aims, target=amos).update(
        description="Transmission du plan d'immobilisation avions vers AMOS"
    )
    DataFlow.objects.filter(source=amos, target=aims).update(
        description="Retour de la disponibilité des avions depuis AMOS"
    )

    # Recréer les flux supprimés
    DataFlow.objects.get_or_create(source=amos, target=sage_stock, defaults={
        'description': 'Besoins en pièces de rechange vers SAGE Stock', 'frequency': 'PERIODIC'})
    DataFlow.objects.get_or_create(source=qpulse, target=amos, defaults={
        'description': 'Actions correctives vers AMOS', 'frequency': 'PERIODIC'})
    DataFlow.objects.get_or_create(source=amos, target=qpulse, defaults={
        'description': 'Incidents et non-conformités vers Q-Pulse', 'frequency': 'PERIODIC'})
    DataFlow.objects.get_or_create(source=amos, target=ags, defaults={
        'description': 'Données de maintenance vers AGS pour analyse', 'frequency': 'PERIODIC'})


class Migration(migrations.Migration):
    dependencies = [
        ('cartography', '0020_seed_process_world_tracer'),
    ]
    operations = [
        migrations.RunPython(update_amos_flows, reverse_amos_flows),
    ]
