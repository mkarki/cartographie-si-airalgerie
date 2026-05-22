"""
Genere un fichier MAILS_PROCESS_PAR_DIRECTION.md contenant un mail par
direction/division, avec la liste des key users concernes en destinataires.

Source : EMAILS_FONCTIONNELS_KEY_USERS.md (sections '### N. SYSTEME — DIRECTION')
Sortie : MAILS_PROCESS_PAR_DIRECTION.md
"""
import os
import re
from collections import OrderedDict, defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(BASE, 'EMAILS_FONCTIONNELS_KEY_USERS.md')
OUT = os.path.join(BASE, 'MAILS_PROCESS_PAR_DIRECTION.md')

# Pattern pour extraire une entree de personne : "Nom Prenom — email@domain"
PERSON_RE = re.compile(r'([^—,]+?)\s*—\s*([\w._%+-]+@[\w.-]+\.[a-zA-Z]{2,})')


def primary_direction(label: str) -> str:
    """Normalise un libelle de direction en sa direction primaire.

    Exemples :
        'DC + DIVEX'                  -> 'DC'
        'DIVEX (CCO)'                 -> 'DIVEX (CCO)'
        'DSI + DC + DIVEX + DMRA'     -> 'DSI'
        'DPD + DOS'                   -> 'DPD'
    """
    label = label.strip().rstrip(' *_')
    # Retirer les annotations entre parentheses si elles sont a la fin
    label = re.sub(r'\s*\*\([^)]*\)\*\s*$', '', label).strip()
    # Garder la 1re composante avant " + "
    if ' + ' in label:
        label = label.split(' + ')[0].strip()
    return label


