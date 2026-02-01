# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fullsend is an autonomous GTM (Go-To-Market) agent that generates ideas, builds its own tools, runs outreach, and learns from results. The system runs continuously, compounding knowledge over time. See [VISION.md](./VISION.md) for the full concept and the core loop: generate ideas → build tools → execute → learn → repeat.

## Common Commands

```bash
# Install dependencies (uses uv package manager)
uv sync

# Run tests
uv run pytest

# Run a single test file
uv run pytest services/watcher/tests/test_classifier.py

# Run tests with verbose output
uv run pytest -v services/orchestrator/tests/

# Lint
uv run ruff check .

# Run Discord service
ENV=discord uv run python -m services.discord.main
ENV=web uv run python -m services.discord.main    # web dashboard only
ENV=both uv run python -m services.discord.main   # both

# Run Watcher service
uv run python -m services.watcher.main

# Run Roundtable (multi-agent ideation)
./run_roundtable.sh "Topic: What GTM channels should we try next?"
# Or manually:
python -m services.roundtable "Your topic here"

# Register tools in Redis
python -m tools.register browserbase
python -m tools.register --all
```

## Architecture

### Service Communication Pattern
All services communicate via Redis pub/sub. The channel naming convention is `fullsend:{channel_name}`:
- `fullsend:discord_raw` - Discord publishes raw messages here (Watcher subscribes)
- `fullsend:from_orchestrator` - Orchestrator/Watcher publish responses (Discord subscribes)
- `fullsend:to_orchestrator` - Escalations from Watcher to Orchestrator
- `fullsend:experiment_results` - Executor publishes completion/failure notifications

### Core Services

**Orchestrator** (`services/orchestrator/`) - The "brain" that makes strategic decisions using Claude with extended thinking. Receives escalations, maintains context, dispatches work.

**Watcher** (`services/watcher/`) - Filters Discord noise using Gemini Flash. Classifies messages as ignore/answer/escalate. Handles simple queries directly, escalates complex ones to Orchestrator.

**Executor** (`services/executor/`) - Runs experiments by loading and executing tools. Handles scheduling, metrics, retries, and failure reporting.

**Discord** (`services/discord/`) - Communication interface with Discord bot and web dashboard. Uses adapter pattern (`adapters/discord_adapter.py`, `adapters/web_adapter.py`) with shared message router.

**Roundtable** (`services/roundtable/`) - Multi-agent ideation where ARTIST, BUSINESS, and TECH personas discuss topics via shared transcript.

**Builder** (`services/builder/`) - Creates new tools when needed. Uses templates from `services/builder/templates/`.

**Redis Agent** (`services/redis_agent/`) - Monitors Redis health, analyzes patterns, sends alerts.

### Tool System
Tools live in `tools/` and are registered in Redis via `tools/register.py`. The Executor dynamically loads tools by name from the `tools/` directory. Each tool must export a function matching its name or a `run` alias.

### Context Flow
1. Discord receives message → publishes to Watcher
2. Watcher classifies (ignore/answer/escalate)
3. If escalated → Orchestrator decides action using extended thinking
4. Orchestrator may dispatch to Executor or Builder
5. Results flow back through Redis to Discord

## Code Conventions

- Python 3.11+, async/await throughout
- Pydantic for settings and data models
- Each service has its own `config.py` with Settings class
- Tests use pytest-asyncio with `asyncio_mode = "auto"`
- Line length 100, ruff for linting

## Environment Variables

Copy `.env.example` to `.env`. Key variables:
- `DISCORD_TOKEN`, `DISCORD_GUILD_ID` - Discord bot credentials
- `REDIS_URL` - Redis connection (default: `redis://localhost:6379`)
- `ANTHROPIC_API_KEY` - For Orchestrator's Claude calls
- `GOOGLE_API_KEY` - For Watcher's Gemini Flash calls
- `BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID` - For web scraping tool

## Workspace Structure

This is a uv workspace with two package members:
- `services/discord` (fullsend-discord)
- `services/watcher` (fullsend-watcher)

Other services (`roundtable`, `redis`, `orchestrator`, `executor`) run under root dependencies.
