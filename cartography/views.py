import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q, Avg
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import datetime
import markdown
from .models import (
    Structure, SystemCategory, System, DataFlow, 
    DataField, MessageFormat, MessageField, DataDomain,
    DataSample, FlowFieldHypothesis, FlowValidation,
    ReferenceData, FlowReferential, DataImportHistory, COUNTRY_CHOICES,
    Questionnaire, QuestionSection, Question, KeyUserAccess, AuditorAccess, DivisionAccess,
    Process, ProcessStep
)


# ─── Auth views ───────────────────────────────────────────────────────────

def login_view(request):
    """Page de connexion admin + accès key user"""
    if request.user.is_authenticated:
        return redirect('cartography:dashboard')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            error = 'Identifiants incorrects.'
    return render(request, 'cartography/login.html', {'error': error})


def logout_view(request):
    """Déconnexion admin, key user ou auditeur"""
    request.session.pop('key_user_token', None)
    request.session.pop('key_user_name', None)
    request.session.pop('key_user_questionnaire_id', None)
    request.session.pop('key_user_questionnaires', None)
    request.session.pop('auditor_token', None)
    request.session.pop('auditor_name', None)
    request.session.pop('division_token', None)
    request.session.pop('division_name', None)
    request.session.pop('division_structure_id', None)
    request.session.pop('division_structure_code', None)
    logout(request)
    return redirect('cartography:login')


def unified_token_login(request):
    """Accès unifié — détecte automatiquement le type de token (auditeur, division, key user)"""
    token = request.GET.get('token', '').strip()
    if not token:
        return redirect('cartography:login')
    # 1. Essayer AuditorAccess (PDG, conseillers)
    try:
        access = AuditorAccess.objects.get(token=token, is_active=True)
        access.last_accessed = timezone.now()
        access.save(update_fields=['last_accessed'])
        request.session['auditor_token'] = token
        request.session['auditor_name'] = access.name
        return redirect('cartography:kpi_dashboard')
    except AuditorAccess.DoesNotExist:
        pass
    # 2. Essayer DivisionAccess (divisionnaires, directeurs)
    try:
        access = DivisionAccess.objects.select_related('structure').get(token=token, is_active=True)
        access.last_accessed = timezone.now()
        access.save(update_fields=['last_accessed'])
        request.session['division_token'] = token
        request.session['division_name'] = access.name
        request.session['division_structure_id'] = access.structure.pk
        request.session['division_structure_code'] = access.structure.code
        return redirect('cartography:division_dashboard')
    except DivisionAccess.DoesNotExist:
        pass
    # 3. Essayer KeyUserAccess
    try:
        access = KeyUserAccess.objects.select_related('questionnaire').get(token=token, is_active=True)
        access.last_accessed = timezone.now()
        access.save(update_fields=['last_accessed'])
        request.session['key_user_token'] = token
        request.session['key_user_name'] = access.name
        request.session['key_user_questionnaire_id'] = access.questionnaire.pk
        all_access = KeyUserAccess.objects.filter(
            name=access.name, is_active=True
        ).select_related('questionnaire').order_by('questionnaire__system_name')
        request.session['key_user_questionnaires'] = [
            {'id': a.questionnaire.pk, 'name': a.questionnaire.system_name, 'token': a.token}
            for a in all_access
        ]
        return redirect('cartography:questionnaire_form', pk=access.questionnaire.pk)
    except KeyUserAccess.DoesNotExist:
        pass
    return render(request, 'cartography/login.html', {'error': 'Code d\'accès invalide ou désactivé.'})


def key_user_login(request):
    """Accès key user via token — redirige vers le questionnaire"""
    token = request.GET.get('token', '').strip()
    if not token:
        return redirect('cartography:login')
    try:
        access = KeyUserAccess.objects.select_related('questionnaire').get(token=token, is_active=True)
        access.last_accessed = timezone.now()
        access.save(update_fields=['last_accessed'])
        request.session['key_user_token'] = token
        request.session['key_user_name'] = access.name
        request.session['key_user_questionnaire_id'] = access.questionnaire.pk
        # Find all questionnaires this key user has access to (by name)
        all_access = KeyUserAccess.objects.filter(
            name=access.name, is_active=True
        ).select_related('questionnaire').order_by('questionnaire__system_name')
        request.session['key_user_questionnaires'] = [
            {'id': a.questionnaire.pk, 'name': a.questionnaire.system_name, 'token': a.token}
            for a in all_access
        ]
        return redirect('cartography:questionnaire_form', pk=access.questionnaire.pk)
    except KeyUserAccess.DoesNotExist:
        return render(request, 'cartography/login.html', {'error': 'Code d\'accès invalide ou désactivé.'})


def auditor_login(request):
    """Accès auditeur via token — redirige vers le KPI dashboard"""
    token = request.GET.get('token', '').strip()
    if not token:
        return redirect('cartography:login')
    try:
        access = AuditorAccess.objects.get(token=token, is_active=True)
        access.last_accessed = timezone.now()
        access.save(update_fields=['last_accessed'])
        request.session['auditor_token'] = token
        request.session['auditor_name'] = access.name
        return redirect('cartography:kpi_dashboard')
    except AuditorAccess.DoesNotExist:
        return render(request, 'cartography/login.html', {'error': 'Code auditeur invalide ou désactivé.'})


def division_login(request):
    """Accès division via token — redirige vers le dashboard division"""
    token = request.GET.get('token', '').strip()
    if not token:
        return redirect('cartography:login')
    try:
        access = DivisionAccess.objects.select_related('structure').get(token=token, is_active=True)
        access.last_accessed = timezone.now()
        access.save(update_fields=['last_accessed'])
        request.session['division_token'] = token
        request.session['division_name'] = access.name
        request.session['division_structure_id'] = access.structure.pk
        request.session['division_structure_code'] = access.structure.code
        return redirect('cartography:division_dashboard')
    except DivisionAccess.DoesNotExist:
        return render(request, 'cartography/login.html', {'error': 'Code division invalide ou désactivé.'})


