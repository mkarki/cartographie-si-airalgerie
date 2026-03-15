#!/usr/bin/env python
"""
Script de mise à jour de la cartographie SI avec les nouvelles infos
(structures, systèmes, key users) du fichier Word DAG.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from cartography.models import Structure, System, SystemCategory

# ============================================================
# 1. Nouvelles structures à ajouter
# ============================================================
new_structures = [
    {'code': 'DAGP', 'name': 'Direction Administration Générale et Patrimoine', 'color': '#8b5cf6'},
    {'code': 'DFC', 'name': 'Direction Finance et Comptabilité', 'color': '#f59e0b'},
    {'code': 'DIVEX', 'name': 'Direction de l\'Exploitation', 'color': '#06b6d4'},
    {'code': 'DSC', 'name': 'Direction Sûreté et Conformité', 'color': '#ec4899'},
    {'code': 'RGF', 'name': 'Représentation Générale France', 'color': '#84cc16'},
]

for s in new_structures:
    obj, created = Structure.objects.update_or_create(
        code=s['code'],
        defaults={'name': s['name'], 'color': s['color']}
    )
    print(f"{'✅ Créé' if created else '🔄 Mis à jour'} structure: {obj.code} - {obj.name}")

# Renommer DD -> DC (Direction Commerciale gère distribution aussi)
# Renommer DF -> DFC
try:
    df = Structure.objects.get(code='DF')
    df.code = 'DFC'
    df.name = 'Direction Finance et Comptabilité'
    df.save()
    print("🔄 Renommé DF -> DFC")
except Structure.DoesNotExist:
    pass
except Exception as e:
    print(f"⚠️ DF->DFC: {e}")

# Renommer DQSA -> DSC
try:
    dqsa = Structure.objects.get(code='DQSA')
    dqsa.code = 'DSC'
    dqsa.name = 'Direction Sûreté et Conformité'
    dqsa.save()
    print("🔄 Renommé DQSA -> DSC")
except Structure.DoesNotExist:
    pass
except Exception as e:
    print(f"⚠️ DQSA->DSC: {e}")

# Fusionner RGFN + RGFS -> RGF
try:
    rgf = Structure.objects.get(code='RGF')
    # Rattacher les systèmes de RGFN et RGFS à RGF
    for old_code in ['RGFN', 'RGFS']:
        try:
            old = Structure.objects.get(code=old_code)
            System.objects.filter(structure=old).update(structure=rgf)
            old.delete()
            print(f"🔄 Fusionné {old_code} -> RGF")
        except Structure.DoesNotExist:
            pass
except Structure.DoesNotExist:
    pass

# Renommer DVR -> DC (BAC est sous DC dans le nouveau fichier)
try:
    dvr = Structure.objects.get(code='DVR')
    dc = Structure.objects.get(code='DC')
    System.objects.filter(structure=dvr).update(structure=dc)
    dvr.delete()
    print("🔄 Fusionné DVR -> DC (BAC sous DC)")
except Structure.DoesNotExist:
    pass

# Renommer DRM -> DC (ATPCO est sous DC dans le nouveau fichier)
try:
    drm = Structure.objects.get(code='DRM')
    dc = Structure.objects.get(code='DC')
    System.objects.filter(structure=drm).update(structure=dc)
    drm.delete()
    print("🔄 Fusionné DRM -> DC (ATPCO sous DC)")
except Structure.DoesNotExist:
    pass

# DD -> DC (ACCELYA DIST, BSP LINK, HERMES, SITE WEB sont sous DC)
try:
    dd = Structure.objects.get(code='DD')
    dc = Structure.objects.get(code='DC')
    System.objects.filter(structure=dd).update(structure=dc)
    dd.delete()
    print("🔄 Fusionné DD -> DC")
except Structure.DoesNotExist:
    pass

# DL (SAGE STOCK) -> DAGP
try:
    dl = Structure.objects.get(code='DL')
    dagp = Structure.objects.get(code='DAGP')
    System.objects.filter(structure=dl).update(structure=dagp)
    dl.delete()
    print("🔄 Fusionné DL -> DAGP (SAGE STOCK)")
except Structure.DoesNotExist:
    pass

# DP -> DIVEX (AIMS et OAG sont sous DIVEX dans le nouveau fichier)
try:
    dp = Structure.objects.get(code='DP')
    divex = Structure.objects.get(code='DIVEX')
    System.objects.filter(structure=dp).update(structure=divex)
    dp.delete()
    print("🔄 Fusionné DP -> DIVEX (AIMS, OAG)")
except Structure.DoesNotExist:
    pass

# CCO -> DIVEX (CCO)
try:
    cco = Structure.objects.get(code='CCO')
    divex = Structure.objects.get(code='DIVEX')
    System.objects.filter(structure=cco).update(structure=divex)
    cco.delete()
    print("🔄 Fusionné CCO -> DIVEX")
except Structure.DoesNotExist:
    pass

# DO -> DOA (JET PLANER, SKYBOOK sous DOA)
try:
    do = Structure.objects.get(code='DO')
    doa = Structure.objects.get(code='DOA')
    System.objects.filter(structure=do).update(structure=doa)
    do.delete()
    print("🔄 Fusionné DO -> DOA")
except Structure.DoesNotExist:
    pass

# DPD -> DIVEX (QLIK sous DPD+DOS)
try:
    dpd = Structure.objects.get(code='DPD')
    divex = Structure.objects.get(code='DIVEX')
    System.objects.filter(structure=dpd).update(structure=divex)
    dpd.delete()
    print("🔄 Fusionné DPD -> DIVEX")
except Structure.DoesNotExist:
    pass

# ALTEA : DC -> DC (déjà OK)
# ACCELYA (Rapid) : DF -> DFC
try:
    accelya = System.objects.get(code='ACCELYA')
    dfc = Structure.objects.get(code='DFC')
    accelya.structure = dfc
    accelya.save()
    print("🔄 ACCELYA (Rapid Passagers) -> DFC")
except (System.DoesNotExist, Structure.DoesNotExist):
    pass

# FLYSMART : mettre à jour l'éditeur
try:
    flysmart = System.objects.get(code='FLYSMART')
    flysmart.vendor = 'AIRBUS/BOEING/ATR'
    flysmart.save()
    print("🔄 FLYSMART éditeur mis à jour")
except System.DoesNotExist:
    pass

# ============================================================
# 2. Nouveaux systèmes à ajouter
# ============================================================
print("\n=== Ajout des nouveaux systèmes ===")

dc = Structure.objects.get(code='DC')
doa = Structure.objects.get(code='DOA')
divex = Structure.objects.get(code='DIVEX')
dos = Structure.objects.get(code='DOS')
dsi = Structure.objects.get(code='DSI')

# Catégories
cat_core = SystemCategory.objects.get(id=1)       # Core Business
cat_dist = SystemCategory.objects.get(id=2)        # Distribution & Commercial
cat_ops = SystemCategory.objects.get(id=6)         # Qualité & Opérations
cat_rh = SystemCategory.objects.get(id=4)          # RH & Formation
cat_comm = SystemCategory.objects.get(id=7)        # Communication & Support

new_systems = [
    # DOA - nouveaux systèmes
    {
        'code': 'DOA-MAILING',
        'name': 'DOA Mailing',
        'description': 'Système de mailing de la Direction des Opérations Aériennes',
        'vendor': 'Boite de développement',
        'category': cat_comm,
        'structure': doa,
        'criticality': 'BASSE',
        'mode': 'INHOUSE',
    },
    {
        'code': 'CALL-DOA',
        'name': 'Call DOA',
        'description': 'Application de gestion des appels de la Direction des Opérations Aériennes',
        'vendor': 'Boite de développement CampusAve',
        'category': cat_comm,
        'structure': doa,
        'criticality': 'BASSE',
        'mode': 'INHOUSE',
    },
    # DIVEX (CCO) - nouveaux applicatifs
    {
        'code': 'CTRL-PROG',
        'name': 'Application de contrôle des programmes PN/Avions',
        'description': 'Application de contrôle des programmes Personnel Navigant et Avions',
        'vendor': 'Ingénieur CCO',
        'category': cat_ops,
        'structure': divex,
        'criticality': 'HAUTE',
        'mode': 'INHOUSE',
    },
    {
        'code': 'DASH-PONCT-J',
        'name': 'Dashboard Ponctualité le jour J',
        'description': 'Tableau de bord de suivi de la ponctualité des vols en temps réel',
        'vendor': 'DSI',
        'category': cat_ops,
        'structure': divex,
        'criticality': 'HAUTE',
        'mode': 'INHOUSE',
    },
    {
        'code': 'DASH-PONCT-H',
        'name': 'Dashboard Historique Ponctualité',
        'description': 'Tableau de bord historique de la ponctualité des vols',
        'vendor': 'DSI',
        'category': cat_ops,
        'structure': divex,
        'criticality': 'MOYENNE',
        'mode': 'INHOUSE',
    },
    {
        'code': 'SUIVI-IRREG',
        'name': 'Applicatif suivi des irrégularités des vols le jour J',
        'description': 'Application de suivi des irrégularités des vols en temps réel',
        'vendor': 'DSI',
        'category': cat_ops,
        'structure': divex,
        'criticality': 'HAUTE',
        'mode': 'INHOUSE',
    },
]

for sys_data in new_systems:
    obj, created = System.objects.update_or_create(
        code=sys_data['code'],
        defaults={
            'name': sys_data['name'],
            'description': sys_data['description'],
            'vendor': sys_data['vendor'],
            'category': sys_data['category'],
            'structure': sys_data['structure'],
            'criticality': sys_data['criticality'],
            'mode': sys_data['mode'],
        }
    )
    print(f"{'✅ Créé' if created else '🔄 Mis à jour'} système: {obj.code} - {obj.name}")

# SAGE Finance : fusionner RGFN et RGFS en un seul
try:
    sage_n = System.objects.get(code='SAGE-FIN-N')
    sage_n.code = 'SAGE-FIN'
    sage_n.name = 'SAGE Finance (PAR/LYS/MRS)'
    sage_n.vendor = 'MERCURIA'
    sage_n.save()
    print("🔄 SAGE-FIN-N -> SAGE-FIN (fusionné)")
except System.DoesNotExist:
    pass

try:
    sage_s = System.objects.get(code='SAGE-FIN-S')
    sage_s.delete()
    print("🗑️ Supprimé SAGE-FIN-S (fusionné dans SAGE-FIN)")
except System.DoesNotExist:
    pass

# ============================================================
# 3. Résumé final
# ============================================================
print("\n" + "=" * 50)
print("RÉSUMÉ FINAL")
print("=" * 50)
print(f"Structures: {Structure.objects.count()}")
print(f"Systèmes: {System.objects.count()}")
print()
print("Structures:")
for s in Structure.objects.all():
    count = System.objects.filter(structure=s).count()
    print(f"  {s.code}: {s.name} ({count} systèmes)")
print()
print("Systèmes:")
for sys in System.objects.select_related('structure').all():
    print(f"  [{sys.structure.code}] {sys.code} - {sys.name}")
