"""Where water lies and runs on a surface (docs/foundations.md, The shared surface layers: the water layer): the bake
every generator gives the one water layer every shader draws (unity/Assets/Shaders/Water.hlsl), from the surface's
shape and gravity. Rain lands on what faces up and runs to the low edges and joints; it drips off copings, sills and
nosings and streaks down the faces below, most under joints and low points and strongest near the top; it gathers in
hollows, joints and at every foot (the splash and the damp); it dries from the crowns and the exposed edges first.
How a material answers it (how dark, how glossy, how long it holds water, how readily it stains) is the material's
own water profile (Water.hlsl; the shared materials' in the setting pack's WaterPack).

Each function takes per-vertex arrays and returns how much water lies or runs there, 0 to 1. Numpy only.
"""

import numpy as np


def on_top(back=None, joint=None, hollow=None, floor=0.12):
    """A surface that faces up: water lingers against what stands behind it (back, 0 to 1), in its joints (joint,
    0 to 1) and in its hollows (hollow, 0 to 1: a worn dish, a sett's low corner); its crown dries first (floor)."""
    parts = [np.asarray(p, float) for p in (back, joint, hollow) if p is not None]
    return np.clip(np.maximum.reduce(parts) if parts else floor, floor, 1.0)


def over_edge(drain, below):
    """A face below an edge water runs over (a step's front under its nosing): drain (0 to 1) where along the edge
    it runs over (a worn dish drains through its middle, a joint), below how far under the edge (m)."""
    return (0.2 + 0.8 * np.clip(drain, 0.0, 1.0)) * (0.5 + 0.5 * np.exp(-np.clip(below, 0.0, None) / 0.08))


def drips(where, strength):
    """Where water drips off an edge above a face: list of (s along the face, strength 0 to 1)."""
    return list(zip(where, strength))


def down_face(s, below_top, above_foot, drip_list, width=0.07, reach=0.6, splash=0.35):
    """A face water runs down: streaks under the drips (each drip_list's (s, strength), a streak about width wide,
    strongest within reach of the top, below_top m under it), the splash and damp at its foot (above_foot m over the
    ground or the step beside it)."""
    streak = np.zeros(len(s))
    for sj, k in drip_list:
        streak = np.maximum(streak, k * np.exp(-((s - sj) / width) ** 2))
    w = (0.12 + 0.88 * streak) * (0.45 + 0.55 * np.exp(-np.clip(below_top, 0.0, None) / reach))
    return np.clip(w + 0.6 * np.clip(1.0 - above_foot / splash, 0.0, 1.0), 0.0, 1.0)


HOLDS = 0.9     # a joint's soil, a crack's grit: they hold water
