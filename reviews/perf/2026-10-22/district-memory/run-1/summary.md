# Frame time: the corner, run 1

2026-10-22 00:48:27, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 1 rounds of 20 frames a segment, each after 10 warm-up, after 60 frames to settle; 27 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

The district: 2048 m square, 8,960 plots in 1024 chunks of 64 m (2112 meshes), 708 MB on disk, loaded in 0.7 s (953 MB/s); a chunk 0.34 ms (95th 4.10, worst 9.24), a core chunk 5.46 ms (95th 8.29); triangles: L0 9,193,684, shells 119,266, ground 2,097,152; resident memory 359 MB before, 579 MB after; footprint (GPU memory included) 1407 MB before, 2281 MB after, 2583 MB at the end.

Rebuilding c_18_14.bin (264,820 triangles, 553,476 vertices, 1384 parts): placed in C# 23.83 ms, as a Burst job 1.77 ms (Burst on), uploaded 1.27 ms. A 1024 by 512 history page: drawn 0.75 ms, read back 0.69 ms, compressed to DXT5 8.3 ms (fast 5.2 ms).

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| district-l0-street@1300-drizzle | 34.0 / 35.3 | 28.8 / 35.2 | 47.9 / 55.9 | 0.62 | 0.58 | 12,858,397 | 1017 | 46 | 33 | 257 |
| district-l0-city@1300-drizzle | 54.1 / 55.3 | 43.0 / 54.8 | 78.3 / 88.0 | 0.69 | 0.70 | 15,508,813 | 958 | 43 | 2 | 258 |
| district-l0-street@1600-low-sun | 94.5 / 95.5 | 80.5 / 88.0 | 148.7 / 156.3 | 0.78 | 0.73 | 15,353,621 | 1046 | 47 | 61 | 259 |
| district-l0-city@1600-low-sun | 111.8 / 112.9 | 93.3 / 105.9 | 177.4 / 186.0 | 1.23 | 1.05 | 15,336,433 | 958 | 44 | 1 | 240 |
| district-l0-street@1750-blue-hour | 27.0 / 27.7 | 23.1 / 28.1 | 41.0 / 45.9 | 0.52 | 0.57 | 8,126,001 | 984 | 42 | 0 | 240 |
| district-l0-city@1750-blue-hour | 46.8 / 48.4 | 38.2 / 49.7 | 66.7 / 73.6 | 1.42 | 1.20 | 15,082,465 | 956 | 42 | 0 | 241 |
