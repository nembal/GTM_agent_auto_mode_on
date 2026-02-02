#!/usr/bin/env python3
"""
Manual execution script for exp_20260201_ops_leader_agentforge

Demonstrates two-phase workflow:
1. browserbase_email_finder - Discover contacts at target companies
2. cold_email_sender - Send personalized emails to discovered contacts

Usage:
    python experiments/run_ops_leader_experiment.py [--dry-run]

Options:
    --dry-run    Run email discovery but don't send emails (test mode)
"""

import sys
import yaml
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from browserbase_email_finder import browserbase_email_finder
from cold_email_sender import cold_email_sender


def load_experiment_spec():
    """Load experiment YAML spec."""
    spec_path = Path(__file__).parent / "exp_20260201_ops_leader_agentforge.yaml"
    with open(spec_path) as f:
        return yaml.safe_load(f)


def run_phase_1_discovery(companies, target_roles):
    """
    Phase 1: Discover email contacts at target companies.

    Returns:
        List of recipient dicts with: email, first_name, last_name, company, title, custom_fields
    """
    print("\n=== PHASE 1: EMAIL DISCOVERY ===\n")

    all_recipients = []

    for company_info in companies:
        company_name = company_info["name"]
        company_url = company_info["url"]
        industry = company_info["industry"]

        print(f"Researching: {company_name} ({company_url})")

        # Run browserbase_email_finder for each target role
        for role in target_roles:
            print(f"  → Looking for: {role}")

            result = browserbase_email_finder(
                company_name=company_name,
                company_url=company_url,
                target_role=role
            )

            if result["success"]:
                contacts = result["result"]["contacts"]
                print(f"    ✓ Found {len(contacts)} contacts")

                # Convert to recipient format for cold_email_sender
                for contact in contacts:
                    # Extract first/last name from full name
                    name_parts = contact["name"].split() if contact["name"] else ["", ""]
                    first_name = name_parts[0] if len(name_parts) > 0 else ""
                    last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

                    recipient = {
                        "email": contact["email"],
                        "first_name": first_name,
                        "last_name": last_name,
                        "company": company_name,
                        "title": contact["role"] or role,
                        "custom_fields": {
                            "industry": industry,
                            "source_url": contact["source_url"]
                        }
                    }
                    all_recipients.append(recipient)
            else:
                print(f"    ✗ Error: {result['error']}")

        print()

    print(f"Total contacts discovered: {len(all_recipients)}")
    print(f"Email discovery rate: {len([c for c in companies if any(r['company'] == c['name'] for r in all_recipients)]) / len(companies) * 100:.1f}%\n")

    return all_recipients


def run_phase_2_send(recipients, dry_run=False):
    """
    Phase 2: Send personalized emails to discovered contacts.

    Args:
        recipients: List of recipient dicts from phase 1
        dry_run: If True, print what would be sent but don't actually send
    """
    print("\n=== PHASE 2: EMAIL SENDING ===\n")

    if dry_run:
        print("🔍 DRY RUN MODE - No emails will be sent\n")
        print(f"Would send to {len(recipients)} recipients:\n")
        for i, r in enumerate(recipients[:5], 1):  # Show first 5
            print(f"{i}. {r['first_name']} {r['last_name']} ({r['title']}) at {r['company']}")
            print(f"   Email: {r['email']}")
            print()
        if len(recipients) > 5:
            print(f"... and {len(recipients) - 5} more\n")
        return

    # Email template from experiment spec
    template = {
        "subject": "Re: AI workforce deployment",
        "body": """Hi {{first_name}},

Your competitors are hiring more ops teams. You could be deploying AI agents instead.

I'm reaching out because {{company}} operates in {{industry}} where operational efficiency = competitive advantage. Most ops leaders I talk to waste 6 months evaluating AI vendors. We ship working agents in days, not quarters.

AgentForge is different: AI agents that build AI agents. It's meta, but it works. Proof? An autonomous agent found your email, wrote this message, and sent it. Same tech we'd deploy for your operations.

Three angles we're testing with ops leaders:

1. **Speed to value**: Deploy in days vs. 6-month pilot purgatory
2. **Meta proof**: This email was designed and sent by an agent—it's the product
3. **Operational AI**: Not chatbots. Process automation, data pipelines, workflow orchestration

{{company}} likely has:
- Manual data entry workflows eating hours/day
- Reporting dashboards that take a week to generate
- Cross-system reconciliation that's still Excel hell

We'd build the agents to fix them. Days, not months.

Worth a 15-minute call this week?

Best,
Alex Chen
Founder, AgentForge
alex@agentforge.dev

P.S. — If you're curious how an agent found your contact info and wrote this email, I'll show you the architecture on the call. It's the same stack we'd use for your ops workflows.
"""
    }

    send_options = {
        "sender_email": "alex@agentforge.dev",
        "sender_name": "Alex Chen",
        "daily_limit": 30,
        "delay_seconds": 3
    }

    print(f"Sending to {len(recipients)} recipients...")
    print(f"Campaign: ops_leader_agentforge_v1")
    print(f"Sender: {send_options['sender_name']} <{send_options['sender_email']}>")
    print()

    result = cold_email_sender(
        recipients=recipients,
        template=template,
        campaign_name="ops_leader_agentforge_v1",
        send_options=send_options
    )

    if result["success"]:
        stats = result["result"]["campaign_stats"]
        print(f"✓ Campaign complete!")
        print(f"  Sent: {stats['total_sent']}")
        print(f"  Failed: {stats['total_failed']}")
        print()
        print("Monitor replies at: alex@agentforge.dev")
        print("Track opens/clicks in Resend dashboard")
    else:
        print(f"✗ Campaign failed: {result['error']}")


def main():
    """Run the full experiment."""
    dry_run = "--dry-run" in sys.argv

    print("=" * 60)
    print("EXPERIMENT: exp_20260201_ops_leader_agentforge")
    print("=" * 60)

    # Load experiment spec
    spec = load_experiment_spec()
    experiment = spec["experiment"]

    print(f"\nHypothesis: {experiment['hypothesis'][:120]}...\n")

    # Phase 1: Discover emails
    companies = experiment["target"]["companies_to_research"]
    target_roles = experiment["execution"]["phase_1_find_emails"]["params"]["target_roles"]

    recipients = run_phase_1_discovery(companies, target_roles)

    if not recipients:
        print("⚠️  No contacts discovered. Check browserbase_email_finder configuration.")
        return

    # Phase 2: Send emails
    run_phase_2_send(recipients, dry_run=dry_run)

    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Monitor replies at alex@agentforge.dev (check every 4 hours)")
    print("2. Track metrics in Resend dashboard")
    print("3. Store learnings after 7 days using:")
    print("   ./scripts/redis_publish.sh store_learning '<insight>' exp_20260201_ops_leader_agentforge")


if __name__ == "__main__":
    main()
