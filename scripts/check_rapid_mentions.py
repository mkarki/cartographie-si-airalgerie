"""
Vérifie où ACCELYA / RAPID est mentionné dans la base locale :
- Systèmes ACCELYA*
- Process liés M2M aux systèmes ACCELYA*
- Process avec context/problems/recommendations mentionnant rapid/accelya
- Étapes de process mentionnant rapid/accelya

Usage:
    venv/bin/python scripts/check_rapid_mentions.py
"""
import os
import sys
import django

# Bootstrap Django
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from cartography.models import Process, System, ProcessStep  # noqa: E402


def section(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def main() -> None:
    section("Systèmes ACCELYA en base")
    sys_qs = System.objects.filter(code__icontains="accelya").order_by("code")
    if not sys_qs.exists():
        print("  (aucun)")
    for s in sys_qs:
        print(f"  {s.code:20s} | {s.name:45s} | criticité={s.criticality}")

    section("Process liés (M2M) à chaque système ACCELYA*")
    for s in sys_qs:
        procs = s.processes.all().order_by("code")
        print(f"  ▶ {s.code} ({procs.count()} process)")
        for p in procs:
            print(f"      - {p.code:28s} | {p.name}")

    section("Process mentionnant 'rapid' ou 'accelya' dans context / problems / recommendations")
    found = 0
    for p in Process.objects.all().order_by("code"):
        blob = " ".join([p.context or "", p.problems or "", p.recommendations or ""]).lower()
        hits = [k for k in ("rapid", "accelya") if k in blob]
        if hits:
            found += 1
            print(f"  - {p.code:28s} | {p.name[:55]:55s} | mots-clés={','.join(hits)}")
    if not found:
        print("  (aucun)")

    section("Process avec étapes mentionnant 'rapid' ou 'accelya'")
    grouped: dict[str, list[str]] = {}
    for ps in ProcessStep.objects.select_related("process").order_by("process__code", "order"):
        blob = " ".join([
            ps.title or "",
            ps.description or "",
            ps.interactions or "",
            ps.data_inputs or "",
            ps.data_outputs or "",
        ]).lower()
        if "rapid" in blob or "accelya" in blob:
            grouped.setdefault(ps.process.code, []).append(
                f"      → étape {ps.order}: {ps.title}"
            )
    if not grouped:
        print("  (aucune)")
    for code, lines in grouped.items():
        print(f"  ▶ {code}")
        for line in lines:
            print(line)

    section("Synthèse")
    print(f"  Systèmes ACCELYA*           : {sys_qs.count()}")
    print(f"  Process avec mention texte  : {found}")
    print(f"  Process avec mention étape  : {len(grouped)}")


if __name__ == "__main__":
    main()
