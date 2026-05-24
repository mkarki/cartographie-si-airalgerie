"""
Enrichit le process PROC-AA-DRM-10 (Etablissement des factures) pour expliciter
le rôle de ACCELYA RAPID en amont (Revenue Accounting) :
- context : ajout de la précision sur la chaîne RAPID -> ARD Web -> ERP
- recommendations : ajout d'une recommandation d'interface directe RAPID
- étape 3 (extraction ARD Web) : précision sur l'origine RAPID des données

Idempotent : marqueur texte "[RAPID-LINK]" pour éviter les doublons.
Cible : SQLite locale uniquement. Régénère le diagramme Mermaid statique.

Usage:
    venv/bin/python scripts/enrich_drm10_rapid.py
"""
import os
import sys
import django

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from cartography.models import Process, ProcessStep, System  # noqa: E402

MARKER = "[RAPID-LINK]"

CONTEXT_ADDITION = (
    "\n\n" + MARKER + " Précision restitution DC 24/05/2026 : "
    "les données comptables exploitées dans ce process proviennent en amont du "
    "**Revenue Accounting ACCELYA RAPID** (capture des ventes directes et indirectes, "
    "rapprochements automatisés par n° de billet, détection d'anomalies). "
    "ARD Web consolide les données issues de RAPID avant extraction manuelle pour "
    "constituer la facture. La facturation client elle-même reste manuelle (ERP-AH + Word)."
)

RECO_ADDITION = (
    "\n\n" + MARKER + " Vision cible (restitution 24/05/2026) : "
    "construire une **interface directe RAPID → ARD Web → ERP-AH** pour supprimer "
    "l'extraction manuelle, et industrialiser l'émission via templates standardisés "
    "alimentés par les données RAPID."
)

STEP3_DESC_ADDITION = (
    " " + MARKER + " ARD Web restitue ici les données issues du Revenue Accounting "
    "ACCELYA RAPID (ventes directes + indirectes, rapprochements automatiques)."
)

STEP3_INPUT_ADDITION = " ; données amont issues de ACCELYA RAPID (Revenue Accounting)"


def _rebuild_mermaid_from_steps(process: Process) -> str:
    steps = list(process.steps.all().order_by("order"))
    if not steps:
        return ""
    lines = ["flowchart TD"]
    prev = None
    for ps in steps:
        node_id = f"S{ps.order}"
        title = (ps.title or f"Étape {ps.order}").replace('"', "'")
        lines.append(f'    {node_id}["{ps.order}. {title}"]')
        if prev is not None:
            lines.append(f"    {prev} --> {node_id}")
        prev = node_id
    return "\n".join(lines)


def main() -> None:
    try:
        p = Process.objects.get(code="PROC-AA-DRM-10")
    except Process.DoesNotExist:
        print("[ERREUR] PROC-AA-DRM-10 introuvable")
        sys.exit(1)

    changed = False

    # Context
    if MARKER not in (p.context or ""):
        p.context = (p.context or "") + CONTEXT_ADDITION
        print("  [OK] context enrichi")
        changed = True
    else:
        print("  [SKIP] context déjà enrichi")

    # Recommendations
    if MARKER not in (p.recommendations or ""):
        p.recommendations = (p.recommendations or "") + RECO_ADDITION
        print("  [OK] recommendations enrichies")
        changed = True
    else:
        print("  [SKIP] recommendations déjà enrichies")

    if changed:
        p.save()

    # Étape 3 (Extraction ARD Web)
    step3 = p.steps.filter(order=3).first()
    if step3:
        s_changed = False
        if MARKER not in (step3.description or ""):
            step3.description = (step3.description or "") + STEP3_DESC_ADDITION
            s_changed = True
            print("  [OK] étape 3 description enrichie")
        if "RAPID" not in (step3.data_inputs or ""):
            step3.data_inputs = (step3.data_inputs or "") + STEP3_INPUT_ADDITION
            s_changed = True
            print("  [OK] étape 3 inputs enrichis")
        if s_changed:
            step3.save()
            # Lier le système ACCELYA à l'étape si pas déjà
            try:
                acc = System.objects.get(code="ACCELYA")
                if not step3.systems_used.filter(pk=acc.pk).exists():
                    step3.systems_used.add(acc)
                    print("  [OK] système ACCELYA lié à l'étape 3")
            except System.DoesNotExist:
                print("  [WARN] système ACCELYA introuvable")
        else:
            print("  [SKIP] étape 3 déjà enrichie")
    else:
        print("  [WARN] étape 3 introuvable")

    # Régénérer Mermaid (statique)
    mermaid = _rebuild_mermaid_from_steps(p)
    if mermaid:
        p.workflow_mermaid = mermaid
        p.ai_generated = False
        p.save(update_fields=["workflow_mermaid", "ai_generated"])
        print("  [OK] mermaid régénéré (statique)")

    print("\n=== État final ===")
    print(f"Process: {p.code} - {p.name}")
    print(f"Étapes : {p.steps.count()}")
    print(f"Systèmes liés (M2M process) : {[s.code for s in p.systems.all()]}")
    s3 = p.steps.filter(order=3).first()
    if s3:
        print(f"Étape 3 systèmes : {[s.code for s in s3.systems_used.all()]}")


if __name__ == "__main__":
    main()
