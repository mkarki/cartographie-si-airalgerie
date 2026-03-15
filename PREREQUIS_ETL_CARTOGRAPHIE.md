# Prérequis Fonctionnels & Techniques — ETL Cible et Cartographie
## Pour chaque système du SI Air Algérie

> **Objectif :** Pour chacun des systèmes identifiés, définir les prérequis fonctionnels et techniques pour :
> 1. Dupliquer les bases de données sur un environnement dédié
> 2. Mettre en place un **ETL cible** (Extract – Transform – Load)
> 3. Identifier les **référentiels maîtres** (sources de vérité)
>
> *Basé sur le fichier DAG du 11/02/2026*

---

## Référentiels maîtres — Sources de vérité

| Domaine de données | Système référentiel | Consommateurs |
|-------------------|---------------------|---------------|
| **Programmes de vols** | AIMS | Altéa, EUROCONTROL, OAG, Dashboards CCO, ACARS |
| **Réservations & PNR** | Altéa (Reservation) | Rapid, BSP Link, Site Web, BAC |
| **Billetterie & coupons** | Altéa (Ticketing) | Rapid, BAC, BSP Link |
| **DCS** | Altéa (DCS) | AIMS, World Tracer, SITATEX |
| **Revenue accounting** | Rapid Passagers | SAGE Finance, BAC |
| **Équipages** | AIMS (Crew) | DOA Mailing, Call DOA, E-Learning |
| **Maintenance** | AMOS | AIMS, SAGE STOCK |
| **Stocks & pièces** | SAGE STOCK | AMOS |
| **Tarifs aériens** | ATPCO | Altéa, GDS |
| **Messages aéronautiques** | SITATEX | Altéa, AIMS, ACARS, Zimbra |
| **Données de vol FDR/QAR** | AGS | Q-Pulse |
| **Qualité & non-conformités** | Q-Pulse | AGS, AMOS |
| **Réclamations passagers** | E-Doléance | — |
| **Parc informatique** | GLPI | — |
| **Bagages** | World Tracer | Altéa DCS |
| **Reporting transverse** | Power BI | Multiples sources |

---

## 1. SAGE STOCK — DAGP 🟠

**Éditeur :** Sans contrat | **Key User :** ATTOUT Abedlhafid / AIT MEZIANE Amar

### Prérequis fonctionnels
- [ ] Inventaire des modules utilisés (stocks, inventaire, mouvements, bons de commande)
- [ ] Liste des types d'articles gérés (pièces avion, fournitures, consommables)
- [ ] Processus métier : circuit d'un mouvement de stock
- [ ] Règles de gestion : seuils réapprovisionnement, valorisation
- [ ] Volumétrie : nombre d'articles, mouvements/mois

### Prérequis techniques
- [ ] Version exacte de SAGE
- [ ] Architecture : client/serveur, BDD (SQL Server, propriétaire)
- [ ] Serveur d'hébergement (nom, OS, IP)
- [ ] Schéma BDD (tables, colonnes, types, relations)
- [ ] Mode d'accès réseau, politique de sauvegarde
- [ ] **Absence de contrat** : identifier risques et alternatives

### ETL cible
```
SOURCE : SAGE STOCK (BDD SQL Server / propriétaire)
EXTRACT : Connecteur ODBC/JDBC — Tables : articles, mouvements_stock, bons_commande
TRANSFORM : Normalisation codes articles (mapping vers AMOS si pièces avion)
LOAD : Base cartographie → dim_articles, fact_mouvements_stock
RÉFÉRENTIEL : REF Stocks & pièces
FLUX → AMOS : pièces de rechange (à automatiser)
Fréquence : quotidien (batch nuit)
Base dupliquée : réplique read-only + dump quotidien
```

---

## 2. E-DOLÉANCE — DC 🟢

**Éditeur :** DSI (in-house) | **Key User :** AKKACHA Mohamed Amine / BELDJERDI Zakaria

### Prérequis fonctionnels
- [ ] Types de réclamations, circuit de traitement, règles d'escalade
- [ ] Rapports et statistiques produits
- [ ] Lien avec données passagers (PNR Altéa)

