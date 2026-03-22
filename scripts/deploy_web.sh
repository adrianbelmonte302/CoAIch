#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
FRONTEND_DIR="${PROJECT_DIR}/frontend"
WEB_ROOT="/var/www/html"

if [[ "$EUID" -eq 0 ]]; then
  echo "Este script debe correrse como user adrian (no root)."
  exit 1
fi

cd "${PROJECT_DIR}"
if [[ ! -f "${FRONTEND_DIR}/package.json" ]]; then
  echo "No se encontro package.json en ${FRONTEND_DIR}. Revisa la ruta del repo."
  exit 1
fi
echo "[1/3] Actualizando codigo"
git fetch origin
git reset --hard origin/main

cd "${FRONTEND_DIR}"
echo "[2/3] Construyendo web"
npm install
echo "Asegurando dependencias web (react-native-web, react-dom, @expo/webpack-config)"
npx expo install react-native-web@~0.19.6 react-dom@18.2.0 @expo/webpack-config@^19.0.0
WEB_API_BASE="${EXPO_PUBLIC_API_BASE:-${API_BASE:-http://127.0.0.1:8000}}"
EXPO_PUBLIC_API_BASE="${WEB_API_BASE}" npx expo export:web

echo "[3/3] Publicando web en nginx"
sudo rm -rf "${WEB_ROOT:?}/"*
sudo cp -r web-build/* "${WEB_ROOT}/" 2>/dev/null || true

echo "web actualizada"
