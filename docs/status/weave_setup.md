## Weave Setup

### Enable tracing
- Default: tracing is enabled automatically when Weave is installed.
- Disable: set `WEAVE_DISABLED=1`.
- Project override: set `WEAVE_PROJECT` (e.g., `fullsend/orchestrator`).

### Required credentials
Provide one of:
- `WANDB_KEY`
- `OPENAI_API_KEY`

### Where tracing is wired
- LLM calls: Orchestrator, Roundtable, Watcher, Redis Agent analysis
- Tool executions: Executor

### Trace metadata included
- Model name, prompt size, round/role context
- Tool name, experiment/run IDs, param keys

### Local sanity check
Run a service and confirm spans appear:
- `uv run python -m services.orchestrator.main`
- `uv run python -m services.watcher.main`
- `./run_roundtable.sh "Topic: test"`
