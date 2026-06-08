"""Provisionne l'accès Division manquant pour la DAGP (HABEL Rachid) et
réactive par sécurité l'accès DFC (KHELFI Redouane).

Même principe que 0017 : token fixe + idempotent (get_or_create), afin que
le lien soit déterministe et provisionné en prod au déploiement.
"""
from django.db import migrations

# (code structure, nom, email, token fixe)
NEW_DIVISION_PROFILES = [
    ('DAGP', 'HABEL Rachid', 'habel.rachid@airalgerie.dz',
     'DKTCy9F4eQF1xOx5XeFN4MKhzrg6rAlaYvzOWXUlGfg'),
]

# Accès existants à s'assurer actifs (token de la migration 0017)
ENSURE_ACTIVE_TOKENS = [
    'JazLAOvgbFrMX1BLGxN19AzasbuiHzfyx3lNBO-A00o',  # DFC — KHELFI Redouane
]


def provision(apps, schema_editor):
    Structure = apps.get_model('cartography', 'Structure')
    DivisionAccess = apps.get_model('cartography', 'DivisionAccess')

    for code, name, email, token in NEW_DIVISION_PROFILES:
        try:
            struct = Structure.objects.get(code=code)
        except Structure.DoesNotExist:
            continue
        DivisionAccess.objects.get_or_create(
            token=token,
            defaults={'structure': struct, 'name': name,
                      'email': email, 'is_active': True},
        )

    # Réactiver les accès existants éventuellement désactivés
    DivisionAccess.objects.filter(token__in=ENSURE_ACTIVE_TOKENS).update(is_active=True)


class Migration(migrations.Migration):

    dependencies = [
        ('cartography', '0030_add_process_edit_log'),
    ]

    operations = [
        migrations.RunPython(provision, migrations.RunPython.noop),
    ]
