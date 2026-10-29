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
- **State (29 Oct, t09):** the shore block as the ice made it, `whaleback.py` (kit.json `whaleback`; out
  `cache/rock/kit/gen/carve/W.blend`, `-- --bake 1` adds `W-game` and its 2048 maps; shown by `tip.py -- --lone 1
  --show W-high|W-game`). One heightfield hull in the ice's frame, its crest at the record's back (2.9 m), cut by
  exact plane booleans in two passes, every size drawn from a skewed spread (kit.json [mean, shape, least, most], a
  gamma: a few big, many small):
  - the back's sheets (thickness's mean the fixture's foliation spacing), parted along the strike by J1 joints at the
    fixture's spacing, none thicker than the fixture's most; each edge offset across every joint (`jogM`) and ending
    at one `end` of the time (a tenth: where one ends, two sheets share one tread, a big flat face); in each sheet
    between two joints one planar tread fitted under the hull above the wet line, rising toward the dip by its own
    `rise`; bites of skewed size plucked from the edges between J1 joints;
  - the plucked lee in J2, foliation and J3 strips, each step's rise and width skewed and its tread its own dip;
  - one J1 and one J2 crack, 4-10 cm wide, their lips chipped by small wedges.
  Crumbs a cut leaves are dropped. Grey check: Eevee, one neutral sun (az 330, el 35) and one raking (az 255, el 7),
  the lone views and a lee view 7 m off at bearing 215. Still wrong: the land flank keeps the hull's smooth round
  under the wet line (faceting it crumpled it, t07 x4); every face is an exact plane, so up close it reads as
  low-poly crystal, not rock (t06-t09 alike). t10 (rung 1, not in Unity) laid `rock_face_01`'s relief on the cut
  faces: the crystal is gone up close, but from 12 m the plates' grid is the patchwork, and the relief is one even
  crinkle. The prototype (`wdetail2.py`, scan windows from `scanras.py` and `scanpatch.py`) is in the coordinator's
  notes folder, `rock-t10-tools/`, until it holds. t11 (scan windows cut to t09's faces) and t12 (a few whole scans, sunk and overlapping over t09 as a core) both failed at rung 1 (Rounds); the method goes to Øystein. Prototypes in the coordinator's notes folder, `rock-t11/` (`kb.py`, `kb3.py`) and `rock-t12/` (`kf.py`, the fit). After the method is settled: the land
  flank; the game mesh as a coarse hull cut on the same planes. Turf test C, the toe line and the storm fixes queued.

## Rounds

- **t12** (`reviews/lt1/rock/t12/grey.jpg`, Blender grey; rows: neutral, raking, the core blue and every scan's back
  red, t09; columns eye, 12 m, sea, lee; then ref 16 and t05's coast_rocks_05). Rung 1 only, FAIL. Whole scans, rigid,
  sunk and overlapping over t09 remeshed and pushed in 0.5 m as a core, nothing clipped: coast_rocks_05 (no layering
  to read, kept upright and tilted to its place), mountainside in four 5 m regions and rock_face_01 with their
  layering on our foliation, scale within 15%, placed by a fit (`kf.py`, 37 s) for cover, the silhouette, buried rims,
  the crest and no repeat. Five pieces: 42% of t09's surface above the sea still bare (the core shows on the back and
  the land flank), a quarter of the rim points in the air, backs showing at the crest; from the sea one sharp alpine
  peak, not the whaleback. With the rims weighted fully, the fit sinks the pieces under the sea (80% bare): these
  scans, a concave 10 m cliff shell and a 4 m low outcrop with its skirt, can't wrap a convex 14 m dome inside its
  silhouette with their edges buried. Where the scans show, rock up close, but mountainside's crags, not ice-worn
  phyllite.

- **t11** (`reviews/lt1/rock/t11/grey.jpg`, Blender grey; top: eye, 12 m, sea neutral, then 12 m with the backing blue;
  bottom: eye, 12 m, sea raking, then ref 16). Rung 1 only, FAIL. Kitbash: each planar face of t09's cut form above
  the sea took one window of a scan (rock_face_01's slabs on the treads, mountainside's plates on the steep faces),
  turned rigidly onto it (Kabsch: the window's mean normal to the face, the scan's layering to our foliation or, on the
  treads, its strike to the foliation's trace), its tenth percentile on the plane, cut by bisect on its neighbours'
  planes so every rim lies on a joint; faces too big for a scan parted on a minor J1, J2 or J3 joint. 60 pieces. The
  pieces cover only about a third of the backing (measured: 62% of the cut faces bare, 7% with a piece sunk under
  them): each neighbour's plane, extended, shaved off most of a window's relief, so the cut form's planes still show,
  with ragged scan islands on them. A first
  try with solidified windows and an exact boolean left only fragments. Not rock beside ref 16.

- **t10** (`reviews/lt1/rock/t10/grey.jpg`, Blender grey; top row eye level: t10 neutral, t10 raking, t09 neutral,
  t09 raking; bottom: t10 and t09 from 12 m, refs 16 and 15). Rung 1 only. The research: unique form plus a scan
  detail layer in the rock's own frame (DICE's Battlefront rocks), box projection with one axis per planar face,
  displacement inward along the face's flat normal on the high mesh (averaged normals round arrises), chips as
  planar cuts, relief 1-3 cm. Built: each cut face re-gridded at 1.5 cm with its arrises exact, then pushed inward
  by one continuous field of `rock_face_01` windows (0.8 m, true scale, high-passed at 8 cm) laid in the foliation's
  frame; an arris takes its deepest face, so no arris rounds and no plane rises (depth p50 0.5 cm, p99 2.5 cm; 233
  open edges left). A first version with a random window per face (d1) Øystein called "very patchworky - and not
  very rocky". With the continuous field, eye level reads as stone, not crystal, and the arrises hold. But from
  12 m the plates' grid of full-length straight grooves is still the patchwork, where ref 16's fractures are short,
  staggered and dying out. The relief is one even crinkle everywhere, neither ref 16's foliation ridges nor ref
  15's granular pitting. Not taken to Unity.

- **t09** (`reviews/lt1/rock/t09/`; `grey.jpg` Blender grey, rows t09 neutral, t09 raking, t08 neutral, columns
  eye, 12 m, sea, lee, refs 16, 15, 48, 51; `sheet.jpg` columns t09 W high, t08 W high, t07 W high; rows eye, 12 m,
  sea, each overcast then low sun). One change: an edge ends at a joint a tenth of the time, not a third, and no
  sheet is thicker than the fixture's 1.8 m (was 3.0). At eye level the big triangular face is gone and the back reads
  sheeted, edges and joints crossing; from the sea broken, the crest broader and at 2.76 m nearer the record (t08
  2.52). From 12 m a loose grid of plates, less broken than t08, no slats. Seeds 7 and 8 agree. One small square pit
  (a bite) reads as a hole. The trade-off: an ending edge breaks the 12 m read but merges two treads into one face; an
  edge that dies out between joints instead of merging would answer both.

- **t08** (`reviews/lt1/rock/t08/`; `grey.jpg` Blender grey, rows t08 neutral, t08 raking, t07 neutral, columns
  eye, 12 m, sea, lee, refs 16, 15, 48, 51; `sheet.jpg` columns t08 W high, t07 W high, t04b; rows eye, 12 m, sea,
  each overcast then low sun). Regularity broken by the rock's causes: skewed sheet thickness, edges stepping over
  and ending at J1 joints, bites a few near a metre and most 10-30 cm, a lee of skewed steps. Rung 1 passes: no run of
  even slats, the lee plucked and no longer a cog, the sea profile held. On the way: with skew alone the slats stayed
  parallel, jogs only notches (y1). In Unity, from 12 m and the sea in low sun, no slats and no cog; but at eye level
  merged sheets leave one big cut face, less sheeted than t07, and the crest from the sea is a little more peaked.
  Next for the back: fewer merges and thinner most-sheets near the crest (`end`, `thick` most).

- **t07** (`reviews/lt1/rock/t07/`; `grey.jpg` Blender grey, one sun, eye, 12 m, sea and the lee over refs 16, 15,
  48, 51; `sheet.jpg` columns t07 W high, t06 W high, t04b; rows eye, 12 m, sea, each overcast then low sun). The bun
  is gone: at eye level a sheeted face of broad treads with sheet edges and a chipped crack; from 12 m one mass in
  facets; from the sea the profile holds at the record's height. Bad: the sheet edges read as long regular slats
  from the sea and 12 m in low sun; the land flank's lower edge a smooth rind. On the way: planks while every edge ran
  the full width (x1), a rise per tread barely changed it (x2), bites too small to show (x3), the land flank
  faceted crumpled into blades (x4, reverted), the crumb cleanup first dropped the blocks the joints part (x4).

- **t06** (`reviews/lt1/rock/t06/`; `grey.jpg` Blender grey, one sun, 12 m, sea and the lee over refs 48, 51, 16;
  `sheet.jpg` columns W high, W game, t04b; rows eye, 12 m, sea, each overcast then low sun; refs 48, 51, 16, 15).
  From the sea a long back from the stoss toe to the crest and a steep broken lee, nearer 48 and 51 than t04b's tiers;
  from 12 m one mass with two straight joints. Bad: at eye level a smooth bun, the 18-32 mm cracks drawn lines; W game
  (1224 tris) keeps the sea silhouette but flattens the lee's steps into a pale patch from above; half the record's
  height and without its row, so small beside t04b. On the way: the lee nicked only the crest of a paraboloid (w1),
  terraces (w2), a sliver between the arms (w3), fins from jogs per step (w4), spikes from cutters coplanar with a
  crack's walls (w5, fixed by a 3 mm overlap), an oval outline (w6), a staircase while the strips stepped together
  (w8, w9).

- **t05** (`reviews/lt1/rock/t05/sheet.jpg`; columns A high, A game, B game, t04b; rows eye, 12 m, sea, each overcast
  then low sun; refs 15, 48, 51, 16 and 53-56 below). A melted: the wash round and the sheet displacement turned its
  planes into draped cloth, the sheets running down the walls as drips, the foot a cushion; from 12 m still t04b's
  tiers, now soft. The bake holds (A game reads as A high; a few dark specks in deep cracks). B is true rock up close
  but a 1.1 m pitted boulder, not phyllite bedrock, its scan skirt lying on the water as debris. On the way: striped
  boxes (round 1), a box stack with crumbs (2), melted by a swell on the walls (3); the first sheet missed the rock
  (the carve blend kept its location unevaluated, so `tip.py` placed it twice its offset).
- **t04** (`reviews/lt1/rock/t04/sheet.jpg`; rows eye, 12 m, sea; columns t04a overcast, t04b overcast and low sun;
  refs 15, 48, 51, 16 and the study board 53-56 below). t04a (leaves, each its own stair, `lone8`) read as a grid of
  rounded boxes: tiles. t04b (pieces) better: one mass stepping down in ledges along the shore, cracks that wander,
  lips rounded at the sea, the lee crisp; from the sea nearest the frame. Bad: every piece 0.5-1 m, so from 12 m it
  reads as a heap of rounded cubes where the references show big surfaces and few joints; one pillow piece at the
  far tip; the row's outer sides show long sheared faces. On the way: booleans crumpled (lone5), one body read as
  courses (lone6), a sweep per corner twisted every wall (lone10).

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
