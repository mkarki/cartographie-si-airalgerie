"""Affichage lisible du contenu du questionnaire AMOS + process DMRA pour rédaction."""
import json
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "LIVRABLES_PHASE_1" / "Restitutions_Directions" / "_data_dmra.json"
data = json.loads(D.read_text(encoding="utf-8"))

print("=" * 80)
print("QUESTIONNAIRE AMOS — toutes les réponses")
print("=" * 80)
q = data["questionnaires"][0]
print(f"Système : {q['system_name']} | Direction : {q['direction']} | Statut : {q['status']}")
print(f"Key users : {q['key_users']}")
print(f"Date entretien : {q['interview_date']}")
print(f"Notes entretien : {q['interview_notes']}")
print()
for sec in q["sections"]:
    print(f"\n## {sec['title']}")
    for qu in sec["questions"]:
        print(f"\n  [{qu['number']}] {qu['text']}")
        print(f"      → {qu['answer']}")
        if qu["notes"]:
            print(f"      Notes : {qu['notes']}")

print("\n" + "=" * 80)
print("PROCESS DMRA — détails")
print("=" * 80)
for p in data["processes"]:
    print(f"\n## [{p['code']}] {p['name']}")
    print(f"   Catégorie : {p['category']} | Statut : {p['status']} | Validation : {p['validation_status']}")
    print(f"   Description : {p['description'][:300]}")
    if p["problems"]:
        print(f"   Problèmes : {p['problems'][:300]}")
    if p["recommendations"]:
        print(f"   Recommandations : {p['recommendations'][:300]}")
    print(f"   Étapes ({len(p['steps'])}) :")
    for st in p["steps"]:
        print(f"     {st['ord']:2d}. [{st['step_type']}] {st['title']} — Acteur : {st['actor_role']}")

print("\n" + "=" * 80)
print("FLUX impliquant AMOS")
print("=" * 80)
for f in data["flows"]:
    print(f"\n[{f['source_code']} → {f['target_code']}] {f['name']}")
    print(f"   Fréquence : {f['frequency']} | Protocole : {f['protocol']} | Format : {f['format']}")
    print(f"   Automatisé : {bool(f['is_automated'])} | Critique : {bool(f['is_critical'])} | Volume : {f['volume']}")
    print(f"   Description : {f['description'][:300]}")
