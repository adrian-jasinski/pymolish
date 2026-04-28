"""Transparency animation commands for PyMOL movies."""

from __future__ import annotations

from pymol import cmd

from ...core.logging import plog

_TAG = "animation.transparency"

# Map integer transparency_type to PyMOL setting names.
_SETTINGS: dict[int, str] = {
    0: "transparency",
    1: "cartoon_transparency",
    2: "sphere_transparency",
    3: "cgo_transparency",
}


def _clean(value: str) -> str:
    """Strip one layer of surrounding quotes from PyMOL CLI arguments."""
    if not isinstance(value, str):
        return value
    return value.strip().strip("'\"")


def _validate_transparency_type(t: int) -> bool:
    """Return True when *t* is a recognised transparency-type integer."""
    return t in _SETTINGS


def _validate_transparency_value(v: float, label: str) -> bool:
    """Return True when *v* is in [0.0, 1.0]; log an error otherwise."""
    if not (0.0 <= v <= 1.0):
        plog(_TAG, f"{label} ({v}) must be between 0.0 and 1.0", "error")
        return False
    return True


def _resolve_selection(selection: str) -> bool:
    """Return True when *selection* resolves to at least one atom."""
    try:
        if cmd.count_atoms(selection) == 0:
            plog(_TAG, f"selection {selection!r} has no atoms", "error")
            return False
    except Exception as exc:  # noqa: BLE001
        plog(_TAG, f"invalid selection {selection!r}: {exc}", "error")
        return False
    return True


# ---------------------------------------------------------------------------
# Public commands
# ---------------------------------------------------------------------------


def suggest_transparency_type(selection: str = "all") -> tuple[int, str]:
    """Suggest the most appropriate transparency type for *selection*.

    Inspects which PyMOL representations are active on the objects in
    *selection* and returns the type integer that best matches them.

    Args:
        selection: PyMOL selection to analyse (default: ``"all"``).

    Returns:
        A ``(type_int, explanation)`` tuple where ``type_int`` is 0–3.

    Examples:
        PyMOL> suggest_transparency_type
        PyMOL> suggest_transparency_type protein
        PyMOL> suggest_transparency_type ligand_binding_site

    Since:
        1.0.0

    See Also:
        movie_transparency, set_frame_transparency
    """
    selection = _clean(selection) or "all"
    try:
        objects = cmd.get_object_list(selection)
        if not objects:
            msg = "No objects found, using surface transparency (type 0)"
            plog(_TAG, msg)
            return 0, msg

        has_surface = has_cartoon = has_spheres = False
        for obj in objects:
            try:
                if cmd.get_setting_boolean("surface", obj):
                    has_surface = True
                if cmd.get_setting_boolean("cartoon", obj):
                    has_cartoon = True
                if cmd.get_setting_boolean("spheres", obj):
                    has_spheres = True
            except Exception:  # noqa: BLE001
                pass

        if has_cartoon and not has_surface and not has_spheres:
            msg = "Cartoon detected — use cartoon_transparency (type 1)"
            plog(_TAG, msg)
            return 1, msg
        if has_spheres and not has_cartoon and not has_surface:
            msg = "Spheres detected — use sphere_transparency (type 2)"
            plog(_TAG, msg)
            return 2, msg
        if has_surface:
            msg = "Surface detected — use surface transparency (type 0)"
            plog(_TAG, msg)
            return 0, msg

        msg = "Default: use surface transparency (type 0)"
        plog(_TAG, msg)
        return 0, msg

    except Exception as exc:  # noqa: BLE001
        msg = f"Error analysing selection: {exc}; using surface transparency (type 0)"
        plog(_TAG, msg, "warn")
        return 0, msg


