"""Regenerate ``docs/commands/<category>.md`` from the command registry.

Run from the repo root::

    uv run python scripts/generate_docs.py

The script installs a minimal ``pymol`` mock into ``sys.modules`` so the
pymolish package can be imported without a real PyMOL install, invokes
``pymolish.__init_plugin__`` to populate the registry, then walks the
registry and emits one Markdown file per category under ``docs/commands/``.
"""

from __future__ import annotations

import re
import sys
import textwrap
from dataclasses import replace
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs" / "commands"


def _install_pymol_mock() -> None:
    """Insert a pymol mock so pymolish can import without a real PyMOL build."""
    pymol_mod = ModuleType("pymol")
    cmd_mock = MagicMock(name="pymol.cmd")
    cmd_mock.get_names.return_value = []
    cmd_mock.get_object_list.return_value = []
    cmd_mock.get_type.return_value = ""
    cmd_mock.count_atoms.return_value = 0
    cmd_mock.auto_arg = [{}, {}, {}, {}]
    pymol_mod.cmd = cmd_mock  # type: ignore[attr-defined]
    pymol_mod.plugins = MagicMock(name="pymol.plugins")  # type: ignore[attr-defined]
    pymol_mod.Qt = MagicMock(name="pymol.Qt")  # type: ignore[attr-defined]

    sys.modules.setdefault("pymol", pymol_mod)
    sys.modules.setdefault("pymol.cmd", cmd_mock)
    sys.modules.setdefault("pymol.plugins", pymol_mod.plugins)  # type: ignore[attr-defined]
    sys.modules.setdefault("pymol.Qt", pymol_mod.Qt)  # type: ignore[attr-defined]


def _slug(category: str) -> str:
    """Turn a category label like ``"I/O"`` into a safe filename stem."""
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", category).strip("_").lower()
    return cleaned or "uncategorized"


def _dedent_docstring(doc: str | None) -> str:
    """Normalize a function docstring for embedding in Markdown."""
    if not doc:
        return ""
    return textwrap.dedent(doc).strip()


def _format_list(items: list[str]) -> str:
    return ", ".join(f"`{item}`" for item in items) if items else "_none_"


def _render_command(info) -> str:  # noqa: ANN001 — CommandInfo kept local
    """Render a single :class:`CommandInfo` as a Markdown block."""
    lines: list[str] = []
    lines.append(f"### `{info.name}`")
    lines.append("")
    lines.append(info.description)
    lines.append("")
    lines.append(f"- **Usage:** `{info.usage}`")
    lines.append(f"- **Since:** {info.since}")
    if info.tags:
        lines.append(f"- **Tags:** {_format_list(info.tags)}")
    if info.see_also:
        lines.append(f"- **See also:** {_format_list(info.see_also)}")
    if info.examples:
        lines.append("")
        lines.append("**Examples:**")
        lines.append("")
        lines.append("```")
        for example in info.examples:
            lines.append(example)
        lines.append("```")

    doc = _dedent_docstring(info.function.__doc__)
    if doc:
        lines.append("")
        lines.append("<details><summary>Full docstring</summary>")
        lines.append("")
        lines.append("```")
        lines.append(doc)
        lines.append("```")
        lines.append("")
        lines.append("</details>")

    lines.append("")
    return "\n".join(lines)


def _render_category(category: str, commands: list) -> str:
    """Render a whole category's Markdown file."""
    lines: list[str] = []
    lines.append(f"# {category}")
    lines.append("")
    lines.append(
        f"_{len(commands)} command(s). Generated from the command registry — "
        "do not edit by hand._"
    )
    lines.append("")
    if commands:
        lines.append("## Commands in this category")
        lines.append("")
        for info in commands:
            lines.append(f"- [`{info.name}`](#{info.name.lower()}) — {info.description}")
        lines.append("")
        lines.append("---")
        lines.append("")
        for info in commands:
            lines.append(_render_command(info))
    return "\n".join(lines).rstrip() + "\n"


def _render_index(entries: list[tuple[str, Path, int]]) -> str:
    """Render the top-level ``docs/commands/README.md`` index."""
    lines: list[str] = []
    lines.append("# PyMOLish command reference")
    lines.append("")
    lines.append(
        "Auto-generated from the command registry by `scripts/generate_docs.py`. "
        "Run `uv run python scripts/generate_docs.py` after editing commands."
    )
    lines.append("")
    lines.append("## Categories")
    lines.append("")
    for category, path, count in entries:
        rel = path.relative_to(DOCS_DIR)
        lines.append(f"- [{category}]({rel}) — {count} command(s)")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    """Populate the registry and write per-category Markdown files."""
    _install_pymol_mock()
    # Ensure src/ is importable when running from the repo root without install.
    sys.path.insert(0, str(REPO_ROOT / "src"))

    import pymolish
    from pymolish.core.registry import CommandRegistry

    pymolish.__init_plugin__(None)
    registry = CommandRegistry.instance()

    by_category: dict[str, list] = {}
    for info in registry.list_commands():
        # Strip trailing whitespace / quote artifacts from descriptions for stable output.
        info = replace(info, description=info.description.strip())
        by_category.setdefault(info.category, []).append(info)

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    # Remove stale files we previously generated (but keep the README.md which we rewrite).
    for existing in DOCS_DIR.glob("*.md"):
        existing.unlink()

    entries: list[tuple[str, Path, int]] = []
    for category in sorted(by_category):
        commands = sorted(by_category[category], key=lambda info: info.name)
        target = DOCS_DIR / f"{_slug(category)}.md"
        target.write_text(_render_category(category, commands), encoding="utf-8")
        entries.append((category, target, len(commands)))
        print(f"wrote {target.relative_to(REPO_ROOT)} ({len(commands)} commands)")

    index_path = DOCS_DIR / "README.md"
    index_path.write_text(_render_index(entries), encoding="utf-8")
    print(f"wrote {index_path.relative_to(REPO_ROOT)} (index)")
    print(f"total: {sum(count for _, _, count in entries)} commands across "
          f"{len(entries)} categories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
