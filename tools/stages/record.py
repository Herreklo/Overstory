"""The stage entries every kind can share (schemas/stages.md): the record as facts, and the generic checks.

    "facts":  { "status": "live", "python": "tools/stages/record.py:facts", ... }
    "checks": { "status": "live", "python": "tools/stages/record.py:checks", ... }

facts validates the record with tools/validate_record.py (in-process where jsonschema is, else by the venv's Python)
and outputs the record itself, so its output hash is the record hash. checks looks over every earlier stage's output
for ids that break schemas/naming.md and counts the floats in the stages that choose (facts, plan and life hold none
once their kind's plan is in integers: decisions D2.2). A kind adds its own checks in its own checks entry.
"""
import copy
import glob
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
import hashes as HX  # noqa: E402
import naming  # noqa: E402

VENV_PYTHON = os.path.join(ROOT, ".venv", "bin", "python")
ID_FIELDS = ("id", "fill", "piece", "slot", "event", "placedBy", "endedBy", "madeBy", "closedBy", "host", "copyOf")
CHOOSING = ("facts", "plan", "life")


def facts(ctx):
    """The record, validated against the contracts and the rules the schemas cannot say."""
    for pattern in ("schemas/*", "kinds/*.json", "packs/**/*.json", "blender/resolver/face_class.py",
                    "tools/validate_record.py", "tools/naming.py"):
        for p in glob.glob(os.path.join(ROOT, pattern), recursive=True):
            if os.path.isfile(p):
                ctx.depends(p)
    try:
        import validate_record as VR
    except ImportError:
        VR = None
    if VR is not None:
        c = VR.Contracts()
        c.check_contracts()
        problems = list(c.problems)
        if not problems:
            ok, problems, counts = VR.validate(ctx.record_path, c)
            ctx.log("valid: %d events, %d slots, %d fills" % (counts["events"], counts["slots"], counts["fills"]))
    else:
        out = subprocess.run([VENV_PYTHON, os.path.join(TOOLS, "validate_record.py"), ctx.record_path],
                             capture_output=True, universal_newlines=True)
        problems = [] if out.returncode == 0 else ([line for line in out.stdout.splitlines() if line.startswith("FAIL")]
                                                   or [out.stdout.strip() or out.stderr.strip()])
        if not problems:
            ctx.log(out.stdout.strip() + " (by the venv)")
    if problems:
        raise ValueError("the record does not validate:\n  " + "\n  ".join(problems[:30]))
    return copy.deepcopy(ctx.source)


def _ids(v, rid, found, where=""):
    """Every id in an output: keys under the record and the values of id fields."""
    if isinstance(v, dict):
        for k, x in v.items():
            if k.startswith(rid + "/"):
                found.append((k, where))
            if k in ID_FIELDS and isinstance(x, str) and x.startswith(rid):
                found.append((x, where + "." + k))
            _ids(x, rid, found, k if k.startswith(rid + "/") else where + "." + k)
    elif isinstance(v, list):
        for x in v:
            _ids(x, rid, found, where)
    return found


def classify(grammar, text):
    """The id level a text matches in schemas/naming.md's grammar: record, event, slot, fill or piece; None if none."""
    for rule in ("piece", "fill", "event", "slot", "record"):
        if grammar.match(rule, text):
            return rule
    return None


def checks(ctx):
    """Ids in every earlier output well formed; the floats in the stages that choose, counted."""
    g = naming.Grammar.load()
    rid = ctx.record["id"]
    problems, n = [], 0
    for stage in HX.STAGES:
        if stage not in ctx.outputs:
            continue
        for text, where in _ids(HX.plain(ctx.outputs[stage]), rid, []):
            n += 1
            if text != rid and classify(g, text) is None:
                problems.append("%s: %s (at %s) matches no id rule in schemas/naming.md" % (stage, text, where or "."))
    floats = dict((s, HX.count_floats(HX.plain(ctx.outputs[s]))) for s in CHOOSING if s in ctx.outputs)
    return {"pass": not problems, "problems": problems[:50], "problemCount": len(problems), "ids": n,
            "floats": floats}
