from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q, Avg
from django.contrib import messages
from django.template.loader import render_to_string
from datetime import datetime
import markdown
from .models import (
    Structure, SystemCategory, System, DataFlow, 
    DataField, MessageFormat, MessageField, DataDomain,
    DataSample, FlowFieldHypothesis, FlowValidation,
    ReferenceData, FlowReferential, DataImportHistory, COUNTRY_CHOICES,
    Questionnaire, QuestionSection, Question
)


def dashboard(request):
    """Dashboard principal avec statistiques"""
    context = {
        'total_systems': System.objects.count(),
        'total_flows': DataFlow.objects.count(),
        'total_structures': Structure.objects.count(),
        'critical_systems': System.objects.filter(criticality='CRITIQUE').count(),
        'manual_flows': DataFlow.objects.filter(is_automated=False).count(),
        'categories': SystemCategory.objects.annotate(system_count=Count('systems')),
        'structures': Structure.objects.annotate(system_count=Count('systems')),
        'recent_systems': System.objects.select_related('category', 'structure')[:10],
        'critical_flows': DataFlow.objects.filter(is_critical=True).select_related('source', 'target')[:5],
    }
    return render(request, 'cartography/dashboard.html', context)


def systems_list(request):
    """Liste des systèmes avec filtres"""
    systems = System.objects.select_related('category', 'structure').all()
    
    category = request.GET.get('category')
    structure = request.GET.get('structure')
    criticality = request.GET.get('criticality')
    country = request.GET.get('country')
    search = request.GET.get('search')
    
    if category:
        systems = systems.filter(category_id=category)
    if structure:
        systems = systems.filter(structure_id=structure)
    if criticality:
        systems = systems.filter(criticality=criticality)
    if country:
        if country == 'foreign':
            systems = systems.exclude(country='DZ')
        else:
            systems = systems.filter(country=country)
    if search:
        systems = systems.filter(
            Q(name__icontains=search) | 
            Q(code__icontains=search) | 
            Q(vendor__icontains=search)
        )
    
    context = {
        'systems': systems,
        'categories': SystemCategory.objects.all(),
        'structures': Structure.objects.all(),
        'criticalities': System.CRITICALITY_CHOICES,
        'countries': COUNTRY_CHOICES,
        'selected_category': category,
        'selected_structure': structure,
        'selected_criticality': criticality,
        'selected_country': country,
        'search': search or '',
    }
    return render(request, 'cartography/systems_list.html', context)


def system_detail(request, pk):
    """Détail d'un système avec ses flux"""
    system = get_object_or_404(System.objects.select_related('category', 'structure'), pk=pk)
    
    incoming_flows = DataFlow.objects.filter(target=system).select_related('source').prefetch_related('fields')
    outgoing_flows = DataFlow.objects.filter(source=system).select_related('target').prefetch_related('fields')
    
    context = {
        'system': system,
        'incoming_flows': incoming_flows,
        'outgoing_flows': outgoing_flows,
        'mastered_domains': system.mastered_domains.all(),
        'consumed_domains': system.consumed_domains.all(),
    }
    return render(request, 'cartography/system_detail.html', context)


def flows_list(request):
    """Liste des flux de données"""
    flows = DataFlow.objects.select_related('source', 'target').all()
    
    source = request.GET.get('source')
    target = request.GET.get('target')
    frequency = request.GET.get('frequency')
    automated = request.GET.get('automated')
    
    if source:
        flows = flows.filter(source_id=source)
    if target:
        flows = flows.filter(target_id=target)
    if frequency:
        flows = flows.filter(frequency=frequency)
    if automated:
        flows = flows.filter(is_automated=(automated == 'true'))
    
    context = {
        'flows': flows,
        'systems': System.objects.all(),
        'frequencies': DataFlow.FREQUENCY_CHOICES,
        'selected_source': source,
        'selected_target': target,
        'selected_frequency': frequency,
        'selected_automated': automated,
    }
    return render(request, 'cartography/flows_list.html', context)


def flow_detail(request, pk):
    """Détail d'un flux avec ses champs"""
    flow = get_object_or_404(
        DataFlow.objects.select_related('source', 'target').prefetch_related('fields'),
        pk=pk
    )
    
    context = {
        'flow': flow,
        'fields': flow.fields.all(),
    }
    return render(request, 'cartography/flow_detail.html', context)


def graph_view(request):
    """Vue graphique interactive de la cartographie"""
    categories = SystemCategory.objects.all()
    structures = Structure.objects.all()
    
    context = {
        'categories': categories,
        'structures': structures,
    }
    return render(request, 'cartography/graph.html', context)


def structures_list(request):
    """Liste des structures organisationnelles"""
    structures = Structure.objects.annotate(
        system_count=Count('systems')
    ).prefetch_related('systems')
    
    context = {
        'structures': structures,
    }
    return render(request, 'cartography/structures_list.html', context)


def messages_list(request):
    """Liste des formats de messages standards"""
    messages = MessageFormat.objects.prefetch_related('fields').all()
    
    context = {
        'messages': messages,
    }
    return render(request, 'cartography/messages_list.html', context)


def message_detail(request, pk):
    """Détail d'un format de message"""
    message = get_object_or_404(MessageFormat.objects.prefetch_related('fields'), pk=pk)
    
    context = {
        'message': message,
        'fields': message.fields.all(),
    }
    return render(request, 'cartography/message_detail.html', context)


def domains_list(request):
    """Liste des domaines de données avec système maître"""
    domains = DataDomain.objects.select_related('master_system').prefetch_related('consumer_systems')
    
    context = {
        'domains': domains,
    }
    return render(request, 'cartography/domains_list.html', context)


# API Views
def api_graph_data(request):
    """API pour les données du graphe avec structures comme groupes"""
    category_filter = request.GET.get('category')
    structure_filter = request.GET.get('structure')
    show_structures = request.GET.get('show_structures', 'true') == 'true'
    
    systems = System.objects.select_related('category', 'structure')
    structures = Structure.objects.annotate(system_count=Count('systems'))
    
    if category_filter:
        systems = systems.filter(category_id=category_filter)
    if structure_filter:
        systems = systems.filter(structure_id=structure_filter)
        structures = structures.filter(id=structure_filter)
    
    system_ids = list(systems.values_list('id', flat=True))
    
    flows = DataFlow.objects.filter(
        Q(source_id__in=system_ids) | Q(target_id__in=system_ids)
    ).select_related('source', 'target')
    
    # Build nodes
    nodes = []
    
    # Add structure nodes (parent nodes)
    if show_structures:
        structure_ids_with_systems = set(systems.values_list('structure_id', flat=True))
        for structure in structures:
            if structure.id in structure_ids_with_systems:
                nodes.append({
                    'id': f'struct_{structure.id}',
                    'label': structure.code,
                    'name': structure.name,
                    'type': 'structure',
                    'color': structure.color,
                    'system_count': structure.system_count,
                    'description': structure.description,
                })
    
    # Add system nodes
    for system in systems:
        node = {
            'id': f'sys_{system.id}',
            'label': system.code,
            'name': system.name,
            'type': 'system',
            'category': system.category.name,
            'category_id': system.category.id,
            'category_color': system.category.color,
            'structure': system.structure.code,
            'structure_id': system.structure.id,
            'parent': f'struct_{system.structure.id}' if show_structures else None,
            'criticality': system.criticality,
            'color': system.criticality_color,
            'vendor': system.vendor,
            'mode': system.get_mode_display(),
        }
        nodes.append(node)
    
    # Build edges
    edges = []
    for flow in flows:
        if flow.source_id in system_ids and flow.target_id in system_ids:
            edges.append({
                'id': f'flow_{flow.id}',
                'source': f'sys_{flow.source_id}',
                'target': f'sys_{flow.target_id}',
                'label': flow.name,
                'frequency': flow.get_frequency_display(),
                'protocol': flow.get_protocol_display(),
                'is_automated': flow.is_automated,
                'is_critical': flow.is_critical,
                'format': flow.format,
            })
    
    return JsonResponse({
        'nodes': nodes,
        'edges': edges,
    })


