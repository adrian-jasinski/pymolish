"""PyMOLish — curated PyMOL command extension library.

PyMOL discovers plugins via :func:`__init_plugin__`; importing this module is
cheap by design — optional dependencies are imported only when a command
needs them, never during plugin initialization or command registration.
"""

from __future__ import annotations

import importlib
import pkgutil
from types import ModuleType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core.registry import CommandInfo


def _read_version() -> str:
    """Single source of truth is pyproject.toml.

    Installed from the plugin ZIP -> ``_version.py`` stamped by
    ``scripts/build_plugin.py`` (checked first: a stale pip install of an
    older version in PyMOL's Python must not shadow the ZIP's version).
    Installed via pip/uv -> package metadata.
    """
    try:
        from ._version import __version__ as stamped

        return stamped
    except ImportError:
        pass
    try:
        from importlib.metadata import version

        return version("pymolish")
    except Exception:  # noqa: BLE001 - PackageNotFoundError or odd envs
        return "0+unknown"


__version__ = _read_version()

_EXTENSION_SUBPACKAGE = ".extensions"
_EXTENSION_ABSOLUTE = "pymolish.extensions"
_META_CATEGORY = "Meta"

_extensions_loaded: bool = False


def __init_plugin__(app: object | None = None) -> None:
    """Entry point invoked by PyMOL when the plugin is loaded.

    Walks every sub-package under :mod:`pymolish.extensions` and calls its
    ``__init_plugin__`` if defined. Registers the ``pymolish_*`` meta-commands.
    """
    _register_meta_commands()
    _bootstrap_extensions(app)


def _import_extensions_package() -> ModuleType | None:
    """Import the ``pymolish.extensions`` package, tolerating load context.

    PyMOL can load the plugin in a context where ``__package__`` is unset, which
    breaks the relative import. Fall back to the absolute name so extension
    discovery survives both the Plugin Manager and a plain ``import pymolish``.
    """
    from .core.logging import plog

    for module_name, anchor in (
        (_EXTENSION_SUBPACKAGE, __package__),
        (_EXTENSION_ABSOLUTE, None),
    ):
        if module_name.startswith(".") and not anchor:
            continue
        try:
            return importlib.import_module(module_name, anchor)
        except ImportError as exc:
            last_exc = exc
    plog("bootstrap", f"extensions package missing: {last_exc}", "error")
    return None


def _bootstrap_extensions(app: object | None) -> None:
    """Import every extension sub-package and run its ``__init_plugin__``."""
    from .core.logging import plog

    global _extensions_loaded

    package = _import_extensions_package()
    if package is None:
        return
    _extensions_loaded = True

    for module_info in pkgutil.iter_modules(package.__path__):
        if not module_info.ispkg:
            continue
        full_name = f"{package.__name__}.{module_info.name}"
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


def _ensure_extensions_loaded() -> None:
    """Bootstrap extension commands on demand if they are not registered yet.

    The discovery meta-commands call this so they list the full library even
    when PyMOL loaded the plugin in a way that ran the meta registration but
    never completed ``_bootstrap_extensions`` (e.g. an unusual plugin loader).
    The attempt runs at most once.
    """
    if _extensions_loaded:
        return
    _bootstrap_extensions(None)


