"""Diagnostic détaillé du delta local → prod (ce qui doit être poussé).

Compare via SSH/psql et SQLite local sur les axes :
- Systèmes (par code)
- Flux (par id ET par tuple source/target/name)
- Process (par code)
- Questionnaires (par system_name)
- Structures (par code)

Sortie : rapport texte + JSON.
"""
import json
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "db.sqlite3"
OUT_DIR = ROOT / "prod_data"
OUT_DIR.mkdir(exist_ok=True)
TS = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def psql(sql):
    """Exécute du SQL en prod et renvoie les lignes en TSV (sans header)."""
    r = subprocess.run(
        ["ssh", "airalgerie-vps",
         f"sudo -u postgres psql cartographie_si -At -F$'\\t' -c \"{sql}\""],
        capture_output=True, text=True, timeout=60,
    )
    if r.returncode != 0:
        print("psql err:", r.stderr)
        raise SystemExit(1)
    return [l.split("\t") for l in r.stdout.strip().split("\n") if l.strip()]


con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()

report = {"ts": TS}

# ---------------------------------------------------------------- 1. Structures
print("=== 1. STRUCTURES ===")
local_st = {r["code"]: dict(r) for r in cur.execute(
    "SELECT id, code, name, parent_id FROM cartography_structure"
)}
prod_st_rows = psql("SELECT id, code, name, parent_id FROM cartography_structure ORDER BY code")
prod_st = {r[1]: {"id": int(r[0]), "code": r[1], "name": r[2], "parent_id": r[3]} for r in prod_st_rows}
print(f"  Local: {len(local_st)}  |  Prod: {len(prod_st)}")
new_struct = sorted(set(local_st) - set(prod_st))
miss_struct = sorted(set(prod_st) - set(local_st))
print(f"  Locales absentes en prod : {new_struct}")
print(f"  Prod absentes en local   : {miss_struct}")
report["structures"] = {"local_count": len(local_st), "prod_count": len(prod_st),
                         "to_create_in_prod": new_struct, "missing_in_local": miss_struct}

# ---------------------------------------------------------------- 2. Systèmes
print("\n=== 2. SYSTÈMES ===")
local_sys = {r["code"]: dict(r) for r in cur.execute(
    "SELECT id, code, name, structure_id, criticality, mode, country, vendor, version "
    "FROM cartography_system"
)}
prod_sys_rows = psql("SELECT id, code, name, structure_id FROM cartography_system ORDER BY code")
prod_sys = {r[1]: {"id": int(r[0]), "code": r[1], "name": r[2]} for r in prod_sys_rows}
print(f"  Local: {len(local_sys)}  |  Prod: {len(prod_sys)}")
new_sys = sorted(set(local_sys) - set(prod_sys))
miss_sys = sorted(set(prod_sys) - set(local_sys))
print(f"  Locaux absents en prod : {new_sys}")
print(f"  Prod absents en local  : {miss_sys}")
report["systems"] = {"local_count": len(local_sys), "prod_count": len(prod_sys),
                      "to_create_in_prod": new_sys, "missing_in_local": miss_sys}

# ---------------------------------------------------------------- 3. Flux
print("\n=== 3. FLUX ===")
local_fl = {}
for r in cur.execute(
    "SELECT f.id, f.name, f.description, f.frequency, f.is_critical, f.is_automated, "
    "src.code as src, tgt.code as tgt FROM cartography_dataflow f "
    "JOIN cartography_system src ON f.source_id=src.id "
    "JOIN cartography_system tgt ON f.target_id=tgt.id"
):
    key = (r["src"], r["tgt"], r["name"])
    local_fl[key] = dict(r)

prod_fl_rows = psql(
    "SELECT f.id, f.name, src.code, tgt.code, f.frequency, f.is_critical, f.is_automated "
    "FROM cartography_dataflow f "
    "JOIN cartography_system src ON f.source_id=src.id "
    "JOIN cartography_system tgt ON f.target_id=tgt.id ORDER BY f.id"
)
prod_fl = {}
for r in prod_fl_rows:
    key = (r[2], r[3], r[1])
    prod_fl[key] = {"id": int(r[0]), "name": r[1], "src": r[2], "tgt": r[3]}

