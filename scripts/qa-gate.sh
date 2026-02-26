#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_URL="${QA_BASE_URL:-http://127.0.0.1:8000}"
PYTEST_CMD="${PYTEST_CMD:-./.venv/bin/pytest -q}"

echo "[qa-gate] backend tests"
(
  cd "$ROOT_DIR/backend"
  PYTHONPATH=. bash -lc "$PYTEST_CMD"
)

echo "[qa-gate] smoke baseline"
SMOKE_BASE_URL="$BASE_URL" "$ROOT_DIR/scripts/smoke.sh"

echo "[qa-gate] smoke onboarding"
SMOKE_BASE_URL="$BASE_URL" SMOKE_ONBOARDING=1 "$ROOT_DIR/scripts/smoke.sh"

echo "QA_GATE_PASS"