def movie_transparency(
    selection: str = "all",
    start_frame: int | str = 1,
    end_frame: int | str = 30,
    start_transparency: float | str = 0.0,
    end_transparency: float | str = 1.0,
    transparency_type: int | str = 0,
    direction: str = "increase",
) -> int:
    """Animate transparency over a frame range in a PyMOL movie.

    Sets a per-frame ``mdo`` command that linearly interpolates between
    *start_transparency* and *end_transparency* over frames
    *start_frame*–*end_frame*.

    Args:
        selection: PyMOL selection (default: ``"all"``).
        start_frame: First frame of the animation (default: ``1``).
        end_frame: Last frame of the animation (default: ``30``).
        start_transparency: Starting transparency value 0.0–1.0 (default: ``0.0``).
        end_transparency: Ending transparency value 0.0–1.0 (default: ``1.0``).
        transparency_type: Transparency setting index (default: ``0``).
            ``0`` = ``transparency`` (surface),
            ``1`` = ``cartoon_transparency``,
            ``2`` = ``sphere_transparency``,
            ``3`` = ``cgo_transparency``.
        direction: ``"increase"`` or ``"decrease"`` (default: ``"increase"``).
            When ``"decrease"``, start and end values are swapped.

    Returns:
        Number of frames successfully processed (``0`` on validation failure).

    Examples:
        PyMOL> movie_transparency protein, 10, 50, 0.0, 1.0, 1
        PyMOL> movie_transparency ligand, 1, 100, 0.5, 0.0, 2, decrease

    Since:
        1.0.0

    See Also:
        fade_in, fade_out, transparency_pulse, transparency_range,
        set_frame_transparency
    """
    selection = _clean(selection) or "all"
    start_frame = int(start_frame)
    end_frame = int(end_frame)
    start_transparency = float(start_transparency)
    end_transparency = float(end_transparency)
    transparency_type = int(transparency_type)
    direction = _clean(direction).lower()

    if start_frame >= end_frame:
        plog(
            _TAG,
            f"start_frame ({start_frame}) must be less than end_frame ({end_frame})",
            "error",
        )
        return 0
    if not _validate_transparency_value(start_transparency, "start_transparency"):
        return 0
    if not _validate_transparency_value(end_transparency, "end_transparency"):
        return 0
    if not _validate_transparency_type(transparency_type):
        plog(_TAG, f"transparency_type ({transparency_type}) must be 0–3", "error")
        return 0
    if direction not in ("increase", "decrease"):
        plog(_TAG, "direction must be 'increase' or 'decrease'", "error")
        return 0
    if not _resolve_selection(selection):
        return 0

    setting_name = _SETTINGS[transparency_type]

    if transparency_type == 3:
        plog(
            _TAG,
            "cgo_transparency (type 3) is for CGO objects; "
            "consider type 0/1/2 for molecular structures.",
            "warn",
        )
        try:
            cgo_objects = [
                o
                for o in (cmd.get_names("objects") or [])
                if cmd.get_type(o) == "object:cgo"
            ]
            if not cgo_objects:
                plog(
                    _TAG,
                    "no CGO objects found; cgo_transparency may have no effect",
                    "warn",
                )
        except Exception:  # noqa: BLE001
            pass

    if direction == "decrease":
        actual_start, actual_end = end_transparency, start_transparency
    else:
        actual_start, actual_end = start_transparency, end_transparency

    num_frames = end_frame - start_frame + 1
    if num_frames == 1:
        values = [actual_end]
        step = 0.0
    else:
        step = (actual_end - actual_start) / (num_frames - 1)
        values = [actual_start + i * step for i in range(num_frames)]

    success = 0
    for i, frame in enumerate(range(start_frame, end_frame + 1)):
        try:
            cmd.mdo(frame, f"set {setting_name}, {values[i]:.3f}, ({selection})")
            success += 1
            if num_frames > 20 and (i + 1) % 10 == 0:
                plog(_TAG, f"processed frame {frame} ({i + 1}/{num_frames})")
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"failed to set frame {frame}: {exc}", "warn")

    direction_text = "increasing" if direction == "increase" else "decreasing"
    plog(
        _TAG,
        f"applied {direction_text} {setting_name} to {selection!r}: "
        f"frames {start_frame}–{end_frame}, "
        f"{actual_start:.3f}→{actual_end:.3f}, "
        f"step={step:.4f}, "
        f"{success}/{num_frames} frames OK",
    )
    if success < num_frames:
        plog(_TAG, f"{num_frames - success} frame(s) failed", "warn")

    return success


