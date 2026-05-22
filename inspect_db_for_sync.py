"""
Inspecte la BDD locale pour preparer la creation des process manquants
et le dispatch Altea. Lecture seule - pas de modification.
"""
import sqlite3
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB = BASE / 'db.sqlite3'

c = sqlite3.connect(DB).cursor()


def schema(table):
    print(f'\n=== {table} ===')
    c.execute(f'PRAGMA table_info({table})')
    for r in c.fetchall():
        print(f'  {r[1]:30s} {r[2]:15s} {"NOT NULL" if r[3] else ""}')


def sample(table, where='', limit=2):
    sql = f'SELECT * FROM {table}'
    if where:
        sql += f' WHERE {where}'
    sql += f' LIMIT {limit}'
    c.execute(sql)
    cols = [d[0] for d in c.description]
    for row in c.fetchall():
        print('  ', dict(zip(cols, row)))


# Schemas
for t in ('cartography_process', 'cartography_processstep'):
    schema(t)

print('\n=== Process existant (id=1) ===')
sample('cartography_process', 'id=1', 1)
print('\n=== ProcessStep existants pour process 1 ===')
sample('cartography_processstep', 'process_id=1', 3)

# Altea
print('\n=== Questionnaires Altea locaux ===')
c.execute("""SELECT id, system_name FROM cartography_questionnaire
             WHERE system_name LIKE 'Alt%' OR system_name LIKE '%Amadeus Data%'
             ORDER BY id""")
for r in c.fetchall():
    print(f'  qid={r[0]:>3}  {r[1]}')

print('\n=== Nombre de questions par questionnaire Altea ===')
c.execute("""SELECT q.id, q.system_name, COUNT(qu.id)
             FROM cartography_questionnaire q
             LEFT JOIN cartography_questionsection s ON s.questionnaire_id=q.id
             LEFT JOIN cartography_question qu ON qu.section_id=s.id
             WHERE q.system_name LIKE 'Alt%' OR q.system_name LIKE '%Amadeus Data%'
             GROUP BY q.id ORDER BY q.id""")
for r in c.fetchall():
    print(f'  qid={r[0]:>3}  {r[1]:35s} {r[2]:>3} questions')

print('\n=== question_ids des reponses prod Altea ===')
data = json.load(open('prod_data/altea/01_alt_a_r_servation.json'))
print(f'  prod : {len(data["questions"])} questions')
prod_qids = sorted(q['question_id'] for q in data['questions'])
print(f'  ids : {prod_qids}')

# Pour chacun de ces ids, on regarde s'il existe en local
print('\n=== Mapping prod_qid -> questionnaire local ===')
for qid in prod_qids:
    c.execute("""SELECT qu.id, qu.text, q.system_name
                 FROM cartography_question qu
                 JOIN cartography_questionsection s ON qu.section_id=s.id
                 JOIN cartography_questionnaire q ON s.questionnaire_id=q.id
                 WHERE qu.id=?""", (qid,))
    r = c.fetchone()
    if r:
        print(f'  qid={qid:>3} -> "{r[2][:30]}"  Q: {r[1][:60]}...')
    else:
        print(f'  qid={qid:>3} -> ABSENT en local')

# Process manquants
print('\n=== Process manquants en local ===')
c.execute('SELECT id FROM cartography_process')
existing = {r[0] for r in c.fetchall()}
prod_ids = [1, 2, 3, 4, 5]
missing = sorted(set(prod_ids) - existing)
print(f'  IDs prod absents en local : {missing}')
