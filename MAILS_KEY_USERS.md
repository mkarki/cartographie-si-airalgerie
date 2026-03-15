# Mails aux Key Users — Projet Urbanisation SI Air Algérie

> Ce document contient un mail type par système, prêt à être envoyé aux Key Users concernés.

---

## Phase 1 🔴 — Systèmes critiques

---

### Mail 1 — Suite Altéa (Amadeus)

**À :** FAIDI Fouad, FIALA Zahra, LOUNAOUCI Nassim, HASBELLAOUI Imen, GHARBI Mohamed, NAMOUNI Ali
**En copie :** DEBAB Noureddine, BERRABIA Mokrane, FAIDI Fouad, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système Suite Altéa

Bonjour,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **Suite Altéa (Reservation, Ticketing, Inventory, DCS)**.

Pour ce faire, voici les questions :

- Quels sont les canaux de vente connectés à Altéa Reservation ? Quel est le volume de PNR créés par jour et par canal ?
- Quelles sont les règles de gestion spécifiques appliquées lors de la création d'un PNR ?
- Comment sont gérés les PNR de groupe vs les PNR individuels ?
- Quels rapports ou extractions sont produits régulièrement à partir des données de réservation ?
- Quel est le volume quotidien de coupons émis ? Quelle répartition entre billets électroniques, EMD et documents manuels ?
- Comment fonctionne le processus de remboursement et de réémission ?
- Comment sont gérés les billets interline avec les compagnies partenaires ?
- Comment sont gérées les classes de réservation et les disponibilités ?
- Existe-t-il un système de Revenue Management connecté à l'Inventory ?
- Comment sont gérés les codeshares et les accords interline au niveau de l'inventaire ?
- Quel est le processus d'enregistrement des passagers ? Quels canaux sont actifs aujourd'hui ?
- Comment sont gérés les cas de surbooking, de no-show et de go-show au niveau du DCS ?
- Quelles données DCS sont transmises aux autorités (API/PNR) ? Vers quels pays et dans quel format ?
- Comment le DCS interagit-il avec le système bagages (World Tracer) ?
- Quels sont les principaux irritants métier aujourd'hui avec la suite Altéa ?
- Quels indicateurs clés (KPI) aimeriez-vous suivre à partir des données Altéa ?
- Y a-t-il des processus métier qui nécessitent aujourd'hui des extractions manuelles ou des contournements ?
- Quels sont les data feeds Amadeus actuellement actifs ? Lesquels sont souhaités mais non encore en place ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Extrait d'un PNR type (masqué)
- Extrait d'un coupon de vol (masqué)
- Exemple de rapport de ventes quotidien
- Exemple de liste de passagers DCS (anonymisée)
- Liste des data feeds actifs et leur format

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 2 — AIMS

**À :** BENAOUICHA Hanane, SIDAHMED AKKOUCHE, BENNOUAR Adnane, BADAOUI Youcef, HASSAINE Hassen, GACIMI Mohamed
**En copie :** DEBAB Noureddine, BOUTEMADJA Samu El Karim, BOULAOUAD Said, BERRABIA Mokrane, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système AIMS

Bonjour,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **AIMS (Programmes vols, Crew Management, Crew Tracking, Operations, Training)**.

Pour ce faire, voici les questions :

- Quel est le processus complet de création d'un programme de vols, de l'initiative commerciale jusqu'à la publication SSIM ?
- Combien de vols sont programmés en moyenne par jour / par saison IATA ?
- Comment sont gérées les modifications de programme en cours de saison ?
- Comment le programme de vols est-il transmis à Altéa (format SSIM) ?
- Comment sont planifiés les rotations et les rosters des équipages ?
- Combien de membres d'équipage sont gérés dans AIMS ?
- Comment sont gérés les cas d'indisponibilité imprévue ?
- Quelles sont les règles FTL appliquées ? Sont-elles configurées dans AIMS ?
- Comment sont suivies les qualifications et les échéances de validité ?
- Comment le CCO utilise-t-il AIMS le jour J pour suivre les opérations ?
- Comment sont gérées les irrégularités dans AIMS ?
- Comment AIMS reçoit-il les heures réelles de vol (ACARS/OOOI) ?
- Comment sont affectés les avions aux vols dans AIMS ?
- Comment AIMS est-il informé de la disponibilité/indisponibilité des avions (AMOS) ?
- Quels sont les principaux irritants métier avec AIMS aujourd'hui ?
- Quels indicateurs clés (KPI) aimeriez-vous suivre à partir des données AIMS ?
- Y a-t-il des processus métier qui nécessitent des extractions manuelles ou des fichiers Excel en parallèle ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Extrait d'un programme de vols (SSIM ou format interne)
- Extrait d'un roster équipage type (anonymisé)
- Exemple de rapport de ponctualité
- Exemple de rapport d'affectation avions

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 3 — AMOS

**À :** BOUGUEZIZ Samir
**En copie :** DEBAB Noureddine, HACHELAF Mourad, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système AMOS

Bonjour BOUGUEZIZ Samir,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **AMOS (OT, Planification maintenance, Navigabilité, Pièces)**.

Pour ce faire, voici les questions :

