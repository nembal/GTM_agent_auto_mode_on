# Tasks

- [ ] TASK-001: Confirm Redis channels (`fullsend:discord_raw`, `fullsend:to_orchestrator`, `fullsend:from_orchestrator`) and message formats per PRD.
- [ ] TASK-002: Create `services/watcher/` skeleton with `main.py`, `config.py`, `classifier.py`, `responder.py`, `prompts/`.
- [ ] TASK-003: Implement classification flow with Gemini 2.0 Flash and escalation rules.
- [ ] TASK-004: Implement simple response path (status queries) + Redis reads only.
- [ ] TASK-005: Add retry + safe fallback (escalate on errors).
- [ ] TASK-006: Add basic unit/integration tests from PRD test plan.
- [ ] TASK-007: Verify acceptance criteria checklist in PRD.
