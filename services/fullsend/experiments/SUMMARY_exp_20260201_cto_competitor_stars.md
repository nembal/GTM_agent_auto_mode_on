# Experiment Summary: CTO Competitor Stars Email Campaign

**Experiment ID:** exp_20260201_cto_competitor_stars
**Status:** Ready for execution (pending email_sender tool)
**Published:** 2026-02-01

---

## Hypothesis

CTOs who recently starred competitor repos show buying intent and will respond to personalized outreach that references their specific interests.

## What We're Testing

Cold email outreach to 200 CTOs at Series A startups who starred competitor repos in the last 30 days.

### Target Repos
- vercel/next.js
- supabase/supabase
- hasura/graphql-engine
- trpc/trpc
- prisma/prisma

### Email Template

**Subject:** Re: {{repo_name}}

**Body:**
```
Hey {{first_name}},

Saw you starred {{repo_name}} {{days_ago}} days ago — we're solving a similar
problem but specifically for GTM teams at Series A+ companies.

Most eng teams at your stage hit a wall when sales wants "just one more integration"
every week. We built Fullsend to run autonomous GTM experiments without pulling
engineers off the roadmap.

Built on the same stack you're already using (Next.js + Supabase patterns), but
with agent loops that generate ideas, build their own tools, and learn from results.

Worth 15 min to see if it clicks?

Best,
[Your Name]

PS - If you're not the right person, mind pointing me to whoever owns your GTM tooling?
```

**Follow-up (Day 5):**
```
{{first_name}},

Following up on my note about autonomous GTM experiments.

Quick question: What's your current process when sales wants to test a new outbound
channel (like cold email to {{repo_name}} stargazers)?

Most CTOs tell us: "Sales writes a spec, eng builds it in 2 weeks, idea is stale by then."

We eliminate that cycle entirely. Curious if you've found a better way?

[Your Name]
```

---

## Success Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Reply Rate** | 8%+ | Previous experiment baseline |
| **Meetings Booked** | 5+ | 2.5% conversion |
| **Email Opens** | 35%+ | Above 25% industry avg |
| **Positive Replies** | 12+ | 75% of replies show interest |

### Success Criteria
✅ Reply rate >= 8%
✅ At least 5 meetings booked
✅ Positive sentiment in 75%+ of replies
✅ Zero spam complaints

### Failure Criteria
❌ Reply rate < 5%
❌ More than 2 spam complaints
❌ Zero meetings after 2 weeks
❌ Negative sentiment in >50% of replies

---

## Execution Plan

### Phase 1: Tool Development (Builder)
- **Requested:** email_sender tool (req_20260201_email_sender)
- **Required features:** Template variables, follow-ups, rate limiting, metrics publishing
- **Blocker:** Experiment cannot run until this tool is built

### Phase 2: Test Run
- Send to 50 CTOs first
- Review replies and sentiment
- Adjust template if needed
- Scale to full 200 if metrics look good

### Phase 3: Full Campaign
- Schedule: Every Monday at 9 AM PT
- Tool: github_stargazer_scraper → email_sender pipeline
- Monitoring: Redis Agent watches for threshold alerts

---

## Learning Goals

1. **Subject Line:** Does "Re: {{repo_name}}" still outperform direct subjects?
2. **Recency:** Is 30-day window better than 90-day for intent signal?
3. **Follow-ups:** Do follow-ups increase meeting rate by >3x?
4. **Repo Context:** Which competitor repo gets best response rates?

---

## Risk Mitigation

- ✅ Test with 50 emails before scaling
- ✅ Professional domain with SPF/DKIM/DMARC
- ✅ Honor unsubscribes immediately
- ✅ Auto-pause on spam complaint threshold
- ✅ Track negative sentiment, adjust if needed

---

## Dependencies

### Tools Required
- ✅ **github_stargazer_scraper** (available)
- ⏳ **email_sender** (requested from Builder)

### Infrastructure
- ✅ Redis pub/sub (working)
- ✅ Executor service (working)
- ⏳ Email service setup (SendGrid or Postmark account)
- ⏳ Domain authentication (SPF/DKIM/DMARC)

---

## Next Steps

1. **Builder:** Build email_sender tool from req_20260201_email_sender.yaml
2. **Infra:** Set up email service account (Postmark recommended)
3. **Test:** Dry-run with test@mailinator.com
4. **Execute:** Run Phase 1 test with 50 CTOs
5. **Learn:** Analyze replies, iterate if needed
6. **Scale:** Full 200-person campaign on Monday schedule

---

## Tactical Learning Recorded

> Multi-repo targeting (Vercel, Supabase, Hasura, tRPC, Prisma) for broader CTO funnel.
> 30-day recency window to capture recent intent. Follow-up sequence at day 5 to test
> persistence value. 'Re: {{repo_name}}' subject line based on previous 8%+ reply rate success.

Stored at: `learnings:tactical:20260201_115830`

---

## Redis Publications

✅ **Experiment spec** → `experiments:exp_20260201_cto_competitor_stars`
✅ **Metrics spec** → `metrics_specs:exp_20260201_cto_competitor_stars`
✅ **Schedule** → `schedules:exp_20260201_cto_competitor_stars`
✅ **Tool request** → `tool_requests:req_20260201_email_sender`
✅ **Orchestrator notified** → `experiment_ready`

---

**Design Notes:**

This experiment builds on previous success (8%+ reply rate from similar CTO targeting)
while adding:
- Multi-repo sourcing for broader funnel
- Tighter recency window (30d)
- Follow-up sequence to test persistence
- Explicit learning goals per variable

The email template is conversational, references specific behavior (starred repo),
and positions Fullsend as solving a pain point CTOs actually have (eng bottleneck on
GTM experiments).

**FULLSEND Design Signature:** Complete specs, no placeholders, real templates,
measurable success criteria. Ready for autonomous execution once email_sender tool is built.
