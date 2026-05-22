"""
Corrige MAILS_PROCESS_PAR_DIRECTION.md en remplacant les anciens couples
'Nom <email>' par les couples mis a jour depuis 'LISTE_KEY_USERS (1).xlsx'
(rempli par la secretaire).

Strategie : on identifie chaque key user par son ancien email (unique dans
le doc) et on substitue par 'NouveauNom <nouveau_email>'.
Les personnes non presentes dans la liste (ex. M. Ali KARKI) sont conservees
telles quelles.
"""
import os
import re
from openpyxl import load_workbook

BASE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(BASE, 'MAILS_PROCESS_PAR_DIRECTION.md')
XLSX = '/Users/mohamedamine/Air Algérie/LISTE_KEY_USERS (1).xlsx'

# Map : ancien email (lower) -> (nouveau nom, nouveau email)
# Elabore manuellement par appariement nom de famille.
MAP = {
    'akkacha@airalgerie.dz':              ('AKKACHA Mohamed Amine',     'akkacha.amine@airalgerie.dz'),
    'saad@airalgerie.dz':                 ('SAAD Nassima',              'saad.nassima@airalgerie.dz'),
    'bouchik@airalgerie.dz':              ('BOUCHIK Mounir',            'bouchik.mounir@airalgerie.dz'),
    'beldjerdi@airalgerie.dz':            ('BELDJERDI Zakaria',         'beldjerdi.zakaria@airalgerie.dz'),
    'laidani@airalgerie.dz':              ('LAIDANI Zakaria',           'laidani.zakaria@airalgerie.dz'),
    'hassissene@airalgerie.dz':           ('HASSISSENE Chemseddine',    'hassissene.chemseddine@airalgerie.dz'),
    'faidi@airalgerie.dz':                ('FAIDI Fouad',               'faidi.fouad@airalgerie.dz'),
    'halisse@airalgerie.dz':              ('HALISSE Abderrahim',        'halisse.abderrahim@airalgerie.dz'),
    'fodili@airalgerie.dz':               ('FODILI Mohamed Yacine',     'fodili.yacine@airalgerie.dz'),
    'bacha@airalgerie.dz':                ('BACHA Amine',               'bacha.amine@airalgerie.dz'),
    'benmadi@airalgerie.dz':              ('BENMADI Soumia',            'benmadi.soumia@airalgerie.dz'),
    'safarzitoun@airalgerie.dz':          ('SAFARZITOUN Naim',          'safarzitoun.naim@airalgerie.dz'),
    'fiala.zahra@airalgerie.dz':          ('FIALA Zahra',               'fiala.zahra@airalgerie.dz'),
    'lounaouci.nassim@airalgerie.dz':     ('LOUNAOUCI Nassim',          'lounaouci.nassim@airalgerie.dz'),
    'hasbellaoui.imen@airalgerie.dz':     ('HASBELLAOUI Imen',          'hasbellaoui.imen@airalgerie.dz'),
    'gharbi.mohamed@airalgerie.dz':       ('GHARBI Mohamed',            'gharbi.mohamed@airalgerie.dz'),
    'namouni.ali@airalgerie.dz':          ('NAMOUNI Ali',               'namouni.ali@airalgerie.dz'),
    'benyelles.djamaleddine@airalgerie.dz': ('BENYELLES Djamal Eddine', 'benyelles.djamaleddine@airalgerie.dz'),
    'said.sihem@airalgerie.dz':           ('SAID Sihem',                'said.sihem@airalgerie.dz'),
    'beslama.lamya@airalgerie.dz':        ('BENSALEM Lamya',            'bensalem.lamya@airalgerie.dz'),
    'smalah.yasmine@airalgerie.dz':       ('SMAALLAH Yasmine',          'smaallah.yasmine@airalgerie.dz'),
    'azerouzl.salima@airalgerie.dz':      ('AZEROUAL Salima',           'azeroual.salima@airalgerie.dz'),
    'toutou.aghiles@airalgerie.dz':       ('TOUTOU Aghiles',            'toutou.aghiles@airalgerie.dz'),
    'manseur.amine@airalgerie.dz':        ('MANSEUR Amine',             'manseur.amine@airalgerie.dz'),
    'hadji.racim@airalgerie.dz':          ('HADJI Racim',               'hadji.racim@airalgerie.dz'),
    'hassini.samir@airalgerie.dz':        ('HASSINI Samir',             'hassini.samir@airalgerie.dz'),
    'bouras.ferial@airalgerie.dz':        ('BOURAS Ferial',             'bouras.ferial@airalgerie.dz'),
    'chenoufi.sidali@airalgerie.dz':      ('CHENNOUFI Sid Ali',         'chennoufi.sidali@airalgerie.dz'),
    'youcefachira.abdellah@airalgerie.dz': ('YOUCEF ACHIRA Abdellah',   'youcefachira.abdellah@airalgerie.dz'),
    'esseminia.adnan@airalgerie.dz':      ('ESSEMIANI Adnan',           'essemiani.adnan@airalgerie.dz'),
    'salahrouana.med@airalgerie.dz':      ('SALAH ROUANA Mohamed',      'salahrouana.mohamed@airalgerie.dz'),
    'boukaiou.ahlem@airalgerie.dz':       ('BOUTOUT Allaa Eddine',      'boutout.allaaeddine@airalgerie.dz'),
    'agha.riadh@airalgerie.dz':           ('AGHA Riadh',                'agha.riadh@airalgerie.dz'),
    'youbi.mourad@airalgerie.dz':         ('YOUBI Mourad',              'youbi.mourad@airalgerie.dz'),
    'mebarki.medhamza@airalgerie.dz':     ('MEBARKI Med Hamza',         'mebarki.hamza@airalgerie.dz'),
    'sidahmed.akkouche@airalgerie.dz':    ('SIDAHMED AKKOUCHE',         'akkouche.sidahmed@airalgerie.dz'),
    'bennouar.a@airalgerie.dz':           ('BENNOUAR Adnane',           'bennouar.adnane@airalgerie.dz'),
    'badaoui.youcef@airalgerie.dz':       ('BADAOUI Youcef',            'badaoui.youcef@airalgerie.dz'),
    'hassaine.hassen@airalgerie.dz':      ('HASSAINE Hassen',           'hassaine.hassen@airalgerie.dz'),
    'gacimi@airalgerie.dz':               ('GACIMI Mohamed',            'gacimi.mohamed@airalgerie.dz'),
    'bouabdallah.akram@airalgerie.dz':    ('BOUABDALLAH Mohamed Akram', 'bouabdallah.akram@airalgerie.dz'),
    'ladjici.a@airalgerie.dz':            ('LADJICI Fatima',            'ladjici.fatima@airalgerie.dz'),
    'benmouffok.e@airalgerie.dz':         ('BENMOUFFOK El Hadi',        'benmouffok.elhadi@airalgerie.dz'),
    'chabane.a@airalgerie.dz':            ('CHABANE Amel',              'chabane.amel@airalgerie.dz'),
    'mazari.a@airalgerie.dz':             ('MAZARI Assia',              'mazari.assia@airalgerie.dz'),
    'bougueziz@airalgerie.dz':            ('BOUGUEZIZ Samir',           'bougueziz.samir@airalgerie.dz'),
    'ferradji@airalgerie.dz':             ('FERRADJI Farid',            'ferradji.farid@airalgerie.dz'),
    'touahria.faiza@airalgerie.dz':       ('TOUAHRIA Faiza',            'touahria.faiza@airalgerie.dz'),
    'hadjsaid.nadir@airalgerie.dz':       ('HADJ SAID Nadir',           'hadjsaid.nadir@airalgerie.dz'),
    'belkacemi.mohand@airalgerie.dz':     ('BELKACEMI Mohand Said',     'belkacemi.said@airalgerie.dz'),
    'kari@airalgerie.dz':                 ('KARRI Fateh',               'karri.fateh@airalgerie.dz'),
    'benaouicha@airalgerie.dz':           ('BENAOUICHA Hanane',         'benaouicha.hanane@airalgerie.dz'),
    'attout.abedlhafid@airalgerie.dz':    ('ATTOUT Abedlhafid',         'attout.abdelhafid@airalgerie.dz'),
    'aitmeziane.amar@airalgerie.dz':      ('AIT MEZIANE Ahcene',        'aitmeziane.ahcene@airalgerie.dz'),
    'lakama.abdallah@airalgerie.dz':      ('LAKAMA Abdellah',           'lakama.abdellah@airalgerie.dz'),
    'sameur@airalgerie.dz':               ('SAMEUR Yacine',             'sameur.yacine@airalgerie.dz'),
}

