"""
Import des process metier collectés via les canevas Excel
('process AIRDZ/' rempli par les key users) dans la base locale.

Lit `process_airdz_extracted.json` (produit par extract_processes_airdz.py),
matche les Structures et les Systems existants, et crée/maj les Process.
Pour chaque Process matché à un Système, le `source_questionnaire`
est renseigné et les réponses non-vides du questionnaire sont jointes
au champ `context` afin d'enrichir la fiche.

Note : le préfixe historique des codes était `PROC-AIRDZ-`. Il a été renommé
en `PROC-AA-` (Air Algérie) le 22/05/2026. Les noms de fichiers physiques
('process AIRDZ/', 'process_airdz_extracted.json') sont conservés tels quels.

Usage:
    python manage.py import_process_airdz
    python manage.py import_process_airdz --dry-run
    python manage.py import_process_airdz --reset   # supprime les process Air Algérie déjà importés
"""
import json
import os
import re
import unicodedata

from django.core.management.base import BaseCommand
from django.db import transaction

from cartography.models import (
    Process,
    Question,
    Questionnaire,
    Structure,
    System,
)


JSON_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', '..', '..',
    'process_airdz_extracted.json',
)
JSON_FILE = os.path.abspath(JSON_FILE)


# ---- Mapping dossier → code Structure -----------------------------------
DIRECTION_FOLDER_TO_STRUCTURE = {
    'DC': 'DC',
    'DIVEX:CCO$': 'DIVEX',
    'DOA': 'DOA',
    'DSC': 'DSC',
    'DSI': 'DSI',
    # DCS = sous-direction SI au sein d'AH Ground Operation (LOUNAOUCI)
    # → rattachée fonctionnellement à la DOS (Direction des Opérations Sol)
    'DCS': 'DOS',
}

# Catégorie Process par défaut selon la direction
DIRECTION_TO_CATEGORY = {
    'DC': 'COMMERCIAL',
    'DIVEX': 'OPERATIONAL',
    'CCO': 'OPERATIONAL',
    'DOA': 'OPERATIONAL',
    'DSC': 'SUPPORT',
    'DSI': 'IT',
    'DRH': 'HR',
    'DRM': 'COMMERCIAL',
    'DOS': 'OPERATIONAL',
    'DMRA': 'MAINTENANCE',
    'DFC': 'FINANCE',
    'DAGP': 'SUPPORT',
}

# Mapping ad-hoc (raw fragment → System.code) pour les libellés ambigus
SYSTEM_ALIASES = {
    'zimbra admin': 'ZIMBRA',
    'zimbra backup': 'ZIMBRA',
    'zimbra': 'ZIMBRA',
    'liferay': 'PORTAIL',
    'portail ah': 'PORTAIL',
    'glpi': 'GLPI',
    'aims': 'AIMS',
    'q-pulse': 'QPULSE',
    'qpulse': 'QPULSE',
    'q pulse': 'QPULSE',
    'ags': 'AGS',
    'hermes-net': 'VOCALCOM',
    'hermes net': 'VOCALCOM',
    'hermes call center': 'VOCALCOM',
    'hermes': 'ACARS',          # contexte CCO (HERMES Collins) — sinon override manuel
    'opscore': None,            # pas dans le SI : à créer plus tard
    'plateforme bsp': 'BSPLINK',
    'iata billing and settlement plan': 'BSPLINK',
    'bsp link': 'BSPLINK',
    'bsplink': 'BSPLINK',
    'accelya bidt': 'ACCELYA-DIST',
    'bidt audit': 'ACCELYA-DIST',
    'accelya': 'ACCELYA-DIST',
    'plateforme e-exam': 'EEXAM',
    'e-exam': 'EEXAM',
    'eexam': 'EEXAM',
    'outil de mailing': 'DOA-MAILING',
    'doa mailing': 'DOA-MAILING',
    'call 360': 'CALL-DOA',
    'centre d\u2019appels': 'CALL-DOA',
    'centre d\'appels': 'CALL-DOA',
    'call doa': 'CALL-DOA',
    'erp-rh': None,             # système non encore créé
    'erp rh': None,
    'sitatex': 'SITATEX',
    'world tracer': 'WORLDTRACER',
    'amos': 'AMOS',
    'altea': 'ALTEA',
    'sage finance': 'SAGE-FIN',
    'sage stock': 'SAGE-STOCK',
    'site web': 'SITEWEB',
    'jetplanner': 'JETPLAN',
    'jetplanner pro': 'JETPLAN',
    'jet planner': 'JETPLAN',
    'jet planner pro': 'JETPLAN',
    'skybook': 'SKYBOOK',
    'le systeme inventaire ah': 'ALTEA',  # canevas LOUNAOUCI : Altéa Inventory côté AH
    'systeme inventaire ah': 'ALTEA',
}

