"""Tests for the hash chain, the runner and diff_stage (schemas/hashing.md, schemas/stages.md). A plain script, for
both Pythons, each checking against the same golden files, so passing in both proves they agree:

    .venv/bin/python tools/tests/test_stages.py
    /Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13 tools/tests/test_stages.py

Exit 0 when every test passes. Caches and runs go to a temporary folder (TMPDIR), removed at the end.
"""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
for p in (TOOLS, os.path.join(TOOLS, "stages")):
    if p not in sys.path:
        sys.path.insert(0, p)
import diff_stage  # noqa: E402
import hashes as HX  # noqa: E402
import run_kind as RK  # noqa: E402
from hashes import Blob  # noqa: E402

try:
    import numpy as np
except ImportError:
    np = None

PROBE = os.path.join(HERE, "probe")
RECORD = os.path.join(PROBE, "st-probe.json")
GOLDEN = os.path.join(PROBE, "golden")
HOUSE = os.path.join(ROOT, "fixtures", "records", "bld-104.json")
HOUSE_GOLDEN = os.path.join(ROOT, "fixtures", "golden", "house")
TMP = tempfile.mkdtemp(prefix="test-stages-")
RESULTS = []


def quiet(*_):
    pass


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


def probe(cache, **kw):
    kw.setdefault("kinds_dir", os.path.join(PROBE, "kinds"))
    kw.setdefault("packs_dir", os.path.join(PROBE, "packs"))
    kw.setdefault("out", os.path.join(cache, "out"))
    return RK.run(kw.pop("record", RECORD), cache_dir=cache, say=quiet, **kw)


def ran(s):
    return [x["stage"] for x in s["stages"] if not x.get("skipped")]


def links(s):
    return dict((x["stage"], x.get("link")) for x in s["stages"])


def tmp(name):
    p = os.path.join(TMP, name)
    os.makedirs(p, exist_ok=True)
    return p


# ---------------------------------------------------------------- the encoding

@test
def vectors():
    check(HX.check(), "the canonical vectors differ (tools/hashes.py check)")


@test
def encoding_rules():
    h = HX.hash_hex
    check(h({"b": 1, "a": 2}) == h({"a": 2, "b": 1}), "key order counts")
    distinct = [h(1), h(1.0), h("1"), h(True), h(None), h([1]), h({"1": 1}), h(0), h(False), h(""), h([])]
    check(len(set(distinct)) == len(distinct), "values of different types collide")
    check(h(-0.0) == h(0.0), "minus zero is not zero")
    check(h((1, 2.5)) == h([1, 2.5]), "a tuple is not its list")
    check(h(2 ** 64) != h(0), "an int beyond 64 bits wraps")
    check(h(["a", "b"]) != h(["ab"]) and h(["a", ["b"]]) != h([["a"], "b"]), "the structure is ambiguous")
    for bad in (float("nan"), float("inf"), {1: 2}, {"a": {1}}, b"x"):
        try:
            h(bad)
        except HX.Refused:
            continue
        raise AssertionError("%r was not refused" % (bad,))
    sample = {"a": [0.1, -0.0, 1e-300, 5e-324, 2 ** 70, -5, 1.0, "xæ", None, True], "b": {"c": [[]], "d": {}}}
    back = json.loads(json.dumps(HX.plain(sample), sort_keys=True))
    check(h(back) == h(sample), "a value written as JSON and read back hashes differently")
    pieces = {"r/s/0#0": {"fill": "r/s/0", "chunk": "ch-0-0", "hash": "01", "vertices": 8},
              "r/s/0#1": {"fill": "r/s/0", "chunk": "ch-1-0", "hash": "02", "vertices": 4}}
    s = HX.summarise_pieces(pieces)
    check(s["fills"]["r/s/0"]["pieces"] == 2 and s["fills"]["r/s/0"]["vertices"] == 12, "per-fill sums")
    check(sorted(s["chunks"]) == ["ch-0-0", "ch-1-0"], "per-chunk summaries")
    check(HX.chunk_of(-1, 4000) == "ch-m1-1" and HX.chunk_of(3999, 0) == "ch-0-0", "chunk names")


