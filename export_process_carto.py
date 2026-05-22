"""
Génère deux livrables et impacte la cartographie :
1. Exports_Cartographie/process_par_structure.md — vue tabulaire des 76 process
2. Exports_Cartographie/carto_impact_process.md   — delta entre process et carto
   (systèmes mentionnés mais non liés, flux suggérés, structures à compléter)

Idempotent : peut être relancé sans risque.
"""
import django
import os
import re
from collections import defaultdict

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from cartography.models import Process, System, Structure, DataFlow

EXPORT_DIR = "/Users/mohamedamine/Air Algérie/LIVRABLES_PHASE_1/Exports_Cartographie"

# Aliases pour détecter les mentions de systèmes dans le texte des process
SYSTEM_TOKENS = {
    # code : [aliases dans le texte]
    "ALTEA": ["altea", "altéa", "amadeus", "altea res", "altea inv", "altea dcs"],
    "AIMS": ["aims"],
    "AMOS": ["amos"],
    "SITATEX": ["sitatex", "sita gateway", "sita tex"],
    "WORLDTRACER": ["worldtracer", "world tracer", "world-tracer"],
    "ACARS": ["acars", "hermes"],
    "ACCELYA": ["accelya", "rapid passagers", "rapid pax", "rapid prism", "rapid"],
    "ACCELYA-DIST": ["bidt"],
    "BSPLINK": ["bsp link", "bsplink", "bsp-link"],
    "ATPCO": ["atpco"],
    "OAG": ["oag", "innovata"],
    "ZIMBRA": ["zimbra"],
    "GLPI": ["glpi"],
    "PORTAIL": ["portail ah", "liferay"],
    "SITEWEB": ["site web", "site internet", "ah.com"],
    "QPULSE": ["q-pulse", "qpulse", "q pulse"],
    "AGS": ["ags"],
    "JETPLAN": ["jetplan", "jet planner", "jetplanner"],
    "SKYBOOK": ["skybook", "sky book"],
    "EUROCONTROL": ["eurocontrol", "cfmu", "nm b2b"],
    "FLYSMART": ["flysmart"],
    "EEXAM": ["e-exam", "eexam", "exam"],
    "DOA-MAILING": ["mailing doa", "doa mailing"],
    "CALL-DOA": ["call doa", "call 360"],
    "EVALCOM": ["evalcom"],
    "POWERBI": ["power bi", "powerbi"],
    "QLIK": ["qlik"],
    "VOCALCOM": ["vocalcom", "hermes net", "hermes-net"],
    "EDOLEANCE": ["e-doleance", "edoleance"],
    "SAGE-FIN": ["sage finance"],
    "SAGE-STOCK": ["sage stock"],
    "DATAWINGS": ["datawings"],
    "BODET": ["bodet"],
    "BRINKS": ["brinks"],
    "BAC": ["bac amadeus"],
    "CTRL-PROG": ["controle programme", "ctrl-prog"],
    "DASH-PONCT-H": ["ponctualite historique"],
    "DASH-PONCT-J": ["ponctualite jour j", "ponctualite j"],
    "SUIVI-IRREG": ["suivi irreg", "irregularite"],
}


def detect_mentions(text: str) -> set:
    """Détecte les systèmes mentionnés dans un texte."""
    lower = text.lower()
    mentions = set()
    for code, aliases in SYSTEM_TOKENS.items():
        for alias in aliases:
            if re.search(rf"\b{re.escape(alias)}\b", lower):
                mentions.add(code)
                break
    return mentions


def category_label(c: str) -> str:
    return {
        "OPERATIONAL": "Opérationnel",
        "SUPPORT": "Support",
        "MANAGEMENT": "Management",
        "COMMERCIAL": "Commercial",
        "MAINTENANCE": "Maintenance",
        "FINANCE": "Finance",
        "HR": "RH",
        "IT": "IT",
        "OTHER": "Autre",
    }.get(c, c)


def status_label(s: str) -> str:
    return {
        "DRAFT": "Brouillon",
        "DOCUMENTED": "Documenté",
        "VALIDATED": "Validé",
        "TO_BE": "Cible",
    }.get(s, s)


