from django.contrib import admin
from .models import (
    Structure, SystemCategory, System, DataFlow, 
    DataField, MessageFormat, MessageField, DataDomain,
    Questionnaire, QuestionSection, Question, KeyUserAccess, AuditorAccess, DivisionAccess,
    Process, ProcessStep
)


@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'parent', 'level', 'responsable']
    list_filter = ['level']
    search_fields = ['code', 'name', 'responsable']


@admin.register(SystemCategory)
class SystemCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    ordering = ['order']


class DataFieldInline(admin.TabularInline):
    model = DataField
    extra = 1


@admin.register(System)
class SystemAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'vendor', 'category', 'structure', 'criticality']
    list_filter = ['category', 'structure', 'criticality', 'mode']
    search_fields = ['code', 'name', 'vendor']


@admin.register(DataFlow)
class DataFlowAdmin(admin.ModelAdmin):
    list_display = ['name', 'source', 'target', 'frequency', 'protocol', 'is_automated']
    list_filter = ['frequency', 'protocol', 'is_automated', 'is_critical']
    search_fields = ['name', 'source__name', 'target__name']
    inlines = [DataFieldInline]


class MessageFieldInline(admin.TabularInline):
    model = MessageField
    extra = 1


@admin.register(MessageFormat)
class MessageFormatAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'standard']
    inlines = [MessageFieldInline]


@admin.register(DataDomain)
class DataDomainAdmin(admin.ModelAdmin):
    list_display = ['name', 'master_system', 'criticality']
    filter_horizontal = ['consumer_systems']


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ['number', 'text', 'answer', 'is_answered', 'attachment', 'order']
    readonly_fields = ['is_answered']


class QuestionSectionInline(admin.TabularInline):
    model = QuestionSection
    extra = 0
    show_change_link = True


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ['system_name', 'phase', 'priority_in_phase', 'editor', 'status', 'progress_percent']
    list_filter = ['phase', 'status']
    search_fields = ['system_name', 'editor', 'key_users']
    inlines = [QuestionSectionInline]


@admin.register(QuestionSection)
class QuestionSectionAdmin(admin.ModelAdmin):
    list_display = ['questionnaire', 'title', 'order']
    list_filter = ['questionnaire']
    inlines = [QuestionInline]


@admin.register(KeyUserAccess)
class KeyUserAccessAdmin(admin.ModelAdmin):
    list_display = ['name', 'questionnaire', 'email', 'token', 'is_active', 'last_accessed']
    list_filter = ['is_active', 'questionnaire']
    search_fields = ['name', 'email', 'token']
    readonly_fields = ['token', 'created_at', 'last_accessed']


@admin.register(AuditorAccess)
class AuditorAccessAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'token', 'is_active', 'last_accessed']
    list_filter = ['is_active']
    search_fields = ['name', 'email', 'token']
    readonly_fields = ['token', 'created_at', 'last_accessed']


@admin.register(DivisionAccess)
class DivisionAccessAdmin(admin.ModelAdmin):
    list_display = ['name', 'structure', 'email', 'token', 'is_active', 'last_accessed']
    list_filter = ['is_active', 'structure']
    search_fields = ['name', 'email', 'token', 'structure__code']
    readonly_fields = ['token', 'created_at', 'last_accessed']


class ProcessStepInline(admin.TabularInline):
    model = ProcessStep
    extra = 0
    fields = ['order', 'title', 'step_type', 'actor_role', 'actor_structure', 'duration_estimate']
    ordering = ['order']


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'status', 'step_count', 'ai_generated', 'updated_at']
    list_filter = ['category', 'status', 'ai_generated']
    search_fields = ['code', 'name', 'description', 'context']
    filter_horizontal = ['structures', 'systems']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ProcessStepInline]
    fieldsets = (
        (None, {'fields': ('code', 'name', 'description', 'category', 'status', 'created_by')}),
        ('Contexte entretien', {'fields': ('context', 'source_questionnaire'), 'classes': ('collapse',)}),
        ('Périmètre', {'fields': ('structures', 'systems')}),
        ('Analyse', {'fields': ('problems', 'recommendations')}),
        ('Workflow IA', {'fields': ('workflow_mermaid', 'workflow_json', 'ai_generated'), 'classes': ('collapse',)}),
        ('Métadonnées', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(ProcessStep)
class ProcessStepAdmin(admin.ModelAdmin):
    list_display = ['process', 'order', 'title', 'step_type', 'actor_role', 'actor_structure']
    list_filter = ['step_type', 'actor_structure', 'process']
    search_fields = ['title', 'description', 'actor_role']
    filter_horizontal = ['systems_used']
