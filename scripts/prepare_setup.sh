#!/usr/bin/env bash
set -euo pipefail

if [[ "$EUID" -ne 0 ]]; then
  echo "Este script debe ejecutarse como root."
  exit 1
fi

echo "[1/3] Limpieza y reinstalación de Node"
sudo chmod +x scripts/fix_dependencies.sh scripts/install_node.sh
sudo scripts/fix_dependencies.sh
sudo scripts/install_node.sh

echo "[2/3] Ejecutar el setup principal"
sudo chmod +x scripts/setup_vps.sh
sudo scripts/setup_vps.sh

echo "[3/3] Verificar servicios"
sudo systemctl status coai-ch-backend nginx
