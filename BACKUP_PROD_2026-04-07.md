# Sauvegarde État Production — 12 avril 2026, 15:59 (avant push correction flux AMOS)

| Indicateur | Valeur |
|------------|--------|
| Systèmes | 38 |
| Flux | 70 (était 73, -4 supprimés +1 créé) |
| Structures | 17 |
| Process | 1 |
| ProcessSteps | 8 |
| Dernière migration locale | 0020_seed_process_world_tracer |

## Corrections flux AMOS (entretien DMRA 12/04/2026)

- **Supprimé** AMOS → SAGE-STOCK (id=31) : aucun échange, stock AMOS autonome
- **Supprimé** QPULSE → AMOS (id=55) : systèmes indépendants
- **Supprimé** AMOS → QPULSE (id=54) : systèmes indépendants
- **Supprimé** AMOS → AGS (id=29) : données viennent de l'avion, pas d'AMOS
- **Corrigé** AIMS → AMOS (id=3) : heures de vol, cycles, programme des vols
- **Corrigé** AMOS → AIMS (id=4) : prévisions d'immobilisation maintenance
- **Créé** AMOS → SAGE-FIN : stock et valorisation pièces vers ERP comptable

---

# Sauvegarde État Production — 12 avril 2026, 13:13 (avant push module Process)

| Indicateur | Valeur |
|------------|--------|
| Systèmes | 38 |
| Flux | 73 |
| Structures | 17 |
| Questionnaires | 40 |
| Questions | 619 |
| Échantillons | 14 |
| KeyUserAccess | 40 |
| AuditorAccess | 4 |
| DivisionAccess | 11 |
| Process | 1 (test local) |
| ProcessSteps | 8 |
| Dernière migration prod | 0018_edoleance_dvr_dag_auditor |

## Changements à pousser

- `0019_add_process_models` — Modèles Process + ProcessStep
- Module Process complet : CRUD + service IA Claude + diagramme Mermaid
- Accès Process réservé aux admins (staff_member_required)
- Lien sidebar masqué pour non-admins

---

# Sauvegarde État Production — 10 avril 2026, 08:54 (avant transfert e-doléance + DAG admin)

| Indicateur | Valeur |
|------------|--------|
| Systèmes | 38 |
| Questionnaires | 40 (15 terminés, 5 en cours) |
| Questions | 619 (202 répondues, 32%) |
| Phase 1 (Critique) | 96/332 (28%), 3 terminés / 7 |
| Phase 2 (Important) | 40/150 (26%), 4 terminés / 15 |
| Phase 3 (Standard) | 66/137 (48%), 8 terminés / 18 |
| Flux documentés | 73 |
| Échantillons | 14 |
| Questions validées | 0 |
| Dernière migration prod | 0015_add_division_access |

## Changements à pousser

- `0016_create_division_tokens` — Création des tokens divisionnaires
- `0017_personalized_division_access` — Accès personnalisés
- **E-doléance** : transféré de DRM → DVR (System id=34)
- **Mme la DAG** : convertie DivisionAccess → AuditorAccess (vue complète, même token)
- PostgreSQL Render : `dpg-d743dghaae7s73bad4og-a`
- App Render : `cartographie-si-airalgerie.onrender.com`

## Progression depuis le 8 avril

- Questions répondues : 135 → **202** (+67, soit +49%)
- Questionnaires terminés : 12 → **15** (+3)
- Phase 1 : 30 → **96** réponses (+220%)

---

# Sauvegarde État Production — 8 avril 2026, 12:02 (avant push accès personnalisés)

| Indicateur | Valeur |
|------------|--------|
| Systèmes | 38 |
| Questionnaires | 40 (12 terminés, 5 en cours) |
| Questions | 619 (135 répondues, 21%) |
| Phase 1 | 30/332 (9%), 1 terminé |
| Phase 2 | 40/150 (26%), 4 terminés |
| Phase 3 | 65/137 (47%), 7 terminés |
| Dernière migration | 0016_create_division_tokens |

---

# Sauvegarde État Production — 7 avril 2026, 18:06

## KPI Stats

| Indicateur | Valeur |
|------------|--------|
| Systèmes | 38 |
| Questionnaires | 40 |
| Questionnaires terminés | 12 |
| Questionnaires en cours | 5 |
| Questions totales | 619 |
| Questions répondues | 135 (21%) |
| Questions validées | 0 |
| Flux documentés | 73 |
| Échantillons | 14 |

## Par Phase

| Phase | Questions | Répondues | Progress | Terminés | Total Q. |
|-------|-----------|-----------|----------|----------|----------|
| Phase 1 (Critique) | 332 | 30 | 9% | 1 | 7 |
| Phase 2 (Important) | 150 | 40 | 26% | 4 | 15 |
| Phase 3 (Standard) | 137 | 65 | 47% | 7 | 18 |

## Contexte

- Dernière migration appliquée en prod : `0014_reset_sage_stock_questionnaire`
- Prochaine migration à pousser : `0015_add_division_access`
- PostgreSQL Render : `dpg-d743dghaae7s73bad4og-a`
- App Render : `cartographie-si-airalgerie.onrender.com`
