# Plan de Priorisation ETL — Cartographie SI Air Algérie
## Document détaillé par phase, ordre d'importance et justification

> **Objectif :** Définir l'ordre d'implémentation des ETL pour les 40 systèmes du SI Air Algérie, en trois phases, classés par ordre d'importance décroissant au sein de chaque phase.
>
> *Basé sur le document PREREQUIS_ETL_CARTOGRAPHIE.md — Février 2026*

---

# Phase 1 — Systèmes Critiques 🔴
**Période : Mois 1–2 | 6 systèmes**

> Ces systèmes constituent le socle opérationnel, financier et réglementaire d'Air Algérie. Tout retard sur l'un d'eux bloque en cascade l'intégration des systèmes aval. Leur mise en place conditionne la viabilité de l'ensemble du projet de cartographie.

---

## 1.1 — ALTÉA (Suite Amadeus) — Priorité #1 absolue

**Modules :** Reservation, Ticketing, Inventory, DCS
**Éditeur :** Amadeus | **Direction :** DC + DIVEX
**Key Users :** FAIDI Fouad, FIALA Zahra, LOUNAOUCI Nassim, HASBELLAOUI Imen, GHARBI Mohamed, NAMOUNI Ali

### Justification

| Critère | Détail |
|---------|--------|
| **Centralité** | Hub central du SI — alimente directement ou indirectement **plus de 15 systèmes** (Rapid, BSP Link, Site Web, BAC, World Tracer, SITATEX, AIMS, etc.) |
| **Référentiels maîtres** | Source de vérité pour **3 domaines critiques** : Réservations & PNR, Billetterie & coupons, DCS |
| **Volume** | Système le plus volumineux : milliers de PNR/jour, coupons/jour, vols/jour |
| **Impact blocage** | Sans Altéa, impossible d'alimenter le revenue accounting (Rapid), la distribution (Accelya), le suivi bagages (World Tracer), ni les messages opérationnels (SITATEX) |
| **Complexité technique** | Accès via Data Feeds SFTP + API Web Services Amadeus — nécessite négociation contractuelle préalable |
| **Contrainte réglementaire** | Anonymisation RGPD obligatoire sur les données passagers |

### Actions prioritaires
1. **Négocier l'accès aux data feeds avec Amadeus** (PNR, APS, FLP, coupons, DCS feeds)
2. Mettre en place le serveur SFTP de réception
3. Développer les parsers EDIFACT/XML pour les feeds
4. Implémenter la dé-duplication PNR et l'anonymisation
5. Charger les tables : `fact_reservations`, `fact_coupons`, `fact_dcs`, `dim_vols`, `dim_passagers`

### Dépendances aval
- Rapid Passagers (coupons)
- BSP Link (ventes)
- Site Web (réservations en ligne)
- World Tracer (DCS bagages)
- SITATEX (messages opérationnels)
- AIMS (synchronisation programmes)
- BAC (coupons interline)

---

## 1.2 — AIMS — Priorité #2

**Modules :** Programmes vols, Crew Management, Crew Tracking, Operations, Training
**Éditeur :** Solution Soft | **Directions :** DIVEX + DC + DMRA
**Key Users :** BENAOUICHA Hanane, SIDAHMED AKKOUCHE, BENNOUAR Adnane, BADAOUI Youcef, HASSAINE Hassen

### Justification

| Critère | Détail |
|---------|--------|
| **Référentiel maître** | Source de vérité pour **2 domaines** : Programmes de vols et Équipages |
| **Centralité opérationnelle** | Alimente **10+ systèmes** : Altéa (SSIM), EUROCONTROL (FPL), ACARS, OAG, Dashboards CCO, AMOS, DOA Mailing, Call DOA, E-Learning, Contrôle Programmes |
| **Criticité sécurité** | Gestion des règles FTL (Flight Time Limitations) — non-conformité = risque réglementaire majeur |
| **Temps réel** | Données nécessaires en temps réel pour les opérations du jour (CCO, DOA) |
| **Transversalité** | Touche 3 directions (DIVEX, DC, DMRA) — le système le plus transversal après Altéa |

### Actions prioritaires
1. **Obtenir l'accès read-only à la BDD AIMS** (négociation Solution Soft)
2. Documenter le schéma BDD (tables : `flights`, `crew_roster`, `crew_qualifications`, `aircraft`, `rotations`)
3. Mettre en place la réplication read-only
4. Développer les exports SSIM et les parsers associés
5. Charger : `fact_vols`, `fact_crew_roster`, `dim_aircraft`, `dim_crew`