def fade_in(
    selection: str = "all",
    start_frame: int | str = 1,
    end_frame: int | str = 30,
    transparency_type: int | str = 0,
) -> int:
    """Fade objects in (decrease transparency from 1.0 to 0.0).

    Convenience wrapper around :func:`movie_transparency`.

    Args:
        selection: PyMOL selection (default: ``"all"``).
        start_frame: First frame (default: ``1``).
        end_frame: Last frame (default: ``30``).
        transparency_type: Transparency setting index 0–3 (default: ``0``).

    Returns:
        Number of frames successfully processed.

    Examples:
        PyMOL> fade_in protein, 1, 30
        PyMOL> fade_in ligand, 10, 50, 1

    Since:
        1.0.0

    See Also:
        fade_out, movie_transparency
    """
    return movie_transparency(
        selection=selection,
        start_frame=start_frame,
        end_frame=end_frame,
        start_transparency=1.0,
        end_transparency=0.0,
        transparency_type=transparency_type,
        direction="decrease",
    )


def fade_out(
    selection: str = "all",
    start_frame: int | str = 1,
    end_frame: int | str = 30,
    transparency_type: int | str = 0,
) -> int:
    """Fade objects out (increase transparency from 0.0 to 1.0).

    Convenience wrapper around :func:`movie_transparency`.

    Args:
        selection: PyMOL selection (default: ``"all"``).
        start_frame: First frame (default: ``1``).
        end_frame: Last frame (default: ``30``).
        transparency_type: Transparency setting index 0–3 (default: ``0``).

    Returns:
        Number of frames successfully processed.

    Examples:
        PyMOL> fade_out protein, 1, 30
        PyMOL> fade_out complex, 20, 60, 1

    Since:
        1.0.0

    See Also:
        fade_in, movie_transparency
    """
    return movie_transparency(
        selection=selection,
        start_frame=start_frame,
        end_frame=end_frame,
        start_transparency=0.0,
        end_transparency=1.0,
        transparency_type=transparency_type,
        direction="increase",
    )


def transparency_pulse(
    selection: str = "all",
    start_frame: int | str = 1,
    end_frame: int | str = 60,
    min_transparency: float | str = 0.0,
    max_transparency: float | str = 1.0,
    transparency_type: int | str = 0,
    cycles: int | str = 1,
) -> int:
    """Create a pulsing transparency effect over multiple cycles.

    Divides the frame range into *cycles* equal segments, each containing
    a fade-out followed by a fade-in.

    Args:
        selection: PyMOL selection (default: ``"all"``).
        start_frame: First frame (default: ``1``).
        end_frame: Last frame (default: ``60``).
        min_transparency: Minimum transparency (default: ``0.0``).
        max_transparency: Maximum transparency (default: ``1.0``).
        transparency_type: Transparency setting index 0–3 (default: ``0``).
        cycles: Number of complete pulse cycles (default: ``1``).

    Returns:
        Total number of frames successfully processed across all cycles.

    Examples:
        PyMOL> transparency_pulse protein, 1, 60
        PyMOL> transparency_pulse ligand, 1, 90, 0.2, 0.8, 1, 3

    Since:
        1.0.0

    See Also:
        fade_in, fade_out, movie_transparency
    """
    cycles = int(cycles)
    if cycles < 1:
        plog(_TAG, "cycles must be at least 1", "error")
        return 0

    start_frame = int(start_frame)
    end_frame = int(end_frame)
    min_transparency = float(min_transparency)
    max_transparency = float(max_transparency)
    transparency_type = int(transparency_type)

    total_frames = end_frame - start_frame + 1
    frames_per_cycle = total_frames // cycles

    if frames_per_cycle < 2:
        plog(_TAG, "not enough frames for the requested number of cycles", "error")
        return 0

    total_success = 0
    current_frame = start_frame

    for cycle in range(cycles):
        cycle_start = current_frame
        cycle_end = min(current_frame + frames_per_cycle - 1, end_frame)
        mid_frame = cycle_start + (cycle_end - cycle_start) // 2

        total_success += movie_transparency(
            selection=selection,
            start_frame=cycle_start,
            end_frame=mid_frame,
            start_transparency=min_transparency,
            end_transparency=max_transparency,
            transparency_type=transparency_type,
            direction="increase",
        )

        if mid_frame < cycle_end:
            total_success += movie_transparency(
                selection=selection,
                start_frame=mid_frame + 1,
                end_frame=cycle_end,
                start_transparency=max_transparency,
                end_transparency=min_transparency,
                transparency_type=transparency_type,
                direction="decrease",
            )

        plog(
            _TAG,
            f"cycle {cycle + 1}/{cycles} done (frames {cycle_start}–{cycle_end})",
        )
        current_frame = cycle_end + 1

    return total_success


