#!/usr/bin/env python3
"""
Génère un mail Word (.docx) personnalisé par destinataire via l'API Markpresso.
Chaque fichier contient le mail d'accès à la plateforme Cartographie SI.
"""

import requests
import os
import time

API_URL = "https://markpresso.pro/api/v1/convert/docx"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "mails_acces")
os.makedirs(OUTPUT_DIR, exist_ok=True)

STYLE = {
    "primaryColor": "#003366",
    "fontHeading": "Georgia",
    "fontBody": "Calibri",
    "companyName": "Air Algérie — Direction des Systèmes d'Information"
}

BASE_URL = "https://cartographie-si-airalgerie.onrender.com/access/?token="

# --- Liste des destinataires ---

destinataires = [
    # Administrateurs
    {
        "nom": "M. le PDG",
        "fichier": "Mail_PDG",
        "role": "Administrateur",
        "perimetre": "Vue complète sur l'ensemble des systèmes, questionnaires et KPI",
        "token": "O1rsN-PB1BKO8v6np1Bg0Bg6NoSBN00PkgutOn7G69M",
    },
    {
        "nom": "M. DOUMI Nabil",
        "fichier": "Mail_DOUMI_Nabil",
        "role": "Administrateur (Conseiller du PDG)",
        "perimetre": "Vue complète sur l'ensemble des systèmes, questionnaires et KPI",
        "token": "OaNymGx3ZeBWZTBxFqCd6CVuqcm_hEeuBNvFoJ7EnXo",
    },
    {
        "nom": "Mme la DAG",
        "fichier": "Mail_DAG",
        "role": "Administrateur (Division des Affaires Générales)",
        "perimetre": "Vue complète sur l'ensemble des systèmes, questionnaires et KPI",
        "token": "qYymtXBumq3o0BDdFvyO74FjwWuqn_8XeutquSSmUBg",
    },
    # Divisionnaires
    {
        "nom": "M. BOUTEMADJA Samy",
        "fichier": "Mail_BOUTEMADJA_Samy",
        "role": "Divisionnaire DC",
        "perimetre": "Toutes les directions et systèmes rattachés à la division DC (DRM, DVR)",
        "token": "1gZ_9JMxC0QTcY9XyHCYFeWW7YzDtWO0-OCt48MHqOM",
    },
    {
        "nom": "M. BENBOUAZIZ Lyes",
        "fichier": "Mail_BENBOUAZIZ_Lyes_DIVEX",
        "role": "Divisionnaire DIVEX (p/i)",
        "perimetre": "Toutes les directions et systèmes rattachés à la division DIVEX (CCO, DOA, DOS)",
        "token": "LYmlpP9IWIPM9d6A7gXxvwK3hu3a41a9UsjSApbzGlo",
    },
    {
        "nom": "M. HACHELAF Mourad",
        "fichier": "Mail_HACHELAF_Mourad",
        "role": "Divisionnaire DMRA",
        "perimetre": "Tous les systèmes rattachés à la division DMRA (AMOS)",
        "token": "zmgCAn1EI7h_DL-FaxRuXrQrmynXYE07JWj648p69Jk",
    },
    # Directeurs
    {
        "nom": "M. KRAIMECHE Abdelkrim",
        "fichier": "Mail_KRAIMECHE_Abdelkrim",
        "role": "Directeur DRH",
        "perimetre": "Les systèmes rattachés à la Direction des Ressources Humaines (DRH)",
        "token": "0aLgUODgi580CWOUbNbPvVYMqEGScp0AK_gWTN7OziE",
    },
    {
        "nom": "M. DEBAB",
        "fichier": "Mail_DEBAB",
        "role": "Directeur DSI",
        "perimetre": "Les systèmes rattachés à la Direction des Systèmes d'Information (DSI)",
        "token": "MS14bS1w8jrKtxr2KGbnPwiJIw2nZ1XVkWlq95buRss",
    },
    {
        "nom": "M. MERDACI Adel",
        "fichier": "Mail_MERDACI_Adel",
        "role": "Directeur adjoint DSI",
        "perimetre": "Les systèmes rattachés à la Direction des Systèmes d'Information (DSI)",
        "token": "kb2HMNgtwGkzrCuD10rk9dOwY_EtvkdBvhkS_exprXY",
    },
    {
        "nom": "Mme BOUNAB Nihad",
        "fichier": "Mail_BOUNAB_Nihad",
        "role": "Directrice DVR",
        "perimetre": "Les systèmes rattachés à la Direction de la Vente et de la Réservation (DVR)",
        "token": "250LRTA7DV2_-_Tk-tdD8e21l69xNXlNwvvnWtF1fvU",
    },
    {
        "nom": "M. FAIDI Fouad",
        "fichier": "Mail_FAIDI_Fouad",
        "role": "Directeur DRM",
        "perimetre": "Les systèmes rattachés à la Direction du Revenue Management (DRM)",
        "token": "rtZgim5mm0vasK8hBIm_s4GDlMUAJ7HN-RErx7826qc",
    },
    {
        "nom": "M. KHELFI Redouane",
        "fichier": "Mail_KHELFI_Redouane",
        "role": "Directeur DFC",
        "perimetre": "Les systèmes rattachés à la Direction Finances et Comptabilité (DFC)",
        "token": "JazLAOvgbFrMX1BLGxN19AzasbuiHzfyx3lNBO-A00o",
    },
    {
        "nom": "M. BENBOUAZIZ Lyes",
        "fichier": "Mail_BENBOUAZIZ_Lyes_DOA",
        "role": "Directeur DOA",
        "perimetre": "Les systèmes rattachés à la Direction des Opérations Aériennes (DOA)",
        "token": "ZEIdYfcQC3_AXTHwImCV1H8ZNSE-KKSsqLAJABD37Fc",
    },
]


