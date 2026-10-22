"""Damage and repair (docs/foundations.md, the shared surface layers, 6; docs/research/repairs.md): what happened to
a built thing's parts between the year it was built and now, from its facts. A thing is kept by someone (the town, an
owner) with some care, decade by decade (its upkeep), and has the works done on it that its facts record (campaigns:
the town's crew resetting a flight, relaying a street). Between them its parts wear, settle and break, and most of
what is done about it is patchwork: a quick fix with whatever the era had at hand, often over an earlier one. So a
thing's repairs are spread over it and over the years, each its own material and date, never one new part in an old
whole. Three ways a thing changes, besides being left alone: renewed (made new, whole: a flight recast, a street
repaved), worked on in a campaign (a crew over part of it), and patched (quick fixes, one at a time).

Every generator runs its parts through here (steps now; walls, paving, quays, houses next) and draws each part's
state as it is now. The rates are the research's (docs/research/repairs.md); what a part is made of and how it breaks
is the generator's. Deterministic from the world seed and the parts' stable ids: every draw is keyed on the id of the
thing it is about, what it decides and the decade (the hash spec, blender/resolver/hashing.py), so one slab's history
never moves because another's changed, and a slab replaced (renewed, or swapped for one from the stock) is a new fill
of its slot, with a new id and so its own history from then on.
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resolver"))
import hashing as HS  # noqa: E402  (the one hash spec)

# What the era had at hand (docs/research/repairs.md, Materials by era): lime mortar, tar and stone until cement
# took over (Norway's first cement works about 1890; cement in every crew's barrow from about 1910).
CEMENT_FROM = 1910

# Quick fixes a decade on a flight of about thirty steps, by who keeps it (docs/research/repairs.md, Patchwork; starting
# values, unverified): the town's lone workman between campaigns, more of them once the skilled crews went (after
# about 1960); an owner's own cement.
QUICK = {"town": lambda y: 0.6 if y < 1960 else 1.5,
         "owner": lambda y: 0.8,
         "society": lambda y: 0.9}


def mortar_of(year):
    """A crew's mortar for pointing in its year: lime until about 1930, lime and cement then cement after (it shows
    as cement: grey, hard, struck wider than the joint)."""
    return "cement" if year >= 1930 else "lime"


def keeper_in(upkeep, year):
    """Who kept the thing in a year and how well (0 left alone to 1 kept well), from its upkeep facts: a list of
    dict(by, since, care), each until the next."""
    k = dict(by="town", care=0.0)
    for u in sorted(upkeep, key=lambda u: u["since"]):
        if u["since"] <= year:
            k = u
    return k


def _poisson(rng, lam):
    """How many of a thing that comes lam times on average (Knuth's)."""
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= L:
            return k
        k += 1


def _fill(sl):
    """A slab's id now: its slot and the fill that stands in it (0 as laid, one more each time it was replaced)."""
    return f"{sl['slot']}/{sl['fill']}"


def _u(seed, *key):
    """One keyed draw in [0, 1)."""
    return HS.unit(HS.h(seed, *key))


def flight(steps, built, now, upkeep, works, seed, slots, wet=None, busy=None, cracks=1.0):
    """The life of a flight of steps, decade by decade. steps: for each step its tread slabs as (from, to) across the
    flight (m); wet: for each step how much water its bed takes (0 to 1; the lane's drainage, the bottom of a flight);
    busy(x): how much of the traffic passes at x across (0 to 1: loads are dropped and corners knocked where people
    go). works: the facts' renewals (dict(kind="renewed", year, steps=(from, to), material, mortar)) and campaigns
    (dict(kind="campaign", year, share, mortar, stock): a crew resets the run of steps that moved most, a share of
    the flight long; past half of it, the whole flight). seed: the world seed; slots: the stable ids the draws are
    keyed on, dict(flight, steps (each step's slot id), slabs (for each step its tread slabs' slot ids)).

    Returns, for each step, dict(reset (the year its bed was last laid), settled (m it has gone off true since),
    mortar (its joints' pointing: None (dry: soil and moss), or (material, year)), slabs: for each tread slab
    dict(origin ("laid" or "reclaimed"), placed (the year it was laid here), lifted (the year hands last lifted it),
    bare (the year its top was last bare), cracked (None or dict(year, at, filled (None or (material, year)))),
    corner (None or dict(year, side ("l" or "r"), size (m), filled (None or (material, year)))), shim (None or the
    year a wedge was driven under it), slot (its slot id), fill (the fill in it now: 0 as laid, one more each time the
    slab was replaced)))."""
    n = len(steps)
    wet = wet or [0.5] * n
    busy = busy or (lambda x: 0.5)
    # each step's bed: how fast it goes off true (frost lifts it, water washes its bed out), a centimetre or so a
    # century, more where it is wet and some by luck
    rate = [0.0001 * (0.5 + wet[i]) * math.exp(HS.Stream(seed, slots["steps"][i], "settle").normal(0.0, 0.45))
            for i in range(n)]   # m a year
    S = []
    for i in range(n):
        S.append(dict(reset=built, settled=0.0, mortar=None,
                      slabs=[dict(origin="laid", placed=built, lifted=built, bare=built, at=(xa, xb), width=xb - xa,
                                  cracked=None, corner=None, shim=None, slot=slots["slabs"][i][k], fill=0)
                             for k, (xa, xb) in enumerate(steps[i])]))
    for decade in range(built, now, 10):
        y0, y1 = decade, min(decade + 10, now)
        span = (y1 - y0) / 10.0
        for i, st in enumerate(S):
            st["settled"] += rate[i] * (y1 - y0)
            for sl in st["slabs"]:
                # damage: a long slab on a moving bed cracks across; a nosing loses a corner where loads are dropped
                # and people go (a frost, a barrow, an iron-shod wheel)
                if sl["cracked"] is None and sl["width"] > 0.8:
                    r = HS.Stream(seed, _fill(sl), "crack", y0)
                    if r.random() < span * 0.025 * cracks * (1.0 + st["settled"] / 0.01):
                        sl["cracked"] = dict(year=r.randint(y0, y1 - 1), at=r.uniform(0.35, 0.65), filled=None)
                bl, br = busy(sl["at"][0]), busy(sl["at"][1])
                r = HS.Stream(seed, _fill(sl), "corner", y0)
                if sl["corner"] is None and r.random() < span * 0.03 * max(bl, br):
                    sl["corner"] = dict(year=r.randint(y0, y1 - 1), side="l" if r.random() * (bl + br) < bl else "r",
                                        size=r.uniform(0.04, 0.09), filled=None)
        # patchwork: a few quick fixes a decade, by whoever keeps it and as much as they care, each on what shows
        # most (a corner gone from the walking line, then an open crack, then a step that rocks), with what the
        # decade had: before cement only a stone wedge
        keep = keeper_in(upkeep, y0)
        k = _poisson(HS.Stream(seed, slots["flight"], "quick", y0),
                     QUICK[keep["by"]](y0) * span * (n / 30.0) * keep["care"] / 0.4)
        todo = []
        for i, st in enumerate(S):
            for sl in st["slabs"]:
                c, kc = sl["cracked"], sl["corner"]
                if kc and kc["filled"] is None and kc["year"] < y1:
                    todo.append((3.0 * max(busy(sl["at"][0]), busy(sl["at"][1]))
                                 + _u(seed, _fill(sl), "fix", "corner", y0), "corner", sl))
                if c and c["filled"] is None and c["year"] < y1:
                    todo.append((1.0 + _u(seed, _fill(sl), "fix", "crack", y0), "crack", sl))
                if sl["shim"] is None and st["settled"] > 0.012:
                    todo.append((0.8 + _u(seed, _fill(sl), "fix", "rock", y0), "rock", sl))
        for _, what, sl in sorted(todo, key=lambda t: -t[0])[:k]:
            year = HS.between(HS.h(seed, _fill(sl), "fix", what, y0, "year"), y0, y1 - 1)
            if what == "rock":
                sl["shim"] = year
            elif y0 >= CEMENT_FROM:
                d = sl["corner"] if what == "corner" else sl["cracked"]
                d["filled"] = ("cement", max(d["year"] + 1, year))
        # the works the facts record, in their year. Renewal: the flight (or a run of its steps) made new, its
        # history begun again, in its own stone or the era's new material
        for w in works:
            if w["kind"] == "renewed" and y0 <= w["year"] < y1:
                lo_, hi_ = w.get("steps", (0, n))
                for i in range(lo_, min(hi_, n)):
                    S[i].update(reset=w["year"], settled=0.0, mortar=(w["mortar"], w["year"]) if w.get("mortar") else None)
                    for sl in S[i]["slabs"]:
                        sl.update(origin=w.get("material", "laid"), placed=w["year"], lifted=w["year"],
                                  bare=w["year"], cracked=None, corner=None, shim=None, fill=sl["fill"] + 1)
        # a campaign follows its cause's reach: the run of steps that moved most (where the water gathers), lifted,
        # set aside and bedded again level in the era's mortar; a slab broken too badly to bed again swapped for a
        # weathered one from the town's stock; the crew's own patches on the run, and the old ones left
        for w in works:
            if w["kind"] == "campaign" and y0 <= w["year"] < y1:
                m = n if w["share"] > 0.5 else max(1, round(w["share"] * n))
                lo_ = max(range(n - m + 1), key=lambda j: sum(S[i]["settled"] * (0.5 + wet[i]) for i in range(j, j + m)))
                for i in range(lo_, lo_ + m):
                    st = S[i]
                    st["reset"], st["settled"] = w["year"], 0.0
                    st["mortar"] = (w.get("mortar") or mortar_of(w["year"]), w["year"])
                    for sl in st["slabs"]:
                        sl["shim"] = None
                        sl["lifted"] = w["year"]
                        c = sl["cracked"]
                        if c and c["year"] >= w["year"]:
                            continue
                        r = HS.Stream(seed, _fill(sl), "campaign", w["year"])
                        if c and c["filled"] is None and w["year"] - c["year"] > 15 and w.get("stock") == "reclaimed" \
                                and r.random() < 0.35:
                            # (stored in a heap, its lichen partly kept: a new fill of the slot)
                            sl.update(origin="reclaimed", placed=w["year"], bare=w["year"] - r.randint(15, 40),
                                      cracked=None, corner=None, fill=sl["fill"] + 1)
                        elif c and c["filled"] is None:
                            c["filled"] = (st["mortar"][0], w["year"])
    return S
