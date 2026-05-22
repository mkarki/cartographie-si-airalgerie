"""Renomme les 76 codes Process PROC-AIRDZ-XXX en PROC-AA-XXX dans la base locale.

La table cartography_process a `code` UNIQUE. SQLite gère bien le rename via UPDATE
direct (pas de FK sur cette colonne).

Usage : python scripts/airdz_rename_codes.py [--dry-run]
"""
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

DB = Path(__file__).resolve().parent.parent / "db.sqlite3"
DRY_RUN = "--dry-run" in sys.argv

OLD_PREFIX = "PROC-AIRDZ-"
NEW_PREFIX = "PROC-AA-"

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()

print("=" * 80)
print(f"Renommage codes Process  ({'DRY-RUN' if DRY_RUN else 'EXECUTION'})")
print(f"DB : {DB}")
print(f"Date : {datetime.now().isoformat()}")
print("=" * 80)

# Vérifier qu'aucun PROC-AA- n'existe déjà (sinon collision)
cur.execute(f"SELECT code FROM cartography_process WHERE code LIKE '{NEW_PREFIX}%'")
existing = cur.fetchall()
if existing:
    print(f"⚠️  ATTENTION : {len(existing)} codes commençant par {NEW_PREFIX} existent déjà :")
    for r in existing[:5]:
        print(f"  {r['code']}")
    print("Annulation pour éviter une collision.")
    sys.exit(1)

# Inventaire avant
cur.execute(
    f"SELECT id, code FROM cartography_process WHERE code LIKE '{OLD_PREFIX}%' ORDER BY code"
)
to_rename = cur.fetchall()
print(f"\n{len(to_rename)} codes à renommer.")

try:
    cur.execute("BEGIN")
    n = 0
    for r in to_rename:
        old_code = r["code"]
        new_code = NEW_PREFIX + old_code[len(OLD_PREFIX):]
        cur.execute(
            "UPDATE cartography_process SET code=? WHERE id=?",
            (new_code, r["id"]),
        )
        n += 1
        if n <= 5 or n % 20 == 0:
            print(f"  {old_code:40s} → {new_code}")

    print(f"\nTotal renommé : {n}")

    # Vérification
    cur.execute(f"SELECT COUNT(*) FROM cartography_process WHERE code LIKE '{OLD_PREFIX}%'")
    remaining = cur.fetchone()[0]
    cur.execute(f"SELECT COUNT(*) FROM cartography_process WHERE code LIKE '{NEW_PREFIX}%'")
    new_count = cur.fetchone()[0]
    print(f"Restant {OLD_PREFIX}* : {remaining}")
    print(f"Nouveaux {NEW_PREFIX}* : {new_count}")

    if DRY_RUN:
        con.rollback()
        print("\n⚠️  DRY-RUN — rollback effectué.")
    else:
        con.commit()
        print("\n✅ COMMIT.")
except Exception as e:
    con.rollback()
    print(f"\n❌ Erreur : {e}")
    raise
finally:
    con.close()
