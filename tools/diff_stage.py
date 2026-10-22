"""Diff two runs' stage outputs by stable id (schemas/stages.md, Diffs).

    python tools/diff_stage.py <run A> <run B>          two folders of stage files (a run's out, a golden folder)
    python tools/diff_stage.py <a/life.json> <b/life.json>
        --stage STAGE   only this stage (repeatable)
        --tol T         floats within T are the same (default 0: bit for bit)
        --limit N       at most N lines per stage (default 40)

It names the first stage whose output differs, then each difference as `<stage> <id> <field>: a -> b`: the id is the
nearest record, event, slot, fill or piece id above the difference (by schemas/naming.md), the field the path below it.
Things are matched by id, never by position, wherever there is one: a dict keyed by ids by its keys, a list of dicts
that each carry a unique id field (id, piece, fill, slot or event) by that field. A blob ({"$blob": ...}) compares as
one value. A stage whose output is the same but whose chain differs is named so (it rests on a link that moved).

Exit 0 when the runs are the same, 1 when they differ, 2 on a usage error. Runs in both Pythons.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import hashes as HX  # noqa: E402
import naming  # noqa: E402

ID_KEYS = ("id", "piece", "fill", "slot", "event")
LEVELS = ("piece", "fill", "event", "slot", "record")


class Ids(object):
    def __init__(self):
        self.grammar = naming.Grammar.load()
        self.memo = {}

    def level(self, text):
        if text not in self.memo:
            self.memo[text] = next((r for r in LEVELS if "/" in text or "-" in text
                                    if self.grammar.match(r, text)), None)
        return self.memo[text]


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _same_leaf(a, b, tol):
    if type(a) is not type(b):
        return False
    if isinstance(a, float):
        return a == b or (tol > 0 and abs(a - b) <= tol)
    return a == b


def _show(v):
    if isinstance(v, dict) and set(v) == {"$blob"}:
        s = v["$blob"]
        return "blob %s %s %s" % (s["dtype"], "x".join(str(n) for n in s["shape"]), s["hash"])
    text = json.dumps(v, ensure_ascii=False, sort_keys=True)
    if isinstance(v, float) and float(text) == v and "." not in text and "e" not in text:
        text += ".0"
    return text if len(text) <= 80 else text[:77] + "..."


def _id_field(a, b):
    """The id field that tells apart the dicts of each list, or None."""
    for k in ID_KEYS:
        if all(isinstance(x, dict) and isinstance(x.get(k), str) for x in a + b) and \
                all(len(set(x[k] for x in items)) == len(items) for items in (a, b)):
            return k
    return None


def diff_values(a, b, ids, tol=0.0, out=None, at=".", field=""):
    """Differences between two plain values: (id, field, a, b) with a or b None for 'only in'."""
    out = [] if out is None else out

    def add(fa, fb, f=field):
        out.append((at, f or "(value)", fa, fb))

    if isinstance(a, dict) and isinstance(b, dict) and not (set(a) == {"$blob"} or set(b) == {"$blob"}):
        for k in sorted(set(a) | set(b)):
            lvl = ids.level(k)
            sub_at, sub_field = (k, "") if lvl else (at, (field + "." + k) if field else k)
            if k not in a:
                out.append((sub_at, sub_field or "(itself)", Missing, b[k]))
            elif k not in b:
                out.append((sub_at, sub_field or "(itself)", a[k], Missing))
            else:
                diff_values(a[k], b[k], ids, tol, out, sub_at, sub_field)
        return out
    if isinstance(a, list) and isinstance(b, list):
        key = _id_field(a, b) if (a or b) else None
        if key:
            ma, mb = dict((x[key], x) for x in a), dict((x[key], x) for x in b)
            for k in sorted(set(ma) | set(mb)):
                lvl = ids.level(k)
                sub_at, sub_field = (k, "") if lvl else (at, "%s[%s=%s]" % (field, key, k))
                if k not in ma:
                    out.append((sub_at, sub_field or "(itself)", Missing, mb[k]))
                elif k not in mb:
                    out.append((sub_at, sub_field or "(itself)", ma[k], Missing))
                else:
                    diff_values(ma[k], mb[k], ids, tol, out, sub_at, sub_field)
            order_a, order_b = [x[key] for x in a], [x[key] for x in b]
            if set(order_a) == set(order_b) and order_a != order_b:  # (the order is hashed, so it is a difference)
                add("order " + ", ".join(order_a[:4]), "order " + ", ".join(order_b[:4]),
                    (field + " (order)") if field else "(order)")
            return out
        for i in range(max(len(a), len(b))):
            f = "%s[%d]" % (field, i)
            if i >= len(a):
                out.append((at, f, Missing, b[i]))
            elif i >= len(b):
                out.append((at, f, a[i], Missing))
            else:
                diff_values(a[i], b[i], ids, tol, out, at, f)
        return out
    if not _same_leaf(a, b, tol):
        add(a, b)
    return out


class _Missing(object):
    def __repr__(self):
        return "(absent)"


Missing = _Missing()


def _stage_files(path, stages):
    if os.path.isfile(path):
        doc = _read(path)
        return {doc.get("stage", os.path.basename(path)[:-5]): doc}
    found = {}
    for st in HX.STAGES:
        p = os.path.join(path, st + ".json")
        if os.path.exists(p) and (not stages or st in stages):
            found[st] = _read(p)
    return found


def _read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def diff_docs(a, b, ids, tol=0.0):
    """One stage's two files: (output differences, chain differences)."""
    outputs = diff_values(a.get("output"), b.get("output"), ids, tol)
    chain = [(f, ca, cb) for f, ca, cb in
             ((k, a.get("chain", {}).get(k, Missing), b.get("chain", {}).get(k, Missing))
              for k in sorted(set(a.get("chain", {})) | set(b.get("chain", {}))))
             if ca != cb]
    return outputs, chain


