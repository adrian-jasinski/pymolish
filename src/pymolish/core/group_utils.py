"""Shared PyMOL group and object helpers used across extension categories."""

from __future__ import annotations

import re
from collections.abc import Iterable

from pymol import cmd

from .logging import plog


class GroupUtils:
    """Stateless helpers for working with PyMOL groups and object collections.

    All methods are class-level so the helper is easy to import and use without
    threading state through call sites. The class exists primarily to group
    related helpers together.
    """

    # ----- Object / group introspection -------------------------------------

    @staticmethod
    def get_all_objects() -> list[str]:
        """Return every loaded PyMOL object (including members of groups)."""
        try:
            return list(cmd.get_names("objects") or [])
        except Exception:  # noqa: BLE001
            return []

    @staticmethod
    def get_all_groups() -> list[str]:
        """Return names of all PyMOL groups.

        Tries ``cmd.get_names("group_objects")`` first (Open Source), falling
        back to ``cmd.get_names("groups")`` (commercial PyMOL), then to a scan
        over object types.
        """
        for key in ("group_objects", "groups"):
            try:
                groups = cmd.get_names(key)
                if groups:
                    return list(groups)
            except Exception:  # noqa: BLE001
                continue
        try:
            return [
                name
                for name in cmd.get_names("objects") or []
                if GroupUtils.is_group(name)
            ]
        except Exception:  # noqa: BLE001
            return []

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
    def is_object(name: str) -> bool:
        """Return ``True`` if ``name`` is a loaded PyMOL object."""
        if not name:
            return False
        return name in GroupUtils.get_all_objects()

    @staticmethod
    def get_group_objects(group_name: str) -> list[str] | None:
        """Return objects contained in ``group_name`` or ``None`` if absent.

        Attempts multiple PyMOL APIs so the helper works across Open Source
        and commercial builds.
        """
        if not group_name:
            return None
        candidates: Iterable = (
            lambda: cmd.get_names("objects", selection=group_name),
            lambda: cmd.get_object_list(f"({group_name})"),
            lambda: cmd.get_names("objects", group_name),
        )
        for getter in candidates:
            try:
                result = getter()
                if result:
                    return list(result)
            except Exception:  # noqa: BLE001
                continue
        return None

    @staticmethod
    def group_members(group_name: str) -> list[str]:
        """Return direct members of ``group_name`` or ``[]`` if missing."""
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

    # ----- Naming / pattern matching ----------------------------------------

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
    def find_objects_by_pattern(pattern: str) -> list[str]:
        """Return loaded objects matching ``pattern`` (supports ``*`` and ``?``)."""
        if not pattern:
            return []
        regex = pattern.replace("*", ".*").replace("?", ".")
        try:
            compiled = re.compile(regex, re.IGNORECASE)
            return [
                name for name in GroupUtils.get_all_objects() if compiled.match(name)
            ]
        except re.error:
            needle = pattern.lower()
            return [
                name for name in GroupUtils.get_all_objects() if needle in name.lower()
            ]

    # ----- Mutation helpers --------------------------------------------------

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
        if not members:
            cmd.group(group_name, "")
            return group_name
        for member in members:
            cmd.group(group_name, member, action="add")
        return group_name

    @staticmethod
    def add_to_group(group_name: str, object_names: str | list[str]) -> bool:
        """Add one or more existing objects to ``group_name``.

        Args:
            group_name: Target group.
            object_names: Single name or iterable of names.

        Returns:
            ``True`` on success, ``False`` if any call raised.
        """
        names = [object_names] if isinstance(object_names, str) else list(object_names)
        try:
            for obj in names:
                cmd.group(group_name, obj, action="add")
            return True
        except Exception as exc:  # noqa: BLE001
            plog("group_utils", f"add_to_group({group_name!r}) failed: {exc}", "warn")
            return False

    @staticmethod
    def remove_from_group(group_name: str, object_names: str | list[str]) -> bool:
        """Remove objects from ``group_name``."""
        names = [object_names] if isinstance(object_names, str) else list(object_names)
        try:
            for obj in names:
                cmd.group(group_name, obj, action="remove")
            return True
        except Exception as exc:  # noqa: BLE001
            plog(
                "group_utils",
                f"remove_from_group({group_name!r}) failed: {exc}",
                "warn",
            )
            return False

    @staticmethod
    def list_groups() -> list[str]:
        """Return names of all top-level PyMOL groups."""
        return GroupUtils.get_all_groups()
