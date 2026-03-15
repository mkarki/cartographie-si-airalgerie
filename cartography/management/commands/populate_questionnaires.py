"""
Management command to populate questionnaires from Markdown fiches systèmes.
Parses each fiche to extract system info, sections, and questions.
"""
import os
import re
from django.core.management.base import BaseCommand
from cartography.models import Questionnaire, QuestionSection, Question


# Mapping: (filename_prefix, phase, priority_in_phase)
FICHES = [
    # Phase 1
    ('Phase1_01_ALTEA.md', 1, 1),
    ('Phase1_02_AIMS.md', 1, 2),
    ('Phase1_03_AMOS.md', 1, 3),
    ('Phase1_04_RAPID.md', 1, 4),
    ('Phase1_05_SITATEX.md', 1, 5),
    ('Phase1_06_ACARS.md', 1, 6),
    # Phase 2
    ('Phase2_01_SAGE_STOCK.md', 2, 1),
    ('Phase2_02_ATPCO.md', 2, 2),
    ('Phase2_03_BAC.md', 2, 3),
    ('Phase2_04_DASHBOARDS_CCO.md', 2, 4),
    ('Phase2_05_AGS.md', 2, 5),
    ('Phase2_06_QPULSE.md', 2, 6),
    ('Phase2_07_EUROCONTROL.md', 2, 7),
    ('Phase2_08_JET_PLANER.md', 2, 8),
    ('Phase2_09_WORLD_TRACER.md', 2, 9),
    ('Phase2_10_SITE_WEB.md', 2, 10),
    ('Phase2_11_ACCELYA_DISTRIBUTION.md', 2, 11),
    ('Phase2_12_QLIK_SENSE.md', 2, 12),
    ('Phase2_13_POWER_BI.md', 2, 13),
    ('Phase2_14_AIMS_FORMATION.md', 2, 14),
    ('Phase2_15_SAGE_FINANCE.md', 2, 15),
    # Phase 3
    ('Phase3_01_BSP_LINK.md', 3, 1),
    ('Phase3_02_EDOLEANCE.md', 3, 2),
    ('Phase3_03_GLPI.md', 3, 3),
    ('Phase3_04_HERMES_CALL_CENTER.md', 3, 4),
    ('Phase3_05_OAG.md', 3, 5),
    ('Phase3_06_ELEARNING.md', 3, 6),
    ('Phase3_07_ZIMBRA.md', 3, 7),
    ('Phase3_08_CONTROLE_PROGRAMMES.md', 3, 8),
    ('Phase3_09_DOA_MAILING.md', 3, 9),
    ('Phase3_10_CALL_DOA.md', 3, 10),
    ('Phase3_11_SKYBOOK.md', 3, 11),
    ('Phase3_12_FLYSMART.md', 3, 12),
    ('Phase3_13_PORTAIL_AH.md', 3, 13),
    ('Phase3_14_EVALCOM.md', 3, 14),
    ('Phase3_15_BODET.md', 3, 15),
    ('Phase3_16_DATAWINGS.md', 3, 16),
    ('Phase3_17_AIMS_FORMATION_PNC.md', 3, 17),
    ('Phase3_18_AIMS_FORMATION_PNT.md', 3, 18),
]


def extract_table_field(content, field_name):
    """Extract a value from a markdown table row like | **Field** | Value |"""
    pattern = rf'\|\s*\*\*{re.escape(field_name)}\*\*\s*\|\s*(.*?)\s*\|'
    match = re.search(pattern, content)
    if match:
        return match.group(1).strip()
    return ''


