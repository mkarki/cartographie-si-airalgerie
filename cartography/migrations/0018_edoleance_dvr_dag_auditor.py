# Migration: transfert E-doléance DRM→DVR + DAG DivisionAccess→AuditorAccess

from django.db import migrations


def apply_changes(apps, schema_editor):
    System = apps.get_model('cartography', 'System')
    Structure = apps.get_model('cartography', 'Structure')
    DivisionAccess = apps.get_model('cartography', 'DivisionAccess')
    AuditorAccess = apps.get_model('cartography', 'AuditorAccess')

    # 1. E-doléance : DRM → DVR
    dvr = Structure.objects.get(code='DVR')
    System.objects.filter(name__icontains='dol').update(structure=dvr)

    # 2. Mme la DAG : DivisionAccess → AuditorAccess (même token, vue complète)
    dag_token = 'qYymtXBumq3o0BDdFvyO74FjwWuqn_8XeutquSSmUBg'
    try:
        dag_div = DivisionAccess.objects.get(token=dag_token)
        AuditorAccess.objects.get_or_create(
            token=dag_token,
            defaults={'name': 'Mme la DAG', 'email': dag_div.email or ''}
        )
        dag_div.is_active = False
        dag_div.save()
    except DivisionAccess.DoesNotExist:
        # Déjà migré (shell local), s'assurer que l'AuditorAccess existe
        AuditorAccess.objects.get_or_create(
            token=dag_token,
            defaults={'name': 'Mme la DAG', 'email': ''}
        )


def reverse_changes(apps, schema_editor):
    System = apps.get_model('cartography', 'System')
    Structure = apps.get_model('cartography', 'Structure')
    DivisionAccess = apps.get_model('cartography', 'DivisionAccess')
    AuditorAccess = apps.get_model('cartography', 'AuditorAccess')

    # Reverse E-doléance : DVR → DRM
    drm = Structure.objects.get(code='DRM')
    System.objects.filter(name__icontains='dol').update(structure=drm)

    # Reverse DAG : réactiver DivisionAccess, supprimer AuditorAccess
    dag_token = 'qYymtXBumq3o0BDdFvyO74FjwWuqn_8XeutquSSmUBg'
    AuditorAccess.objects.filter(token=dag_token).delete()
    DivisionAccess.objects.filter(token=dag_token).update(is_active=True)


class Migration(migrations.Migration):

    dependencies = [
        ('cartography', '0017_personalized_division_access'),
    ]

    operations = [
        migrations.RunPython(apply_changes, reverse_changes),
    ]
