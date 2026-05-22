"""
Génère le workflow IA (étapes structurées + Mermaid) pour chaque Process
en utilisant Claude (Anthropic) via le service ProcessWorkflowGenerator.

Usage :
    python manage.py generate_process_workflows                # tous les Process Air Algérie sans workflow
    python manage.py generate_process_workflows --all          # même ceux qui ont déjà un workflow
    python manage.py generate_process_workflows --force        # écrase les workflows existants
    python manage.py generate_process_workflows --code PROC-AA-DOA-11
    python manage.py generate_process_workflows --limit 5
    python manage.py generate_process_workflows --prefix PROC-AA
    python manage.py generate_process_workflows --sleep 2      # délai entre 2 appels API

Source clé :
    1) variable d'environnement ANTHROPIC_API_KEY
    2) sinon, fichier --key-file (défaut : ../key.txt à la racine workspace)
"""
import os
import time

from django.core.management.base import BaseCommand
from django.db import transaction

from cartography.models import (
    Process,
    ProcessStep,
    Structure,
    System,
)


DEFAULT_KEY_FILE = '/Users/mohamedamine/Air Algérie/key.txt'


def load_api_key(key_file: str) -> str:
    key = os.environ.get('ANTHROPIC_API_KEY', '').strip()
    if key:
        return key
    if key_file and os.path.isfile(key_file):
        with open(key_file, encoding='utf-8') as fh:
            return fh.read().strip()
    return ''


