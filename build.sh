#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
mkdir -p staticfiles media/question_attachments
python manage.py collectstatic --no-input || true
