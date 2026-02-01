# Status: fullsend

State: COMPLETE
Started: 2026-02-01T03:14:29-08:00
Completed: 2026-02-01T11:45:00-08:00

## Inputs
- PRD: docs/prd/PRD_FULLSEND.md
- Tasks: RALPH/TASKS_FULLSEND.md

## Outputs
- services/fullsend/run.sh (Claude Code entry point)
- services/fullsend/listener.py (Redis listener daemon) **NEW**
- services/fullsend/__init__.py, __main__.py (module support) **NEW**
- services/fullsend/prompts/system.txt
- services/fullsend/requests/current.md
- services/fullsend/experiments/SPEC_FORMAT.md
- services/fullsend/experiments/TOOL_REQUEST_FORMAT.md
- services/fullsend/experiments/examples/*.yaml (3 examples)
- services/fullsend/scripts/redis_publish.sh
- services/fullsend/scripts/REDIS_PUBLISH_GUIDE.md
- services/fullsend/ralph.sh (RALPH loop spawner)
- services/fullsend/tests/test_plan.sh

## What It Does
FULLSEND has two components:

### 1. Listener Daemon (`listener.py`)
Python daemon that bridges Redis → Claude Code:
- Subscribes to `fullsend:to_fullsend`
- Writes incoming requests to `requests/current.md`
- Spawns `run.sh` (or `ralph.sh` for complex tasks)
- Reports completion/failure back to Orchestrator

**Run:** `uv run python -m services.fullsend.listener`

### 2. Claude Code Agent (`run.sh`)
The actual experiment designer:
1. Read request from `requests/current.md`
2. Design experiment with real templates (no placeholders)
3. Output YAML spec to `experiments/`
4. Publish to Redis: experiment, schedule, metrics spec
5. Request tools from Builder if needed
6. Spawn RALPH loops for complex multi-step tasks

## Redis Integration

**Subscribes to:**
- `fullsend:to_fullsend` - Receives experiment requests from Orchestrator

**Publishes to:**
- `fullsend:experiments` - New experiment specs (Executor listens)
- `fullsend:schedules` - Schedules (Executor listens)
- `fullsend:builder_requests` - Tool requests (Builder listens)
- `fullsend:to_orchestrator` - Status updates (started, completed, failed)
- `metrics_specs:{id}` - Store metrics specs for Redis Agent

## Key Decisions
- Listener daemon bridges Redis pub/sub → file-based Claude Code
- HTML comment stripping for request detection
- YAML spec format with validation rules
- RALPH spawner for multi-step builds (unique work IDs)
- 10-minute default timeout for Claude Code execution

## Blockers
None
