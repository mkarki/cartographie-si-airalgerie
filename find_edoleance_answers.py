"""
Cherche les vraies reponses E-DOLEANCE partout :
  - BDD locale
  - Tous les backups JSON
  - Tous les fichiers JSONL d'export
  - Les fiches MD systemes
  - Le HTML scrape de prod
"""
import json
import os
import re
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parent
EDOL_QIDS = list(range(247, 258))  # 247..257 = questions fonctionnelles E-Doleance
TECH_QIDS = list(range(2722, 2740))  # questions techniques E-Doleance


def is_real_answer(s):
    if not s:
        return False
    s = s.strip()
    if not s:
        return False
    if s.lower() in ('pas encore de réponse', 'pas encore de reponse',
                     'pas de reponse', 'n/a', '-', '—', 'tbd'):
        return False
    if 'pas encore' in s.lower() and len(s) < 30:
        return False
    return True


def search_json(path):
    try:
        data = json.loads(Path(path).read_text(encoding='utf-8'))
    except Exception:
        return []
    found = []
    # Format Django backup : {'question': [...], ...}
    if isinstance(data, dict):
        qs = data.get('question') or data.get('questions') or []
    elif isinstance(data, list):
        qs = data
    else:
        return []
    for q in qs:
        if not isinstance(q, dict):
            continue
        qid = q.get('id') or q.get('pk')
        if qid in EDOL_QIDS or qid in TECH_QIDS:
            ans = q.get('answer') or q.get('fields', {}).get('answer', '')
            if is_real_answer(ans):
                found.append((qid, ans))
    return found


def search_jsonl(path):
    """Format Django dumpdata --format jsonl : 1 objet par ligne."""
    found = []
    try:
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                # Soit {'pk': X, 'fields': {...}} soit objet plat
                if 'fields' in obj:
                    qid = obj.get('pk')
                    fields = obj.get('fields', {})
                    ans = fields.get('answer', '')
                else:
                    qid = obj.get('id')
                    ans = obj.get('answer', '')
                if qid in EDOL_QIDS or qid in TECH_QIDS:
                    if is_real_answer(ans):
                        found.append((qid, ans))
    except Exception:
        return []
    return found


def search_db(db_path):
    if not os.path.exists(db_path):
        return []
    try:
        c = sqlite3.connect(db_path).cursor()
        all_qids = EDOL_QIDS + TECH_QIDS
        placeholders = ','.join('?' * len(all_qids))
        c.execute(f"SELECT id, answer FROM cartography_question WHERE id IN ({placeholders})",
                  all_qids)
        rows = c.fetchall()
        return [(qid, ans) for qid, ans in rows if is_real_answer(ans)]
    except Exception:
        return []


def search_text_file(path):
    """Pour fichiers MD : on extrait toutes les lignes contenant des reponses."""
    found = []
    try:
        text = Path(path).read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return []
    # On cherche des mentions explicites de E-Doleance + reponses formatees
    # Heuristique : chaque section "Q<n>" ou "Question X" suivie de la reponse
    if 'doléance' not in text.lower() and 'doleance' not in text.lower():
        return []
    # Extrait les blocs Q?: ... R: ...
    for m in re.finditer(
            r'(?:^|\n)\s*(?:Q\d+|Question\s*\d+|###?\s*\d+).*?\n(.{20,800}?)(?=\n\s*(?:Q\d+|Question|##)|\Z)',
            text, re.DOTALL):
        chunk = m.group(0)[:800]
        if is_real_answer(chunk):
            found.append(('?', chunk[:300].strip()))
    return found


# ----------------------------------------------------------------------
# Lance la recherche
# ----------------------------------------------------------------------

print('=' * 70)
print('Recherche des reponses E-DOLEANCE (qids fonctionnels 247-257 + techniques 2722+)')
print('=' * 70)

