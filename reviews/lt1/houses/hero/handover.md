**Paused 27 October (Øystein is reconsidering the style).** The second lead judged the hero houses in the painted corner (`painted/p00-*`): they hold at the street stop, but C's husmor windows read as flat stickers up close, and D reads as clean as C, because the painted surface draws no peel.
The two builders (`brief-common.md`: walls and openings; roof and eaves; four views every round) were stopped early: walls bb61098 (corner boards chamfered and proud, the drip board a chamfered section; built, never rendered), roofs 84c78b5 (counts by part, nothing built); their notes are `walls-handover.md` and `roofs-handover.md`.
Open: near budgets (the plinth was ~16k of C's and D's near count, pantiles and slates the rest); the painted scene draws the street tier at every distance (per-distance levels were asked of the coordinator, not done).

# The walked corner's elements: hand-over (27 October, 18:20)

The lead stopped here at about 80% context. The branch is `lt/1-harbour-street`, and the brief is `corner-elements-brief.md` in the parent's notes folder. Nothing below has been judged against the art-direction frame yet, and none of it is finished work for Øystein.

## Houses (the lead's own)

**Committed:**
- **63d613a, the roofs, as modelled parts.** Slates and pantiles are laid from their records (`packs/.../materials/*.json`, `laid`), with ridge tiles and chamfered barge boards.
  - C's open eave is the boarding on rafter tails, with a frieze; its gutter hangs on hooks, and the downpipe runs by a swan neck to a shoe at the ground.
  - Chimney aprons; ridge sag from age.
  - The window parts, and the craft note `craft.md`.
- **ee5bee5, the bake per piece** (`tools/houses.py`).
  - Each board, casing member or facet gets one even light, so no wall follows a triangle edge.
  - Level lips throw a band below them (timber.json `push.lipShade`).
  - Stills: `bake/`.

**Triangle counts (near / street):** C 45.2k / 8.0k, D 56.6k / 8.4k, E 40.6k / 6.6k.

**Next, in order:**
1. Push the cladding lap: its shadow line is 1 to 2 px at the street stop.
2. Corner boards and a frieze board, chamfered, on classical houses too.
3. Profiles for the rafter tails, and a chamfer on the fascia.
4. Doors and steps.
5. The plinth.
6. History as whole shapes.
7. A budget script.
8. Build into `cache/houses`, the folder the painted corner loads.
9. Painted stills.

**Open look faults:**
- **The walls are still flat in fog.** Each board is now one clean light, and the top courses darken under the eave. But the band under a sill is faint, so raise `lipShade.shade` or deepen the lap. The relief has to come from real depth.
- **C's west eave end** reads as a dark hole from the south-east (`bake/b02-...-c-wide`).
- **D's paint flakes** stand in ragged columns beside the boarded window. They should be whole peeled patches.
- **The plinth stone** looks blocky.
- **E** is too dark in sea fog; judge its form in drizzle or low sun.

**Painted stills wait.** Paint() is flat grey while the builder's PaintAir work is uncommitted (the art-direction session, 18:15).

## Trees: agent ad7b8d572a86601ab (alive)
**In flight, uncommitted:**
- `blender/parts/trees/corner.py`, `corner.json`, `mass_card.py`;
- `fixtures/lt1-corner-trees.json`;
- `LT1CornerTrees.cs`, `Corner/Elements/trees/`.

Its last steps were the shared C# (loader, materials, placement), a shader rework for FXC, and data-driven self-pruning.

The hook now skips renderers that bring their own shader (`"OverstoryPaint"="Own"` or `_PaintOwn = 1`), as it asked; I've relayed this to it.

**Next:** judge its stills, eye level and the street stop, in grey and one light, before accepting them. The Firewatch aspens are the lead reference.

## Growth: agent a02202beb7e4ea00b (alive)
- **Committed:** 16bf976, on_rock (lichen and moss from sky, foot, joints and years).
- **In flight:** `CornerGrowth.hlsl` filled in, a GrowthDraw MonoBehaviour, `blender/parts/growth/`, `growth.py`, `growth.json`, `fixtures/lt1-corner-growth.json`, and `reviews/lt1/growth/`.
- **Next:** judge its stills, the same way.

## Rock and ground: agent ac9170ed361a99884 (alive)
- **In flight, uncommitted:** the site extraction, `blender/generators/bedrock.py`, `fixtures/lt1-corner-ground.json`, `reviews/lt1/corner/base/`, `headings/`, and a check for water runs.
- **Next:** judge its stills, the same way.

## For the fresh lead
- **Agents.** All three report to the old session (af2437bc). Their commits land on the branch: judge them from there. Never accept a still unseen.
- **Commands.** The stills' commands are in the parent's notes folder, `houses-hero-handover.md`.
- **At the end:** one strict review of the whole corner on Fable (Opus if Fable is out, and the packet says so), then NOW's line and the report.
