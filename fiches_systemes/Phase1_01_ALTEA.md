# Fiche Système — SUITE ALTÉA AMADEUS
## Phase 1 🔴 — Priorité #1 absolue

---

## Identification

| Champ | Valeur |
|-------|--------|
| **Système** | Suite Altéa (Reservation, Ticketing, Inventory, DCS) |
| **Éditeur** | Amadeus |
| **Division** | DC – DIVEX |
| **Direction** | DOS / DRM |
| **Responsable hiérarchique** | BERRABIA Mokrane (DOS) / FAIDI Fouad (DRM) |
| **Key User Principal** | FAIDI Fouad (DRM), FIALA Zahra (DOS), LOUNAOUCI Nassim (DOS), HASBELLAOUI Imen (DOS), GHARBI Mohamed (DOS), NAMOUNI Ali (DOS) |
| **Key User Backup** | SAFARZITOUN Naim (DRM), TACHTIOUI Omar (DOS), OUNISSI Akli (DOS), BELAMINE Ryad (DOS), TOUAHRIA Faiza (DOS), RAHAL Djalal (DOS), DAHMANI Koceila (DOS) |

---

## Justification de la priorité

| Critère | Détail |
|---------|--------|
| **Centralité** | Hub central du SI — alimente directement ou indirectement **plus de 15 systèmes** |
| **Référentiels maîtres** | Source de vérité pour **3 domaines** : Réservations & PNR, Billetterie & coupons, DCS |
| **Volume** | Système le plus volumineux : milliers de PNR/jour, coupons/jour, vols/jour |
| **Impact blocage** | Sans Altéa, impossible d'alimenter Rapid, Accelya, World Tracer, SITATEX |
| **Contrainte réglementaire** | Anonymisation RGPD obligatoire sur les données passagers |

---

## Systèmes alimentés par Altéa

Rapid Passagers, BSP Link, Site Web, BAC, World Tracer, SITATEX, AIMS, Accelya Distribution

## Systèmes qui alimentent Altéa

ATPCO (tarifs), AIMS (programmes SSIM), Site Web (réservations en ligne)

---

## Questions à adresser au métier

### A — Module Reservation

**Q1.** Quels sont les canaux de vente connectés à Altéa Reservation (agences, site web, call center, GDS tiers) ? Quel est le volume de PNR créés par jour et par canal ?

> **Réponse :**
>
>

**Q2.** Quelles sont les règles de gestion spécifiques appliquées lors de la création d'un PNR (limites de segments, délais de ticketing, politiques d'annulation automatique) ?

> **Réponse :**
>
>

**Q3.** Comment sont gérés les PNR de groupe vs les PNR individuels ? Y a-t-il des processus métier différents ?

> **Réponse :**
>
>

**Q4.** Quels rapports ou extractions sont produits régulièrement à partir des données de réservation ? Par qui et à quelle fréquence ?

> **Réponse :**
>
>

### B — Module Ticketing

**Q5.** Quel est le volume quotidien de coupons émis ? Quelle répartition entre billets électroniques, EMD, et documents manuels ?

> **Réponse :**
>
>

**Q6.** Comment fonctionne le processus de remboursement et de réémission ? Quelles sont les règles de gestion associées (délais, pénalités, autorisations) ?

> **Réponse :**
>
>

**Q7.** Comment sont gérés les billets interline avec les compagnies partenaires ? Quelles compagnies sont concernées et quel est le volume mensuel ?

> **Réponse :**
>
>

### C — Module Inventory

**Q8.** Comment sont gérées les classes de réservation et les disponibilités ? Qui décide de l'ouverture/fermeture des classes et selon quels critères ?

> **Réponse :**
>
>

**Q9.** Existe-t-il un système de Revenue Management connecté à l'Inventory ? Si oui, lequel et comment interagit-il ?

> **Réponse :**
>
>

**Q10.** Comment sont gérés les codeshares et les accords interline au niveau de l'inventaire ?

> **Réponse :**
>
>

### D — Module DCS (Departure Control System)

**Q11.** Quel est le processus d'enregistrement des passagers (comptoir, en ligne, kiosque) ? Quels canaux sont actifs aujourd'hui ?

> **Réponse :**
>
>

**Q12.** Comment sont gérés les cas de surbooking, de no-show et de go-show au niveau du DCS ?

> **Réponse :**
>
>

**Q13.** Quelles données DCS sont transmises aux autorités (API/PNR advance passenger information) ? Vers quels pays et dans quel format ?

> **Réponse :**
>
>

**Q14.** Comment le DCS interagit-il avec le système bagages (World Tracer) ? Quelles données sont échangées au moment de l'enregistrement ?

> **Réponse :**
>
>

### E — Processus transverses

**Q15.** Quels sont les principaux irritants métier aujourd'hui avec la suite Altéa ? Quelles données manquent ou sont difficiles à obtenir ?

> **Réponse :**
>
>

**Q16.** Quels indicateurs clés (KPI) aimeriez-vous suivre à partir des données Altéa qui ne sont pas disponibles aujourd'hui ?

> **Réponse :**
>
>

**Q17.** Y a-t-il des processus métier qui nécessitent aujourd'hui des extractions manuelles ou des contournements par rapport à Altéa ?

> **Réponse :**
>
>

**Q18.** Quels sont les data feeds Amadeus actuellement actifs (PNR feed, APS, FLP, coupon feed, DCS feed) ? Lesquels sont souhaités mais non encore en place ?

> **Réponse :**
>
>

---

*Fiche générée le 14 février 2026 — Projet Cartographie SI Air Algérie*
