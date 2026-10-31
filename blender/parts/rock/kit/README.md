# The Holm tip's rock, the street's way

Nature restarted on the street's recipe (29 October): the tip's rock made as a small kit of rigid parts, each made
with care, assembled by a generator from `fixtures/lt1-holm-tip.json`, with house 107 in every frame, in the street's
finish, light and cameras. The first lane's meshes are not used; its exposure rule, `WEAR` table, foliation and
zonation are (`../README.md`).

## What our rock takes from the board (30 Oct)

Judged beside a board, never one sheet (the coordinator, after Øystein: ref 57 is one quick idea among these): our
coast's rock (`docs/references/stone/` 15, 16, 49, 50, 52, `study/` 56), the painters (48, 17, 51, 19), the best
stylised rock (`study/` 21, 22, 26, 27; Totoro 09 and 16), and our own house in the painted finish in the same light.
Our main inspiration for rocks is `study/58`, the rock-family sheet (Øystein, 30 October: "i want this to be our main inspo
for rocks"), for the family, its forms and its painting; 59 for edges, and Firewatch's recipe (`docs/research/land-rock-and-water.md`, How studios
make rock).

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
  own tangent normal). Holds on try 2. Stage 4: `paint.py` (kit.json `skin`, the rock's own page; its material
  `gneiss`), then `run/render.sh <round>` (stage 5's Unity view beside 107). Fails its three tries (Rounds, r04).
  Next (r05, the coordinator's verdict: s1-b3 the best stage, stage 2 made it a cushion under a sheet): stage 2
  again with every plane flat, two-size chamfers by the weather, V-groove cracks on the joints, planar chips; each
  stage judged by the coordinator beside s1-b3 and the board before the next. r05: stage 2 passes (the coordinator:
  the planes and chamfers; the geometric cracks taken out, kit.json `sculpt.crack.count` 0), stage 3 holds, stage 4
  (the page: calm base, broad variation, cavities, one drawn crack, lichen colonies) fails its three tries on the
  lichen and the crack (Rounds, r05). Then stage 3 again (hard plane edges, Unity's grey beside s2) passes, and stage
  4 simple (calm base, broad variation, cavities; no lichen, no crack) holds on try 3 in a side low sun
  (`TIP_SUN=-10`), then its calibration (gneiss L 46 in the stone's blue-grey, a paler top, a damper foot). Then the
  cleanup and stage 5 (Rounds, r05 stage 5): the levels shade by their exact planes, the chamfers are fixed bisector
  planes per arris (`sculpt.py` `chamfers`, a check refuses an arris under `sculpt.leastArrisM`), chips planar; the
  mass sunk `sinkM` and leaned by `tilt` (`mass.py` `lean`, a rigid turn about its foot); `foot.py -- --mass boulder`
  (kit.json `foot`) writes `foot.fbx`, the till stones at the turf line, drawn by `Nature/RockFoot.shader`;
  kit.json `beside.high` adds the 12 m view and `beside.iso` the near-isometric (`render.sh <round> eye,street,high,iso`).
  r06 stage 6, the ground: `$PY blender/parts/growth/tufts.py`, then `ground.py` (kit.json `ground`; the pack's
  growth.json habitat `tipTurf`) writes `cache/rock/kit/gen/ground` (the tufts as instances, the ground map Pc and P),
  which `render.sh` installs and LT1HolmTip draws through the growth's own GrowthTufts in the street ground's place.
  Fails its three tries on the heather patches and the till stones; try 4, aimed only at what failed, holds on its
  four asks (Rounds, r06). Stages 7 and 8 go to a fresh session (next bullet).
- **State (30 Oct, r07 stage 7, the edges):** `sculpt.py`'s worn arrises are true rounds, a cylinder tangent to both
  faces (kit.json `sculpt.chamfer`: setback `small` 0.02 m in shelter to `big` 0.04 toward the weather, tapering end to
  end by `taper`), a fresh arris one crisp 12 mm facet. `game.py` shades each level smooth across the rounds: a face on a
  designed plane takes the plane's exact normal, a face on a round the form's own gradient, and edges are hard only
  between two planes. `Sculpt.place_breaks` knocks a few flakes off arrises as planar cuts (kit.json `sculpt.breaks`,
  59's notches): the top corner the mass's record says frost spalled (`mass.masses` `boulder` `spall`, bearing 125),
  two or three along the fresh face's arrises, and one on the front's level foot arris (a place's `steepest` and
  `floorUp`). Each is a floor biting `biteM` [upper, lower] into the arris's two faces, so it faces the sky, and a
  step 25–35° off square at its upper end (a square step is grazed by the bake's rays into a beaded line). Breaks are
  concave, so they are in the high-poly alone and the bake carries them. Chips are off (`chip` shares 0). Try 3 holds
  (the coordinator, Rounds r07).
- **State (30 Oct, r07 stage 8, the page):** `paint.py` paints the gneiss as ref 58 paints its boulders. The stone is
  a neutral grey a shade warm (kit.json `colour.gneiss` `paint` [1.2, 70]): in overcast its top sits at L 70 against
  107's white at 85, with no blue (the shade's coolness is the sky's); in low sun its warmth is the light's and its lit
  top sits 15 L under 107's lit boards. Weathering holds 58's three values: the top 7 L paler (`skin.top`), the
  under-planes 7 darker (`skin.under`), the sides between. The top's stipple (`skin.dabs`) is soft painted dabs, 2–6 cm,
  irregular and overlapping at ±2.5 L, one at most to each 4 cm cell of a seeded lattice, densest on the top and toward
  the weather and fading down over the shoulders. Weathering runs (`skin.runs`) shed down the old sides from under the
  top's lips as many narrow, broken streaks, 2–4 cm wide, at most 5 L, a few together where the water sheds and gaps
  elsewhere, through the street's own `run` (finish paint.py) measured around the stone; they barely read at eye level,
  as 58's brushwork. The breaks
  (`skin.breaks`, from `Sculpt(...).breaks`' planes) are 3 L paler, clean of dabs and lichen, with a 9 mm lit lip times
  the occlusion, as are the fresh face's arrises. The lichen (`skin.lichen`) is a population of small pale grey-green
  rosettes (the material's stain: `stainDL` -3, tint [4, 115]) on the top's weather side, a few merging pairwise,
  nothing wider than 12 cm. The page is dithered by one 8-bit step (its gentle gradients banded). Try 2 held but for the
  runs; try 3 changes only them (Rounds, r07). Stage 9 (one drawn crack) goes to a fresh session.
- **State (30 Oct, r08 stage 9, the crack, try 2; then stages 10 and 11, below):** `paint.py` draws one crack as 58 draws its big boulder's
  (kit.json `skin.crack`, `use` 1). It is the frost joint's trace (dip 86 toward 245) down side/5, the biggest side
  facing the front (bearing 153), at a seeded offset clear of the scars. It starts as a 2 cm notch on the shoulder above
  (top/6), crosses their arris and ends at 79% of side/5 (40 of 50 cm). Along it, measured from the planes exactly:
  - the mouth on the arris is the widest and darkest part (2 cm, 28 L), easing over 2.5 cm to the line;
  - one continuous line, 1.1 cm and 22 L, tapering to 55% of its width and 70% of its value, with a turn of up to 14°
    every 6–14 cm (never 1.6 cm off the trace);
  - it breaks up and fades only in its last fifth;
  - a 7 mm lip, 14 L paler, on the side away from the key light (`lip.light`, bearing 200 at 30°, as both the street's
    suns stand), where 58 draws its lit far wall, over 85% of it;
  - one branch, 8–12 cm long at 30–45°, 0.8 of the line's width and 0.95 of its value.
  It is drawn on those two faces only. The page is 128 px/m, so the line is about a texel and a half. Each texel is the
  mean of 5×5 points over its footprint (a texel square in its face's plane), so the stroke is smooth when magnified
  and keeps its weight down the mips. Try 1's hard edge, softened over 2.5 mm, was stair-stepped. Its own stream
  (`st("crack")`) and keys (`p-crack-break`) leave every other mark as it was.
  **The far side's dotted line** along the lower right arris is not the rock. The tufts cast no shadows
  (`GrowthTufts.cs`), and the dots stand in the same place in overcast and low sun. They are grass blades thinner than a
  pixel, in front of the lower face, aliasing into dots as the blades against the ground do. A fix would be in the
  tufts' shader, outside the rock's paths.
  `probe/faces.py` in the coordinator's notes folder (`rock-r08`) maps each designed face into each
  view. **The street stop sees the boulder from bearing 222**, almost face-on to the fresh face, which is the frost
  joint's own plane. Every frost-joint trace is on a face 70° or more off its view, so from there the crack is a
  hairline at most.
- **Hand-over for stages 7 and 8 (30 Oct, end of r06):**
  - **The ground is a stand-in.** The grass and heath element will make the real one; keep it as it is unless the
    boulder needs it changed. It is the tip's one community (`packs/stavanger-1989/growth.json` habitat `tipTurf`:
    turf with hair-grass through it, summer colours, no heather) over kit.json `ground.box`, built by `ground.py`:
    seeded feet (`growth.place_community`), the bank at the foot (kit.json `ground.bank`: fuller where the stone sheds
    and in its lee, off the till stones by `stoneClear`), `tufts.bin` with each tuft's matrix, rank, hue and damp, and
    the ground map (`growth.ground_map`, Pc and P) damper where the stone sheds. `render.sh` copies
    `cache/rock/kit/gen/ground` into `HolmTip/Generated/ground`; `LT1HolmTip.Ground()` draws the tufts through the
    growth's own GrowthTufts (BatchRendererGroup) over a quad with the map. `GrowthTuft.shader`'s `_GT_SUN` path:
    each tuft's root takes the map's colour under its foot (`_GT_GroundMap`, `_GT_GroundBox`), its normal pulled
    `look.upNormal` toward up, so blades light as the ground; `_GT_Grey` 1 for P. Past 20 m every tuft is its last
    level (`draw.to` [8, 20, 34]), so from the 12 m and iso views the map carries the look; keep its marks round
    (clumpM and grainM [across, along] equal), since a stretch reads as a mown lawn's stripes. Rebuild after a change
    to the stone's foot: `foot.py -- --mass boulder`, then `ground.py`, then `render.sh`.
  - **Where stage 7 starts (the edges).** The boulder's form is `mass.py` (kit.json `mass.masses` `boulder`: its
    designed planes and their kinds; a `pluck` face is fresh) then `sculpt.py` (kit.json `sculpt`): `Sculpt.chamfers`
    gives every arris one flat bisector chamfer, `big` toward the weather, `small` in shelter, `fresh` where a fresh
    face meets; `Sculpt.place_chips` knocks off corners by planar cuts (`chip`: `fresh` and `worn` shares and
    depths, at most `most`, never one reaching past `reach` times its depth). Stage 7's chipped breaks of varied width
    (59) go there, as more planar cuts by place (one fresh corner, the foot), never a jagged ring. `design.py` and
    `carve.py` are r01's and the shore block's makings; nothing on the boulder's path calls them. After a sculpt
    change, in order: `sculpt.py -- --out cache/rock/kit/renders/r07/<r> --masses boulder` (writes
    `gen/boulder/high.blend`; refuses a pinch under `leastArrisM`), `game.py -- --mass boulder`, `bake.py` and
    `paint.py` (each `-- --gen cache/rock/kit/gen/boulder --cache cache/rock/kit/bake/boulder`), `foot.py`, `ground.py`,
    then `TIP_SUN=-10 python3 tools/unity_lock.py run -- bash blender/parts/rock/kit/run/render.sh <round>
    eye,back,street,high,iso P,Pc overcast,lowsun` (about 12 minutes, so run it in the background; `back` is kit.json
    `beside.back`, the far side at eye level, where the fresh face is).
  - **Where stage 9 starts (one drawn crack).** Drawn in r08 (State, r08 stage 9); what follows is the brief it began from. The coordinator's brief: one drawn crack following a joint, a thin
    dark line with a slight light lip, never a seam or a knife slit; ref 58's cracks (the big boulder's, running from
    the top over the shoulder) are the bar, Hertervig's (17) the drawing. The rule exists and is off: kit.json
    `skin.crack` (`faces` 0; set 1 or 2) in `paint.py` (the block after the cavities): the `set` joint's trace (the
    boulder's `frost` joint, `mass.masses` `boulder` `structure.joints`: dip 86 toward 245) across the biggest side
    facing the front (`front`), at a seeded offset, carried onto the face its upper end runs into, drawn on those
    faces only so it ends where the planes change; `widthM`, `lipM`, `L`, `lipL` and `wander` set the line. Untested
    on the boulder since r05: check it ends at plane changes rather than mid-face, stays out of the scars (mask it by
    `scar < 0`, as the dabs and lichen are), and reads from the street stop without becoming a slit. A page-only change
    needs only `paint.py` then `render.sh` (`eye,back` about 4 minutes; all five views about 12). The boulder is drawn
    in the street's OS_Finish through `LT1Street`; changes to that shader need the coordinator's approval. The till
    stones are vertex colour in `Nature/RockFoot.shader`, outside the page.
  - **Why stages 10 and 11 (30 Oct).** The page was accepted against its previous try, not beside 58, and the
    coordinator found it fails there. Beside 58's large boulder:
    - our faces are nearly blank, one flat value each;
    - the top's dabs read as pits;
    - the lichen and runs hardly register past eye level;
    - old faces, the fresh face and the breaks wear one smooth skin;
    - every arris and silhouette segment is ruler-straight, since every face is a true plane;
    - the three triangular bites on the top's edge read as stamped cut-outs: one size and shape, each alone on a
      straight edge.

    Øystein, 30 Oct:
    - "remember to thing about how a rock looks after it breaks. a "break" mark looks different to something that has
      been filed down over years";
    - "also look at the sloping (not stright lines) on some of the edges. like in and out";
    - "Lets really really nail this rock thing".

    The edges' line comes first, because the page bakes onto the final form.
  - **Where stage 10 starts (the edges' line by age: geometry).**
    1. **The target first.** Paint over our own boulder render (`r08-s9f`), at eye level and from the street stop, in
       58's manner:
       - the edges going in and out;
       - fresh breaks against worn faces;
       - the graded faces and the speckled top;
       - the crack.

       The coordinator judges the paintover before any building, and stages 10 and 11 are judged beside it and 58.
       Claude paints it in code (VD5). `rock-r08/probe/faces.py` in the coordinator's notes folder projects each
       designed face and arris into each view, and that places the strokes. A paintover may change forms and surfaces,
       never a fact. The first code target (LT1, `docs/experiments.md`) read as Minecraft because it painted forms onto
       boxes. Here the forms exist and only the edges and the skin change, so paint them as 58 does: in value shapes,
       not texture.
    2. **What 58 does** (the coordinator, on a crop of the sheet):
       - On the large boulder, the border between the light top and the front face jogs in and out. The top bites into
         the side and the side cuts back into the top in small steps, with a notch where the crack meets the edge. The
         long silhouette segments bow gently outward.
       - On the small boulder, the lower edge breaks out into a stepped ledge.
       - On the slanted rock, long thin dark notches entering along the layers serrate the lit top's edges.
       - It works at two scales: whole edges bow gently, and along breaks the line jogs in steps that follow the layers
         or joints.
    **The target (r09, try 3, `reviews/lt1/rock/r09/s10-target-board-try3.jpg`, with try 2 and 58 beside it).** Painted
    in code over the `r08-s9f` stills by `review/paintover.py` (passes from `review/passes.py` at 3x supersampling in a
    window round the boulder, `review/geom.py` writes the sculpt's planes; run with `--ss 3 --box x0,y0,x1,y1`). The
    language Øystein asked for ("not smudges ... how crisp") and the numbers that read at eye level, which the geometry
    and page must reach:
      - planes flat and crisp: each face one value from our light, meeting its neighbour in a hard edge; old arrises
        0.5–1 cm, a pale lip of about 6 mm on the lit side only, broken in runs, none on the silhouette;
      - long edges bowed out by 3.5–4% of their length (worn 0.04, facet 0.035, pluck 0.012 of the arris);
      - old top/side borders walk in and out in steps of 1.2–3.5 cm, 15–50 cm long, risers on the foliation;
      - breaks (spall, the fresh ones, the foot) step 5–15 cm deep in few big stages 10–40 cm long, with a few small
        steps of 2–4 cm beside them; the band they cut lies on the face turned to the eye, paler than both faces;
        a fresh arris gets a few small chips; the old geometry's equal triangular bites are gone;
      - the crack's notch 16 x 7.5 cm on the top/side border, on the crack's own trace;
      - the fresh face paler and neutral (never greener), finer and more contrasty grain than the top's; its
        foliation as soft, uneven, broken bands and one long and one short step, not quite parallel, broken and
        fading mid-face, dark only where the riser turns from the light; from the street stop a hint of banding and
        one step at most;
      - no foot ledge (the grass hides it).
    Still short in the painting: the breaks' bands read a little as flat grey patches (they want the fresh grain and
    a darker riser at each step end in the geometry's own light). The colour (58's use: warm lit, mauve in shade,
    plum only in the occlusion) is the light's and the material's in the build, never a value-to-hue ramp in the
    albedo; the painter's ramp shows the goal only.

    3. **Build it** in `sculpt.py` (kit.json `sculpt`) by rules from the mass's record (see the way of shaping, below),
       never keyed to this boulder's face ids or bearings:
       - The faces are slightly convex, so arrises and the silhouette bow. `mass.py`'s `bulge` already domes each face
         by its kind; `Sculpt.form` keeps every plane flat. Carry the bulge into the high-poly, more on worn faces than
         on the pluck.
       - Old edges wander softly (a seeded, low offset of each plane along its arris) and are rounded at only
         0.5–1 cm (r09, Øystein: "how crisp"; the 2–4 cm rounds made the floor soft, 7–14 px at eye level). The lit
         lip and the flat plane values are the page's (stage 11). Fresh breaks are sharper still: single facets with
         small chips. Old against fresh is then line and surface: long, gently bowed, smooth lines with a lip, against
         stepped, chipped, rough breaks.
       - Breaks jog in and out in steps along the foliation (dip 35 toward 300) and the frost joint (dip 86 toward
         245). Each break is a few planar steps whose risers lie on those planes, sized from few big to many small
         (skewed), never stamped alike. They replace `breaks.fresh`'s equal bites and the foot's.
       - The crack's mouth gets a small notch at the arris, on the crack's own trace. Move the trace's choice (now in
         `paint.py`'s crack block) to where both `sculpt.py` and `paint.py` read it.
       - It stays rigid, with no spikes or slivers (`Sculpt.spikes`, body.py's measure).
    4. **The board:** the silhouette and arris lines in grey (P, overcast, plus one grey light) at all five views,
       beside 58's crop, s8 try 3 (`r07-s8j`, `r07-s8h`) and the paintover.

    After a sculpt change, rerun the chain in stage 7's order (above), `bake.py` and `paint.py` included.
  - **State (31 Oct, r10 stage 10, try 2, built; awaiting the coordinator's word):** `sculpt.py` builds the edges' line
    by age. Every mark is planar cuts in the high-poly, placed by general rules from the record (`kit.json` `sculpt`;
    nothing keyed to face ids or bearings).
    - **Bows:** `bow` domes each face by kind, through `mass.py` `bulge` with `power`. At the shares in `kit.json`,
      arris bows run a median 1.7% of the arris, max 8.5%. Try 1's double share made a loaf, 10 cm taller, its top
      planes merged.
    - **Rounds and wander:** old rounds 0.5–1 cm (`chamfer`), fresh 0.3 cm; old arrises wander 1.6 cm (`wander`).
    - **Breaks are chips, as rock breaks** (`chip()`): a wedge of two planes.
      - The floor is a fracture plane cutting the corner. It runs out to nothing at one end and is `depthM` down the
        lower face and `ratio` of that into the upper face at the other.
      - That other end has one riser on the structure, at a slant (`breaks.riser`: cosine 0.3–0.85 to the arris).
      - Beyond the riser, a small chip (`breaks.small`) steps the deep end down twice.
      - Try 1's box ledges (floor, back wall, two square risers) read as machined slots and hinges, and failed.
    - **Placement:** few and big.
      - `corner`: one plane takes the true top corner nearest the record's `spall` bearing (three faces each turning
        ≥35°, one a top). A kink on a border made a 39 cm slash.
      - `fresh`: 1–2 chips on the fresh face's arrises.
      - `foot`: one big chip off the foot arris, its floor falling to the turf.
      - `border`: the old top/side borders' long steps, 35–80 cm along and 8–16 cm deep.
      - `nick`: a few small chips on the fresh arrises.
      - `notch`: a V of two planes across the arris on the crack's trace.
      - `paint.py` reads the same regions, each bounded by its sphere.
    - **Checks:**
      - Spikes 0; game mesh 846 tris near.
      - A cold reader (fresh Opus, the grey eye and back crops only) called every stage 10 mark a chip, spall or step,
        none a cut, slot, box or inset.
      - It read the painted crack's dashes as "drill or wedge marks". That is stage 11: the crack's page and its
        mouth over the notch.
      - It read the whole stone as "cut or low-poly" for its dead-flat planes and straight edges. That is the form's
        style (58's planes), which the page and the bows carry.
    - **Weakness:** the chips read as small at eye level, quieter than the target's painted breaks.
  - **State (31 Oct, r11 stage 10, try 3, the border steps and the foot; awaiting the coordinator's word):** as try 2,
    with two changes.
    - **Border steps** (`breaks.border`, `chip(onto=True)`): each step is a chip whose ends sit on the form's own worn
      arris (its rounds and wander), not the domed planes' sharp one, which stands up to a centimetre proud of it.
      Measured from the sharp arris, a shallow step was all fillet and read as a dark pocket.
      - The floor is laid `toward` 0.5–0.6 of the way from the upper face to the bisector, so it takes a middle value
        between the faces. It tapers out at one end and ends in a riser on the structure at the other.
      - 30–80 cm along, 5–9 cm into the lower face (`wideM`), crisp to `soft` 1.2 mm (the form's 4 mm rounded a 25°
        crease over 2–3 cm). Its riser stands at the end whose riser faces the front (`riserFaces`, as the foot's).
      - Only borders turning ≥40° (`minDeg`) carry one. A 24° border (top/6–side/5) can't carry a band: its two
        faces take nearly the same value and the riser is a sliver.
      - `paint.py` gives a step's upper edge a lit lip (`old` beside `scar`) and keeps its skin as old as the faces.
    - **Foot** (`breaks.foot` `riserFaces: front`, `small: false`, `fit`, 25–45 cm): one floor and one riser, at the
      end whose riser faces the front. Seen from the front, the riser is a short face in its own shade, not edge-on as a
      lit sliver.
    - **Apart from the notch:** marks keep off the crack's notch by half its width and `breaks.apartM` 10 cm
      (`trace_clear()`), so two marks on one arris read as two.
    - **A cut's own faces are its own** (`skin.breaks.onM` 1 mm): the page's rest point on a cut's face lies on the
      cut's plane to the bake's precision, so `scar` and `old` sat at ≈ 0 there and flickered in and out of the cut.
      That speckled the band like orange peel, ribbed the back strip and outlined it in white (`r11b`). Within 1 mm the
      faces are wholly the cut's: the band is clean (`r11c`).
    - **Seen:** at the eye, a band on top/2–side/2 (where the target painted it), tapering out, under a lit lip, with
      a dark riser at its deep end. At the back, a band on top/3–side/3 and a riser on top/3–side/6.
    - **Shortfalls:**
      - top/2–side/2 turns both faces away from the street stop, so the eye's step can't jog the line there. The
        street stop's jogs are the top/3–side/3 step's small dark notch and the fresh break's triangle, nearly as in
        try 2.
      - The eye band is subtle: its floor sits between the faces' values and its lip is faint. Its riser stands on the
        frost set at 45° to the arris (no set crosses it squarer), so in low sun it reads as a long black blade seen
        edge-on, with pale hairlines below it. The target's riser is a short tick.
      - The foot's floor runs out beside the notch, 9 cm from it, so from the front it reads as a pale strip between two
        dark ends (its riser and the notch's V), both stair-stepped.
      - At 3× the back riser's edge, the foot's and the notch's edges stair-step on the 5 mm voxels.
      - The 0.64 m back step (top/3–side/6) reads as a chamfer more than a step.
    - **Checks:** spikes 0; the high-poly 1,504,520 tris; the game mesh 846 tris near.
    - **The cold reader fails it** (fresh Fable, the grey eye and back crops only; try 2's reader was Opus, so the
      counts don't compare). It reads seven marks as made:
      - the eye riser as a kerf, its pale streaks as striations;
      - the band's lower edge, stair-stepped on the voxels, as a row of drill points;
      - the foot's riser and the notch's V as a slot and a saw kerf (both as in try 2);
      - the crack's mouth with the spot beside it as a drilled hole with a wedge slot (as in try 2);
      - the back step's square jog on the dark face as sawn or cast;
      - the lit rim along the back's top arris as moulded.

      Only the foliation step, the spall's notch, a small nick and the speckle read as nature. The long edges read as
      clean lines with a few isolated nicks: "a dressed quarry block". The common cause is the chips themselves: two
      planes give dead-straight, parallel-sided edges, where a break's outline wanders.
    - **Look first:** `review/look.py` renders the high-poly in grey from the tip's own cameras and suns, windowed, in
      a minute, before the bake and Unity.
  - **State (31 Oct, r12, stage 10's last change: worn old edges, the ragged rule at the dated breaks; awaiting the
    coordinator's word).** The coordinator stopped the chips on try 3's cold read. The boulder is an erratic rounded by
    the ice, and a break no fact dates has weathered into the edge (58's large boulder has no small chips). The
    jagged in-and-out lives on bedrock broken by frost along its layers: the outcrop's kind, the next one built.
    - **Old edges are worn:** the nicks, the border steps, the foot chip and the fresh face's two chips are off in the
      data (`count` 0, `share` 0). The bows stay, and so do the 0.5–1 cm rounds.
    - **The ragged rule** (`ragged()`, `breaks.ragged`, the core tool for the outcrop, slabs and bluffs) breaks a
      dated fracture's outline along its layers, in bites as 58's broken slabs, never across its face.
      - **Where:** on `runs` of its border arrises (the spall 1, the plucked face 2–3), seeded among those the
        foliation crosses at 60° or less from square (`crossLeast` 0.5), only their stretch 10 cm clear of the turf.
      - **A run** is 1–2 bites (`bites`) with 3–5 facets in all (`facets`), each 6–20 cm along (`facetM`).
      - **A bite** sinks the break's plane toward the arris by a depth that rises and falls along it, 1.2–3.5 cm at
        its knots (`stepM`; a cut's at most 0.4 of its own depth). Each facet is one plane, so the facets meet in
        creases and the outline zigzags where they run out on the old face. The depth's upper hull keeps the bite
        convex. Its riser end is the deepest or 0.3–0.6 of the deepest (`fallShare`), so no facet runs as an even band.
      - **Inward,** each facet rises to meet the break's plane 4–12 cm in at its deepest (`inM`). Its turn off the
        plane stays within 20° and half the arris's own turn, so it runs out on the old face a little past the arris.
      - **The riser:** a bite runs out at its first end and stops at its last on the foliation. The riser stands the
        bite's depth there and runs out to nothing inward.
      - **The two dated breaks:** the spall (top/front corner's right end, seen from the eye; a run on its top/2
        border) and the plucked face (side/7, which the back view shows; runs on top/4, top/0 and side/11). The
        plucked face's bites take the face's skin (`paint.py`). The spall faces away from the back camera.
      - **Tried and dropped** (r12, r12b, r12c): slabs split across the whole fracture by the foliation read as
        slits on the spall and planks on the plucked face; facets as strips between foliation risers read as a
        ladder of piano keys.
    - **Finer near the crisp marks** (`refine()`): the faces on a mark's own surface where it meets the form or two
      of its planes meet, within 8 mm, are cut three times along each edge and laid back onto the field. A crease runs as a line at
      1.25 mm, not a 5 mm staircase. The faces are laid back along each vertex's own normal, at most 2 mm a step
      (`stepCapM`). A vertex whose move would turn a triangle over stays where the cut left it. A region's own
      planes meet in a smooth minimum (its `soft`), so the floor and the riser meet in a round, not a fold
      (r12e: 238 folded faces there drew the risers' valleys as rows of dots).
    - **A crease thinner than a texel** (7.8 mm at the page's 128 px/m) is drawn as a line, never a staircase of dots:
      - the cavity, convexity and both levels' normals bake 4× and are box-filtered down (`cavitySuper`,
        `normalSuper`);
      - paint's scar, lip and fresh-lip steps are each at least a texel wide (`tx`).

      The risers stay on the foliation, so on the plucked face a 1.3 cm riser covers only 5 mm of the page, and on
      the spall almost none.
    - **Cold read of r12g (Fable, blind, grey eye and back crops): fails.**
      - On the eye crop, the overcast notch beads into "drill points" and a stroke beside it reads as tool scrapes.
        The spall reads as "a cut rebate", its rim "beveled".
      - On the back, the plucked face's bites read as "a drill-point slot" (beaded riser), "a saw kerf" (straight
        riser), and the floors with their lip as "a dressed chamfer band" with a "moulded" hairline. Its arris is "a
        straight continuous line with … tool marks".
    - **Shortfalls:**
      - the valleys' voxel lumps bead every riser and the notch (Rounds, r12);
      - at 1–3.5 cm the bites are below what the page and the eye resolve as broken: they read as small made
        marks on a clean edge.
      - Per the coordinator's rule, the notch goes into the page in stage 11.
    - **The notch** is the crack's own opening only: 8 cm along the arris, 5.5 cm down, 3.5 cm back (was 16, 7.5
      and 6).
    - **Quiet lips:** `skin.breaks` `lipL` 2 (was 4), `lipM` 6 mm (was 9). A lit rim read as a moulded edge.
  - **Stage 10 closes with r12h (the coordinator, 31 Oct).** Geometry carries the big forms only (about 8 cm and
    more, several texels, a plane at the street stop): the spall's scoop, the plucked face's plane, the bows, the old
    rounds and the crack. The break detail goes into the page, as 58 draws its break steps with paint, not relief.
    Anything 1–3.5 cm on a 7.8 mm page bakes into an even dark line 2–4 texels wide, and an even dark line reads as
    a tool mark (four tries).
    - The bites are off (`breaks.ragged.use` 0), and so is the notch (`notch.use` 0, now the page's).
    - `ragged()` stays, for the outcrop's metre-scale steps.
    - The fine local voxels run only if beads or smear streaks survive r12h.
  - **Stage 11 hand-over (the coordinator's word, 31 Oct): the history form, the age bake, the page by age in 58's
    language.**
    - **The form (approved):** a `history` list in the mass's record (`mass.masses.<id>`, later the pack's place
      record), in calendar years, so age = the scene's year − `year`. Each entry has `what`, `year`, `by`, `on` or
      `at` (placed by the structure, never by coordinates), `label` and `says`. This boulder:

      ```json
      "history": [
        {"what": "rest",  "year": -15000, "by": "ice",   "label": "authored", "says": "the ice left it on the moraine"},
        {"what": "pluck", "year": 1950,   "by": "frost", "label": "authored", "on": {"joint": "frost", "face": 245},
         "says": "frost broke the south-west face off along the frost joint"},
        {"what": "spall", "year": 1985,   "by": "frost", "label": "authored", "at": {"bearing": 125, "corner": "top"},
         "says": "frost spalled a flake off the south-east top corner"}
      ]
      ```

      The old `spall` field and `says` fold into it. That gives one rock three ages (about 17,000 years, 39 and 4).
      A 39-year face shows patina coming back and the first small lichens, not a fresh face.
    - **A human act fits without changing the format:** `by: "person"`, `how` (wedge | plug-and-feather | blast),
      and `event` (the engine's event id). Its label is the engine's, because a person's act is a canonical fact.
      Build nothing for it now; only check that the fields sit cleanly.
    - **One curve, one source:** a single curve in kit.json maps years to edge, grain, value and cover.
      - `sculpt.py` reads it for each region's edge radius, and `paint.py` for the rest.
      - `sculpt.py` tags each region with its entry: the spall's cut takes `spall`, the plucked face takes `pluck`,
        and everything else takes `rest`.
      - `bake.py` writes each texel's age beside `ident`, by the same depth test paint uses.
    - **The page in 58's language:**
      - a value per plane and crisp lit lips;
      - the break steps and the notch drawn as 58 draws them: varied, never an even dark line;
      - colour from the material and the light.

      Draw every thin mark as the mean of its footprint, at least a texel wide (`tx` in paint.py).
    - **Open from stage 10:** vertical smear streaks at the top of the mid (front) face where it meets the arris,
      seen in overcast eye 2× (the cold reader's "chisel scratches"). Find whether they come from the page or the
      normal before painting over them.
    - **The test:** a cold reader (Fable) says which surface broke recently and is right, and nothing reads as made.
      Firewatch's divots stay an A/B in case the low-poly read persists.
    - **Still owed from the brief, after stage 11:** the tuft shader's least blade width in
      `unity/Assets/Shaders/GrowthTuft.shader`. `_GT_LookB.w` (lines 52 and 99) is "a blade's least width (px of a
      1440-line frame)". Blades narrower than a pixel take the least width, with their coverage faded to match. A/B it
      on the rock's and the street's stills.
  - **Where stage 11 starts (the page by age),** only after stage 10's board passes.
    - **Age from the record.** Every surface region carries its exposure age from the record:
      - the old faces date from when the boulder came to rest;
      - the frost spall dates from its own fact;
      - the fresh (pluck) face dates from the frost's fact.

      A break that is not a fact is old and weathers like the faces around it. Today that is the foot break
      (`breaks.foot`). Only a dated break may look fresh, since anything that reads as history must be a fact.

      The record holds no years yet. `mass.masses.boulder` has `spall` (bearing 125, "a few winters ago") and `says`
      ("frost broke one fresh face off"), as text, and the fixture has nothing on the boulder. So the first step is to
      record the ages as dated facts in the mass's record: what, where by its structure, and how many years ago. Agree
      the form with the coordinator (`docs/facts-contract.md`: whose fact it is). Then `bake.py` writes each texel's
      age beside `ident`, and `paint.py` and the normal read it.
    - **One age value drives everything,** as upkeep drives wear in the town:
      - edge: fresh is crisp, single facets with a few small chips along the arris; old is rounded, 0.5–1 cm (r09);
      - grain: fresh is rough and granular, stepped along the foliation, with small scoops, in the near level's normal
        (from the high-poly); old is smooth with a broad undulation;
      - value and colour: fresh is paler and cleaner; old carries a greyer patina;
      - cover: fresh has none; old has speckle, lichen, runs and a dark foot.
    - **Against 58's large boulder:**
      - each face graded in value, lighter at its top and darker and cooler toward the foot;
      - a fine granular speckle on the top, never dots that read as pits (today's dabs, 1.2–3 cm across, do read as
        pits);
      - soft brushy streaks down the sides along the runs;
      - a drybrush light on the arrises;
      - Firewatch's "smooth surfaces interrupted by jagged edges and detailed divots" (21), where the jagged edges are
        the fresh breaks; 58's medium and layered rocks show crisp fresh breaks beside worn tops.
    - **Craft first, briefly:** how fresh fractures in gneiss look against weathered surfaces (colour, grain, lichen
      coming back over the years), and how stylised studios paint the two.
    - **The crack** sits on an old face, so it is old, and its age read is settled here. Keep r08 try 2's line. Draw
      every thin mark the way it is drawn: each texel the mean of its footprint (`skin.crack.samples`), or the mark
      stair-steps and breaks into dots. Take the crack lip's key light (`skin.crack.lip.light`) from the pack's light,
      not kit.json, once the pack carries it.
    - **The test:** a cold reader shown the board says which surface broke recently and which is old, and is right.
    - **The board:** all five views in both lights, beside 58, s8 try 3 and the paintover.
  - **After the strict review: the way of shaping** (Øystein, 30 Oct: "should not shape be easier when we have a "way
    of shaping"?"; "Lets really really nail this rock thing"). The boulder's planes in kit.json (`tops`, `sides`) are
    laid by eye. That makes them the proof of what good looks like, not the method.

    Every edge jog, bow, fresh or old difference and page mark comes from the mass's record through general rules in
    `sculpt.py` and `paint.py`, with their values in kit.json. The record gives:
    - its planes and kinds;
    - its structure (foliation, joints);
    - its dated facts (the spall);
    - its weather side.

    Nothing is keyed to this boulder's face ids or bearings.

    The way:
    1. The rock's structure gives its planes: the joint sets and foliation, with their orientation and spacing.
    2. A block is what those planes cut out.
    3. Its history moves it (rounded if transported), breaks it (frost along a joint, a dated spall) and wears it by
       exposure age. History takes human acts as well as nature's. Øystein (30 Oct): "or split by human - as a lead
       for a murder mystery etc" (an idea, not a chosen game). A rock can be split, drilled, moved, built into a wall or
       carved. Each act is a dated fact from the engine and leaves its own marks:
       - plug and feathers: a row of half-round drill grooves down the face;
       - older wedge splitting: chiselled slots;
       - blasting: half-pipe drill traces on a rough face.

       The same age rule weathers them: chips and rock dust at the foot after days, a clean pale face after years,
       the lichen returning over decades. The format holds these acts from the start; build nothing for them now.
    4. The ground meets it.

    The same steps make a pebble, a boulder, layered slabs, a slanted group all at one dip, a stacked outcrop or a
    bluff. Only the facts change: scale, geology, history. `mass.py`'s `fracture` and `wear` already do part of this.
    What is missing is the outer form from facts instead of hand-laid `tops` and `sides`.

    The design principles go into the rule, never left to luck:
    - few big planes;
    - sizes from few big to many small, never on a grid;
    - no spikes;
    - simple shape, detail in the faces.

    The test:
    1. The rule shapes the boulder from its facts alone.
    2. That boulder is judged beside the hand-designed one, which is the floor, and must match it before hand-laying
       stops.
    3. The rule then shapes 4–5 other rocks from data alone, with no code change, judged as a family beside 58. A rock
       that needs code means the rule was not general.
  - **Stage 8's page, as it stands (keep it until stage 11):** the values and colour (`colour.gneiss`, `skin.top`, `skin.under`), the
    dabs, the rosettes, the runs and the breaks' lip are accepted or in their last try; change none of them for the
    crack. The page is 8-bit (`finishlib.write`): `dl` is dithered by one step before writing (`p-dither`), or gentle
    gradients band. The lichen is the material's stain with a negative `stainDL` (paler); OS_Finish lowers L by
    `_StainDL`, so a negative value lightens. Every mark is keyed by `key(meta, "p-…")`; a new mark takes its own key so
    the others do not move. `HS.Stream` draws are ordered: drawing more in one stream (`st("lichen")`, `st("runs")`)
    reshuffles everything after it in that stream.
  - **Board tools:** a board of seven rows at full size crashes `sheet.py` (memory: it holds float64 tiles): shrink
    the stills to 1280 wide first (`sips -Z 1280`). Close-ups are `sips -c 620 1150 --cropOffset 790 670` (eye) and
    `-c 560 900 --cropOffset 860 900` (far side); the 12 m close-up `-c 560 840 --cropOffset 400 860`.
  - **Boards:** ref 58 first, then 59, 17 and 21 (`docs/references/stone/study/58-rock-family-concept-sheet.webp`,
    `study/59-stylised-sculpted-rocks.png`, `17-hertervig-boulders-1856.jpg`, `study/21-firewatch-rock-formations.jpg`);
    stills shrunk with `sips`, laid out by `blender/parts/rock/sheet.py -- OUT.png 5 IMG...`, the board at 2560 wide.
  - **Gotchas:** colours set on a material from C# go through `new Color(r, g, b).gamma` (the project is linear).
    `LT1HolmTip.cs` holds an uncommitted grade line (`LT1Street.Grade(...)`, the coordinator's): commit the file without
    it by staging a copy (`git hash-object -w` plus `git update-index --cacheinfo`) and committing from the index,
    then check that HEAD lacks it and the working tree keeps it. Never commit `fixtures/lt1-*.json`,
    `unity/Assets/Resources.meta` or `M_Sky.mat`. Blender's own Python (`/Applications/Blender.app/Contents/Resources/
    5.2/python/bin/python3.13`) has numpy for quick checks outside Blender; the system one has none.
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

- **r12** stage 10's last change: worn old edges, the ragged rule at the dated breaks. Board
  `reviews/lt1/rock/r12/s10-final-board.jpg`: columns try 2 (`r10t2`), `r12g`, target try 3, floor (`r08-s9f`); rows
  as r11's. The back 3× crop moved onto the plucked face's top/4 border (frame 1150,990–1480,1175).
  - `r12b` split the fractures into slabs, and `r12c` made strips between risers: slits, planks, piano keys.
  - `r12d` brought in bites, but its top/4 second facet ran as an even band (`fallShare` mended it).
  - `r12e` drew the risers as rows of dots: refine folded 238 faces in the floor–riser valleys.
  - `r12f` brought own-normal projection, the revert, the regions' smooth minimum and the cavity at 3×. The dots
    joined into soft lines with a dot at each end.
  - `r12g` brought normals and cavity at 4× and paint's steps at least a texel wide. The lines softened a little,
    but the dots stayed.
  - The cause, probed with rays along the top/4 valleys: the valley sits a steady 1.2 mm proud (its round). Every
    7–10 mm a voxel lump fills it by a further 2.5–4.6 mm, so the cavity, and the value with it, rises and falls
    along each riser.
  - Two tries to lay the lumps back did not shift them (each still 2.5–4.6 mm): halving a folding move instead of
    undoing it, and laying it onto the round along the field. Neither is kept.
  - The fix is finer voxels local to the break, as the coordinator asked. That is stage 11's first job or this
    stage's try 5.
  - `r12h`, stage 10's close (the coordinator: the break detail goes to the page): bites and notch off. Board
    `reviews/lt1/rock/r12/s10-close-board.jpg`, columns try 2, `r12h`, target, floor, with 58 in the overcast rows.
    - The plucked face's border is a clean, worn arris, with no slots, kerfs or chamfer band.
    - The beads left are all in the page or the grass: the painted crack's line through the foot below its old
      notch, the smear streaks at its top (the crack's mouth and the spot beside it, stage 11's), and grass blades
      thinner than a pixel (the tuft shader's least width). No geometry beads, so no fine voxels.
    - Cold read (fresh Opus, blind, grey eye and back crops): still made, and every remaining read is stage 11's:
      - the painted crack's beaded line through the foot reads as "a drill line, or a screw or bolt" (the worst);
      - the foot's straight top with an even lit lip reads as "a sawn bed with a plinth riser";
      - the old round, even along the back arris, reads as "a machined chamfer or pencil-round" (the edge by age:
        let the round's width wander);
      - the spall's arc reads as moulded, its streaks as claw-chisel marks;
      - the smear fan at the crack's top reads as "clay pinched and pulled down";
      - the whole reads as "a cut block": flat faces, straight edges (the low-poly read; the page, then the divots
        A/B).

- **r11** stage 10 try 3, the border steps and the foot (the coordinator, on try 2: the long top/front step read as a
  thin dark hairline, its floor taking the top's value; the foot chip's bright slivers read as noise). Board
  `reviews/lt1/rock/r11/s10-try3-board.jpg`: columns try 2 (`r10t2`), try 3 (`r11c`), target try 3, floor (`r08-s9f`);
  rows low sun P eye, eye 2×, back, back 3×, street stop 3×; overcast P eye 2× and back 3×, with 58's boulder beside
  the target.
  - Looks first (`review/look.py`): from the sharp arris the s3 step read as a pocket; `onto` and `soft` 1.2 mm made
    it a band.
  - `r11` baked at 64 cavity samples, `r11b` at 256: the band's lumps stayed. They were the cut faces' speckle in the
    page; `onM` cleared them in `r11c`, which also keeps marks off the notch (`apartM`), fits the foot to its run and
    narrows the border bands to 5–9 cm.
- **r10** stage 10, the edges' line by age (Unity grey P, five views, eye and back also in low sun; boards
  `reviews/lt1/rock/r10/s10-try1-board.jpg`, `s10-try2-board.jpg`: try 2, try 1, target try 3, floor r08, 58).
  - Try 1 failed (the coordinator): box ledges read as machined recesses, slots and a hinge, many and small. Worse
    as a whole than the floor's stamped triangles.
  - Try 2 builds the chips as two-plane wedges, few and big, with a V notch. The cold reader names them chips and
    spalls. See the State above.
- **r08** stage 9, the crack (the coordinator: one thin dark line with a slight light lip along the frost joint across a
  face; it ends where the planes change or fades out, stays out of the scars, reads from the street stop as a crack and
  never as a seam, slit or painted line, and is quiet or gone at 12 m and iso; one crack with at most one short branch;
  `TIP_SUN=-10`). `reviews/lt1/rock/r08/s9-try1-board.jpg`:
  - top: rows low sun Pc, low sun P, overcast Pc, overcast P; columns 58, 59, 17 and 21, then the eye, the street stop,
    12 m, iso and the far side;
  - close-ups, three a row: the eye in overcast P (s8 try 3, try 1, 58's boulders); the eye in low sun Pc (s8 try 3,
    try 1, the crack at 2× in low sun P); the street stop in low sun Pc at 1:1, then at 3× in overcast P and low sun Pc;
    12 m in overcast P and iso in low sun Pc and overcast P, at 1:1; the far side (s8 try 3 overcast P, try 1 overcast P,
    try 1 low sun Pc).
  - Looks before the board (`r08-s9a` to `r08-s9c`, the eye only): a 3 cm mouth easing over 5 cm read as a dark
    leaf-shaped gash, its line breaking up from halfway; narrower, with a 2 cm ease, it reads as a crack but as a
    soft pencil stroke, the lip unseen at 6 L; a crisper edge and the lip at 8 L draw it.
  - Try 1 (`r08-s9d`): at the eye a crack from the shoulder arris down side/5, its lip faint on the upper half. From the
    street stop it is a hairline (the face is 71° off its view). It is quiet at 12 m and iso, and unseen from the far
    side (82° off).
  - Try 1 not accepted (the coordinator): it read as a short scratch, dark over only the top 40%, the tail too faint,
    the stroke stair-stepped and the lip only at the top. Keep side/5 and the street stop's hairline; redraw the line.
  - Try 2 (`r08-s9f`), `reviews/lt1/rock/r08/s9-try2-board.jpg`. The top is as try 1's. The close-ups, three a row:
    - the eye in overcast P, then in low sun Pc, at 1:1;
    - the crack at 3× in low sun P, then overcast P;
    - each of those as s8 try 3, try 1 and try 2;
    - then 58's boulders, the street stop at 3× and at 1:1 (low sun Pc);
    - 12 m and iso at 1:1;
    - the far side in overcast P and low sun Pc, and its lower right arris at 3×.

    Try 2 is one continuous line from a 2 cm notch to 79% of the face, smooth at 3×. Its lip shows on the light-far side
    in both lights, and the branch reads at the eye. It is as quiet as try 1 at 12 m and iso, and a line there, not dashes.
    A look at the eye first (`r08-s9e`, lip 10 L, kinks 10°) showed the lip too faint at 1:1.
  - Then the plan changed (the coordinator, 30 Oct). There is no final board: beside 58 the page fails (Hand-over, why
    stages 10 and 11), and the hand-over now covers stage 10 (the edges' line by age), stage 11 (the page by age) and
    the way of shaping that follows the strict review.

- **r07** stage 8, the page (the coordinator: about three values as 58 paints them, the top lightest with a fine
  stipple of grain and lichen, sides mid, under-planes very dark; a neutral to slightly warm stone, its overcast top
  clearly below 107's white, no icy blue; a subtle edge highlight along the breaks times the occlusion; lichen last,
  the speckle thickening into a few flat crusts with crisp, irregular edges; `reviews/lt1/rock/r07/s8-try2-board.jpg`:
  rows low sun Pc, low sun P, overcast Pc, overcast P across eye, far side, street stop, 12 m and iso, right column
  58, 59, 17, 21; bottom try 1 beside try 2: the eye close-ups in low sun Pc and overcast Pc, the 12 m close-ups in
  overcast, the far side in overcast, then try 2's far side in low sun, both eye close-ups in overcast P, and try 2's
  12 m close-up in low sun; `TIP_SUN=-10`). Try 3 (the runs only) waits for the coordinator's word.
  - Looks before the board (`r07-s8a` to `r07-s8d`): a coarse dense speckle on every face read as terrazzo; the
    pigment at C 2.5 made the stone sandy tan in low sun (C 13–19); fixed by a 1 cm clustered stipple on the top
    only and the pigment at C 1.2. Lichen as clusters of round spots read as polka dots, then merged; two crusts side
    by side on the top read from 12 m as a pair of eyes (`r07-s8d`), so one colony a face, stretched (`r07-s8e`).
  - Try 1 (`r07-s8e`, `s8-try1-board.jpg`): overcast top L 70 C 2 h 73, sides 62 and 54, under-planes 20, 107's
    gable 85; low sun lit planes C 18 h 83 (107's lit paint C 17 h 85). Lichen 2.1 % of the texels in two colonies
    (top/0, side/6); scars 0.75 %, lip 1.7 %. The coordinator: values and colour right; the 1 cm flecks read as
    terrazzo, the lobed crust as a stain or paw print (the second single crust to fail, so a new model), the sides
    plain; check the low sun top's value against 107's lit wall.
  - Try 2 (`r07-s8f` to `r07-s8h`, `s8-try2-board.jpg`): the stipple as soft dabs on a seeded lattice (`skin.dabs`);
    round 2–6 cm discs at ±3 L read as polka dots (`r07-s8f`), so their outline is broken by a noise warp, their
    edge soft over 0.9 of the radius, more of them overlapping at ±2.5 L, and none below the shoulders. The top's
    faint contour banding was the 8-bit page (0.63 L a step) on the broad variation; a seeded one-step dither ends
    it. Lichen as 29 rosettes 2–8 cm across, 4 merged pairs. Runs at 4–6 L were not seen; at 10 L, 10 cm and more
    wide and half faded at 30–50 cm they read as soft streaks. Low sun: 107's lit boards L 82–85, the stone's lit
    top 68 and its lit face 66. The coordinator: the stipple, the lichen and the low sun hold; the runs fail (one
    broad dark band on the front read as a smear or a shadow stripe).
  - Try 3 (`r07-s8i`, `r07-s8j`, `s8-try3-board.jpg`: try 2 beside try 3, columns try 2 P, try 3 P, try 2 Pc, try 3
    Pc; rows the eye in overcast, the eye in low sun, the far side in overcast P and low sun Pc; ref 58 last): only the
    runs, as many narrow broken streaks, 2–4 cm wide, 5 L, 3–6 together where the water sheds, at least 12 mm apart,
    starting 1–3 cm under the top's lip, of uneven length, broken over 9 cm. A cut head and short breaks made one piece
    a dark square on the far side (`r07-s8i`); the head fades in over 3 cm and the pieces run longer (`r07-s8j`). 20
    streaks; they barely read at eye level, as asked.

- **r07** stage 7, the edges (the coordinator: shape simple, most edges broad and soft from transport, a few chipped
  breaks of varied width as 59's where a break makes sense, one fresh corner and the foot; Firewatch's jag as accent
  only; never splinters; `reviews/lt1/rock/r07/s7-try3-board.jpg`: rows low sun Pc, low sun P, overcast Pc, overcast
  P across eye, the far side at eye level, street stop, 12 m and iso, right column 58's boulders, 59, 17, 21; bottom
  the eye close-up low sun Pc of s6, try 3 and try 2, overcast P of s6 and try 3, and try 3's fresh face close-up in
  overcast P; `TIP_SUN=-10`). Try 2's board is `s7-try2-board.jpg`. Try 3 holds (the coordinator).
  - Try 1 (`r07-s7a`, no board): the rounds 0.05–0.12 m in three facets; breaks a floor tilted the wrong way, so a
    one-step break deepened without end and cut a striped wedge across the front (the bake's rays could not reach
    it). Apart from the bug, the broad rounds made it a cushion in overcast and soft from 12 m beside r06's crisp
    bevels; 6 cm breaks read as nicks; a step in shade as a slit.
  - Try 2 (`r07-s7b`): the floor runs out away from its step; rounds 0.035–0.09 m; steps sloped 45–65° toward the
    light; breaks 16–45 cm long and 1–4 cm deep, one step each. The frost-spalled corner reads as a lit broken facet
    with a crisp step; the foot chip as a long shallow scallop ending in a step; edges vary from soft on the weather
    side to crisp at the fresh face; from 12 m and iso still planar, as 58. spikeVoxels 0, game near 815 / street 260
    / city 25 tris. The edge's light lip is stage 8's (the page). The coordinator: drifted softer than s6, toward a
    pebble or soap, and the character can't be seen; four asks for try 3 (tighter rounds, smooth shading, breaks
    that read from the street stop, judge the fresh face).
  - Try 3 (`r07-s7c`, then `r07-s7d` on the board): the rounds true and tangent, 2–4 cm, shaded smooth by the form's
    gradient between exact plane normals, so planes meet as a change of value and the overcast cushion is gone.
    Breaks bite set widths into each face (a depth and a lean made one floor nearly parallel to its face, a 40 cm
    sliver); the foot's on the front's level arris only (on a steep one it read as a dark slot); steps 25–35° off
    square (`r07-s7c`'s square steps baked as beaded lines on the fresh face). From the street stop the fresh face's
    top edge reads as two clean steps; at eye level the front shows the spalled corner and the foot notch, and the
    fresh face's notches in silhouette. spikeVoxels 0, game near 824 / street 263 / city 26 tris.

- **r06** stage 6, the ground (the coordinator: continuous dry summer turf and heath out to the frame's edge, the
  growth's instanced tufts, a bank at the foot denser and taller in the lee and the shed, 3–6 darker till stones half
  sunk; `reviews/lt1/rock/r06/s6-board.jpg`: rows low sun Pc, low sun P, overcast Pc, overcast P across eye, street
  stop, 12 m and iso, try 3; right column s5 try 2 eye and 12 m, 17, 21; bottom 02, 09, the foot at eye level (low
  sun Pc), a heather patch from the iso view, try 2's iso; `TIP_SUN=-10`). Fails its three tries; try 4 holds on its
asks (`s6-try4-board.jpg`).
  - Try 1: the tip's community (growth.json `tipTurf`: turf, hair-grass, heather patches) as 37,180 instanced tufts
    over 80 by 80 m, the ground map under them. The ground read as ochre sand under sparse black hairs: the tufts
    darker than the ground they stand on, so each is a mark on it; the heather dark on dark, its patches soft stains
    (the patch edge was set in the field's units, not metres); the bank 87 tufts, unseen.
  - Try 2: each tuft's root takes the ground map's colour under its foot (GrowthTuft `_GT_GroundOn`, as Ghost of
    Tsushima's blades take the terrain's), summer greens (sward `#4f5a33`), blades twice as wide and taller, the
    patch edge crisp in metres, dry drifts and clump marks in the map. From the eye a continuous turf to the horizon;
    but the blades lit by the clump's sideways dome went darker than the ground in the shade and the overcast (dark
    stars from above), the drifts read as camouflage, the patches as stains.
  - Try 3: the dome pulled 0.6 toward up (`look.upNormal`), heather patches small, ragged and full (every foot kept),
    the clump marks strokes with the wind, the bank 430 tufts, the stones darker (dL −16) and rounder. Holds: the
    turf is one continuous mass in all four views and both lights, rooted in its ground; up close the foot is the
    best so far (the bank rises over the foot in the lee, unevenly, never a ring). Fails: from the street stop, 12 m
    and the iso view the heather patches read as bare mud, a history the facts do not give. Past 20 m every tuft is
    its last level (a few blades), so the patch's map colour (soil brown) carries it alone. The till stones read as
    pale shards (lit flat tops at the turf).
  - Next: the patch's map colour the heather mat's own as seen from afar (dark grey-olive, lumpy), not the soil under
    it; the stones sunk deeper with only their rounded backs out, and no top lift. In overcast the turf goes lime; it
    should be muted toward 17's heath.
  - Cost (eye level, try 3): 4,204 tufts and 59,105 triangles drawn of 48,662 placed in 12 kinds (budget 6,000 and
    60,000), one ground map of 2048² BC7 a way, the stones 452 triangles.
  - Try 4 (the coordinator: one more try, aimed only at what failed; `s6-try4-board.jpg`: rows as try 3's, the right
    column 58, 59, 17, 21; bottom try 3's eye (overcast), 12 m and iso, then this try's stones at eye level (overcast)
    and from the iso view (low sun)). Holds on its four asks:
    - The heather patches are gone: `tipTurf` has no `patch` (heather is the grass and heath element's).
    - The stripes came from the map, not the tufts: the clump marks were strokes three times longer along the wind
      (295°) and the grain ten times, and from 12 m they read as a mown lawn's stripes (in the map's 0.5–8 m band,
      stripes along the wind carried 6.1 times the energy of those across it; the field's hash made no difference).
      Both are now round (`clumpM` [0.35, 0.35], `grainM` [0.1, 0.1]; 1.0); the tufts' rank and hue were never banded.
    - The till stones read as 58's fallen pieces: four, a little angular (9 points, chamfer 0.09), sunk half to 62%,
      20 L* below the boulder in a soil-stained grey (`paint` [1, 80]: no blue), no top lift (`topL` 0), placed
      clear of each other (rigid), the bank kept off them (`stoneClear` 1.25). One pass between: smaller and sunk
      deeper (55–70%), they vanished in the bank.
    - The turf is muted toward a summer heath (the sward C* 24 to 17, the turf's tips 36 to 25, hue a little warmer).
    - Still to see: in overcast the bank's tall hair-grass makes a slightly darker ring round the foot from 12 m and
      the iso view; the turf is still greener than 17's straw, as summer is.
    - Cost (eye level): 4,092 tufts and 54,772 triangles drawn of 47,648 placed in 8 kinds; the stones 320 triangles.

- **r05** cleanup and stage 5, the foot (the coordinator: fix the fans, the pinched cuts and the notch, then sink and
  tilt the boulder with grass and a few stones at its foot, nature studies 02 and 09 and Hertervig 17;
  `reviews/lt1/rock/r05/s5-board.jpg`: top try 3 eye Pc, eye P, 12 m Pc; second try 2 eye Pc, try 2 12 m Pc, s4-calib
  eye Pc; third the lit faces before and after (s4-calib, try 3; P), the back's top-left before and after (s2-4b,
  s5-3); bottom 17, 21, 02, 09; all low sun at `TIP_SUN=-10`).
  - Cleanup, holds: the fans were the levels' smooth normals between the planes' own; `game.py` now gives each plane
    face its exact plane normal as a custom split normal (inside a chart the near normal's spread is 0.003, 8-bit
    noise). The pinch and the beads along the apex came from chamfers cut against the running form's gradient; each
    arris now gets one fixed bisector plane (convex, so no slits), and an arris under 0.12 m is refused (least 0.133).
    The notch was a sphere-bounded chip; chips are planar and one that would bite past its reach is dropped.
  - Sink and tilt, holds: sunk 0.22 m of 1.36 (16%), leaned 4° toward bearing 18 (the north end, the heavier, sunk
    deeper in the soft till); `game.py` re-cuts at the turf, so the foot's damp band starts at the turf line.
  - The foot, fails its three tries. Try 1: 88 tufts at the cap, the species' 1 cm blades, hairline straw on bare
    floor; from 12 m a wreath. Try 2: blades 3× wide (the street's GrowthTuft keeps a least width on screen; this
    mesh has to carry it), up to 280 tufts, a blade that would enter the stone left out so a tuft banks against it,
    the reach varied by bearing: up close a mass that hides the foot unevenly (the best so far), but the stones are
    lost in it and from 12 m it is an oval patch on dirt. Try 3: stones at the turf line where it breaks, stray tufts
    past the band, some of the root's green kept everywhere: the stones show but read as pale broken concrete (a
    22-point hull is too many facets), and the strays read as a sparse steppe. Under all three: the stand-in floor is
    bare brown, so any foot reads as a patch; Hertervig's boulders stand in a continuous dry heath of the same straw.
    Next: try 2's band, a third of try 3's strays, stones of 8–10 points and darker; the turf beyond is the tip's
    ground, not the foot's. Cost: the foot 16,628 tris in one mesh at every level (the boulder 809); as placements
    of the growth's instanced tufts (GrowthDraw) it would cost a draw and its levels.
- **r05** stage 4 simple, calibration (the coordinator: lit planes as bright as white paint, cream as sandstone, the
  shade near black, the broad variation unseen; `reviews/lt1/rock/r05/s4-calib-board.jpg`: top Pc, try 3 then this;
  middle the boulder at full size, Pc then P, each try 3 then this; bottom s3's Unity grey, s1-b3's front, 17, 21). One
  change: gneiss L 46 (was 52), its colour the stone's own [3, 250] (107's plinth is gathered gneiss; the warmth is the
  light's), `skin.top` +4 on faces looking up (bleached, rain-washed), `skin.foot` −7 over 0.5 m (was −5 over 0.25).
  Measured in the P still (sRGB): the lit face 162 against the white front's 174–211 (was 180, as bright); down the lit
  face 164 to 141 (was 184 to 176); the top plane lost 5% to the sides' 23%. The shade side, why near black: the page's
  occlusion is about 1 (median 1.0; no ground in the bake), its dL about 0 above the foot; at equal albedo 107's own
  plinth stone (L 51.9) is darker in shade (30) than the rock (39, now 33), and the white gable gets the same share of
  its albedo in shade as the rock (0.12 against 0.10). It is the tip light's sun-to-sky ratio on a mid-grey stone, not
  the page; lifting it is the scene light's, house and rock together. Holds as a calibration.
- **r05** stage 4 simple, the bare stone's page (the coordinator: lichen and the crack come back later, one decision
  each, once the bare stone holds; `reviews/lt1/rock/r05/s4-simple-board.jpg`: top Pc and P in the low sun with 107;
  middle the boulder at full size, s3's Unity grey front, s1-b3's front; bottom 17 and 21). kit.json `skin.lichen.faces`
  and `skin.crack.faces` 0 (none drawn), `skin.broad` ±5 over 1 m cells in two octaves; cavities and the foot darker as
  before. The tip's own low sun (`sunOff` 45, bearing 135) stands behind the eye (`beside.eye` from bearing 125), so
  it lights every plane alike and flattened them in every earlier tip still; `TIP_SUN=-10` (`render.sh`, LT1HolmTip
  `-tipSunOff`) puts it at bearing 190, 65° off the eye's line as s2's judge, still on 107's front.
  - Try 1 (gneiss L 44, paint and under [3, 240]): the planes read; the stone is olive, its shade side near black.
  - Try 2 (L 52, [3, 70]): lighter, tan.
  - Try 3 (L 52, [2, 70]): a pale warm grey as 17's lit boulders; the broad variation calm, barely seen at the eye;
    holds. The shade side stays near black: the scene light's answer (107's plinth in shade is as dark), not the
    page's. Faint triangle fans show inside the lit planes (the levels' normals, not snapped to their plane): a
    follow-up, with the coordinator's two tidies (the pinched cuts at the back's top-left, the notch on the top edge).
- **r05** stage 3 again, the game mesh in Unity's grey (the coordinator: the planes went soft in Unity;
  `reviews/lt1/rock/r05/s3-unity-grey.jpg`, rows front, back, side, near; columns Blender's s2 grey, Unity with the
  bake's normal, Unity bare). `game.py`'s levels shade by their designed planes (kit.json `game.flatDeg`: a face within
  12° of its plane is that plane's, the rest the chamfers' turn; every edge between them hard: 430 on the near level,
  half its faces the planes'). `LT1HolmTip -tipJudge 1` (`TIP_JUDGE=1 run/render.sh <round> front,back,side,near N,M
  lowsun`) draws each part alone in stage 2's clay, sun, sky and views (game.py's `judge.json`), the house away and
  the grade off. Holds: with its bake the near level matches the high-poly in every view, crisp faces, each its own
  value under the low sun; bare, the hard planes hold but the chamfers' turn smears on the back. The first run's
  marks were URP Lit reading the normal on UV0 (metres) where the page is UV1; the judge gives its mesh the page's UV.
  With its bake the levels' own normals hardly show (hardDeg 10 for 50 moved 0.5% of the tip's pixels), so the soft
  planes in the tip's stills come from their view and light or the page, not the mesh.
- **r05** stage 4 again, the boulder's page (Unity, the eye view beside 107, P and Pc in low sun and overcast;
  `reviews/lt1/rock/r05/s4-try1.jpg` to `s4-try3.jpg`, `s4-try3-near.jpg` at full size, `s4-try3-board.jpg`: beside
  s1-b3, 21, 17 and 15). `paint.py` rewritten on the designed faces (kit.json `skin`): a calm base (gneiss L 44) under
  one broad soft variation (±3), the foot's damp, contact and cavities darker; one crack drawn as Hertervig's, the frost
  joint's trace across the biggest front face and onto the next face up, a dark line with a lighter lip, ending where
  the planes change; lichen as the stain (stainDL 9, a dark crust as 15's) in colonies on the three biggest old faces
  looking up or to the sea.
  - Try 1: the crack draws as a level rail across the front (the joint's normal took 90 − dip for its slope); the
    lichen is one blob with satellites and reads as a spill.
  - Try 2, the joint's slope its dip, each colony 25–50 round spots skewed small, thickest at its middle: the crack
    crosses the front face top to turf and reads as a seam on a cushion, even in width, its lit lip a welt; the top
    colony, seen grazing from the eye, reads as scribbles; the broad variation barely shows; the base is calm and the
    planes take their values from the light.
  - Try 3, 9–16 spots of 2.5–7.5 cm radius: the colony reads as paw prints, a few equal rounds in a row; the crack is
    unchanged. Hard level normals (`game.hardDeg` 10 for 50) were tried beside it and changed nothing in Unity (0.5%
    of pixels, all lichen: the bake carries the planes), so it stays 50. Fails. Holds: the base, the light's planes,
    no camouflage. Next: a colony as 15's, many spots of strongly skewed size merging into one irregular blot that
    frays into small dots at its rim, over a faint wash, hugging the face's upper edge rather than its middle; the
    crack shorter and straighter along a plane change, darkest at its middle and tapering to its ends, its lip fainter.
- **r05** stage 3, the bake (Blender grey: high-poly, near and street with their normals, near without): holds on try
  1 with stage 2's form, the cracks taken out (kit.json `sculpt.crack.count` 0, the coordinator's word: no geometric
  cracks on this boulder; one or two drawn in the page instead). Near 871, street 279, city 27 triangles for 9.6 m².
- **r05** stage 2 again, the boulder's high-poly as flat planes (Blender grey; `reviews/lt1/rock/r05/s2-try1.jpg` to
  `s2-try3.jpg`: front, back, side, near; `s2-try3-board.jpg`: beside s1-b3, 21, 17 and 15). `sculpt.py`'s own form:
  the designed planes cut in turn, each arris a flat chamfer (kit.json `sculpt.chamfer`: 0.1 m where its bisector
  faces the tip's sea and wind at 295, 0.022 m sheltered, 0.006 m at the fresh face); no bulge, grain or ridges.
  - Try 1: the planes stay flat and the chamfers draw every edge, wide on the weather side, as 21; but two parallel
    frost cracks run from the top to the turf and slice it like a loaf, and the foliation crack beads into a zipper.
  - Try 2, one frost crack, shorter reaches, the V's depth (not its width) fading where its plane meets shallow:
    the frost crack reads, a clean V from the top shoulder tapering down the front; the top's cracks still terrace.
  - Try 3, the V cut square into the surface (both walls alike whatever the joint's angle): the frost crack holds;
    the foliation's two run along the top-front crease (its strike near the boulder's long edge), so they read as
    a beaded edge and meet the frost crack in an X at the front shoulder; the frost crack zigzags over the pluck
    corner's small chamfers. 0 spikes (least share 0.254), 1.5M tris.
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
- **r04** stage 4, the boulder's painted finish (Unity, beside 107's new page at 9 m; `reviews/lt1/rock/r04/s4-try1.jpg`
  to `s4-try3.jpg`: low sun and overcast, P and Pc; `s4-try3-board.jpg`: the eye view beside 26, 19, 17, 21 and 15).
  Before the tries, 107's page was stale (`107z4/out-hull`), so its roof read broken beside the street's; now
  `107z5/out-r09`.
  - Try 1, the house plinth's recipe on the rock: a dark olive tarp (its strokes and wet band are a wall's, not a
    rock's).
  - Try 2, the rock's own page (`skin`: damp foot, contact, cracks by cavity, rounds lit by arris, lichen as the
    stain on old faces): L 55 reads as plaster, every round piped light, the lichen flat blobs.
  - Try 3, L 44, the arris only on sharp edges (`arris` 8–30 1/m), the lichen at two scales and quieter: the best
    grey and the planes read, but it fails beside the board. The lichen is camouflage (tan decals of one value,
    spread evenly, tied to no form), where 26 and 15 mottle in value and 17 crusts the tops; the wide rounds read
    as a cushion where 17 and 21 meet planes in a drawn edge; the cracks do not show from the eye.
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
