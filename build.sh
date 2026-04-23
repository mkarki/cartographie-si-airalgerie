#!/usr/bin/env bash
set -o errexit

# Assertion : ssh binary required by start.sh when SSH_TUNNEL_HOST is set.
# Render's Python runtime ships openssh-client by default ; fail loudly at
# build time if that ever changes.
if ! command -v ssh >/dev/null 2>&1; then
  echo "FATAL : 'ssh' binary not found in PATH." >&2
  echo "start.sh needs openssh-client to open the tunnel to the VPS PostgreSQL." >&2
  exit 1
fi
echo "[build] ssh : $(command -v ssh) ($(ssh -V 2>&1))"

pip install -r requirements.txt
mkdir -p staticfiles media/question_attachments
python manage.py collectstatic --no-input || true
