# Réponses Questionnaire — Site Web Air Algérie
> Référent : BELDJERDI Zakaria (DRM)
> Source : Entretien téléphonique du 29 mars 2026

---

### A — Fonctionnalités et parcours client

**Q1 — Quelles fonctionnalités sont disponibles sur le site web aujourd'hui ? Lesquelles sont les plus utilisées ?**

Les fonctionnalités disponibles sur le site web airalgerie.dz :
- **Réservation de vols** (domestiques et internationaux)
- **Paiement en ligne** (carte CIB, carte Edahabia/CCP, Visa, Mastercard)
- **Consultation des horaires et des tarifs**
- **Gestion de réservation** (consultation PNR)
- **Informations pratiques** (bagages, formalités, etc.)

À noter : une **application mobile** (iOS et Android) existe également et propose quasiment les mêmes fonctionnalités. La différence principale est que le **site web (portail) est développé par une agence de développement algérienne** (backend PHP, frontend/CMS WordPress), tandis que l'**application mobile est un produit Amadeus de bout en bout**.

Les deux plateformes (site web + app mobile) partagent le même moteur de réservation : l'**IBE (Internet Booking Engine) d'Amadeus**, qui gère toute la partie e-commerce — génération des dossiers de réservation, émission des billets et paiement en ligne. L'application mobile est en réalité la partie responsive de la solution e-commerce web.

La réservation de vols est la fonctionnalité la plus utilisée.

---

**Q2 — Quel est le parcours client type pour une réservation en ligne ? Quels sont les principaux points d'abandon ?**

Le parcours type est le suivant :
1. Recherche de vol (origine, destination, dates, nombre de passagers)
2. Affichage des disponibilités et tarifs
3. Sélection du vol et de la classe tarifaire
4. Saisie des informations passagers
5. Récapitulatif de la réservation
6. Paiement en ligne
7. Émission du billet et confirmation

Les principaux points d'abandon :
- **Étape de paiement** : les plateformes de paiement algériennes (CIB, CCP/Edahabia) nécessitent des **redirections** vers des plateformes externes. Ces redirections génèrent des coupures entre les deux systèmes, provoquant des **échecs de capture de paiement et des cas de non-émission de billets**. Ce problème n'existe pas avec les cartes Visa/Mastercard dont le paiement est intégré nativement dans la solution IBE Amadeus.
- **Parcours de réservation jugé long** par certains utilisateurs sur le site web

Le parcours est en cours d'amélioration avec le déploiement de la solution **RFX (Reference Experience) d'Amadeus** qui apportera un meilleur UX, un nouveau design et de nouvelles fonctionnalités.

---

**Q3 — Quels moyens de paiement sont acceptés en ligne ? Y a-t-il des contraintes spécifiques au marché algérien ?**

Trois moyens de paiement sont acceptés :
- **Carte CIB** (carte interbancaire algérienne) — plateforme de paiement externe avec redirection
- **Carte CCP / Edahabia** — plateforme de paiement externe avec redirection
- **Cartes internationales** (Visa, Mastercard) — paiement intégré directement dans l'IBE Amadeus, sans redirection

Contraintes spécifiques au marché algérien :
- Les paiements CIB et CCP nécessitent des **redirections vers des plateformes de paiement externes**, contrairement aux cartes internationales intégrées dans l'IBE
- Ces redirections génèrent des **coupures** entre les deux plateformes, provoquant des échecs de capture de paiement et des non-émissions de billets
- Le site doit se conformer à l'**instruction 082001 de la Banque d'Algérie**, ce qui impose des adaptations via des scripts en arrière-plan sur la solution communautaire Amadeus, contribuant à la **lenteur du site web**
- Des **stratégies internes** doivent également être supportées, nécessitant des scripts supplémentaires pour forcer le fonctionnement standard de l'application

---

**Q4 — Le check-in en ligne est-il actif ? Si oui, quel est le taux d'utilisation ? Si non, est-il prévu et quels sont les freins ?**

Le check-in en ligne n'a pas été abordé spécifiquement lors de l'entretien. Les fonctionnalités mentionnées par le référent sont la réservation, le paiement, la consultation des horaires/tarifs, la gestion de réservation et les informations pratiques. Le check-in en ligne ne figure pas parmi les fonctionnalités actuellement disponibles sur le site web ni sur l'application mobile.

---

### B — Performance commerciale

**Q5 — Quel est le volume de réservations via le site web par mois ? Quelle part dans les ventes totales ?**

Le volume combiné de réservations via le site web et l'application mobile est d'environ **5 000 transactions par jour** (soit environ **150 000 par mois**). Ce chiffre varie significativement selon la **saisonnalité** et les **périodes de promotion**.

Note : ce volume englobe site web + application mobile, les deux partageant le même IBE Amadeus. Il n'y a pas de ventilation séparée site web vs application mobile communiquée.

