"""Where things grow on a surface, and for how long (docs/nature.md, Growth on surfaces): the growth potentials every
generator bakes into what it builds (stone now; timber, roofs, bark, concrete next), from the surface's facts, so
that the one growth layer every shader draws (unity/Assets/Shaders/Growth.hlsl) puts lichen, moss and algae only where
the facts say they grow, for as long as they have been growing. The species, their pigments and rates are the setting
pack's (Overstory.World.GrowthPack); here only where and how long.

Each function takes per-vertex arrays and returns arrays, numpy only.
"""

import numpy as np

# How long after a surface was bare (built, relaid, cleaned) the first lichen shows, in years (the map lichen's own
# rate is the pack's: about 0.7 mm a year on this coast).
LICHEN_DELAY = 12
# Feet kill growth fast: no plot kept half its cover after 200 passes (secondary, docs/research/stone.md). Traffic
# here is 0 (never trodden) to 1 (the busiest line).


def lichen_years(years_bare, traffic, exposed=None):
    """The years lichen has grown at each point: from a few years after the surface was bare, where it is quiet;
    nothing on a busy line. exposed (0 to 1, optional): how open the surface is to air and light (lichen wants both;
    it thins in a dark, damp corner where moss and algae take over). Returned over 200, as the shaders read it."""
    quiet = (1.0 - np.clip(traffic, 0.0, 1.0)) ** 1.5
    if exposed is not None:
        quiet = quiet * (0.35 + 0.65 * np.clip(exposed, 0.0, 1.0))
    return np.clip(np.clip(years_bare - LICHEN_DELAY, 0, None) * quiet / 200.0, 0.0, 1.0)


def moss(damp, traffic, years_bare, sheltered=None):
    """Moss: where the surface stays damp (a joint, an inside corner, a wall's foot, a north face), is not trodden,
    and has had the years to fill in (about forty to be full). sheltered (optional, 0 to 1) adds where the town or a
    tree shades it (the shader also reads the sky map, so this is for shelter the generator knows of itself).
    0 to 1."""
    m = np.clip(damp, 0.0, 1.0)
    if sheltered is not None:
        m = m * (0.7 + 0.5 * np.clip(sheltered, 0.0, 1.0))
    return np.clip(m * (1.0 - 0.85 * np.clip(traffic, 0.0, 1.0)) * np.minimum(np.asarray(years_bare, float) / 40.0, 1.0), 0.0, 1.0)
