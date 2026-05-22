"""
Genere un fichier MAILS_PROCESS_PAR_SYSTEME.md contenant UN mail par systeme,
avec les key users TO/Cc deja extraits depuis EMAILS_FONCTIONNELS_KEY_USERS.md,
M. Ali KARKI systematiquement en Cc, et un exemple de process dans chaque mail.

Source : EMAILS_FONCTIONNELS_KEY_USERS.md (sections '### N. SYSTEME — DIRECTION')
Sortie : MAILS_PROCESS_PAR_SYSTEME.md
"""
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(BASE, 'EMAILS_FONCTIONNELS_KEY_USERS.md')
OUT = os.path.join(BASE, 'MAILS_PROCESS_PAR_SYSTEME.md')

PERSON_RE = re.compile(r'([^—,]+?)\s*—\s*([\w._%+-]+@[\w.-]+\.[a-zA-Z]{2,})')

RESPONSABLE = ('M. Ali KARKI', 'karki.ali@airalgerie.dz')

# Responsables de division/direction (source : table cartography_divisionaccess
# de la cartographie SI). Cles = codes utilises dans EMAILS_FONCTIONNELS_KEY_USERS.md.
DIVISION_RESPONSABLES = {
    'DC':       ('BOUTEMADJA Samy',     'boutemadja.samy@airalgerie.dz'),
    'DVR':      ('BOUNAB Nihad',        'bounab.nihad@airalgerie.dz'),
    'DRM':      ('FAIDI Fouad',         'faidi.fouad@airalgerie.dz'),
    'DFC':      ('KHELFI Redouane',     'khelfi.redouane@airalgerie.dz'),
    'DIVEX':    ('BENBOUAZIZ Lyes',     'benbouaziz.lyes@airalgerie.dz'),
    'DOA':      ('BENBOUAZIZ Lyes',     'benbouaziz.lyes@airalgerie.dz'),
    'DOS':      ('BENBOUAZIZ Lyes',     'benbouaziz.lyes@airalgerie.dz'),  # DOS sous DIVEX
    'CCO':      ('BENBOUAZIZ Lyes',     'benbouaziz.lyes@airalgerie.dz'),  # CCO sous DIVEX
    'DPD':      ('BENBOUAZIZ Lyes',     'benbouaziz.lyes@airalgerie.dz'),  # DPD sous DIVEX
    'DMRA':     ('HACHELAF Mourad',     'hachelaf.mourad@airalgerie.dz'),
    'DRH':      ('KRAIMECHE Abdelkrim', 'kraimeche.abdelkrim@airalgerie.dz'),
    'DSI':      ('MERDACI Adel',        'merdaci.adel@airalgerie.dz'),
    'DAGP':     None,  # Mme la DAG — pas d'email enregistre
    'DSC':      None,  # responsable DG, email non disponible
    'RGF':      None,  # responsable DG, email non disponible
}


def responsables_for(direction_label: str):
    """Retourne la liste de (nom, email) des responsables de division a mettre
    en Cc pour une direction donnee, en gerant les composites 'DC + DIVEX',
    'DIVEX (CCO)', etc."""
    label = direction_label.strip()
    # Extraire les codes : tout ce qui ressemble a un acronyme majuscule
    codes = re.findall(r'\b([A-Z]{2,5})\b', label)
    seen = set()
    out = []
    for c in codes:
        resp = DIVISION_RESPONSABLES.get(c)
        if resp and resp[1] not in seen:
            seen.add(resp[1])
            out.append(resp)
    return out

# Exemple verbatim fourni par M. KARKI (formulation a conserver telle quelle)
EXEMPLE_PROCESS = (
    "**Exemple de process :**\n"
    "\n"
    "> AIMS Va fournir à Amos les heures de vols effectué, les cycles effectué et les programmes des vols.\n"
    ">\n"
    "> AMOS va fournir à AIMS les prévision d'imobilisation de maintenance des avions.\n"
    "> on fournit d'abord les prévisions d'immobilisations pour pouvoir avoir les programmes de vol"
)

# Systemes a exclure de la generation (traites a part)
SKIP_SYSTEMS = {'SUITE ALTÉA AMADEUS'}


def parse_source():
    with open(SOURCE, 'r', encoding='utf-8') as f:
        text = f.read()

    entries = []
    current = None

    for line in text.split('\n'):
        m_section = re.match(r'^###\s+([\d-]+)\.\s+(.+?)\s+—\s+(.+?)\s*$', line)
        if m_section:
            if current and (current['to'] or current['cc']):
                entries.append(current)
            num = m_section.group(1)
            system = m_section.group(2).strip()
            direction_raw = m_section.group(3).strip()
            current = {
                'num': num,
                'system': system,
                'direction': direction_raw,
                'to': [],
                'cc': [],
            }
            continue

        if current is None:
            continue

        m_to = re.match(r'^\*\*[ÀA]\s*:\*\*\s*(.+)$', line)
        m_cc = re.match(r'^\*\*Cc\s*:\*\*\s*(.+)$', line)
        if m_to:
            for name, email in PERSON_RE.findall(m_to.group(1)):
                current['to'].append((name.strip(), email.strip()))
        elif m_cc:
            for name, email in PERSON_RE.findall(m_cc.group(1)):
                current['cc'].append((name.strip(), email.strip()))

    if current and (current['to'] or current['cc']):
        entries.append(current)
    return entries


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def first_name(full_name: str) -> str:
    """Retourne le 1er prenom si present, sinon le 1er token."""
    parts = full_name.replace('M.', '').replace('Mme', '').strip().split()
    return parts[0] if parts else ''


