# History pages: the craft

Step 3's craft study (R0). Marks: (primary) a maker's docs, code or paper; (secondary) a summary; (ours) our arithmetic, code or experiment. Opus 5.5, 22 October 2026.

## In short

- **Binding:** global `Texture2DArray`s and piece table, the pick index in the user value: no extra draws or SRP batches, and the Resident Drawer reads the same line.
- **Compression:** RGBA8 for the A/B, then BC7 from Unity's bc7e (about 0.5 steps off on average, up to 5); BC5 as fallback.
- **Encoding:** each of today's layers varies per texel in one quantity, so H1 holds one linear drive per layer. Resets and a stone's age go per piece. Pages hold only what is continuous.
- **Charts:** per run, not per piece (10 to 15 % waste against 25 to 70 %), on a 4-texel grid with three mips.

## 1. How a draw finds its pages

In URP 17.6, `unity_RendererUserValue` is `asuint(unity_RenderingLayer.y)` in `UnityPerDraw`, and a DOTS-instanced property under the Resident Drawer: one name for both (primary: `UnityInput.hlsl` line 177), set by `Renderer.SetShaderUserValue(uint)`. It "doesn't interfere with batching" and needs no material copies (primary). Rendering layer and user value are one; `.x` stays the light-layer mask.

The SRP Batcher batches by shader variant across "as many different materials" as you want (primary): a material per group costs nothing today, but under the Resident Drawer splits instanced kit parts by group.

**Default (R2),** costing no draws or SRP batches; per pixel, three array samples and a flat varying:
- One `Texture2DArray` per GPU format, bound globally: RGBA for P0, P1 and H1 to H3; RG for the bent normal; R for litter. A slice per group and page: about 240 within 80 m (ours).
- A global `StructuredBuffer` piece table, read in the vertex stage by UV3's piece index; slice, resets and piece age pass flat to the fragment. Per piece, so 2a's one-FBX flight across two groups works.
- The user value is the pick index; its unit slot will give the piece table's base (step 3: base 0).
- Streaming by `Graphics.CopyTexture` into a slice and mip, on the GPU; compressed regions are multiples of 4 (primary).

**Unknowns:** the cost on the M4 (R2's quad); whether Metal copies a `Texture2D` into a slice (R2); the DOTS variant (with the Resident Drawer).

## 2. Data in block compression

A BC4 block is two 8-bit endpoints and eight levels; BC5 is two BC4s (primary, Reed). BC7 has alpha only in modes 4 to 7: one RGBA line, an RGB line plus one free channel, or two coarse RGBA lines (primary, Microsoft). Four uncorrelated channels get one free axis at most.

Error in 8-bit steps on 512×256 pages (ours: numpy, a BC7 of modes 4 to 6, an upper bound on bc7e):

| Data | BC7 mean/99th/max | BC4 ×4 |
| --- | --- | --- |
| Charts (per-piece values, gradients, noise) | 0.46/2/5 | 0.15/0.7/1.3 |
| Smooth fields (σ 16 texels) | 0.73/3/7 | 0.26/1.1/2.1 |

A step inside a block cost BC4 4 steps. Bytes a texel: BC7 1, two BC5 pages 2, RGBA8 4.

Apple silicon samples BC (secondary). Unity compresses at import on macOS: 6000.6.6f1 ships arm64 `libcompress_bc7e` and `libispc_texcomp` (primary), reached by `EditorUtility.CompressTexture`. The player's `Texture2D.Compress` makes BC4 and BC5 but not BC7, and its high quality dithers (primary). Linear import: sRGB off; Alpha Is Transparency off, since it dilates colour (primary); Box mips; Crunch off.

**Default (R2, R5):** RGBA8 first, then BC7 from an editor script compressing our chart-aware mips at Best. Over 2/255, H1 becomes two BC5 pages. Nothing that steps goes into a BC page.

**Unknowns (R2):** bc7e's real error; whether it runs perceptual on linear data (unequal channel errors show it); whether `CompressTexture` keeps our mips. The player's GPU encoder stays `maps.json`'s.

## 3. Time-varying inputs per texel

Gu et al. store four half-float maps per parameter (amplitude scale, time scale, time offset, amplitude offset) and one curve per process (primary, STAF). Games keep a per-texel factor against a global value: Lagarde's porosity in a spare channel against a wet level (shipped static in *Remember Me*); Valve's water, with a time offset per texel from noise (primary). No source stores resets per texel.

Our laws (ours):
- polish = (1 − e^(−F·min(t, 40)/4×10⁵)) × foot;
- lichen = clamp((t − 12) × quiet/200);
- moss = damp × (1 − 0.85 traffic) × min(t/60, 1).

Each varies per texel in one quantity: polish and moss in amplitude, lichen in rate. Footfall is per flight; the delay is the material's. So the brief's unknown 1, the missing amplitude, needs no second page if R1 agrees.

An 8-bit amplitude errs half a step; a linear rate at most x_max/510, x_max being the fastest rate times the longest age: 0.5/255 for lichen (ours). Log wins only where rates span decades under a saturating curve: 32 codes an octave hold 1 − e^(−x) to 1/255 (ours).

**Default (R1):**
- *Rate:* linear UNorm8, a fraction of the material's fastest; log2 at 32 codes an octave (0 meaning none) only beyond 30:1.
- *Amplitude:* linear UNorm8.
- *Reset year, 1850 to 2050:* per piece, a u16 of year × 16 + month from the pack's first year (the affordances' grid), so exact. The shader's date is float32, never half.
- *Age offset, to 40 years:* per piece, on the same grid. A per-texel onset, if R1 finds one, takes H1.a as biased quarter years (−16 to +47.75), costing r × 0.125 years: small for lichen and moss, 4/255 for the busiest polish at onset.

