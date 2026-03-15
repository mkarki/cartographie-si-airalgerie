# Fiche Système — SAGE STOCK
## Phase 2 🟠 — Priorité #1

---

## Identification

| Champ | Valeur |
|-------|--------|
| **Système** | SAGE STOCK (Gestion des stocks et pièces) |
| **Éditeur** | Sans contrat |
| **Division** | DAG |
| **Direction** | DAGP |
| **Responsable hiérarchique** | HABEL Rachid |
| **Key User Principal** | ATTOUT Abedlhafid |
| **Key User Backup** | AIT MEZIANE Amar |

---

## Justification de la priorité

| Critère | Détail |
|---------|--------|
| **Référentiel maître** | Source de vérité pour **Stocks & pièces** |
| **Lien AMOS critique** | Alimente AMOS en données pièces de rechange |
| **Risque contractuel** | **Absence de contrat éditeur** — risque majeur |
| **Impact maintenance** | Sans données stock fiables, la planification maintenance est compromise |

---

## Systèmes alimentés par SAGE STOCK

AMOS (pièces de rechange)

## Systèmes qui alimentent SAGE STOCK

AMOS (retours de pièces, consommations)

---

## Questions à adresser au métier

### A — Périmètre fonctionnel

**Q1.** Quels modules SAGE sont utilisés aujourd'hui (gestion des stocks, inventaire, mouvements, bons de commande, réception) ? Y a-t-il des modules disponibles mais non utilisés ?

> **Réponse :**
>
>

**Q2.** Quels types d'articles sont gérés dans SAGE STOCK (pièces avion rotables, consommables, outillage, fournitures de bureau, produits de bord) ? Quelle est la volumétrie par catégorie ?

> **Réponse :**
>
>

**Q3.** Combien d'articles sont référencés au total ? Combien de mouvements de stock sont enregistrés par mois (entrées, sorties, transferts) ?

> **Réponse :**
>
>

### B — Processus métier

**Q4.** Quel est le circuit complet d'un mouvement de stock, de la demande de pièce (OT AMOS ou demande directe) jusqu'à la sortie physique du magasin ? Quelles validations sont nécessaires ?

> **Réponse :**
>
>

**Q5.** Comment fonctionne le processus de réapprovisionnement ? Existe-t-il des seuils de réapprovisionnement automatiques dans SAGE ou sont-ils gérés manuellement ?

> **Réponse :**
>
>

**Q6.** Comment sont gérés les inventaires (fréquence, méthode — tournant ou annuel, écarts constatés) ?

> **Réponse :**
>
>

**Q7.** Comment est gérée la valorisation des stocks (FIFO, CUMP, prix standard) ? Cette valorisation alimente-t-elle la comptabilité ?

> **Réponse :**
>
>

### C — Lien avec AMOS

**Q8.** Comment se fait concrètement l'échange d'information entre SAGE STOCK et AMOS pour les pièces avion ? Est-ce automatisé, par fichier, ou par ressaisie manuelle ?

> **Réponse :**
>
>

**Q9.** Les codes articles sont-ils les mêmes dans SAGE STOCK et AMOS (Part Number) ou existe-t-il un mapping entre les deux référentiels ?

> **Réponse :**
>
>

**Q10.** Comment sont gérées les pièces sous traçabilité aéronautique (certificats, numéros de série) dans SAGE STOCK vs dans AMOS ?

> **Réponse :**
>
>

### D — Besoins et irritants

**Q11.** L'absence de contrat éditeur pose-t-elle des problèmes concrets aujourd'hui (mises à jour, support, bugs) ? Quelles alternatives sont envisagées ?

> **Réponse :**
>
>

**Q12.** Quels rapports de stock produisez-vous régulièrement ? Sont-ils générés depuis SAGE ou via des extractions manuelles ?

> **Réponse :**
>
>

**Q13.** Quels indicateurs de gestion de stock aimeriez-vous suivre (taux de rotation, valeur immobilisée, taux de rupture, délai moyen de réapprovisionnement) ?

> **Réponse :**
>
>

---

*Fiche générée le 14 février 2026 — Projet Cartographie SI Air Algérie*
