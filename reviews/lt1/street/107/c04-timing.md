Offscreen in the editor, batch mode (LT1Street.Timing; Apple M4, 2560x1440, MSAA 4x, way Pc, low sun, one 4096 shadow cascade, screen-space occlusion; median of 6 batches of 6). A row of 50 copies of house 107 on 7.0 m plots, near level within 10 m, city level from 60 m. Not the player's frame.

City level one mesh, one material; far shadows dropped beyond the shadow distance and the shadow's reach.

| View | Houses | Near | City | Casting none | Triangles in view | Draws in view (counted) | Renderer: draw calls / batches / set-pass / shadow casters | ms a frame | Batches |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| street | 50 | 0 | 43 | 43 | 24,960 | 43 | - / - / - / - | 3.6 | 3.5 3.6 3.6 3.6 3.6 3.7 |
| raised | 50 | 0 | 43 | 43 | 28,109 | 51 | - / - / - / - | 4.1 | 4.0 4.1 4.1 4.1 4.2 4.3 |
| along | 50 | 0 | 42 | 35 | 80,532 | 127 | - / - / - / - | 4.8 | 4.6 4.6 4.7 4.8 4.8 4.9 |

Textures streamed (GPU, counted, not measured: the mip each house's page would hold at its nearest point for 128 px/m at 2560x1440, at most 4 mips dropped, the quality setting; one shared stroke texture):

| View | MB streamed | Houses at mip 0 / 1 / ... / 4 | MB all at full |
| --- | --- | --- | --- |
| street | 91 | 4 / 0 / 0 / 0 / 46 | 1068 |
| raised | 80 | 3 / 2 / 0 / 0 / 45 | 1068 |
| along | 97 | 3 / 3 / 7 / 13 / 24 | 1068 |

One house's page on the GPU at full: 21.3 MB, at mip 4 and down 0.08 MB; shared strokes 1.3 MB.

One house, as the editor counts it (a CPU copy beside the GPU's): textures 45.3 MB (hist-p 2048x2048 BC7 10.7 MB; geo 2048x2048 BC7 10.7 MB; street-normal 2048x2048 BC7 10.7 MB; paint-stroke 1024x1024 BC7 2.7 MB; hist-p2 2048x2048 BC7 10.7 MB; mattab-P 7x11 RGBAFloat 0.0 MB; mattab-Pc 7x11 RGBAFloat 0.0 MB); meshes, every level, 5.1 MB.
