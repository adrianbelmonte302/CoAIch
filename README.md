# CoAIch Training Lab

Aplicación MVP para preservar entrenamientos históricos desde JSON y ofrecer una experiencia tipo TrueCoach con una API FastAPI protegida, raw/canonical persistence en PostgreSQL y cliente Expo React Native.

## Contenido

- `docs/ARCHITECTURE.md`: visión del pipeline raw/canonical y UX.
- `docs/DATA_MODEL.md`: esquema relacional detallado.
- `backend/`: FastAPI, SQLAlchemy, Alembic y el importador adaptable con tests.
- `frontend/`: Expo + React Navigation para listado y detalle.
- `scripts/`: utilidades `setup_vps.sh`, `deploy_app.sh`, `install_node.sh`, `fix_dependencies.sh`.

## Primeros pasos (máquina local)

1. **Variables críticas:** crea `backend/.env` (no lo subas a GitHub).
   ```bash
   DATABASE_URL=postgresql+psycopg2://adrian:<contraseña-postgres>@localhost:5432/coaih
   API_USERNAME=adrian
   API_PASSWORD=<contraseña-http-basic>
   ```
   - Escapa caracteres especiales (ej. `G7%24k9%23vQ8xh%212B`) si usas `#`, `%`, `&`.
   - El backend ahora convierte `PostgresDsn` a string antes de pasarlo a Alembic, así que el valor debe ser texto válido (si ves `TypeError: option values must be strings`, revisa que la línea no sea un objeto con metadatos).
2. **Backend:**
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   alembic upgrade head
   ```
3. **Importación histórica:** (usa rutas absolutas)
   ```bash
   python importer_cli.py /ruta/workouts_octubre_2025.json \
       /ruta/workouts_noviembre_2025.json \
       /ruta/workouts_diciembre_2025.json
   ```
4. **Levanta FastAPI con autenticación básica**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
5. **Frontend Expo**
   ```bash
   cd ../frontend
   npm install
   npm run start
   ```
   Ajusta `API_BASE` en `frontend/App.tsx` si el backend vive en otra máquina.

## Migración y tests

```bash
cd backend
pytest
```

## Despliegue en Linux / VPS / RPi

1. **Limpia dependencias rotas e instala Node 20 desde NodeSource**
   ```bash
   cd ~/CoAIch
   sudo chmod +x scripts/fix_dependencies.sh scripts/install_node.sh
   sudo scripts/fix_dependencies.sh
   sudo scripts/install_node.sh
   ```
   - `fix_dependencies.sh` libera held packages, purga nodejs/npm antiguos y reinstala desde NodeSource.
   - `install_node.sh` puede ir ajustando prefijos de `npm` o `PATH` si expandes la configuración.
2. **Setup inicial (como root)** – *asegúrate de haber ejecutado primero los scripts anteriores*
   ```bash
   sudo chmod +x scripts/setup_vps.sh
   sudo scripts/setup_vps.sh
   ```
   Esto instala dependencias, crea `.env`, configura PostgreSQL y deja uvicorn/nginx listos.
3. **Despliegues sucesivos**
   ```bash
   cd ~/CoAIch
   chmod +x scripts/deploy_app.sh
   ./scripts/deploy_app.sh
   ```
   - Actualiza el código (`git reset --hard origin/main`)
   - Reactiva el virtualenv y reinstala dependencias
   - Ejecuta `alembic upgrade head`
   - Reinicia el servicio systemd `coai-ch-backend`
   - Reconstruye la UI web con `npm run web` y publica `web-build/` en `/var/www/html`
4. **Verifica servicios y seguridad**
   ```bash
   sudo systemctl status coai-ch-backend nginx
   sudo ufw allow 80/tcp 443/tcp
   sudo ufw enable
   ```

## Qué hacer si el password rompe Alembic

- Si `.env` tiene caracteres reservados, percent-encodéalos en la URL (ej. `G7%24k9%23vQ8xh%212B`) o encierra la línea entre comillas.
- Alternativamente elige claves sin `#` ni espacios para evitar parsing errors.

## Notas finales

- `.env` está en `.gitignore`; nunca lo subas.
- La UI siempre muestra el raw text del coach. El canonical layer se usa para orden, filtros y futura analítica.
- Puedes usar `npm config set prefix '~/.npm-global'` si quieres instalar herramientas Node sin `sudo`.