def set_frame_transparency(
    selection: str = "all",
    frame: int | str = 1,
    transparency: float | str = 0.5,
    transparency_type: int | str = 1,
) -> bool:
    """Set transparency for a specific frame in a PyMOL movie.

    Args:
        selection: PyMOL selection (default: ``"all"``).
        frame: Target frame number (default: ``1``).
        transparency: Transparency value 0.0–1.0 (default: ``0.5``).
        transparency_type: Transparency setting index 0–3 (default: ``1``).
            ``0`` = ``transparency`` (surface),
            ``1`` = ``cartoon_transparency``,
            ``2`` = ``sphere_transparency``,
            ``3`` = ``cgo_transparency``.

    Returns:
        ``True`` on success, ``False`` on validation or command failure.

    Examples:
        PyMOL> set_frame_transparency protein, 50, 0.5, 1
        PyMOL> set_frame_transparency complex, 100, 0.8, 0

    Since:
        1.0.0

    See Also:
        movie_transparency, transparency_sequence, transparency_range
    """
    selection = _clean(selection) or "all"
    frame = int(frame)
    transparency = float(transparency)
    transparency_type = int(transparency_type)

    if not _validate_transparency_value(transparency, "transparency"):
        return False
    if not _validate_transparency_type(transparency_type):
        plog(_TAG, f"transparency_type ({transparency_type}) must be 0–3", "error")
        return False
    if not _resolve_selection(selection):
        return False

    setting_name = _SETTINGS[transparency_type]
    try:
        cmd.mdo(frame, f"set {setting_name}, {transparency:.3f}, {selection}")
        plog(
            _TAG,
            f"set {setting_name}={transparency:.3f} for {selection!r} at frame {frame}",
        )
        return True
    except Exception as exc:  # noqa: BLE001
        plog(_TAG, f"failed to set frame {frame}: {exc}", "error")
        return False


def transparency_sequence(
    selection: str = "all",
    frame_transparency_pairs: str | None = None,
    transparency_type: int | str = 1,
) -> int:
    """Set transparency for multiple frames using ``frame:value`` pair strings.

    Args:
        selection: PyMOL selection (default: ``"all"``).
        frame_transparency_pairs: Comma-separated ``frame:transparency`` pairs,
            e.g. ``"386:0.1,387:0.2,388:0.3"``.
        transparency_type: Transparency setting index 0–3 (default: ``1``).

    Returns:
        Number of frames successfully processed (``0`` on parse or validation
        failure).

    Examples:
        PyMOL> transparency_sequence protein, 100:0.0,110:0.5,120:1.0, 1
        PyMOL> transparency_sequence chain A, 1:0.2,5:0.6,10:1.0, 0

    Since:
        1.0.0

    See Also:
        set_frame_transparency, movie_transparency, transparency_range
    """
    if frame_transparency_pairs is None:
        plog(
            _TAG,
            "frame_transparency_pairs is required; "
            "format: 'frame1:value1,frame2:value2,...'",
            "error",
        )
        return 0

    frame_transparency_pairs = _clean(frame_transparency_pairs)
    transparency_type = int(transparency_type)

    pairs: list[tuple[int, float]] = []
    try:
        for chunk in frame_transparency_pairs.split(","):
            frame_str, val_str = chunk.strip().split(":")
            pairs.append((int(frame_str.strip()), float(val_str.strip())))
    except Exception as exc:  # noqa: BLE001
        plog(
            _TAG,
            f"failed to parse frame_transparency_pairs: {exc}; "
            "expected 'frame:value,...'",
            "error",
        )
        return 0

    if not pairs:
        plog(_TAG, "no valid frame:transparency pairs found", "error")
        return 0

    success = sum(
        1
        for frame, transparency in pairs
        if set_frame_transparency(selection, frame, transparency, transparency_type)
    )

    plog(
        _TAG,
        f"applied transparency to {success}/{len(pairs)} frames for {selection!r}",
    )
    return success


