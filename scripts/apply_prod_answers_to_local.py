"""Applique les réponses prod (export JSON) sur la base locale db.sqlite3.

Matching par identifiants stables (questionnaire.system_name + section_title +
question.number) — indépendant des IDs autoincrement.

Stratégie :
- Pour chaque ligne prod, on tente de matcher la question locale.
- Si match et la valeur diffère, on UPDATE en local (la prod fait foi).
- Si pas de match, on logue (warning) et on continue.
- Tout est dans une transaction unique.

Usage : python scripts/apply_prod_answers_to_local.py [--dry-run] [--input <file.json>]
"""
import json
import sys
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "db.sqlite3"
PROD_DIR = ROOT / "prod_data"

DRY_RUN = "--dry-run" in sys.argv

# Trouver le dernier export
input_path = None
if "--input" in sys.argv:
    input_path = Path(sys.argv[sys.argv.index("--input") + 1])
else:
    candidates = sorted(PROD_DIR.glob("answers_full_*.json"))
    if not candidates:
        print("Aucun export trouvé dans prod_data/answers_full_*.json")
        sys.exit(1)
    input_path = candidates[-1]

print(f"=== Apply prod answers to local  ({'DRY-RUN' if DRY_RUN else 'EXECUTION'}) ===")
print(f"Source : {input_path.name}")
data = json.loads(input_path.read_text(encoding="utf-8"))
rows = data["rows"]
print(f"Lignes prod : {len(rows)}")

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()


def normalize(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return v
    return str(v)


# Index local : (system_name, section_title, question.number) → question row
local_index = {}
cur.execute(
    """SELECT q.id, q.number, q.is_answered, q.answer, q.notes,
              q.validation_status, q.validated_by, q.validated_at, q.validation_comment,
              q.auditor_comment, q.auditor_comment_by, q.auditor_comment_at,
              q.attachment_filename, q.attachment_size,
              qs.title as section_title, qs."order" as section_order,
              qn.system_name
       FROM cartography_question q
       JOIN cartography_questionsection qs ON q.section_id=qs.id
       JOIN cartography_questionnaire qn ON qs.questionnaire_id=qn.id"""
)
for r in cur.fetchall():
    key = (r["system_name"], r["section_title"], r["number"])
    local_index[key] = dict(r)

print(f"Lignes locales indexées : {len(local_index)}")

# Champs à propager (clé prod → clé locale + parser)
FIELDS = [
    ("is_answered", "is_answered", lambda v: 1 if v in (True, "t", "true", 1) else 0),
    ("answer", "answer", lambda v: v or ""),
    ("notes", "notes", lambda v: v or ""),
    ("validation_status", "validation_status", lambda v: v or "PENDING"),
    ("validated_by", "validated_by", lambda v: v or ""),
    ("validated_at", "validated_at", lambda v: v or None),
    ("validation_comment", "validation_comment", lambda v: v or ""),
    ("auditor_comment", "auditor_comment", lambda v: v or ""),
    ("auditor_comment_by", "auditor_comment_by", lambda v: v or ""),
    ("auditor_comment_at", "auditor_comment_at", lambda v: v or None),
    ("attachment_filename", "attachment_filename", lambda v: v or ""),
]

stats = {
    "matched": 0,
    "updated": 0,
    "no_match": 0,
    "unchanged": 0,
}
not_matched_examples = []
updates_examples = []

try:
    cur.execute("BEGIN")
    for prod_r in rows:
        key = (prod_r["system_name"], prod_r["section_title"], prod_r["question_number"])
        if key not in local_index:
            stats["no_match"] += 1
            if len(not_matched_examples) < 10:
                not_matched_examples.append(key)
            continue
        stats["matched"] += 1
        local_r = local_index[key]

        # Construire l'UPDATE pour les champs qui diffèrent
        updates = {}
        for prod_key, local_key, parser in FIELDS:
            new_val = parser(prod_r.get(prod_key))
            old_val = local_r.get(local_key)
            # normalisation pour comparaison
            if normalize(new_val) != normalize(old_val):
                updates[local_key] = new_val

        if not updates:
            stats["unchanged"] += 1
            continue

        if len(updates_examples) < 5:
            updates_examples.append({
                "key": key,
                "diff": {k: {"old": local_r.get(k), "new": v} for k, v in updates.items()},
            })

        if not DRY_RUN:
            cols = ", ".join(f'"{k}"=?' for k in updates)
            cur.execute(
                f"UPDATE cartography_question SET {cols} WHERE id=?",
                list(updates.values()) + [local_r["id"]],
            )
        stats["updated"] += 1

    if DRY_RUN:
        con.rollback()
        print("\n⚠️  DRY-RUN — rollback")
    else:
        con.commit()
        print("\n✅ COMMIT")

except Exception as e:
    con.rollback()
    print(f"❌ Erreur : {e}")
    raise
finally:
    con.close()

print(f"\n=== Stats ===")
for k, v in stats.items():
    print(f"  {k:12s} : {v}")

if not_matched_examples:
    print(f"\n--- Échantillons NON MATCHÉS (premières {len(not_matched_examples)}) ---")
    for k in not_matched_examples:
        print(f"  {k}")

if updates_examples:
    print(f"\n--- Échantillons d'UPDATE ({len(updates_examples)}) ---")
    for u in updates_examples:
        print(f"  {u['key']}")
        for fld, vals in u["diff"].items():
            old = (str(vals['old']) or '')[:60]
            new = (str(vals['new']) or '')[:60]
            print(f"    {fld:25s} : {old!r} → {new!r}")
