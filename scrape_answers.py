#!/usr/bin/env python3
"""
Script pour scraper les réponses textuelles des questionnaires depuis la prod Render.
On utilise le token auditeur pour accéder à chaque formulaire et extraire les réponses.
"""
import re
import json
import subprocess
import time
import sqlite3
import os

AUDITOR_TOKEN = "oSE3uRQC5nPv5Bekf3ruh70rg-trgvyYFdqNyVBYPuU"
BASE_URL = "https://cartographie-si-airalgerie.onrender.com"
COOKIE_FILE = "/tmp/cookies_scrape.txt"
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.sqlite3")

# Systèmes qui avaient des réponses (récupérés du HTML scrapé)
SYSTEMS_WITH_ANSWERS = {
    "SAGE STOCK": {"answered": 13, "total": 13},
    "ATPCO": {"answered": 10, "total": 10},
    "SITE WEB AIR ALGÉRIE": {"answered": 11, "total": 11},
    "E-DOLÉANCE": {"answered": 11, "total": 11},
    "E-LEARNING E-EXAM PN": {"answered": 8, "total": 8},
    "DOA MAILING": {"answered": 7, "total": 7},
    "CALL DOA": {"answered": 7, "total": 7},
    "WORLD TRACER": {"answered": 2, "total": 11},
}

def curl(url, output_file=None):
    """Exécute un curl avec cookies"""
    cmd = ["curl", "-s", "-L", "-b", COOKIE_FILE, "-c", COOKIE_FILE, url]
    if output_file:
        cmd.extend(["-o", output_file])
        subprocess.run(cmd, capture_output=True)
        with open(output_file, "r") as f:
            return f.read()
    else:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout


def extract_answers_from_html(html):
    """Extrait les réponses des textareas, inputs value, et JSON embarqué"""
    answers = []

    # Méthode 1: Textareas avec contenu (answer_XXX)
    textarea_pattern = r'name=["\']answer_(\d+)["\'][^>]*>(.*?)</textarea>'
    for m in re.finditer(textarea_pattern, html, re.DOTALL):
        q_id = m.group(1)
        content = m.group(2).strip()
        if content:
            answers.append({"question_id": int(q_id), "answer": content, "source": "textarea"})

    # Méthode 2: Textareas dans l'autre sens (contenu puis name)
    textarea_pattern2 = r'<textarea[^>]*?>(.*?)</textarea>'
    names_pattern = r'name=["\']answer_(\d+)["\']'
    all_textareas = list(re.finditer(r'<textarea([^>]*)>(.*?)</textarea>', html, re.DOTALL))
    for m in all_textareas:
        attrs = m.group(1)
        content = m.group(2).strip()
        name_m = re.search(r'answer_(\d+)', attrs)
        if name_m and content:
            q_id = int(name_m.group(1))
            # Eviter les doublons
            if not any(a["question_id"] == q_id for a in answers):
                answers.append({"question_id": q_id, "answer": content, "source": "textarea2"})

    # Méthode 3: Divs/spans avec la réponse affichée (mode auditeur)
    # Le mode auditeur affiche les réponses dans des <p> ou <div> avec classe spéciale
    answer_divs = re.findall(r'class="[^"]*answer[^"]*"[^>]*>(.*?)</(?:div|p|span)>', html, re.DOTALL | re.IGNORECASE)
    for a in answer_divs:
        clean = re.sub(r'<[^>]+>', '', a).strip()
        if clean and len(clean) > 3:
            print(f"  [div] Found answer in div: {clean[:80]}...")

    # Méthode 4: JSON embarqué dans les scripts
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    for s in scripts:
        if 'answer' in s.lower():
            # Chercher des objets JSON avec des réponses
            json_matches = re.findall(r'\{[^{}]*"answer"[^{}]*\}', s)
            for jm in json_matches:
                try:
                    obj = json.loads(jm)
                    if obj.get("answer"):
                        answers.append({"question_id": obj.get("id", 0), "answer": obj["answer"], "source": "json"})
                except:
                    pass

    # Méthode 5: Inputs hidden avec les réponses
    hidden_pattern = r'<input[^>]*name=["\']answer_(\d+)["\'][^>]*value=["\']([^"\']+)["\']'
    for m in re.finditer(hidden_pattern, html):
        q_id = int(m.group(1))
        value = m.group(2).strip()
        if value and not any(a["question_id"] == q_id for a in answers):
            answers.append({"question_id": q_id, "answer": value, "source": "hidden_input"})

    # Méthode 6: Pre-filled content in any element after question text
    # Pattern: question text followed by answer content
    q_blocks = re.findall(r'question-text[^>]*>(.*?)</.*?answer[^>]*>(.*?)</', html, re.DOTALL | re.IGNORECASE)
    for qt, qa in q_blocks:
        clean_a = re.sub(r'<[^>]+>', '', qa).strip()
        if clean_a:
            print(f"  [block] Q: {qt[:50]}... A: {clean_a[:80]}...")

    return answers


