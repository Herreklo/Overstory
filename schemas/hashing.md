# Hashing

How a value is hashed, so two languages agree, and how the hashes chain into the cache keys of the stages (`docs/building-blocks.md`, The stage map; decisions §2, D2.4). `tools/hashes.py` is the Python; a C# twin (`Hashes.cs`, at the kind's port) reproduces it from `fixtures/golden/canon-vectors.json`. Both sit on the one hash spec, `blender/resolver/hashing.py`, which `Hash.cs` already matches (`fixtures/golden/hash-vectors.json`).

## The spec underneath

`h(part, part, ...)` folds parts into 64 bits: it starts at `0x2545F4914F6CDD1D`, and for each part takes an integer as its low 64 bits (two's complement) or a string as its 64-bit FNV-1a over UTF-8, then `acc = SplitMix64(acc ^ part)`. Hashes are written as 16 lowercase hex digits.

## The encoding

A value made of JSON's types becomes a stream of parts, and its hash is `h` over the stream. Each value writes a tag, then its payload:

| Value | Parts |
| --- | --- |
| null | `"n"` |
| true, false | `"t"`, `"f"` |
| integer | `"i"`, then its decimal text as a string (any size, `-` for a negative, no leading zeros) |
| float | `"d"`, then its IEEE-754 binary64 bits as an integer. Minus zero is written as zero. NaN and the infinities are refused. |
| string | `"s"`, then the string |
| array | `"a"`, its length as an integer, then each item |
| object | `"o"`, its count as an integer, then each key (a string part, no tag) and its value, the keys in code-point order |

The rules a twin must keep:
- **Integers and floats differ.** `1` and `1.0` hash apart. In a JSON file a number is a float when its text holds `.`, `e` or `E`, an integer otherwise. Python's `json` reads them so and writes floats so (`1.0`, never `1`), so a stage file read back hashes as it was written. A C# reader must keep the same distinction.
- **Floats are never formatted.** Their bits are hashed: the binary64 value, after a float32 is widened exactly.
- **Keys sort by code point,** which is UTF-8 byte order. In C#, that is `string.CompareOrdinal` only for keys without surrogates; sort by `Rune` or by UTF-8 bytes. The vector `{"a", "B", "é", "z", "｡", "😀", "ab", ""}` catches UTF-16 order.
- Keys are strings; sets, bytes and other objects are refused, never coerced.
- A tuple is its list. numpy scalars and arrays (Blender's Python) are the Python values they hold, so a run with numpy and a run without hash the same.

## Blobs: bulk numbers

A stage's bulk numbers (a mesh's positions, a per-vertex channel) are a blob: a numpy array, or nested lists with a declared dtype. Its hash is `h("array", "f" or "i", ndim, *shape, *words)` with one 64-bit word per element in row-major order: a float's binary64 bits (a float32 widened, minus zero as zero, NaN and infinities refused); an integer or boolean as its two's complement. Dtypes: `float64`, `float32`, `int8` to `int64`, `uint8` to `uint64`, `bool`.

In JSON a blob appears only as its summary, `{"$blob": {"dtype", "shape", "hash"}}`, and a blob hashes as that summary does. So a stage file's output hash can be recomputed from the file alone, with the full arrays kept out of git. The cache holds them whole as `.npy` files, which both Pythons write and read (numpy, or by hand where there is none).

## The chain

Each link is a hash of the link before it, what the stage read and what it wrote:

- **The head:** `{"schemaVersion": int, "rulesetVersion": hex, "worldSeed": hex}`, hashed.
  - `rulesetVersion` hashes `{"kind": the kind file without its prose (describes, frame), "parts": {path: version}}`. The parts are every part definition in the pack under a family one of the kind's slots admits, with the removal marks those parts name.
  - A container's rulesetVersion (`chunk-format.md`) is the hash of `{kind: rulesetVersion}` over the kinds it holds.
  - `worldSeed` is written as 16 hex digits, as `plan.schema.json` holds it.
- **A stage's key:** `{"stage": name, "after": the previous link (the head's hash for facts), "inputs": {...}}`, hashed. Its inputs are:
  - for facts, `"record"`: the record file's content hash, so layout and key order never count;
  - for each word in the stage's `reads`, either the run's input (`"date"`: the fabric's year, by value) or a pack table (`"table:<word>"`: the hash of `packs/<pack>/<word>.json`, or of every JSON file in the folder `packs/<pack>/<word>/` by path; `"absent"` when there is neither);
  - for bake, `"bakeVersion"`: the hash of `schemas/layers.json` and `schemas/maps.json` today. From step 3 it also covers the `OS_History` include, the layer curves' code, the bake and shell-bake code and the shaders.
- **A stage's link:** the key's three fields and `"output"`, the hash of the stage's output, hashed together.

A JSON file is hashed by its content; any other file by `h("text", its text)`.

The chain is content-addressed: a stage whose output comes out the same leaves the next stage's key unchanged, so the next stage is skipped. Any rule change moves the head and reruns every stage. A new date reruns the first stage that declares `date` among its reads, and the ones after it only as far as its output changes.

## The vectors

`python tools/hashes.py check` runs the vectors in `fixtures/golden/canon-vectors.json` in either Python. Each value's JSON text comes with its parts and its hash. Each blob comes with its words and its hash, and a chain with fixed outputs is written out link by link. `python tools/hashes.py write` rewrites them, and only a change to this page may do so, with a line in `CHANGELOG.md`.
