# Questions Techniques ETL — Par Système, Par Phase

> **Objectif :** Recueillir les informations techniques nécessaires à la mise en place des ETL et à la duplication des bases de données pour chaque système du SI Air Algérie.
>
> *Basé sur le document PREREQUIS_ETL_CARTOGRAPHIE.md — Février 2026*
> *Ordre de priorisation issu du PLAN_PRIORISATION_ETL.md*

---

# Phase 1 — Systèmes Critiques 🔴 (Mois 1–2)

---

## 1.1 — SUITE ALTÉA (Amadeus)

**Éditeur :** Amadeus | **Modules :** Reservation, Ticketing, Inventory, DCS
**Key Users :** FAIDI Fouad, FIALA Zahra, LOUNAOUCI Nassim, HASBELLAOUI Imen, GHARBI Mohamed, NAMOUNI Ali

### Questions techniques

1. Quelle est la version exacte d'Altéa actuellement en production ? Existe-t-il un environnement de test (TEST/UAT) en plus de la PROD ?
2. Quelles API Amadeus sont actuellement disponibles et/ou activées (e-Retail, Web Services, NDC) ?
3. Quels data feeds Amadeus sont actifs aujourd'hui (PNR Data Feed, APS, FLP, Coupon feeds, DCS feeds) ? Par quel canal sont-ils reçus (FTP/SFTP) ?
4. Quels sont les formats des données reçues via les data feeds (EDIFACT, XML, CSV) ?
5. Le contrat Amadeus actuel inclut-il l'accès aux data feeds ? Si non, quelles sont les conditions pour les obtenir ?
6. Existe-t-il un serveur SFTP dédié à la réception des data feeds Amadeus ? Si oui, quel est son adresse/nom ?
7. Quelles contraintes de sécurité et d'anonymisation (RGPD) s'appliquent aux données passagers extraites d'Altéa ?
8. Quel est le volume estimé de données quotidien (nombre de PNR, coupons, enregistrements DCS) ?

> **Réponse :**
>
>

---

## 1.2 — AIMS (Solution Soft)

**Éditeur :** Solution Soft | **Modules :** Programmes vols, Crew Management, Crew Tracking, Operations, Training
**Key Users :** BENAOUICHA Hanane, SIDAHMED AKKOUCHE, BENNOUAR Adnane, BADAOUI Youcef, HASSAINE Hassen

### Questions techniques

1. Quelle est la version exacte d'AIMS en production ?
2. Quelle est l'architecture du système (client/serveur, web) ? Quel est le SGBD utilisé (Oracle, SQL Server, autre) ?
3. Quels sont les environnements disponibles (PROD, TEST, DEV) ?
4. Le schéma de la base de données est-il documenté ? Pouvez-vous fournir la liste des tables principales (flights, crew_roster, crew_qualifications, aircraft, rotations) avec leurs colonnes et relations ?
5. Existe-t-il une API AIMS ou un module d'export natif ? Si oui, quels formats sont supportés (SSIM, CSV, XML) ?
6. Le contrat Solution Soft permet-il l'accès en lecture seule à la base de données ? Sinon, quelles sont les conditions pour l'obtenir ?
7. Sur quel serveur AIMS est-il hébergé (nom, OS, IP) ? Quel est le mode d'accès réseau ?
8. Quelle est la politique de sauvegarde actuelle ? Est-il possible de mettre en place une réplication read-only de la BDD ?
9. Quels sont les flux de données existants entre AIMS et les autres systèmes (Altéa SSIM, EUROCONTROL FPL, ACARS, AMOS) ? Sont-ils automatisés ?

> **Réponse :**
>
>

---

## 1.3 — AMOS (Swiss Aviation Software)

**Éditeur :** Swiss Aviation Software | **Modules :** OT, Planification maintenance, Navigabilité, Pièces
**Key Users :** BOUGUEZIZ Samir, FERRADJI Farid

### Questions techniques

