"""URGENT — Restauration locale des 19 étapes refondues de PROC-AA-DIVEX-02.

L'IA a écrasé nos 19 étapes (refonte restitution 24/05/2026) en 14 étapes
Claude-generated. On reconstruit l'état "post-refonte" :

  - Étapes 1-6 + 10-19  : 16 étapes originales du manuel processus (récupérées
    depuis la prod via /tmp/divex02_prod_steps.json). Ordres 7..16 prod → 10..19.
  - Étapes 7, 8, 9      : 3 nouvelles étapes issues de la refonte 24/05/2026
                          (élaboration devis / transmission client / acceptation).
  - Étape 16 (Lancement) : mention Mass Mailing ERP HADGE ajoutée.

Régénération du workflow_mermaid via _rebuild_mermaid_from_steps (statique, pas
d'IA). Repasse ai_generated=False.

Bonus : régénère aussi le mermaid de tous les autres process modifiés aujourd'hui
(24/05/2026) en gardant leurs étapes telles quelles (séance live + IA).

LOCAL UNIQUEMENT — la prod n'est pas touchée.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402
django.setup()

from cartography.models import Process, ProcessStep  # noqa: E402
from cartography.views import _rebuild_mermaid_from_steps  # noqa: E402
from django.db import transaction  # noqa: E402


PROD_STEPS_PATH = Path("/tmp/divex02_prod_steps.json")
PROCESS_CODE = "PROC-AA-DIVEX-02"

# Les 3 nouvelles étapes de la refonte 24/05/2026 (cf. reorganize_divex02.py)
NEW_STEPS_REFONTE = [
    {
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
        "next_steps": [],
    },
    {
        "order": 8,
        "title": "Transmission du devis chiffré au client par la DVR",
        "description": (
            "Le devis chiffré élaboré par la DVR est transmis au client final "
            "(format Excel par mail). En cas d'acceptation : passage à l'intention "
            "de programmation. En cas de refus : annulation de la demande. "
            "(Correction restitution DC 24/05/2026 — auparavant en étape 17, "
            "désormais en étape 8 juste après la proposition à la DVR.)"
        ),
        "step_type": "OUTPUT",
        "actor_role": "Cadre Commercial/Sous directeur charter",
        "data_inputs": "Devis chiffré finalisé (étape 7).",
        "data_outputs": "Devis chiffré transmis au client par mail.",
        "interactions": "Mail / Excel.",
        "problems": "",
        "duration_estimate": "2 jours",
        "next_steps": [],
    },
    {
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
        "next_steps": [],
    },
]

LANCEMENT_MASS_MAILING_ADDENDUM = (
    "\n\n[Restitution DC 24/05/2026 — nihad bounab] : "
    "L'application Mass Mailing ERP HADGE (développée il y a 3 ans pour les "
    "opérations HADGE) permet l'émission de billets en 2-3 minutes sur des "
    "vols full capacity, à partir d'une liste passagers. Elle DOIT être "
    "étendue aux vols charters (caractéristique full capacity identique) "
    "afin de remplacer l'émission manuelle actuelle, source d'erreurs."
)


def restore_divex02():
    """Restaure les 19 étapes de PROC-AA-DIVEX-02."""
    print("=== Restauration PROC-AA-DIVEX-02 ===")

    if not PROD_STEPS_PATH.exists():
        raise SystemExit(
            f"Fichier {PROD_STEPS_PATH} introuvable. Re-exécuter le dump prod d'abord."
        )

    prod_steps = json.loads(PROD_STEPS_PATH.read_text())
    if len(prod_steps) != 16:
        raise SystemExit(
            f"Attendu 16 étapes prod, trouvé {len(prod_steps)}. Abort."
        )
    print(f"  Source : {len(prod_steps)} étapes originales du manuel processus (prod)")

    proc = Process.objects.get(code=PROCESS_CODE)
    print(f"  Process : {proc.code} (id={proc.id}, {proc.steps.count()} étapes IA actuellement)")

    with transaction.atomic():
        # 1) Supprimer les 14 étapes IA actuelles
        n_deleted = proc.steps.all().delete()[0]
        print(f"  🗑  {n_deleted} étapes IA supprimées")

        # 2) Insérer les 16 étapes prod avec les ordres FINAUX (1-6, puis 10-19)
        for s in prod_steps:
            old_order = s["order"]
            new_order = old_order if old_order <= 6 else old_order + 3
            # parser next_steps (jsonb→string via COPY)
            try:
                next_steps = json.loads(s.get("next_steps") or "[]")
            except json.JSONDecodeError:
                next_steps = []

            desc = s.get("description") or ""
            # Mention Mass Mailing sur l'étape Lancement (ex-13, devient 16)
            if old_order == 13 and "Mass Mailing ERP HADGE" not in desc:
                desc = desc + LANCEMENT_MASS_MAILING_ADDENDUM

            ProcessStep.objects.create(
                process=proc,
                order=new_order,
                title=s.get("title") or "",
                description=desc,
                step_type=s.get("step_type") or "MANUAL",
                actor_role=s.get("actor_role") or "",
                data_inputs=s.get("data_inputs") or "",
                data_outputs=s.get("data_outputs") or "",
                interactions=s.get("interactions") or "",
                problems=s.get("problems") or "",
                duration_estimate=s.get("duration_estimate") or "",
                next_steps=next_steps,
            )
        print(f"  ✚ 16 étapes prod restaurées (ordres 1-6 + 10-19, dont Mass Mailing sur Lancement)")

        # 3) Insérer les 3 nouvelles étapes de la refonte (orders 7, 8, 9)
        for st in NEW_STEPS_REFONTE:
            ProcessStep.objects.create(
                process=proc,
                order=st["order"],
                title=st["title"],
                description=st["description"],
                step_type=st["step_type"],
                actor_role=st["actor_role"],
                data_inputs=st["data_inputs"],
                data_outputs=st["data_outputs"],
                interactions=st["interactions"],
                problems=st["problems"],
                duration_estimate=st["duration_estimate"],
                next_steps=st["next_steps"],
            )
            print(f"  ✚ Nouvelle étape order={st['order']} : {st['title']}")

        # 4) Régénérer le workflow_mermaid à partir des étapes (statique, pas d'IA)
        proc.refresh_from_db()
        proc.workflow_mermaid = _rebuild_mermaid_from_steps(proc)
        proc.ai_generated = False  # marqueur : restauré manuellement
        proc.save(update_fields=["workflow_mermaid", "ai_generated", "updated_at"])
        print(f"  🎨 workflow_mermaid régénéré ({len(proc.workflow_mermaid)} octets) — ai_generated=False")

    # Vérif
    proc.refresh_from_db()
    print(f"\n  Résultat : {proc.steps.count()} étapes finales :")
    for st in proc.steps.all().order_by("order"):
        marker = "🆕" if st.order in (7, 8, 9) else "  "
        print(f"    {marker} {st.order:>2}. {st.title}")


def rebuild_mermaids_for_session():
    """Régénère le mermaid de tous les autres process modifiés en séance aujourd'hui."""
    today = date.today()  # 2026-05-24
    print(f"\n=== Régénération mermaid des process modifiés le {today} ===")

    qs = Process.objects.filter(updated_at__date=today).exclude(code=PROCESS_CODE)
    count_done = 0
    for proc in qs.order_by("code"):
        if proc.steps.count() == 0:
            print(f"  ⊘  {proc.code} : aucune étape, skip")
            continue
        new_mermaid = _rebuild_mermaid_from_steps(proc)
        if new_mermaid == proc.workflow_mermaid:
            print(f"  =  {proc.code} : mermaid déjà à jour, skip")
            continue
        proc.workflow_mermaid = new_mermaid
        proc.save(update_fields=["workflow_mermaid", "updated_at"])
        print(f"  🎨 {proc.code} ({proc.steps.count()} étapes) : mermaid régénéré "
              f"({len(new_mermaid)} octets)")
        count_done += 1
    print(f"\n  {count_done} process re-mermaidés.")


if __name__ == "__main__":
    restore_divex02()
    rebuild_mermaids_for_session()
    print("\n✅ Restauration locale terminée. La prod n'a pas été touchée.")
