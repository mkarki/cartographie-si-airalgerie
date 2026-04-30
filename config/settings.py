"""
Django settings for Air Algérie SI Cartography project.
"""

import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-airalgerie-cartographie-si-2026')

DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
# Domaines additionnels (Cloudflare + sous-domaine airalgerie.dz).
# Configurable via env var EXTRA_ALLOWED_HOSTS="host1.airalgerie.dz,host2.airalgerie.dz"
EXTRA_ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get('EXTRA_ALLOWED_HOSTS', 'cartographie-si.airalgerie.dz').split(',')
    if h.strip()
]
ALLOWED_HOSTS = ['*']
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
ALLOWED_HOSTS.extend(EXTRA_ALLOWED_HOSTS)

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8888',
    'http://localhost:8888',
    'http://85.31.237.249',
    'https://*.onrender.com',
    'https://*.airalgerie.dz',
]
# Derrière Cloudflare : header X-Forwarded-Proto pour détecter HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Récupérer la vraie IP client derrière Cloudflare (middleware audit log)
USE_X_FORWARDED_HOST = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cartography',
]

if os.environ.get('CLOUDINARY_CLOUD_NAME'):
    INSTALLED_APPS.insert(-1, 'cloudinary_storage')
    INSTALLED_APPS.insert(-1, 'cloudinary')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'cartography.middleware.SecurityHeadersMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
]
if not DEBUG:
    MIDDLEWARE.append('django.middleware.csrf.CsrfViewMiddleware')
MIDDLEWARE += [
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cartography.middleware.AuditLogMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
    )
}
# SSL obligatoire si la DB est externe (PostgreSQL distant)
# Surchargable via env var PGSSLMODE si besoin
if DATABASES['default'].get('ENGINE', '').endswith('postgresql'):
    DATABASES['default'].setdefault('OPTIONS', {})
    DATABASES['default']['OPTIONS']['sslmode'] = os.environ.get('PGSSLMODE', 'require')

    # Si le serveur utilise une PKI interne, le CA est fourni via env var DB_CA_CERT.
    # On l'écrit sur disque et on force sslmode=verify-full pour valider la chaîne.
    _db_ca = os.environ.get('DB_CA_CERT', '').strip()
    if _db_ca:
        _ca_path = Path('/tmp/db-ca.crt')
        if not _ca_path.exists() or _ca_path.read_text() != _db_ca:
            _ca_path.write_text(_db_ca)
            _ca_path.chmod(0o600)
        DATABASES['default']['OPTIONS']['sslrootcert'] = str(_ca_path)
        # verify-full valide le CN/SAN du cert contre l'hôte de DATABASE_URL.
        # On prend verify-ca (moins strict) par défaut pour tolérer le switch IP/FQDN.
        DATABASES['default']['OPTIONS']['sslmode'] = os.environ.get('PGSSLMODE', 'verify-ca')

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Algiers'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Cloudinary — persistent media storage for Render
# Set these env vars on Render: CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
if os.environ.get('CLOUDINARY_CLOUD_NAME'):
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.environ['CLOUDINARY_CLOUD_NAME'],
        'API_KEY': os.environ['CLOUDINARY_API_KEY'],
        'API_SECRET': os.environ['CLOUDINARY_API_SECRET'],
    }
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.RawMediaCloudinaryStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── Sécurité (loi 18-07 art. 2 — mesures techniques) ────────────────────
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    # SECURE_PROXY_SSL_HEADER déjà défini plus haut (support Cloudflare)
    SECURE_HSTS_SECONDS = 31536000  # 1 an
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = False  # CSRF token lu par JS côté formulaire
CSRF_COOKIE_SAMESITE = 'Lax'
X_FRAME_OPTIONS = 'DENY'

# Session expirée après 2 h d'inactivité
SESSION_COOKIE_AGE = 60 * 60 * 2
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# ─── Rétention / conformité ───────────────────────────────────────────────
# Nombre de jours avant purge automatique via management command cleanup_expired_data
RETENTION_AUDIT_DAYS = int(os.environ.get('RETENTION_AUDIT_DAYS', 365))  # journal d'audit : 12 mois
RETENTION_RIGHTS_REQUESTS_DAYS = int(os.environ.get('RETENTION_RIGHTS_REQUESTS_DAYS', 1095))  # 3 ans (contentieux)

# ─── Rate limiting (simple, via cache) ────────────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cartography_cache',
    }
}
RATELIMIT_LOGIN_ATTEMPTS = 5  # 5 tentatives
RATELIMIT_LOGIN_WINDOW = 300  # par 5 min

# ─── Contact DPO (affiché dans /privacy/) ─────────────────────────────────
# Délégué à la protection des données désigné (loi 18-07 art. 30)
DPO_CONTACT_NAME = os.environ.get('DPO_CONTACT_NAME', 'M. SEKKAL Mohamed Djawed')
DPO_CONTACT_EMAIL = os.environ.get('DPO_CONTACT_EMAIL', 'sekkal.djawed@airalgerie.dz')
