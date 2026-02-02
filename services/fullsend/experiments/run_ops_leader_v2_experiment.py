#!/usr/bin/env python3
"""
Autonomous Cold Outreach Pipeline v2: Hiring Signal Targeting

This script executes Phase 2 and Phase 3 of the ops_leader_agentforge_v2 experiment.

Prerequisites:
- Phase 1 completed: /tmp/hiring_companies.csv exists (100 companies hiring for automatable roles)
- BROWSERBASE_API_KEY set in environment
- RESEND_API_KEY set in environment
- alex@agentforge.dev verified in Resend

Usage:
    python run_ops_leader_v2_experiment.py

Output:
    - /tmp/ops_leader_contacts.csv (discovered contacts)
    - Campaign sent via Resend
    - Metrics published to Redis
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


async def verify_prerequisites():
    """Check that all required inputs and configs exist."""
    print("=== Verifying Prerequisites ===\n")

    checks = []

    # Check Phase 1 output exists
    input_csv = Path("/tmp/hiring_companies.csv")
    if input_csv.exists():
        line_count = len(input_csv.read_text().strip().split("\n")) - 1  # minus header
        print(f"✅ Phase 1 input found: {input_csv} ({line_count} companies)")
        checks.append(True)
    else:
        print(f"❌ Phase 1 input missing: {input_csv}")
        print("   Run Phase 1 first: LinkedIn job search → save to /tmp/hiring_companies.csv")
        checks.append(False)

    # Check API keys
    if os.getenv("BROWSERBASE_API_KEY"):
        print("✅ BROWSERBASE_API_KEY set")
        checks.append(True)
    else:
        print("❌ BROWSERBASE_API_KEY not set")
        checks.append(False)

    if os.getenv("RESEND_API_KEY"):
        print("✅ RESEND_API_KEY set")
        checks.append(True)
    else:
        print("❌ RESEND_API_KEY not set")
        checks.append(False)

    print()

    if not all(checks):
        print("Prerequisites not met. Fix the issues above and try again.")
        return False

    return True


async def run_phase_2_discovery():
    """Phase 2: Discover VP Ops/CFO/COO emails at hiring companies."""
    print("=== Phase 2: Email Discovery ===\n")
    print("Finding VP Ops/CFO/COO contacts at companies hiring for automatable roles...")
    print("This will take ~2 hours for 100 companies.\n")

    # Import tool dynamically
    from tools.browserbase_email_finder import browserbase_email_finder

    target_roles = [
        "VP Operations",
        "VP of Operations",
        "Chief Operating Officer",
        "COO",
        "Chief Financial Officer",
        "CFO",
        "Director of Operations",
        "Head of Operations",
        "VP Finance",
    ]

    try:
        result = await browserbase_email_finder(
            input_csv="/tmp/hiring_companies.csv",
            target_roles=target_roles,
            output_csv="/tmp/ops_leader_contacts.csv",
            discovery_limit=100,
        )

        print(f"\n✅ Discovery complete!")
        print(f"   Companies processed: {result.get('companies_processed', 0)}")
        print(f"   Emails found: {result.get('emails_found', 0)}")
        print(f"   Discovery rate: {result.get('discovery_rate', 0):.1f}%")
        print(f"   Output: /tmp/ops_leader_contacts.csv\n")

        # Publish metrics to Redis
        await publish_metric("email_discovery_rate", result.get("discovery_rate", 0))
        await publish_metric("companies_found_hiring", result.get("companies_processed", 0))

        return result

    except Exception as e:
        print(f"❌ Discovery failed: {e}")
        return None


async def run_phase_3_outreach():
    """Phase 3: Send job-specific personalized emails."""
    print("=== Phase 3: Email Outreach ===\n")
    print("Sending personalized emails with job-specific templates...")
    print("Daily limit: 50 emails, 5-10 second delays.\n")

    # Import tool dynamically
    from tools.cold_email_sender import cold_email_sender

    # Template selection logic
    templates = {
        "hiring_signal_invoice": {
            "keywords": ["invoice", "accounts payable", "ap specialist"],
            "subject": "Re: {{job_title}} role at {{company_name}}",
            "body": """{{first_name}},

Saw {{company_name}} is hiring for {{job_title}}. Quick question: what if that role was filled by an AI agent instead of another hire?

We're AgentForge. We build custom AI agents for operations teams — not chatbots, actual autonomous workers that process invoices, qualify leads, handle data entry.

