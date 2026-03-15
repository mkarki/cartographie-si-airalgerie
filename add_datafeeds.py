#!/usr/bin/env python
"""
Script pour ajouter les nouveaux datafeeds Amadeus à la cartographie SI
Basé sur les données reçues le 01/02/2026 dans data/01_02/DATAFEEDSS
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from cartography.models import System, DataFlow, SystemCategory, Structure, MessageFormat, MessageField

def add_datafeeds():
    # Récupérer les systèmes existants
    altea = System.objects.get(code='ALTEA')
    accelya = System.objects.get(code='ACCELYA')
    
    # Récupérer les structures
    df_structure = Structure.objects.get(code='DF')  # Direction Financière
    dc_structure = Structure.objects.get(code='DC')  # Direction Commerciale
    do_structure = Structure.objects.get(code='DO')  # Direction des Opérations
    dsi_structure = Structure.objects.get(code='DSI')  # DSI
    
    # Récupérer les catégories
    core_category = SystemCategory.objects.get(name='Core Business')
    finance_category = SystemCategory.objects.get(name='Finance & Comptabilité')
    
    print("=" * 60)
    print("AJOUT DES NOUVEAUX DATAFEEDS AMADEUS")
    print("=" * 60)
    
    # =========================================================================
    # 1. NOUVEAUX FORMATS DE MESSAGES
    # =========================================================================
    print("\n1. Ajout des nouveaux formats de messages...")
    
    new_formats = [
        {
            'code': 'SBRRES',
            'name': 'PNR Datafeed (SBRRES)',
            'description': 'Format EDIFACT pour l\'export des données PNR. Contient les informations complètes de réservation: segments, passagers, contacts, paiements, remarques.',
            'standard': 'EDIFACT',
            'example': 'UNB+IATB:1+1A+AH+260201:1200+SBRRES001++SBRRES\'UNH+1+SBRRES:15:1:1A\'...'
        },
        {
            'code': 'HOT-LIFT',
            'name': 'HOTE Lift File',
            'description': 'Fichier de coupons de vol utilisés (lifted). Contient les détails de chaque coupon volé: statut, vol, passager, tarif, taxes.',
            'standard': 'Amadeus',
            'example': 'Version 2.6a - Champs: Final Status, Airline Code, Document Number, Coupon Number, Flight Details...'
        },
        {
            'code': 'EMD-LIFT',
            'name': 'EMD Lift File',
            'description': 'Fichier de documents électroniques divers (EMD) utilisés. Services ancillaires, pénalités, frais.',
            'standard': 'Amadeus',
            'example': 'Version 1.03 - EMD Type, RFIC, RFIS, Amount, Status...'
        },
        {
            'code': 'APS',
            'name': 'Amadeus Payment Services',
            'description': 'Flux de transactions de paiement. Captures, autorisations, remboursements. Détails carte, 3DS, DCC.',
            'standard': 'Amadeus',
            'example': 'Timestamp, Type (CAPTURE/AUTH/REFUND), Status, ReferenceID, CC_CardCode, Amount...'
        },
        {
            'code': 'RAPID-FLP',
            'name': 'RAPID Flight Proration',
            'description': 'Prorata des revenus par segment de vol. Répartition du revenu entre les différents segments.',
            'standard': 'Accelya',
            'example': 'Carrier, Document, Coupon, Sector, Proration Value, Currency...'
        },
        {
            'code': 'RAPID-IBP',
            'name': 'RAPID Interline Billing',
            'description': 'Facturation intercompagnies. Coupons volés sur d\'autres compagnies, acceptation/rejet.',
            'standard': 'Accelya',
            'example': 'Billing Month, Billing Carrier, Document, Coupon, Billed Value, Accepted Value...'
        },
        {
            'code': 'RAPID-SLP',
            'name': 'RAPID Sales Proration',
            'description': 'Prorata des ventes. Détail des ventes et remboursements avec répartition par devise.',
            'standard': 'Accelya',
            'example': 'Reporting Date, Sale/Refund, Carrier, Document, Gross Amt, Net Amt, Taxes...'
        },
        {
            'code': 'IFLIRR',
            'name': 'Inventory Feed (EDIFACT)',
            'description': 'Flux d\'inventaire EDIFACT. Disponibilités et statuts des classes de réservation.',
            'standard': 'EDIFACT',
            'example': 'UNB+IATB:1+1A+AH+260201:0800+IFLIRR001\'UNH+1+IFLIRR:15:2:1A\'...'
        },
        {
            'code': 'DCS-CDW',
            'name': 'DCS Data Warehouse Feed',
            'description': 'Flux DCS vers Data Warehouse. Données d\'enregistrement, seatmap, identification passagers.',
            'standard': 'Amadeus',
            'example': 'CDWCPRIdentification, CDWGetFDSeatmap - Passenger details, seat assignments...'
        },
        {
            'code': 'TDNA',
            'name': 'TDNA Batch/LiveFeed',
            'description': 'Flux temps réel et batch pour analytics. Données de réservation et ticketing en temps réel.',
            'standard': 'Amadeus XML',
            'example': 'XSD Schema v3.0 - Batch and LiveFeed elements for real-time data streaming'
        },
    ]
    
    for fmt_data in new_formats:
        fmt, created = MessageFormat.objects.get_or_create(
            code=fmt_data['code'],
            defaults={
                'name': fmt_data['name'],
                'description': fmt_data['description'],
                'standard': fmt_data['standard'],
                'example': fmt_data['example']
            }
        )
        status = "CRÉÉ" if created else "existe déjà"
        print(f"  - {fmt_data['code']}: {status}")
    
    # =========================================================================
    # 2. NOUVEAUX FLUX DE DONNÉES
    # =========================================================================
    print("\n2. Ajout des nouveaux flux de données...")
    
    new_flows = [
        # Flux PNR Datafeed
        {
            'source': altea,
            'target': accelya,
            'name': 'PNR Datafeed (SBRRES)',
            'description': 'Export complet des données PNR vers Revenue Accounting. Format EDIFACT SBRRES 15.1. Contient segments, passagers, paiements, remarques.',
            'frequency': 'CONTINUOUS',
            'protocol': 'FILE',
            'format': 'SBRRES/EDIFACT',
            'is_automated': True,
            'is_critical': True,
            'volume': '~50000 PNR/jour'
        },
        # Flux HOTE/LIFT
        {
            'source': altea,
            'target': accelya,
            'name': 'HOTE Lift File',
            'description': 'Fichiers de coupons de vol utilisés. Détails des billets volés pour le revenue accounting. Version 2.6a.',
            'frequency': 'DAILY',
            'protocol': 'FILE',
            'format': 'HOT-LIFT',
            'is_automated': True,
            'is_critical': True,
            'volume': '~15000 coupons/jour'
        },
        # Flux EMD Lift
        {
            'source': altea,
            'target': accelya,
            'name': 'EMD Lift File',
            'description': 'Fichiers EMD (Electronic Miscellaneous Document) utilisés. Services ancillaires, pénalités. Version 1.03.',
            'frequency': 'DAILY',
            'protocol': 'FILE',
            'format': 'EMD-LIFT',
            'is_automated': True,
            'is_critical': True,
            'volume': '~2000 EMD/jour'
        },
        # Flux E-Ticket History
        {
            'source': altea,
            'target': accelya,
            'name': 'E-Ticket History File',
            'description': 'Historique complet des billets électroniques. Émissions, échanges, remboursements.',
            'frequency': 'DAILY',
            'protocol': 'FILE',
            'format': 'ETKT-HIST',
            'is_automated': True,
            'is_critical': True,
            'volume': ''
        },
        # Flux APS Payment
        {
            'source': altea,
            'target': accelya,
            'name': 'APS Payment Transactions',
            'description': 'Transactions de paiement Amadeus Payment Services. Captures, autorisations, 3D Secure, DCC.',
            'frequency': 'CONTINUOUS',
            'protocol': 'FILE',
            'format': 'APS',
            'is_automated': True,
            'is_critical': True,
            'volume': '~5000 transactions/jour'
        },
        # Flux RAPID FLP
        {
            'source': altea,
            'target': accelya,
            'name': 'RAPID Flight Proration',
            'description': 'Prorata des revenus par segment de vol pour la répartition des recettes.',
            'frequency': 'DAILY',
            'protocol': 'FILE',
            'format': 'RAPID-FLP',
            'is_automated': True,
            'is_critical': True,
            'volume': ''
        },
        # Flux RAPID IBP
        {
            'source': altea,
            'target': accelya,
            'name': 'RAPID Interline Billing',
            'description': 'Facturation intercompagnies. Coupons volés sur compagnies partenaires, acceptation/rejet.',
            'frequency': 'MONTHLY',
            'protocol': 'FILE',
            'format': 'RAPID-IBP',
            'is_automated': True,
            'is_critical': True,
            'volume': ''
        },
        # Flux RAPID SLP
        {
            'source': altea,
            'target': accelya,
            'name': 'RAPID Sales Proration',
            'description': 'Prorata des ventes avec détail par devise. Ventes et remboursements.',
            'frequency': 'DAILY',
            'protocol': 'FILE',
            'format': 'RAPID-SLP',
            'is_automated': True,
            'is_critical': True,
            'volume': ''
        },
        # Flux Inventaire
        {
            'source': altea,
            'target': accelya,
            'name': 'Inventory Feed (IFLIRR)',
            'description': 'Flux d\'inventaire EDIFACT. Disponibilités et statuts des classes de réservation.',
            'frequency': 'CONTINUOUS',
            'protocol': 'FILE',
            'format': 'IFLIRR/EDIFACT',
            'is_automated': True,
            'is_critical': True,
            'volume': ''
        },
        # Flux DCS CDW
        {
            'source': altea,
            'target': accelya,
            'name': 'DCS Data Warehouse Feed',
            'description': 'Données DCS vers Data Warehouse. Enregistrement, seatmap, identification passagers.',
            'frequency': 'CONTINUOUS',
            'protocol': 'FILE',
            'format': 'DCS-CDW',
            'is_automated': True,
            'is_critical': True,
            'volume': ''
        },
        # Flux TDNA
        {
            'source': altea,
            'target': accelya,
            'name': 'TDNA LiveFeed',
            'description': 'Flux temps réel pour analytics. Données de réservation et ticketing en streaming.',
            'frequency': 'REALTIME',
            'protocol': 'API_REST',
            'format': 'TDNA/XML',
            'is_automated': True,
            'is_critical': False,
            'volume': ''
        },
    ]
    
    for flow_data in new_flows:
        flow, created = DataFlow.objects.get_or_create(
            source=flow_data['source'],
            target=flow_data['target'],
            name=flow_data['name'],
            defaults={
                'description': flow_data['description'],
                'frequency': flow_data['frequency'],
                'protocol': flow_data['protocol'],
                'format': flow_data['format'],
                'is_automated': flow_data['is_automated'],
                'is_critical': flow_data['is_critical'],
                'volume': flow_data.get('volume', '')
            }
        )
        status = "CRÉÉ" if created else "existe déjà"
        print(f"  - {flow_data['name']}: {status}")
    
    # =========================================================================
    # 3. MISE À JOUR DU FLUX HOT EXISTANT
    # =========================================================================
    print("\n3. Mise à jour du flux HOT Billetterie existant...")
    
    try:
        hot_flow = DataFlow.objects.get(name='Fichiers HOT Billetterie')
        hot_flow.description = 'Transactions de billetterie quotidiennes. Inclut: HOTE Lift Files, EMD Lift, E-Ticket History. ~35 fichiers/jour.'
        hot_flow.save()
        print("  - Flux HOT Billetterie mis à jour avec plus de détails")
    except DataFlow.DoesNotExist:
        print("  - Flux HOT Billetterie non trouvé")
    
    # =========================================================================
    # 4. AJOUT DES CHAMPS POUR LE FORMAT SBRRES
    # =========================================================================
    print("\n4. Ajout des champs pour le format SBRRES (PNR Datafeed)...")
    
    try:
        sbrres_format = MessageFormat.objects.get(code='SBRRES')
        
        sbrres_fields = [
            {'name': 'Amadeus PNR Locator', 'position_start': 1, 'position_end': 6, 'length': 6, 'field_type': 'Alphanum', 'description': 'Record locator Amadeus', 'example': 'WE6MDX', 'is_mandatory': True},
            {'name': 'PNR Purge Date', 'position_start': 7, 'position_end': 12, 'length': 6, 'field_type': 'Date', 'description': 'Date de purge du PNR (ddmmyy)', 'example': '150326', 'is_mandatory': True},
            {'name': 'Last EOT Date', 'position_start': 13, 'position_end': 18, 'length': 6, 'field_type': 'Date', 'description': 'Date du dernier End of Transaction', 'example': '010226', 'is_mandatory': True},
            {'name': 'Activity Type', 'position_start': 19, 'position_end': 22, 'length': 4, 'field_type': 'Alpha', 'description': 'Type d\'activité (AIR, TSM, etc.)', 'example': 'AIR', 'is_mandatory': True},
            {'name': 'Segment Name', 'position_start': 23, 'position_end': 30, 'length': 8, 'field_type': 'Alpha', 'description': 'Nom du segment', 'example': 'SEGMENT', 'is_mandatory': False},
            {'name': 'Passenger Name', 'position_start': 31, 'position_end': 80, 'length': 50, 'field_type': 'Alpha', 'description': 'Nom du passager', 'example': 'DUPONT/JEAN MR', 'is_mandatory': True},
        ]
        
        for field_data in sbrres_fields:
            field, created = MessageField.objects.get_or_create(
                message_format=sbrres_format,
                name=field_data['name'],
                defaults=field_data
            )
            status = "CRÉÉ" if created else "existe déjà"
            print(f"  - {field_data['name']}: {status}")
            
    except MessageFormat.DoesNotExist:
        print("  - Format SBRRES non trouvé")
    
    # =========================================================================
    # RÉSUMÉ
    # =========================================================================
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    
    total_systems = System.objects.count()
    total_flows = DataFlow.objects.count()
    total_formats = MessageFormat.objects.count()
    total_fields = MessageField.objects.count()
    
    print(f"  - Systèmes: {total_systems}")
    print(f"  - Flux de données: {total_flows}")
    print(f"  - Formats de messages: {total_formats}")
    print(f"  - Champs de messages: {total_fields}")
    print("\nMise à jour terminée avec succès!")

if __name__ == '__main__':
    add_datafeeds()
