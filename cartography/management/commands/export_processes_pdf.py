"""
Export PDF — Génère un PDF consolidé contenant tous les process documentés,
avec rendu graphique des workflows Mermaid (SVG via mmdc ou mermaid.ink).

Usage :
    python manage.py export_processes_pdf --out "/chemin/vers/Processes.pdf"
    python manage.py export_processes_pdf --out "..." --only-with-workflow
    python manage.py export_processes_pdf --out "..." --structure DOA
    python manage.py export_processes_pdf --out "..." --renderer mermaid_ink

Dépendances :
  - mmdc (mermaid-cli) installé via npm/npx — auto-détecté
  - sinon fallback réseau sur https://mermaid.ink/svg/<base64>
"""
import base64
import os
import re
import shutil
import subprocess
import tempfile
import zlib
from datetime import datetime
from urllib.parse import quote

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from cartography.models import Process


def _which_mmdc():
    """Localise mmdc (mermaid-cli) sur le PATH, sinon tente npx."""
    path = shutil.which('mmdc')
    if path:
        return ['mmdc']
    npx = shutil.which('npx')
    if npx:
        return [npx, '-y', '-p', '@mermaid-js/mermaid-cli', 'mmdc']
    return None


def _render_via_mmdc(mermaid_code, work_dir, code, base_cmd, stderr):
    """Rend un Mermaid en PNG via mmdc local. Retourne (png_bytes|None)."""
    in_path = os.path.join(work_dir, f'{code}.mmd')
    out_path = os.path.join(work_dir, f'{code}.png')
    with open(in_path, 'w', encoding='utf-8') as f:
        f.write(mermaid_code)
    cmd = base_cmd + [
        '-i', in_path,
        '-o', out_path,
        '-b', 'white',
        '-t', 'default',
        '-w', '1600',
        '-s', '2',  # scale factor pour qualité
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except Exception as e:
        stderr.write(f"  mmdc erreur ({code}): {e}")
        return None
    if res.returncode != 0 or not os.path.exists(out_path):
        stderr.write(f"  mmdc échec ({code}): {res.stderr[:200]}")
        return None
    with open(out_path, 'rb') as f:
        return f.read()


def _render_via_mermaid_ink(mermaid_code, code, stderr):
    """Fallback : rend en PNG via mermaid.ink. Retourne (png_bytes|None)."""
    try:
        import urllib.request
        b64 = base64.urlsafe_b64encode(mermaid_code.encode('utf-8')).decode('ascii')
        url = f'https://mermaid.ink/img/{b64}?type=png&bgColor=FFFFFF&scale=2'
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; AirAlgerieCartographie/1.0)',
            'Accept': 'image/png,image/*,*/*;q=0.8',
        })
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = resp.read()
        # PNG signature: \x89PNG\r\n\x1a\n
        if not data.startswith(b'\x89PNG'):
            stderr.write(f"  mermaid.ink retour non-PNG ({code})")
            return None
        return data
    except Exception as e:
        stderr.write(f"  mermaid.ink erreur ({code}): {e}")
        return None


def _render_via_kroki(mermaid_code, code, stderr):
    """Rend en PNG via kroki.io. Retourne (png_bytes|None).

    PNG plutôt que SVG car les SVG Mermaid utilisent <foreignObject>
    pour les labels HTML, non supporté par WeasyPrint.
    """
    try:
        import urllib.request
        compressed = zlib.compress(mermaid_code.encode('utf-8'), 9)
        b64 = base64.urlsafe_b64encode(compressed).decode('ascii')
        url = f'https://kroki.io/mermaid/png/{b64}'
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; AirAlgerieCartographie/1.0)',
            'Accept': 'image/png,*/*;q=0.8',
        })
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        if not data.startswith(b'\x89PNG'):
            stderr.write(f"  kroki retour non-PNG ({code}) — {data[:50]!r}")
            return None
        return data
    except Exception as e:
        stderr.write(f"  kroki erreur ({code}): {e}")
        return None