### Prérequis techniques
- [ ] Technologie (langage, framework, BDD)
- [ ] Schéma BDD, API existante, code source accessible

### ETL cible
```
SOURCE : E-Doléance (BDD interne DSI)
EXTRACT : SQL direct ou API REST — Tables : reclamations, types, statuts
TRANSFORM : Enrichissement PNR Altéa, agrégation stats
LOAD : fact_reclamations — RÉFÉRENTIEL : REF Réclamations
Fréquence : quotidien — Anonymisation passagers obligatoire
```

---

## 3. ACCELYA DISTRIBUTION — DC 🟠

**Éditeur :** Accelya | **Key User :** SAAD Nasima / HALISSE Abderrahim

### Prérequis fonctionnels
- [ ] Périmètre : distribution, ventes, émission billets, canaux
- [ ] Rapports de ventes, lien avec BSP Link

### Prérequis techniques
- [ ] Mode d'accès SaaS, API Accelya, formats (CSV/XML/EDIFACT)

### ETL cible
```
SOURCE : Accelya Distribution (SaaS)
EXTRACT : API Accelya ou export fichiers
TRANSFORM : Rapprochement Altéa, normalisation codes IATA
LOAD : fact_ventes_distribution
FLUX ← Altéa : réservations | FLUX → Rapid : revenue accounting
Fréquence : quotidien
```

---

## 4. BSP LINK — DC 🟢

**Éditeur :** IATA | **Key User :** SAAD Nassima / HALISSE Abderrahim

### Prérequis fonctionnels
- [ ] Rapports BSP consultés, fréquence, données reprises ailleurs

### Prérequis techniques
- [ ] Portail IATA, export automatisé (API/fichiers), formats CSV/XML

### ETL cible
```
SOURCE : BSP Link (portail IATA)
EXTRACT : Export fichiers BSP ou API IATA
TRANSFORM : Rapprochement Accelya + Rapid, normalisation codes agences
LOAD : fact_bsp_ventes — Fréquence : hebdomadaire (cycle BSP)
```

---

## 5. HERMES CALL CENTER — DC 🟢

**Éditeur :** Vocalcom | **Key User :** BOUCHIK Mounir / FODILI Mohamed Yacine

### Prérequis fonctionnels
- [ ] Types d'appels, nb agents, volumétrie, stats produites
- [ ] Lien Altéa (consultation PNR), lien E-Doléance

### Prérequis techniques
- [ ] Version Vocalcom, BDD appels/stats, API ou export, intégration CTI

### ETL cible
```
SOURCE : Hermes (Vocalcom)
EXTRACT : Export stats ou API — Données : appels, durées, agents, motifs
TRANSFORM : Agrégation par motif, corrélation E-Doléance
LOAD : fact_appels_callcenter — Fréquence : quotidien
Anonymisation numéros téléphone
```

---

## 6. SITE WEB AIR ALGÉRIE — DC 🟠

**Éditeur :** KYO | **Key User :** BELDJERDI Zakaria / BACHA Amine

### Prérequis fonctionnels
- [ ] Fonctionnalités (réservation, check-in, fidélité), taux conversion, CMS

### Prérequis techniques
- [ ] Stack technique, hébergement, intégration Altéa (API Amadeus), analytics, contrat KYO

### ETL cible
```
SOURCE : Site Web (CMS + analytics)
EXTRACT : API Analytics + logs — Réservations via Altéa
TRANSFORM : Agrégation trafic, taux conversion
LOAD : fact_trafic_web
FLUX ← Altéa : disponibilités/tarifs | FLUX → Altéa : réservations en ligne
Fréquence : quotidien
```

---

## 7. ATPCO — DC 🟠

**Éditeur :** ATPCO | **Key User :** LAIDANI Zakaria / FAIDI Foued

### Prérequis fonctionnels
- [ ] Types tarifs publiés, fréquence, règles tarifaires, reprise Altéa/GDS

### Prérequis techniques
- [ ] Portail ATPCO, formats (ATPCO Category, EDIFACT), API

### ETL cible
```
SOURCE : ATPCO (SaaS)
EXTRACT : Export tarifs ou API — RÉFÉRENTIEL : REF Tarifs aériens
TRANSFORM : Parsing formats ATPCO, mapping O&D/classes
LOAD : dim_tarifs, fact_publications_tarifs
FLUX → Altéa/GDS : tarifs publiés (automatique)
Fréquence : à chaque publication
```

