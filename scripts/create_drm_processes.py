"""Crée les 12 process DRM issus du canevas BELDJERDI (19/05/2026).

Périmètre :
  - 12 process PROC-AA-DRM-01..12 rattachés à la structure DRM (code='DRM').
  - Pour chaque process : 2 étapes (MANUAL puis OUTPUT) avec les systèmes
    cités EN TEXTE dans `interactions`/`data_inputs`/`data_outputs` (pas de
    lien FK vers `cartography_system`).
  - AUCUNE création de système ni de DataFlow.

Idempotent :
  - LOCAL : si un code PROC-AA-DRM-XX existe déjà, on saute.
  - PROD  : INSERT ... ON CONFLICT (code) DO NOTHING (et NOT EXISTS pour M2M).

Usage :
    python scripts/create_drm_processes.py              # dry-run prod, applique en local
    python scripts/create_drm_processes.py --apply      # applique aussi en prod
    python scripts/create_drm_processes.py --local-only # local uniquement, pas de SQL prod
    python scripts/create_drm_processes.py --skip-local # local déjà fait, ne touche pas local
"""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "db.sqlite3"
OUT_DIR = ROOT / "prod_data"
OUT_DIR.mkdir(exist_ok=True)
TS = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

APPLY = "--apply" in sys.argv
SKIP_LOCAL = "--skip-local" in sys.argv
LOCAL_ONLY = "--local-only" in sys.argv

SOURCE = "BELDJERDI Zakaria (canevas DRM 19/05/2026)"
STRUCTURE_CODE = "DRM"

