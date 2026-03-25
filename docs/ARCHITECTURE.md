# CoAIch Training Lab — Arquitectura MVP

## Visión general
El MVP está dividido en tres superficies principales:

1. **Capa de persistencia** — PostgreSQL guarda exactamente lo que el coach exportó en una tabla `raw_imports` y además una capa canonical que permite búsquedas y evolución futura.
2. **Backend FastAPI** — expone endpoints REST minimalistas para obtener listados y detalles y contiene la lógica de importación adaptable a las variantes de JSON (octubre con `exercises[]`, noviembre/diciembre con `prescription`/`coach_notes`).
3. **Frontend Expo React Native** — lista de sesiones + detalle tipo TrueCoach con jerarquía clara que prioriza mostrar todo lo que haya en la sesión, usando primero el modelo canónico pero cayendo al raw cuando algo falta.

## Capa de datos

1. **Raw Layer**
   - Cada archivo importado se inserta en `raw_imports`, manteniendo `raw_json` completo, metadatos del origen y la versión del parser.
   - Nunca se modifica el JSON original.

2. **Canonical Layer**
   - `sessions` normaliza metadatos clave (fecha, título, etiquetas, duración, flags de descanso/descarga y referencia externa).
   - `warmups` y `session_blocks` permiten reconstruir la sesión ordenada.
   - `block_exercises_raw` guarda tal como venían los exercises[] de octubre.
   - `block_items_canonical` modela cada ítem interpretado para atender futuras fases de análisis (movimientos, patrones, intensidad). Nunca inventa valores: si no se puede inferir, se deja `null` y se guarda el texto bruto.

La UI consume ambos modelos: los campos canónicos ofrecen orden y estructura, mientras que los textos de la capa raw garantizan que **nada escrito por el coach se pierda**.

## Pipeline de importación

1. **Detectar variante**
   - Se cuentan bloques con `exercises[]` vs. bloques con `prescription`/`coach_notes`.
   - Se selecciona el adaptador correspondiente pero el parser siempre tolera campos opcionales ausentes.

2. **Persistir raw**
   - Antes de cualquier transformación se guarda el JSON completo en `raw_imports`.

3. **Transformar**
   - Se crean sesiones canónicas asociadas al raw import.
   - Para cada bloque se genera `session_blocks` con `content_mode` ("exercise_notes" o "prescription"), `raw_text`, `coach_notes` y banderas de referencia externa.
   - Si un bloque usa `exercises[]`, se crean registros en `block_exercises_raw` y se agregan ítems canónicos por cada entrada.
   - Si el bloque solo tiene texto libre y/o `prescription`, se crea un ítem canónico con `raw_origin_text`.

4. **Warnings**
   - Se registran mensajes (en logs y respuesta del importador) cuando falta información esperada o se detecta referencia externa.

## API REST

- `GET /sessions`: lista paginada ordenada por fecha, con fecha, título, duración, etiquetas y flags (rest/deload/external_reference).
- `GET /sessions/{id}`: devuelve toda la información de la sesión, incluyendo warmup, bloques (con `session_blocks`, `block_exercises_raw` y `block_items_canonical`) y `raw_import` reference.
- `POST /import`: endpoint administrativo que recibe un `source_file`/`source_month` y delega al importador con adaptador detectado.

## Frontend móvil

- Pantalla **Lista de sesiones**: timeline/calendario con tarjetas limpias. Orden cronológico, muestra título, fecha, tags y duración.
- Pantalla **Detalle de sesión**: muestra warmup, cada bloque en orden y dentro de cada bloque:
  - `content_mode`, `coach_notes`, `prescription`, `exercises[]` (si existen) y `external_reference`.
  - En paralelo, se renderizan los ítems canónicos junto con el texto bruto asociado.
- La UI da prioridad a no truncar, mostrando `raw_text` completo y resaltando si algo viene de referencias externas.

## Futuros pasos considerados desde hoy

- Integración de tracking de ejecución y métricas de carga partiendo de `block_items_canonical`.
- APIs de feedback, lesiones, nutrición y recomendaciones basadas en los datos ya normalizados.
- Posible motor de inferencia que analice `block_items_canonical.intensity_value_json`.

El diseño actual garantiza que el MVP sea sólido (ingesta, persistencia y visualización fiel) pero deja la puerta abierta para exposición de métricas y análisis avanzados sin tener que reorganizar la base de datos central.

## Evolución hacia Program Days (schema v2)

Desde marzo 2026 el backend incorpora un **Domain Layer** nuevo con `program_days` como entidad canonica de calendario. Este modelo reemplaza gradualmente el uso directo de `sessions` (legacy), pero mantiene compatibilidad:

- `program_days` almacena el JSON v2 (session_flow, variantes, bloques, sub-bloques y ejercicios) sin aplanar la estructura.
- `workout_definitions`, `competitions`, `competition_workouts`, `competition_results` y `athlete_executions` están creados como scaffolding para benchmarks, eventos y resultados.
- El importador detecta `entity_type=program_day` y valida con schema v2.
- La API `GET /program-days` devuelve program days; si no existen, puede mapear legacy con `include_legacy=1`.

La UI prioriza `program_days` cuando existen y cae a `sessions` cuando el pipeline v2 aún no está disponible.
