#!/usr/bin/env bash
set -euo pipefail

if [[ "$EUID" -ne 0 ]]; then
  echo "Ejecuta este script como root."
  exit 1
fi

BASE_DIR="/home/adrian/CoAIch"
SERVICE="coai-ch-backend"

echo "[1/6] Parando servicios"
systemctl stop "${SERVICE}" || true
systemctl disable "${SERVICE}" || true
systemctl stop nginx || true

echo "[2/6] Eliminando proyecto y web-build"
cd / || true
rm -rf "${BASE_DIR}"
rm -rf /var/www/html/*

echo "[3/6] Purga paquetes de sistema"
apt-mark unhold nodejs npm || true
apt update
apt install -f || true
apt remove --purge -y \
  nginx postgresql postgresql-contrib \
  nodejs npm \
  python3 python3-venv python3-pip build-essential libpq-dev \
  git || true
apt autoremove -y || true
apt purge -y nodesource* || true
rm -f /etc/apt/sources.list.d/nodesource.list

echo "[4/6] Quitando PostgreSQL user/db"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS coaih;" || true
sudo -u postgres psql -c "DROP USER IF EXISTS adrian;" || true

echo "[5/6] Limpiando repositorios y cache"
rm -f /etc/apt/sources.list.d/nodesource.list
apt update

echo "[6/6] Reporte final"
echo "El proyecto CoAIch ha sido purgado."
echo "Revisa que no queden procesos de uvicorn/node en ejecución."
