"""The hash chain and its canonical encoding (schemas/hashing.md), on the one hash spec (blender/resolver/hashing.py).

A stage output, a record, a kind file: any value made of JSON's types is hashed by turning it into a stream of parts
(ints and strings) and folding them with hashing.h(). The stream is the canonical encoding: keys sorted by code point,
integers as decimal text, floats by their IEEE-754 binary64 bits (never formatted), strings as UTF-8, each value
tagged. A C# twin (Hashes.cs, later) reproduces it from fixtures/golden/canon-vectors.json. Bulk numbers (a mesh's
positions, a channel) are wrapped as a Blob: hashed word by word and summarised in JSON by dtype, shape and hash.

The chain (docs/building-blocks.md, Contracts): the head (schemaVersion, rulesetVersion, worldSeed), then each stage's
link, which hashes the link before it, the inputs the stage reads and the hash of what it wrote: record, plan, life,
mesh, bake (with bakeVersion among its inputs), export, checks. tools/run_kind.py keys its cache on it.

Runs in both Pythons: the venv's 3.9 without numpy and Blender's 3.13 with it, where numpy scalars and arrays hash as
the Python values they hold.

    python tools/hashes.py check              this file against fixtures/golden/canon-vectors.json; exit 1 on any difference
    python tools/hashes.py write              write the vectors again: only when the encoding itself changes
    python tools/hashes.py value <json>...    each file's content hash
"""
import glob
import json
import math
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "blender", "resolver"))
import hashing as HS  # noqa: E402  (the one hash spec)

M64 = HS.M64
VECTORS = os.path.join(ROOT, "fixtures", "golden", "canon-vectors.json")

# The seven stages, in the order every kind runs them (docs/building-blocks.md, The stage map).
STAGES = ("facts", "plan", "life", "geometry", "bake", "export", "checks")

# The kind file's prose: never read by a stage, so outside the rulesetVersion.
PROSE = ("describes", "frame")

# What bakeVersion hashes (decisions §2): the layer registry and the map registry now; the OS_History include, the
# layer curves' code, the bake and shell-bake code and the shaders they run in join from step 3, when the bake leaves
# Python. A pattern that matches nothing is hashed as absent, so a file added later changes it.
BAKE_INPUTS = ("schemas/layers.json", "schemas/maps.json")

FLOAT_DTYPES = ("float32", "float64")
INT_DTYPES = {"bool": (0, 1), "int8": (-2 ** 7, 2 ** 7 - 1), "int16": (-2 ** 15, 2 ** 15 - 1),
              "int32": (-2 ** 31, 2 ** 31 - 1), "int64": (-2 ** 63, 2 ** 63 - 1), "uint8": (0, 2 ** 8 - 1),
              "uint16": (0, 2 ** 16 - 1), "uint32": (0, 2 ** 32 - 1), "uint64": (0, 2 ** 64 - 1)}


class Refused(ValueError):
    """A value the encoding has no form for: NaN or an infinity, a key that is not a string, a set, bytes, an object."""


def hex64(n):
    return "%016x" % (n & M64)


def _is_numpy(v):
    return type(v).__module__ == "numpy" and hasattr(v, "tolist")


def float_bits(x, where="$"):
    """A float's IEEE-754 binary64 bits as an unsigned 64-bit int; minus zero is zero; NaN and infinities refused."""
    x = float(x)
    if not math.isfinite(x):
        raise Refused("%s: %r has no canonical form (a stage output must be finite)" % (where, x))
    if x == 0.0:
        x = 0.0
    return struct.unpack("<Q", struct.pack("<d", x))[0]


# ---------------------------------------------------------------- blobs

