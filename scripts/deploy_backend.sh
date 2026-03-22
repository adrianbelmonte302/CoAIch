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
echo "[1/4] Actualizando codigo"
git fetch origin
git reset --hard origin/main

cd "${BACKEND_DIR}"
echo "[2/4] Actualizando dependencias"
source .venv/bin/activate
pip install -r requirements.txt

echo "[3/4] Ejecutando migraciones"
alembic upgrade head

echo "[4/4] Reiniciando servicio backend"
sudo systemctl restart "${SERVICE}"
sudo journalctl -u "${SERVICE}" --no-pager -n 20

echo "backend actualizado"
