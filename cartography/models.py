from django.db import models


COUNTRY_CHOICES = [
    ('DZ', 'Algérie'),
    ('FR', 'France'),
    ('EU', 'Europe (autre)'),
    ('INTL', 'International/Cloud'),
]


class Structure(models.Model):
    """Structure organisationnelle (Direction, Service)"""
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6366f1')
    country = models.CharField(max_length=10, choices=COUNTRY_CHOICES, default='DZ', help_text="Pays où la structure est localisée")
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children', help_text="Structure parente (ex: Direction parente d'un Service)")
    level = models.CharField(max_length=30, blank=True, default='', help_text="Niveau hiérarchique (PDG, DGA, Direction, Sous-direction, Service)")
    responsable = models.CharField(max_length=200, blank=True, help_text="Nom du responsable de la structure")
    
    class Meta:
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class SystemCategory(models.Model):
    """Catégorie de système"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='server')
    color = models.CharField(max_length=7, default='#3b82f6')
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name_plural = "System Categories"
    
    def __str__(self):
        return self.name


class System(models.Model):
    """Système informatique"""
    CRITICALITY_CHOICES = [
        ('CRITIQUE', 'Critique'),
        ('HAUTE', 'Haute'),
        ('MOYENNE', 'Moyenne'),
        ('BASSE', 'Basse'),
    ]
    
    MODE_CHOICES = [
        ('SAAS', 'SaaS'),
        ('CLOUD', 'Cloud Hébergé'),
        ('ONPREMISE', 'On-Premise'),
        ('INHOUSE', 'In-House'),
        ('RESEAU', 'Réseau'),
    ]
    
    inventory_id = models.IntegerField(null=True, blank=True)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    vendor = models.CharField(max_length=200)
    category = models.ForeignKey(SystemCategory, on_delete=models.CASCADE, related_name='systems')
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE, related_name='systems')
    criticality = models.CharField(max_length=20, choices=CRITICALITY_CHOICES, default='MOYENNE')
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='ONPREMISE')
    country = models.CharField(max_length=10, choices=COUNTRY_CHOICES, default='DZ', help_text="Pays où le système est installé/hébergé")
    is_master_for = models.TextField(blank=True, help_text="Domaines de données dont ce système est la source de vérité")
    version = models.CharField(max_length=50, blank=True)
    modules = models.JSONField(default=list, blank=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return self.name
    
    @property
    def criticality_color(self):
        colors = {
            'CRITIQUE': '#ef4444',
            'HAUTE': '#f97316',
            'MOYENNE': '#eab308',
            'BASSE': '#22c55e',
        }
        return colors.get(self.criticality, '#6b7280')


class DataFlow(models.Model):
    """Flux de données entre systèmes"""
    FREQUENCY_CHOICES = [
        ('REALTIME', 'Temps réel'),
        ('CONTINUOUS', 'Continu'),
        ('DAILY', 'Quotidien'),
        ('WEEKLY', 'Hebdomadaire'),
        ('MONTHLY', 'Mensuel'),
        ('BATCH', 'Batch'),
        ('ONDEMAND', 'À la demande'),
    ]
    
    PROTOCOL_CHOICES = [
        ('API_REST', 'API REST'),
        ('API_SOAP', 'API SOAP'),
        ('FILE', 'Fichier'),
        ('MESSAGE', 'Message IATA'),
        ('DATABASE', 'Base de données'),
        ('MANUAL', 'Manuel'),
        ('PROPRIETARY', 'Propriétaire'),
    ]
    
    source = models.ForeignKey(System, on_delete=models.CASCADE, related_name='outgoing_flows')
    target = models.ForeignKey(System, on_delete=models.CASCADE, related_name='incoming_flows')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='DAILY')
    protocol = models.CharField(max_length=20, choices=PROTOCOL_CHOICES, default='PROPRIETARY')
    format = models.CharField(max_length=100, blank=True, help_text="Format des données (SSIM, MVT, JSON, etc.)")
    is_automated = models.BooleanField(default=True)
    is_critical = models.BooleanField(default=False)
    volume = models.CharField(max_length=100, blank=True, help_text="Volume de données (ex: ~35 fichiers/jour)")
    
    class Meta:
        ordering = ['source', 'target']
    
    def __str__(self):
        return f"{self.source.code} → {self.target.code}: {self.name}"


class DataField(models.Model):
    """Champ de données échangé dans un flux"""
    FIELD_TYPE_CHOICES = [
        ('STRING', 'Chaîne'),
        ('INTEGER', 'Entier'),
        ('DECIMAL', 'Décimal'),
        ('DATE', 'Date'),
        ('DATETIME', 'Date/Heure'),
        ('BOOLEAN', 'Booléen'),
        ('ALPHANUM', 'Alphanumérique'),
    ]
    
    flow = models.ForeignKey(DataFlow, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES, default='STRING')
    length = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    is_mandatory = models.BooleanField(default=True)
    example = models.CharField(max_length=200, blank=True)
    position = models.IntegerField(null=True, blank=True, help_text="Position dans le message (pour formats positionnels)")
    
    class Meta:
        ordering = ['flow', 'position', 'name']
    
    def __str__(self):
        return f"{self.flow.name}.{self.name}"


class MessageFormat(models.Model):
    """Format de message standard (IATA, etc.)"""
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    standard = models.CharField(max_length=50, default='IATA')
    example = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class MessageField(models.Model):
    """Champ d'un format de message standard"""
    message_format = models.ForeignKey(MessageFormat, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=100)
    position_start = models.IntegerField(null=True, blank=True)
    position_end = models.IntegerField(null=True, blank=True)
    length = models.IntegerField(null=True, blank=True)
    field_type = models.CharField(max_length=50)
    description = models.TextField()
    example = models.CharField(max_length=200, blank=True)
    is_mandatory = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['message_format', 'position_start', 'name']
    
    def __str__(self):
        return f"{self.message_format.code}.{self.name}"


