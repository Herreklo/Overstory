# The walk, W1 and W2: the corner composed in the town, the overlay and the build

LT1g Phase 1a (`reviews/lt1/playable/outline.md` §2), 22 October, Opus 5.5. W1 composes the corner inside the clay town as a generated scene; W2 puts the frame time on screen and builds the Mac player from that scene.

## In short

- `tools/playable.sh` (Build) composes `Assets/Experiments/LT1/Playable/Generated/LT1_Playable.unity` and builds `unity/Builds/Playable/OverstoryPlayable.app` (2560×1440 full screen, MSAA 4x, frame timing on) under the Unity lock. `tools/playable.sh -method Compose -stills <dir>` composes, checks and renders the five judging views.
- The scene holds the heart's clay, the gully's stone, rigs and moods as `LT1Stone.Stage(grey:false)` stages them, the five houses at 1989 in the stronger style in place of the heart's grey masses for them, the corner's birch, and the play object (`PlayCorner` and `FrameTimeOverlay`). Nothing in it is invented: every place, rig and mood comes from a record or a tool already judged.
- Compose refuses to run unless the gully's stair and walls hash as accepted (recomputed from the FBX by `mesh_hash.py` on every run), and it never saves `LT1_Heart.unity`.
- The overlay reads in the built player (`overlay.png`): frame, main thread and GPU, the mean and the worst 1% over two seconds, with the light and view. F1 hides it.
- Compose plus Build: 14 s from the command to the app (compose and check 3 s, build 6 s, Unity's start the rest), with the harness's shaders already compiled. The gully's 15 golden frames are bit-identical after W1 (`golden.sh`: PASSED).
- Commits: W1 `aff1022`, W2 (this report's commit).

## What was built

**W1, compose (`unity/Assets/Code/Editor/LT1Play.cs`, new).**
- `Compose()`: `ComposeOpen()`, then saves the open scene as a copy into `Generated/` and checks the saved scene (`Check()`); with `-stills <dir>` it renders the judging views from it.
- `ComposeOpen()` (public, for W3): the gully's hashes; the houses' record (`Assets/Art/Buildings/playable/manifest.json`, which must hold five houses of the real arm at 1989 in the stronger style); `LT1Stone.Stage(false)`; the heart's `buildings_corner` masses hidden and the five houses stood in their place by `LT1Time.PlaceHouses` (the placement the time test uses, now shared); `LT1Perf.PlantBirch()`; the play object; the first view (eye-foot) and light (drizzle) aimed; the town's sky map rebuilt over the new houses.
- `Check()`: opens the saved scene and prints the gully's hashes and that the stair and cheek walls in it are the hashed FBX, the five houses with their hashes and triangles, the birch, the rigs, views and moods. It throws on any miss.
- `Stills(dir)`: each judging view (drizzle unless `-moments`) from the saved scene at the player's size through `PlayerFrame`, as `PlayCorner.Begin` sets the globals in the player.

**The houses (`blender/tools/export_time.py`).** It gains `--years` (a subset of the diaries' years; a missing year fails) and `--out` (any folder under the Unity project; the record there is `manifest.json`, and `time.json` only in the time test's own folder). Every export now writes `mesh-hashes.json` beside its FBX and each row's `hash` in the record. Run once:

    python3 tools/unity_lock.py run --purpose "the walk's houses at 1989" -- /Applications/Blender.app/Contents/MacOS/Blender -b \
        --factory-startup --python blender/tools/export_time.py -- unity --style stronger --arms real --years 1989 \
        --out Assets/Art/Buildings/playable

It ran after test 5's commit (`739c24d`) and `tools/playable/facts.py` exits 0 on those diaries: A `daa2fde1cf905da5` (13,874 triangles), B `3b5d87a497f5545a` (10,578), C `cfffec1f4401f862` (8,906), D `16dd653b6f112fb1` (10,162), E `88be137d457c3710` (6,378); 49,898 in all, about 4 s. Two runs into scratch folders gave the same hashes.

**The harness's build takes a scene (`unity/Assets/Code/Editor/Measuring/LT1Perf.cs`).** `Compose(string scenePath = ScenePath)` and `BuildPlayer(string app, string scenePath = ScenePath)`; the defaults keep `tools/perf.sh` as it was. Proved on a rerun of its existing arm, `-perf-only eye-on@1300,street@1300`, against the day's earlier run (`reviews/perf/2026-10-22/history-r2/run-1`, the same flights): the settings line is identical and every counter is identical to the triangle (eye-on 139 draws, 63 SetPass, 15,907,493 triangles, 63 shadow casters; street 142, 65, 15,634,387, 66). The timings sit within the corner's noise (offscreen 38.4 against 40.7 ms and 38.0 against 39.4; GPU −1.8 and −1.9%; frame −1.1 and −3.7%; the day's round spread reaches 16.6%). Kept in `reviews/perf/2026-10-22/w1-scene-path/run-1/`.

**W2, the overlay (`unity/Assets/Code/Play/FrameTimeOverlay.cs`, new).** IMGUI, one label redrawn four times a second, no layout pass. From `FrameTimingManager`: the presented frame's period (`cpuFrameTime`, waits included, as the harness's "frame"), the main thread (`cpuMainThreadFrameTime`) and the GPU (`gpuFrameTime`), each as the mean and the 99th percentile (nearest rank, the harness's p99) over the last two seconds of real time, with the frame count, the screen size and the MSAA; then the light, the view and the mood. F1 (Input System) hides and shows it. Without frame timing stats it says so.

**The play object (`unity/Assets/Code/Play/PlayCorner.cs`, new).** What the player switches between: the five judging views (`LT1Stone.Views`), the three judging lights (the heart's rigs), and the six moods (`LT1Heart.Moods`), in their tools' order. At start it sets what the editor's frames set and a scene does not keep (the growth and water packs, `_OS_NearForce`, the sun's shadow reach of 120 m, the birch's leaf bounds), turns vsync off and uncaps the frame rate as the harness does, and shows the first view in drizzle.

**The player's own shot (`unity/Assets/Code/Play/PlayerShot.cs`, new).** `-shot <png> [-shot-after 20]` makes the player capture its screen, overlay included, and quit. macOS `screencapture` from the shell here shows only the desktop and menu bar (it lacks the Screen Recording permission: two tries showed no window at all, not even the frontmost Claude app's), so the player takes its own.

**W2, the build (`LT1Play.Build`, `tools/playable.sh`, new).** `Build()` composes, asserts the pipeline draws MSAA 4x (it checks, it does not set), and builds through `LT1Perf.BuildPlayer(app, ScenePath)`: the harness's player settings (frame timing stats on, full-screen window at 2560×1440, run in background), put back after. `tools/playable.sh` runs it under the Unity lock (not timing mode), puts back the settings a build rewrites that were clean before (as `perf.sh` does), and prints the `[LT1Play]` lines and the check.

## Files

- New: `unity/Assets/Code/Editor/LT1Play.cs`, `unity/Assets/Code/Play/PlayCorner.cs`, `FrameTimeOverlay.cs`, `PlayerShot.cs` (and their metas, the folder's meta), `tools/playable.sh`, `unity/Assets/Art/Buildings/playable/manifest.json`, `playable/real/mesh-hashes.json` (and metas), the stills in `reviews/lt1/playable/walk/w1/`, `reviews/lt1/playable/walk/w2/overlay.png`, `reviews/perf/2026-10-22/w1-scene-path/run-1/{summary.json, summary.md, machine.json}`, this report.
- Changed: `blender/tools/export_time.py`, `unity/Assets/Code/Editor/LT1Time.cs` (`Houses(record)`, `PlaceHouses`, a row's `hash`), `unity/Assets/Code/Editor/Measuring/LT1Perf.cs` (the scene path), `.gitignore` (`Playable/Generated/`, `Playable.meta` while the folder holds nothing else, the playable houses' FBX), `docs/measuring.md` (the walk's player).
- Not kept in git: the generated scene, the houses' FBX (rebuilt; their record and hashes are kept), the app.

## Decisions and why

- **The houses replace the heart's grey masses for them, placed by the time test's own code.** `LT1Time.PlaceHouses` is the time test's loop moved into a function, so the walk and the time test stand the same record the same way; the houses wear `M_Street` and cast, as there.
- **Only the record's arm.** `--arms real`: the shuffled arm is the time test's control and has no place in the town.
- **A record and a hash per export.** `manifest.json` plus `mesh-hashes.json` per folder, as every other export keeps its hashes; the time test's `time.json` keeps its name, so `LT1Time` reads it unchanged.
- **Compose checks the gully by recomputing, not by trusting the manifest.** It hashes the FBX with `mesh_hash.py` (about 2 s) and requires both the manifest and the result to equal the accepted hashes.
- **The heart's scene is never saved.** Compose saves the open scene as a copy by its own path, then opens the copy to check it, so a later save cannot touch `LT1_Heart.unity` (its mtime stayed at 11:55 through every run).
- **The overlay measures as the harness does.** "Worst 1%" is the p99 the harness reports; the rows are the harness's frame, main thread and GPU. On the M4 the GPU row overlaps frames and can exceed the frame (first build: frame 29.8 ms, GPU 45.8 ms at the foot in drizzle; the harness shows the same, `reviews/perf/2026-10-22/w1-scene-path/run-1/summary.md`). It is a guide while walking; the harness measures.
- **Vsync off, frame rate uncapped,** as the harness runs, so the overlay's numbers are the harness's. macOS still presents on the display's refresh, so nothing tears.
- **No composite formatting in the overlay.** The first build's player threw a `FormatException` from the rows' `string.Format` and interpolation at the first frames (Mono's formatter, cause not pinned down); the rows are padded by hand now, and the second build ran clean.
- **MSAA is asserted, not set.** The standalone quality is PC, whose asset already draws 4x.
- **Moods are in the play object now,** so W4's M key needs only a key; the overlay shows the mood only when one is on.
- **`-houses <record>`** lets Compose and Build use another set of houses at 1989 (the time test's gentle set was used to try the whole path before test 5's fixes landed); the style check applies only to the walk's own record.

## The batch check

`tools/playable.sh -method Compose -stills reviews/lt1/playable/walk/w1` (11 s in all):

    [LT1Play] the gully unchanged: stairs bff7858b698f3efd, walls 0a3d7db3100df20b (recomputed from the FBX by mesh_hash.py)
    [LT1Play] the corner: stone stone_gully; 5 houses (A (104) 1989, B (105) 1989, C (1203) 1989, D (1107) 1989, E (304) 1989); the birch 16.7 m; 5 views, 3 lights, 6 moods
    [LT1Play] saved Assets/Experiments/LT1/Playable/Generated/LT1_Playable.unity (the open scene, Assets/Experiments/LT1/Heart/LT1_Heart.unity, not saved)
    [LT1Play] composed in 3 s
    [LT1Play] check Assets/Experiments/LT1/Playable/Generated/LT1_Playable.unity:
      the gully: stairs bff7858b698f3efd, walls 0a3d7db3100df20b (accepted bff7858b698f3efd, 0a3d7db3100df20b); in the scene 1 stairs, 1 cheek walls
      5 houses at 1989 (stronger): A (104) daa2fde1cf905da5 13874 triangles; B (105) 3b5d87a497f5545a 10578 triangles; C (1203) cfffec1f4401f862 8906 triangles; D (1107) 16dd653b6f112fb1 10162 triangles; E (304) 88be137d457c3710 6378 triangles
      1 birch
      3 rigs: 1300-drizzle, 1600-low-sun, 1750-blue-hour
      5 views: eye-foot, eye-on, street, into12, high; 6 moods: hopeless, hopeful, grand, sad, gritty, success
      PASS

The stills, drizzle, at 2560×1440 (looked at reduced for gross faults only, none found; the look is not judged here): `reviews/lt1/playable/walk/w1/{eye-foot,eye-on,street,into12,high}-1300-drizzle.png`.

**The golden views after W1** (`tools/golden.sh`, timing mode, after the compose and the stills): all 15 frames `PASS … 0 pixels changed (identical)`, ending `PASSED reviews/golden/compare/report.md`. Nothing under `reviews/golden/baseline/` was touched.

## Compose plus Build, timed once

Timed once with `/usr/bin/time -p zsh tools/playable.sh` (Build), the lock free:

    [LT1Play] built …/unity/Builds/Playable/OverstoryPlayable.app (PC_RPAsset, MSAA 4x, 2560x1440): compose and check 3 s, build 6 s, both 9 s
    [LT1Perf] build Succeeded: …/OverstoryPlayable.app, 254 MB, 6 s, 0 errors
    LT1Play.Build: exit 0 in 14 s
    real 14.30

The shaders were already compiled for the harness's player (the playable scene uses the same shaders), so this is the warm figure. A first build on a clean Library compiles them, about 6 minutes by `docs/measuring.md`; not measured here. In `docs/measuring.md`, The frame-time harness, The walk's player.

The app opened full screen at 2560×1440 and the overlay read, 20 s in (`reviews/lt1/playable/walk/w2/overlay.png`, the player's own capture, the overlay included): frame 29.5 ms, worst 1% 35.2 (34 fps); main thread 0.9, worst 1.6; GPU 45.2, worst 54.4; 68 frames in 2 s, 2560×1440, MSAA 4x; 1300-drizzle, eye-foot. No exception in the player's log; it quit by itself.

## For W3 and W4

- **Scene and build.** `LT1Play.ScenePath` (`Assets/Experiments/LT1/Playable/Generated/LT1_Playable.unity`); `LT1Play.App` (`Builds/Playable/OverstoryPlayable.app`, under `unity/`). `LT1Play.ComposeOpen()` composes into the open scene without saving and returns `(StreetStage, PlayCorner)`: W3's harness arm can call it, add its `PerfRunner` as `LT1Perf.Compose` does for the perf scene, save to its own generated path, and build with `LT1Perf.BuildPlayer(app, scenePath)` (any scene, the harness's player settings). `LT1Play.Check()` rechecks a saved scene.
- **PlayCorner hooks.** `PlayCorner.Current`; `SetView(i)` (0 to 4 in `LT1Stone.Views`' order: eye-foot, eye-on, street, into12, high; keys 1 to 5), `SetLight(i)` and `NextLight()` (drizzle, low sun, blue hour; wraps: the L key), `SetMood(i)` and `NextMood()` (−1 is none; none after the last), `Release()` (the walker takes the camera: views stop placing it until `SetView`), `HoldsCamera`, `ViewName`, `LightName`, `MoodName`, and the static event `Changed`. LT1g's four views can be appended to `views` (street metres: x along, y back from the building line, z up).
- **The shafts follow the camera only through `stage.Apply()`** (`_OS_SunScreen` is computed there). A walker that moves the camera itself must call `PlayCorner.Current.stage.Apply()` when it moves, or the beams stay aimed at the last view.
- **Overlay hooks.** `FrameTimeOverlay.LightName`, `ViewName`, `MoodName` (static strings; null shows a dash; set `ViewName = "walk"` or "free" when the walker has the camera) and `Visible` on the component. It reads `FrameTimingManager` only and sets nothing. W3 should hide it in harness runs (`Visible = false`, or leave the component out of the harness's scene) so the label's draw is not in the numbers.
- **The player's own shot.** `-shot /abs/path.png -shot-after <s>` for any automated look at the built player; the shell's `screencapture` cannot see app windows on this machine.
- **The F1 key** comes from the Input System (`activeInputHandler` is the new system only): W4's keys should read `Keyboard.current` the same way.
- **The first light is drizzle and the first view eye-foot;** `PlayCorner.Begin()` sets the globals at start and can be called again after a scene change.

## Open problems

- **A's café still lights the pavement in the blue hour (for W6).** Test 5 moved A's café to 2000, so A is without a business in 1989. The houses in the scene are the record's, but `blender/blockouts/heart_layout.py` still casts A as the café: line 465's name `"A (104, café 1988)"` and line 752's `shop="open"`. A's lit shopfront panes sit in `buildings_corner`, which the playable hides; its two shop lights do not. They are in `Assets/Art/Blockout/heart/lights.json` at (39.79, 1.36) and (44.4, 1.31), and `TownLights` lights them in the blue hour on Harbour Row in front of A. So the false state is visible in the playable. I did not fix it, because the fix cannot leave the golden views identical. The fix means rebuilding the heart (`heart_build.py`), whose committed FBX predate heart_layout's last change (`800085a`, the way to D's door), so a rebuild also moves D's way. D stands on the knuckle beside the gully, so that change is likely to show in the golden frames (not rendered to check). Renaming A also reseeds A's windows (`windows:{key}`). W6 should make the two-line fix together with a deliberate rebuild of the heart and a new golden baseline, or drop the corner houses' shop lights in the playable from the record (A has no business at 1989).
- **F1 was not pressed.** The shell here cannot send keys to the player, so the toggle is untested beyond its code (`Keyboard.current.f1Key.wasPressedThisFrame`, as W4's keys will read). W4's key check should include it.
- **macOS `screencapture` sees no app windows from this shell** (no Screen Recording permission), hence `PlayerShot`. A one-minute capture (W7) needs the player's own frames or the permission.
- **The first build's `FormatException`** came from composite formatting in the overlay under the player's Mono; I worked around it (the rows are padded by hand) and did not find the cause. Other runtime code that uses composite formatting may hit it in the player.
- **The cold build time is not measured** (the Library was warm).
- `export_time.py` now writes `mesh-hashes.json` beside every export, so the time test's next export adds `time/real/mesh-hashes.json` and `time/shuffled/mesh-hashes.json` (to be tracked then). The time test's own set in `Assets/Art/Buildings/time/` (b7add8a, 21 October) predates test 5's fixes. As the coordinator said, I did not rerun `time_key.py`: its sources still hold the old lines.
