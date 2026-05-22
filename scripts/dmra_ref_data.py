"""Affiche catégories, SAGE-FIN, BODET et structure DFC pour calibrer ERP-AH."""
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "db.sqlite3"
con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()


def show(title, sql, params=()):
    print(f"\n=== {title} ===")
    cur.execute(sql, params)
    for r in cur.fetchall():
        print("  " + " | ".join(f"{k}={r[k]}" for k in r.keys()))


show(
    "Systèmes Finance/Compta de référence",
    """SELECT s.id, s.code, s.name, s.vendor, s.criticality, s.mode, s.country,
              s.category_id, s.structure_id, sc.name as category, st.code as struct
       FROM cartography_system s
       JOIN cartography_systemcategory sc ON s.category_id=sc.id
       JOIN cartography_structure st ON s.structure_id=st.id
       WHERE s.code IN ('SAGE-FIN','SAGE-STOCK','BODET','ACCELYA')""",
)

show("Catégories existantes", "SELECT id, name FROM cartography_systemcategory ORDER BY id")

show("Structure DFC + DAGP", "SELECT id, code, name FROM cartography_structure WHERE code IN ('DFC','DAGP','DAG')")

con.close()