class DataDomain(models.Model):
    """Domaine de données avec système maître"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    master_system = models.ForeignKey(System, on_delete=models.CASCADE, related_name='mastered_domains')
    consumer_systems = models.ManyToManyField(System, related_name='consumed_domains', blank=True)
    criticality = models.CharField(max_length=20, default='HAUTE')
    
    def __str__(self):
        return f"{self.name} (Master: {self.master_system.code})"


class DataSample(models.Model):
    """Échantillon de données réelles importées pour validation"""
    SOURCE_SYSTEM_CHOICES = [
        ('AIMS', 'AIMS'),
        ('AMADEUS', 'AMADEUS'),
        ('RAPID', 'RAPID'),
        ('ALTEA', 'ALTEA'),
        ('AMOS', 'AMOS'),
        ('ACCELYA', 'ACCELYA'),
        ('OTHER', 'Autre'),
    ]
    
    DATA_TYPE_CHOICES = [
        ('FLT', 'Flight Schedule (FLT)'),
        ('APS', 'Amadeus Payment (APS)'),
        ('PNR', 'PNR Data Feed'),
        ('FLP', 'FLP Transport'),
        ('IBP', 'Interline Billing (IBP)'),
        ('SLP', 'Sales Report (SLP)'),
        ('LIFT', 'LIFT File'),
        ('MVT', 'Movement Message'),
        ('SSIM', 'SSIM Schedule'),
        ('OTHER', 'Autre'),
    ]
    
    name = models.CharField(max_length=200)
    source_system = models.CharField(max_length=50, choices=SOURCE_SYSTEM_CHOICES)
    data_type = models.CharField(max_length=50, choices=DATA_TYPE_CHOICES)
    description = models.TextField(blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    imported_at = models.DateTimeField(auto_now_add=True)
    sample_date = models.DateField(null=True, blank=True, help_text="Date des données échantillon")
    record_count = models.IntegerField(default=0)
    
    # Stockage des données réelles
    columns_json = models.JSONField(default=list, blank=True, help_text="Liste des colonnes découvertes")
    sample_rows_json = models.JSONField(default=list, blank=True, help_text="Quelques lignes d'exemple")
    column_stats_json = models.JSONField(default=dict, blank=True, help_text="Stats par colonne (type, exemples)")
    
    class Meta:
        ordering = ['-imported_at']
    
    def __str__(self):
        return f"{self.source_system} - {self.data_type} ({self.imported_at.strftime('%Y-%m-%d')})"


class FlowFieldHypothesis(models.Model):
    """Hypothèse sur un champ de flux - ce qu'on pense qu'il contient"""
    STATUS_CHOICES = [
        ('HYPOTHESIS', 'Hypothèse'),
        ('CONFIRMED', 'Confirmé'),
        ('PARTIAL', 'Partiellement confirmé'),
        ('INCORRECT', 'Incorrect'),
    ]
    
    flow = models.ForeignKey(DataFlow, on_delete=models.CASCADE, related_name='field_hypotheses')
    field_name = models.CharField(max_length=100)
    hypothesis_type = models.CharField(max_length=50, blank=True, help_text="Type supposé")
    hypothesis_format = models.CharField(max_length=200, blank=True, help_text="Format supposé")
    hypothesis_description = models.TextField(blank=True)
    hypothesis_example = models.CharField(max_length=500, blank=True)
    
    # Données réelles observées
    real_type = models.CharField(max_length=50, blank=True)
    real_format = models.CharField(max_length=200, blank=True)
    real_description = models.TextField(blank=True)
    real_example = models.CharField(max_length=500, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='HYPOTHESIS')
    validated_from_sample = models.ForeignKey(DataSample, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['flow', 'field_name']
        unique_together = ['flow', 'field_name']
    
    def __str__(self):
        return f"{self.flow.name}.{self.field_name} [{self.status}]"
    
    @property
    def has_discrepancy(self):
        """Vérifie s'il y a une différence entre hypothèse et réalité"""
        if not self.real_type and not self.real_format:
            return False
        return (self.hypothesis_type != self.real_type) or (self.hypothesis_format != self.real_format)


