#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKEND_DIR="${PROJECT_DIR}/backend"
BACKUP_ROOT="${PROJECT_DIR}/backups"

mkdir -p "${BACKUP_ROOT}"

load_env() {
  if [[ -f "${BACKEND_DIR}/.env" ]]; then
    set -a
    # shellcheck disable=SC1091
    source "${BACKEND_DIR}/.env"
    set +a
  fi
}

require_db_url() {
  if [[ -z "${DATABASE_URL:-}" ]]; then
    echo "ERROR: DATABASE_URL no está definido."
    echo "Ejemplo:"
    echo "  export DATABASE_URL='postgresql://user:pass@host:5432/dbname'"
    exit 1
  fi
}

db_type() {
  if [[ "${DATABASE_URL}" == sqlite:* ]]; then
    echo "sqlite"
  else
    echo "postgres"
  fi
}

check_tools() {
  if [[ "$(db_type)" == "postgres" ]]; then
    command -v pg_dump >/dev/null 2>&1 || { echo "ERROR: falta pg_dump"; exit 1; }
    command -v pg_restore >/dev/null 2>&1 || { echo "ERROR: falta pg_restore"; exit 1; }
    command -v psql >/dev/null 2>&1 || { echo "ERROR: falta psql"; exit 1; }
  fi
}

timestamp() {
  date +"%Y%m%d_%H%M%S"
}

do_backup() {
  local ts
  ts="$(timestamp)"
  local backup_dir="${BACKUP_ROOT}/${ts}"
  mkdir -p "${backup_dir}"
  if [[ "$(db_type)" == "sqlite" ]]; then
    local db_path="${DATABASE_URL#sqlite:///}"
    cp "${db_path}" "${backup_dir}/db.sqlite3"
    echo "Backup sqlite creado en ${backup_dir}/db.sqlite3"
  else
    pg_dump --format=custom --no-owner --no-privileges --file "${backup_dir}/db.dump" "${DATABASE_URL}"
    echo "Backup postgres creado en ${backup_dir}/db.dump"
  fi
  echo "${backup_dir}"
}

list_backups() {
  ls -1 "${BACKUP_ROOT}" 2>/dev/null | sort
}

restore_backup() {
  local backups
  backups="$(list_backups)"
  if [[ -z "${backups}" ]]; then
    echo "No hay backups en ${BACKUP_ROOT}"
    return
  fi
  echo "Backups disponibles:"
  nl -w2 -s'. ' <<<"${backups}"
  echo -n "Elige número de backup a restaurar: "
  read -r choice
  local selected
  selected="$(sed -n "${choice}p" <<<"${backups}")"
  if [[ -z "${selected}" ]]; then
    echo "Selección inválida."
    return
  fi
  local backup_dir="${BACKUP_ROOT}/${selected}"
  if [[ "$(db_type)" == "sqlite" ]]; then
    local db_path="${DATABASE_URL#sqlite:///}"
    if [[ ! -f "${backup_dir}/db.sqlite3" ]]; then
      echo "No se encontró ${backup_dir}/db.sqlite3"
      return
    fi
    cp "${backup_dir}/db.sqlite3" "${db_path}"
    echo "SQLite restaurada desde ${backup_dir}/db.sqlite3"
  else
    if [[ ! -f "${backup_dir}/db.dump" ]]; then
      echo "No se encontró ${backup_dir}/db.dump"
      return
    fi
    pg_restore --clean --if-exists --no-owner --dbname="${DATABASE_URL}" "${backup_dir}/db.dump"
    echo "Postgres restaurado desde ${backup_dir}/db.dump"
  fi
}

clean_menu() {
  echo "Selecciona qué limpiar:"
  echo "  1) Sessions legacy (sessions, warmups, blocks, ejercicios)"
  echo "  2) Program days (program_days)"
  echo "  3) Workouts (workout_definitions)"
  echo "  4) Competitions (competitions, competition_workouts, competition_results)"
  echo "  5) Athlete executions (athlete_executions)"
  echo "  6) Raw imports (raw_imports)"
  echo "  7) ALL (todas las tablas)"
  echo "  0) Volver"
  echo -n "Opción: "
  read -r option
  echo "${option}"
}

truncate_tables() {
  local tables=("$@")
  if [[ "$(db_type)" == "sqlite" ]]; then
    echo "SQLite no soporta TRUNCATE. Abortando."
    exit 1
  fi
  local joined
  joined=$(printf "%s," "${tables[@]}")
  joined="${joined%,}"
  psql "${DATABASE_URL}" -c "TRUNCATE ${joined} RESTART IDENTITY CASCADE;"
}

do_clean() {
  local option
  option="$(clean_menu)"
  if [[ "${option}" == "0" ]]; then
    return
  fi

  local tables=()
  case "${option}" in
    1)
      tables=(warmups block_exercises_raw block_items_canonical session_blocks sessions)
      ;;
    2)
      tables=(program_days)
      ;;
    3)
      tables=(workout_definitions)
      ;;
    4)
      tables=(competition_results competition_workouts competitions)
      ;;
    5)
      tables=(athlete_executions)
      ;;
    6)
      tables=(raw_imports)
      ;;
    7)
      tables=(
        warmups block_exercises_raw block_items_canonical session_blocks sessions
        program_days workout_definitions
        competition_results competition_workouts competitions
        athlete_executions raw_imports
      )
      ;;
    *)
      echo "Opción inválida."
      return
      ;;
  esac

  echo "Se va a limpiar: ${tables[*]}"
  echo -n "Confirmar limpieza? (y/N): "
  read -r confirm
  if [[ "${confirm}" != "y" && "${confirm}" != "Y" ]]; then
    echo "Cancelado."
    return
  fi

  echo "Creando backup antes de limpiar..."
  do_backup >/dev/null
  truncate_tables "${tables[@]}"
  echo "Limpieza completada."
}

main_menu() {
  echo "=============================="
  echo "CoAIch DB Manager"
  echo "=============================="
  echo "1) Backup completo"
  echo "2) Restaurar backup"
  echo "3) Limpiar datos"
  echo "0) Salir"
  echo -n "Opción: "
  read -r option
  echo "${option}"
}

main() {
  load_env
  require_db_url
  check_tools

  while true; do
    case "$(main_menu)" in
      1)
        do_backup >/dev/null
        ;;
      2)
        restore_backup
        ;;
      3)
        do_clean
        ;;
      0)
        echo "Bye."
        exit 0
        ;;
      *)
        echo "Opción inválida."
        ;;
    esac
  done
}

main
