#!/usr/bin/env bash
set -o errexit

echo "=== BUILD START ==="
pip install -r requirements.txt

echo "=== COLLECTSTATIC ==="
mkdir -p staticfiles
python manage.py collectstatic --no-input
mkdir -p media/question_attachments

echo "=== BUILD COMPLETE (DB ops deferred to runtime) ==="
