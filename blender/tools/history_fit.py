"""History as a function, the fit (step 3, rung R1; docs/research/building-blocks-decisions.md D5.1, D5.2): whether
the stone's per-vertex history today (stone.py at a858766) can be drawn from inputs per texel and the date, by which
law, and at what error after an 8-bit encoding. Numbers only: it builds nothing for Unity and changes no generator.

It drives a frozen copy of the generators, never the live ones (they are being refactored in step 2a):

    git archive a858766 blender | tar -x -C <frozen>
    blender -b --factory-startup --python blender/tools/history_fit.py -- prepare <frozen>
    blender -b --factory-startup --python blender/tools/history_fit.py -- prove   <frozen> <scratch>
    blender -b --factory-startup --python blender/tools/history_fit.py -- collect <frozen> <cache>
    blender -b --factory-startup --python blender/tools/history_fit.py -- fit     <frozen> <cache> [<fit.md>]

prepare  instruments the frozen copy (and only it): stone.py's put() appends its inputs and outputs to stone.TRACE,
         upkeep.flight() appends each event it applies to upkeep.LOG. The arithmetic is untouched (two expressions are
         named, not changed); `prove` shows it by the hash.
prove    builds the gully's stair from the frozen copy into <scratch> and checks its mesh hash is bff7858b698f3efd.
collect  lays the gully at YEAR 1989, 1953, 1964, 1966 and 1975 with the trace on, and runs each flight's life at
         1900, 1930, 1960 and 1975 from the 1989 call's own arguments; pickles both into <cache>.
fit      the fit: (a) the clocks checked; (b) the page model against the 1989 values, float and 8-bit; (c) the same
         at the earlier builds on unchanged fills, by cause, with the rate-only law of D5.1 beside it and the care
         jumps; (d) the prefix test, and the proposed fix run (flight_whole: upkeep.flight's loop with every decade
         drawn whole, checked against the frozen code with the fix off; it lays the gully once more at 1989 to get
         the flights' own arguments). Writes the tables into
         <fit.md> between the markers <!-- fit:tables --> and <!-- /fit:tables --> (the prose around them is kept),
         and prints them.

Runs in Blender's Python (numpy); nothing here needs bpy except `prove`.
"""

import math
import os
import pickle
import sys

import numpy as np

BASELINE = "bff7858b698f3efd"
TODAY = 1989
YEARS = (1953, 1964, 1966, 1975)
CUTS = (1900, 1930, 1960, 1975)
MARK_A, MARK_B = "<!-- fit:tables -->", "<!-- /fit:tables -->"


# ---------------------------------------------------------------------------------------------------------- prepare

STONE_PATCH = [
    ("YEAR = 1989\n",
     "YEAR = 1989\nTRACE = None   # (history_fit instrumentation: a list to append each put's inputs to)\n"),
    ("            lichen = GR.lichen_years(lich_y, np.where(foot_on, traffic, traffic * 0.75), exposed)\n",
     "            ltr = np.where(foot_on, traffic, traffic * 0.75)\n"
     "            lichen = GR.lichen_years(lich_y, ltr, exposed)\n"),
    ("            damp = damp * (1.15 - 0.75 * care_now)\n",
     "            damp_pre = damp\n            damp = damp * (1.15 - 0.75 * care_now)\n"),
    ("            moss = GR.moss(damp, trod * walking(across, W, lean) * np.where(foot_on & (kind != 6), "
     "np.maximum(np.exp(-((np.clip(along, 0, 1) - 0.3) / 0.35) ** 2), 0.7), 1.0), moss_y)\n",
     "            mtr = trod * walking(across, W, lean) * np.where(foot_on & (kind != 6), "
     "np.maximum(np.exp(-((np.clip(along, 0, 1) - 0.3) / 0.35) ** 2), 0.7), 1.0)\n"
     "            moss = GR.moss(damp, mtr, moss_y)\n"),
    ("            out[\"UV3\"].append(np.stack([sky, ground], -1))\n"
     "            return np.stack([x0 + P[:, 0], s0 + P[:, 1], z0 + P[:, 2]], -1)\n",
     "            out[\"UV3\"].append(np.stack([sky, ground], -1))\n"
     "            if TRACE is not None:\n"
     "                TRACE.append(dict(fi=fi, dst=(\"setts\" if dst is not None else \"main\"), base=base, n=len(P),\n"
     "                                  key=getattr(rng, \"key\", None), kind=np.asarray(kind).copy(), foot_on=bool(foot_on),\n"
     "                                  worn_y=worn_y, bare_y=bare_y, bed_y=bed_y, lifted_y=lifted_y, polish0=polish0,\n"
     "                                  year=YEAR, care_now=care_now, footfall=spec[\"footfall\"], wear=stone[\"wear\"], W=W,\n"
     "                                  foot=np.asarray(foot, float).copy(), worn=np.asarray(worn, float).copy(), top=np.asarray(top).copy(),\n"
     "                                  nose=np.asarray(nose).copy(), ltr=np.asarray(ltr, float).copy(),\n"
     "                                  exposed=np.broadcast_to(exposed, (len(P),)).astype(float),\n"
     "                                  lich_y=np.broadcast_to(lich_y, (len(P),)).astype(float),\n"
     "                                  damp_pre=np.broadcast_to(damp_pre, (len(P),)).astype(float),\n"
     "                                  mtr=np.broadcast_to(mtr, (len(P),)).astype(float),\n"
     "                                  moss_y=np.broadcast_to(moss_y, (len(P),)).astype(float),\n"
     "                                  back=np.asarray(back).copy(), joint=np.asarray(joint).copy(),\n"
     "                                  water=np.asarray(water, float).copy(), held=np.asarray(held, float).copy(),\n"
     "                                  polish=np.asarray(polish, float).copy(), lichen=np.asarray(lichen, float).copy(),\n"
     "                                  moss=np.asarray(moss, float).copy(), var=var, edge=np.asarray(piece[\"edge\"], float).copy(),\n"
     "                                  along=np.asarray(along, float).copy(), across=np.asarray(across, float).copy(),\n"
     "                                  sky=np.asarray(sky, float).copy(), ground=np.asarray(ground, float).copy()))\n"
     "            return np.stack([x0 + P[:, 0], s0 + P[:, 1], z0 + P[:, 2]], -1)\n"),
]