1. Quelle est la version exacte d'AMOS en production ?
2. Quelle est l'architecture du système ? Le SGBD est-il Oracle ? Quelle version ?
3. Le schéma de la base de données Oracle est-il documenté ? Pouvez-vous fournir la structure des tables principales ?
4. Le module AMOS Connect est-il activé ou disponible dans le contrat actuel avec Swiss-AS ?
5. Si AMOS Connect n'est pas disponible, est-il possible d'accéder directement à la base Oracle en lecture seule ?
6. Quelles sont les conditions contractuelles Swiss-AS pour l'accès aux données (API, réplication, export) ?
7. Sur quel serveur AMOS est-il hébergé (nom, OS, IP) ? Quel est le mode d'accès réseau ?
8. Quelle est la politique de sauvegarde actuelle ? Est-il possible de mettre en place une réplication Oracle read-only ?
9. Comment les données de SAGE STOCK (pièces) sont-elles actuellement échangées avec AMOS ? Ce flux est-il automatisé ou manuel ?
10. Comment AMOS reçoit-il les heures de vol et les cycles depuis AIMS ? Ce flux est-il automatisé ?

> **Réponse :**
>
>

---

## 1.4 — RAPID PASSAGERS (Accelya)

**Éditeur :** Accelya
**Key Users :** HADJ SAID Nadir, BELKACEMI Mohand

### Questions techniques

1. Quelle est la version exacte de Rapid Passagers en production ?
2. Quelle est l'architecture du système : SaaS ou on-premise ?
3. Quel est le SGBD utilisé (Oracle, SQL Server, autre) ?
4. Existe-t-il une API ou un module d'export natif ? Quels formats sont supportés ?
5. Le contrat Accelya actuel permet-il l'accès aux données (API, exports) ? Quelles sont les conditions ?
6. Si on-premise : sur quel serveur est-il hébergé (nom, OS, IP) ? Quel est le mode d'accès réseau ?
7. Comment les coupons Altéa sont-ils actuellement transmis à Rapid ? Ce flux est-il automatisé ?
8. Comment les écritures comptables sont-elles transmises à SAGE Finance ? Quel format ?
9. Quelle est la politique de sauvegarde actuelle ?

> **Réponse :**
>
>

---

## 1.5 — SITATEX ONLINE (SITA)

**Éditeur :** SITA
**Key Users :** SALAH ROUANA Mohamed, MEBARKI Med Hamza

### Questions techniques

1. Quelle est l'architecture du réseau SITA utilisé par Air Algérie ?
2. Quel est le format exact des messages Type B échangés (MVT, LDM, PSM, ASM, SSM) ?
3. Les messages SITATEX sont-ils stockés localement ? Si oui, où et dans quel format (logs, BDD) ?
4. Existe-t-il une API SITA pour accéder aux messages ou aux logs ?
5. Le contrat SITA actuel permet-il l'accès aux logs SITATEX ? Quelles sont les conditions pour l'obtenir ?
6. Comment fonctionne la passerelle SITATEX → Zimbra ? Est-elle documentée ?
7. Quel est le volume quotidien de messages échangés ?
8. Quels sont les flux automatisés existants entre SITATEX et les autres systèmes (Altéa, AIMS, ACARS, World Tracer) ?

> **Réponse :**
>
>

---

## 1.6 — ACARS / HERMES (Collins ARINC)

**Éditeur :** Collins ARINC
**Key Users :** LADJICI Fatima, BENNOUAR Adnane

### Questions techniques

1. Quelle est la version exacte du système Hermes en production ?
2. Quel réseau est utilisé (ARINC, SITA, les deux) ?
3. Quel est le format exact des messages ACARS reçus (OOOI, techniques, free text) ?
4. Comment les messages ACARS sont-ils stockés ? Existe-t-il une base de données de logs ? Si oui, quel SGBD ?
5. Existe-t-il un export ou une API pour accéder aux logs de messages ?
6. Sur quel serveur Hermes est-il hébergé (nom, OS, IP) ?
7. Comment les données ACARS (heures réelles OOOI) sont-elles actuellement transmises à AIMS ? Ce flux est-il automatisé ?
8. Quel est le volume quotidien de messages ACARS reçus ?