### Dépendances aval
- Altéa (programmes SSIM)
- EUROCONTROL (plans de vol)
- ACARS (corrélation mouvements)
- OAG (programmes publiés)
- AMOS (heures vol/cycles, disponibilité avions)
- Dashboards CCO, Suivi Irrégularités
- DOA Mailing, Call DOA, E-Learning
- Contrôle Programmes PN/Avions
- AIMS Formation PNC/PNT, Conception Programme PN

---

## 1.3 — AMOS — Priorité #3

**Modules :** OT, Planification maintenance, Navigabilité, Pièces
**Éditeur :** Swiss Aviation Software | **Direction :** DMRA
**Key Users :** BOUGUEZIZ Samir, FERRADJI Farid

### Justification

| Critère | Détail |
|---------|--------|
| **Criticité sécurité** | Système de maintenance aéronautique — **impact direct sur la navigabilité des aéronefs** |
| **Référentiel maître** | Source de vérité pour le domaine **Maintenance** |
| **Conformité réglementaire** | Suivi des AD/SB/CDCCL — obligations de l'autorité de l'aviation civile |
| **Lien AIMS** | Dépend des heures vol/cycles d'AIMS et alimente AIMS en disponibilité avions |
| **Lien SAGE STOCK** | Consomme les données pièces de SAGE STOCK — flux bidirectionnel |
| **Indicateurs critiques** | Calcul MTBF/MTTR indispensable pour la planification maintenance |

### Actions prioritaires
1. **Négocier l'accès AMOS Connect ou réplication Oracle read-only** (contrat Swiss-AS)
2. Documenter le schéma Oracle
3. Développer le connecteur Oracle ou AMOS Connect API
4. Implémenter le rapprochement SAGE STOCK (pièces)
5. Charger : `fact_work_orders`, `fact_maintenance`

### Dépendances
- **Entrantes :** AIMS (heures vol/cycles), SAGE STOCK (pièces)
- **Sortantes :** AIMS (disponibilité avions), Q-Pulse (corrélation non-conformités)

---

## 1.4 — RAPID PASSAGERS — Priorité #4

**Éditeur :** Accelya | **Direction :** DFC
**Key Users :** HADJ SAID Nadir, BELKACEMI Mohand

### Justification

| Critère | Détail |
|---------|--------|
| **Criticité financière** | Système de **revenue accounting** — cœur de la chaîne financière de la compagnie |
| **Référentiel maître** | Source de vérité pour le domaine **Revenue accounting** |
| **Flux financiers** | Alimente SAGE Finance (écritures comptables) et BAC (facturation interline) |
| **Dépendance Altéa** | Consomme les coupons d'Altéa — doit être implémenté juste après |
| **Impact décisionnel** | Calcul des revenus nets par route — données stratégiques pour le réseau |

### Actions prioritaires
1. **Négocier l'accès API/exports avec Accelya**
2. Identifier l'architecture (SaaS vs on-premise) et la BDD
3. Développer le rapprochement coupons Altéa
4. Implémenter le calcul revenus nets par route
5. Charger : `fact_revenue_accounting`

### Dépendances
- **Entrantes :** Altéa (coupons)
- **Sortantes :** SAGE Finance (écritures), BAC (facturation interline)

---

## 1.5 — SITATEX ONLINE — Priorité #5

**Éditeur :** SITA | **Directions :** DSI + DC + DIVEX + DMRA
**Key Users :** SALAH ROUANA Mohamed, MEBARKI Med Hamza

### Justification

| Critère | Détail |
|---------|--------|
| **Transversalité maximale** | Touche **4 directions** — le système le plus transversal en termes de directions impliquées |
| **Référentiel maître** | Source de vérité pour les **Messages aéronautiques** |
| **Flux critique** | Véhicule les messages MVT, LDM, PSM, ASM, SSM — indispensables aux opérations quotidiennes |
| **Interconnexions** | Flux bidirectionnels avec Altéa, AIMS, ACARS, World Tracer + passerelle vers Zimbra |
| **Temps réel** | Messages en temps réel — tout retard impacte les opérations |
| **Complexité technique** | Parsing messages Type B (format IATA) — compétence spécialisée requise |

### Actions prioritaires
1. **Négocier l'accès aux logs SITATEX avec SITA**
2. Documenter l'architecture réseau SITA et le format Type B
3. Développer le parser Type B (IATA)
4. Implémenter la classification et l'extraction de données structurées
5. Charger : `fact_messages_sita`

