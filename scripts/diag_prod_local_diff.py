"""Compte par champ les différences entre prod et local pour comprendre l'ampleur du sync."""
import json
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "db.sqlite3"
PROD_DIR = ROOT / "prod_data"

candidates = sorted(PROD_DIR.glob("answers_full_*.json"))
data = json.loads(candidates[-1].read_text(encoding="utf-8"))
rows = data["rows"]

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()
cur.execute(
    """SELECT q.id, q.number, q.is_answered, q.answer, q.notes,
              q.validation_status, q.validated_by, q.validated_at, q.validation_comment,
              q.auditor_comment, q.auditor_comment_by, q.auditor_comment_at,
              q.attachment_filename,
              qs.title as section_title,
              qn.system_name
       FROM cartography_question q
       JOIN cartography_questionsection qs ON q.section_id=qs.id
       JOIN cartography_questionnaire qn ON qs.questionnaire_id=qn.id"""
)
local_index = {(r["system_name"], r["section_title"], r["number"]): dict(r) for r in cur.fetchall()}

FIELDS = [
    "is_answered", "answer", "notes",
    "validation_status", "validated_by", "validated_at", "validation_comment",
    "auditor_comment", "auditor_comment_by", "auditor_comment_at",
    "attachment_filename",
]

field_diffs = Counter()
new_answers = 0  # réponses qui n'existaient pas en local
modif_answers = 0  # réponses modifiées
no_match = 0

for prod in rows:
    key = (prod["system_name"], prod["section_title"], prod["question_number"])
    if key not in local_index:
        no_match += 1
        continue
    loc = local_index[key]

    for f in FIELDS:
        pv = prod.get(f)
        lv = loc.get(f)
        # Normalisation
        if pv is True or pv == "t":
            pv_n = 1
        elif pv is False or pv == "f":
            pv_n = 0
        else:
            pv_n = pv if pv else ""
        lv_n = lv if lv not in (None, False) else (0 if lv is False else "")
        if isinstance(lv, int):
            lv_n = lv

        if pv_n != lv_n:
            field_diffs[f] += 1

    # Détail réponses
    pa = prod.get("answer") or ""
    la = loc.get("answer") or ""
    if pa and not la:
        new_answers += 1
    elif pa and la and pa != la:
        modif_answers += 1

print("=== Différences par champ (prod ≠ local) ===")
for f, n in field_diffs.most_common():
    print(f"  {f:25s} : {n}")

print(f"\nRéponses NOUVELLES (vide en local) : {new_answers}")
print(f"Réponses MODIFIÉES (différentes)   : {modif_answers}")
print(f"Questions non matchées             : {no_match}")
con.close()