---

## 8. BAC (AMADEUS) — DC 🟠

**Éditeur :** Amadeus | **Key User :** HASSISSENE Chemseddine / BENMADI Soumeya

### Prérequis fonctionnels
- [ ] Facturation interline, proration, volume transactions, compagnies partenaires

### Prérequis techniques
- [ ] Module Amadeus SaaS, formats EDIFACT (IDEC), API BAC

### ETL cible
```
SOURCE : BAC Amadeus (SaaS)
EXTRACT : Export EDIFACT/CSV ou API
TRANSFORM : Parsing EDIFACT, rapprochement Rapid
LOAD : fact_interline_billing
FLUX ← Altéa : coupons interline | FLUX → Rapid : facturation
Fréquence : mensuel (cycle interline)
```

---

## 9. SUITE ALTÉA AMADEUS — DC + DIVEX 🔴

**Éditeur :** Amadeus | **Key Users :** FAIDI Fouad, FIALA Zahra, LOUNAOUCI Nassim, HASBELLAOUI Imen, GHARBI Mohamed, NAMOUNI Ali

### Prérequis fonctionnels
- [ ] Modules : Reservation, Ticketing, Inventory, DCS
- [ ] Processus métier par module, volumétrie (PNR/jour, coupons/jour, vols/jour)
- [ ] Canaux de vente connectés, règles de gestion spécifiques

### Prérequis techniques
- [ ] Version Altéa, environnements (PROD, TEST)
- [ ] API Amadeus (e-Retail, Web Services, NDC)
- [ ] Data feeds Amadeus (FTP/SFTP) : PNR, APS, FLP, coupons, DCS
- [ ] Formats : EDIFACT, XML, CSV
- [ ] Contrat Amadeus : périmètre data feeds inclus

### ETL cible
```
SOURCE : Altéa Amadeus (SaaS)
EXTRACT : Data Feeds (SFTP) + API Web Services
  - PNR Data Feed, APS (paiements), FLP, Coupon feeds, DCS feeds
TRANSFORM : Parsing EDIFACT/XML, dé-duplication PNR, enrichissement ATPCO
LOAD : fact_reservations, fact_coupons, fact_dcs, dim_vols, dim_passagers
RÉFÉRENTIEL : REF Réservations, Billetterie, DCS
FLUX SORTANTS → Rapid, BSP Link, Site Web, World Tracer, SITATEX, AIMS
FLUX ENTRANTS ← ATPCO, AIMS, Site Web
Fréquence : temps réel (feeds) + batch quotidien
Base dupliquée : serveur SFTP + data lake — Anonymisation RGPD obligatoire
⚠️ PRIORITÉ ABSOLUE : négocier accès data feeds avec Amadeus
```

---

## 10. RAPID PASSAGERS — DFC 🔴

**Éditeur :** Accelya | **Key User :** HADJ SAID Nadir / BELKACEMI Mohand

### Prérequis fonctionnels
- [ ] Revenue accounting, interline billing, proration, rapports financiers

### Prérequis techniques
- [ ] Version, architecture (SaaS/on-premise), BDD (Oracle/SQL Server), API/exports, contrat Accelya

### ETL cible
```
SOURCE : Rapid Passagers (Accelya)
EXTRACT : Export fichiers ou API
TRANSFORM : Rapprochement coupons Altéa, calcul revenus nets par route
LOAD : fact_revenue_accounting — RÉFÉRENTIEL : REF Revenue accounting
FLUX ← Altéa : coupons | FLUX → SAGE Finance : écritures | FLUX → BAC : interline
Fréquence : quotidien
```

---

## 11. OAG / INNOVATA — DIVEX + DC 🟢

**Éditeur :** OAG | **Key User :** SAFAR ZITOUN Naim / KARI Fateh

### Prérequis fonctionnels
- [ ] Usage (horaires, analyse routes), données envoyées/reçues

### Prérequis techniques
- [ ] Portail OAG, API Schedules, formats SSIM/CSV

