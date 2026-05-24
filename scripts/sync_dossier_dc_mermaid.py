"""
Synchronise les diagrammes Mermaid du dossier de restitution DC avec la base locale.

- Lit `workflow_mermaid` pour chaque process clé du dossier.
- Insère/remplace une section §6.5 "Diagrammes Mermaid (extraits cartographie locale)"
  juste avant la section §7, encadrée par les marqueurs HTML
  <!-- BEGIN_MERMAID_DIAGRAMS --> / <!-- END_MERMAID_DIAGRAMS --> pour idempotence.

Usage:
    venv/bin/python scripts/sync_dossier_dc_mermaid.py
"""
import os
import sys
import django
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from cartography.models import Process  # noqa: E402

# Le dossier de restitution DC est maintenu à 2 emplacements (gardés en miroir) :
# 1. Hors repo (workspace utilisateur) — diffusion/lecture directe
# 2. Dans le repo git — versionnement et traçabilité
DOSSIERS = [
    Path("/Users/mohamedamine/Air Algérie/LIVRABLES_PHASE_1/Restitutions_Directions/DC/Dossier_Restitution_DC.md"),
    ROOT / "LIVRABLES_PHASE_1" / "Restitutions_Directions" / "DC" / "Dossier_Restitution_DC.md",
]

# Structures appartenant à la Division Commerciale (DC + sous-directions DVR + DRM)
DC_STRUCTURES = ["DC", "DVR", "DRM"]


def list_dc_processes() -> list[str]:
    """Retourne la liste ordonnée de tous les process liés à DC, DVR ou DRM."""
    qs = (
        Process.objects.filter(structures__code__in=DC_STRUCTURES)
        .distinct()
        .order_by("code")
    )
    return [p.code for p in qs]

BEGIN = "<!-- BEGIN_MERMAID_DIAGRAMS -->"
END = "<!-- END_MERMAID_DIAGRAMS -->"


def build_section() -> str:
    codes = list_dc_processes()
    lines = [
        BEGIN,
        "",
        "### 6.5 Diagrammes Mermaid des process DC *(extraits cartographie locale)*",
        "",
        f"> **{len(codes)} process** liés à la **Division Commerciale** (structures : "
        f"{', '.join(DC_STRUCTURES)}) — diagrammes générés depuis la base locale `cartographie_si`.",
        "> **Source de vérité** : champ `workflow_mermaid` du modèle `Process`.",
        "> Synchronisé automatiquement par `scripts/sync_dossier_dc_mermaid.py` "
        "(filtre dynamique : tous les process où DC, DVR ou DRM apparaît dans `structures`).",
        "",
    ]

    for code in codes:
        p = Process.objects.get(code=code)
        ai_flag = "🤖 généré IA" if p.ai_generated else "✍️ statique (étapes)"
        structs = ", ".join(s.code for s in p.structures.all().order_by("code"))
        lines.append(f"#### {code} — {p.name}")
        lines.append("")
        lines.append(
            f"- **Étapes** : {p.steps.count()} · **Statut diagramme** : {ai_flag} · "
            f"**Catégorie** : `{p.category}` · **Statut process** : `{p.status}`"
        )
        lines.append(f"- **Structures impactées** : {structs}")
        lines.append("")
        if p.workflow_mermaid:
            lines.append("```mermaid")
            lines.append(p.workflow_mermaid.strip())
            lines.append("```")
        else:
            lines.append("_Diagramme Mermaid non disponible._")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(END)
    return "\n".join(lines)


def _process_one(dossier: Path, section: str) -> str:
    if not dossier.exists():
        return "ABSENT"
    text = dossier.read_text(encoding="utf-8")
    if BEGIN in text and END in text:
        before, _, rest = text.partition(BEGIN)
        _, _, after = rest.partition(END)
        new_text = before + section + after
        action = "REMPLACÉE"
    else:
        marker = "\n## 7. "
        idx = text.find(marker)
        if idx < 0:
            return "MARKER_NOT_FOUND"
        new_text = text[:idx] + "\n" + section + "\n" + text[idx:]
        action = "INSÉRÉE"
    if new_text == text:
        return "UNCHANGED"
    dossier.parent.mkdir(parents=True, exist_ok=True)
    dossier.write_text(new_text, encoding="utf-8")
    return action


def main() -> None:
    section = build_section()
    codes = list_dc_processes()

    for dossier in DOSSIERS:
        result = _process_one(dossier, section)
        print(f"[{result:18s}] {dossier}")

    print(f"\n→ {len(codes)} diagrammes Mermaid synchronisés :")
    for c in codes:
        p = Process.objects.get(code=c)
        print(
            f"  - {c:25s} | {p.steps.count():2d} étapes | "
            f"{len(p.workflow_mermaid or ''):4d} chars | "
            f"{','.join(s.code for s in p.structures.all())}"
        )


if __name__ == "__main__":
    main()