### Dépendances
- **Bidirectionnelles :** Altéa, AIMS, ACARS, World Tracer
- **Sortantes :** Zimbra (passerelle messages)

---

## 1.6 — ACARS / HERMES — Priorité #6

**Éditeur :** Collins ARINC | **Direction :** DIVEX (CCO)
**Key Users :** LADJICI Fatima, BENNOUAR Adnane

### Justification

| Critère | Détail |
|---------|--------|
| **Temps réel opérationnel** | Seule source de données **en temps réel** sur les mouvements avions (OOOI : Out, Off, On, In) |
| **Calcul ponctualité** | Indispensable pour le calcul OTP (On-Time Performance) — indicateur clé de la compagnie |
| **Alimentation CCO** | Alimente les Dashboards CCO et le Suivi Irrégularités en données temps réel |
| **Corrélation AIMS** | Permet de comparer heures planifiées (AIMS) vs heures réelles (ACARS) |
| **Volume** | Messages techniques continus pendant chaque vol |

### Actions prioritaires
1. Documenter la version Hermes et le réseau ARINC/SITA
2. Identifier le format des messages et le stockage des logs
3. Développer le parser ACARS (messages OOOI)
4. Implémenter la corrélation avec AIMS
5. Charger : `fact_mouvements_avions`

### Dépendances
- **Sortantes :** AIMS, Dashboards CCO, SITATEX
- **Corrélation :** AIMS (heures planifiées vs réelles)

---

# Phase 2 — Systèmes Importants 🟠
**Période : Mois 3–4 | 15 systèmes**

> Ces systèmes complètent l'écosystème opérationnel et financier. Ils dépendent pour la plupart des systèmes de Phase 1 et apportent une valeur significative en termes de suivi, conformité et pilotage. Classés par ordre d'importance décroissant.

---

## 2.1 — SAGE STOCK (DAGP) — Priorité #1 Phase 2

**Éditeur :** Sans contrat | **Key Users :** ATTOUT Abedlhafid, AIT MEZIANE Amar

### Justification

| Critère | Détail |
|---------|--------|
| **Référentiel maître** | Source de vérité pour **Stocks & pièces** |
| **Lien AMOS critique** | Alimente AMOS en données pièces de rechange — flux à automatiser |
| **Risque contractuel** | **Absence de contrat éditeur** — risque majeur à adresser en priorité |
| **Impact maintenance** | Sans données stock fiables, la planification maintenance (AMOS) est compromise |

### Actions prioritaires
1. Identifier les risques liés à l'absence de contrat et les alternatives
2. Documenter la version SAGE, l'architecture et le schéma BDD
3. Mettre en place le connecteur ODBC/JDBC
4. Normaliser les codes articles (mapping vers AMOS)
5. Charger : `dim_articles`, `fact_mouvements_stock`

---

## 2.2 — ATPCO — Priorité #2 Phase 2

**Éditeur :** ATPCO | **Key Users :** LAIDANI Zakaria, FAIDI Foued

### Justification

| Critère | Détail |
|---------|--------|
| **Référentiel maître** | Source de vérité pour les **Tarifs aériens** |
| **Alimentation Altéa/GDS** | Les tarifs publiés alimentent directement Altéa et les GDS — impact commercial direct |
| **Complexité formats** | Formats ATPCO Category spécifiques — parsing spécialisé nécessaire |
| **Fréquence dynamique** | Chargement à chaque publication tarifaire — pas de batch fixe |

### Actions prioritaires
1. Négocier l'accès API ATPCO
2. Développer le parser formats ATPCO Category
3. Implémenter le mapping O&D/classes
4. Charger : `dim_tarifs`, `fact_publications_tarifs`

---

## 2.3 — BAC (Amadeus) — Priorité #3 Phase 2

**Éditeur :** Amadeus | **Key Users :** HASSISSENE Chemseddine, BENMADI Soumeya

### Justification

| Critère | Détail |
|---------|--------|
| **Facturation interline** | Gère la facturation entre compagnies — impact financier direct |
| **Lien Rapid** | Alimente Rapid en données de facturation interline |
| **Lien Altéa** | Consomme les coupons interline d'Altéa |
| **Cycle mensuel** | Cycle interline mensuel — fenêtre de réconciliation contrainte |

### Actions prioritaires
1. Documenter les formats EDIFACT (IDEC) et l'API BAC
2. Développer le parser EDIFACT
3. Implémenter le rapprochement avec Rapid
4. Charger : `fact_interline_billing`

