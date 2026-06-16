#!/usr/bin/env bash
# Minimal 24/7 runner for hosts without systemd/docker (uses nohup).
#   ./deploy/run.sh           # foreground
#   nohup ./deploy/run.sh > polybot.log 2>&1 &   # background
set -euo pipefail
cd "$(dirname "$0")/.."           # -> polybot/ directory
if [ -f .env ]; then
  set -a; . ./.env; set +a        # load secrets from .env
fi
exec python3 -m polybot --config config.politics.json run --loop
