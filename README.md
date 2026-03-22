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
- Canonical Layer: `sessions`, `warmups`, `session_blocks`, `block_exercises_raw`, `block_items_canonical`.
- UI: consume canonical para ordenar y raw para mostrar todo lo que falte.

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
- `sessions`: metadatos generales, tags, duracion, estado de data.
- `warmups`: quote, mobility, activation, raw_text.
- `session_blocks`: orden, tipo, raw_text, coach_notes, referencias externas.
- `block_exercises_raw`: preserva `exercises[]` de octubre.
- `block_items_canonical`: normalizado para futuro (movimiento, sets, reps, etc.).

**Reglas de importacion**
- Siempre guardar raw antes de transformar.
- Detectar variante por predominio de `exercises[]` vs `prescription/coach_notes`.
- Nunca inventar datos. Si no se infiere, `null` y conservar `raw_origin_text`.
- Si hay referencias externas, marcar `has_external_reference` y `data_status`.

**Autenticacion**
- Login simple por usuario y contrasena, sin registro.
- Endpoint `POST /auth/login` valida credenciales.
- `GET /sessions` y `GET /sessions/{id}` requieren Basic Auth.
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
- `GET /sessions`
- `GET /sessions/{id}`

---

**Despliegue en VPS**
1. Preparacion inicial:
```
cd ~/CoAIch
sudo chmod +x scripts/prepare_setup.sh
sudo scripts/prepare_setup.sh
```
2. Despliegues posteriores:
```
cd ~/CoAIch
chmod +x scripts/deploy_app.sh
EXPO_PUBLIC_API_BASE=http://<IP-VPS>:8000 ./scripts/deploy_app.sh
```

`deploy_app.sh` ejecuta `npx expo export:web` y publica `web-build/`.

**Checklist de deploy VPS**
1. Backend: servicio activo
```
sudo systemctl status coai-ch-backend
```
2. API responde sin auth prompt:
```
curl -s http://<IP-VPS>:8000/sessions/ | head
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

---

**Notas**
- `.env` esta en `.gitignore`.
- La UI siempre muestra `raw_text` cuando falta canonico.
- La base esta preparada para futuras fases (carga, feedback, lesiones, nutricion).