def api_system_detail(request, pk):
    """API pour le détail d'un système"""
    system = get_object_or_404(System.objects.select_related('category', 'structure'), pk=pk)
    
    incoming = DataFlow.objects.filter(target=system).select_related('source')
    outgoing = DataFlow.objects.filter(source=system).select_related('target')
    
    return JsonResponse({
        'id': system.id,
        'code': system.code,
        'name': system.name,
        'description': system.description,
        'vendor': system.vendor,
        'category': system.category.name,
        'structure': system.structure.code,
        'structure_name': system.structure.name,
        'criticality': system.criticality,
        'mode': system.get_mode_display(),
        'is_master_for': system.is_master_for,
        'modules': system.modules,
        'incoming_flows': [
            {'id': f.id, 'name': f.name, 'source': f.source.code}
            for f in incoming
        ],
        'outgoing_flows': [
            {'id': f.id, 'name': f.name, 'target': f.target.code}
            for f in outgoing
        ],
    })


def api_flow_detail(request, pk):
    """API pour le détail d'un flux"""
    flow = get_object_or_404(
        DataFlow.objects.select_related('source', 'target').prefetch_related('fields'),
        pk=pk
    )
    
    return JsonResponse({
        'id': flow.id,
        'name': flow.name,
        'description': flow.description,
        'source': {'id': flow.source.id, 'code': flow.source.code, 'name': flow.source.name},
        'target': {'id': flow.target.id, 'code': flow.target.code, 'name': flow.target.name},
        'frequency': flow.get_frequency_display(),
        'protocol': flow.get_protocol_display(),
        'format': flow.format,
        'is_automated': flow.is_automated,
        'is_critical': flow.is_critical,
        'volume': flow.volume,
        'fields': [
            {
                'name': f.name,
                'type': f.get_field_type_display(),
                'length': f.length,
                'description': f.description,
                'mandatory': f.is_mandatory,
                'example': f.example,
            }
            for f in flow.fields.all()
        ],
    })


# ============================================
# VALIDATION - Hypothèse vs Réalité
# ============================================

def validation_dashboard(request):
    """Dashboard de validation des données - comparaison hypothèse vs réalité"""
    samples = DataSample.objects.all()[:10]
    
    # Statistiques de validation
    total_hypotheses = FlowFieldHypothesis.objects.count()
    confirmed = FlowFieldHypothesis.objects.filter(status='CONFIRMED').count()
    partial = FlowFieldHypothesis.objects.filter(status='PARTIAL').count()
    incorrect = FlowFieldHypothesis.objects.filter(status='INCORRECT').count()
    pending = FlowFieldHypothesis.objects.filter(status='HYPOTHESIS').count()
    
    # Flux avec le plus de divergences
    flows_with_issues = DataFlow.objects.annotate(
        issues_count=Count('field_hypotheses', filter=Q(field_hypotheses__status='INCORRECT'))
    ).filter(issues_count__gt=0).order_by('-issues_count')[:10]
    
    # Dernières validations
    recent_validations = FlowValidation.objects.select_related('flow', 'sample')[:10]
    
    context = {
        'samples': samples,
        'total_hypotheses': total_hypotheses,
        'confirmed': confirmed,
        'partial': partial,
        'incorrect': incorrect,
        'pending': pending,
        'flows_with_issues': flows_with_issues,
        'recent_validations': recent_validations,
    }
    return render(request, 'cartography/validation_dashboard.html', context)


def samples_list(request):
    """Liste des échantillons de données importés"""
    samples = DataSample.objects.all()
    
    source_filter = request.GET.get('source')
    data_type_filter = request.GET.get('data_type')
    
    if source_filter:
        samples = samples.filter(source_system=source_filter)
    if data_type_filter:
        samples = samples.filter(data_type=data_type_filter)
    
    context = {
        'samples': samples,
        'source_choices': DataSample.SOURCE_SYSTEM_CHOICES,
        'data_type_choices': DataSample.DATA_TYPE_CHOICES,
        'selected_source': source_filter,
        'selected_data_type': data_type_filter,
    }
    return render(request, 'cartography/samples_list.html', context)


def sample_detail(request, pk):
    """Détail d'un échantillon avec ses validations"""
    sample = get_object_or_404(DataSample, pk=pk)
    validations = sample.flow_validations.select_related('flow')
    
    # Préparer les colonnes avec stats
    columns = sample.columns_json or []
    column_stats = sample.column_stats_json or {}
    sample_rows = sample.sample_rows_json or []
    
    columns_with_stats = []
    for col in columns:
        stats = column_stats.get(col, {})
        examples = stats.get('examples', [])
        columns_with_stats.append({
            'name': col,
            'type': stats.get('type', 'STRING'),
            'unique_count': stats.get('unique_count', 0),
            'non_null_count': stats.get('non_null_count', 0),
            'example': examples[0] if examples else '',
        })
    
    # Identifier les colonnes clés (celles qui semblent importantes)
    key_patterns = ['document', 'carrier', 'flight', 'pax', 'passenger', 'amount', 
                    'date', 'currency', 'status', 'type', 'code', 'number', 'id']
    key_columns = []
    for col in columns[:30]:  # Limiter à 30
        col_lower = col.lower()
        for pattern in key_patterns:
            if pattern in col_lower:
                key_columns.append(col)
                break
        if len(key_columns) >= 10:
            break
    
    # Définir les tables attendues par système pour valider les flux
    expected_data_map = {
        'AMADEUS': {
            'flows': [
                {'name': 'Réservations PNR', 'source': 'ALTEA', 'target': 'Systèmes internes', 'status': 'pending'},
                {'name': 'Paiements APS', 'source': 'ALTEA', 'target': 'Finance', 'status': 'received' if sample.data_type == 'APS' else 'pending'},
                {'name': 'DCS Embarquement', 'source': 'DCS', 'target': 'Opérations', 'status': 'pending'},
            ],
            'expected_tables': [
                {'name': 'PNR Data Feed', 'code': 'PNR', 'description': 'Données de réservation passagers', 'received': False},
                {'name': 'APS Payment', 'code': 'APS', 'description': 'Transactions de paiement CB', 'received': sample.data_type == 'APS'},
                {'name': 'DCS Check-in', 'code': 'DCS', 'description': 'Données d\'enregistrement', 'received': False},
                {'name': 'Inventory', 'code': 'INV', 'description': 'Disponibilité sièges', 'received': False},
                {'name': 'LIFT File', 'code': 'LIFT', 'description': 'Passagers embarqués', 'received': False},
            ]
        },
        'RAPID': {
            'flows': [
                {'name': 'Recettes BSP', 'source': 'ACCELYA', 'target': 'Finance/ERP', 'status': 'received' if sample.data_type == 'SLP' else 'pending'},
                {'name': 'Transport Passagers', 'source': 'ACCELYA', 'target': 'Revenue Accounting', 'status': 'received' if sample.data_type == 'FLP' else 'pending'},
                {'name': 'Facturation Interline', 'source': 'ACCELYA', 'target': 'Partenaires', 'status': 'received' if sample.data_type == 'IBP' else 'pending'},
            ],
            'expected_tables': [
                {'name': 'SLP Sales Ledger', 'code': 'SLP', 'description': 'Rapport ventes BSP', 'received': sample.data_type == 'SLP'},
                {'name': 'FLP Transport', 'code': 'FLP', 'description': 'Coupons de vol passagers', 'received': sample.data_type == 'FLP'},
                {'name': 'IBP Interline', 'code': 'IBP', 'description': 'Facturation intercompagnies', 'received': sample.data_type == 'IBP'},
                {'name': 'Refund Report', 'code': 'RFD', 'description': 'Remboursements', 'received': False},
                {'name': 'ADM/ACM', 'code': 'ADM', 'description': 'Ajustements agents', 'received': False},
            ]
        },
        'AIMS': {
            'flows': [
                {'name': 'Programme de Vol', 'source': 'AIMS', 'target': 'ALTEA/PSS', 'status': 'pending'},
                {'name': 'Planning Équipages', 'source': 'AIMS', 'target': 'Crew Management', 'status': 'pending'},
                {'name': 'Messages OOOI', 'source': 'AIMS', 'target': 'Opérations', 'status': 'pending'},
            ],
            'expected_tables': [
                {'name': 'FLT Schedule', 'code': 'FLT', 'description': 'Programme de vol journalier', 'received': sample.data_type == 'FLT'},
                {'name': 'Crew Roster', 'code': 'CREW', 'description': 'Planning équipages', 'received': False},
                {'name': 'SSIM Schedule', 'code': 'SSIM', 'description': 'Horaires saison IATA', 'received': False},
                {'name': 'MVT Messages', 'code': 'MVT', 'description': 'Mouvements avions', 'received': False},
            ]
        },
    }
    
    # Récupérer les infos pour ce système
    system_data = expected_data_map.get(sample.source_system, {'flows': [], 'expected_tables': []})
    
    # Récupérer TOUS les échantillons reçus pour ce système (pas juste celui-ci)
    all_samples_for_system = DataSample.objects.filter(source_system=sample.source_system)
    received_data_types = set(s.data_type for s in all_samples_for_system)
    
    # Mettre à jour le statut des tables en fonction de tous les échantillons reçus
    for table in system_data['expected_tables']:
        table['received'] = table['code'] in received_data_types
    
    # Mettre à jour le statut des flux
    for flow in system_data['flows']:
        # Déterminer si le flux est validable basé sur les tables reçues
        if sample.source_system == 'RAPID':
            if 'BSP' in flow['name'] or 'Recettes' in flow['name']:
                flow['status'] = 'received' if 'SLP' in received_data_types else 'pending'
            elif 'Transport' in flow['name']:
                flow['status'] = 'received' if 'FLP' in received_data_types else 'pending'
            elif 'Interline' in flow['name']:
                flow['status'] = 'received' if 'IBP' in received_data_types else 'pending'
        elif sample.source_system == 'AMADEUS':
            if 'APS' in flow['name'] or 'Paiement' in flow['name']:
                flow['status'] = 'received' if 'APS' in received_data_types else 'pending'
            elif 'PNR' in flow['name'] or 'Réservation' in flow['name']:
                flow['status'] = 'received' if 'PNR' in received_data_types else 'pending'
        elif sample.source_system == 'AIMS':
            if 'Programme' in flow['name'] or 'Vol' in flow['name']:
                flow['status'] = 'received' if 'FLT' in received_data_types else 'pending'
    
    # Calculer les stats de complétion
    tables_received = sum(1 for t in system_data['expected_tables'] if t['received'])
    tables_total = len(system_data['expected_tables'])
    completion_pct = int((tables_received / tables_total * 100)) if tables_total > 0 else 0
    
    context = {
        'sample': sample,
        'validations': validations,
        'columns': columns,
        'columns_with_stats': columns_with_stats[:50],
        'sample_rows': sample_rows[:5],
        'key_columns': key_columns,
        'expected_flows': system_data['flows'],
        'expected_tables': system_data['expected_tables'],
        'tables_received': tables_received,
        'tables_total': tables_total,
        'completion_pct': completion_pct,
        'received_data_types': list(received_data_types),
    }
    return render(request, 'cartography/sample_detail.html', context)


