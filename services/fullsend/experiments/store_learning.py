#!/usr/bin/env python3
"""
Helper script to store tactical learnings from experiments.

Usage:
    python experiments/store_learning.py <experiment_id>

Interactive mode - prompts for learning insights after experiment completion.

Example:
    python experiments/store_learning.py exp_20260201_ops_leader_agentforge
"""

import sys
import subprocess
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: python experiments/store_learning.py <experiment_id>")
        print("\nAvailable experiments:")
        exp_dir = Path(__file__).parent
        for yaml_file in exp_dir.glob("exp_*.yaml"):
            exp_id = yaml_file.stem
            print(f"  - {exp_id}")
        sys.exit(1)

    exp_id = sys.argv[1]
    exp_file = Path(__file__).parent / f"{exp_id}.yaml"

    if not exp_file.exists():
        print(f"Warning: {exp_file} not found (but you can still store learnings)")

    print("=" * 60)
    print(f"STORE LEARNINGS: {exp_id}")
    print("=" * 60)
    print()

    # Guide the user through capturing learnings
    print("Answer these questions to capture learnings:\n")

    learnings = []

    # 1. Core result
    print("1. What was the core result?")
    print("   Examples:")
    print("   - 'Reply rate: 12%, positive replies: 4, meetings booked: 2'")
    print("   - 'Email discovery rate: 85%, bounce rate: 3%'")
    result = input("   → ").strip()
    if result:
        learnings.append(f"Result: {result}")

    # 2. What worked
    print("\n2. What worked well?")
    print("   Examples:")
    print("   - 'Subject line \"Re: AI workforce\" got 45% open rate'")
    print("   - 'Manufacturing companies responded 2x better than logistics'")
    what_worked = input("   → ").strip()
    if what_worked:
        learnings.append(f"What worked: {what_worked}")

    # 3. What didn't work
    print("\n3. What didn't work?")
    print("   Examples:")
    print("   - 'Meta narrative confused non-technical ops leaders'")
    print("   - 'CFOs had 0% reply rate (wrong persona)'")
    what_didnt = input("   → ").strip()
    if what_didnt:
        learnings.append(f"What didn't work: {what_didnt}")

    # 4. Hypothesis validation
    print("\n4. Was the hypothesis validated? (yes/no/partially)")
    hypothesis = input("   → ").strip().lower()
    if hypothesis:
        learnings.append(f"Hypothesis: {hypothesis}")

    # 5. Next iteration
    print("\n5. What should we try next?")
    print("   Examples:")
    print("   - 'Scale to 100 contacts, test variant without meta narrative'")
    print("   - 'Focus only on VP Ops (not CFOs), add follow-up sequence'")
    next_step = input("   → ").strip()
    if next_step:
        learnings.append(f"Next: {next_step}")

    # 6. Free-form insight
    print("\n6. Any other insights?")
    other = input("   → ").strip()
    if other:
        learnings.append(other)

    if not learnings:
        print("\nNo learnings captured. Exiting.")
        sys.exit(0)

    # Combine into single learning string
    learning_text = " | ".join(learnings)

    print("\n" + "=" * 60)
    print("LEARNING TO STORE:")
    print("=" * 60)
    print(learning_text)
    print()

    confirm = input("Store this learning? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        sys.exit(0)

    # Store learning via redis_publish.sh
    script_path = Path(__file__).parent.parent.parent / "scripts" / "redis_publish.sh"
    cmd = [str(script_path), "store_learning", learning_text, exp_id]

    result = subprocess.run(cmd, capture_output=True, text=True)

    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)

    if result.returncode == 0:
        print("\n✓ Learning stored successfully!")
        print("\nView recent learnings:")
        print("  ./scripts/redis_publish.sh get_learnings 10")
    else:
        print("\n✗ Failed to store learning")
        sys.exit(1)


if __name__ == "__main__":
    main()
