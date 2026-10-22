# Contracts changelog

Every change to the files in `schemas/` with its migration. The contracts' version is `schemaVersion`, carried by every record, kind, pack file and fixture. `tools/migrate.py` runs `migrations/NNN_<name>.py` in order on every file behind; `tools/migrate.py --check` fails while any is behind. `tools/validate_record.py` checks records, kinds, parts and the registries against the current version.

## 2, unchanged: the hash chain and the stage contract (22 October, the gully port's step 2 groundwork)

No migration: no field changed, and no record, kind or part needs rewriting.

New:
- `hashing.md`: the canonical encoding a C# twin reproduces (sorted keys, integers as decimal text, floats by their binary64 bits, strings as UTF-8), the blob hash for bulk numbers and the chain's links and cache keys. `tools/hashes.py` implements it; its vectors are `fixtures/golden/canon-vectors.json`.
- `stages.md`: the stage contract, run by `tools/run_kind.py`. It covers the entry and its context, outputs, the cache, stage files, the golden fixtures in `fixtures/golden/<kind>/<stage>.json` and `tools/diff_stage.py`.

Changed:
- `kind.schema.json`: a stage's `reads` also admits the run's input `date`, besides the pack's tables. Only the description changed.
- `kinds/house.json`: facts is live through the shared `tools/stages/record.py:facts`. Checks moves from `tools/validate_record.py:validate`, whose signature never fit a stage, to `tools/stages/record.py:checks`.

## 2: the contracts as files (22 October, the gully port's step 1)

Migration: `migrations/001_schema_2.py`. The provenance word `engine` is retired for `simulated`; every file's `schemaVersion` goes from 1 to 2. Today's bundles (`fixtures/lt1-corner.json`, `lt1-street.json`, `lt1-town.json`) held no `engine`, so only their version changed. They stay bundles; each kind's port turns its part of them into records, with that port's migration.

New:
- `naming.md`, the grammar every id and name follows, read by `tools/naming.py`, which writes each schema's patterns.
- `record.schema.json`, `slot.schema.json`, `interval.schema.json`, `kind.schema.json`, `part.schema.json`, `plan.schema.json`, `world-state.schema.json`, `change-query.schema.json`, `chunk.schema.json`.
- `channels.json`, `maps.json` (with the face classes, the texel rule, each map's format and encoder, the shell bake's input and the four unknowns), `layers.json`.
- `chunk-format.md`, the container and its units, reserved: no writer or reader until step 5.
- `kinds/house.json` and `fixtures/records/bld-104.json`: a second kind on paper, validated and not built. `packs/stavanger-1989/` with its years (`pack.json`), its tools (`tooling.json`) and the five draft parts house 104 uses.

Pending, for step 2's re-baseline: `stone.py` keys a sett row's setts as `<row>/<c>` and `wall.py` a wall course's stones as `<course>/<j>`. By the grammar a bare count after a slot is a fill, so these become `<row>/0#<c>` (the setts as pieces of the row's fill) and `<course>/sp-<j>`. Both re-seed only what they name; step 2 keeps the generators' keys until its deliberate re-baseline, and that step's migration renames them in any record that holds them.

Also pending: `blender/tools/corner_fixture.py` and `grow_town.py` still write `schemaVersion` 1. A bundle written again comes out behind, `migrate.py --check` fails on it, and `migrate.py` brings it up. The writers move to 2 when next changed.
