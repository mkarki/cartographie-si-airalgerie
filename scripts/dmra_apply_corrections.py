"""Applique les corrections DMRA en local (db.sqlite3) suite à l'entretien
collégial du 12/04/2026 et au questionnaire AMOS rempli par M. BOUGUEZIZ.

Modifications :
1. Création du système ERP-AH (ERP Air Algérie côté DZ, DFC).
2. Redirection du flux F-83 (AMOS → SAGE-FIN) vers ERP-AH avec description enrichie
   (contexte 2025 : abandon de l'ancien système au profit d'AMOS).
3. Renommage et reformulation du flux F-4 (AMOS → AIMS) :
   "Prévisions immobilisation + Pannes limitantes" → "Prévisions d'immobilisation
   maintenance" (les pannes limitantes sont marquées comme hypothèse à reconfirmer).

Tout est exécuté dans une transaction unique. En cas d'erreur, rollback complet.

Usage : python scripts/dmra_apply_corrections.py [--dry-run]
"""
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

DB = Path(__file__).resolve().parent.parent / "db.sqlite3"
DRY_RUN = "--dry-run" in sys.argv

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()


def fetch_one(sql, params=()):
    cur.execute(sql, params)
    return cur.fetchone()


def show_diff(label, before, after):
    print(f"\n  {label}")
    after_keys = after.keys() if after else []
    before_keys = before.keys() if before else []
    for k in after_keys:
        b = before[k] if k in before_keys else None
        a = after[k]
        marker = "≠" if b != a else "="
        b_disp = (str(b)[:120] + "...") if b and len(str(b)) > 120 else b
        a_disp = (str(a)[:120] + "...") if a and len(str(a)) > 120 else a
        print(f"    {marker} {k}: {b_disp!r}")
        if b != a:
            print(f"        → {a_disp!r}")


print("=" * 80)
print(f"DMRA — Corrections cartographie locale  ({'DRY-RUN' if DRY_RUN else 'EXECUTION'})")
print(f"DB : {DB}")
print(f"Date : {datetime.now().isoformat()}")
print("=" * 80)