def _register_meta_commands() -> None:
    """Register the ``pymolish_*`` meta-commands exposed to PyMOL."""
    from .core.autocompletion import AutocompletionRegistry
    from .core.deps import EXTRAS, pymolish_install_deps
    from .core.registry import CommandRegistry
    from .core.upgrade import pymolish_reload, pymolish_upgrade

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
        (
            "pymolish_logo",
            pymolish_logo,
            "Show or hide the PyMOLish logo + version overlay in the viewer",
            ["pymolish_logo", "pymolish_logo 0", "pymolish_logo toggle"],
            ["meta", "logo", "overlay"],
        ),
        (
            "pymolish_install_deps",
            pymolish_install_deps,
            "Install optional dependencies into PyMOL's Python (pip or uv)",
            [
                "pymolish_install_deps",
                "pymolish_install_deps biopython",
                "pymolish_install_deps numpy matplotlib, dry_run=1",
            ],
            ["meta", "install", "dependencies"],
        ),
        (
            "pymolish_upgrade",
            pymolish_upgrade,
            "Install the newest plugin ZIP from GitHub and offer to reload",
            ["pymolish_upgrade", "pymolish_upgrade check_only=1"],
            ["meta", "upgrade", "update"],
        ),
        (
            "pymolish_reload",
            pymolish_reload,
            "Reload pymolish in place (after installing a new plugin ZIP)",
            ["pymolish_reload"],
            ["meta", "upgrade", "reload"],
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

    autocomplete = AutocompletionRegistry.instance()
    autocomplete.register(
        "pymolish_install_deps",
        0,
        lambda token: [n for n in [*EXTRAS, "all"] if n.startswith(token)],
        "extra",
    )
    autocomplete.apply()


def pymolish_list(category: str | None = None) -> list[str]:
    """Print registered commands, optionally filtered by ``category``.

    Returns:
        List of command names printed (useful for programmatic callers).
    """
    from .core.logging import plog
    from .core.registry import CommandRegistry

    _ensure_extensions_loaded()
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

    _ensure_extensions_loaded()
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

    _ensure_extensions_loaded()
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

    _ensure_extensions_loaded()
    total = len(CommandRegistry.instance())
    plog("version", f"pymolish {__version__} ({total} commands loaded)")
    return __version__


_LOGO_LINES = (
    "  ___      __  __  ___  _    _    _  ",
    " | _ \\_  _|  \\/  |/ _ \\| |  (_)__| |_ ",
    " |  _/ || | |\\/| | (_) | |__| (_-< ' \\",
    " |_|  \\_, |_|  |_|\\___/|____|_/__/_||_|",
    "       |__/",
)


def pymolish_logo(show: str | int = "toggle") -> bool:
    """Show or hide a PyMOLish logo + version overlay in the viewer.

    The overlay is drawn via PyMOL's wizard prompt (top-left of the 3D view),
    so it stays fixed on screen while the scene rotates.

    Args:
        show: ``1``/``on`` to show, ``0``/``off`` to hide, ``toggle`` (default)
            to flip the current state.

    Returns:
        ``True`` if the overlay is visible after the call, ``False`` otherwise.

    Examples:
        pymolish_logo
        pymolish_logo 0

    Since:
        0.1.25

    See Also:
        pymolish_version
    """
    from pymol import cmd

    from .core.logging import plog

    # ponytail: uses the wizard prompt slot; any other wizard replaces it.
    try:
        from pymol.wizard import Wizard
    except ImportError:  # tests / headless mock
        Wizard = object  # noqa: N806

    class _LogoWizard(Wizard):  # type: ignore[misc,valid-type]
        def get_prompt(self):
            return [*_LOGO_LINES, f" pymolish v{__version__}"]

        def get_panel(self):
            return None

    visible = type(cmd.get_wizard()).__name__ == "_LogoWizard"
    want = (
        not visible
        if str(show).lower() in ("toggle", "")
        else str(show).lower() in ("1", "on", "true", "yes")
    )
    if want == visible:
        return visible
    if want:
        cmd.set_wizard(_LogoWizard(cmd) if Wizard is not object else _LogoWizard())
        cmd.refresh_wizard()
        plog("logo", f"overlay shown (pymolish v{__version__})")
    else:
        cmd.set_wizard()
        plog("logo", "overlay hidden")
    return want


def _suffix_for_category(category: str | None) -> str:
    return f" in category {category!r}" if category else ""


__all__ = [
    "__init_plugin__",
    "__version__",
    "pymolish_categories",
    "pymolish_help",
    "pymolish_list",
    "pymolish_logo",
    "pymolish_search",
    "pymolish_version",
]
