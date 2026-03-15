# Cartographie SI Air Algérie

Application Django pour visualiser la cartographie du Système d'Information d'Air Algérie.

## Fonctionnalités

- **Dashboard** - Vue d'ensemble avec statistiques
- **Cartographie Interactive** - Visualisation graphique des systèmes et flux (Cytoscape.js)
- **Systèmes** - Liste et détail des 38 systèmes informatiques
- **Flux de Données** - Détail des échanges inter-systèmes avec champs
- **Structures** - Organisation par direction responsable
- **Messages IATA** - Formats standards (SSIM, SSM, ASM, MVT, LDM)
- **Domaines de Données** - Identification des systèmes maîtres

## Installation

```bash
# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Migrations
python manage.py migrate

# Charger les données initiales (38 systèmes, flux, messages)
python manage.py loaddata initial_data

# Lancer le serveur
python manage.py runserver
```

## Accès

- Application: http://localhost:8000
- Admin: http://localhost:8000/admin

## Structure

```
cartographie_si/
├── config/              # Configuration Django
├── cartography/         # Application principale
│   ├── models.py        # Modèles de données
│   ├── views.py         # Vues et API
│   ├── urls.py          # Routes
│   └── fixtures/        # Données initiales
├── templates/           # Templates HTML
└── static/              # Fichiers statiques
```

## Technologies

- Django 4.2+
- TailwindCSS (CDN)
- Cytoscape.js (visualisation graphe)
- Lucide Icons