Pour gérer les pics de trafic, l'équipe **augmente la bande passante et les capacités des serveurs d'hébergement** lors des périodes de forte sollicitation. Les périodes de pic sont monitorées afin d'anticiper les besoins en ressources.

---

**Q6 — Quel est le taux de conversion actuel ? Quels sont les objectifs ?**

Le taux de conversion est suivi via **Google Analytics**. Le référent a confirmé que l'outil permet d'obtenir les chiffres relatifs au taux de conversion, au nombre de sessions et au nombre d'utilisateurs en temps réel. Les chiffres exacts n'ont pas été communiqués lors de l'entretien.

---

**Q7 — Quels indicateurs de trafic web sont suivis aujourd'hui ? Quel outil analytics est utilisé ?**

**Google Analytics** est l'outil utilisé pour le suivi des performances. Les indicateurs suivis incluent :
- **Taux de conversion**
- **Nombre de sessions**
- **Nombre d'utilisateurs en temps réel**

---

### C — Contenu et gestion

**Q8 — Comment est géré le contenu du site (CMS) ? Qui met à jour les informations ?**

Le site web utilise **WordPress** pour la partie frontend — affichage et gestion du contenu. Le backend est développé en **PHP**. Le portail est développé et maintenu par une **agence de développement algérienne**.

Une **nouvelle équipe interne** est en cours de formation au sein de la structure de Beldjerdi. Cette équipe participera au développement de modules spécifiques et à l'amélioration de l'UX, en complément des produits proposés par Amadeus.

---

**Q9 — Existe-t-il un programme de fidélité en ligne ?**

Oui. Le programme de fidélité **Air Algérie Plus (FFP — Frequent Flyer Program)** existe et est accessible depuis le site web. Cependant, il est **géré par une structure distincte** (la structure FFP).

Côté site web, l'intégration se fait via des **API** qui effectuent des **redirections vers la plateforme FFP** pour :
- Les inscriptions des clients
- La gestion des dossiers clients FFP

Tout le backend de la gestion client FFP (accumulation de points, échanges, etc.) est géré directement par les outils FFP, pas par l'équipe du site web.

---

### D — Besoins et irritants

**Q10 — Quels sont les principaux irritants avec le site web aujourd'hui ?**

Les irritants principaux identifiés lors de l'entretien :

1. **Problèmes de paiement en Algérie** (irritant majeur) :
   - Les cartes CIB et CCP/Edahabia nécessitent des redirections vers des plateformes de paiement externes
   - Ces redirections génèrent des coupures entre les plateformes, provoquant des **échecs de capture de paiement** et des **non-émissions de billets**
   - Ce problème n'existe pas pour les paiements Visa/Mastercard, intégrés nativement dans l'IBE Amadeus

2. **Lenteur du site web** :
   - Causée par l'utilisation de **scripts en arrière-plan** (CSS et autres) nécessaires pour forcer le fonctionnement standard de la solution communautaire Amadeus
   - Ces scripts sont requis pour respecter l'**instruction 082001 de la Banque d'Algérie** et les stratégies internes d'Air Algérie
   - La solution Amadeus étant communautaire (utilisée par plusieurs compagnies aériennes), les adaptations locales doivent passer par des scripts de contournement

3. **Parcours de réservation long** sur le site web (retour d'enquête utilisateurs)

---

**Q11 — Quelles fonctionnalités ou analyses aimeriez-vous avoir ?**

Améliorations en cours ou souhaitées :
- **Déploiement de la solution RFX (Reference Experience) d'Amadeus** : nouvelle solution avec un meilleur UX, un nouveau design et de nouvelles fonctionnalités — devrait résoudre les problèmes de lenteur et de parcours long
- **Renforcement de l'équipe interne** pour le développement spécifique et l'amélioration UX
- **Amélioration de l'intégration des paiements algériens** pour réduire les échecs liés aux redirections

---

### Informations complémentaires (hors questionnaire)

**Architecture technique :**
- **Site web** : backend PHP + frontend WordPress, développé par une agence algérienne
- **Application mobile** : produit Amadeus de bout en bout (iOS + Android)
- **Moteur e-commerce** : IBE (Internet Booking Engine) d'Amadeus — partagé entre site web et app mobile
- L'IBE gère : génération des dossiers de réservation, émission des billets, paiement en ligne

**Interopérabilité :**
- L'IBE est **connecté au système de réservation Amadeus** (suite Altéa) — les informations passagers, dossiers de réservation et billets remontent directement dans le système de réservation
- L'IBE **n'est pas connecté directement** aux systèmes de comptabilité (direction financière) — le lien passe par le système passager Amadeus qui fait l'intermédiaire
- Le système est connecté aux plateformes de paiement et au système de réservation (suite Altéa), mais pas aux systèmes Rapid ou autres systèmes financiers

**Action en cours :**
- Zakaria Beldjerdi va exporter des échantillons des données/informations qu'il consulte côté IBE et les partager avec l'équipe projet pour mieux comprendre le modèle de données