def division_dashboard(request):
    """Dashboard division — avancement des questionnaires de la division"""
    division_token = request.session.get('division_token')
    if not division_token:
        return redirect('cartography:login')
    
    try:
        access = DivisionAccess.objects.select_related('structure').get(token=division_token, is_active=True)
    except DivisionAccess.DoesNotExist:
        request.session.pop('division_token', None)
        return redirect('cartography:login')
    
    division = access.structure
    # Get all child structures (directions under this division)
    children = Structure.objects.filter(parent=division)
    all_structures = [division] + list(children)
    
    # Get all systems belonging to this division or its child directions
    systems = System.objects.filter(structure__in=all_structures).select_related('structure')
    
    # Get questionnaires for these systems
    questionnaires = Questionnaire.objects.filter(
        system__in=systems
    ).prefetch_related('sections__questions').select_related('system__structure')
    
    # Stats
    total_q = questionnaires.count()
    completed = questionnaires.filter(status='COMPLETED').count()
    in_progress = questionnaires.filter(status='IN_PROGRESS').count()
    not_started = questionnaires.filter(status='NOT_STARTED').count()
    
    total_questions = 0
    total_answered = 0
    for q in questionnaires:
        total_questions += q.total_questions
        total_answered += q.answered_questions
    
    global_progress = int((total_answered / total_questions * 100)) if total_questions > 0 else 0
    
    # Group by child direction
    directions_data = []
    for struct in all_structures:
        struct_systems = systems.filter(structure=struct)
        struct_quests = [q for q in questionnaires if q.system and q.system.structure_id == struct.pk]
        if struct_quests:
            s_total = sum(q.total_questions for q in struct_quests)
            s_answered = sum(q.answered_questions for q in struct_quests)
            s_progress = int((s_answered / s_total * 100)) if s_total > 0 else 0
            directions_data.append({
                'structure': struct,
                'questionnaires': struct_quests,
                'total_questions': s_total,
                'total_answered': s_answered,
                'progress': s_progress,
            })
    
    context = {
        'division': division,
        'access': access,
        'questionnaires': questionnaires,
        'directions_data': directions_data,
        'total_questionnaires': total_q,
        'completed': completed,
        'in_progress': in_progress,
        'not_started': not_started,
        'total_questions': total_questions,
        'total_answered': total_answered,
        'global_progress': global_progress,
    }
    return render(request, 'cartography/division_dashboard.html', context)


def division_questionnaire_view(request, pk):
    """Consultation lecture seule d'un questionnaire par un responsable division"""
    division_token = request.session.get('division_token')
    if not division_token:
        return redirect('cartography:login')
    
    try:
        access = DivisionAccess.objects.select_related('structure').get(token=division_token, is_active=True)
    except DivisionAccess.DoesNotExist:
        return redirect('cartography:login')
    
    division = access.structure
    children = Structure.objects.filter(parent=division)
    all_structures = [division] + list(children)
    
    questionnaire = get_object_or_404(
        Questionnaire.objects.prefetch_related('sections__questions'),
        pk=pk
    )
    
    # Check that this questionnaire belongs to the division
    if questionnaire.system and questionnaire.system.structure not in all_structures:
        return redirect('cartography:division_dashboard')
    
    context = {
        'questionnaire': questionnaire,
        'sections': questionnaire.sections.prefetch_related('questions').all(),
        'division': division,
        'access': access,
        'is_readonly': True,
    }
    return render(request, 'cartography/division_questionnaire.html', context)


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
def graph_view(request):
    """Vue graphique interactive de la cartographie"""
    categories = SystemCategory.objects.all()
    structures = Structure.objects.all()
    
    context = {
        'categories': categories,
        'structures': structures,
    }
    return render(request, 'cartography/graph.html', context)


@login_required(login_url='/login/')
def structures_list(request):
    """Liste des structures organisationnelles"""
    structures = Structure.objects.annotate(
        system_count=Count('systems')
    ).prefetch_related('systems')
    
    context = {
        'structures': structures,
    }
    return render(request, 'cartography/structures_list.html', context)


@login_required(login_url='/login/')
def messages_list(request):
    """Liste des formats de messages standards"""
    messages = MessageFormat.objects.prefetch_related('fields').all()
    
    context = {
        'messages': messages,
    }
    return render(request, 'cartography/messages_list.html', context)


@login_required(login_url='/login/')
def message_detail(request, pk):
    """Détail d'un format de message"""
    message = get_object_or_404(MessageFormat.objects.prefetch_related('fields'), pk=pk)
    
    context = {
        'message': message,
        'fields': message.fields.all(),
    }
    return render(request, 'cartography/message_detail.html', context)


@login_required(login_url='/login/')
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

@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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


# Configuration API Claude (via variable d'environnement)
CLAUDE_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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