- Quel est le circuit complet d'un ordre de travail, de l'ouverture à la clôture ?
- Combien d'ordres de travail sont ouverts en moyenne par mois ?
- Comment sont gérées les priorités entre les différents OT ?
- Comment sont tracées les heures de main-d'œuvre par OT ?
- Comment est élaboré le plan de maintenance à long terme ?
- Comment AMOS reçoit-il les heures de vol et les cycles depuis AIMS ?
- Comment sont planifiées les immobilisations avion pour maintenance ?
- Comment sont suivies les AD, SB et CDCCL dans AMOS ?
- Comment sont gérées les MEL et les reports de maintenance ?
- Quels documents de navigabilité sont produits à partir d'AMOS ?
- Comment fonctionne le processus de demande de pièces depuis AMOS vers SAGE STOCK ?
- Comment est gérée la traçabilité des pièces installées/déposées sur les avions ?
- Comment sont gérés les échanges de pièces avec les fournisseurs ?
- Quels indicateurs de fiabilité suivez-vous aujourd'hui ?
- Quels rapports produisez-vous régulièrement à partir d'AMOS ?
- Quels sont les principaux irritants métier avec AMOS aujourd'hui ?
- Y a-t-il des processus métier qui nécessitent des fichiers Excel ou des outils parallèles ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Extrait d'un ordre de travail type
- Extrait du plan de maintenance (anonymisé)
- Exemple de rapport de fiabilité (MTBF/MTTR)
- Exemple de fiche de suivi navigabilité avion

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 4 — Rapid Passagers

**À :** HADJ SAID Nadir
**En copie :** DEBAB Noureddine, KHELFI Redouane, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système Rapid Passagers

Bonjour HADJ SAID Nadir,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **Rapid Passagers (Revenue Accounting)**.

Pour ce faire, voici les questions :

- Quel est le processus complet de traitement d'un coupon de vol ?
- Quel est le volume mensuel de coupons traités ?
- Comment sont gérés les cas de rejet de coupons ?
- Comment fonctionne le processus de proration pour les coupons interline ?
- Comment fonctionne le processus de facturation interline ?
- Comment se fait le rapprochement entre les données Rapid et les données BSP ?
- Comment sont gérés les remboursements dans Rapid ?
- Quels rapports financiers sont produits à partir de Rapid ?
- Comment les écritures comptables sont-elles transmises à SAGE Finance ?
- Quels indicateurs financiers clés sont calculés à partir de Rapid ?
- Quels sont les principaux irritants métier avec Rapid aujourd'hui ?
- Y a-t-il des analyses financières impossibles avec les données actuelles ?
- Y a-t-il des processus de revenue accounting qui nécessitent des traitements manuels ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Extrait d'un rapport de revenue accounting mensuel (anonymisé)
- Exemple de fichier de coupons traités
- Exemple de rapport de facturation interline
- Exemple d'écritures comptables transmises à SAGE

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 5 — SITATEX Online

**À :** SALAH ROUANA Mohamed
**En copie :** DEBAB Noureddine, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système SITATEX Online

Bonjour SALAH ROUANA Mohamed,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **SITATEX Online (Messagerie aéronautique Type B)**.

Pour ce faire, voici les questions :

- Quels types de messages SITATEX sont utilisés au quotidien ? Pour chaque type, qui est l'émetteur et qui sont les destinataires ?
- Quel est le volume quotidien de messages échangés ?
- Quels messages sont générés automatiquement par d'autres systèmes et lesquels sont saisis manuellement ?
- Quels sont les destinataires externes des messages SITATEX ?
- Comment les messages MVT sont-ils exploités par les opérations ?
- Comment les messages LDM sont-ils utilisés pour le chargement des avions ?
- Comment sont gérés les messages ASM/SSM ?
- Comment fonctionne la passerelle SITATEX → Zimbra ?
- Comment sont archivés les messages SITATEX ?
- Quels sont les principaux irritants avec SITATEX aujourd'hui ?
- Y a-t-il des statistiques que vous aimeriez produire à partir des messages SITATEX ?
- Existe-t-il des messages qui sont aujourd'hui traités manuellement et qui pourraient être automatisés ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple de message MVT (anonymisé)
- Exemple de message LDM
- Exemple de message ASM/SSM
- Liste des adresses SITATEX utilisées

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 6 — ACARS / Hermes

**À :** LADJICI Fatima
**En copie :** DEBAB Noureddine, HOUAOUI Samia, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système ACARS / Hermes

Bonjour LADJICI Fatima,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **ACARS / Hermes (Messages air-sol temps réel)**.

Pour ce faire, voici les questions :

- Quels types de messages ACARS sont reçus et exploités ?
- Quel est le volume quotidien de messages ACARS reçus ?
- Comment les messages OOOI sont-ils exploités par le CCO ?
- Les messages techniques moteurs sont-ils exploités ?
- Comment le CCO suit-il la ponctualité en temps réel ?
- Comment sont détectées et gérées les irrégularités à partir des données ACARS ?
- Comment les heures réelles ACARS sont-elles intégrées dans AIMS ?
- Les équipages utilisent-ils ACARS pour envoyer des messages free text ?
- Comment sont gérés les messages ACARS de demande de maintenance ?
- Quels sont les principaux irritants avec le système ACARS/Hermes aujourd'hui ?
- Quels indicateurs aimeriez-vous calculer à partir des données ACARS ?
- Y a-t-il des données ACARS recopiées manuellement dans des fichiers Excel ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple de message OOOI (anonymisé)
- Exemple de message technique moteur
- Exemple de rapport de ponctualité basé sur ACARS
- Capture d'écran de l'interface Hermes (anonymisée)

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

## Phase 2 🟠 — Systèmes importants

---

### Mail 7 — SAGE STOCK

**À :** ATTOUT Abdelhafid
**En copie :** DEBAB Noureddine, HABEL Rachid, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système SAGE STOCK

Bonjour ATTOUT Abdelhafid,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **SAGE STOCK (Gestion des stocks et pièces)**.

Pour ce faire, voici les questions :

