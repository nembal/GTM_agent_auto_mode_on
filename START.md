# START

This is the practical setup guide for running Fullsend locally.

## What this system is
Fullsend is a multi-service GTM agent. It is not a single monolith; it is a set of
Python services that communicate through Redis (pub/sub + keys). The system is
designed to design experiments, build tools, run them, and learn from results.

At the moment, there is no "active GTM campaign" hard-coded in the repo. Live work
comes from:
- Discord messages (ideas, commands, questions)
- Orchestrator requests written to `services/fullsend/requests/current.md`
- Context docs in `context/` (product, worklist, learnings)

## Where to edit "what it is working on"

### Product Context (Start Here!)
Edit `context/product_context.md` to define:
- **What you're selling** — product/service description
- **Target audience** — ideal customer profile, buyer personas
- **Value proposition** — the core problem you solve
- **Key differentiators** — what makes you different
- **GTM implications** — channels, messaging angles, high-signal targets

This is the seed for all GTM experiments. The richer the context, the better the ideas.

### Other Context Files
- `context/worklist.md` — prioritized work items (Orchestrator-managed)
- `context/learnings.md` — accumulated strategic insights (Orchestrator-managed)
- `services/fullsend/requests/current.md` — current experiment request

### Behavioral Prompts
- `services/orchestrator/prompts/` — decision-making style
- `services/watcher/prompts/` — classification and response
- `services/redis_agent/prompts/` — summaries and analysis

## Documentation
- `SYSTEM_COMPONENTS.md` — complete component guide with Redis wiring
- `VISION.md` — the core concept and architecture
- `CLAUDE.md` — commands and conventions for this repo
- `docs/status/` — status files for each component

## Prereqs
- Python 3.11+
- uv package manager
- Docker (for Redis)
- Discord bot token + guild id

Install uv (once):
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install dependencies:
```
uv sync --dev
```

## Redis (Docker)
Start Redis:
```
docker run --name fullsend-redis -p 6379:6379 -d redis:7
```

Verify:
```
docker exec -it fullsend-redis redis-cli ping
```
Expected: `PONG`

Stop:
```
docker stop fullsend-redis
```

Remove container (optional):
```
docker rm fullsend-redis
```

## Discord setup
1) Copy env template:
```
cp .env.example .env
```

2) Edit `.env`:
- `DISCORD_TOKEN`
- `DISCORD_GUILD_ID`
- `LISTENING_CHANNELS` (comma-separated names)
- `STATUS_CHANNEL`
- `REDIS_URL` (default: `redis://localhost:6379`)

## Run services (local)
Open separate terminals for each service.

Discord bot + web dashboard:
```
ENV=both uv run python -m services.discord.main
```
Web dashboard: `http://localhost:8000`

Watcher (classifies Discord messages):
```
uv run python -m services.watcher.main
```

Orchestrator (strategic decisions):
```
uv run python -m services.orchestrator.main
```

Executor (runs experiments):
```
SCHEDULE_MODE=trigger uv run python -m services.executor.main
```

Redis Agent (metrics + summaries):
```
uv run python -m services.redis_agent.main
```

FULLSEND Listener (bridges Redis → Claude Code):
```
uv run python -m services.fullsend.listener
```

Builder Listener (bridges Redis → Claude Code):
```
uv run python -m services.builder.listener
```

## One-command launch (script)
Use the launcher to start all core services (including listeners and dashboard).
```
chmod +x ./run_all.sh
./run_all.sh
```

This starts:
- Discord bot + web dashboard
- Watcher, Orchestrator, Executor, Redis Agent
- FULLSEND Listener, Builder Listener
- **Real-time Dashboard** at http://127.0.0.1:8050/

Optional extras:
```
SCHEDULE_MODE=cron ./run_all.sh    # Run with cron scheduling
WEAVE_DISABLED=1 ./run_all.sh      # Disable Weave tracing
```

**Note:** Roundtable ideation is now triggered automatically by the Orchestrator when it needs fresh ideas (via `initiate_roundtable` action). You can also trigger it manually via Redis:
```
redis-cli PUBLISH fullsend:to_orchestrator '{"type":"roundtable_request","prompt":"What GTM channels should we try?"}'
```

## Real-time Dashboard
The dashboard shows live system activity:
- **Service status** — which services are active (green pulse)
- **Message flow** — real-time events across all Redis channels
- **Auto-refresh** — updates every 2 seconds

Open http://127.0.0.1:8050/ after starting services.

To run dashboard standalone:
```
uv run python demo/dashboard/dashboard_api.py
```

## What happens when everything is live
1) Discord receives a message and publishes it to Redis (`fullsend:discord_raw`).
2) Watcher reads that channel, classifies the message, and either answers or escalates.
3) Escalations go to Orchestrator (`fullsend:to_orchestrator`).
4) Orchestrator decides next steps:
   - Simple response → publishes to `fullsend:from_orchestrator` → Discord posts it
   - New experiment → publishes to `fullsend:to_fullsend` → FULLSEND Listener picks up
   - Need tool → publishes to `fullsend:builder_tasks` → Builder Listener picks up
5) FULLSEND Listener spawns Claude Code to design experiments, publishes specs to Redis.
6) Builder Listener spawns Claude Code to build tools, registers in Redis.
7) Executor runs experiments and writes metrics to `fullsend:metrics`.
8) Redis Agent monitors metrics, sends alerts to Orchestrator on success/failure.
9) On failure, Orchestrator can dispatch fix requests back to FULLSEND.

## Quick live smoke test
1) Start Redis (`brew services start redis` or Docker)
2) Run `./run_all.sh`
3) Open dashboard: http://127.0.0.1:8050/
4) Test wiring: `./scripts/test_e2e_wiring.sh subs` (verify all channels have subscribers)
5) Send test messages: `./scripts/test_e2e_wiring.sh all`
6) Watch dashboard light up as messages flow
7) Check logs: `tail -f .logs/*.log`

## Full Discord test (Seed Stage)
1) Edit `context/product_context.md` with your product
2) Start all services with `./run_all.sh`
3) Open dashboard: http://127.0.0.1:8050/
4) Send a Discord message with a GTM idea (e.g., "Let's try cold emailing CTOs who attended AI conferences")
5) Watch the dashboard as it flows:
   - Discord (green) → Watcher (green) → Orchestrator (green)
   - If experiment requested: → FULLSEND (green) → Builder (green) → Executor (green)
6) Verify experiment spec created and published to Redis

## Reset / Fresh Start

To reset Fullsend to a clean slate (e.g., to run with a different product):

```bash
./restart.sh          # Interactive reset
./restart.sh --force  # No prompts
./restart.sh --soft   # Keep product context, reset everything else
```

**What gets reset:**
- `context/*.md` → Reset to templates
- `tools/*.py` → Keep only core tools (browserbase.py, register.py)
- All experiments and tool requests
- Redis `fullsend:*` keys
- All logs

**What is preserved:**
- Core tools (browserbase.py, register.py)
- Example experiments in `examples/`
- Prompts and templates
- Configuration (.env)

After reset:
1. Edit `context/product_context.md` with your new product
2. Run `./run_all.sh` to start fresh

## Tests
```
uv run pytest
```