@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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
    if not request.user.is_authenticated and not request.session.get('auditor_token'):
        return redirect('cartography:login')
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
    # Questions répondues = réellement répondues + toutes les questions des questionnaires terminés (même si answer vide)
    completed_qs = Questionnaire.objects.filter(status='COMPLETED')
    completed_q_total = Question.objects.filter(section__questionnaire__in=completed_qs).count()
    non_completed_answered = Question.objects.filter(is_answered=True).exclude(section__questionnaire__in=completed_qs).count()
    total_answered = completed_q_total + non_completed_answered
    
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
    if not request.user.is_authenticated and not request.session.get('auditor_token'):
        return redirect('cartography:login')
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
        if questionnaire.progress_percent == 100:
            questionnaire.status = 'COMPLETED'
            questionnaire.save()
        elif questionnaire.status == 'NOT_STARTED' and questionnaire.answered_questions > 0:
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
    """Organigramme par département — hiérarchie + suivi réponses par direction"""
    if not request.user.is_authenticated and not request.session.get('auditor_token'):
        return redirect('cartography:login')
    structures = Structure.objects.prefetch_related(
        'systems__category',
        'systems__questionnaire__sections__questions',
        'children',
    ).annotate(
        system_count=Count('systems')
    ).order_by('code')
    
    # Build a lookup for all structures
    struct_map = {s.pk: s for s in structures}
    
    def build_dept_data(struct):
        """Build department data dict for a structure"""
        systems_data = []
        dept_questions = 0
        dept_answered = 0
        dept_validated = 0
        dept_rejected = 0
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
            
            q_key_users_backup = ''
            q_responsible = ''
            
            if q:
                q_progress = q.progress_percent
                q_status = q.status
                q_total = q.total_questions
                q_answered = q.answered_questions
                q_validated = q.validated_questions
                q_key_users = q.key_users or ''
                q_key_users_backup = q.key_users_backup or ''
                q_direction = q.direction or ''
                q_editor = q.editor or ''
                q_responsible = q.responsible or ''
                q_pk = q.pk
                dept_questions += q_total
                dept_answered += q_answered
                dept_validated += q_validated
                dept_rejected += q.rejected_questions
                
                for name in q_key_users.split(','):
                    name = name.strip()
                    if name and name != '—':
                        dept_key_users.add(name)
            
            if s.criticality == 'CRITIQUE':
                dept_critiques += 1
            
            # Determine response status for display
            if q_pk is None:
                response_label = 'Pas de questionnaire'
                response_class = 'text-gray-600'
            elif q_status == 'COMPLETED':
                response_label = 'Complété'
                response_class = 'text-green-400'
            elif q_status == 'IN_PROGRESS':
                response_label = f'En cours ({q_progress}%)'
                response_class = 'text-blue-400'
            else:
                response_label = 'Non commencé'
                response_class = 'text-red-400'
            
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
                'q_key_users_backup': q_key_users_backup,
                'q_direction': q_direction,
                'q_editor': q_editor,
                'q_responsible': q_responsible,
                'response_label': response_label,
                'response_class': response_class,
            })
        
        dept_progress = int((dept_answered / dept_questions * 100)) if dept_questions > 0 else 0
        validation_progress = int((dept_validated / dept_questions * 100)) if dept_questions > 0 else 0
        
        return {
            'pk': struct.pk,
            'code': struct.code,
            'name': struct.name,
            'color': struct.color,
            'level': struct.level or '',
            'responsable': struct.responsable or '',
            'parent_id': struct.parent_id,
            'country': struct.get_country_display(),
            'system_count': struct.system_count,
            'systems': systems_data,
            'total_questions': dept_questions,
            'answered_questions': dept_answered,
            'validated_questions': dept_validated,
            'rejected_questions': dept_rejected,
            'progress': dept_progress,
            'validation_progress': validation_progress,
            'critiques': dept_critiques,
            'key_users': sorted(dept_key_users),
            'key_users_count': len(dept_key_users),
            'children': [],
        }
    
    # Build all department data
    all_depts = {}
    total_key_users = set()
    for struct in structures:
        dept = build_dept_data(struct)
        all_depts[struct.pk] = dept
        total_key_users.update(dept['key_users'])
    
    # Build hierarchy tree: attach children to parents
    root_depts = []
    for pk, dept in all_depts.items():
        parent_id = dept['parent_id']
        if parent_id and parent_id in all_depts:
            all_depts[parent_id]['children'].append(dept)
        else:
            root_depts.append(dept)
    
    # Flat list for backward compat (grid view)
    departments = list(all_depts.values())
    
    # Selected department detail
    selected_code = request.GET.get('dept')
    selected_dept = None
    if selected_code:
        selected_dept = next((d for d in departments if d['code'] == selected_code), None)
    
    context = {
        'departments': departments,
        'root_depts': root_depts,
        'selected_dept': selected_dept,
        'total_structures': structures.count(),
        'total_systems': System.objects.count(),
        'total_key_users': len(total_key_users),
    }
    return render(request, 'cartography/organigramme.html', context)


# ─── KPI Dashboard ─────────────────────────────────────────────────────────

