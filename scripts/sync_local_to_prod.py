"""Sync chirurgical local → prod (PostgreSQL via SSH).

Ne touche PAS aux questionnaires/sections/questions/réponses (déjà ISO).

Phases :
  1. Créer le système ERP-AH en prod.
  2. UPDATE flux F-4 (id=4) et F-83 (id=83) avec leurs nouveaux name/description/target.
  3. INSERT les 12 nouveaux flux ALTEA + JETPLAN→SKYBOOK + AMOS→ERP-AH.
  4. INSERT les 76 process PROC-AA-* + leurs ProcessSteps + relations M2M
     (process_structures, process_systems) — matching par code des structures/systèmes.

Skip (pour éviter les doublons fonctionnels) :
  - 4 process locaux à code custom dont la prod a déjà l'équivalent.
  - Questionnaires Altéa splittés (à traiter séparément si demandé).

Sécurité :
  - Backup pg_dump prod déjà fait (étape précédente).
  - Mode --dry-run par défaut.
  - Tout en transaction unique côté prod.
  - Génère un fichier SQL .out qu'on inspecte avant exécution.

Usage :
    python scripts/sync_local_to_prod.py            # dry-run + génération SQL
    python scripts/sync_local_to_prod.py --apply    # exécution effective
"""
import json
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "db.sqlite3"
OUT_DIR = ROOT / "prod_data"
TS = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

APPLY = "--apply" in sys.argv

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()


# ---------------------------------------------------------------- Helpers
def psql_one(sql):
    """Exécute du SQL en prod et renvoie la première ligne (ou None)."""
    r = subprocess.run(
        ["ssh", "airalgerie-vps",
         f"sudo -u postgres psql cartographie_si -At -F$'\\t' -c \"{sql}\""],
        capture_output=True, text=True, timeout=60,
    )
    if r.returncode != 0:
        raise RuntimeError(f"psql err: {r.stderr}")
    line = r.stdout.strip()
    return line.split("\t") if line else None


def psql_many(sql):
    r = subprocess.run(
        ["ssh", "airalgerie-vps",
         f"sudo -u postgres psql cartographie_si -At -F$'\\t' -c \"{sql}\""],
        capture_output=True, text=True, timeout=120,
    )
    if r.returncode != 0:
        raise RuntimeError(f"psql err: {r.stderr}")
    return [l.split("\t") for l in r.stdout.strip().split("\n") if l.strip()]


def sql_lit(v):
    """Littéral SQL (string-quoted ou NULL ou int/bool)."""
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v).replace("\\", "\\\\").replace("'", "''")
    return f"E'{s}'"


# ---------------------------------------------------------------- Index prod (codes → ids)
print("=== Lecture des index prod (structures, systèmes, catégories) ===")
prod_struct_by_code = {r[1]: int(r[0]) for r in psql_many(
    "SELECT id, code FROM cartography_structure"
)}
prod_sys_by_code = {r[1]: int(r[0]) for r in psql_many(
    "SELECT id, code FROM cartography_system"
)}
prod_cat_by_name = {r[1]: int(r[0]) for r in psql_many(
    "SELECT id, name FROM cartography_systemcategory"
)}
print(f"  Structures: {len(prod_struct_by_code)} | Systèmes: {len(prod_sys_by_code)} | Catégories: {len(prod_cat_by_name)}")

# Lecture local : structures et systèmes par code (pour mapper)
local_struct_by_id = {r["id"]: r["code"] for r in cur.execute("SELECT id, code FROM cartography_structure")}
local_sys_by_id = {r["id"]: r["code"] for r in cur.execute("SELECT id, code FROM cartography_system")}
local_cat_by_id = {r["id"]: r["name"] for r in cur.execute("SELECT id, name FROM cartography_systemcategory")}

# Vérifier que tous les codes locaux existent en prod
missing_struct = [c for c in local_struct_by_id.values() if c not in prod_struct_by_code]
missing_sys = [c for c in local_sys_by_id.values() if c not in prod_sys_by_code and c != "ERP-AH"]
missing_cat = [n for n in local_cat_by_id.values() if n not in prod_cat_by_name]
if missing_struct or missing_sys or missing_cat:
    print(f"⚠️  Code(s) absent(s) en prod :")
    if missing_struct: print(f"  Structures: {missing_struct}")
    if missing_sys:    print(f"  Systèmes  : {missing_sys}")
    if missing_cat:    print(f"  Catégories: {missing_cat}")