# Mots à ignorer dans le parsing systems_raw (outils bureautiques / formats)
IGNORE_TOKENS = {
    'excel', 'mails', 'mail', 'email', 'emails', 'word', 'pdf', 'xls', 'xlsx',
    'mysql', 'mariadb', 'base de donn\u00e9es', 'base de donnees', 'crm',
    'sql', 'serveur', 'server', 'scripts', 'script', 'pour les slots',
    'lien de la dmra', 'ssim', 'outils de reporting doa',
}


def _norm(s: str) -> str:
    if not s:
        return ''
    # Normalise les guillemets/apostrophes typographiques avant decomposition
    s = (s.replace('’', "'").replace('‘', "'")
          .replace('“', '"').replace('”', '"'))
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'\s+', ' ', s.lower().strip())


def split_systems_raw(raw: str):
    """Découpe la chaine 'systems used' en tokens nettoyés."""
    if not raw:
        return []
    # remplace les séparateurs courants par des virgules
    cleaned = re.sub(r'[/;|]', ',', raw)
    parts = [p.strip() for p in cleaned.split(',')]
    out = []
    for p in parts:
        n = _norm(p)
        if not n:
            continue
        if n in IGNORE_TOKENS:
            continue
        # Retire des phrases entre parenthèses
        p_clean = re.sub(r'\([^)]*\)', '', p).strip()
        if p_clean:
            out.append(p_clean)
        else:
            out.append(p)
    return out


def match_system(token: str, systems_by_code, systems_by_name_norm):
    """Tente de matcher un token de systems_raw à un System existant.
    Retourne l'objet System ou None."""
    n = _norm(token)
    if not n or n in IGNORE_TOKENS:
        return None

    # 1) alias ad-hoc
    for alias, code in SYSTEM_ALIASES.items():
        if alias in n:
            if code is None:
                return None
            return systems_by_code.get(code)

    # 2) match direct sur code
    for code, sys in systems_by_code.items():
        if _norm(code) == n:
            return sys

    # 3) match par nom (normalisé) — substring dans les 2 sens
    for name_norm, sys in systems_by_name_norm.items():
        if name_norm == n:
            return sys
    for name_norm, sys in systems_by_name_norm.items():
        if name_norm and (name_norm in n or n in name_norm):
            return sys
    return None


def slugify_code(s: str, maxlen: int = 30) -> str:
    s = _norm(s).upper()
    s = re.sub(r'[^A-Z0-9]+', '-', s).strip('-')
    return s[:maxlen]


def build_context(proc, matched_systems, structure):
    """Construit le champ context enrichi à partir de la fiche + des
    réponses des questionnaires associés."""
    parts = []
    parts.append(f"# {proc['name']}")
    parts.append('')
    if proc.get('description'):
        parts.append('## Description')
        parts.append(proc['description'])
        parts.append('')
    if proc.get('systems_raw'):
        parts.append('## Systèmes utilisés (déclaratif key user)')
        parts.append(proc['systems_raw'])
        parts.append('')
    if proc.get('outputs_kpi'):
        parts.append('## Outputs / KPI')
        parts.append(proc['outputs_kpi'])
        parts.append('')

    # Enrichissement depuis les questionnaires des systèmes matchés
    for sys in matched_systems:
        try:
            q = sys.questionnaire
        except Questionnaire.DoesNotExist:
            q = None
        if not q:
            continue
        answered = (
            Question.objects
            .filter(section__questionnaire=q)
            .exclude(answer='')
            .order_by('section__order', 'order')[:8]
        )
        if not answered.exists():
            continue
        parts.append(f"## Contexte questionnaire — {sys.name} ({sys.code})")
        for question in answered:
            ans = (question.answer or '').strip().replace('\r', '')
            if not ans:
                continue
            ans_short = ans if len(ans) <= 350 else ans[:350].rstrip() + '…'
            parts.append(f"- **{question.number} — {question.text[:120]}** : {ans_short}")
        parts.append('')

    return '\n'.join(parts).strip()