---

## 2.4 — Dashboards CCO + Suivi Irrégularités — Priorité #4 Phase 2

**Éditeur :** DSI (in-house) | **Key Users :** CHABANE Amel, MAZARI Assia

### Justification

| Critère | Détail |
|---------|--------|
| **Pilotage opérationnel** | Calcul OTP et agrégation causes retards — outils de décision quotidiens du CCO |
| **Temps réel** | Nécessite des données temps réel (ACARS) + quotidiennes (AIMS) |
| **In-house** | Développé en interne — accès BDD direct, pas de négociation éditeur |
| **Dépendance Phase 1** | Exploitable dès que AIMS et ACARS sont en place |

### Actions prioritaires
1. Accéder à la BDD in-house DSI
2. Implémenter le calcul OTP et l'agrégation causes retards
3. Charger : `fact_ponctualite`, `fact_irregularites`

---

## 2.5 — AGS (Safran) — Priorité #5 Phase 2

**Éditeur :** Safran | **Key User :** SAMEUR Yacine

### Justification

| Critère | Détail |
|---------|--------|
| **Référentiel maître** | Source de vérité pour les **Données de vol FDR/QAR** |
| **Sécurité des vols** | Analyse des données de vol — détection d'événements sécurité |
| **Alimentation Q-Pulse** | Les événements sécurité détectés alimentent Q-Pulse (non-conformités) |
| **Corrélation AMOS** | Permet de croiser événements vol avec données maintenance |

### Actions prioritaires
1. Documenter les formats d'export des analyses vol
2. Développer l'agrégation événements par type/avion
3. Implémenter la corrélation AMOS
4. Charger : `fact_analyses_vol`

---

## 2.6 — Q-PULSE (Ideagen) — Priorité #6 Phase 2

**Éditeur :** Ideagen | **Key User :** SAMEUR Yacine

### Justification

| Critère | Détail |
|---------|--------|
| **Référentiel maître** | Source de vérité pour **Qualité & non-conformités** |
| **Conformité réglementaire** | Suivi des non-conformités — obligation réglementaire aviation |
| **Dépendance AGS** | Consomme les événements sécurité d'AGS |
| **Corrélation AMOS** | Croisement avec les données maintenance |

### Actions prioritaires
1. Négocier l'accès API Q-Pulse (contrat Ideagen)
2. Implémenter le suivi taux de clôture
3. Développer la corrélation AGS/AMOS
4. Charger : `fact_non_conformites`

---

## 2.7 — EUROCONTROL — Priorité #7 Phase 2

**Éditeur :** EUROCONTROL | **Key User :** BENYELLES Djamal Eddine

### Justification

| Critère | Détail |
|---------|--------|
| **Réglementaire** | Gestion des slots et plans de vol — conformité espace aérien européen |
| **Lien AIMS** | Consomme les données AIMS pour générer les FPL |
| **API disponible** | API NM B2B existante — intégration facilitée |

### Actions prioritaires
1. Configurer l'accès API NM B2B
2. Développer le parser FPL (format ICAO) et ADEXP
3. Implémenter la corrélation AIMS
4. Charger : `fact_plans_de_vol`

---

## 2.8 — JET PLANER (Jeppesen/Boeing) — Priorité #8 Phase 2

**Éditeur :** Jeppesen (Boeing) | **Key User :** BENYELLES Djamal Eddine

### Justification

| Critère | Détail |
|---------|--------|
| **Sécurité opérationnelle** | Calcul routes, carburant, météo — données critiques pour chaque vol |
| **Lien AIMS** | Intégré avec AIMS pour les données de vol |
| **Format OFP** | Export OFP (Operational Flight Plan) — extraction données structurées |

### Actions prioritaires
1. Documenter le format OFP et l'intégration AIMS
2. Développer l'extraction de données structurées depuis les OFP
3. Charger : `fact_ofp`

---

## 2.9 — WORLD TRACER (SITA) — Priorité #9 Phase 2

**Éditeur :** SITA | **Key Users :** TOUAHRIA Faiza, HASBELLAOUI Imen

### Justification

| Critère | Détail |
|---------|--------|
| **Référentiel maître** | Source de vérité pour les **Bagages** |
| **Qualité de service** | Taux de perte bagages — indicateur qualité majeur pour les passagers |
| **Lien Altéa DCS** | Consomme les données DCS d'Altéa |
| **Anonymisation** | Données passagers — anonymisation obligatoire |

