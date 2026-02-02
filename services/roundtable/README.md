# Roundtable

ARTIST, BUSINESS, and TECH agents communicate over a shared transcript to generate GTM ideas. Same LLM (W&B Inference), different prompts per persona.

## Integration with Orchestrator

Roundtable is now integrated into the autonomous loop. The Orchestrator can trigger it via the `initiate_roundtable` action when:
- The worklist is empty and it needs fresh ideas
- Current experiments are stalling
- A user asks "what should we try next?"

The Orchestrator runs Roundtable as a subprocess, receives the transcript and summary, then can dispatch experiments based on the generated ideas.

## Manual Trigger

To trigger Roundtable via Redis (which the Orchestrator will pick up):

```bash
redis-cli PUBLISH fullsend:to_orchestrator '{"type":"roundtable_request","prompt":"What GTM channels should we try?"}'
```

## Standalone Run (testing/development)

```bash
# Using uv (project standard):
uv run python -m services.roundtable "Topic: What GTM channels should we try next?"

# With JSON input:
echo '{"prompt": "How can we reach AI CTOs?", "context": "We sell agent building services"}' | uv run python -m services.roundtable
```

## Environment Variables

- `ROUNDTABLE_MAX_ROUNDS` — default `3` (each persona speaks once per round)
- `OPENAI_API_BASE` — default `https://api.inference.wandb.ai/v1`
- `OPENAI_MODEL` — default `openai/gpt-oss-120b`
- `WANDB_KEY` or `OPENAI_API_KEY` — required for LLM calls

## Layout

- `llm.py` — `get_llm()` (W&B only)
- `personas.py` — System prompts for ARTIST, BUSINESS, TECH, SUMMARIZER
- `runner.py` — Loop: build messages, call LLM per speaker, append to transcript
- `__main__.py` — CLI entrypoint (accepts JSON stdin or plain text argument)

## Output Format

```json
{
  "transcript": "--- Round 1 ---\nARTIST: ...\nBUSINESS: ...\nTECH: ...",
  "summary": ["Task 1 (Owner: FULLSEND)", "Task 2 (Owner: Builder)", ...]
}
```

The summary contains 3-5 actionable tasks with owners, ready for the Orchestrator to dispatch.