def flow_validation_view(request, flow_pk):
    """Vue de validation d'un flux - comparaison hypothèse vs réalité"""
    flow = get_object_or_404(DataFlow.objects.select_related('source', 'target'), pk=flow_pk)
    hypotheses = flow.field_hypotheses.all()
    validations = flow.validations.select_related('sample')
    
    # Statistiques
    total = hypotheses.count()
    confirmed = hypotheses.filter(status='CONFIRMED').count()
    issues = hypotheses.filter(status='INCORRECT').count()
    
    context = {
        'flow': flow,
        'hypotheses': hypotheses,
        'validations': validations,
        'total_fields': total,
        'confirmed_fields': confirmed,
        'issues_fields': issues,
        'match_rate': int((confirmed / total * 100)) if total > 0 else 0,
    }
    return render(request, 'cartography/flow_validation.html', context)


def api_validation_stats(request):
    """API pour les stats de validation sur le graphe"""
    flows_data = []
    
    for flow in DataFlow.objects.prefetch_related('field_hypotheses', 'validations'):
        hypotheses = flow.field_hypotheses.all()
        total = hypotheses.count()
        confirmed = hypotheses.filter(status='CONFIRMED').count()
        incorrect = hypotheses.filter(status='INCORRECT').count()
        
        if total > 0:
            match_rate = int((confirmed / total) * 100)
        else:
            match_rate = None  # Pas encore validé
        
        latest_validation = flow.validations.first()
        
        flows_data.append({
            'flow_id': flow.id,
            'total_fields': total,
            'confirmed': confirmed,
            'incorrect': incorrect,
            'match_rate': match_rate,
            'validation_status': latest_validation.status if latest_validation else 'NOT_VALIDATED',
        })
    
    return JsonResponse({'flows': flows_data})


def data_discovery_view(request):
    """Vue synthèse des données découvertes dans les échantillons"""
    samples = DataSample.objects.all().order_by('source_system', 'data_type')
    
    # Grouper par système source
    systems_data = {}
    for sample in samples:
        system = sample.source_system
        if system not in systems_data:
            systems_data[system] = {
                'samples': [],
                'total_files': 0,
                'data_types': set(),
                'total_columns': 0,
            }
        systems_data[system]['samples'].append(sample)
        systems_data[system]['total_files'] += 1
        systems_data[system]['data_types'].add(sample.data_type)
        if sample.columns_json:
            systems_data[system]['total_columns'] += len(sample.columns_json)
    
    # Convertir sets en listes pour le template
    for system in systems_data:
        systems_data[system]['data_types'] = list(systems_data[system]['data_types'])
    
    # Statistiques globales
    total_samples = samples.count()
    total_columns = sum(len(s.columns_json or []) for s in samples)
    systems_count = len(systems_data)
    
    # Types de données par fréquence
    data_types_count = {}
    for sample in samples:
        dt = sample.get_data_type_display()
        data_types_count[dt] = data_types_count.get(dt, 0) + 1
    
    context = {
        'samples': samples,
        'systems_data': systems_data,
        'total_samples': total_samples,
        'total_columns': total_columns,
        'systems_count': systems_count,
        'data_types_count': data_types_count,
    }
    return render(request, 'cartography/data_discovery.html', context)


def referentials_list(request):
    """Liste des référentiels de données"""
    referentials = ReferenceData.objects.select_related('master_system').annotate(
        flows_count=Count('used_in_flows')
    )
    
    ref_type = request.GET.get('type')
    standard = request.GET.get('standard')
    
    if ref_type:
        referentials = referentials.filter(referential_type=ref_type)
    if standard:
        referentials = referentials.filter(standard__icontains=standard)
    
    context = {
        'referentials': referentials,
        'type_choices': ReferenceData.REFERENTIAL_TYPE_CHOICES,
        'selected_type': ref_type,
        'selected_standard': standard,
    }
    return render(request, 'cartography/referentials_list.html', context)