class ReferenceData(models.Model):
    """Référentiel de données utilisé par les flux"""
    REFERENTIAL_TYPE_CHOICES = [
        ('CODE', 'Code de référence'),
        ('TABLE', 'Table de correspondance'),
        ('ENUM', 'Énumération'),
        ('STANDARD', 'Standard (IATA, ISO, etc.)'),
        ('INTERNAL', 'Référentiel interne'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    referential_type = models.CharField(max_length=20, choices=REFERENTIAL_TYPE_CHOICES, default='CODE')
    standard = models.CharField(max_length=100, blank=True, help_text="Standard de référence (IATA, ISO, etc.)")
    master_system = models.ForeignKey(System, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_referentials')
    example_values = models.JSONField(default=list, blank=True, help_text="Exemples de valeurs")
    is_mandatory = models.BooleanField(default=False, help_text="Référentiel obligatoire pour les flux")
    documentation_url = models.URLField(blank=True)
    
    class Meta:
        ordering = ['code']
        verbose_name = "Référentiel"
        verbose_name_plural = "Référentiels"
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class FlowReferential(models.Model):
    """Association entre un flux et ses référentiels requis"""
    USAGE_CHOICES = [
        ('INPUT', 'Entrée'),
        ('OUTPUT', 'Sortie'),
        ('VALIDATION', 'Validation'),
        ('TRANSFORMATION', 'Transformation'),
    ]
    
    flow = models.ForeignKey(DataFlow, on_delete=models.CASCADE, related_name='referentials')
    reference_data = models.ForeignKey(ReferenceData, on_delete=models.CASCADE, related_name='used_in_flows')
    usage = models.CharField(max_length=20, choices=USAGE_CHOICES, default='INPUT')
    field_name = models.CharField(max_length=100, blank=True, help_text="Champ du flux utilisant ce référentiel")
    is_present_in_sample = models.BooleanField(default=False, help_text="Référentiel présent dans les échantillons")
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['flow', 'reference_data']
        unique_together = ['flow', 'reference_data', 'field_name']
    
    def __str__(self):
        return f"{self.flow.name} → {self.reference_data.code}"


class DataImportHistory(models.Model):
    """Historique des imports de données et leurs apports"""
    IMPORT_TYPE_CHOICES = [
        ('DATAFEED', 'Datafeeds'),
        ('SYSTEM', 'Systèmes'),
        ('FLOW', 'Flux de données'),
        ('FORMAT', 'Formats de messages'),
        ('SAMPLE', 'Échantillons'),
        ('REFERENTIAL', 'Référentiels'),
        ('OTHER', 'Autre'),
    ]
    
    STATUS_CHOICES = [
        ('SUCCESS', 'Succès'),
        ('PARTIAL', 'Partiel'),
        ('FAILED', 'Échec'),
    ]
    
    date = models.DateField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    import_type = models.CharField(max_length=20, choices=IMPORT_TYPE_CHOICES, default='DATAFEED')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUCCESS')
    source_folder = models.CharField(max_length=500, blank=True, help_text="Dossier source des données")
    
    # Statistiques d'import
    systems_added = models.IntegerField(default=0)
    flows_added = models.IntegerField(default=0)
    formats_added = models.IntegerField(default=0)
    fields_added = models.IntegerField(default=0)
    samples_added = models.IntegerField(default=0)
    
    # Détails des éléments ajoutés
    details_json = models.JSONField(default=dict, blank=True, help_text="Détails des éléments ajoutés")
    files_processed = models.JSONField(default=list, blank=True, help_text="Liste des fichiers traités")
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = "Historique d'import"
        verbose_name_plural = "Historiques d'imports"
    
    def __str__(self):
        return f"{self.date} - {self.title}"
    
    @property
    def total_items_added(self):
        return self.systems_added + self.flows_added + self.formats_added + self.fields_added + self.samples_added


class Questionnaire(models.Model):
    """Questionnaire pour un système — support d'entretien avec les key users"""
    PHASE_CHOICES = [
        (1, 'Phase 1 — Critique 🔴'),
        (2, 'Phase 2 — Important 🟠'),
        (3, 'Phase 3 — Standard 🟢'),
    ]
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Non commencé'),
        ('IN_PROGRESS', 'En cours'),
        ('COMPLETED', 'Terminé'),
    ]
    
    system = models.OneToOneField(System, on_delete=models.CASCADE, related_name='questionnaire', null=True, blank=True)
    system_name = models.CharField(max_length=200)
    phase = models.IntegerField(choices=PHASE_CHOICES, default=1)
    priority_in_phase = models.IntegerField(default=1)
    editor = models.CharField(max_length=200, blank=True)
    direction = models.CharField(max_length=200, blank=True)
    key_users = models.TextField(blank=True, help_text="Key Users principaux")
    key_users_backup = models.TextField(blank=True, help_text="Key Users backup")
    responsible = models.TextField(blank=True, help_text="Responsable hiérarchique")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    interview_date = models.DateTimeField(null=True, blank=True)
    interview_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['phase', 'priority_in_phase']
    
    def __str__(self):
        return f"[P{self.phase}#{self.priority_in_phase}] {self.system_name}"
    
    @property
    def phase_color(self):
        return {1: '#ef4444', 2: '#f97316', 3: '#22c55e'}.get(self.phase, '#6b7280')
    
    @property
    def phase_label(self):
        return {1: 'Phase 1 🔴', 2: 'Phase 2 🟠', 3: 'Phase 3 🟢'}.get(self.phase, '')
    
    @property
    def total_questions(self):
        return Question.objects.filter(section__questionnaire=self).count()
    
    @property
    def answered_questions(self):
        if self.status == 'COMPLETED':
            return self.total_questions
        return Question.objects.filter(section__questionnaire=self).exclude(answer='').count()
    
    @property
    def progress_percent(self):
        total = self.total_questions
        if total == 0:
            return 0
        return int((self.answered_questions / total) * 100)
    
    @property
    def validated_questions(self):
        return Question.objects.filter(section__questionnaire=self, validation_status='VALIDATED').count()
    
    @property
    def rejected_questions(self):
        return Question.objects.filter(section__questionnaire=self, validation_status='REJECTED').count()
    
    @property
    def validation_percent(self):
        total = self.total_questions
        if total == 0:
            return 0
        return int((self.validated_questions / total) * 100)


class QuestionSection(models.Model):
    """Section de questions dans un questionnaire (ex: Module Reservation, Processus transverses)"""
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.questionnaire.system_name} — {self.title}"


class Question(models.Model):
    """Question individuelle dans une section"""
    VALIDATION_CHOICES = [
        ('PENDING', 'En attente'),
        ('VALIDATED', 'Validée'),
        ('REJECTED', 'Rejetée / À revoir'),
        ('REVISED', 'Révisée'),
    ]
    
    section = models.ForeignKey(QuestionSection, on_delete=models.CASCADE, related_name='questions')
    number = models.CharField(max_length=10, help_text="Numéro de la question (Q1, Q2...)")
    text = models.TextField()
    answer = models.TextField(blank=True)
    notes = models.TextField(blank=True, help_text="Notes prises pendant l'entretien")
    is_answered = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    # Validation
    validation_status = models.CharField(max_length=20, choices=VALIDATION_CHOICES, default='PENDING')
    validated_by = models.CharField(max_length=200, blank=True, help_text="Nom du validateur")
    validated_at = models.DateTimeField(null=True, blank=True)
    validation_comment = models.TextField(blank=True, help_text="Commentaire de validation ou motif de rejet")
    
    # Pièce jointe — déprécié (filesystem Render éphémère, remplacé par binary storage)
    attachment = models.FileField(upload_to='question_attachments/', blank=True, null=True, help_text="[DÉPRÉCIÉ] utiliser attachment_data")
    
    # Pièce jointe — stockage binaire en BDD + anonymisation
    attachment_data = models.BinaryField(blank=True, null=True, help_text="Contenu binaire de la pièce jointe (anonymisé si possible)")
    attachment_filename = models.CharField(max_length=255, blank=True, help_text="Nom de fichier original")
    attachment_content_type = models.CharField(max_length=100, blank=True, help_text="Type MIME")
    attachment_size = models.PositiveIntegerField(null=True, blank=True, help_text="Taille en octets (après anonymisation)")
    attachment_anonymized = models.BooleanField(default=False, help_text="Contenu anonymisé (texte)")
    attachment_uploaded_at = models.DateTimeField(null=True, blank=True)
    
    # Commentaire auditeur
    auditor_comment = models.TextField(blank=True, help_text="Commentaire de l'auditeur")
    auditor_comment_by = models.CharField(max_length=200, blank=True)
    auditor_comment_at = models.DateTimeField(null=True, blank=True)
    
    # Historique des révisions (JSON: [{date, answer, validated_by, action}])
    revision_history = models.JSONField(default=list, blank=True, help_text="Historique des modifications")
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.number} — {self.text[:80]}"
    
    def save(self, *args, **kwargs):
        self.is_answered = bool(self.answer.strip())
        super().save(*args, **kwargs)


