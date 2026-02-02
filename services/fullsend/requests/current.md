# Experiment Request — COMPLETED

**Priority:** high
**Received:** 2026-02-01T22:10:01.007781+00:00
**Completed:** 2026-02-01T22:12:45+00:00
**Status:** ✅ Designed and published to Redis

## Original Request

**Idea/Goal:** Target companies actively hiring for automatable roles as high-signal prospects

**Context:** Companies posting jobs for 'Data Entry Clerk', 'Invoice Processor', 'Manual QA Tester', etc. are explicitly advertising a need we can solve with AI agents. This is intent data — they're already budgeting for the headcount we can replace.

**Messaging Angle:** "You're hiring a [role]. What if you could deploy an AI agent instead? Same output, fraction of the cost, starts Monday."

## What Was Delivered

### Experiment Spec
**ID:** `exp_20260201_hiring_signal_agentforge`

**Files Created:**
- `/services/fullsend/experiments/exp_20260201_hiring_signal_agentforge.yaml`
- `/services/fullsend/experiments/exp_20260201_hiring_signal_agentforge_README.md`

### Pipeline Design

**Phase 1: Discover Companies** (job_posting_finder)
- Find 100 mid-market companies (200-2000 employees)
- Target roles: Data Entry, Invoice Processing, Manual QA, Claims Processing, Order Entry
- Source: LinkedIn Jobs (past 30 days)
- Location: United States

**Phase 2: Find Decision Makers** (browserbase_email_finder)
- Target: VP Ops, COO, CFO, Director of Operations
- Goal: 70%+ email discovery rate (70+ contacts from 100 companies)

**Phase 3: Send Personalized Outreach** (cold_email_sender)
- Job-specific subject line: "Re: {{job_title}} posting"
- Speed advantage messaging: 48 hours vs 6-8 weeks hiring
- Cost comparison: $2K/month vs $45K+ salary
- Meta narrative: "This email was sent by an AI agent"
- Daily limit: 50 emails

### Key Hypothesis

**Active hiring = 2x higher intent than GitHub stars**

Expected reply rate: **10%+** (vs 5% CTO baseline)

**Why this should work:**
1. Job posting = explicit pain + active budget (not passive interest)
2. Ops leaders get fewer cold emails than CTOs (less inbox fatigue)
3. Speed advantage: 48 hours vs 6-8 weeks hiring timeline
4. Budget redirection (not asking for new budget)
5. Job-specific personalization creates relevance

### Success Metrics

| Metric | Target |
|--------|--------|
| Companies Discovered | 100+ |
| Email Discovery Rate | 70%+ |
| Emails Sent | 70+ |
| **Reply Rate** | **10%+** |
| Meetings Booked | 3+ |

### Execution Schedule

**Cadence:** Every Monday at 9 AM PT

**Follow-up sequences:**
- Day 5: First follow-up to non-responders
- Day 10: Final follow-up to non-responders

### Cost Analysis

- Browserbase: $0.20/session × 100 companies = $20.00
- Resend: $0.001/email × 70 emails = $0.07
- **Total:** $20.07 per run
- **Cost per meeting:** $6.69 (if 3 booked)

Compare to SDR: $5K/month → This is **250x cheaper**

### Published to Redis

✅ Experiment spec → `experiments:exp_20260201_hiring_signal_agentforge`
✅ Metrics spec → `metrics_specs:exp_20260201_hiring_signal_agentforge`
✅ Schedule → `schedules:exp_20260201_hiring_signal_agentforge` (cron: `0 9 * * MON`)
✅ Tactical learning stored → `learnings:tactical:20260201_141220`
✅ Orchestrator notified → `experiment_designed`

## Next Actions

1. **Executor** will run first iteration Monday 9 AM PT
2. **Redis Agent** will monitor reply_rate metric
3. **Orchestrator** will receive alerts on:
   - Reply rate hits 10%+ (success milestone)
   - Meetings booked (business outcome)
   - Experiment completion (weekly summary)

## Learning Questions to Answer

- Does hiring signal = higher intent than GitHub stars?
- Which automatable roles have highest reply rates?
- Do ops leaders respond better than CTOs?
- Does job-specific subject line outperform generic?
- What are common objections?

## If Successful (10%+ reply rate)

**Scale plan:**
- Increase to 500 companies/week
- 350 emails → 35 replies → 15 meetings → 5 customers
- **$120K ACV/week** at same 10% reply rate

This would be our highest-leverage GTM channel.

---

**Status:** Ready for execution. Waiting for Executor to run first iteration.