- Quels modules SAGE sont utilisés aujourd'hui ?
- Quels types d'articles sont gérés dans SAGE STOCK ?
- Combien d'articles sont référencés au total ? Combien de mouvements de stock sont enregistrés par mois ?
- Quel est le circuit complet d'un mouvement de stock ?
- Comment fonctionne le processus de réapprovisionnement ?
- Comment sont gérés les inventaires ?
- Comment est gérée la valorisation des stocks ?
- Comment se fait concrètement l'échange d'information entre SAGE STOCK et AMOS ?
- Les codes articles sont-ils les mêmes dans SAGE STOCK et AMOS ?
- Comment sont gérées les pièces sous traçabilité aéronautique dans SAGE STOCK vs dans AMOS ?
- L'absence de contrat éditeur pose-t-elle des problèmes concrets aujourd'hui ?
- Quels rapports de stock produisez-vous régulièrement ?
- Quels indicateurs de gestion de stock aimeriez-vous suivre ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Extrait de la liste des articles référencés (anonymisé)
- Exemple de bon de sortie magasin
- Exemple de rapport d'inventaire
- Exemple de rapport de mouvements de stock

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 8 — ATPCO

**À :** LAIDANI Zakaria
**En copie :** DEBAB Noureddine, BRAHIM BOUNAB Nihad, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système ATPCO

Bonjour LAIDANI Zakaria,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **ATPCO (Publication tarifaire)**.

Pour ce faire, voici les questions :

- Quels types de tarifs sont publiés via ATPCO ?
- Quel est le processus de création et de publication d'un tarif ?
- À quelle fréquence les tarifs sont-ils publiés ou modifiés ?
- Quelles règles tarifaires sont associées aux tarifs ?
- Quels marchés (O&D) sont couverts par les publications ATPCO ?
- Comment sont structurées les classes de réservation et les familles tarifaires ?
- Comment vérifiez-vous que les tarifs publiés sont correctement repris dans Altéa et les GDS ?
- Utilisez-vous ATPCO pour faire de la veille tarifaire concurrentielle ?
- Quels sont les principaux irritants avec ATPCO aujourd'hui ?
- Quelles analyses tarifaires aimeriez-vous réaliser ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple de fiche tarifaire publiée (anonymisée)
- Extrait des règles tarifaires associées
- Exemple de grille tarifaire par marché

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 9 — BAC (Amadeus)

**À :** HASSISSENE Chemseddine
**En copie :** DEBAB Noureddine, BERRABIA Mokrane, FAIDI Fouad, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système BAC

Bonjour HASSISSENE Chemseddine,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **BAC — Billing and Accounting Center (Facturation interline)**.

Pour ce faire, voici les questions :

- Avec quelles compagnies Air Algérie a-t-elle des accords interline actifs ? Quel est le volume mensuel ?
- Quel est le processus complet de facturation interline ?
- Comment fonctionne la proration des revenus interline ?
- Comment se fait le rapprochement entre les données BAC et les données Rapid ?
- Comment sont gérés les rejets et les litiges interline ?
- Quels rapports de facturation interline sont produits ?
- Quels sont les principaux irritants avec BAC aujourd'hui ?
- Quelles analyses interline aimeriez-vous réaliser ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple de facture interline (anonymisée)
- Exemple de rapport de rapprochement BAC/Rapid
- Exemple de fichier EDIFACT interline

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 10 — Dashboards CCO + Suivi Irrégularités

**À :** CHABANE Amel
**En copie :** DEBAB Noureddine, HOUAOUI Samia, DAG

**Objet :** Projet urbanisation SI — Questions relatives aux Dashboards CCO

Bonjour CHABANE Amel,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **Dashboard Ponctualité Jour J + Historique + Suivi Irrégularités**.

Pour ce faire, voici les questions :

- Quelles informations sont affichées sur le dashboard de ponctualité du jour J ?
- Qui consulte ce dashboard au quotidien ? Quelles décisions sont prises ?
- Comment sont calculés les retards ?
- Quelles analyses historiques de ponctualité sont réalisées ?
- Comment sont catégorisées les causes de retard ?
- Quels rapports de ponctualité sont produits régulièrement ?
- Quels types d'irrégularités sont suivis ?
- Quel est le processus de traitement d'une irrégularité ?
- Comment sont calculés les coûts des irrégularités ?
- Quels sont les principaux irritants avec les dashboards actuels ?
- Quels nouveaux indicateurs ou analyses aimeriez-vous avoir ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Capture d'écran du dashboard ponctualité jour J (anonymisée)
- Exemple de rapport de ponctualité mensuel
- Exemple de fiche d'irrégularité
- Liste des codes causes de retard utilisés

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 11 — AGS (Analysis Ground Station)

**À :** SAMEUR Yacine
**En copie :** DEBAB Noureddine, BOUCHAMA Laid, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système AGS

Bonjour SAMEUR Yacine,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **AGS — Analysis Ground Station (Analyse données de vol FDR/QAR)**.

Pour ce faire, voici les questions :

- Quels types de données de vol sont analysés dans AGS ?
- Quels événements de vol sont détectés et surveillés par AGS ?
- Quel est le processus complet d'analyse d'un vol ?
- Comment sont définis les seuils de détection des événements ?
- Comment sont exploités les résultats d'analyse ?
- Comment les événements détectés par AGS sont-ils transmis à Q-Pulse ?
- Quels rapports statistiques sont produits à partir d'AGS ?
- Comment AGS s'intègre-t-il dans le programme de sécurité des vols (SMS) ?
- Les données AGS sont-elles partagées avec des organismes externes ?
- Quels sont les principaux irritants avec AGS aujourd'hui ?
- Quelles analyses supplémentaires aimeriez-vous réaliser ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple de rapport d'analyse de vol (anonymisé)
- Exemple de rapport d'événement détecté
- Exemple de rapport statistique mensuel

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 12 — Q-Pulse

**À :** SAMEUR Yacine
**En copie :** DEBAB Noureddine, BOUCHAMA Laid, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système Q-Pulse

Bonjour SAMEUR Yacine,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **Q-Pulse (Qualité et non-conformités)**.

