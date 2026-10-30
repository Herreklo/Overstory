# The Holm tip's rock, the street's way

Nature restarted on the street's recipe (29 October): the tip's rock made as a small kit of rigid parts, each made
with care, assembled by a generator from `fixtures/lt1-holm-tip.json`, with house 107 in every frame, in the street's
finish, light and cameras. The first lane's meshes are not used; its exposure rule, `WEAR` table, foliation and
zonation are (`../README.md`).

## What our rock takes from the board (30 Oct)

Judged beside a board, never one sheet (the coordinator, after Øystein: ref 57 is one quick idea among these): our
coast's rock (`docs/references/stone/` 15, 16, 49, 50, 52, `study/` 56), the painters (48, 17, 51, 19), the best
stylised rock (`study/` 21, 22, 26, 27; Totoro 09 and 16), and our own house in the painted finish in the same light.

- **Form, from the real rock and Nielsen's svaberg (15, 16, 49, 50, 48):** a few big planes, each from a cause: joint
  faces flat and near vertical with a crisp, slightly broken edge (15), the ice-worn back broad and gently swelling
  (16, 48), dark joints parting it into blocks. A boulder (56, 17, 19) is a block whose transport rounded it: a broad
  top, steep sides tucked in at the turf, one or two fresher breaks.
- **Simplification, from Firewatch, Stålenhag and the painters (21, 22, 26, 17):** big planes of light and shade, each
  nearly one value; detail held to the edges, the cracks and the foot; the rest of a face quiet. The sculpt carries
  the forms, and the bake and paint carry them to a light game mesh, never noise.
- **Edges by exposure:** broad where ice, sea or transport wore them, tight and a little chipped on joints and fresh
  breaks, smooth at the sea foot: one rule from the record's causes, as the art direction's "a few faceted planes and
  cracks, drawn big".
- **Finish, from our houses:** the painted finish (P), up-facing planes lightest, edges drawn by curvature, cracks
  dark, contact shade where it meets the turf; lichen as flat crusts, never mounds.

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
- **State (30 Oct, t13):** the method Øystein chose: one whole scan is the rock, rigid. `scan.py` places "Llyn Idwal"
  (megalitharchive, a roche moutonnée; kit.json `scan`, its source path and credit there) by move, turn and one uniform
  scale only: levelled on its rim's plane, its ice axis (read from its form, 310 in its own frame) turned onto the
  record's 205, its crest at the record's back, its skirt trimmed and its open rim sunk under the low water; t09 only as
  the red outline. Run: `Blender -b --factory-startup -P blender/parts/rock/kit/scan.py -- --glb <scan> --out
  cache/rock/kit/renders/t13/<r> --subject scan|t09` (t09 also writes the masks), then `outline.py -- <dir> scan
  <views> neutral,raking`. A study of a real roche moutonnée's proportions; never in the game (Øystein, 30 Oct:
  nothing downloaded is placed). `scan.py` stays as the study tool; nothing in the kit's build path calls it. t14 was
  not started. Credit wherever credits are listed: "Llyn Idwal by megalitharchive, licensed under Creative Commons
  Attribution".
- **State (30 Oct, r01):** the rock designed as a sculptor would, the houses' way (Øystein, 30 Oct: "It has to look
  truly ours"; a stylised world). `design.py` (kit.json `design`; no scan): the record's facts are constraints (crest
  2.9 m over t09's, the ice's 205, t09's seaward waterline, 107 on its stand), not the generator. The back is section
  lines out from the crest, each segment one plane; the record's sets give the steep planes (J1 the flank walls at the
  foot, J2 and J3 the plucked risers, foliation the sea flank's steps); J1 and J2 are real gaps; the lee is three
  blocks; every piece is a convex intersection of its planes (booleans for the stepped pieces), its arrises a bevel
  weighted by the planes' kinds (ice widest, joints and risers crisp). Ground, turf, tufts and stones as t14's trial,
  the soil read by each face's facing (the record reads the bands by the outcrop's side, which leaves this whole block
  in the storm wash: flagged to the coordinator). Run: `Blender -b --factory-startup -P blender/parts/rock/kit/design.py
  -- --out cache/rock/kit/renders/r01/<r>`. Rung 1 does not hold yet (Rounds, r01). Next: keep r8's making (planes and
  a weighted bevel, 4k tris) and redraw. The back gets fewer, bigger facets whose rounds show, with the bevel unclamped
  on the ice's edges. The lee's three blocks become distinct: each its own size and tilt, a dark seam between them,
  big low and small high. A long low stoss tail must read from the eye view. Then the ground: the land lowered 2.2 m
  is a flat plain, so no turf meets a flank yet.
