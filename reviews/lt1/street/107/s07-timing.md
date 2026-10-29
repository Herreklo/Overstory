Offscreen in the editor, batch mode (LT1Street.Timing; Apple M4, 2560x1440, MSAA 4x, way Pc, low sun, one 4096 shadow cascade, screen-space occlusion; median of 6 batches of 6). A row of 50 copies of house 107 on 7.0 m plots, near level within 10 m. Not the player's frame.

| View | Houses | Near | Triangles in view | Draws in view | ms a frame | Batches |
| --- | --- | --- | --- | --- | --- | --- |
| street | 50 | 0 | 24,960 | 43 | 3.8 | 3.8 3.8 3.8 3.8 3.8 4.0 |
| raised | 50 | 0 | 28,109 | 51 | 4.4 | 4.3 4.3 4.4 4.4 4.4 4.5 |
| along | 50 | 0 | 312,456 | 547 | 10.3 | 10.2 10.2 10.3 10.3 10.5 10.6 |

Textures streamed (GPU, counted, not measured: the mip each house's page would hold at its nearest point for 128 px/m at 2560x1440, at most 2 mips dropped, the quality setting; one shared stroke texture):

| View | MB streamed | Houses at mip 0 / 1 / ... / 2 | MB all at full |
| --- | --- | --- | --- |
| street | 148 | 4 / 0 / 46 | 1068 |
| raised | 136 | 3 / 2 / 45 | 1068 |
| along | 140 | 3 / 3 / 44 | 1068 |

One house's page on the GPU at full: 21.3 MB, at mip 2 and down 1.33 MB; shared strokes 1.3 MB.

One house, as the editor counts it (a CPU copy beside the GPU's): textures 45.3 MB (hist-p 2048x2048 BC7 10.7 MB; geo 2048x2048 BC7 10.7 MB; street-normal 2048x2048 BC7 10.7 MB; paint-stroke 1024x1024 BC7 2.7 MB; hist-p2 2048x2048 BC7 10.7 MB); meshes, both levels, 4.9 MB.
