#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/adrian/CoAIch"
FRONTEND_DIR="${PROJECT_DIR}/frontend"
WEB_ROOT="/var/www/html"

if [[ "$EUID" -eq 0 ]]; then
  echo "Este script debe correrse como user adrian (no root)."
  exit 1
fi

cd "${PROJECT_DIR}"
echo "[1/3] Actualizando codigo"
git fetch origin
git reset --hard origin/main

cd "${FRONTEND_DIR}"
echo "[2/3] Construyendo web"
npm install
WEB_API_BASE="${EXPO_PUBLIC_API_BASE:-${API_BASE:-http://127.0.0.1:8000}}"
EXPO_PUBLIC_API_BASE="${WEB_API_BASE}" npx expo export:web

echo "[3/3] Publicando web en nginx"
sudo rm -rf "${WEB_ROOT:?}/"*
sudo cp -r web-build/* "${WEB_ROOT}/" 2>/dev/null || true

echo "web actualizada"
