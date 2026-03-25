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

---

## 7. `program_days` (nuevo canon calendario)

| Campo | Tipo | Notas |
| --- | --- | --- |
| `id` | UUID | PK. |
| `raw_import_id` | UUID | FK a `raw_imports`. |
| `day_id` | text | Identificador lógico del día (YYYY-MM-DD). |
| `date` | date | Fecha del calendario. |
| `weekday` | text | Día en palabras. |
| `display_title` | text | Título visible para la UI. |
| `is_rest_day` | boolean | Descanso explícito. |
| `day_type` | text | `training`, `rest`, etc. |
| `deload_week` | boolean | Semana de descarga. |
| `program_source` | text | `truecoach`, `legacy_sessions`, etc. |
| `athlete_ref` | text | Identificador de atleta (opcional). |
| `classification` | jsonb | Modalidades, patrones, energy systems. |
| `related_workout_ids` | jsonb | Vínculos a workouts reutilizables. |
| `related_competition_ids` | jsonb | Vínculos a competiciones. |
| `source_integrity` | jsonb | Señales de completitud y confianza. |
| `raw_content` | jsonb | Texto literal de origen. |
| `session_context` | jsonb | Tags, duración, estímulo. |
| `session_flow` | jsonb | Variantes, bloques, sub-bloques, ejercicios. |
| `execution_log` | jsonb | Futuro: ejecución del atleta. |
| `athlete_feedback` | jsonb | Futuro: feedback y dolor. |
| `derived_metrics` | jsonb | Futuro: métricas agregadas. |
| `ai_annotations` | jsonb | Futuro: anotaciones IA. |
| `schema_version` | text | `2.0.0` u otras. |
| `entity_type` | text | `program_day`. |
| `source_hash` | text | Hash del payload completo para dedupe. |

## 8. `workout_definitions`

| Campo | Tipo | Notas |
| --- | --- | --- |
| `id` | UUID | PK. |
| `name` | text | Nombre del benchmark o workout. |
| `slug` | text | Slug normalizado. |
| `description` | text | Descripción libre. |
| `workout_type` | text | `benchmark`, `event`, etc. |
| `source` | text | `crossfit_open`, `wodbuster`, etc. |
| `metadata` | jsonb | Campos futuros. |

## 9. `competitions`

| Campo | Tipo | Notas |
| --- | --- | --- |
| `id` | UUID | PK. |
| `name` | text | Nombre del evento. |
| `season_year` | int | Año o temporada. |
| `organizer` | text | Organizador. |
| `metadata` | jsonb | Campos futuros. |

## 10. `competition_workouts`

| Campo | Tipo | Notas |
| --- | --- | --- |
| `id` | UUID | PK. |
| `competition_id` | UUID | FK a `competitions`. |
| `workout_definition_id` | UUID | FK a `workout_definitions`. |
| `label` | text | Etiqueta del WOD (`Open 26.1`, etc.). |
| `metadata` | jsonb | Campos futuros. |

## 11. `competition_results`

| Campo | Tipo | Notas |
| --- | --- | --- |
| `id` | UUID | PK. |
| `competition_workout_id` | UUID | FK a `competition_workouts`. |
| `athlete_ref` | text | Atleta. |
| `result` | jsonb | Score, time, notes. |
| `created_at` | timestamptz | Timestamp. |

## 12. `athlete_executions`

| Campo | Tipo | Notas |
| --- | --- | --- |
| `id` | UUID | PK. |
| `program_day_id` | UUID | FK a `program_days`. |
| `athlete_ref` | text | Atleta. |
| `data` | jsonb | RPE, pesos, score, notas. |
| `created_at` | timestamptz | Timestamp. |
