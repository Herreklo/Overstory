# The Holm tip's rock, the street's way

Nature restarted on the street's recipe (29 October): the tip's rock made as a small kit of rigid parts, each made
with care, assembled by a generator from `fixtures/lt1-holm-tip.json`, with house 107 in every frame, in the street's
finish, light and cameras. The first lane's meshes are not used; its exposure rule, `WEAR` table, foliation and
zonation are (`../README.md`).

## Hand-over (kept current at each commit)

- **Where:** parts and generator here (`blender/parts/rock/kit/`), the scene `unity/Assets/Experiments/LT1/Nature/HolmTip.unity`
  built by `Nature/Editor/LT1HolmTip.cs`, renders in `cache/rock/kit/renders/<round>/`.
- **The pipeline is the street's, called unchanged:**
  - `part.py` builds a part's levels as `geom.to_object` builds a house's (uv0, page, Col, rest, piece; face-weighted
    normals), charts packed by `geom.Charts`, and writes `house-<level>.fbx` and a `house.json` with the fields the
    street's Unity code reads, so `LT1Street`'s import and materials take a rock unchanged. Budgets by surface, as
    `street.json`'s (a square metre of rock may cost what a square metre of house does), enforced at export.
  - `bake.py` bakes the page with the finish's bake (`finish/bake.py` helpers, as `street/bake.py` does).
  - `paint.py` writes the page's marks with p3's rules (`finish.json` `painted`, unchanged) and the digest.
  - `LT1HolmTip.cs` builds the scene and calls `LT1Street`'s import, materials, lights and capture by reflection.
- **Order:** 1 port one part beside 107 (look-in 1); 2 target frame (look-in 2); 3 the kit, 6–8 parts (look-in 3);
  4 assemble (look-in 4); 5 done sheet.
- **Run:** `Blender -b --factory-startup -P blender/parts/rock/kit/part.py -- --part <p> --out cache/rock/kit/gen/<p>`;
  then `bake.py` and `paint.py` with `-- --gen cache/rock/kit/gen/<p> --cache cache/rock/kit/bake/<p>`; then
  `python3 tools/unity_lock.py run -- bash blender/parts/rock/kit/run/render.sh <round>`; sheets by `blender/parts/rock/sheet.py`
  (`-- OUT.png COLS IMG...`), shrunk with `sips -Z 2560` into `reviews/lt1/rock/<round>/`.
- **The house** is the street's current 107 (kit.json `beside`: `gen`, `paint`), checked by md5 against
  `Street/Generated/107`; when the street rebuilds 107, update both. k01 took a stale pair (page painted before the mesh
  was rebuilt): streaked roof and reveals, no boards.
- **Grey-box and plan:** `tip.py` builds `blockin.py`'s masses with 107 where the customs house stands, in 107's
  frame (`-- --out cache/rock/kit/gen/tip`); `TIP_GREY=1 render.sh <round> street P` draws them in Unity from the street
  stop; `tip.py -- --plan <grey still> --to <png>` lays the form plan (kit.json `tip.plan`) over that still.
- **State (29 Oct, end of this session):** the coordinator's verdict on t01: the wear plan passes and the frame
  fails. Don't build the slab block yet. Next, in grey only, in this order:
  1. **A frame for the rock's spectacle.** Low, from the water or the skerry, looking back at the tip: the
     whalebacks, the plucked lee and the storm-wash, with 107 small on top. Put the Bluff's 20 m face behind it if
     the layout allows (`docs/town-plan.md` section 5); otherwise the tip's own biggest forms carry the frame. Keep
     the street stop as the second still, to check 107 still holds there. The views live in `LT1HolmTip.cs` (the
     street stop from `LT1Street.Views`, `eye` from kit.json `beside.eye`); a new view belongs in kit.json as data.
  2. **Hierarchy in the masses.** Today they are many slabs of about the same size: flat planes, straight edges,
     the same tilt, a steady rhythm. That reads as paving ("looks like it's been built"). Aim for one or two big
     whalebacks that dominate, a few middle ones and many small ones, with wavy outlines and backs rounded where
     the ice planed them. Keep the fixture's footprint and heights (`fixtures/lt1-holm-tip.json` `outcrop`) and
     change how `blockin.py` and `outcrop.py` (`build`: blocks by the joint families' spacing under the landform's
     envelope) divide and shape them. If the fixture itself forces equal slabs, tell the coordinator.
  3. **The plinth.** A grey-box of dry stone that steps down with the rock and sits lower on the high side, in place
     of the 2 m box (`tip.py`, `stand-plinth`).
  4. **Judge** at 25% size beside t01 and beside the Jæren and stone study references 53-56, by squinting: two
     or three values and a few big shapes should read at once. Then Look-in 2 again.
  Then the slab block for that frame's foreground, against the plan. Treads vary in width (1.6-3.6 m) and risers
  wander in plan, never parallel rulings: the plan's 0.6 m lines read as decking, k02's board grain again.
  Build it with a handful of leaves and ledges 0.1-0.6 m with wavy outlines, plucked back in steps on the lee, an
  ice-planed top and rounds by exposure. Put the cm laminae in the bake at the near level only. Give the rock its
  own marks (short, broken, along the foliation's trace) and banded colour, grey-green to graphite with rust,
  through its own material and data; ask the coordinator with the diff before touching the Finish shader. Page 512.
  The eye camera frames it from the front with its foot in view, and 107 stays at the street's own camera.

## Rounds

- **t01** (`reviews/lt1/rock/t01/`; top: the grey-box from the street stop, overcast and low sun; bottom: the form plan
  over each). Bad: the frame sees the lee and the shore, not the whalebacks, which lie behind 107; the plinth under 107
  is a 2 m grey box where the fixture has dry stone; the plan is zones and lines on the block-in's blocks, not a
  painting (a paintover cannot paint forms onto boxes, visual-direction VD5). Good: where each wear falls and how big
  is now on the frame, from the facts: the plucked lee in front (treads 1.6-3.6 m, risers 0.45-0.9 m), the storm-wash
  along the shore and the skerry, the joints and foliation faces at the sides. Verdict: the plan passes; the frame
  fails (no spectacle, the whalebacks hidden, the block-in reads as paving).

- **k02** (`reviews/lt1/rock/k02/`; rows eye overcast, eye low sun, street overcast, street low sun; columns floor P,
  rock P, floor Pc, rock Pc). Bad: the block reads as made, not grown: four plates of flat faces with rounded rims, a cast
  slab or a gravestone, the tiles Øystein named; no lamination inside a face, no ledges, no break. Bad: the eye frame cuts
  its foot (`eye.from` must stand off the part's front, not its middle); its page costs 0.26 MB/m² to 107's 0.08.
  Good: 107 is the street's again, and the rock takes the street's pipeline, light and finish unchanged.
  Cost: 107 near 24590 tris / 11 draws, street 5459 / 11, city 705 / 1, 12 materials, page 21.3 MB; slab-block near
  1263 / 1, street 360 / 1, city 14 / 1, 1 material, page 5.3 MB (1024 BC7 ×4); strokes 1.3 MB shared.
