#!/usr/bin/env python3
"""
Publish FULLSEND experiment to Redis.
Usage: python publish_experiment.py <experiment_yaml_path>
"""
import asyncio
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

import redis.asyncio as redis
import yaml

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CHANNEL_TO_ORCHESTRATOR = "fullsend:to_orchestrator"


async def publish_experiment(yaml_path: Path):
    """Publish experiment to Redis and notify orchestrator."""
    # Load YAML
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    experiment = data.get("experiment", {})
    exp_id = experiment.get("id")

    if not exp_id:
        print("Error: No experiment ID found in YAML")
        sys.exit(1)

    # Connect to Redis
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)

    try:
        await redis_client.ping()
        print(f"Connected to Redis at {REDIS_URL}")

        # Store experiment in Redis
        exp_key = f"experiments:{exp_id}"
        await redis_client.set(exp_key, json.dumps(experiment))
        print(f"Stored experiment: {exp_key}")

        # Store metrics spec if present
        metrics = experiment.get("metrics", [])
        if metrics:
            metrics_key = f"metrics_specs:{exp_id}"
            await redis_client.set(metrics_key, json.dumps(metrics))
            print(f"Stored metrics: {metrics_key}")

        # Store schedule if present
        schedule = experiment.get("execution", {}).get("schedule")
        timezone = experiment.get("execution", {}).get("timezone", "UTC")
        if schedule:
            schedule_key = f"schedules:{exp_id}"
            schedule_data = {
                "experiment_id": exp_id,
                "cron": schedule,
                "timezone": timezone,
                "enabled": True,
            }
            await redis_client.set(schedule_key, json.dumps(schedule_data))
            print(f"Stored schedule: {schedule_key}")

        # Notify orchestrator
        notification = {
            "type": "experiment_ready",
            "source": "fullsend",
            "experiment_id": exp_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "notify_channel": "1467242749848981648",  # From the request context
            "message": f"Experiment {exp_id} is ready. Manual steps required: source CTO emails from LinkedIn Sales Navigator before execution.",
        }
        await redis_client.publish(CHANNEL_TO_ORCHESTRATOR, json.dumps(notification))
        print(f"Notified orchestrator: experiment_ready")

        print(f"\n✓ Experiment {exp_id} published successfully!")
        print(f"  - File: {yaml_path}")
        print(f"  - Hypothesis: {experiment.get('hypothesis', 'N/A')[:100]}...")
        print(f"  - Target size: {experiment.get('target', {}).get('size', 'N/A')}")
        print(f"  - Schedule: {schedule or 'Manual trigger only'}")

    finally:
        await redis_client.aclose()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python publish_experiment.py <experiment_yaml_path>")
        sys.exit(1)

    yaml_path = Path(sys.argv[1])
    if not yaml_path.exists():
        print(f"Error: File not found: {yaml_path}")
        sys.exit(1)

    asyncio.run(publish_experiment(yaml_path))
