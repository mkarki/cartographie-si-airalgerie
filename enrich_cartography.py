"""
Enrichit la cartographie en base avec les nouveaux flux et alias systèmes
révélés par les canevas LOUNAOUCI (DCS) et BENYELLES (DOA) — mai 2026.

Crée :
- Flux Altéa → SITATEX : détaille les sous-messages (MVT, LDM, ETL, PFS, UCM,
  DUO, FZFW, BSM) en complément du flux générique existant.
- Flux Altéa → PNRGOV (autorités frontière, DGSI).
- Flux Altéa → Datawarehouse (Datawarehouse Feeds — CM, FM).
- Flux JETPLAN → SKYBOOK (OFP — plans de vol techniques).

Idempotent : utilise update_or_create sur (source, target, name).
"""
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from cartography.models import DataFlow, System, Process
from django.db import transaction


# (source_code, target_code, name, frequency, protocol, format, is_automated,
#  is_critical, description)
NEW_FLOWS = [
    # --- Altéa → SITATEX : détail des messages opérationnels ---
    (
        "ALTEA", "SITATEX", "MVT — Mouvements vol",
        "REALTIME", "MESSAGE", "Type B / MVT", True, True,
        "Messages MVT (départ/arrivée/retard) générés par Altéa DCS et "
        "transmis via SITATEX aux structures concernées (CCO, escales, DOA).",
    ),
    (
        "ALTEA", "SITATEX", "LDM — Loadsheet message",
        "REALTIME", "MESSAGE", "Type B / LDM", True, True,
        "Loadsheet final transmise après bouclage du vol (poids, balance, "
        "passagers, fret).",
    ),
    (
        "ALTEA", "SITATEX", "ETL — Electronic Ticket List",
        "REALTIME", "MESSAGE", "Type B / ETL", True, False,
        "Liste passagers embarqués avec billets électroniques.",
    ),
    (
        "ALTEA", "SITATEX", "PFS — Passenger Final Sale",
        "REALTIME", "MESSAGE", "Type B / PFS", True, True,
        "Liste passagers NOSHOW / GOSHOW transmise après clôture du vol "
        "(intégration Rapid Pax pour la facturation).",
    ),
    (
        "ALTEA", "SITATEX", "UCM — ULD Control Message",
        "REALTIME", "MESSAGE", "Type B / UCM", True, False,
        "Suivi des ULD (Unit Load Devices) entre escales.",
    ),
    (
        "ALTEA", "SITATEX", "DUO — Deadload Uplift/Offload",
        "REALTIME", "MESSAGE", "Type B / DUO", True, False,
        "Mouvements de fret / deadload (chargement/déchargement).",
    ),
    (
        "ALTEA", "SITATEX", "FZFW — Forecast Zero Fuel Weight",
        "REALTIME", "MESSAGE", "Type B / FZFW", True, False,
        "Estimation du poids sans carburant (planification équilibrage).",
    ),
    (
        "ALTEA", "SITATEX", "BSM — Baggage Source Message",
        "REALTIME", "MESSAGE", "Type B / BSM", True, True,
        "Données bagages source (BSM) pour interconnexion avec World Tracer "
        "et systèmes de tri bagages aéroport.",
    ),
    (
        "ALTEA", "SITATEX", "API — Advance Passenger Information",
        "REALTIME", "MESSAGE", "Type B / API", True, True,
        "Données API passagers transmises aux autorités via passerelle SITATEX.",
    ),
    # --- Altéa → PNRGOV (autorités) ---
    # Si SITATEX joue rôle de gateway, on rattache à SITATEX. Sinon flux direct
    # vers un système externe — pour l'instant on l'attache à SITATEX qui sert
    # de gateway IATA.
    (
        "ALTEA", "SITATEX", "PNRGOV — Push autorités frontière",
        "REALTIME", "MESSAGE", "Type B / PNRGOV", True, True,
        "Push 0 PNRGOV vers DGSI / autorités frontière. Déclenchement "
        "automatique côté Altéa, transit via passerelle SITATEX.",
    ),
    # --- JETPLAN → SKYBOOK ---
    (
        "JETPLAN", "SKYBOOK", "OFP — Plans de vol techniques",
        "REALTIME", "API_REST", "OFP / XML", True, True,
        "Calcul et publication des plans de vol techniques (OFP) calculés "
        "par JetPlanner et consommés par SkyBook (DOA, BENYELLES) pour "
        "exploitation numérique en cockpit.",
    ),
]


# Flux Datawarehouse Feeds — pas de système DWH en base ; on documente comme
# flux entrant vers ACCELYA (Rapid Pax / DWH) qui consomme ces feeds pour le
# revenue accounting. Sinon, on peut le rattacher à un futur système DWH.
NEW_FLOWS.append(
    (
        "ALTEA", "ACCELYA", "Datawarehouse Feeds — CM/FM (XML/SFTP)",
        "DAILY", "FILE", "XML / SFTP", True, True,
        "Flux d'alimentation Datawarehouse depuis Altéa (modules Customer "
        "Management et Flight Management). Aujourd'hui FTP sur 192.168.104.8, "
        "à migrer vers SFTP (cf. réunion Amadeus 29/04/2026).",
    )
)


def main() -> None:
    sys_by_code = {s.code: s for s in System.objects.all()}
    created, updated, skipped = 0, 0, 0

    with transaction.atomic():
        for src_code, tgt_code, name, freq, proto, fmt, auto, crit, desc in NEW_FLOWS:
            src = sys_by_code.get(src_code)
            tgt = sys_by_code.get(tgt_code)
            if not src or not tgt:
                print(f"  SKIP   {src_code} -> {tgt_code} : système absent")
                skipped += 1
                continue
            flow, was_created = DataFlow.objects.update_or_create(
                source=src,
                target=tgt,
                name=name,
                defaults={
                    "description": desc,
                    "frequency": freq,
                    "protocol": proto,
                    "format": fmt,
                    "is_automated": auto,
                    "is_critical": crit,
                },
            )
            if was_created:
                created += 1
                marker = "+"
            else:
                updated += 1
                marker = "~"
            print(f"  {marker} [{flow.id:3d}] {src.code} -> {tgt.code} : {name}")

    print()
    print(f"OK   created={created}  updated={updated}  skipped={skipped}")
    print(f"Total flows en base : {DataFlow.objects.count()}")

    # Re-link BENYELLES OFP process to JETPLAN if needed
    print()
    print("=== Relink process BENYELLES OFP ===")
    jetplan = sys_by_code.get("JETPLAN")
    skybook = sys_by_code.get("SKYBOOK")
    for code in ("PROC-AA-DOA-11", "PROC-AA-DOA-12"):
        try:
            p = Process.objects.get(code=code)
        except Process.DoesNotExist:
            continue
        existing = list(p.systems.all())
        new_set = list(existing)
        if jetplan and jetplan not in new_set:
            new_set.append(jetplan)
        if skybook and skybook not in new_set and code == "PROC-AA-DOA-12":
            new_set.append(skybook)
        if set(new_set) != set(existing):
            p.systems.set(new_set)
            print(f"  ~ {code} : {[s.code for s in existing]} -> {[s.code for s in new_set]}")
        else:
            print(f"  = {code} : {[s.code for s in existing]} (inchangé)")


if __name__ == "__main__":
    main()
