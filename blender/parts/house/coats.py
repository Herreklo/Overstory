"""A house's coats on a date, from its facts and the pack's paint rule (packs/<pack>/paint.json): the colour each part
wears, the year and paint of its top coat, the colour under it and how many coats lie on the wood.

The care rule walks the house's life from the year it was built: a coat on every part then, in its period's colours; a
repaint every interval its wealth keeps (longer after a 'neglected' event, none while it stands boarded); a dated
'repainted' or 'restored' event puts a coat on in its year, a repaint choosing its colours again from its period; new
windows come painted in their year. A care repaint chooses its colours again from its own period at the rule's
recolourShare, otherwise keeps them; it shows no year a player can read. Under a scheme of the paint rule (a quarter
whose rule chose the colour) a coat from the scheme's year keeps a part's colour while the scheme allows it. Pure
Python: tools/houses.py writes the result into houses.json.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "resolver"))
import hashing as HS  # noqa: E402

PARTS = ("body", "back", "trim", "window", "door")


def _period(paint, year):
    return next(p for p in paint["periods"] if p["from"] <= year < p["to"])


def _system(paint, year, rng):
    s = next(x for x in paint["systems"] if x["from"] <= year < x["to"])
    if s.get("or") and year >= s["orFrom"] and rng.random() < s["orShare"]:
        return s["or"]
    return s["paint"]


def _choose(paint, year, part, rng, colour):
    """A colour from the period's list for the part; a back the period paints as the body takes the body's."""
    p = _period(paint, year)
    if part == "back" and not p.get("back"):
        return colour["body"]
    return rng.choice(p[part])


def scheme_of(paint, lane):
    """The paint rule's scheme over a house placed on the lane, or None."""
    return next((s for s in paint.get("schemes", []) if lane in s["lanes"]), None)


def coats(facts, paint, seed, date, scheme=None):
    """{part: dict(colour, srgb, year, paint, under, underSrgb, count)} for each of PARTS on the date; under is the
    colour of the coat below the top one (the top's own when it was a like-for-like repaint, None on bare wood).
    scheme: the paint rule's scheme the house is under (scheme_of), or None."""
    hid = facts["id"]
    care = paint["care"]
    lo, hi = care["intervalYears"]
    wealth = facts["wealth"] / 1000.0
    rng = HS.Stream(seed, hid, "coats")
    stack = {part: [] for part in PARTS}
    colour = {}

    def coat(year, parts, choose):
        system = _system(paint, year, rng)
        for part in parts:
            was = colour.get(part)
            if choose or part not in colour:
                colour[part] = _choose(paint, year, part, rng, colour)
            # under a scheme the colour stays one it allows (the seed's draws as without it)
            allowed = scheme.get(part) if scheme and year >= scheme["from"] else None
            if allowed and was in allowed:
                colour[part] = was
            elif allowed and colour[part] not in allowed:
                colour[part] = allowed[0]
            stack[part].append((year, colour[part], system))

    def interval(neglect):
        base = lo + (hi - lo) * wealth
        return base * (1.0 + care["intervalJitter"] * (2.0 * rng.random() - 1.0)) / max(0.05, 1.0 - neglect)

    coat(facts["built"], PARTS, True)
    neglect, active = 0.0, True
    due = facts["built"] + interval(neglect)
    for e in [e for e in facts["events"] if e["year"] <= date]:
        y, kind, prm = e["year"], e["kind"], e.get("params", {})
        while active and due <= y:
            coat(due, PARTS, rng.random() < care["recolourShare"])
            due += interval(neglect)
        if kind in ("repainted", "restored"):
            coat(y, PARTS, kind == "repainted")
            due = y + interval(neglect)
        elif kind == "windows_replaced":
            stack["window"] = []
            coat(y, ("window",), True)
        elif kind == "neglected":
            neglect = prm.get("amount", 0) / 1000.0
            due = max(due, y + interval(neglect))
        elif kind == "boarded" and prm.get("scope") == "all":
            active = False
        elif kind == "unboarded" and prm.get("scope") == "all":
            active, due = True, y + interval(neglect)
    while active and due <= date:
        coat(due, PARTS, rng.random() < care["recolourShare"])
        due += interval(neglect)
    out = {}
    for part, st in stack.items():
        year, c, system = st[-1]
        under = st[-2][1] if len(st) > 1 else None
        out[part] = dict(colour=c, srgb=paint["colours"][c]["srgb"], year=round(year, 2), paint=system, under=under,
                         underSrgb=paint["colours"][under]["srgb"] if under else "", count=len(st))
    return out
