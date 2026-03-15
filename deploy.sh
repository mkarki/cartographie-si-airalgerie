#!/bin/bash

# =============================================================================
# Script de déploiement - Cartographie SI Air Algérie
# =============================================================================
# Usage: ./deploy.sh
# Ce script doit être exécuté depuis votre machine locale
# =============================================================================

set -e

# Configuration
SERVER_IP="85.31.237.249"
SERVER_USER="root"
REMOTE_PATH="/var/www/cartographie_si"
APP_PORT="8000"  # Port 3000 occupé, on utilise 8000
LOCAL_PATH="$(dirname "$(readlink -f "$0")")"

echo "=============================================="
echo "  Déploiement Cartographie SI Air Algérie"
echo "=============================================="
echo ""

# Vérification de la connexion SSH
echo "[1/7] Test de connexion SSH..."
ssh -o ConnectTimeout=10 ${SERVER_USER}@${SERVER_IP} "echo 'Connexion OK'" || {
    echo "❌ Impossible de se connecter au serveur. Vérifiez vos identifiants SSH."
    exit 1
}

# Création du répertoire distant
echo "[2/7] Création du répertoire distant..."
ssh ${SERVER_USER}@${SERVER_IP} "mkdir -p ${REMOTE_PATH}"

# Synchronisation des fichiers (sans venv et fichiers inutiles)
echo "[3/7] Synchronisation des fichiers avec rsync..."
rsync -avz --progress \
    --exclude 'venv/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '.DS_Store' \
    --exclude 'deploy.sh' \
    --exclude '.git/' \
    "${LOCAL_PATH}/" ${SERVER_USER}@${SERVER_IP}:${REMOTE_PATH}/

echo "[4/7] Installation des dépendances sur le serveur..."
ssh ${SERVER_USER}@${SERVER_IP} << 'REMOTE_SCRIPT'
set -e

# Installation de Python et pip si nécessaire
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx

# Création de l'environnement virtuel
cd /var/www/cartographie_si
python3 -m venv venv
source venv/bin/activate

# Installation des dépendances
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Collecte des fichiers statiques
python manage.py collectstatic --noinput 2>/dev/null || true

echo "✅ Dépendances installées"
REMOTE_SCRIPT

echo "[5/7] Configuration du service systemd..."
ssh ${SERVER_USER}@${SERVER_IP} << 'REMOTE_SCRIPT'
cat > /etc/systemd/system/cartographie_si.service << 'EOF'
[Unit]
Description=Cartographie SI Air Algérie - Django Application
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/var/www/cartographie_si
Environment="PATH=/var/www/cartographie_si/venv/bin"
ExecStart=/var/www/cartographie_si/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 config.wsgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable cartographie_si
systemctl restart cartographie_si

echo "✅ Service systemd configuré et démarré"
REMOTE_SCRIPT

echo "[6/7] Configuration de Nginx (reverse proxy 80 -> 8000)..."
ssh ${SERVER_USER}@${SERVER_IP} << 'REMOTE_SCRIPT'
cat > /etc/nginx/sites-available/cartographie_si << 'EOF'
server {
    listen 80;
    server_name _;

    location /static/ {
        alias /var/www/cartographie_si/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
    }
}
EOF

# Activer le site et désactiver le default
ln -sf /etc/nginx/sites-available/cartographie_si /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test et redémarrage de Nginx
nginx -t && systemctl restart nginx

echo "✅ Nginx configuré"
REMOTE_SCRIPT

echo "[7/7] Vérification finale..."
ssh ${SERVER_USER}@${SERVER_IP} << 'REMOTE_SCRIPT'
echo ""
echo "=== Status des services ==="
systemctl status cartographie_si --no-pager | head -5
systemctl status nginx --no-pager | head -5
echo ""
echo "=== Test de l'application ==="
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://127.0.0.1:8000/ || echo "⚠️  L'application met peut-être du temps à démarrer"
REMOTE_SCRIPT

echo ""
echo "=============================================="
echo "  ✅ Déploiement terminé avec succès!"
echo "=============================================="
echo ""
echo "  🌐 Accès: http://${SERVER_IP}/"
echo ""
echo "  Commandes utiles sur le serveur:"
echo "    - Logs: journalctl -u cartographie_si -f"
echo "    - Restart: systemctl restart cartographie_si"
echo "    - Status: systemctl status cartographie_si"
echo ""
