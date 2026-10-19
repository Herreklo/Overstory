"""The resolver: a building's diary, read up to a year, becomes a plan.

The plan says what is there and where (volumes, facade cells and the part in each,
coats of paint, the business, condition) and why (every part names the event that
installed it). It does not depend on stylisation: how far shapes are pushed is a
view setting applied when the plan is built.

Lengths are millimetres. Each choice is seeded with hashing.h(world, building,
event, purpose, ...), so a new event re-picks only what it touches.
"""

import copy

from hashing import h, between, weighted, unit
from eras import ERAS, era_for

BAY = {"classical": 2000, "chalet": 2300, "jugend": 2300, "functionalist": 2600, "postwar": 2600, "seventies": 2600, "eighties": 2400}


def resolve(building, year, world_seed):
    """Plan for one building in one year, or None if it does not stand then."""
    events = sorted((e for e in building["events"] if e["year"] <= year), key=lambda e: (e["year"], e["id"]))
    if not events or events[0]["kind"] != "built":
        return None
    bid = building["id"]
    plan = None
    for ev in events:
        k = ev["kind"]
        if k == "built":
            plan = _built(building, ev, world_seed)
        elif k == "demolished":
            return None
        elif plan is None:
            continue
        elif k == "extended":
            _extended(plan, ev, world_seed, bid)
        elif k == "windows_replaced":
            _windows_replaced(plan, ev, world_seed, bid)
        elif k == "repainted":
            _repainted(plan, ev, world_seed, bid)
        elif k == "roof_retiled":
            plan["main"]["roof"]["swatch"] = ev["params"].get("swatch", "roof_slate")
            plan["main"]["roof"]["event"] = ev["id"]
        elif k == "shop_fitted":
            _shop_fitted(plan, ev, world_seed, bid)
        elif k == "business_opened":
            p = ev["params"]
            plan["business"] = dict(kind=p["kind"], name=p.get("name", ""), opened=ev["year"], era=era_for(ev["year"], h(world_seed, bid, ev["id"], "era")), event=ev["id"])
        elif k == "business_closed":
            if plan["business"]:
                plan["ghosts"].append(dict(plan["business"], closed=ev["year"]))
            plan["business"] = None
        elif k == "boarded":
            _set_boarded(plan, ev, True)
        elif k == "unboarded":
            _set_boarded(plan, ev, False)
        elif k == "neglected":
            plan["condition"] = max(0, plan["condition"] - ev["params"].get("amount", 200))
        elif k == "restored":
            plan["condition"] = min(1000, plan["condition"] + ev["params"].get("amount", 400))
            if ev["params"].get("windows") == "original":
                _windows_restored(plan, ev)
    plan["year"] = year
    plan["paint_age"] = year - plan["coats"][-1]["year"]
    return plan


# -- built ---------------------------------------------------------------------


