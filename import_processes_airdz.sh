#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# import_processes_airdz.sh
#
# Pipeline complet d'import des canevas process Air Algérie remplis par les key users
# vers la base locale (db.sqlite3).
# Note : le dossier source physique reste nommé 'process AIRDZ/' (legacy).
#
#   1. Active le venv si présent
#   2. Extrait les .xlsx du dossier `process AIRDZ/` -> process_airdz_extracted.json
#   3. Importe le JSON en base via la commande Django `import_process_airdz`
#
# Options :
#   --dry-run   N'écrit rien en base (affiche ce qui serait fait)
#   --reset     Supprime les Process existants (code commençant par PROC-AA-)
#               avant import
#   --skip-extract   Ne re-génère pas le JSON (réutilise celui déjà présent)
#
# Exemple :
#   ./import_processes_airdz.sh
#   ./import_processes_airdz.sh --dry-run
#   ./import_processes_airdz.sh --reset
# ---------------------------------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# --- Couleurs ---
if [[ -t 1 ]]; then
    BOLD=$'\e[1m'; GREEN=$'\e[32m'; YELLOW=$'\e[33m'; RED=$'\e[31m'; RESET=$'\e[0m'
else
    BOLD=''; GREEN=''; YELLOW=''; RED=''; RESET=''
fi

log()  { echo "${BOLD}${GREEN}==>${RESET} $*"; }
warn() { echo "${BOLD}${YELLOW}!! ${RESET} $*"; }
err()  { echo "${BOLD}${RED}xx ${RESET} $*" >&2; }

# --- Parse args ---
DRY_RUN=0
RESET=0
SKIP_EXTRACT=0
EXTRA_ARGS=()
for arg in "$@"; do
    case "$arg" in
        --dry-run)      DRY_RUN=1 ;;
        --reset)        RESET=1 ;;
        --skip-extract) SKIP_EXTRACT=1 ;;
        -h|--help)
            sed -n '2,21p' "${BASH_SOURCE[0]}"
            exit 0
            ;;
        *)              EXTRA_ARGS+=("$arg") ;;
    esac
done

# --- Active le venv si présent ---
if [[ -f "venv/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source venv/bin/activate
    log "venv activé : $(python -V)"
else
    warn "pas de venv détecté — utilisation du Python système ($(python3 -V 2>/dev/null || echo 'absent'))"
fi

PYTHON="${PYTHON:-python}"
command -v "$PYTHON" >/dev/null 2>&1 || PYTHON="python3"

# --- Vérifs préalables ---
SOURCE_DIR="/Users/mohamedamine/Air Algérie/process AIRDZ"
if [[ ! -d "$SOURCE_DIR" ]]; then
    err "dossier source introuvable : $SOURCE_DIR"
    exit 1
fi

if ! "$PYTHON" -c "import openpyxl" 2>/dev/null; then
    warn "openpyxl manquant — installation..."
    "$PYTHON" -m pip install --quiet openpyxl
fi

JSON_FILE="$SCRIPT_DIR/process_airdz_extracted.json"

# --- Étape 1 : Extraction Excel -> JSON ---
if [[ $SKIP_EXTRACT -eq 1 ]]; then
    if [[ ! -f "$JSON_FILE" ]]; then
        err "--skip-extract demandé mais $JSON_FILE absent"
        exit 1
    fi
    warn "extraction sautée — réutilisation de $JSON_FILE"
else
    log "étape 1/2 — extraction des canevas Excel"
    "$PYTHON" extract_processes_airdz.py
    if [[ ! -s "$JSON_FILE" ]]; then
        err "extraction échouée — $JSON_FILE vide ou absent"
        exit 1
    fi
fi

# --- Étape 2 : Import Django ---
log "étape 2/2 — import en base locale"

CMD=("$PYTHON" manage.py import_process_airdz)
[[ $DRY_RUN -eq 1 ]] && CMD+=(--dry-run)
[[ $RESET   -eq 1 ]] && CMD+=(--reset)
[[ ${#EXTRA_ARGS[@]} -gt 0 ]] && CMD+=("${EXTRA_ARGS[@]}")

"${CMD[@]}"

# --- Résumé ---
if [[ $DRY_RUN -eq 1 ]]; then
    warn "DRY-RUN : aucune écriture effectuée en base"
else
    COUNT=$("$PYTHON" manage.py shell -c "from cartography.models import Process; print(Process.objects.filter(code__startswith='PROC-AA-').count())" 2>/dev/null | tail -1)
    log "process Air Algérie en base : $COUNT"
fi

log "terminé."
