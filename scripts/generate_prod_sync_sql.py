"""
Génère un script SQL idempotent transactionnel qui synchronise sur la prod
PostgreSQL les 6 process modifiés en local après la restitution DC 24/05/2026 :

- PROC-AA-DIVEX-02  (refonte 16 -> 19 étapes)
- PROC-WT-001       (corrections transcript)
- PROC-AA-DOS-05    (corrections transcript)
- PROC-AA-DC-03     (corrections transcript)
- PROC-AA-DRM-06    (corrections transcript)
- PROC-AA-DRM-10    (enrichissement RAPID)

Pour chaque process le SQL :
1. UPDATE de cartography_process (context, problems, recommendations,
   workflow_mermaid, ai_generated, name, description, category, status,
   updated_at).
2. DELETE + INSERT de M2M cartography_process_structures (par code).
3. DELETE + INSERT de M2M cartography_process_systems (par code).
4. DELETE + INSERT de cartography_processstep avec RETURNING id pour ré-injecter
   les M2M cartography_processstep_systems_used.

Tout est encadré BEGIN / COMMIT avec ON_ERROR_STOP=1.

Idempotent : un re-run écrase les mêmes champs/étapes à l'identique.

Usage:
    venv/bin/python scripts/generate_prod_sync_sql.py
    # → écrit prod_data/sync_processes_<ts>.sql
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

import django

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from cartography.models import Process  # noqa: E402


PROCESS_CODES = [
    "PROC-AA-DIVEX-02",
    "PROC-WT-001",
    "PROC-AA-DOS-05",
    "PROC-AA-DC-03",
    "PROC-AA-DRM-06",
    "PROC-AA-DRM-10",
]

OUT_DIR = ROOT / "prod_data"
OUT_DIR.mkdir(exist_ok=True)


def q(s: str | None) -> str:
    """Échappe une chaîne pour SQL Postgres (apostrophe doublée)."""
    if s is None:
        return "NULL"
    return "'" + s.replace("\\", "\\\\").replace("'", "''") + "'"


def qbool(b: bool) -> str:
    return "TRUE" if b else "FALSE"


def qjson(d) -> str:
    import json as _json
    return q(_json.dumps(d, ensure_ascii=False)) + "::jsonb"


def build_sql_for_process(p: Process) -> str:
    structs = sorted({s.code for s in p.structures.all()})
    syscodes = sorted({s.code for s in p.systems.all()})
    steps = list(p.steps.all().order_by("order"))

    out = []
    out.append(f"-- {'=' * 70}")
    out.append(f"-- {p.code}  ({p.name})")
    out.append(f"-- structures = {structs}")
    out.append(f"-- systèmes   = {syscodes}")
    out.append(f"-- étapes     = {len(steps)}")
    out.append(f"-- {'=' * 70}")
    out.append("DO $$")
    out.append("DECLARE")
    out.append("  v_pid BIGINT;")
    out.append("  v_step_id BIGINT;")
    out.append("BEGIN")
    out.append(f"  SELECT id INTO v_pid FROM cartography_process WHERE code = {q(p.code)};")
    out.append(f"  IF v_pid IS NULL THEN RAISE EXCEPTION 'Process {p.code} introuvable en prod'; END IF;")
    out.append("")
    out.append("  -- 1) UPDATE cartography_process")
    out.append("  UPDATE cartography_process SET")
    out.append(f"    name            = {q(p.name)},")
    out.append(f"    description     = {q(p.description or '')},")
    out.append(f"    context         = {q(p.context or '')},")
    out.append(f"    category        = {q(p.category)},")
    out.append(f"    status          = {q(p.status)},")
    out.append(f"    problems        = {q(p.problems or '')},")
    out.append(f"    recommendations = {q(p.recommendations or '')},")
    out.append(f"    workflow_mermaid= {q(p.workflow_mermaid or '')},")
    out.append(f"    ai_generated    = {qbool(p.ai_generated)},")
    out.append("    updated_at      = NOW()")
    out.append("  WHERE id = v_pid;")
    out.append("")
    out.append("  -- 2) M2M structures (DELETE + INSERT par code)")
    out.append("  DELETE FROM cartography_process_structures WHERE process_id = v_pid;")
    if structs:
        codes = ", ".join(q(c) for c in structs)
        out.append("  INSERT INTO cartography_process_structures (process_id, structure_id)")
        out.append(f"    SELECT v_pid, id FROM cartography_structure WHERE code IN ({codes});")
    out.append("")
    out.append("  -- 3) M2M systèmes (DELETE + INSERT par code)")
    out.append("  DELETE FROM cartography_process_systems WHERE process_id = v_pid;")
    if syscodes:
        codes = ", ".join(q(c) for c in syscodes)
        out.append("  INSERT INTO cartography_process_systems (process_id, system_id)")
        out.append(f"    SELECT v_pid, id FROM cartography_system WHERE code IN ({codes});")
    out.append("")
    out.append("  -- 4) Étapes : DELETE cascade + INSERT séquentiel")
    out.append("  DELETE FROM cartography_processstep WHERE process_id = v_pid;")
    out.append("")

    for step in steps:
        step_syscodes = sorted({s.code for s in step.systems_used.all()})
        next_steps = step.next_steps if step.next_steps else []
        actor_struct = step.actor_structure.code if step.actor_structure_id else None

        out.append(f"  -- étape {step.order} : {step.title[:60]}")
        out.append("  INSERT INTO cartography_processstep")
        out.append("    (process_id, \"order\", title, description, step_type, actor_role,")
        out.append("     data_inputs, data_outputs, interactions, problems, duration_estimate,")
        out.append("     next_steps, actor_structure_id)")
        out.append("  VALUES (")
        out.append(f"    v_pid, {step.order}, {q(step.title)}, {q(step.description or '')},")
        out.append(f"    {q(step.step_type)}, {q(step.actor_role or '')},")
        out.append(f"    {q(step.data_inputs or '')}, {q(step.data_outputs or '')},")
        out.append(f"    {q(step.interactions or '')}, {q(step.problems or '')},")
        out.append(f"    {q(step.duration_estimate or '')},")
        out.append(f"    {qjson(next_steps)},")
        if actor_struct:
            out.append(f"    (SELECT id FROM cartography_structure WHERE code = {q(actor_struct)})")
        else:
            out.append("    NULL")
        out.append("  ) RETURNING id INTO v_step_id;")

        if step_syscodes:
            codes = ", ".join(q(c) for c in step_syscodes)
            out.append("  INSERT INTO cartography_processstep_systems_used (processstep_id, system_id)")
            out.append(f"    SELECT v_step_id, id FROM cartography_system WHERE code IN ({codes});")
        out.append("")

    out.append("END $$;")
    out.append("")
    return "\n".join(out)


def main() -> None:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_file = OUT_DIR / f"sync_processes_{ts}.sql"

    header = [
        "-- =============================================================================",
        "-- Sync prod PostgreSQL ← état local SQLite (restitution DC 24/05/2026)",
        f"-- Généré : {datetime.now().isoformat()}",
        f"-- Process : {len(PROCESS_CODES)}",
        f"--   {', '.join(PROCESS_CODES)}",
        "-- Exécution : sudo -u postgres psql cartographie_si -v ON_ERROR_STOP=1 -f <ce_fichier>",
        "-- Rollback   : pg_restore depuis dump-<TS>.dump (cf. /home/ubuntu/backups/)",
        "-- =============================================================================",
        "BEGIN;",
        "",
    ]

    blocks = []
    for code in PROCESS_CODES:
        try:
            p = Process.objects.get(code=code)
        except Process.DoesNotExist:
            print(f"[WARN] {code} introuvable en local — skip")
            continue
        blocks.append(build_sql_for_process(p))

    footer = ["COMMIT;", ""]

    out_file.write_text("\n".join(header) + "\n".join(blocks) + "\n".join(footer), encoding="utf-8")
    print(f"[OK] SQL généré : {out_file}")
    print(f"     Taille     : {out_file.stat().st_size:,} octets")
    print(f"     Process    : {len(blocks)}")
    print()
    print("Prochaine étape :")
    print(f"  scp {out_file} airalgerie-vps:/tmp/sync_processes.sql")
    print("  ssh airalgerie-vps \"sudo -u postgres psql cartographie_si -v ON_ERROR_STOP=1 -f /tmp/sync_processes.sql\"")


if __name__ == "__main__":
    main()
