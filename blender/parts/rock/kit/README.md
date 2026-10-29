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
- **Grey-box views:** kit.json `tip.views` holds the target frame's own views in site metres (`water`: 0.8 m over
  the sea, 3 m off the north-west shore); `tip.grey` holds the frame's values and the shore bands; `tip.py` moves them into 107's frame in `tip.json` with the site's own low
  sun (`sunOff`), and `LT1HolmTip.cs` adds them beside the street stop. Run:
  `TIP_GREY=1 render.sh <round> water,street P overcast,lowsun`.
- **State (29 Oct, t03):** the whole Holm tip is one grey frame of simple masses (the coordinator's scope): the sea,
  the shore bands by exposure (wet and black band, storm-wash to the storm top, `kit.json` `tip.grey`; the Roads'
  fetch only, decided from the map and recorded there), turf caps in the lee's sheltered hollows, 107 and its plinth,
  the office past the frame. The shore blocks now end in a lip at the sea (`outcrop.py` `lip`), their joint sides
  stand steep (`crossShare`) and their treads step down where the joints opened (`shoreTilt`). The camera is chosen
  (t03 below). Next, unless the coordinator says otherwise: the slab block for the frame's foreground, which must
  fill the lower right third the grey masses leave as open water. Its s10 design is in `kit.json` `parts.slab-block`
  and `part.py` (leaves joined with a LAP overlap); it stood too close to 107 in s01, and its page is 5.3 MB against
  512 because its charts are each leaf face's bounding rectangle. Treads 1.6-3.6 m, risers wandering in plan, never
  parallel rulings; leaves and ledges 0.1-0.6 m, plucked back in steps on the lee, an ice-planed top, rounds by
  exposure; the cm laminae in the bake at the near level only; its own marks and banded colour through its own
  material and data (ask the coordinator with the diff before touching the Finish shader).

## Rounds

- **t03** (`reviews/lt1/rock/t03/`; `sheet.jpg` rows water, street stop, columns overcast, low sun; `squint.jpg` at
  25%: t02 water, t03 water overcast and low sun, t03 street stop, over refs 53-56). Bad: the near rock fills a
  quarter of the frame, not a third, and the lower 40% is open sea; the shore blocks read as smooth slabs with sharp
  prows where a lip plane cuts a tread obliquely; the lee plates from the street stop keep straight edges; the
  skerry is harder (power 3) but still smooth. Good: three values at 25% (the sea darker than the sky, the wet lips
  dark, the tops lightest), one subject (107 on the skyline atop the big back, the back rising to it on the
  diagonal), depth in layers (near blocks, the back, the far shore), every block meets the sea at a lip, and the
  office is out of the frame. Camera chosen by squint from three low candidates (north, north-west, north point);
  the north-west one shows the shore's steps in profile. 234 blocks, 17114 tris.

- **t02** (`reviews/lt1/rock/t02/`; `sheet.jpg` rows water, street stop, columns overcast, low sun; `squint.jpg` at 25%:
  t01 street, t02 street, t02 water low sun and overcast over refs 53-56). Bad: the near blocks in the water frame
  read as cushions or loaves: same-sized, rounded on every side to the waterline, their joints cracks in a crust, no
  storm-wash steps or lip at the sea; the frame is low and level, all mid-grey, and the harbour office's stand-in box
  takes the eye from 107 (on the west shoulder it is nearer from every western bearing; the Bluff stands too far round
  to share the frame without making the tip small). Bad: from the street stop the lee in front of 107 still reads as
  straight plates, and the skerry as a melted shell. Good: one big ice-planed back carries 107, with middle backs on
  the flanks and small ones at the shore, and it reads at 25%; the dry-stone plinth takes up the slope (107 0.3-1.5 m
  over the rock, the office 0.6-2.2) in place of the 2 m box. 277 blocks, 15832 tris.

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