> **Réponse :**
>
>

---

# Phase 2 — Systèmes Importants 🟠 (Mois 3–4)

---

## 2.1 — SAGE STOCK (DAGP)

**Éditeur :** Sans contrat
**Key Users :** ATTOUT Abdelhafid, AIT MEZIANE Amar

### Questions techniques

1. Quelle est la version exacte de SAGE utilisée ?
2. Quelle est l'architecture du système (client/serveur) ? Quel est le SGBD (SQL Server, propriétaire) ?
3. Sur quel serveur SAGE STOCK est-il hébergé (nom, OS, IP) ?
4. Le schéma de la base de données est-il documenté ? Pouvez-vous fournir la structure des tables principales (articles, mouvements_stock, bons_commande) ?
5. Quel est le mode d'accès réseau au serveur ?
6. Quelle est la politique de sauvegarde actuelle ?
7. Est-il possible de mettre en place une réplique read-only de la base ou un dump quotidien ?
8. Un connecteur ODBC/JDBC est-il disponible et fonctionnel ?
9. L'absence de contrat éditeur pose-t-elle des risques techniques concrets (mises à jour, support, sécurité) ? Quelles alternatives sont envisagées ?

> **Réponse :**
>
>

---

## 2.2 — ATPCO

**Éditeur :** ATPCO
**Key Users :** LAIDANI Zakaria, FAIDI Fouad

### Questions techniques

1. Quel est le mode d'accès au portail ATPCO (SaaS, identifiants, rôles) ?
2. Existe-t-il une API ATPCO pour l'extraction automatisée des tarifs ? Est-elle incluse dans le contrat ?
3. Quels sont les formats de données utilisés (ATPCO Category, EDIFACT, CSV) ?
4. Comment les tarifs publiés sont-ils actuellement repris dans Altéa et les GDS ? Ce flux est-il automatique ?
5. Est-il possible d'exporter automatiquement les tarifs et les règles tarifaires ?

> **Réponse :**
>
>

---

## 2.3 — BAC (Amadeus)

**Éditeur :** Amadeus
**Key Users :** HASSISSENE Chemseddine, BENMADI Soumeya

### Questions techniques

1. BAC est-il un module SaaS Amadeus ? Quel est le mode d'accès ?
2. Quels sont les formats de données utilisés pour la facturation interline (EDIFACT IDEC, CSV) ?
3. Existe-t-il une API BAC pour l'extraction des données de facturation ?
4. Comment les coupons interline d'Altéa sont-ils transmis à BAC ? Ce flux est-il automatisé ?
5. Comment les données de facturation BAC sont-elles transmises à Rapid ? Quel format ?

> **Réponse :**
>
>

---

## 2.4 — Dashboards CCO + Suivi Irrégularités

**Éditeur :** DSI (in-house)
**Key Users :** CHABANE Amel, MAZARI Assia

### Questions techniques

1. Quelle est la technologie utilisée pour les dashboards (langage, framework, BDD) ?
2. Quel est le SGBD de la base de données sous-jacente ?
3. Le schéma de la base de données est-il documenté ?
4. Sur quel serveur les dashboards sont-ils hébergés (nom, OS, IP) ?
5. Comment les données AIMS (programme) et ACARS (heures réelles) alimentent-elles les dashboards ? Ces flux sont-ils automatisés ?
6. Le code source est-il accessible et documenté ?
7. Existe-t-il une API ou un export pour accéder aux données calculées (OTP, causes retards) ?

> **Réponse :**
>
>

---

## 2.5 — AGS (Safran)

**Éditeur :** Safran
**Key User :** SAMEUR Yacine

### Questions techniques