### ETL cible
```
SOURCE : OAG (SaaS) — EXTRACT : API ou fichiers SSIM
TRANSFORM : Parsing SSIM, comparaison avec AIMS
LOAD : dim_horaires_marche — REF Horaires marché
FLUX ← AIMS : programmes SSIM — Fréquence : hebdomadaire
```

---

## 12. AIMS — DIVEX + DC + DMRA 🔴

**Éditeur :** Solution Soft | **Key Users :** BENAOUICHA Hanane, SIDAHMED AKKOUCHE, BENNOUAR Adnane, BADAOUI Youcef, HASSAINE Hassen

### Prérequis fonctionnels
- [ ] Modules : programmes vols, crew management, crew tracking, operations, training
- [ ] Processus : création programme → affectation équipages → suivi jour J
- [ ] Volumétrie, règles FTL, interactions DOA

### Prérequis techniques
- [ ] Version, architecture, BDD (Oracle/SQL Server), environnements
- [ ] Schéma BDD, API AIMS, formats (SSIM, CSV, XML)
- [ ] Contrat Solution Soft : support, accès données

### ETL cible
```
SOURCE : AIMS (on-premise)
EXTRACT : ODBC/JDBC + exports SSIM
  - Tables : flights, crew_roster, crew_qualifications, aircraft, rotations
TRANSFORM : Parsing SSIM, calcul indicateurs (utilisation flotte, heures vol), vérif FTL
LOAD : fact_vols, fact_crew_roster, dim_aircraft, dim_crew
RÉFÉRENTIEL : REF Programmes de vols, Équipages
FLUX SORTANTS → Altéa (SSIM), EUROCONTROL (FPL), ACARS, OAG, Dashboards, AMOS, DOA
FLUX ENTRANTS ← Altéa DCS, ACARS (MVT), AMOS (dispo avions)
Fréquence : temps réel + quotidien
⚠️ PRIORITÉ ABSOLUE : réplication read-only BDD AIMS
```

---

## 13. ACARS / HERMES — DIVEX (CCO) 🔴

**Éditeur :** Collins ARINC | **Key User :** LADJICI Fatima / BENNOUAR Adnane

### Prérequis fonctionnels
- [ ] Types messages (OOOI, techniques, free text), volume quotidien

### Prérequis techniques
- [ ] Version Hermes, réseau ARINC/SITA, format messages, stockage logs

### ETL cible
```
SOURCE : ACARS/Hermes (réseau ARINC)
EXTRACT : Export logs ou connecteur BDD Hermes
TRANSFORM : Parsing ACARS (OOOI), calcul ponctualité, corrélation AIMS
LOAD : fact_mouvements_avions
FLUX → AIMS, Dashboards CCO, SITATEX — Fréquence : temps réel
```

---

## 14. AMOS — DMRA 🔴

**Éditeur :** Swiss Aviation Software | **Key User :** BOUGUEZIZ Samir / FERRADJI Farid

### Prérequis fonctionnels
- [ ] Modules : OT, planification maintenance, navigabilité, pièces
- [ ] Suivi AD/SB/CDCCL, lien SAGE STOCK

### Prérequis techniques
- [ ] Version, architecture Oracle, schéma BDD, API AMOS Connect, contrat Swiss-AS

### ETL cible
```
SOURCE : AMOS (on-premise, Oracle)
EXTRACT : AMOS Connect API ou connecteur Oracle
TRANSFORM : Calcul MTBF/MTTR, suivi navigabilité, rapprochement SAGE STOCK
LOAD : fact_work_orders, fact_maintenance — RÉFÉRENTIEL : REF Maintenance
FLUX ← AIMS : heures vol/cycles | FLUX ← SAGE STOCK : pièces | FLUX → AIMS : dispo avions
Fréquence : quotidien
⚠️ PRIORITÉ : réplication Oracle read-only ou AMOS Connect
```

---

## 15. EUROCONTROL — DOA 🟠

**Éditeur :** EUROCONTROL | **Key User :** BENYELLES Djamal Eddine

### Prérequis fonctionnels / techniques
- [ ] Services : CFMU, slots, FPL | API NM B2B | Formats : ICAO FPL, ADEXP, XML

