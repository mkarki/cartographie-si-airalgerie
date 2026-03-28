# Guide Utilisateur — Remplissage du Questionnaire Key User

**Cartographie SI — Air Algérie**
**URL** : https://cartographie-si-airalgerie.onrender.com/

> Ce guide est destiné aux **Key Users** désignés pour chaque système d'information. Il décrit pas à pas comment accéder au questionnaire, le remplir et soumettre vos réponses.

---

## Table des matières

1. [Prérequis](#1-prérequis)
2. [Accéder au questionnaire](#2-accéder-au-questionnaire)
3. [Comprendre l'interface du questionnaire](#3-comprendre-linterface-du-questionnaire)
4. [Remplir le questionnaire](#4-remplir-le-questionnaire)
5. [Enregistrer vos réponses](#5-enregistrer-vos-réponses)
6. [Joindre des pièces jointes](#6-joindre-des-pièces-jointes)
7. [Basculer entre plusieurs questionnaires](#7-basculer-entre-plusieurs-questionnaires)
8. [Comprendre les statuts et la validation](#8-comprendre-les-statuts-et-la-validation)
9. [Bonnes pratiques](#9-bonnes-pratiques)
10. [FAQ — Questions fréquentes](#10-faq--questions-fréquentes)
11. [Support](#11-support)

---

## 1. Prérequis

Avant de commencer, vérifiez que vous disposez de :

- **Un navigateur web récent** : Chrome, Firefox, Edge ou Safari (version récente)
- **Une connexion internet** active
- **Votre lien d'accès personnel** : un lien unique vous a été transmis par email par l'équipe DSI. Ce lien a la forme :
  ```
  https://cartographie-si-airalgerie.onrender.com/key-user/?token=VOTRE_CODE_UNIQUE
  ```
- **Les informations sur votre système** : préparez les données relatives au système dont vous êtes le référent (volumes, processus, irritants, etc.)

> **Important** : Votre lien est personnel et confidentiel. Ne le partagez pas avec des personnes non autorisées.

---

## 2. Accéder au questionnaire

### Méthode 1 — Via le lien direct (recommandé)

1. **Cliquez sur le lien** reçu par email
2. Vous êtes automatiquement redirigé vers le **formulaire de votre questionnaire**
3. Aucun identifiant ni mot de passe n'est nécessaire

### Méthode 2 — Via la page d'accueil

Si vous n'avez plus le lien complet mais seulement votre code d'accès (token) :

1. Rendez-vous sur : **https://cartographie-si-airalgerie.onrender.com/**
2. Sur la page de connexion, repérez la section **« Accès Key User »** en bas de page (encadré avec une icône de clé dorée)

```
┌──────────────────────────────────────────────┐
│  🔑  Accès Key User                         │
│                                              │
│  Vous êtes un interlocuteur métier ?         │
│  Entrez votre code d'accès personnel.        │
│                                              │
│  ┌─────────────────────────┐ ┌──────────┐   │
│  │ Votre code d'accès      │ │ Accéder  │   │
│  └─────────────────────────┘ └──────────┘   │
└──────────────────────────────────────────────┘
```

3. **Collez votre code d'accès** (la partie après `?token=` dans votre lien) dans le champ
4. Cliquez sur **« Accéder »**

> **Note** : La section du haut (« Connexion Admin ») est réservée aux administrateurs. En tant que Key User, utilisez uniquement la section **« Accès Key User »**.

---

## 3. Comprendre l'interface du questionnaire

Une fois connecté, vous arrivez sur le formulaire de votre questionnaire. L'interface se compose de **4 zones principales** :

### 3.1 — En-tête du questionnaire

```
┌──────────────────────────────────────────────────────────────────┐
│  📋  GLPI                                    Phase 1            │
│  Questionnaire de cartographie SI — Air Algérie                 │
│                                                                  │
│  Éditeur         Direction        Key Users                      │
│  Open Source     DAG / DSI        YOUCEF ACHIRA Abdellah         │
└──────────────────────────────────────────────────────────────────┘
```

Vous y trouvez :
- **Le nom du système** dont vous êtes le référent
- **La phase** du projet (Phase 1 🔴 = Critique, Phase 2 🟠 = Important, Phase 3 🟢 = Standard)
- **L'éditeur** du logiciel, la **direction** concernée et les **key users** assignés

### 3.2 — Barre de progression

```
┌──────────────────────────────────────────────────────────────────┐
│  Votre progression                    3 / 8 questions répondues  │
│  ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  37%       │
└──────────────────────────────────────────────────────────────────┘
```

- La barre se met à jour **en temps réel** au fur et à mesure que vous répondez
- **Bleu** = en cours, **Vert** = 100% complété

### 3.3 — Navigation par sections (colonne gauche)

Sur écran large (PC/laptop), un **panneau de navigation** apparaît à gauche :

```
┌─────────────────────────┐
│  SECTIONS               │
│                         │
│  A — Gestion du parc    │
│      informatique (3)   │
│  B — Gestion des        │
│      tickets support (3)│
│  C — Besoins et         │
│      irritants (2)      │
└─────────────────────────┘
```

- Cliquez sur une section pour **y accéder directement**
- La section active est **surlignée en rouge** lors du défilement
- Le nombre entre parenthèses indique le **nombre de questions** dans chaque section

### 3.4 — Zone des questions (partie principale)

Chaque question est présentée dans une **carte individuelle** :

```
┌──────────────────────────────────────────────────────────────────┐
│  ┌────┐                                                          │
│  │ Q1 │  Quels types d'équipements sont inventoriés dans GLPI   │
│  └────┘  (postes de travail, serveurs, imprimantes...) ?         │
│          Quel est le volume total par catégorie ?                 │
│                                                                  │
│          ┌──────────────────────────────────────────────────┐    │
│          │ Saisissez votre réponse ici...                   │    │
│          │                                                  │    │
│          │                                                  │    │
│          └──────────────────────────────────────────────────┘    │
│          [💾 Enregistrer]                                        │
│          📎 Pièce jointe                                         │
└──────────────────────────────────────────────────────────────────┘
```

- Le **numéro de la question** (Q1, Q2...) est affiché dans un badge
- Badge **gris** = pas encore répondu / Badge **vert** = réponse saisie
- Un **liseré vert à gauche** apparaît sur les questions déjà répondues
- Un **liseré rouge à gauche** apparaît lorsque vous saisissez une réponse (focus)

---

## 4. Remplir le questionnaire

### Étape par étape

1. **Lisez attentivement la question** — prenez le temps de bien comprendre ce qui est demandé
2. **Cliquez dans la zone de texte** sous la question
3. **Rédigez votre réponse** — soyez aussi précis et complet que possible
4. **Passez à la question suivante** en faisant défiler vers le bas

### Conseils pour la rédaction

| Élément demandé | Exemple de bonne réponse |
|------------------|--------------------------|
| **Volume de données** | « ~15 000 tickets/mois dont 60% incidents et 40% demandes de service » |
| **Processus** | « 1) L'utilisateur ouvre un ticket via le portail web → 2) Le N1 qualifie → 3) Escalade N2 si non résolu sous 4h → 4) Clôture avec satisfaction » |
| **Fréquence** | « Import quotidien à 6h00 via script automatique, durée ~20 min » |
| **Irritants** | « L'inventaire n'est fiable qu'à 70%, les agents d'inventaire ne remontent pas les équipements réseau » |

> **Astuce** : Vous pouvez **redimensionner** la zone de texte en tirant le coin inférieur droit si votre réponse est longue.

---

## 5. Enregistrer vos réponses

Il existe **deux méthodes** pour sauvegarder votre travail :

### Méthode 1 — Sauvegarde individuelle (recommandé)

Après avoir répondu à chaque question, cliquez sur le bouton **« 💾 Enregistrer »** situé juste en dessous de la zone de texte.

```
┌────────────────────────────────────────────┐
│  [💾 Enregistrer]   ✓ Sauvegardé à 14:32  │
└────────────────────────────────────────────┘
```

- Le bouton devient **vert** avec la mention **« ✓ Enregistré »** pendant quelques secondes
- L'heure de sauvegarde est affichée à côté
- La barre de progression se met à jour automatiquement
- **Aucun rechargement de page** n'est nécessaire (sauvegarde instantanée)

### Méthode 2 — Soumission globale

En bas du questionnaire, un bouton rouge permet de soumettre **toutes les réponses d'un coup** :

```
┌──────────────────────────────────────────────────────────────────┐
│  Vos réponses seront sauvegardées et visibles par l'équipe      │
│  projet. Vous pouvez revenir modifier vos réponses à tout       │
│  moment via ce lien.                                             │
│                                              [📤 Envoyer mes    │
│                                                  réponses]       │
└──────────────────────────────────────────────────────────────────┘
```

- Cliquez sur **« Envoyer mes réponses »**
- Un **bandeau vert de confirmation** apparaît en haut de page :

```
┌──────────────────────────────────────────────────────────────────┐
│  ✅  Réponses enregistrées avec succès !                        │
│  Merci pour votre contribution. Vous pouvez modifier vos        │
│  réponses à tout moment.                                         │
└──────────────────────────────────────────────────────────────────┘
```

> **Important** : Vous pouvez **revenir à tout moment** via votre lien pour compléter ou modifier vos réponses. Le questionnaire conserve toutes les réponses déjà saisies.

---

## 6. Joindre des pièces jointes

Vous pouvez joindre des **fichiers** à chaque question (captures d'écran, documents PDF, exports Excel, etc.).

### Comment faire

1. Sous chaque question, cliquez sur **« 📎 Pièce jointe »** pour déplier la zone de téléversement
2. Cliquez sur **« Joindre un fichier (PDF, image, doc...) »**
3. Sélectionnez le fichier depuis votre ordinateur
4. Le nom du fichier sélectionné s'affiche
5. Cliquez sur **« Envoyer mes réponses »** en bas de page pour transmettre le fichier

```
┌──────────────────────────────────────────────────────────────────┐
│  📎 Pièce jointe  (1 fichier)                                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  📄 export_inventaire_glpi.pdf                           │    │
│  └──────────────────────────────────────────────────────────┘    │
│  ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐   │
│  │  ⬆️  Remplacer le fichier                                │   │
│  └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘   │
└──────────────────────────────────────────────────────────────────┘
```

### Formats acceptés

- **Documents** : PDF, Word (.doc, .docx), Excel (.xls, .xlsx)
- **Images** : PNG, JPG, GIF
- **Autres** : tout type de fichier courant

> **Note** : Les pièces jointes sont transmises lors de la **soumission globale** (bouton « Envoyer mes réponses »), pas via le bouton « Enregistrer » individuel.

---

## 7. Basculer entre plusieurs questionnaires

Certains Key Users sont référents de **plusieurs systèmes** (ex : YOUCEF ACHIRA Abdellah est référent de GLPI, ZIMBRA, PORTAIL AH et des Questions Techniques).

Dans ce cas, une **barre de navigation** apparaît en haut de l'écran avec les noms de vos systèmes :

```
┌──────────────────────────────────────────────────────────────────┐
│  [GLPI]  [PORTAIL AH]  [Questions Techniques]  [ZIMBRA]  [Quitter] │
└──────────────────────────────────────────────────────────────────┘
```

- Cliquez sur le **nom du système** souhaité pour basculer vers son questionnaire
- Vos réponses sur le questionnaire précédent sont **automatiquement conservées**
- Le bouton **« Quitter »** vous déconnecte et vous ramène à la page de connexion

---

## 8. Comprendre les statuts et la validation

### Progression du questionnaire

| Statut | Signification |
|--------|---------------|
| **Non commencé** | Aucune réponse saisie |
| **En cours** | Au moins une réponse saisie, questionnaire incomplet |
| **Terminé** | 100% des questions répondues |

### Validation par l'auditeur

Après soumission de vos réponses, un **auditeur DSI** les examine. Vous pouvez voir l'état de validation de chaque question :

| Indicateur | Signification |
|------------|---------------|
| ✅ **Validée** (badge vert) | Votre réponse a été acceptée par l'auditeur |
| ❌ **À revoir** (badge rouge) | L'auditeur demande des précisions ou corrections |
| _(aucun badge)_ | Réponse en attente de validation |

### Commentaires de l'auditeur

Si l'auditeur a laissé un commentaire sur une de vos réponses, il apparaît dans un **encadré violet** sous votre réponse :

```
┌──────────────────────────────────────────────────────────────────┐
│  💬 Commentaire de l'auditeur                                    │
│  « Pouvez-vous préciser le nombre exact de serveurs virtuels     │
│    vs physiques dans l'inventaire ? »                             │
│                              — Auditeur DSI · 15/03/2026 10:30   │
└──────────────────────────────────────────────────────────────────┘
```

> **Action requise** : Si une question est marquée **« À revoir »**, revenez sur votre questionnaire via votre lien, corrigez ou complétez votre réponse, puis cliquez à nouveau sur « Enregistrer ».

---

## 9. Bonnes pratiques

### Avant de commencer
- [ ] Rassemblez les **documents de référence** de votre système (documentation technique, dashboards, rapports)
- [ ] Prévoyez **30 à 60 minutes** pour compléter le questionnaire
- [ ] Si possible, consultez votre **Key User backup** pour valider vos réponses

### Pendant le remplissage
- [ ] Répondez de manière **détaillée et structurée** (utilisez des listes numérotées si nécessaire)
- [ ] Indiquez les **chiffres et volumes** quand c'est pertinent (nombre d'utilisateurs, fréquences, volumes de données)
- [ ] Si vous ne connaissez pas une réponse, indiquez-le clairement : _« Information non disponible — à vérifier avec [personne/service] »_
- [ ] **Sauvegardez régulièrement** question par question (bouton « Enregistrer »)
- [ ] Joignez des **captures d'écran** ou documents quand cela peut clarifier votre réponse

### Après le remplissage
- [ ] Vérifiez que la **barre de progression atteint 100%**
- [ ] Cliquez sur **« Envoyer mes réponses »** pour la soumission finale
- [ ] Conservez votre **lien d'accès** pour revenir modifier vos réponses si nécessaire
- [ ] Revenez **sous 48h** si l'auditeur demande des compléments

---

## 10. FAQ — Questions fréquentes

### « J'ai perdu mon lien d'accès »
Contactez l'équipe DSI qui vous renverra votre lien personnel. Chaque Key User possède un token unique et confidentiel.

### « Puis-je remplir le questionnaire en plusieurs fois ? »
**Oui, absolument.** Vos réponses sont sauvegardées à chaque fois que vous cliquez sur « Enregistrer » ou « Envoyer mes réponses ». Vous pouvez revenir via votre lien autant de fois que nécessaire.

### « Le lien ne fonctionne pas / message "Code d'accès invalide" »
Vérifiez que :
- Vous avez copié **l'intégralité du lien** (il est long et peut être tronqué par email)
- Votre accès n'a pas été désactivé — contactez l'équipe DSI en cas de doute

### « Puis-je modifier une réponse déjà soumise ? »
**Oui.** Retournez sur le questionnaire via votre lien. Vos anciennes réponses sont pré-remplies dans les champs. Modifiez-les puis cliquez à nouveau sur « Enregistrer ».

### « Je suis Key User backup, comment accéder au questionnaire ? »
Le Key User backup dispose de son **propre lien d'accès** avec un token différent, pointant vers le même questionnaire. Contactez l'équipe DSI si vous n'avez pas reçu votre lien.

### « Mon questionnaire contient une question à laquelle je ne sais pas répondre »
Indiquez-le dans la réponse : _« Je n'ai pas l'information — à vérifier avec [nom/service] »_. Ne laissez pas le champ vide si possible.

### « Comment savoir si l'auditeur a validé mes réponses ? »
Reconnectez-vous via votre lien. Les questions validées affichent un badge vert ✅ « Validée ». Les questions à revoir affichent un badge rouge ❌ « À revoir » accompagné d'un commentaire de l'auditeur.

### « Puis-je accéder au questionnaire depuis mon téléphone ? »
**Oui**, l'interface est responsive. Cependant, pour le confort de rédaction de réponses détaillées, un **ordinateur est recommandé**.

---

## 11. Support

Pour toute question ou problème technique :

| Canal | Contact |
|-------|---------|
| **Email** | Équipe projet DSI |
| **Référent technique** | YOUCEF ACHIRA Abdellah (DSI) |

---

## Annexe — Récapitulatif visuel du parcours Key User

```
  ┌─────────────────┐
  │  Email reçu     │
  │  avec lien      │
  │  personnel      │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │  Clic sur le    │
  │  lien d'accès   │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐     ┌─────────────────┐
  │  Page du        │     │  Si plusieurs    │
  │  questionnaire  │────▶│  systèmes :      │
  │  s'affiche      │     │  navigation en   │
  │                 │     │  haut de page    │
  └────────┬────────┘     └─────────────────┘
           │
           ▼
  ┌─────────────────┐
  │  Répondre aux   │
  │  questions      │
  │  section par    │
  │  section        │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │  💾 Enregistrer │
  │  chaque réponse │
  │  individuellement│
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │  📎 Joindre des │
  │  fichiers si    │
  │  nécessaire     │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │  📤 Envoyer mes │
  │  réponses       │
  │  (bouton final) │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │  ✅ Confirmation│
  │  Attendre la    │
  │  validation de  │
  │  l'auditeur     │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │  Si "À revoir": │
  │  Revenir via le │
  │  lien, corriger │
  │  et re-soumettre│
  └─────────────────┘
```

---

*Guide rédigé le 16 mars 2026 — Direction des Systèmes d'Information — Air Algérie*
*Application : Cartographie SI v1.0 — Alpha Aero Systems*
