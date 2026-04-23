#!/usr/bin/env bash
# =============================================================================
# Cartographie SI - Render entrypoint
#
# Handles optional SSH tunnel to a VPS PostgreSQL (used when the VPS provider
# blocks direct ingress on 5432/6432), then Django migrations, then gunicorn.
#
# Tunnel is enabled if SSH_TUNNEL_HOST env var is set. When the VPS provider
# finally opens the DB ports, simply unset SSH_TUNNEL_HOST on Render and point
# DATABASE_URL straight at the VPS - no code change required.
#
# Required env vars when SSH_TUNNEL_HOST is set:
#   SSH_TUNNEL_HOST           FQDN of VPS (e.g. cartsiairdz.alphaaerosystem.com)
#   SSH_TUNNEL_PRIVATE_KEY    OpenSSH private key (base64 or raw PEM)
#   SSH_TUNNEL_HOST_KEY       known_hosts line for the VPS (anti-MITM)
# Optional:
#   SSH_TUNNEL_USER           SSH user (default: pgtunnel)
#   SSH_TUNNEL_LOCAL_PORT     local bind port (default: 5433)
#   SSH_TUNNEL_REMOTE_PORT    remote port on VPS (default: 6432 / PgBouncer)
#   GUNICORN_WORKERS          default: 2
# =============================================================================

set -euo pipefail

log() { printf '[start.sh %(%Y-%m-%dT%H:%M:%S)T] %s\n' -1 "$*" >&2; }

cleanup() {
  if [[ -n "${TUNNEL_SUP_PID:-}" ]]; then
    log "stopping tunnel supervisor (pid=${TUNNEL_SUP_PID})"
    kill -TERM "${TUNNEL_SUP_PID}" 2>/dev/null || true
  fi
}
trap cleanup EXIT

# -----------------------------------------------------------------------------
# Optional SSH tunnel
# -----------------------------------------------------------------------------
if [[ -n "${SSH_TUNNEL_HOST:-}" ]]; then
  : "${SSH_TUNNEL_USER:=pgtunnel}"
  : "${SSH_TUNNEL_LOCAL_PORT:=5433}"
  : "${SSH_TUNNEL_REMOTE_PORT:=6432}"

  log "SSH tunnel enabled  host=${SSH_TUNNEL_HOST}  user=${SSH_TUNNEL_USER}  local=127.0.0.1:${SSH_TUNNEL_LOCAL_PORT}  remote=127.0.0.1:${SSH_TUNNEL_REMOTE_PORT}"

  if [[ -z "${SSH_TUNNEL_PRIVATE_KEY:-}" ]]; then
    log "FATAL  SSH_TUNNEL_PRIVATE_KEY env var is required when SSH_TUNNEL_HOST is set"
    exit 1
  fi
  if [[ -z "${SSH_TUNNEL_HOST_KEY:-}" ]]; then
    log "FATAL  SSH_TUNNEL_HOST_KEY env var is required when SSH_TUNNEL_HOST is set"
    exit 1
  fi
  if ! command -v ssh >/dev/null 2>&1; then
    log "FATAL  'ssh' binary not found in PATH"
    exit 1
  fi

  # Materialize SSH material in $HOME/.ssh (ephemeral, never persisted)
  mkdir -p "${HOME}/.ssh"
  chmod 700 "${HOME}/.ssh"

  # Accept the private key either as base64 (safer for single-line env var)
  # or as raw PEM with literal newlines
  if [[ "${SSH_TUNNEL_PRIVATE_KEY}" != *"BEGIN "* ]]; then
    printf '%s' "${SSH_TUNNEL_PRIVATE_KEY}" | base64 -d > "${HOME}/.ssh/id_tunnel" 2>/dev/null \
      || { log "FATAL  could not base64-decode SSH_TUNNEL_PRIVATE_KEY"; exit 1; }
  else
    printf '%s\n' "${SSH_TUNNEL_PRIVATE_KEY}" > "${HOME}/.ssh/id_tunnel"
  fi
  chmod 600 "${HOME}/.ssh/id_tunnel"

  # Host key pinning (no TOFU)
  printf '%s\n' "${SSH_TUNNEL_HOST_KEY}" > "${HOME}/.ssh/known_hosts_tunnel"
  chmod 600 "${HOME}/.ssh/known_hosts_tunnel"

  log "ssh material ready  ($(stat -c '%a %n' "${HOME}/.ssh/id_tunnel" 2>/dev/null || stat -f '%Mp %N' "${HOME}/.ssh/id_tunnel"))"

  # Supervisor loop: keep tunnel alive with capped exponential backoff
  (
    backoff=3
    attempt=0
    while true; do
      attempt=$((attempt + 1))
      log "[tunnel] attempt #${attempt} connecting to ${SSH_TUNNEL_USER}@${SSH_TUNNEL_HOST}:22"
      set +e
      /usr/bin/ssh -N -T \
        -o ServerAliveInterval=20 \
        -o ServerAliveCountMax=3 \
        -o ExitOnForwardFailure=yes \
        -o StrictHostKeyChecking=yes \
        -o UserKnownHostsFile="${HOME}/.ssh/known_hosts_tunnel" \
        -o IdentitiesOnly=yes \
        -o ConnectTimeout=10 \
        -i "${HOME}/.ssh/id_tunnel" \
        -L "127.0.0.1:${SSH_TUNNEL_LOCAL_PORT}:127.0.0.1:${SSH_TUNNEL_REMOTE_PORT}" \
        "${SSH_TUNNEL_USER}@${SSH_TUNNEL_HOST}"
      rc=$?
      set -e
      log "[tunnel] ssh exited (rc=${rc}), sleeping ${backoff}s before reconnect"
      sleep "${backoff}"
      # cap backoff at 60s
      if [[ $backoff -lt 30 ]]; then
        backoff=$((backoff * 2))
      else
        backoff=60
      fi
    done
  ) &
  TUNNEL_SUP_PID=$!
  log "tunnel supervisor pid=${TUNNEL_SUP_PID}"

  # Wait for local tunnel port (up to 45s)
  log "waiting for 127.0.0.1:${SSH_TUNNEL_LOCAL_PORT} ..."
  for i in $(seq 1 45); do
    if python -c "import socket,sys; s=socket.create_connection(('127.0.0.1',${SSH_TUNNEL_LOCAL_PORT}),2); s.close(); sys.exit(0)" 2>/dev/null; then
      log "tunnel UP after ${i}s"
      break
    fi
    sleep 1
    if [[ $i -eq 45 ]]; then
      log "FATAL  tunnel never came up on 127.0.0.1:${SSH_TUNNEL_LOCAL_PORT} after 45s"
      exit 1
    fi
  done
else
  log "no SSH tunnel configured (SSH_TUNNEL_HOST empty)  -  DATABASE_URL used directly"
fi

# -----------------------------------------------------------------------------
# Django migrations + cache table
# -----------------------------------------------------------------------------
log "running Django migrations"
python manage.py migrate --noinput

log "ensuring cache table exists"
python manage.py createcachetable

# -----------------------------------------------------------------------------
# Launch gunicorn (foreground, exec so signals propagate)
# -----------------------------------------------------------------------------
: "${PORT:=8000}"
: "${GUNICORN_WORKERS:=2}"
log "launching gunicorn on 0.0.0.0:${PORT}  workers=${GUNICORN_WORKERS}"
exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT}" \
  --timeout 120 \
  --workers "${GUNICORN_WORKERS}" \
  --access-logfile - \
  --error-logfile -
