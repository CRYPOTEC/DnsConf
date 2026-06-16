#!/usr/bin/env bash
# One-shot setup for a fresh Linux server.
# Installs deps, writes .env from environment variables, installs the systemd
# service, and starts it. Run it once; the agent then runs 24/7.
#
# Usage (after extracting the archive to /opt):
#   ANTHROPIC_API_KEY=... TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=... \
#     bash /opt/polybot/deploy/bootstrap.sh
set -euo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"   # this script lives in polybot/deploy/
TARGET="/opt/polybot"

if [ "$HERE" != "$TARGET" ]; then
  echo ">> copying $HERE -> $TARGET"
  mkdir -p "$TARGET"
  cp -r "$HERE/." "$TARGET/"
fi
cd "$TARGET"

echo ">> installing python3 + pip"
if command -v apt-get >/dev/null 2>&1; then
  apt-get update -y && apt-get install -y python3 python3-pip
fi

echo ">> installing python deps (anthropic, websockets)"
pip3 install --quiet anthropic websockets \
  || pip3 install --quiet --break-system-packages anthropic websockets

if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  echo ">> writing .env"
  {
    echo "ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}"
    echo "TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-}"
    echo "TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID:-}"
    [ -n "${NEWSAPI_KEY:-}" ] && echo "NEWSAPI_KEY=${NEWSAPI_KEY}"
    [ -n "${TWITTER_BEARER_TOKEN:-}" ] && echo "TWITTER_BEARER_TOKEN=${TWITTER_BEARER_TOKEN}"
  } > .env
  chmod 600 .env
elif [ ! -f .env ]; then
  cp deploy/.env.example .env
  echo "!! .env создан из шаблона — впиши ключи в $TARGET/.env, затем перезапусти"
fi

echo ">> installing + starting systemd service"
cp deploy/polybot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now polybot

echo ">> DONE. Статус:"
systemctl --no-pager --full status polybot | head -n 6 || true
echo ">> Логи: journalctl -u polybot -f"