def _built(b, ev, ws):
    bid, p = b["id"], ev["params"]
    key = lambda *parts: h(ws, bid, ev["id"], *parts)
    kind = b.get("type", "house")
    era = p.get("era") or era_for(ev["year"], key("era"))
    E = ERAS[era]
    wealth = p.get("wealth", 500)
    rich = lambda chance, purpose: (key(purpose) % 1000) < chance * (500 + wealth) // 1000

    W, D = b["plot"]["w"], b["plot"]["d"]
    if kind == "warehouse":
        W, D = D, W  # gable to the quay: the ridge runs back from the water
    storeys = p.get("storeys") or weighted(key("storeys"), E["storeys"])
    if kind == "warehouse":
        storeys = p.get("storeys", 2500)
    full = storeys // 1000
    knee = 1200 if storeys % 1000 else 0
    roof_type = p.get("roof") or weighted(key("roof"), E["roof"])
    if kind == "warehouse":
        roof_type = "gable"
    pitch = between(key("pitch"), *E["pitch"])
    roof = dict(type=roof_type, pitch=pitch, eave=E["eave"], gable=E["gable"], kick=(key("kick") % 1000) < E["kick"],
                swatch=weighted(key("roof_c"), E["roofs"]), event=ev["id"])
    if roof_type == "mansard":
        roof.update(lower_pitch=between(key("lpitch"), 650, 720), lower_run=between(key("lrun"), 800, 1100), pitch=between(key("upitch"), 220, 300))
        knee = 0
    if roof_type == "flat":
        roof.update(pitch=50, eave=E["eave"], kick=False)

    orn = {name: rich(chance, "orn_" + name) for name, chance in E["ornament"].items()}
    if kind == "warehouse":
        orn = {name: False for name in orn}
    main = dict(era=era, W=W, D=D, storeys=storeys, full=full, knee=knee, storey_h=E["storey"],
                H=full * E["storey"] + knee, plinth=between(key("plinth"), *E["plinth"]), roof=roof,
                cladding=E.get("cladding", "clapboard"), material=p.get("material", "timber"), ornament=orn,
                orient="gable" if kind == "warehouse" else "eaves", event=ev["id"], care=E["care"])

    walls = weighted(key("wall"), E["walls"])
    trim = weighted(key("trim"), E["trims"])
    if kind == "warehouse":
        walls = weighted(key("wall"), [("wall_oxred", 45), ("wall_white", 35), ("wall_ochre", 20)])
        trim = "trim_white"
    door = weighted(key("door"), E["doors"])
    plan = dict(id=bid, type=kind, seed=ws, main=main, additions=[], cells=[], chimneys=[],
                coats=[dict(year=ev["year"], wall=walls, trim=trim, door=door, event=ev["id"])],
                business=None, ghosts=[], condition=1000, built=ev["year"])

    if kind == "warehouse":
        _warehouse_cells(plan, ev, ws)
        return plan

    # additions that came with the house: named in the diary, or by the era's habits and the owner's wealth
    add = dict(E["additions"])
    for name in p.get("with", []):
        add[name] = 100000
    if storeys >= 1500 and W >= 7000 and roof_type == "gable" and rich(add["ark"], "ark"):
        plan["additions"].append(dict(kind="ark", era=era, event=ev["id"]))
    if storeys >= 1500 and rich(add["bislag"], "bislag"):
        plan["additions"].append(dict(kind="bislag", era=era, event=ev["id"]))
    if rich(add["veranda"], "veranda"):
        plan["additions"].append(dict(kind="veranda", era=era, event=ev["id"], side=1 if key("vside") % 2 else -1))
    if full >= 2 and rich(add["bay"], "bay"):
        plan["additions"].append(dict(kind="bay", era=era, event=ev["id"]))
    if roof_type in ("gable", "mansard") and (knee or roof_type == "mansard") and rich(add["dormer"], "dormer"):
        plan["additions"].append(dict(kind="dormers", era=era, event=ev["id"], count=2 if roof_type == "mansard" else 1 + key("dn") % 2))

    # chimneys at or near the ridge
    n = 2 if era == "classical" else (1 + (key("chim") % 2) if era in ("chalet", "jugend") else 1)
    for i in range(n):
        if n == 2 and E.get("symmetric", 0) > 500:
            x = (-1 if i == 0 else 1) * W * 22 // 100
        else:
            x = (between(key("chx", i), 0, 1000) - 500) * W // 2000
        plan["chimneys"].append(dict(x=x, y=0, era=era, event=ev["id"]))

    _house_cells(plan, ev, ws)
    return plan


def _cell(facade, a, w, b0, b1, ptype, style, era, event, **extra):
    c = dict(facade=facade, a=a, w=w, b0=b0, b1=b1, part=dict(type=ptype, style=style, era=era, event=event))
    c.update(extra)
    return c


