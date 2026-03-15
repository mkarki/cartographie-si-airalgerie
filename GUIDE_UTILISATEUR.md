# Guide Utilisateur - Cartographie SI Air Algérie

**URL d'accès** : http://85.31.237.249/

---

## Table des matières

1. [Dashboard](#1-dashboard)
2. [Systèmes](#2-systèmes)
3. [Flux de données](#3-flux-de-données)
4. [Vue Graphique](#4-vue-graphique)
5. [Structures](#5-structures)
6. [Domaines de données](#6-domaines-de-données)
7. [Formats de messages](#7-formats-de-messages)
8. [Validation des données](#8-validation-des-données)
9. [Référentiels](#9-référentiels)
10. [Rapports](#10-rapports)

---

## 1. Dashboard

**Accès** : Page d'accueil `/`

Le dashboard présente une vue synthétique de la cartographie SI :

- **Statistiques globales** : Nombre total de systèmes, flux, structures
- **Systèmes critiques** : Nombre de systèmes avec criticité "CRITIQUE"
- **Flux manuels** : Flux non automatisés nécessitant une attention
- **Systèmes récents** : Les 10 derniers systèmes ajoutés
- **Flux critiques** : Les 5 flux les plus critiques

---

## 2. Systèmes

**Accès** : Menu → Systèmes ou `/systems/`

### Liste des systèmes

Affiche tous les systèmes du SI avec possibilité de filtrer par :

| Filtre | Description |
|--------|-------------|
| **Catégorie** | Core Business, Distribution, Finance, RH, etc. |
| **Structure** | Direction/département propriétaire |
| **Criticité** | CRITIQUE, HAUTE, MOYENNE, BASSE |
| **Pays** | Algérie (DZ) ou étranger |
| **Recherche** | Recherche par nom, code ou éditeur |

### Détail d'un système

Cliquez sur un système pour voir :

- **Informations générales** : Code, nom, description, éditeur
- **Classification** : Catégorie, structure, criticité, mode (SaaS/On-premise)
- **Flux entrants** : Données reçues par ce système
- **Flux sortants** : Données envoyées par ce système
- **Domaines maîtrisés** : Données dont ce système est la source de vérité
- **Domaines consommés** : Données utilisées par ce système

---

## 3. Flux de données

**Accès** : Menu → Flux ou `/flows/`

### Liste des flux

Affiche tous les flux de données entre systèmes avec filtres :

| Filtre | Description |
|--------|-------------|
| **Source** | Système émetteur |
| **Cible** | Système récepteur |
| **Fréquence** | Temps réel, horaire, journalier, etc. |
| **Automatisé** | Oui/Non |

### Détail d'un flux

Pour chaque flux, visualisez :

- **Systèmes** : Source → Cible
- **Caractéristiques** : Fréquence, protocole, format, volume
- **Criticité** : Indicateur si le flux est critique
- **Champs transportés** : Liste des données échangées avec leur type et description

---

## 4. Vue Graphique

**Accès** : Menu → Graphe ou `/graph/`

Visualisation interactive de la cartographie sous forme de graphe :

### Navigation

- **Zoom** : Molette de la souris ou boutons +/-
- **Déplacement** : Cliquer-glisser sur le fond
- **Sélection** : Cliquer sur un nœud pour voir ses détails

### Filtres

- **Par catégorie** : Afficher uniquement certains types de systèmes
- **Par structure** : Filtrer par direction/département
- **Afficher structures** : Grouper les systèmes par structure organisationnelle

### Légende

- **Nœuds colorés** : Couleur selon la criticité du système
- **Liens** : Représentent les flux de données
- **Épaisseur des liens** : Peut indiquer le volume ou la criticité

---

## 5. Structures

**Accès** : Menu → Structures ou `/structures/`

Liste des structures organisationnelles (directions, départements) avec :

- **Code** : Identifiant court
- **Nom** : Nom complet de la structure
- **Nombre de systèmes** : Systèmes rattachés à cette structure
- **Description** : Rôle et périmètre

---

## 6. Domaines de données

**Accès** : Menu → Domaines ou `/domains/`

Cartographie des domaines de données métier :

- **Domaine** : Nom du domaine (ex: Passagers, Vols, Recettes)
- **Système maître** : Système source de vérité pour ce domaine
- **Systèmes consommateurs** : Systèmes utilisant ces données

---

## 7. Formats de messages

**Accès** : Menu → Messages ou `/messages/`

Catalogue des formats de messages standards (IATA, internes) :

- **Code** : Identifiant du format (ex: PNR, PNRGOV, SSM)
- **Nom** : Nom descriptif
- **Standard** : Norme associée (IATA, SITA, interne)
- **Champs** : Structure détaillée du message

---

## 8. Validation des données

### Dashboard de validation

**Accès** : `/validation/`

Suivi de la validation des hypothèses de cartographie vs données réelles :

- **Statistiques** : Hypothèses confirmées, partielles, incorrectes
- **Flux problématiques** : Flux avec le plus de divergences
- **Validations récentes** : Dernières validations effectuées

### Échantillons de données

**Accès** : `/validation/samples/`

Liste des fichiers de données importés pour validation :

- **Source** : Système d'origine (AMADEUS, RAPID, AIMS, etc.)
- **Type** : Type de données (APS, SLP, FLP, etc.)
- **Colonnes** : Nombre de champs détectés
- **Lignes** : Volume de l'échantillon

### Détail d'un échantillon

Cliquez sur un échantillon pour voir :

- **Colonnes avec statistiques** : Types détectés, valeurs uniques, exemples
- **Aperçu des données** : Premières lignes de l'échantillon
- **Tables attendues** : Checklist des données attendues vs reçues
- **Taux de complétion** : Pourcentage de données reçues

### Découverte des données

**Accès** : `/data-discovery/`

Vue synthèse de toutes les données découvertes, groupées par système source.

---

## 9. Référentiels

**Accès** : `/referentials/`

Catalogue des données de référence utilisées dans les flux :

| Type | Exemples |
|------|----------|
| **Codes IATA** | Compagnies aériennes, aéroports, types d'avions |
| **Devises** | Codes ISO des monnaies |
| **Pays** | Codes ISO des pays |
| **Classes de service** | F, C, Y, etc. |
| **Types de paiement** | CB, espèces, BSP |
| **Statuts** | Statuts tickets, PNR, vols |

### Détail d'un référentiel

Pour chaque référentiel :

- **Système maître** : Source de vérité
- **Standard** : Norme de référence (IATA, ISO, interne)
- **Flux utilisant ce référentiel** : Liste des flux concernés
- **Systèmes utilisateurs** : Confirmés et potentiels

---

## 10. Rapports

### Rapport des écarts

**Accès** : `/reports/data-gaps/`

Analyse des éléments manquants dans les échantillons de données :

- **Filtres** : Par système source, cible, statut
- **Statuts** :
  - ✅ **COMPLETE** : Toutes les données validées
  - ⚠️ **PARTIAL** : Validation en cours
  - ❌ **ISSUES** : Divergences détectées
  - 📭 **NO_SAMPLE** : Pas d'échantillon reçu

### Rapport IA

**Accès** : `/reports/ai/`

Génération de rapports d'analyse assistée par IA (nécessite clé API Anthropic).

### Schéma de base de données

**Accès** : `/database-schema/`

Visualisation du modèle de données de l'application.

---

## Historique des imports

**Accès** : `/import-history/`

Journal des imports de données effectués :

- **Date** : Date de l'import
- **Source** : Système source
- **Fichiers** : Nombre de fichiers importés
- **Statut** : Succès/Échec

---

## Raccourcis clavier (Vue Graphique)

| Touche | Action |
|--------|--------|
| `+` / `-` | Zoom avant/arrière |
| `Échap` | Désélectionner |
| `F` | Ajuster à l'écran |

---

## Support

Pour toute question ou problème :

- **Logs serveur** : `journalctl -u cartographie_si -f`
- **Redémarrage** : `systemctl restart cartographie_si`

---

*Documentation générée le 4 février 2026*