## 4. Charts, gutters and mips

At 80 m a 2 cm texel reads at about mip 1.5, a mip more at grazing angles (ours), so three mips suffice. A chart is clean at mip m with 2^m texels of padding and alignment. Unity pads lightmap UVs 4 pixels (secondary); xatlas offers padding and "Align charts to 4x4 blocks" (primary). Jylänki favours Shelf "only if implementation simplicity is a concern" (primary).

At 2 texels a side on a 4-texel grid, a 1.4 × 0.38 m tread at 2 cm wastes 27 %, a riser at 4 cm 64 %, a 40 × 25 cm wall stone two thirds; a run (a wall's face, a flight unrolled along its walking line) 10 to 15 % (ours).

**Default (R3):**
- Charts per run of one face kind, joints inside: rates and amplitudes are continuous across joints; resets are per piece.
- An unrolled flight gives its risers the treads' 2 cm: about what their padding costs, but finer than S3's rule. R3 measures both.
- 2 texels of padding; rectangles on a 4-texel grid, so no mip-0 BC block spans two charts; chunk regions on a 16-texel grid, so a regional rebake copies whole blocks.
- Barycentric fill, dilation over the whole page; three mips baked within each chart; trilinear, no anisotropy (the fields are smooth; marks come from UV2).
- Shelf packing; MaxRects if waste passes 150 ‰.

**xatlas:** not worth asking for: our charts are UV0 rectangles, and our packer stays deterministic. Ask if R3 finds overlapping islands (the brief's unknown 8), or when houses need unwrapping.

**Unknown:** shimmer at chart borders from mips 1 and 2 (R6).

## Sources

Ours: URP and Core 17.6 source (`unity/Library/PackageCache`); Unity 6000.6.6f1's `Contents/Frameworks`; `wear.py`, `growth.py`.

- [Renderer Shader User Value](https://docs.unity3d.com/6000.6/Documentation/Manual/renderer-shader-user-value-intro.html) · [SRP Batcher](https://docs.unity3d.com/6000.6/Documentation/Manual/SRPBatcher.html) · [its compatibility](https://docs.unity3d.com/6000.6/Documentation/Manual/SRPBatcher-Materials.html) · [CopyTexture](https://docs.unity3d.com/6000.6/Documentation/ScriptReference/Graphics.CopyTexture.html) · [CompressTexture](https://docs.unity3d.com/6000.6/Documentation/ScriptReference/EditorUtility.CompressTexture.html) · [Texture2D.Compress](https://docs.unity3d.com/6000.6/Documentation/ScriptReference/Texture2D.Compress.html) · [Import settings](https://docs.unity3d.com/6000.6/Documentation/Manual/texture-type-default.html) · [Lightmap UVs](https://docs.unity3d.com/Manual/LightingGiUvs-Reference.html)
- [Reed, BCn formats](https://www.reedbeta.com/blog/understanding-bcn-texture-compression-formats/) · [Microsoft, BC7 modes](https://learn.microsoft.com/en-us/windows/win32/direct3d11/bc7-format-mode-reference) · [Apple forum, BC on macOS](https://developer.apple.com/forums/thread/693265)
- [Gu et al., STAF format](https://www.cs.columbia.edu/CAVE/databases/staf/STAF_format.html) · [Lagarde, wet surfaces](https://seblagarde.wordpress.com/2013/04/14/water-drop-3b-physically-based-wet-surfaces/) · [Vlachos, water flow](https://alex.vlachos.com/graphics/Vlachos-SIGGRAPH10-WaterFlow.pdf)
- [xatlas](https://github.com/jpcy/xatlas) · [Jylänki, rectangle packing](https://github.com/juj/RectangleBinPack)
