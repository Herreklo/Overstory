---
name: blender-generators
description: Use when making any part or generator in Blender, by script or through the Blender MCP: fixed and fitted parts, kinds as data, stone, buildings, trees, props, base bodies or clothing. Covers part code, seeds, units and metrics, pivots, the vertex layout and history maps, levels, export, checks and contact sheets.
---

# Building parts in Blender

A summary of `docs/building-blocks.md`, which holds the detail and wins where they differ.

## The rule: parts made with care, assembled by generators

Parts are Python generators, not hand-modelled `.blend` files: a part is its code in `blender/parts/<family>/`. Each is built a step at a time, looked at from the judging camera against its reference board, and corrected.
- **A fixed part** is a judged mesh, made in Blender (a sett, a slab, a lamp).
- **A fitted part** is a judged function whose inputs are facts (a tread fitted to its flight, a course to its ground). It is judged on a sheet across its inputs.
- **A stone is rigid** (BB3 in `docs/building-blocks.md`). A fitted course chooses and cuts its stones, then places each by moving and turning it. Never bend, shear or stretch a rigid piece's mesh to make it fit: no per-vertex height from a curve, no `z += x * k`. Only parts that really flex deform, from their rest position.
- The generator chooses, fits and places them, and invents no geometry outside a judged part or function.
- **A part asks for properties, never a member** (`docs/taxonomy.md`, TX4): a step takes a stone that breaks in slabs and names its finish, and the record names the phyllite. A new member then works in every part that asks for what it has. There are no good and bad versions of a part: the maker's skill, the means and the era are inputs, mostly to how the generator places pieces.
- Each family has a definition (`schemas/part.schema.json`): `made_as`, era, sizes, fits, pivot, sockets, removal mark, levels, roles, lifecycle.
- A part joins the corner only after its sheet, checks, a fresh reviewer and Øystein's judgement.
- **Repetition:** libraries only for what was mass-produced (bricks, roof tiles, factory windows and doors, catalogue houses, setts), each varied by placement, wear and history. Everything made by hand for one place is its own.

## Kinds and stages

A kind is data in `kinds/<kind>.json` at the repo root (`schemas/kind.schema.json`), run by one runner through seven stages, each with a hashed output: facts, plan, life, geometry, bake, export and cache, checks.
- Facts come from fixture records, never from code: no `FLIGHTS` dicts, no hard-coded `YEAR`.
- Python is the source until a kind is ported to C#, then the frozen parity reference. Golden fixtures per stage: `fixtures/golden/<kind>/<stage>.json`.
- Today `stone.py` and `wall.py` are one monolith each; the gully port's step 2 splits them into `kinds/stair.json` and `kinds/wall.json`.

## Seeds

The same building looks the same until its history changes it.
- Seeds come from stable ids (part path and purpose) through SplitMix64, by `blender/resolver/hashing.py`, the one hash spec that `Hash.cs` matches. Never `random.Random`, and never keys from formatted floats. A replaced part takes a new id and a new seed.
- Choices use only integers, the four operations and square root. A transcendental may place a vertex, never choose.
- Everything sorts by stable id.
- The gully's stone, walls and upkeep draw every seed through `blender/resolver/hashing.py` (`HS.Stream(seed, id, purpose)`, `HS.h`), keyed by the ids in `schemas/naming.md`. `house.py`, the trees, `stair_facts.py`, the clay and the grain painters still use `random` or numpy's generator: debts in `docs/systems.md` (Seeds).

## Units and metrics

- Plans are integer millimetres; life is per mille, years and months. Blender works in metres, Z up; the export turns it to Unity's Y up.
- Sizes come from the pack's metrics table (`packs/<pack>/metrics.json`: storeys, openings, rises, kerbs, thicknesses, grid, by era), never a fixed grid or storey. Era values live in `packs/<pack>/eras.json`.

## Pivots and names

- The pivot is at the part's true base, where it bears on what holds it; at its hinge for hinged and swinging parts. Apply rotation and scale.
- Names follow `schemas/naming.md`: record, slot and fill ids are stable (`st-gully/tr-17/2`); pieces (`<fill>#<i>`) exist only at the geometry stage.

## What a part carries

- **The vertex layout** is `schemas/channels.json` (grain, atlas address, mark coordinate, piece index, face kind and the like). Per vertex sit only piece constants and what moves geometry (a hollow's rate).
- **History lives in maps, not vertices.** The place and history pages hold inputs (rates, reset years, age offsets); the shader evaluates them at the date. Intrinsic channels (face kind, edge distance, own occlusion) are in the mesh; extrinsic ones (years, feet, water, damp, care) come per instance, field or map. Today the stone carries history in six UV channels; the port's step 3 moves it.
- Nothing is rolled that the record lacks: anything that reads as history is a fact.
- Materials are records in `packs/<pack>/materials/`, not Blender materials. The buildings' palette swatches are the test-quality path.
- Each element has a motion class and a collision role. The export carries breaklines, joints, affordances and sockets.

## Levels

- Five levels, L0 to L4, each with its error in mm and its budget in the part file.
- Fitted parts make their own levels in the generator from the same seed and outline. Natural stone and land use meshoptimizer. Decimate only for offline library parts that pass the A/B.
- Each level is at most 60 % of the one before, with a median visible triangle of ten pixels or more.

## Export

- **Library parts** go out as FBX plus a JSON sidecar naming each UV set's channel: transforms applied, forward −Z, up Y, scale 1.
- **Chunks are never FBX:** fitted geometry becomes a binary chunk (`schemas/chunk-format.md`) in `cache/chunks/`, built in the player once the kind is ported.
- **Generated meshes stay out of git,** rebuilt from their generators; the hash manifest stays. Never add a new generated FBX.

## Checks (after every generator change)

- Records (`tools/validate_record.py`), ids, plan validity, budgets per level; refused fits are never silent.
- The kit validator per family (buildings: `blender/generators/validate.py` and `blender/tools/stress.py`).
- Mesh hashes on every export, golden views with FLIP, motion sheets with their shimmer index (`docs/measuring.md`).
- A failure is fixed at its cause in the rules, never hidden with a special case.

## Contact sheets

A quick sheet in Blender checks that a generator works; it judges nothing. Judged frames are rendered in Unity at the player's size, one sample a pixel, never supersampled: grey light first, then three lights, with motion sheets for anything that moves or carries fine marks. Sheets go in `reviews/<experiment>/`.

## Honest limits

Good at parametric, architectural and hard-surface shapes, stone and plants by rule, batch work. Weak at organic sculpting, faces, hands, hand-painted texture, animation: say so and suggest a free or open base. No commissions and no Houdini: its free version forbids commercial use, and there is no money for Indie; free and open bases only (Øystein, 21 October).
