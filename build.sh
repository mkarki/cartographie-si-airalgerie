#!/usr/bin/env bash
set -o errexit

echo "=== BUILD START ==="
pip install -r requirements.txt

echo "=== COLLECTSTATIC ==="
mkdir -p staticfiles
python manage.py collectstatic --no-input

echo "=== DATABASE INFO ==="
python -c "
import dj_database_url, os
url = os.environ.get('DATABASE_URL', 'NOT SET')
print(f'DATABASE_URL set: {bool(url and url != \"NOT SET\")}')
if url and url != 'NOT SET':
    print(f'URL prefix: {url[:30]}...')
    conf = dj_database_url.config()
    print(f'Engine: {conf.get(\"ENGINE\")}')
    print(f'Name: {conf.get(\"NAME\")}')
    print(f'Host: {conf.get(\"HOST\")}')
"

echo "=== MIGRATE ==="
python manage.py migrate --verbosity 2

echo "=== SHOWMIGRATIONS ==="
python manage.py showmigrations cartography

echo "=== LOAD FIXTURE ==="
python manage.py loaddata initial_data --verbosity 2 || echo "WARNING: Fixture load failed (may already exist)"

echo "=== CREATE SUPERUSER ==="
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@airalgerie.dz', 'AirAlgerie2026!')
    print('Superuser admin created.')
else:
    print('Superuser admin already exists.')
"

echo "=== DATA CHECK ==="
python manage.py shell -c "
from cartography.models import System, Questionnaire, Question, KeyUserAccess
print(f'Systems: {System.objects.count()}')
print(f'Questionnaires: {Questionnaire.objects.count()}')
print(f'Questions: {Question.objects.count()}')
print(f'KeyUserAccess: {KeyUserAccess.objects.count()}')
"

mkdir -p media/question_attachments
echo "=== BUILD COMPLETE ==="