Pour ce faire, voici les questions :

- Quels types de non-conformités sont gérés dans Q-Pulse ?
- Quel est le processus complet de traitement d'une non-conformité ?
- Comment sont classifiées les non-conformités en termes de gravité et d'urgence ?
- Comment sont définies et suivies les actions correctives et préventives ?
- Quelles sont les différentes sources de signalement des non-conformités ?
- Comment les événements détectés par AGS sont-ils intégrés dans Q-Pulse ?
- Comment sont gérés les rapports volontaires de sécurité ?
- Comment Q-Pulse est-il utilisé pour la gestion des audits ?
- Quels rapports et indicateurs qualité sont produits à partir de Q-Pulse ?
- Quels sont les principaux irritants avec Q-Pulse aujourd'hui ?
- Quelles analyses supplémentaires aimeriez-vous réaliser ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple de fiche de non-conformité (anonymisée)
- Exemple de rapport d'audit
- Exemple de tableau de bord qualité

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 13 — EUROCONTROL

**À :** BENYELLES Djamal Eddine
**En copie :** DEBAB Noureddine, BENBOUAZIZ Lyes, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système EUROCONTROL

Bonjour BENYELLES Djamal Eddine,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **EUROCONTROL (CFMU, Slots, Plans de vol)**.

Pour ce faire, voici les questions :

- Quels services EUROCONTROL sont utilisés par Air Algérie ?
- Quel est le processus de dépôt d'un plan de vol (FPL) ?
- Comment sont gérées les régulations ATFM ?
- Combien de plans de vol sont déposés par jour en moyenne ?
- Quelles données EUROCONTROL sont exploitées après le vol ?
- Comment sont gérées les redevances de navigation aérienne EUROCONTROL ?
- Quels sont les principaux irritants avec EUROCONTROL aujourd'hui ?
- Quelles analyses aimeriez-vous réaliser à partir des données EUROCONTROL ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple de plan de vol déposé (FPL anonymisé)
- Exemple de message de régulation ATFM
- Exemple de facture de redevances EUROCONTROL

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 14 — Jet Planer

**À :** BENYELLES Djamal Eddine
**En copie :** DEBAB Noureddine, BENBOUAZIZ Lyes, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système Jet Planer

Bonjour BENYELLES Djamal Eddine,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **Jet Planer (Calcul routes, carburant, météo)**.

Pour ce faire, voici les questions :

- Quel est le processus de préparation d'un vol dans Jet Planer ?
- Comment sont sélectionnées les routes ?
- Comment est calculé le carburant nécessaire ?
- Comment les données météo sont-elles intégrées dans Jet Planer ?
- Comment l'OFP est-il distribué à l'équipage ?
- Quelles informations de l'OFP sont les plus critiques ?
- Réalisez-vous des analyses post-vol à partir des données Jet Planer ?
- Quels indicateurs aimeriez-vous suivre à partir des données Jet Planer ?
- Quels sont les principaux irritants avec Jet Planer aujourd'hui ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple d'OFP (Operational Flight Plan) anonymisé
- Exemple de briefing météo
- Exemple de calcul carburant

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 15 — World Tracer

**À :** TOUAHRIA Faiza
**En copie :** DEBAB Noureddine, BERRABIA Mokrane, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système World Tracer

Bonjour TOUAHRIA Faiza,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **World Tracer (Suivi bagages perdus/retardés)**.

Pour ce faire, voici les questions :

- Quel est le processus complet de déclaration d'un bagage perdu ou retardé ?
- Combien de déclarations sont enregistrées par mois ?
- Comment sont gérés les bagages endommagés ?
- Comment World Tracer interagit-il avec les compagnies partenaires pour les bagages interline ?
- Quels indicateurs de performance bagages sont suivis aujourd'hui ?
- Comment sont identifiées les causes de perte de bagages ?
- Quels rapports bagages sont produits régulièrement ?
- Comment est géré le processus d'indemnisation des passagers ?
- Avez-vous une visibilité sur le coût total des bagages perdus/retardés ?
- Quels sont les principaux irritants avec World Tracer aujourd'hui ?
- Quelles analyses supplémentaires aimeriez-vous réaliser ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple de déclaration de bagage perdu (anonymisée)
- Exemple de rapport mensuel bagages
- Exemple de suivi d'indemnisation

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 16 — Site Web Air Algérie

**À :** BELDJERDI Zakaria
**En copie :** DEBAB Noureddine, FAIDI Fouad, DAG

**Objet :** Projet urbanisation SI — Questions relatives au Site Web

Bonjour BELDJERDI Zakaria,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le **Site Web Air Algérie (Réservation en ligne, check-in, CMS)**.

Pour ce faire, voici les questions :

- Quelles fonctionnalités sont disponibles sur le site web aujourd'hui ?
- Quel est le parcours client type pour une réservation en ligne ?
- Quels moyens de paiement sont acceptés en ligne ?
- Le check-in en ligne est-il actif ?
- Quel est le volume de réservations réalisées via le site web par mois ?
- Quel est le taux de conversion actuel ?
- Quels indicateurs de trafic web sont suivis aujourd'hui ?
- Comment est géré le contenu du site (CMS) ?
- Existe-t-il un programme de fidélité en ligne ?
- Quels sont les principaux irritants avec le site web aujourd'hui ?
- Quelles fonctionnalités ou analyses aimeriez-vous avoir ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Capture d'écran du parcours de réservation
- Exemple de rapport analytics (trafic, conversion)
- Exemple de rapport de ventes en ligne

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 17 — Accelya Distribution

**À :** SAAD Nasima
**En copie :** DEBAB Noureddine, BOUNEB Brahim Nihad, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système Accelya Distribution

Bonjour SAAD Nasima,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **Accelya Distribution (Ventes, émission billets, canaux)**.

