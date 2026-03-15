# Projet de Cartographie du Système d'Information
## Comité Exécutif — Air Algérie
### 11 février 2026

---

## 1. Contexte et enjeux

Le Système d'Information d'Air Algérie repose aujourd'hui sur **38 systèmes** répartis dans **12 structures** (DAGP, DC, DFC, DIVEX, DMRA, DOA, DOS, DPD, DRH, DSC, DSI, RGF).

**Constat actuel :**
- Les systèmes fonctionnent **en silos**, avec des échanges de données souvent **manuels** (fichiers Excel, ressaisie, emails)
- Pas de **vision globale** des flux de données entre systèmes
- Pas de **documentation centralisée** sur l'architecture SI
- Des **risques** non maîtrisés : dépendances inconnues, points de défaillance non identifiés, absence de plan de continuité documenté

**Enjeu stratégique :** Air Algérie ne peut pas piloter la modernisation de son SI sans connaître précisément ce qui existe, comment les systèmes communiquent, et où se trouvent les points critiques.

---

## 2. Objectifs du projet

| Objectif | Description |
|----------|-------------|
| **Inventorier** | Recenser l'ensemble des 38 systèmes, leurs versions, éditeurs, modes d'hébergement |
| **Cartographier les flux** | Identifier et documenter chaque échange de données entre systèmes (source, destination, format, fréquence, volume) |
| **Évaluer la criticité** | Classer chaque système selon son impact métier (Critique / Haute / Moyenne / Basse) |
| **Identifier les risques** | Détecter les systèmes isolés, les dépendances critiques, les contrats expirés |
| **Préparer l'interopérabilité** | Poser les bases pour automatiser les échanges et éliminer les traitements manuels |

---

## 3. Périmètre — Les 38 systèmes identifiés

### Systèmes aériens critiques (Opérations & Réservation)
| Système | Éditeur | Structure | Rôle |
|---------|---------|-----------|------|
| **Suite Altéa Amadeus** | Amadeus | DC + DIVEX | Réservation, billetterie, DCS, inventaire |
| **AIMS** | Solution Soft | DIVEX + DC + DMRA + DOA | Gestion des opérations aériennes, programmes vols, équipages |
| **AMOS** | Swiss Aviation Software | DMRA | Maintenance aéronautique, navigabilité |
| **ACARS / Hermes** | Collins ARINC | DIVEX (CCO) | Messages opérationnels avions en temps réel |
| **EUROCONTROL** | EUROCONTROL | DOA | Plans de vol, slots, CFMU |
| **Jet Planer** | Jeppesen (Boeing) | DOA | Calcul routes, carburant, météo |
| **SkyBook** | Bytron | DOA | EFB — documentation de vol électronique |
| **FlySmart** | Airbus/Boeing/ATR | DOA | Performances avions |
| **SITATEX Online** | SITA | DSI + DC + DIVEX + DMRA | Messagerie aéronautique Type B |
| **World Tracer** | SITA | DOS | Traçabilité bagages |

### Systèmes commerciaux & distribution
| Système | Éditeur | Structure | Rôle |
|---------|---------|-----------|------|
| **Accelya Distribution** | Accelya | DC | Distribution et ventes |
| **BSP Link** | IATA | DC | Rapports BSP, réconciliation agences |
| **ATPCO** | ATPCO | DC | Publication des tarifs |
| **BAC (Amadeus)** | Amadeus | DC | Facturation interline, proration |
| **Rapid Passagers** | Accelya | DFC | Revenue accounting |
| **OAG / Innovata** | OAG | DIVEX + DC | Données horaires marché |
| **Site Web Air Algérie** | KYO | DC | Vente en ligne, check-in, info vols |
| **Hermes Call Center** | Vocalcom | DC | Centre d'appels |

### Systèmes de gestion & support
| Système | Éditeur | Structure | Rôle |
|---------|---------|-----------|------|
| **SAGE STOCK** | Sans contrat | DAGP | Gestion des stocks |
| **SAGE Finance** | Mercuria | RGF | Comptabilité France |
| **EVALCOM** | EVALCOM | DRH | Évaluation du personnel |
| **BODET** | Bodet | RGF | Gestion des temps |
| **DATAWINGS** | Datawings | RGF | Gestion aéroportuaire France |
| **GLPI** | Open Source | DSI | Tickets support, parc informatique |

### Systèmes BI, dashboards & outils internes
| Système | Éditeur | Structure | Rôle |
|---------|---------|-----------|------|
| **Power BI** | Microsoft | DSI + Structures | Tableaux de bord, reporting |
| **Qlik Sense** | Qlik | DPD + DOS | Business intelligence |
| **Dashboards CCO** | DSI (in-house) | DIVEX (CCO) | Ponctualité, suivi irrégularités |
| **Contrôle Programmes PN** | Ingénieur CCO | DIVEX (CCO) | Vérification programmes PN/avions |
| **E-Doléance** | DSI (in-house) | DC | Gestion des réclamations |
| **DOA Mailing / Call DOA** | Développement externe | DOA | Communication PN |
| **E-Learning E-Exam PN** | Développement externe | DOA | Formation en ligne PN |
| **Portail AH** | DSI (in-house) | DSI | Intranet |
| **Zimbra** | Umaitek | DSI | Messagerie d'entreprise |
| **AGS** | Safran | DSC | Analyse données de vol (FDR/QAR) |
| **Q-Pulse** | Ideagen | DSC | Gestion qualité, non-conformités |

---

## 4. Ce qui a été réalisé

### Phase 1 — Inventaire et identification des référents ✅

