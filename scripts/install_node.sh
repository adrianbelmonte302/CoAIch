#!/usr/bin/env bash
set -euo pipefail

if [[ "$EUID" -ne 0 ]]; then
  echo "Ejecutar como root para instalar Node.js con apt."
  exit 1
fi

echo "[1/5] Limpiando retenciones y paquetes rotos"
apt-mark unhold nodejs npm || true
apt update
apt install -f
dpkg --configure -a

echo "[2/5] Eliminando Node/npm antiguos"
apt remove --purge -y nodejs npm || true
apt autoremove -y

echo "[3/5] Añadiendo repositorio oficial NodeSource para Node 20"
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -

echo "[4/5] Instalando nodejs"
apt install -y nodejs

echo "[5/5] Verificación"
node -v
npm -v

echo "Instalación completada. Ahora puedes ejecutar npm install desde ~/CoAIch/frontend sin apt."