Pour ce faire, voici les questions :

- Quels canaux de distribution sont gérés via Accelya Distribution ?
- Comment fonctionne le processus d'émission de billets par canal ?
- Comment sont gérées les agences de vente ?
- Quels rapports de ventes sont produits à partir d'Accelya Distribution ?
- Comment se fait le rapprochement entre les ventes Accelya et les données BSP Link ?
- Comment sont suivies les commissions agents et les incentives ?
- Quels sont les principaux irritants avec Accelya Distribution aujourd'hui ?
- Quelles analyses commerciales aimeriez-vous réaliser ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple de rapport de ventes par canal (anonymisé)
- Exemple de rapport de commissions agents
- Exemple de fichier de rapprochement BSP

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 18 — Qlik Sense

**À :** BADAOUI Youcef
**En copie :** DEBAB Noureddine, BERRABIA Mokrane, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système Qlik Sense

Bonjour BADAOUI Youcef,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **Qlik Sense (BI opérations sol)**.

Pour ce faire, voici les questions :

- Quels dashboards Qlik Sense sont en production aujourd'hui ?
- Quelles sources de données alimentent chaque dashboard ?
- Combien d'utilisateurs actifs consultent Qlik Sense ?
- À quelle fréquence les données sont-elles rafraîchies ?
- Existe-t-il des scripts de chargement documentés ?
- Quels sont les principaux irritants avec Qlik Sense aujourd'hui ?
- Quels nouveaux dashboards ou analyses aimeriez-vous avoir ?
- Y a-t-il une volonté de migrer certains dashboards vers Power BI ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Liste des dashboards en production avec description
- Capture d'écran d'un dashboard type (anonymisée)
- Schéma des sources de données par dashboard

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 19 — Power BI

**À :** ESSEMINIA Adnan
**En copie :** DEBAB Noureddine, KRAIMECHE Abdelkrim, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système Power BI

Bonjour ESSEMINIA Adnan,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **Power BI (Reporting transverse)**.

Pour ce faire, voici les questions :

- Quels dashboards Power BI sont en production aujourd'hui ?
- Quelles directions/structures utilisent Power BI ?
- Quelles sources de données alimentent chaque dashboard ?
- Qui développe et maintient les dashboards Power BI ?
- Comment sont gérés les accès et les droits sur les dashboards ?
- À quelle fréquence les données sont-elles rafraîchies ?
- Quels sont les principaux irritants avec Power BI aujourd'hui ?
- Quels nouveaux dashboards ou analyses sont demandés ?
- Comment Power BI coexiste-t-il avec Qlik Sense ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Liste des dashboards en production avec description
- Capture d'écran d'un dashboard type (anonymisée)
- Schéma des sources de données par dashboard

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 20 — AIMS Formation PNC/PNT + Conception Programme PN

**À :** BENSALEM Lamya, SMAALLAH Yasmine, AZEROUAL Salima
**En copie :** DEBAB Noureddine, BENBOUAZIZ Lyes, DAG

**Objet :** Projet urbanisation SI — Questions relatives aux modules AIMS Formation

Bonjour,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant les modules **AIMS Formation PNC, Formation PNT et Conception Programme PN**.

Pour ce faire, voici les questions :

- Quels types de formations PNC sont gérés dans AIMS ?
- Comment est planifié le programme de formation PNC annuel ?
- Comment sont suivies les échéances de validité des qualifications PNC ?
- Comment les résultats de formation/examen (E-Learning) sont-ils intégrés dans AIMS ?
- Quels types de formations PNT sont gérés dans AIMS ?
- Comment est planifié le programme de formation PNT annuel ?
- Comment sont suivies les licences et qualifications PNT ?
- Comment sont conçus les programmes (rosters) des PN dans AIMS ?
- Quel est le cycle de conception d'un programme PN ?
- Comment sont gérées les modifications de programme en cours de mois ?
- Quels sont les principaux irritants avec les modules formation et conception programme ?
- Quels indicateurs aimeriez-vous suivre ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple de planning de formation PNC/PNT (anonymisé)
- Exemple de roster PN (anonymisé)
- Exemple de fiche de suivi des qualifications

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 21 — SAGE Finance

**À :** (Key User à désigner)
**En copie :** DEBAB Noureddine, AOUDIA Soufiane, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système SAGE Finance

Bonjour,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **SAGE Finance — PAR/LYS/MRS (Comptabilité)**.

Pour ce faire, voici les questions :

- Quels modules SAGE Finance sont utilisés ?
- Quelles entités comptables sont gérées dans SAGE Finance ?
- Quel est le plan comptable utilisé ?
- Comment les écritures de revenue accounting (Rapid) sont-elles intégrées dans SAGE Finance ?
- Quelles autres sources alimentent SAGE Finance ?
- Comment se fait le rapprochement entre les données de revenue accounting et les écritures comptables ?
- Quels rapports financiers sont produits à partir de SAGE Finance ?
- Comment sont produits les reportings de gestion ?
- Quels sont les principaux irritants avec SAGE Finance aujourd'hui ?
- Quelles analyses financières aimeriez-vous réaliser ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Extrait du plan comptable
- Exemple d'écriture comptable (anonymisée)
- Exemple de rapport de gestion mensuel

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

## Phase 3 🟢 — Systèmes standard

---

### Mail 22 — BSP Link

**À :** SAAD Nassima
**En copie :** DEBAB Noureddine, BRAHIM BOUNAB Nihad, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système BSP Link

Bonjour SAAD Nassima,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **BSP Link (Rapports BSP — Billing and Settlement Plan)**.

Pour ce faire, voici les questions :

