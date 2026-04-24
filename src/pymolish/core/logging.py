"""Unified logging helper for the pymolish package.

All runtime console output inside ``pymolish`` should flow through :func:`plog`
so messages carry a consistent, grep-friendly ``[pext:<tag>]`` prefix.
"""

from __future__ import annotations

from .types import LogLevel

_PREFIX = "pext"


def plog(tag: str, message: str, level: LogLevel = "info") -> None:
    """Emit a prefixed log line to the PyMOL console.

    Args:
        tag: Short identifier for the originating subsystem (e.g. ``"io"``,
            ``"groups"``, ``"registry"``). Appears after the package prefix.
        message: Human-readable message body.
        level: ``"info"`` (default), ``"warn"``, or ``"error"``.
    """
    prefix = f"[{_PREFIX}:{tag}]"
    if level == "error":
        print(f"{prefix} ERROR: {message}")
    elif level == "warn":
        print(f"{prefix} WARNING: {message}")
    else:
        print(f"{prefix} {message}")