### Actions prioritaires
1. Négocier l'accès API/export SITA
2. Implémenter le calcul taux de perte et délais
3. Charger : `fact_bagages_perdus`

---

## 2.10 — SITE WEB AIR ALGÉRIE — Priorité #10 Phase 2

**Éditeur :** KYO | **Key Users :** BELDJERDI Zakaria, BACHA Amine

### Justification

| Critère | Détail |
|---------|--------|
| **Canal de vente direct** | Réservation en ligne, check-in — canal commercial stratégique |
| **Flux bidirectionnel Altéa** | Consomme disponibilités/tarifs, envoie réservations |
| **Analytics** | Taux de conversion, trafic — données marketing essentielles |
| **Contrat KYO** | Nécessite coordination avec l'éditeur |

### Actions prioritaires
1. Documenter le stack technique et l'intégration Altéa (API Amadeus)
2. Configurer l'accès analytics + logs
3. Implémenter l'agrégation trafic et taux de conversion
4. Charger : `fact_trafic_web`

---

## 2.11 — ACCELYA DISTRIBUTION — Priorité #11 Phase 2

**Éditeur :** Accelya | **Key Users :** SAAD Nasima, HALISSE Abderrahim

### Justification

| Critère | Détail |
|---------|--------|
| **Distribution commerciale** | Gestion des ventes et émission billets par canaux |
| **Lien Altéa** | Rapprochement avec les réservations Altéa |
| **Lien Rapid** | Alimente le revenue accounting |
| **Même éditeur que Rapid** | Synergie de négociation contractuelle avec Accelya |

### Actions prioritaires
1. Documenter le mode d'accès SaaS et les API/formats disponibles
2. Développer le rapprochement Altéa et la normalisation codes IATA
3. Charger : `fact_ventes_distribution`

---

## 2.12 — QLIK SENSE — Priorité #12 Phase 2

**Éditeur :** Qlik | **Key Users :** BADAOUI Youcef, HASSAINE Hassen

### Justification

| Critère | Détail |
|---------|--------|
| **BI opérations sol** | Dashboards existants pour les opérations — documentation des flux existants |
| **Sources multiples** | Consomme AIMS, Altéa, bases internes — cartographie des dépendances BI |
| **Documentation** | Permet de documenter automatiquement les flux de données existants |

### Actions prioritaires
1. Documenter les dashboards existants et scripts de chargement
2. Négocier l'accès API Qlik ou QVD
3. Charger : `dim_dashboards_qlik`

---

## 2.13 — POWER BI — Priorité #13 Phase 2

**Éditeur :** Microsoft | **Key Users :** ESSEMINIA Adnan, AGHA Riadh, YOUBI Mourad

### Justification

| Critère | Détail |
|---------|--------|
| **Référentiel reporting** | Source de vérité pour le **Reporting transverse** |
| **Multi-sources** | Consomme de multiples sources — cartographie des dépendances BI |
| **API native** | API Power BI REST disponible — pas de duplication nécessaire |
| **Documentation auto** | Permet de documenter automatiquement les dépendances des dashboards |

### Actions prioritaires
1. Configurer l'accès API Power BI REST
2. Extraire les métadonnées (dashboards, datasets, refresh)
3. Charger : `dim_dashboards_pbi`

---

## 2.14 — AIMS Formation PNC/PNT + Conception Programme PN — Priorité #14 Phase 2

**Key Users :** BENSALEM Lamya, SMAALLAH Yasmine, AZEROUAL Salima

### Justification

| Critère | Détail |
|---------|--------|
| **Même BDD qu'AIMS** | Intégré à l'ETL AIMS principal — effort marginal |
| **Gestion équipages** | Formation et conception des programmes PN — lien direct avec les qualifications |
| **Lien E-Learning** | Consomme les résultats d'examens de E-Learning |

### Actions prioritaires
1. Identifier les tables spécifiques : `crew_training_pnc`, `crew_training_pnt`, `roster_design`
2. Étendre l'ETL AIMS existant (Phase 1)

---

## 2.15 — SAGE FINANCE (volet RGF) — Priorité #15 Phase 2

**Direction :** RGF | **Key Users :** À désigner

### Justification

| Critère | Détail |
|---------|--------|
| **Comptabilité** | Écritures comptables — lien direct avec Rapid (revenue accounting) |
| **Connecteur existant** | Connecteur ODBC disponible (même technologie que SAGE STOCK) |
| **Fréquence mensuelle** | Batch mensuel — charge technique limitée |

