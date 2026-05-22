"""Extrait toutes les informations DMRA (structure_id=9) depuis la base locale.
Génère un JSON consolidé pour servir de source au dossier de restitution.
Usage : python scripts/restitution_dmra_extract.py
"""
import json
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "db.sqlite3"
OUT = Path(__file__).resolve().parent.parent / "LIVRABLES_PHASE_1" / "Restitutions_Directions" / "_data_dmra.json"

STRUCTURE_ID = 9  # DMRA

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()


def rows(sql, params=()):
    cur.execute(sql, params)
    return [dict(r) for r in cur.fetchall()]


data = {}

# 1. Structure
data["structure"] = rows("SELECT id, code, name, parent_id FROM cartography_structure WHERE id=?", (STRUCTURE_ID,))[0]

# 2. Systèmes
data["systems"] = rows(
    """SELECT s.id, s.code, s.name, s.description, s.vendor, s.criticality, s.mode,
              s.version, s.country, sc.name as category
       FROM cartography_system s
       JOIN cartography_systemcategory sc ON s.category_id=sc.id
       WHERE s.structure_id=?
       ORDER BY s.name""",
    (STRUCTURE_ID,),
)
sys_ids = [s["id"] for s in data["systems"]]
sys_ids_str = ",".join(str(i) for i in sys_ids) or "0"

# 3. Flux impliquant ces systèmes
data["flows"] = rows(
    f"""SELECT f.id, f.name, f.description, f.frequency, f.protocol, f.format,
               f.is_automated, f.is_critical, f.volume,
               src.code as source_code, src.name as source_name,
               tgt.code as target_code, tgt.name as target_name
        FROM cartography_dataflow f
        JOIN cartography_system src ON f.source_id=src.id
        JOIN cartography_system tgt ON f.target_id=tgt.id
        WHERE f.source_id IN ({sys_ids_str}) OR f.target_id IN ({sys_ids_str})
        ORDER BY f.name"""
)

# 4. Questionnaires
data["questionnaires"] = rows(
    """SELECT q.id, q.system_name, q.phase, q.priority_in_phase, q.direction,
              q.editor, q.key_users, q.key_users_backup, q.responsible, q.status,
              q.interview_date, q.interview_notes
       FROM cartography_questionnaire q
       JOIN cartography_system s ON q.system_id=s.id
       WHERE s.structure_id=?
       ORDER BY q.system_name""",
    (STRUCTURE_ID,),
)

# 5. Sections + questions + réponses par questionnaire
for q in data["questionnaires"]:
    q["sections"] = rows(
        """SELECT id, title, "order" as ord
           FROM cartography_questionsection
           WHERE questionnaire_id=?
           ORDER BY "order" """,
        (q["id"],),
    )
    for sec in q["sections"]:
        sec["questions"] = rows(
            """SELECT id, "order" as ord, number, text, is_answered, answer, notes,
                      validation_status, attachment_filename
               FROM cartography_question
               WHERE section_id=?
               ORDER BY "order" """,
            (sec["id"],),
        )

# 6. Key users
qids = [q["id"] for q in data["questionnaires"]]
qids_str = ",".join(str(i) for i in qids) or "0"
data["key_users"] = rows(
    f"""SELECT k.id, k.name, k.email, k.is_active, k.last_accessed, k.created_at,
               q.system_name
        FROM cartography_keyuseraccess k
        JOIN cartography_questionnaire q ON k.questionnaire_id=q.id
        WHERE k.questionnaire_id IN ({qids_str})
        ORDER BY q.system_name, k.name"""
)

# 7. Process
data["processes"] = rows(
    """SELECT DISTINCT p.id, p.code, p.name, p.description, p.context, p.category,
              p.status, p.problems, p.recommendations, p.validation_status,
              p.validated_by, p.validated_at, p.created_by, p.created_at
       FROM cartography_process p
       JOIN cartography_process_structures ps ON p.id=ps.process_id
       WHERE ps.structure_id=?
       ORDER BY p.code""",
    (STRUCTURE_ID,),
)
for p in data["processes"]:
    p["steps"] = rows(
        """SELECT id, "order" as ord, title, description, step_type, actor_role,
                  data_inputs, data_outputs, interactions, problems, duration_estimate
           FROM cartography_processstep
           WHERE process_id=?
           ORDER BY "order" """,
        (p["id"],),
    )

# 8. KPI synthèse
total_q = sum(len(s["questions"]) for q in data["questionnaires"] for s in q["sections"])
answered = sum(
    1
    for q in data["questionnaires"]
    for s in q["sections"]
    for qu in s["questions"]
    if qu["is_answered"]
)
data["kpi"] = {
    "nb_systemes": len(data["systems"]),
    "nb_flux": len(data["flows"]),
    "nb_questionnaires": len(data["questionnaires"]),
    "nb_questionnaires_completed": sum(
        1 for q in data["questionnaires"] if q["status"] == "completed"
    ),
    "nb_questions_total": total_q,
    "nb_questions_repondues": answered,
    "taux_completion_pct": round(100 * answered / total_q, 1) if total_q else 0,
    "nb_key_users": len(data["key_users"]),
    "nb_processes": len(data["processes"]),
    "nb_process_steps": sum(len(p["steps"]) for p in data["processes"]),
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

print(f"OK -> {OUT}")
print(json.dumps(data["kpi"], ensure_ascii=False, indent=2))
print("\n--- Systèmes ---")
for s in data["systems"]:
    print(f"  {s['code']:12s} | {s['name']} | {s['vendor']} | {s['criticality']}")
print("\n--- Questionnaires ---")
for q in data["questionnaires"]:
    print(f"  Q{q['id']:3d} | {q['system_name']:25s} | phase {q['phase']} | {q['status']} | KU: {q['key_users'][:60]}")
print("\n--- Process ---")
for p in data["processes"]:
    print(f"  {p['code']} | {p['name']} | {p['status']} | {len(p['steps'])} étapes")
print("\n--- Key users ---")
for k in data["key_users"]:
    print(f"  {k['name']:30s} | {k['system_name']:25s} | actif={k['is_active']}")
print("\n--- Flux ---")
for f in data["flows"]:
    print(f"  F{f['id']:3d} | {f['source_code']:8s} -> {f['target_code']:8s} | {f['name']}")
