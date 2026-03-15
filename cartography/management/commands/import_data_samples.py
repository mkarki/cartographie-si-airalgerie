"""
Commande Django pour importer et analyser les échantillons de données Air Algérie
"""
import os
import json
from datetime import datetime
from django.core.management.base import BaseCommand
from cartography.models import DataSample, System, DataFlow


class Command(BaseCommand):
    help = 'Importe et analyse les échantillons de données depuis le dossier data/'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data-path',
            type=str,
            default='/Users/mohamedamine/Air Algérie/data/20_01',
            help='Chemin vers le dossier de données'
        )

    def handle(self, *args, **options):
        data_path = options['data_path']
        self.stdout.write(f"Analyse des données dans: {data_path}")
        
        # Structure des données découvertes
        discovered_data = {
            'AIMS': [],
            'AMADEUS': [],
            'RAPID': [],
        }
        
        # Parcourir récursivement tous les fichiers
        for root, dirs, files in os.walk(data_path):
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, data_path)
                
                # Déterminer le système source
                parts = rel_path.split(os.sep)
                if len(parts) >= 1:
                    source_system = parts[0].upper()
                else:
                    source_system = 'OTHER'
                
                # Analyser le fichier
                file_info = self.analyze_file(file_path, file)
                file_info['relative_path'] = rel_path
                file_info['source_system'] = source_system
                
                if source_system in discovered_data:
                    discovered_data[source_system].append(file_info)
                
                self.stdout.write(f"  Analysé: {rel_path}")
        
        # Afficher le résumé
        self.stdout.write("\n" + "="*60)
        self.stdout.write("RÉSUMÉ DES DONNÉES DÉCOUVERTES")
        self.stdout.write("="*60)
        
        for system, files in discovered_data.items():
            if files:
                self.stdout.write(f"\n{system} ({len(files)} fichiers):")
                for f in files:
                    self.stdout.write(f"  - {f['name']} ({f['type']}) - {f['size_kb']:.1f} KB")
                    if f.get('columns'):
                        self.stdout.write(f"    Colonnes: {', '.join(f['columns'][:10])}")
                    if f.get('description'):
                        self.stdout.write(f"    Description: {f['description']}")
        
        # Créer les DataSample dans la base
        self.create_data_samples(discovered_data)
        
        self.stdout.write(self.style.SUCCESS('\nImportation terminée!'))

    def analyze_file(self, file_path, filename):
        """Analyse un fichier et extrait ses métadonnées"""
        info = {
            'name': filename,
            'path': file_path,
            'size_kb': os.path.getsize(file_path) / 1024,
            'type': 'unknown',
            'columns': [],
            'sample_rows': [],
            'description': '',
        }
        
        ext = os.path.splitext(filename)[1].lower()
        
        if ext == '.txt':
            info['type'] = 'TXT'
            info.update(self.analyze_txt(file_path))
        elif ext == '.xlsx' or ext == '.xls':
            info['type'] = 'EXCEL'
            info.update(self.analyze_excel_metadata(file_path, filename))
        elif ext == '.pdf':
            info['type'] = 'PDF'
            info['description'] = self.get_pdf_description(filename)
        elif ext == '.xsd':
            info['type'] = 'XSD'
            info['description'] = 'Schéma XML'
        elif ext == '.htm' or ext == '.html':
            info['type'] = 'HTML'
            info['description'] = 'Documentation HTML'
        elif ext == '.zip':
            info['type'] = 'ZIP'
            info['description'] = 'Archive compressée'
        
        return info

    def analyze_txt(self, file_path):
        """Analyse un fichier texte tabulé"""
        result = {'columns': [], 'sample_rows': [], 'record_count': 0}
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            if len(lines) >= 3:
                # Ligne 1: Titre
                result['description'] = lines[0].strip()
                
                # Ligne 3: En-têtes (généralement)
                if len(lines) >= 3:
                    headers = lines[2].strip().split('\t')
                    result['columns'] = [h.strip() for h in headers if h.strip()]
                
                # Lignes de données
                result['record_count'] = max(0, len(lines) - 3)
                
                # Échantillon de données
                for line in lines[3:8]:
                    values = line.strip().split('\t')
                    if values and values[0].strip():
                        result['sample_rows'].append(values[:10])
                        
        except Exception as e:
            result['description'] = f'Erreur lecture: {str(e)}'
        
        return result

    def analyze_excel_metadata(self, file_path, filename):
        """Extrait les métadonnées d'un fichier Excel basé sur son nom"""
        result = {'columns': [], 'description': ''}
        
        name_lower = filename.lower()
        
        if 'aps' in name_lower:
            result['description'] = 'Amadeus Payment Platform - Transactions CB'
            result['columns'] = ['Document_Number', 'Carrier_Code', 'Transaction_Type', 
                                'Amount', 'Currency', 'Card_Type', 'Authorization_Code']
        elif 'flp' in name_lower or 'transport' in name_lower:
            result['description'] = 'FLP Transport - Coupons de vol passagers'
            result['columns'] = ['Ticket_Number', 'Coupon_Number', 'Flight_Number',
                                'Origin', 'Destination', 'Class', 'Fare_Basis']
        elif 'ibp' in name_lower or 'interline' in name_lower:
            result['description'] = 'IBP Interline - Facturation intercompagnies'
            result['columns'] = ['Billing_Period', 'Partner_Airline', 'Document_Number',
                                'Amount', 'Currency', 'Prorate_Factor']
        elif 'slp' in name_lower:
            result['description'] = 'SLP Sales Ledger - Rapport ventes BSP'
            result['columns'] = ['Agent_Code', 'Document_Number', 'Issue_Date',
                                'Amount', 'Commission', 'Net_Amount']
        elif 'lift' in name_lower:
            result['description'] = 'LIFT File - Passagers embarqués'
            result['columns'] = ['Flight_Number', 'Flight_Date', 'Origin', 'Destination',
                                'Ticket_Number', 'Passenger_Name', 'Seat', 'Class']
        elif 'emd' in name_lower:
            result['description'] = 'EMD - Electronic Miscellaneous Document'
            result['columns'] = ['EMD_Number', 'Type', 'Amount', 'Currency', 'Status']
        elif 'etkt' in name_lower or 'ticket' in name_lower:
            result['description'] = 'E-Ticket History - Historique billets électroniques'
            result['columns'] = ['Ticket_Number', 'Issue_Date', 'Status', 'Fare', 'Tax']
        elif 'pnr' in name_lower or 'mapping' in name_lower:
            result['description'] = 'PNR Data Feed - Mapping des données de réservation'
            result['columns'] = ['Record_Locator', 'Creation_Date', 'Passenger_Name',
                                'Segments', 'Contact', 'Ticketing_Info']
        
        return result

    def get_pdf_description(self, filename):
        """Retourne une description basée sur le nom du PDF"""
        name_lower = filename.lower()
        
        if 'cm_feed' in name_lower or 'dcs' in name_lower:
            return 'DCS Feed - Documentation flux Departure Control System'
        elif 'mvt' in name_lower or 'mva' in name_lower:
            return 'MVT/MVA Messages - Types de messages mouvement avion'
        elif 'bsp' in name_lower:
            return 'BSP - Documentation Billing Settlement Plan'
        elif 'edifact' in name_lower:
            return 'EDIFACT - Grammaire messages EDI'
        elif 'iflirr' in name_lower:
            return 'IFLIRR - Inventaire Flight Irregularity'
        elif 'seatmap' in name_lower:
            return 'Seat Map - Plan de cabine'
        elif 'farcrq' in name_lower:
            return 'FARCRQ - Fare Request/Response'
        
        return 'Documentation technique'

    def create_data_samples(self, discovered_data):
        """Crée les DataSample dans la base de données"""
        
        # Mapping dossier -> système source réel
        # RAPID = Accelya Revenue Accounting
        # AMADEUS = Suite Altéa (PSS)
        # AIMS = AIMS (Planning vols)
        system_mapping = {
            'AIMS': 'AIMS',
            'AMADEUS': 'AMADEUS',
            'RAPID': 'ACCELYA',  # RAPID est le nom du produit Accelya
        }
        
        # Mapping type de données
        data_type_mapping = {
            'FLT': 'FLT',
            'APS': 'APS',
            'FLP': 'FLP',
            'IBP': 'IBP',
            'SLP': 'SLP',
            'LIFT': 'LIFT',
            'PNR': 'PNR',
        }
        
        for system, files in discovered_data.items():
            for file_info in files:
                if file_info['type'] in ['TXT', 'EXCEL']:
                    # Déterminer le type de données
                    data_type = 'OTHER'
                    name_upper = file_info['name'].upper()
                    for key, value in data_type_mapping.items():
                        if key in name_upper:
                            data_type = value
                            break
                    
                    # Créer ou mettre à jour le DataSample
                    sample, created = DataSample.objects.update_or_create(
                        name=file_info['name'],
                        defaults={
                            'source_system': system_mapping.get(system, 'OTHER'),
                            'data_type': data_type,
                            'description': file_info.get('description', ''),
                            'file_path': file_info['path'],
                            'record_count': file_info.get('record_count', 0),
                            'columns_json': file_info.get('columns', []),
                            'sample_rows_json': file_info.get('sample_rows', []),
                        }
                    )
                    
                    action = 'Créé' if created else 'Mis à jour'
                    self.stdout.write(f"  {action}: {sample.name}")
