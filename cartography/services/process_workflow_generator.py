"""
Service de génération de workflow process via Claude API.
Prend un contexte en langage naturel et génère :
- Un workflow structuré (JSON steps)
- Un diagramme Mermaid
- L'identification des acteurs, systèmes, problèmes
"""
import json
import anthropic
from django.conf import settings


class ProcessWorkflowGenerator:
    """Génère un workflow structuré à partir d'une description en langage naturel."""

    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"

    def generate(self, process_name, context_text, existing_structures=None, existing_systems=None):
        """
        Génère le workflow complet à partir du contexte.
        
        Returns dict:
            steps: [{order, title, description, step_type, actor_role, actor_structure_code,
                      systems_used, data_inputs, data_outputs, interactions, problems, duration_estimate}]
            mermaid: str (code Mermaid flowchart)
            problems: str (problèmes consolidés)
            recommendations: str
            structures_identified: [str] (codes structures)
            systems_identified: [str] (noms systèmes)
        """
        structures_list = ""
        if existing_structures:
            structures_list = "\n".join(
                f"- {s['code']}: {s['name']}" for s in existing_structures
            )

        systems_list = ""
        if existing_systems:
            systems_list = "\n".join(
                f"- {s['name']} ({s['code']}): {s['description'][:100]}" for s in existing_systems
            )

        prompt = f"""Tu es un expert en modélisation de processus métier pour Air Algérie.

CONTEXTE: On documente les process métier dans le cadre d'une cartographie SI. 
Le texte ci-dessous est une description en langage naturel d'un process, issue d'un entretien.

PROCESS: {process_name}

DESCRIPTION:
{context_text}

---

STRUCTURES ORGANISATIONNELLES EXISTANTES (utilise ces codes quand possible):
{structures_list or "Non fournies"}

SYSTÈMES SI EXISTANTS (utilise ces noms quand possible):
{systems_list or "Non fournis"}

---

INSTRUCTIONS:
Analyse cette description et génère un JSON avec la structure EXACTE suivante (pas de texte avant/après, uniquement le JSON):

{{
  "steps": [
    {{
      "order": 1,
      "title": "Titre court de l'étape",
      "description": "Description détaillée de ce qui se passe",
      "step_type": "MANUAL|AUTOMATED|DECISION|INPUT|OUTPUT|WAIT|PARALLEL",
      "actor_role": "Poste/rôle responsable (ex: Agent d'escale, Chef de station)",
      "actor_structure_code": "Code structure existante ou null",
      "systems_used": ["Nom du système utilisé"],
      "data_inputs": "Données en entrée",
      "data_outputs": "Données en sortie",
      "interactions": "Type d'interaction (homme→système, système→système, etc.)",
      "problems": "Problème spécifique à cette étape (ou vide)",
      "duration_estimate": "Estimation de durée (ou vide)",
      "next_steps": [2]
    }}
  ],
  "mermaid": "flowchart TD\\n    A[Étape 1] --> B[Étape 2]\\n    ...",
  "problems": "Liste consolidée des problèmes et dysfonctionnements identifiés",
  "recommendations": "Recommandations d'amélioration",
  "structures_identified": ["CODE1", "CODE2"],
  "systems_identified": ["Système1", "Système2"]
}}

RÈGLES IMPORTANTES:
1. Le Mermaid DOIT être un flowchart TD (top-down) valide et lisible
2. Chaque nœud Mermaid doit avoir un ID court (A, B, C...) et un label descriptif entre crochets
3. Les points de décision utilisent la syntaxe losange {{  }} en Mermaid
4. Utilise des couleurs dans le Mermaid: style pour les problèmes (rouge), les systèmes (bleu), les décisions (orange)
5. actor_structure_code DOIT correspondre à un code existant de la liste fournie, ou être null
6. systems_used DOIT correspondre aux noms exacts des systèmes de la liste fournie quand possible
7. Si un système n'est pas dans la liste (ex: Excel, email), l'indiquer quand même
8. Sois exhaustif: décompose le process en maximum d'étapes pertinentes
9. Les next_steps permettent de modéliser les branches (décisions avec plusieurs sorties)
10. Le Mermaid doit inclure des sous-graphes (subgraph) pour regrouper par acteur/structure quand pertinent

Réponds UNIQUEMENT avec le JSON, sans ```json ni texte autour."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=6000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        raw = message.content[0].text.strip()
        # Nettoyage si Claude ajoute des backticks
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()

        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            # Tenter d'extraire le JSON du texte
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start >= 0 and end > start:
                result = json.loads(raw[start:end])
            else:
                raise ValueError(f"Impossible de parser la réponse IA: {raw[:200]}")

        return result

    def regenerate_mermaid(self, steps_data):
        """Régénère uniquement le diagramme Mermaid à partir des étapes structurées."""
        steps_text = json.dumps(steps_data, ensure_ascii=False, indent=2)

        prompt = f"""Génère un diagramme Mermaid flowchart TD à partir de ces étapes de process.

ÉTAPES:
{steps_text}

RÈGLES:
- flowchart TD (top-down)
- IDs courts (A, B, C...)
- Labels descriptifs entre crochets [ ] ou losanges {{ }} pour les décisions
- Sous-graphes par structure/acteur quand pertinent
- Couleurs: rouge pour les problèmes, bleu pour les systèmes
- Le code Mermaid doit être valide et directement utilisable

Réponds UNIQUEMENT avec le code Mermaid, sans backticks ni texte autour."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()

        return raw