def kpi_dashboard_view(request):
    """Dashboard KPI avec avancement cartographie en temps réel vs roadmap"""
    if not request.user.is_authenticated and not request.session.get('auditor_token'):
        return redirect('cartography:login')
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
    # Questions répondues = réellement répondues + toutes les questions des questionnaires terminés
    completed_qs_kpi = Questionnaire.objects.filter(status='COMPLETED')
    completed_q_total_kpi = Question.objects.filter(section__questionnaire__in=completed_qs_kpi).count()
    non_completed_answered_kpi = Question.objects.exclude(answer='').exclude(section__questionnaire__in=completed_qs_kpi).count()
    total_answered = completed_q_total_kpi + non_completed_answered_kpi
    total_validated = Question.objects.filter(validation_status='VALIDATED').count()
    
    questionnaire_progress = int((total_answered / total_questions * 100)) if total_questions > 0 else 0
    validation_progress = int((total_validated / total_questions * 100)) if total_questions > 0 else 0
    
    # ── Per-phase breakdown
    phase_data = []
    for phase_num, phase_label in [(1, 'Phase 1 — Critique'), (2, 'Phase 2 — Important'), (3, 'Phase 3 — Standard')]:
        phase_qs = Questionnaire.objects.filter(phase=phase_num)
        phase_questions = Question.objects.filter(section__questionnaire__phase=phase_num)
        p_total = phase_questions.count()
        # Compter toutes les questions des questionnaires terminés comme répondues
        phase_completed_qs = phase_qs.filter(status='COMPLETED')
        p_completed_total = Question.objects.filter(section__questionnaire__in=phase_completed_qs).count()
        p_non_completed_answered = phase_questions.exclude(answer='').exclude(section__questionnaire__in=phase_completed_qs).count()
        p_answered = p_completed_total + p_non_completed_answered
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
    
    # ── Flow validation — Hypothèse vs Réalité (données réelles)
    total_hypotheses = FlowFieldHypothesis.objects.count()
    hyp_confirmed = FlowFieldHypothesis.objects.filter(status='CONFIRMED').count()
    hyp_partial = FlowFieldHypothesis.objects.filter(status='PARTIAL').count()
    hyp_incorrect = FlowFieldHypothesis.objects.filter(status='INCORRECT').count()
    hyp_pending = FlowFieldHypothesis.objects.filter(status='HYPOTHESIS').count()
    hyp_validated_pct = int(((hyp_confirmed + hyp_partial) / total_hypotheses * 100)) if total_hypotheses > 0 else 0
    
    total_flow_validations = FlowValidation.objects.count()
    fv_validated = FlowValidation.objects.filter(status='VALIDATED').count()
    fv_partial = FlowValidation.objects.filter(status='PARTIAL').count()
    fv_issues = FlowValidation.objects.filter(status='ISSUES').count()
    
    # Flows with at least one sample (data received)
    flows_with_samples = DataFlow.objects.filter(
        Q(source__code__in=[s.source_system for s in DataSample.objects.all()]) |
        Q(field_hypotheses__validated_from_sample__isnull=False)
    ).distinct().count()
    
    # Per-system: which systems have real data samples
    systems_with_samples = set(DataSample.objects.values_list('source_system', flat=True))
    
    # Build flow validation detail table
    flow_validation_data = []
    for flow in DataFlow.objects.select_related('source', 'target').prefetch_related('field_hypotheses', 'validations'):
        hyps = flow.field_hypotheses.all()
        h_total = hyps.count()
        if h_total == 0:
            continue
        h_confirmed = hyps.filter(status='CONFIRMED').count()
        h_partial_f = hyps.filter(status='PARTIAL').count()
        h_incorrect = hyps.filter(status='INCORRECT').count()
        h_pending_f = hyps.filter(status='HYPOTHESIS').count()
        has_sample = hyps.filter(validated_from_sample__isnull=False).exists()
        latest_v = flow.validations.first()
        
        flow_validation_data.append({
            'flow': flow,
            'total_fields': h_total,
            'confirmed': h_confirmed,
            'partial': h_partial_f,
            'incorrect': h_incorrect,
            'pending': h_pending_f,
            'has_sample': has_sample,
            'match_pct': int(((h_confirmed + h_partial_f) / h_total * 100)) if h_total > 0 else 0,
            'validation_status': latest_v.status if latest_v else 'PENDING',
        })
    flow_validation_data.sort(key=lambda x: x['confirmed'], reverse=True)
    
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
        # Flow validation data
        'total_hypotheses': total_hypotheses,
        'hyp_confirmed': hyp_confirmed,
        'hyp_partial': hyp_partial,
        'hyp_incorrect': hyp_incorrect,
        'hyp_pending': hyp_pending,
        'hyp_validated_pct': hyp_validated_pct,
        'total_flow_validations': total_flow_validations,
        'fv_validated': fv_validated,
        'fv_partial': fv_partial,
        'fv_issues': fv_issues,
        'flows_with_samples': flows_with_samples,
        'systems_with_samples': systems_with_samples,
        'flow_validation_data': flow_validation_data,
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
    # Questions répondues = réellement répondues + toutes les questions des questionnaires terminés
    api_completed_qs = Questionnaire.objects.filter(status='COMPLETED')
    api_completed_q_total = Question.objects.filter(section__questionnaire__in=api_completed_qs).count()
    api_non_completed_answered = Question.objects.exclude(answer='').exclude(section__questionnaire__in=api_completed_qs).count()
    total_answered = api_completed_q_total + api_non_completed_answered
    total_validated = Question.objects.filter(validation_status='VALIDATED').count()
    
    # Per-phase
    phases = []
    for p in [1, 2, 3]:
        pq = Question.objects.filter(section__questionnaire__phase=p)
        pt = pq.count()
        # Compter toutes les questions des questionnaires terminés comme répondues
        p_completed_qs = Questionnaire.objects.filter(phase=p, status='COMPLETED')
        p_completed_total = Question.objects.filter(section__questionnaire__in=p_completed_qs).count()
        p_non_completed_answered = pq.exclude(answer='').exclude(section__questionnaire__in=p_completed_qs).count()
        pa = p_completed_total + p_non_completed_answered
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