UPKEEP_PATCH = [
    ("CEMENT_FROM = 1910\n",
     "CEMENT_FROM = 1910\nLOG = None   # (history_fit instrumentation: a list to append each event to)\n\n\n"
     "def _log(*ev):\n    if LOG is not None:\n        LOG.append(ev)\n"),
    ("                        sl[\"cracked\"] = dict(year=r.randint(y0, y1 - 1), at=r.uniform(0.35, 0.65), filled=None)\n",
     "                        sl[\"cracked\"] = dict(year=r.randint(y0, y1 - 1), at=r.uniform(0.35, 0.65), filled=None)\n"
     "                        _log(\"crack\", _fill(sl), sl[\"cracked\"][\"year\"], round(sl[\"cracked\"][\"at\"], 12))\n"),
    ("                                        size=r.uniform(0.04, 0.09), filled=None)\n",
     "                                        size=r.uniform(0.04, 0.09), filled=None)\n"
     "                    _log(\"corner\", _fill(sl), sl[\"corner\"][\"year\"], sl[\"corner\"][\"side\"], "
     "round(sl[\"corner\"][\"size\"], 12))\n"),
    ("            if what == \"rock\":\n                sl[\"shim\"] = year\n            elif y0 >= CEMENT_FROM:\n"
     "                d = sl[\"corner\"] if what == \"corner\" else sl[\"cracked\"]\n"
     "                d[\"filled\"] = (\"cement\", max(d[\"year\"] + 1, year))\n",
     "            if what == \"rock\":\n                sl[\"shim\"] = year\n                _log(\"shim\", _fill(sl), year)\n"
     "            elif y0 >= CEMENT_FROM:\n                d = sl[\"corner\"] if what == \"corner\" else sl[\"cracked\"]\n"
     "                d[\"filled\"] = (\"cement\", max(d[\"year\"] + 1, year))\n"
     "                _log(\"fix-\" + what, _fill(sl), d[\"filled\"][1])\n"),
    ("                    S[i].update(reset=w[\"year\"], settled=0.0, mortar=(w[\"mortar\"], w[\"year\"]) if w.get(\"mortar\") else None)\n",
     "                    S[i].update(reset=w[\"year\"], settled=0.0, mortar=(w[\"mortar\"], w[\"year\"]) if w.get(\"mortar\") else None)\n"
     "                    _log(\"renew\", slots[\"steps\"][i], w[\"year\"])\n"),
    ("                    st[\"mortar\"] = (w.get(\"mortar\") or mortar_of(w[\"year\"]), w[\"year\"])\n",
     "                    st[\"mortar\"] = (w.get(\"mortar\") or mortar_of(w[\"year\"]), w[\"year\"])\n"
     "                    _log(\"campaign\", slots[\"steps\"][i], w[\"year\"], st[\"mortar\"][0])\n"),
    ("                        sl[\"lifted\"] = w[\"year\"]\n",
     "                        sl[\"lifted\"] = w[\"year\"]\n                        _log(\"lift\", _fill(sl), w[\"year\"])\n"),
    ("                                      cracked=None, corner=None, fill=sl[\"fill\"] + 1)\n"
     "                        elif c and c[\"filled\"] is None:\n                            c[\"filled\"] = (st[\"mortar\"][0], w[\"year\"])\n",
     "                                      cracked=None, corner=None, fill=sl[\"fill\"] + 1)\n"
     "                            _log(\"reclaim\", _fill(sl), w[\"year\"], sl[\"bare\"])\n"
     "                        elif c and c[\"filled\"] is None:\n                            c[\"filled\"] = (st[\"mortar\"][0], w[\"year\"])\n"
     "                            _log(\"campaign-fill\", _fill(sl), w[\"year\"], st[\"mortar\"][0])\n"),
]


def _patch(path, edits, marker):
    with open(path) as fh:
        s = fh.read()
    if marker in s:
        return "already instrumented"
    for old, new in edits:
        if s.count(old) != 1:
            raise SystemExit(f"{path}: anchor found {s.count(old)} times, expected once: {old[:70]!r}")
        s = s.replace(old, new)
    with open(path, "w") as fh:
        fh.write(s)
    return "instrumented"


def prepare(frozen):
    g = os.path.join(frozen, "blender", "generators")
    print("stone.py", _patch(os.path.join(g, "stone.py"), STONE_PATCH, "TRACE = None"))
    print("upkeep.py", _patch(os.path.join(g, "upkeep.py"), UPKEEP_PATCH, "LOG = None"))


def _import(frozen):
    """The frozen generators, with draws that remember their key (the same draws: a Stream's subclass that keeps the
    key it was seeded from, so a trace can name its piece)."""
    g = os.path.join(frozen, "blender", "generators")
    if os.path.abspath(g).startswith(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))):
        raise SystemExit("refusing to drive the live generators: pass the frozen copy")
    sys.path.insert(0, g)
    import stone as ST
    import upkeep as UP
    import hashing as HS
    if not hasattr(ST, "TRACE") or not hasattr(UP, "LOG"):
        raise SystemExit("the frozen copy is not instrumented: run prepare first")
    if not getattr(HS.Stream, "_keyed", False):
        base = HS.Stream

        class Keyed(base):
            _keyed = True

            def __init__(self, *key):
                base.__init__(self, *key)
                self.key = key
        HS.Stream = Keyed
    return ST, UP, HS


# ------------------------------------------------------------------------------------------------------------ prove

def prove(frozen, scratch):
    ST, UP, HS = _import(frozen)
    sys.path.insert(0, os.path.join(frozen, "blender", "tools"))
    ST.build("gully", scratch)
    fbx = os.path.join(scratch, "Assets", "Art", "Stone", "stone_gully.fbx")
    import json
    with open(os.path.join(os.path.dirname(fbx), "mesh-hashes.json")) as fh:
        got = json.load(fh)["stone_gully.fbx"]["hash"]
    print("PROVE", got, "expected", BASELINE, "OK" if got == BASELINE else "DIFFERENT")
    if got != BASELINE:
        raise SystemExit(1)


# ---------------------------------------------------------------------------------------------------------- collect

