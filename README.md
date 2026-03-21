# CoAIch Training Lab

Aplicación MVP para preservar entrenamientos históricos desde JSON y ofrecer una experiencia tipo TrueCoach: backend FastAPI protegido, capa raw/canonical sobre PostgreSQL y frontend Expo para listar/detallar sesiones con todos los datos originales del coach.

## Contenido

- `docs/ARCHITECTURE.md`: Visión de arquitectura (raw+canonical, UX y pipeline de importación).
- `docs/DATA_MODEL.md`: Modelo de datos relacional completo.
- `backend/`: FastAPI, SQLAlchemy, Alembic, importador adaptable y pruebas.
- `frontend/`: Expo + React Navigation para listado y detalle de sesiones.
- `scripts/setup_vps.sh`: Instalación automática para VPS/RPi.

## Prerrequisitos

1. PostgreSQL (local o remoto) accesible desde `DATABASE_URL`.
2. Python 3.11+, Node 20+, npm.
3. Archivos JSON históricos listos (octubre, noviembre, diciembre).

## Primeros pasos

1. **Configurar variables obligatorias en `backend/.env`:**
   ```bash
   DATABASE_URL=postgresql+psycopg2://adrian:<contraseña-postgres>@localhost:5432/coaih
   API_USERNAME=adrian
   API_PASSWORD=<contraseña-http-basic>
   ```
2. **Backend:**
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   alembic upgrade head
   ```
3. **Importar los JSON históricos (ajusta rutas absolutas):**
   ```bash
   python importer_cli.py /ruta/workouts_octubre_2025.json \
       /ruta/workouts_noviembre_2025.json \
       /ruta/workouts_diciembre_2025.json
   ```
4. **Levantar la API:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   Accede a `http://localhost:8000/docs` con `API_USERNAME` + `API_PASSWORD`.
5. **Frontend:**
   ```bash
   cd ../frontend
   npm install
   npm run start
   ```
   Ajusta `API_BASE` en `frontend/App.tsx` si la API vive en otro host.

## Despliegue en Linux / VPS / RPi

1. Instala dependencias básicas (Python, Node, PostgreSQL y nginx).
2. Usa `scripts/setup_vps.sh` como root para automatizar instalación y configuración (te pedirá contraseñas seguras para PostgreSQL y HTTP Basic).
3. Una vez desplegado, el script `scripts/deploy_app.sh` sirve para actualizar el VPS con la última versión: desde el usuario `adrian` ejecuta `./scripts/deploy_app.sh` (aclárale que debe ser ejecutable `chmod +x scripts/deploy_app.sh`).  
   - Hace `git reset --hard origin/main`, reinstala deps, aplica migraciones, reinicia el servicio systemd, rebuild del frontend (`npm run build`) y copia el resultado a `/var/www/html` si existe.
4. Verifica `systemctl status coai-ch-backend nginx` y protege puertos con `ufw`.

## Tests

```bash
cd backend
pytest
```

## Notas importantes

- `backend/.env` está en `.gitignore`; nunca subas credenciales reales.
- La UI muestra siempre los datos raw completos y solo usa el modelo canonical para ordenar y preparar futuras analíticas.
- Puedes cambiar las credenciales HTTP Basic actualizando `.env` y reiniciando uvicorn.
