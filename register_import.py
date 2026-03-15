#!/usr/bin/env python
"""
Script pour enregistrer l'import des datafeeds Amadeus du 01/02/2026
"""
import os
import sys
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from cartography.models import DataImportHistory

def register_import():
    # Créer l'enregistrement de l'import du 01/02/2026
    import_record, created = DataImportHistory.objects.get_or_create(
        date=date(2026, 2, 1),
        title="Datafeeds Amadeus - ALTEA vers ACCELYA",
        defaults={
            'description': """Import des datafeeds Amadeus reçus le 01/02/2026. 
Ces données documentent les flux de données entre le système ALTEA (Amadeus) et ACCELYA (Revenue Accounting).

Les datafeeds couvrent :
- Données PNR (réservations passagers)
- Fichiers HOTE/LIFT (coupons de vol utilisés)
- Transactions de paiement (APS)
- Prorata des revenus (RAPID FLP/IBP/SLP)
- Flux DCS et inventaire
- Données temps réel (TDNA)""",
            'import_type': 'DATAFEED',
            'status': 'SUCCESS',
            'source_folder': 'data/01_02/DATAFEEDSS',
            'systems_added': 0,
            'flows_added': 11,
            'formats_added': 10,
            'fields_added': 6,
            'samples_added': 0,
            'details_json': {
                'flows': [
                    {'name': 'PNR Datafeed (SBRRES)', 'source': 'ALTEA', 'target': 'ACCELYA', 'format': 'SBRRES/EDIFACT', 'frequency': 'Continu'},
                    {'name': 'HOTE Lift File', 'source': 'ALTEA', 'target': 'ACCELYA', 'format': 'HOT-LIFT', 'frequency': 'Quotidien'},
                    {'name': 'EMD Lift File', 'source': 'ALTEA', 'target': 'ACCELYA', 'format': 'EMD-LIFT', 'frequency': 'Quotidien'},
                    {'name': 'E-Ticket History File', 'source': 'ALTEA', 'target': 'ACCELYA', 'format': 'ETKT-HIST', 'frequency': 'Quotidien'},
                    {'name': 'APS Payment Transactions', 'source': 'ALTEA', 'target': 'ACCELYA', 'format': 'APS', 'frequency': 'Continu'},
                    {'name': 'RAPID Flight Proration', 'source': 'ALTEA', 'target': 'ACCELYA', 'format': 'RAPID-FLP', 'frequency': 'Quotidien'},
                    {'name': 'RAPID Interline Billing', 'source': 'ALTEA', 'target': 'ACCELYA', 'format': 'RAPID-IBP', 'frequency': 'Mensuel'},
                    {'name': 'RAPID Sales Proration', 'source': 'ALTEA', 'target': 'ACCELYA', 'format': 'RAPID-SLP', 'frequency': 'Quotidien'},
                    {'name': 'Inventory Feed (IFLIRR)', 'source': 'ALTEA', 'target': 'ACCELYA', 'format': 'IFLIRR/EDIFACT', 'frequency': 'Continu'},
                    {'name': 'DCS Data Warehouse Feed', 'source': 'ALTEA', 'target': 'ACCELYA', 'format': 'DCS-CDW', 'frequency': 'Continu'},
                    {'name': 'TDNA LiveFeed', 'source': 'ALTEA', 'target': 'ACCELYA', 'format': 'TDNA/XML', 'frequency': 'Temps réel'},
                ],
                'formats': [
                    {'code': 'SBRRES', 'name': 'PNR Datafeed (SBRRES)', 'standard': 'EDIFACT', 'description': 'Format EDIFACT pour l\'export des données PNR'},
                    {'code': 'HOT-LIFT', 'name': 'HOTE Lift File', 'standard': 'Amadeus', 'description': 'Fichier de coupons de vol utilisés'},
                    {'code': 'EMD-LIFT', 'name': 'EMD Lift File', 'standard': 'Amadeus', 'description': 'Fichier de documents électroniques divers'},
                    {'code': 'APS', 'name': 'Amadeus Payment Services', 'standard': 'Amadeus', 'description': 'Flux de transactions de paiement'},
                    {'code': 'RAPID-FLP', 'name': 'RAPID Flight Proration', 'standard': 'Accelya', 'description': 'Prorata des revenus par segment'},
                    {'code': 'RAPID-IBP', 'name': 'RAPID Interline Billing', 'standard': 'Accelya', 'description': 'Facturation intercompagnies'},
                    {'code': 'RAPID-SLP', 'name': 'RAPID Sales Proration', 'standard': 'Accelya', 'description': 'Prorata des ventes'},
                    {'code': 'IFLIRR', 'name': 'Inventory Feed (EDIFACT)', 'standard': 'EDIFACT', 'description': 'Flux d\'inventaire'},
                    {'code': 'DCS-CDW', 'name': 'DCS Data Warehouse Feed', 'standard': 'Amadeus', 'description': 'Flux DCS vers Data Warehouse'},
                    {'code': 'TDNA', 'name': 'TDNA Batch/LiveFeed', 'standard': 'Amadeus XML', 'description': 'Flux temps réel pour analytics'},
                ],
                'fields': [
                    {'format': 'SBRRES', 'name': 'Amadeus PNR Locator', 'type': 'Alphanum', 'description': 'Record locator Amadeus'},
                    {'format': 'SBRRES', 'name': 'PNR Purge Date', 'type': 'Date', 'description': 'Date de purge du PNR'},
                    {'format': 'SBRRES', 'name': 'Last EOT Date', 'type': 'Date', 'description': 'Date du dernier End of Transaction'},
                    {'format': 'SBRRES', 'name': 'Activity Type', 'type': 'Alpha', 'description': 'Type d\'activité'},
                    {'format': 'SBRRES', 'name': 'Segment Name', 'type': 'Alpha', 'description': 'Nom du segment'},
                    {'format': 'SBRRES', 'name': 'Passenger Name', 'type': 'Alpha', 'description': 'Nom du passager'},
                ],
            },
            'files_processed': [
                'APS AMADEUS PAYMENT PLATFORM/APS.xlsx',
                'DCS CM FM MESSAGES OPERATIONNELS/GUI-IMP-0187- CM_Feed.pdf',
                'DCS CM FM MESSAGES OPERATIONNELS/GUI-IMP-0204-CM Feed.pdf',
                'DCS CM FM MESSAGES OPERATIONNELS/OAG-MVT-MVA-DIV-Message-Types.pdf',
                'DCS CM FM MESSAGES OPERATIONNELS/UG_WBS_DCSFM_DataWarehouseFeed.pdf',
                'HOTE _LIFT file/EMD Lift layout v1.03.xlsx',
                'HOTE _LIFT file/EMDHistoryFile Layout v100.xlsx',
                'HOTE _LIFT file/EtktHistoryFile Layout v101.xlsx',
                'HOTE _LIFT file/Lift File Layout v2.6a.xls',
                'INVENTAIRE/EDIFACT_IFLIRR_15.2.pdf',
                'PNR/174782115_MAPPING_SBRRES_15.1_PNRDATAFEED.xlsx',
                'PNR/SBRRES_15_1_EDIFACT_Grammar.zip',
                'RAPID/FLP TRANSPORT.xlsx',
                'RAPID/IBP INTERLINE.xlsx',
                'RAPID/SLP4027.xlsx',
                'TDNA/Batch_LiveFeed_V3_0.xsd',
            ],
            'notes': """Données reçues de la part d'Amadeus/Accelya.
Ces datafeeds documentent les échanges entre le PSS (ALTEA) et le système de Revenue Accounting (ACCELYA/RAPID).

Points clés :
- Le flux PNR utilise le format EDIFACT SBRRES 15.1
- Les fichiers LIFT sont en version 2.6a pour les billets et 1.03 pour les EMD
- Les flux RAPID couvrent FLP (transport), IBP (interline) et SLP (ventes)
- Le flux TDNA permet le streaming temps réel vers les outils analytics"""
        }
    )
    
    if created:
        print(f"✅ Import enregistré: {import_record.title}")
        print(f"   - Date: {import_record.date}")
        print(f"   - Flux ajoutés: {import_record.flows_added}")
        print(f"   - Formats ajoutés: {import_record.formats_added}")
        print(f"   - Champs ajoutés: {import_record.fields_added}")
        print(f"   - Fichiers traités: {len(import_record.files_processed)}")
    else:
        print(f"ℹ️  Import déjà existant: {import_record.title}")
    
    return import_record

if __name__ == '__main__':
    register_import()
