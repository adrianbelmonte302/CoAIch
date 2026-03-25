# CoAIch Training Lab

MVP para preservar entrenamientos historicos desde JSON con arquitectura raw + canonical, API FastAPI y cliente Expo. En esta fase la app solo consulta entrenamientos ya cargados, sin logica de coaching ni analitica.

**Objetivo clave**
No perder ningun dato del coach. Todo lo importado queda guardado en la capa raw y visible en UI. La capa canonical sirve para estructura, orden y futuras fases.

**Contenido del repo**
- `docs/ARCHITECTURE.md` vision del pipeline raw/canonical y UX.
- `docs/DATA_MODEL.md` esquema relacional detallado.
- `backend/` FastAPI, SQLAlchemy, Alembic, importador y tests.
- `frontend/` Expo + React Navigation para listado y detalle.
- `scripts/` setup VPS y despliegue.

**Stack**
- Backend: FastAPI + SQLAlchemy + Alembic
- DB: PostgreSQL
- Frontend: React Native (Expo) + Web export
- Validacion: Pydantic

**Arquitectura**
- Raw Layer: `raw_imports` guarda el JSON completo, versiona parser y metadatos de origen.
- Canonical Layer (legacy): `sessions`, `warmups`, `session_blocks`, `block_exercises_raw`, `block_items_canonical` (solo historial v1).
- Domain Layer (nuevo): `program_days` como entidad canonica principal del calendario + scaffolding de futuro (`workout_definitions`, `competitions`, `competition_workouts`, `competition_results`, `athlete_executions`).
- UI: consume solo `program_days`. El JSON v1 se adapta a v2 antes de llegar al dominio.

**Diagrama (flujo de datos)**
```
JSON historicos
   |
   v
RAW IMPORTS (raw_imports.raw_json)
   |
   v
CANONICAL (sessions / warmups / session_blocks / items)
   |
   v
API REST
   |
   v
UI (usa canonical + fallback raw)
```

**Modelo de datos (resumen)**
- `raw_imports`: `source_file`, `source_month`, `raw_json`, `parser_version`, `imported_at`.
- `sessions`: metadatos generales, tags, duracion, estado de data (legacy).
- `program_days`: nuevo canon para calendario y schema v2 (session_flow, variants, blocks, etc.).
- `warmups`: quote, mobility, activation, raw_text.
- `session_blocks`: orden, tipo, raw_text, coach_notes, referencias externas.
- `block_exercises_raw`: preserva `exercises[]` de octubre.
- `block_items_canonical`: normalizado para futuro (movimiento, sets, reps, etc.).
- `workout_definitions`, `competitions`, `competition_workouts`, `competition_results`, `athlete_executions`: scaffolding para benchmark, eventos y resultados futuros.

**Program Day schema v2**
- Formato canonico de importacion para TrueCoach y programacion diaria.
- Soporta variantes, bloques, sub-bloques, ejercicios y notas de coach sin perder fidelidad.
- Fixture de ejemplo: `docs/fixtures/program_day_sample.json`.
- Compatibilidad v1: `app/importer/v1_adapter.py` transforma JSON legacy a v2 antes de guardar.

**Reglas de importacion**
- Siempre guardar raw antes de transformar.
- Detectar variante por predominio de `exercises[]` vs `prescription/coach_notes`.
- Nunca inventar datos. Si no se infiere, `null` y conservar `raw_origin_text`.
- Si hay referencias externas, marcar `has_external_reference` y `data_status`.

**Autenticacion**
- Login simple por usuario y contrasena, sin registro.
- Endpoint `POST /auth/login` valida credenciales.
- `GET /program-days` y `GET /program-days/{id}` requieren Basic Auth.
- Frontend guarda credenciales en web si el usuario elige "Recordarme".
- Auto logout tras `AUTO_LOGOUT_MIN` (60 min).

---

**Requisitos**
- Python 3.10+
- Node 18+
- PostgreSQL 14+
- Nginx (para web)

---

**Variables de entorno**
Archivo `backend/.env`:
```
DATABASE_URL=postgresql+psycopg2://adrian:<password>@localhost:5432/coaich
API_USERNAME=<usuario>
API_PASSWORD=<password>
```

Para build web:
```
EXPO_PUBLIC_API_BASE=http://<IP-VPS>:8000
```

---

**Backend local**
1. Crear entorno y dependencias
```
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
2. Migraciones
```
alembic upgrade head
```
3. Iniciar API
```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

**Importacion historica**
```
cd backend
python importer_cli.py /ruta/workouts_octubre_2025.json \
  /ruta/workouts_noviembre_2025.json \
  /ruta/workouts_diciembre_2025.json
```

