#!/usr/bin/env python3
"""
Store tactical learning in Redis.
Usage: python store_learning.py "<learning_text>" <experiment_id>
"""
import asyncio
import json
import os
import sys
from datetime import UTC, datetime

import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


async def store_learning(learning_text: str, experiment_id: str):
    """Store a tactical learning in Redis."""
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)

    try:
        await redis_client.ping()
        print(f"Connected to Redis at {REDIS_URL}")

        # Create learning entry
        timestamp = datetime.now(UTC).isoformat()
        learning_key = f"learnings:tactical:{experiment_id}:{timestamp}"
        learning_data = {
            "text": learning_text,
            "experiment_id": experiment_id,
            "timestamp": timestamp,
            "type": "tactical",
        }

        # Store learning
        await redis_client.set(learning_key, json.dumps(learning_data))
        print(f"Stored learning: {learning_key}")

        # Add to sorted set for retrieval
        await redis_client.zadd(
            "learnings:tactical:index",
            {learning_key: datetime.now(UTC).timestamp()},
        )
        print(f"Indexed learning in sorted set")

        print(f"\n✓ Learning stored successfully!")
        print(f"  - Experiment: {experiment_id}")
        print(f"  - Text: {learning_text[:100]}...")

    finally:
        await redis_client.aclose()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Usage: python store_learning.py "<learning_text>" <experiment_id>')
        sys.exit(1)

    learning_text = sys.argv[1]
    experiment_id = sys.argv[2]

    asyncio.run(store_learning(learning_text, experiment_id))
