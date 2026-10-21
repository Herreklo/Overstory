"""The facts of every flight in the town plan, until the engine's fabric pass has them (docs/engine-requests.md, 6,
13, 14; docs/living-fabric.md): who built it and when, with what means, how (its construction), of what stone, how
busy it is, who has kept it and how well, and the works its records hold. Rules by the flight's kind, its district
and its role, seeded by its name, so every flight has a life of its own and two flights differ by what happened to
them; the beauty corner's own flight (the gully) keeps its hand-authored facts. Provenance: authored by rule.

    facts_for(lane) -> the flight's spec, as stone.py's FLIGHTS hold it
"""

import random

import stone as ST


def _town(rng, since, care, drops):
    """The town's care by decade, each change from the one before: steady, cut in the thirties, a post-war effort,
    let slide from the sixties."""
    u = [dict(by="town", since=since, care=care)]
    c = care
    for year, f in drops:
        if year > since:
            c = c * f * rng.uniform(0.9, 1.05) if f < 1.0 else c * f
            u.append(dict(by="town", since=year, care=round(c, 2)))
    return u


def _care_at(upkeep, year):
    c = upkeep[0]["care"]
    for u in upkeep:
        if u["since"] <= year:
            c = u["care"]
    return c


def _campaigns(rng, built, windows, upkeep=None):
    """Campaigns the town's works department ran, one in each window it reached (a share of the flight each), likelier
    where the stair was cared for in that decade."""
    out = []
    for lo, hi, p, share, mortar in windows:
        care = _care_at(upkeep, lo) if upkeep else 0.4
        if hi > built + 20 and rng.random() < p * min(max(care / 0.4, 0.3), 1.6):
            out.append(dict(kind="campaign", year=rng.randint(max(lo, built + 20), hi), share=share,
                            mortar=mortar, stock="reclaimed"))
    return out


def facts_for(lane, seed=1):
    name = lane["name"]
    rng = random.Random(f"facts-{name}-{seed}")
    if name == "Gully Steps":
        return ST.FLIGHTS["gully"]
    base = dict(lane=name, stone="slate")
    windows = [(1905, 1915, 0.6, 0.3, None), (1946, 1958, 0.7, 0.4, "cement"), (1975, 1985, 0.3, 0.25, "cement")]
    if name == "Tanner's Steps":
        # the old town's other public stair: local slate blocks, laid by the town in the 1860s, busy
        built = rng.randint(1858, 1872)
        up = _town(rng, built, 0.45, [(1930, 0.65), (1946, 1.35), (1965, 0.5)])
        return dict(base, built=built, built_as="block", finish="split", footfall=rng.randint(30000, 55000),
                    upkeep=up, works=_campaigns(rng, built, windows, up))
    if name == "Bishop's Steps":
        # the better-off district's stair, built by the town with money: dressed granite blocks brought in, kept
        # better, its walking line keeping to the rail side
        built = rng.randint(1888, 1896)
        up = _town(rng, built, 0.65, [(1930, 0.85), (1946, 1.2), (1965, 0.8)])
        return dict(base, stone="granite", built=built, built_as="block", finish="dressed",
                    footfall=rng.randint(20000, 35000), upkeep=up, works=_campaigns(rng, built, windows[:2], up))
    if name == "the Hundred Steps":
        # a town society's walk up the Bluff (after Ålesund's Aksla, begun 1885): split slabs set into the rock,
        # walkers rather than errands; the society kept it until the town took it over
        built = rng.randint(1886, 1898)
        up = [dict(by="society", since=built, care=0.55), dict(by="town", since=1934, care=0.3),
              dict(by="town", since=1968, care=0.2)]
        return dict(base, built=built, built_as="block", finish="rough", footfall=rng.randint(12000, 22000),
                    upkeep=up, works=_campaigns(rng, built, [(1936, 1940, 0.8, 0.5, "cement")], up))
    if name == "the Crack":
        # a stepped path down a cleft in the rock: rough slabs, little used, seldom kept
        built = rng.randint(1895, 1910)
        return dict(base, built=built, built_as="block", finish="rough", footfall=rng.randint(4000, 9000),
                    upkeep=_town(rng, built, 0.25, [(1946, 1.2), (1965, 0.5)]), works=[])
    if name.startswith("the path to Lookout Park"):
        # the park's path (laid with the park in the 1920s): thin treads on cheap risers, the park's men
        built = rng.randint(1922, 1928)
        up = [dict(by="town", since=built, care=0.5), dict(by="town", since=1965, care=0.3)]
        return dict(base, built=built, built_as="tread_on_riser", finish="split", footfall=rng.randint(8000, 16000),
                    upkeep=up, works=_campaigns(rng, built, windows[1:], up))
    if name.startswith("passage at"):
        # a passage between houses, laid by the neighbours: thin treads on rough risers, kept or let go by whoever
        # owns the house beside it, patched with what they had
        built = rng.randint(1868, 1915)
        care = [dict(by="owner", since=built, care=round(rng.uniform(0.15, 0.6), 2))]
        for year in (rng.randint(1925, 1945), rng.randint(1955, 1980)):
            care.append(dict(by="owner", since=year, care=round(rng.uniform(0.05, 0.6), 2)))
        return dict(base, built=built, built_as="tread_on_riser", finish="split", footfall=rng.randint(2000, 9000),
                    upkeep=care, works=[])
    if name.startswith("stair-lane"):
        # the Holm's stair-lanes, laid by the town when the Holm was rebuilt after the 1860s (docs/town-system.md):
        # dressed granite as it came in from about 1870
        built = rng.randint(1868, 1880)
        up = _town(rng, built, 0.55, [(1930, 0.8), (1946, 1.25), (1965, 0.6)])
        return dict(base, stone="granite", built=built, built_as="block", finish="dressed",
                    footfall=rng.randint(12000, 30000), upkeep=up, works=_campaigns(rng, built, windows[1:], up))
    if name.startswith("the way to"):
        # a house's own doorsteps, laid with the house by its owner; an empty house's let go
        built = rng.randint(1850, 1930)
        care = [dict(by="owner", since=built, care=round(rng.uniform(0.3, 0.7), 2))]
        if "empty since" in name:
            year = int(name.split("empty since ")[1].split(")")[0])
            care.append(dict(by="owner", since=year, care=0.0))
        return dict(base, built=built, built_as="block", finish="split", footfall=rng.randint(800, 2500),
                    upkeep=care, works=[])
    return None
