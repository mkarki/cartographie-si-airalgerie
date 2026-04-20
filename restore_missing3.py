#!/usr/bin/env python3
"""Restaure les 3 réponses manquantes (Q56, Q57, Q58) dans la DB locale"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
BASE = os.path.dirname(os.path.abspath(__file__))
os.environ['DATABASE_URL'] = f"sqlite:///{os.path.join(BASE, 'db.sqlite3')}"
django.setup()

from cartography.models import Question

MISSING = {
    56: """La facturation est établie au terme de chacune des 04 périodes mensuelle via la plateforme IATA SIS "Simplified Invoicing and Settlement"
Le process est automatisé et procéde conformément aux règles IATA de proration en la matière MPA.SPA.MITA.BITA et aux régles et procédures de facturation contenues dans le RAM "Revenue Accounting Manual".""",
    57: """02 process:
- process ICH: les documents sont facturés via la plateforme SIS électronique IATA  et réglées par le méthode de compensation via ICH "IATA Clearing House"
- Process Bilatéral: les documents sont facturés via la plateforme SIS mais le règlement se fait via transfert bancaire de compte  à compte.""",
    58: """Rapprochement entre les données des fichiers BAR " Billing Analysis Reports" du BSP et les fichiers SLP4027 de RAPID.
Les écarts sont quasiment inexistants sauf pour les cas de documents manquants.
Ils sont régularisés comme suit :
Intégration dans RAPID dans le cas ou l'anomalie concerne RAPID
Emission d'ADM à l'agence BSP dans le cas où l'anomalie résulte d'une irrégularité chez l'agence BSP""",
}

updated = 0
for qid, answer in MISSING.items():
    try:
        q = Question.objects.get(id=qid)
        q.answer = answer
        q.is_answered = True
        q.save()
        updated += 1
        print(f"  Q{qid} restauree ({len(answer)} chars)")
    except Question.DoesNotExist:
        print(f"  Q{qid} introuvable")

print(f"\n{updated}/3 restaurees")
print(f"Total reponses en local: {Question.objects.exclude(answer='').count()}")
