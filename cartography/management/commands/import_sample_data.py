"""
Management command to import sample data and create validation hypotheses.
Usage: python manage.py import_sample_data
"""
import os
import pandas as pd
from datetime import date
from django.core.management.base import BaseCommand
from cartography.models import (
    DataSample, DataFlow, FlowFieldHypothesis, FlowValidation, System
)


class Command(BaseCommand):
    help = 'Import sample data from the data/20_01 folder and create validation entries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data-path',
            type=str,
            default='/Users/mohamedamine/Air Algérie/data/20_01',
            help='Path to the data folder'
        )

    def handle(self, *args, **options):
        data_path = options['data_path']
        self.stdout.write(f"Importing data from {data_path}")
        
        # Import AIMS FLT data
        self.import_aims_flt(data_path)
        
        # Import AMADEUS APS data
        self.import_amadeus_aps(data_path)
        
        # Import RAPID data
        self.import_rapid_flp(data_path)
        self.import_rapid_ibp(data_path)
        self.import_rapid_slp(data_path)
        
        # Create hypotheses for existing flows
        self.create_flow_hypotheses()
        
        self.stdout.write(self.style.SUCCESS('Data import completed successfully'))

    def import_aims_flt(self, data_path):
        """Import AIMS FLT flight schedule data"""
        flt_path = os.path.join(data_path, 'AIMS', 'FLT.txt')
        if not os.path.exists(flt_path):
            self.stdout.write(self.style.WARNING(f'FLT.txt not found at {flt_path}'))
            return
        
        try:
            # Read tab-separated file
            df = pd.read_csv(flt_path, sep='\t', encoding='utf-8', nrows=100)
            record_count = len(df)
            
            sample, created = DataSample.objects.update_or_create(
                name='AIMS Flight Schedule 12-19 Jan 2026',
                defaults={
                    'source_system': 'AIMS',
                    'data_type': 'FLT',
                    'description': 'Daily Flight Schedule Report from AIMS system',
                    'file_path': flt_path,
                    'sample_date': date(2026, 1, 12),
                    'record_count': record_count,
                }
            )
            
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'{action} AIMS FLT sample with {record_count} records')
            
            # Store discovered fields
            self.discovered_fields['AIMS_FLT'] = list(df.columns)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing AIMS FLT: {e}'))

    def import_amadeus_aps(self, data_path):
        """Import AMADEUS APS payment data"""
        aps_path = os.path.join(data_path, 'AMADEUS', 'APS AMADEUS PAYMENT PLATFORM', 'APS.xlsx')
        if not os.path.exists(aps_path):
            self.stdout.write(self.style.WARNING(f'APS.xlsx not found'))
            return
        
        try:
            df = pd.read_excel(aps_path)
            record_count = len(df)
            
            # Extraire les colonnes et stats
            columns = [str(c) for c in df.columns.tolist()]
            sample_rows = df.head(5).fillna('').astype(str).to_dict('records')
            column_stats = self._get_column_stats(df)
            
            sample, created = DataSample.objects.update_or_create(
                name='AMADEUS Payment Platform (APS)',
                defaults={
                    'source_system': 'AMADEUS',
                    'data_type': 'APS',
                    'description': 'Amadeus Payment Services - transactions de paiement par carte bancaire. Contient les captures, autorisations et détails des paiements.',
                    'file_path': aps_path,
                    'sample_date': date(2022, 6, 9),
                    'record_count': record_count,
                    'columns_json': columns,
                    'sample_rows_json': sample_rows,
                    'column_stats_json': column_stats,
                }
            )
            
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'{action} AMADEUS APS sample with {record_count} records, {len(columns)} columns')
            
            self.discovered_fields['AMADEUS_APS'] = columns
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing AMADEUS APS: {e}'))

    def import_rapid_flp(self, data_path):
        """Import RAPID FLP Transport data"""
        flp_path = os.path.join(data_path, 'RAPID', 'FLP TRANSPORT.xlsx')
        if not os.path.exists(flp_path):
            return
        
        try:
            df = pd.read_excel(flp_path)
            record_count = len(df)
            
            columns = [str(c) for c in df.columns.tolist()]
            sample_rows = df.head(5).fillna('').astype(str).to_dict('records')
            column_stats = self._get_column_stats(df)
            
            sample, created = DataSample.objects.update_or_create(
                name='RAPID FLP Transport',
                defaults={
                    'source_system': 'RAPID',
                    'data_type': 'FLP',
                    'description': 'FLP Transport - Données de transport passagers. Contient les coupons de vol, prorata, taxes, informations passagers et segments.',
                    'file_path': flp_path,
                    'sample_date': date(2026, 1, 9),
                    'record_count': record_count,
                    'columns_json': columns,
                    'sample_rows_json': sample_rows,
                    'column_stats_json': column_stats,
                }
            )
            
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'{action} RAPID FLP sample with {record_count} records, {len(columns)} columns')
            
            self.discovered_fields['RAPID_FLP'] = columns
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing RAPID FLP: {e}'))

    def import_rapid_ibp(self, data_path):
        """Import RAPID IBP Interline data"""
        ibp_path = os.path.join(data_path, 'RAPID', 'IBP INTERLINE.xlsx')
        if not os.path.exists(ibp_path):
            return
        
        try:
            df = pd.read_excel(ibp_path)
            record_count = len(df)
            
            columns = [str(c) for c in df.columns.tolist()]
            sample_rows = df.head(5).fillna('').astype(str).to_dict('records')
            column_stats = self._get_column_stats(df)
            
            sample, created = DataSample.objects.update_or_create(
                name='RAPID IBP Interline Billing',
                defaults={
                    'source_system': 'RAPID',
                    'data_type': 'IBP',
                    'description': 'Interline Billing Platform - Facturation intercompagnies aériennes. Contient les montants facturés, acceptés, rejetés entre compagnies partenaires.',
                    'file_path': ibp_path,
                    'sample_date': date(2025, 9, 1),
                    'record_count': record_count,
                    'columns_json': columns,
                    'sample_rows_json': sample_rows,
                    'column_stats_json': column_stats,
                }
            )
            
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'{action} RAPID IBP sample with {record_count} records, {len(columns)} columns')
            
            self.discovered_fields['RAPID_IBP'] = columns
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing RAPID IBP: {e}'))

    def import_rapid_slp(self, data_path):
        """Import RAPID SLP Sales data"""
        slp_path = os.path.join(data_path, 'RAPID', 'SLP4027.xlsx')
        if not os.path.exists(slp_path):
            return
        
        try:
            df = pd.read_excel(slp_path)
            record_count = len(df)
            
            columns = [str(c) for c in df.columns.tolist()]
            sample_rows = df.head(5).fillna('').astype(str).to_dict('records')
            column_stats = self._get_column_stats(df)
            
            sample, created = DataSample.objects.update_or_create(
                name='RAPID SLP Sales Report',
                defaults={
                    'source_system': 'RAPID',
                    'data_type': 'SLP',
                    'description': 'Sales Ledger Platform - Rapport de ventes BSP. Contient les documents de vente, remboursements, taxes, commissions et détails des transactions.',
                    'file_path': slp_path,
                    'sample_date': date(2026, 1, 1),
                    'record_count': record_count,
                    'columns_json': columns,
                    'sample_rows_json': sample_rows,
                    'column_stats_json': column_stats,
                }
            )
            
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'{action} RAPID SLP sample with {record_count} records, {len(columns)} columns')
            
            self.discovered_fields['RAPID_SLP'] = columns
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing RAPID SLP: {e}'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.discovered_fields = {}
    
    def _get_column_stats(self, df):
        """Extraire des stats pour chaque colonne"""
        stats = {}
        for col in df.columns:
            col_str = str(col)
            col_data = df[col].dropna()
            
            # Déterminer le type
            if col_data.empty:
                dtype = 'EMPTY'
            elif pd.api.types.is_numeric_dtype(col_data):
                if pd.api.types.is_integer_dtype(col_data):
                    dtype = 'INTEGER'
                else:
                    dtype = 'DECIMAL'
            elif pd.api.types.is_datetime64_any_dtype(col_data):
                dtype = 'DATETIME'
            else:
                dtype = 'STRING'
            
            # Exemples de valeurs uniques
            unique_vals = col_data.astype(str).unique()[:5].tolist()
            
            # Stats
            stats[col_str] = {
                'type': dtype,
                'non_null_count': int(col_data.count()),
                'unique_count': int(col_data.nunique()),
                'examples': unique_vals,
            }
        
        return stats

    def create_flow_hypotheses(self):
        """Create hypotheses for flows based on discovered fields"""
        
        # Map data types to potential flows
        flow_mappings = {
            'AIMS_FLT': ['AIMS', 'Programme de vol'],
            'AMADEUS_APS': ['ALTEA', 'Paiement'],
            'RAPID_FLP': ['ACCELYA', 'Transport'],
            'RAPID_IBP': ['ACCELYA', 'Interline'],
            'RAPID_SLP': ['ACCELYA', 'Ventes'],
        }
        
        for data_key, fields in self.discovered_fields.items():
            if data_key not in flow_mappings:
                continue
            
            system_code, flow_keyword = flow_mappings[data_key]
            
            # Find related flows
            flows = DataFlow.objects.filter(
                source__code__icontains=system_code
            ) | DataFlow.objects.filter(
                target__code__icontains=system_code
            )
            
            if not flows.exists():
                # Try to find by name
                flows = DataFlow.objects.filter(name__icontains=flow_keyword)
            
            for flow in flows[:3]:  # Limit to 3 flows per data type
                sample = DataSample.objects.filter(
                    data_type=data_key.split('_')[1] if '_' in data_key else data_key
                ).first()
                
                if not sample:
                    continue
                
                # Create hypotheses for discovered fields
                created_count = 0
                for field_name in fields[:20]:  # Limit to 20 fields
                    field_name_clean = str(field_name).strip()
                    if not field_name_clean or field_name_clean == 'nan':
                        continue
                    
                    hypothesis, created = FlowFieldHypothesis.objects.get_or_create(
                        flow=flow,
                        field_name=field_name_clean,
                        defaults={
                            'hypothesis_type': 'STRING',
                            'hypothesis_format': 'Variable',
                            'hypothesis_description': f'Champ découvert dans {data_key}',
                            'real_type': 'STRING',
                            'real_format': 'Observé',
                            'real_example': f'Valeur de {field_name_clean}',
                            'status': 'HYPOTHESIS',
                            'validated_from_sample': sample,
                        }
                    )
                    if created:
                        created_count += 1
                
                if created_count > 0:
                    self.stdout.write(f'Created {created_count} hypotheses for flow: {flow.name}')
