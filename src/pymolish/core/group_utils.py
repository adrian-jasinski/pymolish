"""Shared PyMOL group and object helpers used across extension categories."""

from __future__ import annotations

from pymol import cmd

from .logging import plog


class GroupUtils:
    """Stateless helpers for working with PyMOL groups and object collections.

    All methods are class-level so the helper is easy to import and use without
    threading state through call sites. The class exists primarily to group
    related helpers together.
    """

    @staticmethod
    def is_group(name: str) -> bool:
        """Return ``True`` if ``name`` is a PyMOL group object."""
        if not name:
            return False
        try:
            return cmd.get_type(name) == "object:group"
        except Exception:  # noqa: BLE001
            return False

    @staticmethod
    def group_members(group_name: str) -> list[str]:
        """Return the direct members of ``group_name`` (objects or nested groups)."""
        if not GroupUtils.is_group(group_name):
            return []
        try:
            return list(cmd.get_object_list(group_name) or [])
        except Exception as exc:  # noqa: BLE001
            plog(
                "group_utils",
                f"get_object_list({group_name!r}) failed: {exc}",
                "warn",
            )
            return []

    @staticmethod
    def ensure_group(group_name: str, members: list[str] | None = None) -> str:
        """Create ``group_name`` if missing and add ``members`` to it.

        Args:
            group_name: Desired group name.
            members: Optional object names to add to the group.

        Returns:
            The group name (for chaining convenience).
        """
        if not group_name:
            raise ValueError("group_name must be non-empty")
        joined = " ".join(members) if members else ""
        cmd.group(group_name, joined)
        return group_name

    @staticmethod
    def unique_name(desired: str, existing: list[str] | None = None) -> str:
        """Return ``desired`` or a ``desired_N`` variant to avoid name collisions."""
        taken = set(existing if existing is not None else cmd.get_names() or [])
        if desired not in taken:
            return desired
        idx = 2
        while f"{desired}_{idx}" in taken:
            idx += 1
        return f"{desired}_{idx}"

    @staticmethod
    def list_groups() -> list[str]:
        """Return names of all top-level PyMOL groups."""
        try:
            names = cmd.get_names("objects") or []
        except Exception:  # noqa: BLE001
            return []
        return [n for n in names if GroupUtils.is_group(n)]
