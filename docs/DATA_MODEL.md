# Data Model: Raw + Canonical Layers

## 1. `raw_imports`

| Campo | Tipo | Notas |
| --- | --- | --- |
| `id` | UUID | PK autogenerado. |
| `source_file` | text | Nombre del archivo JSON (ej. `workouts_octubre_2025.json`). |
| `source_month` | text | Mes inferido (`octubre`, `noviembre`, etc.). |
| `raw_json` | jsonb | JSON completo tal como llegó. |
| `parser_version` | text | Versión del adaptador que hizo la lectura. |
| `imported_at` | timestamptz | Timestamp UTC del import. |

## 2. `sessions`

| Campo | Tipo | Notas |
| --- | --- | --- |
| `id` | UUID | PK. |
| `raw_import_id` | UUID | FK a `raw_imports`. |
| `source_session_id` | text | Identificador del entrenador, si existe. |
| `date` | date | Fecha del entrenamiento. |
| `weekday` | text | Día en palabras (p. ej. `martes`). |
| `title` | text | Título visible. |
| `is_rest_day` | boolean | |
| `deload_week` | boolean | |
| `data_status` | text | `complete`, `external_reference`, etc. |
| `estimated_duration_min` | integer | Duración estimada. |
| `session_tags` | jsonb | Lista de etiquetas/tags. |
| `source_ref_file` | text | Si hay referencia externa explícita. |

## 3. `warmups`

| Campo | Tipo | Notas |
| --- | --- | --- |
| `id` | UUID | PK. |
| `session_id` | UUID | FK a `sessions`. |
| `quote` | text | Frase destacada. |
| `mobility` | text | Detalle de movilidad. |
| `activation` | text | Activación muscular. |
| `raw_text` | text | Texto bruto si aplica. |

## 4. `session_blocks`

| Campo | Tipo | Notas |
| --- | --- | --- |
| `id` | UUID | PK. |
| `session_id` | UUID | FK. |
| `block_order` | integer | Orden dentro de la sesión. |
| `original_block_id` | text | ID/protector del JSON original. |
| `title` | text | Nombre (p.ej. `Benchmark` o `Main`). |
| `type` | text | Categoría del bloque. |
| `is_optional` | boolean | Si se puede omitir. |
| `content_mode` | text | `exercise_notes` / `prescription`. |
| `raw_text` | text | Texto completo del bloque. |
| `coach_notes` | text | Notas adicionales del coach. |
| `has_external_reference` | boolean | Cliente tiene que visitar TrueCoach u otro lugar. |
| `external_reference_text` | text | Texto donde se cita esa fuente. |
| `parsed_confidence` | real | Cuánto confía el parser en la explicación. |

## 5. `block_exercises_raw`

| Campo | Tipo | Notas |
| --- | --- | --- |
| `id` | UUID | PK. |
| `block_id` | UUID | FK. |
| `name` | text | Nombre tal cual. |
| `format` | text | Formato (EMOM, AMRAP...). |
| `notes` | text | Notas específicas. |
| `raw_payload` | jsonb | Ejercicio JSON completo. |

## 6. `block_items_canonical`

| Campo | Tipo | Notas |
| --- | --- | --- |
| `id` | UUID | PK. |
| `block_id` | UUID | FK. |
| `movement_name` | text | Nombre del movimiento extraído. |
| `movement_family` | text | Categoría (peso libre, gimnasta...). |
| `pattern_primary` | text | Patrón principal (p. ej. `push`, `pull`). |
| `pattern_secondary` | text | Patrón secundario si hay. |
| `modality` | text | Cardio / fuerza / gimnasta / mixed. |
| `sets` | integer | Sets declarados. |
| `reps` | text | Reps aparentes. |
| `intensity_type` | text | RPE, peso, duración... |
| `intensity_value_json` | jsonb | Objeto flexible que almacena intensidad quantizada. |
| `execution_notes` | text | Observaciones útiles para el coach/atleta. |
| `raw_origin_text` | text | Texto original usado para esta interpretación. |

Aunque hoy no usemos todos los campos, se deja el esquema listo para análisis, nutrición o recomendaciones futuras. Todas las relaciones están configuradas para preservar trazabilidad hacia el JSON fuente.
