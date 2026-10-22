"""The landing rule's check (blender/generators/stone.py, step_plan): every named stair's flights set out over seeds 1
to 500, each held to the rule, read back from the set-out itself (its fronts S and depths D), not from what step_plan
says it did:

- no flight raises (a flight that cannot be set out is the plan's fault: listed, with its reason);
- the rests it needs are laid, and no run between them is longer than the builder's patience, or the limit of real
  practice (18 risers, 3.3 m of rise) where the flight is flagged for it;
- the rise is one the stone's range gives, rounded to whole risers;
- two rises and a going stay within 0.59 to 0.70 m;
- every landing between runs is at least one stride and one going (landing_min);
- the set-out spans the flight's run exactly.

Prints each flight's riser counts, rises, fallbacks and turn landings shorter than landing_min (the turn's landing
gives way to the steps and their rests: shown, not failed), and exits 1 on any failure.

    blender -b --factory-startup --python blender/tools/setout_check.py [-- seeds]
"""

import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "generators"))
sys.path.insert(0, os.path.join(HERE, "..", "blockouts"))
sys.path.insert(0, os.path.join(HERE, "..", "resolver"))
import hashing as HS  # noqa: E402
import stone as ST  # noqa: E402
# (stair_facts and the town plan, heart_layout, are imported in main(): the plan takes a minute to import, and the
# stair kind's checks stage calls check_flight without it)

BLONDEL = (0.59, 0.70)
TOL = 1e-6


def check_flight(f, spec, fi, seed):
    """One flight, one seed: (plan or None, [failures], feasibility)."""
    feas = ST.setout_feasible(f, spec, fi, seed)
    try:
        p = ST.step_plan(f, spec, fi, seed)
    except Exception as e:      # noqa: BLE001  (every failure is listed, whatever raised it)
        return None, [f"raises: {e}"], feas
    bad = []
    if not feas["ok"]:
        bad.append(f"set out though setout_feasible says no: {feas['reason']}")
    if feas["fallback"] != (p["fallback"] is not None):
        bad.append("setout_feasible and step_plan disagree on the fallback")
    a, b = f["a"], f["b"]
    run = float(((b - a)[:2] ** 2).sum() ** 0.5)
    Hh = float(b[2] - a[2])
    n, r, g, S, D = p["n"], p["r"], p["g"], p["S"], p["D"]
    lo, hi = ST.stone_rises(spec)
    # the rise: a count of risers the stone's range rounds to
    if not max(1, round(Hh / hi)) <= n <= max(1, round(Hh / lo)):
        bad.append(f"rise {r:.4f} outside the stone's {lo:.2f} to {hi:.2f} m ({n} risers over {Hh:.3f} m)")
    if abs(n * r - Hh) > TOL:
        bad.append(f"{n} risers of {r:.4f} m do not make {Hh:.3f} m")
    # two rises and a going
    if not BLONDEL[0] - TOL <= 2 * r + g <= BLONDEL[1] + TOL:
        bad.append(f"2R + G = {2 * r + g:.3f} m outside {BLONDEL[0]} to {BLONDEL[1]}")
    # the landings, read from the depths: a step whose tread runs on past its going, but for the top one
    land = [(i, D[i] - g) for i in range(n - 1) if D[i] > g + TOL]
    L = ST.landing_min(ST.going_of(r))
    for i, x in land:
        if x < L - TOL:
            bad.append(f"landing after step {i} is {x:.3f} m, under {L:.3f} m")
    # the runs between them, against the patience, or the limit of real practice where flagged
    if p["fallback"]:
        limit = ST.practice_limit(r)
        if limit > ST.RUN_RISERS_MAX or limit * r > ST.RUN_RISE_MAX + TOL:
            bad.append(f"fallback limit {limit} risers of {r:.3f} m breaks real practice")
    else:
        limit = feas["patience"]
    # (the patience drawn as the rule draws it: the rise's unit first where the stone gives a range, then the patience)
    rng = HS.Stream(seed, ST.flight_id(spec, fi), "setout")
    if hi > lo:
        rng.random()
    if rng.randint(*ST.PATIENCE.get(spec["upkeep"][0]["by"], ST.OWN_PATIENCE)) != feas["patience"]:
        bad.append("the patience is not the flight's second draw")
    edges = [0] + [i + 1 for i, _ in land] + [n]
    runs = [y - x for x, y in zip(edges, edges[1:])]
    if max(runs) > limit:
        bad.append(f"a run of {max(runs)} risers where no more than {limit} may run unbroken (runs {runs})")
    if len(land) < ST.rests_needed(n, limit):
        bad.append(f"{len(land)} landings where {n} risers need {ST.rests_needed(n, limit)}")
    # the set-out spans the run: the turn's landing, the goings and the landings, to the top
    if abs(S[-1] + D[-1] - run) > TOL or abs(S[0] - p["start"]) > TOL:
        bad.append(f"the set-out spans {S[-1] + D[-1]:.4f} m of a {run:.4f} m run")
    return p, bad, feas


