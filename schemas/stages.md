# Stages

The contract between a kind's stages and the one runner, `tools/run_kind.py` (`docs/building-blocks.md`, The stage map). A kind file names, for each of the seven stages (facts, plan, life, geometry, bake, export, checks), its status, its Python entry (`file.py:function`, from the repo's root), its C# entry, the words it reads and its params (`kind.schema.json`). The runner reads that and nothing else about the kind: it never branches on a kind's name.

## Running

    .venv/bin/python tools/run_kind.py <record.json> [--world-seed N] [--date YEAR] [--until STAGE]
    /Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13 tools/run_kind.py <record.json>   (numpy)
    /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python tools/run_kind.py -- <record.json>   (bpy)

The runner runs in whichever Python starts it. A stage that needs numpy or bpy says so when it cannot import it. The kind file is validated against `kind.schema.json` first, in-process where jsonschema is and by the venv's Python where it is not (`--validate-kind`). The world seed is the pack's `worldSeed`, or `--world-seed` when the pack has none. The date is `--date`, or the pack's `showYear`.

Stages run in order. A `live` or `frozen` stage runs from its Python entry. The run stops at the first `planned` or `ported` stage, or at one with no Python entry, since every later stage reads the ones before it. A stage that raises fails the run, and nothing of it is cached. An output holding `"pass": false` is cached and then fails the run, as a checks stage does.

## The entry and its context

An entry is `def stage(ctx) -> dict`. Its file is imported by its module name with its folder first on `sys.path`, so its sibling imports work. Two entry files with one module name are refused rather than loaded twice. The context gives:

| Field | What |
| --- | --- |
| `stage`, `kind`, `params` | its stage's name, the kind file, its stage's params |
| `record_path`, `source` | the record file and the record as read (facts turns it into the record) |
| `record` | the facts stage's output |
| `outputs` | every earlier stage's output, by stage, with blobs whole |
| `world_seed`, `pack`, `pack_dir`, `root` | the world seed (an int), the pack's `pack.json`, its folder, the repo |
| `date` | the fabric's year, only for a stage that reads `date` |
| `table(word)` | a pack table the stage reads: `packs/<pack>/<word>.json`, or the folder `packs/<pack>/<word>/` as `{path: definition}`; `None` when absent |
| `inputs` | the stage's inputs as hashed into its key |
| `work` | a folder of its own in the cache, one per key, for files it writes |
| `wrote(path)` | names a file it wrote outside the cache: its cache entry holds only while that file is unchanged |
| `depends(path)` | names a file its output rests on that no input or import shows (a schema, a JSON table read directly) |
| `log(text)` | a line for the run's report, never hashed |

Reading the date or a table a stage has not declared raises, so a stage cannot depend on what its key does not hold.

## Outputs

An output is a dict of JSON's types, with blobs (`tools/hashes.py`'s `Blob`) for bulk numbers anywhere in it. numpy values are turned into the Python values they hold, and tuples into lists. NaN, infinities and non-string keys are refused, naming where they are. `"$blob"` is a reserved key. The output's hash is its canonical hash (`hashing.md`). What each stage outputs is the kind's to say, with these rules, so diffs and checks can read any kind:

- **Things are keyed by their stable ids:** a dict keyed by record, slot, fill or piece id, or a list of dicts each carrying one in `id`, `fill`, `piece`, `slot` or `event`. Lists are sorted by id; order is hashed.
- **Facts** outputs the record itself, so its output hash is the record hash. The shared entry is `tools/stages/record.py:facts`: it validates the record with `tools/validate_record.py` and returns it.
- **Plan and life** choose, so they hold integers, words and booleans only once a kind's plan is in integers (decisions D2.2). Until then the shared checks count their floats.
- **Geometry and bake** output blobs (the meshes, the channels) with per-piece summaries keyed by piece id, `{"fill", "chunk", "hash", counts...}`, and per-fill and per-chunk summaries made from them (`hashes.summarise_pieces`). A piece's hash is the array hash of its own rows. Chunks are named by `naming.md`'s units (`hashes.chunk_of`).
- **Export** writes its files into `work` (or names them with `wrote`) and outputs their hashes and counts.
- **Checks** outputs `{"pass", "problems", ...}`. The shared entry, `tools/stages/record.py:checks`, checks every id in every earlier output against `naming.md` and counts the floats in facts, plan and life. A kind adds its own checks in an entry of its own.

## The cache

The cache lives in `cache/stages/<record>/<stage>/<key>/` and is kept out of git. Each entry holds the output (`output.json`), its blobs (`blobs/<hash>.npy`) and `meta.json`.

- **The key** is the stage's chain key (`hashing.md`).
- **The entry holds** only while every code and data file it rests on hashes as it did. Those are the runner and the hash spec, the entry's file, every repo module loaded when it ran (the venv's excepted), and what it named with `depends`. Every file it named with `wrote` must also keep its size and time.
- **Kept:** the three latest entries per record and stage, so going back to an earlier date is still a skip. Entries are written atomically.
- **Options:** `--rerun STAGE` (or `all`) runs a stage despite a valid entry; `--no-cache` neither reads nor writes.

A run's stage files go to `cache/runs/<record>/` (or `--out`), with `run.json`: what ran, what was skipped, the keys and the times. These are machine-local, so they stay out of the stage files.

## Stage files and golden fixtures

A stage file is `{"what", "schemaVersion", "record", "kind", "stage", "chain": {"after", "inputs", "output", "link"}, "output"}`, written with sorted keys. The facts file's chain also holds the head. The output is written in full, except that blobs appear as their summaries. Geometry and bake therefore keep counts and hashes per piece, fill and chunk, and the meshes stay out of git.

The golden fixtures are stage files at `fixtures/golden/<kind>/<stage>.json`, written by `--golden` and compared by `--check`. One record per kind is the golden one. Today that is `fixtures/golden/house/facts.json`, house 104's facts at world seed 1. The probe's goldens live with its tests (`tools/tests/probe/golden/`), so they never move when the town's pack does.

## Diffs

`tools/diff_stage.py <run A> <run B>` (two folders of stage files, or two files) names the first stage whose output differs. It then gives each difference as `<stage> <id> <field>: a -> b`. The id is the nearest record, event, slot, fill or piece id above the difference, matched by the grammar, and the field is the path below it. Things are matched by id wherever there is one: dicts by their id keys, lists by their id field. `--tol` compares floats within a tolerance, for comparing across languages (decisions D2.3). A stage whose output is the same but whose chain moved is named as such.

## Tests

`tools/tests/test_stages.py`, in both Pythons, against the same golden files. It runs a synthetic kind, `probe`, through all seven stages without Blender (`tools/tests/probe/`: its kind, record, pack and stages), and house 104 through facts. It checks:
- the vectors, numpy against lists, `.npy` both ways;
- skipping on a second run, a new date rerunning from life, a layout-only record edit skipping;
- a record, param or code change rerunning, a deleted export rerunning export alone;
- undeclared reads failing, a planned stage stopping the run;
- diff_stage naming the fill and field.
