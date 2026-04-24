"""PyMOLish — curated PyMOL command extension library.

PyMOL discovers plugins via :func:`__init_plugin__`; importing this module is
cheap by design — heavy dependencies are loaded lazily from inside each
extension sub-package only when :func:`__init_plugin__` runs.
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core.registry import CommandInfo

__version__ = "1.0.0"

_EXTENSION_PACKAGE = "pymolish.extensions"
_META_CATEGORY = "Meta"


def __init_plugin__(app: object | None = None) -> None:
    """Entry point invoked by PyMOL when the plugin is loaded.

    Walks every sub-package under :mod:`pymolish.extensions` and calls its
    ``__init_plugin__`` if defined. Registers the ``pymolish_*`` meta-commands.
    """
    _register_meta_commands()
    _bootstrap_extensions(app)


def _bootstrap_extensions(app: object | None) -> None:
    """Import every extension sub-package and run its ``__init_plugin__``."""
    from .core.logging import plog

    try:
        package = importlib.import_module(_EXTENSION_PACKAGE)
    except ImportError as exc:
        plog("bootstrap", f"extensions package missing: {exc}", "error")
        return

    for module_info in pkgutil.iter_modules(package.__path__):
        if not module_info.ispkg:
            continue
        full_name = f"{_EXTENSION_PACKAGE}.{module_info.name}"
        try:
            module = importlib.import_module(full_name)
        except ImportError as exc:
            plog("bootstrap", f"failed to import {full_name}: {exc}", "error")
            continue
        initializer = getattr(module, "__init_plugin__", None)
        if callable(initializer):
            try:
                initializer(app)
            except Exception as exc:  # noqa: BLE001
                plog("bootstrap", f"{full_name}.__init_plugin__ failed: {exc}", "error")


def _register_meta_commands() -> None:
    """Register the ``pymolish_*`` meta-commands exposed to PyMOL."""
    from .core.autocompletion import AutocompletionRegistry
    from .core.registry import CommandRegistry

    registry = CommandRegistry.instance()

    meta_specs = [
        (
            "pymolish_list",
            pymolish_list,
            "List all registered commands, optionally filtered by category",
            ["pymolish_list", "pymolish_list I/O"],
            ["meta", "discovery"],
        ),
        (
            "pymolish_help",
            pymolish_help,
            "Print detailed help for a registered command",
            ["pymolish_help load_files"],
            ["meta", "help"],
        ),
        (
            "pymolish_search",
            pymolish_search,
            "Search commands by name, description, or tags",
            ["pymolish_search export", "pymolish_search color"],
            ["meta", "search"],
        ),
        (
            "pymolish_categories",
            pymolish_categories,
            "List categories with command counts",
            ["pymolish_categories"],
            ["meta", "discovery"],
        ),
        (
            "pymolish_version",
            pymolish_version,
            "Show pymolish version and number of loaded commands",
            ["pymolish_version"],
            ["meta", "version"],
        ),
    ]

    for name, func, description, examples, tags in meta_specs:
        if name in registry:
            continue
        registry.register(
            name,
            func,
            category=_META_CATEGORY,
            description=description,
            examples=examples,
            since=__version__,
            tags=tags,
        )

    AutocompletionRegistry.instance().apply()


def pymolish_list(category: str | None = None) -> list[str]:
    """Print registered commands, optionally filtered by ``category``.

    Returns:
        List of command names printed (useful for programmatic callers).
    """
    from .core.logging import plog
    from .core.registry import CommandRegistry

    registry = CommandRegistry.instance()
    entries = registry.list_commands(category)
    if not entries:
        plog("list", f"no commands registered{_suffix_for_category(category)}")
        return []

    current: str | None = None
    for info in entries:
        if info.category != current:
            current = info.category
            plog("list", f"== {current} ==")
        plog("list", f"  {info.name:<28} {info.description}")
    return [info.name for info in entries]


def pymolish_help(name: str) -> CommandInfo | None:
    """Print detailed help for a registered command.

    Args:
        name: Command name, e.g. ``"load_files"``.

    Returns:
        The :class:`CommandInfo` when found, ``None`` otherwise.
    """
    from .core.logging import plog
    from .core.registry import CommandRegistry

    info = CommandRegistry.instance().get(name)
    if info is None:
        plog("help", f"command {name!r} is not registered", "warn")
        return None

    plog("help", f"{info.name} — {info.description}")
    plog("help", f"  category: {info.category}   since: {info.since}")
    plog("help", f"  usage: {info.usage}")
    if info.examples:
        plog("help", "  examples:")
        for example in info.examples:
            plog("help", f"    {example}")
    if info.see_also:
        plog("help", f"  see also: {', '.join(info.see_also)}")
    if info.tags:
        plog("help", f"  tags: {', '.join(info.tags)}")
    docstring = (info.function.__doc__ or "").strip()
    if docstring:
        plog("help", "  docstring:")
        for line in docstring.splitlines():
            plog("help", f"    {line}")
    return info


def pymolish_search(term: str) -> list[str]:
    """Search registered commands by ``term`` across names, descriptions, tags."""
    from .core.logging import plog
    from .core.registry import CommandRegistry

    matches = CommandRegistry.instance().search(term)
    if not matches:
        plog("search", f"no matches for {term!r}")
        return []
    for info in matches:
        plog("search", f"  {info.name:<28} {info.description}")
    return [info.name for info in matches]


def pymolish_categories() -> dict[str, int]:
    """Print each category with the number of commands it contains."""
    from .core.logging import plog
    from .core.registry import CommandRegistry

    registry = CommandRegistry.instance()
    counts: dict[str, int] = {}
    for info in registry.list_commands():
        counts[info.category] = counts.get(info.category, 0) + 1
    for cat in sorted(counts):
        plog("categories", f"  {cat:<20} {counts[cat]:>3} commands")
    return counts


def pymolish_version() -> str:
    """Print the pymolish version and loaded command count."""
    from .core.logging import plog
    from .core.registry import CommandRegistry

    total = len(CommandRegistry.instance())
    plog("version", f"pymolish {__version__} ({total} commands loaded)")
    return __version__


def _suffix_for_category(category: str | None) -> str:
    return f" in category {category!r}" if category else ""


__all__ = [
    "__init_plugin__",
    "__version__",
    "pymolish_categories",
    "pymolish_help",
    "pymolish_list",
    "pymolish_search",
    "pymolish_version",
]