class KeyUserAccess(models.Model):
    """Accès key user — token unique pour remplir un questionnaire"""
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name='access_tokens')
    name = models.CharField(max_length=200, help_text="Nom du key user")
    email = models.EmailField(blank=True)
    token = models.CharField(max_length=64, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['questionnaire', 'name']
        verbose_name = "Accès Key User"
        verbose_name_plural = "Accès Key Users"
    
    def __str__(self):
        return f"{self.name} → {self.questionnaire.system_name}"
    
    def save(self, *args, **kwargs):
        if not self.token:
            import secrets
            self.token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)


class AuditorAccess(models.Model):
    """Accès auditeur — token unique pour consulter KPI + questionnaires et valider/commenter"""
    name = models.CharField(max_length=200, help_text="Nom de l'auditeur")
    email = models.EmailField(blank=True)
    token = models.CharField(max_length=64, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Accès Auditeur"
        verbose_name_plural = "Accès Auditeurs"
    
    def __str__(self):
        return f"Auditeur: {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.token:
            import secrets
            self.token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)


class DivisionAccess(models.Model):
    """Accès division — token unique pour consulter l'avancement des questionnaires de sa division"""
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE, related_name='division_tokens',
                                  help_text="Division rattachée")
    name = models.CharField(max_length=200, help_text="Nom du responsable division")
    email = models.EmailField(blank=True)
    token = models.CharField(max_length=64, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['structure', 'name']
        verbose_name = "Accès Division"
        verbose_name_plural = "Accès Divisions"
    
    def __str__(self):
        return f"{self.name} → {self.structure.code}"
    
    def save(self, *args, **kwargs):
        if not self.token:
            import secrets
            self.token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)


