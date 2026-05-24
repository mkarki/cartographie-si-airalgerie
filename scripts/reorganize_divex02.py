"""Réorganisation des étapes du process PROC-AA-DIVEX-02 (vols charter).

Correction issue de la restitution DC du 24/05/2026 (nihad bounab — DVR).

Refonte :
  - L'étape 17 (id=1424) "Transmission de la proposition Chiffré par la DVR au client"
    était en bout de chaîne après les autorisations. Elle remonte juste après
    l'étape 6 (transmission proposition à DVR).
  - 2 nouvelles étapes sont insérées :
      * order=7 : Élaboration du devis chiffré par la DVR (Excel manuel, IMS+Altea)
      * order=9 : Acceptation / Refus du devis par le client
  - L'étape 17 actuelle devient order=8 avec titre clarifié.
  - Les anciennes étapes 7..16 sont décalées de +3 → deviennent 10..19.
  - L'étape "Lancement des vols charters" (ex-13, nouvelle 16) reçoit une
    mention "Mass Mailing ERP HADGE" dans description + interactions.

Idempotence :
  - Le script vérifie d'abord si les 2 nouvelles étapes existent déjà
    (par titre exact) → si oui, skip total.
  - Le script vérifie que l'étape 1424 a bien order=17 avant de déplacer.

Usage :
    python scripts/reorganize_divex02.py             # LOCAL only + génère SQL prod (dry-run)
    python scripts/reorganize_divex02.py --apply     # LOCAL + applique en PROD via SSH
    python scripts/reorganize_divex02.py --skip-local # SQL prod uniquement
"""
from __future__ import annotations

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

PROCESS_CODE = "PROC-AA-DIVEX-02"
SOURCE = "Restitution DC 24/05/2026 — nihad bounab (DVR)"

# ID local de l'étape "Transmission de la proposition Chiffré par la DVR au client"
EXISTING_STEP_ID_LOCAL = 1424
EXISTING_STEP_OLD_ORDER = 17
EXISTING_STEP_NEW_ORDER = 8
EXISTING_STEP_NEW_TITLE = "Transmission du devis chiffré au client par la DVR"
EXISTING_STEP_NEW_DESC = (
    "Le devis chiffré élaboré par la DVR est transmis au client final "
    "(format Excel par mail). En cas d'acceptation : passage à l'intention "
    "de programmation. En cas de refus : annulation de la demande. "
    "(Correction restitution DC 24/05/2026 — auparavant en étape 17, "
    "désormais en étape 8 juste après la proposition à la DVR.)"
)

# Nouvelles étapes à insérer
NEW_STEP_ELABORATION = {
    "order": 7,
    "title": "Élaboration du devis chiffré par la DVR",
    "description": (
        "La DVR élabore le devis en fonction des coûts (heure de vol DPD), "
        "du temps de vol (DOA), de la disponibilité appareil (DMRA via IMS), "
        "des taxes (extraites de la Suite Altéa), du nombre de passagers et "
        "du type d'appareil. Devis créé manuellement sur tableau Excel : "
        "majoration manuelle des coûts, formules de calcul Excel pour le "
        "temps de vol, double ou triple check par collègue / chef de "
        "département / sous-directeur charter. "
        "Durée : 10-15 min si toutes les données sont disponibles, 2-3 jours "
        "sinon. En urgence, devis estimatifs (sans retour DPD/DOA) avec "
        "moyenne réseau. "
        "Erreur humaine possible, impact financier majeur sur un volume "
        "croissant de vols charter."
    ),
    "step_type": "MANUAL",
    "actor_role": "Cadre Commercial / Sous-directeur Charter",
    "data_inputs": (
        "Coût heure de vol (DPD), temps de vol (DOA), disponibilité appareil "
        "(DMRA via IMS), taxes émission (Suite Altéa), nombre de passagers, "
        "destination, type d'appareil."
    ),
    "data_outputs": "Devis chiffré (tableau Excel) prêt à transmettre au client.",
    "interactions": (
        "Systèmes mobilisés : IMS (disponibilité), Suite Altéa Amadeus "
        "(taxes), Excel (calcul). Aucun outil de cotation dédié — "
        "tentative antérieure SD Systèmes non aboutie, nouvelle demande à "
        "l'ADSI en priorité basse."
    ),
    "problems": (
        "Erreur humaine possible car beaucoup de données en entrée et "
        "beaucoup de saisie manuelle sur Excel, très contraignant. "
        "Parfois les devis sont estimatifs pour les besoins urgents."
    ),
    "duration_estimate": "10-15 min (données OK) à 2-3 jours (données manquantes)",
    "next_steps": "[]",
}

