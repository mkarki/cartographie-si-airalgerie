"""Compteurs cartographie pour synchro avec le livrable Markdown."""
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from cartography.models import Process, Structure, System, DataFlow


def main() -> None:
    print(f"Systems    : {System.objects.count()}")
    print(f"Structures : {Structure.objects.count()}")
    print(f"DataFlows  : {DataFlow.objects.count()}")
    print(f"Processes  : {Process.objects.count()}")
    print(f"Process Air Algérie : {Process.objects.filter(code__startswith='PROC-AA-').count()}")

    print("\n=== Systems triés par structure ===")
    for s in System.objects.select_related("structure").order_by("structure__code", "code"):
        print(f"  {s.structure.code:8s} | {s.code:25s} | crit={s.criticality:8s} | {s.name[:55]}")


if __name__ == "__main__":
    main()
