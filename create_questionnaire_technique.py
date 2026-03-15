#!/usr/bin/env python3
"""Crée le questionnaire 'Questions Techniques' et le lie à YOUCEF ACHIRA Abdellah."""
import os, sys, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from docx import Document
from cartography.models import Questionnaire, QuestionSection, Question, KeyUserAccess

DOC_PATH = "/Users/mohamedamine/Air Algérie/Questions Techniques — Par Système, Par Phase.docx"

# 1. Parse le docx
doc = Document(DOC_PATH)
sections, cur = [], None
for p in doc.paragraphs:
    t = p.text.strip()
    if not t or t.startswith("\u2501"):
        continue
    s = p.style.name if p.style else ""
    if s == "Heading 1" and "requis" in t.lower():
        cur = {"title": t, "q": []}
        sections.append(cur)
    elif s == "Heading 2":
        cur = {"title": t, "q": []}
        sections.append(cur)
    elif s == "Heading 3" and "question" not in t.lower():
        cur = {"title": t, "q": []}
        sections.append(cur)
    elif s == "List Paragraph" and cur:
        cur["q"].append(t)

sections = [s for s in sections if s["q"]]
print(f"Parsed: {len(sections)} sections")

# 2. Crée le questionnaire
q = Questionnaire.objects.create(
    system_name="Questions Techniques — Tous Systèmes",
    phase=1,
    priority_in_phase=99,
    editor="DSI",
    direction="DSI",
    key_users="YOUCEF ACHIRA Abdellah",
    key_users_backup="BOUKAIOU Ahlem",
    responsible="DEBAB NOUREDDINE",
    status="NOT_STARTED",
)
print(f"Questionnaire créé: pk={q.pk}")

# 3. Crée les sections et questions
total_q = 0
for i, sec in enumerate(sections):
    qs = QuestionSection.objects.create(
        questionnaire=q, title=sec["title"], order=i + 1
    )
    for j, qt in enumerate(sec["q"]):
        Question.objects.create(
            section=qs, number=f"Q{total_q + 1}", text=qt, order=j + 1
        )
        total_q += 1

print(f"{len(sections)} sections, {total_q} questions créées")

# 4. Crée l'accès key user lié à ce questionnaire
ka = KeyUserAccess.objects.create(
    questionnaire=q,
    name="YOUCEF ACHIRA Abdellah",
    email="youcef.achira@airalgerie.dz",
    is_active=True,
)
print(f"KeyUserAccess créé — Token: {ka.token}")
print(f"Lien: /key-user/?token={ka.token}")
print("DONE")
