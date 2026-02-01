# Status: watcher

State: COMPLETE
Started: 2026-02-01T02:23:56-08:00
Completed: 2026-02-01T02:48:14-08:00

## Inputs
- PRD: docs/prd/PRD_WATCHER.md
- Tasks: RALPH/TASKS_WATCHER.md

## Outputs
- services/watcher/__init__.py
- services/watcher/main.py (daemon loop)
- services/watcher/config.py (Pydantic settings)
- services/watcher/classifier.py (Gemini classification)
- services/watcher/responder.py (simple query answers)
- services/watcher/escalator.py (typed payloads)
- services/watcher/retry.py (exponential backoff)
- services/watcher/prompts/classify.txt, respond.txt
- services/watcher/tests/ (70 tests)

## What It Does
Watcher filters Discord messages using Gemini 2.0 Flash.

**Subscribes:** `fullsend:discord_raw`
**Publishes:** `fullsend:to_orchestrator` (escalations), `fullsend:from_orchestrator` (simple responses)

**Classification Actions:**
| Action | What Happens |
|--------|--------------|
| ignore | Off-topic, no action |
| answer | Simple query, respond from Redis state |
| escalate | Important, forward to Orchestrator |

**Answerable Queries (reads Redis):**
- `fullsend:status` - System status
- `experiments:*` - Count active experiments
- `fullsend:recent_runs` - Recent activity

## Key Decisions
- Gemini 2.0 Flash (not Haiku as PRD acceptance criteria incorrectly stated)
- Retry with exponential backoff (1s → 2s → 4s, max 10s)
- Failed classification after retries → escalate with error details
- Watcher is read-only for Redis keys

## Blockers
None
