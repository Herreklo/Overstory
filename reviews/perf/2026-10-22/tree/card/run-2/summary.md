# Frame time: the walk's corner in the town, run 2

2026-10-22 19:54:09, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 76 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| street@1300-drizzle | 39.7 / 40.8 | 33.3 / 38.9 | 60.0 / 64.7 | 0.98 | 0.62 | 15,753,077 | 148 | 63 | 70 | 280 |
| high@1300-drizzle | 44.0 / 45.2 | 36.5 / 42.2 | 67.6 / 72.1 | 1.13 | 0.70 | 14,298,459 | 130 | 57 | 54 | 281 |
| street@1300-drizzle-nobirch | 28.6 / 30.2 | 23.5 / 29.3 | 41.3 / 46.2 | 1.01 | 0.61 | 15,246,161 | 134 | 49 | 62 | 281 |
| high@1300-drizzle-nobirch | 28.8 / 30.2 | 23.8 / 29.2 | 42.9 / 46.9 | 1.01 | 0.60 | 13,951,323 | 120 | 47 | 50 | 282 |
