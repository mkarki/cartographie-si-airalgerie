"""
Rate limiting simple pour les endpoints d'authentification.
Utilise le cache Django pour compter les tentatives par IP.
"""
from django.conf import settings
from django.core.cache import cache


def _get_ip(request):
    # Derrière Cloudflare : CF-Connecting-IP = vraie IP utilisateur (non spoofable)
    cf_ip = request.META.get('HTTP_CF_CONNECTING_IP')
    if cf_ip:
        return cf_ip.strip()
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def check_rate_limit(request, scope='login'):
    """
    Retourne True si la tentative est autorisée, False si limite atteinte.
    """
    max_attempts = getattr(settings, 'RATELIMIT_LOGIN_ATTEMPTS', 5)
    window = getattr(settings, 'RATELIMIT_LOGIN_WINDOW', 300)
    ip = _get_ip(request)
    key = f"ratelimit:{scope}:{ip}"
    current = cache.get(key, 0)
    if current >= max_attempts:
        return False
    cache.set(key, current + 1, window)
    return True


def reset_rate_limit(request, scope='login'):
    """Appelé après une action légitime pour remettre à zéro le compteur."""
    ip = _get_ip(request)
    cache.delete(f"ratelimit:{scope}:{ip}")
