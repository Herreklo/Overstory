"""A house's page as arrays, read wall by wall (blender/parts/finish/marks.py's Page grown to a whole house), and the
maps of its geometry that every way shares. paint.py reads it; it runs nothing of its own.

Each texel's wall is its piece's (house.json pieces[i].wall); along and up are in that wall's frame (from
walls[i].origin in walls[i].dir, z up), and out is its distance proud of the wall's plane. A lean-to's pieces stand
turned out of plumb about the foot of the house's back wall (house.py lt_place), so their rest is turned back first.
A View is one wall's texels (or a part of them) as flat arrays under the names the corner's marks read, so the
finishing test's shapes (finish/paint.py) run on it unchanged, and its results go back onto the page.
"""

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "finish"))
import finishlib as FL  # noqa: E402
from finishlib import HS  # noqa: E402


class Page:
    """The bakes as arrays, and the per-texel facts every mark reads: the page's own, as the corner's Page."""

    def __init__(self, cache, meta, mats):
        rd = lambda n: FL.read(os.path.join(cache, f"{n}.exr"))  # noqa: E731
        rest, nrm, ident = rd("rest"), rd("normal"), rd("ident")
        self.cov = rest[..., 3] > 0.5
        self.p = rest[..., :3] - 2.0
        self.n = nrm[..., :3] * 2.0 - 1.0
        self.piece = np.where(self.cov, np.rint(ident[..., 0]).astype(np.int64), 0)
        self.mat = np.where(self.cov, np.rint(ident[..., 1]).astype(np.int64), -1)
        self.arris = ident[..., 2]
        self.ao = rd("ao")[..., 0]
        self.cav = rd("cavity")[..., 0]
        self.sky = rd("sky")[..., 0]
        self.street_n = rd("street-normal")
        self.x, self.y, self.z = self.p[..., 0], self.p[..., 1], self.p[..., 2]
        self.up = self.n[..., 2] > 0.55
        self.vertical = np.abs(self.n[..., 2]) < 0.5
        self.mats = mats
        self.m = {k: self.mat == i for i, k in enumerate(mats)}
        self.meta = meta
        self.shape = self.cov.shape
        pieces = meta["pieces"]
        self.wall_of = np.array([pc["wall"] for pc in pieces], np.int64)
        self.kind_of = np.array([pc["kind"] for pc in pieces])
        self.wall = np.where(self.cov, self.wall_of[np.clip(self.piece, 0, len(pieces) - 1)], -1)

    def per_piece(self, values, reduce):
        """Each piece's min or max of `values` over its texels, spread back over them."""
        n = self.piece.max() + 1
        out = np.full(n, np.inf if reduce == "min" else -np.inf)
        idx, val = self.piece[self.cov], values[self.cov]
        (np.minimum if reduce == "min" else np.maximum).at(out, idx, val)
        return out[self.piece]


def upright(p, meta):
    """A lean-to's rest turned back to plumb: house.py turns its pieces by -plumb about x at the back wall's foot."""
    lt = meta["leanTo"]
    t = lt["plumb"]
    y, z = p[..., 1] - meta["size"][1], p[..., 2]
    out = p.copy()
    out[..., 1] = meta["size"][1] + y * math.cos(t) - z * math.sin(t)
    out[..., 2] = y * math.sin(t) + z * math.cos(t)
    return out


class View:
    """The texels of `mask` on one wall as flat arrays, named as the corner's Page names them: along the wall, z up,
    y its distance behind the wall's face (negative proud of it, as the corner's street wall), `street` all of them.
    get/put move whole-page arrays in and out."""

    def __init__(self, pg, mask, wall):
        self.idx = np.flatnonzero(mask & pg.cov)
        flat = lambda a: a.reshape(-1, *a.shape[2:])[self.idx]  # noqa: E731
        for name in ("p", "n", "piece", "mat", "arris", "ao", "cav", "sky", "up", "vertical"):
            setattr(self, name, flat(getattr(pg, name)))
        q = upright(self.p, pg.meta) if wall["kind"] == "lean" else self.p
        rel = q[:, :2] - np.asarray(wall["origin"])
        self.along = rel @ np.asarray(wall["dir"])
        self.out = rel @ np.asarray(wall["out"])
        self.x, self.y, self.z = self.along, -self.out, q[:, 2]
        self.shape = self.along.shape
        self.cov = np.ones(self.shape, bool)
        self.street = np.ones(self.shape, bool)
        self.m = {k: self.mat == i for i, k in enumerate(pg.mats)}
        self.meta = pg.meta
        self.wall = wall

    def per_piece(self, values, reduce):
        """Each piece's min or max of `values` over this view's texels, spread back over them."""
        n = int(self.piece.max()) + 1 if self.piece.size else 1
        out = np.full(n, np.inf if reduce == "min" else -np.inf)
        (np.minimum if reduce == "min" else np.maximum).at(out, self.piece, values)
        return out[self.piece]

    def get(self, full):
        return full.reshape(-1, *full.shape[2:])[self.idx]

    def put(self, full, values, how="max"):
        """Lay `values` back onto the page's `full`: the larger of the two ("max"), or added ("add")."""
        f = full.reshape(-1, *full.shape[2:])
        f[self.idx] = np.maximum(f[self.idx], values) if how == "max" else f[self.idx] + values


def lap_line(pg, P, meta):
    """marks.py's lap line for every wall's cladding, each from its own course table (by its wall's group): the
    signed distance to the nearest butt, 0.5 + d / (2 `lapPageMm`), 1 off the cladding."""
    page = P["marks"]["shade"]["lapPageMm"] / 1000.0
    out = np.ones(pg.shape)
    for w in meta["walls"]:
        v = View(pg, (pg.wall == w["i"]) & pg.m["cladding"] & pg.vertical, w)
        if not v.idx.size:
            continue
        courses = np.asarray(meta["courses"][str(w["group"])])
        i = np.searchsorted(courses, v.z, side="right")
        up = np.where(i < len(courses), courses[np.clip(i, 0, len(courses) - 1)], np.inf) - v.z
        down = v.z - np.where(i > 0, courses[np.clip(i - 1, 0, len(courses) - 1)], -np.inf)
        d = np.clip(0.5 + 0.5 * np.where(up <= down, up, -down) / page, 0.0, 0.98)
        out.reshape(-1)[v.idx] = d
    return out


def geo(pg, P, meta):
    """geo.png as marks.py writes it: R occlusion, G cavity (lighter on a worn arris), B the lap line, A the arris."""
    cav = np.clip((1.0 - pg.cav) * 1.3, 0, 1)
    g = np.stack([pg.ao, 0.5 + 0.5 * (pg.arris * 0.6 - cav), lap_line(pg, P, meta), pg.arris], axis=-1)
    pad = meta["page"]["padPx"]
    return FL.dilate(np.where(pg.cov[..., None], g, 0), pg.cov, pad + 2)


def street_normal(pg, meta):
    sn = pg.street_n
    return FL.dilate(sn[..., :3], sn[..., 3] > 0.5, meta["page"]["padPx"] + 2)
