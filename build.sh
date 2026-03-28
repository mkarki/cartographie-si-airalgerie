#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
mkdir -p staticfiles
python manage.py collectstatic --no-input
python manage.py migrate

# Load initial data if database is empty (first deploy on PostgreSQL)
python manage.py loaddata initial_data 2>/dev/null || echo "Fixture already loaded or skipped"

# Create superuser if not exists
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@airalgerie.dz', 'AirAlgerie2026!')
    print('Superuser admin created.')
else:
    print('Superuser admin already exists.')
"

mkdir -p media/question_attachments
