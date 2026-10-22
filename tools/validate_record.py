"""Validate records against the contracts (schemas/) and the rules the schemas cannot say.

    .venv/bin/python tools/validate_record.py                  every record in fixtures/records/, with the registries
    .venv/bin/python tools/validate_record.py <record.json>...  those records, with the registries
    .venv/bin/python tools/validate_record.py --self-test      break house 104 in each way the checks guard; all must fail

Exit 0 when everything passes; 1 on any failure, each line naming the record and the slot, fill or event.

The checks, beyond the JSON Schema (draft 2020-12, the files' $refs resolved through `referencing`):
- the contracts themselves: each schema is valid; every grammar pattern equals schemas/naming.md's (tools/naming.py);
  the vertex layouts add up; every layer sits on a map channel of its own name; every kind and part validates, and
  every pack's materials, each named as its file;
- ids: well formed by naming.md, unique, under their record; events numbered 1.. and fills 0.. in date order, fills of
  one event in the kind's role order; every slot path matches one of the kind's slot rules, of the rule's type, and the
  slots and fills it is held by exist and outlive it;
- dates: slots, fills, keepers, care, use and the lifespan in order and tied to the events that made and ended them
  (use from the lifespan's start, its periods in order); fills
  within their slot's dates and size and their host inside its host; no two fills of one role in a slot at once; a
  slot that takes others' places (spans) lies over them and none of their fills stands while it is open; two open
  openings on one host never overlap unless one spans the other;
- parts: defined in the pack, of a family the kind admits for the role, within the part's (or its variant's, or its
  copied fill's) era, of a fit the part takes, of a shader family the kind budgets;
- the face class of every surface region is the plan's function's (blender/resolver/face_class.py);
- the facts contract's hand-off (docs/facts-contract.md): no person or household acts or keeps before the people's
  start year; generated-past only before it; from the show year only the engine's events or marked stand-ins; a
  derived fact names its rule; a replaced fact stays, marked by the simulated event that replaced it; care never
  rests on character;
- nothing deleted: every event, slot and fill of the committed version (git show HEAD:<path>) is still there, and
  what fixes it (an event's date and kind, a slot's type, place and size, a fill's part, role and date) is unchanged.
"""
import copy
import importlib.util
import json
import os
import subprocess
import sys

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import naming  # noqa: E402

SCHEMAS = os.path.join(ROOT, "schemas")
CURRENT = 2