### ETL cible
```
EXTRACT : API NM B2B ou fichiers FPL — TRANSFORM : Parsing FPL, corrélation AIMS
LOAD : fact_plans_de_vol — FLUX ← AIMS — Fréquence : par vol
```

---

## 16. JET PLANER — DOA 🟠

**Éditeur :** Jeppesen (Boeing) | **Key User :** BENYELLES Djamal Eddine

### Prérequis fonctionnels / techniques
- [ ] Calcul routes/carburant/météo | Version, intégration AIMS, format OFP

### ETL cible
```
EXTRACT : Export OFP — TRANSFORM : Extraction données structurées
LOAD : fact_ofp — FLUX ← AIMS — Fréquence : par vol
```

---

## 17. SKYBOOK — DOA 🟢

**Éditeur :** Bytron | **Key User :** BENYELLES Djamal Eddine

### ETL cible
```
EXTRACT : API SkyBook ou logs — LOAD : fact_efb_usage
FLUX ← Jet Planer (OFP), AIMS — Fréquence : quotidien
```

---

## 18. FLYSMART — DOA 🟢

**Éditeur :** Airbus/Boeing/ATR | **Key User :** BENYELLES Djamal Eddine

### ETL cible
```
EXTRACT : Export logs performances — LOAD : fact_performances_avion
Fréquence : quotidien
```

---

## 19. E-LEARNING E-EXAM PN — DOA 🟢

**Éditeur :** Développement externe | **Key User :** SAID Sihem

### ETL cible
```
EXTRACT : Export résultats (CSV/API) — TRANSFORM : Rapprochement AIMS qualifications
LOAD : fact_formations_pn — FLUX → AIMS : qualifications validées
Fréquence : hebdomadaire — Anonymisation résultats individuels
```

---

## 20. DOA MAILING — DOA 🟢

**Éditeur :** Développement externe | **Key User :** SAID Sihem / TOUTOU Aghiles, MANSEUR Amine

### ETL cible
```
EXTRACT : Export logs envois — LOAD : fact_mailings_doa
FLUX ← AIMS : listes équipages — Fréquence : quotidien
```

---

## 21. CALL DOA — DOA 🟢

**Éditeur :** Campusave | **Key User :** SAID Sihem / TOUTOU Aghiles, MANSEUR Amine

### ETL cible
```
EXTRACT : Export logs appels — LOAD : fact_appels_doa
FLUX ← AIMS : listes équipages — Fréquence : quotidien
```

---

## 22. QLIK SENSE — DPD + DOS 🟠

**Éditeur :** Qlik | **Key User :** BADAOUI Youcef / HASSAINE Hassen

### Prérequis fonctionnels / techniques
- [ ] Dashboards existants, sources de données, scripts de chargement
- [ ] Version, API Qlik, accès QVD

### ETL cible
```
EXTRACT : API Qlik ou QVD — TRANSFORM : Documentation auto des flux
LOAD : dim_dashboards_qlik — REF BI opérations sol
FLUX ← AIMS, Altéa, bases internes — Fréquence : selon rafraîchissement
```

---

## 23. WORLD TRACER — DOS 🟠

**Éditeur :** SITA | **Key User :** TOUAHRIA Faiza / HASBELLAOUI Imen

### ETL cible
```
EXTRACT : Export SITA ou API — TRANSFORM : Calcul taux perte, délais
LOAD : fact_bagages_perdus — REF Bagages
FLUX ← Altéa DCS — Fréquence : quotidien — Anonymisation passagers
```

---

## 24. CONTRÔLE PROGRAMMES PN/AVIONS — CCO 🟢

**Key User :** BENMOUFFOK El Hadi

### ETL cible
```
EXTRACT : Export résultats contrôles — LOAD : fact_controles_programmes
FLUX ← AIMS — Fréquence : quotidien
```

---

## 25-26. DASHBOARDS CCO + SUIVI IRRÉGULARITÉS — CCO 🟠

**Éditeur :** DSI (in-house) | **Key User :** CHABANE Amel / MAZARI Assia

### ETL cible
```
EXTRACT : Accès BDD (in-house DSI)
TRANSFORM : Calcul OTP, agrégation causes retards
LOAD : fact_ponctualite, fact_irregularites
FLUX ← AIMS (programme), ACARS (heures réelles) — Fréquence : temps réel + quotidien
```

