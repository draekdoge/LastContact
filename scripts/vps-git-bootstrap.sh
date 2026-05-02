#!/usr/bin/env bash
# Одноразово: заменить дерево /opt/virus-contact на git clone ветки drakedoge.
# Требуется SSH-доступ к репо на GitHub с ключом из ~/.ssh/config (Host github.com-lastcontact).
# Перед запуском добавь публичный ключ сервера как Deploy key (read-only) в репозиторий на GitHub.
set -euo pipefail

APP="${APP_DIR:-/opt/virus-contact}"
ORIGIN="${ORIGIN_SSH:-git@github.com-lastcontact:ephemeral172/contact.git}"
BRANCH="${DEPLOY_BRANCH:-drakedoge}"

tmp_env="$(mktemp)"
chmod 600 "$tmp_env"
cp -a "$APP/.env" "$tmp_env"

docker compose -f "$APP/docker-compose.yml" down

backup="${APP}.bak-$(date +%Y%m%d%H%M%S)"
mv "$APP" "$backup"

GIT_TERMINAL_PROMPT=0 git clone -b "$BRANCH" --single-branch "$ORIGIN" "$APP"
cp -a "$tmp_env" "$APP/.env"
chmod 600 "$APP/.env"
rm -f "$tmp_env"

cd "$APP"
git rev-parse HEAD > .deploy-revision
docker compose build --pull
docker compose up -d --remove-orphans
