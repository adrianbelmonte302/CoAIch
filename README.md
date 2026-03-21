# CoAIch Training Lab

Aplicación MVP para preservar entrenamientos históricos desde JSON y ofrecer una consulta tipo TrueCoach, tanto por API como desde un cliente Expo React Native.

## Contenido

- `docs/ARCHITECTURE.md`: Propuesta de arquitectura (capas raw/canonical, pipeline de importación y consideraciones UX).
- `docs/DATA_MODEL.md`: Esquema relacional detallado para el raw layer y el canonical layer.
- `backend/`: FastAPI, SQLAlchemy/Alembic, importador adaptable y tests.
- `frontend/`: Proyecto Expo mínimo con lista y detalle de sesiones.
- `backend/importer_cli.py`: Script de carga inicial para los JSON históricos de octubre, noviembre y diciembre.

## Arquitectura resumida

1. **Raw Layer**: `raw_imports` guarda el JSON completo con metadatos —jamás se modifica— y sirve como fuente de verdad para cada importación.
2. **Canonical Layer**: `sessions`, `warmups`, `session_blocks`, `block_exercises_raw` y `block_items_canonical` transforman los datos a un modelo estable sin perder trazabilidad (se conserva el texto crudo).
3. **Backoffice API**: FastAPI expone `/sessions` y `/sessions/{id}` para listar/detallar entrenamientos. La pantalla del día usa primero la capa canónica pero se apoya en el raw cuando falta algún dato.
4. **Frontend móvil**: Expo + React Navigation muestra listas y detalles con look & feel sobrio, resaltando etiquetas, bloques y texto íntegro del coach.

La arquitectura está pensada desde ya para futuras fases (analítica de carga, nutrición, feedback de lesiones, motor de recomendaciones) sin reestructurar la base de datos original.

## Primeros pasos

### 1. Backend

1. Definir variables de entorno:
   - Crea un archivo `backend/.env` con `DATABASE_URL=postgresql+psycopg2://user:pass@host:port/db`.
2. Instalar dependencias:
   ```bash
   cd backend
   python -m pip install -r requirements.txt
   ```
3. Ejecutar migraciones (Alembic ya configurado para cargar `app.models`):
   ```bash
   alembic upgrade head
   ```
4. Levantar el servidor FastAPI:
   ```bash
   uvicorn app.main:app --reload
   ```

### 2. Importar los JSON de entrenamiento

Los archivos originales viven fuera del repositorio (e.g. `c:/Users/.../workouts_octubre_2025.json`). El script `backend/importer_cli.py` detecta variantes y guarda raw + canonical:

```bash
cd backend
python importer_cli.py "c:/Users/.../workouts_octubre_2025.json" \
    "c:/Users/.../workouts_noviembre_2025.json" \
    "c:/Users/.../workouts_diciembre_2025.json"
```

- El script autosugiere el `source_month` (octubre/noviembre/diciembre) a partir del nombre del archivo.
- Detecta la variante (ejercicios con `exercises[]` vs `prescription/coach_notes`) y adapta `content_mode` en `session_blocks`.
- Siempre conserva el JSON original en `raw_imports`.
- Registra warnings cuando se omiten bloques mal formados o se detectan referencias externas como “TrueCoach”.

### 3. API REST

- `GET /sessions`: lista ordenada por fecha (incluye título, tags, duración, flags de descanso/deload/external).
- `GET /sessions/{id}`: retorna warmup, cada bloque ordenado, coach notes, exercises raw, ítems canónicos y texto bruto para no perder contenido del entrenador.

La API está preparada para agregar filtros (calendario, tags, posesión del atleta) cuando lleguen las fases posteriores.

### 4. Frontend Expo

1. Instalar dependencias:
   ```bash
   cd frontend
   npm install
   ```
2. Ajustar la constante `API_BASE` en `frontend/App.tsx` si el backend corre en otra URL.
3. Ejecutar:
   ```bash
   npm run start
   ```
4. El prototipo ofrece:
   - Pantalla de lista de sesiones (título, fecha, duración, tags, badges).
   - Pantalla de detalle con warmup, bloques, notas del coach, ejercicios originales y items canónicos (en orden).

## Tests

Desde `backend/`:

```bash
pytest
```

- Se validan las tres variantes (octubre, noviembre y diciembre) sin romper el importador.
- Se comprueba que `raw_imports` conserva el JSON original y que no se pierden ejercicios ni texto canónico.

## Próximos pasos

1. Integrar autenticación y permisos para coaches/atletas.
2. Añadir tablas auxiliares para métricas de ejecución, nutrición y síntomas/lesiones, tomando como punto de partida `block_items_canonical`.
3. Desarrollar dashboards de análisis de carga y sugerencias automáticas sin truncar el contenido original.
4. Evolucionar la app móvil para permitir feedback y seguimiento en tiempo real.

## Notas adicionales

- Todas las decisiones de parsing se guían por el principio “si el coach lo escribió, el usuario debe verlo”. Cuando el modelo canónico no alcanza, la UI recurre al texto raw.
- Las claves `block_items_canonical.intensity_value_json` y `block_exercises_raw.raw_payload` mantienen la información cruda lista para futuros análisis.
