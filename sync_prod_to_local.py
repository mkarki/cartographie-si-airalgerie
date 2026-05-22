"""
Synchronise les donnees de prod_data/ vers la BDD locale db.sqlite3 :

  - Reponses (cartography_question.answer)  : depuis prod_data/answers/*.json
    (les sous-modules Altea splittes en local sont laisses INTACTS)
  - Process metier                          : depuis prod_data/processes/*.json
    (extrait le titre depuis le HTML brut)

Backup automatique de la BDD avant modification.
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


def backup_db():
    bkp = str(DB) + f'.bak.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    shutil.copy2(DB, bkp)
    print(f'  Backup BDD : {bkp}')
    return bkp


def clean_html(s):
    s = re.sub(r'<[^>]+>', '', s or '')
    for k, v in [('&#x27;', "'"), ('&quot;', '"'), ('&amp;', '&'),
                 ('&lt;', '<'), ('&gt;', '>'), ('&nbsp;', ' ')]:
        s = s.replace(k, v)
    return ' '.join(s.split())


def sync_answers():
    """Pour chaque fichier prod_data/answers/*.json, met a jour les Question
    correspondantes dans la BDD locale. Ne touche pas aux questionnaires Altea
    splittes localement (eux sont sous prod_data/altea/)."""
    print('\n[1] Sync des reponses (hors Altea)...')
    answer_files = sorted((PROD / 'answers').glob('*.json'))
    if not answer_files:
        print('  Aucun fichier d\'answers trouve.')
        return 0

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    updated = 0
    skipped = 0
    for f in answer_files:
        data = json.loads(f.read_text(encoding='utf-8'))
        sys_name = data['system_name']
        nb_ans = data['answered_questions']
        for q in data['questions']:
            qid = q['question_id']
            answer = q.get('answer', '')
            if not answer:
                continue
            cur.execute(
                'UPDATE cartography_question SET answer=?, is_answered=1, '
                'validation_status=COALESCE(validation_status, ?) '
                'WHERE id=?',
                (answer, q.get('validation') or 'PENDING', qid))
            if cur.rowcount > 0:
                updated += 1
            else:
                skipped += 1
        # Mise a jour status questionnaire
        if nb_ans > 0:
            cur.execute(
                'UPDATE cartography_questionnaire SET status=? '
                'WHERE system_name=?',
                ('COMPLETED' if nb_ans == data['total_questions']
                 else 'IN_PROGRESS', sys_name))
    conn.commit()
    conn.close()
    print(f'  {updated} reponses synchronisees ({skipped} ignorees : qid absent en local)')
    return updated


def sync_altea_separately():
    """Pour Altea : on ne synchronise PAS dans la BDD (split local). On affiche
    juste un resume pour info."""
    print('\n[2] Altea : split local conserve, donnees prod stockees a part.')
    altea_files = sorted((PROD / 'altea').glob('*.json'))
    for f in altea_files:
        data = json.loads(f.read_text(encoding='utf-8'))
        print(f'  - {data["system_name"]:30s} {data["answered_questions"]:>2}/{data["total_questions"]} reponses (prod_data/altea/{f.name})')


def extract_process_title(html):
    """Le 1er <h1> est 'Air Algerie' (nom du site). Le 2eme est le vrai titre."""
    h1s = re.findall(r'<h1[^>]*>([^<]+)</h1>', html or '')
    for h in h1s:
        h = clean_html(h)
        if h and 'air alg' not in h.lower():
            return h
    # Fallback : depuis <title>NOM — Process - Air Algerie</title>
    m = re.search(r'<title>([^<]+?)\s*[—-]\s*Process', html or '', re.IGNORECASE)
    if m:
        return clean_html(m.group(1))
    return None


def extract_process_steps(html):
    """Extrait les etapes (h3) avec leur numero d'ordre."""
    steps = []
    for m in re.finditer(r'<h3[^>]*>([^<]+)</h3>', html or ''):
        title = clean_html(m.group(1))
        if title and title.lower() not in ('air algérie', 'air algerie'):
            steps.append(title)
    return steps


def fix_process_titles():
    """Met a jour les fichiers JSON des process avec le bon titre + les etapes."""
    print('\n[3] Correction des titres de process...')
    proc_dir = PROD / 'processes'
    fixed_files = []
    for f in sorted(proc_dir.glob('*.json')):
        data = json.loads(f.read_text(encoding='utf-8'))
        new_title = extract_process_title(data.get('html', ''))
        if new_title:
            steps = extract_process_steps(data['html'])
            data['title'] = new_title
            data['steps'] = steps
            # Renommer le fichier avec le bon slug
            slug = re.sub(r'[^a-zA-Z0-9]+', '_', new_title).strip('_').lower()[:50]
            new_name = f'{data["id"]:03d}_{slug}.json'
            new_path = proc_dir / new_name
            f.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            if new_path != f:
                f.rename(new_path)
            fixed_files.append((data['id'], new_title, len(steps)))
            print(f'  - process #{data["id"]:>2}  {new_title}  ({len(steps)} etapes)')
        else:
            print(f'  - process #{data["id"]:>2}  (titre non extrait)')
    return fixed_files


def sync_processes_to_db(fixed_files):
    """Met a jour les Process en BDD locale a partir des donnees prod."""
    print('\n[4] Sync des process dans la BDD locale...')
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('SELECT id, name FROM cartography_process')
    db_procs = {row[0]: row[1] for row in cur.fetchall()}
    updated = 0
    for pid, title, n_steps in fixed_files:
        if pid in db_procs:
            cur.execute('UPDATE cartography_process SET name=? WHERE id=?',
                        (title, pid))
            if cur.rowcount > 0:
                updated += 1
                print(f'  process #{pid} : "{db_procs[pid]}" -> "{title}"')
        else:
            print(f'  process #{pid} ABSENT en BDD locale ("{title}")')
    conn.commit()
    conn.close()
    print(f'  {updated} process mis a jour')


def main():
    if not PROD.exists():
        print(f'!!! {PROD} introuvable. Lance d\'abord fetch_prod_data.py.')
        return
    backup_db()
    sync_answers()
    sync_altea_separately()
    fixed = fix_process_titles()
    if fixed:
        sync_processes_to_db(fixed)
    print('\nOK Synchronisation terminee.')


if __name__ == '__main__':
    main()
