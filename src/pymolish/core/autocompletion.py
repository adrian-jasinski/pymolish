"""Argument autocompletion registry for pymolish commands.

Each category registers per-argument completers during its ``__init_plugin__``.
Calling :meth:`AutocompletionRegistry.apply` pushes the accumulated entries
into ``cmd.auto_arg`` so PyMOL's tab completion picks them up.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import ClassVar

from pymol import cmd

from .logging import plog

Completer = Callable[[str], Iterable[str]]
"""A completer takes the current token and returns completion candidates."""


@dataclass(frozen=True)
class Completion:
    """A single autocompletion binding for one argument slot."""

    command: str
    position: int
    completer: Completer
    label: str = ""


class _BuiltinCompleters:
    """Small collection of generic completers commonly needed by commands."""

    @staticmethod
    def directory(token: str) -> list[str]:
        """Complete directory paths relative to the current token."""
        from pathlib import Path

        base = Path(token or ".").expanduser()
        if base.is_dir():
            parent = base
        elif base.parent.exists():
            parent = base.parent
        else:
            parent = Path(".")
        try:
            return sorted(str(p) + "/" for p in parent.iterdir() if p.is_dir())
        except OSError:
            return []

    @staticmethod
    def format(token: str) -> list[str]:
        """Complete supported file extensions used by I/O commands."""
        known = ["pdb", "cif", "sdf", "mol", "mol2", "xyz", "pse", "mmtf"]
        return [fmt for fmt in known if fmt.startswith(token.lower())]

    @staticmethod
    def object_name(token: str) -> list[str]:
        """Complete loaded PyMOL object names."""
        try:
            names = cmd.get_object_list() or []
        except Exception:  # noqa: BLE001
            return []
        return [n for n in names if n.startswith(token)]

    @staticmethod
    def group_name(token: str) -> list[str]:
        """Complete loaded PyMOL group names."""
        try:
            names = cmd.get_names("objects") or []
        except Exception:  # noqa: BLE001
            return []
        return [n for n in names if n.startswith(token) and _is_group(n)]


def _is_group(name: str) -> bool:
    try:
        return cmd.get_type(name) == "object:group"
    except Exception:  # noqa: BLE001
        return False


class AutocompletionRegistry:
    """Singleton registry of argument completers awaiting installation."""

    _instance: ClassVar[AutocompletionRegistry | None] = None
    completers: ClassVar[type[_BuiltinCompleters]] = _BuiltinCompleters

    def __init__(self) -> None:
        """Initialize an empty registry. Prefer :meth:`instance` for normal use."""
        self._entries: list[Completion] = []
        self._applied: bool = False

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Prevent subclassing — the registry is meant to be used as-is."""
        raise TypeError("AutocompletionRegistry may not be subclassed")

    @classmethod
    def instance(cls) -> AutocompletionRegistry:
        """Return the process-wide autocompletion registry."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def _reset_for_tests(cls) -> None:
        """Drop the singleton — used by the test harness to isolate runs."""
        cls._instance = None

    def register(
        self,
        command: str,
        position: int,
        completer: Completer,
        label: str = "",
    ) -> None:
        """Queue a completer for ``command`` argument at ``position``."""
        self._entries.append(
            Completion(
                command=command,
                position=position,
                completer=completer,
                label=label,
            )
        )

    def entries(self) -> list[Completion]:
        """Return a copy of all queued completions."""
        return list(self._entries)

    def apply(self) -> None:
        """Install queued completions into ``cmd.auto_arg``."""
        auto_arg = getattr(cmd, "auto_arg", None)
        if auto_arg is None:
            plog("autocomplete", "cmd.auto_arg unavailable; skipping apply()", "warn")
            return
        for entry in self._entries:
            while len(auto_arg) <= entry.position:
                auto_arg.append({})
            slot = auto_arg[entry.position]
            slot[entry.command] = [entry.completer, entry.label]
        self._applied = True


@dataclass
class CategoryCompletions:
    """Helper that batches registrations for a single category.

    Not used by the core; provided for extension authors who want a tidy local
    DSL.
    """

    command: str
    registry: AutocompletionRegistry
    bindings: list[tuple[int, Completer, str]] = field(default_factory=list)

    def add(
        self,
        position: int,
        completer: Completer,
        label: str = "",
    ) -> CategoryCompletions:
        """Queue a binding and return ``self`` for chaining."""
        self.bindings.append((position, completer, label))
        return self

    def commit(self) -> None:
        """Flush queued bindings into the shared registry."""
        for position, completer, label in self.bindings:
            self.registry.register(self.command, position, completer, label)
        self.bindings.clear()
