"""Weave tracing helpers with safe, lazy initialization."""

from __future__ import annotations

import os
from typing import Any, Awaitable, Callable, TypeVar

try:
    import weave
except Exception:
    weave = None

_init_attempted = False
_enabled = False

T = TypeVar("T")


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
    if not _enabled or weave is None:
        return fn(*args, **kwargs)

    @weave.op(name=name)
    def _wrapped(*args: Any, _trace_meta: dict[str, Any] | None = None, **kwargs: Any) -> T:
        return fn(*args, **kwargs)

    return _wrapped(*args, _trace_meta=trace_meta, **kwargs)


async def trace_call_async(
    name: str,
    fn: Callable[..., Awaitable[T]],
    *args: Any,
    trace_meta: dict[str, Any] | None = None,
    **kwargs: Any,
) -> T:
    """Trace an async call when Weave is enabled."""
    init_tracing()
    if not _enabled or weave is None:
        return await fn(*args, **kwargs)

    @weave.op(name=name)
    async def _wrapped(
        *args: Any, _trace_meta: dict[str, Any] | None = None, **kwargs: Any
    ) -> T:
        return await fn(*args, **kwargs)

    return await _wrapped(*args, _trace_meta=trace_meta, **kwargs)