class Command(BaseCommand):
    help = "Exporte tous les process documentés dans un seul PDF (avec workflows graphiques)."

    def add_arguments(self, parser):
        parser.add_argument('--out', required=True, help="Chemin du PDF en sortie")
        parser.add_argument('--only-with-workflow', action='store_true',
                            help="N'inclure que les process avec un workflow Mermaid")
        parser.add_argument('--structure', default=None,
                            help="Filtrer par code structure (ex: DOA)")
        parser.add_argument('--renderer', choices=['auto', 'mmdc', 'mermaid_ink', 'kroki', 'none'],
                            default='auto',
                            help="Mode de rendu Mermaid (auto = mmdc → kroki → mermaid.ink)")
        parser.add_argument('--title', default='Cartographie des Processus — Air Algérie',
                            help="Titre du PDF")

    def handle(self, *args, **opts):
        from weasyprint import HTML

        qs = (Process.objects
              .prefetch_related('structures', 'systems',
                                'steps__systems_used', 'steps__actor_structure')
              .all().order_by('code'))

        if opts['only_with_workflow']:
            qs = qs.exclude(workflow_mermaid='')
        if opts['structure']:
            qs = qs.filter(structures__code=opts['structure']).distinct()

        processes = list(qs)
        self.stdout.write(f"Process à inclure : {len(processes)}")

        if not processes:
            self.stderr.write("Aucun process à exporter — abandon.")
            return

        # ─── Rendu des workflows Mermaid en SVG ───
        renderer = opts['renderer']
        nb_with_mermaid = sum(1 for p in processes if p.workflow_mermaid)
        if nb_with_mermaid and renderer != 'none':
            self.stdout.write(f"Rendu graphique de {nb_with_mermaid} workflow(s) Mermaid…")
            mmdc_cmd = _which_mmdc() if renderer in ('auto', 'mmdc') else None
            use_mmdc = mmdc_cmd is not None
            if use_mmdc:
                self.stdout.write(self.style.SUCCESS(f"  mmdc détecté : {' '.join(mmdc_cmd[:2])}…"))
            elif renderer == 'mmdc':
                self.stderr.write(self.style.WARNING(
                    "  mmdc introuvable — installe @mermaid-js/mermaid-cli ou utilise --renderer mermaid_ink"))

            work_dir = tempfile.mkdtemp(prefix='mermaid_render_')
            ok = 0
            ko = 0
            try:
                for p in processes:
                    p.workflow_png_b64 = None
                    if not p.workflow_mermaid:
                        continue
                    png = None
                    if use_mmdc:
                        png = _render_via_mmdc(p.workflow_mermaid, work_dir, p.code,
                                               mmdc_cmd, self.stderr)
                    if png is None and renderer in ('auto', 'kroki'):
                        png = _render_via_kroki(p.workflow_mermaid, p.code, self.stderr)
                    if png is None and renderer in ('auto', 'mermaid_ink'):
                        png = _render_via_mermaid_ink(p.workflow_mermaid, p.code, self.stderr)
                    if png:
                        p.workflow_png_b64 = base64.b64encode(png).decode('ascii')
                        ok += 1
                        self.stdout.write(f"  ✓ {p.code} ({len(png):,} octets PNG)")
                    else:
                        ko += 1
                        self.stdout.write(self.style.WARNING(
                            f"  ✗ {p.code} — rendu indisponible, fallback source Mermaid"))
            finally:
                shutil.rmtree(work_dir, ignore_errors=True)
            self.stdout.write(f"Rendu terminé : {ok} OK, {ko} en fallback texte")
        elif renderer == 'none':
            self.stdout.write("Rendu graphique désactivé (--renderer none).")
            for p in processes:
                p.workflow_png_b64 = None

        html = render_to_string('cartography/process_pdf.html', {
            'processes': processes,
            'count': len(processes),
            'title': opts['title'],
            'generation_date': datetime.now().strftime('%d/%m/%Y'),
        })

        out_path = opts['out']
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        self.stdout.write(f"Génération du PDF → {out_path}")
        HTML(string=html).write_pdf(out_path)

        self.stdout.write(self.style.SUCCESS(f"\n✓ PDF généré : {out_path}"))