class Blob(object):
    """Bulk numbers a stage writes: a numpy array, or a nested list with its dtype (where there is no numpy). Hashed
    by array_hash; in JSON (a run's files, the golden fixtures) only its summary, {"$blob": {dtype, shape, hash}};
    whole only in the cache."""

    __slots__ = ("values", "dtype", "shape", "_hash")

    def __init__(self, values, dtype=None):
        if isinstance(values, Blob):
            values, dtype = values.values, dtype or values.dtype
        if _is_numpy(values) and hasattr(values, "shape"):
            import numpy as np
            if dtype and str(values.dtype) != dtype:
                values = values.astype(dtype)
            dtype = str(values.dtype)
            self.shape = tuple(int(n) for n in values.shape)
            self.values = np.ascontiguousarray(values)
        else:
            if dtype is None:
                raise Refused("a Blob of plain values needs its dtype")
            self.shape = _shape(values)
            self.values = values
        if dtype not in FLOAT_DTYPES and dtype not in INT_DTYPES:
            raise Refused("a Blob's dtype is one of %s, not %r" % (", ".join(FLOAT_DTYPES + tuple(INT_DTYPES)), dtype))
        self.dtype = dtype
        self._hash = None

    def words(self):
        """Each element in row-major order as a 64-bit word: a float's binary64 bits (a float32 widened exactly),
        an integer or bool as its two's complement."""
        floats = self.dtype in FLOAT_DTYPES
        if _is_numpy(self.values):
            import numpy as np
            if floats:
                a = self.values.astype(np.float64).ravel()
                if not np.isfinite(a).all():
                    raise Refused("a Blob holds NaN or an infinity")
                return (a + 0.0).view(np.uint64).tolist()
            return self.values.astype(np.uint64 if self.dtype == "uint64" else np.int64).ravel().tolist()
        flat = list(_flatten(self.values))
        if floats:
            if self.dtype == "float32":
                flat = [struct.unpack("<f", struct.pack("<f", float(x)))[0] for x in flat]
            return [float_bits(x, "blob") for x in flat]
        lo, hi = INT_DTYPES[self.dtype]
        out = []
        for x in flat:
            v = int(x)
            if not (lo <= v <= hi) or (self.dtype != "bool" and isinstance(x, bool)):
                raise Refused("blob: %r is not a %s" % (x, self.dtype))
            out.append(v)
        return out

    @property
    def hash(self):
        if self._hash is None:
            kind = "f" if self.dtype in FLOAT_DTYPES else "i"
            self._hash = HS.h("array", kind, len(self.shape), *(list(self.shape) + self.words()))
        return self._hash

    def summary(self):
        return {"$blob": {"dtype": self.dtype, "shape": list(self.shape), "hash": hex64(self.hash)}}

    def slice_hash(self, start, stop):
        """The array_hash of rows start to stop (a piece's vertices in its mesh)."""
        return Blob(self.values[start:stop], self.dtype).hash

    def tolist(self):
        return self.values.tolist() if _is_numpy(self.values) else self.values


def _shape(values):
    shape, v = [], values
    while isinstance(v, (list, tuple)):
        shape.append(len(v))
        if not v:
            break
        v = v[0]
    def check(v, depth):
        if depth == len(shape):
            if isinstance(v, (list, tuple)):
                raise Refused("a Blob's values must be rectangular")
            return
        if not isinstance(v, (list, tuple)) or len(v) != shape[depth]:
            raise Refused("a Blob's values must be rectangular")
        for x in v:
            check(x, depth + 1)
    check(values, 0)
    return tuple(shape)


def _flatten(v):
    if isinstance(v, (list, tuple)):
        for x in v:
            for y in _flatten(x):
                yield y
    else:
        yield v


def array_hash(values, dtype=None):
    """h("array", "f" or "i", ndim, *shape, *words): the hash of bulk numbers (schemas/hashing.md, Blobs)."""
    return Blob(values, dtype).hash


# ---------------------------------------------------------------- the canonical encoding

def _encode(v, out, where):
    """Append v's canonical parts to out (schemas/hashing.md, The encoding)."""
    if isinstance(v, Blob):
        _encode(v.summary(), out, where)
    elif _is_numpy(v):
        _encode(v.tolist(), out, where)
    elif v is None:
        out.append("n")
    elif v is True:
        out.append("t")
    elif v is False:
        out.append("f")
    elif isinstance(v, int):
        out.append("i")
        out.append(str(int(v)))
    elif isinstance(v, float):
        out.append("d")
        out.append(float_bits(v, where))
    elif isinstance(v, str):
        out.append("s")
        out.append(str(v))
    elif isinstance(v, (list, tuple)):
        out.append("a")
        out.append(len(v))
        for i, x in enumerate(v):
            _encode(x, out, "%s[%d]" % (where, i))
    elif isinstance(v, dict):
        for k in v:
            if not isinstance(k, str):
                raise Refused("%s: key %r is not a string" % (where, k))
        out.append("o")
        out.append(len(v))
        for k in sorted(v):
            out.append(str(k))
            _encode(v[k], out, "%s.%s" % (where, k))
    else:
        raise Refused("%s: a %s has no canonical form" % (where, type(v).__name__))