@test
def blobs_and_npy():
    cases = [("float64", [[0.1, -0.0], [2.5, 1e300]]), ("float32", [0.1, 1.0, -0.0]), ("int64", [-1, 2 ** 63 - 1]),
             ("uint64", [2 ** 64 - 1, 0]), ("int32", [[7], [-7]]), ("uint8", [0, 255]), ("bool", [True, False]),
             ("float64", [])]
    for dtype, values in cases:
        b = Blob(values, dtype)
        summary = b.summary()
        check(HX.hash_value(b) == HX.hash_value(summary), "a blob hashes unlike its summary")
        path = os.path.join(tmp("npy"), "%s.npy" % dtype)
        RK.npy_write(path, b)
        back = Blob(RK.npy_read(path, dtype, use_numpy=False), dtype)
        check(back.hash == b.hash and back.shape == b.shape, "%s: the hand-read .npy differs" % dtype)
        if np is not None:
            arr = np.load(path)
            check(Blob(arr).hash == b.hash, "%s: numpy reads the hand-written .npy differently" % dtype)
            path2 = os.path.join(tmp("npy"), "%s-np.npy" % dtype)
            RK.npy_write(path2, Blob(arr))
            check(Blob(RK.npy_read(path2, dtype, use_numpy=False), dtype).hash == b.hash,
                  "%s: the hand reader reads numpy's .npy differently" % dtype)
    try:
        Blob([1.0, float("nan")], "float64").hash
        raise AssertionError("a blob with NaN was hashed")
    except HX.Refused:
        pass


@test
def numpy_is_its_values():
    if np is None:
        return
    h = HX.hash_hex
    check(h(np.float32(0.1)) == h(float(np.float32(0.1))), "a numpy float32 is not its Python value")
    check(h(np.int64(-5)) == h(-5) and h(np.bool_(True)) == h(True), "numpy ints and bools")
    check(h({"a": np.arange(3)}) == h({"a": [0, 1, 2]}), "a numpy array in a value is not its list")
    check(h(np.float64(-0.0)) == h(0.0), "numpy minus zero")
    for dtype in ("float64", "float32", "int32", "int64", "uint64", "bool", "uint8"):
        values = [[1, 0], [0, 1]] if dtype in ("bool", "uint8", "uint64") else [[0.1, -2.5], [3.0, -0.0]]
        if dtype.startswith("int"):
            values = [[1, -2], [3, -4]]
        a = np.array(values, dtype=dtype)
        check(Blob(a).hash == Blob(a.tolist(), dtype).hash, "%s: a numpy blob is not its list" % dtype)
        check(Blob(a).slice_hash(0, 1) == Blob(a.tolist()[0:1], dtype).hash, "%s: slices" % dtype)


# ---------------------------------------------------------------- the runner on the probe

@test
def probe_runs_and_skips():
    cache = tmp("p1")
    s1 = probe(cache)
    check(s1["ok"] and s1["stopped"] is None, "the probe did not run through: %s" % s1["stopped"])
    check(ran(s1) == list(HX.STAGES), "not every stage ran: %s" % ran(s1))
    s2 = probe(cache)
    check(ran(s2) == [], "a second run reran %s" % ran(s2))
    check(links(s1) == links(s2), "the links moved between two runs")
    report = diff_stage.diff_runs(GOLDEN, s2["out"])
    if report["differ"]:
        diff_stage.show(report, "golden", "run")
    check(not report["differ"], "the probe differs from its golden files (in this Python: %s)" % sys.version.split()[0])
    for st in HX.STAGES:  # each file's content hash can be recomputed from the JSON alone
        doc = json.load(open(os.path.join(s2["out"], st + ".json")))
        check(HX.hash_hex(doc["output"]) == doc["chain"]["output"], "%s: its output does not hash to its chain" % st)


