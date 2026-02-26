#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${1:-$HOME/maisu_repo}"
RUNTIME_DIR="${2:-$HOME/maisu}"

echo "[deploy] repo=$REPO_DIR runtime=$RUNTIME_DIR"

if [[ ! -d "$REPO_DIR/.git" ]]; then
  echo "[deploy][error] $REPO_DIR is not a git repository"
  exit 1
fi
if [[ ! -d "$RUNTIME_DIR" ]]; then
  echo "[deploy][error] runtime dir not found: $RUNTIME_DIR"
  exit 1
fi

# 1) Update repo
cd "$REPO_DIR"
git pull --rebase

# 2) Sync repo -> runtime (preserve runtime secrets/venvs)
rsync -av --delete \
  --exclude '.git/' \
  --exclude '.env' \
  --exclude '.venv/' \
  --exclude '__pycache__/' \
  "$REPO_DIR/" "$RUNTIME_DIR/"

# 3) Restart services (manual uvicorn lanes)
pkill -f "uvicorn app:app --host 0.0.0.0 --port 8000" || true
pkill -f "uvicorn app:app --host 0.0.0.0 --port 8001" || true

nohup bash -lc "cd '$RUNTIME_DIR/code/integrations_service' && source .venv/bin/activate && uvicorn app:app --host 0.0.0.0 --port 8000" > "$RUNTIME_DIR/code/integrations_service/runtime.log" 2>&1 &
nohup bash -lc "cd '$RUNTIME_DIR/code/llm_service' && source .venv/bin/activate && uvicorn app:app --host 0.0.0.0 --port 8001" > "$RUNTIME_DIR/code/llm_service/runtime.log" 2>&1 &

sleep 4

# 4) Health checks
curl -sf http://127.0.0.1:8000/docs >/dev/null && echo "[deploy] OK integrations :8000" || {
  echo "[deploy][fail] integrations :8000"
  tail -n 80 "$RUNTIME_DIR/code/integrations_service/runtime.log" || true
  exit 1
}

curl -sf http://127.0.0.1:8001/docs >/dev/null && echo "[deploy] OK llm :8001" || {
  echo "[deploy][fail] llm :8001"
  tail -n 80 "$RUNTIME_DIR/code/llm_service/runtime.log" || true
  exit 1
}

echo "[deploy] SUCCESS"