- **38 systèmes** inventoriés et classés par structure et catégorie
- **Key Users désignés** pour 34 systèmes sur 38 (Principal + Suppléant)
- **4 systèmes** en attente de désignation : E-Learning E-Exam PN, BODET, DATAWINGS, SAGE Finance RGF

### Phase 2 — Application web de cartographie ✅

Une **application web** a été développée et déployée pour centraliser toutes les informations :

| Fonctionnalité | Description |
|---------------|-------------|
| **Inventaire interactif** | Visualisation de tous les systèmes avec filtres par structure, catégorie, criticité |
| **Cartographie des flux** | Visualisation graphique des échanges de données entre systèmes |
| **Fiches système** | Détail complet de chaque système (version, éditeur, hébergement, modules, Key Users) |
| **Modèle de données** | Structures, systèmes, catégories, flux de données, formats de messages, domaines de données |
| **Import de données réelles** | Capacité d'importer et analyser des échantillons de données (SSIM, PNR, MVT, etc.) |

**Stack technique :** Django, Python, déployé sur serveur dédié (85.31.237.249)

### Phase 3 — Collecte d'informations auprès des Key Users 🔄 En cours

**31 emails préparés** couvrant les 38 systèmes, en deux versions :

| Type | Cible | Contenu |
|------|-------|---------|
| **Fonctionnel** | Key Users métier (nominatif) | Questions simples sur l'usage, les échanges, les difficultés, l'impact |
| **Technique** | Experts SI | Templates détaillés par catégorie : architecture, BDD, protocoles, SLA, sécurité |

Chaque email demande :
- Description de l'usage quotidien du système
- Identification des flux de données (sources, destinations, formats)
- Exemples d'extraction et d'importation avec échantillons anonymisés
- Difficultés rencontrées et impact en cas d'indisponibilité

---

## 5. Vision cible — Interopérabilité et automatisation

### Situation actuelle vs. situation cible

| Aspect | Aujourd'hui | Demain |
|--------|------------|--------|
| **Échanges de données** | Manuels (Excel, email, ressaisie) | Automatisés (API, fichiers structurés, ETL) |
| **Visibilité** | Chaque structure connaît ses outils | Vision transverse de tout le SI |
| **Documentation** | Inexistante ou dispersée | Centralisée dans l'application de cartographie |
| **Détection de pannes** | Réactive (on découvre les impacts) | Proactive (dépendances connues, alertes) |
| **Nouveaux projets** | Sans connaissance de l'existant | Basés sur la cartographie à jour |
| **Conformité** | Difficile à démontrer | Traçabilité complète des flux |

### Bénéfices attendus

1. **Réduction des erreurs** — Élimination de la ressaisie manuelle entre systèmes
2. **Gain de temps** — Automatisation des échanges récurrents (programmes vols, données passagers, maintenance)
3. **Maîtrise des risques** — Connaissance des dépendances critiques et plans de continuité
4. **Aide à la décision** — Dashboards consolidés alimentés automatiquement
5. **Conformité réglementaire** — Documentation des flux pour les audits (OACI, IATA, autorités)
6. **Préparation à la modernisation** — Base solide pour tout projet de transformation digitale

---

## 6. Flux de données critiques identifiés

```
AIMS ←→ Altéa          Programmes vols, équipages, DCS
AIMS ←→ AMOS           Heures de vol, cycles, maintenance
AIMS ←→ EUROCONTROL    Plans de vol, slots
AIMS ←→ ACARS          Messages opérationnels temps réel
Altéa ←→ Site Web      Réservation en ligne
Altéa ←→ Rapid         Revenue accounting, coupons
Altéa ←→ BSP Link      Ventes agences
Altéa ←→ World Tracer  Bagages
Altéa ←→ SITATEX       Messages Type B (MVT, LDM, ASM, SSM)
AMOS ←→ SAGE STOCK     Pièces de rechange
AGS ←→ Q-Pulse         Analyse vol → non-conformités
ACARS ←→ SITATEX       Messages aéronautiques
Power BI ← Multiples   Reporting transverse
```

---

## 7. Prochaines étapes

| Étape | Échéance | Responsable |
|-------|----------|-------------|
| **Envoi des 31 emails** aux Key Users | Semaine du 11 février | DSI |
| **Relance** des non-répondants | J+10 ouvrés | DSI |
| **Désignation Key Users manquants** (RGF, DOA) | Février 2026 | Structures concernées |
| **Consolidation des réponses** dans l'application | Mars 2026 | DSI |
| **Validation** avec chaque structure | Mars 2026 | DSI + Structures |
| **Cartographie complète des flux** | Avril 2026 | DSI |
| **Plan d'interopérabilité** — priorisation des automatisations | Mai 2026 | DSI + Comité SI |
| **Premiers projets d'intégration** (flux critiques) | S2 2026 | DSI |

---

## 8. Ce que nous demandons au Comité Exécutif

1. **Validation** de la démarche et du périmètre présenté
2. **Appui hiérarchique** pour garantir la réponse des Key Users dans les délais
3. **Désignation rapide** des Key Users manquants (RGF, E-Learning DOA)
4. **Arbitrage** sur la priorisation des flux à automatiser en premier
5. **Engagement** des directions métier dans la phase de validation

---

## 9. Chiffres clés

| | |
|---|---|
| **38** | systèmes identifiés |
| **12** | structures concernées |
| **34/38** | systèmes avec Key User désigné (89%) |
| **31** | emails de collecte préparés |
| **13+** | flux de données critiques identifiés |
| **5** | catégories de templates techniques |
| **1** | application web de cartographie déployée |

---

*Direction des Systèmes d'Information — Air Algérie*
*Février 2026*