- **State (30 Oct, r04):** the studio pipeline (the coordinator, after Øystein: "SO many games have done this before"):
  1 blockout of big planes, 2 high-poly sculpt by script, 3 bake onto a light game mesh, 4 the painted finish, 5 Unity
  beside a house; one boulder of 2–3 m end to end first, then the outcrop cut from one mass along its joints. Stage 1:
  `mass.py -- --step block --out cache/rock/kit/renders/r04/<r> --masses boulder` (kit.json `mass.masses` `boulder`:
  21 designed planes, sunk `sinkM`). Holds on try 3 (Rounds, r04). Stage 2: `sculpt.py -- --out <dir>` (kit.json
  `sculpt`; the mass's own `structure`; `split` false keeps an erratic whole) writes `cache/rock/kit/gen/<id>/high.blend`
  (`high_<id>`, about 1.6M tris at 5 mm). Holds on try 3. Stage 3: `game.py -- --mass boulder` (kit.json `game`: the
  form without its fine marks, cut under the turf and decimated to street.json's budgets by surface; charts on the
  designed planes; `high_rock` beside the levels in `house.blend`), then `bake.py -- --gen cache/rock/kit/gen/boulder
  --cache cache/rock/kit/bake/boulder` (selected-to-active from the high-poly: occlusion, cavity, sky and each level's
  own tangent normal). Holds on try 2. Next: stage 4, the painted finish (`paint.py`).
- **State (30 Oct, r03):** the outcrop as a few rigid masses, ref 57's LOW ROCKY OUTCROP the only bar (the
  coordinator's brief: step 1 the masses alone beside 57's boulders, step 2 arranged into the outcrop, step 3 the
  outcrop beside 57's; one change a try, at most three a step). `mass.py` (kit.json `mass`): each mass a convex
  polytope on the record's joint sets with the wear rule's arris and corner facets, every face bulged a little by its
  kind, then split along the record's joints, foliation and sheeting into rigid blocks parted by seams of the
  record's tight width; each block settles by a small seeded turn and is rounded on its own (rolling-ball rounds by
  kind, capped at the record's `capShare` of the block's least width). Run: `Blender -b --factory-startup -P
  blender/parts/rock/kit/mass.py -- --step 1 --out cache/rock/kit/renders/r03/<r>`. Step 1 failed its three tries
  (Rounds, r03), the third closest. Next: more, smaller blocks (57's jagged boulder has about ten, our lee three, and
  its front shows none), seams uneven in width, and the tertiary surface in the bake and paint, never the mesh; then
  step 2.
