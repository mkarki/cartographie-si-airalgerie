#!/usr/bin/env python3
"""Importe les réponses prod du Q40 dans la DB locale."""
import os, sys, json, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from cartography.models import Questionnaire, QuestionSection, Question

d = json.load(open('/tmp/q40_prod.json'))
q40 = Questionnaire.objects.get(id=40)

imported = 0
not_found = 0
for s in d['sections']:
    try:
        local_sec = QuestionSection.objects.get(questionnaire=q40, order=s['order'])
    except QuestionSection.DoesNotExist:
        print(f"SKIP section order {s['order']}: pas en local")
        continue
    for q_data in s['questions']:
        if not q_data['answer'].strip():
            continue
        try:
            local_q = Question.objects.get(section=local_sec, number=q_data['number'])
        except Question.DoesNotExist:
            not_found += 1
            continue
        local_q.answer = q_data['answer']
        local_q.notes = q_data.get('notes', '') or ''
        local_q.validation_status = q_data.get('validation_status', 'PENDING')
        local_q.is_answered = True
        local_q.save()
        imported += 1

q40.status = d['status']
q40.save()

print(f"Importé : {imported} réponses")
print(f"Non trouvé : {not_found}")
print(f"Q40 local : {Question.objects.filter(section__questionnaire=q40).exclude(answer='').count()} réponses non vides")
print(f"Status Q40 : {q40.status}")
