#!/usr/bin/env bash
# Обновление уже клонированного /opt/virus-contact с пересборкой контейнеров.
set -euo pipefail

APP="${APP_DIR:-/opt/virus-contact}"
BRANCH="${DEPLOY_BRANCH:-drakedoge}"

cd "$APP"
[[ -d .git ]] || { echo "нет .git — сначала scripts/vps-git-bootstrap.sh" >&2; exit 1; }

GIT_TERMINAL_PROMPT=0 git fetch origin "$BRANCH"
git checkout "$BRANCH"
git reset --hard "origin/$BRANCH"
git rev-parse HEAD > .deploy-revision

docker compose build --pull
docker compose up -d --remove-orphans