- **State (30 Oct, r02):** the rock as designed signed-distance bodies, silhouette first (the coordinator's brief:
  step 1 the silhouette, step 2 the body, each looked at before the next, at most three tries each). `body.py`
  (kit.json `body`): a smooth back from a long section, a plan and a cross power each side; blocks parted along the
  record's joints (real gaps, `gapM`), each cut by planes and plucked, every cut a rolling-ball round by its kind
  (ice-worn wide, plucked and joints tight). A splinter check (`spike`, after Øystein's 30 Oct direction: no sharp
  pointy things) runs before meshing. Run: `Blender -b --factory-startup -P blender/parts/rock/kit/body.py -- --step
  1|2 --out cache/rock/kit/renders/r02/<r>`. Step 1 holds; step 2 failed its three tries (Rounds, r02), so steps 3
  (the ground by ref 57) and 4 (the Unity frame) were not started. Kept: step 1's outline, the blocks' layout (stoss
  and main parted by Jback, the lee split by Jlee and plucked big low, small high), the spike measure, the narrow-band
  mesher and the near level. Next: a second, medium scale of form at rung 1 (the round varying along each arris by
  exposure, as data; a few low sheeting steps across the back; a broad swell or two on the crown), or back to r01 r8's
  faceted making with step 1's outline. The coordinator's asks for step 2, which arrived after the three tries: from
  12 m a faceted block, not a torpedo (one long, nearly straight flank along a joint set, the lee end squared off
  unevenly); lee steps uneven in rise and depth, never three equal treads; a shallow shoulder or saddle in the back's
  skyline from the sea where a cross joint runs over it (t13 has one); judged on s1's four-column sheet.
  - **Step 3 inputs** (the coordinator, 30 Oct): the ground at the foot is a planned place, never scatter, by the
    record's exposure and `docs/nature.md`'s communities (thrift and salt grass on the shore, heath and turf above the
    wash band, grass in the joints); the summer flowers placed as form in clay (thrift cushions in the lee joints, a
    flowered turf edge), their colour in the colour pass. Beside ref 57 on the step 3 sheet: `docs/references/nature/
    study/` 09 (stones sunk in grass), 02 (grass along a step's edge), 03 (stone in shade by sunlit grass), 07 (grass
    as a few big lit tufts), 15 (stones in meadow grass by a path; AI-made, composition only) and 16 (stones in roots
    and moss): how rock and growth meet and their masses, never the drawing style.
- **Craft** (a short look, 30 Oct; sources in the session's craft note): Firewatch's rocks were a handful of "rock
  words", each a strong silhouette from every side with flat planes and abstracted inner detail, sunk into the ground;
  edge highlights and a soft occlusion bake carried the rest (Jane Ng, GDC 2015). Big, medium and small: one mass
  carries the silhouette, with a few secondary forms and wide resting areas; the tertiary detail goes in paint and
  normals only. Breaks are cut in the same direction but on a different plane, so the block reads broken and shifted;
  chips come last, only where wear acts. Value comes from baked curvature and occlusion (light edges, dark joints),
  growth from N·up times cavity, and the ground's colour at the base. Never use Voronoi faceting (crystal), smoothing
  all over (potato), tri-planar noise as detail or evenly spread chips. Budget: about 4–10k triangles at LOD0 for a
  15 m hero (inferred; no studio figure).

## Rounds

- **r04** stage 1, the boulder's blockout (Blender grey; `reviews/lt1/rock/r04/s1-b2.jpg`, `s1-b3.jpg`: front, back
  and side, then board crops 26, 17, 19, 21).
  - Try 1: sides from the joint sets' bearings; a crate.
  - Try 2: tops and sides designed from the boulder's story (a broad top with a high north end, one fresh break): the
    planes hold, but its sides lean in from the foot, so it is widest at the turf and grows out of the ground.
  - Try 3, the girth raised (sides 76–86°, tucks 122–128° under them): it sits on the ground, its girth 0.45 m up over a
    shaded undercut, as 26 and 19; 21 big planes, each nearly one value, as 17 and 21. Holds as a blockout; the
    girth's crisp straight edge is stage 2's to roll.
- **r04** stage 2, the boulder's high-poly (Blender grey, 1440 wide; `reviews/lt1/rock/r04/s2-try1.jpg` to `s2-try3.jpg`:
  front, back, side, near). Before the tries, r03's Mass as it was (wear rule, rounds to 0.9 m) melted the blockout to a
  dome (`renders/r04/m0`), so the sculpt rounds the designed planes alone, on its own table.
  - Try 1: planes and exposure rounds hold, the girth rolled; the cracks are knife cuts (straight, rails where the
    plane meets the surface shallowly, beads at the ends) and the chips round craters.
  - Try 2, the cutters reshaped (cracks wandering in two octaves, width held on the surface; chips as flat dishes on
    sharp arrises): cracks still hairlines, chips still pits.
  - Try 3, the marks redrawn: two cracks, wider, lips weathered open, none where the plane meets too shallow; chips
    as planar facets knocked off sharp corners; grain halved. Holds: the fresh break crisp with a chipped corner and a
    crack, worn faces quiet, 0 spikes (least share 0.257). The cracks are slim at the judging distance: stage 4 says
    whether the paint draws them from the cavity bake, and they widen there if not.
