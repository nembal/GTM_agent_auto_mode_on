# Status: fullsend

State: COMPLETE
Started: 2026-02-01T03:14:29-08:00
Completed: 2026-02-01T04:06:12-08:00

## Inputs
- PRD: docs/prd/PRD_FULLSEND.md
- Tasks: RALPH/TASKS_FULLSEND.md

## Outputs
- services/fullsend/run.sh (entry point)
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
FULLSEND **IS** Claude Code - it reads experiment requests and generates complete experiment specs.

**Flow:**
1. Read request from `requests/current.md`
2. Design experiment with real templates (no placeholders)
3. Output YAML spec to `experiments/`
4. Publish to Redis: experiment, schedule, metrics spec
5. Request tools from Builder if needed
6. Spawn RALPH loops for complex multi-step tasks

## Redis Integration
- `fullsend:experiments` - Publish new experiments
- `fullsend:schedules` - Publish schedules to Executor
- `fullsend:builder_requests` - Request tools from Builder
- `fullsend:to_orchestrator` - Status updates
- `metrics_specs:{id}` - Store metrics specs for Redis Agent

## Key Decisions
- HTML comment stripping for request detection
- YAML spec format with validation rules
- RALPH spawner for multi-step builds (unique work IDs)

## Blockers
None