# ---------------------------------------------------------------- Données
# Les 12 process. `systems_text` = liste des systèmes mentionnés (textuel).
PROCESSES: list[dict] = [
    {
        "code": "PROC-AA-DRM-01",
        "name": "Affichage de nouvelles destinations sur l'IBE",
        "category": "COMMERCIAL",
        "description": "Affichage des nouvelles destinations sur le site web et l'application mobile d'Air Algérie.",
        "context": "Lors de l'ouverture d'une nouvelle route commerciale, la DRM/IBE configure et publie la destination sur l'IBE web et mobile pour la rendre visible des passagers.",
        "systems_text": ["Site Manager", "CMS", "PCM"],
        "outputs": "Affichage de la nouvelle destination sur le site web et l'application mobile.",
    },
    {
        "code": "PROC-AA-DRM-02",
        "name": "Filling de tarifs",
        "category": "COMMERCIAL",
        "description": "Configuration des tarifs (classes / cabines) afin de permettre leur affichage sur les canaux de vente.",
        "context": "Le filling tarifaire consiste à configurer dans Site Manager et Farexpert les familles tarifaires, classes et cabines pour que les tarifs soient correctement publiés.",
        "systems_text": ["Site Manager", "Farexpert"],
        "outputs": "Affichage des familles tarifaires sur l'IBE.",
    },
    {
        "code": "PROC-AA-DRM-03",
        "name": "Configuration et mapping de nouvelles destinations",
        "category": "COMMERCIAL",
        "description": "Configuration de la nouvelle destination pour qu'elle soit commercialisable avec les bonnes règles.",
        "context": "Le mapping PCM est l'étape technique préalable à la commercialisation d'une nouvelle ligne sur l'IBE et les GDS.",
        "systems_text": ["PCM"],
        "outputs": "Ligne commercialisable côté IBE et GDS.",
    },
    {
        "code": "PROC-AA-DRM-04",
        "name": "Publication et affichage sur le site et l'application mobile",
        "category": "COMMERCIAL",
        "description": "Publication du contenu (pages d'informations, promotions, visuels, etc.) sur le site web et l'application mobile.",
        "context": "L'équipe contenu DRM publie via le CMS les pages info, visuels, promos qui apparaissent ensuite sur le site web et l'app mobile.",
        "systems_text": ["CMS"],
        "outputs": "Affichage du contenu éditorial sur l'IBE web + mobile.",
    },
    {
        "code": "PROC-AA-DRM-05",
        "name": "Configuration des codes promo / discounts",
        "category": "COMMERCIAL",
        "description": "Paramétrage des codes promotionnels ou des réductions pour une vente sur l'IBE.",
        "context": "Les campagnes commerciales (offres, codes promo) sont paramétrées dans AAM et Site Manager pour application automatique au check-out IBE.",
        "systems_text": ["AAM", "Site Manager"],
        "outputs": "Affichage d'une réduction lors de la réservation IBE.",
    },
    {
        "code": "PROC-AA-DRM-06",
        "name": "Comptabilité et rapprochement IBE",
        "category": "FINANCE",
        "description": "Mise en œuvre de la comptabilité IBE ainsi que du rapprochement financier et commercial.",
        "context": "Quotidiennement, les ventes IBE sont rapprochées avec les transactions de paiement et intégrées en comptabilité dans l'ERP. Une partie reste manuelle sur Excel.",
        "systems_text": ["ERP-AH", "Amadeus Payment Platform", "Excel", "Plateformes de paiement"],
        "outputs": "Comptabilité IBE journalière, état de rapprochement.",
    },
    {
        "code": "PROC-AA-DRM-07",
        "name": "Suivi des anomalies de paiement",
        "category": "FINANCE",
        "description": "Suivi et traitement quotidien des anomalies de paiement constatées sur les ventes IBE.",
        "context": "Toute anomalie détectée (échec, double prélèvement, écart) est tracée dans Excel et investiguée via les outils paiement (ARD Web, Amadeus Payment Platform, ELAVON) avant correction.",
        "systems_text": ["Excel", "ARD Web", "Amadeus Payment Platform", "ELAVON", "Plateformes de paiement"],
        "outputs": "Correction et traitement des anomalies de paiement.",
    },
    {
        "code": "PROC-AA-DRM-08",
        "name": "Traitement des chargebacks",
        "category": "FINANCE",
        "description": "Traitement des demandes de remboursement transmises par les banques (chargebacks).",
        "context": "Lorsque la banque émet un chargeback, l'équipe DRM/Comptabilité IBE investigue le PNR, le ticket et la transaction, et instruit le remboursement via les canaux paiement (ELAVON, SATIM, CCP, Amadeus Payment Platform). Traçabilité Excel.",
        "systems_text": ["ELAVON", "SATIM", "CCP", "ARD Web", "Amadeus Payment Platform", "Excel"],
        "outputs": "Remboursement effectif au porteur de carte.",
    },
    {
        "code": "PROC-AA-DRM-09",
        "name": "Traitement des demandes de remboursement",
        "category": "FINANCE",
        "description": "Traitement des demandes de remboursement reçues via E-Doléance.",
        "context": "Les demandes de remboursement passagers arrivent via E-Doléance et sont rapprochées avec le PNR/ticket dans ARD Web puis remboursées via les canaux paiement appropriés. Trace transversale via DataHub.",
        "systems_text": ["ELAVON", "SATIM", "CCP", "ARD Web", "Amadeus Payment Platform", "DataHub"],
        "outputs": "Remboursement passager et clôture de la doléance.",
    },
    {
        "code": "PROC-AA-DRM-10",
        "name": "Etablissement des factures",
        "category": "FINANCE",
        "description": "Etablissement des factures pour les clients IBE après réception de la demande.",
        "context": "À la demande d'un client (transmise via E-Doléance), la facture est produite manuellement à partir des données ARD Web et émise via l'ERP avec mise en forme Word.",
        "systems_text": ["ERP-AH", "E-Doléance", "Word", "ARD Web"],
        "outputs": "Facture client émise.",
    },
    {
        "code": "PROC-AA-DRM-11",
        "name": "Analyse de performance du site web et de l'application mobile",
        "category": "IT",
        "description": "Analyse de la performance, de l'expérience utilisateur et du fonctionnement du site et de l'app.",
        "context": "Suivi régulier des KPI d'audience et de conversion via Google Analytics (web), Firebase (mobile), Google Play Console (Android) et App Store Connect (iOS).",
        "systems_text": ["Google Analytics", "Firebase", "Google Play Console", "App Store Connect"],
        "outputs": "Rapport de performance / fonctionnement / UX.",
    },
    {
        "code": "PROC-AA-DRM-12",
        "name": "Suivi de l'état de santé des plateformes (monitoring)",
        "category": "IT",
        "description": "Surveillance du bon fonctionnement de toutes les plateformes (paiement, IBE, app).",
        "context": "Monitoring continu via Freshping (uptime) et RPTG monitoring pour détecter au plus tôt les anomalies plateformes et alerter les équipes techniques.",
        "systems_text": ["Freshping", "RPTG monitoring"],
        "outputs": "Rapports de suivi / alertes plateformes.",
    },
]

assert len(PROCESSES) == 12


def build_steps(p: dict) -> list[dict]:
    """Deux étapes minimales par process : MANUAL puis OUTPUT."""
    systems_str = ", ".join(p["systems_text"])
    return [
        {
            "order": 1,
            "title": f"Réalisation — {p['name']}",
            "description": p["context"],
            "step_type": "MANUAL",
            "actor_role": "Équipe DRM / IBE",
            "data_inputs": f"Déclencheur métier ({p['name']})",
            "data_outputs": p["outputs"],
            "interactions": f"Systèmes mobilisés : {systems_str}",
            "problems": "",
            "duration_estimate": "",
            "next_steps": "[]",
        },
        {
            "order": 2,
            "title": f"Production des outputs — {p['name']}",
            "description": "Vérification, validation et publication des outputs du process.",
            "step_type": "OUTPUT",
            "actor_role": "Équipe DRM / IBE",
            "data_inputs": p["outputs"],
            "data_outputs": p["outputs"],
            "interactions": f"Systèmes mobilisés : {systems_str}",
            "problems": "",
            "duration_estimate": "",
            "next_steps": "[]",
        },
    ]


