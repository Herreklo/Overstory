"""Score the cold readers of the corner through the years (docs/experiments.md, LT1f; docs/foundations.md, Cold readers).

    python3 blender/tools/time_score.py [reviews/lt1/time/readers]

Reads, under the readers' folder:
- key.json (time_key.py): each house's parts per year and its changes per pair of years, for the record (real) and
  the shuffled control;
- codes.json per arm (packs/<arm>/codes.json): which frame code is which year;
- answers/<reader>-<phase>.json: each reader's answers, as they gave them;
- coding/<key>.json: the coder's codes for every free-text claim, against the real key and against the shuffled one,
  made blind to the arm (claims/claims.json lists the claims under neutral ids).
Writes scores.json and scores.md beside them. Plain Python; no numbers are typed in by hand.
"""

import json
import os
import sys
from collections import defaultdict

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
YEARS = ("1989", "2000", "2010", "2020")
PAIRS = ("1989-2000", "2000-2010", "2010-2020")
PARTS = ("roof", "upper windows", "ground floor", "additions", "care")
VIEWS = ("eye", "street", "12m", "city")
FALSE = ("texture", "contradiction")
FRAMES = 16  # four views at four years

# the direction between each pair, from the record: open businesses and neglected houses counted
# (2010 to 2020 changes neither count; A's front and C's windows were renewed, so "better kept" is also accepted)
DIRECTION = {
    "real": {"1989-2000": ({"busier"}, {"worse kept"}), "2000-2010": ({"quieter"}, {"better kept"}),
             "2010-2020": ({"same"}, {"same", "better kept"})},
}


def load(path, default=None):
    return json.load(open(path)) if os.path.exists(path) else default


def directions(key):
    """The direction between each pair from a key: businesses open (a house whose ground floor holds an open shop)
    and houses neglected."""
    out = {}
    for t0, t1 in zip(YEARS, YEARS[1:]):
        neg = [sum(key["houses"][h]["parts"][y]["care"]["state"] == "neglected" for h in key["houses"]) for y in (t0, t1)]
        out[f"{t0}-{t1}"] = neg
    return out


def parts_score(answer, key, against="state"):
    """Of the parts a reader marked (not unsure), how many match the key; and of all parts, how many were marked right."""
    marked = right = total = 0
    by_part = defaultdict(lambda: [0, 0])
    for h, years in key["houses"].items():
        for y in YEARS:
            for p in PARTS:
                truth = years["parts"][y][p][against]
                total += 1
                a = (((answer.get(h) or {}).get(y) or {}).get(p) or ["unsure"])
                state = a[0] if isinstance(a, list) else a
                if state in ("unsure", None, ""):
                    continue
                marked += 1
                ok = state == truth
                right += ok
                by_part[p][0] += ok
                by_part[p][1] += 1
    return dict(precision=right / marked if marked else None, recall=right / total, marked=marked, right=right, total=total,
                by_part={p: (r / n if n else None) for p, (r, n) in by_part.items()})


def order_score(answer, codes):
    out = {}
    for view in VIEWS:
        a = (answer.get("order") or {}).get(view) or {}
        seq = a.get("sequence") or []
        truth = sorted((c.split("-")[-1] for c in codes if codes[c]["view"] == view), key=lambda k: codes[f"{view}-{k}"]["year"])
        years = a.get("years") or {}
        errs = {k: abs(int(years[k]) - codes[f"{view}-{k}"]["year"]) for k in years if f"{view}-{k}" in codes and str(years[k]).lstrip("-").isdigit()}
        out[view] = dict(right=list(seq) == truth, sequence=seq, truth=truth, confidence=a.get("confidence"),
                         within5=sum(e <= 5 for e in errs.values()), within10=sum(e < 10 for e in errs.values()), dated=len(errs),
                         mean_error=sum(errs.values()) / len(errs) if errs else None)
    return out


def changes_score(reader, key, coding, rec):
    """Per pair, the changes clay draws (one per house that changed in a drawn way) found by at least one of the
    reader's claims for that pair, coded as a fact (or a fair reading) matching an event of that house in that pair."""
    found, drawn = {}, {}
    for pair in PAIRS:
        need = {h for h, hk in key["houses"].items() if any(c["drawn"] for c in hk["changes"][pair])}
        got = set()
        for c in coding:
            if c.get("reader") == reader and c.get("task") == "changes" and c.get("pair") == pair and c["code"] in ("fact", "fair"):
                for m in c.get("matches", []):
                    h = m[0]
                    if h in need and m in rec[h]["pairs"][pair]:
                        got.add(h)
        found[pair], drawn[pair] = sorted(got), sorted(need)
    n = sum(len(v) for v in drawn.values())
    return dict(found=found, drawn=drawn, recall=sum(len(v) for v in found.values()) / n if n else None)


def false_claims(reader, coding):
    bad = [c for c in coding if c["reader"] == reader and c["code"] in FALSE]
    return dict(count=len(bad), per_frame=len(bad) / FRAMES, high=sum(1 for c in bad if (c.get("confidence") or 0) >= 3),
                claims=[(c["text"], c["code"], c.get("confidence")) for c in bad])


