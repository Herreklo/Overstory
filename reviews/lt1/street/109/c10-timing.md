Offscreen in the editor, batch mode (LT1Street.Timing; Apple M4, 2560x1440, MSAA 4x, way Pc, low sun, one 4096 shadow cascade, screen-space occlusion; median of 6 batches of 6). A row of 50 copies of house 109 on 9.0 m plots, near level within 10 m, city level from 60 m. Not the player's frame.

City level one mesh, one material; far shadows dropped beyond the shadow distance and the shadow's reach.

| View | Houses | Near | City | Casting none | Triangles in view | Draws in view (counted) | Renderer: draw calls / batches / set-pass / shadow casters | ms a frame | Batches |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| street | 50 | 0 | 44 | 44 | 37,808 | 28 | - / - / - / - | 4.5 | 4.4 4.5 4.5 4.5 4.6 4.6 |
| raised | 50 | 0 | 45 | 44 | 41,404 | 31 | - / - / - / - | 4.6 | 4.5 4.5 4.6 4.6 4.7 4.7 |
| along | 50 | 0 | 44 | 38 | 89,624 | 86 | - / - / - / - | 5.2 | 5.0 5.1 5.2 5.2 5.2 5.2 |
| near3 | 50 | 3 | 42 | 43 | 169,142 | 28 | - / - / - / - | 5.5 | 5.3 5.4 5.4 5.5 5.6 5.7 |

Textures streamed (GPU, counted, not measured: the mip each house's page would hold at its nearest point for 128 px/m at 2560x1440, at most 4 mips dropped, the quality setting; one shared stroke texture):

| View | MB streamed | Houses at mip 0 / 1 / ... / 4 | MB all at full |
| --- | --- | --- | --- |
| street | 294 | 3 / 1 / 0 / 0 / 46 | 4268 |
| raised | 315 | 3 / 2 / 0 / 0 / 45 | 4268 |
| along | 287 | 2 / 3 / 5 / 11 / 29 | 4268 |
| near3 | 358 | 4 / 0 / 0 / 0 / 46 | 4268 |

One house's page on the GPU at full: 85.3 MB, at mip 4 and down 0.33 MB; shared strokes 1.3 MB.

One house, as the editor counts it (a CPU copy beside the GPU's): textures 173.3 MB (hist-p 4096x4096 BC7 42.7 MB; geo 4096x4096 BC7 42.7 MB; street-normal 4096x4096 BC7 42.7 MB; paint-stroke 1024x1024 BC7 2.7 MB; hist-p2 4096x4096 BC7 42.7 MB; mattab-P 7x12 RGBAFloat 0.0 MB; mattab-Pc 7x12 RGBAFloat 0.0 MB); meshes, every level, 9.7 MB.
