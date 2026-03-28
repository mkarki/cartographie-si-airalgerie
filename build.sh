#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
mkdir -p staticfiles
python manage.py collectstatic --no-input
python manage.py migrate

# Load initial data if database is empty (first deploy on PostgreSQL)
python manage.py shell -c "
from cartography.models import System
if System.objects.count() == 0:
    print('Database is empty — loading initial data from fixture...')
    import django.core.management
    django.core.management.call_command('loaddata', 'initial_data', verbosity=1)
    print('Initial data loaded successfully.')
else:
    print(f'Database already has {System.objects.count()} systems — skipping fixture load.')
"

mkdir -p media/question_attachments
