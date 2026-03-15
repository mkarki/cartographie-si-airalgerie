"""
Management command to apply DSI feedback from M. Abdellah YOUCEF-ACHIRA (Feb 2026).

Updates based on observations:
1. SITATEX ONLINE: client messagerie cloud, visualisation messages Type B uniquement
2. SAGE Stock: en cours d'implémentation, pas encore opérationnel
3. Dashboards CCO + Suivi Irrégularités: modules ERP, utilisation limitée, données déjà dans AIMS
4. Qlik Sense: obsolète (pas de licences), en remplacement par Power BI, priorité revue à la baisse
5. Power BI: version Report Server (On-Premise), pas Services (SaaS)
6. Zimbra: client messagerie SMTP standard, aucun interfaçage avec SITATEX ou autres systèmes
7. Portail AH: portail publication notes et informations internes uniquement
"""
from django.core.management.base import BaseCommand
from cartography.models import System


class Command(BaseCommand):
    help = "Applique les retours DSI (M. Youcef-Achira, Fév 2026) sur les systèmes"

    def handle(self, *args, **options):
        updates = 0

        # 1. SITATEX ONLINE
        try:
            sys = System.objects.get(code='SITATEX')
            sys.description = (
                "Client de messagerie en cloud dédié à la visualisation des messages de type B. "
                "La génération et l'envoi de ces messages est assuré au niveau des autres systèmes "
                "opérationnels (Altéa, AIMS, etc.). SITATEX Online ne fait que la consultation."
            )
            sys.mode = 'SAAS'
            sys.save()
            self.stdout.write(self.style.SUCCESS(f"[OK] SITATEX ONLINE mis à jour"))
            updates += 1
        except System.DoesNotExist:
            self.stdout.write(self.style.WARNING("[SKIP] SITATEX non trouvé"))

        # 2. SAGE Stock — en cours d'implémentation
        try:
            sys = System.objects.get(code='SAGE-STOCK')
            sys.description = (
                "Système Gestion Stock. "
                "⚠️ En cours d'implémentation — pas encore opérationnel (retour DSI Fév 2026)."
            )
            sys.criticality = 'BASSE'
            sys.save()
            self.stdout.write(self.style.SUCCESS(f"[OK] SAGE Stock mis à jour (non opérationnel)"))
            updates += 1
        except System.DoesNotExist:
            self.stdout.write(self.style.WARNING("[SKIP] SAGE-STOCK non trouvé"))

        # 3. Dashboards CCO + Suivi Irrégularités — modules ERP, usage limité
        #    Systèmes concernés : DASH-PONCT-H, DASH-PONCT-J, SUIVI-IRREG
        note_dsi = (
            " ⚠️ Module développé au sein de l'ERP. Utilisation limitée, "
            "les données étant déjà disponibles dans AIMS (retour DSI Fév 2026)."
        )
        for code in ['DASH-PONCT-H', 'DASH-PONCT-J', 'SUIVI-IRREG']:
            try:
                sys = System.objects.get(code=code)
                if 'retour DSI' not in sys.description:
                    sys.description += note_dsi
                sys.criticality = 'BASSE'
                sys.save()
                self.stdout.write(self.style.SUCCESS(f"[OK] {code} mis à jour (module ERP, usage limité)"))
                updates += 1
            except System.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"[SKIP] {code} non trouvé"))

        # 4. Qlik Sense — obsolète, pas de licences, remplacement par Power BI
        try:
            sys = System.objects.get(code='QLIK')
            sys.description = (
                "Outil BI avec licences. "
                "⚠️ OBSOLÈTE : absence de licences utilisateurs. "
                "En cours de remplacement par Power BI (retour DSI Fév 2026). "
                "Priorité revue à la baisse."
            )
            sys.criticality = 'BASSE'
            sys.save()
            self.stdout.write(self.style.SUCCESS(f"[OK] Qlik Sense mis à jour (obsolète)"))
            updates += 1
        except System.DoesNotExist:
            self.stdout.write(self.style.WARNING("[SKIP] QLIK non trouvé"))

        # 5. Power BI — Report Server (On-Premise), pas Services (SaaS)
        try:
            sys = System.objects.get(code='POWERBI')
            sys.mode = 'ONPREMISE'
            sys.description = (
                "Outil BI Microsoft — version Power BI Report Server (On-Premise). "
                "Note DSI (Fév 2026) : la version déployée est Report Server, "
                "et non Power BI Services (cloud)."
            )
            sys.save()
            self.stdout.write(self.style.SUCCESS(f"[OK] Power BI mis à jour (Report Server / On-Premise)"))
            updates += 1
        except System.DoesNotExist:
            self.stdout.write(self.style.WARNING("[SKIP] POWERBI non trouvé"))

        # 6. Zimbra — messagerie SMTP standard, aucun interfaçage
        try:
            sys = System.objects.get(code='ZIMBRA')
            sys.description = (
                "Client de messagerie standard SMTP. "
                "Aucune vocation d'interfaçage avec d'autres systèmes, "
                "notamment SITATEX (retour DSI Fév 2026)."
            )
            sys.save()
            self.stdout.write(self.style.SUCCESS(f"[OK] Zimbra mis à jour (SMTP standard, pas d'interfaçage)"))
            updates += 1
        except System.DoesNotExist:
            self.stdout.write(self.style.WARNING("[SKIP] ZIMBRA non trouvé"))

        # 7. Portail AH — publication notes internes uniquement
        try:
            sys = System.objects.get(code='PORTAIL')
            sys.description = (
                "Portail pour la publication de notes et informations internes. "
                "Pas de vocation applicative ou d'interfaçage avec d'autres systèmes "
                "(retour DSI Fév 2026)."
            )
            sys.save()
            self.stdout.write(self.style.SUCCESS(f"[OK] Portail AH mis à jour (publication interne uniquement)"))
            updates += 1
        except System.DoesNotExist:
            self.stdout.write(self.style.WARNING("[SKIP] PORTAIL non trouvé"))

        self.stdout.write(self.style.SUCCESS(f"\n✅ {updates} systèmes mis à jour avec les retours DSI."))
