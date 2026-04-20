#!/usr/bin/env python3
"""Restaure les réponses de la prod dans la DB locale via le backup JSON complet"""
import json, os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
BASE = os.path.dirname(os.path.abspath(__file__))
os.environ['DATABASE_URL'] = f"sqlite:///{os.path.join(BASE, 'db.sqlite3')}"
django.setup()

from cartography.models import Question

# Charger le backup complet
backup_path = os.path.join(BASE, 'backups', 'BACKUP_COMPLET_2026-04-06.json')
with open(backup_path, encoding='utf-8') as f:
    backup = json.load(f)

questions = backup.get('question', [])
answered = [q for q in questions if q.get('answer', '').strip()]
print(f"{len(answered)} reponses trouvees dans le backup (sur {len(questions)} questions)")

updated = 0
missing = 0
for a in answered:
    try:
        q = Question.objects.get(id=a['id'])
        q.answer = a['answer']
        q.is_answered = a['is_answered']
        q.notes = a.get('notes', '') or ''
        q.validation_status = a.get('validation_status', 'PENDING') or 'PENDING'
        q.validated_by = a.get('validated_by', '') or ''
        q.validation_comment = a.get('validation_comment', '') or ''
        q.auditor_comment = a.get('auditor_comment', '') or ''
        q.auditor_comment_by = a.get('auditor_comment_by', '') or ''
        q.save()
        updated += 1
    except Question.DoesNotExist:
        missing += 1
        print(f"  Q{a['id']} introuvable en local")
    except Exception as e:
        print(f"  Erreur Q{a['id']}: {e}")

print(f"\n{updated}/{len(answered)} reponses synchronisees ({missing} manquantes)")
print(f"Verification: {Question.objects.exclude(answer='').count()} questions avec reponse en local")