def tokens(v):
    """v's canonical encoding: the parts hashing.h() folds, in order."""
    out = []
    _encode(v, out, "$")
    return out


def hash_value(v):
    """The 64-bit hash of a value: h(*tokens(v))."""
    return HS.h(*tokens(v))


def hash_hex(v):
    return hex64(hash_value(v))


def plain(v, where="$", blobs=False):
    """v as plain JSON values, which hash the same: numpy as the Python values it holds, tuples as lists, a Blob as its
    summary (or kept, with blobs=True), minus zero as zero. Refuses what the encoding refuses, naming where."""
    if isinstance(v, Blob):
        return v if blobs else v.summary()
    if _is_numpy(v):
        return plain(v.tolist(), where, blobs)
    if v is None or v is True or v is False:
        return v
    if isinstance(v, str):
        return str(v)
    if isinstance(v, int):
        return int(v)
    if isinstance(v, float):
        float_bits(v, where)
        return 0.0 if v == 0.0 else float(v)
    if isinstance(v, (list, tuple)):
        return [plain(x, "%s[%d]" % (where, i), blobs) for i, x in enumerate(v)]
    if isinstance(v, dict):
        out = {}
        for k, x in v.items():
            if not isinstance(k, str):
                raise Refused("%s: key %r is not a string" % (where, k))
            out[k] = plain(x, "%s.%s" % (where, k), blobs)
        return out
    raise Refused("%s: a %s has no canonical form" % (where, type(v).__name__))


def count_floats(v):
    """How many floats a plain value holds (the integer stages hold none from step 2b; decisions D2.2)."""
    if isinstance(v, float):
        return 1
    if isinstance(v, list):
        return sum(count_floats(x) for x in v)
    if isinstance(v, dict):
        return sum(count_floats(x) for x in v.values())
    return 0


# ---------------------------------------------------------------- files

def text_hash(text):
    """A text's hash: h("text", text), over its UTF-8."""
    return hex64(HS.h("text", text))


def file_hash(path):
    """A JSON file by its content (so neither its layout nor its key order counts); any other file by its text."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if path.endswith(".json"):
        return hash_hex(json.loads(text))
    return text_hash(text)


def files_hash(root, patterns):
    """Every file matching the patterns (relative to root, ** allowed), by relative path; a pattern matching nothing
    is named absent."""
    found = {}
    for pat in patterns:
        hits = sorted(glob.glob(os.path.join(root, pat), recursive=True))
        if not hits:
            found[pat] = "absent"
        for p in hits:
            if os.path.isfile(p):
                found[os.path.relpath(p, root).replace(os.sep, "/")] = file_hash(p)
    return hash_hex(found)


def bake_version(root=ROOT):
    return files_hash(root, BAKE_INPUTS)


# ---------------------------------------------------------------- the chain

def admitted_parts(kind, parts):
    """The part definitions a kind's rules rest on: every part under a family one of its slots admits, and the marks
    those parts leave when removed. parts: {path: definition}. Returns {path: version}, sorted."""
    families = set()
    for slot in kind.get("slots", []):
        for fams in slot.get("roles", {}).values():
            families.update(fams)
    taken = set(p for p in parts if any(p == f or p.startswith(f + "/") for f in families))
    for p in list(taken):
        mark = parts[p].get("removalMark")
        mark = mark.get("part") if isinstance(mark, dict) else mark
        if mark in parts:
            taken.add(mark)
    return dict((p, parts[p]["version"]) for p in sorted(taken))


def ruleset_version(kind, part_versions):
    """rulesetVersion: the kind file without its prose, and the versions of the parts it admits."""
    rules = dict((k, v) for k, v in kind.items() if k not in PROSE)
    return hash_hex({"kind": rules, "parts": part_versions})


def head(schema_version, ruleset, world_seed):
    """The chain's head as written in a run's files: schemaVersion, rulesetVersion and worldSeed (as 16 hex digits,
    as plan.schema.json and the chunk header hold it)."""
    if not (0 <= world_seed <= M64):
        raise Refused("the world seed is an unsigned 64-bit integer, not %r" % world_seed)
    return {"schemaVersion": int(schema_version), "rulesetVersion": ruleset, "worldSeed": hex64(world_seed)}


def head_hash(h):
    return hash_hex(h)


def stage_key(stage, after, inputs):
    """What a stage's run is cached under: its name, the link before it (the head for facts) and its inputs."""
    return hash_hex({"stage": stage, "after": after, "inputs": inputs})