1. Quelle est la version exacte d'AGS en production ?
2. Quelle est l'architecture du système ? Quel SGBD est utilisé ?
3. Existe-t-il un module d'export natif pour les résultats d'analyse de vol ?
4. Quels sont les formats d'export disponibles (CSV, XML, autre) ?
5. Comment les événements détectés par AGS sont-ils actuellement transmis à Q-Pulse ? Ce flux est-il automatisé ?
6. Sur quel serveur AGS est-il hébergé (nom, OS, IP) ?
7. Existe-t-il une API AGS ?

> **Réponse :**
>
>

---

## 2.6 — Q-PULSE (Ideagen)

**Éditeur :** Ideagen
**Key User :** SAMEUR Yacine

### Questions techniques

1. Quelle est la version exacte de Q-Pulse en production ?
2. Quelle est l'architecture du système (SaaS, on-premise) ? Quel SGBD ?
3. Existe-t-il une API Q-Pulse pour l'extraction des données ?
4. Le contrat Ideagen actuel inclut-il l'accès API ? Quelles sont les conditions ?
5. Quels sont les formats d'export disponibles ?
6. Sur quel serveur Q-Pulse est-il hébergé (nom, OS, IP) ?
7. Comment les événements AGS sont-ils actuellement intégrés dans Q-Pulse ? Ce flux est-il automatisé ?

> **Réponse :**
>
>

---

## 2.7 — EUROCONTROL

**Éditeur :** EUROCONTROL
**Key User :** BENYELLES Djamal Eddine

### Questions techniques

1. Quels services EUROCONTROL sont utilisés (CFMU, NM B2B, autre) ?
2. L'API NM B2B est-elle configurée et accessible pour Air Algérie ?
3. Quels sont les formats de données utilisés (ICAO FPL, ADEXP, XML) ?
4. Comment les plans de vol sont-ils actuellement déposés ? Depuis quel système (AIMS, manuel) ?
5. Les données EUROCONTROL post-vol sont-elles récupérées automatiquement ?

> **Réponse :**
>
>

---

## 2.8 — JET PLANER (Jeppesen/Boeing)

**Éditeur :** Jeppesen (Boeing)
**Key User :** BENYELLES Djamal Eddine

### Questions techniques

1. Quelle est la version exacte de Jet Planer en production ?
2. Comment Jet Planer est-il intégré avec AIMS (import données de vol) ?
3. Quel est le format des OFP générés (PDF, texte structuré, XML) ?
4. Existe-t-il un export automatisé des OFP ou des données de calcul (routes, carburant) ?
5. Sur quel serveur Jet Planer est-il hébergé (nom, OS, IP) ?
6. Comment les données météo sont-elles reçues et intégrées ?

> **Réponse :**
>
>

---

## 2.9 — WORLD TRACER (SITA)

**Éditeur :** SITA
**Key Users :** TOUAHRIA Faiza, HASBELLAOUI Imen

### Questions techniques

1. World Tracer est-il un service SaaS SITA ? Quel est le mode d'accès ?
2. Existe-t-il une API SITA pour l'extraction des données bagages ?
3. Quels sont les formats d'export disponibles (CSV, XML) ?
4. Le contrat SITA actuel inclut-il l'accès API World Tracer ?
5. Comment les données DCS d'Altéa alimentent-elles World Tracer ? Ce flux est-il automatisé ?
6. Quelles contraintes d'anonymisation s'appliquent aux données passagers ?

> **Réponse :**
>
>

---

## 2.10 — SITE WEB AIR ALGÉRIE (KYO)

**Éditeur :** KYO
**Key Users :** BELDJERDI Zakaria, BACHA Amine

### Questions techniques

1. Quel est le stack technique du site web (langage, framework, CMS) ?
2. Où le site est-il hébergé (serveur interne, cloud, éditeur KYO) ?
3. Comment le site est-il intégré avec Altéa (API Amadeus e-Retail, Web Services) ?
4. Quel outil d'analytics est utilisé (Google Analytics, Matomo, autre) ?
5. Existe-t-il un accès aux logs serveur et aux données analytics ?
6. Le contrat KYO permet-il l'accès aux données et aux API ?
7. Quels moyens de paiement en ligne sont intégrés ? Via quelle passerelle ?

