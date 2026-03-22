#!/usr/bin/env bash
set -euo pipefail

SERVICE="coai-ch-backend"

if [[ "$EUID" -ne 0 ]]; then
  echo "Este script debe ejecutarse como root."
  echo "Ejemplo: sudo ./scripts/stop_app.sh"
  exit 1
fi

echo "[1/2] Parando backend"
systemctl stop "${SERVICE}" || true
systemctl disable "${SERVICE}" || true

echo "[2/2] Parando nginx"
systemctl stop nginx || true
systemctl disable nginx || true

echo "App detenida (backend + nginx)."
