"""Tests for test 2a's sight script (tools/playable/sight.py): toy rays through a toy town, a window's opening, the
camera's numbers and the sun's clock, checked by hand before the script judges the corner. A plain script:

    python3 tools/tests/test_sight.py

Exit 0 when every test passes. Reads the layout, the diaries and the corner fixture; writes nothing.
"""
import datetime
import json
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "playable"))
import sight as S  # noqa: E402

RESULTS = []


def check(cond, what):
    if not cond:
        raise AssertionError(what)


def test(fn):
    try:
        fn()
        RESULTS.append((True, fn.__name__, ""))
    except Exception as e:  # report each test, keep going
        RESULTS.append((False, fn.__name__, "%s\n%s" % (e, traceback.format_exc())))
    return fn


def toy_layout(buildings=()):
    """Flat ground at z 0 on a 100 m square, no walls or details; the birch stays where it is (44.5, 28.0)."""
    n = 41
    return {"ground": {"x0": -50.0, "y0": -50.0, "step": 2.5, "nx": n, "ny": n, "z": [[0.0] * n for _ in range(n)]},
            "buildings": list(buildings), "walls": [], "details": []}


HOUSE = dict(name="toy house", ox=0.0, oy=-3.0, angle=0.0, w=4.0, d=6.0, base=0.0, eave=5.0, pitch=40.0, roof="gable")


@test
def a_house_between_blocks_and_a_clear_line_does_not():
    sc = S.Scene(toy_layout([HOUSE]))
    check(sc.blocker((-10.0, 0.0, 1.6), (10.0, 0.0, 1.6)) == "toy house", "through the house at head height")
    check(sc.blocker((-10.0, 10.0, 1.6), (10.0, 10.0, 1.6)) is None, "10 m north of it, clear")
    # over the gable: the ridge runs front to back at u = 2 (x 2), 5 + tan(40) * 2 = 6.68 m high
    check(sc.blocker((-10.0, 0.0, 7.0), (10.0, 0.0, 7.0)) is None, "over the ridge at 7 m")
    check(sc.blocker((-10.0, 0.0, 6.4), (10.0, 0.0, 6.4)) == "toy house", "through the roof at 6.4 m")


@test
def the_ground_blocks_a_line_that_runs_under_it():
    sc = S.Scene(toy_layout())
    check(sc.blocker((-10.0, -40.0, 1.0), (10.0, -40.0, -1.0)) == "the ground", "a line sinking 1 m below the ground")
    check(abs(sc.ground(3.3, -7.1)) < 1e-9, "flat ground reads 0")


@test
def the_birch_trunk_is_in_every_scene():
    sc = S.Scene(toy_layout())
    z = S.BIRCH["z"] + 1.6
    check(sc.blocker((40.0, 28.0, z), (49.0, 28.0, z)) == "the birch's trunk", "through the trunk")
    check(sc.blocker((40.0, 28.6, z), (49.0, 28.6, z)) is None, "0.6 m beside it, clear (bare crown)")
    hi = S.BIRCH["z"] + S.BIRCH["h"] * 0.6
    check(S.Scene(toy_layout(), crown=True).blocker((35.0, 30.0, hi), (54.0, 30.0, hi)) == "the birch's crown",
          "the opaque crown blocks at 60% of its height, 2 m off the trunk")


@test
def a_window_lets_through_only_what_its_opening_frames():
    # a window facing +y at the origin, 1 m wide, from 1 to 2.5 m; the eye 0.49 m behind the face at 1.6 m
    win = dict(n=(0.0, 1.0), u=(1.0, 0.0), c=(0.0, 0.0), hw=0.5, z0=1.0, z1=2.5)
    eye = (0.0, -S.GLASS_BACK - S.EYE_BACK, 1.6)
    check(S.through_opening(win, eye, (0.0, 20.0, 1.6)), "straight out")
    check(S.through_opening(win, eye, (5.0, 20.0, 1.6)), "14 degrees aside")
    check(not S.through_opening(win, eye, (20.0, 5.0, 1.6)), "76 degrees aside: the reveal hides it")
    check(not S.through_opening(win, eye, (0.0, -20.0, 1.6)), "behind the wall")
    check(not S.through_opening(win, eye, (0.0, 2.0, 8.0)), "too steep up for the head of the opening")


@test
def a_figures_height_in_pixels():
    # 1.75 m at 10 m with 37.8 degrees vertical over 1440 rows: 1440 * 0.175 / (2 tan 18.9) = 368.5
    check(abs(S.px_height(10.0, "Lens35") - 368.5) < 0.5, S.px_height(10.0, "Lens35"))
    check(abs(S.hfov("Lens35") - 62.5) < 0.2, S.hfov("Lens35"))


@test
def norways_clocks_and_the_sun():
    check(S.utc_offset(datetime.date(1989, 11, 15)) == 1 and S.utc_offset(datetime.date(1989, 9, 20)) == 2,
          "1989: summer time to the last Sunday of September (24 September)")
    check(S.utc_offset(datetime.date(1989, 9, 25)) == 1, "25 September 1989 is winter time")
    check(S.utc_offset(datetime.date(1998, 10, 16)) == 2 and S.utc_offset(datetime.date(1998, 10, 26)) == 1,
          "1998: to the last Sunday of October (25 October)")
    # Stavanger's sunset on 15 December is about 15:40 local; at midsummer about 23:00 (CEST)
    check(S.sunset(datetime.date(1989, 12, 15))[0] in ("15:38", "15:39", "15:40", "15:41", "15:42"),
          S.sunset(datetime.date(1989, 12, 15)))
    check(S.sunset(datetime.date(1989, 6, 21))[0][:2] in ("22", "23"), S.sunset(datetime.date(1989, 6, 21)))


@test
def as_window_sits_on_its_house():
    layout = json.loads(S.LAYOUT.read_text(encoding="utf-8"))
    wins, info = S.a_windows(layout)
    check(abs(info["W"] - 9.0) < 0.01 and abs(info["D"] - 9.0) < 0.01, "A's 1989 plan is 9 x 9 m: %r" % (info,))
    backs = [w for w in wins if w["facade"] == "back" and w["level"] == 1]
    check(len(backs) >= 3, "three or more back first-floor windows: %r" % [w["name"] for w in wins])
    cx, cy = info["centre"]
    for w in wins:
        d = ((w["c"][0] - cx) ** 2 + (w["c"][1] - cy) ** 2) ** 0.5
        check(4.4 <= d <= 6.5, "%s is on a face of the 9 m house (%.2f m from its centre)" % (w["name"], d))
        e = w["eyes"][1]
        back = ((w["c"][0] - e[0]) * w["n"][0] + (w["c"][1] - e[1]) * w["n"][1])
        check(abs(back - S.GLASS_BACK - S.EYE_BACK) < 1e-6, "the eye stands behind the glass")


def main():
    for ok, name, why in RESULTS:
        print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else ": " + why))
    n_bad = sum(1 for ok, _, _ in RESULTS if not ok)
    print("%d of %d passed (Python %s)" % (len(RESULTS) - n_bad, len(RESULTS), sys.version.split()[0]))
    return 1 if n_bad else 0


if __name__ == "__main__":
    sys.exit(main())
