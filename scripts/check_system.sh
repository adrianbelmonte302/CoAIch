#!/usr/bin/env bash
set -euo pipefail

SERVICE="coai-ch-backend"
API_BASE="${API_BASE:-http://127.0.0.1:8000}"
WEB_ROOT="${WEB_ROOT:-/var/www/html}"

RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
NC="\033[0m"

ok() { echo -e "${GREEN}OK${NC} $*"; }
warn() { echo -e "${YELLOW}WARN${NC} $*"; }
fail() { echo -e "${RED}FAIL${NC} $*"; }

echo "=== CoAIch System Check ==="

if systemctl is-active --quiet "${SERVICE}"; then
  ok "Backend service '${SERVICE}' activo"
else
  fail "Backend service '${SERVICE}' NO activo"
fi

if systemctl is-active --quiet nginx; then
  ok "nginx activo"
else
  warn "nginx NO activo"
fi

if [[ -f "${WEB_ROOT}/index.html" ]]; then
  ok "Web root tiene index.html"
else
  warn "No se encontro ${WEB_ROOT}/index.html"
fi

if rg -n "localhost:8000" "${WEB_ROOT}/static/js" >/dev/null 2>&1; then
  warn "Build web contiene 'localhost:8000' (build viejo)"
else
  ok "Build web no contiene 'localhost:8000'"
fi

echo "--- API checks ---"
status_unauth="$(curl -s -o /dev/null -w "%{http_code}" "${API_BASE}/sessions/")"
if [[ "${status_unauth}" == "401" ]]; then
  ok "GET /sessions/ sin auth devuelve 401 (correcto)"
else
  warn "GET /sessions/ sin auth devuelve ${status_unauth} (esperado 401)"
fi

if [[ -n "${API_CHECK_USER:-}" && -n "${API_CHECK_PASS:-}" ]]; then
  auth_status="$(curl -s -o /dev/null -w "%{http_code}" -u "${API_CHECK_USER}:${API_CHECK_PASS}" "${API_BASE}/sessions/")"
  if [[ "${auth_status}" == "200" ]]; then
    ok "GET /sessions/ con auth devuelve 200"
  else
    warn "GET /sessions/ con auth devuelve ${auth_status} (esperado 200)"
  fi

  login_status="$(curl -s -o /dev/null -w "%{http_code}" -X POST "${API_BASE}/auth/login" -H "Content-Type: application/json" -d "{\"username\":\"${API_CHECK_USER}\",\"password\":\"${API_CHECK_PASS}\"}")"
  if [[ "${login_status}" == "200" ]]; then
    ok "POST /auth/login devuelve 200"
  else
    warn "POST /auth/login devuelve ${login_status} (esperado 200)"
  fi
else
  warn "API_CHECK_USER/PASS no definidos; se omiten checks autenticados"
fi

echo "=== Fin del chequeo ==="
