"""
Middleware de journalisation et sécurité — loi 18-07 art. 2.
"""
import re


# Routes sensibles dont on trace la consultation (GET)
SENSITIVE_VIEW_PATTERNS = [
    (re.compile(r'^/questionnaires/\d+/?$'), 'VIEW_QUESTIONNAIRE', 'questionnaire'),
    (re.compile(r'^/form/\d+/?$'), 'VIEW_QUESTIONNAIRE', 'questionnaire'),
    (re.compile(r'^/systems/\d+/?$'), 'VIEW_SYSTEM', 'system'),
    (re.compile(r'^/flows/\d+/?$'), 'VIEW_FLOW', 'flow'),
    (re.compile(r'^/question/(\d+)/attachment/?$'), 'DOWNLOAD_ATTACHMENT', 'question'),
    (re.compile(r'^/kpi/export-md/?$'), 'EXPORT', 'kpi'),
    (re.compile(r'^/reports/ai/pdf/?$'), 'EXPORT', 'report'),
    (re.compile(r'^/admin/'), 'ADMIN_ACTION', 'admin'),
]


def _get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _get_actor(request):
    if request.user.is_authenticated:
        return request.user.username
    actor = request.session.get('auditor_name') or request.session.get('key_user_name')
    if actor:
        return actor
    token = request.GET.get('token', '')
    if token:
        return f"token:{token[:8]}..."
    return ''


class AuditLogMiddleware:
    """
    Trace les consultations et actions sensibles dans le modèle AuditLog.
    Silencieux en cas d'erreur (ne doit jamais casser la réponse).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._log(request, response)
        except Exception:
            pass
        return response

    def _log(self, request, response):
        # On trace uniquement succès 2xx et 3xx (4xx/5xx via autre mécanisme si besoin)
        if response.status_code >= 500:
            return

        path = request.path

        # Skip static/media/healthcheck pour éviter le bruit
        if any(path.startswith(p) for p in ('/static/', '/media/', '/favicon', '/robots')):
            return

        action = None
        target_type = ''
        target_id = ''

        for pattern, act, ttype in SENSITIVE_VIEW_PATTERNS:
            match = pattern.match(path)
            if match:
                action = act
                target_type = ttype
                if match.groups():
                    target_id = match.group(1)
                else:
                    # Extract trailing int from path if present
                    trail = re.search(r'/(\d+)/?$', path)
                    if trail:
                        target_id = trail.group(1)
                break

        # Actions POST sensibles
        if not action and request.method == 'POST':
            if path.startswith('/form/'):
                action = 'SUBMIT_ANSWER'
                target_type = 'questionnaire'
                trail = re.search(r'/form/(\d+)/', path)
                if trail:
                    target_id = trail.group(1)
            elif path == '/rights-request/':
                action = 'RIGHTS_REQUEST'

        if not action:
            return

        from .models import AuditLog
        AuditLog.objects.create(
            action=action,
            actor=_get_actor(request),
            ip_address=_get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            target_type=target_type,
            target_id=str(target_id)[:50],
            path=path[:500],
            success=(response.status_code < 400),
            details={
                'method': request.method,
                'status': response.status_code,
            },
        )


class SecurityHeadersMiddleware:
    """
    Ajoute les en-têtes HTTP de sécurité recommandés (défense en profondeur).
    Complète les settings Django (SECURE_*).
    """
    CSP = (
        "default-src 'self'; "
        "img-src 'self' data: blob: https:; "
        "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdn.jsdelivr.net https://unpkg.com https://fonts.googleapis.com; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://cdn.jsdelivr.net https://unpkg.com; "
        "font-src 'self' data: https://fonts.gstatic.com https://cdn.jsdelivr.net; "
        "connect-src 'self' https://cdn.jsdelivr.net; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault('X-Content-Type-Options', 'nosniff')
        response.setdefault('X-Frame-Options', 'DENY')
        response.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        response.setdefault('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
        response.setdefault('Content-Security-Policy', self.CSP)
        return response