def greeting_for(to_list):
    if not to_list:
        return 'Bonjour,'
    if len(to_list) == 1:
        name = to_list[0][0]
        # Si format 'PRENOM Nom' ou 'M. NOM', on fait simple
        return f'Bonjour {name},'
    return 'Bonjour à toutes et à tous,'


def build_mails(entries):
    entries = [e for e in entries if e['system'].upper() not in SKIP_SYSTEMS]
    out = []
    out.append('# Mails par système — Recueil des process métier')
    out.append('')
    out.append('> Un mail **par système**. Le ou les key users référents sont en TO, '
               "les co-référents en Cc, et **M. Ali KARKI** est systématiquement en copie.")
    out.append('')
    out.append('**Pièce jointe à chaque mail** : `CANEVAS_PROCESS_KEY_USERS.xlsx`')
    out.append('')
    out.append('---')
    out.append('')
    out.append('## Sommaire')
    out.append('')
    for e in entries:
        out.append(f"- [{e['num']}. {e['system']} — {e['direction']}](#{slug(e['num'] + '-' + e['system'])})")
    out.append('')
    out.append('---')
    out.append('')

    for e in entries:
        anchor = slug(e['num'] + '-' + e['system'])
        out.append(f'<a id="{anchor}"></a>')
        out.append(f"## {e['num']}. {e['system']} — {e['direction']}")
        out.append('')

        to_line = '; '.join(f'{n} <{em}>' for n, em in e['to'])
        # Cc = co-referents systeme + responsables de division + M. Ali KARKI
        # (sans doublon avec TO ni entre eux)
        emails_to = {em for _, em in e['to']}
        cc_full = []
        cc_emails = set()

        def _add_cc(person):
            n, em = person
            if em in emails_to or em in cc_emails:
                return
            cc_emails.add(em)
            cc_full.append(person)

        # 1. Co-referents systeme
        for person in e['cc']:
            _add_cc(person)
        # 2. Responsables de division/direction du systeme
        for person in responsables_for(e['direction']):
            _add_cc(person)
        # 3. Responsable projet
        _add_cc(RESPONSABLE)

        cc_line = '; '.join(f'{n} <{em}>' for n, em in cc_full)

        out.append('**À :** ' + (to_line or '(à compléter)'))
        out.append('')
        out.append('**Cc :** ' + cc_line)
        out.append('')
        out.append(f"**Objet :** Cartographie SI — {e['system']} — Recueil de vos process métier")
        out.append('')
        out.append('---')
        out.append('')

        out.append(greeting_for(e['to']))
        out.append('')
        out.append("Dans le cadre de la cartographie du SI, nous consolidons pour chaque système la liste "
                   "des process métier afin de la renseigner dans l'outil et de l'intégrer au mapping système.")
        out.append('')
        out.append(f"En tant que key user(s) référent(s) pour le système **{e['system']}**, nous vous sollicitons "
                   "pour nous transmettre la liste de vos process métier.")
        out.append('')
        out.append(EXEMPLE_PROCESS)
        out.append('')
        out.append("Pour faciliter la collecte, vous trouverez ci-joint un canevas Excel prêt à remplir "
                   "(`CANEVAS_PROCESS_KEY_USERS.xlsx`). Il suffit de :")
        out.append('')
        out.append('1. Indiquer votre nom et votre direction en en-tête')
        out.append('2. Lister vos process, une ligne par process, avec :')
        out.append('   - **Nom du process**')
        out.append('   - **Description** (1-2 phrases suffisent)')
        out.append('   - **Systèmes utilisés** (ex. AIMS, AMOS, Excel…)')
        out.append('   - **Outputs / KPI produits**')
        out.append('')
        out.append("Inutile de rédiger en détail : nous reviendrons vers vous si un process nécessite un approfondissement.")
        out.append('')
        out.append("Merci de nous retourner le canevas rempli **d'ici [JJ/MM]** par retour de mail.")
        out.append('')
        out.append('Bien cordialement,')
        out.append('')
        out.append('**Mohamedamine KARKI**')
        out.append('Équipe projet Cartographie SI — Air Algérie')
        out.append('')
        out.append('---')
        out.append('')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))

    print(f'OK  {OUT}')
    print(f'    {len(entries)} mails generes (1 par systeme)')


def main():
    entries = parse_source()
    print(f'  {len(entries)} entrees parsees depuis EMAILS_FONCTIONNELS_KEY_USERS.md')
    build_mails(entries)


if __name__ == '__main__':
    main()
