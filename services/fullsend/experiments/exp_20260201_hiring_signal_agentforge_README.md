# Hiring Signal → AgentForge Outreach

**Experiment ID:** `exp_20260201_hiring_signal_agentforge`
**Status:** Ready to execute
**Priority:** High
**Created:** 2026-02-01

## The Hypothesis

Companies actively hiring for automatable back-office roles (Data Entry, Invoice Processing, Manual QA, etc.) are **high-intent prospects**. They have:

1. **Active Pain** — Need is urgent enough to post a job
2. **Active Budget** — Already allocated $45K+ for salary + benefits
3. **Decision Timeline** — Hiring takes 6-8 weeks; we can deploy in 48 hours

**Expected reply rate:** 10%+ (vs 5% baseline from CTO experiments)

## The Strategy

### Phase 1: Discover Companies (job_posting_finder)
Find 100 mid-market companies (200-2000 employees) with active job postings for:
- Data Entry Clerk
- Invoice Processor
- Document Processing Specialist
- Manual QA Tester
- Claims Processor
- Order Entry Specialist

**Source:** LinkedIn Jobs (past 30 days)

### Phase 2: Find Decision Makers (browserbase_email_finder)
At each company, find contacts for:
- VP Operations
- COO
- CFO
- Director of Operations
- Head of Operations

**Target:** 70%+ email discovery rate (70+ contacts from 100 companies)

### Phase 3: Send Personalized Outreach (cold_email_sender)
Send job-specific cold emails with:

**Subject:** `Re: {{job_title}} posting`

**Body:**
> Hi {{first_name}},
>
> I saw you're hiring for a {{job_title}} at {{company}}.
>
> What if instead of hiring and onboarding for 6-8 weeks, you could deploy an AI agent that starts Monday?
>
> AgentForge builds custom AI agents for back-office work:
> → Same output as a human hire
> → Fraction of the cost ($2K/month vs $45K+ salary)
> → Zero ramp time (live in 48 hours)
> → Scales instantly
>
> Worth a 15-min call this week?
>
> Best,
> Alex Chen
> AgentForge
>
> P.S. This email was sent by an AI agent. That's how confident we are in the tech.

## Success Metrics

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| Companies Discovered | 100+ | Enough pipeline for statistically valid test |
| Email Discovery Rate | 70%+ | Can we find decision makers at scale? |
| Emails Sent | 70+ | Actual outreach volume |
| Reply Rate | **10%+** | Key hypothesis: hiring signal = 2x CTO baseline |
| Meetings Booked | 3+ | Real business outcome |

## Why This Should Work

1. **Intent Signal Strength**
   - GitHub stars = "I'm interested in this tech" (passive)
   - Job posting = "I have $50K budget to solve this NOW" (active)

2. **Lower Inbox Competition**
   - CTOs get 50+ cold emails/week
   - Ops leaders get fewer, are less jaded

3. **Urgency Asymmetry**
   - Their timeline: 6-8 weeks (post job → interview → hire → onboard)
   - Our timeline: 48 hours (kickoff → deploy)

4. **Budget Already Allocated**
   - Not asking for new budget — redirecting existing headcount budget
   - $2K/month vs $45K+ salary = easy ROI story

5. **Job-Specific Personalization**
   - Subject: "Re: Invoice Processor posting" (not generic)
   - Body references exact role they're hiring for
   - Demonstrates we did research, not spray-and-pray

## What We'll Learn

- **Channel Effectiveness:** Hiring signal vs GitHub stars vs competitor usage?
- **Role Performance:** Which automatable roles have highest reply rates?
- **Buyer Persona:** Ops leaders vs CTOs — who's more responsive?
- **Messaging Impact:** Job-specific subject line vs generic?
- **Objection Patterns:** Already filled? Too expensive? Not interested?

## Cost Analysis

| Item | Calculation | Cost |
|------|-------------|------|
| Browserbase Sessions | $0.20 × 100 companies | $20.00 |
| Email Sends | $0.001 × 70 emails | $0.07 |
| **Total per run** | | **$20.07** |
| **Cost per meeting** | (if 3 booked) | **$6.69** |

