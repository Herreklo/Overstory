"""The corner through the years (docs/experiments.md, LT1f): its five houses' record, the cold readers' key and the page.

    python3 blender/tools/time_key.py [--out reviews/lt1/time/readers]

Plain Python, no Blender: the resolver alone says what each house is in each year.

- HOUSES: the five houses, each with its letter, its id in fixtures/lt1-corner.json and its place in the heart.
- diaries(arm): the five diaries. Arm "real" is the record; arm "shuffled" (the control) moves each house's later
  history, everything after its standing house was built, to another house, renumbered and otherwise unchanged.
- parts(plan): the readers' checklist (roof, upper windows, ground floor: every opening at street level on any
  wall, additions, care) and each item's state in
  the record: original, changed or neglected (care: kept or neglected). `drawn` is what clay shows for it: a restored
  copy is drawn exactly as the original it copies, so it is "changed" in the record and "original" on screen.
- changes(diary, t0, t1): what happened between two years, event by event, with its cause, and whether clay draws it
  (a repaint is a coat, which clay has none of; a sign is drawn only where the shopfront's style has a sign board).
- page(diaries): the record as text, every dated event with its cause, as the cause view would print it.

Writes key.json (both arms), page.md (the real record) and diaries.json (both arms' diaries, which export_time.py
builds from).
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [os.path.join(HERE, "..", "resolver"), os.path.join(HERE, "..", "generators")]

from resolve import resolve, standing  # noqa: E402

YEARS = (1989, 2000, 2010, 2020)

# The five houses. `heart`: the heart's footprint for the house (blender/blockouts/heart_layout.py, lay_out, the
# corner): its front-left corner on the ground, the turn of its front, its width and depth and the height of its
# ground floor, in street metres. The diary's house is set with its front's middle on the heart's and facing as the
# heart's does. `place`: where it stands, in the words both the scene's and the page's readers get.
HOUSES = [
    dict(letter="A", id=104, heart=dict(ox=37.2, oy=1.7966, angle=-0.7093, w=9.8, d=9.2, base=1.9),
         place="on the quay road at the foot of the stepped lane, on the left of the lane as you look up it"),
    dict(letter="B", id=105, heart=dict(ox=52.0, oy=1.6133, angle=-0.7093, w=9.4, d=8.4, base=1.9),
         place="on the quay road at the foot of the stepped lane, on the right of the lane as you look up it"),
    dict(letter="C", id=1203, heart=dict(ox=41.4, oy=38.3, angle=180.0, w=7.2, d=7.4, base=8.2),
         place="halfway up, on the left, beside the landing where the lane turns"),
    dict(letter="D", id=1107, heart=dict(ox=53.6, oy=48.0969, angle=-90.0, w=7.6, d=7.0, base=12.65),
         place="halfway up, on the right, on top of the rock outcrop above the landing"),
    dict(letter="E", id=304, heart=dict(ox=50.0, oy=86.2016, angle=90.0, w=7.0, d=6.8, base=16.6),
         place="at the top of the lane, the small house that closes the view up it"),
]

# The shuffled control: each house takes the later history of another (a derangement, fixed).
SHUFFLE = {"A": "B", "B": "C", "C": "D", "D": "E", "E": "A"}

PARTS = ("roof", "upper windows", "ground floor", "additions", "care")


def fixture():
    return json.load(open(os.path.join(ROOT, "fixtures", "lt1-corner.json")))


def standing_built(diary):
    """The index of the event that built the house standing now (after a fire, the rebuilding)."""
    return max(i for i, e in enumerate(diary["events"]) if e["kind"] == "built")


def diaries(arm="real"):
    fx = fixture()
    by_id = {b["id"]: b for b in fx["buildings"]}
    real = {h["letter"]: json.loads(json.dumps(by_id[h["id"]])) for h in HOUSES}
    if arm == "real":
        return real
    out = {}
    for letter, donor in SHUFFLE.items():
        own = real[letter]
        k = standing_built(own)
        head = own["events"][: k + 1]
        tail = real[donor]["events"][standing_built(real[donor]) + 1:]
        d = json.loads(json.dumps(own))
        d["events"] = head + [dict(e, id=len(head) + 1 + i, shuffled_from=donor) for i, e in enumerate(json.loads(json.dumps(tail)))]
        d["note"] = f"Shuffled control: {letter}'s own house, with {donor}'s later history."
        out[letter] = d
    return out


# -- the parts on the readers' checklist ----------------------------------------------------------------------------


def _windows_state(cells, built):
    if not cells:
        return dict(state="none", drawn="none")
    if any("boarded" in c for c in cells):
        return dict(state="neglected", drawn="neglected")
    if all(c["part"]["event"] == built and not c["part"].get("restored") for c in cells):
        return dict(state="original", drawn="original")
    later = [c for c in cells if c["part"]["event"] != built or c["part"].get("restored")]
    copies = all(c["part"].get("restored") for c in later)
    return dict(state="changed", drawn="original" if copies else "changed")


def parts(plan):
    built = plan["main"]["event"]
    cells = [c for c in plan["cells"] if standing(c)]
    windows = [c for c in cells if c["part"]["type"] == "window"]
    upper = [c for c in windows if c.get("row", 0) >= 1]
    ground = [c for c in cells if c.get("row", 0) == 0 and c["part"]["type"] in ("window", "door", "inner_door", "shopfront")]
    out = {}
    out["roof"] = dict(state="original" if plan["main"]["roof"]["event"] == built else "changed")
    out["roof"]["drawn"] = out["roof"]["state"]
    out["upper windows"] = _windows_state(upper, built)
    g = _windows_state([c for c in ground if c["part"]["type"] != "shopfront"], built)
    if any(c["part"]["type"] == "shopfront" and c["part"]["event"] != built for c in ground):
        g = dict(state="neglected" if g["state"] == "neglected" else "changed", drawn="neglected" if g["state"] == "neglected" else "changed")
    if any(c["part"]["type"] == "shopfront" and "boarded" in c for c in ground):
        g = dict(state="neglected", drawn="neglected")
    out["ground floor"] = g
    adds = plan["additions"]
    if not adds:
        out["additions"] = dict(state="none", drawn="none")
    else:
        later = [a for a in adds if a["event"] != built]
        s = "changed" if later else "original"
        out["additions"] = dict(state=s, drawn=s, kinds=sorted(a["kind"] for a in adds), later=sorted(a["kind"] for a in later))
    neglected = plan["condition"] < 500 or any("boarded" in c for c in cells)
    out["care"] = dict(state="neglected" if neglected else "kept", drawn="neglected" if neglected else "kept", condition=plan["condition"])
    return out


# -- what changed between two years ---------------------------------------------------------------------------------

SIGNED = ("shop_1900", "shop_1960", "shop_1980")  # shopfront styles whose sign is a board or a box, not a colour


def _shop_style(plan):
    for c in plan["cells"]:
        if c["part"]["type"] == "shopfront" and standing(c):
            return c["part"]["style"]
    for c in plan["cells"]:
        if c["part"]["type"] == "shopfront":
            return c["part"]["style"]
    return None


def changes(diary, t0, t1, ws):
    """Every event in (t0, t1], with whether clay draws it. Events that change nothing drawn are kept (the key holds
    the whole record), marked drawn=False."""
    out = []
    for e in sorted(diary["events"], key=lambda e: (e["year"], e["id"])):
        if not (t0 < e["year"] <= t1):
            continue
        before = resolve(diary, e["year"] - 1, ws) if e["year"] - 1 >= t0 else resolve(diary, t0, ws)
        after = resolve(diary, e["year"], ws)
        k = e["kind"]
        if k == "repainted":
            drawn = False
        elif k in ("business_opened", "business_closed"):
            drawn = (_shop_style(after) or _shop_style(before)) in SIGNED
        elif k == "neglected":
            cb, ca = before["condition"] if before else 1000, after["condition"] if after else 0
            drawn = (cb > 450) != (ca > 450)  # the curtains go when no one lives there; sag alone is too slight to count
        elif k == "restored":
            drawn = bool(e["params"].get("windows")) or (before and after and (before["condition"] > 450) != (after["condition"] > 450))
        else:
            drawn = True
        out.append(dict(year=e["year"], kind=k, params=e["params"], cause=e.get("cause", ""), rule=e.get("rule"),
                        drawn=bool(drawn), words=event_words(e, diary)))
    return out


# -- the page ---------------------------------------------------------------------------------------------------------

ERA_WORDS = dict(classical="classical (empire)", chalet="Swiss chalet", jugend="jugend (art nouveau)",
                 functionalist="functionalist", postwar="post-war", seventies="1970s", eighties="1980s", recent="present-day")
SCOPE_WORDS = dict(all="all of them", street="those on the front", upper="those on the upper floor",
                   ground="those on the front of the ground floor", back="those at the back")
STOREY_WORDS = {1000: "one-storey", 1500: "storey-and-a-half", 2000: "two-storey", 2500: "two-and-a-half-storey"}
ADD_WORDS = dict(veranda="a balcony", lean_to="a lean-to", bislag="a porch", bay="a bay window", dormers="dormers", ark="a cross-gable")


def event_words(e, diary=None):
    p, k = e["params"], e["kind"]
    if k == "built":
        roof = f", with a {p['roof']} roof" if p.get("roof") in ("mansard", "flat") else ""
        return f"built: a {STOREY_WORDS.get(p.get('storeys'), '')} house in the {ERA_WORDS.get(p.get('era'), p.get('era'))} style{roof}"
    if k == "demolished":
        return "burned down" if p.get("by") == "fire" else "demolished"
    if k == "shop_fitted":
        return f"a shopfront fitted in the ground floor, across {p.get('cols', 2)} window bays"
    if k == "business_opened":
        name = f" ({p['name']})" if p.get("name") else ""
        what = {"cafe": "café"}.get(p["kind"], p["kind"].replace("_", " "))
        return f"{'an' if what[0] in 'aeiou' else 'a'} {what} opens in the shop{name}"
    if k == "business_closed":
        return "the shop closes"
    if k == "repainted":
        return "repainted"
    if k == "windows_replaced":
        return f"windows replaced: {SCOPE_WORDS.get(p.get('scope', 'all'), p.get('scope'))}"
    if k == "restored":
        w = ", windows copied from the originals" if p.get("windows") == "original" else ""
        sc = f" ({SCOPE_WORDS.get(p['scope'], p['scope'])})" if p.get("scope") else ""
        return f"restored{w}{sc}"
    if k == "boarded":
        return f"windows and doors boarded up: {SCOPE_WORDS.get(p.get('scope', 'ground'), p.get('scope'))}"
    if k == "unboarded":
        return f"the boards taken down: {SCOPE_WORDS.get(p.get('scope', 'ground'), p.get('scope'))}"
    if k == "neglected":
        return "neglected"
    if k == "extended":
        side = " over the lane" if p.get("kind") == "veranda" else (" at the back" if p.get("side") == "back" else "")
        return f"extended: {ADD_WORDS.get(p.get('kind'), p.get('kind'))}{side}"
    if k == "shop_removed":
        w = ", with copies of the windows it had covered" if p.get("windows") == "original" else ", with new windows"
        return f"the shopfront taken out and the ground floor made a home{w}"
    if k == "roof_retiled":
        return "the roof retiled"
    return k.replace("_", " ")


def page(ds):
    lines = ["# The corner's record", "",
             "Five houses on a stepped lane that climbs from a harbour's quay road, in a Norwegian west-coast town. "
             "Every dated event the town's record holds for each house, with its cause.", ""]
    for h in HOUSES:
        d = ds[h["letter"]]
        lines += [f"## House {h['letter']}", "", f"Where: {h['place']}.", ""]
        for e in sorted(d["events"], key=lambda e: (e["year"], e["id"])):
            cause = f" Cause: {e['cause']}." if e.get("cause") and e["cause"] != "upkeep" else (" Cause: upkeep." if e.get("cause") == "upkeep" else "")
            lines.append(f"- {e['year']}: {event_words(e, d)}.{cause}")
        lines.append("")
    return "\n".join(lines)


# -- the key ----------------------------------------------------------------------------------------------------------


def key(arm, ws):
    ds = diaries(arm)
    out = dict(arm=arm, years=list(YEARS), parts=list(PARTS), houses={})
    for h in HOUSES:
        d = ds[h["letter"]]
        per_year = {}
        for y in YEARS:
            plan = resolve(d, y, ws)
            per_year[str(y)] = parts(plan)
        pairs = {}
        for t0, t1 in zip(YEARS, YEARS[1:]):
            pairs[f"{t0}-{t1}"] = changes(d, t0, t1, ws)
        out["houses"][h["letter"]] = dict(id=h["id"], place=h["place"], parts=per_year, changes=pairs,
                                          before=[dict(year=e["year"], kind=e["kind"], words=event_words(e, d), cause=e.get("cause", ""))
                                                  for e in sorted(d["events"], key=lambda e: (e["year"], e["id"])) if e["year"] <= YEARS[0]])
    # the budget per pair: the changes clay draws, house by house
    out["drawn_per_pair"] = {f"{t0}-{t1}": sum(any(c["drawn"] for c in out["houses"][h["letter"]]["changes"][f"{t0}-{t1}"]) for h in HOUSES)
                             for t0, t1 in zip(YEARS, YEARS[1:])}
    return out


def main(argv):
    opts = dict(zip(argv[0::2], argv[1::2]))
    out = os.path.join(ROOT, opts.get("--out", "reviews/lt1/time/readers"))
    os.makedirs(out, exist_ok=True)
    ws = fixture()["worldSeed"]
    keys = dict(real=key("real", ws), shuffled=key("shuffled", ws))
    with open(os.path.join(out, "key.json"), "w") as f:
        json.dump(keys, f, indent=1, ensure_ascii=False)
        f.write("\n")
    with open(os.path.join(out, "page.md"), "w") as f:
        f.write(page(diaries("real")) + "\n")
    with open(os.path.join(out, "diaries.json"), "w") as f:
        json.dump(dict(real=diaries("real"), shuffled=diaries("shuffled"), houses=HOUSES, years=list(YEARS)), f, indent=1, ensure_ascii=False)
        f.write("\n")
    for arm, k in keys.items():
        print(arm, "houses changed in clay per pair:", k["drawn_per_pair"])
        for letter, hk in k["houses"].items():
            row = " | ".join(f"{y}: " + ",".join(f"{p[0:2]}={hk['parts'][str(y)][p]['drawn'][0:4]}" for p in PARTS) for y in YEARS)
            print(f"  {letter} {row}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