### Actions prioritaires
1. Désigner les key users RGF
2. Réutiliser le connecteur ODBC de SAGE STOCK
3. Charger : `fact_comptabilite_rgf`

---

# Phase 3 — Systèmes Standard 🟢
**Période : Mois 5–6 | 18 systèmes**

> Ces systèmes sont soit autonomes, soit à faible volumétrie, soit dotés d'API natives facilitant l'intégration. Leur implémentation est plus rapide et moins risquée. Classés par ordre d'importance décroissant.

---

## 3.1 — BSP LINK (IATA) — Priorité #1 Phase 3

**Éditeur :** IATA | **Key Users :** SAAD Nassima, HALISSE Abderrahim

### Justification

| Critère | Détail |
|---------|--------|
| **Rapprochement financier** | Rapports BSP — rapprochement avec Accelya et Rapid |
| **Cycle BSP** | Fréquence hebdomadaire (cycle BSP IATA) |
| **Export disponible** | Portail IATA avec export fichiers CSV/XML |

### Actions prioritaires
1. Configurer l'export automatisé depuis le portail IATA
2. Développer le rapprochement Accelya + Rapid
3. Charger : `fact_bsp_ventes`

---

## 3.2 — E-DOLÉANCE — Priorité #2 Phase 3

**Éditeur :** DSI (in-house) | **Key Users :** AKKACHA Mohamed Amine, BELDJERDI Zakaria

### Justification

| Critère | Détail |
|---------|--------|
| **Référentiel maître** | Source de vérité pour les **Réclamations passagers** |
| **In-house** | Développé en interne — accès direct BDD et code source |
| **Lien Altéa** | Enrichissement possible avec les PNR Altéa |
| **Anonymisation** | Données passagers — anonymisation obligatoire |

### Actions prioritaires
1. Documenter la technologie, le schéma BDD et les API existantes
2. Développer l'enrichissement PNR Altéa
3. Charger : `fact_reclamations`

---

## 3.3 — GLPI — Priorité #3 Phase 3

**Éditeur :** Open Source | **Key Users :** YOUCEF ACHIRA Abdellah, BOUKAIOU Ahlem

### Justification

| Critère | Détail |
|---------|--------|
| **Référentiel maître** | Source de vérité pour le **Parc informatique** |
| **API REST native** | GLPI dispose d'une API REST native — intégration immédiate |
| **Pas de duplication** | API native suffisante — pas besoin de réplication BDD |
| **Gouvernance IT** | Visibilité sur le parc informatique et les tickets support |

### Actions prioritaires
1. Configurer l'accès API REST GLPI
2. Charger : `fact_tickets_glpi`, `dim_parc_informatique`

---

## 3.4 — HERMES CALL CENTER (Vocalcom) — Priorité #4 Phase 3

**Éditeur :** Vocalcom | **Key Users :** BOUCHIK Mounir, FODILI Mohamed Yacine

### Justification

| Critère | Détail |
|---------|--------|
| **Qualité de service** | Statistiques appels, durées, motifs — indicateurs qualité service client |
| **Corrélation E-Doléance** | Croisement avec les réclamations pour une vue complète du service client |
| **Lien Altéa** | Consultation PNR par les agents |

### Actions prioritaires
1. Documenter la version Vocalcom, BDD et API/exports disponibles
2. Développer l'agrégation par motif et la corrélation E-Doléance
3. Charger : `fact_appels_callcenter` (anonymisation numéros téléphone)

---

## 3.5 — OAG / INNOVATA — Priorité #5 Phase 3

**Éditeur :** OAG | **Key Users :** SAFAR ZITOUN Naim, KARI Fateh

### Justification

| Critère | Détail |
|---------|--------|
| **Analyse marché** | Horaires et analyse routes — intelligence concurrentielle |
| **Comparaison AIMS** | Permet de comparer les programmes publiés vs planifiés |
| **API disponible** | API Schedules OAG + formats SSIM/CSV |

### Actions prioritaires
1. Configurer l'accès API OAG ou fichiers SSIM
2. Développer le parsing SSIM et la comparaison AIMS
3. Charger : `dim_horaires_marche`

---

## 3.6 — E-LEARNING E-EXAM PN — Priorité #6 Phase 3

**Éditeur :** Développement externe | **Key User :** SAID Sihem

### Justification

| Critère | Détail |
|---------|--------|
| **Qualifications équipages** | Résultats examens — alimentation des qualifications AIMS |
| **Conformité** | Suivi des formations obligatoires PN |

