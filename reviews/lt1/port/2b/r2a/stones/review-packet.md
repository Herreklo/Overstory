# R2a stones: review packet

For a strict reviewer who has seen nothing. The folder is `reviews/lt1/port/2b/r2a/stones/`. The contract is `plan.md`, and the full findings are in `report.md`.

## The question and "done"

R2a redrew three stones of the gully: a step, a wall stone and a coping. It asks three things:
- Do they hold SN7's restraint at 1, 5 and 12 m (a split face within about 2 L* in grey; edges drawn by light, never by a dark line) and SN8's budgets?
- Does L1 pass for L0 at 8, 10 or 12 m?
- Which split face does the wall stone want: patches as built, facets ×2 or minor ledges off?

"Done" means the checks and budgets pass, the sheets and numbers are in the folder, the A/B gives evidence for SN7's number, and this review passes. The bar is the reference board, not the street target.

## Look at these

The references are in `docs/references/stone/`: `05-aksla-old-split-stone-steps.jpg` and `10-bergen-dry-stone-wall-and-bedrock.jpg` for the faces, and `06-worn-stair-with-lichen-dale-vestland.jpg` for the stair.

1. `sheets/wallstone/material.png`, beside 10. Split stone, or tiles in dark mortar? Note the near-black joints.
2. `sheets/wallstone/grey.png`. At the sun stand, each stone has a light line on its right and a dark line on its left. The course below lines its facet steps up into one line.
3. `sheets/wallstone/levels.png`, the 8 m pair in sun and in drizzle. Do the joints narrow at the switch?
4. `sheets/wallstone/joints.png`. How much chamfer does the fill leave showing?
5. `sheets/wallstone/arms.png`. Can you tell as built, facets ×2 and minor off apart?
6. `sheets/step/levels.png`: the nosing at the sun stand, in grey.
7. `sheets/step/material.png`, beside 06.
8. `sheets/coping/material.png`: the blue top, the smudge at the left end, and the dark edge lines in sun.
9. `blender-sheet-wallstone.png`: the part alone, with its open band.

## Key numbers

- **Triangles,** L0 / L1 (budget): step 144 / 69 (300 / 120), wall stone 18 / 10 (40 / 16), coping 36 / 26 (120 / 48).
- **Thin at L0, 8 m:** 7.3% over the level, but steps 13.7% and copings 23.4%.
- **Open faces in context:** 0 px everywhere.
- **Switch p99 minus motion p99,** at 8 / 12 m:
  - wall stone in sun, +15.6 / +8.9 (alone, within +0.4);
  - step in sun, grey, +3.4 / +4.2;
  - coping, at most +2.1 / +1.3.
- **Visible joint at 1 m,** L0 to L1: 13.7–24.4 mm becomes 4.2–9.5 mm. The wall stone's chamfer is 1 px at 8 m in context (SN4 asks for 2).
- **Joint against face in material:** −28 in sun, −14 in drizzle, −11.4 in low-sun shade, −3.6 in blue hour. The face is 3.8 times the joint's luminance in sun and about 18 times in shade, against about 2.7 in the albedo.
- **The split face's spread,** grey, sun stand, 1 m: as built 1.68, facets ×2 3.01, minor off 1.68. Patch on against patch off: 1.35 against 1.35.

## Attack these

- "Grey joints within 2.2 L*": grey gives the fill and the stone one albedo, so this passes by construction.
- "Thin triangles pass": only over the level. The wall stones carry the steps and the copings.
- "The off-state is byte-identical": one frame, in one light.
- "Facets ×2 changes nothing visible": measured in grey only. Minor off may never have reached the shader.
- The switch rule: motion p99 is noisy (0.4 to 2.6 at one stand), and the 2 L* margin is chosen, not derived.
- Option 1's inset (about 4 mm at the top and bottom, 8 mm at the ends) is read off frames, not off the geometry.
- The step's pop at the sun stand: the builder said about 1 L*. That holds in material only.
- `tools/check.py` does not exist. Nothing claims it passed.
- The rigs' light (the orange sun, the blue shade, the near-black foot) may hide faults or invent them.

## The proposals

1. **SN7:** keep about 2 L* and the patches as built. The A/B cannot set the number, because what reads is form at block scale. The split patches draw under 1 L*, which is a question for R2b.
2. **The switch:**
   - one rule: switch p99 at most motion p99 + 2 L*, for every part, light and stand, in grey and in material;
   - the coping at 12 m;
   - the step at 8 m, once L1 keeps the nosing's facets;
   - the wall stone: L1's outline moved to where L0's stone meets the fill, after SN4 against SN5 is settled;
   - L1's 9 mm error replaced by the visible joint error (about 16 mm);
   - not 18 m.
3. **The soil:** into `packs/stavanger-1989/materials/soil.json`, named by walling's working. First find out why the ratio depends on the light, in a short Unity run: the `-albedo` view, then the fill's moss, wet, smoothness and occlusion off in turn. The JointFloor clamp is not the fix.
