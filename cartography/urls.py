from django.urls import path
from . import views

app_name = 'cartography'

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('key-user/', views.key_user_login, name='key_user_login'),
    path('auditor/', views.auditor_login, name='auditor_login'),
    path('division/', views.division_login, name='division_login'),
    path('division/dashboard/', views.division_dashboard, name='division_dashboard'),
    path('division/questionnaire/<int:pk>/', views.division_questionnaire_view, name='division_questionnaire'),
    
    path('', views.dashboard, name='dashboard'),
    path('systems/', views.systems_list, name='systems_list'),
    path('systems/<int:pk>/', views.system_detail, name='system_detail'),
    path('flows/', views.flows_list, name='flows_list'),
    path('flows/<int:pk>/', views.flow_detail, name='flow_detail'),
    path('graph/', views.graph_view, name='graph'),
    path('structures/', views.structures_list, name='structures_list'),
    path('messages/', views.messages_list, name='messages_list'),
    path('messages/<int:pk>/', views.message_detail, name='message_detail'),
    path('domains/', views.domains_list, name='domains_list'),
    
    # Validation - Hypothèse vs Réalité
    path('validation/', views.validation_dashboard, name='validation_dashboard'),
    path('validation/samples/', views.samples_list, name='samples_list'),
    path('validation/samples/<int:pk>/', views.sample_detail, name='sample_detail'),
    path('validation/flow/<int:flow_pk>/', views.flow_validation_view, name='flow_validation'),
    
    # Découverte des données
    path('data-discovery/', views.data_discovery_view, name='data_discovery'),
    
    # Référentiels
    path('referentials/', views.referentials_list, name='referentials_list'),
    path('referentials/<int:pk>/', views.referential_detail, name='referential_detail'),
    
    # Rapports
    path('reports/data-gaps/', views.data_gaps_report, name='data_gaps_report'),
    path('reports/ai/', views.ai_report_view, name='ai_report'),
    path('reports/ai/pdf/', views.ai_report_pdf_view, name='ai_report_pdf'),
    path('database-schema/', views.database_schema_view, name='database_schema'),
    
    # Historique des imports
    path('import-history/', views.import_history_list, name='import_history_list'),
    path('import-history/<int:pk>/', views.import_history_detail, name='import_history_detail'),
    
    # Questionnaires
    path('questionnaires/', views.questionnaires_list, name='questionnaires_list'),
    path('questionnaires/<int:pk>/', views.questionnaire_detail, name='questionnaire_detail'),
    
    # Organigramme
    path('organigramme/', views.organigramme_view, name='organigramme'),
    
    # KPI Dashboard
    path('kpi/', views.kpi_dashboard_view, name='kpi_dashboard'),
    path('kpi/export-md/', views.export_kpi_md, name='export_kpi_md'),
    
    # Questionnaire form (public access for key users)
    path('form/<int:pk>/', views.questionnaire_form_view, name='questionnaire_form'),
    
    # API endpoints for graph data
    path('api/graph-data/', views.api_graph_data, name='api_graph_data'),
    path('api/graph-data-validation/', views.api_graph_data_with_validation, name='api_graph_data_validation'),
    path('api/system/<int:pk>/', views.api_system_detail, name='api_system_detail'),
    path('api/flow/<int:pk>/', views.api_flow_detail, name='api_flow_detail'),
    path('api/validation-stats/', views.api_validation_stats, name='api_validation_stats'),
    path('api/database-schema/', views.api_database_schema, name='api_database_schema'),
    path('api/save-answer/', views.api_save_answer, name='api_save_answer'),
    path('api/kpi-stats/', views.api_kpi_stats, name='api_kpi_stats'),
]