def referential_detail(request, pk):
    """Détail d'un référentiel avec ses flux associés"""
    referential = get_object_or_404(ReferenceData.objects.select_related('master_system'), pk=pk)
    flow_refs = referential.used_in_flows.select_related('flow__source', 'flow__target')
    
    # Identifier tous les systèmes qui utilisent potentiellement ce référentiel
    # 1. Systèmes liés via les flux (source ou target)
    systems_from_flows = set()
    for ref in flow_refs:
        systems_from_flows.add(ref.flow.source)
        systems_from_flows.add(ref.flow.target)
    
    # 2. Identifier les systèmes potentiels basés sur le type de référentiel
    potential_systems = System.objects.select_related('category', 'structure').all()
    
    # Mapping référentiel -> catégories de systèmes susceptibles de l'utiliser
    ref_to_categories = {
        'IATA_AIRLINE': [1, 2],  # Core Business, Distribution
        'IATA_AIRPORT': [1, 2],  # Core Business, Distribution
        'IATA_AIRCRAFT': [1, 6],  # Core Business, Qualité & Opérations
        'CURRENCY': [1, 2, 3],  # Core Business, Distribution, Finance
        'COUNTRY': [1, 2, 3],  # Core Business, Distribution, Finance
        'CLASS_OF_SERVICE': [1, 2],  # Core Business, Distribution
        'PAYMENT_TYPE': [1, 2, 3],  # Core Business, Distribution, Finance
        'TICKET_STATUS': [1, 2, 3],  # Core Business, Distribution, Finance
        'PNR_STATUS': [1, 2],  # Core Business, Distribution
        'CREW_RANK': [1, 4],  # Core Business, RH
        'FLIGHT_STATUS': [1, 6],  # Core Business, Qualité & Opérations
        'MSG_TYPE_IATA': [1, 6],  # Core Business, Qualité & Opérations
    }
    
    category_ids = ref_to_categories.get(referential.code, [1, 2, 3])
    potential_systems = potential_systems.filter(category_id__in=category_ids)
    
    # Marquer les systèmes confirmés (via flux) vs potentiels
    systems_usage = []
    confirmed_ids = {s.id for s in systems_from_flows}
    
    for system in potential_systems:
        systems_usage.append({
            'system': system,
            'confirmed': system.id in confirmed_ids,
            'via_flows': [ref for ref in flow_refs if ref.flow.source_id == system.id or ref.flow.target_id == system.id]
        })
    
    # Trier: confirmés en premier
    systems_usage.sort(key=lambda x: (not x['confirmed'], x['system'].name))
    
    context = {
        'referential': referential,
        'flow_refs': flow_refs,
        'systems_usage': systems_usage,
        'confirmed_count': len(confirmed_ids),
        'potential_count': len(systems_usage) - len(confirmed_ids),
    }
    return render(request, 'cartography/referential_detail.html', context)


def data_gaps_report(request):
    """Rapport des éléments manquants dans les échantillons de données pour les flux"""
    # Récupérer tous les flux avec leurs référentiels et échantillons
    flows = DataFlow.objects.select_related('source', 'target').prefetch_related(
        'referentials__reference_data',
        'field_hypotheses',
        'validations__sample'
    )
    
    # Filtres
    source_filter = request.GET.get('source')
    target_filter = request.GET.get('target')
    status_filter = request.GET.get('status')
    selected_flows = request.GET.getlist('flows')
    
    if source_filter:
        flows = flows.filter(source_id=source_filter)
    if target_filter:
        flows = flows.filter(target_id=target_filter)
    if selected_flows:
        flows = flows.filter(id__in=selected_flows)
    
    # Analyser chaque flux pour les éléments manquants
    flows_analysis = []
    total_missing_refs = 0
    total_missing_samples = 0
    total_missing_fields = 0
    
    for flow in flows:
        # Référentiels manquants
        refs = flow.referentials.all()
        missing_refs = [r for r in refs if not r.is_present_in_sample]
        present_refs = [r for r in refs if r.is_present_in_sample]
        
        # Champs hypothèses non validés
        hypotheses = flow.field_hypotheses.all()
        pending_hypotheses = [h for h in hypotheses if h.status == 'HYPOTHESIS']
        incorrect_hypotheses = [h for h in hypotheses if h.status == 'INCORRECT']
        
        # Validations
        validations = flow.validations.all()
        has_sample = validations.exists()
        
        # Calcul du score de complétude
        total_items = len(refs) + len(hypotheses)
        complete_items = len(present_refs) + len([h for h in hypotheses if h.status == 'CONFIRMED'])
        completeness = int((complete_items / total_items * 100)) if total_items > 0 else 0
        
        # Déterminer le statut global
        if not has_sample:
            status = 'NO_SAMPLE'
        elif len(missing_refs) > 0 or len(incorrect_hypotheses) > 0:
            status = 'ISSUES'
        elif len(pending_hypotheses) > 0:
            status = 'PARTIAL'
        elif completeness == 100:
            status = 'COMPLETE'
        else:
            status = 'PENDING'
        
        # Appliquer le filtre de statut
        if status_filter and status != status_filter:
            continue
        
        total_missing_refs += len(missing_refs)
        total_missing_samples += (0 if has_sample else 1)
        total_missing_fields += len(pending_hypotheses) + len(incorrect_hypotheses)
        
        flows_analysis.append({
            'flow': flow,
            'missing_refs': missing_refs,
            'present_refs': present_refs,
            'pending_hypotheses': pending_hypotheses,
            'incorrect_hypotheses': incorrect_hypotheses,
            'has_sample': has_sample,
            'validations': validations,
            'completeness': completeness,
            'status': status,
        })
    
    # Trier par complétude (les moins complets en premier)
    flows_analysis.sort(key=lambda x: x['completeness'])
    
    # Statistiques globales
    total_flows = len(flows_analysis)
    complete_flows = len([f for f in flows_analysis if f['status'] == 'COMPLETE'])
    partial_flows = len([f for f in flows_analysis if f['status'] == 'PARTIAL'])
    issues_flows = len([f for f in flows_analysis if f['status'] == 'ISSUES'])
    no_sample_flows = len([f for f in flows_analysis if f['status'] == 'NO_SAMPLE'])
    
    context = {
        'flows_analysis': flows_analysis,
        'systems': System.objects.all(),
        'all_flows': DataFlow.objects.all(),
        'selected_source': source_filter,
        'selected_target': target_filter,
        'selected_status': status_filter,
        'selected_flows': selected_flows,
        'total_flows': total_flows,
        'complete_flows': complete_flows,
        'partial_flows': partial_flows,
        'issues_flows': issues_flows,
        'no_sample_flows': no_sample_flows,
        'total_missing_refs': total_missing_refs,
        'total_missing_samples': total_missing_samples,
        'total_missing_fields': total_missing_fields,
        'status_choices': [
            ('NO_SAMPLE', 'Sans échantillon'),
            ('ISSUES', 'Problèmes détectés'),
            ('PARTIAL', 'Partiellement validé'),
            ('COMPLETE', 'Complet'),
            ('PENDING', 'En attente'),
        ],
    }
    return render(request, 'cartography/data_gaps_report.html', context)


def database_schema_view(request):
    """Vue du schéma de base de données - Systèmes Air Algérie réels"""
    
    # Récupérer les vrais systèmes Air Algérie
    systems = System.objects.select_related('category', 'structure').all()
    flows = DataFlow.objects.select_related('source', 'target').all()
    
    tables = []
    relations = []
    
    # Créer les "tables" pour chaque système réel
    for system in systems:
        mastered_domains = list(system.mastered_domains.values_list('name', flat=True))
        
        fields = []
        fields.append({
            'name': 'id',
            'type': 'PK',
            'is_pk': True,
            'is_fk': False,
            'is_nullable': False,
        })
        
        # Ajouter les domaines maîtrisés
        for domain in mastered_domains[:5]:
            fields.append({
                'name': domain,
                'type': 'Master Data',
                'is_pk': False,
                'is_fk': False,
                'is_nullable': False,
            })
        
        # Ajouter les modules
        if system.modules:
            for module in system.modules[:5]:
                fields.append({
                    'name': module,
                    'type': 'Module',
                    'is_pk': False,
                    'is_fk': True,
                    'is_nullable': True,
                })
        
        incoming = flows.filter(target=system).count()
        outgoing = flows.filter(source=system).count()
        
        tables.append({
            'name': system.code,
            'model_name': system.name,
            'verbose_name': system.vendor,
            'fields': fields,
            'record_count': f'{incoming} flux entrants, {outgoing} flux sortants',
            'category': system.category.name,
            'criticality': system.criticality,
            'mode': system.get_mode_display(),
        })
    
    # Créer les relations basées sur les flux de données réels
    for flow in flows:
        relations.append({
            'from_table': flow.source.code,
            'from_field': flow.name,
            'to_table': flow.target.code,
            'to_field': flow.format or flow.get_protocol_display(),
            'type': 'CRITIQUE' if flow.is_critical else flow.get_frequency_display(),
            'frequency': flow.get_frequency_display(),
            'protocol': flow.get_protocol_display(),
            'is_critical': flow.is_critical,
        })
    
    # Trier les tables par catégorie puis nom
    tables.sort(key=lambda x: (x.get('category', ''), x['name']))
    
    context = {
        'tables': tables,
        'relations': relations,
        'total_systems': len(tables),
        'total_flows': len(relations),
    }
    return render(request, 'cartography/database_schema.html', context)


