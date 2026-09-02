#!/usr/bin/env bash
# ECSACONM Events — deploy script.
#
# Mirrors the manual process documented in TEAM.md §6/§7 (no Docker in
# production — plain systemd service + Nginx serving a static Vue build).
# Transfers over plain `ssh`/`tar` (part of core OpenSSH) with an `rsync`
# fast path when it's installed — no extra tooling required either way.
#
# Usage:
#   deploy.sh api  [--dry-run] [--allow-dirty]   sync api/ to the server, restart the ecsaconm service
#   deploy.sh web  [--dry-run] [--allow-dirty]   build web_vue/, sync dist/ to the server
#   deploy.sh migrate                            run `alembic upgrade head` on the server
#   deploy.sh status                             show systemd status + last 30 log lines
#   deploy.sh logs                                follow live API logs
#
# --dry-run      show what would be sent, without touching the server
# --allow-dirty  skip the local "uncommitted changes" guard (off by default — see below)
#
# The API and the frontend build are NOT deployed via `git pull` on the server —
# the server's git checkout is a reference copy only; deploys sync the built
# artifacts directly, same as TEAM.md always has. That means: commit and push
# your changes first (so the server's git history stays truthful), THEN deploy.
set -euo pipefail

KEY="${ECSACONM_DEPLOY_KEY:-$HOME/Downloads/keys/voting_ecsaconm/voting.pem}"
HOST="${ECSACONM_DEPLOY_HOST:-ubuntu@ec2-54-242-206-111.compute-1.amazonaws.com}"
REMOTE_ROOT="/var/www/ecsaconm_events"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

DRY_RUN=0
ALLOW_DIRTY=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --allow-dirty) ALLOW_DIRTY=1 ;;
  esac
done

if [ ! -f "$KEY" ]; then
  echo "Deploy key not found at $KEY" >&2
  echo "Set ECSACONM_DEPLOY_KEY to override, or check the key was downloaded." >&2
  exit 1
fi
chmod 600 "$KEY" 2>/dev/null || true

SSH_OPTS=(-i "$KEY" -o IdentitiesOnly=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new)
ssh_cmd() { ssh "${SSH_OPTS[@]}" "$HOST" "$@"; }

# Guard against shipping uncommitted local work by accident. Deploys read
# straight from the working tree, so a forgotten WIP edit would otherwise go
# straight to production. --allow-dirty opts out (e.g. for a genuine
# emergency hotfix — see deployment.md for why that should still get
# committed/pushed as soon as possible afterwards).
check_clean() {
  local subdir="$1"
  if [ "$ALLOW_DIRTY" = "1" ]; then return; fi
  if [ -n "$(cd "$REPO_ROOT" && git status --porcelain -- "$subdir")" ]; then
    echo "error: uncommitted changes under $subdir — commit and push first, or pass --allow-dirty." >&2
    (cd "$REPO_ROOT" && git status --short -- "$subdir") >&2
    exit 1
  fi
}

# Sync a local directory to a remote one. Prefers rsync (delta transfer,
# --delete support, real remote diff for --dry-run) when it's installed;
# otherwise falls back to a plain tar-over-ssh copy, which needs nothing
# beyond OpenSSH but always ships the full tree and can't preview a remote
# diff — --dry-run there just lists what's in the local tree.
sync_dir() {
  local local_dir="$1" remote_dir="$2" delete_extra="$3"; shift 3
  local excludes=("$@")

  if command -v rsync >/dev/null 2>&1; then
    local rsync_excludes=()
    for e in "${excludes[@]}"; do rsync_excludes+=(--exclude "$e"); done
    local flags=(-az -v --itemize-changes)
    [ "$DRY_RUN" = "1" ] && flags+=(-n)
    [ "$delete_extra" = "1" ] && flags+=(--delete)
    rsync "${flags[@]}" "${rsync_excludes[@]}" \
      -e "ssh ${SSH_OPTS[*]}" \
      "$local_dir/" "$HOST:$remote_dir/"
    return
  fi

  echo "(rsync not found locally — falling back to tar-over-ssh; full-tree copy, no delta/--delete)"
  local tar_excludes=()
  for e in "${excludes[@]}"; do tar_excludes+=(--exclude "$e"); done

  if [ "$DRY_RUN" = "1" ]; then
    echo "==> [dry-run] Files that would be sent from $local_dir:"
    tar -C "$local_dir" "${tar_excludes[@]}" -cf - . | tar -tf -
    return
  fi

  tar -C "$local_dir" "${tar_excludes[@]}" -czf - . \
    | ssh "${SSH_OPTS[@]}" "$HOST" "mkdir -p '$remote_dir' && tar -xzf - -C '$remote_dir'"
}

deploy_api() {
  check_clean api
  echo "==> ${DRY_RUN:+[dry-run] }Syncing api/ to $HOST:$REMOTE_ROOT/api/ ..."
  sync_dir "$REPO_ROOT/api" "$REMOTE_ROOT/api" 0 \
    venv .env uploads __pycache__ '*.pyc'

  if [ "$DRY_RUN" = "1" ]; then
    echo "==> Dry run only — service was not restarted."
    return
  fi

  echo "==> Restarting ecsaconm service..."
  ssh_cmd "sudo systemctl restart ecsaconm && sudo systemctl is-active ecsaconm"
  echo "==> Recent logs:"
  ssh_cmd "sudo journalctl -u ecsaconm -n 20 --no-pager"

  echo
  echo "Reminder: if api/models/models.py changed, run '$0 migrate' too — it is NOT"
  echo "automatic. (2026-09-02 outage: a model column shipped without it. See deployment.md.)"
}

deploy_web() {
  check_clean web_vue/src
  echo "==> Building web_vue..."
  (cd "$REPO_ROOT/web_vue" && npm run build)

  echo "==> ${DRY_RUN:+[dry-run] }Syncing web_vue/dist/ to $HOST:$REMOTE_ROOT/web_vue/dist/ ..."
  sync_dir "$REPO_ROOT/web_vue/dist" "$REMOTE_ROOT/web_vue/dist" 1

  if [ "$DRY_RUN" = "1" ]; then
    echo "==> Dry run only — nothing was uploaded."
  else
    echo "==> Done. No service restart needed — Nginx serves the static files directly."
  fi
}

migrate() {
  echo "==> Running 'alembic upgrade head' on the server..."
  ssh_cmd "cd $REMOTE_ROOT/api && source venv/bin/activate && alembic upgrade head"
}

status() {
  ssh_cmd "sudo systemctl status ecsaconm --no-pager | tail -8 && echo --- && sudo journalctl -u ecsaconm -n 30 --no-pager"
}

logs() {
  ssh_cmd "sudo journalctl -u ecsaconm -f"
}

cmd="${1:-}"
shift || true
case "$cmd" in
  api) deploy_api ;;
  web) deploy_web ;;
  migrate) migrate ;;
  status) status ;;
  logs) logs ;;
  *)
    echo "Usage: $0 {api|web|migrate|status|logs} [--dry-run] [--allow-dirty]" >&2
    exit 1
    ;;
esac