class FlowValidation(models.Model):
    """Validation d'un flux complet basée sur des échantillons"""
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('VALIDATED', 'Validé'),
        ('PARTIAL', 'Partiellement validé'),
        ('ISSUES', 'Problèmes détectés'),
    ]
    
    flow = models.ForeignKey(DataFlow, on_delete=models.CASCADE, related_name='validations')
    sample = models.ForeignKey(DataSample, on_delete=models.CASCADE, related_name='flow_validations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Comparaison hypothèse vs réalité
    hypothesis_frequency = models.CharField(max_length=50, blank=True)
    real_frequency = models.CharField(max_length=50, blank=True)
    hypothesis_protocol = models.CharField(max_length=50, blank=True)
    real_protocol = models.CharField(max_length=50, blank=True)
    hypothesis_format = models.CharField(max_length=100, blank=True)
    real_format = models.CharField(max_length=100, blank=True)
    hypothesis_volume = models.CharField(max_length=100, blank=True)
    real_volume = models.CharField(max_length=100, blank=True)
    
    fields_confirmed = models.IntegerField(default=0)
    fields_with_issues = models.IntegerField(default=0)
    fields_new_discovered = models.IntegerField(default=0)
    
    notes = models.TextField(blank=True)
    validated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-validated_at']
        unique_together = ['flow', 'sample']
    
    def __str__(self):
        return f"{self.flow.name} - {self.sample.name} [{self.status}]"
    
    @property
    def match_percentage(self):
        """Pourcentage de correspondance entre hypothèse et réalité"""
        total = self.fields_confirmed + self.fields_with_issues
        if total == 0:
            return 0
        return int((self.fields_confirmed / total) * 100)


class Process(models.Model):
    """Process métier documenté lors des entretiens"""
    STATUS_CHOICES = [
        ('DRAFT', 'Brouillon'),
        ('DOCUMENTED', 'Documenté'),
        ('VALIDATED', 'Validé'),
        ('TO_BE', 'Cible (TO-BE)'),
    ]
    CATEGORY_CHOICES = [
        ('OPERATIONAL', 'Opérationnel'),
        ('SUPPORT', 'Support'),
        ('MANAGEMENT', 'Management'),
        ('COMMERCIAL', 'Commercial'),
        ('MAINTENANCE', 'Maintenance'),
        ('FINANCE', 'Finance'),
        ('HR', 'Ressources Humaines'),
        ('IT', 'Informatique'),
        ('OTHER', 'Autre'),
    ]

    name = models.CharField(max_length=300)
    code = models.CharField(max_length=50, unique=True, help_text="Code court (ex: PROC-WT-001)")
    description = models.TextField(blank=True, help_text="Description courte du process")
    context = models.TextField(blank=True, help_text="Description complète en langage naturel (entretien)")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OPERATIONAL')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    structures = models.ManyToManyField(Structure, blank=True, related_name='processes', help_text="Structures impactées")
    systems = models.ManyToManyField(System, blank=True, related_name='processes', help_text="Systèmes impliqués")
    problems = models.TextField(blank=True, help_text="Problèmes et dysfonctionnements identifiés")
    recommendations = models.TextField(blank=True, help_text="Recommandations d'amélioration")
    workflow_json = models.JSONField(default=dict, blank=True, help_text="Workflow structuré (nœuds + arêtes)")
    workflow_mermaid = models.TextField(blank=True, help_text="Code Mermaid du diagramme")
    ai_generated = models.BooleanField(default=False, help_text="Workflow généré par IA")
    source_questionnaire = models.ForeignKey(Questionnaire, on_delete=models.SET_NULL, null=True, blank=True, related_name='processes')
    created_by = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']
        verbose_name = "Process"
        verbose_name_plural = "Process"

    def __str__(self):
        return f"[{self.code}] {self.name}"

    @property
    def step_count(self):
        return self.steps.count()

    @property
    def structure_codes(self):
        return list(self.structures.values_list('code', flat=True))

    @property
    def system_names(self):
        return list(self.systems.values_list('name', flat=True))


class ProcessStep(models.Model):
    """Étape individuelle d'un process"""
    STEP_TYPE_CHOICES = [
        ('MANUAL', 'Action manuelle'),
        ('AUTOMATED', 'Action automatisée'),
        ('DECISION', 'Point de décision'),
        ('INPUT', 'Entrée / Déclencheur'),
        ('OUTPUT', 'Sortie / Résultat'),
        ('WAIT', 'Attente / Délai'),
        ('PARALLEL', 'Actions parallèles'),
    ]

    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name='steps')
    order = models.IntegerField(default=0)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    step_type = models.CharField(max_length=20, choices=STEP_TYPE_CHOICES, default='MANUAL')
    actor_role = models.CharField(max_length=200, blank=True, help_text="Poste/rôle responsable")
    actor_structure = models.ForeignKey(Structure, on_delete=models.SET_NULL, null=True, blank=True, help_text="Structure responsable")
    systems_used = models.ManyToManyField(System, blank=True, related_name='process_steps', help_text="Systèmes utilisés à cette étape")
    data_inputs = models.TextField(blank=True, help_text="Données en entrée")
    data_outputs = models.TextField(blank=True, help_text="Données en sortie")
    interactions = models.TextField(blank=True, help_text="Interactions (homme↔système, système↔système, etc.)")
    problems = models.TextField(blank=True, help_text="Problèmes spécifiques à cette étape")
    duration_estimate = models.CharField(max_length=100, blank=True, help_text="Durée estimée")
    next_steps = models.JSONField(default=list, blank=True, help_text="IDs des étapes suivantes (pour branches)")

    class Meta:
        ordering = ['process', 'order']

    def __str__(self):
        return f"{self.process.code} — Étape {self.order}: {self.title}"