class Command(BaseCommand):
    help = "Génère les workflows IA des Process via Claude API."

    def add_arguments(self, parser):
        parser.add_argument('--prefix', default='PROC-AA',
                            help="Préfixe des codes Process à traiter (défaut: PROC-AA)")
        parser.add_argument('--code', default=None,
                            help="Ne générer que pour un code Process précis (ex: PROC-AA-DOA-11)")
        parser.add_argument('--all', action='store_true',
                            help="Inclure les process qui ont déjà un workflow (sans écraser)")
        parser.add_argument('--force', action='store_true',
                            help="Écrase les workflows existants")
        parser.add_argument('--limit', type=int, default=0,
                            help="Limite le nombre de Process traités (0 = pas de limite)")
        parser.add_argument('--sleep', type=float, default=1.5,
                            help="Délai (s) entre 2 appels API (défaut: 1.5)")
        parser.add_argument('--key-file', default=DEFAULT_KEY_FILE,
                            help="Fichier contenant la clé API si la var d'env est absente")
        parser.add_argument('--dry-run', action='store_true',
                            help="N'effectue pas les appels API, affiche juste les Process ciblés")

    def handle(self, *args, **opts):
        prefix = opts['prefix']
        code = opts['code']
        force = opts['force']
        include_all = opts['all'] or force
        limit = opts['limit']
        sleep_s = opts['sleep']
        dry = opts['dry_run']

        # --- Sélection des Process ---
        qs = Process.objects.all()
        if code:
            qs = qs.filter(code=code)
        else:
            qs = qs.filter(code__startswith=f"{prefix}-")
        if not include_all:
            qs = qs.filter(workflow_mermaid='')
        qs = qs.order_by('code')
        if limit:
            qs = qs[:limit]

        processes = list(qs)
        if not processes:
            self.stdout.write(self.style.WARNING("Aucun Process à traiter."))
            return

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"Process à traiter : {len(processes)}"
        ))

        if dry:
            for p in processes:
                self.stdout.write(f"  - [{p.code}] {p.name[:80]}  (steps existants={p.steps.count()})")
            return

        # --- Chargement de la clé + service ---
        api_key = load_api_key(opts['key_file'])
        if not api_key:
            self.stderr.write(self.style.ERROR(
                f"Clé Anthropic introuvable (env ANTHROPIC_API_KEY ou fichier {opts['key_file']})"
            ))
            return

        from cartography.services.process_workflow_generator import (
            ProcessWorkflowGenerator,
        )

        generator = ProcessWorkflowGenerator(api_key)

        # Données de référence pour le prompt
        existing_structures = list(Structure.objects.values('code', 'name'))
        existing_systems = list(System.objects.values('code', 'name', 'description'))

        ok = 0
        skipped = 0
        failed = []

        for i, process in enumerate(processes, start=1):
            self.stdout.write('')
            self.stdout.write(self.style.MIGRATE_HEADING(
                f"[{i}/{len(processes)}] {process.code} — {process.name[:80]}"
            ))

            if process.workflow_mermaid and not force:
                self.stdout.write(self.style.WARNING(
                    "  ↷ workflow déjà présent, ignoré (utiliser --force pour réécrire)"
                ))
                skipped += 1
                continue

            ctx_text = process.context.strip()
            if not ctx_text:
                # Fallback : reconstruit un mini-contexte à partir des
                # métadonnées du Process (nom, description, structures,
                # systèmes liés). Permet de générer un workflow même
                # quand le champ `context` n'a pas été rempli.
                struct_lines = '\n'.join(
                    f"- {s.code} : {s.name}" for s in process.structures.all()
                ) or '- (non précisé)'
                sys_lines = '\n'.join(
                    f"- {s.code} : {s.name} — {s.description[:120]}"
                    for s in process.systems.all()
                ) or '- (non précisé)'
                ctx_text = (
                    f"# {process.name}\n\n"
                    f"## Description\n{process.description or '(à inférer)'}\n\n"
                    f"## Structures impliquées\n{struct_lines}\n\n"
                    f"## Systèmes utilisés\n{sys_lines}\n"
                )
                self.stdout.write(self.style.WARNING(
                    "  ! context vide → fallback sur metadata (name+structures+systems)"
                ))

            try:
                result = generator.generate(
                    process_name=process.name,
                    context_text=ctx_text,
                    existing_structures=existing_structures,
                    existing_systems=existing_systems,
                )
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"  !! échec API : {e}"))
                failed.append((process.code, str(e)))
                # backoff léger en cas de rate limit
                time.sleep(max(sleep_s, 5))
                continue

            steps_data = result.get('steps', []) or []
            mermaid = result.get('mermaid', '') or ''
            problems = result.get('problems', '') or ''
            recommendations = result.get('recommendations', '') or ''

            try:
                with transaction.atomic():
                    process.workflow_json = steps_data
                    process.workflow_mermaid = mermaid
                    if problems:
                        process.problems = problems
                    if recommendations:
                        process.recommendations = recommendations
                    process.ai_generated = True
                    process.save()

                    # Reset des étapes existantes
                    process.steps.all().delete()

                    extra_struct_ids = set()
                    extra_sys_ids = set()

                    for step_data in steps_data:
                        step = ProcessStep.objects.create(
                            process=process,
                            order=step_data.get('order', 0),
                            title=(step_data.get('title') or '')[:300],
                            description=step_data.get('description', '') or '',
                            step_type=step_data.get('step_type', 'MANUAL'),
                            actor_role=(step_data.get('actor_role') or '')[:200],
                            data_inputs=step_data.get('data_inputs', '') or '',
                            data_outputs=step_data.get('data_outputs', '') or '',
                            interactions=step_data.get('interactions', '') or '',
                            problems=step_data.get('problems', '') or '',
                            duration_estimate=(step_data.get('duration_estimate') or '')[:100],
                            next_steps=step_data.get('next_steps', []) or [],
                        )
                        struct_code = step_data.get('actor_structure_code')
                        if struct_code:
                            try:
                                s = Structure.objects.get(code=struct_code)
                                step.actor_structure = s
                                step.save(update_fields=['actor_structure'])
                                extra_struct_ids.add(s.id)
                            except Structure.DoesNotExist:
                                pass
                        for sys_name in step_data.get('systems_used', []) or []:
                            sys = (System.objects.filter(name__iexact=sys_name).first()
                                   or System.objects.filter(code__iexact=sys_name).first())
                            if not sys and sys_name:
                                first_word = sys_name.split()[0]
                                sys = System.objects.filter(name__icontains=first_word).first()
                            if sys:
                                step.systems_used.add(sys)
                                extra_sys_ids.add(sys.id)

                    # Auto-augment des structures/systems du process
                    if extra_struct_ids:
                        current = set(process.structures.values_list('id', flat=True))
                        process.structures.set(current | extra_struct_ids)
                    if extra_sys_ids:
                        current = set(process.systems.values_list('id', flat=True))
                        process.systems.set(current | extra_sys_ids)
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"  !! échec sauvegarde : {e}"))
                failed.append((process.code, str(e)))
                continue

            self.stdout.write(self.style.SUCCESS(
                f"  ✓ {len(steps_data)} étapes, {len(mermaid)} car. Mermaid"
            ))
            ok += 1

            if i < len(processes):
                time.sleep(sleep_s)

        # --- Résumé ---
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f"OK  généré={ok}  ignoré={skipped}  échec={len(failed)}"
        ))
        if failed:
            self.stdout.write(self.style.ERROR("\nÉchecs :"))
            for code, msg in failed:
                self.stdout.write(f"  - {code} : {msg[:150]}")
