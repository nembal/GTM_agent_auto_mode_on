# Status: roundtable

State: COMPLETE
Started: 2026-02-01T07:29:21-08:00
Completed: 2026-02-01T07:42:27-08:00

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

## Blockers
None - LLM error handling not implemented but noted for future
