"""
Data migration: seed the World Tracer baggage irregularity process
created and validated locally, into production.
"""
from django.db import migrations


CONTEXT = """Contexte : Air Algérie utilise World Tracer pour gérer les irrégularités bagages (pertes, retards, objets trouvés). Le système est centralisé : toutes les compagnies interlines peuvent consulter et modifier les mêmes dossiers. La recherche est mondiale.

Flux opérationnel actuel :

1. Déclaration d'irrégularité — Quand un bagage est perdu ou retardé, l'agent d'escale crée un dossier dans World Tracer (rapport AHL ou DPR). Si le système n'est pas utilisé dans l'escale, la réclamation est faite manuellement : par écrit ou par e-mail, sans aucune recherche automatique.

2. Recherche des bagages — World Tracer centralise les dossiers et effectue une recherche mondiale automatique, y compris pour les bagages interlines (multi-compagnies). Les escales doivent enregistrer les OHD (On-Hand bagages, objets en main trouvés) et les AGL (bagages non réclamés à l'arrivée) en volume suffisant pour permettre le matching.

3. Suivi des KPI — Le département Qualité (sous-direction contrôle des escales, contact : Mme Abdoun Zakia) suit les indicateurs de performance à partir des statistiques générées par World Tracer. Le département de Mme Touahria (Recherche) produit des statistiques mais ne gère pas directement les KPI.

4. Indemnisation — Gérée manuellement par le département Recherche et Indemnisation, sans outil dédié. Le DPR est transmis au contentieux qui l'analyse manuellement. Les frais de livraison à l'étranger sont réglés par les délégations ou directions régionales. Il n'existe pas de vision consolidée des coûts totaux (abonnement WT + frais de recherche + indemnisations + frais de livraison + storage). Convention de Varsovie appliquée.

5. Clôture des dossiers — Un fichier clôturé reste 60 jours sur le système. Un fichier ouvert (non clôturé) reste 180 jours + 3 ans d'archivage, générant des frais de stockage et de recherche supplémentaires.

Problèmes identifiés :

- Migration World Tracer natif → World Tracer Desktop incomplète : 12 escales migrées sur l'ensemble du réseau, fin prévue octobre 2026 au plus tard. Formation de 133 personnes restantes à réaliser entre avril et septembre 2026 (pas pendant le Hadj ni la haute saison août).
- Agents polyvalents dans les escales nationales : un même agent gère enregistrement, embarquement, transit, assistance PMR et litiges bagages. Résultat : remplissage partiel des dossiers (champs obligatoires seulement), pas de recherche effectuée dans certaines escales.
- Personnel dédié insuffisant même dans les escales qui en ont.
- Formation non terminée (de 112 à 133 personnes à former). Certaines directions régionales ne répondent pas aux emails.
- Pas de vision globale des coûts liés aux bagages perdus : chaque processus et chaque coût sont gérés séparément.
- Fichiers non clôturés engendrent des frais supplémentaires de storage et de recherche.
- Utilisation de fichiers Excel en parallèle pour pallier les lacunes du système (notamment au département Contentieux).
- Interconnexion World Tracer ↔ ALTEA prévue mais en attente de fin de migration.
- 2000 à 3000 pertes de bagages par mois en haute saison. Majorité due au chargement et au transit.
- Le système pourrait faire 90% du travail si les fichiers AHL et les données OHD étaient correctement remplis au lieu des seuls champs obligatoires."""

MERMAID = """flowchart TD
    subgraph Escale["Escales DOS"]
        A["Déclaration irrégularité<br/>AHL/DPR"]
        C["Enregistrement OHD/AGL"]
        H["Clôture dossiers"]
    end
    
    subgraph WT["World Tracer"]
        B["Recherche automatique<br/>mondiale"]
    end
    
    subgraph Qualité["Département Qualité DOS"]
        D["Suivi KPI<br/>et statistiques"]
    end
    
    subgraph Contentieux["Contentieux DAG"]
        E["Analyse pour<br/>indemnisation"]
    end
    
    subgraph Régional["Délégations"]
        F["Gestion frais<br/>de livraison"]
    end
    
    subgraph Compta["Comptabilité DFC"]
        G["Paiement<br/>indemnisations"]
    end
    
    A --> B
    C --> B
    B --> D
    B --> E
    D --> F
    D --> G
    E --> G
    F --> H
    G --> H
    
    style A fill:#ffcccc
    style C fill:#ffcccc  
    style D fill:#ffcccc
    style E fill:#ffcccc
    style B fill:#cceeff
    style F fill:#ffe6cc
    style G fill:#ffe6cc
    style H fill:#ccffcc"""

