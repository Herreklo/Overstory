---
name: blender-generators
description: Use when making any 3D asset in Blender through the Blender MCP: kit pieces, buildings, props, furniture, base bodies or clothing. Covers generator scripts, units, pivots, naming, UVs, validation, export to Unity and contact sheets.
---

# Building assets in Blender

## The rule: generators, not assets

Never model one object by hand. Write a Python generator (`bpy`, or geometry nodes driven from Python) that makes a family of variants from parameters. One generator can be changed in one place; two hundred hand-made objects cannot.

- Generators live in the game repo under `blender/generators/<family>.py`, one file per family (`shopfront.py`, `roof.py`, `chair.py`).
- Each generator has a parameter block at the top, with sensible ranges, and a `build(params, seed)` function.
- Randomness comes only from the `seed` argument (`random.Random(seed)`), never from global state, so a variant can always be rebuilt.
- Run generators through the Blender MCP's code tool. Keep each call small: build, check, then the next step.

## Units and grid

- Metres, Blender's default. Z is up in Blender; the export handles Unity's Y up.
- One grid module is 1 m wide. One storey is 3 m. Kit pieces snap to whole modules so any piece fits next to any other.
- These numbers are provisional until the art bible fixes them. If the art bible exists, it wins.

## Pivots and naming

- Pivot at the bottom centre of the piece's footprint, on the grid. Doors, windows and trims pivot at the bottom left of the opening they fill.
- Apply all transforms before export (location for kit pieces, rotation and scale always).
- Name: `kit_<family>_<variant>_<lod>`, all lower case: `kit_shopfront_1930s-a_lod0`. LOD0 is the scene-view version, LOD1 the world-view version.

## Materials and UVs

- Colour comes from one shared palette texture. UV each face onto a swatch of the palette instead of making a material per colour. This keeps thousands of buildings on one material.
- Wear, dirt and age are separate texture layers or vertex colours, set by Unity from engine facts, not baked into the mesh.
- No image textures per object unless the art bible asks for them.

## Validation (run after every generator change)

A validation script in `blender/validate.py` checks every exported piece:

- name follows the pattern;
- dimensions are whole grid modules (within 1 mm);
- pivot is where the rules say;
- triangle count is under the family's budget (set in the art bible; provisional: 2,000 for LOD0 kit pieces, 300 for LOD1);
- no unapplied scale or rotation, no loose vertices, normals facing out.

Report failures; do not export a failing piece.

## Export to Unity

- Export FBX to `Assets/Art/Kit/<family>/` in the Unity project: apply transforms, forward −Z, up Y, scale 1.0, no animation for static pieces.
- One file per piece, named like the object.

## Contact sheets

After a generator run, render every variant with the same orthographic three-quarter camera and neutral light, and tile them into one image (`reviews/<experiment>/<family>-blender.png`) for a quick check. This is a check that the generator works, not a judgement of beauty: beauty is judged in Unity, with the real shading and light.

## Honest limits

Good at: parametric, architectural and hard-surface shapes, consistent families, batch work. Weak at: organic sculpting, faces, hands, hand-painted texture, animation. For those, say so and suggest a bought or commissioned base.
