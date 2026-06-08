"""Gestion des accès « Division/Direction » (token de connexion par lien).

Permet de diagnostiquer et de provisionner rapidement les accès des directeurs
(type ``DivisionAccess``) sans passer par l'admin — utile en prod (shell Render).

Exemples :
    # Vérifier l'accès d'un ou plusieurs responsables (recherche par nom)
    python manage.py division_access --check KHELFI HABEL

    # Lister tous les accès division et leur lien
    python manage.py division_access --list

    # Créer (ou réutiliser) l'accès d'un directeur pour une structure
    python manage.py division_access --issue --code DAGP \
        --name "HABEL Rachid" --email habel.rachid@airalgerie.dz

    # Réactiver un accès désactivé
    python manage.py division_access --activate HABEL

Le lien généré est de la forme :  <BASE_URL>/access/?token=<token>
BASE_URL = settings.PUBLIC_BASE_URL si défini, sinon l'URL Render par défaut.
"""
from django.conf import settings
from django.core.management.base import BaseCommand

from cartography.models import DivisionAccess, Structure

DEFAULT_BASE_URL = "https://cartographie-si-airalgerie.onrender.com"


class Command(BaseCommand):
    help = "Vérifie / crée / réactive les accès Division (lien à token) des directeurs"

    def add_arguments(self, parser):
        parser.add_argument('--check', nargs='+', metavar='NOM',
                            help='Cherche des accès par nom (insensible à la casse)')
        parser.add_argument('--list', action='store_true',
                            help='Liste tous les accès division')
        parser.add_argument('--issue', action='store_true',
                            help='Crée (ou réutilise) un accès — requiert --code et --name')
        parser.add_argument('--activate', nargs='+', metavar='NOM',
                            help='Réactive les accès correspondant au(x) nom(s)')
        parser.add_argument('--code', help='Code structure (ex: DAGP, DFC)')
        parser.add_argument('--name', help='Nom du responsable')
        parser.add_argument('--email', default='', help='Email du responsable')
        parser.add_argument('--base-url', default=None, help='URL publique de base')

    # ------------------------------------------------------------------
    def _base_url(self, options):
        return (options.get('base_url')
                or getattr(settings, 'PUBLIC_BASE_URL', None)
                or DEFAULT_BASE_URL).rstrip('/')

    def _link(self, base_url, token):
        return f"{base_url}/access/?token={token}"

    def _print_access(self, access, base_url):
        flag = self.style.SUCCESS('actif') if access.is_active else self.style.ERROR('INACTIF')
        last = access.last_accessed.strftime('%Y-%m-%d %H:%M') if access.last_accessed else 'jamais'
        self.stdout.write(
            f"  • {access.name} [{access.structure.code}] — {flag} — "
            f"dernier accès : {last}"
        )
        self.stdout.write(f"    email : {access.email or '(non renseigné)'}")
        self.stdout.write(f"    lien  : {self._link(base_url, access.token)}")

    # ------------------------------------------------------------------
    def handle(self, *args, **options):
        base_url = self._base_url(options)

        if options.get('list'):
            qs = DivisionAccess.objects.select_related('structure').all()
            self.stdout.write(self.style.MIGRATE_HEADING(
                f"{qs.count()} accès division :"))
            for a in qs:
                self._print_access(a, base_url)
            return

        if options.get('check'):
            for needle in options['check']:
                matches = DivisionAccess.objects.select_related('structure').filter(
                    name__icontains=needle)
                self.stdout.write(self.style.MIGRATE_HEADING(
                    f"Recherche « {needle} » : {matches.count()} résultat(s)"))
                if not matches:
                    self.stdout.write(self.style.WARNING(
                        "    Aucun accès — à créer avec --issue."))
                for a in matches:
                    self._print_access(a, base_url)
            return

        if options.get('activate'):
            for needle in options['activate']:
                matches = DivisionAccess.objects.filter(name__icontains=needle)
                n = matches.update(is_active=True)
                self.stdout.write(self.style.SUCCESS(
                    f"✅ {n} accès réactivé(s) pour « {needle} »"))
            return

        if options.get('issue'):
            code = options.get('code')
            name = options.get('name')
            if not code or not name:
                self.stderr.write(self.style.ERROR(
                    "--issue requiert --code et --name"))
                return
            try:
                struct = Structure.objects.get(code=code)
            except Structure.DoesNotExist:
                self.stderr.write(self.style.ERROR(
                    f"Structure introuvable pour le code « {code} »"))
                return
            access, created = DivisionAccess.objects.get_or_create(
                structure=struct, name=name,
                defaults={'email': options.get('email', ''), 'is_active': True},
            )
            if not created:
                # réutilise l'accès existant ; complète l'email + réactive si besoin
                changed = False
                if options.get('email') and not access.email:
                    access.email = options['email']
                    changed = True
                if not access.is_active:
                    access.is_active = True
                    changed = True
                if changed:
                    access.save()
            verb = "créé" if created else "déjà existant (réutilisé)"
            self.stdout.write(self.style.SUCCESS(f"✅ Accès {verb} :"))
            self._print_access(access, base_url)
            return

        self.stdout.write(self.help)
        self.stdout.write("Utilisez --check / --list / --issue / --activate.")
