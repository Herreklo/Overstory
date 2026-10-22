"""Bring every versioned file up to the contracts' schemaVersion, by the migrations in migrations/.

    .venv/bin/python tools/migrate.py           migrate every file that is behind, in place
    .venv/bin/python tools/migrate.py --check   exit 1 if any file is behind or a migration would not apply

The files are every JSON file carrying schemaVersion under fixtures/ (but not fixtures/engine/, which is the engine's
own export, or fixtures/golden/, which the stages write), kinds/ and packs/. Each migration is
migrations/NNN_<name>.py with FROM, TO and migrate(doc, path) -> doc; they run in order, each on every file at its
FROM. A file keeps its own JSON layout (indent, escaping, final newline) when a dump can reproduce it; a hand-laid
file that must change is rewritten with an indent of 2 and said so. Never hand-edit a file a migration should change:
rerun this instead, so the curated town and its pins migrate by the same scripts.
"""
import importlib.util
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIGRATIONS = os.path.join(ROOT, "migrations")
SCAN = ["fixtures", "kinds", "packs"]
SKIP = [os.path.join("fixtures", "engine"), os.path.join("fixtures", "golden")]


def migrations():
    found = []
    for name in sorted(os.listdir(MIGRATIONS)):
        m = re.match(r"^(\d{3})_[a-z0-9_]+\.py$", name)
        if not m:
            continue
        spec = importlib.util.spec_from_file_location("migration_" + m.group(1), os.path.join(MIGRATIONS, name))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.NAME = name
        found.append(module)
    for a, b in zip(found, found[1:]):
        if b.FROM != a.TO:
            raise SystemExit("migrations/%s starts at %d, but %s ends at %d" % (b.NAME, b.FROM, a.NAME, a.TO))
    return found


def current(found):
    return found[-1].TO if found else 1


def files():
    for top in SCAN:
        for dirpath, dirnames, names in os.walk(os.path.join(ROOT, top)):
            relp = os.path.relpath(dirpath, ROOT)
            dirnames[:] = sorted(d for d in dirnames if os.path.join(relp, d) not in SKIP)
            for n in sorted(names):
                if n.endswith(".json"):
                    yield os.path.join(dirpath, n)


STYLES = [dict(indent=i, ensure_ascii=a) for i in (2, 1, 4, None) for a in (False, True)]


def style_of(text, doc):
    """The dump settings that reproduce the file exactly, or None for a hand-laid file."""
    newline = text.endswith("\n")
    for s in STYLES:
        if json.dumps(doc, **s) + ("\n" if newline else "") == text:
            return dict(s, newline=newline)
    return None


def dump(doc, style):
    if style is None:
        style = dict(indent=2, ensure_ascii=False, newline=True)
    out = json.dumps(doc, indent=style["indent"], ensure_ascii=style["ensure_ascii"])
    return out + ("\n" if style["newline"] else "")


def run(check):
    found = migrations()
    target = current(found)
    record_schema = json.load(open(os.path.join(ROOT, "schemas", "record.schema.json"), encoding="utf-8"))
    problems = []
    if record_schema["$defs"]["schemaVersion"].get("const") != target:
        problems.append("schemas/record.schema.json's schemaVersion is %r, the last migration ends at %d"
                        % (record_schema["$defs"]["schemaVersion"].get("const"), target))
    seen = 0
    for path in files():
        relp = os.path.relpath(path, ROOT)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        try:
            doc = json.loads(text)
        except ValueError as e:
            problems.append("%s: not JSON: %s" % (relp, e))
            continue
        if not isinstance(doc, dict) or "schemaVersion" not in doc:
            problems.append("%s: carries no schemaVersion" % relp)
            continue
        seen += 1
        version = doc["schemaVersion"]
        if not isinstance(version, int) or version > target:
            problems.append("%s: schemaVersion %r, the contracts are at %d" % (relp, version, target))
            continue
        if version == target:
            print("current %s (schemaVersion %d)" % (relp, version))
            continue
        style = style_of(text, doc)
        steps = []
        for m in found:
            if doc["schemaVersion"] == m.FROM:
                doc = m.migrate(doc, relp)
                if doc.get("schemaVersion") != m.TO:
                    problems.append("%s: %s left schemaVersion at %r" % (relp, m.NAME, doc.get("schemaVersion")))
                    break
                steps.append(m.NAME)
        if check:
            problems.append("%s: behind at schemaVersion %d; %s would bring it to %d" % (relp, version, ", ".join(steps), target))
            continue
        with open(path, "w", encoding="utf-8") as f:
            f.write(dump(doc, style))
        print("migrated %s: %d to %d by %s%s" % (relp, version, target, ", ".join(steps),
                                                "" if style else " (hand-laid: rewritten with an indent of 2)"))
    for p in problems:
        print("FAIL " + p)
    if not problems:
        print("%d files at schemaVersion %d" % (seen, target) if check else "done: %d files" % seen)
    return 1 if problems else 0


def main(argv):
    if argv[1:] not in ([], ["--check"]):
        print(__doc__)
        return 2
    return run(check=argv[1:] == ["--check"])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