def diff_runs(a, b, stages=None, tol=0.0):
    """Two runs (folders or files): per stage its differences, the first stage whose output differs, and whether
    they differ at all."""
    ids = Ids()
    fa, fb = _stage_files(a, stages), _stage_files(b, stages)
    report = {"stages": {}, "only": {}, "first": None, "differ": False}
    for st in HX.STAGES + tuple(sorted(set(fa) | set(fb) - set(HX.STAGES))):
        if st not in fa and st not in fb:
            continue
        if st not in fa or st not in fb:
            report["only"][st] = "a" if st in fa else "b"
            report["differ"] = True
            if report["first"] is None:
                report["first"] = st
            continue
        outputs, chain = diff_docs(fa[st], fb[st], ids, tol)
        if outputs or chain:
            report["stages"][st] = {"outputs": outputs, "chain": chain}
            report["differ"] = True
        if outputs and report["first"] is None:
            report["first"] = st
    return report


def show(report, name_a="a", name_b="b", limit=40, say=print):
    if not report["differ"]:
        say("same: every stage's output and chain")
        return
    say("first stage whose output differs: %s" % (report["first"] or "none (the chain alone differs)"))
    for st, side in report["only"].items():
        say("%s: only in %s" % (st, name_a if side == "a" else name_b))
    for st in report["stages"]:
        d = report["stages"][st]
        if not d["outputs"]:
            say("%s: the same output; its chain differs (%s)" % (st, ", ".join(f for f, _, _ in d["chain"])))
            continue
        say("%s: %d difference%s in its output" % (st, len(d["outputs"]), "" if len(d["outputs"]) == 1 else "s"))
        for at, field, va, vb in d["outputs"][:limit]:
            if va is Missing:
                say("  %s %s %s: only in %s" % (st, at, field, name_b))
            elif vb is Missing:
                say("  %s %s %s: only in %s" % (st, at, field, name_a))
            else:
                say("  %s %s %s: %s -> %s" % (st, at, field, _show(va), _show(vb)))
        if len(d["outputs"]) > limit:
            say("  ... and %d more" % (len(d["outputs"]) - limit))


def main(argv):
    ap = argparse.ArgumentParser(prog="diff_stage.py", description="Diff two runs' stage outputs by stable id.")
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--stage", action="append", default=[])
    ap.add_argument("--tol", type=float, default=0.0)
    ap.add_argument("--limit", type=int, default=40)
    try:
        a = ap.parse_args(argv[1:])
    except SystemExit:
        return 2
    for p in (a.a, a.b):
        if not os.path.exists(p):
            print("diff_stage: no such file or folder %s" % p)
            return 2
    bad = [s for s in a.stage if s not in HX.STAGES]
    if bad:
        print("diff_stage: no such stage %s" % ", ".join(bad))
        return 2
    report = diff_runs(a.a, a.b, a.stage or None, a.tol)
    show(report, a.a, a.b, a.limit)
    return 1 if report["differ"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