# 1. BDD principale
print('\n[1] BDD principale db.sqlite3')
hits = search_db(BASE / 'db.sqlite3')
for qid, ans in hits:
    print(f'    Q{qid}: {ans[:200]}')
print(f'    -> {len(hits)} reponses reelles')

# 2. Tous les backups db.sqlite3.bak.*
print('\n[2] Backups SQLite (db.sqlite3.bak.*)')
for f in sorted(BASE.glob('db.sqlite3.bak*')):
    hits = search_db(f)
    if hits:
        print(f'  {f.name}')
        for qid, ans in hits:
            print(f'    Q{qid}: {ans[:200]}')

# 3. JSON de backup
print('\n[3] Fichiers JSON de backup')
for json_path in BASE.rglob('*.json'):
    p = str(json_path)
    if 'venv' in p or 'node_modules' in p or '__pycache__' in p:
        continue
    if 'prod_data' in p:
        continue  # gere a part
    hits = search_json(json_path)
    if hits:
        print(f'  {json_path.relative_to(BASE)}')
        for qid, ans in hits:
            print(f'    Q{qid}: {ans[:200]}')

# 4. JSONL (exports Django)
print('\n[4] Fichiers JSONL (dumpdata)')
for jsonl in BASE.rglob('*.jsonl'):
    if 'venv' in str(jsonl):
        continue
    hits = search_jsonl(jsonl)
    if hits:
        print(f'  {jsonl.relative_to(BASE)}')
        for qid, ans in hits:
            print(f'    Q{qid}: {ans[:200]}')

# 5. prod_data
print('\n[5] prod_data/answers/23_e_dol_ance.json')
prod_file = BASE / 'prod_data' / 'answers' / '23_e_dol_ance.json'
if prod_file.exists():
    d = json.loads(prod_file.read_text(encoding='utf-8'))
    real = [(q['question_id'], q['answer']) for q in d['questions']
            if is_real_answer(q.get('answer', ''))]
    placeholders = [q['question_id'] for q in d['questions']
                    if not is_real_answer(q.get('answer', ''))]
    print(f'    {len(real)} reponses reelles, {len(placeholders)} placeholders')
    for qid, ans in real:
        print(f'    Q{qid}: {ans[:200]}')

# 6. Fiche MD
print('\n[6] fiches_systemes/Phase3_02_EDOLEANCE.md')
md = BASE / 'fiches_systemes' / 'Phase3_02_EDOLEANCE.md'
if md.exists():
    text = md.read_text(encoding='utf-8')
    # Extrait la section "Reponses au questionnaire" si elle existe
    print(f'    Taille : {len(text)} chars')
    # Cherche les blocs de reponses
    for m in re.finditer(r'#+\s*(.*[Qq]uestion.*|R[ée]ponse.*)\n+(.+?)(?=\n#|\Z)',
                         text, re.DOTALL):
        sect = m.group(1).strip()
        body = m.group(2).strip()
        if len(body) > 30:
            print(f'    [{sect[:50]}] {body[:300]}')
            print()

# 7. /tmp/form_*.html (vieux scrapes eventuels)
print('\n[7] /tmp/form_*.html (anciens scrapes)')
import glob
for f in sorted(glob.glob('/tmp/form_*.html')) + sorted(glob.glob('/tmp/*doleance*')):
    try:
        text = Path(f).read_text(encoding='utf-8', errors='ignore')
    except Exception:
        continue
    if 'doléance' not in text.lower() and 'doleance' not in text.lower():
        continue
    print(f'  {f} ({len(text)} bytes)')
    # Cherche les textareas avec contenu
    for m in re.finditer(
            r'name=["\']answer_(\d+)["\'][^>]*>(.+?)</textarea>',
            text, re.DOTALL):
        qid = int(m.group(1))
        ans = m.group(2).strip()
        if qid in EDOL_QIDS + TECH_QIDS and is_real_answer(ans):
            print(f'    Q{qid}: {ans[:200]}')

print('\n' + '=' * 70)
print('Recherche terminee.')