def transparency_range(
    selection: str = "all",
    start_frame: int | str = 1,
    end_frame: int | str = 10,
    start_transparency: float | str = 0.0,
    step: float | str = 0.1,
    direction: str = "increase",
    transparency_type: int | str = 1,
) -> int:
    """Set transparency for a frame range using a fixed step increment.

    Unlike :func:`movie_transparency` (which interpolates to a fixed end
    value), this command advances by *step* per frame and clamps to [0, 1].

    Args:
        selection: PyMOL selection (default: ``"all"``).
        start_frame: First frame (default: ``1``).
        end_frame: Last frame (default: ``10``).
        start_transparency: Initial transparency value 0.0–1.0 (default: ``0.0``).
        step: Transparency increment per frame (default: ``0.1``).
        direction: ``"increase"`` or ``"decrease"`` (default: ``"increase"``).
        transparency_type: Transparency setting index 0–3 (default: ``1``).

    Returns:
        Number of frames successfully processed (``0`` on validation failure).

    Examples:
        PyMOL> transparency_range protein, 385, 415, 0.1, 0.05, increase, 1
        PyMOL> transparency_range ligand, 50, 60, 0.0, 0.2, increase, 2

    Since:
        1.0.0

    See Also:
        movie_transparency, set_frame_transparency, transparency_sequence
    """
    selection = _clean(selection) or "all"
    start_frame = int(start_frame)
    end_frame = int(end_frame)
    start_transparency = float(start_transparency)
    step = float(step)
    transparency_type = int(transparency_type)
    direction = _clean(direction).lower()

    if start_frame >= end_frame:
        plog(
            _TAG,
            f"start_frame ({start_frame}) must be less than end_frame ({end_frame})",
            "error",
        )
        return 0
    if not _validate_transparency_value(start_transparency, "start_transparency"):
        return 0
    if step <= 0:
        plog(_TAG, f"step ({step}) must be positive", "error")
        return 0
    if not _validate_transparency_type(transparency_type):
        plog(_TAG, f"transparency_type ({transparency_type}) must be 0–3", "error")
        return 0
    if direction not in ("increase", "decrease"):
        plog(_TAG, "direction must be 'increase' or 'decrease'", "error")
        return 0
    if not _resolve_selection(selection):
        return 0

    setting_name = _SETTINGS[transparency_type]
    actual_step = step if direction == "increase" else -step
    frame_count = end_frame - start_frame + 1

    plog(
        _TAG,
        f"setting {setting_name} for {selection!r} "
        f"from frame {start_frame} to {end_frame}, "
        f"start={start_transparency:.3f}, step={actual_step:+.3f} ({direction})",
    )

    success = 0
    for offset in range(frame_count):
        current_frame = start_frame + offset
        current_t = max(0.0, min(1.0, start_transparency + offset * actual_step))
        try:
            cmd.mdo(
                current_frame,
                f"set {setting_name}, {current_t:.3f}, {selection}",
            )
            success += 1
            if offset < 3 or offset >= frame_count - 3 or (offset + 1) % 10 == 0:
                plog(_TAG, f"  frame {current_frame}: {current_t:.3f}")
            elif offset == 3 and frame_count > 10:
                plog(_TAG, "  ... (showing every 10th frame)")
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"failed to set frame {current_frame}: {exc}", "warn")

    final_t = max(0.0, min(1.0, start_transparency + (frame_count - 1) * actual_step))
    plog(
        _TAG,
        f"processed {success}/{frame_count} frames; final transparency={final_t:.3f}",
    )
    if success < frame_count:
        plog(_TAG, f"{frame_count - success} frame(s) failed", "warn")

    return success


# Expose coerce_bool for internal use by __init__.py tests
__all__ = [
    "suggest_transparency_type",
    "movie_transparency",
    "fade_in",
    "fade_out",
    "transparency_pulse",
    "set_frame_transparency",
    "transparency_sequence",
    "transparency_range",
]