# Pattern : '... Name <old_email>' -> on capture le segment 'Name <email>' borne
# par la separation '; ' ou debut ': '. On reecrit Name + new email.

# Regex pour matcher tout segment 'Texte <email>' dans une ligne **À :** ou **Cc :**
SEG_RE = re.compile(r'([^;:\n*]+?)\s*<([^>]+)>')


def transform_line(line: str) -> str:
    if not (line.startswith('**À :**') or line.startswith('**Cc :**')):
        return line

    def repl(m):
        old_name = m.group(1).strip()
        old_email = m.group(2).strip()
        # Conserver les annotations entre parentheses (ex. "(SDR)") en suffixe
        suffix_match = re.search(r'\s*(\([^)]+\))\s*$', old_name)
        suffix = suffix_match.group(1) if suffix_match else ''

        if old_email.lower() in MAP:
            new_name, new_email = MAP[old_email.lower()]
            if suffix:
                new_name = f'{new_name} {suffix}'
            return f'{new_name} <{new_email}>'
        # Pas dans la liste : on conserve tel quel
        return m.group(0)

    # On veut garder la structure '**Cc :** seg1; seg2; seg3'
    # Approche : split sur '; ', appliquer SEG_RE a chaque segment
    prefix_match = re.match(r'^(\*\*(?:À|Cc) :\*\*\s*)(.*)$', line)
    if not prefix_match:
        return line
    prefix, rest = prefix_match.group(1), prefix_match.group(2)

    new_segments = []
    for seg in rest.split(';'):
        seg = seg.strip()
        if not seg:
            continue
        new_seg = SEG_RE.sub(repl, seg)
        new_segments.append(new_seg.strip())
    return prefix + '; '.join(new_segments)


def main():
    with open(MD, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')
    new_lines = [transform_line(l) for l in lines]
    with open(MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    print(f'OK  {MD} mis a jour')


if __name__ == '__main__':
    main()
