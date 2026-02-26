#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${1:-$HOME/maisu_repo}"
RUNTIME_DIR="${2:-$HOME/maisu}"

INTEGRATIONS_PATH="code/integrations_service"
LLM_PATH="code/llm_service"

log() { echo "[deploy] $*"; }
fail() { echo "[deploy][error] $*"; exit 1; }

require_dir() {
  local d="$1"
  [[ -d "$d" ]] || fail "Directory not found: $d"
}

check_layout_or_fail() {
  local missing=()
  [[ -d "$REPO_DIR/$INTEGRATIONS_PATH" ]] || missing+=("$INTEGRATIONS_PATH")
  [[ -d "$REPO_DIR/$LLM_PATH" ]] || missing+=("$LLM_PATH")

  if (( ${#missing[@]} > 0 )); then
    echo "[deploy][error] Unsupported repository layout in: $REPO_DIR"
    echo "[deploy][error] Required for 2-service deploy:"
    echo "  - $INTEGRATIONS_PATH (port 8000)"
    echo "  - $LLM_PATH (port 8001)"
    echo "[deploy][error] Missing: ${missing[*]}"
    echo "[deploy][error] Action: verify branch/layout or use the deploy flow matching your repo structure."
    exit 1
  fi

  log "Detected 2-service layout ($INTEGRATIONS_PATH, $LLM_PATH)."
}

sync_repo_to_runtime() {
  log "Syncing repo -> runtime (preserving .env/.venv in runtime)"
  rsync -av --delete \
    --exclude '.git/' \
    --exclude '.env' \
    --exclude '**/.env' \
    --exclude '.venv/' \
    --exclude '**/.venv/' \
    --exclude '__pycache__/' \
    --exclude '**/__pycache__/' \
    "$REPO_DIR/" "$RUNTIME_DIR/"
}

restart_service() {
  local name="$1"
  local service_dir="$2"
  local port="$3"
  local log_file="$service_dir/runtime.log"
  local app_ref="app:app"

  if [[ ! -x "$service_dir/.venv/bin/uvicorn" ]]; then
    fail "$name missing venv uvicorn: $service_dir/.venv/bin/uvicorn"
  fi

  pkill -f "uvicorn $app_ref --host 0.0.0.0 --port $port" || true

  nohup bash -lc "cd '$service_dir' && source .venv/bin/activate && exec uvicorn $app_ref --host 0.0.0.0 --port $port" > "$log_file" 2>&1 &
  log "Restarted $name on :$port (log: $log_file)"
}

health_check() {
  local name="$1"
  local port="$2"
  local log_file="$3"
  local url="http://127.0.0.1:$port/docs"

  for _ in {1..15}; do
    if curl -sf "$url" >/dev/null; then
      log "OK $name :$port"
      return 0
    fi
    sleep 1
  done

  echo "[deploy][fail] Health check failed for $name :$port ($url)"
  echo "[deploy][fail] Last logs from $log_file:"
  tail -n 80 "$log_file" || true
  return 1
}

log "repo=$REPO_DIR runtime=$RUNTIME_DIR"

[[ -d "$REPO_DIR/.git" ]] || fail "$REPO_DIR is not a git repository"
require_dir "$RUNTIME_DIR"

check_layout_or_fail

cd "$REPO_DIR"
log "Updating repository"
git pull --rebase

sync_repo_to_runtime

INTEGRATIONS_RUNTIME="$RUNTIME_DIR/$INTEGRATIONS_PATH"
LLM_RUNTIME="$RUNTIME_DIR/$LLM_PATH"
require_dir "$INTEGRATIONS_RUNTIME"
require_dir "$LLM_RUNTIME"

restart_service "integrations_service" "$INTEGRATIONS_RUNTIME" "8000"
restart_service "llm_service" "$LLM_RUNTIME" "8001"

health_check "integrations_service" "8000" "$INTEGRATIONS_RUNTIME/runtime.log" || exit 1
health_check "llm_service" "8001" "$LLM_RUNTIME/runtime.log" || exit 1

log "SUCCESS"