def collect(frozen, cache):
    ST, UP, HS = _import(frozen)
    os.makedirs(cache, exist_ok=True)
    calls = []
    real_flight = UP.flight

    def flight(*a, **k):
        calls.append((a, k))
        return real_flight(*a, **k)
    UP.flight = flight
    for year in (TODAY,) + YEARS:
        ST.YEAR = year
        ST.TRACE, UP.LOG = [], []
        del calls[:]
        meshes, origin, flags = ST.lay(ST.FLIGHTS["gully"], 1)
        out = dict(year=year, trace=ST.TRACE, log=list(UP.LOG),
                   meshes=[(nm, {k: m[k] for k in ("COL", "UV1", "UV2", "UV3", "steps", "life")}) for nm, m in meshes],
                   calls=[(a, {k: v for k, v in kw.items() if k != "busy"}) for a, kw in calls])
        if year == TODAY:
            # each flight's life re-run at the cuts from the 1989 call's own arguments (now replaced)
            cuts = {}
            for c in CUTS:
                logs = []
                for a, kw in calls:
                    UP.LOG = []
                    args = list(a)
                    args[2] = c
                    real_flight(*args, **kw)
                    logs.append(list(UP.LOG))
                cuts[c] = logs
            out["cuts"] = cuts
            out["flight_logs"] = []
            for a, kw in calls:
                UP.LOG = []
                real_flight(*a, **kw)
                out["flight_logs"].append(list(UP.LOG))
        ST.TRACE, UP.LOG = None, None
        with open(os.path.join(cache, f"trace-{year}.pkl"), "wb") as fh:
            pickle.dump(out, fh, protocol=4)
        print("COLLECT", year, len(out["trace"]), "puts", len(out["log"]), "events")
    UP.flight = real_flight


# -------------------------------------------------------------------------------------------------------------- fit
#
# The page model (the law proposed in fit.md): each layer is an amplitude times its material's curve at a speed, from
# a clock the piece table holds, cut by the date. Per texel only one number a layer (polish's amplitude, lichen's rate,
# moss's amplitude) and the bed's reach; per piece its clocks (placed P, disturbed D, the age it brought X: bare
# B = P - X), its variation, its flags (walked, lifted by hands) and an inherited polish; per thing its use (footfall)
# and its wear rate; per vertex the face kind and the edge distance; per material the curves' constants. The dish's
# share of the wear on a walked tread is the polish amplitude (both are wear.py's foot).

POLISH_CAP = 40.0        # wear.polish: the years after which polish keeps
LICHEN_DELAY = 12.0      # growth.LICHEN_DELAY
LICHEN_FULL = 200.0      # lichen's channel is its years over 200
MOSS_FULL = 60.0         # growth.moss: about sixty years to be full
HELD_FROM, HELD_SPAN = 0.003, 0.003     # stone.put: water stands where the dish is deeper than 3 mm, full at 6 mm
WATER_DISH = 0.004       # water.on_top's hollow: a dish of 4 mm holds water all the time
EDGE_HANDS = 0.06        # stone.put: lichen torn where hands gripped, within 6 cm of a top's edge


def _care_f(care):
    return 1.15 - 0.75 * care


def _q8(x):
    return np.round(np.clip(x, 0.0, 1.0) * 255.0) / 255.0


def assemble(d):
    """Every vertex of the stair (both flights, in mesh order) with its inputs as the page model would hold them, and
    today's values as the FBX holds them (float32)."""
    tr = d["trace"]
    Y = d["year"]
    cols = {k: [] for k in ("fi", "piece", "kind", "walked", "edge", "P", "B", "D", "lifted", "floor", "foot", "q",
                            "damp", "mtr", "Lc", "Mc", "reach_code", "top", "worn", "S", "polish", "lichen", "moss",
                            "held", "water", "years", "var", "sky", "ground", "back", "joint", "hr")}
    pieces = []
    for pi, t in enumerate(tr):
        n, kind = t["n"], t["kind"].astype(int)
        P = Y - t["worn_y"]
        B, D = Y - t["bare_y"], Y - t["bed_y"]
        L = None if t["lifted_y"] is None else Y - t["lifted_y"]
        lifted = L is not None and L > B
        walked = t["foot_on"]
        q = (1.0 - np.clip(t["ltr"], 0, 1)) ** 1.5 * (0.35 + 0.65 * np.clip(t["exposed"], 0, 1))
        q = np.where(kind == 6, 0.0, q)
        reach = t["back"] | t["joint"] | (kind == 4) | (kind == 6) | (not walked)
        rate_m = t["wear"] * (t["footfall"] / 1e5) * float(np.clip(3.2 / max(t["W"], 0.8), 0.6, 2.5)) / 100.0 / 1000.0
        S = np.where(kind == 0, np.clip(np.maximum(np.where(t["back"], (t["along"] - 0.8) / 0.2, 0.0),
                                                   np.where(t["joint"], 0.8, 0.0)), 0.12, 1.0), t["water"])
        pieces.append(dict(fi=t["fi"], key=t["key"][1], n=n, kind=kind, P=P, B=B, D=D, L=L, lifted=lifted,
                           walked=walked, floor=t["polish0"], var=t["var"], care=t["care_now"],
                           footfall=t["footfall"], rate_m=rate_m))
        for k, v in (("fi", np.full(n, t["fi"])), ("piece", np.full(n, pi)), ("kind", kind),
                     ("walked", np.full(n, walked)), ("edge", t["edge"]), ("P", np.full(n, float(P))),
                     ("B", np.full(n, float(B))), ("D", np.full(n, float(D))), ("lifted", np.full(n, lifted)),
                     ("floor", np.full(n, t["polish0"])), ("foot", t["foot"]), ("q", q), ("damp", t["damp_pre"]),
                     ("mtr", t["mtr"]), ("Lc", Y - t["lich_y"]), ("Mc", Y - t["moss_y"]), ("reach_code", reach),
                     ("top", t["top"]), ("worn", t["worn"]), ("S", S), ("polish", t["polish"]),
                     ("lichen", t["lichen"]), ("moss", t["moss"]), ("held", np.clip(t["held"], 0, 1)),
                     ("water", np.clip(t["water"], 0, 1)), ("years", np.full(n, t["bare_y"] / 200.0)),
                     ("var", np.full(n, t["var"])), ("sky", t["sky"]), ("ground", t["ground"]), ("back", t["back"]),
                     ("joint", t["joint"]), ("hr", np.full(n, rate_m))):
            cols[k].append(np.asarray(v))
    V = {k: np.concatenate(v) for k, v in cols.items()}
    for k in ("polish", "lichen", "moss", "held", "water", "years", "var", "sky", "ground"):
        V[k + "32"] = V[k].astype(np.float32).astype(np.float64)     # as the FBX carries it
    V["year"], V["care"] = Y, tr[0]["care_now"]
    return V, pieces


