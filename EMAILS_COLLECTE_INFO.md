# Emails Techniques — Collecte d'informations Experts SI

> Modèles d'emails génériques orientés technique, à adapter selon le système concerné.
> Pour les emails fonctionnels personnalisés (avec noms des Key Users), voir `EMAILS_FONCTIONNELS_KEY_USERS.md`.
> 
> **Usage :** Remplacer `[NOM DU SYSTÈME]`, `[ÉDITEUR]`, `[STRUCTURE]` par les valeurs du système concerné.

---

## Template A — Système de gestion (ERP, Stock, Finance, RH)

*S'applique à : SAGE STOCK, SAGE FINANCE, RAPID PASSAGERS, EVALCOM, BODET*

```
Objet : [Cartographie SI — Technique] [NOM DU SYSTÈME] — Collecte d'informations

Bonjour,

Dans le cadre du projet de cartographie technique du SI d'Air Algérie,
nous collectons les informations détaillées sur le système [NOM DU SYSTÈME]
(Éditeur : [ÉDITEUR] — Structure : [STRUCTURE]).

Merci de nous fournir les éléments suivants :

1. INFORMATIONS TECHNIQUES
   - Version exacte du logiciel (ex : SAGE X3 v12.0.25) :
   - Architecture (client/serveur, web, SaaS) :
   - Serveur(s) d'hébergement (nom, OS, RAM, stockage) :
   - Base de données utilisée (Oracle, SQL Server, PostgreSQL, fichiers) :
   - Protocoles réseau (ports, VPN, accès distant) :

2. INTERFACES ET FLUX DE DONNÉES
   Pour chaque interface existante, merci de préciser :
   - Système source / cible :
   - Type d'échange (API REST/SOAP, fichier plat, CSV, XML, EDIFACT, BDD) :
   - Fréquence (temps réel, batch quotidien, hebdomadaire, mensuel) :
   - Volume estimé (nb enregistrements/jour, taille fichiers) :
   - Sens de l'échange (entrant, sortant, bidirectionnel) :
   - Automatisé ou manuel :

3. SÉCURITÉ ET ACCÈS
   - Nombre d'utilisateurs actifs :
   - Mode d'authentification (LDAP, SSO, local) :
   - Gestion des droits (profils, rôles) :
   - Politique de sauvegarde (fréquence, rétention, localisation) :

4. CONTRAT ET SUPPORT
   - Contrat de maintenance actif (oui/non, prestataire, échéance) :
   - SLA défini (temps de réponse, disponibilité) :
   - Documentation technique existante (schéma BDD, doc API, manuel admin) :

5. EXTRACTION DE DONNÉES ANONYMISÉES
   Merci de nous fournir si possible :
   - Export de la structure de la base de données (tables, colonnes, types)
   - Exemple de fichier d'échange anonymisé
   - Captures d'écran des interfaces principales (sans données personnelles)

Nous pouvons fixer un rendez-vous pour vous accompagner dans cette collecte.

Cordialement,
Direction des Systèmes d'Information — Air Algérie
```

---

## Template B — Système aérien critique (Réservation, Opérations, Maintenance)

*S'applique à : SUITE ALTÉA, AIMS, AMOS, ACARS/HERMES, EUROCONTROL, JET PLANER, SKYBOOK, FLYSMART, WORLD TRACER, SITATEX*

```
Objet : [Cartographie SI — Technique] [NOM DU SYSTÈME] — Collecte d'informations

Bonjour,

Dans le cadre du projet de cartographie technique du SI d'Air Algérie,
nous collectons les informations détaillées sur le système [NOM DU SYSTÈME]
(Éditeur : [ÉDITEUR] — Structure : [STRUCTURE]).

Ce système étant classé critique pour les opérations, nous avons besoin
d'informations précises.

1. INFORMATIONS TECHNIQUES
   - Version exacte :
   - Architecture (SaaS éditeur, on-premise, réseau dédié) :
   - Environnements disponibles (production, test, formation) :
   - Serveur(s) / Data Center (localisation, redondance) :
   - Base de données :
   - Protocoles spécifiques (SITA, ARINC, EDIFACT, Type B, IATA) :

2. INTERFACES ET FLUX DE DONNÉES — DÉTAIL COMPLET
   Pour CHAQUE interface, fournir un tableau :

   | Système connecté | Direction | Type données | Format | Protocole | Fréquence | Volume | Automatisé |
   |-----------------|-----------|-------------|--------|-----------|-----------|--------|------------|
   | ex: AIMS        | Entrant   | Programmes  | SSIM   | FTP       | Quotidien | 1 fichier | Oui     |

   Interfaces connues à documenter :
   - [Lister les systèmes connectés identifiés dans la cartographie]

3. FORMATS DE MESSAGES
   - Types de messages échangés (MVT, LDM, ASM, SSM, PSM, SSIM, etc.) :
   - Standards utilisés (IATA Type B, EDIFACT, XML, JSON) :
   - Exemple de message anonymisé pour chaque type :

4. DISPONIBILITÉ ET CONTINUITÉ
   - Disponibilité requise (24/7, heures ouvrées) :
   - Plan de continuité existant (PCA/PRA) :
   - Temps de reprise (RTO) et perte de données acceptable (RPO) :
   - Incidents majeurs récents (date, durée, impact) :

5. SÉCURITÉ ET ACCÈS
   - Nombre d'utilisateurs actifs (par profil/rôle) :
   - Mode d'authentification :
   - Accès distant (VPN, réseau SITA/ARINC) :
   - Politique de sauvegarde :

6. CONTRAT ET SUPPORT
   - Contrat actif (éditeur, périmètre, échéance) :
   - SLA (disponibilité garantie, temps de réponse) :
   - Support éditeur (niveaux, contacts, horaires) :
   - Documentation technique existante :

7. EXTRACTION DE DONNÉES ANONYMISÉES
   Merci de nous fournir si possible :
   - Schéma d'architecture technique du système
   - Exemples de messages/fichiers échangés (anonymisés)
   - Export structure BDD ou API documentation
   - Captures d'écran des interfaces principales

Nous pouvons fixer un rendez-vous pour vous accompagner dans cette collecte.

Cordialement,
Direction des Systèmes d'Information — Air Algérie
```

