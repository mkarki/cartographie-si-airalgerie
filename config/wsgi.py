import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()

# Auto-migrate + load fixture at startup (for Render PostgreSQL)
def _auto_migrate():
    try:
        from django.core.management import call_command
        from django.db import connection
        # Test if tables exist
        with connection.cursor() as cursor:
            try:
                cursor.execute("SELECT COUNT(*) FROM django_migrations")
                count = cursor.fetchone()[0]
                if count > 0:
                    return  # Already migrated
            except Exception:
                pass  # Table doesn't exist, need to migrate
        
        print("[STARTUP] Running migrations...")
        call_command('migrate', verbosity=1)
        
        print("[STARTUP] Loading fixture...")
        try:
            call_command('loaddata', 'initial_data', verbosity=1)
        except Exception as e:
            print(f"[STARTUP] Fixture load skipped: {e}")
        
        print("[STARTUP] Creating superuser...")
        from django.contrib.auth.models import User
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@airalgerie.dz', 'AirAlgerie2026!')
            print("[STARTUP] Superuser created.")
        
        print("[STARTUP] Database ready!")
    except Exception as e:
        print(f"[STARTUP] Auto-migrate error: {e}")

_auto_migrate()
