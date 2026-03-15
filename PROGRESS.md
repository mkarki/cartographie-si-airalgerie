# Cartographie SI Air Algérie - État d'avancement

## Résumé du projet

Application Django de cartographie du Système d'Information d'Air Algérie permettant de visualiser les systèmes, leurs interconnexions et les flux de données.

---

## Fonctionnalités réalisées

### 1. Structure de l'application Django
- **Framework**: Django avec templates HTML/Tailwind CSS
- **Base de données**: SQLite avec les modèles suivants :
  - `Structure` : Directions/départements (CCO, DC, DD, DF, DO, etc.)
  - `SystemCategory` : Catégories de systèmes (PSS, OPS, Finance, etc.)
  - `System` : Systèmes informatiques (ALTEA, AIMS, AMOS, etc.)
  - `DataFlow` : Flux de données entre systèmes
  - `MessageFormat` : Formats de messages IATA (SSIM, SSM, ASM, MVT, LDM)
  - `MessageField` : Champs des formats de messages
  - `DataDomain` : Domaines de données

### 2. Interface utilisateur
- **Sidebar** avec navigation :
  - Dashboard
  - Systèmes
  - Flux de données
  - Cartographie (graphe interactif)
  - Formats de messages
- **Logo Air Algérie** intégré dans la sidebar
- **Design moderne** avec effet glassmorphism et dégradé

### 3. Cartographie Interactive (page principale)
- **Visualisation Cytoscape.js** avec :
  - **Compound nodes** : Les structures contiennent visuellement leurs systèmes
  - **Layout cose-bilkent** : Disposition automatique sans chevauchement
  - **Couleurs par criticité** : Rouge (critique), Orange (haute), Jaune (moyenne), Vert (basse)
  - **Flux visualisés** : Flèches entre systèmes avec styles différents (automatisé/manuel, critique/normal)

- **Filtres** :
  - Par catégorie de système
  - Par structure
  - Toggle pour afficher/masquer les structures

- **Légendes cliquables** :
  - Structures (toutes listées avec couleurs)
  - Criticité (Critique, Haute, Moyenne, Basse)
  - Types de flux (Automatisé, Manuel)

- **Panneau latéral d'information** :
  - Détails du système au clic (nom, structure, catégorie, fournisseur, mode, criticité)
  - Détails du flux au clic (fréquence, protocole, format, automatisé, critique)
  - Lien vers la page de détail

- **Contrôles** :
  - Zoom (molette)
  - Pan (glisser)
  - Bouton "Ajuster" pour recentrer
  - Bouton "Reset" pour réinitialiser les filtres

### 4. Données chargées
- **18 structures** : CCO, DC, DD, DF, DO, DL, DRH, DVR, DOA, DPD, DQSA, DCS, RGFN, RGFS, DP, DSI, DMRA, DOS
- **38 systèmes** : ALTEA, AIMS, AMOS, JETPLAN, ACCELYA, etc.
- **69 flux de données** entre les systèmes (dont 11 nouveaux datafeeds Amadeus)
- **15 formats de messages** : SSIM, SSM, ASM, MVT, LDM + 10 nouveaux formats Amadeus
- **18 champs de message** documentés
- **8 domaines de données** : Programme de Vol, Réservations, Billets, etc.

### 5. Nouveaux Datafeeds Amadeus (ajoutés le 01/02/2026)

Basé sur les données reçues dans `data/01_02/DATAFEEDSS` :

