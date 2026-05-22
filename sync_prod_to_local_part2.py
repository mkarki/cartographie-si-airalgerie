"""
Sync prod -> local : partie 2

  A. Cree les process metier absents en local (ids 2, 3, 4, 5) avec :
     - Header (titre, description, structures liees, systemes lies)
     - Etapes (ordre, titre, type, description, acteur, systeme, duree, interaction)
  B. Synchronise les reponses du questionnaire Altea unifie de prod
     sur les 6 sous-modules locaux (le split a conserve les question_id,
     donc l'UPDATE par id dispatche tout naturellement).

Backup BDD avant toute modification.
"""
import json
import os
import re
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB = BASE / 'db.sqlite3'
PROD = BASE / 'prod_data'


def clean(s):
    s = re.sub(r'<[^>]+>', '', s or '')
    for k, v in [('&#x27;', "'"), ('&quot;', '"'), ('&amp;', '&'),
                 ('&lt;', '<'), ('&gt;', '>'), ('&nbsp;', ' ')]:
        s = s.replace(k, v)
    return ' '.join(s.split())


def backup_db():
    bkp = str(DB) + f'.bak.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    shutil.copy2(DB, bkp)
    print(f'  Backup BDD : {bkp}')


# =============================================================================
# B - Sync Altea
# =============================================================================

def sync_altea_answers():
    print('\n[B] Sync des 18 reponses Altea (dispatch auto par question_id)...')
    altea_file = PROD / 'altea' / '01_alt_a_r_servation.json'
    if not altea_file.exists():
        print('  ! prod_data/altea/01_alt_a_r_servation.json manquant')
        return 0
    data = json.loads(altea_file.read_text(encoding='utf-8'))

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    updated = 0
    for q in data['questions']:
        qid = q['question_id']
        ans = q.get('answer', '')
        if not ans:
            continue
        cur.execute(
            'UPDATE cartography_question SET answer=?, is_answered=1, '
            'validation_status=COALESCE(NULLIF(validation_status,""), ?) '
            'WHERE id=?',
            (ans, q.get('validation') or 'PENDING', qid))
        if cur.rowcount > 0:
            # Recuperer le sous-questionnaire local
            cur.execute("""SELECT q.system_name FROM cartography_questionnaire q
                           JOIN cartography_questionsection s ON s.questionnaire_id=q.id
                           JOIN cartography_question qu ON qu.section_id=s.id
                           WHERE qu.id=?""", (qid,))
            r = cur.fetchone()
            sub = r[0] if r else '?'
            print(f'  qid={qid:>3} -> {sub}')
            updated += 1

    # Recalcul du status des 6 sous-questionnaires
    altea_names = ['Altéa Réservation', 'Altéa Ticketing', 'Altéa Inventory',
                   'Altéa DCS', 'Altéa RMS', 'Amadeus Data Feeds']
    for name in altea_names:
        cur.execute("""SELECT q.id,
                              COUNT(qu.id),
                              SUM(CASE WHEN qu.answer != '' THEN 1 ELSE 0 END)
                       FROM cartography_questionnaire q
                       JOIN cartography_questionsection s ON s.questionnaire_id=q.id
                       JOIN cartography_question qu ON qu.section_id=s.id
                       WHERE q.system_name=?
                       GROUP BY q.id""", (name,))
        r = cur.fetchone()
        if r:
            qid_q, total, ans_count = r
            new_status = ('COMPLETED' if total > 0 and ans_count == total
                          else 'IN_PROGRESS' if ans_count > 0
                          else 'NOT_STARTED')
            cur.execute('UPDATE cartography_questionnaire SET status=? WHERE id=?',
                        (new_status, qid_q))
            print(f'  {name:30s} {ans_count}/{total} -> {new_status}')

    conn.commit()
    conn.close()
    print(f'  -> {updated} reponses Altea synchronisees')
    return updated


# =============================================================================
# A - Creation des process manquants
# =============================================================================

STEP_TYPE_MAP = {
    'AUTOMATED': 'AUTOMATED',
    'MANUAL': 'MANUAL',
    'INPUT': 'INPUT',
    'OUTPUT': 'OUTPUT',
    'DECISION': 'DECISION',
    'COMMUNICATION': 'COMMUNICATION',
}


