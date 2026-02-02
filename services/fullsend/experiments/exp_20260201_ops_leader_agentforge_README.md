# Experiment: Ops Leader AgentForge Outreach

**ID**: `exp_20260201_ops_leader_agentforge`
**Status**: Ready for execution
**Type**: Two-phase automated prospecting (Email Discovery → Send)

## Overview

First fully automated email prospecting workflow for AgentForge. Chains two tools:
1. `browserbase_email_finder` - Scrape company websites for VP Ops/CFO/COO contacts
2. `cold_email_sender` - Send personalized outreach with meta narrative

## Target Audience

**ICP**: VP Operations, CFO, COO at mid-market companies ($50M-$500M revenue)

**Industries**: Manufacturing, Logistics, Healthcare, Financial Services (ops-heavy verticals)

**Why these roles?**
- Ops leaders feel manual process pain daily
- Clear ROI for automation (unlike generic "AI transformation")
- Budget authority for operational tools
- Shorter sales cycles than strategic initiatives

## Hypothesis

Ops leaders at mid-market companies will respond to:
1. **Speed narrative**: "Days vs months" (they've been burned by slow vendors)
2. **Meta proof**: "An agent found your email and wrote this" (proves product works)
3. **Operational focus**: Not chatbots, real process automation

## Execution Flow

### Phase 1: Email Discovery (browserbase_email_finder)

```python
# For each target company:
browserbase_email_finder(
    company_name="ProMach",
    company_url="promachbuilt.com",
    target_role="VP Operations"  # Also searches: COO, CFO, Head of Ops
)
# Returns: List of contacts with email, name, role, source_url
```

**Target companies** (10 companies, ~30 contacts expected):
- Manufacturing: ProMach, Pactiv Evergreen, Chart Industries
- Logistics: J.B. Hunt, Ryder, XPO
- Healthcare: Fresenius Medical Care, Encompass Health, BrightSpring
- Financial Services: First Horizon Bank

### Phase 2: Send Personalized Emails (cold_email_sender)

```python
cold_email_sender(
    recipients=discovered_contacts,  # From phase 1
    template={
        "subject": "Re: AI workforce deployment",
        "body": "Hi {{first_name}}, your competitors are hiring... (see spec)"
    },
    campaign_name="ops_leader_agentforge_v1",
    send_options={
        "sender_email": "alex@agentforge.dev",
        "daily_limit": 30,
        "delay_seconds": 3
    }
)
```

**Personalization variables**:
- `{{first_name}}`, `{{company}}`, `{{industry}}`
- Industry-specific pain points (manufacturing = data entry, logistics = reconciliation)

## Email Template

**Subject**: `Re: AI workforce deployment`

**Body** (abbreviated):
```
Hi {{first_name}},

Your competitors are hiring more ops teams. You could be deploying AI agents instead.

{{company}} operates in {{industry}} where operational efficiency = competitive advantage.
Most ops leaders waste 6 months on AI pilots. We ship working agents in days.

Proof? An autonomous agent found your email, wrote this message, and sent it.
Same tech we'd deploy for your operations.

Worth a 15-minute call this week?

Alex Chen
Founder, AgentForge
```

**Why this template works**:
- Opening line: Bold contrast (hiring vs deploying)
- Personalization: Company + industry
- Meta narrative: Agent-sent email proves product
- Pain points: Manual workflows, slow vendors
- CTA: Low-commitment (15 min call)
- P.S.: Offers to show architecture (nerd bait)

## Success Metrics

| Metric | Target | Benchmark |
|--------|--------|-----------|
| Email discovery rate | 70%+ | N/A (first run) |
| Emails sent | 20+ | N/A |
| Reply rate | 8%+ | CTO experiments |
| Positive replies | 1-2 meetings | 3%+ interest rate |
| Bounce rate | <8% | Acceptable for scraping |

**Success = All criteria met**:
- Find contacts at 7/10 companies
- Send 20+ emails
- Get 8%+ reply rate
- Book 1-2 meetings
- Prove automation works end-to-end

## Execution Instructions

### Prerequisites

1. **Environment variables**:
```bash
export BROWSERBASE_API_KEY="..."
export BROWSERBASE_PROJECT_ID="..."
export RESEND_API_KEY="..."
export RESEND_SENDER_EMAIL="alex@agentforge.dev"
```

2. **Verify sender in Resend**:
- Ensure `alex@agentforge.dev` is verified in Resend dashboard
- Set up webhook for reply tracking

### Run Experiment

**Option 1: Via Executor (scheduled)**
```bash
# Publish to Redis (Executor will run on schedule)
./scripts/redis_publish.sh publish_experiment_full experiments/exp_20260201_ops_leader_agentforge.yaml

# Schedule: Wednesdays at 10am PT
```

**Option 2: Manual trigger**
```bash
# Run immediately
SCHEDULE_MODE=trigger uv run python -m services.executor.main

# Or directly:
python tools/run_experiment.py exp_20260201_ops_leader_agentforge
```

### Monitoring

1. **Watch logs during execution**:
```bash
tail -f logs/executor.log
```

2. **Check Redis for results**:
```bash
redis-cli GET "experiments:exp_20260201_ops_leader_agentforge:results"
```

3. **Monitor Resend dashboard**:
- Opens, clicks, bounces in real-time
- Set up webhook to pipe events to Redis

4. **Manual reply monitoring**:
- Check `alex@agentforge.dev` inbox every 4 hours
- Fast replies = higher conversion

## Learnings to Capture

After 7 days, store tactical learnings:

```bash
./scripts/redis_publish.sh store_learning "Ops leaders in manufacturing responded 2x better than logistics" exp_20260201_ops_leader_agentforge

./scripts/redis_publish.sh store_learning "Subject line 'Re: AI workforce deployment' got 40% open rate" exp_20260201_ops_leader_agentforge
```

**Questions to answer**:
- Which industry responded best?
- Does meta narrative intrigue or annoy?
- Optimal company size ($50M-$200M vs $200M-$500M)?
- Which pain points resonate?
- Does automated discovery work at scale?

## Iteration Plan

### If Success (8%+ reply rate, 1-2 meetings)

1. **Scale to 100+ companies**:
   - Add more verticals (retail ops, supply chain)
   - Expand to $25M-$50M companies (faster decision-makers)

2. **A/B test variants**:
   - Subject: "Re: AI workforce" vs "Re: your competitors are hiring"
   - Opening: Bold contrast vs direct pain point

3. **Build follow-up sequence**:
   - Day 5: "Saw you opened the email about AgentForge..."
   - Day 10: Case study approach

4. **Capture learnings**:
   - Which industries convert best
   - Optimal messaging per vertical
   - Best pain points per role (VP Ops vs CFO)

### If Failure (<3% reply rate, zero meetings)

**Diagnosis checklist**:

1. **Email discovery failed** (<50% success rate):
   - Improve browserbase_email_finder (try LinkedIn, Crunchbase)
   - Add fallback sources

2. **High bounce rate** (>15%):
   - Add email validation step (Hunter.io, NeverBounce)
   - Verify contacts before sending

3. **Low reply rate** (<3%):
   - Test different angles (less meta, more ROI)
   - Try warmer intro strategies
   - Pivot to LinkedIn outreach

4. **Zero positive replies**:
   - Wrong ICP (ops leaders don't care about AI)
   - Wrong pain points (not operational enough)
   - Wrong industries (test B2B SaaS, fintech instead)

## Why This Experiment Matters

If this succeeds, we've validated:

1. **End-to-end automation**: Find → personalize → send with zero manual work
2. **New ICP**: Ops leaders (not just CTOs) respond to AgentForge
3. **New verticals**: Manufacturing, logistics, healthcare have real demand
4. **Meta narrative**: Agent-sent emails work across audiences
5. **Repeatable motion**: Foundation for scaling to 1000s of prospects

This is the first experiment that chains multiple tools autonomously. If the workflow succeeds, it proves FULLSEND can design AND execute complex GTM playbooks without human intervention.

## Files

- `exp_20260201_ops_leader_agentforge.yaml` - Full experiment spec
- `exp_20260201_ops_leader_agentforge_README.md` - This file
- Results will be stored in Redis: `experiments:exp_20260201_ops_leader_agentforge:results`