> **Réponse :**
>
>

---

## 2.11 — ACCELYA DISTRIBUTION

**Éditeur :** Accelya
**Key Users :** SAAD Nasima, HALISSE Abderrahim

### Questions techniques

1. Accelya Distribution est-il un service SaaS ? Quel est le mode d'accès ?
2. Existe-t-il une API Accelya pour l'extraction des données de ventes et distribution ?
3. Quels sont les formats de données disponibles (CSV, XML, EDIFACT) ?
4. Le contrat Accelya actuel inclut-il l'accès API Distribution ? (Synergie avec le contrat Rapid)
5. Comment les données de réservation Altéa alimentent-elles Accelya Distribution ?

> **Réponse :**
>
>

---

## 2.12 — QLIK SENSE

**Éditeur :** Qlik
**Key Users :** BADAOUI Youcef, HASSAINE Hassen

### Questions techniques

1. Quelle est la version exacte de Qlik Sense en production ?
2. Qlik Sense est-il hébergé en interne ou en cloud ? Sur quel serveur (nom, OS, IP) ?
3. Existe-t-il une API Qlik pour accéder aux métadonnées des dashboards et aux données QVD ?
4. Le contrat Qlik actuel inclut-il l'accès API/QVD ?
5. Les scripts de chargement (load scripts) sont-ils documentés et accessibles ?
6. Quelles sont les sources de données connectées à Qlik Sense (AIMS, Altéa, bases internes) ?

> **Réponse :**
>
>

---

## 2.13 — POWER BI

**Éditeur :** Microsoft
**Key Users :** ESSEMINIA Adnan, AGHA Riadh, YOUBI Mourad

### Questions techniques

1. Power BI est-il utilisé en version Pro, Premium ou Embedded ?
2. L'API Power BI REST est-elle configurée et accessible ?
3. Quels datasets et dataflows sont configurés dans Power BI ?
4. Quelles sont les sources de données connectées à chaque dashboard ?
5. Comment sont gérés les accès et les droits (Azure AD, groupes) ?
6. À quelle fréquence les données sont-elles rafraîchies (scheduled refresh) ?

> **Réponse :**
>
>

---

## 2.14 — AIMS Formation PNC/PNT + Conception Programme PN

**Key Users :** BENSALEM Lamya, SMAALLAH Yasmine, AZEROUAL Salima

### Questions techniques

1. Les modules Formation PNC, Formation PNT et Conception Programme PN utilisent-ils la même base de données qu'AIMS principal ?
2. Quelles sont les tables spécifiques à ces modules (crew_training_pnc, crew_training_pnt, roster_design) ?
3. Le schéma de ces tables est-il documenté ?
4. Comment les résultats de formation E-Learning sont-ils intégrés dans AIMS ? Ce flux est-il automatisé ?
5. Existe-t-il des exports spécifiques à ces modules ?

> **Réponse :**
>
>

---

## 2.15 — SAGE FINANCE (volet RGF)

**Key Users :** À désigner

### Questions techniques

1. Quelle est la version exacte de SAGE Finance utilisée ?
2. Quelle est l'architecture du système (client/serveur) ? Quel est le SGBD ?
3. Sur quel serveur SAGE Finance est-il hébergé (nom, OS, IP) ?
4. Un connecteur ODBC/JDBC est-il disponible et fonctionnel (même technologie que SAGE STOCK) ?
5. Le schéma de la base de données est-il documenté ?
6. Comment les écritures de revenue accounting (Rapid) sont-elles actuellement intégrées dans SAGE Finance ? Ce flux est-il automatisé ? Quel format ?
7. Quelle est la politique de sauvegarde actuelle ?

> **Réponse :**
>
>

---

# Phase 3 — Systèmes Standard 🟢 (Mois 5–6)

---

## 3.1 — BSP LINK (IATA)

**Éditeur :** IATA
**Key Users :** SAAD Nassima, HALISSE Abderrahim

### Questions techniques