def export_kpi_md(request):
    """Génère un rapport Markdown complet de l'avancement KPI — téléchargeable"""
    if not request.user.is_authenticated and not request.session.get('auditor_token'):
        return redirect('cartography:login')
    
    now = timezone.now()
    date_str = now.strftime('%d/%m/%Y à %Hh%M')
    date_file = now.strftime('%Y-%m-%d')
    
    # ── Stats globales
    total_systems = System.objects.count()
    systems_with_data = System.objects.filter(
        Q(outgoing_flows__isnull=False) | Q(incoming_flows__isnull=False)
    ).distinct().count()
    total_questionnaires = Questionnaire.objects.count()
    total_questions = Question.objects.count()
    # Questions répondues = réellement répondues + toutes les questions des questionnaires terminés
    md_completed_qs = Questionnaire.objects.filter(status='COMPLETED')
    md_completed_q_total = Question.objects.filter(section__questionnaire__in=md_completed_qs).count()
    md_non_completed_answered = Question.objects.exclude(answer='').exclude(section__questionnaire__in=md_completed_qs).count()
    total_answered = md_completed_q_total + md_non_completed_answered
    total_validated = Question.objects.filter(validation_status='VALIDATED').count()
    questionnaire_progress = int((total_answered / total_questions * 100)) if total_questions > 0 else 0
    total_flows = DataFlow.objects.count()
    total_samples = DataSample.objects.count()
    
    # ── Compute real status from answers (not relying solely on status field)
    q_completed = 0
    q_in_progress = 0
    q_not_started = 0
    for q in Questionnaire.objects.prefetch_related('sections__questions').all():
        if q.progress_percent == 100:
            q_completed += 1
        elif q.answered_questions > 0:
            q_in_progress += 1
        else:
            q_not_started += 1
    
    # ── Par phase
    phase_data = []
    for phase_num, phase_label in [(1, 'Phase 1 — Critique'), (2, 'Phase 2 — Important'), (3, 'Phase 3 — Standard')]:
        phase_qs = list(Questionnaire.objects.filter(phase=phase_num).prefetch_related('sections__questions'))
        phase_questions = Question.objects.filter(section__questionnaire__phase=phase_num)
        p_total = phase_questions.count()
        # Compter toutes les questions des questionnaires terminés comme répondues
        md_phase_completed_qs = [q for q in phase_qs if q.status == 'COMPLETED']
        md_phase_completed_ids = [q.id for q in md_phase_completed_qs]
        p_completed_q_total = Question.objects.filter(section__questionnaire__id__in=md_phase_completed_ids).count() if md_phase_completed_ids else 0
        p_non_completed_answered = phase_questions.exclude(answer='').exclude(section__questionnaire__id__in=md_phase_completed_ids).count() if md_phase_completed_ids else phase_questions.exclude(answer='').count()
        p_answered = p_completed_q_total + p_non_completed_answered
        p_validated = phase_questions.filter(validation_status='VALIDATED').count()
        p_completed = sum(1 for q in phase_qs if q.progress_percent == 100)
        p_in_progress = sum(1 for q in phase_qs if 0 < q.answered_questions < q.total_questions)
        p_not_started = sum(1 for q in phase_qs if q.answered_questions == 0)
        phase_data.append({
            'phase': phase_num,
            'label': phase_label,
            'total_systems': len(phase_qs),
            'completed': p_completed,
            'in_progress': p_in_progress,
            'not_started': p_not_started,
            'total_questions': p_total,
            'answered': p_answered,
            'validated': p_validated,
            'progress': int((p_answered / p_total * 100)) if p_total > 0 else 0,
        })
    
    # ── Tous les questionnaires avec détails
    all_qs = Questionnaire.objects.prefetch_related('sections__questions').order_by('direction', 'phase', 'system_name')
    
    # ── Grouper par direction
    from collections import OrderedDict
    by_direction = OrderedDict()
    it_systems = []  # Systèmes où la DSI doit répondre (Questions Techniques)
    
    for q in all_qs:
        direction = q.direction or '(Non renseigné)'
        if direction not in by_direction:
            by_direction[direction] = []
        by_direction[direction].append(q)
        # Identifier les systèmes IT (DSI doit répondre)
        if 'DSI' in direction or 'technique' in q.system_name.lower():
            it_systems.append(q)
    
    # ── Construction du MD
    lines = []
    lines.append(f'# Rapport d\'avancement — Cartographie SI Air Algérie')
    lines.append(f'')
    lines.append(f'> Généré le **{date_str}** depuis le KPI Dashboard')
    lines.append(f'> URL : https://cartographie-si-airalgerie.onrender.com/kpi/')
    lines.append(f'')
    lines.append(f'---')
    lines.append(f'')
    
    # ── Synthèse globale
    lines.append(f'## 1. Synthèse globale')
    lines.append(f'')
    lines.append(f'| Indicateur | Valeur |')
    lines.append(f'|------------|--------|')
    lines.append(f'| Systèmes inventoriés | **{total_systems}** |')
    lines.append(f'| Systèmes avec flux documentés | **{systems_with_data}** / {total_systems} |')
    lines.append(f'| Questionnaires total | **{total_questionnaires}** |')
    lines.append(f'| Questionnaires terminés | **{q_completed}** ({int(q_completed/total_questionnaires*100) if total_questionnaires else 0}%) |')
    lines.append(f'| Questionnaires en cours | **{q_in_progress}** |')
    lines.append(f'| Questionnaires non commencés | **{q_not_started}** |')
    lines.append(f'| Questions répondues | **{total_answered}** / {total_questions} (**{questionnaire_progress}%**) |')
    lines.append(f'| Questions validées | **{total_validated}** / {total_questions} |')
    lines.append(f'| Flux de données documentés | **{total_flows}** |')
    lines.append(f'| Échantillons collectés | **{total_samples}** |')
    lines.append(f'')
    
    # ── Avancement par phase
    lines.append(f'---')
    lines.append(f'')
    lines.append(f'## 2. Avancement par phase')
    lines.append(f'')
    for p in phase_data:
        emoji = {1: '🔴', 2: '🟠', 3: '🟢'}.get(p['phase'], '')
        lines.append(f'### {p["label"]} {emoji}')
        lines.append(f'')
        lines.append(f'| Indicateur | Valeur |')
        lines.append(f'|------------|--------|')
        lines.append(f'| Systèmes | {p["total_systems"]} |')
        lines.append(f'| Terminés | **{p["completed"]}** |')
        lines.append(f'| En cours | {p["in_progress"]} |')
        lines.append(f'| Non commencés | {p["not_started"]} |')
        lines.append(f'| Questions répondues | {p["answered"]} / {p["total_questions"]} (**{p["progress"]}%**) |')
        lines.append(f'| Questions validées | {p["validated"]} / {p["total_questions"]} |')
        progress_bar = '█' * (p['progress'] // 5) + '░' * (20 - p['progress'] // 5)
        lines.append(f'| Progression | `{progress_bar}` {p["progress"]}% |')
        lines.append(f'')
    
    # ── Avancement par direction
    lines.append(f'---')
    lines.append(f'')
    lines.append(f'## 3. Avancement par direction')
    lines.append(f'')
    
    for direction, qs_list in by_direction.items():
        dir_total_q = sum(q.total_questions for q in qs_list)
        dir_answered = sum(q.answered_questions for q in qs_list)
        dir_progress = int(dir_answered / dir_total_q * 100) if dir_total_q > 0 else 0
        dir_completed = sum(1 for q in qs_list if q.status == 'COMPLETED')
        dir_in_progress = sum(1 for q in qs_list if q.status == 'IN_PROGRESS')
        dir_not_started = sum(1 for q in qs_list if q.status == 'NOT_STARTED')
        
        lines.append(f'### {direction}')
        lines.append(f'')
        lines.append(f'**{len(qs_list)} système(s)** — Progression globale : **{dir_progress}%** ({dir_answered}/{dir_total_q} questions) — ✅ {dir_completed} terminé(s), 🔄 {dir_in_progress} en cours, ⏳ {dir_not_started} non commencé(s)')
        lines.append(f'')
        lines.append(f'| Système | Phase | Key User | Questions | Progression | Statut |')
        lines.append(f'|---------|-------|----------|-----------|-------------|--------|')
        
        for q in qs_list:
            phase_tag = {1: 'P1 🔴', 2: 'P2 🟠', 3: 'P3 🟢'}.get(q.phase, f'P{q.phase}')
            ku = q.key_users[:40] if q.key_users else '—'
            progress = q.progress_percent
            answered = q.answered_questions
            total = q.total_questions
            if q.status == 'COMPLETED':
                status = '✅ Terminé'
            elif q.status == 'IN_PROGRESS':
                status = f'🔄 En cours ({progress}%)'
            else:
                status = '⏳ Non commencé'
            lines.append(f'| {q.system_name} | {phase_tag} | {ku} | {answered}/{total} | {progress}% | {status} |')
        
        lines.append(f'')
    
    # ── Systèmes IT / DSI
    lines.append(f'---')
    lines.append(f'')
    lines.append(f'## 4. Systèmes IT (DSI) — Avancement des réponses techniques')
    lines.append(f'')
    
    if it_systems:
        it_total_q = sum(q.total_questions for q in it_systems)
        it_answered = sum(q.answered_questions for q in it_systems)
        it_progress = int(it_answered / it_total_q * 100) if it_total_q > 0 else 0
        lines.append(f'**{len(it_systems)} système(s) IT** — Progression : **{it_progress}%** ({it_answered}/{it_total_q} questions)')
        lines.append(f'')
        lines.append(f'| Système | Key User | Éditeur | Questions | Progression | Statut |')
        lines.append(f'|---------|----------|---------|-----------|-------------|--------|')
        for q in it_systems:
            ku = q.key_users[:35] if q.key_users else '—'
            ed = q.editor[:25] if q.editor else '—'
            progress = q.progress_percent
            if q.status == 'COMPLETED':
                status = '✅ Terminé'
            elif q.status == 'IN_PROGRESS':
                status = f'🔄 En cours ({progress}%)'
            else:
                status = '⏳ Non commencé'
            lines.append(f'| {q.system_name} | {ku} | {ed} | {q.answered_questions}/{q.total_questions} | {progress}% | {status} |')
        lines.append(f'')
    else:
        lines.append(f'Aucun système IT identifié.')
        lines.append(f'')
    
    # ── Tableau complet de tous les systèmes
    lines.append(f'---')
    lines.append(f'')
    lines.append(f'## 5. Tableau complet — Tous les systèmes')
    lines.append(f'')
    lines.append(f'| # | Système | Direction | Phase | Key User | Questions | Progression | Statut |')
    lines.append(f'|---|---------|-----------|-------|----------|-----------|-------------|--------|')
    
    for i, q in enumerate(Questionnaire.objects.prefetch_related('sections__questions').order_by('phase', 'priority_in_phase'), 1):
        phase_tag = {1: 'P1 🔴', 2: 'P2 🟠', 3: 'P3 🟢'}.get(q.phase, f'P{q.phase}')
        ku = q.key_users[:30] if q.key_users else '—'
        direction = q.direction[:25] if q.direction else '—'
        progress = q.progress_percent
        if q.status == 'COMPLETED':
            status = '✅ Terminé'
        elif q.status == 'IN_PROGRESS':
            status = f'🔄 En cours'
        else:
            status = '⏳ Non commencé'
        lines.append(f'| {i} | {q.system_name} | {direction} | {phase_tag} | {ku} | {q.answered_questions}/{q.total_questions} | {progress}% | {status} |')
    
    lines.append(f'')
    lines.append(f'---')
    lines.append(f'')
    lines.append(f'*Rapport généré automatiquement le {date_str} — Cartographie SI Air Algérie — Alpha Aero Systems*')
    
    md_content = '\n'.join(lines)
    
    response = HttpResponse(md_content, content_type='text/markdown; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="rapport_avancement_cartographie_SI_{date_file}.md"'
    return response


def questionnaire_form_view(request, pk):
    """Formulaire de questionnaire — accès admin, key user ou auditeur"""
    is_admin = request.user.is_authenticated
    is_auditor = bool(request.session.get('auditor_token'))
    session_q_id = request.session.get('key_user_questionnaire_id')
    key_user_name = request.session.get('key_user_name', '')
    auditor_name = request.session.get('auditor_name', '')
    
    if not is_admin and not is_auditor and session_q_id != pk:
        return redirect('cartography:login')
    
    questionnaire = get_object_or_404(
        Questionnaire.objects.prefetch_related('sections__questions'),
        pk=pk
    )
    
    token = request.GET.get('token', '')
    
    if request.method == 'POST':
        # Auditor: handle validation + comments only
        if is_auditor:
            for key, value in request.POST.items():
                if key.startswith('validate_'):
                    q_id = key.replace('validate_', '')
                    try:
                        question = Question.objects.get(pk=q_id)
                        question.validation_status = value
                        question.validated_by = auditor_name
                        question.validated_at = timezone.now()
                        question.save()
                    except Question.DoesNotExist:
                        pass
                elif key.startswith('auditor_comment_'):
                    q_id = key.replace('auditor_comment_', '')
                    try:
                        question = Question.objects.get(pk=q_id)
                        if value.strip():
                            question.auditor_comment = value
                            question.auditor_comment_by = auditor_name
                            question.auditor_comment_at = timezone.now()
                            question.save()
                    except Question.DoesNotExist:
                        pass
            messages.success(request, f'Validation enregistrée pour « {questionnaire.system_name} ».')
            return redirect(f"{request.path}?saved=1")
        
        # Key user / admin: handle answers + notes + attachments
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
        
        # Handle file attachments — stockage binaire en BDD + anonymisation
        from .anonymizer import anonymize_bytes
        for key, f in request.FILES.items():
            if key.startswith('attachment_'):
                q_id = key.replace('attachment_', '')
                try:
                    question = Question.objects.get(pk=q_id)
                    content = f.read()
                    anonymized_content, was_anonymized, nb = anonymize_bytes(
                        content, f.name, getattr(f, 'content_type', '') or ''
                    )
                    question.attachment_data = anonymized_content
                    question.attachment_filename = f.name
                    question.attachment_content_type = getattr(f, 'content_type', '') or 'application/octet-stream'
                    question.attachment_size = len(anonymized_content)
                    question.attachment_anonymized = was_anonymized
                    question.attachment_uploaded_at = timezone.now()
                    # On neutralise l'ancien FileField (plus utilisé)
                    question.attachment = None
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
        'key_user_name': key_user_name,
        'is_admin': is_admin,
        'is_auditor': is_auditor,
        'auditor_name': auditor_name,
    }
    return render(request, 'cartography/questionnaire_form.html', context)


def question_attachment_download(request, question_id):
    """Streame la pièce jointe stockée en BDD (binary) avec son nom et type MIME d'origine."""
    question = get_object_or_404(Question, pk=question_id)
    # Contrôle d'accès : admin, auditeur (token) ou key user (token sur le questionnaire)
    is_admin = request.user.is_authenticated and request.user.is_staff
    is_auditor = bool(request.session.get('auditor_token'))
    questionnaire = question.section.questionnaire
    has_ku_token = False
    token = request.GET.get('token', '')
    if token:
        has_ku_token = KeyUserAccess.objects.filter(
            questionnaire=questionnaire, token=token, is_active=True
        ).exists()
    if not (is_admin or is_auditor or has_ku_token):
        return HttpResponse(status=403)

    if not question.attachment_data:
        return HttpResponse(status=404)

    response = HttpResponse(
        bytes(question.attachment_data),
        content_type=question.attachment_content_type or 'application/octet-stream',
    )
    filename = question.attachment_filename or f'attachment_{question.pk}'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response['Content-Length'] = str(question.attachment_size or len(question.attachment_data))
    return response


# ─── Process views ──────────────────────────────────────────────────────────

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required(login_url='/login/')
def processes_list(request):
    """Liste des process avec filtres"""
    processes = Process.objects.prefetch_related('structures', 'systems', 'steps').all()

    category = request.GET.get('category')
    status = request.GET.get('status')
    structure = request.GET.get('structure')
    system = request.GET.get('system')
    search = request.GET.get('search')

    if category:
        processes = processes.filter(category=category)
    if status:
        processes = processes.filter(status=status)
    if structure:
        processes = processes.filter(structures__id=structure).distinct()
    if system:
        processes = processes.filter(systems__id=system).distinct()
    if search:
        processes = processes.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(description__icontains=search) |
            Q(context__icontains=search)
        )

    context = {
        'processes': processes,
        'categories': Process.CATEGORY_CHOICES,
        'statuses': Process.STATUS_CHOICES,
        'structures': Structure.objects.all(),
        'systems_list': System.objects.all(),
        'selected_category': category,
        'selected_status': status,
        'selected_structure': structure,
        'selected_system': system,
        'search': search or '',
    }
    return render(request, 'cartography/process_list.html', context)