# ---------------------------------------------------------------- Construction du SQL
sql_chunks = []
sql_chunks.append("-- =====================================================")
sql_chunks.append(f"-- Sync local → prod  ({TS})")
sql_chunks.append("-- =====================================================")
sql_chunks.append("BEGIN;")
sql_chunks.append("")

# ---- Phase 1 : ERP-AH
print("\n=== Phase 1 : Création ERP-AH ===")
local_erp = cur.execute(
    "SELECT * FROM cartography_system WHERE code='ERP-AH'"
).fetchone()
if not local_erp:
    print("  ERP-AH absent en local — skip")
else:
    cat_id = prod_cat_by_name[local_cat_by_id[local_erp["category_id"]]]
    struct_code = local_struct_by_id[local_erp["structure_id"]]
    struct_id = prod_struct_by_code[struct_code]
    sql_chunks.append("-- Phase 1 : INSERT système ERP-AH")
    sql_chunks.append(
        "INSERT INTO cartography_system "
        "(code, name, description, vendor, criticality, mode, is_master_for, version, "
        "modules, category_id, structure_id, country) "
        "VALUES ("
        f"{sql_lit(local_erp['code'])}, {sql_lit(local_erp['name'])}, "
        f"{sql_lit(local_erp['description'])}, {sql_lit(local_erp['vendor'])}, "
        f"{sql_lit(local_erp['criticality'])}, {sql_lit(local_erp['mode'])}, "
        f"{sql_lit(local_erp['is_master_for'])}, {sql_lit(local_erp['version'])}, "
        f"{sql_lit(local_erp['modules'])}, {cat_id}, {struct_id}, {sql_lit(local_erp['country'])}"
        ");"
    )
    sql_chunks.append("")
    print(f"  → INSERT ERP-AH (cat_id={cat_id}, struct_id={struct_id})")

# ---- Phase 2 : UPDATE flux F-4 et F-83
print("\n=== Phase 2 : UPDATE flux F-4 et F-83 ===")
local_f4 = cur.execute("SELECT * FROM cartography_dataflow WHERE id=4").fetchone()
local_f83 = cur.execute("SELECT * FROM cartography_dataflow WHERE id=83").fetchone()

sql_chunks.append("-- Phase 2 : UPDATE F-4 (AMOS → AIMS)")
sql_chunks.append(
    f"UPDATE cartography_dataflow SET "
    f"name={sql_lit(local_f4['name'])}, "
    f"description={sql_lit(local_f4['description'])} "
    f"WHERE id=4;"
)
print(f"  F-4 : new name = {local_f4['name']!r}")

# F-83 : récupérer l'id ERP-AH prod après son INSERT — utiliser une CTE / lookup par code
sql_chunks.append("")
sql_chunks.append("-- Phase 2 : UPDATE F-83 (AMOS → ERP-AH)")
sql_chunks.append(
    "UPDATE cartography_dataflow SET "
    f"description={sql_lit(local_f83['description'])}, "
    "target_id=(SELECT id FROM cartography_system WHERE code='ERP-AH') "
    "WHERE id=83;"
)
print(f"  F-83 : target → ERP-AH (par lookup), description mise à jour")

# ---- Phase 3 : INSERT 12 nouveaux flux
print("\n=== Phase 3 : INSERT nouveaux flux (sauf F-4/F-83 déjà gérés) ===")
sql_chunks.append("")
sql_chunks.append("-- Phase 3 : INSERT nouveaux flux")

# Récupérer flux prod par tuple
prod_flows = psql_many(
    "SELECT f.id, f.name, src.code, tgt.code "
    "FROM cartography_dataflow f "
    "JOIN cartography_system src ON f.source_id=src.id "
    "JOIN cartography_system tgt ON f.target_id=tgt.id"
)
prod_flow_keys = {(r[2], r[3], r[1]) for r in prod_flows}

