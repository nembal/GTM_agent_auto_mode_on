"""Run roundtable from CLI: python -m roundtable "Topic: ..." """

import os
import sys

# Allow running as python -m roundtable from repo root (services/roundtable/ or GTM_agent_auto_mode_on/services/roundtable/)
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    from .runner import run_roundtable

    topic = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else None
    if not topic:
        print("Usage: python -m roundtable \"Topic: your GTM idea or question\"", file=sys.stderr)
        sys.exit(1)

    max_rounds = int(os.getenv("ROUNDTABLE_MAX_ROUNDS", "2"))
    result = run_roundtable(topic, max_rounds=max_rounds)

    print(result["summary"])
