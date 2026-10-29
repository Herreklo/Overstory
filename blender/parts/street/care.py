"""A keeper's care, derived (docs/engine-requests.md 13): when each house was repainted, by one seeded rule.

    python3 blender/parts/street/care.py fixtures/lt1-street.json

Before the pack's peopleStart a kept house was repainted every cycle (paints.json upkeep: the pack's past). From then
on care is the keeper's: until the engine exports keepers it is derived here from the record, the keeper's wealth (the
house's, as built) and whether they live there (its type), each turn's length seeded, until the record's neglect or
boarding stops it. The derived coats are written into the fixture as dated 'repainted' events with provenance
'derived', so the record is the only thing paint.py reads; a recorded repaint resets the turn. Run again, it replaces
its own events and keeps every other.
"""

import json
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "blender", "resolver"))
import hashing as HS  # noqa: E402

CAUSE = "upkeep (derived)"


def cycle(wealth, paints):
    """The pack's cycle: years between coats by the house's wealth (the poor less often)."""
    lo, hi = paints["upkeep"]["cycleYears"]
    return lo + (hi - lo) * min(max(wealth / 1000.0, 0.0), 1.0)


def stop_year(events, year):
    """The first neglect or boarding by `year`, which ends the care; else `year`."""
    stops = [e["year"] for e in events if e["kind"] in ("neglected", "boarded") and e["year"] <= year]
    return min(stops) if stops else year


def pack_last(since, cyc, until):
    """The pack's last coat before `until`: its cycle's last turn, counted from `since`."""
    return since + max(0, math.floor((until - since) / cyc - 1e-9)) * cyc


def derive(rec, pack, paints):
    """The years of a building's derived coats, from peopleStart to its stop (or the show year)."""
    D = paints["upkeep"]["derived"]
    ev = [e for e in rec["events"] if e.get("cause") != CAUSE]
    built = next(e for e in ev if e["kind"] == "built")
    cyc0 = cycle(built["params"]["wealth"], paints)
    cyc = cyc0 * (1.0 if rec["type"] in D["livedIn"] else D["absentFactor"])
    start, show = pack["peopleStart"], pack["showYear"]
    stop = stop_year(ev, show)
    recorded = sorted(e["year"] for e in ev if e["kind"] == "repainted")
    t = pack_last(built["year"], cyc0, min(stop, start)) if built["year"] < start else built["year"]
    out, n = [], 0
    while True:
        u = HS.unit(HS.h(pack["worldSeed"], rec["id"], "care", n))
        nxt = t + cyc * (1.0 + D["jitter"] * (2.0 * u - 1.0))
        n += 1
        rec_ = [y for y in recorded if t < y <= nxt]
        if rec_:
            t = rec_[-1]
            continue
        if nxt >= stop or nxt > show:
            return out
        if nxt >= start:
            out.append(int(round(nxt)))
        t = nxt


def main():
    path = sys.argv[1]
    fx = json.load(open(path))
    St = json.load(open(os.path.join(ROOT, "blender", "parts", "street", "street.json")))
    pack = json.load(open(os.path.join(ROOT, St["pack"])))
    paints = json.load(open(os.path.join(ROOT, St["paints"])))
    for rec in fx["buildings"]:
        kept = [e for e in rec["events"] if e.get("cause") != CAUSE]
        nid = max(e["id"] for e in kept) + 1
        years = derive(rec, pack, paints)
        new = [{"id": nid + k, "year": y, "kind": "repainted", "params": {}, "cause": CAUSE, "provenance": "derived"}
               for k, y in enumerate(years)]
        rec["events"] = sorted(kept + new, key=lambda e: (e["year"], e["id"]))
        print(f"[care] {rec['id']} ({rec['type']}): derived coats {years}")
    with open(path, "w") as f:
        json.dump(fx, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