---

## Template C — Application interne / Dashboard / BI

*S'applique à : E-DOLÉANCE, CTRL PROGRAMMES, DASHBOARDS CCO, SUIVI IRRÉGULARITÉS, QLIK SENSE, POWER BI, GLPI, PORTAIL AH, DOA MAILING, CALL DOA, E-LEARNING E-EXAM*

```
Objet : [Cartographie SI — Technique] [NOM DU SYSTÈME] — Collecte d'informations

Bonjour,

Dans le cadre du projet de cartographie technique du SI d'Air Algérie,
nous collectons les informations détaillées sur le système [NOM DU SYSTÈME]
(Éditeur/Développeur : [ÉDITEUR] — Structure : [STRUCTURE]).

1. INFORMATIONS TECHNIQUES
   - Technologie utilisée (langage, framework, CMS) :
   - Version :
   - Architecture (application web, desktop, Power BI, Excel avancé) :
   - Serveur d'hébergement (nom, OS, URL d'accès) :
   - Base de données (type, taille estimée) :

2. SOURCES DE DONNÉES
   Pour chaque source de données alimentant ce système :
   - Système source :
   - Mode de connexion (connecteur BDD, API, fichier, saisie manuelle) :
   - Fréquence de rafraîchissement :
   - Volume de données :
   - Transformation appliquée (ETL, requêtes, calculs) :

3. SORTIES ET EXPORTS
   - Rapports / exports produits :
   - Format de sortie (PDF, Excel, API, écran) :
   - Destinataires :
   - Fréquence :

4. SÉCURITÉ ET ACCÈS
   - Nombre d'utilisateurs actifs :
   - Mode d'authentification (LDAP, SSO, local) :
   - Gestion des droits :

5. MAINTENANCE
   - Développé par qui (DSI, prestataire externe, éditeur) :
   - Code source accessible (oui/non, dépôt) :
   - Contrat de maintenance (si externe) :
   - Documentation technique existante :

6. EXTRACTION DE DONNÉES ANONYMISÉES
   Merci de nous fournir si possible :
   - Captures d'écran des interfaces principales
   - Structure des tables / modèle de données
   - Exemple de rapport ou dashboard (anonymisé)

Nous pouvons fixer un rendez-vous pour vous accompagner dans cette collecte.

Cordialement,
Direction des Systèmes d'Information — Air Algérie
```

---

## Template D — Plateforme SaaS / Distribution

*S'applique à : ACCELYA DISTRIBUTION, BSP LINK, ATPCO, BAC (AMADEUS), OAG/INNOVATA, DATAWINGS, Q-PULSE, AGS*

```
Objet : [Cartographie SI — Technique] [NOM DU SYSTÈME] — Collecte d'informations

Bonjour,

Dans le cadre du projet de cartographie technique du SI d'Air Algérie,
nous collectons les informations détaillées sur le système [NOM DU SYSTÈME]
(Éditeur : [ÉDITEUR] — Structure : [STRUCTURE]).

1. INFORMATIONS TECHNIQUES
   - Mode d'accès (SaaS, portail web, client lourd, API) :
   - URL d'accès :
   - Version / niveau de service souscrit :
   - Environnements disponibles (production, test) :

2. INTERFACES ET FLUX DE DONNÉES
   Pour chaque interface :
   - Système connecté :
   - Type d'échange (API, fichier, portail, message SITA) :
   - Format (CSV, XML, JSON, EDIFACT, Type B) :
   - Fréquence et volume :
   - Automatisé ou manuel :
   - Sens (entrant/sortant/bidirectionnel) :

3. SÉCURITÉ ET ACCÈS
   - Nombre d'utilisateurs / licences actives :
   - Mode d'authentification :
   - Gestion des profils/rôles :

4. CONTRAT ET SUPPORT
   - Contrat actif (éditeur, périmètre, échéance, coût annuel) :
   - SLA (disponibilité, temps de réponse) :
   - Support éditeur (contacts, niveaux) :
   - Documentation technique fournie par l'éditeur :

5. EXTRACTION DE DONNÉES ANONYMISÉES
   Merci de nous fournir si possible :
   - Exemple de fichier d'échange anonymisé
   - Captures d'écran du portail (sans données sensibles)
   - Documentation API si disponible

Nous pouvons fixer un rendez-vous pour vous accompagner dans cette collecte.

Cordialement,
Direction des Systèmes d'Information — Air Algérie
```