@test
def probe_date_reruns_from_life():
    cache = tmp("p2")
    s1 = probe(cache, out=os.path.join(cache, "a"))
    s2 = probe(cache, date=1990, out=os.path.join(cache, "b"))
    check(ran(s2) == ["life", "geometry", "bake", "export", "checks"], "a new date reran %s" % ran(s2))
    check(links(s1)["plan"] == links(s2)["plan"] and links(s1)["life"] != links(s2)["life"], "the date's links")
    report = diff_stage.diff_runs(s1["out"], s2["out"])
    check(report["first"] == "life", "the first differing stage is %s, not life" % report["first"])
    named = [(at, f) for at, f, _, _ in report["stages"]["life"]["outputs"]]
    check(("st-probe/fl-0/tr-0/sl-0/1", "years") in named and (".", "date") in named,
          "diff_stage did not name the fill and field: %s" % named[:6])
    lines = []
    diff_stage.show(report, "1989", "1990", say=lines.append)
    check(any(l.strip() == "life st-probe/fl-0/tr-0/sl-0/1 years: 37 -> 38" for l in lines),
          "diff_stage's line for a fill's years: %s" % lines[:8])
    s3 = probe(cache, out=os.path.join(cache, "c"))
    check(ran(s3) == [], "going back to 1989 reran %s (the cache keeps %d per stage)" % (ran(s3), RK.KEEP))


@test
def probe_record_edits():
    cache = tmp("p3")
    probe(cache)
    rec = json.load(open(RECORD))
    spaced = os.path.join(tmp("p3-rec"), "st-probe.json")
    with open(spaced, "w") as f:
        json.dump(rec, f, indent=4, sort_keys=True)  # the same content, laid out otherwise
    check(ran(probe(cache, record=spaced)) == [], "a layout-only edit of the record reran stages")
    for s in rec["slots"]:
        for f in s["fills"]:
            if f["id"] == "st-probe/fl-0/tr-0/sl-0/1":
                f["origin"] = "new"
    with open(spaced, "w") as f:
        json.dump(rec, f, indent=1)
    s = probe(cache, record=spaced, out=os.path.join(cache, "edited"))
    check(ran(s) == list(HX.STAGES), "a record change did not rerun every stage: %s" % ran(s))
    report = diff_stage.diff_runs(GOLDEN, s["out"])
    check(report["first"] == "facts", "the first differing stage is %s" % report["first"])
    named = [(at, f) for at, f, _, _ in report["stages"]["facts"]["outputs"]]
    check(named == [("st-probe/fl-0/tr-0/sl-0/1", "origin")], "facts' difference: %s" % named)
    check("plan" in report["stages"] and not report["stages"]["plan"]["outputs"],
          "the plan's output should be the same with only its chain moved")


