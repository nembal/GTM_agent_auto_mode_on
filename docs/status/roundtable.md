# Status: roundtable

State: INTEGRATED
Started: 2026-02-01T07:29:21-08:00
Completed: 2026-02-01T07:42:27-08:00
Updated: 2026-02-01 (Orchestrator integration)

## Inputs
- PRD: docs/prd/PRD_ROUNDTABLE.md
- Tasks: RALPH/TASKS_ROUNDTABLE.md

## Outputs
- services/roundtable/runner.py (debate orchestration)
- services/roundtable/personas.py (loads from files)
- services/roundtable/__main__.py (CLI)
- services/roundtable/run.sh (wrapper)
- services/roundtable/llm.py (W&B Inference)
- services/roundtable/personas/*.txt (4 persona files)
- services/roundtable/test_roundtable.py (28 tests)
- services/roundtable/conftest.py

## What It Does
Roundtable runs a 3-agent debate to generate actionable GTM ideas.

**Personas:**
| Agent | Focus |
|-------|-------|
| ARTIST | Creative, unconventional, metaphors |
| BUSINESS | Revenue, conversion, ROI |
| TECH | Automation, tools, APIs |
| SUMMARIZER | Distills to 3-5 tasks with owners |

**Flow:**
1. Run 3 rounds of debate (each agent responds to transcript)
2. Summarizer extracts tasks with owners (FULLSEND/Builder/Orchestrator)
3. Return `{transcript: str, summary: list[str]}`

**CLI Modes:**
```bash
echo '{"prompt": "..."}' | python -m services.roundtable  # JSON stdin
python -m services.roundtable input.json                   # File arg
./services/roundtable/run.sh "prompt"                      # Wrapper
```

## Key Decisions
- Default 3 rounds (was 2)
- Persona prompts in .txt files (not inline)
- Summary format: `"Task description (Owner: who)"`
- Uses W&B Inference (OpenAI-compatible) not Gemini

## Post-Build Fixes
- Made weave project ID configurable via WEAVE_PROJECT env var
- Added API key validation in llm.py

## Orchestrator Integration (Feb 2026)

Roundtable is now callable by the Orchestrator as part of the autonomous loop:

**How it works:**
1. Orchestrator decides it needs fresh ideas (via `initiate_roundtable` action)
2. Dispatcher runs `uv run python -m services.roundtable` as subprocess
3. Input: JSON with prompt, context, learnings
4. Output: transcript + summary (3-5 tasks with owners)
5. Orchestrator can then dispatch experiments based on ideas

**Trigger points:**
- Worklist empty, no active experiments
- Experiments stalling, need new angles
- User asks "what should we try next?"

**Removed:**
- `run_roundtable.sh` (was using conda, inconsistent with project)
- `ROUNDTABLE_TOPIC` env var in run_all.sh (Orchestrator triggers now)

## Blockers
None - LLM error handling not implemented but noted for future