| Datafeed | Format | Description | Fréquence |
|----------|--------|-------------|------------|
| **PNR Datafeed** | SBRRES/EDIFACT | Export complet des données PNR | Continu |
| **HOTE Lift File** | HOT-LIFT v2.6a | Coupons de vol utilisés | Quotidien |
| **EMD Lift File** | EMD-LIFT v1.03 | Documents électroniques divers | Quotidien |
| **E-Ticket History** | ETKT-HIST | Historique des billets électroniques | Quotidien |
| **APS Payment** | APS | Transactions de paiement (3DS, DCC) | Continu |
| **RAPID FLP** | RAPID-FLP | Prorata revenus par segment | Quotidien |
| **RAPID IBP** | RAPID-IBP | Facturation intercompagnies | Mensuel |
| **RAPID SLP** | RAPID-SLP | Prorata des ventes | Quotidien |
| **Inventory Feed** | IFLIRR/EDIFACT | Disponibilités classes | Continu |
| **DCS CDW Feed** | DCS-CDW | Données DCS vers Data Warehouse | Continu |
| **TDNA LiveFeed** | TDNA/XML | Flux temps réel analytics | Temps réel |

---

## Architecture technique

```
cartographie_si/
├── config/                 # Configuration Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── cartography/           # Application principale
│   ├── models.py          # Modèles de données
│   ├── views.py           # Vues (dashboard, graph, API)
│   ├── urls.py            # Routes
│   ├── admin.py           # Interface admin
│   └── fixtures/
│       └── initial_data.json  # Données initiales
├── templates/
│   ├── base.html          # Template de base avec sidebar
│   └── cartography/
│       ├── dashboard.html
│       ├── graph.html     # Cartographie interactive
│       ├── system_list.html
│       ├── system_detail.html
│       ├── flow_list.html
│       └── flow_detail.html
├── static/
│   └── logo.png           # Logo Air Algérie
└── db.sqlite3             # Base de données
```

---

## Comment lancer l'application

```bash
cd /Users/mohamedamine/Air\ Algérie/cartographie_si
python manage.py runserver 8001
```

Accès : http://127.0.0.1:8001/

### 6. Retour DSI — M. Youcef-Achira (23 février 2026)

Suite au mail de la Sous-Direction Études & Développements (DSI), les observations suivantes ont été intégrées dans la base de données :

| Système | Mise à jour |
|---------|-------------|
| **SITATEX ONLINE** | Clarifié : client cloud de visualisation messages Type B uniquement. La génération/envoi est assurée par les autres systèmes (Altéa, AIMS…) |
| **SAGE Stock** | Marqué **non opérationnel** — en cours d'implémentation. Criticité → Basse |
| **DASH-PONCT-H** | Module ERP, utilisation limitée, données déjà disponibles dans AIMS. Criticité → Basse |
| **DASH-PONCT-J** | Idem |
| **SUIVI-IRREG** | Idem |
| **Qlik Sense** | Marqué **OBSOLÈTE** — absence de licences utilisateurs, en remplacement par Power BI. Criticité → Basse |
| **Power BI** | Mode corrigé : **On-Premise** (Report Server), et non SaaS (Services) |
| **Zimbra** | Clarifié : messagerie SMTP standard, aucun interfaçage avec SITATEX ou autres systèmes |
| **Portail AH** | Clarifié : portail de publication de notes et informations internes uniquement |

**Remarques DSI non encore traitées :**
- La DSI recommande d'impliquer les métiers (divisions) pour la validation des priorisations de : **Site Web AH**, **OAG/Innovata**, **SkyBook**, **Hermes Call Center**
- Commande de mise à jour re-exécutable : `python3 manage.py update_dsi_feedback`

---

## Prochaines étapes possibles

1. **Améliorer les pages de détail** des systèmes et flux
2. **Ajouter la recherche** globale
3. **Export PDF/PNG** de la cartographie
4. **Historique des modifications** des flux
5. **Alertes** sur les flux critiques
6. **Documentation API** pour intégration externe
7. **Authentification** utilisateurs
8. **Mode sombre/clair** toggle
9. **Validation métiers** des priorisations (Site Web AH, OAG/Innovata, SkyBook, Hermes Call Center) — recommandation DSI

---

## Dernière mise à jour
23 février 2026 - Intégration retours DSI (M. Youcef-Achira) : corrections SITATEX, SAGE Stock, Dashboards CCO, Qlik Sense, Power BI, Zimbra, Portail AH