class AuditLog(models.Model):
    """
    Journal d'audit des accès et actions sensibles — exigence loi 18-07 art. 2 (sécurité).
    Conserve qui a fait quoi, quand, depuis où.
    Rétention par défaut : 12 mois (ajustable via CLEANUP_AUDIT_DAYS settings).
    """
    ACTION_CHOICES = [
        ('LOGIN_SUCCESS', 'Connexion réussie'),
        ('LOGIN_FAILED', 'Échec de connexion'),
        ('LOGOUT', 'Déconnexion'),
        ('TOKEN_ACCESS', 'Accès par token'),
        ('TOKEN_INVALID', 'Token invalide'),
        ('VIEW_QUESTIONNAIRE', 'Consultation questionnaire'),
        ('VIEW_SYSTEM', 'Consultation système'),
        ('VIEW_FLOW', 'Consultation flux'),
        ('SUBMIT_ANSWER', 'Soumission réponse'),
        ('VALIDATE_ANSWER', 'Validation réponse'),
        ('UPLOAD_ATTACHMENT', 'Upload pièce jointe'),
        ('DOWNLOAD_ATTACHMENT', 'Téléchargement pièce jointe'),
        ('EXPORT', 'Export de données'),
        ('RIGHTS_REQUEST', 'Demande exercice des droits'),
        ('ADMIN_ACTION', 'Action administrative'),
        ('OTHER', 'Autre'),
    ]

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES, db_index=True)
    actor = models.CharField(max_length=200, blank=True, help_text="Utilisateur (username ou matricule ou anonyme)")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    target_type = models.CharField(max_length=50, blank=True, help_text="Type de ressource consultée (questionnaire, system, question...)")
    target_id = models.CharField(max_length=50, blank=True)
    path = models.CharField(max_length=500, blank=True)
    details = models.JSONField(default=dict, blank=True, help_text="Contexte additionnel (JSON)")
    success = models.BooleanField(default=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Journal d'audit"
        verbose_name_plural = "Journal d'audit"
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['actor', '-timestamp']),
        ]

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.action} / {self.actor or '(anonyme)'}"


