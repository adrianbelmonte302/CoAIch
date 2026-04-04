#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

chmod +x "${SCRIPT_DIR}/deploy_app.sh" || true
chmod +x "${SCRIPT_DIR}/deploy_backend.sh" || true
chmod +x "${SCRIPT_DIR}/deploy_web.sh" || true
chmod +x "${SCRIPT_DIR}/prepare_setup.sh" || true
chmod +x "${SCRIPT_DIR}/setup_vps.sh" || true
chmod +x "${SCRIPT_DIR}/fix_dependencies.sh" || true
chmod +x "${SCRIPT_DIR}/install_node.sh" || true
chmod +x "${SCRIPT_DIR}/stop_app.sh" || true
chmod +x "${SCRIPT_DIR}/uninstall_vps.sh" || true
chmod +x "${SCRIPT_DIR}/check_system.sh" || true
chmod +x "${SCRIPT_DIR}/make_executable.sh" || true
chmod +x "${SCRIPT_DIR}/db_manage.sh" || true
chmod +x "${SCRIPT_DIR}/../backend/scripts/export_program_days.py" || true

echo "Permisos de ejecucion aplicados en scripts/"