class Command(BaseCommand):
    help = "Importe les process Air Algérie depuis process_airdz_extracted.json"

    def add_arguments(self, parser):
        parser.add_argument('--json', default=JSON_FILE, help='Chemin du JSON')
        parser.add_argument('--dry-run', action='store_true',
                            help="Affiche ce qui serait fait, sans écrire en DB")
        parser.add_argument('--reset', action='store_true',
                            help="Supprime tous les process avec code commençant par PROC-AA-")
        parser.add_argument('--prefix', default='PROC-AA',
                            help="Préfixe des codes Process générés")

    def handle(self, *args, **opts):
        path = opts['json']
        dry = opts['dry_run']
        prefix = opts['prefix']

        if not os.path.isfile(path):
            self.stderr.write(self.style.ERROR(f"JSON introuvable : {path}"))
            return

        with open(path, encoding='utf-8') as fh:
            data = json.load(fh)

        # --- Index Structures et Systems ---
        structures = {s.code: s for s in Structure.objects.all()}
        systems = list(System.objects.select_related('structure', 'category'))
        systems_by_code = {s.code: s for s in systems}
        systems_by_name_norm = {_norm(s.name): s for s in systems}

        # --- Reset éventuel ---
        if opts['reset']:
            qs = Process.objects.filter(code__startswith=prefix + '-')
            n = qs.count()
            self.stdout.write(self.style.WARNING(f"Reset : {n} process supprimés (prefix={prefix})"))
            if not dry:
                qs.delete()

        created = 0
        updated = 0
        unmatched_systems = []
        warnings = []

        with transaction.atomic():
            for block in data:
                struct_code = DIRECTION_FOLDER_TO_STRUCTURE.get(block['direction_folder'])
                structure = structures.get(struct_code)
                if not structure:
                    warnings.append(f"Direction non mappée : {block['direction_folder']}")
                    continue

                # Cas particulier : ADNAN.XLSX → DSI mais division "DAG/DRH"
                # → on lie aussi DRH si la division le suggère
                extra_structures = []
                div_norm = _norm(block.get('division', ''))
                if 'drh' in div_norm and 'DRH' in structures:
                    extra_structures.append(structures['DRH'])
                if 'cco' in div_norm and 'CCO' in structures:
                    extra_structures.append(structures['CCO'])
                if 'dvr' in div_norm or 'vente' in div_norm and 'DVR' in structures:
                    if 'DVR' in structures:
                        extra_structures.append(structures['DVR'])

                # Pour le code, on prend le code de structure principal
                effective_struct_code = struct_code
                # Adnan : c'est RH → préférence DRH pour catégorisation
                if 'drh' in div_norm:
                    effective_struct_code = 'DRH'

                category = DIRECTION_TO_CATEGORY.get(effective_struct_code, 'OPERATIONAL')

                # Sequencing par direction (les codes restent uniques
                # même en dry-run grâce au compteur local).
                if not hasattr(self, '_seq'):
                    self._seq = {}
                if struct_code not in self._seq:
                    self._seq[struct_code] = (
                        Process.objects.filter(code__startswith=f"{prefix}-{struct_code}-")
                        .count()
                    )
                seq_start = self._seq[struct_code] + 1

                self.stdout.write('')
                self.stdout.write(self.style.MIGRATE_HEADING(
                    f"== {block['file']} — {block['key_user']} ({len(block['processes'])} process)"
                ))

                for i, proc in enumerate(block['processes']):
                    seq = seq_start + i
                    code = f"{prefix}-{struct_code}-{seq:02d}"
                    self._seq[struct_code] = seq

                    # Match systèmes
                    matched = []
                    raw_tokens = split_systems_raw(proc.get('systems_raw', ''))
                    for tok in raw_tokens:
                        sys = match_system(tok, systems_by_code, systems_by_name_norm)
                        if sys and sys not in matched:
                            matched.append(sys)
                        elif not sys:
                            unmatched_systems.append((block['file'], proc['name'], tok))

                    # Source questionnaire = celui du premier système matché qui en a un
                    source_q = None
                    for s in matched:
                        try:
                            source_q = s.questionnaire
                            break
                        except Questionnaire.DoesNotExist:
                            continue

                    description = (proc.get('description') or '')[:1000]
                    context_md = build_context(proc, matched, structure)

                    name_clean = (proc['name'] or '').strip()[:300]

                    if dry:
                        sys_codes = ','.join(s.code for s in matched) or '—'
                        self.stdout.write(
                            f"  [{code}] {name_clean[:70]}  systems={sys_codes}"
                        )
                        continue

                    p, was_created = Process.objects.update_or_create(
                        code=code,
                        defaults={
                            'name': name_clean,
                            'description': description,
                            'context': context_md,
                            'category': category,
                            'status': 'DOCUMENTED',
                            'source_questionnaire': source_q,
                            'created_by': block.get('key_user', ''),
                        },
                    )
                    p.structures.set([structure] + extra_structures)
                    p.systems.set(matched)
                    if was_created:
                        created += 1
                    else:
                        updated += 1
                    sys_codes = ','.join(s.code for s in matched) or '—'
                    self.stdout.write(
                        f"  {'+' if was_created else '~'} [{code}] {name_clean[:60]}  → {sys_codes}"
                    )

            if dry:
                self.stdout.write(self.style.WARNING('\nDRY-RUN : aucune écriture'))
                transaction.set_rollback(True)

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f"OK  Process créés={created}  mis à jour={updated}"
        ))
        if unmatched_systems:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING(
                f"Tokens systèmes non matchés ({len(unmatched_systems)}) :"
            ))
            seen = set()
            for f, p, t in unmatched_systems:
                key = (f, t)
                if key in seen:
                    continue
                seen.add(key)
                self.stdout.write(f"  - {f}  proc='{p[:40]}'  token='{t}'")
        if warnings:
            self.stdout.write('')
            for w in warnings:
                self.stdout.write(self.style.WARNING(w))
