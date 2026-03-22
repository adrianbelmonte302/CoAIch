#!/usr/bin/env bash
set -euo pipefail

PROJECT_USER="adrian"
PROJECT_HOME="/home/${PROJECT_USER}/CoAIch"
BACKEND_DIR="${PROJECT_HOME}/backend"
FRONTEND_DIR="${PROJECT_HOME}/frontend"
SERVICE_NAME="coai-ch-backend"

if [[ "$EUID" -ne 0 ]]; then
  echo "Este script debe correrse con sudo o como root."
  exit 1
fi

echo "[1/7] Actualizando paquetes del sistema"
apt update
apt upgrade -y

echo "[2/7] Instalando dependencias básicas"
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y python3 python3-venv python3-pip build-essential libpq-dev nodejs postgresql postgresql-contrib nginx git

escape_sql() {
  printf "%s" "$1" | sed "s/'/''/g"
}

echo "[3/7] Preparando PostgreSQL"
DB_PASSWORD="${DB_PASSWORD:-}"
if [[ -z "$DB_PASSWORD" ]]; then
  read -rsp "Introduce la contraseña segura para el usuario PostgreSQL 'adrian': " DB_PASSWORD
  echo
fi
DB_PASSWORD_ESCAPED=$(escape_sql "$DB_PASSWORD")

# Migrate legacy DB name "coaih" to "coaich" if present.
LEGACY_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='coaih';" || true)
TARGET_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='coaich';" || true)
if [[ "$LEGACY_EXISTS" == "1" && "$TARGET_EXISTS" != "1" ]]; then
  sudo -u postgres psql -c "ALTER DATABASE coaih RENAME TO coaich;" >/dev/null 2>&1 || true
fi

sudo -u postgres psql -c "CREATE DATABASE coaich;" >/dev/null 2>&1 || true
sudo -u postgres psql -c "CREATE USER adrian WITH PASSWORD '${DB_PASSWORD_ESCAPED}';" >/dev/null 2>&1 || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE coaich TO adrian;" >/dev/null 2>&1 || true

echo "[4/7] Configurando backend"
if [[ ! -d "${PROJECT_HOME}" ]]; then
  echo "Copiando el repositorio al home de ${PROJECT_USER}"
  git clone https://github.com/adrianbelmonte302/CoAIch.git "${PROJECT_HOME}"
else
  echo "Reutilizando repo existente en ${PROJECT_HOME}"
fi

cd "${BACKEND_DIR}"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

API_USERNAME="${API_USERNAME:-adrian}"
DATABASE_URL="postgresql+psycopg2://adrian:${DB_PASSWORD}@localhost:5432/coaich"
cat <<EOF > .env
DATABASE_URL=${DATABASE_URL}
API_USERNAME=${API_USERNAME}
# API_PASSWORD must be set manually before starting the service
API_PASSWORD=
EOF

alembic upgrade head

echo "[5/7] Instalando frontend y ajustando API_BASE"
cd "${FRONTEND_DIR}"
npm install
node -e "const fs = require('fs'); const file = 'App.tsx'; let data = fs.readFileSync(file,'utf8'); data = data.replace(/const API_BASE = \".*\";/, 'const API_BASE = \"http://localhost:8000\";'); fs.writeFileSync(file,data);"

echo "[6/7] Importando entrenamientos históricos (opcional)"
cd "${BACKEND_DIR}"
if [[ -d "/opt/CoAIch-data" ]]; then
  python importer_cli.py /opt/CoAIch-data/workouts_octubre_2025.json \
      /opt/CoAIch-data/workouts_noviembre_2025.json \
      /opt/CoAIch-data/workouts_diciembre_2025.json
else
  echo "No se encontraron datos en /opt/CoAIch-data; omitiendo importación."
fi

echo "[7/7] Configurando servicio y proxy"
cp "${BACKEND_DIR}/deploy/uvicorn.service" "/etc/systemd/system/${SERVICE_NAME}.service"
systemctl daemon-reload
systemctl enable --now "${SERVICE_NAME}.service"

cat <<'EOF' > /etc/nginx/sites-available/coai-ch
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF
ln -sf /etc/nginx/sites-available/coai-ch /etc/nginx/sites-enabled/coai-ch
nginx -t
systemctl restart nginx

echo "Configurar el firewall y cambiar la contraseña de la base/HTTP Basic antes de exponer el VPS."
