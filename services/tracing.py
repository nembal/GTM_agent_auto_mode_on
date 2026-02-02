"""Weave tracing helpers with safe, lazy initialization and Redis LLM call events."""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, TypeVar

try:
    import weave
except Exception:
    weave = None

try:
    import redis
    _redis_client: redis.Redis | None = None
except Exception:
    redis = None
    _redis_client = None

_init_attempted = False
_enabled = False

T = TypeVar("T")

LLM_CALLS_CHANNEL = "fullsend:llm_calls"


def _get_redis() -> "redis.Redis | None":
    """Get or create Redis client for LLM call events."""
    global _redis_client
    if redis is None:
        return None
    if _redis_client is None:
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            _redis_client = redis.from_url(redis_url, decode_responses=True)
            _redis_client.ping()  # Test connection
        except Exception:
            _redis_client = None
    return _redis_client


def _publish_llm_event(
    event_type: str,
    name: str,
    trace_meta: dict[str, Any] | None = None,
    duration_ms: float | None = None,
    error: str | None = None,
) -> None:
    """Publish LLM call event to Redis for dashboard visibility."""
    client = _get_redis()
    if client is None:
        return
    
    try:
        event = {
            "type": event_type,  # "llm_start" or "llm_complete"
            "source": name.split(".")[1] if "." in name else name,  # e.g., "orchestrator" from "llm.orchestrator"
            "operation": name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "meta": trace_meta or {},
        }
        if duration_ms is not None:
            event["duration_ms"] = round(duration_ms, 1)
        if error:
            event["error"] = error
        
        client.publish(LLM_CALLS_CHANNEL, json.dumps(event))
    except Exception:
        pass  # Don't fail the main operation if Redis fails


def _is_disabled() -> bool:
    return os.getenv("WEAVE_DISABLED") == "1"


def init_tracing(project: str | None = None) -> None:
    """Initialize Weave tracing once. Fail silently if unavailable."""
    global _init_attempted, _enabled
    if _init_attempted:
        return
    _init_attempted = True

    if _is_disabled() or weave is None:
        _enabled = False
        return

    try:
        weave.init(project or os.getenv("WEAVE_PROJECT", "fullsend"))
        _enabled = True
    except Exception:
        _enabled = False


def trace_call(
    name: str,
    fn: Callable[..., T],
    *args: Any,
    trace_meta: dict[str, Any] | None = None,
    **kwargs: Any,
) -> T:
    """Trace a synchronous call when Weave is enabled."""
    init_tracing()
    
    # Publish LLM start event to Redis (for llm.* operations)
    is_llm = name.startswith("llm.")
    if is_llm:
        _publish_llm_event("llm_start", name, trace_meta)
    
    start_time = time.time()
    error_msg = None
    
    try:
        if not _enabled or weave is None:
            return fn(*args, **kwargs)

        @weave.op(name=name)
        def _wrapped(*args: Any, _trace_meta: dict[str, Any] | None = None, **kwargs: Any) -> T:
            return fn(*args, **kwargs)

        return _wrapped(*args, _trace_meta=trace_meta, **kwargs)
    except Exception as e:
        error_msg = str(e)
        raise
    finally:
        if is_llm:
            duration_ms = (time.time() - start_time) * 1000
            _publish_llm_event("llm_complete", name, trace_meta, duration_ms, error_msg)


async def trace_call_async(
    name: str,
    fn: Callable[..., Awaitable[T]],
    *args: Any,
    trace_meta: dict[str, Any] | None = None,
    **kwargs: Any,
) -> T:
    """Trace an async call when Weave is enabled."""
    init_tracing()
    
    # Publish LLM start event to Redis (for llm.* operations)
    is_llm = name.startswith("llm.")
    if is_llm:
        _publish_llm_event("llm_start", name, trace_meta)
    
    start_time = time.time()
    error_msg = None
    
    try:
        if not _enabled or weave is None:
            return await fn(*args, **kwargs)

        @weave.op(name=name)
        async def _wrapped(
            *args: Any, _trace_meta: dict[str, Any] | None = None, **kwargs: Any
        ) -> T:
            return await fn(*args, **kwargs)

        return await _wrapped(*args, _trace_meta=trace_meta, **kwargs)
    except Exception as e:
        error_msg = str(e)
        raise
    finally:
        if is_llm:
            duration_ms = (time.time() - start_time) * 1000
            _publish_llm_event("llm_complete", name, trace_meta, duration_ms, error_msg)
