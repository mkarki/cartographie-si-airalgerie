#!/usr/bin/env python3
"""
Script de récupération des données de production depuis le HTML scrapé
et injection dans la base SQLite locale.
"""
import re
import json

# ═══════════════════════════════════════════════════════════════
# ÉTAPE 1 : Parser /tmp/questionnaires.html pour extraire les
#           statuts et progressions de chaque questionnaire
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("ÉTAPE 1 : Parsing du HTML scrapé /tmp/questionnaires.html")
print("=" * 60)

try:
    with open('/tmp/questionnaires.html', 'r') as f:
        html = f.read()
    print(f"Fichier chargé : {len(html)} caractères")
except FileNotFoundError:
    print("ERREUR: /tmp/questionnaires.html non trouvé !")
    exit(1)

# Split by system name headers: <h3 class="font-semibold text-lg">NAME</h3>
name_pattern = r'<h3 class="font-semibold text-lg">([^<]+)</h3>'
name_positions = [(m.start(), m.group(1).strip()) for m in re.finditer(name_pattern, html)]
print(f"Systèmes trouvés dans le HTML : {len(name_positions)}")

results = []
for idx, (pos, name) in enumerate(name_positions):
    # Get the chunk between this name and the next (or end)
    end_pos = name_positions[idx + 1][0] if idx + 1 < len(name_positions) else len(html)
    # Also look backwards ~500 chars for the status badge
    start_pos = max(0, pos - 500)
    chunk = html[start_pos:end_pos]
    
    # After the name: questions count, progress width, phase, direction
    after_name = html[pos:end_pos]
    
    q_m = re.search(r'(\d+)\s*/\s*(\d+)\s*questions', after_name)
    prog_m = re.search(r'style="width:\s*(\d+)%', after_name)
    phase_m = re.search(r'Phase\s+(\d)', chunk)
    dir_m = re.search(r'text-gray-500[^>]*>\s*([^<]*(?:DAG|DC|DG|DIVEX|DMRA|DSI|DSC|DOA|DOS|CCO|DRM|DVR|DFC|DRH|DAGP|RGF|DPD)[^<]*)', after_name)
    
    answered = int(q_m.group(1)) if q_m else 0
    total = int(q_m.group(2)) if q_m else 0
    progress = int(prog_m.group(1)) if prog_m else 0
    phase = int(phase_m.group(1)) if phase_m else 0
    direction = dir_m.group(1).strip() if dir_m else ''
    
    # Status: derive from actual data (most reliable)
    if answered > 0 and answered == total:
        status = 'COMPLETED'
    elif answered > 0:
        status = 'IN_PROGRESS'
    else:
        status = 'NOT_STARTED'
    
    results.append({
        'name': name,
        'phase': phase,
        'direction': direction,
        'status': status,
        'answered': answered,
        'total': total,
        'progress': progress,
    })

print(f"\nRésultats extraits du HTML :")
print(f"{'Système':<45} {'Phase':<5} {'Statut':<15} {'Questions':<15} {'Progress'}")
print("-" * 100)
total_answered_all = 0
completed_count = 0
in_progress_count = 0
for r in results:
    emoji = {'COMPLETED': '✅', 'IN_PROGRESS': '🔄', 'NOT_STARTED': '⏳'}.get(r['status'], '?')
    print(f"{r['name']:<45} P{r['phase']:<4} {emoji} {r['status']:<12} {r['answered']}/{r['total']:<10} {r['progress']}%")
    total_answered_all += r['answered']
    if r['status'] == 'COMPLETED':
        completed_count += 1
    elif r['status'] == 'IN_PROGRESS':
        in_progress_count += 1

print(f"\n📊 TOTAL : {len(results)} questionnaires, {completed_count} terminés, {in_progress_count} en cours, {total_answered_all} questions répondues")

# ═══════════════════════════════════════════════════════════════
# ÉTAPE 2 : Sauvegarder les résultats dans un JSON
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("ÉTAPE 2 : Sauvegarde JSON des données récupérées")
print("=" * 60)

output_file = '/Users/mohamedamine/Air Algérie/cartographie_si/recovered_production_data.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'source': '/tmp/questionnaires.html (scrapé le 28/03/2026 à ~20h33)',
        'total_questionnaires': len(results),
        'total_answered': total_answered_all,
        'completed': completed_count,
        'in_progress': in_progress_count,
        'questionnaires': results,
    }, f, ensure_ascii=False, indent=2)

print(f"Données sauvegardées dans : {output_file}")

# ═══════════════════════════════════════════════════════════════
# ÉTAPE 3 : Mettre à jour les statuts dans la base SQLite locale
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("ÉTAPE 3 : Mise à jour des statuts dans la base SQLite locale")
print("=" * 60)

import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')
print(f"Base de données : {db_path}")

if not os.path.exists(db_path):
    print("ERREUR: db.sqlite3 non trouvé !")
    exit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Lire les questionnaires existants
cur.execute("SELECT id, system_name, status FROM cartography_questionnaire")
db_qs = {row[1]: {'id': row[0], 'status': row[1]} for row in cur.fetchall()}
print(f"Questionnaires en base : {len(db_qs)}")

