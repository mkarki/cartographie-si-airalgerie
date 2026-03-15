# Guide de Déploiement - Cartographie SI Air Algérie

## Prérequis

- Accès SSH au serveur `85.31.237.249`
- `rsync` installé sur votre machine locale

## Déploiement

### Étape 1 : Rendre le script exécutable

```bash
cd "/Users/mohamedamine/Air Algérie/cartographie_si"
chmod +x deploy.sh
```

### Étape 2 : Lancer le déploiement

```bash
./deploy.sh
```

Le script vous demandera le mot de passe SSH à plusieurs reprises (ou utilisez une clé SSH).

## Ce que fait le script

1. **Synchronise tous les fichiers** (y compris `db.sqlite3` avec toutes les données)
2. **Installe Python, pip, venv et Nginx** sur le serveur
3. **Crée un environnement virtuel** et installe Django + Gunicorn
4. **Configure un service systemd** pour que l'app tourne en permanence
5. **Configure Nginx** comme reverse proxy (port 80 → port 8000)

## Accès après déploiement

- **URL** : http://85.31.237.249/

## Commandes utiles sur le serveur

```bash
# Voir les logs en temps réel
journalctl -u cartographie_si -f

# Redémarrer l'application
systemctl restart cartographie_si

# Voir le status
systemctl status cartographie_si

# Redémarrer Nginx
systemctl restart nginx
```

## En cas de mise à jour

Relancez simplement `./deploy.sh` - rsync ne transférera que les fichiers modifiés.

## Configuration

- **Port de l'application** : 8000 (interne)
- **Port public** : 80 (via Nginx)
- **Chemin sur le serveur** : `/var/www/cartographie_si`