def parse_process_html(html):
    """Extrait header + steps du HTML d'un /processes/<id>/."""
    # Titre : 2eme h1 (1er = 'Air Algerie')
    h1s = re.findall(r'<h1[^>]*>([^<]+)</h1>', html)
    title = next((clean(h) for h in h1s if 'air alg' not in clean(h).lower()), None)

    # Description du process : <p class="text-gray-400 text-sm mt-1"> juste apres le titre
    desc = ''
    if title:
        i = html.find(title)
        sub = html[i:i + 4000]
        m = re.search(r'<p class="text-gray-400 text-sm mt-1">(.*?)</p>',
                      sub, re.DOTALL)
        if m:
            desc = clean(m.group(1))

    # Structures (tags indigo) : "DMRA — Division ..."
    structures = []
    for m in re.finditer(
            r'bg-indigo-500/20[^>]*>.*?<i[^>]*data-lucide="building-2"[^>]*></i>([^<]+)</span>',
            html, re.DOTALL):
        txt = clean(m.group(1))
        # "CODE — Nom complet" -> on prend le code
        code_m = re.match(r'^([A-Z]{2,6})\s*[—-]', txt)
        if code_m:
            structures.append(code_m.group(1))

    # Systemes (tags cyan) : "ACARS / HERMES"
    systems = []
    for m in re.finditer(
            r'bg-cyan-500/20[^>]*>.*?<i[^>]*data-lucide="server"[^>]*></i>([^<]+)</span>',
            html, re.DOTALL):
        systems.append(clean(m.group(1)))

    # Etapes : on parcourt les step-card
    steps = []
    cards = list(re.finditer(r'<div class="step-card[^"]*"[^>]*>(.*?)(?=<div class="step-card|<!-- /steps)',
                             html, re.DOTALL))
    if not cards:
        # Fallback : par h3
        for m in re.finditer(r'<h3[^>]*>([^<]+)</h3>(.{0,2500}?)(?=<h3|</div>\s*</div>\s*</div>\s*</div>)',
                             html, re.DOTALL):
            steps.append(parse_step(clean(m.group(1)), m.group(2), len(steps) + 1))
    else:
        for idx, m in enumerate(cards, 1):
            chunk = m.group(1)
            h3_m = re.search(r'<h3[^>]*>([^<]+)</h3>', chunk)
            if h3_m:
                steps.append(parse_step(clean(h3_m.group(1)), chunk, idx))

    return {
        'title': title,
        'description': desc,
        'structures': structures,
        'systems': systems,
        'steps': steps,
    }


def parse_step(title, chunk, order):
    # type (badge)
    t_m = re.search(r'step-type-badge\s+type-(\w+)', chunk)
    step_type = STEP_TYPE_MAP.get((t_m.group(1) if t_m else '').upper(), 'MANUAL')
    # description
    d_m = re.search(r'<p class="text-gray-400 text-sm mt-1">(.*?)</p>',
                    chunk, re.DOTALL)
    description = clean(d_m.group(1)) if d_m else ''
    # acteur
    a_m = re.search(r'<i[^>]*data-lucide="user"[^>]*></i>([^<]+)</span>', chunk)
    actor = clean(a_m.group(1)) if a_m else ''
    # systemes utilises (cyan)
    systems = [clean(m.group(1)) for m in re.finditer(
        r'text-cyan-400[^>]*>.*?<i[^>]*data-lucide="server"[^>]*></i>([^<]+)</span>',
        chunk, re.DOTALL)]
    # duree
    dur_m = re.search(r'<i[^>]*data-lucide="clock"[^>]*></i>([^<]+)</span>', chunk)
    duration = clean(dur_m.group(1)) if dur_m else ''
    # interaction
    int_m = re.search(
        r'<i[^>]*data-lucide="arrow-right-left"[^>]*></i>([^<]+)</div>', chunk)
    interaction = clean(int_m.group(1)) if int_m else ''
    return {
        'order': order,
        'title': title,
        'description': description,
        'step_type': step_type,
        'actor_role': actor,
        'systems_used': systems,
        'duration_estimate': duration,
        'interactions': interaction,
        'data_inputs': '',
        'data_outputs': '',
        'problems': '',
        'next_steps': '[]',
    }