@staff_member_required(login_url='/login/')
def process_detail(request, pk):
    """Détail d'un process avec diagramme Mermaid"""
    process = get_object_or_404(
        Process.objects.prefetch_related('steps__systems_used', 'steps__actor_structure', 'structures', 'systems'),
        pk=pk
    )
    context = {
        'process': process,
        'steps': process.steps.all().order_by('order'),
    }
    return render(request, 'cartography/process_detail.html', context)


@staff_member_required(login_url='/login/')
def process_create(request):
    """Création d'un nouveau process"""
    if request.method == 'POST':
        import json as json_mod
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()
        description = request.POST.get('description', '').strip()
        context_text = request.POST.get('context', '').strip()
        category = request.POST.get('category', 'OPERATIONAL')
        structure_ids = request.POST.getlist('structures')
        system_ids = request.POST.getlist('systems')

        if not name or not code:
            messages.error(request, 'Le nom et le code sont obligatoires.')
            return render(request, 'cartography/process_form.html', {
                'categories': Process.CATEGORY_CHOICES,
                'structures': Structure.objects.all(),
                'systems_list': System.objects.all(),
            })

        process = Process.objects.create(
            name=name,
            code=code,
            description=description,
            context=context_text,
            category=category,
            created_by=request.user.username if request.user.is_authenticated else '',
        )
        if structure_ids:
            process.structures.set(structure_ids)
        if system_ids:
            process.systems.set(system_ids)

        messages.success(request, f'Process « {name} » créé avec succès.')
        return redirect('cartography:process_detail', pk=process.pk)

    context = {
        'categories': Process.CATEGORY_CHOICES,
        'structures': Structure.objects.all(),
        'systems_list': System.objects.all(),
    }
    return render(request, 'cartography/process_form.html', context)


