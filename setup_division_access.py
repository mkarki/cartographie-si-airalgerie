"""
Script de création des accès division personnalisés.
Usage: python manage.py runscript setup_division_access
   ou: python manage.py shell < setup_division_access.py
"""
import os, sys, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from cartography.models import DivisionAccess, Structure, AuditorAccess

# ── 1. Supprimer les anciens tokens division ──
deleted = DivisionAccess.objects.all().delete()
print(f"[1/3] Anciens tokens supprimés: {deleted}")

# ── 2. Créer les accès admin (PDG + Conseiller) via AuditorAccess ──
admin_profiles = [
    ("M. le PDG", ""),
    ("DOUMI Nabil (Conseiller PDG)", "doumi.nabil@airalgerie.dz"),
]

print("\n[2/3] Accès admin (vue complète):")
for name, email in admin_profiles:
    obj, created = AuditorAccess.objects.get_or_create(
        name=name,
        defaults={"email": email}
    )
    if not created and email and not obj.email:
        obj.email = email
        obj.save()
    status = "CREE" if created else "EXISTE"
    print(f"  {status} | {name:40} | {obj.token}")

# ── 3. Créer les accès division/direction personnalisés ──
division_profiles = [
    # Divisionnaires (voient toute la division + sous-directions)
    ("DAG",   "Mme la DAG",               ""),
    ("DC",    "BOUTEMADJA Samy",           "boutemadja.samy@airalgerie.dz"),
    ("DIVEX", "BENBOUAZIZ Lyes",           "benbouaziz.lyes@airalgerie.dz"),
    ("DMRA",  "HACHELAF Mourad",           "hachelaf.mourad@airalgerie.dz"),
    # Directeurs (voient leur direction)
    ("DRH",   "KRAIMECHE Abdelkrim",       "kraimeche.abdelkrim@airalgerie.dz"),
    ("DSI",   "DEBAB",                     ""),
    ("DSI",   "MERDACI Adel",              "merdaci.adel@airalgerie.dz"),
    ("DVR",   "BOUNAB Nihad",              "bounab.nihad@airalgerie.dz"),
    ("DRM",   "FAIDI Fouad",               "faidi.fouad@airalgerie.dz"),
    ("DFC",   "KHELFI Redouane",           "khelfi.redouane@airalgerie.dz"),
    ("DOA",   "BENBOUAZIZ Lyes (DOA)",     "benbouaziz.lyes@airalgerie.dz"),
]

print("\n[3/3] Accès division/direction:")
for code, name, email in division_profiles:
    struct = Structure.objects.get(code=code)
    obj = DivisionAccess.objects.create(structure=struct, name=name, email=email)
    print(f"  CREE | {code:6} | {name:30} | {obj.token}")

print("\n=== TERMINE ===")
print(f"Total accès admin:    {AuditorAccess.objects.count()}")
print(f"Total accès division: {DivisionAccess.objects.count()}")