### Actions prioritaires
1. Configurer l'export résultats (CSV/API)
2. Développer le rapprochement AIMS qualifications
3. Charger : `fact_formations_pn` (anonymisation résultats individuels)

---

## 3.7 — ZIMBRA — Priorité #7 Phase 3

**Éditeur :** Umaitek | **Key Users :** YOUCEF ACHIRA Abdellah, BOUKAIOU Ahlem

### Justification

| Critère | Détail |
|---------|--------|
| **Messagerie entreprise** | Statistiques d'usage — pas le contenu des messages |
| **Passerelle SITATEX** | Reçoit les messages SITATEX via passerelle |
| **API disponible** | API Zimbra ou logs — intégration simple |

### Actions prioritaires
1. Configurer l'accès API Zimbra ou logs
2. Charger : `fact_zimbra_stats`

---

## 3.8 — CONTRÔLE PROGRAMMES PN/AVIONS — Priorité #8 Phase 3

**Key User :** BENMOUFFOK El Hadi

### Justification

| Critère | Détail |
|---------|--------|
| **Contrôle qualité** | Résultats des contrôles sur les programmes PN et avions |
| **Dépendance AIMS** | Consomme les données AIMS — exploitable dès Phase 1 terminée |
| **Faible complexité** | Export simple de résultats |

### Actions prioritaires
1. Configurer l'export résultats contrôles
2. Charger : `fact_controles_programmes`

---

## 3.9 — DOA MAILING — Priorité #9 Phase 3

**Éditeur :** Développement externe | **Key Users :** SAID Sihem, TOUTOU Aghiles, MANSEUR Amine

### Justification

| Critère | Détail |
|---------|--------|
| **Communication équipages** | Envoi de mailings aux équipages — lien AIMS |
| **Faible complexité** | Export logs envois uniquement |

### Actions prioritaires
1. Configurer l'export logs envois
2. Charger : `fact_mailings_doa`

---

## 3.10 — CALL DOA — Priorité #10 Phase 3

**Éditeur :** Campusave | **Key Users :** SAID Sihem, TOUTOU Aghiles, MANSEUR Amine

### Justification

| Critère | Détail |
|---------|--------|
| **Communication équipages** | Appels aux équipages — lien AIMS |
| **Faible complexité** | Export logs appels uniquement |

### Actions prioritaires
1. Configurer l'export logs appels
2. Charger : `fact_appels_doa`

---

## 3.11 — SKYBOOK (Bytron) — Priorité #11 Phase 3

**Éditeur :** Bytron | **Key User :** BENYELLES Djamal Eddine

### Justification

| Critère | Détail |
|---------|--------|
| **EFB** | Usage des tablettes de vol (Electronic Flight Bag) |
| **Lien Jet Planer/AIMS** | Consomme les OFP et données AIMS |
| **Faible volumétrie** | Logs d'usage uniquement |

### Actions prioritaires
1. Configurer l'accès API SkyBook ou logs
2. Charger : `fact_efb_usage`

---

## 3.12 — FLYSMART — Priorité #12 Phase 3

**Éditeur :** Airbus/Boeing/ATR | **Key User :** BENYELLES Djamal Eddine

### Justification

| Critère | Détail |
|---------|--------|
| **Performances avion** | Données de performances — utile pour l'optimisation |
| **Autonome** | Pas de dépendance forte avec d'autres systèmes |
| **Export simple** | Logs performances uniquement |

### Actions prioritaires
1. Configurer l'export logs performances
2. Charger : `fact_performances_avion`

---

## 3.13 — PORTAIL AH — Priorité #13 Phase 3

**Éditeur :** DSI (in-house) | **Key Users :** YOUCEF ACHIRA Abdellah, BOUKAIOU Ahlem

### Justification

| Critère | Détail |
|---------|--------|
| **Portail interne** | Usage du portail interne — statistiques |
| **In-house** | Accès BDD direct |
| **Faible fréquence** | Hebdomadaire — faible charge |

### Actions prioritaires
1. Accéder à la BDD in-house
2. Charger : `fact_portail_usage`

---

## 3.14 — EVALCOM — Priorité #14 Phase 3

**Éditeur :** EVALCOM | **Key User :** LAKAMA Abdallah

### Justification

| Critère | Détail |
|---------|--------|
| **RH** | Évaluation du personnel — données sensibles |
| **Fréquence annuelle** | Export agrégé annuel uniquement |
| **Anonymisation stricte** | Données individuelles — anonymisation obligatoire |

