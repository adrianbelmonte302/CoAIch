#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKEND_DIR="${PROJECT_DIR}/backend"
SERVICE="coai-ch-backend"

if [[ "$EUID" -eq 0 ]]; then
  echo "Este script debe correrse como user adrian (no root)."
  exit 1
fi

cd "${PROJECT_DIR}"
if [[ -x "${SCRIPT_DIR}/make_executable.sh" ]]; then
  "${SCRIPT_DIR}/make_executable.sh" || true
fi
if [[ ! -f "${BACKEND_DIR}/requirements.txt" ]]; then
  echo "No se encontro requirements.txt en ${BACKEND_DIR}. Revisa la ruta del repo."
  exit 1
fi
echo "[1/5] Actualizando código"
git fetch origin
git reset --hard origin/main

cd "${BACKEND_DIR}"
echo "[2/5] Actualizando dependencias"
source .venv/bin/activate
pip install -r requirements.txt

echo "[3/5] Ejecutando migraciones"
alembic upgrade head

echo "[4/5] Reiniciando servicio backend"
sudo systemctl restart "${SERVICE}"
sudo journalctl -u "${SERVICE}" --no-pager -n 20

echo "[5/5] (Opcional) rebuild frontend web"
cd "${PROJECT_DIR}/frontend"
if [[ ! -f "${PROJECT_DIR}/frontend/package.json" ]]; then
  echo "No se encontro package.json en ${PROJECT_DIR}/frontend. Revisa la ruta del repo."
  exit 1
fi
npm install
echo "Asegurando dependencias web (react-native-web, react-dom, @expo/webpack-config)"
npx expo install react-native-web@~0.19.6 react-dom@18.2.0 @expo/webpack-config@^19.0.0
WEB_API_BASE="${EXPO_PUBLIC_API_BASE:-${API_BASE:-http://127.0.0.1:8000}}"
EXPO_PUBLIC_API_BASE="${WEB_API_BASE}" npx expo export:web
sudo rm -rf /var/www/html/*
sudo cp -r web-build/* /var/www/html/ 2>/dev/null || true

echo "despliegue completado"