# =============================================================================
# 1. Export : process_par_structure.md
# =============================================================================
def export_process_par_structure():
    out = []
    out.append("# Process métier Air Algérie — par structure")
    out.append("")
    out.append("> Export généré automatiquement depuis la plateforme `cartographie_si`.")
    out.append(f"> **Source** : 76 process Air Algérie collectés via canevas key users (mai 2026)")
    out.append("> **Statut workflow** : ✅ tous générés (IA Claude Sonnet 4.5)")
    out.append("")
    out.append("---")
    out.append("")

    structures = Structure.objects.order_by("code")
    for struct in structures:
        processes = Process.objects.filter(
            structures=struct,
            code__startswith="PROC-AA-",
        ).prefetch_related("systems", "structures").order_by("code")
        if not processes.exists():
            continue
        out.append(f"## {struct.code} — {struct.name}")
        out.append("")
        out.append(f"**Nombre de process** : {processes.count()}")
        out.append("")
        out.append("| Code | Nom | Catégorie | Systèmes | Workflow |")
        out.append("|---|---|---|---|:---:|")
        for p in processes:
            systems = ", ".join(sorted(s.code for s in p.systems.all())) or "—"
            wf = "✅" if p.workflow_mermaid else "—"
            name = p.name.replace("|", "/")[:80]
            out.append(f"| `{p.code}` | {name} | {category_label(p.category)} | {systems} | {wf} |")
        out.append("")

    # Processus non rattachés à une structure
    orphans = Process.objects.filter(
        code__startswith="PROC-AA-",
        structures__isnull=True,
    )
    if orphans.exists():
        out.append("## ⚠️ Process orphelins (sans structure)")
        out.append("")
        for p in orphans:
            out.append(f"- `{p.code}` — {p.name}")
        out.append("")

    out.append("---")
    out.append("")
    out.append("## Journal")
    out.append("")
    out.append("| Date | Action |")
    out.append("|---|---|")
    out.append(f"| {Process.objects.filter(code__startswith='PROC-AA-').order_by('-updated_at').first().updated_at:%Y-%m-%d %H:%M} | Dernière mise à jour workflow |")

    path = os.path.join(EXPORT_DIR, "process_par_structure.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"✓ {path}")
    return path


# =============================================================================
# 2. Analyse d'impact cartographie
# =============================================================================
def analyse_carto_impact():
    all_systems = {s.code for s in System.objects.all()}
    delta_per_process = []
    new_links = defaultdict(set)  # process_id -> set of system codes to link
    flow_suggestions = []  # (src, tgt, justif)

    processes = Process.objects.filter(
        code__startswith="PROC-AA-"
    ).prefetch_related("systems")

    for p in processes:
        text = f"{p.name}\n{p.description}\n{p.context}\n{p.problems}\n{p.recommendations}"
        mentions = detect_mentions(text)
        # Restreindre aux systèmes connus en base
        mentions = mentions & all_systems
        already_linked = {s.code for s in p.systems.all()}
        missing = mentions - already_linked
        if missing:
            delta_per_process.append((p, sorted(missing), sorted(already_linked)))
            for code in missing:
                new_links[p.id].add(code)

        # Heuristique flux : si 2 systèmes mentionnés simultanément ET texte
        # contient "envoie", "transmet", "génère vers", "alimente", "feed", "vers"
        if len(mentions) >= 2:
            patterns = [
                r"envoie\s+(?:un\s+|une\s+|le\s+|la\s+)?\w+",
                r"transmet",
                r"alimente",
                r"feed",
                r"export\w*\s+vers",
                r"push\w*\s+vers",
            ]
            for pat in patterns:
                if re.search(pat, text.lower()):
                    flow_suggestions.append((p, sorted(mentions)))
                    break

    # Compteurs systèmes
    sys_usage = defaultdict(int)
    for p in processes:
        for s in p.systems.all():
            sys_usage[s.code] += 1

    unused = sorted(all_systems - set(sys_usage.keys()))

    # Génération du rapport markdown
    out = []
    out.append("# Impact cartographie — synchronisation process ↔ systèmes ↔ flux")
    out.append("")
    out.append("> Rapport d'écart entre les **76 process métier Air Algérie** et la cartographie SI")
    out.append("> (systèmes et flux). Objectif : enrichir la carto avec les liens implicites.")
    out.append("")
    out.append("---")
    out.append("")

    # Section 1 : taux de couverture systèmes
    out.append("## 1. Utilisation des systèmes par les process")
    out.append("")
    out.append("| Système | # process | Statut |")
    out.append("|---|---:|:---:|")
    for code in sorted(all_systems, key=lambda c: (-sys_usage.get(c, 0), c)):
        cnt = sys_usage.get(code, 0)
        status = "🟢" if cnt >= 3 else "🟡" if cnt >= 1 else "🔴 inutilisé"
        out.append(f"| `{code}` | {cnt} | {status} |")
    out.append("")
    out.append(f"**Systèmes jamais référencés par un process** : {len(unused)}")
    if unused:
        out.append("")
        out.append(", ".join(f"`{c}`" for c in unused))
    out.append("")
    out.append("---")
    out.append("")

    # Section 2 : delta — systèmes mentionnés mais non liés
    out.append("## 2. Process avec systèmes mentionnés mais non rattachés (delta)")
    out.append("")
    out.append(f"**{len(delta_per_process)} process** présentent un delta entre les systèmes")
    out.append("explicitement liés et ceux mentionnés dans leur texte.")
    out.append("")
    if delta_per_process:
        out.append("| Process | Liés | À ajouter (delta) |")
        out.append("|---|---|---|")
        for p, missing, linked in delta_per_process[:30]:
            linked_str = ", ".join(f"`{c}`" for c in linked) or "—"
            missing_str = ", ".join(f"**`{c}`**" for c in missing)
            out.append(f"| `{p.code}` {p.name[:60]} | {linked_str} | {missing_str} |")
        if len(delta_per_process) > 30:
            out.append(f"| ... | ... | ({len(delta_per_process) - 30} autres) |")
    out.append("")
    out.append("---")
    out.append("")

    # Section 3 : suggestions flux
    out.append("## 3. Flux suggérés à partir du texte des process")
    out.append("")
    flow_seen = set()
    unique_flows = []
    for p, syscodes in flow_suggestions:
        for i, src in enumerate(syscodes):
            for tgt in syscodes[i + 1:]:
                key = tuple(sorted([src, tgt]))
                if key not in flow_seen:
                    flow_seen.add(key)
                    unique_flows.append((src, tgt, p.code, p.name))
    out.append(f"**{len(unique_flows)} paires** de systèmes potentiellement connectés (à arbitrer manuellement).")
    out.append("")
    if unique_flows:
        existing_pairs = set()
        for f in DataFlow.objects.select_related("source", "target"):
            existing_pairs.add(tuple(sorted([f.source.code, f.target.code])))
        out.append("| Paire | Process témoin | Flux existant ? |")
        out.append("|---|---|:---:|")
        for src, tgt, pcode, pname in unique_flows[:40]:
            exists = "✅" if tuple(sorted([src, tgt])) in existing_pairs else "❌ à créer"
            out.append(f"| `{src}` ↔ `{tgt}` | `{pcode}` {pname[:50]} | {exists} |")
        if len(unique_flows) > 40:
            out.append(f"| ... | ... | ({len(unique_flows) - 40} autres) |")
    out.append("")
    out.append("---")
    out.append("")

    # Section 4 : recommandations
    out.append("## 4. Actions recommandées")
    out.append("")
    out.append("1. **Relier automatiquement** les systèmes manquants détectés en §2 "
               "(script `enrich_process_systems.py` à venir)")
    out.append("2. **Arbitrer les paires de flux** en §3 — créer les DataFlow manquants si pertinent")
    out.append("3. **Auditer les systèmes inutilisés** (🔴 §1) : sont-ils réellement obsolètes "
               "ou simplement absents des canevas key users ?")
    out.append("")

    path = os.path.join(EXPORT_DIR, "carto_impact_process.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"✓ {path}")

    # Application automatique des liens manquants (action 1)
    print()
    print("=== Application des liens process ↔ systèmes manquants ===")
    sys_obj_by_code = {s.code: s for s in System.objects.all()}
    nb_added = 0
    for pid, codes in new_links.items():
        p = Process.objects.get(id=pid)
        for code in codes:
            sys_obj = sys_obj_by_code.get(code)
            if sys_obj:
                p.systems.add(sys_obj)
                nb_added += 1
    print(f"  → {nb_added} liens process↔système ajoutés")

    return path


if __name__ == "__main__":
    print("=== (b) Export process_par_structure.md ===")
    export_process_par_structure()
    print()
    print("=== (d) Analyse d'impact cartographique ===")
    analyse_carto_impact()
    print()
    print("Terminé.")
