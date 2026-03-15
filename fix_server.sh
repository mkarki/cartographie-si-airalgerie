#!/bin/bash

# =============================================================================
# Script de correction des erreurs serveur - Cartographie SI Air Algérie
# =============================================================================
# Usage: Copiez ce script sur le serveur et exécutez-le
# ssh root@85.31.237.249 'bash -s' < fix_server.sh
# =============================================================================

set -e

echo "=============================================="
echo "  Correction des erreurs - Cartographie SI"
echo "=============================================="

cd /var/www/cartographie_si

echo "[1/4] Activation de l'environnement virtuel..."
source venv/bin/activate

echo "[2/4] Installation des dépendances manquantes..."
pip install markdown pandas anthropic openpyxl gunicorn

echo "[3/4] Redémarrage du service..."
systemctl restart cartographie_si

echo "[4/4] Vérification..."
sleep 2
systemctl status cartographie_si --no-pager | head -10

echo ""
echo "=============================================="
echo "  ✅ Correction terminée!"
echo "=============================================="
echo ""
echo "Test: curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://127.0.0.1:8000/ || echo "⚠️ L'app démarre..."
echo ""
echo "Logs: journalctl -u cartographie_si -f"
