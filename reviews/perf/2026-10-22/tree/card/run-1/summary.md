# Frame time: the walk's corner in the town, run 1

2026-10-22 19:52:48, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 77 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| street@1300-drizzle | 40.9 / 42.1 | 33.6 / 39.8 | 60.5 / 65.7 | 1.04 | 0.62 | 15,753,077 | 148 | 63 | 70 | 280 |
| high@1300-drizzle | 45.2 / 46.8 | 36.8 / 42.2 | 68.1 / 72.7 | 1.06 | 0.62 | 14,298,459 | 130 | 57 | 54 | 281 |
| street@1300-drizzle-nobirch | 28.4 / 29.6 | 23.4 / 30.6 | 41.5 / 45.8 | 1.02 | 0.59 | 15,246,161 | 134 | 49 | 62 | 281 |
| high@1300-drizzle-nobirch | 29.1 / 30.1 | 23.8 / 29.4 | 43.4 / 47.0 | 1.02 | 0.58 | 13,951,323 | 120 | 47 | 50 | 282 |
