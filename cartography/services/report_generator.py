"""
Service de génération de rapports IA avec Claude API
"""
import anthropic
from datetime import datetime
from django.conf import settings


class ReportGenerator:
    """Générateur de rapports IA utilisant Claude"""
    
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
    
    def collect_knowledge(self, systems, flows, samples, domains):
        """Collecte tout le knowledge disponible"""
        
        # Mapping pour clarifier les sources
        source_clarification = {
            'RAPID': 'ACCELYA (RAPID)',  # RAPID est un produit Accelya
            'AMADEUS': 'ALTEA (Amadeus)',
        }
        
        # Compter les échantillons avec données réelles vs layouts
        samples_with_data = sum(1 for s in samples if s.record_count > 0)
        samples_layouts = sum(1 for s in samples if s.record_count == 0)
        total_columns = sum(len(s.columns_json or []) for s in samples)
        
        # Compter les systèmes par localisation
        systemes_algerie = systems.filter(country='DZ').count()
        systemes_france = systems.filter(country='FR').count()
        systemes_international = systems.filter(country__in=['EU', 'INTL']).count()
        
        knowledge = {
            'date_rapport': datetime.now().strftime('%d/%m/%Y à %H:%M'),
            'systemes': [],
            'flux': [],
            'echantillons': [],
            'domaines': [],
            'systemes_par_localisation': {
                'algerie': [],
                'france': [],
                'international': [],
            },
            'statistiques': {
                'total_systemes': systems.count(),
                'total_flux': flows.count(),
                'total_echantillons': samples.count(),
                'echantillons_avec_donnees': samples_with_data,
                'echantillons_layouts': samples_layouts,
                'total_colonnes_documentees': total_columns,
                'systemes_avec_echantillons': 0,
                'flux_critiques': flows.filter(is_critical=True).count(),
                'systemes_algerie': systemes_algerie,
                'systemes_france': systemes_france,
                'systemes_international': systemes_international,
            },
            'source_clarification': source_clarification,
        }
        
        # Systèmes
        for sys in systems:
            # Déterminer la localisation lisible
            localisation_map = {
                'DZ': 'Algérie',
                'FR': 'France', 
                'EU': 'Europe',
                'INTL': 'International/Cloud',
            }
            localisation = localisation_map.get(sys.country, 'Algérie')
            
            sys_data = {
                'code': sys.code,
                'nom': sys.name,
                'vendor': sys.vendor,
                'categorie': sys.category.name if sys.category else 'N/A',
                'structure': sys.structure.code if sys.structure else 'N/A',
                'criticite': sys.criticality,
                'mode': sys.get_mode_display(),
                'localisation': localisation,
                'country_code': sys.country,
                'description': sys.description or '',
                'modules': sys.modules or [],
                'domaines_maitrises': list(sys.mastered_domains.values_list('name', flat=True)),
            }
            knowledge['systemes'].append(sys_data)
            
            # Classer par localisation
            if sys.country == 'DZ':
                knowledge['systemes_par_localisation']['algerie'].append(sys_data)
            elif sys.country == 'FR':
                knowledge['systemes_par_localisation']['france'].append(sys_data)
            else:
                knowledge['systemes_par_localisation']['international'].append(sys_data)
        
        # Flux
        for flow in flows:
            flow_data = {
                'nom': flow.name,
                'source': flow.source.code,
                'cible': flow.target.code,
                'frequence': flow.get_frequency_display(),
                'protocole': flow.get_protocol_display(),
                'format': flow.format,
                'critique': flow.is_critical,
                'description': flow.description or '',
            }
            knowledge['flux'].append(flow_data)
        
        # Échantillons
        systems_with_samples = set()
        for sample in samples:
            sample_data = {
                'nom': sample.name,
                'systeme_source': sample.source_system,
                'type': sample.get_data_type_display(),
                'description': sample.description or '',
                'colonnes': sample.columns_json or [],
                'nb_enregistrements': sample.record_count,
            }
            knowledge['echantillons'].append(sample_data)
            systems_with_samples.add(sample.source_system)
        
        knowledge['statistiques']['systemes_avec_echantillons'] = len(systems_with_samples)
        
        # Domaines
        for domain in domains:
            knowledge['domaines'].append({
                'nom': domain.name,
                'description': domain.description or '',
            })
        
        return knowledge
    
    def generate_report(self, knowledge):
        """Génère le rapport avec Claude"""
        
        prompt = f"""Tu es un expert en architecture des systèmes d'information pour Air Algérie.

IMPORTANT - CLARIFICATIONS:
- RAPID est un PRODUIT d'ACCELYA (Revenue Accounting), pas un système distinct
- Les fichiers AMADEUS proviennent du système ALTEA (PSS Amadeus)
- Distingue bien les "layouts" (structures de fichiers sans données) des échantillons avec données réelles
- La LOCALISATION indique où le système est installé/hébergé (Algérie = on-premise local, France = hébergé en France, International = Cloud mondial)

Voici l'intégralité du knowledge sur la cartographie SI d'Air Algérie au {knowledge['date_rapport']}:

## STATISTIQUES GLOBALES
- {knowledge['statistiques']['total_systemes']} systèmes cartographiés
- {knowledge['statistiques']['total_flux']} flux de données
- {knowledge['statistiques']['total_echantillons']} fichiers d'échantillons reçus
  - {knowledge['statistiques']['echantillons_avec_donnees']} avec données réelles
  - {knowledge['statistiques']['echantillons_layouts']} layouts/templates (structures sans données)
- {knowledge['statistiques']['total_colonnes_documentees']} colonnes/champs documentés au total
- {knowledge['statistiques']['systemes_avec_echantillons']} systèmes sources identifiés
- {knowledge['statistiques']['flux_critiques']} flux critiques

## LOCALISATION DES SYSTÈMES (IMPORTANT)
- **{knowledge['statistiques']['systemes_algerie']} systèmes installés en Algérie** (on-premise)
- **{knowledge['statistiques']['systemes_france']} systèmes hébergés en France**
- **{knowledge['statistiques']['systemes_international']} systèmes sur Cloud international**

### Systèmes hébergés en FRANCE:
{self._format_systems_by_location(knowledge['systemes_par_localisation']['france'])}

### Systèmes sur Cloud INTERNATIONAL:
{self._format_systems_by_location(knowledge['systemes_par_localisation']['international'])}

## SYSTÈMES ({len(knowledge['systemes'])})
{self._format_systems(knowledge['systemes'])}

## FLUX DE DONNÉES ({len(knowledge['flux'])})
{self._format_flows(knowledge['flux'])}

## ÉCHANTILLONS REÇUS ({len(knowledge['echantillons'])})
{self._format_samples(knowledge['echantillons'])}

## DOMAINES DE DONNÉES ({len(knowledge['domaines'])})
{self._format_domains(knowledge['domaines'])}

---

Génère un rapport d'analyse complet et professionnel en français avec les sections suivantes:

1. **RÉSUMÉ EXÉCUTIF** (2-3 paragraphes)
   - Vue d'ensemble de la cartographie SI
   - Points clés et chiffres importants
   - Mention de la répartition géographique des systèmes

2. **LOCALISATION DES SYSTÈMES** (SECTION OBLIGATOIRE)
   - Tableau récapitulatif des systèmes par pays d'hébergement
   - Liste détaillée des systèmes hébergés en France avec leur fonction
   - Liste des systèmes sur Cloud international
   - Implications en termes de souveraineté des données et dépendances

3. **DONNÉES REÇUES** 
   - Liste détaillée des échantillons reçus avec leur provenance
   - Analyse de la qualité et complétude des données
   - Colonnes/champs identifiés par système

4. **IMPLICATIONS POUR LA CARTOGRAPHIE**
   - Ce que les données reçues nous apprennent sur les flux
   - Validation des hypothèses existantes
   - Nouvelles informations découvertes

5. **ANALYSE DES GAPS**
   - Systèmes sans échantillons de données
   - Flux non documentés ou partiellement documentés
   - Données manquantes critiques

6. **RECOMMANDATIONS**
   - Actions prioritaires à mener
   - Données à collecter en priorité
   - Améliorations suggérées

7. **CONCLUSION ET ATTENTES** (SECTION OBLIGATOIRE)
   Cette section doit clairement énoncer:
   - **Ce que nous attendons des équipes métier**: quels documents, échantillons de données, ou informations sont nécessaires
   - **Ce que nous attendons de la DSI**: accès aux systèmes, documentation technique, contacts des éditeurs
   - **Prochaines étapes concrètes**: planning suggéré pour compléter la cartographie
   - **Livrables attendus**: ce que cette cartographie permettra de produire une fois complète

8. **ANNEXES**
   - Liste complète des systèmes par catégorie
   - Matrice des flux critiques

Le rapport doit être factuel, précis et actionnable. Utilise des listes à puces et des tableaux markdown quand c'est pertinent.
"""
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text
    
    def _format_systems(self, systems):
        """Formate les systèmes pour le prompt"""
        lines = []
        for s in systems:
            modules = ', '.join(s['modules'][:5]) if s['modules'] else 'N/A'
            domains = ', '.join(s['domaines_maitrises'][:3]) if s['domaines_maitrises'] else 'N/A'
            localisation = s.get('localisation', 'Algérie')
            lines.append(f"- **{s['code']}** ({s['nom']}) - Vendor: {s['vendor']}, Catégorie: {s['categorie']}, Criticité: {s['criticite']}, Mode: {s['mode']}, **Localisation: {localisation}**, Modules: {modules}, Domaines maîtrisés: {domains}")
        return '\n'.join(lines)
    
    def _format_systems_by_location(self, systems):
        """Formate les systèmes d'une localisation spécifique"""
        if not systems:
            return "Aucun système"
        lines = []
        for s in systems:
            lines.append(f"- **{s['code']}** ({s['nom']}) - {s['vendor']} - Mode: {s['mode']} - Criticité: {s['criticite']}")
        return '\n'.join(lines)
    
    def _format_flows(self, flows):
        """Formate les flux pour le prompt"""
        lines = []
        for f in flows:
            critical = " [CRITIQUE]" if f['critique'] else ""
            lines.append(f"- {f['source']} → {f['cible']}: **{f['nom']}** ({f['frequence']}, {f['protocole']}, {f['format']}){critical}")
        return '\n'.join(lines)
    
    def _format_samples(self, samples):
        """Formate les échantillons pour le prompt"""
        lines = []
        for s in samples:
            cols = ', '.join(s['colonnes'][:8]) if s['colonnes'] else 'N/A'
            nb_cols = len(s['colonnes']) if s['colonnes'] else 0
            
            # Clarifier la source
            source = s['systeme_source']
            if source == 'RAPID':
                source = 'ACCELYA (produit RAPID)'
            elif source == 'AMADEUS':
                source = 'ALTEA (Amadeus)'
            
            # Indiquer si c'est un layout ou des données réelles
            data_status = f"{s['nb_enregistrements']} enregistrements" if s['nb_enregistrements'] > 0 else "LAYOUT (structure uniquement, pas de données)"
            
            lines.append(f"- **{s['nom']}** (Source: {source}, Type: {s['type']})")
            lines.append(f"  Description: {s['description']}")
            lines.append(f"  Colonnes ({nb_cols}): {cols}")
            lines.append(f"  Données: {data_status}")
        return '\n'.join(lines)
    
    def _format_domains(self, domains):
        """Formate les domaines pour le prompt"""
        lines = []
        for d in domains:
            lines.append(f"- **{d['nom']}**: {d['description']}")
        return '\n'.join(lines)