PROBLEMS = "Migration World Tracer incomplète (12/toutes escales migrées), formation insuffisante (133 personnes à former), agents polyvalents avec temps limité, remplissage partiel des dossiers (champs obligatoires seulement), enregistrement OHD insuffisant, processus d'indemnisation entièrement manuel, gestion décentralisée des frais, utilisation parallèle d'Excel, interconnexion ALTEA-World Tracer en attente, fichiers non clôturés générant des coûts supplémentaires, absence de vision consolidée des coûts totaux, 2000-3000 pertes/mois en haute saison"

RECOMMENDATIONS = "Accélérer la migration World Tracer Desktop et les formations, dédier du personnel spécialisé bagages dans les escales principales, améliorer la qualité de saisie des données OHD/AGL, développer un outil dédié pour l'indemnisation, centraliser la gestion des coûts, mettre en place des tableaux de bord consolidés, automatiser l'interconnexion avec ALTEA, optimiser la clôture des dossiers, établir des procédures standardisées"

STEPS = [
    {
        "order": 1, "title": "Déclaration d'irrégularité bagage", "step_type": "INPUT",
        "description": "L'agent d'escale crée un dossier dans World Tracer (rapport AHL pour bagages perdus ou DPR pour retards) lorsqu'un passager signale un problème de bagage. Si World Tracer n'est pas disponible, la déclaration se fait manuellement par écrit ou email.",
        "actor_role": "Agent d'escale", "actor_structure_code": "DOS",
        "data_inputs": "Informations passager, détails du bagage, numéro de vol",
        "data_outputs": "Dossier AHL ou DPR créé",
        "interactions": "Homme→système (World Tracer) ou homme→papier",
        "problems": "Escales non migrées vers World Tracer Desktop, remplissage partiel des dossiers (champs obligatoires uniquement), pas de recherche effectuée dans certaines escales",
        "duration_estimate": "10-15 minutes", "next_steps": [2],
    },
    {
        "order": 2, "title": "Recherche automatique mondiale", "step_type": "AUTOMATED",
        "description": "World Tracer effectue une recherche automatique mondiale des bagages en croisant les dossiers d'irrégularités avec les OHD (objets trouvés) et AGL (bagages non réclamés) enregistrés par toutes les compagnies du réseau interlines.",
        "actor_role": "Système World Tracer", "actor_structure_code": "",
        "data_inputs": "Dossiers AHL/DPR, base OHD/AGL mondiale",
        "data_outputs": "Résultats de matching, propositions de correspondances",
        "interactions": "Système→système (recherche automatique)",
        "problems": "Données OHD insuffisamment renseignées, qualité des données limitée par le remplissage partiel",
        "duration_estimate": "Temps réel", "next_steps": [3, 4],
    },
    {
        "order": 3, "title": "Enregistrement des OHD et AGL", "step_type": "MANUAL",
        "description": "Les escales doivent enregistrer dans World Tracer tous les bagages trouvés (OHD - On-Hand) et les bagages non réclamés à l'arrivée (AGL) pour alimenter la base de données de recherche.",
        "actor_role": "Agent d'escale", "actor_structure_code": "DOS",
        "data_inputs": "Bagages physiques trouvés ou non réclamés",
        "data_outputs": "Fiches OHD/AGL dans World Tracer",
        "interactions": "Homme→système",
        "problems": "Volume insuffisant d'enregistrement OHD, personnel polyvalent avec peu de temps dédié",
        "duration_estimate": "5-10 minutes par bagage", "next_steps": [2],
    },
    {
        "order": 4, "title": "Suivi des KPI qualité", "step_type": "MANUAL",
        "description": "Le département Qualité (sous-direction contrôle des escales) suit les indicateurs de performance à partir des statistiques générées par World Tracer pour mesurer l'efficacité du processus.",
        "actor_role": "Responsable Qualité", "actor_structure_code": "DOS",
        "data_inputs": "Statistiques World Tracer",
        "data_outputs": "Tableaux de bord KPI, rapports qualité",
        "interactions": "Homme→système→fichiers Excel",
        "problems": "Utilisation de fichiers Excel en parallèle, pas de vision consolidée des coûts totaux",
        "duration_estimate": "Quotidien/hebdomadaire", "next_steps": [5, 6],
    },
    {
        "order": 5, "title": "Analyse pour indemnisation", "step_type": "MANUAL",
        "description": "Le département Contentieux analyse manuellement les dossiers DPR transmis pour déterminer les indemnisations selon la Convention de Varsovie. Aucun outil dédié n'est utilisé.",
        "actor_role": "Agent contentieux", "actor_structure_code": "DAG",
        "data_inputs": "Dossiers DPR, réclamations passagers",
        "data_outputs": "Décisions d'indemnisation",
        "interactions": "Homme→fichiers Excel",
        "problems": "Processus entièrement manuel, pas d'outil dédié, pas de vision consolidée des coûts",
        "duration_estimate": "30-60 minutes par dossier", "next_steps": [7],
    },
    {
        "order": 6, "title": "Gestion des frais de livraison", "step_type": "MANUAL",
        "description": "Les frais de livraison à l'étranger sont réglés par les délégations ou directions régionales de manière décentralisée, sans coordination centrale.",
        "actor_role": "Délégations régionales", "actor_structure_code": "",
        "data_inputs": "Demandes de livraison, factures transporteurs",
        "data_outputs": "Paiements frais de livraison",
        "interactions": "Homme→systèmes comptables locaux",
        "problems": "Gestion décentralisée, pas de vision consolidée des coûts de livraison",
        "duration_estimate": "Variable", "next_steps": [8],
    },
    {
        "order": 7, "title": "Paiement des indemnisations", "step_type": "MANUAL",
        "description": "Traitement des paiements d'indemnisation aux passagers selon les décisions du contentieux, en application de la Convention de Varsovie.",
        "actor_role": "Service comptabilité", "actor_structure_code": "DFC",
        "data_inputs": "Décisions d'indemnisation validées",
        "data_outputs": "Paiements aux passagers",
        "interactions": "Homme→systèmes de paiement",
        "problems": "Processus manuel, suivi des coûts non centralisé",
        "duration_estimate": "Variable", "next_steps": [8],
    },
    {
        "order": 8, "title": "Clôture des dossiers", "step_type": "MANUAL",
        "description": "Les dossiers sont clôturés une fois le bagage retrouvé et livré, ou après indemnisation. Un dossier clôturé reste 60 jours sur le système, un dossier non clôturé reste 180 jours + 3 ans d'archivage.",
        "actor_role": "Agent d'escale ou département Recherche", "actor_structure_code": "DOS",
        "data_inputs": "Confirmation livraison ou indemnisation",
        "data_outputs": "Dossier clôturé dans World Tracer",
        "interactions": "Homme→système",
        "problems": "Fichiers non clôturés génèrent des frais supplémentaires de storage et recherche",
        "duration_estimate": "5 minutes", "next_steps": [],
    },
]