def _house_cells(plan, ev, ws):
    m, bid = plan["main"], plan["id"]
    E = ERAS[m["era"]]
    key = lambda *parts: h(ws, bid, ev["id"], *parts)
    W, D, S = m["W"], m["D"], m["storey_h"]
    bay = BAY[m["era"]]
    nb = max(2, round(W / bay))
    symmetric = (key("sym") % 1000) < E["symmetric"]
    if symmetric and nb % 2 == 0:
        nb += 1 if W / (nb + 1) >= 1500 else -1
    nb = max(2, nb)
    cols = [-W // 2 + (2 * i + 1) * W // (2 * nb) for i in range(nb)]
    win = E["window"]
    ww, wh, sill = _window_size(win)
    m["cols"] = cols
    if symmetric and nb % 2 == 1:
        door_i = nb // 2
    else:
        door_i = pick_door(key("door_i"), nb)
    m["door_col"] = door_i
    cells = plan["cells"]
    for st in range(m["full"]):
        base = st * S
        for i, a in enumerate(cols):
            if st == 0 and i == door_i:
                cells.append(_cell("front", a, 1000, 0, 2200, "door", E["door"], m["era"], ev["id"], col=i, row=st))
                continue
            cells.append(_cell("front", a, ww, base + sill, base + sill + wh, "window", win, m["era"], ev["id"], col=i, row=st))
            if key("back", st, i) % 1000 < 800:
                cells.append(_cell("back", -a, ww, base + sill, base + sill + wh, "window", win, m["era"], ev["id"], col=i, row=st))
        ng = max(1, round(D / bay) - 1)
        for side in ("left", "right"):
            for k in range(ng):
                if key("gable", side, st, k) % 1000 < 750:
                    a = -D // 2 + (2 * k + 1) * D // (2 * ng)
                    cells.append(_cell(side, a, ww, base + sill, base + sill + wh, "window", win, m["era"], ev["id"], col=k, row=st))
    # loft windows in the gables
    if m["roof"]["type"] == "gable" and m["roof"]["pitch"] >= 300:
        for side in ("left", "right"):
            cells.append(_cell(side, 0, ww * 9 // 10, m["H"] + 450, m["H"] + 450 + wh * 8 // 10, "window", win, m["era"], ev["id"], col=99, row=99))
    for add in plan["additions"]:
        _layout_addition(plan, add, key, win, ww, wh, sill)


def _layout_addition(plan, add, key, win, ww, wh, sill):
    """Place an addition on the house and add its cells. Used at building and for later extensions."""
    m = plan["main"]
    E = ERAS[add["era"]]
    W, D, S = m["W"], m["D"], m["storey_h"]
    cols, door_i = m["cols"], m["door_col"]
    nb = len(cols)
    cells = plan["cells"]
    ev_id = add["event"]
    if True:
            if add["kind"] == "ark":
                add["x"] = cols[nb // 2] if nb % 2 else 0
                add["w"] = min(W * 45 // 100, max(2600, W * 13 // (10 * nb)))
                cells.append(_cell("front", add["x"], ww * 9 // 10, m["H"] + 300, m["H"] + 300 + wh * 8 // 10, "window", win, add["era"], ev_id, col=98, row=98))
            if add["kind"] == "bislag":
                add["x"] = cols[door_i]
                add["w"] = between(key("bw"), 1800, 2400)
                add["d"] = between(key("bd"), 1300, 1900)
                for c in cells:
                    if c["facade"] == "front" and c["part"]["type"] == "door":
                        c["part"]["type"] = "inner_door"
                cells.append(_cell("bislag", 0, 950, 0, 2200, "door", E["door"], add["era"], ev_id))
            if add["kind"] == "bay":
                choices = [i for i in range(nb) if i != door_i]
                i = choices[key("bay_i") % len(choices)]
                add["x"], add["w"], add["d"] = cols[i], min(2400, W // nb + 600), 650
                add["col"] = i
                # windows behind the bay are replaced by the bay's own
                plan["cells"] = cells = [c for c in cells if not (c["facade"] == "front" and c.get("col") == i and c.get("row", 0) >= 1)]
                for st in range(1, m["full"]):
                    base = st * S
                    cells.append(_cell("bay_front", 0, add["w"] - 700, base + sill, base + sill + wh, "window", win, add["era"], ev_id, row=st))
                    for side in ("bay_left", "bay_right"):
                        cells.append(_cell(side, 0, 380, base + sill, base + sill + wh, "window", win, add["era"], ev_id, row=st))
            if add["kind"] == "veranda":
                add["w"] = D - between(key("vw"), 800, 1600)
                add["d"] = between(key("vd"), 2000, 2600)
                add["y"] = -(D - add["w"]) // 2
                if m["full"] >= 2:
                    side = "left" if add["side"] < 0 else "right"
                    plan["cells"] = cells = [c for c in cells if not (c["facade"] == side and c.get("row") == 1)]
                    a = add["y"]
                    cells.append(_cell(side, a, 950, S, S + 2200, "door", E["door"], add["era"], ev_id, row=1))
            if add["kind"] == "dormers":
                taken = [plan_add["x"] for plan_add in plan["additions"] if plan_add["kind"] == "ark" and "x" in plan_add]
                xs = []
                if add["count"] == 1:
                    xs = [cols[(door_i + 1) % nb] if not taken else (W // 4 if taken[0] <= 0 else -W // 4)]
                else:
                    xs = [-W // 4, W // 4]
                add["xs"] = xs
                add["w"] = 1500




def pick_door(key, nb):
    if nb >= 3 and key % 1000 < 450:
        return 0 if (key >> 10) % 2 else nb - 1
    return nb // 2 if nb % 2 else (nb // 2 - (key >> 12) % 2)


def _window_size(style):
    """Nominal opening width, height and sill height, millimetres."""
    return {
        "small_panes": (850, 1300, 850),
        "cross_t": (900, 1550, 800),
        "cross_arch": (900, 1500, 850),
        "band": (1600, 1200, 900),
        "picture": (1800, 1300, 800),
        "casement": (1200, 1100, 950),
        "stick_bars": (1000, 1300, 850),
    }[style]


def _warehouse_cells(plan, ev, ws):
    """A quay warehouse: gable to the quay, strictly symmetric, loading doors up the middle."""
    m = plan["main"]
    D, S = m["D"], m["storey_h"]
    cells = plan["cells"]
    for st in range(m["full"]):
        base = st * S
        cells.append(_cell("front", 0, 1600, base, base + 2200, "loading_door", "plank", m["era"], ev["id"], row=st))
        for s in (-1, 1):
            cells.append(_cell("front", s * D * 30 // 100, 600, base + 1000, base + 1700, "window", "small_panes", m["era"], ev["id"], row=st))
    cells.append(_cell("front", 0, 1200, m["H"] + 300, m["H"] + 1700, "loading_door", "plank", m["era"], ev["id"], row=9))
    plan["additions"].append(dict(kind="hoist", era=m["era"], event=ev["id"]))


# -- later events ------------------------------------------------------------------


def _extended(plan, ev, ws, bid):
    p = ev["params"]
    era = era_for(ev["year"], h(ws, bid, ev["id"], "era"))
    add = dict(kind=p["kind"], era=era, event=ev["id"])
    add.update({k: v for k, v in p.items() if k != "kind"})
    m = plan["main"]
    if add["kind"] == "lean_to":
        add.setdefault("side", "back")
        add.setdefault("d", 2400)
        add.setdefault("w", m["W"] * 6 // 10)
    plan["additions"].append(add)
    if add["kind"] in ("ark", "bislag", "bay", "veranda", "dormers") and "cols" in m:
        if add["kind"] == "veranda":
            add.setdefault("side", 1 if h(ws, bid, ev["id"], "vside") % 2 else -1)
        if add["kind"] == "dormers":
            add.setdefault("count", 1)
        win = ERAS[era]["window"]
        ww, wh, sill = _window_size(win)
        key = lambda *parts: h(ws, bid, ev["id"], *parts)
        _layout_addition(plan, add, key, win, ww, wh, sill)


def _in_scope(cell, scope):
    if scope == "all":
        return True
    if scope == "upper":
        return cell.get("row", 0) >= 1
    if scope == "street":
        return cell["facade"] in ("front", "bay_front", "bay_left", "bay_right")
    if scope == "ground":
        return cell.get("row", 0) == 0 and cell["facade"] == "front"
    return cell["facade"] == scope


def _windows_replaced(plan, ev, ws, bid):
    era = era_for(ev["year"], h(ws, bid, ev["id"], "era"))
    style = ERAS[era]["window"]
    for c in plan["cells"]:
        if c["part"]["type"] == "window" and _in_scope(c, ev["params"].get("scope", "all")):
            if "original" not in c:
                c["original"] = copy.deepcopy(c["part"])
            c["part"] = dict(type="window", style=style, era=era, event=ev["id"])
            # careless eras fit a smaller standard window into the old opening
            if style in ("casement",) and ERAS[era]["care"] < 500:
                c["reduced"] = True


def _windows_restored(plan, ev):
    for c in plan["cells"]:
        if "original" in c:
            c["part"] = dict(c["original"], event=ev["id"], restored=True)
            c.pop("reduced", None)


def _repainted(plan, ev, ws, bid):
    era = era_for(ev["year"], h(ws, bid, ev["id"], "era"))
    E = ERAS[era]
    last = plan["coats"][-1]
    key = lambda purpose: h(ws, bid, ev["id"], purpose)
    plan["coats"].append(dict(year=ev["year"], event=ev["id"],
                              wall=ev["params"].get("wall") or weighted(key("wall"), E["walls"]),
                              trim=ev["params"].get("trim") or weighted(key("trim"), E["trims"]),
                              door=ev["params"].get("door") or last["door"]))


def _shop_fitted(plan, ev, ws, bid):
    era = era_for(ev["year"], h(ws, bid, ev["id"], "era"))
    m = plan["main"]
    cols, door_i = m.get("cols", []), m.get("door_col", 0)
    if len(cols) < 2:
        return
    want = ev["params"].get("cols", 2)
    candidates = [i for i in range(len(cols) - want + 1) if not (i <= door_i < i + want)]
    if not candidates:
        candidates = [0]
    start = candidates[h(ws, bid, ev["id"], "shop") % len(candidates)]
    span = list(range(start, start + want))
    plan["cells"] = [c for c in plan["cells"] if not (c["facade"] == "front" and c.get("row", 0) == 0 and c.get("col") in span and c["part"]["type"] == "window")]
    a0 = cols[span[0]] - m["W"] // (2 * len(cols)) + 300
    a1 = cols[span[-1]] + m["W"] // (2 * len(cols)) - 300
    plan["cells"].append(_cell("front", (a0 + a1) // 2, a1 - a0, 600, 2400, "shopfront", ERAS[era]["shopfront"], era, ev["id"], row=0, col=span[0], span=span))


def _set_boarded(plan, ev, value):
    scope = ev["params"].get("scope", "ground")
    for c in plan["cells"]:
        if c["part"]["type"] in ("window", "shopfront", "door") and _in_scope(c, scope):
            if value:
                c["boarded"] = ev["id"]
            else:
                c.pop("boarded", None)


def plan_signature(plan):
    """A canonical string of the plan, for hashing and comparing."""
    import json

    return json.dumps(plan, sort_keys=True, separators=(",", ":"))