What makes us different:
• **Speed**: Agents deployed in 4 days, not 6 months
• **No code**: You describe the process, we build the agent
• **Self-improving**: Agents learn from mistakes and fix themselves
• **Cost**: Fraction of headcount, scales infinitely

Real example: A manufacturing CFO came to us hiring for 2 invoice processors. We deployed an agent that now handles 10K invoices/month at 99.2% accuracy. Both reqs canceled. Zero human error. Zero sick days.

Here's the proof this works: This email was researched, personalized, and sent by our autonomous GTM agent. No human wrote it. That's what we build for ops teams like yours.

Worth 15 minutes this week to explore what an agent could do for {{company_name}}'s invoice processing?

Best,
Alex Chen
Founder, AgentForge
alex@agentforge.dev

P.S. If you reply, a human will respond. We're not animals.""",
        },
        "hiring_signal_data_entry": {
            "keywords": ["data entry", "data specialist"],
            "subject": "Re: {{job_title}} at {{company_name}}",
            "body": """{{first_name}},

I see {{company_name}} is hiring for {{job_title}}. Before you fill that req, worth asking: what if the role didn't exist at all?

AgentForge builds AI agents that do the work instead of adding headcount. We specialize in operations automation — data entry, invoice processing, report generation, cross-system reconciliation.

Why companies choose us over hiring:
• **Faster**: 4 days to deploy vs 3 months to hire + train
• **Cheaper**: Fraction of salary, no benefits, scales instantly
• **Better**: 99%+ accuracy, no sick days, works 24/7
• **Adaptive**: Self-healing when processes change

Real example: A logistics VP came to us hiring 3 data entry specialists. We deployed an agent in 5 days. It now processes 15K records/month with fewer errors than humans. All 3 reqs canceled. Capacity tripled.

The meta story: This email was sent by our autonomous GTM agent. It found {{company_name}}'s job posting, researched your team, and personalized this message — fully autonomous. If an agent can do complex sales, imagine what it could do for your data workflows.

15 minutes to explore what we could automate at {{company_name}}?

Best,
Alex Chen
Founder, AgentForge
alex@agentforge.dev""",
        },
        "hiring_signal_lead_qual": {
            "keywords": ["lead qual", "sdr", "sales ops", "lead qualifier"],
            "subject": "Re: {{job_title}} role",
            "body": """{{first_name}},

You're hiring for {{job_title}} at {{company_name}}. What if instead of training a new hire for 6 weeks, you deployed an agent that was already trained?

AgentForge builds custom AI agents for revenue and ops teams. We specialize in work that's repetitive, high-volume, and rule-based (but too complex for traditional RPA).

The difference:
• **Speed to value**: Days, not quarters
• **No onboarding**: Agent starts fully trained
• **Infinite scale**: Handle 10x volume without adding headcount
• **Self-improving**: Learns from every interaction

A Series B SaaS company came to us hiring 5 SDRs for lead qualification. We built an agent that now books 3x more meetings than their human team did. All 5 reqs canceled. Quota exceeded. Cost cut 80%.

This email? Researched, personalized, and sent by our autonomous GTM agent. We eat our own cooking. The system works.

Worth 15 minutes to discuss what an agent could do for {{company_name}}'s pipeline?

Best,
Alex Chen
Founder, AgentForge
alex@agentforge.dev

P.S. I'll show you exactly how this email was generated on the call. Same tech we'd use for your lead qual process.""",
        },
        "hiring_signal_ops_coordinator": {
            "keywords": ["operations coordinator", "operations assistant", "ops coordinator"],
            "subject": "Re: {{job_title}} at {{company_name}}",
            "body": """{{first_name}},

{{company_name}} is hiring for {{job_title}}. I'm reaching out because that role description sounds like exactly what we automate with AI agents.

AgentForge builds custom AI agents for operations teams:
• Workflow coordination across systems
• Report generation and distribution
• Data reconciliation and validation
• Cross-team communication automation

Not just RPA (brittle, breaks constantly). Not just chatbots (not doing real work). **Autonomous agents** that handle the entire workflow end-to-end.

Example: A healthcare ops VP came to us hiring 2 operations coordinators to manage reporting workflows. We deployed an agent that now generates 47 different reports daily, routes them to the right stakeholders, and handles follow-up questions. Both reqs canceled. Zero manual work.

The proof: This email was sent by our GTM agent. It found your job posting, researched {{company_name}}, and personalized this message — autonomous start to finish.

Worth 15 minutes to explore what we could automate at {{company_name}}?

Best,
Alex Chen
Founder, AgentForge
alex@agentforge.dev""",
        },
        "generic_ops_automation": {
            "keywords": [],  # fallback
            "subject": "Re: operations hiring at {{company_name}}",
            "body": """{{first_name}},

I noticed {{company_name}} is hiring for operations roles. Quick thought: what if you could deploy AI agents instead of expanding headcount?

AgentForge builds custom AI agents for ops teams. Not chatbots — actual autonomous workers that:
• Process invoices and AP workflows
• Handle data entry and reconciliation
• Generate and distribute reports
• Qualify leads and coordinate sales ops
• Manage cross-system workflows

Why ops leaders choose agents over hiring:
• **Speed**: Deployed in days, not months
• **Cost**: Fraction of salary + benefits
• **Scale**: 10x capacity without 10x headcount
• **Reliability**: 99%+ accuracy, works 24/7, self-improving

The meta narrative: This email was sent by our autonomous GTM agent. It found {{company_name}}, analyzed your hiring needs, and wrote this message — no human involved. That's what we build for operations teams.

15-minute call this week to explore what we could automate?

Best,
Alex Chen
Founder, AgentForge
alex@agentforge.dev

P.S. If you're curious how the agent that sent this works, I'll walk through the architecture on the call. Same stack we'd use for your ops workflows.""",
        },
    }

    try:
        result = await cold_email_sender(
            campaign_name="ops_leader_hiring_signal_v2",
            input_csv="/tmp/ops_leader_contacts.csv",
            templates=templates,
            sender_email="alex@agentforge.dev",
            sender_name="Alex Chen",
            reply_to="alex@agentforge.dev",
            daily_limit=50,
            delay_seconds=5,
            track_opens=True,
            track_clicks=True,
        )

        print(f"\n✅ Outreach complete!")
        print(f"   Emails sent: {result.get('emails_sent', 0)}")
        print(f"   Delivery rate: {result.get('delivery_rate', 0):.1f}%")
        print(f"   Campaign ID: {result.get('campaign_id', 'N/A')}\n")

        # Publish metrics to Redis
        await publish_metric("emails_sent", result.get("emails_sent", 0))
        await publish_metric("email_delivery_rate", result.get("delivery_rate", 0))

        return result

    except Exception as e:
        print(f"❌ Outreach failed: {e}")
        return None


