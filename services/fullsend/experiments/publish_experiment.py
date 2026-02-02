#!/usr/bin/env python3
"""
Helper script to publish experiments to Redis.

Usage:
    python experiments/publish_experiment.py <experiment_id>

Example:
    python experiments/publish_experiment.py exp_20260201_ops_leader_agentforge
"""

import sys
import subprocess
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: python experiments/publish_experiment.py <experiment_id>")
        print("\nAvailable experiments:")
        exp_dir = Path(__file__).parent
        for yaml_file in exp_dir.glob("exp_*.yaml"):
            exp_id = yaml_file.stem
            print(f"  - {exp_id}")
        sys.exit(1)

    exp_id = sys.argv[1]
    exp_file = Path(__file__).parent / f"{exp_id}.yaml"

    if not exp_file.exists():
        print(f"Error: {exp_file} not found")
        sys.exit(1)

    print(f"Publishing experiment: {exp_id}")
    print(f"File: {exp_file}")
    print()

    # Run redis publish script
    script_path = Path(__file__).parent.parent.parent / "scripts" / "redis_publish.sh"
    cmd = [str(script_path), "publish_experiment_full", f"experiments/{exp_id}.yaml"]

    result = subprocess.run(cmd, capture_output=True, text=True)

    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)

    if result.returncode == 0:
        print(f"\n✓ Experiment published successfully!")
        print(f"\nNext steps:")
        print(f"1. Wait for scheduled run (check YAML for schedule)")
        print(f"2. OR trigger manually:")
        print(f"   SCHEDULE_MODE=trigger uv run python -m services.executor.main")
        print(f"3. Monitor results in Redis:")
        print(f"   redis-cli GET 'experiments:{exp_id}:results'")
    else:
        print(f"\n✗ Failed to publish experiment")
        sys.exit(1)


if __name__ == "__main__":
    main()