- **r04** stage 3, the boulder's game mesh and bake (Blender grey; `reviews/lt1/rock/r04/s3-try1.jpg`: high-poly, near
  with its normal, street with its, near without; `s3-try2.jpg`: high-poly, try 1's near, try 2's near). Near 903
  triangles, street 288, city 27 for 9.9 m², the house's density; page 1024 at 128 px/m; the levels lie within 7 mm
  of the form, so the rays never miss.
  - Try 1: planes, rounds, chips, ridges and grain carry over; a streak along a round at the back's lower corner,
    where the house's face-area-weighted normals crowd the round's whole turn into a few small triangles, steeper
    than the page's texels can correct.
  - Try 2, the levels' normals the plain corner-angle average (`hardDeg` for a hard edge): the streak is gone and the
    corner's facet reads as on the high-poly. Holds. The frost crack is a hairline on the levels: its dark is
    occlusion, which the normal cannot carry, so stage 4's paint must draw it from the cavity bake.
- **r03** (Blender grey; `reviews/lt1/rock/r03/s1-try1.jpg` to `s1-try3.jpg`: the top row is ref 57's ROUNDED
  BOULDER, JAGGED BOULDER and a crop of its outcrop's slabs; below, the crown, stoss and lee from their front and back,
  57's view and a low warm sun; full size in `cache/rock/kit/renders/r03/s1h`, `s1i`, `s1j`).
  - Before the tries, scars cut into the faces failed three ways in quick looks (`s1e`–`s1g`): dense crisp flakes read
    as crazy paving, broad shallow ones as dents, edge chips as round bites. Taken out; the small scale goes to the
    bake and paint.
  - Try 1, every face bulged by its kind: still softened low-poly solids beside 57; the bulge barely shows.
  - Try 2, the masses split into blocks along the record's joints: the first that is the right kind of thing, but
    the seams are cut lines through one continuous surface, and thin sheets under full worn rounds read as cushions.
  - Try 3, each block its own rigid piece (a small seeded settle; rounds capped at the record's `capShare` of the
    block's least width): the stoss's upper slab sits on the lower with a dark opening, as 57's slabs do, and the
    lee's top block steps out over its foot. It does not stand on 57 yet: too few, too big blocks (crown 5, stoss 4,
    lee 3), the crown's front still a clean faceted dome, seams of even width, and no tertiary surface.
  - Measures (try 3): 0 spikes on all three (least share 0.145 to 0.181 against 0.09); flat share 0.77 to 0.85.

- **r02** (Blender grey; `reviews/lt1/rock/r02/s1-silhouettes.jpg` and `s1-drawing.jpg` for step 1, `s2-grey.jpg` for
  step 2: rows g0, g1, g2 neutral, g2 raking; columns eye, 12 m, sea, lee, water; then refs 16, 57, 48, 51 and r01's
  grey; full size in `cache/rock/kit/renders/r02/s3` and `g0`–`g2`).
  - Step 1, the silhouette, holds on try 3. One whaleback from the sea and in the water frame, one long bullet from
    12 m (the 12 m lens widened to 52 degrees, `view12`, as 30 degrees cut the block). Crest 2.90 at 75% along, 11.67 m
    along and 8.15 m across at the sea. Weak: the plan is a regular capsule at 1.43:1 (aimed at 1.7), the lee's steps are
    even, and the slabs' corners leave small spurs.
  - Step 2, the body, fails in three tries.
    - g0 is a loaf: one full-width lee plane across a smooth, even back is a bread end, and the three slabs read as
      boxes leaned against it.
    - g1 is a slipper: a J3 riser facing the land leaves a long sloped toe, and the steep lee is gone.
    - g2 is a rounded box with cushions, a sofa: a crown on sea-rounded walls is a loaf's section. g2 has two blocks
      parted by Jback, the lee split by Jlee and plucked big low, small high. Its measures: 0 spikes (least share 0.152
      against 0.09), 14.95k tris on 172.8 m² at the near level, 10.82 m along and 7.19 m across at the sea, and the lee
      toe 2.9 m down the ice. It does not keep step 1's outline: 0.6 m narrower on the sea side and 0.9 m shorter at
      the stoss.
  - The splinter check first flagged a sliver in the Jlee gap. The notch's sides were written as [315, 84] and
    [135, 84], which are mirror planes, not the joint's two parallel faces, so they crossed in the gap. Joint sides are
    now named ("Jlee", "~Jlee").
  - Why it fails: perfect planes on a smooth analytic back, joined by rounds of one radius, make CAD primitives
    (loaf, cushion, sofa) whatever the arrangement. In refs 48, 16 and 57, three things read as rock and are missing
    here: faces planar only in the large, with sheeting and foliation steps across the back; arrises whose round
    changes along their length by exposure (crisp, broken back, sea-worn), never one fillet; a back of broad swells,
    never one surface of even curvature.
  - The grey check is low in contrast (rock 0.32 on ground 0.27, as r01's), so the form reads weaker than it is.

- **r01** (`reviews/lt1/rock/r01/grey.jpg`, Blender grey, r8; rows: neutral, raking, t09, the t13 study; columns eye,
  12 m, sea, lee; then refs 16, 57, 48, 51; every round in `cache/rock/kit/renders/r01/r1`–`r8`). The restart: t13 was
  stopped before it was built on, by Øystein's direction (30 Oct: nothing downloaded is placed; the form designed, not
  simulated). Rung 1 does not hold. r1–r2, section rings in every direction with a bevel: an igloo, a geodesic dome
  (radial facets have no logic); the bevel threw stray vertices until the boolean's slivers were cleaned. r3, planes on
  the record's sets: rounded boxes, a table top, a J1 wall the length of the sea side, the lee three loaves in a row.
  r4, tilted and asymmetric planes, crisp: a low-poly gem, and the lee concentric terraces, because its blocks took the
  back's lowered flanks. r5–r7, each piece's planes joined by a smooth max on a voxel remesh: soap, cushions, then
  dough. It rounds by value, so planes meeting at a gentle angle melt across metres and no flat survives, and the
  voxels serrate the crisp edges. r8, section-line facets (a faceted barrel, not a ridge or a table) with the weighted
  bevel, the lee crisp: the first that reads as rock, but a generic low-poly boulder, not yet ours. The bevel clamps
  on short edges, so the arrises are nearly crisp; from the eye view there is no long stoss; the lee's blocks merge
  into one faceted face; the ground is a flat plain round it, its turf far off. 4.2k tris, crest 2.90, 11.4 m along
  and 8.7 m across at the sea, its seaward waterline 4.05 m out (t09's).

- **t13** (a study of a real roche moutonnée's proportions; never in the game (Øystein, 30 Oct: nothing downloaded is
  placed). `reviews/lt1/rock/t13/grey.jpg`, Blender grey; rows: neutral with t09's outline red, raking, t09 from the
  same cameras; columns eye, 12 m, sea, lee, the water frame with 107; then refs 16, 57, 48, 51). Rung 1 holds, with
  faults. One whole scan, rigid, scale 0.602: crest 2.90 m (exact), length along the ice 14.9 m at t09's foot (-0.8 m;
  "about 14", +7%) and 9.0 m at the sea (the whaleback's hull 9.5). Ice exact (205); the scan's main plane family
  (its lee, dip 67) lands toward 213, 37° off the foliation's 250, dip right. 1.09 M tris; 150 skirt islands dropped,
  78 pinhole edges filled, no core; every open edge under the sea (highest -0.24 m). From the sea one whaleback: a
  long back to the crest, a steep stepped lee, layering ridges in the raking light, close to t09's outline (the lee end
  a little beyond it, no long low stoss tail, the crest a little lumpy). From 12 m one mass, wandering joints, no grid,
  patchwork or tiles. Up close rock, photogrammetry-soft, neither crystal nor melted. Bad: twice t09's width across
  the ice (13.1 m at the sea against 6.6), so it sits 3.9 m landward to keep the seaward waterline, into what will be
  land, and its plan from 12 m is a big angular kite, three times t09's; scanned grass spikes on the crest ridge; the
  plucked lee a little lumpy and soft; the water frame's land is a crude stand-in (a dark band, no edge).

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
