"""Stress test: random diaries, resolved at several years, built in every style, checked.

    python stress.py --n 200 --styles gentle,strong,wild [--to 2020]

Each random diary is seeded from its index, so a failure can be reproduced by number. With --to 2020 each diary
also gets events after 1989 (a later key, so the diaries up to 1989 are the same), among them shops taken out,
windows restored a floor at a time and houses burned and rebuilt, and is checked in 2000, 2010 and 2020 as well.
Prints every failure and a summary; exits non-zero if anything failed.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "generators"), os.path.join(HERE, "..", "resolver")]

import bpy  # noqa: E402

import building  # noqa: E402
import validate  # noqa: E402
from hashing import h, between, pick  # noqa: E402
from resolve import resolve  # noqa: E402
from eras import DEFAULT_STYLE, ORDER, ERAS  # noqa: E402

ADDITIONS = ["ark", "bislag", "veranda", "bay", "dormer"]
# the eras a random house is built in: those of the first shelves, so a diary's number names the same diary as new
# shelves are added (the shelf of parts installed after 1995 is reached through --to 2020)
BUILT_ERAS = [e for e in ORDER if e != "recent"]
AFTER = ["repainted", "windows_replaced", "shop_fitted", "shop_removed", "boarded", "unboarded", "neglected", "restored",
         "restored_scope", "extended_veranda", "extended_lean_to", "extended_dormers", "rebuilt"]
LATER = ["extended_lean_to", "extended_bislag", "extended_dormers", "extended_veranda", "windows_replaced", "repainted", "shop_fitted", "boarded", "neglected", "restored"]


def random_diary(i, to=1989):
    k = lambda *p: h(7777, i, *p)
    kind = "warehouse" if k("kind") % 10 == 0 else "house"
    era = pick(k("era"), BUILT_ERAS)
    y0 = between(k("y0"), *ERAS[era]["years"])
    if kind == "warehouse":
        era, y0 = "classical", between(k("wy"), 1820, 1880)
    storeys = pick(k("st"), [1000, 1500, 2000, 2500])
    with_ = [a for a in ADDITIONS if k("with", a) % 3 == 0]
    events = [dict(id=1, year=y0, kind="built", params=dict(era=era, storeys=storeys, wealth=between(k("w"), 100, 950), **({"with": with_} if with_ else {})))]
    year = y0
    for n in range(between(k("n"), 0, 6)):
        year += between(k("dy", n), 3, 25)
        if year > 1989:
            break
        what = pick(k("what", n), LATER)
        ev = dict(id=n + 2, year=year, params={})
        if what.startswith("extended_"):
            ev["kind"] = "extended"
            ev["params"]["kind"] = what.split("_", 1)[1]
        elif what == "windows_replaced":
            ev["kind"] = what
            ev["params"]["scope"] = pick(k("sc", n), ["all", "upper", "street", "back"])
        elif what == "restored":
            ev["kind"] = what
            ev["params"]["windows"] = "original"
        else:
            ev["kind"] = what
        events.append(ev)
    if to > 1989:
        year = max(y0, 1989)  # the later events start after 1989 (or after the house, if it is newer)
        for n in range(between(k("an"), 0, 6)):
            year += between(k("ady", n), 2, 12)
            if year > to:
                break
            what = pick(k("awhat", n), AFTER)
            ev = dict(id=len(events) + 1, year=year, params={})
            if what.startswith("extended_"):
                ev["kind"] = "extended"
                ev["params"]["kind"] = what.split("_", 1)[1]
            elif what == "windows_replaced":
                ev["kind"] = what
                ev["params"]["scope"] = pick(k("asc", n), ["all", "upper", "street", "back", "ground"])
            elif what == "restored":
                ev["kind"] = what
                ev["params"]["windows"] = "original"
            elif what == "restored_scope":
                ev["kind"] = "restored"
                ev["params"] = dict(windows="original", scope=pick(k("ars", n), ["upper", "ground", "street"]))
            elif what == "shop_removed":
                ev["kind"] = what
                if k("aorig", n) % 2:
                    ev["params"]["windows"] = "original"
            elif what in ("boarded", "unboarded"):
                ev["kind"] = what
                ev["params"]["scope"] = pick(k("abs", n), ["all", "ground"])
            elif what == "rebuilt":
                ev["kind"] = "demolished"
                events.append(ev)
                ev = dict(id=len(events) + 1, year=year + 1, kind="built",
                          params=dict(era="recent" if year + 1 >= 1995 else "eighties", storeys=pick(k("ast", n), [1500, 2000]), wealth=500))
                year += 1
            else:
                ev["kind"] = what
            events.append(ev)
    plot = dict(x=0, w=between(k("pw"), 6, 12) * 1000, d=between(k("pd"), 6, 10) * 1000)
    if kind == "warehouse":
        plot = dict(x=0, w=between(k("pw"), 7, 10) * 1000, d=between(k("pd"), 11, 16) * 1000)
    return dict(id=10000 + i, type=kind, plot=plot, events=events)


def main(n, styles, years=(1900, 1935, 1960, 1989), to=1989):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mat = None
    failures, checked = [], 0
    for i in range(n):
        d = random_diary(i, to)
        for year in years + tuple(y for y in (2000, 2010, 2020) if y <= to):
            plan = resolve(d, year, 1989)
            if plan is None:
                continue
            for style in styles:
                try:
                    ob = building.build(plan, style, material=mat)
                    mat = ob.data.materials[0]
                    probs = validate.check(ob)
                    bpy.data.objects.remove(ob, do_unlink=True)
                except Exception as e:  # a crash is a failure too
                    probs = [f"crash: {type(e).__name__}: {e}"]
                checked += 1
                if probs:
                    failures.append((i, year, style, plan["main"]["era"], [a["kind"] for a in plan["additions"]], probs))
    for f in failures:
        print("FAIL", f)
    print(f"checked {checked} buildings, {len(failures)} failed")
    return len(failures)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    opts = dict(zip(argv[0::2], argv[1::2]))
    sys.exit(1 if main(int(opts.get("--n", 100)), opts.get("--styles", DEFAULT_STYLE).split(","), to=int(opts.get("--to", 1989))) else 0)