def inputs(V, care=None, enc=False):
    """The page model's inputs from the traced fields: per texel the polish amplitude, the lichen rate (as a share of
    the material's top rate, 1/200 a year), the moss amplitude (at the keeper's care), the bed reach and the static
    water; per vertex the dish's share; 8-bit where enc."""
    care = V["care"] if care is None else care
    kind = V["kind"]
    walked = V["walked"]
    mask_p = walked & ((kind <= 1) | (kind == 5))
    I = dict(AP=np.where(mask_p, V["foot"], 0.0), q=V["q"],
             AM=np.clip(V["damp"] * _care_f(care), 0.0, 1.0) * (1.0 - 0.85 * np.clip(V["mtr"], 0.0, 1.0)),
             reach=V["reach_code"].astype(float), S=V["S"])
    if enc:
        for k in ("AP", "q", "AM", "reach", "S"):
            I[k] = _q8(I[k])
    return I


def clocks(V):
    """Each layer's clock per vertex, from the piece's clocks and the reaches (fit.md, the resets)."""
    kind, B, D, P = V["kind"], V["B"], V["D"], V["P"]
    hands = V["lifted"] & (((kind == 0) & (V["edge"] < EDGE_HANDS)) | (kind == 1) | (kind == 2))
    return dict(polish=P, lichen=np.where(hands, D, B), hands=hands, bare=B, D=D)


def model(V, I, t, k_polish, floor=None):
    """The layers at date t."""
    C = clocks(V)
    kind = V["kind"]
    floor = V["floor"] if floor is None else floor
    age_p = np.clip(t - C["polish"], 0.0, None)
    polish = np.maximum(I["AP"] * (1.0 - np.exp(-k_polish * np.minimum(age_p, POLISH_CAP))),
                        np.where(V["walked"] & (kind <= 1), floor, 0.0))
    age_l = np.clip(t - C["lichen"] - LICHEN_DELAY, 0.0, None)
    lichen = np.where(kind == 6, 0.0, np.clip(age_l * I["q"] / LICHEN_FULL, 0.0, 1.0))
    mclock = C["bare"] + I["reach"] * np.clip(C["D"] - C["bare"], 0.0, None)
    moss = np.clip(I["AM"] * np.minimum(np.clip(t - mclock, 0.0, None) / MOSS_FULL, 1.0), 0.0, 1.0)
    # the dish's depth (m): the thing's wear rate (facts) times the polish amplitude (the foot's share) on a walked
    # tread, from its worn clock; off the walking line nothing wears
    dish = V["hr"] * np.where((kind == 0) & V["walked"], I["AP"], 0.0) * np.clip(t - V["P"], 0.0, None)
    held = np.clip((dish - HELD_FROM) / HELD_SPAN, 0.0, 1.0) * V["top"]
    water = np.where(kind == 0, np.maximum(I["S"], np.minimum(dish / WATER_DISH, 1.0)), I["S"])
    return dict(polish=polish, lichen=lichen, moss=moss, held=held, water=np.clip(water, 0, 1),
                years=np.clip(t - C["bare"], 0, None) / 200.0)


def rate_only(V, I89, t, k_polish):
    """D5.1 as written: each layer its curve at rate x age, no amplitude; the rate fitted per vertex so that 1989 is
    met (the clocks given exactly, so only the law is tested): polish 1 - exp(-u), lichen clip(u) after its delay,
    moss min(u, 1)."""
    m89 = model(V, I89, TODAY, k_polish)
    C = clocks(V)
    a89 = np.clip(TODAY - C["polish"], 1e-9, None)
    r_p = -np.log(np.clip(1.0 - m89["polish"], 1e-12, 1.0)) / a89
    mclock = C["bare"] + I89["reach"] * np.clip(C["D"] - C["bare"], 0.0, None)
    am89 = np.clip(TODAY - mclock, 1e-9, None)
    r_m = m89["moss"] / am89
    out = model(V, I89, t, k_polish)
    out["polish"] = 1.0 - np.exp(-r_p * np.clip(t - C["polish"], 0.0, None))
    out["moss"] = np.minimum(r_m * np.clip(t - mclock, 0.0, None), 1.0)
    return out


def _err(a, b, sel=None):
    e = np.abs(np.asarray(a, float) - np.asarray(b, float))
    if sel is not None:
        e = e[sel]
    if e.size == 0:
        return (0.0, 0.0)
    return float(e.max()), float(np.percentile(e, 99.9))


def _f(x):
    """An error in 255ths."""
    return f"{x * 255:.2f}"


def _slot_step(pid):
    import re
    m = re.match(r"(.*?/tr-\d+)(/sl-\d+)?", pid)
    if not m:
        return None, None
    return (m.group(1) + m.group(2)) if m.group(2) else None, m.group(1)


def _touch(log):
    """Each event's slot (slabs) or step, with its year."""
    out = []
    for ev in log:
        kind, ident, year = ev[0], ev[1], ev[2]
        if kind in ("campaign", "renew"):
            out.append(("step", ident, year, ev))
        else:
            out.append(("slot", ident.rsplit("/", 1)[0], year, ev))
    return out


def unchanged(V89, P89, d89, dY):
    """The pieces of the 1989 build that stand unchanged since year Y (same piece, same clocks, no event on their
    slot or step from Y on, and the year's own life agreeing with 1989's before Y), and the matching vertex indices in
    the two builds."""
    Y = dY["year"]
    VY, PY = assemble(dY)
    idx_y = {(p["fi"], p["key"]): i for i, p in enumerate(PY)}
    start89 = np.concatenate([[0], np.cumsum([p["n"] for p in P89])])
    startY = np.concatenate([[0], np.cumsum([p["n"] for p in PY])])
    late, differ = set(), set()
    t89 = _touch(d89["log"])
    tY = _touch(dY["log"])
    for scope, ident, year, ev in t89:
        if year >= Y:
            late.add((scope, ident))
    cut = set(ev for _, _, year, ev in t89 if year < Y)
    own = set(ev for _, _, _, ev in tY)
    for scope, ident, year, ev in t89 + tY:
        if (ev in cut) != (ev in own):
            differ.add((scope, ident))
    keep89, keepY, why = [], [], dict(missing=0, clocks=0, events=0, prefix=0, kept=0)
    for i, p in enumerate(P89):
        j = idx_y.get((p["fi"], p["key"]))
        if j is None or PY[j]["n"] != p["n"] or not np.array_equal(PY[j]["kind"], p["kind"]):
            why["missing"] += 1
            continue
        q = PY[j]
        same = (q["B"], q["D"], q["L"], q["floor"]) == (p["B"], p["D"], p["L"], p["floor"]) and \
            (q["P"] == p["P"] or not ((p["kind"] == 0).any() or ((p["kind"] <= 1) | (p["kind"] == 5)).any()) or
             not p["walked"] and not (p["kind"] == 0).any())
        slot, step = _slot_step(p["key"])
        tags = {("step", step)} | ({("slot", slot)} if slot else set())
        if tags & differ:
            why["prefix"] += 1
            continue
        if tags & late:
            why["events"] += 1
            continue
        if not same:
            why["clocks"] += 1
            continue
        why["kept"] += 1
        keep89.append(np.arange(start89[i], start89[i + 1]))
        keepY.append(np.arange(startY[j], startY[j + 1]))
    return VY, PY, np.concatenate(keep89), np.concatenate(keepY), why