NEW_STEP_ACCEPTATION = {
    "order": 9,
    "title": "Acceptation / Refus du devis par le client",
    "description": (
        "Le client retourne sa décision sur le devis transmis. "
        "Si acceptation : on passe à l'étape suivante (validation interne "
        "DVR puis diffusion intention de programmation). "
        "Si refus : la demande de proposition est annulée."
    ),
    "step_type": "DECISION",
    "actor_role": "Client + Cadre Commercial / Sous-directeur Charter (DVR)",
    "data_inputs": "Devis chiffré transmis au client (étape 8).",
    "data_outputs": (
        "Décision client : acceptation → intention de programmation ; "
        "refus → annulation de la demande."
    ),
    "interactions": "Échange mail / téléphone DVR ↔ client.",
    "problems": "",
    "duration_estimate": "1-7 jours",
    "next_steps": "[]",
}

# Mention Mass Mailing ERP HADGE à ajouter à l'étape Lancement (ex-13, devient 16)
LANCEMENT_OLD_ORDER = 13
LANCEMENT_NEW_ORDER = 16
LANCEMENT_MASS_MAILING_ADDENDUM = (
    "\n\n[Restitution DC 24/05/2026 — nihad bounab] : "
    "L'application Mass Mailing ERP HADGE (développée il y a 3 ans pour les "
    "opérations HADGE) permet l'émission de billets en 2-3 minutes sur des "
    "vols full capacity, à partir d'une liste passagers. Elle DOIT être "
    "étendue aux vols charters (caractéristique full capacity identique) "
    "afin de remplacer l'émission manuelle actuelle, source d'erreurs."
)


# ---------------------------------------------------------------- Helpers
def sql_lit(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v).replace("\\", "\\\\").replace("'", "''")
    return f"E'{s}'"


# ---------------------------------------------------------------- Phase A : LOCAL
con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()


def apply_local() -> dict:
    """Applique en local. Renvoie dict {process_id, did_apply}."""
    print("=== Phase A : LOCAL ===")
    proc = cur.execute(
        "SELECT id FROM cartography_process WHERE code=?", (PROCESS_CODE,)
    ).fetchone()
    if not proc:
        raise SystemExit(f"Process {PROCESS_CODE} introuvable en local")
    pid = proc["id"]
    print(f"  Process {PROCESS_CODE} id local = {pid}")

    # Vérifier idempotence : si une étape order=7 existe avec le titre cible, skip
    existing_elab = cur.execute(
        "SELECT id FROM cartography_processstep WHERE process_id=? AND title=?",
        (pid, NEW_STEP_ELABORATION["title"]),
    ).fetchone()
    if existing_elab:
        print(f"  ↺ Étape 'Élaboration du devis chiffré par la DVR' "
              f"déjà présente (id={existing_elab['id']}) — refonte déjà faite, skip")
        return {"process_id": pid, "did_apply": False}

    # Pré-check : l'étape 1424 doit avoir order=17 sur ce process
    existing = cur.execute(
        "SELECT id, process_id, \"order\", title FROM cartography_processstep WHERE id=?",
        (EXISTING_STEP_ID_LOCAL,),
    ).fetchone()
    if not existing or existing["process_id"] != pid or existing["order"] != EXISTING_STEP_OLD_ORDER:
        raise SystemExit(
            f"  ⚠️  L'étape id={EXISTING_STEP_ID_LOCAL} attendue à order=17 "
            f"sur process {pid} est introuvable ou déjà déplacée. "
            f"État trouvé : {dict(existing) if existing else 'aucun'}"
        )

    cur.execute("BEGIN")
    try:
        # 1) Décaler les étapes order 7..16 vers 10..19 (+3)
        cur.execute(
            'UPDATE cartography_processstep SET "order" = "order" + 3 '
            'WHERE process_id=? AND "order" BETWEEN 7 AND 16',
            (pid,),
        )
        n1 = cur.rowcount
        print(f"  ↪ Décalage +3 sur {n1} étapes (ex 7..16 → 10..19)")

        # 2) Déplacer l'étape 1424 (ex-17) → order=8 + mise à jour titre/description
        cur.execute(
            'UPDATE cartography_processstep SET '
            '"order"=?, title=?, description=? '
            'WHERE id=?',
            (EXISTING_STEP_NEW_ORDER, EXISTING_STEP_NEW_TITLE,
             EXISTING_STEP_NEW_DESC, EXISTING_STEP_ID_LOCAL),
        )
        print(f"  ↪ Étape id={EXISTING_STEP_ID_LOCAL} : order 17 → 8, titre mis à jour")

        # 3) Insertion des 2 nouvelles étapes (order=7 et order=9)
        for st in (NEW_STEP_ELABORATION, NEW_STEP_ACCEPTATION):
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
                    st["next_steps"], None, pid,
                ),
            )
            print(f"  ✚ Nouvelle étape order={st['order']} : {st['title']}")

        # 4) Mention Mass Mailing sur l'étape Lancement (maintenant order=16)
        lancement = cur.execute(
            'SELECT id, description FROM cartography_processstep '
            'WHERE process_id=? AND "order"=?',
            (pid, LANCEMENT_NEW_ORDER),
        ).fetchone()
        if lancement and "Mass Mailing ERP HADGE" not in (lancement["description"] or ""):
            new_desc = (lancement["description"] or "") + LANCEMENT_MASS_MAILING_ADDENDUM
            cur.execute(
                'UPDATE cartography_processstep SET description=? WHERE id=?',
                (new_desc, lancement["id"]),
            )
            print(f"  ↪ Étape Lancement (order=16, id={lancement['id']}) : "
                  f"ajout mention Mass Mailing ERP HADGE")
        elif lancement:
            print(f"  ↺ Étape Lancement : mention Mass Mailing déjà présente, skip")

        con.commit()
        print(f"\n  ✅ Phase A LOCAL : refonte appliquée")
        return {"process_id": pid, "did_apply": True}
    except Exception:
        con.rollback()
        raise