---

## 27. EVALCOM — DRH 🟢

**Éditeur :** EVALCOM | **Key User :** LAKAMA Abdallah

### ETL cible
```
EXTRACT : Export agrégé annuel — LOAD : fact_evaluations (agrégé)
REF Évaluation personnel — Anonymisation stricte
```

---

## 28. AGS — DSC 🟠

**Éditeur :** Safran | **Key User :** SAMEUR Yacine

### ETL cible
```
EXTRACT : Export résultats analyses vol
TRANSFORM : Agrégation événements par type/avion, corrélation AMOS
LOAD : fact_analyses_vol — REF Données de vol FDR/QAR
FLUX → Q-Pulse : événements sécurité — Fréquence : par vol
```

---

## 29. Q-PULSE — DSC 🟠

**Éditeur :** Ideagen | **Key User :** SAMEUR Yacine

### ETL cible
```
EXTRACT : Export ou API Q-Pulse
TRANSFORM : Suivi taux clôture, corrélation AGS/AMOS
LOAD : fact_non_conformites — REF Qualité & non-conformités
FLUX ← AGS — Fréquence : hebdomadaire
```

---

## 30-32. AIMS Formation PNC / PNT / Conception Programme PN — DOA

**Key Users :** BENSALEM Lamya, SMAALLAH Yasmine, AZEROUAL Salima

### ETL cible
```
Même BDD que AIMS principal — Intégré à l'ETL AIMS (système 12)
Tables spécifiques : crew_training_pnc, crew_training_pnt, roster_design
FLUX ← E-Learning : résultats examens
```

---

## 33. GLPI — DSI 🟢

**Éditeur :** Open Source | **Key User :** YOUCEF ACHIRA Abdellah / BOUKAIOU Ahlem

### ETL cible
```
EXTRACT : API REST GLPI (native) — Données : tickets, matériels, contrats
LOAD : fact_tickets_glpi, dim_parc_informatique — REF Parc informatique
Fréquence : quotidien — Pas besoin de duplication (API native)
```

---

## 34. PORTAIL AH — DSI 🟢

**Éditeur :** DSI (in-house) | **Key User :** YOUCEF ACHIRA Abdellah / BOUKAIOU Ahlem

### ETL cible
```
EXTRACT : Accès BDD (in-house) — LOAD : fact_portail_usage
Fréquence : hebdomadaire
```

---

## 35. POWER BI — DSI + Structures 🟠

**Éditeur :** Microsoft | **Key Users :** ESSEMINIA Adnan, AGHA Riadh, YOUBI Mourad

### ETL cible
```
EXTRACT : API Power BI REST — Métadonnées dashboards, datasets, refresh
TRANSFORM : Documentation auto des dépendances
LOAD : dim_dashboards_pbi — REF Reporting transverse
FLUX ← Multiples sources — Pas de duplication (API)
```

---

## 36. SITATEX ONLINE — DSI + DC + DIVEX + DMRA 🔴

**Éditeur :** SITA | **Key User :** SALAH ROUANA Mohamed / MEBARKI Med Hamza

### Prérequis fonctionnels
- [ ] Types messages (MVT, LDM, PSM, ASM, SSM), volume quotidien, passerelle Zimbra

### Prérequis techniques
- [ ] Architecture réseau SITA, format Type B, stockage logs, API SITA

### ETL cible
```
EXTRACT : Export logs ou API SITA — Messages Type B
TRANSFORM : Parsing Type B (IATA), classification, extraction données structurées
LOAD : fact_messages_sita — REF Messages aéronautiques
FLUX ↔ Altéa, AIMS, ACARS, World Tracer | FLUX → Zimbra
Fréquence : temps réel — ⚠️ PRIORITÉ : accès logs SITATEX
```

---

## 37. ZIMBRA — DSI 🟢

**Éditeur :** Umaitek | **Key User :** YOUCEF ACHIRA Abdellah / BOUKAIOU Ahlem