def direction_score(answer, arm):
    truth = DIRECTION.get(arm)
    if not truth:
        return None
    out = {}
    for pair in PAIRS:
        a = (answer.get("direction") or {}).get(pair) or {}
        acts, cares = truth[pair]
        out[pair] = dict(activity=a.get("activity") in acts, care=a.get("care") in cares, given=a)
    out["all_right"] = all(v["activity"] and v["care"] for k, v in out.items() if k in PAIRS)
    return out


def main(argv):
    base = os.path.join(ROOT, argv[0] if argv else "reviews/lt1/time/readers")
    keys = load(os.path.join(base, "key.json"))
    readers = load(os.path.join(base, "readers.json"))
    coding = {k: load(os.path.join(base, "coding", f"{k}.json"), []) for k in ("real", "shuffled")}
    claims = {c["cid"]: c for c in load(os.path.join(base, "claims", "claims-map.json"), [])}
    recs = {k: load(os.path.join(base, "claims", f"record-{k}.json")) for k in ("real", "shuffled")}
    for k in coding:
        for c in coding[k]:
            c.update({f: claims[c["cid"]][f] for f in ("reader", "task", "pair", "house", "text", "confidence") if c["cid"] in claims})
    scores = {}
    for r in readers:
        rid, arm = r["id"], r["arm"]
        first = load(os.path.join(base, "answers", f"{rid}-{r['first']}.json"), {})
        s = dict(arm=arm, role=r["role"])
        if arm in ("scene", "shuffled"):
            codes = load(os.path.join(base, "packs", "shuffled" if arm == "shuffled" else "real", "codes.json"))
            s["order"] = order_score(load(os.path.join(base, "answers", f"{rid}-1.json"), {}), codes)
            ans = load(os.path.join(base, "answers", f"{rid}-2.json"), {})
        else:
            ans = first
        s["parts_record"] = parts_score(ans.get("parts") or {}, keys["real"], "state")
        s["parts_drawn"] = parts_score(ans.get("parts") or {}, keys["real"], "drawn")
        if arm == "shuffled":
            s["parts_vs_shown"] = parts_score(ans.get("parts") or {}, keys["shuffled"], "drawn")
            s["changes_vs_shown"] = changes_score(rid, keys["shuffled"], coding["shuffled"], recs["shuffled"])
            s["false_vs_shown"] = false_claims(rid, coding["shuffled"])
        s["changes"] = changes_score(rid, keys["real"], coding["real"], recs["real"])
        s["false"] = false_claims(rid, coding["real"])
        s["direction"] = direction_score(ans, "real")
        last = load(os.path.join(base, "answers", f"{rid}-3.json" if arm == "scene" else f"{rid}-2.json"), {}) if arm in ("scene", "page") else {}
        s["told_more"] = (last.get("told_more") or [None])[0] if last else None
        scores[rid] = s
    with open(os.path.join(base, "scores.json"), "w") as f:
        json.dump(scores, f, indent=1)
        f.write("\n")
    lines = ["# Scores", "", "Written by `blender/tools/time_score.py` from the answers, the key and the blind coding.", "",
             "| Reader | Arm | Role | Order right (views of 4) | Dated within 5 y | Parts right of marked (record / drawn) | Parts right of all (record) | Changes found (drawn) | False claims a frame (high) | Direction | Told more |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    pct = lambda v: "-" if v is None else f"{100 * v:.0f}%"
    for rid, s in scores.items():
        o = s.get("order")
        order = f"{sum(v['right'] for v in o.values())}/4" if o else "-"
        dated = f"{sum(v['within5'] for v in o.values())}/{sum(v['dated'] for v in o.values())}" if o else "-"
        d = s["direction"]
        lines.append(f"| {rid} | {s['arm']} | {s['role']} | {order} | {dated} | {pct(s['parts_record']['precision'])} / {pct(s['parts_drawn']['precision'])} | "
                     f"{pct(s['parts_record']['recall'])} | {pct(s['changes']['recall'])} | {s['false']['per_frame']:.2f} ({s['false']['high']}) | "
                     f"{'right' if d and d['all_right'] else 'wrong somewhere'} | {s['told_more'] or '-'} |")
    sh = [s for s in scores.values() if s["arm"] == "shuffled"]
    sc = [s for s in scores.values() if s["arm"] == "scene"]
    if sh and sc:
        a = sum(s["parts_drawn"]["precision"] or 0 for s in sc) / len(sc)
        b = sum(s["parts_drawn"]["precision"] or 0 for s in sh) / len(sh)
        c = sum(s["parts_vs_shown"]["precision"] or 0 for s in sh) / len(sh)
        lines += ["", f"Shuffled control: parts right of marked, against the real record as drawn, {100 * a:.0f}% in the scene arm and {100 * b:.0f}% "
                      f"in the shuffled arm (a fall of {100 * (a - b):.0f} points; the bar is 30). Against what the shuffled frames showed: {100 * c:.0f}%."]
    by = defaultdict(list)
    for rid, s in scores.items():
        for p, v in s["parts_drawn"]["by_part"].items():
            if v is not None and s["arm"] == "scene":
                by[p].append(v)
    if by:
        lines += ["", "Scene arm, parts right of marked against the drawing, by part: " + ", ".join(f"{p} {pct(sum(v) / len(v))}" for p, v in by.items()) + "."]
    with open(os.path.join(base, "scores.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