def parse_source():
    """Parcourt le markdown source et renvoie une liste d'entrees :
       [{system, direction, to: [(name, email)], cc: [(name, email)]}, ...]
    """
    with open(SOURCE, 'r', encoding='utf-8') as f:
        text = f.read()

    # Ne garder que la zone avant la ligne 'À :** Direction des Systèmes' (qui est un mail global, hors perimetre)
    cutoff_idx = text.find('### 28. E-LEARNING E-EXAM PN')
    # On garde 28 et 29 dans le perimetre meme si pas de KU designe
    body = text

    entries = []
    current = None

    for line in body.split('\n'):
        m_section = re.match(r'^###\s+([\d-]+)\.\s+(.+?)\s+—\s+(.+?)\s*$', line)
        if m_section:
            if current and (current['to'] or current['cc']):
                entries.append(current)
            num = m_section.group(1)
            system = m_section.group(2).strip()
            direction_raw = m_section.group(3).strip()
            # Cas 'AIMS — Formation PNC (DOA)' : la direction reelle est dans les parentheses
            m_paren = re.match(r'^(.+?)\s*\(([A-Z]{2,5})\)\s*$', direction_raw)
            if m_paren:
                subsystem = m_paren.group(1).strip()
                real_direction = m_paren.group(2).strip()
                # 'DIVEX (CCO)' reste tel quel : garder la parenthese
                if real_direction in {'DC', 'DOA', 'DSI', 'DIVEX', 'DMRA', 'DOS',
                                       'DFC', 'DAGP', 'DPD', 'DRH', 'DSC', 'RGF'}:
                    system = f'{system} — {subsystem}'
                    direction_raw = real_direction
            current = {
                'num': num,
                'system': system,
                'direction_raw': direction_raw,
                'direction': primary_direction(direction_raw),
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


def build_mails(entries):
    """Groupe les entrees par direction primaire et construit les mails."""
    by_dir = defaultdict(list)
    for e in entries:
        by_dir[e['direction']].append(e)

    # Trie alphabetique des directions, mais en mettant les directions principales en premier
    direction_order = ['DC', 'DOA', 'DSI', 'DIVEX', 'DIVEX (CCO)', 'DMRA', 'DOS',
                       'DFC', 'DAGP', 'DPD', 'DRH', 'DSC', 'RGF']
    sorted_dirs = sorted(by_dir.keys(), key=lambda d: (
        direction_order.index(d) if d in direction_order else 99, d
    ))

    out_lines = []
    out_lines.append('# Mails par direction — Recueil des process métier')
    out_lines.append('')
    out_lines.append('> Un mail par direction. Tous les key users de la direction sont en destinataires (TO + Cc), '
                     "avec M. Ali KARKI en copie sur l'ensemble.")
    out_lines.append('')
    out_lines.append('**Pièce jointe à chaque mail** : `CANEVAS_PROCESS_KEY_USERS.xlsx`')
    out_lines.append('')
    out_lines.append('---')
    out_lines.append('')
    out_lines.append('## Sommaire')
    out_lines.append('')
    for d in sorted_dirs:
        nb_sys = len(by_dir[d])
        unique_emails = set()
        for e in by_dir[d]:
            for n, em in e['to'] + e['cc']:
                unique_emails.add(em)
        out_lines.append(f'- **[{d}](#{slug(d)})** — {nb_sys} système(s), {len(unique_emails)} key user(s)')
    out_lines.append('')
    out_lines.append('---')
    out_lines.append('')

    for d in sorted_dirs:
        out_lines.append(f'<a id="{slug(d)}"></a>')
        out_lines.append(f'## {d}')
        out_lines.append('')

        # Recuperer les key users uniques pour cette direction.
        # Regle : une personne qui apparait en TO pour au moins un systeme est
        # consideree "principale" (TO) pour la direction, meme si elle est Cc
        # sur d'autres systemes.
        seen_emails_to = OrderedDict()
        seen_emails_cc = OrderedDict()
        systems_covered = []
        # Passe 1 : identifier les principaux (TO d'au moins un systeme)
        for e in by_dir[d]:
            systems_covered.append(f"{e['system']} ({e['direction_raw']})")
            for name, email in e['to']:
                seen_emails_to[email] = name
        # Passe 2 : les backups sont ceux qui n'apparaissent QUE en Cc
        for e in by_dir[d]:
            for name, email in e['cc']:
                if email not in seen_emails_to and email not in seen_emails_cc:
                    seen_emails_cc[email] = name

        # Liste systemes
        out_lines.append('**Systèmes couverts :**')
        out_lines.append('')
        for s in systems_covered:
            out_lines.append(f'- {s}')
        out_lines.append('')

        # En-tete mail
        to_line = '; '.join(f'{n} <{em}>' for em, n in seen_emails_to.items())
        cc_line = '; '.join(f'{n} <{em}>' for em, n in seen_emails_cc.items())
        cc_line_full = (cc_line + '; ' if cc_line else '') + 'M. Ali KARKI <karki.ali@airalgerie.dz>'

        out_lines.append('**À :** ' + (to_line or '(à compléter — pas de key user désigné)'))
        out_lines.append('')
        out_lines.append('**Cc :** ' + cc_line_full)
        out_lines.append('')
        out_lines.append(f'**Objet :** Cartographie SI — {d} — Recueil de vos process métier')
        out_lines.append('')

        # Corps du mail
        out_lines.append('---')
        out_lines.append('')
        if len(seen_emails_to) > 1 or seen_emails_cc:
            greeting = 'Bonjour à toutes et à tous,'
        else:
            # Un seul referent
            only_name = next(iter(seen_emails_to.values()), '')
            first_name = only_name.split()[0] if only_name else ''
            greeting = f'Bonjour {first_name},' if first_name else 'Bonjour,'
        out_lines.append(greeting)
        out_lines.append('')
        out_lines.append("Dans le cadre de la cartographie du SI, nous consolidons pour chaque direction la liste "
                         "des process métier afin de la renseigner dans l'outil et de l'intégrer au mapping système.")
        out_lines.append('')
        out_lines.append("En tant que key user(s) référent(s) pour la direction **" + d + "**, nous vous sollicitons "
                         "pour nous transmettre la liste de vos process métier.")
        out_lines.append('')
        out_lines.append("Pour faciliter la collecte, vous trouverez ci-joint un canevas Excel prêt à remplir "
                         "(`CANEVAS_PROCESS_KEY_USERS.xlsx`). Il suffit de :")
        out_lines.append('')
        out_lines.append('1. Indiquer votre nom et votre direction en en-tête')
        out_lines.append('2. Lister vos process, une ligne par process, avec :')
        out_lines.append('   - **Nom du process**')
        out_lines.append('   - **Description** (1-2 phrases suffisent)')
        out_lines.append('   - **Systèmes utilisés** (ex. AIMS, AMOS, Excel…)')
        out_lines.append('   - **Outputs / KPI produits**')
        out_lines.append('')
        out_lines.append("Inutile de rédiger en détail : nous reviendrons vers vous si un process nécessite un approfondissement.")
        out_lines.append('')
        out_lines.append("Merci de nous retourner le canevas rempli **d'ici [JJ/MM]** par retour de mail.")
        out_lines.append('')
        out_lines.append('Bien cordialement,')
        out_lines.append('')
        out_lines.append('**Mohamedamine KARKI**')
        out_lines.append('Équipe projet Cartographie SI — Air Algérie')
        out_lines.append('')
        out_lines.append('---')
        out_lines.append('')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out_lines))

    print(f'OK  {OUT}')
    print(f'    {len(sorted_dirs)} mails generes pour les directions :')
    for d in sorted_dirs:
        nb = len(by_dir[d])
        nb_users = len({em for e in by_dir[d] for _, em in e['to'] + e['cc']})
        print(f'      - {d:<22} {nb} systeme(s), {nb_users} key user(s)')


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def main():
    entries = parse_source()
    print(f'  {len(entries)} entrees parsees depuis EMAILS_FONCTIONNELS_KEY_USERS.md')
    build_mails(entries)


if __name__ == '__main__':
    main()