def api_database_schema(request):
    """API pour les données du schéma - Systèmes Air Algérie réels avec leurs données"""
    
    # Récupérer les vrais systèmes Air Algérie
    systems = System.objects.select_related('category', 'structure').all()
    flows = DataFlow.objects.select_related('source', 'target').all()
    samples = DataSample.objects.all()
    
    # Mapper les échantillons par système source
    # Mapping des codes échantillons vers les vrais codes systèmes
    sample_to_system_mapping = {
        'AMADEUS': 'ALTEA',      # Les fichiers AMADEUS viennent du PSS Altéa
        'AIMS': 'AIMS',          # AIMS reste AIMS
        'ACCELYA': 'ACCELYA',    # ACCELYA reste ACCELYA
        'RAPID': 'ACCELYA',      # RAPID = produit Accelya
        'ALTEA': 'ALTEA',
        'AMOS': 'AMOS',
    }
    
    samples_by_system = {}
    for sample in samples:
        # Mapper vers le vrai code système
        sys_code = sample_to_system_mapping.get(sample.source_system, sample.source_system)
        if sys_code not in samples_by_system:
            samples_by_system[sys_code] = []
        samples_by_system[sys_code].append(sample)
    
    nodes = []
    edges = []
    
    # Créer les nœuds pour chaque système réel
    for system in systems:
        # Récupérer les domaines de données maîtrisés
        mastered_domains = list(system.mastered_domains.values_list('name', flat=True))
        
        # Récupérer les flux entrants/sortants
        incoming_count = flows.filter(target=system).count()
        outgoing_count = flows.filter(source=system).count()
        
        # Récupérer les échantillons liés à ce système
        system_samples = samples_by_system.get(system.code, [])
        samples_count = len(system_samples)
        
        # Extraire les colonnes des échantillons
        sample_columns = []
        for s in system_samples:
            if s.columns_json:
                sample_columns.extend(s.columns_json[:5])
        sample_columns = list(set(sample_columns))[:10]
        
        # Champs clés du système (basés sur is_master_for, modules ET échantillons)
        fields = []
        
        # Ajouter le code comme PK
        fields.append({'name': system.code, 'type': 'ID', 'is_pk': True, 'is_fk': False})
        
        # Ajouter les colonnes des échantillons (données réelles)
        for col in sample_columns[:5]:
            fields.append({'name': col, 'type': 'Sample', 'is_pk': False, 'is_fk': True})
        
        # Ajouter les domaines maîtrisés comme champs
        for domain in mastered_domains[:3]:
            fields.append({'name': domain, 'type': 'Master', 'is_pk': False, 'is_fk': False})
        
        # Ajouter les modules si disponibles
        if system.modules:
            for module in system.modules[:3]:
                fields.append({'name': module, 'type': 'Module', 'is_pk': False, 'is_fk': False})
        
        # Construire le record_count avec info échantillons
        if samples_count > 0:
            record_count = f'{incoming_count}↓ {outgoing_count}↑ • {samples_count} échant.'
        else:
            record_count = f'{incoming_count}↓ {outgoing_count}↑'
        
        nodes.append({
            'id': f'sys_{system.id}',
            'label': system.code,
            'name': system.name,
            'type': 'system',
            'vendor': system.vendor,
            'category': system.category.name,
            'category_id': system.category.id,
            'structure': system.structure.code,
            'criticality': system.criticality,
            'mode': system.get_mode_display(),
            'fields': fields,
            'record_count': record_count,
            'has_samples': samples_count > 0,
            'samples_count': samples_count,
        })
    
    # Créer les arêtes pour les flux de données
    for flow in flows:
        edges.append({
            'id': f'flow_{flow.id}',
            'source': f'sys_{flow.source_id}',
            'target': f'sys_{flow.target_id}',
            'label': flow.name,
            'type': 'M2M' if flow.is_critical else 'FK',
            'frequency': flow.get_frequency_display(),
            'protocol': flow.get_protocol_display(),
            'format': flow.format,
            'is_critical': flow.is_critical,
        })
    
    return JsonResponse({
        'nodes': nodes,
        'edges': edges,
        'samples_total': samples.count(),
    })


def api_graph_data_with_validation(request):
    """API pour les données du graphe avec statut de validation"""
    category_filter = request.GET.get('category')
    structure_filter = request.GET.get('structure')
    show_structures = request.GET.get('show_structures', 'true') == 'true'
    show_validation = request.GET.get('show_validation', 'false') == 'true'
    
    systems = System.objects.select_related('category', 'structure')
    structures = Structure.objects.annotate(system_count=Count('systems'))
    
    if category_filter:
        systems = systems.filter(category_id=category_filter)
    if structure_filter:
        systems = systems.filter(structure_id=structure_filter)
        structures = structures.filter(id=structure_filter)
    
    system_ids = list(systems.values_list('id', flat=True))
    
    flows = DataFlow.objects.filter(
        Q(source_id__in=system_ids) | Q(target_id__in=system_ids)
    ).select_related('source', 'target').prefetch_related('field_hypotheses')
    
    # Build nodes
    nodes = []
    
    if show_structures:
        structure_ids_with_systems = set(systems.values_list('structure_id', flat=True))
        for structure in structures:
            if structure.id in structure_ids_with_systems:
                nodes.append({
                    'id': f'struct_{structure.id}',
                    'label': structure.code,
                    'name': structure.name,
                    'type': 'structure',
                    'color': structure.color,
                    'system_count': structure.system_count,
                    'description': structure.description,
                })
    
    for system in systems:
        node = {
            'id': f'sys_{system.id}',
            'label': system.code,
            'name': system.name,
            'type': 'system',
            'category': system.category.name,
            'category_id': system.category.id,
            'category_color': system.category.color,
            'structure': system.structure.code,
            'structure_id': system.structure.id,
            'parent': f'struct_{system.structure.id}' if show_structures else None,
            'criticality': system.criticality,
            'color': system.criticality_color,
            'vendor': system.vendor,
            'mode': system.get_mode_display(),
        }
        nodes.append(node)
    
    # Build edges with validation status
    edges = []
    for flow in flows:
        if flow.source_id in system_ids and flow.target_id in system_ids:
            # Calcul du statut de validation
            hypotheses = flow.field_hypotheses.all()
            total = len(hypotheses)
            confirmed = sum(1 for h in hypotheses if h.status == 'CONFIRMED')
            incorrect = sum(1 for h in hypotheses if h.status == 'INCORRECT')
            
            if total > 0:
                match_rate = int((confirmed / total) * 100)
                if incorrect > 0:
                    validation_status = 'ISSUES'
                elif confirmed == total:
                    validation_status = 'VALIDATED'
                elif confirmed > 0:
                    validation_status = 'PARTIAL'
                else:
                    validation_status = 'PENDING'
            else:
                match_rate = None
                validation_status = 'NOT_VALIDATED'
            
            edges.append({
                'id': f'flow_{flow.id}',
                'source': f'sys_{flow.source_id}',
                'target': f'sys_{flow.target_id}',
                'label': flow.name,
                'frequency': flow.get_frequency_display(),
                'protocol': flow.get_protocol_display(),
                'is_automated': flow.is_automated,
                'is_critical': flow.is_critical,
                'format': flow.format,
                'validation_status': validation_status,
                'match_rate': match_rate,
                'total_fields': total,
                'confirmed_fields': confirmed,
                'issues_fields': incorrect,
            })
    
    return JsonResponse({
        'nodes': nodes,
        'edges': edges,
    })


# Configuration API Claude (à mettre dans settings.py en production)
CLAUDE_API_KEY = "REMOVED_API_KEY"


