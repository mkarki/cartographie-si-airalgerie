"""Remplacement AIRDZ → Air Algérie dans les fichiers narratifs (.md, .csv, .json, .txt).

Règles appliquées (dans cet ordre) :
1. `cartsiairdz...` (FQDN technique) — PROTÉGÉ par token, restauré en fin.
2. `PROC-AIRDZ-` → `PROC-AA-`
3. `AIRDZ` → `Air Algérie`
4. `AirDZ` → `Air Algérie`
5. `\bairdz\b` (minuscule en mot isolé) → `Air Algérie`

Exclusions (pas de modification) :
- /Users/mohamedamine/Air Algérie/CONFORMITE/...
- /Users/mohamedamine/Air Algérie/MIGRATION_VPS_ALGERIE/...
- Dossiers `_backup_*`, `.venv`, `node_modules`, `.git`
- Tous les fichiers .py / .sh / .html / .yaml / .yml (gérés manuellement)
- PDFs (non modifiables ici, à régénérer)
- Le fichier source `process_airdz_extracted.json` à la racine du repo (donnée d'import,
  on le régénère en passant via une étape spécifique).

Usage : python scripts/airdz_replace_text.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path("/Users/mohamedamine/Air Algérie")
DRY_RUN = "--dry-run" in sys.argv

EXCLUDE_DIRS = {
    "CONFORMITE",
    "MIGRATION_VPS_ALGERIE",
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
}
EXCLUDE_DIR_PREFIXES = ("_backup_", ".secrets", "backup_")
EXCLUDE_EXT = {".py", ".sh", ".html", ".yaml", ".yml", ".pdf", ".pdfa", ".xlsx",
               ".xls", ".png", ".jpg", ".jpeg", ".db", ".sqlite3", ".pyc", ".bak"}
INCLUDE_EXT = {".md", ".csv", ".json", ".txt"}

PROTECT_TOKEN = "\x00CARTSIAIRDZ_PROTECTED\x00"

REPLACEMENTS = [
    (re.compile(r"PROC-AIRDZ-"), "PROC-AA-"),
    (re.compile(r"AIRDZ"), "Air Algérie"),
    (re.compile(r"AirDZ"), "Air Algérie"),
    (re.compile(r"\bairdz\b"), "Air Algérie"),
]

stats = {"scanned": 0, "modified": 0, "errors": 0, "skipped": 0}
modified_files = []


def should_skip_dir(path: Path) -> bool:
    name = path.name
    if name in EXCLUDE_DIRS:
        return True
    return any(name.startswith(p) for p in EXCLUDE_DIR_PREFIXES)


def process_file(path: Path) -> bool:
    """Renvoie True si modifié."""
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        stats["skipped"] += 1
        return False

    original = text
    text = text.replace("cartsiairdz", PROTECT_TOKEN)

    for pattern, repl in REPLACEMENTS:
        text = pattern.sub(repl, text)

    text = text.replace(PROTECT_TOKEN, "cartsiairdz")

    if text == original:
        return False

    if not DRY_RUN:
        path.write_text(text, encoding="utf-8")
    return True


def walk(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dpath = Path(dirpath)
        # Filtrage in-place des dirnames pour skipper rapidement
        dirnames[:] = [d for d in dirnames if not should_skip_dir(dpath / d)]
        for fname in filenames:
            fpath = dpath / fname
            ext = fpath.suffix.lower()
            if ext in EXCLUDE_EXT:
                continue
            if ext not in INCLUDE_EXT:
                continue
            stats["scanned"] += 1
            try:
                if process_file(fpath):
                    stats["modified"] += 1
                    modified_files.append(str(fpath.relative_to(ROOT)))
            except Exception as e:
                stats["errors"] += 1
                print(f"  ERREUR {fpath}: {e}")


print("=" * 80)
print(f"Remplacement AIRDZ → Air Algérie dans les fichiers texte  ({'DRY-RUN' if DRY_RUN else 'EXECUTION'})")
print(f"Racine : {ROOT}")
print("=" * 80)

walk(ROOT)

print(f"\nFichiers scannés  : {stats['scanned']}")
print(f"Fichiers modifiés : {stats['modified']}")
print(f"Fichiers ignorés (binaire/erreur) : {stats['skipped']}")
print(f"Erreurs : {stats['errors']}")

if modified_files:
    print(f"\n--- Liste des fichiers modifiés ({len(modified_files)}) ---")
    for f in sorted(modified_files):
        print(f"  {f}")

if DRY_RUN:
    print("\n⚠️  DRY-RUN — aucun fichier n'a été écrit.")
else:
    print("\n✅ Modifications appliquées.")