### ETL cible
```
EXTRACT : API Zimbra ou logs — Stats uniquement (pas le contenu)
LOAD : fact_zimbra_stats — REF Messagerie entreprise
Fréquence : quotidien
```

---

## 38-40. BODET, DATAWINGS, SAGE FINANCE — RGF 🟢 *(Key Users à désigner)*

### ETL cible
```
BODET : Export pointages agrégés → fact_temps_rgf (mensuel)
DATAWINGS : Export opérations aéroportuaires → fact_operations_rgf (quotidien)
SAGE FINANCE : Connecteur ODBC → fact_comptabilite_rgf (mensuel)
  FLUX ← Rapid : écritures revenue
```

---

# Plan de priorisation ETL

### Phase 1 — Critiques 🔴 (Mois 1-2)
| # | Système | Justification |
|---|---------|---------------|
| 1 | **Altéa** | Hub central — alimente la majorité des systèmes |
| 2 | **AIMS** | Programmes vols — référentiel maître opérations |
| 3 | **AMOS** | Maintenance — criticité sécurité |
| 4 | **Rapid** | Revenue accounting — criticité financière |
| 5 | **SITATEX** | Messages aéronautiques — flux transversal |
| 6 | **ACARS** | Temps réel opérations |

### Phase 2 — Importants 🟠 (Mois 3-4)
SAGE STOCK, EUROCONTROL, Jet Planer, ATPCO, BAC, Dashboards CCO, Suivi Irrégularités, AGS, Q-Pulse, Qlik Sense, Power BI, World Tracer, Site Web, Accelya, AIMS Conception PN

### Phase 3 — Standard 🟢 (Mois 5-6)
BSP Link, OAG, Hermes Call Center, E-Doléance, GLPI, Portail AH, Zimbra, EVALCOM, DOA Mailing, Call DOA, E-Learning, FlySmart, SkyBook, AIMS Formation PNC/PNT, BODET, DATAWINGS, SAGE Finance RGF, Contrôle Programmes

---

# Architecture ETL cible globale

```
SOURCES (40 systèmes)
  SaaS (Altéa, Accelya, ATPCO, BAC, OAG, BSP Link)
  On-Premise (AIMS, AMOS, SAGE STOCK, Qlik)
  In-House DSI (E-Doléance, GLPI, Dashboards, Portail)
  Réseau (SITATEX, ACARS)
         │
         ▼
ZONE D'EXTRACTION
  API REST/SOAP │ ODBC/JDBC │ FTP/SFTP │ Parsing fichiers │ Data Feeds
         │
         ▼
DATA LAKE INTERMÉDIAIRE (stockage brut, historisation)
         │
         ▼
TRANSFORMATION
  Parsing (SSIM, Type B, EDIFACT) │ Normalisation IATA │ Anonymisation
         │
         ▼
BASE CARTOGRAPHIE (PostgreSQL)
  dim_systemes │ fact_vols │ fact_maintenance │ fact_revenue │ fact_messages
         │
         ▼
APPLICATION CARTOGRAPHIE (Django — 85.31.237.249)
  Visualisation flux │ Fiches système │ Dashboards │ Référentiels
```

---

# Checklist prérequis transverses

### Infrastructure
- [ ] Serveur dédié ETL + data lake
- [ ] Accès réseau aux serveurs on-premise (AIMS, AMOS, SAGE, GLPI)
- [ ] VPN/accès sécurisé aux SaaS
- [ ] Serveur SFTP pour data feeds

### Sécurité
- [ ] Politique anonymisation données personnelles
- [ ] Accès read-only aux bases dupliquées
- [ ] Chiffrement transit + repos
- [ ] Journalisation accès

### Contrats éditeurs à négocier
- [ ] **Amadeus** : accès data feeds Altéa (SFTP/API)
- [ ] **Accelya** : API Rapid + Distribution
- [ ] **SITA** : logs SITATEX + API World Tracer
- [ ] **Solution Soft** : accès BDD AIMS ou API
- [ ] **Swiss-AS** : AMOS Connect
- [ ] **ATPCO** : API tarifs
- [ ] **Qlik** : accès QVD/API
- [ ] **Ideagen** : API Q-Pulse

---

*Généré le 12 février 2026 — Direction des Systèmes d'Information, Air Algérie*
