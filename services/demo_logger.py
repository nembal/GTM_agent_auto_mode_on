"""Demo logging helper for dashboard events."""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = REPO_ROOT / "demo" / "dashboard" / "logs.txt"
ENV_FLAG = "DEMO_LOGS_ENABLED"
_LOCK = Lock()


def _is_enabled() -> bool:
    value = os.getenv(ENV_FLAG, "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def log_event(event: str, payload: dict[str, Any] | None = None) -> None:
    """Append a JSON line for the demo dashboard logs."""
    if not _is_enabled():
        return

    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        data: dict[str, Any] = {"event": event, "ts": datetime.now(UTC).isoformat()}
        if payload:
            data.update(payload)
        line = json.dumps(data, ensure_ascii=True)
        with _LOCK:
            LOG_PATH.open("a", encoding="utf-8").write(line + "\n")
    except Exception as exc:
        logger.debug("Demo log write failed: %s", exc)