updated = 0
for r in results:
    if r['name'] in db_qs:
        q_id = db_qs[r['name']]['id']
        old_status = db_qs[r['name']]['status']
        new_status = r['status']
        if old_status != new_status:
            cur.execute("UPDATE cartography_questionnaire SET status = ? WHERE id = ?", (new_status, q_id))
            print(f"  ✅ {r['name']}: {old_status} → {new_status}")
            updated += 1
    else:
        # Fuzzy match
        for db_name in db_qs:
            if r['name'][:20].lower() in db_name.lower() or db_name[:20].lower() in r['name'].lower():
                q_id = db_qs[db_name]['id']
                old_status = db_qs[db_name]['status']
                new_status = r['status']
                if old_status != new_status:
                    cur.execute("UPDATE cartography_questionnaire SET status = ? WHERE id = ?", (new_status, q_id))
                    print(f"  ✅ {db_name} (match ~{r['name']}): {old_status} → {new_status}")
                    updated += 1
                break

conn.commit()
print(f"\n{updated} questionnaires mis à jour en base.")

# ═══════════════════════════════════════════════════════════════
# ÉTAPE 4 : Générer le rapport MD d'avancement avec les données
#           récupérées de la production
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("ÉTAPE 4 : Génération du rapport MD d'avancement")
print("=" * 60)

from datetime import datetime

now = datetime.now()
date_str = now.strftime('%d/%m/%Y à %Hh%M')

# Grouper par direction
by_direction = {}
it_systems = []
for r in results:
    d = r['direction'] or '(Non renseigné)'
    if d not in by_direction:
        by_direction[d] = []
    by_direction[d].append(r)
    if 'DSI' in d or 'technique' in r['name'].lower():
        it_systems.append(r)

# Grouper par phase
by_phase = {1: [], 2: [], 3: []}
for r in results:
    if r['phase'] in by_phase:
        by_phase[r['phase']].append(r)

lines = []
lines.append('# Rapport d\'avancement — Cartographie SI Air Algérie')
lines.append('')
lines.append(f'> Généré le **{date_str}** — Données récupérées de la production')
lines.append(f'> Source : scraping du dashboard questionnaires (28/03/2026)')
lines.append(f'> URL : https://cartographie-si-airalgerie.onrender.com/kpi/')
lines.append('')
lines.append('---')
lines.append('')

# Synthèse globale
total_q_count = sum(r['total'] for r in results)
total_a_count = sum(r['answered'] for r in results)
global_progress = int(total_a_count / total_q_count * 100) if total_q_count > 0 else 0

lines.append('## 1. Synthèse globale')
lines.append('')
lines.append('| Indicateur | Valeur |')
lines.append('|------------|--------|')
lines.append(f'| Systèmes inventoriés | **38** |')
lines.append(f'| Questionnaires total | **{len(results)}** |')
lines.append(f'| Questionnaires terminés | **{completed_count}** ({int(completed_count/len(results)*100)}%) |')
lines.append(f'| Questionnaires en cours | **{in_progress_count}** |')
lines.append(f'| Questionnaires non commencés | **{len(results) - completed_count - in_progress_count}** |')
lines.append(f'| Questions répondues | **{total_a_count}** / {total_q_count} (**{global_progress}%**) |')
lines.append(f'| Flux de données documentés | **73** |')
lines.append(f'| Échantillons collectés | **14** |')
lines.append('')

# Par phase
lines.append('---')
lines.append('')
lines.append('## 2. Avancement par phase')
lines.append('')

