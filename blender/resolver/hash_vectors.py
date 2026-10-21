"""The hash spec's test vectors (docs/building-blocks.md, Seeds and determinism): 200 keys and the hash and unit that
hashing.py gives each, and eight streams' first draws, in fixtures/golden/hash-vectors.json. Python and C#
(unity/Assets/Code/Editor/Measuring/HashVectors.cs) must both reproduce every one.

    python3 blender/resolver/hash_vectors.py check    # hashing.py against the file; exits 1 on any difference
    python3 blender/resolver/hash_vectors.py write    # (re)write the file: only when the spec itself is changed

The keys cover the edges (no parts, zero, minus one, the 64-bit limits, the empty string, a control character,
multi-byte and four-byte UTF-8, the project's own id forms) and then mixtures of up to six parts drawn from the spec
itself. An int part is written as decimal text, a hash as 16 hex digits, so nothing passes through a JSON number but
the units and the normals.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hashing as HS  # noqa: E402

PATH = os.path.join(HERE, "..", "..", "fixtures", "golden", "hash-vectors.json")
COUNT = 200

EDGES = [
    [], [0], [1], [-1], [42], [255], [256], [65535], [2 ** 32], [-(2 ** 32)], [2 ** 63 - 1], [-(2 ** 63)],
    [2 ** 63], [2 ** 64 - 1], [1874], [1989],
    [""], ["a"], ["0"], ["-1"], ["kerb"], ["st-gully"], ["st-gully/tr-17/2"], ["st-gully/fl-0/tr-3/sl-1/0#1"],
    ["Gully Steps"], ["Tanner's Steps"], ["the way to D (1107, empty since 1986)"], ["Øystein"], ["æøå ÆØÅ"],
    ["日本語"], ["😀"], ["a\u007fb"], ["\t\n"], ["x" * 200],
    [0, ""], ["", 0], [0, 0], ["", ""], [1, "st-gully", "lean"], [1, "st-gully/fl-0", "setout"],
    [1989, "town stone"], [1, 2, 3, 4, 5, 6], ["upkeep", -5, "ø", 2 ** 64 - 1], [7, "😀", -(2 ** 63), "æ"],
]

ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789-/#_ .'ØæøåÆÅé日😀"


def _key(r):
    parts = []
    for _ in range(r.randint(1, 6)):
        kind = r.randint(0, 4)
        if kind == 0:
            parts.append(r.randint(0, 99))
        elif kind == 1:
            parts.append(r.randint(-(2 ** 63), 2 ** 64 - 1))
        elif kind == 2:
            parts.append(-r.randint(1, 10 ** 6))
        else:
            parts.append("".join(r.choice(ALPHABET) for _ in range(r.randint(0, 24))))
    return parts


def keys():
    r = HS.Stream("hash-vectors", 1)
    out = [list(k) for k in EDGES]
    while len(out) < COUNT:
        out.append(_key(r))
    return out


def encode(parts):
    return [dict(t="int", v=str(p)) if isinstance(p, int) else dict(t="str", v=p) for p in parts]


def decode(parts):
    return [int(p["v"]) if p["t"] == "int" else p["v"] for p in parts]


def build():
    vectors = []
    for k in keys():
        v = HS.h(*k)
        vectors.append(dict(key=encode(k), hash=f"{v:016x}", unit=HS.unit(v)))
    streams = []
    for k in [[], [0], ["st-gully/fl-0/tr-3/sl-1/0", "lay"], [1, "slab"], ["😀", -1], [1989, "air motes"],
              [2 ** 64 - 1, ""], ["upkeep", 1952]]:
        s = HS.Stream(*k)
        draws = [f"{s.next():016x}" for _ in range(8)]
        s = HS.Stream(*k)
        normals = [s.normal() for _ in range(2)]
        streams.append(dict(key=encode(k), draws=draws, normals=normals))
    return dict(what="the hash spec's test vectors: h(*key) as 16 hex digits and unit(h); streams' first draws "
                     "(Stream(*key).next()) and two normals from a fresh stream (blender/resolver/hashing.py)",
                spec="FNV-1a 64 over UTF-8; SplitMix64 from 0x2545F4914F6CDD1D; unit = (h >> 11) / 2^53",
                vectors=vectors, streams=streams)


def check(path=PATH):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    bad = 0
    for v in data["vectors"]:
        k = decode(v["key"])
        got = HS.h(*k)
        if f"{got:016x}" != v["hash"] or HS.unit(got) != v["unit"]:
            bad += 1
            print("DIFF", k, f"{got:016x}", v["hash"])
    for s_ in data["streams"]:
        k = decode(s_["key"])
        s = HS.Stream(*k)
        got = [f"{s.next():016x}" for _ in range(len(s_["draws"]))]
        s = HS.Stream(*k)
        normals = [s.normal() for _ in range(len(s_["normals"]))]
        if got != s_["draws"] or normals != s_["normals"]:
            bad += 1
            print("DIFF stream", k)
    n = len(data["vectors"])
    print(f"{'PASS' if not bad else 'FAIL'}: {n} hashes and {len(data['streams'])} streams, {bad} differ")
    return bad == 0 and n == COUNT


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "check"
    if what == "write":
        os.makedirs(os.path.dirname(PATH), exist_ok=True)
        data = build()
        line = lambda o: json.dumps(o, ensure_ascii=False)
        with open(PATH, "w", encoding="utf-8") as fh:
            # (one vector a line, so a diff names the key that moved)
            fh.write("{\n")
            fh.write(f' "what": {line(data["what"])},\n "spec": {line(data["spec"])},\n')
            fh.write(' "vectors": [\n' + ",\n".join("  " + line(v) for v in data["vectors"]) + "\n ],\n")
            fh.write(' "streams": [\n' + ",\n".join("  " + line(v) for v in data["streams"]) + "\n ]\n}\n")
        print("wrote", os.path.normpath(PATH))
    sys.exit(0 if check() else 1)