def prefix(d89):
    """Life at each cut against life at 1989 cut there: events (kind, slot or fill, year, details) before the cut."""
    calls = d89["calls"]
    rows = []
    for c in CUTS:
        mism, kinds, in_last, total = 0, {}, 0, 0
        for fl, (a, kw) in enumerate(calls):
            built = a[1]
            y0 = built + 10 * ((c - built) // 10)
            full = [ev for ev in d89["flight_logs"][fl] if ev[2] < c]
            own = d89["cuts"][c][fl]
            sa, sb = set(full), set(own)
            total += len(sa)
            for ev in sa ^ sb:
                mism += 1
                kinds[ev[0]] = kinds.get(ev[0], 0) + 1
                in_last += int(y0 <= ev[2] < y0 + 10)
        rows.append(dict(cut=c, events=total, mismatches=mism, kinds=kinds, in_last=in_last,
                         last=(built + 10 * ((c - built) // 10), c)))
    return rows


def flight_whole(UP, HS, steps, built, now, upkeep, works, seed, slots, wet=None, busy=None, cracks=1.0, whole=True):
    """upkeep.flight (the frozen code's, line for line) with the fix proposed in fit.md (d) when whole: every decade
    drawn whole (its span ten years, its draws' years over all ten, the settling its probabilities read taken to the
    decade's end) and the life kept only up to now (works before now; damage, fixes and shims from now on dropped;
    the last decade's settling taken back to now). whole=False is the frozen loop itself (the self-check). Returns the
    steps' state and the event log, in the instrumented copy's form."""
    log = []
    n = len(steps)
    wet = wet or [0.5] * n
    busy = busy or (lambda x: 0.5)
    rate = [0.0001 * (0.5 + wet[i]) * math.exp(HS.Stream(seed, slots["steps"][i], "settle").normal(0.0, 0.45))
            for i in range(n)]
    S = []
    for i in range(n):
        S.append(dict(reset=built, settled=0.0, mortar=None,
                      slabs=[dict(origin="laid", placed=built, lifted=built, bare=built, at=(xa, xb), width=xb - xa,
                                  cracked=None, corner=None, shim=None, slot=slots["slabs"][i][k], fill=0)
                             for k, (xa, xb) in enumerate(steps[i])]))
    last = None
    for decade in range(built, now, 10):
        y0, y1 = decade, (decade + 10 if whole else min(decade + 10, now))
        last = (y0, y1)
        span = (y1 - y0) / 10.0
        for i, st in enumerate(S):
            st["settled"] += rate[i] * (y1 - y0)
            for sl in st["slabs"]:
                if sl["cracked"] is None and sl["width"] > 0.8:
                    r = HS.Stream(seed, UP._fill(sl), "crack", y0)
                    if r.random() < span * 0.025 * cracks * (1.0 + st["settled"] / 0.01):
                        sl["cracked"] = dict(year=r.randint(y0, y1 - 1), at=r.uniform(0.35, 0.65), filled=None)
                        log.append(("crack", UP._fill(sl), sl["cracked"]["year"], round(sl["cracked"]["at"], 12)))
                bl, br = busy(sl["at"][0]), busy(sl["at"][1])
                r = HS.Stream(seed, UP._fill(sl), "corner", y0)
                if sl["corner"] is None and r.random() < span * 0.03 * max(bl, br):
                    sl["corner"] = dict(year=r.randint(y0, y1 - 1), side="l" if r.random() * (bl + br) < bl else "r",
                                        size=r.uniform(0.04, 0.09), filled=None)
                    log.append(("corner", UP._fill(sl), sl["corner"]["year"], sl["corner"]["side"],
                                round(sl["corner"]["size"], 12)))
        keep = UP.keeper_in(upkeep, y0)
        k = UP._poisson(HS.Stream(seed, slots["flight"], "quick", y0),
                        UP.QUICK[keep["by"]](y0) * span * (n / 30.0) * keep["care"] / 0.4)
        todo = []
        for i, st in enumerate(S):
            for sl in st["slabs"]:
                c, kc = sl["cracked"], sl["corner"]
                if kc and kc["filled"] is None and kc["year"] < y1:
                    todo.append((3.0 * max(busy(sl["at"][0]), busy(sl["at"][1]))
                                 + UP._u(seed, UP._fill(sl), "fix", "corner", y0), "corner", sl))
                if c and c["filled"] is None and c["year"] < y1:
                    todo.append((1.0 + UP._u(seed, UP._fill(sl), "fix", "crack", y0), "crack", sl))
                if sl["shim"] is None and st["settled"] > 0.012:
                    todo.append((0.8 + UP._u(seed, UP._fill(sl), "fix", "rock", y0), "rock", sl))
        for _, what, sl in sorted(todo, key=lambda t: -t[0])[:k]:
            year = HS.between(HS.h(seed, UP._fill(sl), "fix", what, y0, "year"), y0, y1 - 1)
            if what == "rock":
                sl["shim"] = year
                log.append(("shim", UP._fill(sl), year))
            elif y0 >= UP.CEMENT_FROM:
                d = sl["corner"] if what == "corner" else sl["cracked"]
                d["filled"] = ("cement", max(d["year"] + 1, year))
                log.append(("fix-" + what, UP._fill(sl), d["filled"][1]))
        upto = min(y1, now)
        for w in works:
            if w["kind"] == "renewed" and y0 <= w["year"] < upto:
                lo_, hi_ = w.get("steps", (0, n))
                for i in range(lo_, min(hi_, n)):
                    S[i].update(reset=w["year"], settled=0.0, mortar=(w["mortar"], w["year"]) if w.get("mortar") else None)
                    log.append(("renew", slots["steps"][i], w["year"]))
                    for sl in S[i]["slabs"]:
                        sl.update(origin=w.get("material", "laid"), placed=w["year"], lifted=w["year"],
                                  bare=w["year"], cracked=None, corner=None, shim=None, fill=sl["fill"] + 1)
        for w in works:
            if w["kind"] == "campaign" and y0 <= w["year"] < upto:
                m = n if w["share"] > 0.5 else max(1, round(w["share"] * n))
                lo_ = max(range(n - m + 1), key=lambda j: sum(S[i]["settled"] * (0.5 + wet[i]) for i in range(j, j + m)))
                for i in range(lo_, lo_ + m):
                    st = S[i]
                    st["reset"], st["settled"] = w["year"], 0.0
                    st["mortar"] = (w.get("mortar") or UP.mortar_of(w["year"]), w["year"])
                    log.append(("campaign", slots["steps"][i], w["year"], st["mortar"][0]))
                    for sl in st["slabs"]:
                        sl["shim"] = None
                        sl["lifted"] = w["year"]
                        log.append(("lift", UP._fill(sl), w["year"]))
                        c = sl["cracked"]
                        if c and c["year"] >= w["year"]:
                            continue
                        r = HS.Stream(seed, UP._fill(sl), "campaign", w["year"])
                        if c and c["filled"] is None and w["year"] - c["year"] > 15 and w.get("stock") == "reclaimed" \
                                and r.random() < 0.35:
                            sl.update(origin="reclaimed", placed=w["year"], bare=w["year"] - r.randint(15, 40),
                                      cracked=None, corner=None, fill=sl["fill"] + 1)
                            log.append(("reclaim", UP._fill(sl), w["year"], sl["bare"]))
                        elif c and c["filled"] is None:
                            c["filled"] = (st["mortar"][0], w["year"])
                            log.append(("campaign-fill", UP._fill(sl), w["year"], st["mortar"][0]))
    if whole and last is not None:
        y0, y1 = last
        for i, st in enumerate(S):
            if st["reset"] < y0:
                st["settled"] -= rate[i] * (y1 - now)
            for sl in st["slabs"]:
                for kk in ("cracked", "corner"):
                    d = sl[kk]
                    if d and d["year"] >= now:
                        sl[kk] = None
                    elif d and d["filled"] and d["filled"][1] >= now:
                        d["filled"] = None
                if sl["shim"] is not None and sl["shim"] >= now:
                    sl["shim"] = None
        log = [ev for ev in log if ev[2] < now]
    return S, log


def _live_calls(ST, UP):
    """The flights' upkeep calls of one 1989 lay, with their own arguments (busy is a closure: not in the pickles)."""
    calls, real = [], UP.flight

    def grab(*a, **k):
        calls.append((a, k))
        return real(*a, **k)
    UP.flight = grab
    ST.YEAR, ST.TRACE, UP.LOG = TODAY, None, None
    try:
        ST.lay(ST.FLIGHTS["gully"], 1)
    finally:
        UP.flight = real
    return calls, real


def _sym(a, b):
    return len(set(a) ^ set(b))


def _state(S):
    """A life's state for comparison: settling to the nanometre (whole decades take it back in floating point)."""
    return repr([dict(st, settled=round(st["settled"], 9)) for st in S])


def prefix_fix(ST, UP, HS):
    """The fix, checked: the reimplementation without it against the frozen code (0 expected), with it the prefix at
    each cut (0 expected), and what it moves in today's 1989."""
    calls, real = _live_calls(ST, UP)
    rows = dict(self=0, self_states=0, prefix={}, forward=0, today=0, today_years=set(), today_states=0)

    def run(a, kw, now, whole):
        args = list(a)
        args[2] = now
        return flight_whole(UP, HS, *args, whole=whole, **kw)

    def frozen_run(a, kw, now):
        args = list(a)
        args[2] = now
        UP.LOG = []
        S = real(*args, **kw)
        lg, UP.LOG = list(UP.LOG), None
        return S, lg
    for a, kw in calls:
        for now in (TODAY,) + CUTS:
            S0, l0 = frozen_run(a, kw, now)
            S1, l1 = run(a, kw, now, False)
            rows["self"] += _sym(l0, l1)
            rows["self_states"] += int(_state(S0) != _state(S1))
        Sw, lw = run(a, kw, TODAY, True)
        for c in CUTS:
            _, lc = run(a, kw, c, True)
            rows["prefix"][c] = rows["prefix"].get(c, 0) + _sym([ev for ev in lw if ev[2] < c], lc)
        _, lf = run(a, kw, TODAY + 20, True)
        rows["forward"] += _sym([ev for ev in lf if ev[2] < TODAY], lw)
        S0, l0 = frozen_run(a, kw, TODAY)
        d = set(l0) ^ set(lw)
        rows["today"] += len(d)
        rows["today_years"] |= set(ev[2] for ev in d)
        rows["today_states"] += sum(int(_state([x]) != _state([y])) for x, y in zip(S0, Sw))
        rows["steps"] = rows.get("steps", 0) + len(S0)
    return rows


def fit(frozen, cache, out_md=None):
    ST, UP, HS = _import(frozen)
    with open(os.path.join(cache, f"trace-{TODAY}.pkl"), "rb") as fh:
        d89 = pickle.load(fh)
    V, P = assemble(d89)
    k = d89["trace"][0]["footfall"] / 4e5
    L = []
    nv = len(V["kind"])
    L.append(f"Stair: {nv:,} vertices in {len(P)} pieces (both flights). Clocks: placed, bare, disturbed (bed and "
             f"lifted) per piece; polish speed {k:.3f} a year (footfall {d89['trace'][0]['footfall']:,} / 400,000); "
             f"the keeper's care in 1988 {V['care']}.")

    # (a) the homes reproduce today's values exactly, and how much each 8-bit home costs
    C = clocks(V)
    lich_ok = int((C["lichen"] == V["Lc"]).sum())
    mclock = C["bare"] + V["reach_code"] * np.clip(C["D"] - C["bare"], 0, None)
    moss_ok = int((mclock == V["Mc"]).sum())
    lifted_eq = all(p["L"] is None or p["L"] == p["D"] for p in P)
    L.append("")
    L.append("**(a) The resets, checked.** Lichen's clock from the piece's bare and disturbed years by the hands' reach "
             f"(face kind and edge distance): {lich_ok:,} of {nv:,} vertices exact. Moss's from the bed reach: "
             f"{moss_ok:,} of {nv:,} exact. Lifted equals disturbed on every lifted piece: {'yes' if lifted_eq else 'no'}. "
             f"Vertices whose lichen runs from the lift: {int(C['hands'].sum()):,}; whose moss runs from the bed's "
             f"relaying (reach 1, disturbed after bare): {int(((V['reach_code']) & (V['D'] > V['B'])).sum()):,}. "
             f"Reclaimed slabs in the gully: {sum(1 for p in P if p['B'] < p['P'] and p['walked'] and (p['kind'] == 0).any())}.")

    I = inputs(V)
    I8 = inputs(V, enc=True)
    m = model(V, I, TODAY, k)
    m8 = model(V, I8, TODAY, k)
    L.append("")
    L.append("**(b) The page model at 1989 against today's per-vertex values** (every vertex; errors in 255ths; "
             "today as the FBX carries it, float32):")
    L.append("")
    L.append("| Layer (channel today) | float inputs: max | 99.9th | 8-bit inputs: max | 99.9th | target float / 8-bit |")
    L.append("| --- | --- | --- | --- | --- | --- |")
    for name, ch in (("polish", "UV4.x"), ("lichen", "UV4.y"), ("moss", "UV5.x"), ("held", "UV5.y"),
                     ("water", "UV2.y"), ("years", "UV1.x")):
        a, b = _err(m[name], V[name + "32"]), _err(m8[name], V[name + "32"])
        tgt = "1 / 2" if name in ("polish", "lichen", "moss") else "(not targeted)"
        L.append(f"| {name} ({ch}) | {_f(a[0])} | {_f(a[1])} | {_f(b[0])} | {_f(b[1])} | {tgt} |")
    var16 = np.round(V["var"] * 65535) / 65535
    L.append("")
    L.append(f"Variation (UV1.y) in 16 bits: max error {np.abs(var16 - V['var32']).max():.2e} (half precision, as the "
             f"shader reads it, rounds at 2.4e-4 to 4.9e-4); in 8 bits {np.abs(_q8(V['var']) - V['var32']).max():.2e}. "
             f"Sky and ground seen (UV3) in 8 bits: max {_f(_err(_q8(V['sky']), V['sky32'])[0])} and "
             f"{_f(_err(_q8(V['ground']), V['ground32'])[0])}.")

    # (c) the earlier builds
    L.append("")
    L.append("**(c) Against the frozen code built at an earlier year,** on the pieces unchanged since (no event on their "
             "slot or step from that year on, the same clocks, and the year's own life agreeing with 1989's before it). "
             "Errors in 255ths, max / 99.9th, polish, lichen, moss:")
    L.append("")
    L.append("| Build (care) | pieces kept (vertices) | the law, the build's own fields | 1989's page at that date, float | "
             "same, 8-bit | moss with 1989's care, float | D5.1 rate only, polish and moss |")
    L.append("| --- | --- | --- | --- | --- | --- | --- |")
    builds, drift_rows, causes = {}, [], []
    for Y in YEARS:
        with open(os.path.join(cache, f"trace-{Y}.pkl"), "rb") as fh:
            dY = pickle.load(fh)
        VY, PY, s89, sY, why = unchanged(V, P, d89, dY)
        builds[Y] = (VY, PY, dY, s89, sY)
        own = model(VY, inputs(VY), Y, k)
        j89 = model(V, I, Y, k)
        Ic = inputs(V, care=VY["care"])
        jc = model(V, Ic, Y, k)
        jc8 = model(V, inputs(V, care=VY["care"], enc=True), Y, k)
        ro = rate_only(V, Ic, Y, k)
        e = lambda a_, nm: _err(a_[nm][s89], VY[nm + "32"][sY])
        pm = lambda a_, names: ", ".join(f"{_f(e(a_, nm)[0])} / {_f(e(a_, nm)[1])}" for nm in names)
        lw = ", ".join(_f(_err(own[nm][sY], VY[nm + "32"][sY])[0]) for nm in ("polish", "lichen", "moss"))
        L.append(f"| {Y} ({VY['care']}) | {why['kept']} of {len(P)} ({len(s89):,}) | {lw} | "
                 f"{pm(jc, ('polish', 'lichen', 'moss'))} | {pm(jc8, ('polish', 'lichen', 'moss'))} | "
                 f"{pm(j89, ('moss',))} | {pm(ro, ('polish', 'moss'))} |")
        IYc = inputs(VY, care=V["care"])
        drift_rows.append((Y, _err(IYc["AP"][sY], I["AP"][s89])[0], _err(IYc["q"][sY], I["q"][s89])[0],
                           _err(IYc["AM"][sY], I["AM"][s89])[0],
                           int((VY["reach_code"][sY] != V["reach_code"][s89]).sum()), why))
        # where 1989's page misses by more than 2/255: a mask crossed (the back strip, a joint, the bed reach), the
        # foot band of a front (its damp from its height over the step below), or elsewhere (the walking line's
        # gradients under a settled piece)
        bad = (np.abs(jc["moss"][s89] - VY["moss32"][sY]) > 2 / 255) | \
              (np.abs(jc["polish"][s89] - VY["polish32"][sY]) > 2 / 255) | \
              (np.abs(jc["lichen"][s89] - VY["lichen32"][sY]) > 2 / 255)
        flip = (VY["back"][sY] != V["back"][s89]) | (VY["joint"][sY] != V["joint"][s89]) | \
               (VY["reach_code"][sY] != V["reach_code"][s89])
        band = (V["kind"][s89] == 2) & ~flip
        rest = ~flip & ~band
        er = lambda nm, sel: _err(jc[nm][s89][sel], VY[nm + "32"][sY][sel])
        causes.append((Y, int(bad.sum()), len(s89), int((bad & flip).sum()), int((bad & band).sum()),
                       int((bad & rest).sum()), er("moss", band),
                       ", ".join(f"{_f(er(nm, rest)[0])} / {_f(er(nm, rest)[1])}" for nm in ("polish", "lichen", "moss")),
                       ", ".join(f"{_f(_err(ro[nm][s89][rest], VY[nm + '32'][sY][rest])[0])} / "
                                 f"{_f(_err(ro[nm][s89][rest], VY[nm + '32'][sY][rest])[1])}" for nm in ("polish", "moss"))))
    L.append("")
    L.append("Where 1989's page misses an earlier build by more than 2/255 (any of the three layers), by cause:")
    L.append("")
    L.append("| Build | vertices over 2/255 (of kept) | a mask crossed (back, joint, bed reach) | a front's foot band "
             "(its moss error, max / 99.9th) | elsewhere | the rest (no mask crossed, no band), the amplitude law: "
             "polish, lichen, moss | the rest, D5.1 rate only: polish, moss | the inputs' largest drift: polish "
             "amplitude, lichen rate, moss amplitude |")
    L.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for (Y, nb, nk, nf, nband, nel, eb, er_, ro_), (_, da, dq, dm, _, _) in zip(causes, drift_rows):
        L.append(f"| {Y} | {nb:,} of {nk:,} ({100 * nb / nk:.1f}%) | {nf:,} | {nband:,} ({_f(eb[0])} / {_f(eb[1])}) | "
                 f"{nel:,} | {er_} | {ro_} | {_f(da)}, {_f(dq)}, {_f(dm)} |")
    L.append("")
    L.append("Pieces left out of each comparison (events on them from that year on; their slot's life differing in the "
             "build's own last decade; clocks; not in that build): " +
             "; ".join(f"{Y}: {w['events']}, {w['prefix']}, {w['clocks']}, {w['missing']}" for Y, *_, w in drift_rows) +
             ".")

    # forward: D5.1's rate-only law run on from 1989, against the old law on today's fields
    fwd = TODAY + 60
    mf = model(V, I, fwd, k)
    rf = rate_only(V, I, fwd, k)
    L.append("")
    L.append(f"D5.1's rate-only law run forward to {fwd} (rates fitted to 1989 exactly), against the same code's law "
             f"on today's fields: polish {_f(_err(rf['polish'], mf['polish'])[0])} / "
             f"{_f(_err(rf['polish'], mf['polish'])[1])}, moss {_f(_err(rf['moss'], mf['moss'])[0])} / "
             f"{_f(_err(rf['moss'], mf['moss'])[1])}; lichen is the same law in both (its curve is linear until full).")

    # the old code's own jumps at the care change of 1965 (1964 and 1966 built), and what 1946 asks of the law
    VA, _, _, sa89, sa = builds[1964]
    VB, _, _, sb89, sb = builds[1966]
    both = np.intersect1d(sa89, sb89)
    ia = sa[np.searchsorted(sa89, both)]
    ib = sb[np.searchsorted(sb89, both)]
    L.append("")
    L.append(f"The old code's own jumps (listed, not failed). 1964 to 1966 builds, care 0.45 to 0.25 from 1965, on the "
             f"{len(both):,} vertices unchanged since 1964: two years' growth, the care change and the settling it "
             f"scales (255ths, max and mean):")
    L.append("")
    for n in ("polish", "lichen", "moss"):
        dd = np.abs(VB[n + "32"][ib] - VA[n + "32"][ia])
        L.append(f"- {n}: {_f(dd.max())}, {_f(dd.mean())}")
    sel = (V["Mc"] <= 1946 - MOSS_FULL)
    drop = (inputs(V, care=0.30)["AM"] - inputs(V, care=0.45)["AM"])[sel]
    L.append(f"- 1946, care 0.30 to 0.45: on the {int(sel.sum()):,} vertices whose moss was full by then, the moss "
             f"amplitude falls by up to {_f(drop.max())} (mean {_f(drop.mean())}). A rising curve from a reset cannot "
             f"fall, so the interval model must let moss decline there or jump (R6).")

    # care as an interval's amplitude (a per mille scale on the baked moss amplitude) instead of a rebake: the clip at
    # 1 inside the amplitude makes a scale wrong wherever the bake was full
    cs = []
    for c2 in (0.30, 0.45, 0.50):
        scaled = np.clip(inputs(V)["AM"] * _care_f(c2) / _care_f(V["care"]), 0, 1)
        ee = np.abs(scaled - inputs(V, care=c2)["AM"])
        cs.append(f"care {c2}: {_f(ee.max())} / {_f(np.percentile(ee, 99.9))}, over 1/255 on "
                  f"{int((ee > 1 / 255).sum()):,} vertices")
    L.append(f"- Care as a per-mille scale on 1989's moss amplitude (care {V['care']}) instead of a rebake, max / "
             f"99.9th: " + "; ".join(cs) + ".")

    # reclaimed slabs: the inherited polish and the age brought are in the code, never in the gully
    rec = []
    for Y in (TODAY,) + YEARS:
        dY = d89 if Y == TODAY else builds[Y][2]
        rec.append(f"{Y} {sum(1 for t in dY['trace'] if t['polish0'] > 0)} and "
                   f"{sum(1 for ev in dY['log'] if ev[0] == 'reclaim')}")
    L.append("")
    L.append("Reclaimed slabs (inherited polish 0.3, age brought 15 to 40 years), pieces with an inherited polish and "
             "reclaim events: " + ", ".join(rec) + ".")

    # (d) prefix
    L.append("")
    L.append("**(d) Prefix: life at a cut against life at 1989 cut there** (events before the cut: kind, slot or fill, "
             "year, details):")
    L.append("")
    L.append("| Cut | events before it in 1989's life | mismatches | in the cut's own last decade | by kind |")
    L.append("| --- | --- | --- | --- | --- |")
    for r in prefix(d89):
        L.append(f"| {r['cut']} | {r['events']} | {r['mismatches']} | {r['in_last']} (decade {r['last'][0]} to "
                 f"{r['last'][0] + 9}) | " +
                 (", ".join(f"{kk} {vv}" for kk, vv in sorted(r["kinds"].items())) or "none") + " |")
    fx = prefix_fix(ST, UP, HS)
    L.append("")
    L.append(f"The fix (fit.md, (d)), run: the loop reimplemented without it matches the frozen code at 1989 and every "
             f"cut ({fx['self']} events and {fx['self_states']} lives differ). With it: the prefix at the cuts, "
             + ", ".join(f"{c} {fx['prefix'][c]}" for c in CUTS) +
             f" mismatches; 1989 against {TODAY + 20} cut at 1989, {fx['forward']}. What it moves in today's 1989: "
             f"{fx['today']} events (in {', '.join(str(y) for y in sorted(fx['today_years'])) or 'none'}), "
             f"{fx['today_states']} of {fx['steps']} steps' "
             f"lives; so the fix changes today's hash.")

    text = "\n".join(L)
    print(text)
    if out_md:
        if os.path.exists(out_md):
            with open(out_md) as fh:
                doc = fh.read()
        else:
            doc = f"# History as a function: the fit\n\n{MARK_A}\n{MARK_B}\n"
        a, b = doc.index(MARK_A), doc.index(MARK_B)
        doc = doc[:a + len(MARK_A)] + "\n" + text + "\n" + doc[b:]
        os.makedirs(os.path.dirname(os.path.abspath(out_md)), exist_ok=True)
        with open(out_md, "w") as fh:
            fh.write(doc)
        print("WROTE", out_md)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    cmd = argv[0]
    if cmd == "prepare":
        prepare(argv[1])
    elif cmd == "prove":
        prove(argv[1], argv[2])
    elif cmd == "collect":
        collect(argv[1], argv[2])
    elif cmd == "fit":
        fit(argv[1], argv[2], argv[3] if len(argv) > 3 else None)
    else:
        raise SystemExit(__doc__)
