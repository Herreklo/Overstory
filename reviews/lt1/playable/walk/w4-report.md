# W4: the walker

LT1g, Phase 1a, stage W4 (`reviews/lt1/playable/outline.md` §2), 22 October 2026, Opus 5.5. Everything is in the commit that adds this report.

## In short

- The walk build has a walker.
  - It is a kinematic `CharacterController` at the eye stop (1.65 m), stepping 0.25 m.
  - It walks at 1.4 m/s, or 2.2 m/s on Shift, with 0.55 of that up a flight and 0.6 down. There is no bob, and input reaches speed through a 0.12 s spring.
  - V gives the free camera, and V again lands it.
  - Keys 1 to 5 give the judging views and 6 to 9 LT1g's four views. L changes the light and M the mood. F1 stays the overlay's.
- What it collides with:
  - the clay ground, as 224 mesh colliders, one per 64 m;
  - A to E, as their drawn 1989 meshes;
  - every other house, wall, blocker and stoop, as boxes;
  - the gully's two flights, as ramps through their nosings.
- `LT1Play.CheckProxies` passes all six tests: names, nosings within 1.5 cm, doors, ways, the camera sphere, and the clay drawn under every box.
- The scripted walk from A's door to E's and back reaches 70 of 70 points with 0 falls and 0 sticks. It runs headless as a player argument (`-walk`), which W7 can reuse.
- Physics on the walk costs 66 µs on average, with a p99 of 420 µs. Both are under the 0.5 ms budget.
- Golden passed before the first Unity run and after the last: all 15 frames are identical.
- The overlay's FormatException did not come back in any log.

## What was built

| File | What it does |
| --- | --- |
| `tools/playable/proxies.py` | Writes `proxies.json` from the heart's layout, read at the clay's commit (200d596), and from the stair's sidecars. Runs in Blender's Python, with no scene. |
| `unity/Assets/Experiments/LT1/Playable/proxies.json` | The output, about 660 KB: 3775 proxies (house 620, roof 620, wall 1801, blocker 277, stoop 236, cheek 202, landing 10, ramp 9), 620 doors and 96 ways. Every proxy carries a record id. |
| `unity/Assets/Code/Play/WalkWorld.cs` | Builds the colliders in the player: boxes and ramps from the JSON, and the clay ground cut into 64 m chunks, baked in a job (`Physics.BakeMesh`). Skips the boxes of drawn houses. |
| `unity/Assets/Code/Play/Walker.cs` | The walker and the free camera. |
| `unity/Assets/Code/Play/PlayKeys.cs` | Keys 1 to 9 call `SetView(i-1)`, then L, M and V. |
| `unity/Assets/Code/Play/WalkScript.cs` | Runs a scripted walk from the command line, logs it to CSV, and judges falls and sticks. |
| `unity/Assets/Code/Play/WalkProxy.cs`, `Spring.cs` | The record id on each collider; Holden's critically damped spring. |
| `unity/Assets/Code/Editor/LT1PlayWalk.cs` | `AddWalk`, called from `Compose`: checks the sidecar hashes and adds WalkWorld, Walker, PlayKeys and the drawn houses' MeshColliders. Also `CheckProxies`. |
| `unity/Assets/Code/Editor/LT1Play.cs` | Made `partial`. `Compose` calls `AddWalk` and then `CheckProxies`. |
| `unity/Assets/Code/Scenes/StreetStage.cs` | `SetShafts` made public, so the walker can re-aim the light shafts as it turns. |
| `unity/ProjectSettings/TagManager.asset` | Layers 8 Walk, 9 Camera, 10 Walker, 11 Free camera. |
| `tools/playable/walks.py`, `walks/a-e-a.walk`, `walks/keys.walk` | The scripted walks, written from `proxies.json`. |
| `reviews/lt1/playable/walk/w4/` | The walks' CSVs, player logs and stills. |

All runtime classes are in `Overstory.Play`, so W3's harness arm strips them.

## Decisions, and why

- **The ground is mesh colliders, not boxes from footprints.**
  - The clay is the ground the viewer sees; boxes from footprints would leave the feet off it on every slope.
  - The colliders cost about 110 to 125 ms to cut and 20 to 30 ms to cook, once at load.
  - They did not leak: CheckProxies' test 6 and both walks found no hole.
  - So the fallback was not needed.
- **A to E collide as their drawn 1989 meshes, not as the layout's boxes.**
  - The 1989 houses outgrow the layout's boxes. C reaches from z −5.42 where its box ends at ±3.7, and D reaches to 6.12 where its box ends at 3.5. Their heights pass the roof proxies too.
  - A box would let the walker into a wall or stop it in front of one, at the five houses the walk is about.
  - Each MeshFilter gets a MeshCollider child, with the id `bld/<rec>/1989/<mesh>`. `WalkWorld.drawn` skips their boxes.