# ---------------------------------------------------------------- Phase A : LOCAL
con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()


def get_structure_id_local(code: str) -> int:
    r = cur.execute("SELECT id FROM cartography_structure WHERE code=?", (code,)).fetchone()
    if not r:
        raise SystemExit(f"Structure '{code}' introuvable en local")
    return r["id"]


def apply_local() -> None:
    print("=== Phase A : LOCAL (db.sqlite3) ===")
    drm_id = get_structure_id_local(STRUCTURE_CODE)
    print(f"  Structure DRM id local = {drm_id}")

    cur.execute("BEGIN")
    created = skipped = total_steps = 0
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        for p in PROCESSES:
            r = cur.execute(
                "SELECT id FROM cartography_process WHERE code=?", (p["code"],)
            ).fetchone()
            if r:
                print(f"  ↺ {p['code']} déjà existant (id={r['id']}) — skip")
                skipped += 1
                continue

            cur.execute(
                "INSERT INTO cartography_process "
                "(name, code, description, context, category, status, problems, "
                "recommendations, workflow_json, workflow_mermaid, ai_generated, "
                "created_by, created_at, updated_at, validated_by, validated_role, "
                "validation_comment, validation_requested_by, validation_status, "
                "validation_token) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    p["name"], p["code"], p["description"], p["context"],
                    p["category"], "DRAFT", "", "", "{}", "", 0,
                    SOURCE, now, now, "", "", "", "", "NOT_REQUESTED", None,
                ),
            )
            pid = cur.lastrowid

            # Steps
            for st in build_steps(p):
                cur.execute(
                    "INSERT INTO cartography_processstep "
                    "(\"order\", title, description, step_type, actor_role, "
                    "data_inputs, data_outputs, interactions, problems, "
                    "duration_estimate, next_steps, actor_structure_id, process_id) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        st["order"], st["title"], st["description"], st["step_type"],
                        st["actor_role"], st["data_inputs"], st["data_outputs"],
                        st["interactions"], st["problems"], st["duration_estimate"],
                        st["next_steps"], drm_id, pid,
                    ),
                )
                total_steps += 1

            # M2M structure (DRM)
            cur.execute(
                "INSERT INTO cartography_process_structures (process_id, structure_id) "
                "VALUES (?, ?)", (pid, drm_id),
            )
            print(f"  ✚ {p['code']} créé (id={pid}, 2 steps)")
            created += 1

        con.commit()
        print(f"\n  Résumé local : créés={created} | skip={skipped} | steps={total_steps}")
    except Exception:
        con.rollback()
        raise


# ---------------------------------------------------------------- Phase B/C : PROD
def sql_lit(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v).replace("\\", "\\\\").replace("'", "''")
    return f"E'{s}'"


