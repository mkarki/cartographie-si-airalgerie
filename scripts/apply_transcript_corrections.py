"""Applique les corrections du transcript de restitution DC du 24/05/2026.

Process traités :
  1. PROC-WT-001    — recadrer : World Tracer = Exploitation, pas DC
  2. PROC-AA-DOS-05 — ajouter problématiques (clôture vols TNAO, Moscou, LDM)
  3. PROC-AA-DC-03  — ajouter volumétrie 9 000 appels/jour
  4. PROC-AA-DRM-06 — clarifier acteurs : DRM Financier e-commerce, pas DFC

Stratégie : on enrichit les champs `context`, `problems`, `recommendations` du
process (et certains `actor_role` des étapes pour DRM-06). On NE modifie PAS la
structure des étapes (titres / ordres). Le mermaid est régénéré ensuite.

Idempotence : marqueur "[Restitution DC 24/05/2026]" → skip si présent.

LOCAL UNIQUEMENT.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402
django.setup()

from cartography.models import Process, ProcessStep  # noqa: E402
from cartography.views import _rebuild_mermaid_from_steps  # noqa: E402
from django.db import transaction  # noqa: E402

MARKER = "[Restitution DC 24/05/2026]"


# ─────────────────────────────────────────────────────────────────────────
# PROC-WT-001 — World Tracer / Exploitation
# ─────────────────────────────────────────────────────────────────────────
WT001_CONTEXT_ADDENDUM = (
    f"\n\n{MARKER} Précisions Fiala (DCS) :\n"
    "- Ce process est piloté par la **Division Exploitation (DCS)** et non par la "
    "Division Commerciale. La DVR n'intervient que sur le **traitement des données "
    "passager** lorsque l'irrégularité a un impact commercial (réclamation, "
    "indemnisation, remboursement).\n"
    "- **Migration en cours** vers un accès HTTPS direct à World Tracer ; jusqu'à "
    "**octobre 2026**, l'accès se fait via la suite Altéa / DCS.\n"
    "- **Couverture incomplète** : certaines escales n'utilisent pas encore "
    "World Tracer et transmettent leurs réclamations par **TLX** vers la centrale. "
    "Le déploiement WordTracer dans toutes les escales est en cours."
)

WT001_PROBLEMS_ADDENDUM = (
    f"\n\n{MARKER} Problèmes confirmés en restitution :\n"
    "- Couverture WorldTracer hétérogène entre escales — certains sites passent "
    "encore par TLX manuel.\n"
    "- Cartographie initiale erronée : ce process avait été rattaché à la DVR "
    "alors qu'il relève de l'Exploitation. Key user à réaffecter."
)

WT001_RECOS_ADDENDUM = (
    f"\n\n{MARKER} Recommandations restitution :\n"
    "- **Réaffecter le key user** du process à la Division Exploitation (DCS).\n"
    "- **Accélérer le déploiement de WorldTracer** dans toutes les escales pour "
    "supprimer les transmissions TLX manuelles.\n"
    "- **Préparer la migration HTTPS** post-octobre 2026 (fin de l'intégration "
    "Altéa / DCS)."
)


# ─────────────────────────────────────────────────────────────────────────
# PROC-AA-DOS-05 — Datawarehouse Feeds
# ─────────────────────────────────────────────────────────────────────────
DOS05_CONTEXT_ADDENDUM = (
    f"\n\n{MARKER} Précisions Fiala (DCS) — restitution 24/05/2026 :\n"
    "- Le bon fonctionnement du process dépend de la **clôture correcte des vols** "
    "côté escale (saisie TNAO) et de la **transmission complète des messages "
    "LDM** (Load Distribution Message).\n"
    "- En cas d'escale opérée par un **DCS tiers** (cas notable : Moscou sous "
    "embargo, où les fournisseurs Amadeus refusent d'opérer), les feeds ne "
    "remontent pas au Datawarehouse — on travaille avec des données manquantes.\n"
    "- Pour les affréteurs / charter, l'affréteur peut imposer son équipage et "
    "ses adresses : les LDM ne sont alors pas transmis automatiquement aux "
    "adresses configurées et l'intégration devient **manuelle**.\n"
    "- Migration progressive en cours : déploiement du DCS Amadeus dans toutes "
    "les escales pour homogénéiser les données."
)

DOS05_PROBLEMS_ADDENDUM = (
    f"\n\n{MARKER} Problèmes bloquants identifiés en restitution :\n"
    "- **Intervention manuelle obligatoire** pour clôture des vols : dépendance "
    "à la saisie TNAO côté escale, **non automatisable** dans l'état actuel.\n"
    "- **Escales sous DCS tiers** (ex. Moscou — embargo) : les feeds ne "
    "remontent pas, les données sont absentes ou incomplètes.\n"
    "- **Messages LDM erronés ou absents** : conséquence directe sur AIMS et "
    "AMOS (l'AMOS n'a pas l'information exacte par rapport au vol et au temps "
    "de vol).\n"
    "- Pour les **vols affrétés**, la transmission des LDM passe par l'affréteur "
    "et n'arrive pas toujours sur les adresses configurées — intégration manuelle."
)

DOS05_RECOS_ADDENDUM = (
    f"\n\n{MARKER} Recommandations restitution :\n"
    "- **Déployer le DCS Amadeus** dans toutes les escales accessibles pour "
    "supprimer les transmissions hétérogènes (déploiement progressif déjà en cours).\n"
    "- **Sensibiliser les TNAO** à la clôture des vols à l'ATD (au take-off) — "
    "procédure déjà en place mais non systématique.\n"
    "- Pour les **escales sous embargo** (Moscou), **pas de solution automatique** "
    "possible à ce jour — à documenter comme cas hors-périmètre.\n"
    "- Pour les **affréteurs**, formaliser l'obligation contractuelle de "
    "transmission LDM aux adresses Air Algérie."
)


# ─────────────────────────────────────────────────────────────────────────
# PROC-AA-DC-03 — Appels entrants
# ─────────────────────────────────────────────────────────────────────────
DC03_CONTEXT_ADDENDUM = (
    f"\n\n{MARKER} Précisions nihad bounab — restitution 24/05/2026 :\n"
    "- **Volumétrie** : environ **9 000 appels par jour** sur le call center "
    "(volume variable selon saison et campagnes commerciales).\n"
    "- Le **temps d'attente** dépend directement du nombre d'agents en production. "
    "Plus il y a d'agents, plus le temps d'attente est réduit.\n"
    "- Les **plannings agents** sont gérés directement dans **Hermès**.\n"
    "- **Nouveau service activé en mai 2026** : Gestion du client fidèle — "
    "orientation directe vers le service Fidélisation dès la prise d'appel pour "
    "les clients du programme."
)

DC03_PROBLEMS_ADDENDUM = (
    f"\n\n{MARKER} Constats restitution :\n"
    "- Le temps d'attente augmente significativement à partir d'un certain seuil "
    "d'appels par rapport au nombre d'agents en production.\n"
    "- Pics d'activité saisonniers (HADGE, OMRA, été) et promotionnels qui "
    "saturent ponctuellement le service."
)

DC03_RECOS_ADDENDUM = (
    f"\n\n{MARKER} Recommandations restitution :\n"
    "- Optimiser la **prédiction des pics d'activité** à partir des historiques "
    "et métriques existants.\n"
    "- **Redimensionner dynamiquement les plannings** d'agents en fonction des "
    "pics prévus (HADGE, OMRA, campagnes, été).\n"
    "- Capitaliser sur le nouveau service Fidélité pour fluidifier la file "
    "d'attente principale."
)


# ─────────────────────────────────────────────────────────────────────────
# PROC-AA-DRM-06 — Comptabilité IBE
# ─────────────────────────────────────────────────────────────────────────
DRM06_CONTEXT_ADDENDUM = (
    f"\n\n{MARKER} Correction majeure nassim nassim — restitution 24/05/2026 :\n"
    "- Le **traitement des écarts de rapprochement** est réalisé par l'**équipe "
    "commerciale (DRM)**, **et non par la DFC**.\n"
    "- Rôles précis côté DRM : **Financier e-commerce** et **Responsable Payment** "
    "(sous-direction DRM). La DRM traite en amont toutes les anomalies, écarts et "
    "incohérences avant transmission à la comptabilité finale.\n"
    "- La **DFC** ne reçoit qu'un **dossier final déjà aligné** (balances "
    "mensuelles et trimestrielles). Pas de retour comptable de la DFC à la DRM "
    "sur le rapprochement journalier IBE.\n"
    "- Volume : l'IBE est le **point de vente le plus important** d'Air Algérie ; "
    "d'autres schémas comptables existent pour les agences (vente, comptabilité, "
    "transmission propre)."
)

DRM06_RECOS_ADDENDUM = (
    f"\n\n{MARKER} Recommandations restitution :\n"
    "- Confirmer dans la cartographie que les acteurs du traitement des écarts "
    "sont la **DRM Financier e-commerce / Responsable Payment** (pas la DFC).\n"
    "- Les autres schémas comptables agences (hors IBE) restent à cartographier "
    "séparément si nécessaire."
)


# ─────────────────────────────────────────────────────────────────────────
def append_if_missing(field_value: str | None, addendum: str) -> tuple[str, bool]:
    """Renvoie (nouvelle_valeur, modified)."""
    current = field_value or ""
    if MARKER in current:
        return current, False
    return current + addendum, True


CORRECTIONS = [
    {
        "code": "PROC-WT-001",
        "context": WT001_CONTEXT_ADDENDUM,
        "problems": WT001_PROBLEMS_ADDENDUM,
        "recommendations": WT001_RECOS_ADDENDUM,
    },
    {
        "code": "PROC-AA-DOS-05",
        "context": DOS05_CONTEXT_ADDENDUM,
        "problems": DOS05_PROBLEMS_ADDENDUM,
        "recommendations": DOS05_RECOS_ADDENDUM,
    },
    {
        "code": "PROC-AA-DC-03",
        "context": DC03_CONTEXT_ADDENDUM,
        "problems": DC03_PROBLEMS_ADDENDUM,
        "recommendations": DC03_RECOS_ADDENDUM,
    },
    {
        "code": "PROC-AA-DRM-06",
        "context": DRM06_CONTEXT_ADDENDUM,
        "problems": "",
        "recommendations": DRM06_RECOS_ADDENDUM,
    },
]


def apply_corrections():
    print("=== Application corrections transcript restitution DC 24/05/2026 ===\n")

    for corr in CORRECTIONS:
        try:
            proc = Process.objects.get(code=corr["code"])
        except Process.DoesNotExist:
            print(f"  ⚠️  {corr['code']} : introuvable, skip")
            continue

        with transaction.atomic():
            ctx, modif_ctx = append_if_missing(proc.context, corr["context"])
            pbm, modif_pbm = (proc.problems or "", False)
            if corr["problems"]:
                pbm, modif_pbm = append_if_missing(proc.problems, corr["problems"])
            rec, modif_rec = append_if_missing(proc.recommendations, corr["recommendations"])

            if not (modif_ctx or modif_pbm or modif_rec):
                print(f"  ↺ {corr['code']} : déjà corrigé (marqueur présent), skip")
                continue

            proc.context = ctx
            proc.problems = pbm
            proc.recommendations = rec
            proc.workflow_mermaid = _rebuild_mermaid_from_steps(proc)
            proc.ai_generated = False
            proc.save(update_fields=[
                "context", "problems", "recommendations",
                "workflow_mermaid", "ai_generated", "updated_at",
            ])

            changes = []
            if modif_ctx: changes.append("context")
            if modif_pbm: changes.append("problems")
            if modif_rec: changes.append("recommendations")
            print(f"  ✚ {corr['code']} : {', '.join(changes)} enrichis "
                  f"+ mermaid régénéré ({proc.steps.count()} étapes)")

    # Bonus pour DRM-06 : mettre à jour les actor_role qui mentionnent
    # "Ventes/Financier/Payments" ou "Financier" mais pas "DRM"
    print("\n=== Bonus DRM-06 : précision des actor_role ===")
    try:
        proc = Process.objects.get(code="PROC-AA-DRM-06")
        for step in proc.steps.all():
            ar = step.actor_role or ""
            lar = ar.lower()
            if ("financier" in lar or "payment" in lar or "vente" in lar) \
               and "drm" not in lar:
                new_ar = "DRM — Financier e-commerce / Responsable Payment"
                if new_ar != ar:
                    print(f"  ↪ Étape {step.order} : actor_role '{ar}' → '{new_ar}'")
                    step.actor_role = new_ar
                    step.save(update_fields=["actor_role"])
    except Process.DoesNotExist:
        pass

    print("\n✅ Corrections terminées (local).")


if __name__ == "__main__":
    apply_corrections()
