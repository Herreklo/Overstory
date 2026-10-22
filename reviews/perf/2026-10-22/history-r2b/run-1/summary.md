# Frame time: the corner, run 1

2026-10-22 08:33:34, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 120 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| quad-rgba8-street@1300-drizzle | 13.9 / 14.0 | 12.4 / 13.1 | 24.5 / 25.6 | 1.18 | 0.60 | 18,101 | 40 | 40 | 0 | 293 |
| quad-rgba8-street@1300-drizzle/history-off | 13.5 / 15.4 | 12.0 / 12.9 | 23.6 / 25.2 | 0.80 | 0.50 | 18,101 | 40 | 40 | 0 | 294 |
| quad-bc7-street@1300-drizzle | 13.9 / 14.1 | 12.4 / 12.9 | 24.6 / 25.4 | 0.78 | 0.50 | 18,101 | 40 | 40 | 0 | 293 |
| quad-bc7-street@1300-drizzle/history-off | 13.3 / 14.0 | 11.9 / 12.4 | 23.5 / 24.2 | 0.73 | 0.48 | 18,101 | 40 | 40 | 0 | 295 |
| quad-rgba8-half-street@1300-drizzle | 5.2 / 5.7 | 12.5 / 13.3 | 24.6 / 26.1 | 0.73 | 0.48 | 18,101 | 40 | 40 | 0 | 294 |
| quad-rgba8-half-street@1300-drizzle/history-off | 4.8 / 5.0 | 12.0 / 12.6 | 23.7 / 24.6 | 0.39 | 0.35 | 18,101 | 40 | 40 | 0 | 295 |
| quad-bc7-half-street@1300-drizzle | 5.1 / 5.3 | 12.4 / 12.9 | 24.5 / 25.5 | 0.70 | 0.45 | 18,101 | 40 | 40 | 0 | 294 |
| quad-bc7-half-street@1300-drizzle/history-off | 4.9 / 5.1 | 12.0 / 12.5 | 23.6 / 24.5 | 0.71 | 0.46 | 18,101 | 40 | 40 | 0 | 294 |
| quad-rgba8-two-street@1300-drizzle | 14.2 / 15.7 | 12.6 / 13.8 | 24.6 / 27.3 | 0.64 | 0.43 | 18,101 | 40 | 40 | 0 | 294 |
| quad-rgba8-two-street@1300-drizzle/history-off | 13.2 / 13.6 | 12.1 / 13.0 | 23.7 / 25.7 | 0.75 | 0.46 | 18,101 | 40 | 40 | 0 | 294 |
| quad-bc7-two-street@1300-drizzle | 13.9 / 14.3 | 12.4 / 12.9 | 24.6 / 25.3 | 0.68 | 0.44 | 18,101 | 40 | 40 | 0 | 295 |
| quad-bc7-two-street@1300-drizzle/history-off | 13.3 / 14.0 | 12.0 / 12.5 | 23.7 / 24.6 | 0.58 | 0.42 | 18,101 | 40 | 40 | 0 | 295 |
| quad-rgba8-tile4-street@1300-drizzle | 15.1 / 15.2 | 13.3 / 13.8 | 26.1 / 27.1 | 0.72 | 0.47 | 18,101 | 40 | 40 | 0 | 295 |
| quad-rgba8-tile4-street@1300-drizzle/history-off | 13.3 / 13.7 | 12.0 / 12.6 | 23.7 / 24.7 | 0.75 | 0.48 | 18,101 | 40 | 40 | 0 | 297 |
| quad-bc7-tile4-street@1300-drizzle | 15.3 / 15.6 | 13.4 / 14.2 | 26.1 / 27.8 | 0.82 | 0.51 | 18,101 | 40 | 40 | 0 | 295 |
| quad-bc7-tile4-street@1300-drizzle/history-off | 13.4 / 13.6 | 12.1 / 12.8 | 23.7 / 25.2 | 0.78 | 0.50 | 18,101 | 40 | 40 | 0 | 296 |
| quad-rgba8-tile8-street@1300-drizzle | 15.7 / 16.1 | 13.9 / 15.0 | 27.0 / 29.2 | 0.80 | 0.48 | 18,101 | 40 | 40 | 0 | 295 |
| quad-rgba8-tile8-street@1300-drizzle/history-off | 13.5 / 13.6 | 12.0 / 12.7 | 23.7 / 24.8 | 0.72 | 0.45 | 18,101 | 40 | 40 | 0 | 296 |
| quad-bc7-tile8-street@1300-drizzle | 15.8 / 16.1 | 13.8 / 14.5 | 27.0 / 28.5 | 0.69 | 0.45 | 18,101 | 40 | 40 | 0 | 295 |
| quad-bc7-tile8-street@1300-drizzle/history-off | 13.5 / 13.7 | 12.1 / 12.7 | 23.6 / 24.8 | 0.65 | 0.43 | 18,101 | 40 | 40 | 0 | 295 |
