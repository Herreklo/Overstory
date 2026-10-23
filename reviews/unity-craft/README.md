# Unity craft study: working notes

Raw research notes for `docs/research/unity-craft.md`, which is being written from them. Evidence, not current truth.

- `notes-games.md`: how acclaimed Unity games got their look and frame rate.
- `notes-official.md`: Unity's own Unity 6 guides and samples (pending).
- `notes-cities-apple.md`: large data-driven worlds in Unity, and Unity on Apple silicon and Metal (pending).

If the study is not finished, the next session resumes here: write the study from these notes against the project's settings and code, audit the existing Unity work, update the `unity-conventions` skill, add the checks to Q20's plan, review, push and publish.

## If the two pending notes are missing on Monday

Rerun them as fresh Opus agents (web research, no repo edits, under 2,500 words each, every claim with URL and [primary]/[secondary]/[unverified], a "For us:" line each):
- **Official:** Unity's Unity 6 best-practice guides (URP for advanced creators; performance for mobile, XR and Web; for consoles and PCs; profiling; URP shaders and VFX; productivity; project organisation; DOTS), the Manual on Forward+, the GPU Resident Drawer, GPU occlusion culling, Render Graph on tile GPUs, depth priming, STP and FSR, variants and PSO warm-up, Mesh LOD, Adaptive Probe Volumes, IL2CPP versus Mono on macOS, Metal API validation; the URP 3D Sample and Megacity Metro.
- **Cities and Apple:** Cities: Skylines I and II (makers' words apart from Paavo Huhtala's analysis), Shadows of Doubt, Townscaper, Megacity; URP on Apple's tile GPUs (pass merging, framebuffer fetch, memoryless MSAA, opaque and depth texture costs), the GPU Resident Drawer and BatchRendererGroup on Metal, shader hitches, Xcode profiling.

Already found in the project's own settings (23 October): the GPU Resident Drawer is off in `PC_RPAsset.asset` though the conventions rely on it; no Burst code exists though the skill says it is set up; the opaque texture is required, which `performance-craft.md` says to drop on tile GPUs; timing builds use Mono (no scripting backend set); Metal API validation is on (check whether it reaches players).
