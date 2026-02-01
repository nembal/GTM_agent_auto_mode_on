# Redis Agent

LangChain agent that talks to **Redis at localhost:6379** via the official [redis-mcp-server](https://github.com/redis/mcp-redis) (MCP). Used by the Fullsend GTM orchestrator to store and retrieve learnings, hypotheses, and context.

## Requirements

- Python 3.11+
- Redis running at `localhost:6379` (e.g. `brew services start redis`)
- **uv** on PATH (to run redis-mcp-server), or install `redis-mcp-server` with pip and set `REDIS_MCP_USE_UV=0`

## Install

```bash
pip install langchain-mcp-adapters redis-mcp-server python-dotenv langchain-openai langgraph weave
```

Or from repo root with uv: `uv sync` (if deps are in pyproject.toml) or add the above to your environment.

## Environment

Create `.env` in repo root or in `services/`:

- `REDIS_URL` — default `redis://localhost:6379/0`
- `WANDB_KEY` or `OPENAI_API_KEY` — for the LLM (W&B Inference)
- `OPENAI_API_BASE` — optional, default W&B Inference URL
- `OPENAI_MODEL` — optional
- `REDIS_MCP_USE_UV` — `1` (default) to use `uv run redis-mcp-server`, `0` to use system `redis-mcp-server`

## Run

From repo root:

```bash
uv run python services/redis_agent.py
```

Or from `services/`:

```bash
cd services
python redis_agent.py
```

Type natural-language requests; the agent uses Redis MCP tools (strings, hashes, lists, sets, streams, JSON) to read/write. Type `quit` or `q` to exit.

## Cursor / MCP

If you run redis-mcp-server inside Cursor, use the stdio filter to avoid JSON EOF errors — see `docs/redis-mcp-cursor.md` in the main repo.