@test
def probe_kind_edits():
    cache = tmp("p4")
    probe(cache)
    kind = json.load(open(os.path.join(PROBE, "kinds", "probe.json")))
    kinds = tmp("p4-kinds")
    prose = dict(kind, describes=kind["describes"] + " Reworded.")
    json.dump(prose, open(os.path.join(kinds, "probe.json"), "w"))
    check(ran(probe(cache, kinds_dir=kinds)) == [], "a prose edit of the kind reran stages")
    param = json.loads(json.dumps(kind))
    param["stages"]["plan"]["params"]["jitterMm"] = 5
    json.dump(param, open(os.path.join(kinds, "probe.json"), "w"))
    s = probe(cache, kinds_dir=kinds)
    check(ran(s) == list(HX.STAGES), "a param change did not rerun every stage: %s" % ran(s))
    bad = json.loads(json.dumps(kind))
    bad["stages"]["life"]["reads"] = []
    json.dump(bad, open(os.path.join(kinds, "probe.json"), "w"))
    s = probe(cache, kinds_dir=kinds)
    check(not s["ok"] and s["stopped"] == "life failed" and "without declaring" in s["stages"][-1]["failed"],
          "an undeclared read of the date did not fail: %s" % s["stopped"])
    failing = json.loads(json.dumps(kind))
    failing["stages"]["checks"]["python"] = "tools/tests/probe/probe_stages.py:failing"
    json.dump(failing, open(os.path.join(kinds, "probe.json"), "w"))
    s = probe(cache, kinds_dir=kinds)
    check(not s["ok"] and s["stopped"] == "checks did not pass", "a failing check did not fail the run")
    planned = json.loads(json.dumps(kind))
    planned["stages"]["bake"]["status"] = "planned"
    json.dump(planned, open(os.path.join(kinds, "probe.json"), "w"))
    s = probe(cache, kinds_dir=kinds)
    check(s["ok"] and s["stopped"] == "bake is planned" and [x["stage"] for x in s["stages"]] == list(HX.STAGES[:4]),
          "a planned stage did not stop the run: %s" % s["stopped"])
    invalid = dict(kind, stages=dict(kind["stages"], plan=dict(kind["stages"]["plan"], params={"jitterMm": 0.5})))
    json.dump(invalid, open(os.path.join(kinds, "probe.json"), "w"))
    try:
        probe(cache, kinds_dir=kinds)
        raise AssertionError("a kind with a fractional plan param ran")
    except RK.SetupError as e:
        check("does not validate" in str(e), str(e))


@test
def probe_cache_validity():
    cache = tmp("p5")
    s1 = probe(cache)
    export_key = [x["key"] for x in s1["stages"] if x["stage"] == "export"][0]
    obj = os.path.join(cache, "stages", "st-probe", "export", "files", export_key, "st-probe.obj")
    check(os.path.exists(obj), "the export wrote no file")
    os.remove(obj)
    s2 = probe(cache)
    check(ran(s2) == ["export"], "a deleted export did not rerun export alone: %s" % ran(s2))
    check(links(s1) == links(s2), "rerunning export moved links")
    plan_key = [x["key"] for x in s2["stages"] if x["stage"] == "plan"][0]
    meta_path = os.path.join(cache, "stages", "st-probe", "plan", plan_key, "meta.json")
    meta = json.load(open(meta_path))
    entry = "tools/tests/probe/probe_stages.py"
    check(entry in meta["code"] and "tools/hashes.py" in meta["code"], "the code fingerprint lacks the entry")
    meta["code"][entry] = "0000000000000000"  # as though the stage's code had changed
    json.dump(meta, open(meta_path, "w"))
    s3 = probe(cache)
    check(ran(s3) == ["plan"], "a changed code fingerprint did not rerun plan alone: %s" % ran(s3))
    s4 = probe(cache, rerun=["geometry"])
    check(ran(s4) == ["geometry"], "--rerun geometry reran %s" % ran(s4))
    check(ran(probe(cache, use_cache=False)) == list(HX.STAGES), "--no-cache skipped stages")
    s5 = probe(cache, until="life")
    check(s5["stopped"] == "until life" and len(s5["stages"]) == 3, "--until life")
    check(not os.path.exists(os.path.join(s5["out"], "geometry.json")), "a stage file from an earlier run was left")


@test
def probe_ruleset_parts():
    kind = json.load(open(os.path.join(PROBE, "kinds", "probe.json")))
    parts = RK.load_parts(os.path.join(PROBE, "packs", "probe"))
    admitted = HX.admitted_parts(kind, parts)
    check(sorted(admitted) == ["mark/bed-scar", "repair/cement", "stone/slate/slab"],
          "admitted parts: %s" % sorted(admitted))


# ---------------------------------------------------------------- house 104 and the tools

