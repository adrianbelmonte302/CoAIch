#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/adrian/CoAIch"
BACKEND_DIR="${PROJECT_DIR}/backend"
SERVICE="coai-ch-backend"

if [[ "$EUID" -eq 0 ]]; then
  echo "Este script debe correrse como user adrian (no root)."
  exit 1
fi

cd "${PROJECT_DIR}"
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
npm install
npm run web
sudo rm -rf /var/www/html/*
sudo cp -r web-build/* /var/www/html/ 2>/dev/null || true

echo "despliegue completado"
