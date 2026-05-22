"""Exporte toutes les réponses des questionnaires prod via SSH/psql vers JSON local.

Utilise des identifiants stables (questionnaire.system_name + section.title +
question.number) pour permettre un merge ultérieur indépendant des IDs.

Usage : python scripts/fetch_prod_answers.py
Sortie : prod_data/answers_full_<timestamp>.json
"""
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "prod_data"
OUT_DIR.mkdir(exist_ok=True)

TS = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
OUT_FILE = OUT_DIR / f"answers_full_{TS}.json"
RAW_FILE = OUT_DIR / f"answers_raw_{TS}.tsv"

# Requête : toutes les questions avec leur contexte stable + réponse + métadonnées
SQL = """
COPY (
SELECT
    qn.system_name,
    qs.title          AS section_title,
    qs."order"        AS section_order,
    q.number          AS question_number,
    q."order"         AS question_order,
    q.text            AS question_text,
    q.is_answered,
    q.answer,
    q.notes,
    q.validation_status,
    q.validated_by,
    q.validated_at,
    q.validation_comment,
    q.auditor_comment,
    q.auditor_comment_by,
    q.auditor_comment_at,
    q.attachment_filename,
    q.attachment_size,
    q.attachment_uploaded_at
FROM cartography_question q
JOIN cartography_questionsection qs ON q.section_id = qs.id
JOIN cartography_questionnaire qn ON qs.questionnaire_id = qn.id
ORDER BY qn.system_name, qs."order", q."order"
) TO STDOUT WITH CSV HEADER DELIMITER E'\\t' NULL '\\\\N';
"""

print(f"Export prod via SSH/psql → {RAW_FILE}")

# Encoder le SQL via base64 ou heredoc serait mieux, mais pour aller vite on l'envoie en stdin
result = subprocess.run(
    ["ssh", "airalgerie-vps",
     "sudo -u postgres psql cartographie_si -c \"" + SQL.replace("\n", " ").strip() + "\""],
    capture_output=True, text=True, timeout=120,
)
if result.returncode != 0:
    print("ERREUR ssh/psql :")
    print(result.stderr)
    raise SystemExit(1)

# La sortie contient le COPY directement (pas besoin de l'extraire d'un wrapper)
RAW_FILE.write_text(result.stdout, encoding="utf-8")
print(f"Lignes brutes : {len(result.stdout.splitlines())}")

# Parse TSV
import csv
import io

reader = csv.DictReader(io.StringIO(result.stdout), delimiter="\t")
rows = []
for r in reader:
    # Normalise les NULL psql
    for k, v in list(r.items()):
        if v == "\\N":
            r[k] = None
        elif v == "t":
            r[k] = True
        elif v == "f":
            r[k] = False
    rows.append(r)

# Stats
total = len(rows)
answered = sum(1 for r in rows if r.get("is_answered") in (True, "t"))
with_attachment = sum(1 for r in rows if r.get("attachment_filename"))

print(f"\nQuestions au total : {total}")
print(f"  - répondues : {answered}")
print(f"  - avec pièce jointe : {with_attachment}")

# Stats par questionnaire
by_q = {}
for r in rows:
    sn = r["system_name"]
    by_q.setdefault(sn, {"total": 0, "answered": 0})
    by_q[sn]["total"] += 1
    if r.get("is_answered"):
        by_q[sn]["answered"] += 1

print("\n--- Par questionnaire (TOP 10 par réponses) ---")
for sn, c in sorted(by_q.items(), key=lambda x: -x[1]["answered"])[:10]:
    print(f"  {sn:35s} : {c['answered']:3d}/{c['total']:3d} répondues")

# Sortie JSON
OUT_FILE.write_text(
    json.dumps(
        {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "source": "airalgerie-vps:cartographie_si",
            "total_questions": total,
            "answered_count": answered,
            "rows": rows,
        },
        ensure_ascii=False,
        indent=2,
        default=str,
    ),
    encoding="utf-8",
)
print(f"\n✅ Export JSON : {OUT_FILE}")
print(f"   Taille : {OUT_FILE.stat().st_size} octets")