Reescribir duplicados (mismo contenido):
```
python importer_cli.py --overwrite /ruta/workouts_octubre_2025.json
```

Solo sesiones nuevas (ignora overwrite):
```
python importer_cli.py --only-new /ruta/workouts_octubre_2025.json
```

Dry-run (no escribe en DB):
```
python importer_cli.py --dry-run /ruta/workouts_octubre_2025.json
```

Limitar cantidad por archivo:
```
python importer_cli.py --limit 10 /ruta/workouts_octubre_2025.json
```

---

**Importacion Program Days (schema v2)**
El importador detecta automaticamente listas con `entity_type=program_day` (schema v2). Si recibe JSON legacy v1, lo transforma a v2 con un adaptador antes de guardar.
```
python importer_cli.py /ruta/program_days_agosto_2025.json
```

Reescribir duplicados (mismo hash del payload):
```
python importer_cli.py --overwrite /ruta/program_days_agosto_2025.json
```

Solo nuevos (ignora overwrite):
```
python importer_cli.py --only-new /ruta/program_days_agosto_2025.json
```

Dry-run:
```
python importer_cli.py --dry-run /ruta/program_days_agosto_2025.json
```

---

**Frontend local**
```
cd frontend
npm install
npm run start
```

---

**Build Web (correcto para VPS)**
```
cd frontend
 npx expo install react-native-web@~0.19.6 react-dom@18.2.0 @expo/webpack-config@^19.0.0
EXPO_PUBLIC_API_BASE=http://<IP-VPS>:8000 npx expo export:web
```
Output: `frontend/web-build/`

Publicacion Nginx:
```
sudo rm -rf /var/www/html/*
sudo cp -r web-build/* /var/www/html/
```

---

**API REST minima**
- `POST /auth/login`
- `GET /program-days`
- `GET /program-days/{id}`

---

**Migracion a Program Days (v2)**
1. Ejecutar migraciones nuevas:
```
cd backend
alembic upgrade head
```
2. Migrar datos legacy en la base actual:
```
cd backend
python scripts/migrate_v1_to_v2.py
```
3. Importar JSON v2 (ver `docs/fixtures/program_day_sample.json`).

---

**Despliegue en VPS**
1. Preparacion inicial:
```
cd ~/CoAIch
sudo chmod +x scripts/prepare_setup.sh
sudo scripts/prepare_setup.sh
```
2. Hacer scripts ejecutables (si hace falta):
```
cd ~/CoAIch
./scripts/make_executable.sh
```
3. Despliegues posteriores:
```
cd ~/CoAIch
chmod +x scripts/deploy_app.sh
EXPO_PUBLIC_API_BASE=http://<IP-VPS>:8000 ./scripts/deploy_app.sh
```

`deploy_app.sh` y `deploy_backend.sh` ejecutan automaticamente la migracion v1->v2:
```
python scripts/migrate_v1_to_v2.py
```

**Apagar la app (backend + nginx)**
```
cd ~/CoAIch
sudo ./scripts/stop_app.sh
```

**Chequeo completo del sistema (servicios + API + web)**
```
cd ~/CoAIch
./scripts/check_system.sh
```

Con autenticacion:
```
cd ~/CoAIch
API_CHECK_USER=<usuario> API_CHECK_PASS=<password> ./scripts/check_system.sh
```

**Desinstalacion completa (peligroso)**
```
cd ~/CoAIch
sudo ./scripts/uninstall_vps.sh
```

`deploy_app.sh` ejecuta `npx expo export:web` y publica `web-build/`.

**Deploy separado (backend / web)**
Backend:
```
chmod +x scripts/deploy_backend.sh
./scripts/deploy_backend.sh
```

Web:
```
chmod +x scripts/deploy_web.sh
EXPO_PUBLIC_API_BASE=http://<IP-VPS>:8000 ./scripts/deploy_web.sh
```

**Checklist de deploy VPS**
1. Backend: servicio activo
```
sudo systemctl status coai-ch-backend
```
2. API responde sin auth prompt:
```
curl -s http://<IP-VPS>:8000/program-days/ | head
```
3. Web publicada con build nuevo:
```
grep -R "localhost:8000" -n /var/www/html/static/js || true
```
4. Nginx activo:
```
sudo systemctl status nginx
```

---

**Tests**
```
cd backend
pytest
```

---

