---
name: unity-conventions
description: Use when writing C#, shaders or scenes in the Game Lab's Unity project, or running Unity or anything that writes into unity/: the Unity lock, folder layout, URP settings, determinism and seeding, assembling places from records, levels and instancing, history read from maps, picking, lighting and the shading model.
---

# Unity conventions for the Game Lab

The architecture behind these conventions is `docs/building-blocks.md`; it holds the detail and wins where they differ.

## Setup

- Unity 6 (6000.6), Universal Render Pipeline (URP 17.6). Not HDRP, not the Built-in pipeline. Burst, Collections and Mathematics are listed in `manifest.json`; no Entities.
- Linear colour space. Shaders in Shader Graph or HLSL; custom render passes through URP renderer features.
- For editor work use the Unity skills (`unity-cli`, `urp-postprocessing`, `shader-graph-create-custom-node`, `validate-urp-render-graph-renderer-feature`) and the Unity MCP server when it is connected.

## Using Unity

Several sessions and agents share `unity/` on one Mac, and Unity opens a project only once. Every command that runs Unity on `unity/`, or writes into it, goes through `tools/unity_lock.py`, which runs them one at a time. It waits while another job holds the lock or a Unity outside it has the project open (Øystein's editor too), and prints who every 30 s. `tools/perf.sh` and `tools/golden.sh` take it themselves in timing mode (`--timing`: they also wait for any Blender batch process or player of ours, and write the machine's background load as `machine.json` beside their results), `tools/motion.sh` plainly, and the Blender exports for their install step only. Wait on the lock, never on a `pgrep -f` pattern, which matches the waiting shell itself.

    UNITY_LOCK_OWNER="gully port" zsh tools/perf.sh -perf-only street
    python3 tools/unity_lock.py run --owner "gully port" --purpose "the hash vectors" -- \
        /Applications/Unity/Hub/Editor/6000.6.6f1/Unity.app/Contents/MacOS/Unity -batchmode -quit \
        -projectPath $PWD/unity -executeMethod Overstory.EditorTools.HashVectors.Check -logFile -

`python3 tools/unity_lock.py status` prints the holder, or `free`.

## Folders

```
Assets/
  Art/<family>/            imported library parts (FBX plus sidecar, from blender-generators)
  Art/Palette/             the shared palette texture and its materials
  Code/Core/               the hash (Hash.cs) and shared types
  Code/World/              reading engine data and records
  Code/Assembly/           the assembler: records to chunks, fits and placement
  Code/Parts/              C# twins of fitted parts, at each kind's port
  Code/Scenes/             staging, cameras, lights, interaction
  Shaders/                 the shading model, OS_History and post effects
  Experiments/<LTn>/       one folder and scene per experiment
kinds/, schemas/, packs/   kinds as data, the contracts, setting packs (repo root)
cache/                     untracked: chunks, tree timelines, library meshes
fixtures/                  records, golden fixtures and the engine run
reviews/<LTn>/             contact sheets and renders
```

## Determinism

The same world, seed and history must always give the same picture.

- Never use `UnityEngine.Random` or `System.Random` for anything visible. There is one hash spec, Python's `blender/resolver/hashing.py`: FNV-1a over UTF-8, SplitMix64 from `0x2545F4914F6CDD1D`, `unit = (h>>11)/2^53`. `Code/Core/Hash.cs` matches it and both reproduce `fixtures/golden/hash-vectors.json`. `Overstory.EditorTools.HashVectors.Check` is its test, in batch mode.
- Seed every visual choice from stable ids (record, slot and fill ids, part path and purpose), never from positions. A replaced part takes a new id and so a new seed. Choices use integers, the four operations and square root; sort by stable id.
- No visual choice may depend on frame time, load order or what the camera saw first.

## Unity assembles, and never invents a fact

Plan, life, placement, fitted geometry, the extrinsic bakes and the cheap checks run in C# in the player, so play can change the town. Unity never invents a fact (who is in the bar, whether a shop is open, how a gig went). Player actions go back to the engine as events. If something needs a fact the engine does not have, add a line to `docs/engine-requests.md` and use a clearly marked fixture value meanwhile.

## Assembling a place

A building and the business in it are separate:

- **Building:** footprint, storeys, era of construction, later extensions (each with its own era), condition.
- **Business:** kind, owner, opening year, state (thriving, struggling, closed), sign, fit-out.

A thing holds slots (openings, sockets, surface regions), never deleted; a slot holds dated fills (`docs/building-blocks.md`, Records and ids). The assembler reads the records and the kind files (`kinds/<kind>.json`) and builds 4 m chunks, choosing library parts and fitting fitted parts. Every choice says which fact drives it. A choice with no driving fact uses the seed only, is marked as such, and claims no history.

## Levels and views

- Five levels per kind (L0 close, L1 near, L2 street, L3 shell, L4 block), each switching where its error is under about a pixel at 1440p, not at fixed distances. The judging views (eye level, the street stop, 12 m, the city camera) are bands to judge in, not switch points.
- Hand-over is a dithered cross-fade (`LOD_FADE_CROSSFADE`), never animated.
- Shadows come from caster proxies: L0 and L1 never cast; small parts, tufts and litter never cast.

## Light and shading

- The look lives in our own shading model, not in engine defaults: light ramps, gradient fog by distance, a ground-bounce colour, and a colour script per time of day and weather.
- One shade rule for every surface (`StreetLooks.hlsl`): shade is the surface's own pigment times the light falling on it (the sky term, the sun, bounce, lamps), and how much of the sky's colour shade takes is the light's setting (`_OS_ShadowChroma`, from the stage and style), never a material's. No per-material shadow tint, no shade hue shifted per object, no colour held against the light at dusk (SEASON's lesson, `docs/research/colour-and-shading.md`, rule 1). A material sets its pigment and its form; the light sets everything else. Mud on grey days is answered by the pigment's own strength and by value, never by a tint. Test any light or colour change in drizzle, low sun and blue hour.
- It must not depend on true real-time global illumination. URP's real-time GI is a preview; if it becomes stable it is an extra layer on top.
- No baked lightmaps or baked probes for generated places: they change. The generator places reflection probes.
- **History is read from maps against the date.** Every shader reads layers through one `OS_History(address, layer)` in one include; the fabric date is a shader global, so a jump costs one uniform. The maps hold inputs (rates, reset years, age offsets), never years since. Every shader has the `_OS_BAKE` mode (unlit albedo at the date, normal, history, ids).
- A look is first judged in grey and one light (make, look, fix). Once it holds, it is checked in morning, a grey afternoon and evening.

## Performance

- Budgets are per pass in GPU ms, then triangles, memory and disk (`docs/building-blocks.md`, Budgets); the frame is pixel-bound today, so shaders are A/B'd in the harness first.
- Kit parts and street things draw through the GPU Resident Drawer with the 32-bit Renderer Shader User Value; swarms (setts, slates, tufts, litter) through our own BatchRendererGroup. Shaders use `#pragma target 4.5`, `DOTS_INSTANCING_ON`, `LOD_FADE_CROSSFADE` and `unity_RendererUserValue`.
- **Picking:** the user value is the pick index (unit and piece or instance), which also indexes the cell's facts buffer. Chunks pick through UV3's piece index and the chunk's table, shells per triangle. Ids come from a small id render round the cursor, read back a few frames late, and resolve to a record and part path. One highlight function compares hover and selected ids.
- Crowds: full characters only near the camera or when they matter to the story; the rest instanced with animation baked into textures.
