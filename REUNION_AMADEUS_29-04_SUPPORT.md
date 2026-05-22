# Réunion Amadeus — Support de discussion

**Date :** Mercredi 29 avril 2026 — 11h30 (Algiers Time)
**Côté AAL :** M. Ali KARKI, Mme CHENANE Leila (SDS DC), équipe projet Cartographie SI
**Côté Amadeus :** *(interlocuteurs à confirmer)*

**Objectif :** Obtenir des **échantillons de feeds journaliers** (PNR / Ticket / Payment) anonymisés, définir les **modalités pratiques** de transfert, et explorer les **interconnexions** automatisées entre Altéa et le reste du SI cartographié.

---

## 1. Ce que nous savons déjà *(ne pas reposer en réunion)*

| Élément | Valeur connue |
|---|---|
| Versions prod | CM 87.22.5 / FM 25.3.27 / SAPE 4.15.1 |
| Environnements non-prod | PDT / UAT / SKL |
| Feeds actifs aujourd'hui | **SBR, CM, FM** (XML via FTP — serveur `192.168.104.8`) |
| Format des feeds | XML |
| API active | BLS uniquement |
| Contrat data feeds | Inclus |
| Volumétrie | 225 vols/jour — 16 500 PAX embarqués/jour |

---

## 2. Points à aborder

### 2.1 Feeds journaliers PNR / Ticket / Payment

> *Au-delà des feeds SBR/CM/FM déjà actifs, nous souhaitons obtenir les feeds **PNR, Ticket et Payment**.*

1. Quels sont les **noms commerciaux exacts** côté Amadeus de ces 3 feeds (ex. *PNR Data Feed*, *Coupon Data Feed*, *Sales/Payment Data Feed*) ?
2. Sont-ils **déjà générés** côté Amadeus pour Air Algérie, ou faut-il les **activer** ?
3. **Fréquence** de génération : temps réel, horaire, journalier, en fin de journée comptable BSP ?
4. **Documentation technique** disponible (specs / DTD / XSD / mapping de champs) ?

---

### 2.2 Échantillon anonymisé pour analyse

> *Nous avons besoin d'un échantillon couvrant **1 journée complète** sur les 3 feeds, pour POC ETL côté AAL.*

1. Amadeus peut-il livrer un **dataset déjà anonymisé** (sans donnée confidentielle PAX) ou faut-il que AAL anonymise après réception ?
2. Quelles **règles d'anonymisation** sont appliquées par Amadeus (nom, n° passeport, n° carte, contact) ?
3. **Délai** de mise à disposition de l'échantillon ?
4. Périmètre souhaité : 1 journée, **les 3 feeds cohérents entre eux** pour permettre les rapprochements PNR ↔ Ticket ↔ Payment.

---

### 2.3 Modalités pratiques de transfert

> *Nous sommes aujourd'hui en FTP sur `192.168.104.8`. Comment ça se passe pour les nouveaux feeds ?*

1. **Canal** retenu : SFTP, portail Amadeus Service Hub, API pull, autre ?
2. **Migration FTP → SFTP** du serveur actuel : faisable ? quel délai ?
3. **Authentification** : login/password, clé SSH, certificat ?
4. **Conventions de nommage** des fichiers (préfixe, timestamp, séquence) ?
5. **Politique de rétention** côté Amadeus : combien de jours d'historique disponibles si un transfert échoue ?
6. **Monitoring / alertes** en cas d'échec de génération ou de transfert ?

---

### 2.4 Interconnexions automatisées

> *Aujourd'hui seule l'API BLS est active. Nous voulons activer les autres canaux pour automatiser les flux entre Altéa et les autres systèmes du SI.*

1. **APIs Amadeus disponibles** au-delà de BLS :
   - **Altéa Web Services** (Inventory / DCS / Reservation)
   - **e-Retail** / **NDC**

   Conditions d'activation (technique + contractuel) ?
2. **Sandbox** avec données de test pour valider avant bascule prod ?
3. **Webhooks / push events** côté Amadeus (émission ticket, embarquement DCS, modif PNR) ?
4. **Interfaces Altéa ↔ autres systèmes Air Algérie** — lesquelles sont déjà actives, lesquelles activables ?
   - Altéa ↔ **AIMS** : injection programmes SSIM
   - Altéa DCS ↔ **World Tracer** : messages bagages BSM
   - Altéa ↔ **Rapid Passagers (Accelya)** : coupons & revenue accounting
   - Altéa ↔ **BSP Link / Accelya Distribution** : ventes BSP
   - Altéa ↔ **ATPCO** : mise à jour tarifaire
   - Altéa ↔ **SITATEX** : LDM, MVT, PNL/ADL
   - Altéa ↔ **BAC** : billetterie interline

---

### 2.5 Cas d'usage concret — OFP & opérations vol

> *Exemple concret : OFP du vol DAH6296 DAAG→DAUI ATR72 du 26/04/2026 produit par Jeppesen / SkyBook / FlySmart côté DOA — beaucoup de champs encore à saisie manuelle.*

1. **PAX prévisionnel** : Altéa Inventory peut-il pousser le **booking count** en temps réel vers Jeppesen pour le calcul masse & équilibrage / fuel ?
2. **Programme SSIM** Altéa → Jeppesen : format & fréquence (SSIM standard IATA file ?) ?
3. **Closed Flight Data** (PAX réels, bagages, cargo, ZFW) en retour vers Altéa : feed CDX ?
4. **Block / T-O / Landing times** : capture automatique côté DCS (interface ACARS) ou saisie manuelle ?
5. **MVT messages** : génération automatique vers SITATEX après le vol ?

---

## 3. Livrables attendus du call

1. ✅ Confirmation activation **PNR / Ticket / Payment feeds**
2. ✅ Engagement de fourniture d'un **échantillon anonymisé 1 journée** + date cible
3. ✅ Modalités techniques de **transfert** documentées
4. ✅ **Documentation technique** des feeds (specs / XSD)
5. ✅ Liste des **APIs / interconnexions activables** avec conditions
6. ✅ **Interlocuteur technique dédié** Amadeus pour le projet ETL

---

*Document préparé le 29/04/2026 — Équipe projet Cartographie SI Air Algérie*
