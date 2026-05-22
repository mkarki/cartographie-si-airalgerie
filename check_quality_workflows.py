"""Vérification qualité d'un échantillon de 5 workflows IA."""
import django
import os
import random
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from cartography.models import Process


def main() -> None:
    qs = Process.objects.filter(code__startswith="PROC-AA-").exclude(workflow_mermaid="")
    random.seed(42)
    sample = random.sample(list(qs), 5)

    overall_ok = 0
    overall_total = 0

    for p in sample:
        print("=" * 78)
        print(f"{p.code} | {p.name}")
        print(f"Systèmes liés : {[s.code for s in p.systems.all()]}")
        mm = p.workflow_mermaid
        print(f"Workflow Mermaid ({len(mm)} chars), extrait :")
        print("-" * 40)
        # Affiche les 30 premières lignes
        for line in mm.splitlines()[:30]:
            print(line)
        if len(mm.splitlines()) > 30:
            print(f"... ({len(mm.splitlines()) - 30} lignes supplémentaires)")

        checks = {
            "Démarre par flowchart/graph": bool(re.match(r"^\s*(flowchart|graph)\s+", mm)),
            "Au moins 3 nœuds": len(re.findall(r"\[[^\]]+\]", mm)) >= 3,
            "Au moins 2 transitions -->": mm.count("-->") >= 2,
            "Équilibre crochets [ ]": mm.count("[") == mm.count("]"),
            "Pas de balise vide []": "[]" not in mm,
        }
        print("-" * 40)
        for label, ok in checks.items():
            overall_total += 1
            if ok:
                overall_ok += 1
            print(f"  {'✓' if ok else '✗'} {label}")
        print()

    print("=" * 78)
    print(f"BILAN : {overall_ok}/{overall_total} contrôles OK ({100 * overall_ok / overall_total:.0f} %)")


if __name__ == "__main__":
    main()