inserted_flows = 0
local_flows = list(cur.execute(
    "SELECT f.*, src.code as src_code, tgt.code as tgt_code "
    "FROM cartography_dataflow f "
    "JOIN cartography_system src ON f.source_id=src.id "
    "JOIN cartography_system tgt ON f.target_id=tgt.id"
))
for f in local_flows:
    if f["id"] in (4, 83):
        continue
    key = (f["src_code"], f["tgt_code"], f["name"])
    if key in prod_flow_keys:
        continue
    src_code = f["src_code"]
    tgt_code = f["tgt_code"]
    # Lookup par code (pour ERP-AH qui sera créé en phase 1)
    src_lookup = f"(SELECT id FROM cartography_system WHERE code='{src_code}')"
    tgt_lookup = f"(SELECT id FROM cartography_system WHERE code='{tgt_code}')"
    sql_chunks.append(
        "INSERT INTO cartography_dataflow "
        "(name, description, frequency, protocol, format, is_automated, is_critical, volume, source_id, target_id) "
        "VALUES ("
        f"{sql_lit(f['name'])}, {sql_lit(f['description'])}, {sql_lit(f['frequency'])}, "
        f"{sql_lit(f['protocol'])}, {sql_lit(f['format'])}, "
        f"{sql_lit(bool(f['is_automated']))}, {sql_lit(bool(f['is_critical']))}, "
        f"{sql_lit(f['volume'])}, {src_lookup}, {tgt_lookup}"
        ");"
    )
    inserted_flows += 1
    print(f"  + {src_code} → {tgt_code} : {f['name'][:60]}")
print(f"  Total INSERT flux : {inserted_flows}")

# ---- Phase 4 : INSERT process PROC-AA-* + steps + M2M
print("\n=== Phase 4 : INSERT 76 process PROC-AA-* ===")
sql_chunks.append("")
sql_chunks.append("-- Phase 4 : INSERT process PROC-AA-* + steps + M2M")

local_processes = list(cur.execute(
    "SELECT * FROM cartography_process WHERE code LIKE 'PROC-AA-%' ORDER BY code"
))
print(f"  Process PROC-AA-* en local : {len(local_processes)}")

inserted_steps_total = 0
inserted_pstruct_total = 0
inserted_psys_total = 0

for p in local_processes:
    # Marqueur unique pour récupérer l'id généré
    pcode = p["code"]
    sql_chunks.append(f"-- Process: {pcode}")
    sql_chunks.append(
        "INSERT INTO cartography_process "
        "(name, code, description, context, category, status, problems, recommendations, "
        "workflow_json, workflow_mermaid, ai_generated, created_by, created_at, updated_at, "
        "validated_by, validated_role, validation_comment, validation_requested_by, validation_status, "
        "validation_token) "
        "VALUES ("
        f"{sql_lit(p['name'])}, {sql_lit(pcode)}, {sql_lit(p['description'])}, "
        f"{sql_lit(p['context'])}, {sql_lit(p['category'])}, {sql_lit(p['status'])}, "
        f"{sql_lit(p['problems'])}, {sql_lit(p['recommendations'])}, "
        f"{sql_lit(p['workflow_json'])}, {sql_lit(p['workflow_mermaid'])}, "
        f"{sql_lit(bool(p['ai_generated']))}, {sql_lit(p['created_by'])}, "
        f"NOW(), NOW(), "
        f"{sql_lit(p['validated_by'] or '')}, {sql_lit(p['validated_role'] or '')}, "
        f"{sql_lit(p['validation_comment'] or '')}, {sql_lit(p['validation_requested_by'] or '')}, "
        f"{sql_lit(p['validation_status'] or 'NOT_REQUESTED')}, NULL"
        ");"
    )

    # Steps
    steps = list(cur.execute(
        "SELECT * FROM cartography_processstep WHERE process_id=? ORDER BY \"order\"",
        (p["id"],),
    ))
    for st in steps:
        # actor_structure (peut être NULL)
        actor_struct_lookup = "NULL"
        if st["actor_structure_id"]:
            ac_code = local_struct_by_id.get(st["actor_structure_id"])
            if ac_code and ac_code in prod_struct_by_code:
                actor_struct_lookup = f"(SELECT id FROM cartography_structure WHERE code='{ac_code}')"
        sql_chunks.append(
            "INSERT INTO cartography_processstep "
            "(\"order\", title, description, step_type, actor_role, data_inputs, data_outputs, "
            "interactions, problems, duration_estimate, next_steps, actor_structure_id, process_id) "
            "VALUES ("
            f"{st['order']}, {sql_lit(st['title'])}, {sql_lit(st['description'])}, "
            f"{sql_lit(st['step_type'])}, {sql_lit(st['actor_role'])}, "
            f"{sql_lit(st['data_inputs'])}, {sql_lit(st['data_outputs'])}, "
            f"{sql_lit(st['interactions'])}, {sql_lit(st['problems'])}, "
            f"{sql_lit(st['duration_estimate'])}, {sql_lit(st['next_steps'])}, "
            f"{actor_struct_lookup}, "
            f"(SELECT id FROM cartography_process WHERE code={sql_lit(pcode)})"
            ");"
        )
        inserted_steps_total += 1

    # M2M structures
    pstructs = list(cur.execute(
        "SELECT structure_id FROM cartography_process_structures WHERE process_id=?",
        (p["id"],),
    ))
    for ps in pstructs:
        scode = local_struct_by_id.get(ps["structure_id"])
        if scode and scode in prod_struct_by_code:
            sql_chunks.append(
                "INSERT INTO cartography_process_structures (process_id, structure_id) "
                f"VALUES ((SELECT id FROM cartography_process WHERE code={sql_lit(pcode)}), "
                f"(SELECT id FROM cartography_structure WHERE code='{scode}'));"
            )
            inserted_pstruct_total += 1

    # M2M systems
    psyss = list(cur.execute(
        "SELECT system_id FROM cartography_process_systems WHERE process_id=?",
        (p["id"],),
    ))
    for ps in psyss:
        scode = local_sys_by_id.get(ps["system_id"])
        if scode and scode in prod_sys_by_code:
            sql_chunks.append(
                "INSERT INTO cartography_process_systems (process_id, system_id) "
                f"VALUES ((SELECT id FROM cartography_process WHERE code={sql_lit(pcode)}), "
                f"(SELECT id FROM cartography_system WHERE code='{scode}'));"
            )
            inserted_psys_total += 1