print(f"  Local: {len(local_fl)}  |  Prod: {len(prod_fl)}")
new_fl_keys = sorted(set(local_fl) - set(prod_fl))
miss_fl_keys = sorted(set(prod_fl) - set(local_fl))
print(f"  Flux locaux absents en prod ({len(new_fl_keys)}):")
for k in new_fl_keys[:20]:
    print(f"    + {k[0]} → {k[1]} : {k[2]}")
if len(new_fl_keys) > 20:
    print(f"    ... ({len(new_fl_keys) - 20} autres)")
print(f"  Flux prod absents en local ({len(miss_fl_keys)}):")
for k in miss_fl_keys[:20]:
    print(f"    - {k[0]} → {k[1]} : {k[2]}")
if len(miss_fl_keys) > 20:
    print(f"    ... ({len(miss_fl_keys) - 20} autres)")

report["flows"] = {"local_count": len(local_fl), "prod_count": len(prod_fl),
                    "new_in_local": [list(k) for k in new_fl_keys],
                    "missing_in_local": [list(k) for k in miss_fl_keys]}

# ---------------------------------------------------------------- 4. Processus
print("\n=== 4. PROCESS ===")
local_p = {r["code"]: dict(r) for r in cur.execute(
    "SELECT id, code, name, status, ai_generated FROM cartography_process"
)}
prod_p_rows = psql("SELECT id, code, name FROM cartography_process ORDER BY code")
prod_p = {r[1]: {"id": int(r[0]), "code": r[1], "name": r[2]} for r in prod_p_rows}
print(f"  Local: {len(local_p)}  |  Prod: {len(prod_p)}")
new_p = sorted(set(local_p) - set(prod_p))
miss_p = sorted(set(prod_p) - set(local_p))
print(f"  Process locaux absents en prod ({len(new_p)}) — premiers 10 :")
for c in new_p[:10]:
    print(f"    + {c} — {local_p[c]['name'][:80]}")
print(f"  Process prod absents en local ({len(miss_p)}):")
for c in miss_p:
    print(f"    - {c} — {prod_p[c]['name'][:80]}")
report["processes"] = {"local_count": len(local_p), "prod_count": len(prod_p),
                        "to_create_in_prod": new_p, "missing_in_local": miss_p}

# ---------------------------------------------------------------- 5. Questionnaires
print("\n=== 5. QUESTIONNAIRES ===")
local_qn = {r["system_name"]: dict(r) for r in cur.execute(
    "SELECT id, system_name, phase, status FROM cartography_questionnaire"
)}
prod_qn_rows = psql("SELECT id, system_name, status FROM cartography_questionnaire ORDER BY system_name")
prod_qn = {r[1]: {"id": int(r[0]), "system_name": r[1], "status": r[2]} for r in prod_qn_rows}
print(f"  Local: {len(local_qn)}  |  Prod: {len(prod_qn)}")
new_qn = sorted(set(local_qn) - set(prod_qn))
miss_qn = sorted(set(prod_qn) - set(local_qn))
print(f"  Questionnaires locaux absents en prod ({len(new_qn)}):")
for c in new_qn:
    print(f"    + {c}")
print(f"  Questionnaires prod absents en local ({len(miss_qn)}):")
for c in miss_qn:
    print(f"    - {c}")
report["questionnaires"] = {"local_count": len(local_qn), "prod_count": len(prod_qn),
                             "new_in_local": new_qn, "missing_in_local": miss_qn}

# ---------------------------------------------------------------- 6. Sauvegarde
out = OUT_DIR / f"diff_local_to_prod_{TS}.json"
out.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
print(f"\n✅ Rapport JSON : {out}")
con.close()