---

## Template E — Messagerie / Communication

*S'applique à : ZIMBRA, HERMES CALL CENTER, SITE WEB AIR ALGÉRIE*

```
Objet : [Cartographie SI — Technique] [NOM DU SYSTÈME] — Collecte d'informations

Bonjour,

Dans le cadre du projet de cartographie technique du SI d'Air Algérie,
nous collectons les informations détaillées sur le système [NOM DU SYSTÈME]
(Éditeur : [ÉDITEUR] — Structure : [STRUCTURE]).

1. INFORMATIONS TECHNIQUES
   - Version exacte :
   - Architecture (serveur mail, plateforme web, call center) :
   - Serveur(s) d'hébergement (nom, OS, localisation) :
   - Capacité (nb boîtes mail, nb agents, nb visiteurs/mois) :

2. INTÉGRATIONS
   - Passerelles avec d'autres systèmes (SITATEX, GLPI, Altéa, etc.) :
   - Mode d'intégration (SMTP, API, connecteur, plugin) :
   - Notifications automatiques envoyées par d'autres systèmes :

3. SÉCURITÉ
   - Mode d'authentification :
   - Anti-spam / antivirus :
   - Politique de rétention des données :
   - Sauvegarde :

4. CONTRAT ET SUPPORT
   - Contrat actif :
   - SLA :
   - Documentation technique :

5. EXTRACTION DE DONNÉES ANONYMISÉES
   Merci de nous fournir si possible :
   - Statistiques d'utilisation (nb messages/jour, nb appels, trafic web)
   - Architecture réseau simplifiée
   - Captures d'écran (sans données personnelles)

Nous pouvons fixer un rendez-vous pour vous accompagner dans cette collecte.

Cordialement,
Direction des Systèmes d'Information — Air Algérie
```

---

## Correspondance Système → Template

| # | Système | Structure | Template |
|---|---------|-----------|----------|
| 1 | SAGE STOCK | DAGP | A — Gestion |
| 2 | E-DOLÉANCE | DC | C — App interne |
| 3 | ACCELYA DISTRIBUTION | DC | D — SaaS |
| 4 | BSP LINK | DC | D — SaaS |
| 5 | HERMES CALL CENTER | DC | E — Communication |
| 6 | SITE WEB AIR ALGÉRIE | DC | E — Communication |
| 7 | ATPCO | DC | D — SaaS |
| 8 | BAC (AMADEUS) | DC | D — SaaS |
| 9 | SUITE ALTÉA AMADEUS | DC + DIVEX | B — Aérien critique |
| 10 | RAPID PASSAGERS | DFC | A — Gestion |
| 11 | OAG / INNOVATA | DIVEX + DC | D — SaaS |
| 12 | AIMS | DIVEX + DC + DMRA | B — Aérien critique |
| 13 | ACARS / HERMES | DIVEX (CCO) | B — Aérien critique |
| 14 | AMOS | DMRA | B — Aérien critique |
| 15 | EUROCONTROL | DOA | B — Aérien critique |
| 16 | JET PLANER | DOA | B — Aérien critique |
| 17 | SKYBOOK | DOA | B — Aérien critique |
| 18 | FLYSMART | DOA | B — Aérien critique |
| 19 | E-LEARNING E-EXAM PN | DOA | C — App interne |
| 20 | DOA MAILING | DOA | C — App interne |
| 21 | CALL DOA | DOA | C — App interne |
| 22 | CTRL PROGRAMMES PN | DIVEX (CCO) | C — App interne |
| 23 | DASHBOARDS PONCTUALITÉ | DIVEX (CCO) | C — App interne |
| 24 | SUIVI IRRÉGULARITÉS | DIVEX (CCO) | C — App interne |
| 25 | QLIK SENSE | DPD + DOS | C — App interne |
| 26 | WORLD TRACER | DOS | B — Aérien critique |
| 27 | EVALCOM | DRH | A — Gestion |
| 28 | AGS | DSC | D — SaaS |
| 29 | Q-PULSE | DSC | D — SaaS |
| 30 | GLPI | DSI | C — App interne |
| 31 | PORTAIL AH | DSI | C — App interne |
| 32 | POWER BI | DSI | C — App interne |
| 33 | SITATEX ONLINE | DSI | B — Aérien critique |
| 34 | ZIMBRA | DSI | E — Communication |
| 35 | BODET | RGF | A — Gestion |
| 36 | DATAWINGS | RGF | D — SaaS |
| 37 | SAGE FINANCE | RGF | A — Gestion |

---

*Généré le 9 février 2026*
