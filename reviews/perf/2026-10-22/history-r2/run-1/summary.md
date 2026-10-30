# Frame time: the corner, run 1

2026-10-22 08:04:08, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 124 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eye-on@1300-drizzle/flat | 1.9 / 2.1 | 1.7 / 2.1 | 2.1 / 2.5 | 0.21 | 0.07 | 2,890,132 | 20 | 2 | 0 | 295 |
| street@1300-drizzle/flat | 2.0 / 2.1 | 1.7 / 2.1 | 2.1 / 2.7 | 0.20 | 0.07 | 2,890,132 | 20 | 2 | 0 | 296 |
| eye-on@1300-drizzle | 40.7 / 43.3 | 32.6 / 38.7 | 57.2 / 64.6 | 0.61 | 0.49 | 15,907,493 | 139 | 63 | 63 | 297 |
| street@1300-drizzle | 39.4 / 44.6 | 32.9 / 39.3 | 58.0 / 65.4 | 0.74 | 0.53 | 15,634,387 | 142 | 65 | 66 | 296 |
| eye-on@1300-drizzle/history-off | 40.6 / 42.4 | 33.5 / 39.8 | 58.6 / 65.7 | 0.98 | 0.64 | 15,907,493 | 139 | 63 | 63 | 297 |
| street@1300-drizzle/history-off | 41.0 / 48.8 | 33.7 / 39.7 | 60.8 / 65.7 | 1.01 | 0.62 | 15,634,387 | 142 | 65 | 66 | 296 |
| eye-on@1300-drizzle/haze-off | 39.1 / 47.3 | 33.3 / 42.1 | 56.7 / 66.6 | 1.02 | 0.63 | 15,907,493 | 139 | 63 | 63 | 297 |
| street@1300-drizzle/haze-off | 39.4 / 40.3 | 33.4 / 41.0 | 59.0 / 66.1 | 0.85 | 0.57 | 15,634,387 | 142 | 65 | 66 | 296 |
| quad-rgba8-street@1300-drizzle | 14.1 / 14.4 | 12.8 / 13.6 | 25.1 / 26.3 | 0.36 | 0.35 | 18,101 | 40 | 40 | 0 | 296 |
| quad-rgba8-street@1300-drizzle/history-off | 13.3 / 13.6 | 12.1 / 12.7 | 23.9 / 24.4 | 0.39 | 0.36 | 18,101 | 40 | 40 | 0 | 297 |
| quad-bc7-street@1300-drizzle | 13.9 / 14.1 | 12.4 / 13.0 | 24.6 / 25.2 | 0.42 | 0.36 | 18,101 | 40 | 40 | 0 | 297 |
| quad-bc7-street@1300-drizzle/history-off | 13.4 / 14.1 | 12.1 / 12.7 | 23.7 / 24.5 | 0.41 | 0.37 | 18,101 | 40 | 40 | 0 | 297 |
