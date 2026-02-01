# Status: builder

State: COMPLETE
Started: 2026-02-01T07:20:02-08:00
Completed: 2026-02-01T07:33:25-08:00

## Inputs
- PRD: docs/prd/PRD_BUILDER.md
- Tasks: RALPH/TASKS_BUILDER.md

## Outputs
- services/builder/run.sh (entry point)
- services/builder/prompts/system.txt (system prompt)
- services/builder/templates/tool_template.py
- services/builder/templates/smoke_test_template.sh
- services/builder/requests/prd_template.yaml
- services/builder/status/TASKS.md, STATUS.md
- services/builder/tests/ (test scripts)

## What It Does
Builder is a Claude Code agent that creates tools from PRDs:
1. Reads PRD from `requests/current_prd.yaml`
2. Generates Python tool following the tool contract (function name, `run` alias, dict return)
3. Runs smoke tests before committing
4. Commits to git (YOLO mode - no permissions prompts)
5. Registers tool in Redis at `tools:{name}`
6. Can spawn RALPH loops for complex multi-file tools

## Key Decisions
- Safe default YAML when no PRD present (status: none)
- Tool contract: dict return with `result`, `success`, `error` keys
- Max 3 retry attempts for test failures before BUILD_FAILED
- Builder does NOT push (Orchestrator handles push)

## Blockers
None