def slug_code(title):
    """Genere un code court pour le process (max 50 chars)."""
    s = re.sub(r'[^a-zA-Z0-9]+', '_', title or '').strip('_').upper()[:50]
    return s or 'PROCESS'


def create_missing_processes():
    print('\n[A] Creation des process absents en local...')
    proc_files = sorted((PROD / 'processes').glob('*.json'))
    if not proc_files:
        print('  ! aucun fichier dans prod_data/processes/')
        return

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Chargement des FK
    cur.execute('SELECT id, code FROM cartography_structure')
    struct_by_code = {r[1]: r[0] for r in cur.fetchall()}
    cur.execute('SELECT id, name FROM cartography_system')
    sys_by_name = {r[1]: r[0] for r in cur.fetchall()}
    cur.execute('SELECT id FROM cartography_process')
    existing_ids = {r[0] for r in cur.fetchall()}

    now = datetime.now().isoformat()
    created = 0
    for f in proc_files:
        d = json.loads(f.read_text(encoding='utf-8'))
        pid = d['id']
        if pid in existing_ids:
            print(f'  process #{pid:>2} deja en local (skip)')
            continue
        parsed = parse_process_html(d['html'])
        if not parsed['title']:
            print(f'  process #{pid:>2} titre non extrait, skip')
            continue
        # Insert process avec id explicite
        cur.execute("""
            INSERT INTO cartography_process
              (id, name, code, description, context, category, status, problems,
               recommendations, workflow_json, workflow_mermaid, ai_generated,
               created_by, created_at, updated_at, source_questionnaire_id)
            VALUES (?, ?, ?, ?, '', 'METIER', 'DRAFT', '', '', '{}', '', 0,
                    'sync_prod', ?, ?, NULL)
        """, (pid, parsed['title'], slug_code(parsed['title']),
              parsed['description'], now, now))

        # Liens structures
        for code in parsed['structures']:
            sid = struct_by_code.get(code)
            if sid:
                cur.execute('INSERT INTO cartography_process_structures '
                            '(process_id, structure_id) VALUES (?, ?)',
                            (pid, sid))

        # Liens systemes
        sys_ids_for_proc = set()
        for name in parsed['systems']:
            sid = sys_by_name.get(name)
            if sid:
                cur.execute('INSERT INTO cartography_process_systems '
                            '(process_id, system_id) VALUES (?, ?)',
                            (pid, sid))
                sys_ids_for_proc.add(sid)

        # Etapes
        for st in parsed['steps']:
            cur.execute("""
                INSERT INTO cartography_processstep
                  ("order", title, description, step_type, actor_role,
                   data_inputs, data_outputs, interactions, problems,
                   duration_estimate, next_steps, actor_structure_id, process_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?)
            """, (st['order'], st['title'], st['description'], st['step_type'],
                  st['actor_role'], st['data_inputs'], st['data_outputs'],
                  st['interactions'], st['problems'], st['duration_estimate'],
                  st['next_steps'], pid))
            step_id = cur.lastrowid
            for sname in st['systems_used']:
                sid = sys_by_name.get(sname)
                if sid:
                    cur.execute('INSERT INTO cartography_processstep_systems_used '
                                '(processstep_id, system_id) VALUES (?, ?)',
                                (step_id, sid))

        print(f'  + process #{pid:>2}  {parsed["title"]}')
        print(f'     {len(parsed["steps"])} etapes, '
              f'{len(parsed["structures"])} structures, '
              f'{len(parsed["systems"])} systemes')
        created += 1

    conn.commit()
    conn.close()
    print(f'  -> {created} process crees')


def main():
    if not PROD.exists():
        print(f'{PROD} introuvable')
        return
    backup_db()
    sync_altea_answers()
    create_missing_processes()
    print('\nOK termine.')


if __name__ == '__main__':
    main()