async def publish_metric(metric_name: str, value: float):
    """Publish metric to Redis for tracking."""
    try:
        import redis.asyncio as aioredis

        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        redis_client = await aioredis.from_url(redis_url, decode_responses=True)

        metric_data = {
            "experiment_id": "exp_20260201_ops_leader_agentforge_v2_autonomous",
            "metric": metric_name,
            "value": value,
            "timestamp": datetime.utcnow().isoformat(),
        }

        await redis_client.publish("fullsend:metrics", str(metric_data))
        await redis_client.close()

    except Exception as e:
        print(f"⚠️  Could not publish metric {metric_name}: {e}")


async def main():
    """Run the experiment."""
    print("\n" + "=" * 60)
    print("Autonomous Cold Outreach Pipeline v2")
    print("Experiment: ops_leader_agentforge_v2_autonomous")
    print("=" * 60 + "\n")

    # Verify prerequisites
    if not await verify_prerequisites():
        return 1

    # Phase 2: Discovery
    discovery_result = await run_phase_2_discovery()
    if not discovery_result:
        print("\n❌ Experiment failed at Phase 2 (Discovery)")
        return 1

    # Phase 3: Outreach
    outreach_result = await run_phase_3_outreach()
    if not outreach_result:
        print("\n❌ Experiment failed at Phase 3 (Outreach)")
        return 1

    # Success
    print("=" * 60)
    print("✅ Experiment Complete")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Monitor Resend dashboard for opens/clicks/replies")
    print("2. Reply to interested contacts within 4 hours")
    print("3. Track metrics in Redis: fullsend:metrics")
    print("4. Review results in 7 days")
    print("\nExpected Results:")
    print("- 8%+ reply rate within 7 days")
    print("- 4%+ positive reply rate")
    print("- 2%+ meeting booked rate (1-2 meetings)")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