def ai_report_view(request):
    """Vue pour générer et afficher le rapport IA"""
    from .services.report_generator import ReportGenerator
    
    systems = System.objects.select_related('category', 'structure').prefetch_related('mastered_domains').all()
    flows = DataFlow.objects.select_related('source', 'target').all()
    samples = DataSample.objects.all()
    domains = DataDomain.objects.all()
    
    # Mapping échantillons -> systèmes
    sample_to_system = {
        'AMADEUS': 'ALTEA',
        'AIMS': 'AIMS',
        'ACCELYA': 'ACCELYA',
        'RAPID': 'ACCELYA',
    }
    
    # Systèmes avec échantillons
    samples_by_system = {}
    for sample in samples:
        sys_code = sample_to_system.get(sample.source_system, sample.source_system)
        if sys_code not in samples_by_system:
            samples_by_system[sys_code] = 0
        samples_by_system[sys_code] += 1
    
    systems_with_samples = []
    systems_without_samples = []
    for sys in systems:
        if sys.code in samples_by_system:
            systems_with_samples.append({
                'code': sys.code,
                'name': sys.name,
                'sample_count': samples_by_system[sys.code]
            })
        else:
            systems_without_samples.append({
                'code': sys.code,
                'name': sys.name,
                'criticality': sys.criticality
            })
    
    critical_flows = flows.filter(is_critical=True)[:10]
    
    # Statistiques de localisation
    systems_france = list(systems.filter(country='FR').values('code', 'name', 'vendor'))
    systems_international = list(systems.filter(country__in=['EU', 'INTL']).values('code', 'name', 'vendor'))
    
    stats = {
        'total_systemes': systems.count(),
        'total_flux': flows.count(),
        'total_echantillons': samples.count(),
        'systemes_avec_echantillons': len(systems_with_samples),
        'flux_critiques': flows.filter(is_critical=True).count(),
        'systemes_algerie': systems.filter(country='DZ').count(),
        'systemes_france': systems.filter(country='FR').count(),
        'systemes_international': systems.filter(country__in=['EU', 'INTL']).count(),
    }
    
    report = None
    report_date = None
    error = None
    
    if request.method == 'POST':
        try:
            generator = ReportGenerator(CLAUDE_API_KEY)
            knowledge = generator.collect_knowledge(systems, flows, samples, domains)
            report_markdown = generator.generate_report(knowledge)
            
            # Convertir markdown en HTML
            report = markdown.markdown(report_markdown, extensions=['tables', 'fenced_code'])
            report_date = datetime.now().strftime('%d/%m/%Y à %H:%M')
            
            # Stocker en session pour le PDF
            request.session['last_report'] = report
            request.session['last_report_date'] = report_date
            request.session['last_report_stats'] = stats
            
        except Exception as e:
            error = str(e)
    
    # Récupérer le dernier rapport de la session si disponible
    if not report and 'last_report' in request.session:
        report = request.session.get('last_report')
        report_date = request.session.get('last_report_date')
    
    context = {
        'stats': stats,
        'report': report,
        'report_date': report_date,
        'error': error,
        'systems_with_samples': systems_with_samples,
        'systems_without_samples': systems_without_samples[:15],
        'critical_flows': critical_flows,
        'systems_france': systems_france,
        'systems_international': systems_international,
    }
    
    return render(request, 'cartography/ai_report.html', context)


def ai_report_pdf_view(request):
    """Génère le rapport en PDF"""
    from weasyprint import HTML
    
    report = request.session.get('last_report')
    report_date = request.session.get('last_report_date', datetime.now().strftime('%d/%m/%Y à %H:%M'))
    stats = request.session.get('last_report_stats', {
        'total_systemes': System.objects.count(),
        'total_flux': DataFlow.objects.count(),
        'total_echantillons': DataSample.objects.count(),
        'systemes_avec_echantillons': 0,
        'flux_critiques': DataFlow.objects.filter(is_critical=True).count(),
    })
    
    if not report:
        return HttpResponse("Aucun rapport disponible. Générez d'abord un rapport.", status=400)
    
    html_content = render_to_string('cartography/ai_report_pdf.html', {
        'report_html': report,
        'report_date': report_date,
        'stats': stats,
    })
    
    # Générer le PDF
    pdf = HTML(string=html_content).write_pdf()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="rapport_cartographie_si_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf"'
    
    return response


# ============================================
# HISTORIQUE DES IMPORTS DE DONNÉES
# ============================================

def import_history_list(request):
    """Liste de l'historique des imports de données"""
    imports = DataImportHistory.objects.all()
    
    # Filtres
    import_type = request.GET.get('type')
    status = request.GET.get('status')
    
    if import_type:
        imports = imports.filter(import_type=import_type)
    if status:
        imports = imports.filter(status=status)
    
    # Statistiques globales
    total_imports = imports.count()
    total_systems = sum(i.systems_added for i in imports)
    total_flows = sum(i.flows_added for i in imports)
    total_formats = sum(i.formats_added for i in imports)
    total_fields = sum(i.fields_added for i in imports)
    
    # Grouper par mois pour le graphique
    imports_by_month = {}
    for imp in imports:
        month_key = imp.date.strftime('%Y-%m')
        if month_key not in imports_by_month:
            imports_by_month[month_key] = {
                'count': 0,
                'systems': 0,
                'flows': 0,
                'formats': 0,
            }
        imports_by_month[month_key]['count'] += 1
        imports_by_month[month_key]['systems'] += imp.systems_added
        imports_by_month[month_key]['flows'] += imp.flows_added
        imports_by_month[month_key]['formats'] += imp.formats_added
    
    context = {
        'imports': imports,
        'type_choices': DataImportHistory.IMPORT_TYPE_CHOICES,
        'status_choices': DataImportHistory.STATUS_CHOICES,
        'selected_type': import_type,
        'selected_status': status,
        'total_imports': total_imports,
        'total_systems': total_systems,
        'total_flows': total_flows,
        'total_formats': total_formats,
        'total_fields': total_fields,
        'imports_by_month': imports_by_month,
    }
    return render(request, 'cartography/import_history_list.html', context)


def import_history_detail(request, pk):
    """Détail d'un import avec tous les éléments ajoutés"""
    import_record = get_object_or_404(DataImportHistory, pk=pk)
    
    # Extraire les détails des éléments ajoutés
    details = import_record.details_json or {}
    
    context = {
        'import_record': import_record,
        'flows_added': details.get('flows', []),
        'formats_added': details.get('formats', []),
        'fields_added': details.get('fields', []),
        'systems_added': details.get('systems', []),
        'files_processed': import_record.files_processed or [],
    }
    return render(request, 'cartography/import_history_detail.html', context)


# ─── Questionnaires ─────────────────────────────────────────────────────────

def questionnaires_list(request):
    """Liste des questionnaires par phase avec filtres et progression"""
    questionnaires = Questionnaire.objects.prefetch_related('sections__questions').all()
    
    phase = request.GET.get('phase')
    status = request.GET.get('status')
    search = request.GET.get('search')
    
    if phase:
        questionnaires = questionnaires.filter(phase=int(phase))
    if status:
        questionnaires = questionnaires.filter(status=status)
    if search:
        questionnaires = questionnaires.filter(
            Q(system_name__icontains=search) |
            Q(editor__icontains=search) |
            Q(key_users__icontains=search)
        )
    
    # Stats
    total = Questionnaire.objects.count()
    not_started = Questionnaire.objects.filter(status='NOT_STARTED').count()
    in_progress = Questionnaire.objects.filter(status='IN_PROGRESS').count()
    completed = Questionnaire.objects.filter(status='COMPLETED').count()
    total_questions = Question.objects.count()
    total_answered = Question.objects.filter(is_answered=True).count()
    
    # Group by phase
    phase1 = [q for q in questionnaires if q.phase == 1]
    phase2 = [q for q in questionnaires if q.phase == 2]
    phase3 = [q for q in questionnaires if q.phase == 3]
    
    phases = [
        ('Phase 1 — Critiques 🔴 (Mois 1–2)', '#ef4444', 'bg-red-900/20', phase1),
        ('Phase 2 — Importants 🟠 (Mois 3–4)', '#f97316', 'bg-orange-900/20', phase2),
        ('Phase 3 — Standard 🟢 (Mois 5–6)', '#22c55e', 'bg-green-900/20', phase3),
    ]
    
    context = {
        'questionnaires': questionnaires,
        'phases': phases,
        'total': total,
        'not_started': not_started,
        'in_progress': in_progress,
        'completed': completed,
        'total_questions': total_questions,
        'total_answered': total_answered,
        'global_progress': int((total_answered / total_questions * 100)) if total_questions > 0 else 0,
        'selected_phase': phase,
        'selected_status': status,
        'search': search or '',
    }
    return render(request, 'cartography/questionnaires_list.html', context)