- Quels rapports BSP sont consultés régulièrement sur le portail BSP Link ?
- Comment se fait le rapprochement entre les données BSP et les données internes (Accelya, Rapid) ?
- Quels marchés BSP sont couverts ?
- Comment sont suivies les performances des agences IATA à travers les données BSP ?
- Comment sont gérés les cas de défaut de paiement d'une agence ?
- Quels sont les principaux irritants avec BSP Link aujourd'hui ?
- Quelles analyses aimeriez-vous réaliser à partir des données BSP ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple de rapport Hot File (anonymisé)
- Exemple de rapport Billing Analysis
- Exemple de rapport Agent Sales Summary

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 23 — E-Doléance

**À :** AKKACHA Mohamed Amine
**En copie :** DEBAB Noureddine, BOUNEB Brahim Nihad, FAIDI Fouad, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système E-Doléance

Bonjour AKKACHA Mohamed Amine,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **E-Doléance (Gestion des réclamations passagers)**.

Pour ce faire, voici les questions :

- Quels types de réclamations sont gérés dans E-Doléance ?
- Quel est le circuit complet de traitement d'une réclamation ?
- Comment sont classifiées les réclamations en termes de priorité et de gravité ?
- Par quels canaux les réclamations arrivent-elles ?
- Comment sont gérées les indemnisations passagers ?
- Comment est suivi le délai de réponse aux réclamations ?
- Les réclamations sont-elles liées aux données de vol (PNR Altéa) ?
- Quels rapports et statistiques sont produits à partir d'E-Doléance ?
- Les données de réclamation sont-elles croisées avec les données du call center (Hermes) ?
- Quels sont les principaux irritants avec E-Doléance aujourd'hui ?
- Quelles améliorations ou analyses supplémentaires aimeriez-vous ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple de fiche de réclamation (anonymisée)
- Exemple de rapport mensuel des réclamations
- Exemple de suivi d'indemnisation

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 24 — GLPI

**À :** YOUCEF ACHIRA Abdellah
**En copie :** DEBAB Noureddine, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système GLPI

Bonjour YOUCEF ACHIRA Abdellah,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **GLPI (Gestion du parc informatique et tickets support)**.

Pour ce faire, voici les questions :

- Quels types d'équipements sont inventoriés dans GLPI ?
- Comment est maintenu l'inventaire à jour ?
- Comment sont gérés les contrats de maintenance et les garanties dans GLPI ?
- Quels types de demandes sont gérées via les tickets GLPI ?
- Quel est le processus de traitement d'un ticket ?
- Quels indicateurs de performance IT sont suivis ?
- Quels sont les principaux irritants avec GLPI aujourd'hui ?
- Quelles analyses aimeriez-vous réaliser ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Extrait de l'inventaire du parc (anonymisé)
- Exemple de ticket support
- Exemple de rapport de performance IT

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 25 — Hermes Call Center

**À :** BOUCHIK Mounir
**En copie :** DEBAB Noureddine, BRAHIM BOUNAB Nihad, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système Hermes Call Center

