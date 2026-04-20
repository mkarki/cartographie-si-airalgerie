#!/usr/bin/env python3
"""
Convertit tous les .docx du dossier mails_acces/ en PDF via Microsoft Word.
"""

import os
import glob
from docx2pdf import convert

MAILS_DIR = os.path.join(os.path.dirname(__file__), "mails_acces")


def main():
    docx_files = sorted(glob.glob(os.path.join(MAILS_DIR, "*.docx")))

    if not docx_files:
        print("Aucun fichier .docx trouvé dans mails_acces/")
        return

    print(f"Conversion de {len(docx_files)} fichiers .docx → .pdf\n")

    for i, docx_path in enumerate(docx_files, 1):
        name = os.path.basename(docx_path)
        pdf_path = docx_path.replace(".docx", ".pdf")

        if os.path.exists(pdf_path):
            print(f"[{i}/{len(docx_files)}] {name} — déjà converti, skip.")
            continue

        print(f"[{i}/{len(docx_files)}] {name}...")
        try:
            convert(docx_path, pdf_path)
            print(f"  ✓ {os.path.basename(pdf_path)}")
        except Exception as e:
            print(f"  ✗ Erreur: {e}")

    print(f"\nTerminé ! Fichiers PDF dans : {MAILS_DIR}")


if __name__ == "__main__":
    main()