- **The sunk hollow is bridged.**
  - The stair's staging sinks the clay up to run + 0.3 m past each flight's top, and the 1.5 m grid carries the dip about 1.6 m further.
  - That left a 0.38 m riser, and the walker stuck there going down.
  - The top flat now reaches `0.3 + 1.6` m past the top (`SINK_REACH`).
- **`Physics.Simulate` is skipped when no Rigidbody exists.**
  - Stepping an empty simulation cost 136 µs a frame.
  - `CharacterController.Move` resolves at once, so the walker does not need it.
- **Doorsteps are searched, not assumed.** CheckProxies looks up to 1.0 m out from the layout's stand point for a place the walker fits. A needs +0.1 m and D needs +0.2 m. C fits once its drawn step counts as floor.
- **Doors the layout's own walls fill are warned, not failed.**
  - 16 doors in the corner (Crest Lane, High Terrace and Holm Street "down" houses) open onto a wall the clay itself draws.
  - That is the layout's to fix (W6's heart work), not the walker's.
- **V lands on open ground.**
  - From a high view, V lands straight below if that ground is walkable. If not, it searches rings 1.5 to 12 m out, in 12 directions starting from where the camera faces.
  - It levels the view on landing.
  - Over the water, or with no ground within 12 m, it keeps flying.

## CheckProxies (from `unity/Builds/Playable/build.log`, the last build)

```
[LT1Play] CheckProxies Assets/Experiments/LT1/Playable/Generated/LT1_Playable.unity (0 s), proxies.json from clay 200d596, heart_layout 604e4788, stair f01250ca:
  1. 3994 proxies, every one named (blocker 277, cheek 202, ground 224, house 620, landing 10, ramp 9, roof 615, stoop 236, wall 1801); A to E as bld/104 (1 drawn meshes), bld/105 (1 drawn meshes), bld/1203 (1 drawn meshes), bld/1107 (1 drawn meshes), bld/304 (1 drawn meshes); built in 192 ms (boxes 42, ground cut 123, cooked 20; 224 chunks, 678880 triangles)
  2. 78 nosings, 390 rays: the ramps within st-gully/fl-0 1.49 cm, st-gully/fl-1 1.44 cm (at most 3)
  3. 620 doors: a walker fits at all but 0 in the corner, 16 in the corner where the clay draws the same wall in the door (the layout's), and 25 beyond it; A to E's doorsteps as drawn, out from the layout's stand point: bld/104/door +0.1 m, bld/1107/door +0.2 m
  4. 96 ways, 18949 stations every 0.5 m: a walker passes all but 0 in the corner and 18 beyond it or shut by the clay's own
  5. 99 houses in the corner: the camera's 0.4 m sphere meets a proxy before every face (0 reached one)
  6. 485 houses, walls and blockers in the corner: the clay drawn at each top but 0; A to E collide as their drawn 1989 houses
  warned, the layout's or beyond the corner (44): heart/bld/crest-lane-down-13/door (Crest Lane down 13) filled by heart/wall/-18.06_117.95 & heart/wall/-20.02_118.35, the clay's own; ... (40 more of the same kind)
  PASS
```

## The walks

Both walks run in the built player at a fixed 30 fps (`Time.captureFramerate`). The results are therefore the same however fast the machine draws.

**`a-e-a.walk`** runs from A's door along the Row, up Gully Steps to E's door at walking pace, and back briskly.

```
[WalkWorld] 3756 boxes, 9 ramps, 224 ground chunks (678880 triangles), 5 drawn houses: built in 169 ms (read 9, boxes 14, ground cut 125, cooked 20)
[WalkScript] .../tools/playable/walks/a-e-a.walk: reached 70 of 70 points in 140.7 s (4221 frames at 30 fps); falls 0, sticks 0, abandoned 0, under the surface 0; walker physics mean 67 µs, p99 420, max 2758; PASS
```

- The stills are `a-door`, `foot`, `landing`, `top`, `e-door` and `a-door-again`, as JPEGs in `w4/`.
- The CSV's shot events still name the PNGs the player wrote; the stills were converted to JPEG afterwards.

**`keys.walk`** checks the keys:
- view 1 is taken over as walking, and view 5 as the free camera;
- V lands, then V flies again, and the flight moves;
- views 2 and 6 to 9 hold, then are taken over as walking;
- views 3 and 4 are taken over as the free camera.

```
[WalkScript] .../tools/playable/walks/keys.walk: reached 0 of 0 points in 10.1 s (304 frames at 30 fps); falls 0, sticks 0, abandoned 0, under the surface 0; walker physics mean 46 µs, p99 202, max 1918; PASS
```

## Physics cost

