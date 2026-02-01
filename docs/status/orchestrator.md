# Status: orchestrator

State: COMPLETE
Started: 2026-02-01T02:48:01-08:00
Completed: 2026-02-01T03:15:39-08:00

## Inputs
- PRD: docs/prd/PRD_ORCHESTRATOR.md
- Tasks: RALPH/TASKS_ORCHESTRATOR.md

## Outputs
- services/orchestrator/__init__.py
- services/orchestrator/main.py (daemon loop)
- services/orchestrator/config.py (Pydantic settings)
- services/orchestrator/agent.py (extended thinking)
- services/orchestrator/context.py (file + Redis context)
- services/orchestrator/dispatcher.py (all actions)
- services/orchestrator/prompts/*.txt
- services/orchestrator/tests/ (104 tests)
- context/product_context.md, worklist.md, learnings.md

## What It Does
Orchestrator is the strategic brain (Claude Opus 4 with extended thinking).

**Subscribes:** `fullsend:to_orchestrator`
**Publishes:** `fullsend:from_orchestrator`, `fullsend:to_fullsend`, `fullsend:builder_tasks`

**Context Sources:**
- Files: product_context.md, worklist.md, learnings.md
- Redis: experiments:*, tools:*, learnings:tactical:*, metrics_aggregated:*

**Actions:**
| Action | What It Does |
|--------|--------------|
| dispatch_to_fullsend | Send experiment request |
| dispatch_to_builder | Send tool PRD |
| respond_to_discord | Reply to user |
| update_worklist | Update priorities |
| record_learning | Append strategic insight |
| kill_experiment | Archive failing experiment |
| initiate_roundtable | Start multi-agent debate |
| no_action | Do nothing |

## Key Decisions
- Extended thinking with configurable budget (default 10k tokens)
- Strict JSON parsing with defaults for invalid actions
- Timeout fallback: "I'm still thinking about this"
- Exponential backoff for Redis reconnection

## Blockers
None
