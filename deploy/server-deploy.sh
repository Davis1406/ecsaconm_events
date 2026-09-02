#!/usr/bin/env bash
# ECSACONM Events — deploy from ON the server.
#
# Install once: see deploy/README.md. After that, from anywhere on the box:
#
#   ecsaconm-deploy api       git pull, restart the ecsaconm service
#   ecsaconm-deploy web       git pull, npm install (if needed), npm run build
#   ecsaconm-deploy all       both of the above
#   ecsaconm-deploy migrate   alembic upgrade head
#   ecsaconm-deploy status    systemd status + last 30 log lines
#   ecsaconm-deploy logs      follow live API logs
#
# This pulls straight from git — which only works because the server's
# checkout is meant to stay clean. Never edit files under here directly;
# see deployment.md for what happens when that rule gets broken.
set -euo pipefail

REPO_ROOT="/var/www/ecsaconm_events"
cd "$REPO_ROOT"

check_clean() {
  if [ -n "$(git status --porcelain)" ]; then
    echo "error: this checkout has uncommitted changes — that shouldn't happen on the server." >&2
    echo "Reconcile it first (see deployment.md); refusing to pull over local edits." >&2
    git status --short >&2
    exit 1
  fi
}

pull() {
  check_clean
  echo "==> Pulling origin/main..."
  git fetch origin
  git reset --hard origin/main
  git log --oneline -1
}

deploy_api() {
  pull
  echo "==> Restarting ecsaconm service..."
  sudo systemctl restart ecsaconm
  sudo systemctl is-active ecsaconm
  echo "==> Recent logs:"
  sudo journalctl -u ecsaconm -n 20 --no-pager

  echo
  echo "Reminder: if api/models/models.py changed, run 'ecsaconm-deploy migrate' too — it"
  echo "is NOT automatic. (2026-09-02 outage: a model column shipped without it. See deployment.md.)"
}

deploy_web() {
  pull
  echo "==> Building web_vue..."
  cd "$REPO_ROOT/web_vue"
  npm install
  npm run build
  echo "==> Done — Nginx serves web_vue/dist/ directly, no restart needed."
}

migrate() {
  echo "==> Running 'alembic upgrade head'..."
  cd "$REPO_ROOT/api"
  source venv/bin/activate
  alembic upgrade head
}

status() {
  sudo systemctl status ecsaconm --no-pager | tail -8
  echo ---
  sudo journalctl -u ecsaconm -n 30 --no-pager
}

logs() {
  sudo journalctl -u ecsaconm -f
}

cmd="${1:-}"
case "$cmd" in
  api) deploy_api ;;
  web) deploy_web ;;
  all) deploy_api; deploy_web ;;
  migrate) migrate ;;
  status) status ;;
  logs) logs ;;
  *)
    echo "Usage: ecsaconm-deploy {api|web|all|migrate|status|logs}" >&2
    exit 1
    ;;
esac
