# Tools, pipeline and performance

What we need to build so that generated work can be judged, stays deterministic and runs in Unity 6. Part of the Game Lab research. A few items are marked unverified.

## The tools to build first

1. Plan hasher, in tests. Resolve fixture diaries headless across many years, write each plan as canonical JSON (sorted keys, integers only), and compare its hash with the committed one. Run twice, the second time with the input order shuffled. It names exactly which building and year changed. Determinism is the contract, so this comes first.
2. Contact-sheet renderer. A grid of buildings across years, each labelled with seed, id and the events that changed it. The judging surface for Øystein and for the agents.
3. Diary inspector, in the Unity editor. Pick a building, scrub the year, see the event list beside the model, with each visible part linked to the event that put it there. It tests "the world shows its history" directly.
4. Range plotter. Score thousands of plans on a pair of metrics (one from the diary, one from what is visible) and plot them as a 2D histogram. Smith and Whitehead (2010) found their level generator "clearly biased towards more linear levels" this way, from a detail they "never would have realized". Pairing a diary metric with a visual one tests that variety is readable, not just present.
5. Kit validator. In the Blender generator and on Unity import: pivots, grid fit, triangle budget, naming, vertex colours, sockets, plus a one-page sheet per part. Stops parts breaking silently.
6. Performance harness. A fixed town and fixed camera paths, measured with each rendering option on and off, recording frame time and batches. Rendering decisions rest on numbers.

## Determinism

- Never use .NET hash codes or `UnityEngine.Random` for anything visible. Microsoft says `string.GetHashCode` can differ across .NET implementations, versions, platforms and even runs, and should never be persisted. This matters soon: Unity 6.7 is the last release on Mono, and Unity 7 moves to CoreCLR.
- Use explicit integer hashes: xxHash3 (in Unity.Collections) or a ten-line SplitMix64, with seeds like `hash(worldSeed, buildingId, eventIndex, purpose)`.
- Sort by stable ids before any iteration that affects output. Dictionary and HashSet order is not guaranteed.
- Decisions in integers, floats only for meshes. Burst's deterministic float mode is 64-bit only and was reported on hold in 2022; community tests found basic arithmetic matched across platforms but trigonometry did not. Resolve diaries into plans in integers (grid cells, millimetres, enum ids). Floats appear only when building meshes, where a tiny difference can't change which building you get.

## Rendering many buildings in URP

- GPU Resident Drawer (Unity 6.0 and later). Needs Forward+, the SRP Batcher, compute shaders, and shaders that support DOTS instancing; no `MaterialPropertyBlock` and no per-object render callbacks. It pays when many objects share a mesh and shader, which fits kit parts. Unity recommends turning static batching off. If the game is GPU-bound, frame time can rise. Per-building colour must come from vertex colours or palette UVs, not property blocks.
- GPU occlusion culling needs the Resident Drawer and render graph. It tests bounding spheres and can cost more than it saves when little is hidden, which may be true of the raised view. Measure first.
- Mesh LOD (Unity 6.2 and later) generates LODs at import, but only in the editor, so runtime walls get no automatic LODs. Use it on imported kit parts and give runtime walls simple hand-built LODs.
- Building meshes at runtime: `Mesh.AllocateWritableMeshData` can be filled from jobs on any thread. Merge each neighbourhood's walls and roofs into a few chunk meshes; leave kit parts separate for the Resident Drawer.
- Impostors would need re-baking whenever a building's history changes. Leave for now.

## Blender to Unity

- FBX is the mature path. glTFast imports to URP without its own materials yet, so it gains nothing for us today.
- AssetPostprocessor enforces import settings and validates each part: triangle budget, pivot on the grid, bounds in whole cells, vertex colours present.
- A sidecar JSON per part carries sockets, cell size and tags, safer than custom FBX properties (unverified whether Blender writes those reliably).
- Repo size without LFS: GitHub warns at 50 MB per file and blocks above 100 MB, and recommends repositories under 1 GB. Commit scripts, manifests and small exports; attach bulk exports to releases.

## Engine bridge

- Every snapshot carries a `schemaVersion`; a JSON Schema is generated from the TypeScript types and checked on both sides; pinned fixture snapshots live in the repo.
- Start with files: one snapshot per year, easy to replay and compare. Unity never changes world state, so live messaging can wait. Later, newline-delimited JSON over stdio to a Node child process, the same pattern Unity's own MCP bridge uses.
- `JsonUtility` is fast but can't parse a top-level array; Unity's packaged Newtonsoft is the alternative.

## Agents in the pipeline

- Blender MCP (official, Blender Lab): code execution, file summaries, screenshots, renders, API search, and command-line variants that run in a background Blender. It runs code without guards, so treat it with care.
- Unity MCP in the AI Assistant package is a pre-release: scenes, assets, scripts and console. External clients need approval in project settings.
- Unity batch mode (`-batchmode -executeMethod … -quit`) can run our scripts; renders need a real graphics device, so no `-nographics` for contact sheets.
- Failure modes: silent generator failures, agents grading their own work, drifting import settings, unguarded code.
- The human stays in the loop: agents produce sheets, metrics and diffs; only Øystein accepts a new baseline.

## Sources

[Smith & Whitehead 2010](https://www.pcgworkshop.com/archive/smith2010analyzing.pdf) · [Caves of Qud history](https://gdcvault.com/play/1024990/Procedurally-Generating-History-in-Caves) · [Townscaper](https://www.gamedeveloper.com/game-platforms/how-townscaper-works-a-story-four-games-in-the-making) · [Unity graphics test framework](https://docs.unity3d.com/Packages/com.unity.testframework.graphics@8.9/manual/index.html) · [string.GetHashCode](https://learn.microsoft.com/en-us/dotnet/api/system.string.gethashcode) · [Unity CoreCLR update](https://discussions.unity.com/t/coreclr-scripting-and-serialization-update-june-2026/1723299) · [xxHash3](https://docs.unity3d.com/Packages/com.unity.collections@2.3/api/Unity.Collections.xxHash3.html) · [Burst determinism](https://docs.unity3d.com/Manual/burst/float-precision-determinism.html) · [State of determinism](https://discussions.unity.com/t/state-of-determinism-in-unity/867770) · [GPU Resident Drawer](https://docs.unity3d.com/6000.3/Documentation/Manual/urp/gpu-resident-drawer.html) · [Making objects compatible](https://docs.unity3d.com/Manual/urp/make-object-compatible-gpu-rendering.html) · [GPU culling](https://docs.unity3d.com/6000.2/Documentation/Manual/urp/gpu-culling.html) · [Mesh LOD](https://docs.unity3d.com/6000.2/Documentation/Manual/lod/mesh-lod-introduction.html) · [AllocateWritableMeshData](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Mesh.AllocateWritableMeshData.html) · [glTFast](https://docs.unity3d.com/Packages/com.unity.cloud.gltfast@6.10/manual) · [AssetPostprocessor](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/AssetPostprocessor.html) · [GitHub large files](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github) · [Unity MCP](https://docs.unity3d.com/Packages/com.unity.ai.assistant@2.0/manual/unity-mcp-overview.html) · [Command-line arguments](https://docs.unity3d.com/6000.0/Documentation/Manual/EditorCommandLineArguments.html)
