# Réponses Questionnaire — GLPI
> Référent : YOUCEF ACHIRA Abdellah (DSI)
> Source : Réponses saisies sur la plateforme

---

### A — Gestion du parc informatique

**Q1 — Quels types d'équipements sont inventoriés dans GLPI ? Quel est le volume total par catégorie ?**

Aucun pour le moment.

---

**Q2 — Comment est maintenu l'inventaire à jour ?**

L'inventaire est tenu via une **saisie manuelle**. Pas d'agent d'inventaire automatique déployé.

---

**Q3 — Comment sont gérés les contrats de maintenance et les garanties dans GLPI ?**

Pas de gestion des contrats et garanties dans GLPI.

---

### B — Gestion des tickets support

**Q4 — Quels types de demandes sont gérées via les tickets GLPI ? Quel est le volume mensuel ?**

Les types de demandes gérés actuellement :
- **Incidents**
- **Demandes de service**
- **Demandes de matériel**
- **Demandes d'accès**

Volume mensuel non communiqué.

---

**Q5 — Quel est le processus de traitement d'un ticket ? Quels sont les niveaux de support et SLA ?**

- L'équipe **Helpdesk** assure le **N1** pour le traitement des tickets
- Une **escalade vers le N2** peut être faite si nécessaire
- Pas de mention de N3 ni de SLA formalisés

---

**Q6 — Quels indicateurs de performance IT sont suivis ?**

- **Délai moyen de résolution**
- **Taux de résolution**
- **Taux de disponibilité du réseau**

---

### C — Besoins et irritants

**Q7 — Quels sont les principaux irritants avec GLPI aujourd'hui ?**

L'**absence d'un parc centralisé sous Active Directory (AD)** complique la tâche d'installation des agents de récolte des informations. Sans AD centralisé, le déploiement automatique des agents d'inventaire GLPI n'est pas possible, d'où le recours à la saisie manuelle.

---

**Q8 — Quelles analyses aimeriez-vous réaliser ?**

- **Analyse des incidents récurrents**
- **Planification des remplacements**
- **Répartition du parc informatique**

---

### Points clés à retenir

- GLPI est utilisé principalement comme **outil de ticketing**, pas comme CMDB/gestion de parc
- L'inventaire du parc est **inexistant** dans GLPI (aucun équipement inventorié)
- La saisie manuelle est le seul mode de mise à jour — pas d'agent automatique
- **Frein principal** : absence d'AD centralisé empêche le déploiement d'agents
- Pas de gestion des contrats/garanties
- Support structuré en N1 (Helpdesk) + escalade N2, sans SLA formalisé