def link(stage, after, inputs, output):
    """A stage's link in the chain: its key's fields and the hash of what it wrote."""
    return hash_hex({"stage": stage, "after": after, "inputs": inputs, "output": output})


def summarise_pieces(pieces):
    """Per fill and per chunk, from per-piece summaries ({piece id: {fill, chunk, hash, and counts}}): how many
    pieces, the sum of each count, and a hash over the pieces' hashes by id."""
    def group(by):
        out = {}
        for pid in sorted(pieces):
            p = pieces[pid]
            g = out.setdefault(p[by], {"pieces": 0, "_h": {}})
            g["pieces"] += 1
            g["_h"][pid] = p["hash"]
            for k, v in p.items():
                if k not in ("fill", "chunk", "hash", "mesh") and isinstance(v, int) and not isinstance(v, bool):
                    g[k] = g.get(k, 0) + v
        for g in out.values():
            g["hash"] = hash_hex(g.pop("_h"))
        return dict((k, out[k]) for k in sorted(out))
    return {"fills": group("fill"), "chunks": group("chunk")}


def chunk_of(x_mm, y_mm, size_mm=4000):
    """The draw chunk a point falls in, by schemas/naming.md's units: ch-<i>-<j>, a negative index written with m."""
    def idx(v):
        i = v // size_mm
        return "m%d" % -i if i < 0 else "%d" % i
    return "ch-%s-%s" % (idx(int(x_mm)), idx(int(y_mm)))


# ---------------------------------------------------------------- the vectors

def _typed(parts):
    """Parts as hash_vectors.py writes them: an int as decimal text, a string as itself."""
    return [{"t": "int", "v": str(p)} if isinstance(p, int) else {"t": "str", "v": p} for p in parts]


def _untyped(parts):
    return [int(p["v"]) if p["t"] == "int" else p["v"] for p in parts]


VALUES = [
    "null", "true", "false",
    "0", "1", "-1", "42", "9223372036854775807", "-9223372036854775808", "18446744073709551615",
    "18446744073709551616", "-100000000000000000000000000000",
    "0.0", "-0.0", "1.0", "0.1", "-2.5", "1e+300", "5e-324", "9007199254740993.0", "0.10000000149011612", "1E3",
    "\"\"", "\"a\"", "\"0\"", "\"\\u00e6\\u00f8\\u00e5\"", "\"\\ud83d\\ude00\"", "\"a\\u0000b\"",
    "\"st-gully/fl-0/tr-3/sl-1/0#1\"",
    "[]", "{}", "[[]]", "[{}]", "[1, 1.0, \"1\", true, null]", "[0, 0.0, -0.0, false]",
    "{\"b\": 1, \"a\": 2}", "{\"a\": 2, \"b\": 1}",
    "{\"a\": 1, \"B\": 2, \"\\u00e9\": 3, \"z\": 4, \"\\uff61\": 5, \"\\ud83d\\ude00\": 6, \"ab\": 7, \"\": 8}",
    "{\"id\": \"st-gully/fl-0/tr-3/sl-1/0\", \"at\": [-1200, 350, 2100], \"heading\": 90000, \"fit\": {\"mode\": \"exact\", "
    "\"size\": [900, 400, 70]}, \"to\": null, \"origin\": \"new\"}",
    "{\"$blob\": {\"dtype\": \"float64\", \"shape\": [2, 3], \"hash\": \"0123456789abcdef\"}}",
]