1. Quel est le mode d'accès au portail BSP Link (identifiants, rôles) ?
2. Existe-t-il un export automatisé des rapports BSP (API IATA, fichiers planifiés) ?
3. Quels sont les formats d'export disponibles (CSV, XML) ?
4. Les rapports BSP peuvent-ils être téléchargés automatiquement via un script ou une API ?

> **Réponse :**
>
>

---

## 3.2 — E-DOLÉANCE

**Éditeur :** DSI (in-house)
**Key Users :** AKKACHA Mohamed Amine, BELDJERDI Zakaria

### Questions techniques

1. Quelle est la technologie utilisée (langage, framework) ?
2. Quel est le SGBD de la base de données ?
3. Le schéma de la base de données est-il documenté ? Pouvez-vous fournir la structure des tables principales (reclamations, types, statuts) ?
4. Existe-t-il une API REST ou un autre mode d'accès aux données ?
5. Le code source est-il accessible et documenté ?
6. Sur quel serveur E-Doléance est-il hébergé (nom, OS, IP) ?

> **Réponse :**
>
>

---

## 3.3 — GLPI

**Éditeur :** Open Source
**Key Users :** YOUCEF ACHIRA Abdellah, BOUKAIOU Ahlem

### Questions techniques

1. Quelle est la version exacte de GLPI en production ?
2. L'API REST native de GLPI est-elle activée et accessible ?
3. Quels plugins GLPI sont installés ?
4. Sur quel serveur GLPI est-il hébergé (nom, OS, IP) ?
5. Quel est le SGBD utilisé (MySQL, MariaDB) ?

> **Réponse :**
>
>

---

## 3.4 — HERMES CALL CENTER (Vocalcom)

**Éditeur :** Vocalcom
**Key Users :** BOUCHIK Mounir, FODILI Mohamed Yacine

### Questions techniques

1. Quelle est la version exacte de Vocalcom/Hermes Call Center en production ?
2. Existe-t-il une base de données des appels et statistiques ? Quel SGBD ?
3. Existe-t-il une API ou un export pour accéder aux données d'appels (durées, agents, motifs) ?
4. Comment l'intégration CTI (Computer Telephony Integration) est-elle configurée ?
5. Comment les agents accèdent-ils à Altéa pour la consultation PNR pendant un appel ?

> **Réponse :**
>
>

---

## 3.5 — OAG / INNOVATA

**Éditeur :** OAG
**Key Users :** SAFAR ZITOUN Naim, KARI Fateh

### Questions techniques

1. Quel est le mode d'accès au portail OAG (SaaS, identifiants) ?
2. L'API Schedules OAG est-elle disponible dans le contrat actuel ?
3. Quels sont les formats d'export disponibles (SSIM, CSV) ?
4. Les données OAG peuvent-elles être téléchargées automatiquement ?

> **Réponse :**
>
>

---

## 3.6 — E-LEARNING E-EXAM PN

**Éditeur :** Développement externe
**Key User :** SAID Sihem

### Questions techniques

1. Quelle est la technologie utilisée (langage, framework, LMS) ?
2. Quel est le SGBD de la base de données ?
3. Existe-t-il un export des résultats d'examens (CSV, API) ?
4. Comment les résultats d'examens sont-ils actuellement transmis à AIMS ? Ce flux est-il automatisé ?
5. Sur quel serveur la plateforme est-elle hébergée (nom, OS, IP) ?

> **Réponse :**
>
>

---

## 3.7 — ZIMBRA (Umaitek)

**Éditeur :** Umaitek
**Key Users :** YOUCEF ACHIRA Abdellah, BOUKAIOU Ahlem

### Questions techniques

