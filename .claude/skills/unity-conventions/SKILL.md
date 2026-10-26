---
name: unity-conventions
description: Use when writing C#, shaders or scenes in the Game Lab's Unity project, or running Unity or anything that writes into unity/: the Unity lock, folder layout, URP settings, determinism and seeding, assembling places from records, levels and instancing, history read from maps, picking, lighting and the shading model.
---

# Unity conventions for the Game Lab

One line and one reason per rule. The architecture is `docs/building-blocks.md` and wins where they differ; the craft and the audit behind the settings, shader and build rules are `docs/research/unity-craft.md` (finding numbers U1 to U31).

## Setup

- Unity 6000.6, URP 17.6, Forward+, linear colour, Render Graph. *Why:* the Resident Drawer needs Forward+; Compatibility Mode is gone.
- Burst and Collections arrive as built-in dependencies, not through `manifest.json`; the only Burst job today is the scale bench (`Assets/Code/Perf/DistrictBench.cs`). Name them in the manifest with the first game job. *Why:* the dependency should not hang on another package's (U30).
- Use the Unity skills (`unity-cli`, `urp-postprocessing`, `validate-urp-render-graph-renderer-feature`) and the Unity MCP when connected.

## Running Unity

- Every command that runs Unity on `unity/` or writes into it goes through `tools/unity_lock.py`; wait on the lock, never on `pgrep -f`. *Why:* sessions share one Mac and Unity opens a project once.
- The lock waits while another job holds it or any Unity outside it has the project open (Øystein's editor too), and prints who every 30 s; `python3 tools/unity_lock.py status` prints the holder or `free`. *Why:* never open the project twice.
- `tools/perf.sh` and `tools/golden.sh` take the lock in timing mode (`--timing`), which also waits for Blender batches and our players and writes `machine.json`; `tools/motion.sh` takes it plainly, the Blender exports for their install step only. *Why:* timings need a quiet machine.

      UNITY_LOCK_OWNER="gully port" zsh tools/perf.sh -perf-only street
      python3 tools/unity_lock.py run --owner "gully port" --purpose "the hash vectors" -- \
          /Applications/Unity/Hub/Editor/6000.6.6f1/Unity.app/Contents/MacOS/Unity -batchmode -quit \
          -projectPath $PWD/unity -executeMethod Overstory.EditorTools.HashVectors.Check -logFile -

## Folders

`Assets/Art/<family>/` imported parts · `Art/Palette/` · `Code/Core/` the hash · `Code/World/` records · `Code/Assembly/` the assembler · `Code/Parts/` fitted parts' C# twins (when they come) · `Code/Scenes/` staging, light, passes · `Code/Play/` · `Code/Perf/` the harness · `Code/Editor/` · `Shaders/` · `Experiments/<LTn>/`. Repo root: `kinds/`, `schemas/`, `packs/`, `fixtures/`, `reviews/`; `cache/` untracked.

## Determinism

- Nothing visible uses `UnityEngine.Random`, `System.Random`, frame time, load order or what the camera saw first. *Why:* the same world, seed and history must give the same picture (U26).
- One hash: `Code/Core/Hash.cs` matches `blender/resolver/hashing.py` (FNV-1a over UTF-8, SplitMix64 from `0x2545F4914F6CDD1D`, `unit = (h>>11)/2^53`) and `fixtures/golden/hash-vectors.json`; `HashVectors.Check` tests it. *Why:* Blender and Unity must agree.
- Seed from stable ids (record, slot, fill, part path), never positions; integers, the four operations and square root; sort by id. *Why:* a moved or rebuilt part keeps its look.

## Facts and assembly

- Unity never invents a fact; a missing one goes to `docs/engine-requests.md` with a marked fixture meanwhile; player actions go back to the engine as events. *Why:* the engine decides.
- The assembler reads the records and `kinds/<kind>.json` and builds 4 m chunks, choosing library parts and fitting fitted parts, in C# in the player. *Why:* play can change the town.
- Building and business are separate records; slots are never deleted, fills are dated; every choice names its driving fact or is marked seed-only and claims no history. *Why:* anything that reads as history must be a fact.

## Levels and instancing

- Five levels per kind, switched by pixel error at 1440p; `lodBias` must be 1 or folded into the error (today 2 on PC). *Why:* otherwise every level sits twice as far as designed (U15).
- Hand-over is a dithered cross-fade, never animated; every shader implements `LOD_FADE_CROSSFADE` before levels land. *Why:* URP's cross-fade is on but no shader has it yet, so levels would pop (U14).
- L0 and L1 never cast shadows, nor do small parts, tufts and litter; casters are proxies. *Why:* the cascades draw the town twice more.
- The GPU Resident Drawer is **off**; it is turned on at step 3.4 only if the harness's player A/B shows a gain, with BatchRendererGroup variants set to Keep All. *Why:* it saves CPU and costs GPU, and the frame is GPU-bound (U12).
- New shaders carry, through the shader template once it exists (`docs/research/unity-craft.md`, The order, step 1): `#pragma target 4.5`, `DOTS_INSTANCING_ON`, `LOD_FADE_CROSSFADE`, `unity_RendererUserValue`. Existing shaders (target 3.5, none of these) gain them at 3.4 behind golden views. *Why:* the Drawer only draws DOTS-instanced shaders (U13).
- Swarms (setts, slates, tufts, litter) draw through our own BatchRendererGroup; no Entities. *Why:* one buffer per swarm, no ECS to maintain.
- Per-instance data goes through the user value and the cell's facts buffer, never a `MaterialPropertyBlock` on a renderer. *Why:* a block excludes the renderer from the Drawer and the SRP Batcher (U16).
- Picking: the user value is the pick index; chunks pick through UV3's piece index and the chunk's table, shells per triangle; ids come from a small id render round the cursor, read back a few frames late. *Why:* no synchronous readback in play (U28).

## Shaders and passes

- Every material property in one `UnityPerMaterial` block; opaque shaders carry DepthOnly, DepthNormals and ShadowCaster. *Why:* the SRP Batcher, SSAO and depth need them (U20).
- Harness and look-test switches never ship: a stripper (`IPreprocessShaders`, step 1 of the study's order) removes them from game builds, and check builds log their variant count; until then, add no new `multi_compile` switch. *Why:* on Metal each new variant is a hitch (U17, U18).
- Custom passes are render-graph raster passes (the pattern is `SunBeamsFeature.cs`, the template to come), read the same pixel by framebuffer fetch, skip themselves when idle, and are checked in the Render Graph Viewer. *Why:* on a tile GPU every pass and copy costs bandwidth (U3, U4).
- Alpha test only where needed, depth first; no `clip()` in an expensive colour pass (the tree shader still does, until `performance-craft.md` item 4). *Why:* discard defeats hidden-surface removal (U21).
- A shader found by name needs a serialised reference in the build. *Why:* otherwise it is missing from players (U27).

## Light and shading

- The look lives in our shading model: light ramps, gradient fog, ground bounce, a colour script per hour and weather. *Why:* fog, light and grade carry the look; materials stay cheap.
- One shade rule (`StreetLooks.hlsl`): shade is pigment times the light falling on it; how much sky colour shade takes is the light's setting (`_OS_ShadowChroma`), never a material's. *Why:* light painted into colour breaks when the light changes (`docs/research/colour-and-shading.md`, rule 1).
- No reliance on real-time GI, no baked lightmaps or probes for generated places; the generator places reflection probes. *Why:* generated places change.
- History is read from maps against the date through one `OS_History(address, layer)`; the date is a global; maps hold inputs, never years since; every shader gains `_OS_BAKE` at 3.1 (none has it yet). *Why:* a jump costs one uniform.
- A look is first judged in grey and one light (make, look, fix); once it holds, it is checked in morning, a grey afternoon and evening. *Why:* one still finds most faults cheaply, and a fix for one light can break another.

## Performance and timing

- Budgets are per pass in GPU ms (`docs/building-blocks.md`, Budgets); anything that changes the picture or the frame time is A/B'd in the harness first. *Why:* the frame is pixel-bound and estimates have been wrong.
- Time built players, never the editor; Frame Timing Stats are switched on by the build script (`LT1Perf.BuildPlayer`). *Why:* editor numbers mislead (U23).
- Timing players run Mono; IL2CPP on Apple silicon is A/B'd once Øystein allows the module. *Why:* time the backend that ships (U22).
- Until pipeline states are warmed from a traced `GraphicsStateCollection` (to be measured), read first visits as hitches, apart from the frame time. *Why:* Metal compiles per pipeline state (U19).
- Unity's Metal validation setting checks the editor only; Apple's needs an Xcode Debug run, worth one per new render feature. *Why:* binding errors hide in players (U25).
- Every loop over parts or vertices in play is a Burst job. *Why:* 0.68 ms against 9.1 per 100,000 triangles.
- Crowds: full characters only near the camera or where the story is; the rest instanced with baked animation. *Why:* simulate the few, show the many.
