"""
Genere MAILS_PROCESS_PAR_KEY_USER.md : 1 mail par key user unique.

Source : EMAILS_KEY_USERS.md
Sortie : MAILS_PROCESS_PAR_KEY_USER.md
"""
import os
import re
from collections import OrderedDict

BASE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(BASE, 'EMAILS_KEY_USERS.md')
OUT = os.path.join(BASE, 'MAILS_PROCESS_PAR_KEY_USER.md')

RESPONSABLE = ('M. Ali KARKI', 'karki.ali@airalgerie.dz')

# Responsables de division (depuis la table cartography_divisionaccess).
DIVISION_RESPONSABLES = {
    'DC':    ('BOUTEMADJA Samy',     'boutemadja.samy@airalgerie.dz'),
    'DFC':   ('KHELFI Redouane',     'khelfi.redouane@airalgerie.dz'),
    'DIVEX': ('BENBOUAZIZ Lyes',     'benbouaziz.lyes@airalgerie.dz'),
    'DOA':   ('BENBOUAZIZ Lyes',     'benbouaziz.lyes@airalgerie.dz'),
    'DOS':   ('BENBOUAZIZ Lyes',     'benbouaziz.lyes@airalgerie.dz'),
    'DMRA':  ('HACHELAF Mourad',     'hachelaf.mourad@airalgerie.dz'),
    'DRH':   ('KRAIMECHE Abdelkrim', 'kraimeche.abdelkrim@airalgerie.dz'),
    'DSI':   ('MERDACI Adel',        'merdaci.adel@airalgerie.dz'),
    # DAGP, DSC, RGF : pas d'email enregistre
}


def parse_source():
    """Renvoie un OrderedDict { email : {'name', 'directions': set, 'systems': list } }"""
    with open(SOURCE, 'r', encoding='utf-8') as f:
        text = f.read()

    users = OrderedDict()
    current_dir = None
    current_sys = None

    for line in text.split('\n'):
        # On stoppe avant le recapitulatif final
        if line.startswith('## Récapitulatif'):
            break

        m_dir = re.match(r'^##\s+([A-Z]{2,5})\s+—', line)
        if m_dir:
            current_dir = m_dir.group(1)
            current_sys = None
            continue

        m_sys = re.match(r'^###\s+(.+?)\s*$', line)
        if m_sys:
            # Nettoyer les annotations en italique entre parentheses
            current_sys = re.sub(r'\s*\*\(.*?\)\*\s*$', '', m_sys.group(1)).strip()
            continue

        # Ligne de tableau key user
        m_row = re.match(r'^\|\s*(Key User[^|]*?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$', line)
        if m_row and current_dir and current_sys:
            name = m_row.group(2).strip()
            email = m_row.group(3).strip()
            if email in ('—', '-', '') or 'Non désigné' in name:
                continue
            if email not in users:
                users[email] = {
                    'name': name,
                    'directions': OrderedDict(),  # garder l'ordre
                    'systems': [],
                }
            users[email]['directions'][current_dir] = True
            if current_sys not in users[email]['systems']:
                users[email]['systems'].append(current_sys)
    return users


def build_mail_body(direction_label: str) -> str:
    return (
        "Bonjour,\n"
        "\n"
        "Dans le cadre de la cartographie du SI, nous consolidons pour chaque direction "
        "la liste des process métier afin de la renseigner dans l'outil et de l'intégrer au mapping système.\n"
        "\n"
        f"En tant que key user référent pour la direction **{direction_label}**, nous vous sollicitons "
        "pour nous transmettre la liste de vos process métier.\n"
        "\n"
        "Pour faciliter la collecte, vous trouverez ci-joint un canevas Excel prêt à remplir "
        "(`CANEVAS_PROCESS_KEY_USERS.xlsx`). Il suffit de :\n"
        "\n"
        "1. Indiquer votre nom et votre direction en en-tête\n"
        "2. Lister vos process, une ligne par process, avec :\n"
        "   - **Nom du process**\n"
        "   - **Description** (1-2 phrases suffisent)\n"
        "   - **Systèmes utilisés** (ex. AIMS, AMOS, Excel…)\n"
        "   - **Outputs / KPI produits**\n"
        "\n"
        "**Exemple de process :**\n"
        "\n"
        "> AIMS Va fournir à Amos les heures de vols effectué, les cycles effectué et les programmes des vols.\n"
        ">\n"
        "> AMOS va fournir à AIMS les prévision d'imobilisation de maintenance des avions.\n"
        "> on fournit d'abord les prévisions d'immobilisations pour pouvoir avoir les programmes de vol\n"
        "\n"
        "Inutile de rédiger en détail : nous reviendrons vers vous si un process nécessite un approfondissement.\n"
        "\n"
        "Merci de nous retourner le canevas rempli **d'ici le 11/05/2026** par retour de mail.\n"
        "\n"
        "Bien cordialement,\n"
        "\n"
        "**Mohamedamine KARKI**\n"
        "Équipe projet Cartographie SI — Air Algérie"
    )


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def build(users):
    out = []
    out.append('# Mails par key user — Recueil des process métier')
    out.append('')
    out.append(f'> **{len(users)} mails** — un par key user unique. M. Ali KARKI '
               'et le(s) responsable(s) de division systématiquement en Cc.')
    out.append('')
    out.append('**Pièce jointe** : `CANEVAS_PROCESS_KEY_USERS.xlsx`')
    out.append('')
    out.append('---')
    out.append('')
    out.append('## Sommaire')
    out.append('')
    for i, (email, info) in enumerate(users.items(), 1):
        dirs = '/'.join(info['directions'].keys())
        out.append(f"{i}. [{info['name']} ({dirs})](#{slug(info['name'] + '-' + email)})")
    out.append('')
    out.append('---')
    out.append('')

    for i, (email, info) in enumerate(users.items(), 1):
        anchor = slug(info['name'] + '-' + email)
        dirs = list(info['directions'].keys())
        dirs_label = ' / '.join(dirs)

        out.append(f'<a id="{anchor}"></a>')
        out.append(f"## {i}. {info['name']} — {dirs_label}")
        out.append('')

        # TO
        out.append(f"**À :** {info['name']} <{email}>")
        out.append('')

        # Cc : responsables de division + M. Ali KARKI
        cc = []
        cc_seen = {email}
        for d in dirs:
            resp = DIVISION_RESPONSABLES.get(d)
            if resp and resp[1] not in cc_seen:
                cc.append(resp)
                cc_seen.add(resp[1])
        if RESPONSABLE[1] not in cc_seen:
            cc.append(RESPONSABLE)
        out.append('**Cc :** ' + '; '.join(f'{n} <{em}>' for n, em in cc))
        out.append('')

        # Objet
        out.append(f"**Objet :** Cartographie SI — {dirs_label} — Recueil de vos process métier")
        out.append('')

        # Systemes couverts (info au-dessus du corps, pas dans le mail final)
        out.append(f"_Systèmes couverts : {', '.join(info['systems'])}_")
        out.append('')

        out.append('---')
        out.append('')
        out.append(build_mail_body(dirs_label))
        out.append('')
        out.append('---')
        out.append('')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
    print(f'OK  {OUT}')
    print(f'    {len(users)} mails generes (1 par key user)')


def main():
    users = parse_source()
    build(users)


if __name__ == '__main__':
    main()
