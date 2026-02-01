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

# Run Orchestrator service
uv run python -m services.orchestrator.main

# Run Executor service
SCHEDULE_MODE=trigger uv run python -m services.executor.main

# Run Redis Agent service
uv run python -m services.redis_agent.main

# Run FULLSEND Listener (bridges Redis → Claude Code)
uv run python -m services.fullsend.listener

# Run Builder Listener (bridges Redis → Claude Code)
uv run python -m services.builder.listener

# Run ALL services at once
./run_all.sh

# Test e2e wiring
./scripts/test_e2e_wiring.sh subs    # Check Redis subscriptions
./scripts/test_e2e_wiring.sh all     # Run all wiring tests

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
- `fullsend:discord_raw` - Discord publishes raw messages (Watcher subscribes)
- `fullsend:from_orchestrator` - Orchestrator/Watcher publish responses (Discord subscribes)
- `fullsend:to_orchestrator` - Escalations, alerts (Orchestrator subscribes)
- `fullsend:to_fullsend` - Experiment requests (FULLSEND Listener subscribes)
- `fullsend:builder_tasks` - Tool PRDs (Builder Listener subscribes)
- `fullsend:metrics` - Experiment metrics (Redis Agent subscribes)
- `fullsend:experiment_results` - Executor publishes completion/failure
- `fullsend:execute_now` - Trigger experiment execution (Executor subscribes)
- `fullsend:schedules` - Schedule updates (Executor subscribes)

### Core Services (Python Daemons)

**Discord** (`services/discord/`) - Communication interface with Discord bot and web dashboard. Uses adapter pattern with shared message router.

**Watcher** (`services/watcher/`) - Filters Discord noise using Gemini Flash. Classifies messages as ignore/answer/escalate.

**Orchestrator** (`services/orchestrator/`) - The "brain" that makes strategic decisions using Claude with extended thinking. Dispatches to FULLSEND, Builder, or responds directly.

**Executor** (`services/executor/`) - Runs experiments by loading and executing tools. Three modes: trigger, cron, speedrun.

**Redis Agent** (`services/redis_agent/`) - Monitors metrics, checks thresholds, sends alerts.

**FULLSEND Listener** (`services/fullsend/listener.py`) - Bridges Redis → Claude Code. Subscribes to `to_fullsend`, spawns Claude Code to design experiments.

**Builder Listener** (`services/builder/listener.py`) - Bridges Redis → Claude Code. Subscribes to `builder_tasks`, spawns Claude Code to build tools.

### Claude Code Agents (Shell Scripts)

**FULLSEND** (`services/fullsend/run.sh`) - Claude Code agent that designs experiments. Reads `requests/current.md`, outputs YAML specs, publishes to Redis.

**Builder** (`services/builder/run.sh`) - Claude Code agent that builds tools. Reads `requests/current_prd.yaml`, creates Python tools, registers in Redis.

**Roundtable** (`services/roundtable/`) - Multi-agent ideation with ARTIST, BUSINESS, and TECH personas.

### Tool System
Tools live in `tools/` and are registered in Redis via `tools/register.py`. The Executor dynamically loads tools by name from the `tools/` directory.

### End-to-End Flow
1. Discord receives message → publishes to `fullsend:discord_raw`
2. Watcher classifies → escalates to `fullsend:to_orchestrator`
3. Orchestrator decides → dispatches to `fullsend:to_fullsend`
4. FULLSEND Listener → writes file → spawns Claude Code
5. Claude Code designs experiment → publishes to Redis
6. Executor runs → publishes metrics to `fullsend:metrics`
7. Redis Agent monitors → alerts Orchestrator on success/failure
8. Loop continues

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
