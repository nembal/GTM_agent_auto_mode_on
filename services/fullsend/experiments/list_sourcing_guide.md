# List Sourcing Guide for Email Prospecting Experiments

This guide covers sourcing strategies for all email experiments, including:
- `exp_20260201_cto_cold_agentforge` (CTO manual sourcing)
- `exp_20260201_ops_leader_agentforge` (Ops Leader automated + manual hybrid)

## Overview: Three Sourcing Strategies

### 1. **Automated Web Scraping** (exp_20260201_ops_leader_agentforge)
- Tool: `browserbase_email_finder`
- Best for: Scaling to 100+ contacts, mid-market companies with public leadership pages
- Pros: Fully automated, cost-effective, real-time data
- Cons: 50-80% hit rate, may miss some contacts

### 2. **Manual Curation** (exp_20260201_cto_cold_agentforge)
- Tools: LinkedIn Sales Navigator, ZoomInfo, Apollo.io
- Best for: High-precision targeting, 30-50 contacts
- Pros: Highest quality, rich metadata
- Cons: Time-intensive, doesn't scale

### 3. **Intent Signal Sourcing** (exp_20260201_cto_stargazer_email)
- Tools: GitHub API, Product Hunt, Twitter
- Best for: Developer tools, technical audiences
- Pros: 8%+ reply rates, ultra-high intent
- Cons: Smaller volume, requires API access

---

# Strategy 1: Automated Web Scraping (Ops Leader Experiment)

Used in: `exp_20260201_ops_leader_agentforge`

## How It Works

The `browserbase_email_finder` tool:
1. Takes company name + URL
2. Scrapes pages: /about, /team, /contact, /leadership
3. Extracts emails using regex
4. Filters by target role (VP Ops, CFO, COO)
5. Returns structured contacts: name, role, email, source_url

## Input Format

```yaml
companies_to_research:
  - name: "ProMach"
    url: "promachbuilt.com"
    industry: "manufacturing"
    revenue_range: "$500M"
```

## Quality Metrics

- **Email discovery rate**: Target 70%+ (find contacts at 7/10 companies)
- **Bounce rate**: Target <8% (acceptable for automated discovery)
- **Role accuracy**: 80%+ (correct title extraction)

## When to Use

- Scaling to 100+ contacts
- Mid-market companies with public leadership pages
- Industries with transparent org structures (manufacturing, logistics)

---

# Strategy 2: Manual Curation (CTO Experiment)

Used in: `exp_20260201_cto_cold_agentforge`

## LinkedIn Sales Navigator Filters

### 1. Job Title
```
Current Job Title: CTO OR "Chief Technology Officer" OR "VP Engineering"
```

### 2. Company Size
```
Company Headcount: 50-200 OR 201-500
```

### 3. Industry
```
Industry:
- Computer Software (SaaS)
- Financial Services (Fintech)
- Hospital & Health Care (Healthtech)
- Logistics and Supply Chain
```

### 4. Geography
```
Location: United States (focus on major tech hubs if needed)
```

### 5. Company Revenue (if available)
```
Revenue: $50M - $500M
(Note: LinkedIn Sales Navigator may not have precise revenue filters - use Crunchbase/ZoomInfo to verify)
```

## Verification Steps

For each CTO found:
1. **Verify company revenue** via Crunchbase or ZoomInfo
2. **Check recent activity** - are they posting about AI/automation?
3. **Look for pain signals:**
   - Recent job postings for AI/ML engineers?
   - Posts about vendor evaluation?
   - Signs of scaling challenges?

## Email Finding

Use one of these methods:
1. **Hunter.io** - Company domain + first/last name pattern
2. **Apollo.io** - Direct email lookup
3. **RocketReach** - LinkedIn profile → email
4. **Manual pattern matching** - Most companies use `first.last@company.com` or `first@company.com`

## Customization Fields

For each recipient, collect:
```yaml
- email: "john.smith@company.com"
  first_name: "John"
  last_name: "Smith"
  company: "Acme Corp"
  title: "CTO"
  custom_fields:
    industry: "saas"  # or fintech, healthtech, logistics
    pain_point: "scaling_ai"  # or vendor_fatigue, build_vs_buy
```

**How to infer pain_point:**
- `scaling_ai` - Company is hiring AI engineers, posts about AI challenges
- `vendor_fatigue` - Company recently evaluated multiple vendors, posts about tool sprawl
- `build_vs_buy` - Company is at inflection point, posts about team growth

## Quality Checklist

Before adding a CTO to the list:
- [ ] Valid company email (not personal Gmail/Yahoo)
- [ ] Company revenue verified $50M-$500M
- [ ] Company actively hiring (sign of growth)
- [ ] CTO is active on LinkedIn (not dormant account)
- [ ] Industry matches target (SaaS, fintech, healthtech, logistics)

## Target Profile Example

**Perfect ICP:**
- **Name:** Sarah Johnson
- **Title:** CTO at CloudMetrics (SaaS company)
- **Company:** $120M revenue, 280 employees
- **Recent activity:** Posted about "evaluating AI platforms" last month
- **Pain point:** Vendor fatigue
- **Why good fit:** Technical leader, company scaling, actively exploring AI

**Avoid:**
- CTOs at companies going through layoffs (no budget)
- CTOs at early-stage startups (<$10M revenue - too small)
- CTOs at enterprises (>$1B revenue - too complex sales cycle)
- CTOs with no LinkedIn activity (unlikely to engage)

## Tool Recommendations

**Free tier:**
- LinkedIn Sales Navigator (trial)
- Hunter.io (50 searches/month)
- Crunchbase (limited data)

**Paid (if budget available):**
- Apollo.io ($49/mo - best for email + enrichment)
- ZoomInfo ($250+/mo - overkill for 50 contacts)
- RocketReach ($50/mo - good middle ground)

## Time Estimate

- **Sourcing 50 CTOs:** 2-3 hours
- **Email verification:** 30 minutes
- **Enrichment (industry, pain point):** 1 hour
- **Total:** ~4 hours for high-quality list

## Output Format

Save as CSV or directly update the YAML:

```csv
email,first_name,last_name,company,title,industry,pain_point
john.smith@acme.com,John,Smith,Acme Corp,CTO,saas,scaling_ai
sarah.jones@fintech.io,Sarah,Jones,FinTech Inc,CTO,fintech,vendor_fatigue
```

Then convert to YAML format for experiment file.

---

**Questions?** Check existing learnings in Redis or ask Orchestrator for guidance.
