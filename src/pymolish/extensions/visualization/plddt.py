"""Color predicted models by pLDDT confidence stored in the B-factor column."""

from __future__ import annotations

from pymol import cmd

from ...core.cli import clean as _clean
from ...core.logging import plog
from ...core.validators import coerce_bool

_TAG = "viz.plddt"
_LEGEND = "AF_pLDDT_legend"

# Official AlphaFold DB bin colors: very low, low, confident, very high.
_AF_COLORS = {
    "plddt_very_low": [1.00, 0.49, 0.27],  # #FF7D45
    "plddt_low": [1.00, 0.86, 0.07],  # #FFDB13
    "plddt_confident": [0.40, 0.80, 0.95],  # #65CBF3
    "plddt_very_high": [0.00, 0.33, 0.84],  # #0053D6
}
_AF_BINS = (
    ("plddt_very_low", "b < 50"),
    ("plddt_low", "b >= 50 and b < 70"),
    ("plddt_confident", "b >= 70 and b < 90"),
    ("plddt_very_high", "b >= 90"),
)

PLDDT_PALETTES = {
    "af": "AlphaFold DB bins: orange <50, yellow <70, light blue <90, blue >=90",
    "gradient": "Continuous red (0) -> yellow (50) -> blue (100)",
}


def color_plddt(
    selection: str = "all",
    legend: bool | str | int = True,
    palette: str = "af",
    verbose: bool | str | int = True,
) -> int:
    """Color atoms by pLDDT confidence (B-factor column) and draw a legend.

    AlphaFold DB and ESMFold models store the per-residue pLDDT score
    (0-100) in the B-factor field, so no parsing is required.  The legend is
    a PyMOL ramp object named ``AF_pLDDT_legend``; enabled ramps draw a labelled
    color bar in the viewport.

    Args:
        selection: PyMOL selection to color. Default: ``"all"``.
        legend: Create/refresh the ``AF_pLDDT_legend`` ramp. Default: ``True``.
        palette: ``"af"`` (default; the four AlphaFold DB confidence bins:
            orange <50, yellow <70, light blue <90, dark blue >=90) or
            ``"gradient"`` (continuous red -> yellow -> blue over 0-100).
        verbose: When truthy, log a summary. Default: ``True``.

    Returns:
        Number of atoms in *selection*; ``0`` when it is empty or the
        palette is unknown.

    Examples:
        PyMOL> color_plddt
        PyMOL> color_plddt AF_P04637, palette=gradient
        PyMOL> color_plddt my_model, 0

    Since:
        0.1.21

    See Also:
        fetch_fold, color_secondary_structure
    """
    selection = _clean(selection) or "all"
    palette = _clean(palette).lower()
    legend = coerce_bool(legend)
    verbose = coerce_bool(verbose)

    if palette not in PLDDT_PALETTES:
        plog(_TAG, f"unknown palette '{palette}'", "error")
        plog(_TAG, f"available palettes: {list(PLDDT_PALETTES)}")
        return 0

    n_atoms = cmd.count_atoms(selection)
    if not n_atoms:
        plog(_TAG, f"selection '{selection}' is empty", "error")
        return 0

    for name, rgb in _AF_COLORS.items():
        cmd.set_color(name, rgb)

    if palette == "gradient":
        cmd.spectrum("b", "red_yellow_blue", selection, minimum=0, maximum=100)
        ramp_values, ramp_colors = [0, 50, 100], ["red", "yellow", "blue"]
    else:
        for color, expr in _AF_BINS:
            cmd.color(color, f"({selection}) and {expr}")
        ramp_values = [0, 50, 70, 90, 100]
        ramp_colors = [
            "plddt_very_low",
            "plddt_low",
            "plddt_confident",
            "plddt_very_high",
            "plddt_very_high",
        ]

    if legend:
        cmd.delete(_LEGEND)
        # ponytail: ramp_new needs a source object; the first object in the
        # selection works for a legend (only the range is displayed).
        objects = cmd.get_object_list(selection) or []
        if objects:
            cmd.ramp_new(_LEGEND, objects[0], ramp_values, ramp_colors)
        else:
            plog(_TAG, "no object in selection - legend skipped", "warn")

    if verbose:
        plog(_TAG, f"colored {n_atoms} atom(s) in '{selection}' by pLDDT ({palette})")
    return n_atoms
