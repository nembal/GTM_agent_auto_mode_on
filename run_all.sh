#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

LOG_DIR="${LOG_DIR:-$ROOT_DIR/.logs}"
SCHEDULE_MODE="${SCHEDULE_MODE:-trigger}"
ROUNDTABLE_TOPIC="${ROUNDTABLE_TOPIC:-}"

mkdir -p "$LOG_DIR"

if [[ -f "$ROOT_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.env"
  set +a
fi

function start_service() {
  local name="$1"
  shift
  echo "Starting $name..."
  "$@" >"$LOG_DIR/$name.log" 2>&1 &
  echo "$!" >"$LOG_DIR/$name.pid"
}

function stop_all() {
  echo "Stopping services..."
  for pid_file in "$LOG_DIR"/*.pid; do
    [[ -f "$pid_file" ]] || continue
    pid="$(cat "$pid_file")"
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
    rm -f "$pid_file"
  done
}

trap stop_all EXIT INT TERM

if [[ -z "${WEAVE_DISABLED:-}" && -z "${WANDB_API_KEY:-}" ]]; then
  echo "Note: WANDB_API_KEY not set. Set WEAVE_DISABLED=1 to avoid prompts."
fi

start_service "discord" env ENV=both uv run python -m services.discord.main
start_service "watcher" uv run python -m services.watcher.main
start_service "orchestrator" uv run python -m services.orchestrator.main
start_service "redis_agent" uv run python -m services.redis_agent.main
start_service "executor" env SCHEDULE_MODE="$SCHEDULE_MODE" uv run python -m services.executor.main

# Claude Code agent listeners (bridge Redis -> Claude Code)
start_service "fullsend_listener" uv run python -m services.fullsend.listener
start_service "builder_listener" uv run python -m services.builder.listener

if [[ -n "$ROUNDTABLE_TOPIC" ]]; then
  start_service "roundtable" ./run_roundtable.sh "$ROUNDTABLE_TOPIC"
fi

echo "All services started (including FULLSEND + Builder listeners)."
echo "Logs: $LOG_DIR/*.log"
echo "Press Ctrl+C to stop."

wait
