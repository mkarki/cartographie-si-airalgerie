# Fiche Système — ACARS / HERMES
## Phase 1 🔴 — Priorité #6

---

## Identification

| Champ | Valeur |
|-------|--------|
| **Système** | ACARS / Hermes (Messages air-sol temps réel) |
| **Éditeur** | Collins ARINC |
| **Division** | DIVEX |
| **Direction** | CCO |
| **Responsable hiérarchique** | HOUAOUI Samia |
| **Key User Principal** | LADJICI Fatima |
| **Key User Backup** | BENNOUAR Adnane |

---

## Justification de la priorité

| Critère | Détail |
|---------|--------|
| **Temps réel opérationnel** | Seule source de données temps réel sur les mouvements avions (OOOI) |
| **Calcul ponctualité** | Indispensable pour le calcul OTP (On-Time Performance) |
| **Alimentation CCO** | Alimente les Dashboards CCO et le Suivi Irrégularités |
| **Corrélation AIMS** | Heures planifiées (AIMS) vs heures réelles (ACARS) |

---

## Systèmes alimentés par ACARS

AIMS, Dashboards CCO, SITATEX

## Systèmes qui alimentent ACARS

Avions (messages automatiques air-sol)

---

## Questions à adresser au métier

### A — Types de messages et exploitation

**Q1.** Quels types de messages ACARS sont reçus et exploités (OOOI — Out/Off/On/In, messages techniques moteurs, free text pilotes, météo) ? Lesquels sont les plus critiques pour les opérations ?

> **Réponse :**
>
>

**Q2.** Quel est le volume quotidien de messages ACARS reçus ? Combien de vols sont couverts par ACARS (tous les vols ou seulement certains) ?

> **Réponse :**
>
>

**Q3.** Comment les messages OOOI sont-ils exploités par le CCO ? Quelles décisions sont prises en temps réel sur la base de ces messages ?

> **Réponse :**
>
>

**Q4.** Les messages techniques moteurs (engine reports) sont-ils exploités ? Si oui, par qui (DMRA, CCO) et pour quelles analyses ?

> **Réponse :**
>
>

### B — Processus opérationnels CCO

**Q5.** Comment le CCO suit-il la ponctualité en temps réel ? Les données ACARS sont-elles affichées sur un écran de suivi ou consultées dans Hermes ?

> **Réponse :**
>
>

**Q6.** Comment sont détectées et gérées les irrégularités à partir des données ACARS (retard au départ, déroutement, retour) ? Quel est le processus d'alerte ?

> **Réponse :**
>
>

**Q7.** Comment les heures réelles ACARS sont-elles intégrées dans AIMS ? Ce flux est-il automatique ou y a-t-il une ressaisie manuelle ?

> **Réponse :**
>
>

### C — Communication équipage

**Q8.** Les équipages utilisent-ils ACARS pour envoyer des messages free text au CCO ou au DOA ? Si oui, dans quels cas et quel est le volume ?

> **Réponse :**
>
>

**Q9.** Comment sont gérés les messages ACARS de demande de maintenance (pilot reports / PIREP) ? Sont-ils transmis à la DMRA automatiquement ?

> **Réponse :**
>
>

### D — Besoins et irritants

**Q10.** Quels sont les principaux irritants avec le système ACARS/Hermes aujourd'hui ? Y a-t-il des problèmes de couverture, de fiabilité ou de délai de réception ?

> **Réponse :**
>
>

**Q11.** Quels indicateurs aimeriez-vous calculer à partir des données ACARS qui ne sont pas disponibles aujourd'hui (ponctualité par escale, temps de rotation réel, consommation carburant) ?

> **Réponse :**
>
>

**Q12.** Y a-t-il des données ACARS qui sont aujourd'hui recopiées manuellement dans des fichiers Excel ou d'autres systèmes ?

> **Réponse :**
>
>

---

*Fiche générée le 14 février 2026 — Projet Cartographie SI Air Algérie*
