"""Central command registry for pymolish.

The registry is the single place where commands are tracked and exposed to the
PyMOL terminal. Extension sub-packages register via
:meth:`CommandRegistry.register`; the registry then calls ``cmd.extend`` so the
command becomes callable from the PyMOL prompt.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import ClassVar

from pymol import cmd

from .logging import plog
from .types import CategoryLike


@dataclass(frozen=True)
class CommandInfo:
    """Metadata for a registered pymolish command."""

    name: str
    function: Callable[..., object]
    category: str
    description: str
    usage: str
    examples: list[str] = field(default_factory=list)
    since: str = "1.0.0"
    see_also: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    module: str = ""


class CommandRegistry:
    """Singleton registry for all pymolish commands.

    Use :meth:`CommandRegistry.instance` to access the shared registry. Direct
    instantiation is allowed for tests but not expected in production code.
    """

    _instance: ClassVar[CommandRegistry | None] = None

    def __init__(self) -> None:
        """Initialize an empty registry. Prefer :meth:`instance` for normal use."""
        self._commands: dict[str, CommandInfo] = {}

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Disallow subclassing — the registry is meant to be used as-is."""
        raise TypeError("CommandRegistry may not be subclassed")

    @classmethod
    def instance(cls) -> CommandRegistry:
        """Return the process-wide registry, creating it on first access."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def _reset_for_tests(cls) -> None:
        """Drop the singleton — used by the test harness to isolate runs."""
        cls._instance = None

    def register(
        self,
        name: str,
        function: Callable[..., object],
        *,
        category: CategoryLike,
        description: str,
        usage: str | None = None,
        examples: list[str] | None = None,
        since: str = "1.0.0",
        see_also: list[str] | None = None,
        tags: list[str] | None = None,
        auto_extend: bool = True,
    ) -> CommandInfo:
        """Register ``function`` under ``name`` and expose it to PyMOL.

        Args:
            name: PyMOL command name (used from the PyMOL prompt).
            function: Callable implementing the command.
            category: Category label — accepts :class:`Category` or a string.
            description: One-line summary displayed in listings.
            usage: Optional explicit usage string. When omitted, it is derived
                from the function signature.
            examples: PyMOL terminal examples shown by ``pymolish_help``.
            since: Version string when the command was introduced.
            see_also: Related command names for cross-referencing.
            tags: Searchable tags surfaced by ``pymolish_search``.
            auto_extend: When ``True`` (default) call ``cmd.extend`` so PyMOL
                picks the command up. Set to ``False`` for test scenarios.

        Returns:
            The stored :class:`CommandInfo`.

        Raises:
            ValueError: ``name`` is already registered.
        """
        if name in self._commands:
            raise ValueError(f"command {name!r} is already registered")

        info = CommandInfo(
            name=name,
            function=function,
            category=str(category),
            description=description,
            usage=usage or _infer_usage(name, function),
            examples=list(examples or []),
            since=since,
            see_also=list(see_also or []),
            tags=list(tags or []),
            module=getattr(function, "__module__", ""),
        )
        self._commands[name] = info

        if auto_extend:
            try:
                cmd.extend(name, function)
            except Exception as exc:  # noqa: BLE001
                plog("registry", f"cmd.extend({name!r}) failed: {exc}", "error")

        return info

    def unregister(self, name: str) -> None:
        """Remove ``name`` from the registry (does not detach from ``cmd``)."""
        self._commands.pop(name, None)

    def get(self, name: str) -> CommandInfo | None:
        """Return the :class:`CommandInfo` for ``name`` or ``None``."""
        return self._commands.get(name)

    def list_commands(self, category: CategoryLike | None = None) -> list[CommandInfo]:
        """Return all registered commands, optionally filtered by category."""
        values = list(self._commands.values())
        if category is None:
            return sorted(values, key=lambda info: (info.category, info.name))
        wanted = str(category)
        return sorted(
            (info for info in values if info.category == wanted),
            key=lambda info: info.name,
        )

    def search(self, term: str) -> list[CommandInfo]:
        """Case-insensitive search across name, description, and tags."""
        needle = term.strip().lower()
        if not needle:
            return []
        matches: list[CommandInfo] = []
        for info in self._commands.values():
            haystack = " ".join(
                [info.name, info.description, " ".join(info.tags)]
            ).lower()
            if needle in haystack:
                matches.append(info)
        return sorted(matches, key=lambda info: info.name)

    def categories(self) -> list[str]:
        """Return the sorted set of registered category labels."""
        return sorted({info.category for info in self._commands.values()})

    def __len__(self) -> int:  # pragma: no cover — trivial
        """Return the number of registered commands."""
        return len(self._commands)

    def __contains__(self, name: object) -> bool:  # pragma: no cover — trivial
        """Return ``True`` when a command with ``name`` is registered."""
        return isinstance(name, str) and name in self._commands


def _infer_usage(name: str, function: Callable[..., object]) -> str:
    """Build a simple usage string from ``function``'s signature."""
    try:
        sig = inspect.signature(function)
    except (TypeError, ValueError):
        return name
    parts: list[str] = [name]
    for pname, param in sig.parameters.items():
        if param.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            continue
        if param.default is inspect.Parameter.empty:
            parts.append(f"<{pname}>")
        else:
            parts.append(f"[{pname}={param.default!r}]")
    return " ".join(parts)