def get_questionnaire_ids():
    """Récupère les IDs des questionnaires depuis la base locale"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, system_name FROM cartography_questionnaire ORDER BY id")
    qs = {row[1]: row[0] for row in cur.fetchall()}
    conn.close()
    return qs


print("=" * 70)
print("RÉCUPÉRATION DES RÉPONSES TEXTUELLES DEPUIS LA PRODUCTION")
print("=" * 70)

# Étape 1: Se connecter en tant qu'auditeur
print("\n[1] Connexion auditeur...")
curl(f"{BASE_URL}/auditor/?token={AUDITOR_TOKEN}")
time.sleep(1)

# Récupérer les IDs des questionnaires
q_ids = get_questionnaire_ids()
print(f"    {len(q_ids)} questionnaires en base locale")

# Étape 2: Scraper CHAQUE formulaire (pas seulement ceux avec réponses)
print("\n[2] Scraping de tous les formulaires...")
all_recovered = {}
total_answers_found = 0

for system_name, q_id in sorted(q_ids.items(), key=lambda x: x[1]):
    output_file = f"/tmp/form_{q_id}.html"
    url = f"{BASE_URL}/form/{q_id}/"

    print(f"\n  → [{q_id}] {system_name}...")
    html = curl(url, output_file)

    if not html or len(html) < 1000:
        print(f"    ⚠️  Page trop petite ({len(html) if html else 0} bytes) — possible erreur")
        continue

    file_size = len(html)
    textarea_count = html.count("<textarea")
    print(f"    📄 {file_size} bytes, {textarea_count} textareas")

    # Extraire les réponses
    answers = extract_answers_from_html(html)

    if answers:
        print(f"    ✅ {len(answers)} RÉPONSES TROUVÉES !")
        for a in answers:
            print(f"       Q{a['question_id']}: {a['answer'][:60]}... [{a['source']}]")
        all_recovered[system_name] = answers
        total_answers_found += len(answers)
    else:
        # Vérifier s'il y a du contenu non-vide quelque part
        non_empty = re.findall(r'<textarea[^>]*>(.+?)</textarea>', html, re.DOTALL)
        non_empty = [x.strip() for x in non_empty if x.strip()]
        if non_empty:
            print(f"    ⚠️  {len(non_empty)} textareas non-vides trouvées mais pas parsées:")
            for ne in non_empty:
                print(f"       → {ne[:80]}")
        else:
            # Check for any visible answer text in the page
            visible_answers = re.findall(r'bg-gray-700/30[^>]*>(.*?)</div>', html, re.DOTALL)
            visible_answers = [re.sub(r'<[^>]+>', '', v).strip() for v in visible_answers if len(re.sub(r'<[^>]+>', '', v).strip()) > 5]
            if visible_answers:
                print(f"    ⚠️  {len(visible_answers)} réponses visibles dans des divs:")
                for va in visible_answers[:5]:
                    print(f"       → {va[:80]}")

    time.sleep(0.5)  # Pas trop de requêtes

# Étape 3: Sauvegarder les résultats
print("\n" + "=" * 70)
print(f"RÉSULTAT: {total_answers_found} réponses textuelles récupérées")
print("=" * 70)

output_json = "/Users/mohamedamine/Air Algérie/cartographie_si/recovered_answers.json"
with open(output_json, "w", encoding="utf-8") as f:
    json.dump({
        "total_answers_found": total_answers_found,
        "systems": all_recovered,
    }, f, ensure_ascii=False, indent=2)
print(f"Sauvegardé dans: {output_json}")

# Étape 4: Si des réponses sont trouvées, les injecter dans la base locale
if total_answers_found > 0:
    print("\n[4] Injection des réponses dans la base locale...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    injected = 0
    for system_name, answers in all_recovered.items():
        for a in answers:
            q_id = a["question_id"]
            answer_text = a["answer"]
            cur.execute("UPDATE cartography_question SET answer = ?, is_answered = 1 WHERE id = ?", (answer_text, q_id))
            if cur.rowcount > 0:
                injected += 1
    conn.commit()
    conn.close()
    print(f"    ✅ {injected} réponses injectées dans db.sqlite3")
else:
    print("\n❌ Aucune réponse textuelle récupérée de la production.")
    print("   Les réponses étaient sur le filesystem éphémère de Render")
    print("   et ont été perdues lors du redéploiement.")
    print("\n   Systèmes qui avaient des réponses (compteurs récupérés) :")
    for name, info in SYSTEMS_WITH_ANSWERS.items():
        status = "✅ TERMINÉ" if info["answered"] == info["total"] else "🔄 EN COURS"
        print(f"   - {name}: {info['answered']}/{info['total']} {status}")

print("\n✅ Script terminé.")