Compare to traditional outbound:
- SDR salary: $5K/month
- This experiment: $20 for 70 targeted emails
- **250x cheaper**

## Execution Plan

**Schedule:** Every Monday at 9 AM PT

**Weekly cadence:**
- Monday 9 AM: Run Phase 1 (discover companies)
- Monday 10 AM: Run Phase 2 (find contacts)
- Monday 11 AM: Run Phase 3 (send emails)
- Follow-up sequences:
  - Day 5: First follow-up to non-responders
  - Day 10: Final follow-up to non-responders

## Follow-Up Sequences

**Day 5 (Non-responders):**
> Hi {{first_name}},
>
> Following up on my note about the {{job_title}} role.
>
> Quick question: Did you end up filling the position, or still interviewing candidates?
>
> If you're still looking, I'd love to show you how AgentForge could solve this faster (and cheaper) than a traditional hire.
>
> 15 minutes this week?
>
> Best,
> Alex

**Day 10 (Non-responders):**
> {{first_name}},
>
> Last note on this: If the {{job_title}} role is still open (or if you have other back-office positions), we can get you an AI agent running by Friday.
>
> Worth exploring?
>
> Alex

## Expected Outcomes

| Scenario | Reply Rate | Meetings | Conclusion |
|----------|------------|----------|------------|
| **Optimistic** | 15% | 5+ | Hiring = best signal we've tested. Scale to 500/week. |
| **Realistic** | 10% | 3 | Hypothesis validated. Make this primary channel. |
| **Pessimistic** | 5% | 1 | Same as CTO baseline. Hiring ≠ higher intent. |

## Next Iterations (If Successful)

1. **Role Segmentation** — Which automatable roles convert best?
2. **Timing Test** — Contact day 1 vs day 14 vs day 30 of posting?
3. **Messaging Variants** — Cost savings vs speed vs quality angle?
4. **Multi-Channel** — Add LinkedIn InMail as second touchpoint?
5. **Build Job Monitor** — Real-time alerts when target roles posted?
6. **Scale to 500/week** — If 10%+ reply rate, increase volume 7x

## How to Run

```bash
# Publish experiment to Redis
./scripts/redis_publish.sh publish_experiment_full experiments/exp_20260201_hiring_signal_agentforge.yaml

# Trigger immediate execution (don't wait for Monday)
./scripts/redis_publish.sh trigger_experiment exp_20260201_hiring_signal_agentforge

# Check status
./scripts/redis_publish.sh get_experiment_status exp_20260201_hiring_signal_agentforge

# View results
cat /tmp/fullsend_experiments/exp_20260201_hiring_signal_agentforge/results.json
```

## Tools Used

1. **job_posting_finder** — Scrapes LinkedIn Jobs for automatable role postings
2. **browserbase_email_finder** — Discovers ops leader emails at target companies
3. **cold_email_sender** — Sends personalized outreach with tracking

## Red Flags to Watch For

- **Email discovery < 50%** → Tool broken or companies have no web presence
- **Deliverability < 90%** → Domain reputation issues, need to warm up
- **Reply rate < 5%** → Messaging failed, hypothesis rejected
- **All negative replies** → Messaging angle is off
- **Zero meeting bookings** → Call-to-action too weak

## Success Case Study (Projected)

If this hits 10%+ reply rate:

**Numbers:**
- 100 companies found
- 70 emails sent (70% discovery rate)
- 7 replies (10% reply rate)
- 3 meetings booked (4% meeting rate)
- 1 customer closed (33% close rate on meetings)

**Annual Contract Value (ACV):** $24K ($2K/month × 12)

**Experiment ROI:** $24K revenue / $20 experiment cost = **1,200x ROI**

**Weekly scale:** 500 companies → 350 emails → 35 replies → 15 meetings → 5 customers → **$120K ACV/week**

This would be the highest-leverage GTM channel we've ever built.

---

**Status:** Ready for Orchestrator approval and Executor scheduling.