ARRAYS = [
    ("float64", "[0.0, -0.0, 0.1, -2.5]"),
    ("float32", "[0.10000000149011612, 1.0, -0.0]"),
    ("float64", "[[1.5, 2.5, 3.5], [4.0, 5.0, 6.0]]"),
    ("int64", "[[0, 1, 2, 3], [-1, -2, 9223372036854775807, -9223372036854775808]]"),
    ("uint64", "[18446744073709551615, 0]"),
    ("int32", "[7, -7]"),
    ("uint8", "[0, 255]"),
    ("bool", "[true, false, true]"),
    ("float64", "[]"),
]


def _chain_example():
    """A chain written out link by link, from fixed output hashes: what a twin's chain must reproduce."""
    hd = head(2, "00000000000000aa", 1)
    after = head_hash(hd)
    stages = []
    outputs = {"facts": {"record": "1111111111111111"}, "plan": {}, "life": {"date": 1989}, "geometry": {"date": 1989},
               "bake": {"bakeVersion": "2222222222222222"}, "export": {}, "checks": {}}
    for i, st in enumerate(STAGES):
        out = hex64(HS.h("example output", i))
        k = stage_key(st, after, outputs[st])
        ln = link(st, after, outputs[st], out)
        stages.append({"stage": st, "after": after, "inputs": outputs[st], "output": out, "key": k, "link": ln})
        after = ln
    return {"head": hd, "headHash": head_hash(hd), "stages": stages}


def build():
    values = []
    for text in VALUES:
        v = json.loads(text)
        values.append({"json": text, "tokens": _typed(tokens(v)), "hash": hash_hex(v)})
    arrays = []
    for dtype, text in ARRAYS:
        b = Blob(json.loads(text), dtype)
        arrays.append({"dtype": dtype, "json": text, "shape": list(b.shape), "words": [hex64(w) for w in b.words()],
                       "hash": hex64(b.hash)})
    return {
        "what": "the canonical encoding's test vectors (schemas/hashing.md): each JSON text's tokens and hash; bulk "
                "numbers' words and array hash; a chain written out link by link (tools/hashes.py)",
        "spec": "tokens folded by hashing.h(): null n; true t; false f; int i + decimal text; float d + binary64 bits "
                "(minus zero is zero); string s + text; array a + length + items; object o + count + (key, value) by "
                "code point",
        "values": values, "arrays": arrays, "chain": _chain_example()}


def check(path=VECTORS):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    bad = 0
    for v in data["values"]:
        value = json.loads(v["json"])
        if _typed(tokens(value)) != v["tokens"] or hash_hex(value) != v["hash"] or \
                HS.h(*_untyped(v["tokens"])) != int(v["hash"], 16):
            bad += 1
            print("DIFF value", v["json"])
    for a in data["arrays"]:
        b = Blob(json.loads(a["json"]), a["dtype"])
        if [hex64(w) for w in b.words()] != a["words"] or hex64(b.hash) != a["hash"] or list(b.shape) != a["shape"]:
            bad += 1
            print("DIFF array", a["dtype"], a["json"])
    if _chain_example() != data["chain"]:
        bad += 1
        print("DIFF chain")
    print("%s: %d values, %d arrays and the chain, %d differ" % ("PASS" if not bad else "FAIL", len(data["values"]),
                                                              len(data["arrays"]), bad))
    return bad == 0 and len(data["values"]) == len(VALUES) and len(data["arrays"]) == len(ARRAYS)


def write(path=VECTORS):
    data = build()
    line = lambda o: json.dumps(o, ensure_ascii=False)
    with open(path, "w", encoding="utf-8") as f:
        # (one vector a line, so a diff names the one that moved)
        f.write("{\n")
        f.write(' "what": %s,\n "spec": %s,\n' % (line(data["what"]), line(data["spec"])))
        f.write(' "values": [\n' + ",\n".join("  " + line(v) for v in data["values"]) + "\n ],\n")
        f.write(' "arrays": [\n' + ",\n".join("  " + line(v) for v in data["arrays"]) + "\n ],\n")
        f.write(' "chain": %s\n}\n' % json.dumps(data["chain"], indent=1, ensure_ascii=False).replace("\n", "\n "))
    print("wrote", os.path.relpath(path, ROOT))


def main(argv):
    what = argv[1] if len(argv) > 1 else "check"
    if what == "write":
        write()
        return 0 if check() else 1
    if what == "check":
        return 0 if check() else 1
    if what == "value":
        for p in argv[2:]:
            print(file_hash(p), p)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