def questionnaire_detail(request, pk):
    """Détail d'un questionnaire — formulaire interactif pour l'entretien"""
    questionnaire = get_object_or_404(
        Questionnaire.objects.prefetch_related('sections__questions'),
        pk=pk
    )
    
    if request.method == 'POST':
        # Save all answers
        for key, value in request.POST.items():
            if key.startswith('answer_'):
                q_id = key.replace('answer_', '')
                try:
                    question = Question.objects.get(pk=q_id)
                    question.answer = value
                    question.save()
                except Question.DoesNotExist:
                    pass
            elif key.startswith('notes_'):
                q_id = key.replace('notes_', '')
                try:
                    question = Question.objects.get(pk=q_id)
                    question.notes = value
                    question.save()
                except Question.DoesNotExist:
                    pass
        
        # Save interview notes
        interview_notes = request.POST.get('interview_notes', '')
        questionnaire.interview_notes = interview_notes
        
        # Update status
        new_status = request.POST.get('status', questionnaire.status)
        questionnaire.status = new_status
        questionnaire.save()
        
        messages.success(request, f'Questionnaire « {questionnaire.system_name} » sauvegardé avec succès.')
        return redirect('cartography:questionnaire_detail', pk=pk)
    
    # Navigation: previous and next questionnaire
    all_questionnaires = list(Questionnaire.objects.order_by('phase', 'priority_in_phase').values_list('pk', flat=True))
    current_idx = all_questionnaires.index(pk) if pk in all_questionnaires else -1
    prev_pk = all_questionnaires[current_idx - 1] if current_idx > 0 else None
    next_pk = all_questionnaires[current_idx + 1] if current_idx < len(all_questionnaires) - 1 else None
    
    context = {
        'questionnaire': questionnaire,
        'sections': questionnaire.sections.prefetch_related('questions').all(),
        'prev_pk': prev_pk,
        'next_pk': next_pk,
    }
    return render(request, 'cartography/questionnaire_detail.html', context)


def api_save_answer(request):
    """API endpoint pour sauvegarder une réponse et/ou valider individuellement (AJAX)"""
    if request.method == 'POST':
        import json
        from django.utils import timezone
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        question_id = data.get('question_id')
        answer = data.get('answer')
        notes = data.get('notes')
        validation_status = data.get('validation_status')
        validation_comment = data.get('validation_comment')
        validated_by = data.get('validated_by', '')
        
        try:
            question = Question.objects.select_related('section__questionnaire').get(pk=question_id)
        except Question.DoesNotExist:
            return JsonResponse({'error': 'Question not found'}, status=404)
        
        # Track revision if answer changed
        old_answer = question.answer
        if answer is not None and answer != old_answer:
            if old_answer.strip():
                history = question.revision_history or []
                history.append({
                    'date': timezone.now().isoformat(),
                    'old_answer': old_answer,
                    'action': 'edit',
                    'by': validated_by or 'utilisateur',
                })
                question.revision_history = history
            question.answer = answer
        
        if notes is not None:
            question.notes = notes
        
        # Handle validation
        if validation_status and validation_status in dict(Question.VALIDATION_CHOICES):
            old_status = question.validation_status
            question.validation_status = validation_status
            question.validated_by = validated_by
            question.validated_at = timezone.now()
            if validation_comment is not None:
                question.validation_comment = validation_comment
            
            # Log validation in history
            history = question.revision_history or []
            history.append({
                'date': timezone.now().isoformat(),
                'action': f'validation:{validation_status}',
                'from_status': old_status,
                'by': validated_by or 'validateur',
                'comment': validation_comment or '',
            })
            question.revision_history = history
        
        question.save()
        
        # Update questionnaire status
        questionnaire = question.section.questionnaire
        if questionnaire.status == 'NOT_STARTED' and questionnaire.answered_questions > 0:
            questionnaire.status = 'IN_PROGRESS'
            questionnaire.save()
        
        return JsonResponse({
            'ok': True,
            'is_answered': question.is_answered,
            'validation_status': question.validation_status,
            'progress': questionnaire.progress_percent,
            'answered': questionnaire.answered_questions,
            'total': questionnaire.total_questions,
            'validated': questionnaire.validated_questions,
            'rejected': questionnaire.rejected_questions,
            'validation_percent': questionnaire.validation_percent,
        })
    
    return JsonResponse({'error': 'POST required'}, status=405)


# ─── Organigramme ──────────────────────────────────────────────────────────

def organigramme_view(request):
    """Organigramme par département — fiche détaillée de chaque direction"""
    structures = Structure.objects.prefetch_related(
        'systems__category',
        'systems__questionnaire__sections__questions',
    ).annotate(
        system_count=Count('systems')
    ).order_by('code')
    
    departments = []
    total_key_users = set()
    
    for struct in structures:
        systems_data = []
        dept_questions = 0
        dept_answered = 0
        dept_validated = 0
        dept_key_users = set()
        dept_critiques = 0
        
        for s in struct.systems.all():
            q = getattr(s, 'questionnaire', None)
            q_progress = 0
            q_status = None
            q_total = 0
            q_answered = 0
            q_validated = 0
            q_key_users = ''
            q_direction = ''
            q_editor = ''
            q_pk = None
            
            if q:
                q_progress = q.progress_percent
                q_status = q.status
                q_total = q.total_questions
                q_answered = q.answered_questions
                q_validated = q.validated_questions
                q_key_users = q.key_users or ''
                q_direction = q.direction or ''
                q_editor = q.editor or ''
                q_pk = q.pk
                dept_questions += q_total
                dept_answered += q_answered
                dept_validated += q_validated
                
                # Collect key users
                for name in q_key_users.split(','):
                    name = name.strip()
                    if name:
                        dept_key_users.add(name)
                        total_key_users.add(name)
            
            if s.criticality == 'CRITIQUE':
                dept_critiques += 1
            
            systems_data.append({
                'pk': s.pk,
                'code': s.code,
                'name': s.name,
                'vendor': s.vendor,
                'criticality': s.criticality,
                'criticality_color': s.criticality_color,
                'mode': s.get_mode_display(),
                'category': s.category.name if s.category else '',
                'q_pk': q_pk,
                'q_progress': q_progress,
                'q_status': q_status,
                'q_total': q_total,
                'q_answered': q_answered,
                'q_key_users': q_key_users,
                'q_direction': q_direction,
                'q_editor': q_editor,
            })
        
        dept_progress = int((dept_answered / dept_questions * 100)) if dept_questions > 0 else 0
        
        departments.append({
            'pk': struct.pk,
            'code': struct.code,
            'name': struct.name,
            'color': struct.color,
            'country': struct.get_country_display(),
            'system_count': struct.system_count,
            'systems': systems_data,
            'total_questions': dept_questions,
            'answered_questions': dept_answered,
            'validated_questions': dept_validated,
            'progress': dept_progress,
            'critiques': dept_critiques,
            'key_users': sorted(dept_key_users),
            'key_users_count': len(dept_key_users),
        })
    
    # Selected department detail
    selected_code = request.GET.get('dept')
    selected_dept = None
    if selected_code:
        selected_dept = next((d for d in departments if d['code'] == selected_code), None)
    
    context = {
        'departments': departments,
        'selected_dept': selected_dept,
        'total_structures': structures.count(),
        'total_systems': System.objects.count(),
        'total_key_users': len(total_key_users),
    }
    return render(request, 'cartography/organigramme.html', context)


# ─── KPI Dashboard ─────────────────────────────────────────────────────────