class RightsRequest(models.Model):
    """
    Demande d'exercice des droits d'une personne concernée (accès, rectification,
    opposition, limitation) — loi 18-07 art. 4.
    """
    REQUEST_TYPES = [
        ('ACCESS', 'Accès à mes données'),
        ('RECTIFICATION', 'Rectification'),
        ('DELETION', 'Suppression'),
        ('OPPOSITION', 'Opposition au traitement'),
        ('LIMITATION', 'Limitation du traitement'),
        ('PORTABILITY', 'Portabilité'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('IN_PROGRESS', 'En cours de traitement'),
        ('RESOLVED', 'Résolue'),
        ('REJECTED', 'Rejetée'),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    requester_name = models.CharField(max_length=200)
    requester_email = models.EmailField()
    requester_identifier = models.CharField(max_length=100, blank=True, help_text="Matricule, fonction, numéro employé...")
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    response = models.TextField(blank=True)
    responded_by = models.CharField(max_length=200, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Demande d'exercice des droits"
        verbose_name_plural = "Demandes d'exercice des droits"

    def __str__(self):
        return f"{self.get_request_type_display()} — {self.requester_name} ({self.get_status_display()})"


class MatriculeMap(models.Model):
    """
    Table de correspondance matricule → variantes de nom à anonymiser.
    Utilisée pour anonymiser dynamiquement le contenu des pièces jointes.
    Les noms réels restent uniquement dans cette table (non exposée publiquement)
    et permettent de remplacer à la volée les noms dans les fichiers uploadés.
    """
    matricule = models.CharField(max_length=20, unique=True, db_index=True, help_text="Ex: KU001")
    variants = models.JSONField(default=list, help_text="Liste de variantes de noms à rechercher")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['matricule']
        verbose_name = "Correspondance matricule"
        verbose_name_plural = "Correspondances matricules"

    def __str__(self):
        return f"{self.matricule} ({len(self.variants)} variantes)"