print(f"  Steps insérés        : {inserted_steps_total}")
print(f"  process_structures   : {inserted_pstruct_total}")
print(f"  process_systems      : {inserted_psys_total}")

# ---------------------------------------------------------------- Finalisation
sql_chunks.append("")
sql_chunks.append("COMMIT;")
sql_chunks.append("")
sql_chunks.append("-- Vérifications post-sync")
sql_chunks.append("SELECT 'ERP-AH' as t, COUNT(*) FROM cartography_system WHERE code='ERP-AH';")
sql_chunks.append("SELECT 'flow F-4 name' as t, name FROM cartography_dataflow WHERE id=4;")
sql_chunks.append("SELECT 'flow F-83 target' as t, (SELECT code FROM cartography_system WHERE id=target_id) FROM cartography_dataflow WHERE id=83;")
sql_chunks.append("SELECT 'flux total', COUNT(*) FROM cartography_dataflow;")
sql_chunks.append("SELECT 'process PROC-AA-* total', COUNT(*) FROM cartography_process WHERE code LIKE 'PROC-AA-%';")
sql_chunks.append("SELECT 'process total', COUNT(*) FROM cartography_process;")

sql_text = "\n".join(sql_chunks)
out_sql = OUT_DIR / f"sync_local_to_prod_{TS}.sql"
out_sql.write_text(sql_text, encoding="utf-8")
print(f"\n✅ SQL généré : {out_sql}  ({len(sql_chunks)} lignes, {len(sql_text)} octets)")

if not APPLY:
    print("\n=== DRY-RUN ===")
    print("→ Inspecter le fichier SQL puis relancer avec --apply pour exécuter.")
    sys.exit(0)

# Apply : envoyer le SQL en prod via SSH
print("\n=== APPLY : exécution en prod ===")
# Transférer puis exécuter
remote_path = f"/tmp/sync_local_to_prod_{TS}.sql"
print(f"  Upload SQL → airalgerie-vps:{remote_path}")
subprocess.run(
    ["scp", str(out_sql), f"airalgerie-vps:{remote_path}"],
    check=True,
)
print(f"  Exécution en prod...")
result = subprocess.run(
    ["ssh", "airalgerie-vps",
     f"sudo -u postgres psql cartographie_si -v ON_ERROR_STOP=1 -f {remote_path}"],
    capture_output=True, text=True, timeout=300,
)
print("--- STDOUT ---")
print(result.stdout[-3000:])
print("--- STDERR ---")
print(result.stderr[-1500:])
if result.returncode != 0:
    print(f"❌ Échec (code={result.returncode})")
    sys.exit(1)
print("✅ Sync prod appliqué.")
