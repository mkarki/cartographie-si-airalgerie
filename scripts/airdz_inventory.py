"""Inventaire de toutes les occurrences AIRDZ dans la base locale, par champ.

Ne modifie rien. Sortie : un récapitulatif par table/colonne.
"""
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "db.sqlite3"
con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()

PATTERNS = ["AIRDZ", "AirDZ", "airdz"]

# Tables/colonnes à scanner
TARGETS = [
    ("cartography_process", ["code", "name", "description", "context", "problems", "recommendations"]),
    ("cartography_processstep", ["title", "description", "actor_role", "data_inputs", "data_outputs", "interactions", "problems", "next_steps"]),
    ("cartography_questionnaire", ["system_name", "key_users", "key_users_backup", "responsible", "interview_notes"]),
    ("cartography_questionsection", ["title"]),
    ("cartography_question", ["text", "answer", "notes"]),
    ("cartography_dataflow", ["name", "description"]),
    ("cartography_system", ["code", "name", "description", "vendor"]),
    ("cartography_structure", ["code", "name"]),
    ("cartography_processvalidation", ["comment"]),
    ("cartography_processstructurevalidation", ["comment"]),
    ("cartography_flowvalidation", ["comment"]),
    ("cartography_flowfieldhypothesis", ["comment"]),
]


def count_pattern(table, col, pattern):
    cur.execute(
        f"SELECT COUNT(*) FROM {table} WHERE {col} LIKE ?",
        (f"%{pattern}%",),
    )
    return cur.fetchone()[0]


print("=" * 80)
print("INVENTAIRE AIRDZ dans la base locale")
print("=" * 80)

total = 0
for table, cols in TARGETS:
    # vérifier que la table existe
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    if not cur.fetchone():
        continue
    table_total = 0
    table_lines = []
    for col in cols:
        # vérifier que la colonne existe
        cur.execute(f"PRAGMA table_info({table})")
        cols_info = [r["name"] for r in cur.fetchall()]
        if col not in cols_info:
            continue
        for p in PATTERNS:
            n = count_pattern(table, col, p)
            if n:
                table_lines.append(f"    {col:25s} | {p:6s} | {n} ligne(s)")
                table_total += n
    if table_lines:
        print(f"\n📋 {table} (total: {table_total})")
        for l in table_lines:
            print(l)
        total += table_total

print(f"\n{'=' * 80}")
print(f"TOTAL occurrences AIRDZ en base : {total}")
print("=" * 80)

# Détail des codes Process
print("\n--- Codes de process à renommer ---")
cur.execute(
    "SELECT id, code FROM cartography_process WHERE code LIKE 'PROC-AIRDZ-%' ORDER BY code"
)
codes = cur.fetchall()
print(f"Nombre de codes PROC-AIRDZ- : {len(codes)}")
print("Exemples :")
for r in codes[:10]:
    print(f"  {r['code']}")
if len(codes) > 10:
    print(f"  ... ({len(codes) - 10} autres)")

# Échantillon de textes
print("\n--- Échantillons de textes AIRDZ (process.context) ---")
cur.execute(
    "SELECT code, substr(context, 1, 200) as snippet FROM cartography_process WHERE context LIKE '%AIRDZ%' LIMIT 5"
)
for r in cur.fetchall():
    print(f"  [{r['code']}] {r['snippet']}")

con.close()