**Troubleshooting rapido**
- Si la web llama a `localhost:8000`, es build viejo.
- Rehacer build con `EXPO_PUBLIC_API_BASE` y publicar `web-build/`.
- Si `alembic` falla por caracteres especiales, escapa en `DATABASE_URL`.
- Si aparece `ConfigError: expected package.json ...`, estas en el directorio equivocado. Usa `scripts/deploy_web.sh` o entra en `frontend/` antes de exportar.
- Si aparece error de dependencias web, ejecuta `npx expo install react-native-web@~0.19.6 react-dom@18.2.0 @expo/webpack-config@^19.0.0` antes de `export:web`.

---

**Notas**
- `.env` esta en `.gitignore`.
- La UI siempre muestra `raw_text` cuando falta canonico.
- La base esta preparada para futuras fases (carga, feedback, lesiones, nutricion).
- UI: listado agrupado por mes y dia, con salto por fecha y titulo compuesto por dia/fecha/nombre si existe.
- UI: calendario en web con dias resaltados que tienen sesiones, vista de calendario con resumen por dia, encabezados centrados y textos centrados en listado/detalle. Login compacto con logo. Filtros por tipo (strength, rest, stamina, gymnastic).

---

**Contexto para Codex (handoff)**
Objetivo: MVP tipo TrueCoach para consultar entrenamientos historicos desde JSON, con prioridad absoluta a no perder datos del coach. Arquitectura de doble capa: raw (JSON completo) y canonical (normalizado). UI debe mostrar todo lo disponible, usando canonical para estructura y raw como fallback.

Estado actual:
- Backend FastAPI + PostgreSQL + SQLAlchemy + Alembic.
- Importador con variantes (octubre vs nov/dec) y deteccion automatica.
- Importador v2: detecta `program_days` (schema 2.0.0) y los guarda en `program_days` con deduplicacion por hash.
- Adaptador v1->v2: JSON legacy se transforma a v2 antes de persistir (sin mezclar logica en UI/API).
- Deduplicacion por `source_hash` (hash del payload completo de la sesion).
- CLI admite `--overwrite`, `--only-new`, `--dry-run`, `--limit`.
- Auth: login simple (sin registro) via `POST /auth/login`. Rutas `/program-days` requieren Basic Auth.
- Endpoints `/program-days` y `/program-days/{id}` son la base del dominio (v2).
- Frontend Expo: login, recordarme, auto logout y logout en header.
- UI web: calendario con dias resaltados y vista resumen; lista agrupada por mes/dia; solo consume `program_days`.
- UI web: mejora visual con textos centrados, titulos de meses/dias centrados y logo en login.
- Scripts separados: `deploy_backend.sh` y `deploy_web.sh`.
- Deploy scripts detectan el repo desde su propia ubicacion y validan rutas (evita errores por ejecutar desde el directorio equivocado).
- Deploy scripts aseguran dependencias web antes de `export:web` para evitar fallos en VPS.
- Script `make_executable.sh` para dejar todos los scripts con permisos de ejecucion en una sola orden.
- Script `stop_app.sh` para apagar backend + nginx.
- `uninstall_vps.sh` ahora detecta el repo desde su ubicacion y evita borrar rutas invalidas.
- Script `check_system.sh` para revisar servicios, web root y endpoints basicos.
- `prepare_setup.sh` ahora deja permisos de deploy configurados.

Tabla raw/canonical (resumen):
- raw_imports: JSON original completo + metadatos.
- sessions: metadatos de sesion + `source_hash`.
- program_days: canon calendario (schema v2) + `source_hash`.
- warmups, session_blocks, block_exercises_raw, block_items_canonical.
- workout_definitions, competitions, competition_workouts, competition_results, athlete_executions.

Reglas clave de negocio:
- Nunca inventar datos. Si no se infiere, guardar `null` y `raw_origin_text`.
- Si hay referencia externa, marcar `has_external_reference` y `data_status`.
- UI no trunca ni resume por defecto.

Comandos criticos:
- Importacion: `python importer_cli.py <paths> [--overwrite|--only-new|--dry-run|--limit N]`
- Build web correcto: `EXPO_PUBLIC_API_BASE=http://<IP>:8000 npx expo export:web`

Problemas previos resueltos:
- Web apuntaba a `localhost:8000` por build viejo.
- `npm run web` no genera build. Usar `expo export:web`.

Proximos pasos sugeridos:
1. Configurar Nginx para evitar cache en `index.html`.
2. Endpoint admin para reimport seguro (con auth).
3. UI mejorada con secciones y estado de autenticacion.

**Regla de mantenimiento del contexto**
Cada cambio importante (arquitectura, auth, importador, deploy o UX) debe actualizar esta seccion de README con el nuevo estado. Esto garantiza que Codex o cualquier nuevo colaborador pueda retomar el trabajo sin perder contexto.

