# Status: builder

State: COMPLETE
Started: 2026-02-01T07:20:02-08:00
Completed: 2026-02-01T11:45:00-08:00

## Inputs
- PRD: docs/prd/PRD_BUILDER.md
- Tasks: RALPH/TASKS_BUILDER.md

## Outputs
- services/builder/run.sh (Claude Code entry point)
- services/builder/listener.py (Redis listener daemon) **NEW**
- services/builder/__init__.py, __main__.py (module support) **NEW**
- services/builder/prompts/system.txt (system prompt)
- services/builder/templates/tool_template.py
- services/builder/templates/smoke_test_template.sh
- services/builder/requests/prd_template.yaml
- services/builder/status/TASKS.md, STATUS.md
- services/builder/tests/ (test scripts)

## What It Does
Builder has two components:

### 1. Listener Daemon (`listener.py`)
Python daemon that bridges Redis → Claude Code:
- Subscribes to `fullsend:builder_tasks`
- Writes incoming PRDs to `requests/current_prd.yaml`
- Spawns `run.sh` to build the tool
- Reports completion/failure back to Orchestrator and `fullsend:builder_results`

**Run:** `uv run python -m services.builder.listener`

### 2. Claude Code Agent (`run.sh`)
The actual tool builder:
1. Reads PRD from `requests/current_prd.yaml`
2. Generates Python tool following the tool contract (function name, `run` alias, dict return)
3. Runs smoke tests before committing
4. Commits to git (YOLO mode - no permissions prompts)
5. Registers tool in Redis at `tools:{name}`
6. Can spawn RALPH loops for complex multi-file tools

## Redis Integration

**Subscribes to:**
- `fullsend:builder_tasks` - Receives tool PRDs from Orchestrator/FULLSEND

**Publishes to:**
- `fullsend:builder_results` - Tool build results (tool_built, tool_build_failed)
- `fullsend:to_orchestrator` - Status updates (started, completed, failed)
- `tools:{name}` - Registers completed tools

## Key Decisions
- Listener daemon bridges Redis pub/sub → file-based Claude Code
- Safe default YAML when no PRD present (status: none)
- Tool contract: dict return with `result`, `success`, `error` keys
- Max 3 retry attempts for test failures before BUILD_FAILED
- Builder does NOT push (Orchestrator handles push)
- 15-minute default timeout for Claude Code execution

## Blockers
None