1. Quelle est la version exacte de Zimbra en production ?
2. L'API Zimbra est-elle activée et accessible ?
3. Existe-t-il un accès aux logs de messagerie (statistiques d'usage, pas le contenu) ?
4. Sur quel serveur Zimbra est-il hébergé (nom, OS, IP) ?
5. Comment fonctionne techniquement la passerelle SITATEX → Zimbra ?

> **Réponse :**
>
>

---

## 3.8 — CONTRÔLE PROGRAMMES PN/AVIONS

**Key User :** BENMOUFFOK El Hadi

### Questions techniques

1. Quelle est la technologie utilisée pour cet outil (langage, framework) ?
2. Existe-t-il une base de données dédiée ? Quel SGBD ?
3. Existe-t-il un export des résultats de contrôle ?
4. Comment l'outil accède-t-il aux données AIMS ?
5. Sur quel serveur est-il hébergé (nom, OS, IP) ?

> **Réponse :**
>
>

---

## 3.9 — DOA MAILING

**Éditeur :** Développement externe
**Key Users :** SAID Sihem, TOUTOU Aghiles, MANSEUR Amine

### Questions techniques

1. Quelle est la technologie utilisée (langage, framework) ?
2. Existe-t-il une base de données des envois ? Quel SGBD ?
3. Existe-t-il un export des logs d'envois ?
4. Comment le système récupère-t-il les listes d'équipages depuis AIMS ?
5. Sur quel serveur est-il hébergé (nom, OS, IP) ?

> **Réponse :**
>
>

---

## 3.10 — CALL DOA (Campusave)

**Éditeur :** Campusave
**Key Users :** SAID Sihem, TOUTOU Aghiles, MANSEUR Amine

### Questions techniques

1. Quelle est la version du système Campusave en production ?
2. Existe-t-il une base de données des appels ? Quel SGBD ?
3. Existe-t-il un export des logs d'appels ?
4. Comment le système récupère-t-il les listes d'équipages depuis AIMS ?
5. Sur quel serveur est-il hébergé (nom, OS, IP) ?

> **Réponse :**
>
>

---

## 3.11 — SKYBOOK (Bytron)

**Éditeur :** Bytron
**Key User :** BENYELLES Djamal Eddine

### Questions techniques

1. Quelle est la version exacte de SkyBook en production ?
2. Existe-t-il une API SkyBook pour accéder aux logs d'usage ?
3. Comment les OFP de Jet Planer sont-ils transmis à SkyBook ? Ce flux est-il automatisé ?
4. Comment les données AIMS sont-elles intégrées dans SkyBook ?
5. Les tablettes EFB sont-elles gérées via un MDM (Mobile Device Management) ?

> **Réponse :**
>
>

---

## 3.12 — FLYSMART (Airbus/Boeing/ATR)

**Éditeur :** Airbus/Boeing/ATR
**Key User :** BENYELLES Djamal Eddine

### Questions techniques

1. Quelles versions de FlySmart sont utilisées (par type avion) ?
2. FlySmart est-il installé sur les tablettes EFB ou sur des postes fixes ?
3. Existe-t-il un export des logs de performances ou des calculs ?
4. Comment sont mises à jour les données de performances dans FlySmart ?
5. Les données FlySmart sont-elles stockées localement ou sur un serveur ?

> **Réponse :**
>
>

---

## 3.13 — PORTAIL AH

**Éditeur :** DSI (in-house)
**Key Users :** YOUCEF ACHIRA Abdellah, BOUKAIOU Ahlem

### Questions techniques

1. Quelle est la technologie utilisée (langage, framework, CMS) ?
2. Quel est le SGBD de la base de données ?
3. Sur quel serveur le portail est-il hébergé (nom, OS, IP) ?
4. Existe-t-il un accès direct à la base de données ?
5. Le code source est-il accessible ?

> **Réponse :**
>
>

---

## 3.14 — EVALCOM

**Éditeur :** EVALCOM
**Key User :** LAKAMA Abdallah

### Questions techniques

1. Quelle est la version d'EVALCOM en production ?
2. Quelle est l'architecture du système (SaaS, on-premise) ? Quel SGBD ?
3. Existe-t-il un export agrégé des résultats d'évaluation ?
4. Quels formats d'export sont disponibles ?
5. Quelles contraintes d'anonymisation s'appliquent aux données individuelles ?

> **Réponse :**
>
>

---

## 3.15 — BODET

**Key Users :** À désigner

### Questions techniques

1. Quelle est la version du système BODET en production ?
2. Quelle est l'architecture du système ? Quel SGBD ?
3. Existe-t-il un export des données de pointage (agrégé) ?
4. Quels formats d'export sont disponibles ?
5. Comment les données de pointage alimentent-elles actuellement la paie ?
6. Sur quel serveur BODET est-il hébergé (nom, OS, IP) ?

> **Réponse :**
>
>

---

## 3.16 — DATAWINGS

**Key Users :** À désigner

### Questions techniques

1. Quelle est la version du système DataWings en production ?
2. Quelle est l'architecture du système ? Quel SGBD ?
3. Existe-t-il un export des données d'opérations aéroportuaires ?
4. Quels formats d'export sont disponibles ?
5. Comment DataWings interagit-il techniquement avec les autres systèmes opérationnels ?
6. Sur quel serveur DataWings est-il hébergé (nom, OS, IP) ?

> **Réponse :**
>
>

---

## 3.17 — AIMS Formation PNC

**Key User :** BENSALEM Lamya

### Questions techniques

1. Le module Formation PNC utilise-t-il la même instance BDD qu'AIMS principal ?
2. Quelles sont les tables spécifiques au module Formation PNC (crew_training_pnc) ?
3. Existe-t-il des exports spécifiques à ce module ?
4. Les données de ce module sont-elles accessibles via le même connecteur que l'ETL AIMS principal ?

> **Réponse :**
>
>

---

## 3.18 — AIMS Formation PNT

**Key User :** SMAALLAH Yasmine

### Questions techniques

1. Le module Formation PNT utilise-t-il la même instance BDD qu'AIMS principal ?
2. Quelles sont les tables spécifiques au module Formation PNT (crew_training_pnt) ?
3. Existe-t-il des exports spécifiques à ce module ?
4. Les données de ce module sont-elles accessibles via le même connecteur que l'ETL AIMS principal ?

> **Réponse :**
>
>

---

# Prérequis techniques transverses

> Ces questions s'appliquent à l'ensemble du projet ETL et doivent être adressées à la DSI.

### Infrastructure

1. Un serveur dédié ETL + data lake est-il disponible ou prévu ? Quelles sont ses caractéristiques (CPU, RAM, stockage) ?
2. Les accès réseau aux serveurs on-premise (AIMS, AMOS, SAGE, GLPI) sont-ils ouverts ou à configurer ?
3. Un VPN ou un accès sécurisé aux plateformes SaaS est-il en place ?
4. Un serveur SFTP est-il disponible pour la réception des data feeds (Amadeus, etc.) ?

### Sécurité

5. Existe-t-il une politique d'anonymisation des données personnelles (passagers, employés) ?
6. Les accès read-only aux bases dupliquées sont-ils configurables ?
7. Le chiffrement en transit et au repos est-il en place sur l'infrastructure cible ?
8. Un système de journalisation des accès aux données est-il en place ?

### Contrats éditeurs

9. Quel est l'état d'avancement des négociations avec les éditeurs suivants pour l'accès aux données ?

| Éditeur | Système | Objet | Statut |
|---------|---------|-------|--------|
| Amadeus | Altéa | Data feeds SFTP/API | |
| Solution Soft | AIMS | BDD read-only ou API | |
| Swiss-AS | AMOS | AMOS Connect ou réplication Oracle | |
| Accelya | Rapid + Distribution | API exports | |
| SITA | SITATEX + World Tracer | Logs + API | |
| Collins ARINC | ACARS | Logs Hermes | |
| ATPCO | ATPCO | API tarifs | |
| Ideagen | Q-Pulse | API Q-Pulse | |
| Qlik | Qlik Sense | QVD/API | |

> **Réponse :**
>
>

---

*Document généré le 14 février 2026 — Direction des Systèmes d'Information, Air Algérie*
*Basé sur PREREQUIS_ETL_CARTOGRAPHIE.md et PLAN_PRIORISATION_ETL.md*
