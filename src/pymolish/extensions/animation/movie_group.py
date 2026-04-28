"""Movie-from-group animation: cycle through group objects one scene at a time."""

from __future__ import annotations

from pymol import cmd

from ...core.group_utils import GroupUtils
from ...core.logging import plog

_TAG = "animation.movie_group"


def _clean(value: str) -> str:
    """Strip one layer of surrounding quotes from PyMOL CLI arguments."""
    if not isinstance(value, str):
        return value
    return value.strip().strip("'\"")


def _get_group_members(group_name: str) -> list[str] | None:
    """Return group member names in stable order, or ``None`` if unavailable."""
    try:
        members = cmd.get_object_list(f"({group_name})")
        if members:
            return list(members)
    except Exception:  # noqa: BLE001
        pass
    members = GroupUtils.get_group_objects(group_name)
    return list(members) if members else None


def movie_from_group(
    group_name: str,
    frames_per_object: int | str = 10,
) -> int:
    """Set up a PyMOL movie that cycles through each object in a group.

    Creates one scene per group member (only that member visible at a time),
    sets the movie length to ``num_objects * frames_per_object``, and stores
    ``mview`` keyframes so each scene appears at the correct frame with
    interpolation.

    Args:
        group_name: Name of the PyMOL group containing the objects to cycle.
        frames_per_object: Number of movie frames allocated to each object
            (default: ``10``).

    Returns:
        Total number of frames in the created movie (``0`` on failure).

    Examples:
        PyMOL> movie_from_group my_group, 10
        PyMOL> movie_from_group proteins, 5

    Since:
        1.0.0

    See Also:
        movie_transparency, fade_in, fade_out
    """
    group_name = _clean(group_name)
    if not group_name:
        plog(_TAG, "group_name is required", "error")
        return 0

    try:
        fpo = int(frames_per_object)
    except (TypeError, ValueError):
        plog(_TAG, "frames_per_object must be an integer", "error")
        return 0
    if fpo < 1:
        plog(_TAG, "frames_per_object must be >= 1", "error")
        return 0

    objects = _get_group_members(group_name)
    if objects is None:
        plog(_TAG, f"group {group_name!r} not found", "error")
        return 0
    if not objects:
        plog(_TAG, f"group {group_name!r} is empty", "error")
        return 0

    total_frames = len(objects) * fpo
    cmd.mset(f"1 x{total_frames}")

    scene_names: list[str] = []
    for i, obj in enumerate(objects):
        for other in objects:
            cmd.disable(other)
        cmd.enable(obj, parents=1)
        cmd.refresh()
        scene_name = f"{i + 1:03d}"
        scene_names.append(scene_name)
        cmd.scene(scene_name, "store")

    for i, scene_name in enumerate(scene_names):
        frame = 1 if i == 0 else i * fpo
        cmd.mview("store", first=frame, scene=scene_name)

    cmd.do("mview reinterpolate")

    plog(
        _TAG,
        f"group={group_name!r}, {len(objects)} objects, "
        f"{fpo} frames/object, {total_frames} total frames",
    )
    return total_frames


__all__ = ["movie_from_group"]
