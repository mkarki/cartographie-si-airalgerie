"""Extrait toutes les informations DC (Division Commerciale) depuis la base locale.

Périmètre DC = DC (id=2) + DRM (id=26) + DVR (id=27).

Génère un JSON consolidé pour servir de source au dossier de restitution DC.
Usage : python scripts/restitution_dc_extract.py
"""
import json
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "db.sqlite3"
OUT = Path(__file__).resolve().parent.parent / "LIVRABLES_PHASE_1" / "Restitutions_Directions" / "_data_dc.json"

STRUCTURE_IDS = (2, 26, 27)  # DC, DRM, DVR
STRUCTURE_IDS_STR = ",".join(str(i) for i in STRUCTURE_IDS)

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()


def rows(sql, params=()):
    cur.execute(sql, params)
    return [dict(r) for r in cur.fetchall()]


data = {}

# 1. Structures (DC + enfants)
data["structures"] = rows(
    f"SELECT id, code, name, parent_id FROM cartography_structure "
    f"WHERE id IN ({STRUCTURE_IDS_STR}) ORDER BY id"
)

# 2. Systèmes rattachés aux structures DC
data["systems"] = rows(
    f"""SELECT s.id, s.code, s.name, s.description, s.vendor, s.criticality, s.mode,
               s.version, s.country, s.modules, sc.name as category,
               st.code as structure_code
        FROM cartography_system s
        JOIN cartography_systemcategory sc ON s.category_id=sc.id
        JOIN cartography_structure st ON s.structure_id=st.id
        WHERE s.structure_id IN ({STRUCTURE_IDS_STR})
        ORDER BY st.code, s.name"""
)
sys_ids = [s["id"] for s in data["systems"]]
sys_ids_str = ",".join(str(i) for i in sys_ids) or "0"

# 3. Flux impliquant ces systèmes (entrants ou sortants)
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
    f"""SELECT q.id, q.system_name, q.phase, q.priority_in_phase, q.direction,
               q.editor, q.key_users, q.key_users_backup, q.responsible, q.status,
               q.interview_date, q.interview_notes
        FROM cartography_questionnaire q
        JOIN cartography_system s ON q.system_id=s.id
        WHERE s.structure_id IN ({STRUCTURE_IDS_STR})
        ORDER BY q.system_name"""
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

# 7. Process (DISTINCT car un process peut être rattaché à plusieurs structures DC)
data["processes"] = rows(
    f"""SELECT DISTINCT p.id, p.code, p.name, p.description, p.context, p.category,
               p.status, p.problems, p.recommendations, p.validation_status,
               p.validated_by, p.validated_at, p.created_by, p.created_at
        FROM cartography_process p
        JOIN cartography_process_structures ps ON p.id=ps.process_id
        WHERE ps.structure_id IN ({STRUCTURE_IDS_STR})
        ORDER BY p.code"""
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
    # Structures impliquées pour chaque process
    p["structures"] = rows(
        """SELECT st.code, st.name
           FROM cartography_process_structures ps
           JOIN cartography_structure st ON ps.structure_id=st.id
           WHERE ps.process_id=?""",
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
    "perimetre": "DC + DRM + DVR (structure_ids 2, 26, 27)",
    "nb_systemes": len(data["systems"]),
    "nb_flux": len(data["flows"]),
    "nb_questionnaires": len(data["questionnaires"]),
    "nb_questionnaires_completed": sum(
        1 for q in data["questionnaires"] if q["status"] == "COMPLETED"
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
print("\n--- Structures DC ---")
for s in data["structures"]:
    print(f"  {s['code']:8s} | {s['name']} | parent={s['parent_id']}")
print("\n--- Systèmes ---")
for s in data["systems"]:
    print(f"  {s['code']:14s} | {s['structure_code']:5s} | {s['name']} | {s['vendor']} | {s['criticality']}")
print("\n--- Questionnaires ---")
for q in data["questionnaires"]:
    print(f"  Q{q['id']:3d} | {q['system_name']:30s} | phase {q['phase']} | {q['status']:12s} | KU: {(q['key_users'] or '')[:50]}")
print("\n--- Process ---")
for p in data["processes"]:
    structs = ", ".join(s["code"] for s in p["structures"])
    print(f"  {p['code']:18s} | [{structs:15s}] | {p['name'][:60]} | {len(p['steps'])} étapes")
print("\n--- Key users ---")
for k in data["key_users"]:
    print(f"  {k['name']:30s} | {k['system_name']:30s} | actif={k['is_active']}")
print("\n--- Flux (échantillon) ---")
for f in data["flows"][:20]:
    print(f"  F{f['id']:3d} | {f['source_code']:14s} -> {f['target_code']:14s} | {f['name'][:70]}")
if len(data["flows"]) > 20:
    print(f"  ... ({len(data['flows']) - 20} autres)")