The cost measured is the walker's own physics time each frame: `Move`, the ground probes and the edge probes.

| Walk | Mean | Median | p95 | p99 | Max |
| --- | --- | --- | --- | --- | --- |
| a-e-a | 66 µs | 51 | 130 | 420 | 2758 |
| keys | 42 µs | 34 | 72 | 90 | 1918 |

- The simulation step costs 0 µs, since it is skipped.
- The two earlier a-e-a runs, with the same code, had means of 59 and 67 µs and p99s of 189 and 164.
- The max in each walk is the first frame after `Place`, a one-time cost when the walk starts.
- Of a-e-a's 4222 frames, 33 (0.8%) are over 0.5 ms:
  - 31 come while the walker brushes along E's front (frames 2496 to 2592), against its drawn mesh;
  - the worst of those is 1.55 ms.
- The proxies build once in 165 to 192 ms at load.

## Golden

Before the first Unity run:

```
PASS gully/1300-drizzle/eye-foot.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1300-drizzle/eye-on.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1300-drizzle/high.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1300-drizzle/into12.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1300-drizzle/street.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1600-low-sun/eye-foot.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1600-low-sun/eye-on.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1600-low-sun/high.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1600-low-sun/into12.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1600-low-sun/street.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1750-blue-hour/eye-foot.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1750-blue-hour/eye-on.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1750-blue-hour/high.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1750-blue-hour/into12.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1750-blue-hour/street.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASSED /Users/oystein/code/Overstory/reviews/golden/compare/report.md
```

After the last Unity and player run:

```
PASS gully/1300-drizzle/eye-foot.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1300-drizzle/eye-on.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1300-drizzle/high.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1300-drizzle/into12.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1300-drizzle/street.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1600-low-sun/eye-foot.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1600-low-sun/eye-on.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1600-low-sun/high.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1600-low-sun/into12.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1600-low-sun/street.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1750-blue-hour/eye-foot.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1750-blue-hour/eye-on.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1750-blue-hour/high.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1750-blue-hour/into12.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASS gully/1750-blue-hour/street.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
PASSED /Users/oystein/code/Overstory/reviews/golden/compare/report.md
```

## How W7 drives the walk

```
python3 tools/playable/walks.py            # rewrites walks/a-e-a.walk from proxies.json
python3 tools/unity_lock.py run --owner "W7 ..." --purpose "..." -- \
  unity/Builds/Playable/OverstoryPlayable.app/Contents/MacOS/Overstory \
    -walk $PWD/tools/playable/walks/a-e-a.walk -walk-log $PWD/<out>/walk.csv -walk-fps 30 \
    [-walk-capture $PWD/<out>/frames] [-walk-stay] -logFile $PWD/<out>/player.log
```

- **Use absolute paths.** The player's working directory is not the repo.
- **`-walk-capture` writes every frame as PNG.** At 2560×1440 that is about 17 GB for a-e-a, so use it only for a film, never for a check. Without it, `shot` stills go beside the log.
- **Exit.** The player quits with 0 on PASS, unless `-walk-stay` is given. The verdict is the last `[WalkScript]` line in the player log.
- **The script's ops** (the full list is in `WalkScript.cs`'s header):
  - `start x y fx fy`
  - `pace walk|brisk`
  - `to x y`
  - `look x y z | off`
  - `wait s`
  - `shot name`
  - `mark label`
  - `view n`
  - `takeover`
  - `free`
  - `fly s [pitch]`
  - `expect walk|free|held`
  - `end`

  Coordinates are street metres.
- **The CSV's columns:** `t, frame, x, y, z, speed, grounded, under, factor, mode, physics_us, event, simulate_us`.
- **A new walk is a few lines in `walks.py`,** built from `proxies.json`'s doors, ways and walking lines, so that no waypoint is invented.

## Open problems

- **The proxies follow the clay at 200d596.** A new clay export needs `proxies.py` run again (the command is in its header). D's door path differs between the clay and the current layout (800085a).
- **Only the gully's flights have ramps.** Other flights in the heart have no stair sidecar, so the walker takes them as clay slope, at slope speed.
- **Bridges, moles and the birch have no proxies.** The walker passes through the birch.
- **The 16 corner doors the layout's own walls fill** are W6's heart fix.
- **E's front costs up to 1.55 ms** while the walker brushes along it. If that matters, give the drawn houses a collider cut to their lowest 3 m, or their convex parts.
- **The first frame of a takeover hitches once** (`corner.Release()`), as does the first frame after `Place`.
- **V from the high view lands facing where the camera faced.** In `keys-5-landed` that is a nearby front, close up.
- **The overlay's view name can lag a frame or two** at the start.
- **The `e-door` still is taken from the doorstep (0.4 m),** so the door fills it.
- **There is no sound, no footfalls and no lens shift.**
