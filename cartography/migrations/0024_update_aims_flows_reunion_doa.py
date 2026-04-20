"""
Mise à jour des flux AIMS suite à la réunion DOA du 14/04/2026.
Corrections validées avec M. BENYELLES et Mme SAID :
- Suppression FLYSMART -> AIMS (pas pertinent)
- Suppression AIMS -> ACARS (pas d'intérêt)
- Modification ACARS -> AIMS : ajout OOOI (à construire)
- Modification ALTEA -> AIMS : ajout charges PAX
- Modification AMOS -> AIMS : ajout pannes non-immobilisantes
- Modification AIMS -> SKYBOOK : programme pilote individuel
- Modification AIMS -> DOA-MAILING : saisie manuelle, automatisation souhaitée
- SITATEX <-> AIMS : à confirmer (M. Azil Ali DSI)
- AIMS -> ALTEA : à confirmer (key user Altéa)
- AIMS -> OAG : à confirmer (key user OAG)
"""
from django.db import migrations


def update_aims_flows(apps, schema_editor):
    DataFlow = apps.get_model('cartography', 'DataFlow')
    System = apps.get_model('cartography', 'System')

    aims = System.objects.get(code='AIMS')

    # 1. Supprimer FLYSMART -> AIMS
    deleted = DataFlow.objects.filter(
        source__code='FLYSMART', target=aims
    ).delete()
    print(f"  SUPPR FLYSMART -> AIMS: {deleted}")

    # 2. Supprimer AIMS -> ACARS
    deleted = DataFlow.objects.filter(
        source=aims, target__code='ACARS'
    ).delete()
    print(f"  SUPPR AIMS -> ACARS: {deleted}")

    # 3. Modifier ACARS -> AIMS : ajouter OOOI
    for f in DataFlow.objects.filter(source__code='ACARS', target=aims):
        f.name = 'Position/Fuel + OOOI (à construire)'
        f.description = (
            'Données de position, carburant et messages OOOI '
            '(Out/Off/On/In) depuis ACARS. '
            'Le flux OOOI est souhaité mais pas encore implémenté.'
        )
        f.save()
        print(f"  MODIF ACARS -> AIMS: {f.name}")

    # 4. Modifier ALTEA -> AIMS : charges PAX
    for f in DataFlow.objects.filter(source__code='ALTEA', target=aims):
        f.name = 'MVT Mouvements + Charges PAX'
        f.description = (
            'Messages de mouvement depuis DCS vers AIMS, incluant les charges '
            'prévisionnelles passagers (PAX embarqués et prévisionnels). '
            'Données jugées fiables.'
        )
        f.save()
        print(f"  MODIF ALTEA -> AIMS: {f.name}")

    # 5. Modifier AMOS -> AIMS : pannes non-immobilisantes
    for f in DataFlow.objects.filter(source__code='AMOS', target=aims):
        f.name = 'Prévisions immobilisation + Pannes limitantes'
        f.description = (
            "Prévisions d'immobilisation maintenance et informations sur les "
            "pannes non-immobilisantes limitant la capacité opérationnelle "
            "(ex: limitation RVSM empêchant certaines destinations). "
            "Ce flux de pannes est à construire."
        )
        f.save()
        print(f"  MODIF AMOS -> AIMS: {f.name}")

    # 6. Modifier AIMS -> SKYBOOK : programme pilote individuel
    for f in DataFlow.objects.filter(source=aims, target__code='SKYBOOK'):
        f.name = 'Programme de vol pilote'
        f.description = (
            "Programme de vol et documentation opérationnelle vers SkyBook. "
            "Amélioration souhaitée : le pilote ne devrait voir que son propre "
            "programme de vol (actuellement il voit tous les plans de vol de la journée)."
        )
        f.save()
        print(f"  MODIF AIMS -> SKYBOOK: {f.name}")

    # 7. Modifier AIMS -> DOA-MAILING : saisie manuelle
    for f in DataFlow.objects.filter(source=aims, target__code='DOA-MAILING'):
        f.name = 'Données PN pour mailing (manuel, à automatiser)'
        f.description = (
            "Données du personnel navigant pour le mailing DOA. "
            "Actuellement saisie manuelle, pas de flux automatique depuis AIMS. "
            "Automatisation souhaitée (quick win potentiel vu que le flux existe "
            "déjà vers Call DOA)."
        )
        f.is_automated = False
        f.save()
        print(f"  MODIF AIMS -> DOA-MAILING: {f.name}")

    # 8. Modifier SITATEX -> AIMS : à confirmer
    for f in DataFlow.objects.filter(source__code='SITATEX', target=aims):
        f.name = 'Messages Type B AIMS (à confirmer)'
        f.description = 'Messages SITA vers AIMS. À confirmer avec M. Azil Ali (DSI).'
        f.save()
        print(f"  MODIF SITATEX -> AIMS: {f.name}")

    # 9. Modifier AIMS -> SITATEX : à confirmer
    for f in DataFlow.objects.filter(source=aims, target__code='SITATEX'):
        f.name = 'Messages Sortants AIMS (à confirmer)'
        f.description = 'Messages Type B sortants depuis AIMS. À confirmer avec M. Azil Ali (DSI).'
        f.save()
        print(f"  MODIF AIMS -> SITATEX: {f.name}")

    # 10. Modifier AIMS -> ALTEA : à confirmer
    for f in DataFlow.objects.filter(source=aims, target__code='ALTEA'):
        f.name = 'Programme de Vol (à confirmer)'
        f.description = (
            "Transmission du programme de vol depuis AIMS vers Altéa. "
            "À confirmer avec le key user Altéa."
        )
        f.save()
        print(f"  MODIF AIMS -> ALTEA: {f.name}")

    # 11. Modifier AIMS -> OAG : à confirmer
    for f in DataFlow.objects.filter(source=aims, target__code='OAG'):
        f.name = 'Programme de Vol OAG (à confirmer)'
        f.description = (
            "Diffusion du programme de vol vers OAG/INNOVATA. "
            "À confirmer avec le key user OAG."
        )
        f.save()
        print(f"  MODIF AIMS -> OAG: {f.name}")

    # 12. Modifier AIMS -> EEXAM : saisie manuelle, automatisation souhaitée
    for f in DataFlow.objects.filter(source=aims, target__code='EEXAM'):
        f.name = 'Examens PN (manuel, à automatiser)'
        f.description = (
            "Données de formation PN vers E-Exam. "
            "Actuellement saisie manuelle sur la plateforme. "
            "Automatisation souhaitée."
        )
        f.is_automated = False
        f.save()
        print(f"  MODIF AIMS -> EEXAM: {f.name}")


def reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('cartography', '0023_reset_doa_empty_questionnaires'),
    ]
    operations = [
        migrations.RunPython(update_aims_flows, reverse),
    ]
