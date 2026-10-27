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
    and has had the years to fill in (about sixty to be full). sheltered (optional, 0 to 1) adds where the town or a
    tree shades it (the shader also reads the sky map, so this is for shelter the generator knows of itself).
    0 to 1."""
    m = np.clip(damp, 0.0, 1.0)
    if sheltered is not None:
        m = m * (0.7 + 0.5 * np.clip(sheltered, 0.0, 1.0))
    return np.clip(m * (1.0 - 0.85 * np.clip(traffic, 0.0, 1.0)) * np.minimum(np.asarray(years_bare, float) / 60.0, 1.0), 0.0, 1.0)


# ---- on rock: the knuckle and the walls (interface-growth-rock.md) ----------------------------------------------------

import json
import os

_PACK = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                     "packs", "stavanger-1989", "growth.json")


def pack(path=None):
    """The setting pack's growth data (packs/<pack>/growth.json): on_rock's rules, the painted values, the tufts."""
    with open(path or _PACK) as f:
        return json.load(f)


def _ramp(x, a, b):
    """0 at a, 1 at b (either way round), clipped."""
    return np.clip((np.asarray(x, float) - a) / (b - a), 0.0, 1.0)


def on_rock(points, normals, sky, foot, joint, years_bare, rules=None):
    """Lichen and moss on a rock's or a dry wall's vertices, from what the rock knows of each (per-vertex arrays):
    points (street m, z up), normals (unit, z up), sky (0 to 1, the sky it sees), foot (m over the ground it stands
    in), joint (m to the nearest crack or bed of its own jointing, large where none), and years_bare (the fact: how
    long since it was bare, a number or an array). Lichen on the open, rain-washed tops and sloping faces, thickest
    at the crest, none under an overhang or in the damp foot; moss in the foot, in the joints and on low north faces
    that see little sky. Returns (lichen years / 200, moss 0 to 1), the rock's UV4.y and UV5.x. The numbers are the
    pack's (growth.json, rock)."""
    R = rules or pack()["rock"]
    n = np.asarray(normals, float)
    nz = n[:, 2]
    sky = np.clip(np.asarray(sky, float), 0.0, 1.0)
    foot = np.asarray(foot, float)
    joint = np.asarray(joint, float)
    years = np.broadcast_to(np.asarray(years_bare, float), nz.shape)

    # (rain-washed and open: none under an overhang, none in the damp foot or inside a joint)
    washed = _ramp(nz, R["overhang"], R["fullRain"]) * _ramp(foot, *R["footLichen"]) * (joint > R["jointLip"])

    upright = 1.0 - np.abs(nz)
    north = np.clip(n[:, 1], 0.0, 1.0) * upright
    damp = np.maximum.reduce([
        R["footMossMax"] * (1.0 - _ramp(foot, *R["footMoss"])),
        R["jointMossMax"] * (1.0 - _ramp(joint, *R["jointMoss"])),
        R["northMossMax"] * north * _ramp(sky, R["northShade"][0], R["northShade"][1]),
    ])
    m = moss(damp, 0.0, years)
    lichen = lichen_years(years, 0.0, sky ** R["skyPower"]) * washed * (1.0 - R["mossOverLichen"] * m)
    return lichen, m
