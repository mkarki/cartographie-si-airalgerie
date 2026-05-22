"""
Export Phase 1 — Génère tous les exports tabulaires de la cartographie
nécessaires aux livrables du Lot 1 (Diagnostic & inventaire SI).

Usage :
    python manage.py export_phase1 --out "/Users/mohamedamine/Air Algérie/LIVRABLES_PHASE_1/Exports_Cartographie"

Produit :
    - structures.csv             : 17 structures organisationnelles
    - systemes.csv               : 38 systèmes (inventaire)
    - systemes_inventaire.md     : inventaire formaté markdown groupé par criticité
    - processus.csv              : tous les Process avec liens structures/systems
    - processus_workflows.json   : workflows IA (steps + mermaid + problems + reco)
    - flux_systemes.csv          : flux entre systèmes (si présents)
    - questionnaires.csv         : statut des questionnaires par système
    - donnees_par_systeme.md     : inventaire des données par système (synthèse)
"""
import csv
import json
import os
from collections import defaultdict

from django.core.management.base import BaseCommand

from cartography.models import (
    DataFlow,
    Process,
    Question,
    Questionnaire,
    Structure,
    System,
)


class Command(BaseCommand):
    help = "Exporte les données de la cartographie pour les livrables Phase 1."

    def add_arguments(self, parser):
        parser.add_argument(
            '--out',
            required=True,
            help="Dossier de destination des exports (sera créé si absent)",
        )

    def handle(self, *args, **opts):
        out = opts['out']
        os.makedirs(out, exist_ok=True)

        self.export_structures(out)
        self.export_systemes(out)
        self.export_systemes_inventaire(out)
        self.export_processus(out)
        self.export_processus_workflows(out)
        self.export_flux(out)
        self.export_questionnaires(out)
        self.export_donnees_par_systeme(out)

        self.stdout.write(self.style.SUCCESS(f"\nExports générés dans : {out}"))

    # -------- helpers --------
    def write_csv(self, path, headers, rows):
        with open(path, 'w', newline='', encoding='utf-8') as fh:
            w = csv.writer(fh, quoting=csv.QUOTE_MINIMAL)
            w.writerow(headers)
            w.writerows(rows)
        self.stdout.write(f"  ✓ {os.path.basename(path)} ({len(rows)} lignes)")

    # -------- exports --------
    def export_structures(self, out):
        rows = []
        for s in Structure.objects.all().order_by('code'):
            parent = s.parent.code if s.parent else ''
            rows.append([
                s.code, s.name, s.level or '', parent,
                s.country, s.responsable or '', (s.description or '').strip()[:300],
            ])
        self.write_csv(
            os.path.join(out, 'structures.csv'),
            ['code', 'name', 'level', 'parent_code', 'country', 'responsable', 'description'],
            rows,
        )

    def export_systemes(self, out):
        rows = []
        for s in System.objects.select_related('structure', 'category').all().order_by('structure__code', 'code'):
            rows.append([
                s.code,
                s.name,
                s.structure.code,
                s.structure.name,
                s.category.name if s.category else '',
                s.vendor or '',
                s.mode,
                s.criticality,
                s.country or '',
                s.version or '',
                (s.is_master_for or '').replace('\n', ' ').strip()[:200],
                (s.description or '').replace('\n', ' ').strip()[:500],
            ])
        self.write_csv(
            os.path.join(out, 'systemes.csv'),
            ['code', 'name', 'structure_code', 'structure_name', 'category',
             'vendor', 'mode', 'criticality', 'country', 'version',
             'is_master_for', 'description'],
            rows,
        )

    def export_systemes_inventaire(self, out):
        path = os.path.join(out, 'systemes_inventaire.md')
        groups = defaultdict(list)
        for s in System.objects.select_related('structure').all():
            groups[s.criticality].append(s)
        order = ['CRITIQUE', 'HAUTE', 'MOYENNE', 'BASSE', 'NON_DEFINIE']
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write("# Inventaire des systèmes — par criticité\n\n")
            for crit in order:
                items = sorted(groups.get(crit, []), key=lambda x: (x.structure.code, x.code))
                if not items:
                    continue
                fh.write(f"## {crit} ({len(items)} systèmes)\n\n")
                fh.write("| Code | Nom | Structure | Éditeur | Mode | Pays |\n")
                fh.write("|---|---|---|---|---|---|\n")
                for s in items:
                    fh.write(f"| `{s.code}` | {s.name} | {s.structure.code} | "
                             f"{s.vendor or '—'} | {s.mode} | {s.country or '—'} |\n")
                fh.write("\n")
        self.stdout.write(f"  ✓ systemes_inventaire.md")

    def export_processus(self, out):
        rows = []
        for p in (Process.objects
                  .prefetch_related('structures', 'systems', 'steps')
                  .all().order_by('code')):
            rows.append([
                p.code,
                p.name,
                p.category,
                p.status,
                ','.join(s.code for s in p.structures.all()),
                ','.join(s.code for s in p.systems.all()),
                p.steps.count(),
                'OUI' if p.workflow_mermaid else 'NON',
                'OUI' if p.ai_generated else 'NON',
                p.created_by or '',
                p.source_questionnaire or '',
            ])
        self.write_csv(
            os.path.join(out, 'processus.csv'),
            ['code', 'name', 'category', 'status', 'structures', 'systems',
             'nb_steps', 'has_workflow', 'ai_generated', 'created_by', 'source'],
            rows,
        )

    def export_processus_workflows(self, out):
        data = []
        for p in (Process.objects
                  .prefetch_related('structures', 'systems', 'steps__systems_used',
                                    'steps__actor_structure')
                  .exclude(workflow_mermaid='').order_by('code')):
            steps = []
            for st in p.steps.all().order_by('order'):
                steps.append({
                    'order': st.order,
                    'title': st.title,
                    'description': st.description,
                    'step_type': st.step_type,
                    'actor_role': st.actor_role,
                    'actor_structure': st.actor_structure.code if st.actor_structure else None,
                    'systems_used': [s.code for s in st.systems_used.all()],
                    'data_inputs': st.data_inputs,
                    'data_outputs': st.data_outputs,
                    'interactions': st.interactions,
                    'problems': st.problems,
                    'duration_estimate': st.duration_estimate,
                    'next_steps': st.next_steps,
                })
            data.append({
                'code': p.code,
                'name': p.name,
                'category': p.category,
                'structures': [s.code for s in p.structures.all()],
                'systems': [s.code for s in p.systems.all()],
                'context': p.context,
                'workflow_mermaid': p.workflow_mermaid,
                'problems': p.problems,
                'recommendations': p.recommendations,
                'steps': steps,
            })
        path = os.path.join(out, 'processus_workflows.json')
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        self.stdout.write(f"  ✓ processus_workflows.json ({len(data)} workflows)")

    def export_flux(self, out):
        rows = []
        for f in DataFlow.objects.select_related('source', 'target').all():
            rows.append([
                f.source.code,
                f.target.code,
                f.name,
                (f.description or '').replace('\n', ' ').strip()[:300],
                f.frequency,
                f.protocol,
                f.format,
                f.volume,
                'OUI' if f.is_automated else 'NON',
                'OUI' if f.is_critical else 'NON',
            ])
        self.write_csv(
            os.path.join(out, 'flux_systemes.csv'),
            ['source', 'target', 'name', 'description', 'frequency',
             'protocol', 'format', 'volume', 'automated', 'critical'],
            rows,
        )

    def export_questionnaires(self, out):
        rows = []
        for q in Questionnaire.objects.select_related('system', 'system__structure').all():
            total = Question.objects.filter(section__questionnaire=q).count()
            answered = Question.objects.filter(section__questionnaire=q).exclude(answer='').count()
            sys_code = q.system.code if q.system else ''
            struct_code = q.system.structure.code if q.system and q.system.structure else ''
            rows.append([
                sys_code,
                q.system_name,
                struct_code,
                q.status,
                f"P{q.phase}",
                (q.key_users or '').replace('\n', ' / ')[:200],
                total,
                answered,
                f"{(answered/total*100):.0f}%" if total else "—",
            ])
        self.write_csv(
            os.path.join(out, 'questionnaires.csv'),
            ['system_code', 'system_name', 'structure', 'status', 'phase',
             'key_users', 'questions_total', 'questions_answered', 'pct'],
            rows,
        )

    def export_donnees_par_systeme(self, out):
        """Synthèse markdown : pour chaque système avec questionnaire,
        extrait les réponses contenant des références aux entités/données métier."""
        path = os.path.join(out, 'donnees_par_systeme.md')
        kws = ['donnée', 'donnees', 'donnée', 'entité', 'champs', 'fichier',
               'volume', 'export', 'extract', 'table', 'flux', 'format', 'csv',
               'xml', 'json', 'sftp', 'api', 'base', 'bdd']
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write("# Inventaire des données par système (extraits questionnaires)\n\n")
            fh.write("Synthèse automatique des réponses key users mentionnant "
                     "des entités, formats, volumes ou flux de données.\n\n")
            for q in (Questionnaire.objects
                      .select_related('system', 'system__structure')
                      .order_by('system__criticality', 'system__code')):
                hits = []
                for question in (Question.objects
                                 .filter(section__questionnaire=q)
                                 .exclude(answer='')
                                 .order_by('section__order', 'order')):
                    ans_low = (question.answer or '').lower()
                    if any(k in ans_low for k in kws):
                        hits.append(question)
                if not hits:
                    continue
                sys_code = q.system.code if q.system else q.system_name
                struct_code = q.system.structure.code if q.system and q.system.structure else '—'
                criticality = q.system.criticality if q.system else '—'
                mode = q.system.mode if q.system else '—'
                fh.write(f"## {sys_code} — {q.system_name}\n")
                fh.write(f"*Structure : {struct_code} · Criticité : {criticality} · Mode : {mode}*\n\n")
                for question in hits[:15]:  # max 15 par système
                    a = (question.answer or '').replace('\n', ' ').strip()
                    fh.write(f"- **{question.number} — {question.text[:120]}**  \n"
                             f"  → {a[:500]}\n\n")
                fh.write("\n---\n\n")
        self.stdout.write(f"  ✓ donnees_par_systeme.md")