@staff_member_required(login_url='/login/')
def process_edit(request, pk):
    """Édition d'un process existant"""
    process = get_object_or_404(Process, pk=pk)

    if request.method == 'POST':
        process.name = request.POST.get('name', process.name).strip()
        process.code = request.POST.get('code', process.code).strip()
        process.description = request.POST.get('description', '').strip()
        process.context = request.POST.get('context', '').strip()
        process.category = request.POST.get('category', process.category)
        process.status = request.POST.get('status', process.status)
        process.problems = request.POST.get('problems', '').strip()
        process.recommendations = request.POST.get('recommendations', '').strip()
        process.save()

        structure_ids = request.POST.getlist('structures')
        system_ids = request.POST.getlist('systems')
        if structure_ids:
            process.structures.set(structure_ids)
        if system_ids:
            process.systems.set(system_ids)

        messages.success(request, f'Process « {process.name} » mis à jour.')
        return redirect('cartography:process_detail', pk=process.pk)

    context = {
        'process': process,
        'categories': Process.CATEGORY_CHOICES,
        'statuses': Process.STATUS_CHOICES,
        'structures': Structure.objects.all(),
        'systems_list': System.objects.all(),
    }
    return render(request, 'cartography/process_form.html', context)


@staff_member_required(login_url='/login/')
def api_process_generate_workflow(request, pk):
    """API: génère le workflow IA à partir du contexte du process"""
    import json as json_mod

    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)

    process = get_object_or_404(Process, pk=pk)

    if not process.context.strip():
        return JsonResponse({'error': 'Le champ contexte est vide. Décrivez le process avant de générer.'}, status=400)

    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        return JsonResponse({'error': 'Clé API Anthropic non configurée (ANTHROPIC_API_KEY).'}, status=500)

    try:
        from .services.process_workflow_generator import ProcessWorkflowGenerator

        # Préparer les données existantes pour le matching
        existing_structures = list(Structure.objects.values('code', 'name'))
        existing_systems = list(System.objects.values('code', 'name', 'description'))

        generator = ProcessWorkflowGenerator(api_key)
        result = generator.generate(
            process_name=process.name,
            context_text=process.context,
            existing_structures=existing_structures,
            existing_systems=existing_systems,
        )

        # Sauvegarder le workflow
        process.workflow_json = result.get('steps', [])
        process.workflow_mermaid = result.get('mermaid', '')
        process.problems = result.get('problems', process.problems)
        process.recommendations = result.get('recommendations', process.recommendations)
        process.ai_generated = True
        process.save()

        # Créer les ProcessStep en base
        process.steps.all().delete()  # Supprimer les anciennes étapes
        steps_data = result.get('steps', [])

        for step_data in steps_data:
            step = ProcessStep.objects.create(
                process=process,
                order=step_data.get('order', 0),
                title=step_data.get('title', ''),
                description=step_data.get('description', ''),
                step_type=step_data.get('step_type', 'MANUAL'),
                actor_role=step_data.get('actor_role', ''),
                data_inputs=step_data.get('data_inputs', ''),
                data_outputs=step_data.get('data_outputs', ''),
                interactions=step_data.get('interactions', ''),
                problems=step_data.get('problems', ''),
                duration_estimate=step_data.get('duration_estimate', ''),
                next_steps=step_data.get('next_steps', []),
            )

            # Rattacher la structure si code valide
            struct_code = step_data.get('actor_structure_code')
            if struct_code:
                try:
                    step.actor_structure = Structure.objects.get(code=struct_code)
                    step.save()
                except Structure.DoesNotExist:
                    pass

            # Rattacher les systèmes
            sys_names = step_data.get('systems_used', [])
            for sys_name in sys_names:
                try:
                    system = System.objects.get(name__iexact=sys_name)
                    step.systems_used.add(system)
                except System.DoesNotExist:
                    # Essai fuzzy par contenu
                    matches = System.objects.filter(name__icontains=sys_name.split()[0] if sys_name else '')
                    if matches.exists():
                        step.systems_used.add(matches.first())

        # Auto-set structures and systems on the process
        all_struct_ids = set(process.structures.values_list('id', flat=True))
        all_sys_ids = set(process.systems.values_list('id', flat=True))
        for step in process.steps.all():
            if step.actor_structure:
                all_struct_ids.add(step.actor_structure.id)
            all_sys_ids.update(step.systems_used.values_list('id', flat=True))
        process.structures.set(all_struct_ids)
        process.systems.set(all_sys_ids)

        return JsonResponse({
            'success': True,
            'steps_count': len(steps_data),
            'mermaid': process.workflow_mermaid,
            'problems': process.problems,
            'recommendations': process.recommendations,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required(login_url='/login/')
def api_process_save_mermaid(request, pk):
    """API: sauvegarde le code Mermaid édité manuellement"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)

    import json as json_mod
    process = get_object_or_404(Process, pk=pk)

    try:
        data = json_mod.loads(request.body)
        mermaid_code = data.get('mermaid', '')
        process.workflow_mermaid = mermaid_code
        process.save(update_fields=['workflow_mermaid', 'updated_at'])
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