def _load_face_class():
    path = os.path.join(ROOT, "blender", "resolver", "face_class.py")
    spec = importlib.util.spec_from_file_location("face_class", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


face_class_module = _load_face_class()


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def rel(path):
    return os.path.relpath(os.path.abspath(path), ROOT)


# ---------------------------------------------------------------- dates

def dkey(d):
    """A date as a sortable key; a year alone sorts before its months."""
    return (d["year"], d.get("month", 0))


END = (10 ** 6, 0)


def tkey(d):
    """An end date as a key; null (still standing) is after every date."""
    return END if d is None else dkey(d)


def same_date(a, b):
    if a["year"] != b["year"]:
        return False
    return "month" not in a or "month" not in b or a["month"] == b["month"]


def show(d):
    if d is None:
        return "now"
    return "%d-%02d" % (d["year"], d["month"]) if "month" in d else str(d["year"])


def overlap(a0, a1, b0, b1):
    """Half-open spans [a0, a1) and [b0, b1) share time."""
    return a0 < b1 and b0 < a1


# ---------------------------------------------------------------- the contracts

class Contracts(object):
    """Everything a record is checked against: schemas, grammar, registries, packs, kinds and parts."""

    def __init__(self):
        self.problems = []
        self.grammar = naming.Grammar.load()
        self.schemas = {}
        for name in sorted(os.listdir(SCHEMAS)):
            if name.endswith(".schema.json"):
                self.schemas[name] = read_json(os.path.join(SCHEMAS, name))
        resources = [(s["$id"], Resource.from_contents(s, default_specification=DRAFT202012)) for s in self.schemas.values()]
        self.registry = Registry().with_resources(resources)
        self.channels = read_json(os.path.join(SCHEMAS, "channels.json"))
        self.maps = read_json(os.path.join(SCHEMAS, "maps.json"))
        self.layers = read_json(os.path.join(SCHEMAS, "layers.json"))
        self._kinds = {}
        self._packs = {}
        self._parts = {}

    def fail(self, where, message):
        self.problems.append("%s: %s" % (where, message))

    def validator(self, schema_file):
        return Draft202012Validator(self.schemas[schema_file], registry=self.registry)

    def schema_errors(self, schema_file, doc):
        return sorted(self.validator(schema_file).iter_errors(doc), key=lambda e: list(e.absolute_path))

    # -- the contracts themselves
    def check_contracts(self):
        for name, schema in self.schemas.items():
            try:
                Draft202012Validator.check_schema(schema)
            except Exception as e:  # jsonschema raises SchemaError with the reason
                self.fail("schemas/" + name, "not a valid draft 2020-12 schema: %s" % str(e).splitlines()[0])
            if schema.get("$id") != "https://overstory.invalid/schemas/" + name:
                self.fail("schemas/" + name, "$id must be https://overstory.invalid/schemas/" + name)
        for f, rule, why in naming.drift(self.grammar):
            self.fail(f, "pattern %s: %s (tools/naming.py --render)" % (rule, why))
        for doc, name in ((self.channels, "channels.json"), (self.maps, "maps.json"), (self.layers, "layers.json")):
            if doc.get("schemaVersion") != CURRENT:
                self.fail("schemas/" + name, "schemaVersion %r, the contracts are at %d" % (doc.get("schemaVersion"), CURRENT))
        self._check_channels()
        self._check_maps_and_layers()
        for kind_file in sorted(os.listdir(os.path.join(ROOT, "kinds"))):
            if kind_file.endswith(".json"):
                self.kind(kind_file[:-5])
        packs = os.path.join(ROOT, "packs")
        for pack in sorted(os.listdir(packs)):
            if os.path.isdir(os.path.join(packs, pack)):
                self.pack(pack)
                self.materials(pack)
                parts = os.path.join(packs, pack, "parts")
                for dirpath, _, files in os.walk(parts):
                    for f in sorted(files):
                        if f.endswith(".json"):
                            path = os.path.relpath(os.path.join(dirpath, f), parts)[:-5].replace(os.sep, "/")
                            self.part(pack, path)

    def _check_channels(self):
        sizes = self.channels["sizes"]
        for layout in ("vertex", "shell"):
            spec = self.channels[layout]
            base = total = 0
            for slot in spec["slots"]:
                if sizes.get(slot["format"]) != slot["bytes"]:
                    self.fail("schemas/channels.json", "%s.%s: %s is %s bytes, not %d" % (layout, slot["slot"], slot["format"], sizes.get(slot["format"]), slot["bytes"]))
                total += slot["bytes"]
                if not slot.get("optional"):
                    base += slot["bytes"]
            if base != spec["bytes"]:
                self.fail("schemas/channels.json", "%s: its slots add to %d bytes, it says %d" % (layout, base, spec["bytes"]))
            if "bytesWithOptions" in spec and total != spec["bytesWithOptions"]:
                self.fail("schemas/channels.json", "%s: with options its slots add to %d bytes, it says %d" % (layout, total, spec["bytesWithOptions"]))
        bits = set()
        for field in self.channels["pickIndex"]["fields"]:
            lo, hi = field["bits"]
            span = set(range(lo, hi + 1))
            if bits & span:
                self.fail("schemas/channels.json", "pickIndex.%s overlaps another field" % field["field"])
            bits |= span
        if bits != set(range(32)):
            self.fail("schemas/channels.json", "pickIndex's fields do not fill 32 bits")

    def _check_maps_and_layers(self):
        g = self.grammar
        units = self.maps["units"]
        sizes = []
        for unit, spec in units.items():
            if not g.match("unit", "%s-0-0" % unit):
                self.fail("schemas/maps.json", "unit %s is not in naming.md's unit rule" % unit)
            sizes.append(spec["sizeMm"])
        for a, b in zip(sizes, sizes[1:]):
            if b % a or (b // a) & (b // a - 1):
                self.fail("schemas/maps.json", "unit sizes %d and %d do not nest by a power of two" % (a, b))
        seen = set()
        for row in self.maps["faceClasses"]["table"]:
            for onto in row["looksOnto"]:
                if (row["facing"], onto) in seen:
                    self.fail("schemas/maps.json", "faceClasses: %s onto %s twice" % (row["facing"], onto))
                seen.add((row["facing"], onto))
        self.map_ids = {}
        for m in self.maps["maps"]:
            if not g.match("map", m["id"]):
                self.fail("schemas/maps.json", "map id %r is not a name by naming.md" % m["id"])
            if m["id"] in self.map_ids:
                self.fail("schemas/maps.json", "map %s twice" % m["id"])
            self.map_ids[m["id"]] = m
        self.field_ids = set(self.map_ids["fields"]["slices"])
        self.layer_ids = set()
        taken = {}
        for layer in self.layers["layers"]:
            lid, mid, ch = layer["id"], layer["map"], layer["channel"]
            where = "schemas/layers.json: %s" % lid
            if not g.match("map", lid):
                self.fail(where, "not a name by naming.md")
            if lid in self.layer_ids or lid in self.map_ids or lid in self.field_ids:
                self.fail(where, "its name is taken")
            self.layer_ids.add(lid)
            m = self.map_ids.get(mid)
            if m is None:
                self.fail(where, "map %s is not in maps.json" % mid)
                continue
            if m.get("channels", {}).get(ch) != lid:
                self.fail(where, "maps.json's %s.%s is %r, not this layer" % (mid, ch, m.get("channels", {}).get(ch)))
            if (mid, ch) in taken:
                self.fail(where, "shares %s.%s with %s" % (mid, ch, taken[(mid, ch)]))
            taken[(mid, ch)] = lid
        for r in self.layers["reserved"]:
            if self.map_ids.get(r["map"], {}).get("channels", {}).get(r["channel"]) != "reserved":
                self.fail("schemas/layers.json", "%s.%s is listed reserved but maps.json does not reserve it" % (r["map"], r["channel"]))

    # -- packs, kinds and parts
    def pack(self, pack):
        if pack not in self._packs:
            path = os.path.join(ROOT, "packs", pack, "pack.json")
            if not os.path.exists(path):
                self._packs[pack] = None
                self.fail("packs/%s" % pack, "has no pack.json")
            else:
                p = read_json(path)
                where = rel(path)
                for k in ("schemaVersion", "pack", "peopleStart", "showYear", "firstYear"):
                    if k not in p:
                        self.fail(where, "has no %s" % k)
                if p.get("pack") != pack:
                    self.fail(where, "names pack %r" % p.get("pack"))
                if p.get("schemaVersion") != CURRENT:
                    self.fail(where, "schemaVersion %r, the contracts are at %d" % (p.get("schemaVersion"), CURRENT))
                if not (p.get("firstYear", 0) <= p.get("peopleStart", 0) < p.get("showYear", 0)):
                    self.fail(where, "firstYear, peopleStart and showYear must rise")
                self._packs[pack] = p
        return self._packs[pack]

    def materials(self, pack):
        """The pack's materials (packs/<pack>/materials/<material>.json), each against material.schema.json."""
        folder = os.path.join(ROOT, "packs", pack, "materials")
        if not os.path.isdir(folder):
            return
        for f in sorted(os.listdir(folder)):
            if not f.endswith(".json"):
                continue
            path = os.path.join(folder, f)
            m = read_json(path)
            where = rel(path)
            for e in self.schema_errors("material.schema.json", m):
                self.fail(where, "%s: %s" % ("/".join(str(p) for p in e.absolute_path) or "(top)", e.message))
            if m.get("material") != f[:-5]:
                self.fail(where, "names material %r, its file is %s" % (m.get("material"), f))

    def kind(self, kind):
        if kind not in self._kinds:
            path = os.path.join(ROOT, "kinds", kind + ".json")
            if not os.path.exists(path):
                self._kinds[kind] = None
                self.fail("kinds/%s.json" % kind, "no such kind file")
                return None
            k = read_json(path)
            where = rel(path)
            for e in self.schema_errors("kind.schema.json", k):
                self.fail(where, "%s: %s" % ("/".join(str(p) for p in e.absolute_path) or "(top)", e.message))
            if k.get("kind") != kind:
                self.fail(where, "names kind %r" % k.get("kind"))
            for s in k.get("slots", []):
                if s.get("rule") not in self.grammar.raw:
                    self.fail(where, "slot rule %r is not in naming.md's grammar" % s.get("rule"))
                if s.get("type") == "group" and s.get("roles"):
                    self.fail(where, "slot rule %s: a group takes no fills" % s.get("rule"))
            for a in k.get("affordances", []):
                if a.get("rule") not in self.grammar.raw:
                    self.fail(where, "affordance %s: rule %r is not in naming.md's grammar" % (a.get("name"), a.get("rule")))
            for lid in k.get("layers", []):
                if lid not in self.layer_ids:
                    self.fail(where, "layer %s is not in layers.json" % lid)
            for side in ("reads", "writes"):
                for fid in k.get("fields", {}).get(side, []):
                    if fid not in self.field_ids and fid not in self.map_ids:
                        self.fail(where, "fields.%s: %s is no field or map in maps.json" % (side, fid))
            self._kinds[kind] = k
        return self._kinds[kind]

    def part(self, pack, path):
        key = (pack, path)
        if key not in self._parts:
            file = os.path.join(ROOT, "packs", pack, "parts", *path.split("/")) + ".json"
            if not os.path.exists(file):
                self._parts[key] = None
                return None
            p = read_json(file)
            where = rel(file)
            for e in self.schema_errors("part.schema.json", p):
                self.fail(where, "%s: %s" % ("/".join(str(x) for x in e.absolute_path) or "(top)", e.message))
            if p.get("part") != path:
                self.fail(where, "names part %r, its path is %s" % (p.get("part"), path))
            era = p.get("era", {})
            for v in p.get("variants", []):
                ve = v.get("era")
                if ve and not (era.get("first", 0) <= ve["first"] and (era.get("last") is None or (ve["last"] is not None and ve["last"] <= era["last"]))):
                    self.fail(where, "variant %s's years lie outside the part's" % v["name"])
            if p.get("removalMark") and self.part(pack, p["removalMark"]) is None:
                self.fail(where, "its removal mark %s has no definition in the pack" % p["removalMark"])
            for s in p.get("sizes", {}).values():
                if s[0] > s[1]:
                    self.fail(where, "a size range runs backwards")
            self._parts[key] = p
        return self._parts[key]


# ---------------------------------------------------------------- one record

def floats(o, path=""):
    if isinstance(o, float):
        yield path or "(top)"
    elif isinstance(o, dict):
        for k, v in o.items():
            for p in floats(v, path + "/" + k):
                yield p
    elif isinstance(o, list):
        for i, v in enumerate(o):
            for p in floats(v, "%s/%d" % (path, i)):
                yield p


def schema_where(record, path):
    """The slot, fill or event a schema error's path points into (or None), and the rest of the path."""
    path = list(path)
    try:
        if path[:1] == ["slots"] and len(path) > 1:
            slot = record["slots"][path[1]]
            if path[2:3] == ["fills"] and len(path) > 3:
                fill = slot["fills"][path[3]]
                return fill.get("id", "%s fill %d" % (slot.get("id"), path[3])), path[4:]
            return slot.get("id", "slot %d" % path[1]), path[2:]
        if path[:1] == ["events"] and len(path) > 1:
            return record["events"][path[1]].get("id", "event %d" % path[1]), path[2:]
    except (KeyError, IndexError, TypeError, AttributeError):
        pass
    return None, path


def schema_message(e):
    """A schema error in the project's words: a grammar pattern names its rule, not its regex."""
    if e.validator == "pattern" and str(e.schema.get("$comment", "")).startswith("naming: "):
        return "%r does not match naming.md's %s rule" % (e.instance, e.schema["$comment"][8:])
    if e.validator == "enum" and e.instance == "engine":
        return "provenance 'engine' is retired: it is 'simulated' (tools/migrate.py)"
    if e.validator in ("oneOf", "anyOf") and e.context:
        best = sorted(e.context, key=lambda x: len(list(x.absolute_path)))[-1]
        return "%s (%s)" % (e.message[:200], schema_message(best))
    return e.message


def check_record(contracts, record, previous=None, label=None):
    """Append each failure to contracts.problems; return the record's counts."""
    c = contracts
    g = c.grammar
    rid = record.get("id", "?") if isinstance(record, dict) else "?"
    label = label or rid

    def fail(what, message):
        c.fail("%s: %s" % (label, what) if what else label, message)

    if not isinstance(record, dict):
        fail(None, "a record is a JSON object")
        return None
    for p in floats(record):
        fail(p, "a fraction: records hold integers only (mm, per mille, years and months)")
    if record.get("schemaVersion") != CURRENT:
        fail(None, "schemaVersion %r is behind %d: run tools/migrate.py" % (record.get("schemaVersion"), CURRENT))
        return None
    errors = c.schema_errors("record.schema.json", record)
    for e in errors:
        what, rest = schema_where(record, e.absolute_path)
        fail(what, "%s%s" % ("/".join(str(x) for x in rest) + ": " if rest else "", schema_message(e)))
    if errors:
        return None

    kind = c.kind(record["kind"])
    pack = c.pack(record["pack"])
    if kind is None or pack is None:
        return None
    S, SHOW = pack["peopleStart"], pack["showYear"]
    prefix = rid.split("-", 1)[0]
    if prefix not in kind["recordPrefixes"]:
        fail(None, "prefix %s is not one the %s kind takes (%s)" % (prefix, kind["kind"], ", ".join(kind["recordPrefixes"])))

    # ---- ids: unique, under the record
    events = record["events"]
    slots = record["slots"]
    ids = {}
    for kind_name, items in (("event", events), ("slot", slots)):
        for it in items:
            ids.setdefault(it["id"], []).append(kind_name)
    fills = {}
    fill_slot = {}
    for s in slots:
        for f in s["fills"]:
            ids.setdefault(f["id"], []).append("fill")
            fills[f["id"]] = f
            fill_slot[f["id"]] = s
    for i, twice in ids.items():
        if len(twice) > 1:
            fail(i, "the id is used %d times (%s)" % (len(twice), ", ".join(twice)))
        if not i.startswith(rid + "/"):
            fail(i, "the id is not under its record %s" % rid)
    ev = {e["id"]: e for e in events}
    sl = {s["id"]: s for s in slots}

    # ---- events: numbered from 1 in date order, of the kind's words
    for n, e in enumerate(events, 1):
        if e["id"] != "%s/%d" % (rid, n):
            fail(e["id"], "event %d of the record must be %s/%d: events are numbered from 1, never renumbered" % (n, rid, n))
        if n > 1 and dkey(e["at"]) < dkey(events[n - 2]["at"]):
            fail(e["id"], "dated %s, before the event above it (%s): events are in date order" % (show(e["at"]), show(events[n - 2]["at"])))
        if e["kind"] not in kind["eventKinds"]:
            fail(e["id"], "event kind %s is not one the %s kind admits" % (e["kind"], kind["kind"]))
        for s in e.get("where", {}).get("slots", []):
            if s not in sl:
                fail(e["id"], "touches %s, which the record does not hold" % s)

    def event_at(eid, what, at=None, relation="on"):
        """Check an event exists; when `at` is given, that the event is dated on (or, for 'by', no later than) it."""
        e = ev.get(eid)
        if e is None:
            fail(what, "names event %s, which the record does not hold" % eid)
            return None
        if at is not None:
            if relation == "on" and not same_date(e["at"], at):
                fail(what, "dated %s, but %s is dated %s" % (show(at), eid, show(e["at"])))
            if relation == "after" and dkey(e["at"]) < dkey(at):
                fail(what, "from %s, but its event %s is earlier (%s)" % (show(at), eid, show(e["at"])))
        return e

    # ---- lifespan
    life = record["lifespan"]
    event_at(life["madeBy"], "lifespan", life["from"])
    if (life["to"] is None) != (life["removedBy"] is None):
        fail("lifespan", "to and removedBy are both null or both set")
    elif life["to"] is not None:
        event_at(life["removedBy"], "lifespan", life["to"])
        if dkey(life["to"]) < dkey(life["from"]):
            fail("lifespan", "ends before it begins")
    if events and dkey(events[0]["at"]) < dkey(life["from"]):
        fail(events[0]["id"], "dated before the thing was made (%s)" % show(life["from"]))

    # ---- keepers and care: one at a time, from the making
    for name, rows in (("keepers", record["keepers"]), ("care", record["care"])):
        if not same_date(rows[0]["from"], life["from"]):
            fail(name, "the first runs from %s, the thing from %s: name 'no one' for a gap" % (show(rows[0]["from"]), show(life["from"])))
        for a, b in zip(rows, rows[1:]):
            if dkey(b["from"]) <= dkey(a["from"]):
                fail(name, "%s does not follow %s: each runs to the next one's from" % (show(b["from"]), show(a["from"])))
        for r in rows:
            if "event" in r:
                event_at(r["event"], "%s from %s" % (name, show(r["from"])), r["from"], "after")
            if r["provenance"] == "derived" and "rule" not in r:
                fail("%s from %s" % (name, show(r["from"])), "derived, so it names its rule")

    # ---- use: periods one after another, the first from the making (optional)
    use = record.get("use", [])
    if use and not same_date(use[0]["from"], life["from"]):
        fail("use", "the first period runs from %s, the thing from %s" % (show(use[0]["from"]), show(life["from"])))
    for a, b in zip(use, use[1:]):
        if dkey(b["from"]) <= dkey(a["from"]):
            fail("use", "%s does not follow %s: each period runs to the next one's from" % (show(b["from"]), show(a["from"])))
    for r in use:
        if "event" in r:
            event_at(r["event"], "use from %s" % show(r["from"]), r["from"], "after")
        if r["provenance"] == "derived" and "rule" not in r:
            fail("use from %s" % show(r["from"]), "derived, so it names its rule")

    # ---- slots
    rules = kind["slots"]
    roles_order = {r: i for i, r in enumerate(kind["roles"])}
    families = {}

    def slot_rule(path):
        for r in rules:
            if g.match(r["rule"], path):
                return r
        return None

    def interval(x):
        return dkey(x["from"]), tkey(x["to"])

    for s in slots:
        sid = s["id"]
        path = sid[len(rid) + 1:] if sid.startswith(rid + "/") else sid
        if not g.match("slot", sid):
            fail(sid, "not a slot id by naming.md")
        rule = slot_rule(path)
        if rule is None:
            fail(sid, "its path %s matches none of the %s kind's slot rules" % (path, kind["kind"]))
        elif rule["type"] != s["type"]:
            fail(sid, "a %s by the kind's rule %s, not a %s" % (rule["type"], rule["rule"], s["type"]))
        a0, a1 = interval(s)
        if a1 < a0:
            fail(sid, "closes (%s) before it is made (%s)" % (show(s["to"]), show(s["from"])))
        if "madeBy" in s:
            event_at(s["madeBy"], sid, s["from"])
        if s["to"] is not None and "closedBy" in s:
            event_at(s["closedBy"], sid, s["to"])
        if s["to"] is None and ("closedBy" in s or "closeRule" in s):
            fail(sid, "names what closed it but is still open")
        if a0 < dkey(life["from"]) or (life["to"] is not None and a1 > dkey(life["to"])):
            fail(sid, "outlives the thing (%s to %s)" % (show(life["from"]), show(life["to"])))
        # what holds it: every slot above it, and the fill a name after a count is held by
        segs = path.split("/")
        for k in range(1, len(segs)):
            holder = rid + "/" + "/".join(segs[:k])
            if segs[k - 1].isdigit():
                h = fills.get(holder)
                if h is None:
                    fail(sid, "held by fill %s, which the record does not hold" % holder)
                    continue
            else:
                h = sl.get(holder)
                if h is None:
                    fail(sid, "under slot %s, which the record does not hold" % holder)
                    continue
            h0, h1 = interval(h)
            if a0 < h0 or a1 > h1:
                fail(sid, "outlives %s (%s to %s)" % (holder, show(h["from"]), show(h["to"])))
        # its place
        host = s.get("host")
        if host is not None:
            h = sl.get(host)
            if h is None:
                fail(sid, "hosted by %s, which the record does not hold" % host)
            elif h["type"] == "group":
                fail(sid, "hosted by a group, which has no place")
            else:
                h0, h1 = interval(h)
                if a0 < h0 or a1 > h1:
                    fail(sid, "outlives its host %s" % host)
                for axis, name in enumerate(("width", "height", "depth")):
                    if s["at"][axis] < 0 or s["at"][axis] + s["size"][axis] > h["size"][axis]:
                        fail(sid, "its %s runs outside its host %s" % (name, host))
        if s["type"] == "surface":
            f = s["surface"]
            try:
                want = face_class_module.face_class(f["facing"], f["looksOnto"])
            except ValueError as e:
                fail(sid, str(e))
            else:
                if want != f["faceClass"]:
                    fail(sid, "face class %s, but a %s facing onto %s is %s by the plan's function" % (f["faceClass"], f["facing"], f["looksOnto"], want))

        # ---- its fills
        last_role_by_event = {}
        for n, f in enumerate(s["fills"]):
            fid = f["id"]
            if fid != "%s/%d" % (sid, n):
                fail(fid, "fill %d of %s must be %s/%d: fills are numbered from 0, never renumbered" % (n, sid, sid, n))
            if n and dkey(f["from"]) < dkey(s["fills"][n - 1]["from"]):
                fail(fid, "from %s, before the fill above it: fills are in date order" % show(f["from"]))
            b0, b1 = interval(f)
            if b1 < b0:
                fail(fid, "ends (%s) before it begins (%s)" % (show(f["to"]), show(f["from"])))
            if b0 < a0 or b1 > a1:
                fail(fid, "stands %s to %s, outside its slot's %s to %s" % (show(f["from"]), show(f["to"]), show(s["from"]), show(s["to"])))
            if "placedBy" in f:
                event_at(f["placedBy"], fid, f["from"])
                group = (f["placedBy"], dkey(f["from"]))
                order = roles_order.get(f["role"], -1)
                if group in last_role_by_event and order < last_role_by_event[group]:
                    fail(fid, "placed by %s with the fill above it, so it follows the kind's role order (%s)" % (f["placedBy"], ", ".join(kind["roles"])))
                last_role_by_event[group] = order
            if f["to"] is not None and "endedBy" in f:
                event_at(f["endedBy"], fid, f["to"])
            for axis, name in enumerate(("width", "height", "depth")):
                if f["fit"]["size"][axis] > s["size"][axis]:
                    fail(fid, "fitted %s %d mm, its slot's is %d" % (name, f["fit"]["size"][axis], s["size"][axis]))
            # the kind admits it
            if rule is not None:
                admitted = rule["roles"].get(f["role"])
                if admitted is None:
                    fail(fid, "a %s, which the kind's %s slots do not take" % (f["role"], rule["rule"]))
                elif not any(f["part"] == fam or f["part"].startswith(fam + "/") for fam in admitted):
                    fail(fid, "part %s is of no family the kind takes for a %s there (%s)" % (f["part"], f["role"], ", ".join(admitted)))
            check_part(c, record, kind, f, fid, fills, fail)
        # one role at a time
        for i, f in enumerate(s["fills"]):
            for f2 in s["fills"][i + 1:]:
                if f["role"] == f2["role"] and overlap(*(interval(f) + interval(f2))):
                    fail(f2["id"], "stands with %s, of the same role (%s), at once" % (f["id"], f["role"]))

    # ---- spans and overlapping openings
    for s in slots:
        for spanned in s.get("spans", []):
            t = sl.get(spanned)
            if t is None or spanned == s["id"]:
                fail(s["id"], "spans %s, which is not another slot of the record" % spanned)
                continue
            if t.get("host") != s.get("host"):
                fail(s["id"], "spans %s, which has another host" % spanned)
                continue
            if any(t["at"][a] < s["at"][a] or t["at"][a] + t["size"][a] > s["at"][a] + s["size"][a] for a in range(3)):
                fail(s["id"], "spans %s but does not lie over it" % spanned)
            for f in t["fills"]:
                if overlap(*(interval(f) + interval(s))):
                    fail(f["id"], "stands while %s, which takes its slot's place, is open (%s to %s)" % (s["id"], show(s["from"]), show(s["to"])))
    openings = [s for s in slots if s["type"] in ("opening", "socket") and s.get("host")]
    for i, s in enumerate(openings):
        for t in openings[i + 1:]:
            if s["host"] != t["host"] or not overlap(*(interval(s) + interval(t))):
                continue
            if all(s["at"][a] < t["at"][a] + t["size"][a] and t["at"][a] < s["at"][a] + s["size"][a] for a in (0, 1)):
                if t["id"] not in s.get("spans", []) and s["id"] not in t.get("spans", []):
                    fail(t["id"], "overlaps %s while both are open; one must span the other" % s["id"])

    # ---- the facts contract's hand-off
    persons = lambda actor: "id" in actor and g.match("engine-person", actor["id"])
    for e in events:
        y = e["at"]["year"]
        if y < S and persons(e["actor"]):
            fail(e["id"], "a person or household (%s) acts in %d, before the people's start year %d: before it actors are roles" % (e["actor"]["id"], y, S))
        if e["provenance"] == "generated-past" and y >= S:
            fail(e["id"], "generated-past in %d: the pack's script writes only before the people's start year %d" % (y, S))
        if y >= SHOW and e["provenance"] in ("authored", "derived") and not e.get("standIn"):
            fail(e["id"], "%s in %d: from the show year %d only the engine's events change the record; mark a test stand-in standIn" % (e["provenance"], y, SHOW))
        if e.get("standIn") and (e["provenance"] != "authored" or y < SHOW):
            fail(e["id"], "a stand-in is an authored event from the show year %d" % SHOW)
        if "supersededBy" in e:
            r = ev.get(e["supersededBy"])
            if r is None or r["provenance"] != "simulated":
                fail(e["id"], "superseded by %s, which is not a simulated event of the record" % e["supersededBy"])
            if e["provenance"] == "simulated":
                fail(e["id"], "the engine's own events are never superseded here")
    for e in events:
        if e["provenance"] == "simulated":
            for o in events:
                if o is not e and o["provenance"] in ("authored", "derived", "generated-past") and o["kind"] == e["kind"] \
                        and o["at"]["year"] == e["at"]["year"] and o.get("supersededBy") != e["id"]:
                    fail(o["id"], "the engine has %s for the same thing (%s): mark this one supersededBy it" % (e["id"], e["kind"]))
    for name, rows, field in (("keepers", record["keepers"], "keeper"), ("care", record["care"], None)):
        for r in rows:
            y = r["from"]["year"]
            if field and y < S and persons(r[field]):
                fail("%s from %d" % (name, y), "a person or household keeps it before the people's start year %d" % S)
            if r["provenance"] == "generated-past" and y >= S:
                fail("%s from %d" % (name, y), "generated-past after the people's start year %d" % S)
            if y >= SHOW and r["provenance"] in ("authored", "derived"):
                e = ev.get(r.get("event"))
                if e is None or not e.get("standIn"):
                    fail("%s from %d" % (name, y), "%s from the show year %d: it must come from a stand-in event" % (r["provenance"], SHOW))
    if persons(record["actor"]) and life["from"]["year"] < S:
        fail("actor", "a person or household made it before the people's start year %d" % S)
    for p in record["pins"]:
        if p["on"] not in ev and p["on"] not in sl and p["on"] not in fills:
            fail("pins", "a pin on %s, which the record does not hold" % p["on"])

    # ---- nothing deleted
    if previous is not None:
        check_kept(record, previous, fail)
    return dict(events=len(events), slots=len(slots), fills=len(fills))


def check_part(c, record, kind, f, fid, fills, fail):
    part = c.part(record["pack"], f["part"])
    if part is None:
        fail(fid, "part %s has no definition in packs/%s/parts/" % (f["part"], record["pack"]))
        return
    if f.get("removalMark") and c.part(record["pack"], f["removalMark"]["part"]) is None:
        fail(fid, "removal mark %s has no definition in the pack" % f["removalMark"]["part"])
    variants = {v["name"]: v for v in part.get("variants", [])}
    if variants and f.get("variant") not in variants:
        fail(fid, "part %s comes as %s; the fill names %r" % (f["part"], ", ".join(variants), f.get("variant")))
        return
    if not variants and "variant" in f:
        fail(fid, "part %s has no variants" % f["part"])
        return
    if f["fit"]["mode"] not in part["fits"]:
        fail(fid, "fit %s, but part %s takes %s" % (f["fit"]["mode"], f["part"], ", ".join(part["fits"])))
    if f["fit"]["mode"] in ("exact", "fitted") and "sizes" in part:
        for axis, (name, k) in enumerate((("width", "w"), ("height", "h"), ("depth", "d"))):
            lo, hi = part["sizes"][k]
            if not lo <= f["fit"]["size"][axis] <= hi:
                fail(fid, "%s %d mm, outside part %s's %d to %d" % (name, f["fit"]["size"][axis], f["part"], lo, hi))
    if part["shaderFamily"] not in kind["budgets"]["shadingOverFlatUs"]:
        fail(fid, "part %s is drawn by shader family %s, which the %s kind does not budget" % (f["part"], part["shaderFamily"], kind["kind"]))
    # its years: the variant's, else the part's; a copy keeps the copied fill's
    era = variants.get(f.get("variant"), {}).get("era") or part["era"]
    year = f["from"]["year"]
    if "copyOf" in f:
        orig = fills.get(f["copyOf"])
        if orig is None:
            fail(fid, "a copy of %s, which the record does not hold" % f["copyOf"])
            return
        if orig["part"] != f["part"] or orig.get("variant") != f.get("variant"):
            fail(fid, "a copy of %s, but of another part or variant" % f["copyOf"])
        if dkey(orig["from"]) > dkey(f["from"]):
            fail(fid, "a copy of a later fill, %s" % f["copyOf"])
        year = orig["from"]["year"]
    if year < era["first"] or (era["last"] is not None and year > era["last"]):
        fail(fid, "part %s%s belongs to %d to %s, not %d%s" % (
            f["part"], " (%s)" % f["variant"] if f.get("variant") else "", era["first"],
            era["last"] if era["last"] is not None else "now", year, " (the copied fill's year)" if "copyOf" in f else ""))
    life = part["lifecycle"]
    if life["state"] in ("deprecated", "removed") and "since" in life and dkey(f["from"]) >= dkey(life["since"]) and "copyOf" not in f:
        fail(fid, "part %s is %s since %s; no new fill takes it" % (f["part"], life["state"], show(life["since"])))


def check_kept(record, previous, fail):
    """Nothing the committed version holds is gone or moved."""
    old_events = {e["id"]: e for e in previous.get("events", [])}
    new_events = {e["id"]: e for e in record["events"]}
    for i, e in old_events.items():
        n = new_events.get(i)
        if n is None:
            fail(i, "deleted: the committed version holds it, and events are never deleted")
        elif n["kind"] != e["kind"] or dkey(n["at"]) != dkey(e["at"]):
            fail(i, "renumbered or rewritten: it was %s in %s in the committed version" % (e["kind"], show(e["at"])))
    old_slots = {s["id"]: s for s in previous.get("slots", [])}
    new_slots = {s["id"]: s for s in record["slots"]}
    for i, s in old_slots.items():
        n = new_slots.get(i)
        if n is None:
            fail(i, "deleted: the committed version holds it, and slots are never deleted")
            continue
        for k in ("type", "at", "size", "from"):
            if n.get(k) != s.get(k):
                fail(i, "its %s changed from the committed version: a change of place or size closes it and makes a new slot" % k)
        old_fills = {f["id"]: f for f in s.get("fills", [])}
        new_fills = {f["id"]: f for f in n.get("fills", [])}
        for j, f in old_fills.items():
            m = new_fills.get(j)
            if m is None:
                fail(j, "deleted: the committed version holds it, and fills are never deleted")
            elif any(m.get(k) != f.get(k) for k in ("part", "role", "from")):
                fail(j, "renumbered or rewritten: its part, role or date changed from the committed version")


def committed(path):
    """The record as last committed, or None."""
    try:
        out = subprocess.run(["git", "show", "HEAD:" + rel(path)], cwd=ROOT, capture_output=True, check=False)
    except OSError:
        return None
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout.decode("utf-8"))
    except ValueError:
        return None


def validate(path, contracts=None):
    """The kind files' checks entry point: validate one record file; return (ok, problems)."""
    c = contracts or Contracts()
    before = len(c.problems)
    try:
        record = read_json(path)
    except ValueError as e:
        c.fail(rel(path), "not JSON: %s" % e)
        return False, c.problems[before:], None
    counts = check_record(c, record, committed(path), label="%s (%s)" % (record.get("id", "?"), rel(path)))
    return len(c.problems) == before, c.problems[before:], counts


# ---------------------------------------------------------------- the self-test

def self_test():
    """Break house 104 in each way the checks guard against; every break must fail, the record itself must pass."""
    c = Contracts()
    c.check_contracts()
    if c.problems:
        print("\n".join("FAIL " + p for p in c.problems))
        return 1
    base = read_json(os.path.join(ROOT, "fixtures", "records", "bld-104.json"))

    def slot(r, sid):
        return next(s for s in r["slots"] if s["id"] == "bld-104/" + sid)

    def fill(r, fid):
        sid, n = fid.rsplit("/", 1)
        return slot(r, sid)["fills"][int(n)]

    def m_overlap(r):
        fill(r, "op-f0-0/2")["from"] = {"year": 1925}
        fill(r, "op-f0-0/2")["copyOf"] = "bld-104/op-f0-0/0"

    def m_float(r):
        slot(r, "sf-f")["size"][0] = 9000.5

    def m_wrong_face_class(r):
        slot(r, "sf-f")["surface"]["looksOnto"] = "yard"

    def m_too_big(r):
        fill(r, "op-f0-1/0")["fit"]["size"][0] = 1200

    def m_after_slot(r):
        fill(r, "op-f0-0-1/0")["to"] = None
        for k in ("end", "endedBy", "removalMark"):
            fill(r, "op-f0-0-1/0").pop(k)

    def m_spanned_stands(r):
        f = fill(r, "op-f0-1/0")
        f["to"], f["endedBy"] = {"year": 1949}, "bld-104/4"

    def m_person_before_s(r):
        r["events"][0]["actor"] = {"id": "p-812"}

    def m_no_stand_in(r):
        r["events"][8].pop("standIn")

    def m_generated_after_s(r):
        r["events"][5]["provenance"] = "generated-past"

    def m_engine_word(r):
        r["events"][0]["provenance"] = "engine"

    def m_bad_id(r):
        slot(r, "sf-f")["id"] = "bld-104/SF-F"

    def m_duplicate(r):
        fill(r, "op-f0-1/1")["id"] = "bld-104/op-f0-1/0"

    def m_renumbered(r):
        r["events"][3]["id"] = "bld-104/40"

    def m_out_of_order(r):
        r["events"][3]["at"] = {"year": 1930}

    def m_family(r):
        fill(r, "sf-f/0")["part"] = "window/cross-arch"

    def m_keepers(r):
        r["keepers"][2]["from"] = {"year": 1931}

    def m_no_part(r):
        fill(r, "op-f0-0/0")["part"] = "window/round-top"

    def m_role_order(r):
        s = slot(r, "op-f0-1")
        s["fills"][0]["role"], s["fills"][1]["role"] = "surround", "body"
        s["fills"][0]["part"], s["fills"][1]["part"] = "trim/casing", "window/cross-arch"
        s["fills"][0]["variant"] = "arch"
        s["fills"][1].pop("variant")

    def m_overlap_openings(r):
        slot(r, "op-f0-0-1").pop("spans")

    def m_unknown_slot_rule(r):
        s = slot(r, "sf-f")
        s["id"] = "bld-104/front"
        for i, f in enumerate(s["fills"]):
            f["id"] = "bld-104/front/%d" % i
        for o in r["slots"]:
            if o.get("host") == "bld-104/sf-f":
                o["host"] = "bld-104/front"
        for e in r["events"]:
            if "where" in e:
                e["where"]["slots"] = ["bld-104/front" if x == "bld-104/sf-f" else x for x in e["where"]["slots"]]

    def m_slot_date(r):
        slot(r, "op-f0-0-1")["from"] = {"year": 1932}

    def m_character(r):
        r["care"][1]["basis"] = ["character"]

    cases = [
        ("two fills of one role at once", m_overlap, "of the same role"),
        ("a shopfront out of its years", None, None),
        ("a fraction", m_float, "a fraction"),
        ("the wrong face class", m_wrong_face_class, "by the plan's function"),
        ("a fill bigger than its slot", m_too_big, "its slot's is"),
        ("a fill outliving its slot", m_after_slot, "outside its slot's"),
        ("a spanned window standing under the shop", m_spanned_stands, "which takes its slot's place"),
        ("a person acting before S", m_person_before_s, "before the people's start year"),
        ("an authored event after the show year", m_no_stand_in, "only the engine's events"),
        ("generated-past after S", m_generated_after_s, "generated-past in"),
        ("the retired word engine", m_engine_word, "retired"),
        ("an id against the grammar", m_bad_id, "does not match naming.md's slot rule"),
        ("an id twice", m_duplicate, "is used 2 times"),
        ("an event renumbered", m_renumbered, "numbered from 1"),
        ("events out of date order", m_out_of_order, "date order"),
        ("a family the kind does not take", m_family, "of no family"),
        ("two keepers at once", m_keepers, "does not follow"),
        ("a part with no definition", m_no_part, "has no definition"),
        ("fills against the role order", m_role_order, "role order"),
        ("two openings overlapping unspanned", m_overlap_openings, "one must span the other"),
        ("a slot no rule names", m_unknown_slot_rule, "matches none of"),
        ("a slot dated off its event", m_slot_date, "is dated"),
        ("care resting on character", m_character, "'character' is not one of"),
        ("the retired word engine, in a nested place", None, None),
    ]

    def era_case(r):
        fill(r, "op-f0-0/0")["part"] = "shopfront/shop-1930"
        fill(r, "op-f0-0/0")["fit"]["size"] = [900, 1500, 150]

    cases[1] = ("a shopfront out of its years", era_case, "belongs to 1930 to 1950, not 1912")

    def m_engine_keeper(r):
        r["keepers"][0]["provenance"] = "engine"

    cases[-1] = ("the retired word engine on a keeper", m_engine_keeper, "retired")

    failed = caught = 0
    ok = Contracts()
    ok.check_contracts()
    check_record(ok, copy.deepcopy(base), label="bld-104")
    if ok.problems:
        print("FAIL the unbroken record does not pass:")
        print("\n".join("  " + p for p in ok.problems))
        failed += 1
    for name, mutate, expect in cases:
        r = copy.deepcopy(base)
        mutate(r)
        t = Contracts()
        t._kinds, t._packs, t._parts = ok._kinds, ok._packs, ok._parts
        t.map_ids, t.field_ids, t.layer_ids = ok.map_ids, ok.field_ids, ok.layer_ids
        check_record(t, r, label="bld-104")
        hit = [p for p in t.problems if expect in p]
        if not hit:
            failed += 1
            print("FAIL %s: not caught%s" % (name, (" (it said: %s)" % t.problems[0]) if t.problems else ""))
        else:
            caught += 1
            print("caught %s: %s" % (name, hit[0]))
    # deletion against a committed version
    r = copy.deepcopy(base)
    r["slots"] = [s for s in r["slots"] if s["id"] != "bld-104/op-f0-0-1"]
    for e in r["events"]:
        if "where" in e:
            e["where"]["slots"] = [x for x in e["where"]["slots"] if x != "bld-104/op-f0-0-1"]
    t = Contracts()
    t._kinds, t._packs, t._parts = ok._kinds, ok._packs, ok._parts
    t.map_ids, t.field_ids, t.layer_ids = ok.map_ids, ok.field_ids, ok.layer_ids
    check_record(t, r, previous=base, label="bld-104")
    hit = [p for p in t.problems if "deleted" in p]
    if hit:
        caught += 1
        print("caught a slot deleted since the commit: %s" % hit[0])
    else:
        failed += 1
        print("FAIL a slot deleted since the commit: not caught")
    print("self-test: %d of %d breaks caught; the unbroken record %s" % (caught, len(cases) + 1, "fails" if ok.problems else "passes"))
    return 1 if failed else 0


# ---------------------------------------------------------------- main

def main(argv):
    if argv[1:] == ["--self-test"]:
        return self_test()
    paths = argv[1:]
    if not paths:
        folder = os.path.join(ROOT, "fixtures", "records")
        paths = [os.path.join(folder, f) for f in sorted(os.listdir(folder)) if f.endswith(".json")]
    c = Contracts()
    c.check_contracts()
    if c.problems:
        for p in c.problems:
            print("FAIL " + p)
        return 1
    status = 0
    for path in paths:
        result = validate(path, c)
        ok, problems = result[0], result[1]
        if ok:
            n = result[2]
            print("ok %s: %d events, %d slots, %d fills" % (rel(path), n["events"], n["slots"], n["fills"]))
        else:
            status = 1
            for p in problems:
                print("FAIL " + p)
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv))
