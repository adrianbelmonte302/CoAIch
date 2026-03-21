#!/usr/bin/env bash
set -euo pipefail

if [[ "$EUID" -ne 0 ]]; then
  echo "Ejecutar como root"
  exit 1
fi

echo "[1/4] Liberando paquetes retenidos y limpiando estado"
apt-mark unhold nodejs npm || true
apt update
apt install -f
dpkg --configure -a

echo "[2/4] Retirando Node/NPM conflictivos"
apt remove -y nodejs npm || true
apt purge -y nodejs npm || true
apt autoremove -y

echo "[3/4] Volviendo a inicializar NodeSource y reinstalar binarios"
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y --no-install-recommends nodejs

echo "[4/4] Verificación"
node -v
npm -v

echo "Ahora ejecuta scripts/install_node.sh si necesitas reinstalar Node con otros ajustes."