def seed_process(apps, schema_editor):
    Process = apps.get_model('cartography', 'Process')
    ProcessStep = apps.get_model('cartography', 'ProcessStep')
    Structure = apps.get_model('cartography', 'Structure')
    System = apps.get_model('cartography', 'System')

    if Process.objects.filter(code='PROC-WT-001').exists():
        return

    p = Process.objects.create(
        code='PROC-WT-001',
        name='Gestion des irrégularités bagages (perte, retard, OHD)',
        description="Process de bout en bout de la gestion des bagages irréguliers : déclaration d'irrégularité à l'escale, recherche via World Tracer, suivi OHD/AGL, indemnisation, et clôture des dossiers. Implique les escales, le département Recherche & Indemnisation, le département Qualité, et les délégations à l'étranger.",
        context=CONTEXT,
        category='OPERATIONAL',
        status='VALIDATED',
        problems=PROBLEMS,
        recommendations=RECOMMENDATIONS,
        workflow_mermaid=MERMAID,
        workflow_json=STEPS,
        ai_generated=True,
        created_by='admin',
    )

    # Link structures
    for code in ['DAG', 'DFC', 'DOS', 'DSI', 'DVR']:
        try:
            p.structures.add(Structure.objects.get(code=code))
        except Structure.DoesNotExist:
            pass

    # Link systems
    for code in ['ALTEA', 'WORLDTRACER']:
        try:
            p.systems.add(System.objects.get(code=code))
        except System.DoesNotExist:
            pass

    # Create steps
    for sd in STEPS:
        step = ProcessStep.objects.create(
            process=p,
            order=sd['order'],
            title=sd['title'],
            description=sd['description'],
            step_type=sd['step_type'],
            actor_role=sd['actor_role'],
            data_inputs=sd['data_inputs'],
            data_outputs=sd['data_outputs'],
            interactions=sd['interactions'],
            problems=sd['problems'],
            duration_estimate=sd['duration_estimate'],
            next_steps=sd['next_steps'],
        )
        if sd['actor_structure_code']:
            try:
                step.actor_structure = Structure.objects.get(code=sd['actor_structure_code'])
                step.save()
            except Structure.DoesNotExist:
                pass


def reverse_seed(apps, schema_editor):
    Process = apps.get_model('cartography', 'Process')
    Process.objects.filter(code='PROC-WT-001').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('cartography', '0019_add_process_models'),
    ]
    operations = [
        migrations.RunPython(seed_process, reverse_seed),
    ]