# ---------------------------------------------------------------- Phase B : SQL prod
def build_prod_sql() -> str:
    """Construit le SQL idempotent pour la prod (PostgreSQL).

    L'idempotence est assurée par :
      - Pré-check existence de l'étape 'Élaboration du devis chiffré...' → si oui, abort.
      - Pré-check que l'étape transmission au client existe encore à order=17.
    """
    chunks: list[str] = []
    chunks.append("-- =====================================================")
    chunks.append(f"-- Refonte process PROC-AA-DIVEX-02 (vols charter)")
    chunks.append(f"-- Source : {SOURCE}")
    chunks.append(f"-- Généré : {TS}")
    chunks.append("-- =====================================================")
    chunks.append("BEGIN;")
    chunks.append("")
    chunks.append("-- Pré-checks : abort si refonte déjà appliquée")
    chunks.append(
        "DO $$ "
        "DECLARE pid INT; "
        "DECLARE has_elab INT; "
        "DECLARE has_old_17 INT; "
        "BEGIN "
        f"  SELECT id INTO pid FROM cartography_process WHERE code='{PROCESS_CODE}'; "
        f"  IF pid IS NULL THEN RAISE EXCEPTION 'Process {PROCESS_CODE} absent en prod'; END IF; "
        f"  SELECT COUNT(*) INTO has_elab FROM cartography_processstep "
        f"   WHERE process_id=pid AND title={sql_lit(NEW_STEP_ELABORATION['title'])}; "
        f"  IF has_elab > 0 THEN "
        f"    RAISE NOTICE 'Refonte déjà appliquée (étape Élaboration présente) — rien à faire'; "
        f"    RETURN; "
        f"  END IF; "
        f"  SELECT COUNT(*) INTO has_old_17 FROM cartography_processstep "
        f"   WHERE process_id=pid AND \"order\"=17 "
        f"   AND title LIKE 'Transmission de la proposition Chiffr%'; "
        f"  IF has_old_17 = 0 THEN "
        f"    RAISE EXCEPTION 'État inattendu : étape \"Transmission de la proposition Chiffré...\" à order=17 introuvable'; "
        f"  END IF; "
        f""
        f"  -- 1) Décaler order 7..16 vers 10..19 (+3) "
        f"  UPDATE cartography_processstep SET \"order\" = \"order\" + 3 "
        f"   WHERE process_id=pid AND \"order\" BETWEEN 7 AND 16; "
        f""
        f"  -- 2) Déplacer l'étape order=17 vers order=8 + maj titre/desc "
        f"  UPDATE cartography_processstep SET "
        f"   \"order\"={EXISTING_STEP_NEW_ORDER}, "
        f"   title={sql_lit(EXISTING_STEP_NEW_TITLE)}, "
        f"   description={sql_lit(EXISTING_STEP_NEW_DESC)} "
        f"   WHERE process_id=pid AND \"order\"=17 "
        f"   AND title LIKE 'Transmission de la proposition Chiffr%'; "
        f""
        f"  -- 3) Insérer les 2 nouvelles étapes "
        f"  INSERT INTO cartography_processstep "
        f"   (\"order\", title, description, step_type, actor_role, data_inputs, "
        f"    data_outputs, interactions, problems, duration_estimate, next_steps, "
        f"    actor_structure_id, process_id) VALUES ("
        f"   {NEW_STEP_ELABORATION['order']}, "
        f"   {sql_lit(NEW_STEP_ELABORATION['title'])}, "
        f"   {sql_lit(NEW_STEP_ELABORATION['description'])}, "
        f"   {sql_lit(NEW_STEP_ELABORATION['step_type'])}, "
        f"   {sql_lit(NEW_STEP_ELABORATION['actor_role'])}, "
        f"   {sql_lit(NEW_STEP_ELABORATION['data_inputs'])}, "
        f"   {sql_lit(NEW_STEP_ELABORATION['data_outputs'])}, "
        f"   {sql_lit(NEW_STEP_ELABORATION['interactions'])}, "
        f"   {sql_lit(NEW_STEP_ELABORATION['problems'])}, "
        f"   {sql_lit(NEW_STEP_ELABORATION['duration_estimate'])}, "
        f"   {sql_lit(NEW_STEP_ELABORATION['next_steps'])}::jsonb, "
        f"   NULL, pid); "
        f""
        f"  INSERT INTO cartography_processstep "
        f"   (\"order\", title, description, step_type, actor_role, data_inputs, "
        f"    data_outputs, interactions, problems, duration_estimate, next_steps, "
        f"    actor_structure_id, process_id) VALUES ("
        f"   {NEW_STEP_ACCEPTATION['order']}, "
        f"   {sql_lit(NEW_STEP_ACCEPTATION['title'])}, "
        f"   {sql_lit(NEW_STEP_ACCEPTATION['description'])}, "
        f"   {sql_lit(NEW_STEP_ACCEPTATION['step_type'])}, "
        f"   {sql_lit(NEW_STEP_ACCEPTATION['actor_role'])}, "
        f"   {sql_lit(NEW_STEP_ACCEPTATION['data_inputs'])}, "
        f"   {sql_lit(NEW_STEP_ACCEPTATION['data_outputs'])}, "
        f"   {sql_lit(NEW_STEP_ACCEPTATION['interactions'])}, "
        f"   {sql_lit(NEW_STEP_ACCEPTATION['problems'])}, "
        f"   {sql_lit(NEW_STEP_ACCEPTATION['duration_estimate'])}, "
        f"   {sql_lit(NEW_STEP_ACCEPTATION['next_steps'])}::jsonb, "
        f"   NULL, pid); "
        f""
        f"  -- 4) Mention Mass Mailing sur l'étape Lancement (devenue order=16) "
        f"  UPDATE cartography_processstep "
        f"   SET description = COALESCE(description, '') || "
        f"       {sql_lit(LANCEMENT_MASS_MAILING_ADDENDUM)} "
        f"   WHERE process_id=pid AND \"order\"=16 "
        f"   AND title ILIKE '%lancement%' "
        f"   AND COALESCE(description, '') NOT LIKE '%Mass Mailing ERP HADGE%'; "
        f""
        f"END $$;"
    )
    chunks.append("")
    chunks.append("COMMIT;")
    chunks.append("")
    chunks.append("-- Vérifications post-sync")
    chunks.append(
        f"SELECT \"order\", title FROM cartography_processstep "
        f"WHERE process_id=(SELECT id FROM cartography_process WHERE code='{PROCESS_CODE}') "
        f"ORDER BY \"order\";"
    )
    return "\n".join(chunks)


def apply_prod(sql_text: str) -> None:
    out_sql = OUT_DIR / f"reorganize_divex02_{TS}.sql"
    out_sql.write_text(sql_text, encoding="utf-8")
    print(f"\n✅ SQL prod généré : {out_sql}  ({len(sql_text)} octets)")

    if not APPLY:
        print("\n=== DRY-RUN PROD ===")
        print("→ Inspecter le fichier SQL puis relancer avec --apply pour exécuter.")
        return

    remote_path = f"/tmp/reorganize_divex02_{TS}.sql"
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

print("\n=== Phase B : Génération SQL prod ===")
sql_text = build_prod_sql()
apply_prod(sql_text)
