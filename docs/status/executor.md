# Status: executor

State: COMPLETE
Started: 2026-02-01T04:06:05-08:00
Completed: 2026-02-01T04:24:52-08:00

## Inputs
- PRD: docs/prd/PRD_EXECUTOR.md
- Tasks: RALPH/TASKS_EXECUTOR.md

## Outputs
- services/executor/__init__.py
- services/executor/main.py (3 schedule modes)
- services/executor/config.py (Pydantic settings)
- services/executor/loader.py (dynamic tool loading)
- services/executor/runner.py (execution + metrics)
- services/executor/scheduler.py (cron parsing)
- services/executor/metrics.py (timeout/retry logic)
- services/executor/tests/ (64 tests)

## What It Does
Executor runs experiments by loading and executing tools dynamically:

**Schedule Modes:**
- `trigger`: Listens to `fullsend:execute_now` and `fullsend:schedules`
- `cron`: Runs on schedule (checks every 60s)
- `speedrun`: Runs all due experiments immediately

**Execution Flow:**
1. Load tool via `importlib.util` (supports `run` function fallback)
2. Execute with timeout (`asyncio.wait_for`, default 300s)
3. Retry transient errors with exponential backoff
4. Emit metrics to `fullsend:metrics`
5. Save results to `experiment_runs:{id}:{ts}`
6. Publish completion to `fullsend:experiment_results`

## Key Decisions
- Timeout errors NOT retried (tool is too slow)
- Non-transient errors NOT retried (real problem)
- State transitions: ready → running → run/failed

## Blockers
None