try:
    cur.execute("BEGIN")

    # ----- 1. ERP-AH -----
    print("\n[1/3] Système ERP-AH (Air Algérie / DZ / DFC)")

    existing = fetch_one("SELECT id, code, name FROM cartography_system WHERE code='ERP-AH'")
    if existing:
        print(f"  → existe déjà : id={existing['id']} (aucune création)")
        erp_ah_id = existing["id"]
    else:
        cur.execute(
            """INSERT INTO cartography_system
               (code, name, description, vendor, criticality, mode,
                is_master_for, version, modules, category_id, structure_id, country)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                "ERP-AH",
                "ERP Air Algérie (Comptabilité)",
                (
                    "ERP comptable d'Air Algérie côté Algérie (DZ). Reçoit depuis 2025 "
                    "les valorisations de stock pièces depuis AMOS, suite à l'abandon de "
                    "l'ancien système de valorisation comptable. Système identifié par "
                    "la DMRA lors de l'entretien du 12/04/2026 — éditeur, version et "
                    "modules à compléter avec la DFC."
                ),
                "À préciser (DFC)",
                "HAUTE",
                "ONPREMISE",
                "",
                "",
                "[]",
                3,   # Finance & Comptabilité
                20,  # DFC
                "DZ",
            ),
        )
        erp_ah_id = cur.lastrowid
        print(f"  ✅ créé : id={erp_ah_id}")

    # ----- 2. Flux F-83 : redirection AMOS → ERP-AH -----
    print("\n[2/3] Flux F-83 (AMOS → stock/valorisation des pièces)")

    f83_before = fetch_one(
        """SELECT f.id, f.name, f.description, f.frequency, f.protocol, f.is_critical,
                  f.source_id, f.target_id, src.code as source_code, tgt.code as target_code
           FROM cartography_dataflow f
           JOIN cartography_system src ON f.source_id=src.id
           JOIN cartography_system tgt ON f.target_id=tgt.id
           WHERE f.id=83"""
    )

    new_f83_desc = (
        "Stock et valorisation des pièces de rechange transmis depuis AMOS vers "
        "l'ERP comptable d'Air Algérie. Mis en place en 2025 suite à l'abandon de "
        "l'ancien système de valorisation comptable des stocks pièces (la valorisation "
        "est désormais réalisée nativement dans AMOS). Confirmé par la DMRA lors de "
        "l'entretien du 12/04/2026."
    )

    cur.execute(
        """UPDATE cartography_dataflow
           SET target_id=?, description=?
           WHERE id=83""",
        (erp_ah_id, new_f83_desc),
    )

    f83_after = fetch_one(
        """SELECT f.id, f.name, f.description, f.frequency, f.is_critical,
                  src.code as source_code, tgt.code as target_code
           FROM cartography_dataflow f
           JOIN cartography_system src ON f.source_id=src.id
           JOIN cartography_system tgt ON f.target_id=tgt.id
           WHERE f.id=83"""
    )
    show_diff("F-83 avant/après", f83_before, f83_after)

    # ----- 3. Flux F-4 : renommage + clarification -----
    print("\n[3/3] Flux F-4 (AMOS → AIMS)")

    f4_before = fetch_one(
        """SELECT f.id, f.name, f.description, f.frequency, f.is_critical,
                  src.code as source_code, tgt.code as target_code
           FROM cartography_dataflow f
           JOIN cartography_system src ON f.source_id=src.id
           JOIN cartography_system tgt ON f.target_id=tgt.id
           WHERE f.id=4"""
    )

    new_f4_name = "Prévisions d'immobilisation maintenance"
    new_f4_desc = (
        "Prévisions d'immobilisation de la flotte pour maintenance, transmises depuis "
        "AMOS vers AIMS pour ajustement de la planification des vols. Confirmé en "
        "entretien DMRA du 12/04/2026 (M. ROUKISSI : 'AMOS donne à AIMS les prévisions "
        "d'immobilisation de la flotte pour maintenance'). "
        "HYPOTHÈSE COMPLÉMENTAIRE — Enrichissement futur potentiel : remontée "
        "additionnelle des pannes non-immobilisantes mais limitantes pour l'exploitation "
        "(ex : limitation RVSM empêchant certaines destinations). À reconfirmer avec "
        "DMRA + DOA + CCO avant inscription au backlog Phase 2."
    )

    cur.execute(
        "UPDATE cartography_dataflow SET name=?, description=? WHERE id=4",
        (new_f4_name, new_f4_desc),
    )

    f4_after = fetch_one(
        """SELECT f.id, f.name, f.description, f.frequency, f.is_critical,
                  src.code as source_code, tgt.code as target_code
           FROM cartography_dataflow f
           JOIN cartography_system src ON f.source_id=src.id
           JOIN cartography_system tgt ON f.target_id=tgt.id
           WHERE f.id=4"""
    )
    show_diff("F-4 avant/après", f4_before, f4_after)

    # ----- Commit ou rollback -----
    if DRY_RUN:
        con.rollback()
        print("\n⚠️  DRY-RUN — rollback effectué, aucune modification persistée.")
    else:
        con.commit()
        print("\n✅ COMMIT — corrections appliquées.")

except Exception as e:
    con.rollback()
    print(f"\n❌ Erreur : {e}")
    raise
finally:
    con.close()

# ----- Vérification post-mortem -----
print("\n" + "=" * 80)
print("Vérification finale (lecture indépendante)")
print("=" * 80)
con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()
cur.execute(
    """SELECT f.id, f.name, src.code as src, tgt.code as tgt
       FROM cartography_dataflow f
       JOIN cartography_system src ON f.source_id=src.id
       JOIN cartography_system tgt ON f.target_id=tgt.id
       WHERE f.source_id=6 OR f.target_id=6
       ORDER BY f.id"""
)
print("\nFlux AMOS :")
for r in cur.fetchall():
    print(f"  F-{r['id']:3d} | {r['src']:8s} → {r['tgt']:8s} | {r['name']}")

cur.execute("SELECT id, code, name FROM cartography_system WHERE code='ERP-AH'")
r = cur.fetchone()
if r:
    print(f"\nERP-AH : id={r['id']} | code={r['code']} | name={r['name']}")
con.close()
