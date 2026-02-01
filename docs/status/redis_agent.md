# Status: redis_agent

State: COMPLETE
Started: 2026-02-01T04:24:46-08:00
Completed: 2026-02-01T07:17:00-08:00

## Inputs
- PRD: docs/prd/PRD_REDIS_AGENT.md
- Tasks: RALPH/TASKS_REDIS_AGENT.md

## Outputs
- services/redis_agent/__init__.py
- services/redis_agent/main.py (daemon with parallel tasks)
- services/redis_agent/config.py (Pydantic settings)
- services/redis_agent/monitor.py (metrics stream + thresholds)
- services/redis_agent/analyzer.py (Gemini summaries)
- services/redis_agent/alerts.py (cooldown dedup)
- services/redis_agent/prompts/analyze.txt, summarize.txt
- services/redis_agent/tests/ (pytest + fakeredis)

## What It Does
Redis Agent monitors experiment metrics and alerts Orchestrator.

**Parallel Tasks (asyncio.gather):**
1. `monitor_metrics_stream()` - Subscribe to `fullsend:metrics`, aggregate per experiment
2. `check_thresholds_loop()` - Every 60s, evaluate success/failure criteria
3. `run_periodic_summaries()` - Hourly LLM summaries via Gemini 2.0 Flash

**Metrics Flow:**
```
Executor → fullsend:metrics → Redis Agent → fullsend:to_orchestrator
                                   ↓
                          metrics_aggregated:{exp_id}
```

**Threshold Evaluation:**
- Parses criteria like `"response_rate > 0.10"`
- Supports: >, <, >=, <=, ==, !=
- Alerts with cooldown (default 300s) to prevent spam

## Key Decisions
- New implementation (existing redis_agent.py was interactive CLI, not daemon)
- Gemini 2.0 Flash for cheap, fast analysis
- Alert cooldown keyed by `{experiment_id}:{alert_type}`
- Graceful handling when GOOGLE_API_KEY not set

## Blockers
None