Bonjour BOUCHIK Mounir,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **Hermes Call Center (Centre d'appels)**.

Pour ce faire, voici les questions :

- Comment est organisé le call center ?
- Quel est le volume d'appels quotidien/mensuel ?
- Quels sont les pics d'activité et comment sont-ils gérés ?
- Quels outils les agents utilisent-ils pendant un appel ?
- Les agents peuvent-ils effectuer des réservations et des modifications directement dans Altéa ?
- Comment sont tracés les motifs d'appel ?
- Quels indicateurs de performance du call center sont suivis ?
- Quels rapports sont produits et pour quels destinataires ?
- Quels sont les principaux irritants avec Hermes aujourd'hui ?
- Quelles analyses aimeriez-vous réaliser ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple de rapport d'activité du call center (anonymisé)
- Liste des motifs d'appel utilisés
- Exemple de rapport de performance agents

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 26 — OAG / Innovata

**À :** SAFAR ZITOUN Naim
**En copie :** DEBAB Noureddine, BOUTEMADJA Samu El Karim, BERRABIA Mokrane, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système OAG / Innovata

Bonjour SAFAR ZITOUN Naim,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **OAG / Innovata (Horaires marché et analyse routes)**.

Pour ce faire, voici les questions :

- Comment OAG/Innovata est-il utilisé au quotidien ?
- Quels marchés et quelles compagnies concurrentes sont surveillés via OAG ?
- Les données OAG sont-elles comparées avec les programmes AIMS d'Air Algérie ?
- Comment les données OAG alimentent-elles les décisions de planification réseau ?
- Les données OAG sont-elles utilisées pour des présentations ou rapports réguliers ?
- Quels sont les principaux irritants avec OAG aujourd'hui ?
- Quelles analyses supplémentaires aimeriez-vous ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple de rapport d'analyse de marché (anonymisé)
- Exemple de comparaison de fréquences avec la concurrence
- Exemple d'export SSIM/CSV

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 27 — E-Learning E-Exam PN

**À :** SAID Sihem
**En copie :** DEBAB Noureddine, BENBOUAZIZ Lyes, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système E-Learning

Bonjour SAID Sihem,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **E-Learning E-Exam PN (Formation et examens PN en ligne)**.

Pour ce faire, voici les questions :

- Quels types de formations sont dispensés via la plateforme E-Learning ?
- Combien de membres d'équipage utilisent la plateforme ?
- Comment sont structurés les examens ?
- Comment les résultats d'examen sont-ils transmis à AIMS ?
- Comment est suivi le taux de complétion des formations obligatoires ?
- Comment sont gérés les cas d'échec à un examen ?
- Quels sont les principaux irritants avec la plateforme E-Learning aujourd'hui ?
- Quelles analyses aimeriez-vous réaliser ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Liste des formations disponibles sur la plateforme
- Exemple de résultat d'examen (anonymisé)
- Exemple de rapport de complétion des formations

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 28 — Zimbra

**À :** YOUCEF ACHIRA Abdellah
**En copie :** DEBAB Noureddine, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système Zimbra

Bonjour YOUCEF ACHIRA Abdellah,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **Zimbra (Messagerie d'entreprise)**.

Pour ce faire, voici les questions :

- Combien d'utilisateurs actifs utilisent Zimbra ?
- Quelles fonctionnalités Zimbra sont utilisées ?
- Comment fonctionne la passerelle SITATEX → Zimbra ?
- Quelles statistiques d'usage sont disponibles aujourd'hui ?
- Existe-t-il une politique de rétention des messages et d'archivage ?
- Quels sont les principaux irritants avec Zimbra aujourd'hui ?
- Y a-t-il un projet de migration vers une autre solution de messagerie ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Statistiques d'usage Zimbra (nombre d'utilisateurs, volume de messages)
- Configuration de la passerelle SITATEX → Zimbra

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 29 — Contrôle Programmes PN/Avions

**À :** BENMOUFFOK El Hadi
**En copie :** DEBAB Noureddine, HOUAOUI Samia, DAG

**Objet :** Projet urbanisation SI — Questions relatives à l'application Contrôle Programmes

Bonjour BENMOUFFOK El Hadi,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant l'**Application de contrôle des programmes PN/Avions**.

Pour ce faire, voici les questions :

- Quels types de contrôles sont effectués sur les programmes PN et avions ?
- À quel moment du cycle de planification ces contrôles sont-ils effectués ?
- Comment sont gérées les non-conformités détectées ?
- Quels résultats de contrôle sont produits ?
- Les résultats de contrôle sont-ils archivés ?
- Quels sont les principaux irritants avec cet outil de contrôle aujourd'hui ?
- Quels contrôles supplémentaires aimeriez-vous automatiser ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple de rapport de contrôle (anonymisé)
- Liste des types de contrôles effectués

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 30 — DOA Mailing

**À :** SAID Sihem
**En copie :** DEBAB Noureddine, BERRABIA Mokrane, MERABET Athmane, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système DOA Mailing

Bonjour SAID Sihem,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **DOA Mailing (Envoi de mailings aux équipages)**.

Pour ce faire, voici les questions :

- Quels types de mailings sont envoyés aux équipages via ce système ?
- Comment sont constituées les listes de destinataires ?
- Quel est le processus de validation d'un mailing avant envoi ?
- Comment est suivie la réception des mailings par les équipages ?
- Les mailings envoyés sont-ils archivés ?
- Quels sont les principaux irritants avec DOA Mailing aujourd'hui ?
- Y a-t-il des besoins non couverts ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple de mailing envoyé (anonymisé)
- Exemple de liste de distribution

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 31 — Call DOA

**À :** SAID Sihem
**En copie :** DEBAB Noureddine, BENBOUAZIZ Lyes, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système Call DOA

Bonjour SAID Sihem,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **Call DOA (Appels aux équipages)**.

Pour ce faire, voici les questions :

- Dans quels cas le système Call DOA est-il utilisé ?
- Comment sont sélectionnés les équipages à appeler ?
- Les appels sont-ils automatisés ou passés manuellement ?
- Comment est tracée la confirmation de réception par l'équipage ?
- Que se passe-t-il en cas de non-réponse d'un membre d'équipage ?
- Quels sont les principaux irritants avec Call DOA aujourd'hui ?
- Y a-t-il des besoins non couverts ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple de log d'appels (anonymisé)
- Statistiques d'appels mensuelles

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 32 — SkyBook

**À :** BENYELLES Djamal Eddine
**En copie :** DEBAB Noureddine, BENBOUAZIZ Lyes, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système SkyBook

Bonjour BENYELLES Djamal Eddine,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **SkyBook (Electronic Flight Bag — EFB)**.

Pour ce faire, voici les questions :

- Quelles fonctionnalités de SkyBook sont utilisées par les équipages ?
- Tous les équipages sont-ils équipés de tablettes EFB avec SkyBook ?
- Comment les OFP de Jet Planer sont-ils transmis à SkyBook ?
- Quels documents aéronautiques sont disponibles dans SkyBook ?
- Comment est gérée la synchronisation des tablettes ?
- Quels sont les principaux irritants avec SkyBook aujourd'hui ?
- Quelles fonctionnalités supplémentaires seraient utiles ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Capture d'écran de l'interface SkyBook (anonymisée)
- Liste des documents disponibles dans SkyBook

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 33 — FlySmart

**À :** BENYELLES Djamal Eddine
**En copie :** DEBAB Noureddine, BENBOUAZIZ Lyes, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système FlySmart

Bonjour BENYELLES Djamal Eddine,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **FlySmart (Performances avion)**.

Pour ce faire, voici les questions :

- Quelles fonctionnalités FlySmart sont utilisées ?
- FlySmart est-il utilisé sur les tablettes EFB ou sur des postes fixes ?
- Comment sont mises à jour les données de performances dans FlySmart ?
- Les résultats de calcul de performances sont-ils archivés et exploités a posteriori ?
- Les données FlySmart sont-elles croisées avec d'autres sources ?
- Quels sont les principaux irritants avec FlySmart aujourd'hui ?
- Quelles analyses supplémentaires aimeriez-vous réaliser ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple de calcul de performances décollage (anonymisé)
- Capture d'écran de l'interface FlySmart

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 34 — Portail AH

**À :** YOUCEF ACHIRA Abdellah
**En copie :** DEBAB Noureddine, DAG

**Objet :** Projet urbanisation SI — Questions relatives au Portail AH

Bonjour YOUCEF ACHIRA Abdellah,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le **Portail AH (Portail interne Air Algérie)**.

Pour ce faire, voici les questions :

- Quelles fonctionnalités sont disponibles sur le portail interne AH ?
- Combien d'utilisateurs actifs consultent le portail ?
- Comment est géré le contenu du portail ?
- Quelles statistiques d'usage sont disponibles aujourd'hui ?
- Le portail sert-il de point d'entrée vers d'autres applications métier ?
- Quels sont les principaux irritants avec le portail aujourd'hui ?
- Quelles nouvelles fonctionnalités seraient utiles ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Capture d'écran de la page d'accueil du portail
- Statistiques d'usage (pages vues, utilisateurs actifs)

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 35 — EVALCOM

**À :** LAKAMA Abdallah
**En copie :** DEBAB Noureddine, KRAIMECHE Abdelkrim, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système EVALCOM

Bonjour LAKAMA Abdallah,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **EVALCOM (Évaluation du personnel)**.

Pour ce faire, voici les questions :

- Quel est le processus d'évaluation du personnel géré dans EVALCOM ?
- Combien d'évaluations sont réalisées par an ?
- Comment se déroule le cycle d'évaluation ?
- Quels résultats agrégés sont produits à partir d'EVALCOM ?
- Les résultats d'évaluation alimentent-ils d'autres processus RH ?
- Quels sont les principaux irritants avec EVALCOM aujourd'hui ?
- Quelles analyses RH aimeriez-vous réaliser à partir des données d'évaluation ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple de grille d'évaluation vierge
- Exemple de rapport agrégé d'évaluation (anonymisé)

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 36 — BODET

**À :** (Key User à désigner)
**En copie :** DEBAB Noureddine, AOUDIA Soufiane, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système BODET

Bonjour,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **BODET (Gestion des temps et pointages)**.

Pour ce faire, voici les questions :

- Quels sites et quelles catégories de personnel sont couverts par BODET ?
- Quels types de pointages sont gérés ?
- Combien d'employés sont gérés dans BODET ?
- Comment les données de pointage alimentent-elles la paie ?
- Quels rapports de temps sont produits ?
- Quels sont les principaux irritants avec BODET aujourd'hui ?
- Quelles analyses aimeriez-vous réaliser ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple de rapport de pointage mensuel (anonymisé)
- Exemple de rapport d'absentéisme

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 37 — DataWings

**À :** (Key User à désigner)
**En copie :** DEBAB Noureddine, AOUDIA Soufiane, DAG

**Objet :** Projet urbanisation SI — Questions relatives au système DataWings

Bonjour,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le système **DataWings (Opérations aéroportuaires)**.

Pour ce faire, voici les questions :

- Quelles opérations aéroportuaires sont gérées dans DataWings ?
- Combien de vols sont traités par jour dans DataWings ?
- Comment DataWings interagit-il avec les autres systèmes opérationnels ?
- Quels indicateurs de performance des opérations au sol sont suivis ?
- Quels rapports sont produits à partir de DataWings ?
- Quels sont les principaux irritants avec DataWings aujourd'hui ?
- Quelles analyses supplémentaires aimeriez-vous ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple de rapport d'opérations au sol (anonymisé)
- Exemple de rapport de performance handling

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 38 — AIMS Formation PNC (détail)

**À :** BENSALEM Lamya
**En copie :** DEBAB Noureddine, BENBOUAZIZ Lyes, DAG

**Objet :** Projet urbanisation SI — Questions complémentaires module AIMS Formation PNC

Bonjour BENSALEM Lamya,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le module **AIMS Formation PNC**.

Pour ce faire, voici les questions :

- Quels sont les types de formations spécifiques aux PNC gérés dans AIMS ?
- Combien de PNC sont suivis dans le module formation ?
- Comment sont gérées les qualifications PNC par type avion ?
- Comment sont planifiées les formations PNC par rapport aux programmes de vol ?
- Quel est le taux de conformité actuel des formations PNC ?
- Comment sont gérés les cas de PNC dont une qualification arrive à expiration ?
- Quels sont les principaux irritants spécifiques au suivi de formation PNC ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple de fiche de suivi des qualifications PNC (anonymisée)
- Exemple de planning de formation PNC

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit

---

### Mail 39 — AIMS Formation PNT (détail)

**À :** SMAALLAH Yasmine
**En copie :** DEBAB Noureddine, BENBOUAZIZ Lyes, DAG

**Objet :** Projet urbanisation SI — Questions complémentaires module AIMS Formation PNT

Bonjour SMAALLAH Yasmine,

Pour faire suite au projet d'urbanisation des systèmes DSI d'Air Algérie, nous souhaiterions que vous nous apportiez les réponses suivantes concernant le module **AIMS Formation PNT**.

Pour ce faire, voici les questions :

- Quels sont les types de formations spécifiques aux PNT gérés dans AIMS ?
- Combien de PNT sont suivis dans le module formation ?
- Comment est gérée la disponibilité des simulateurs ?
- Comment sont gérées les qualifications PNT par type avion ?
- Comment sont suivies les licences PNT dans AIMS ?
- Comment sont gérés les contrôles en ligne (OPC/LPC) ?
- Quel est le taux de conformité actuel des formations PNT ?
- Quels sont les principaux irritants spécifiques au suivi de formation PNT ?
- Quels indicateurs aimeriez-vous suivre ?

Afin de constituer au mieux le schéma de données, merci de bien vouloir nous adresser les extraits de fichiers (sans données confidentielles / pas de vrais montants ou de vrais noms) suivants :

- Exemple de fiche de suivi des qualifications PNT (anonymisée)
- Exemple de planning simulateur
- Exemple de suivi des licences

Dans le cadre de la réalisation du planning, nous avons également besoin que vous nous proposiez un atelier d'1h selon vos disponibilités pour échanger.

Merci par avance,
L'équipe d'audit
