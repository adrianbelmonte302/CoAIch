#!/usr/bin/env bash
set -euo pipefail

if [[ "$EUID" -ne 0 ]]; then
  echo "Este script debe ejecutarse como root."
  exit 1
fi

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
SCRIPT_DIR="${BASE_DIR}/scripts"

echo "[1/3] Limpieza y reinstalación de Node"
chmod +x "${SCRIPT_DIR}/fix_dependencies.sh" "${SCRIPT_DIR}/install_node.sh"
"${SCRIPT_DIR}/fix_dependencies.sh"
"${SCRIPT_DIR}/install_node.sh"

echo "[2/3] Ejecutar el setup principal"
chmod +x "${SCRIPT_DIR}/setup_vps.sh"
"${SCRIPT_DIR}/setup_vps.sh"

echo "[3/4] Verificar servicios"
sudo systemctl status coai-ch-backend nginx

echo "[4/4] Permisos de despliegue"
chmod +x "${SCRIPT_DIR}/deploy_app.sh" || true
chmod +x "${SCRIPT_DIR}/deploy_backend.sh" || true
chmod +x "${SCRIPT_DIR}/deploy_web.sh" || true
chmod +x "${SCRIPT_DIR}/make_executable.sh" || true
chmod +x "${SCRIPT_DIR}/stop_app.sh" || true
chmod +x "${SCRIPT_DIR}/uninstall_vps.sh" || true