def main():
    import stair_facts as SF
    import heart_layout as H
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    seeds = range(1, int(argv[0]) + 1) if argv else range(1, 501)
    failures, flights = [], 0
    totals = collections.Counter()
    for name in ST.VARIETY:
        lane = next((l for l in H.LANES if l["name"] == name), None)
        spec = ST.FLIGHTS["gully"] if name == "Gully Steps" else (SF.facts_for(lane) if lane else None)
        if spec is None:
            failures.append((name, "-", "-", "no lane or no facts in the plan"))
            continue
        for fi, f in enumerate(ST.flights_of(lane)):
            if f.get("flag"):
                feas = ST.setout_feasible(f, spec, fi, 1)
                print(f"{name[:26]:26s} fl{fi:<2d} not built: {f['flag']}" +
                      ("" if not feas["ok"] else "  (but setout_feasible says it fits)"))
                if feas["ok"]:
                    failures.append((name, fi, "-", "a flagged flight called feasible"))
                continue
            if f["form"] == "step_ramp":
                for seed in seeds:
                    try:
                        ST.step_plan(f, spec, fi, seed)
                    except Exception as e:      # noqa: BLE001
                        failures.append((name, fi, seed, f"step-ramp raises: {e}"))
                print(f"{name[:26]:26s} fl{fi:<2d} step-ramp, {f['n']} strides")
                continue
            flights += 1
            c = collections.Counter()
            ns, rs = [], []
            for seed in seeds:
                p, bad, feas = check_flight(f, spec, fi, seed)
                for msg in bad:
                    failures.append((name, fi, seed, msg))
                c["fail"] += bool(bad)
                if p is None:
                    c["raise"] += 1
                    continue
                c["fallback"] += p["fallback"] is not None
                c["rests"] += p["rests"] > 0
                c["turn short"] += fi > 0 and p["start"] < p["landing_min"] - TOL
                ns.append(p["n"])
                rs.append(p["r"])
            totals.update(c)
            lo, hi = ST.stone_rises(spec)
            out = "" if not rs or (lo - TOL <= min(rs) and max(rs) <= hi + TOL) else "  (rise outside by rounding)"
            print(f"{name[:26]:26s} fl{fi:<2d} n {min(ns, default=0)}-{max(ns, default=0)}  "
                  f"r {min(rs, default=0):.3f}-{max(rs, default=0):.3f}  needs rests {c['rests']:3d}  "
                  f"fallback {c['fallback']:3d}  raises {c['raise']:3d}  turn landing short {c['turn short']:3d}  "
                  f"failed {c['fail']:3d}{out}")
    print(f"\n{flights} flights x {len(seeds)} seeds: fallback {totals['fallback']}, raises {totals['raise']}, "
          f"failed draws {totals['fail']}, turn landings under landing_min {totals['turn short']} (shown, not failed)")
    if failures:
        print(f"\nFAIL: {len(failures)} failures")
        for fl_ in sorted({(nm, fi, msg.split(':')[0]) for nm, fi, _, msg in failures})[:40]:
            print("  ", fl_)
        for nm, fi, seed, msg in failures[:20]:
            print(f"   {nm}, flight {fi}, seed {seed}: {msg}")
        sys.exit(1)
    print("PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