@test
def house_facts():
    cache = tmp("h1")
    s = RK.run(HOUSE, world_seed=1, cache_dir=cache, out=os.path.join(cache, "out"), say=quiet)
    check(s["ok"] and s["stopped"] == "plan is planned", "house 104: %s" % s["stopped"])
    record_hash = HX.hash_hex(json.load(open(HOUSE)))
    check(s["stages"][0]["output"] == record_hash, "the facts output is not the record hash")
    report = diff_stage.diff_runs(HOUSE_GOLDEN, s["out"])
    if report["differ"]:
        diff_stage.show(report, "golden", "run")
    check(not report["differ"], "house 104's facts differ from fixtures/golden/house/facts.json")
    check(ran(RK.run(HOUSE, world_seed=1, cache_dir=cache, out=os.path.join(cache, "out"), say=quiet)) == [],
          "a second run of house 104 reran facts")


@test
def ids_and_diff_cli():
    import naming
    import record as REC
    g = naming.Grammar.load()
    for text, level in (("st-gully", "record"), ("st-gully/3", "event"), ("st-gully/fl-0/tr-3/sl-1", "slot"),
                        ("st-gully/fl-0/tr-3/sl-1/0", "fill"), ("st-gully/fl-0/tr-3/sl-1/0#1", "piece"),
                        ("st-gully/fl-0/tr-3/sl-1/0/ck", "slot"), ("st-gully/fl-0/tr-3/12/4", None),
                        ("st-gully/fl-0/tr-3/sl-1/0/ck/pt", "slot"), ("st-gully/fl-0/tr-3/sets/rw-2/0#4", "piece"),
                        ("wl-gully/fl-0/l/co-12/sp-6/ht-3", "slot"), ("st-passage-at--172", None)):
        check(REC.classify(g, text) == level, "%s is %s, not %s" % (text, REC.classify(g, text), level))
    # step 0b's seed keys, each under its kind's rule (schemas/naming.md)
    for rule, path in (("stair-flaw-part", "fl-0/tr-3/sl-1/0/ck/pt"), ("stair-flaw-part", "fl-1/tr-0/sl-2/1/ck/front"),
                       ("stair-flaw", "fl-0/tr-3/sl-1/0/dab"), ("stair-sett-row", "fl-0/tr-3/sets/rw-2"),
                       ("stair-row", "fl-1/turn/rw-0"), ("wall-hearting", "fl-0/l/co-12/sp-6/ht-3"),
                       ("wall-backing", "fl-0/r/bk-4-1"), ("wall-coping", "fl-1/l/cp-7")):
        check(g.match(rule, path), "%s is not a %s by naming.md" % (path, rule))
    check(not g.match("stair-flaw-part", "fl-0/tr-3/sl-1/ck/pt"), "a crack's pointing under a slot, not its fill")
    with contextlib.redirect_stdout(io.StringIO()):
        same = diff_stage.main(["diff_stage.py", GOLDEN, GOLDEN])
        differ = diff_stage.main(["diff_stage.py", os.path.join(GOLDEN, "life.json"), os.path.join(TMP, "p2", "b",
                                                                                                 "life.json")])
        missing = diff_stage.main(["diff_stage.py", GOLDEN, os.path.join(TMP, "nowhere")])
    check(same == 0, "diff_stage on one folder twice: exit %d" % same)
    check(differ == 1, "diff_stage on two dates' life: exit %d" % differ)
    check(missing == 2, "diff_stage on a missing folder: exit %d" % missing)

def main():
    try:
        for ok, name, why in RESULTS:
            print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else ": " + why))
        bad = sum(1 for ok, _, _ in RESULTS if not ok)
        print("%d of %d passed (Python %s%s)" % (len(RESULTS) - bad, len(RESULTS), sys.version.split()[0],
                                                 ", numpy %s" % np.__version__ if np is not None else ", no numpy"))
        return 1 if bad else 0
    finally:
        shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