phase_labels = {1: 'Phase 1 — Critique 🔴', 2: 'Phase 2 — Important 🟠', 3: 'Phase 3 — Standard 🟢'}
for pnum in [1, 2, 3]:
    plist = by_phase.get(pnum, [])
    p_total = sum(r['total'] for r in plist)
    p_answered = sum(r['answered'] for r in plist)
    p_completed = sum(1 for r in plist if r['status'] == 'COMPLETED')
    p_in_progress = sum(1 for r in plist if r['status'] == 'IN_PROGRESS')
    p_not_started = sum(1 for r in plist if r['status'] == 'NOT_STARTED')
    p_progress = int(p_answered / p_total * 100) if p_total > 0 else 0
    progress_bar = '█' * (p_progress // 5) + '░' * (20 - p_progress // 5)
    
    lines.append(f'### {phase_labels[pnum]}')
    lines.append('')
    lines.append('| Indicateur | Valeur |')
    lines.append('|------------|--------|')
    lines.append(f'| Systèmes | {len(plist)} |')
    lines.append(f'| Terminés | **{p_completed}** |')
    lines.append(f'| En cours | {p_in_progress} |')
    lines.append(f'| Non commencés | {p_not_started} |')
    lines.append(f'| Questions répondues | {p_answered} / {p_total} (**{p_progress}%**) |')
    lines.append(f'| Progression | `{progress_bar}` {p_progress}% |')
    lines.append('')

# Par direction
lines.append('---')
lines.append('')
lines.append('## 3. Avancement par direction')
lines.append('')

for direction, qs_list in sorted(by_direction.items()):
    dir_total = sum(r['total'] for r in qs_list)
    dir_answered = sum(r['answered'] for r in qs_list)
    dir_progress = int(dir_answered / dir_total * 100) if dir_total > 0 else 0
    dir_completed = sum(1 for r in qs_list if r['status'] == 'COMPLETED')
    dir_in_progress = sum(1 for r in qs_list if r['status'] == 'IN_PROGRESS')
    dir_not_started = sum(1 for r in qs_list if r['status'] == 'NOT_STARTED')
    
    lines.append(f'### {direction}')
    lines.append('')
    lines.append(f'**{len(qs_list)} système(s)** — Progression : **{dir_progress}%** ({dir_answered}/{dir_total} questions) — ✅ {dir_completed} terminé(s), 🔄 {dir_in_progress} en cours, ⏳ {dir_not_started} non commencé(s)')
    lines.append('')
    lines.append('| Système | Phase | Questions | Progression | Statut |')
    lines.append('|---------|-------|-----------|-------------|--------|')
    
    for r in qs_list:
        phase_tag = {1: 'P1 🔴', 2: 'P2 🟠', 3: 'P3 🟢'}.get(r['phase'], f"P{r['phase']}")
        if r['status'] == 'COMPLETED':
            status = '✅ Terminé'
        elif r['status'] == 'IN_PROGRESS':
            status = f"🔄 En cours ({r['progress']}%)"
        else:
            status = '⏳ Non commencé'
        lines.append(f"| {r['name']} | {phase_tag} | {r['answered']}/{r['total']} | {r['progress']}% | {status} |")
    lines.append('')

# Systèmes IT
lines.append('---')
lines.append('')
lines.append('## 4. Systèmes IT (DSI) — Avancement des réponses techniques')
lines.append('')

if it_systems:
    it_total = sum(r['total'] for r in it_systems)
    it_answered = sum(r['answered'] for r in it_systems)
    it_progress = int(it_answered / it_total * 100) if it_total > 0 else 0
    lines.append(f'**{len(it_systems)} système(s) IT** — Progression : **{it_progress}%** ({it_answered}/{it_total} questions)')
    lines.append('')
    lines.append('| Système | Questions | Progression | Statut |')
    lines.append('|---------|-----------|-------------|--------|')
    for r in it_systems:
        if r['status'] == 'COMPLETED':
            status = '✅ Terminé'
        elif r['status'] == 'IN_PROGRESS':
            status = f"🔄 En cours ({r['progress']}%)"
        else:
            status = '⏳ Non commencé'
        lines.append(f"| {r['name']} | {r['answered']}/{r['total']} | {r['progress']}% | {status} |")
    lines.append('')

# Tableau complet
lines.append('---')
lines.append('')
lines.append('## 5. Tableau complet — Tous les systèmes')
lines.append('')
lines.append('| # | Système | Direction | Phase | Questions | Progression | Statut |')
lines.append('|---|---------|-----------|-------|-----------|-------------|--------|')

sorted_results = sorted(results, key=lambda r: (r['phase'], r['name']))
for i, r in enumerate(sorted_results, 1):
    phase_tag = {1: 'P1 🔴', 2: 'P2 🟠', 3: 'P3 🟢'}.get(r['phase'], f"P{r['phase']}")
    direction = r['direction'][:25] if r['direction'] else '—'
    if r['status'] == 'COMPLETED':
        status = '✅ Terminé'
    elif r['status'] == 'IN_PROGRESS':
        status = '🔄 En cours'
    else:
        status = '⏳ Non commencé'
    lines.append(f"| {i} | {r['name']} | {direction} | {phase_tag} | {r['answered']}/{r['total']} | {r['progress']}% | {status} |")

lines.append('')
lines.append('---')
lines.append('')
lines.append(f'*Rapport généré le {date_str} — Données récupérées du scraping production (28/03/2026) — Cartographie SI Air Algérie — Alpha Aero Systems*')

md_content = '\n'.join(lines)

report_path = '/Users/mohamedamine/Air Algérie/cartographie_si/RAPPORT_AVANCEMENT_CARTOGRAPHIE_SI.md'
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(md_content)

print(f"Rapport MD généré : {report_path}")
print(f"Taille : {len(md_content)} caractères, {len(lines)} lignes")

# ═══════════════════════════════════════════════════════════════
# RÉSUMÉ FINAL
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("RÉSUMÉ FINAL")
print("=" * 60)
print(f"✅ {len(results)} questionnaires récupérés du HTML")
print(f"✅ {completed_count} terminés, {in_progress_count} en cours")
print(f"✅ {total_answered_all} / {total_q_count} questions répondues ({global_progress}%)")
print(f"✅ Statuts mis à jour dans db.sqlite3 ({updated} changements)")
print(f"✅ Données JSON sauvegardées : recovered_production_data.json")
print(f"✅ Rapport MD généré : RAPPORT_AVANCEMENT_CARTOGRAPHIE_SI.md")