def kpi_dashboard_view(request):
    """Dashboard KPI avec avancement cartographie en temps réel vs roadmap"""
    import json as json_module
    
    # ── Systems stats
    total_systems = System.objects.count()
    systems_with_data = System.objects.filter(
        Q(outgoing_flows__isnull=False) | Q(incoming_flows__isnull=False)
    ).distinct().count()
    systems_no_data = total_systems - systems_with_data
    
    # By criticality
    crit_stats = {}
    for crit, label in System.CRITICALITY_CHOICES:
        crit_stats[crit] = System.objects.filter(criticality=crit).count()
    
    # ── Questionnaire stats
    total_questionnaires = Questionnaire.objects.count()
    q_not_started = Questionnaire.objects.filter(status='NOT_STARTED').count()
    q_in_progress = Questionnaire.objects.filter(status='IN_PROGRESS').count()
    q_completed = Questionnaire.objects.filter(status='COMPLETED').count()
    
    total_questions = Question.objects.count()
    total_answered = Question.objects.filter(is_answered=True).count()
    total_validated = Question.objects.filter(validation_status='VALIDATED').count()
    
    questionnaire_progress = int((total_answered / total_questions * 100)) if total_questions > 0 else 0
    validation_progress = int((total_validated / total_questions * 100)) if total_questions > 0 else 0
    
    # ── Per-phase breakdown
    phase_data = []
    for phase_num, phase_label in [(1, 'Phase 1 — Critique'), (2, 'Phase 2 — Important'), (3, 'Phase 3 — Standard')]:
        phase_qs = Questionnaire.objects.filter(phase=phase_num)
        phase_questions = Question.objects.filter(section__questionnaire__phase=phase_num)
        p_total = phase_questions.count()
        p_answered = phase_questions.filter(is_answered=True).count()
        p_validated = phase_questions.filter(validation_status='VALIDATED').count()
        phase_data.append({
            'phase': phase_num,
            'label': phase_label,
            'total_systems': phase_qs.count(),
            'completed': phase_qs.filter(status='COMPLETED').count(),
            'in_progress': phase_qs.filter(status='IN_PROGRESS').count(),
            'not_started': phase_qs.filter(status='NOT_STARTED').count(),
            'total_questions': p_total,
            'answered': p_answered,
            'validated': p_validated,
            'progress': int((p_answered / p_total * 100)) if p_total > 0 else 0,
        })
    
    # ── Data collection stats
    total_flows = DataFlow.objects.count()
    automated_flows = DataFlow.objects.filter(is_automated=True).count()
    manual_flows = DataFlow.objects.filter(is_automated=False).count()
    critical_flows = DataFlow.objects.filter(is_critical=True).count()
    
    total_samples = DataSample.objects.count()
    
    # ── Per-system progress for the table
    system_progress = []
    for q in Questionnaire.objects.prefetch_related('sections__questions').order_by('phase', 'priority_in_phase'):
        sys_obj = q.system
        incoming = sys_obj.incoming_flows.count() if sys_obj else 0
        outgoing = sys_obj.outgoing_flows.count() if sys_obj else 0
        system_progress.append({
            'questionnaire': q,
            'system': sys_obj,
            'incoming_flows': incoming,
            'outgoing_flows': outgoing,
            'total_flows': incoming + outgoing,
            'has_data': incoming > 0 or outgoing > 0,
        })
    
    # ── Roadmap targets (based on contract: 640 j/h, 1 year, 5 phases)
    roadmap = {
        'phase1_target': 'Mois 1-2 : Diagnostic + Inventaire',
        'phase2_target': 'Mois 3-4 : Connecteurs + Intégration',
        'phase3_target': 'Mois 5-6 : Automatisation + MDM',
        'total_jh': 640,
        'duration_months': 12,
        'systems_target': total_systems,
        'questionnaires_target': total_questionnaires,
    }
    
    context = {
        'total_systems': total_systems,
        'systems_with_data': systems_with_data,
        'systems_no_data': systems_no_data,
        'crit_stats': crit_stats,
        'total_questionnaires': total_questionnaires,
        'q_not_started': q_not_started,
        'q_in_progress': q_in_progress,
        'q_completed': q_completed,
        'total_questions': total_questions,
        'total_answered': total_answered,
        'total_validated': total_validated,
        'questionnaire_progress': questionnaire_progress,
        'validation_progress': validation_progress,
        'phase_data': phase_data,
        'total_flows': total_flows,
        'automated_flows': automated_flows,
        'manual_flows': manual_flows,
        'critical_flows': critical_flows,
        'total_samples': total_samples,
        'system_progress': system_progress,
        'roadmap': roadmap,
        'phase_data_json': json_module.dumps(phase_data),
    }
    return render(request, 'cartography/kpi_dashboard.html', context)


def api_kpi_stats(request):
    """API JSON pour les KPI temps réel (polling AJAX)"""
    total_systems = System.objects.count()
    systems_with_data = System.objects.filter(
        Q(outgoing_flows__isnull=False) | Q(incoming_flows__isnull=False)
    ).distinct().count()
    
    total_questionnaires = Questionnaire.objects.count()
    q_completed = Questionnaire.objects.filter(status='COMPLETED').count()
    q_in_progress = Questionnaire.objects.filter(status='IN_PROGRESS').count()
    
    total_questions = Question.objects.count()
    total_answered = Question.objects.filter(is_answered=True).count()
    total_validated = Question.objects.filter(validation_status='VALIDATED').count()
    
    # Per-phase
    phases = []
    for p in [1, 2, 3]:
        pq = Question.objects.filter(section__questionnaire__phase=p)
        pt = pq.count()
        pa = pq.filter(is_answered=True).count()
        phases.append({
            'phase': p,
            'total': pt,
            'answered': pa,
            'progress': int((pa / pt * 100)) if pt > 0 else 0,
            'completed_questionnaires': Questionnaire.objects.filter(phase=p, status='COMPLETED').count(),
            'total_questionnaires': Questionnaire.objects.filter(phase=p).count(),
        })
    
    return JsonResponse({
        'total_systems': total_systems,
        'systems_with_data': systems_with_data,
        'systems_coverage': int((systems_with_data / total_systems * 100)) if total_systems > 0 else 0,
        'total_questionnaires': total_questionnaires,
        'questionnaires_completed': q_completed,
        'questionnaires_in_progress': q_in_progress,
        'total_questions': total_questions,
        'total_answered': total_answered,
        'total_validated': total_validated,
        'questionnaire_progress': int((total_answered / total_questions * 100)) if total_questions > 0 else 0,
        'validation_progress': int((total_validated / total_questions * 100)) if total_questions > 0 else 0,
        'phases': phases,
        'total_flows': DataFlow.objects.count(),
        'total_samples': DataSample.objects.count(),
    })


def questionnaire_form_view(request, pk):
    """Formulaire public de questionnaire — pour les key users (accès par lien)"""
    questionnaire = get_object_or_404(
        Questionnaire.objects.prefetch_related('sections__questions'),
        pk=pk
    )
    
    # Token-based access check placeholder (for future smart access)
    token = request.GET.get('token', '')
    
    if request.method == 'POST':
        respondent_name = request.POST.get('respondent_name', '')
        
        for key, value in request.POST.items():
            if key.startswith('answer_'):
                q_id = key.replace('answer_', '')
                try:
                    question = Question.objects.get(pk=q_id)
                    if value.strip():
                        question.answer = value
                        question.save()
                except Question.DoesNotExist:
                    pass
            elif key.startswith('notes_'):
                q_id = key.replace('notes_', '')
                try:
                    question = Question.objects.get(pk=q_id)
                    question.notes = value
                    question.save()
                except Question.DoesNotExist:
                    pass
        
        # Auto-update status
        if questionnaire.status == 'NOT_STARTED':
            questionnaire.status = 'IN_PROGRESS'
        if questionnaire.progress_percent == 100:
            questionnaire.status = 'COMPLETED'
        questionnaire.save()
        
        messages.success(request, f'Merci ! Vos réponses pour « {questionnaire.system_name} » ont été enregistrées.')
        return redirect(f"{request.path}?token={token}&saved=1")
    
    saved = request.GET.get('saved', '')
    
    context = {
        'questionnaire': questionnaire,
        'sections': questionnaire.sections.prefetch_related('questions').all(),
        'token': token,
        'saved': saved,
    }
    return render(request, 'cartography/questionnaire_form.html', context)
