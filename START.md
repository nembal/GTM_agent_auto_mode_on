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
Start here:
- `context/product_context.md` for product description, target users, value prop
- `context/worklist.md` for prioritized work items
- `context/learnings.md` for accumulated knowledge
- `services/fullsend/requests/current.md` for the current Orchestrator request

Behavioral prompts:
- `services/orchestrator/prompts/` for decision-making style
- `services/watcher/prompts/` for classification and response
- `services/redis_agent/prompts/` for summaries and analysis

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

Optional: Roundtable ideation:
```
./run_roundtable.sh "Topic: Next GTM channel experiments"
```

## One-command launch (script)
Use the launcher to start all core services (including listeners).
```
chmod +x ./run_all.sh
./run_all.sh
```

Optional extras:
```
SCHEDULE_MODE=cron ./run_all.sh
ROUNDTABLE_TOPIC="Next GTM experiments" ./run_all.sh
WEAVE_DISABLED=1 ./run_all.sh
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
3) Test wiring: `./scripts/test_e2e_wiring.sh subs` (verify all channels have subscribers)
4) Send test messages: `./scripts/test_e2e_wiring.sh all`
5) Check logs: `tail -f .logs/*.log`

## Full Discord test
1) Start all services with `./run_all.sh`
2) Send a Discord message in `LISTENING_CHANNELS` with a GTM idea
3) Watch the logs as it flows: Discord → Watcher → Orchestrator → FULLSEND
4) Verify experiment spec created and published to Redis

## Tests
```
uv run pytest
```
