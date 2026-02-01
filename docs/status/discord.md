# Status: discord

State: COMPLETE
Started: 2026-01-30
Completed: 2026-02-01

## Inputs
- PRD: Discord Communication Service PRD
- Tasks: RALPH/STATUS.md

## Outputs
- services/discord/ (complete service)
- Adapters: discord_adapter.py, web_adapter.py
- Core: bus.py, messages.py, router.py
- Templates: dashboard.html (dark theme UI)

## What It Does
Discord is the human interface layer with two adapters:
- **Discord Bot**: Slash commands, message listening, emoji reactions
- **Web Dashboard**: FastAPI + WebSocket for real-time UI

Message flow:
```
Discord → fullsend:discord_raw → Watcher → Orchestrator
    ↑                                          ↓
    └──────── fullsend:from_orchestrator ──────┘
```

## Redis Channels
| Channel | Direction |
|---------|-----------|
| `fullsend:discord_raw` | Publishes raw messages |
| `fullsend:from_orchestrator` | Subscribes for responses |

## Key Decisions
- ENV var controls which adapters run (discord/web/both)
- Bot is proactive (posts updates without being asked)
- Memory limits: max 1000 reacted messages, max 100 pending actions

## Post-Build Fixes
- Fixed `_connected` → `is_connected` bug
- Fixed `datetime.utcnow()` → `datetime.now(UTC)`
- Aligned channel names with Watcher/Orchestrator

## Blockers
None