def generate_mail_markdown(dest):
    """Génère le contenu Markdown du mail personnalisé."""
    lien = f"{BASE_URL}{dest['token']}"

    md = f"""# Cartographie du Système d'Information — Air Algérie

**Objet :** Vos accès personnalisés à la plateforme de suivi

---

Bonjour **{dest['nom']}**,

Dans le cadre du projet de **cartographie du Système d'Information** d'Air Algérie, nous avons le plaisir de vous transmettre vos **accès personnalisés** à la plateforme de suivi.

---

## Votre accès

| | |
|---|---|
| **Destinataire** | {dest['nom']} |
| **Rôle** | {dest['role']} |
| **Périmètre** | {dest['perimetre']} |

---

## Votre lien d'accès

Cliquez sur le lien ci-dessous pour accéder à votre tableau de bord :

**{lien}**

> **Votre code d'accès (token) :** `{dest['token']}`

---

## Ce que vous pouvez faire sur la plateforme

- **Suivre l'avancement** des questionnaires concernant les systèmes de votre périmètre
- **Consulter les réponses** déjà fournies par les key users (lecture seule)
- **Visualiser la progression** globale et par direction

---

## Informations importantes

- Ce code est **strictement personnel** — merci de ne pas le partager
- L'accès est en **lecture seule** — aucune modification des questionnaires n'est possible
- Le tableau de bord se met à jour **en temps réel** au fur et à mesure des réponses des key users
- **Premier chargement** : le site peut mettre ~30 secondes à démarrer (hébergement en mode veille)

---

N'hésitez pas à revenir vers nous pour toute question.

Cordialement,

**Équipe Cartographie SI**
Direction des Systèmes d'Information — Air Algérie
"""
    return md


def convert_to_docx(markdown, title, output_path, max_retries=3):
    """Appelle l'API Markpresso pour convertir le Markdown en .docx avec retry."""
    payload = {
        "markdown": markdown,
        "title": title,
        "style": STYLE
    }

    for attempt in range(max_retries):
        response = requests.post(API_URL, json=payload)

        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return True
        elif response.status_code == 429:
            wait = 5 * (attempt + 1)
            print(f"  ⏳ Rate limited, attente {wait}s (tentative {attempt+1}/{max_retries})...")
            time.sleep(wait)
        else:
            print(f"  ERREUR {response.status_code}: {response.text}")
            return False

    print(f"  ERREUR: Échec après {max_retries} tentatives (429)")
    return False


def main():
    print(f"Génération de {len(destinataires)} mails d'accès...\n")

    success = 0
    errors = 0

    for i, dest in enumerate(destinataires, 1):
        filename = f"{dest['fichier']}.docx"
        output_path = os.path.join(OUTPUT_DIR, filename)
        title = f"Accès Plateforme — {dest['nom']}"

        # Skip si le fichier existe déjà (pour reprendre après erreur)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            print(f"[{i}/{len(destinataires)}] {dest['nom']} — déjà généré, skip.")
            success += 1
            continue

        print(f"[{i}/{len(destinataires)}] {dest['nom']} ({dest['role']})...")

        md = generate_mail_markdown(dest)
        if convert_to_docx(md, title, output_path):
            print(f"  ✓ {filename}")
            success += 1
        else:
            print(f"  ✗ Échec pour {dest['nom']}")
            errors += 1

        # Pause entre les requêtes pour éviter le rate limiting
        if i < len(destinataires):
            time.sleep(3)

    print(f"\n{'='*50}")
    print(f"Terminé ! {success} fichiers générés, {errors} erreurs.")
    print(f"Dossier de sortie : {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
