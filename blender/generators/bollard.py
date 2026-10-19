"""Quay bollards, cast iron, set with the stone quay.

build(params, seed) makes one bollard at the origin, pivot at its foot.
"""

from kit import Builder, WORLD

VARIANTS = {
    "cast-iron": dict(colour="metal_dark"),
}


def name(variant):
    return f"kit_bollard_{variant}_lod0"


def build(params, seed=0):
    """params: a variant name from VARIANTS. seed is unused: every bollard of a quay was cast alike."""
    import palette

    col = VARIANTS[params]["colour"]
    b = Builder()
    f = WORLD
    b.prism(f, 0, 0, 0.00, 0.06, 0.19, 0.18, 12, col)
    b.prism(f, 0, 0, 0.06, 0.48, 0.15, 0.125, 12, col)
    b.prism(f, 0, 0, 0.48, 0.55, 0.16, 0.16, 12, col)
    b.prism(f, 0, 0, 0.55, 0.64, 0.115, 0.135, 12, col)
    b.prism(f, 0, 0, 0.64, 0.70, 0.17, 0.17, 12, col)
    b.prism(f, 0, 0, 0.70, 0.80, 0.17, 0.06, 12, col)
    return b.build(name(params), palette.material())
