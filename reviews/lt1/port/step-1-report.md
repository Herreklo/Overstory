# The gully port, step 1: the contracts as files

Commit `0018d9b` on `lt/1-harbour-street`, pushed. Written by the step 1 agent (Opus 5.5), 22 October.

## Files (34)

- `schemas/`: `naming.md`, `record`, `slot`, `interval`, `kind`, `part`, `plan`, `world-state`, `change-query` and `chunk` `.schema.json`, `channels.json`, `maps.json`, `layers.json`, `chunk-format.md`, `CHANGELOG.md`.
- `kinds/house.json`, `fixtures/records/bld-104.json`.
- `packs/stavanger-1989/`: `pack.json` (years), `tooling.json` (Blender 5.2.2 with Python 3.13.13 and numpy 2.3.4, Unity 6000.6.6f1, venv Python 3.9.6; all checked on this machine), and five draft parts house 104 uses (`window/cross-arch`, `trim/casing`, `shopfront/shop-1930`, `coat/paint`, `mark/shopfront-line`).
- `tools/naming.py` (writes each schema's patterns from the grammar; `--render`, `--check`), `tools/validate_record.py`, `tools/migrate.py`, `migrations/001_schema_2.py`.
- `blender/resolver/face_class.py`: the plan's face-class function and texel rule. It reads `maps.json` and runs in both Pythons.
- `requirements.txt`, the venv's pins. In `docs/measuring.md`, only the recreate line changed.
- `fixtures/lt1-corner.json`, `lt1-street.json` and `lt1-town.json`: schemaVersion 1 to 2 by migration 001. That line only.

## Output

    naming.py --check            schema patterns match naming.md (54 rules)
    validate_record.py bld-104   ok fixtures/records/bld-104.json: 10 events, 4 slots, 13 fills
    validate_record.py --self-test   self-test: 25 of 25 breaks caught; the unbroken record passes
    migrate.py --check           12 files at schemaVersion 2

The self-test breaks the record 25 ways and expects each to fail. Among them: a person acting before 1959, generated-past dated 1959 or later, an event from 1989 on that is not `standIn`, an era breach, an overlap without `spans`, a fill under a spanning opening, a wrong face class, a care basis of character, a retired `engine`, and a slot deleted from a committed record.

## Decisions where the architecture left room

- **Ids:** 0b's id paths are adopted. A name is a slot, a count is a fill, a name after a fill is a slot held by that fill, and `#i` is a piece. Events count from 1, everything else from 0. Generations end in `-g<n>`. Groups hold slots, never fills. A family is a part path or its first segments, so a part's definition is the narrowest family.
- **Faces and slot boxes:**
  - Faces use the house's own frame: f, b, l, r.
  - A slot's box is the lower-left outer corner in its host's axes, with size width × height × depth (inward).
  - A surface region uses its face's axes.
- **Spans:** `spans` lets an opening take others' places, as the 1931 shopfront takes two windows. It must lie over them, and none of their fills may stand while it is open.
- **How fills end:**
  - Coats end `covered`.
  - Removals end `removed`, with a `removalMark` (null or a mark part).
  - `copyOf` lets 2016's copies pass the era check.
  - A fill may carry a `rule` instead of an event, for patchwork.
- **Face classes:**
  - Walls onto water or steps are street.
  - Walls onto earth are ground.
  - A mark's texel is half its smallest feature, and the coarser texel wins.
- **The shell bake:** its input is L2, decided at step 1. The atlas is drawn from L2 meshes and pages in `_OS_BAKE` mode, cached on disk by bake hash, dropped when the change query names a thing in the cell, and never shipped beyond the heart.
- **Small calls:**
  - Event kinds are hyphenated.
  - `pack.json` sets firstYear 1800.
  - World-state stores the time of day and derives the sun.
  - Part variants are optional.
- **Nothing stone-only in `kind.schema.json`.** The house kind exercises the schema. The house kind's `shadingOverFlatUs` (street 600) is a provisional guess, marked so.

## Contradictions and follow-ups

1. **0b's keys against the grammar.** `stone.py` keys setts as `<row>/<c>` and `wall.py` keys wall stones as `<course>/<j>`. By the grammar, a bare count after a slot is a fill. They become `<row>/0#<c>` and `<course>/sp-<j>` at step 2's re-baseline, with that step's migration. Until then, step 2 keeps 0b's keys. This is written in `CHANGELOG.md` and `naming.md`.
2. **Two writers still write schemaVersion 1.** They are `blender/tools/corner_fixture.py:260` and `grow_town.py:410`. A rewritten bundle fails `migrate.py --check` until `migrate.py` runs, and the writers should move to 2 when next changed.
3. **D3.1 against `docs/upkeep.md` on patchwork.** The fill's `rule` field holds patchwork without an event, and one of the two docs should be settled.
4. **`docs/building-blocks.md` is out of date.** It says Blender 4.x, where the machine has 5.2.2, and its example id `bld-101/op-n1-2` is in the old form.
5. **The bundles break the new rules, and convert at the house migration.** Their event kinds are snake_case, and lt1-corner holds proper names ("Vik Jernvare", "Kaffebrenneriet").
6. **The resolver and the record disagree on covered windows.** The resolver keeps them. The record removes them in 1931 and copies them in 2016.
7. **The 1931 keeper runs across S, the seam.** The validator allows a keeper who starts before S and keeps after it, but no person may act before S. Worth a line in the facts contract.

## The four unknowns

None shapes a schema field, so none was measured. Each is named in `maps.json` with the step where it is learned:
- **GPU encoder** (BC7/5/4/3 in the player, time per page): before step 5. Step 3's pages bake offline, and `encoder.player` holds "unknown-gpu-encoder" until it is chosen.
- **Place bake cost** against driving's 40 near chunks a second: a spike before step 5. It sets the rebake budget line.
- **Shell bake cost** against the city pan's 90 cells a second: before step 5, with the place bake's spike. If it fails, L2 as the input is reopened.
- **Cold read** (purge, then a district from container files on workers): before 3.4. It sets the page compression choice in `chunk-format.md`.