def build_prod_sql() -> str:
    chunks: list[str] = []
    chunks.append("-- =====================================================")
    chunks.append(f"-- Création process DRM (12 process + 24 steps + 12 M2M)")
    chunks.append(f"-- Source : {SOURCE}")
    chunks.append(f"-- Généré : {TS}")
    chunks.append("-- =====================================================")
    chunks.append("BEGIN;")
    chunks.append("")
    chunks.append(
        "-- Pré-check : la structure DRM doit exister en prod."
    )
    chunks.append(
        "DO $$ BEGIN "
        "IF NOT EXISTS (SELECT 1 FROM cartography_structure WHERE code='DRM') "
        "THEN RAISE EXCEPTION 'Structure DRM absente en prod, abort'; "
        "END IF; END $$;"
    )
    chunks.append("")

    for p in PROCESSES:
        steps = build_steps(p)
        chunks.append(f"-- {p['code']} : {p['name']}")
        chunks.append(
            "INSERT INTO cartography_process "
            "(name, code, description, context, category, status, problems, "
            "recommendations, workflow_json, workflow_mermaid, ai_generated, "
            "created_by, created_at, updated_at, validated_by, validated_role, "
            "validation_comment, validation_requested_by, validation_status, "
            "validation_token) VALUES ("
            f"{sql_lit(p['name'])}, {sql_lit(p['code'])}, {sql_lit(p['description'])}, "
            f"{sql_lit(p['context'])}, {sql_lit(p['category'])}, E'DRAFT', E'', E'', "
            f"'{{}}'::jsonb, E'', FALSE, {sql_lit(SOURCE)}, NOW(), NOW(), "
            "E'', E'', E'', E'', E'NOT_REQUESTED', NULL"
            ") ON CONFLICT (code) DO NOTHING;"
        )

        for st in steps:
            chunks.append(
                "INSERT INTO cartography_processstep "
                "(\"order\", title, description, step_type, actor_role, data_inputs, "
                "data_outputs, interactions, problems, duration_estimate, next_steps, "
                "actor_structure_id, process_id) "
                "SELECT "
                f"{st['order']}, {sql_lit(st['title'])}, {sql_lit(st['description'])}, "
                f"{sql_lit(st['step_type'])}, {sql_lit(st['actor_role'])}, "
                f"{sql_lit(st['data_inputs'])}, {sql_lit(st['data_outputs'])}, "
                f"{sql_lit(st['interactions'])}, {sql_lit(st['problems'])}, "
                f"{sql_lit(st['duration_estimate'])}, "
                f"{sql_lit(st['next_steps'])}::jsonb, "
                "(SELECT id FROM cartography_structure WHERE code='DRM'), "
                f"(SELECT id FROM cartography_process WHERE code={sql_lit(p['code'])}) "
                "WHERE NOT EXISTS ("
                "  SELECT 1 FROM cartography_processstep "
                f"  WHERE process_id=(SELECT id FROM cartography_process WHERE code={sql_lit(p['code'])}) "
                f"  AND \"order\"={st['order']}"
                ");"
            )

        chunks.append(
            "INSERT INTO cartography_process_structures (process_id, structure_id) "
            "SELECT "
            f"(SELECT id FROM cartography_process WHERE code={sql_lit(p['code'])}), "
            "(SELECT id FROM cartography_structure WHERE code='DRM') "
            "WHERE NOT EXISTS ("
            "  SELECT 1 FROM cartography_process_structures "
            f"  WHERE process_id=(SELECT id FROM cartography_process WHERE code={sql_lit(p['code'])}) "
            "  AND structure_id=(SELECT id FROM cartography_structure WHERE code='DRM')"
            ");"
        )
        chunks.append("")

    chunks.append("COMMIT;")
    chunks.append("")
    chunks.append("-- Vérifications post-sync")
    chunks.append(
        "SELECT 'process DRM total', COUNT(*) FROM cartography_process WHERE code LIKE 'PROC-AA-DRM-%';"
    )
    chunks.append(
        "SELECT 'steps DRM total', COUNT(*) FROM cartography_processstep "
        "WHERE process_id IN (SELECT id FROM cartography_process WHERE code LIKE 'PROC-AA-DRM-%');"
    )
    chunks.append(
        "SELECT 'process_structures DRM', COUNT(*) FROM cartography_process_structures "
        "WHERE process_id IN (SELECT id FROM cartography_process WHERE code LIKE 'PROC-AA-DRM-%');"
    )
    return "\n".join(chunks)


def apply_prod(sql_text: str) -> None:
    out_sql = OUT_DIR / f"create_drm_processes_{TS}.sql"
    out_sql.write_text(sql_text, encoding="utf-8")
    print(f"\n✅ SQL prod généré : {out_sql}  ({len(sql_text)} octets, {sql_text.count(chr(10))} lignes)")

    if not APPLY:
        print("\n=== DRY-RUN PROD ===")
        print("→ Inspecter le fichier SQL puis relancer avec --apply pour exécuter.")
        return

    remote_path = f"/tmp/create_drm_processes_{TS}.sql"
    print(f"\n=== APPLY PROD ===")
    print(f"  Upload SQL → airalgerie-vps:{remote_path}")
    subprocess.run(["scp", str(out_sql), f"airalgerie-vps:{remote_path}"], check=True)
    print(f"  Exécution en prod...")
    result = subprocess.run(
        ["ssh", "airalgerie-vps",
         f"sudo -u postgres psql cartographie_si -v ON_ERROR_STOP=1 -f {remote_path}"],
        capture_output=True, text=True, timeout=300,
    )
    print("--- STDOUT ---")
    print(result.stdout[-3000:])
    if result.stderr:
        print("--- STDERR ---")
        print(result.stderr[-1500:])
    if result.returncode != 0:
        print(f"❌ Échec (code={result.returncode})")
        sys.exit(1)
    print("✅ Sync prod appliqué.")


# ---------------------------------------------------------------- Main
if not SKIP_LOCAL:
    apply_local()
else:
    print("=== Phase A LOCAL : skip (--skip-local) ===")

if LOCAL_ONLY:
    print("\n=== --local-only : pas de génération prod ===")
    sys.exit(0)

print("\n=== Phase B : Génération SQL prod ===")
sql_text = build_prod_sql()
apply_prod(sql_text)