### Actions prioritaires
1. Configurer l'export agrégé annuel
2. Charger : `fact_evaluations` (anonymisation stricte)

---

## 3.15 — BODET — Priorité #15 Phase 3

**Direction :** RGF | **Key Users :** À désigner

### Justification

| Critère | Détail |
|---------|--------|
| **Pointages** | Données de pointage du personnel |
| **Fréquence mensuelle** | Export agrégé mensuel — faible charge |
| **Autonome** | Pas de dépendance forte |

### Actions prioritaires
1. Désigner les key users
2. Configurer l'export pointages agrégés
3. Charger : `fact_temps_rgf`

---

## 3.16 — DATAWINGS — Priorité #16 Phase 3

**Direction :** RGF | **Key Users :** À désigner

### Justification

| Critère | Détail |
|---------|--------|
| **Opérations aéroportuaires** | Données opérations au sol |
| **Fréquence quotidienne** | Export quotidien — volumétrie modérée |

### Actions prioritaires
1. Désigner les key users
2. Configurer l'export opérations aéroportuaires
3. Charger : `fact_operations_rgf`

---

## 3.17 — AIMS Formation PNC — Priorité #17 Phase 3

**Key User :** BENSALEM Lamya

### Justification

| Critère | Détail |
|---------|--------|
| **Intégré AIMS** | Même BDD qu'AIMS — déjà couvert par l'ETL AIMS Phase 1/2 |
| **Tables spécifiques** | `crew_training_pnc` — extension marginale |

> *Note : Si non traité en Phase 2 avec le lot AIMS Formation, à finaliser ici.*

---

## 3.18 — AIMS Formation PNT — Priorité #18 Phase 3

**Key User :** SMAALLAH Yasmine

### Justification

| Critère | Détail |
|---------|--------|
| **Intégré AIMS** | Même BDD qu'AIMS — déjà couvert par l'ETL AIMS Phase 1/2 |
| **Tables spécifiques** | `crew_training_pnt` — extension marginale |

> *Note : Si non traité en Phase 2 avec le lot AIMS Formation, à finaliser ici.*

---

# Synthèse globale

## Vue d'ensemble par phase

| Phase | Période | Nb systèmes | Criticité | Effort estimé |
|-------|---------|-------------|-----------|---------------|
| **Phase 1** 🔴 | Mois 1–2 | 6 | Critique — socle opérationnel | **Élevé** — négociations éditeurs, parsing complexe, temps réel |
| **Phase 2** 🟠 | Mois 3–4 | 15 | Important — complément opérationnel et financier | **Moyen** — dépend des acquis Phase 1 |
| **Phase 3** 🟢 | Mois 5–6 | 18 | Standard — autonome, faible risque | **Faible** — API natives, exports simples |

## Négociations contractuelles critiques (à lancer dès le Mois 0)

| Éditeur | Système | Objet de la négociation | Phase |
|---------|---------|------------------------|-------|
| **Amadeus** | Altéa | Accès data feeds SFTP/API | Phase 1 |
| **Solution Soft** | AIMS | Accès BDD read-only ou API | Phase 1 |
| **Swiss-AS** | AMOS | AMOS Connect ou réplication Oracle | Phase 1 |
| **Accelya** | Rapid + Distribution | API exports | Phase 1 + 2 |
| **SITA** | SITATEX + World Tracer | Logs SITATEX + API World Tracer | Phase 1 + 2 |
| **Collins ARINC** | ACARS | Accès logs Hermes | Phase 1 |
| **ATPCO** | ATPCO | API tarifs | Phase 2 |
| **Ideagen** | Q-Pulse | API Q-Pulse | Phase 2 |
| **Qlik** | Qlik Sense | Accès QVD/API | Phase 2 |

## Prérequis transverses (à traiter en parallèle de la Phase 1)

1. **Infrastructure** : Serveur dédié ETL + data lake, accès réseau on-premise, VPN SaaS, serveur SFTP
2. **Sécurité** : Politique anonymisation, accès read-only, chiffrement, journalisation
3. **Compétences** : Parsing EDIFACT, Type B (IATA), SSIM, ACARS — formations ou recrutement si nécessaire
4. **Gouvernance** : Désignation des key users manquants (RGF : BODET, DATAWINGS, SAGE Finance)

---

*Document généré le 14 février 2026 — Direction des Systèmes d'Information, Air Algérie*
*Basé sur le document PREREQUIS_ETL_CARTOGRAPHIE.md*