def parse_fiche(filepath):
    """Parse a fiche markdown file and return structured data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract system name from first heading
    title_match = re.search(r'^# Fiche Système — (.+)$', content, re.MULTILINE)
    system_name = title_match.group(1).strip() if title_match else os.path.basename(filepath)
    
    # Extract identification fields
    editor = extract_table_field(content, 'Éditeur')
    direction = extract_table_field(content, 'Direction')
    division = extract_table_field(content, 'Division')
    if division and direction:
        direction = f"{division} / {direction}"
    elif division:
        direction = division
    responsible = extract_table_field(content, 'Responsable hiérarchique')
    key_users = extract_table_field(content, 'Key User Principal')
    key_users_backup = extract_table_field(content, 'Key User Backup')
    
    # Extract sections and questions
    # Find the "Questions à adresser au métier" section
    questions_start = content.find('## Questions à adresser au métier')
    if questions_start == -1:
        questions_start = content.find('## Questions à adresser')
    
    sections = []
    if questions_start != -1:
        questions_content = content[questions_start:]
        
        # Split by ### headers (sections)
        section_pattern = r'### ([A-Z]) — (.+?)(?=\n)'
        section_matches = list(re.finditer(section_pattern, questions_content))
        
        for i, match in enumerate(section_matches):
            section_title = f"{match.group(1)} — {match.group(2).strip()}"
            start = match.end()
            end = section_matches[i + 1].start() if i + 1 < len(section_matches) else len(questions_content)
            section_text = questions_content[start:end]
            
            # Extract questions from this section
            q_pattern = r'\*\*Q(\d+)\.\*\*\s*(.+?)(?=\n\n|\n>)'
            q_matches = re.finditer(q_pattern, section_text, re.DOTALL)
            
            questions = []
            for qm in q_matches:
                q_num = f"Q{qm.group(1)}"
                q_text = qm.group(2).strip()
                # Clean up the question text
                q_text = re.sub(r'\s+', ' ', q_text)
                questions.append({
                    'number': q_num,
                    'text': q_text,
                })
            
            if questions:
                sections.append({
                    'title': section_title,
                    'questions': questions,
                })
    
    return {
        'system_name': system_name,
        'editor': editor,
        'direction': direction,
        'responsible': responsible,
        'key_users': key_users,
        'key_users_backup': key_users_backup,
        'sections': sections,
    }


class Command(BaseCommand):
    help = 'Populate questionnaires from Markdown fiches systèmes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fiches-dir',
            type=str,
            default=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'fiches_systemes'),
            help='Path to the fiches_systemes directory',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing questionnaires before populating',
        )

    def handle(self, *args, **options):
        fiches_dir = options['fiches_dir']
        
        if options['clear']:
            count = Questionnaire.objects.count()
            Questionnaire.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {count} existing questionnaires'))
        
        created = 0
        total_questions = 0
        
        for filename, phase, priority in FICHES:
            filepath = os.path.join(fiches_dir, filename)
            
            if not os.path.exists(filepath):
                self.stdout.write(self.style.WARNING(f'File not found: {filepath}'))
                continue
            
            data = parse_fiche(filepath)
            
            # Check if questionnaire already exists
            existing = Questionnaire.objects.filter(
                system_name=data['system_name'],
                phase=phase,
                priority_in_phase=priority,
            ).first()
            
            if existing:
                self.stdout.write(f'  Skipping {data["system_name"]} (already exists)')
                continue
            
            # Create questionnaire
            questionnaire = Questionnaire.objects.create(
                system_name=data['system_name'],
                phase=phase,
                priority_in_phase=priority,
                editor=data['editor'],
                direction=data['direction'],
                key_users=data['key_users'],
                key_users_backup=data['key_users_backup'],
                responsible=data['responsible'],
            )
            
            q_count = 0
            for s_idx, section_data in enumerate(data['sections']):
                section = QuestionSection.objects.create(
                    questionnaire=questionnaire,
                    title=section_data['title'],
                    order=s_idx,
                )
                
                for q_idx, q_data in enumerate(section_data['questions']):
                    Question.objects.create(
                        section=section,
                        number=q_data['number'],
                        text=q_data['text'],
                        order=q_idx,
                    )
                    q_count += 1
            
            total_questions += q_count
            created += 1
            self.stdout.write(f'  ✓ {data["system_name"]} — {len(data["sections"])} sections, {q_count} questions')
        
        self.stdout.write(self.style.SUCCESS(
            f'\nDone: {created} questionnaires created, {total_questions} questions total'
        ))
