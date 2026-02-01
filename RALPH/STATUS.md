# RALPH Status (Code Review)

Quick reference for agents working on this codebase.

## System Architecture

```
Discord ──► Watcher ──► Orchestrator ──► FULLSEND/Builder/Roundtable
   ▲            │              │
   │            │              ▼
   └────────────┴──────── Executor ◄── Redis Agent
```

**Redis Channels:**
- `fullsend:discord_raw` - Discord → Watcher
- `fullsend:to_orchestrator` - Watcher → Orchestrator
- `fullsend:from_orchestrator` - Orchestrator → Discord (responses)
- `fullsend:to_fullsend` - Orchestrator → FULLSEND (experiment requests)
- `fullsend:builder_tasks` - Orchestrator → Builder (tool PRDs)
- `fullsend:schedules` - FULLSEND → Executor
- `fullsend:metrics` - Executor → Redis Agent
- `fullsend:experiment_results` - Executor → Orchestrator

---

## Services

### Discord (`services/discord/`)
Human interface - Discord bot + web dashboard.

**Key files:**
- `main.py` - Entry point, runs adapters based on ENV
- `adapters/discord_adapter.py` - Discord bot (slash commands, reactions)
- `adapters/web_adapter.py` - FastAPI + WebSocket dashboard
- `core/bus.py` - Redis pub/sub wrapper
- `core/router.py` - Message routing to both adapters
- `core/messages.py` - Pydantic models for all message types

**Slash commands:** `/status`, `/pause`, `/go`, `/idea <text>`

**Config:** `DISCORD_TOKEN`, `DISCORD_GUILD_ID`, `LISTENING_CHANNELS`, `STATUS_CHANNEL`, `ENV` (discord/web/both)

---

### Watcher (`services/watcher/`)
Filters Discord messages using Gemini 2.0 Flash.

**Key files:**
- `main.py` - Daemon loop
- `classifier.py` - Gemini classification (ignore/answer/escalate)
- `responder.py` - Answers simple queries from Redis state
- `escalator.py` - Formats escalations for Orchestrator

**Actions:**
| Classification | What Happens |
|----------------|--------------|
| `ignore` | Off-topic, no action |
| `answer` | Simple query, respond from Redis |
| `escalate` | Forward to Orchestrator |

**Config:** `GEMINI_API_KEY`, `REDIS_URL`

---

### Orchestrator (`services/orchestrator/`)
Strategic brain - Claude Opus 4 with extended thinking.

**Key files:**
- `main.py` - Daemon loop
- `agent.py` - Claude API with extended thinking
- `context.py` - Loads context from files + Redis
- `dispatcher.py` - Executes all action types

**Actions:**
| Action | Target |
|--------|--------|
| `dispatch_to_fullsend` | Send experiment request |
| `dispatch_to_builder` | Send tool PRD |
| `respond_to_discord` | Reply to user |
| `update_worklist` | Update priorities |
| `record_learning` | Append insight |
| `kill_experiment` | Archive failing experiment |
| `initiate_roundtable` | Start debate |

**Context files:** `context/product_context.md`, `context/worklist.md`, `context/learnings.md`

**Config:** `ANTHROPIC_API_KEY`, `THINKING_BUDGET` (default 10k tokens)

---

### FULLSEND (`services/fullsend/`)
Claude Code agent that designs experiments.

**Key files:**
- `run.sh` - Entry point (runs Claude Code)
- `prompts/system.txt` - System prompt
- `requests/current.md` - Input request
- `experiments/*.yaml` - Output specs
- `ralph.sh` - Spawns RALPH loops for complex tasks

**Flow:**
1. Read request from `requests/current.md`
2. Design experiment with real templates
3. Output YAML to `experiments/`
4. Publish schedule to Executor

---

### Builder (`services/builder/`)
Claude Code agent that creates tools from PRDs.

**Key files:**
- `run.sh` - Entry point (YOLO mode)
- `prompts/system.txt` - System prompt
- `requests/current_prd.yaml` - Input PRD
- `templates/tool_template.py` - Tool contract template

**Tool contract:**
```python
def tool_name(**kwargs) -> dict:
    return {"result": ..., "success": True, "error": None}
run = tool_name  # alias
```

---

### Executor (`services/executor/`)
Runs experiments by loading tools dynamically.

**Key files:**
- `main.py` - Schedule modes (trigger/cron/speedrun)
- `loader.py` - Dynamic tool import via `importlib.util`
- `runner.py` - Execution with timeout + retry
- `metrics.py` - Emits to `fullsend:metrics`

**Schedule modes:**
- `trigger` - Listen for Redis messages
- `cron` - Run on schedule (checks every 60s)
- `speedrun` - Run all due experiments now

**Config:** `REDIS_URL`, `TOOLS_DIR`, `EXECUTION_TIMEOUT` (default 300s)

---

### Redis Agent (`services/redis_agent/`)
Monitors metrics and alerts Orchestrator.

**Key files:**
- `main.py` - Daemon with parallel tasks
- `monitor.py` - Metrics stream + threshold checks
- `analyzer.py` - Gemini summaries
- `alerts.py` - Cooldown deduplication

**Threshold syntax:** `"response_rate > 0.10"` (supports >, <, >=, <=, ==, !=)

**Config:** `GOOGLE_API_KEY`, `REDIS_URL`, `ALERT_COOLDOWN` (default 300s)

---

### Roundtable (`services/roundtable/`)
3-agent debate for GTM ideas.

**Key files:**
- `runner.py` - Debate orchestration
- `personas.py` - Loads persona files
- `llm.py` - W&B Inference client
- `personas/*.txt` - ARTIST, BUSINESS, TECH, SUMMARIZER

**CLI:**
```bash
./services/roundtable/run.sh "prompt"
echo '{"prompt": "..."}' | python -m services.roundtable
```

**Config:** `WANDB_API_KEY`, `WEAVE_PROJECT`

---

## Status Files

Detailed build records: `docs/status/*.md`
- discord.md, watcher.md, orchestrator.md, fullsend.md
- executor.md, redis_agent.md, builder.md, roundtable.md

---

## Running RALPH

```bash
# Single task list
./RALPH/ralph.sh

# Multi-stage build
./RALPH/ralph2.sh
```

RALPH reads `RALPH/TASKS.md`, executes tasks sequentially, updates `RALPH/STATUS.md` as memory between iterations.
