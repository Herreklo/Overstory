# Frame time: the corner, run 1

2026-10-22 08:50:50, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 328 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| quad-bc7-street@1300-drizzle | 13.8 / 14.0 | 12.4 / 12.7 | 24.6 / 25.1 | 0.70 | 0.47 | 18,101 | 40 | 40 | 0 | 300 |
| quad-bc7-street@1300-drizzle/history-off | 13.2 / 13.3 | 12.0 / 12.2 | 23.7 / 24.2 | 0.45 | 0.38 | 18,101 | 40 | 40 | 0 | 299 |
| quad-bc7-tile8-street@1300-drizzle | 15.5 / 15.9 | 13.7 / 14.1 | 27.0 / 27.8 | 0.37 | 0.35 | 18,101 | 40 | 40 | 0 | 299 |
| quad-bc7-tile8-street@1300-drizzle/history-off | 13.2 / 13.3 | 12.0 / 12.3 | 23.6 / 24.1 | 0.33 | 0.33 | 18,101 | 40 | 40 | 0 | 299 |
| quad-bc7-nearmip-street@1300-drizzle | 13.9 / 14.0 | 12.4 / 12.8 | 24.6 / 25.1 | 0.70 | 0.47 | 18,101 | 40 | 40 | 0 | 299 |
| quad-bc7-nearmip-street@1300-drizzle/history-off | 13.2 / 13.3 | 12.0 / 12.3 | 23.8 / 24.2 | 0.65 | 0.41 | 18,101 | 40 | 40 | 0 | 300 |
| quad-bc7-nearmip-tile8-street@1300-drizzle | 15.7 / 16.1 | 13.8 / 14.2 | 27.2 / 28.0 | 0.65 | 0.45 | 18,101 | 40 | 40 | 0 | 300 |
| quad-bc7-nearmip-tile8-street@1300-drizzle/history-off | 13.3 / 13.4 | 12.0 / 12.3 | 23.7 / 24.1 | 0.66 | 0.45 | 18,101 | 40 | 40 | 0 | 299 |
| quad-bc7-tri-street@1300-drizzle | 13.9 / 14.1 | 12.5 / 12.8 | 24.7 / 25.2 | 0.53 | 0.39 | 18,101 | 40 | 40 | 0 | 301 |
| quad-bc7-tri-street@1300-drizzle/history-off | 13.2 / 13.6 | 12.0 / 12.2 | 23.8 / 24.1 | 0.66 | 0.44 | 18,101 | 40 | 40 | 0 | 300 |
| quad-bc7-tri-tile8-street@1300-drizzle | 15.8 / 16.0 | 13.8 / 14.2 | 27.1 / 27.9 | 0.71 | 0.48 | 18,101 | 40 | 40 | 0 | 301 |
| quad-bc7-tri-tile8-street@1300-drizzle/history-off | 13.2 / 13.4 | 12.0 / 12.6 | 23.8 / 24.3 | 0.70 | 0.47 | 18,101 | 40 | 40 | 0 | 300 |
| quad-bc7-lod-street@1300-drizzle | 13.8 / 14.0 | 12.5 / 13.0 | 24.7 / 25.1 | 0.65 | 0.45 | 18,101 | 40 | 40 | 0 | 300 |
| quad-bc7-lod-street@1300-drizzle/history-off | 13.2 / 13.3 | 12.0 / 12.6 | 23.8 / 24.2 | 0.63 | 0.45 | 18,101 | 40 | 40 | 0 | 300 |
| quad-bc7-lod-tile8-street@1300-drizzle | 15.7 / 16.0 | 13.8 / 14.7 | 27.3 / 28.5 | 0.69 | 0.46 | 18,101 | 40 | 40 | 0 | 300 |
| quad-bc7-lod-tile8-street@1300-drizzle/history-off | 13.2 / 13.4 | 12.0 / 12.5 | 23.7 / 24.2 | 0.65 | 0.44 | 18,101 | 40 | 40 | 0 | 300 |
| quad-bc7-grad-street@1300-drizzle | 14.1 / 14.2 | 12.7 / 13.2 | 25.1 / 25.6 | 0.61 | 0.43 | 18,101 | 40 | 40 | 0 | 301 |
| quad-bc7-grad-street@1300-drizzle/history-off | 13.3 / 13.4 | 12.0 / 12.6 | 23.8 / 24.2 | 0.64 | 0.45 | 18,101 | 40 | 40 | 0 | 300 |
| quad-bc7-grad-tile8-street@1300-drizzle | 16.0 / 16.3 | 14.1 / 14.5 | 27.8 / 28.3 | 0.63 | 0.43 | 18,101 | 40 | 40 | 0 | 301 |
| quad-bc7-grad-tile8-street@1300-drizzle/history-off | 13.2 / 13.5 | 12.0 / 12.6 | 23.7 / 24.2 | 0.66 | 0.46 | 18,101 | 40 | 40 | 0 | 302 |
| quad-bc7-direct-street@1300-drizzle | 13.8 / 14.0 | 12.5 / 13.0 | 24.8 / 25.3 | 0.67 | 0.44 | 18,101 | 40 | 40 | 0 | 301 |
| quad-bc7-direct-street@1300-drizzle/history-off | 13.2 / 13.5 | 12.0 / 12.6 | 23.9 / 24.3 | 0.66 | 0.44 | 18,101 | 40 | 40 | 0 | 301 |
| quad-bc7-direct-tile8-street@1300-drizzle | 15.6 / 16.0 | 13.8 / 14.3 | 27.1 / 28.2 | 0.68 | 0.46 | 18,101 | 40 | 40 | 0 | 301 |
| quad-bc7-direct-tile8-street@1300-drizzle/history-off | 13.2 / 13.4 | 12.0 / 12.6 | 23.7 / 24.2 | 0.66 | 0.44 | 18,101 | 40 | 40 | 0 | 301 |
| quad-bc7-tex2d-street@1300-drizzle | 13.8 / 14.1 | 12.5 / 13.0 | 24.7 / 25.3 | 0.67 | 0.45 | 18,101 | 40 | 40 | 0 | 301 |
| quad-bc7-tex2d-street@1300-drizzle/history-off | 13.2 / 14.7 | 12.0 / 12.5 | 23.7 / 24.1 | 0.70 | 0.47 | 18,101 | 40 | 40 | 0 | 302 |
| quad-bc7-tex2d-tile8-street@1300-drizzle | 15.6 / 15.9 | 13.8 / 14.2 | 27.2 / 27.9 | 0.66 | 0.44 | 18,101 | 40 | 40 | 0 | 301 |
| quad-bc7-tex2d-tile8-street@1300-drizzle/history-off | 13.2 / 13.4 | 12.0 / 12.6 | 23.7 / 24.2 | 0.65 | 0.45 | 18,101 | 40 | 40 | 0 | 303 |
| quad-bc7-alu-street@1300-drizzle | 13.3 / 13.4 | 12.1 / 12.6 | 24.1 / 24.4 | 0.67 | 0.46 | 18,101 | 40 | 40 | 0 | 302 |
| quad-bc7-alu-street@1300-drizzle/history-off | 13.2 / 13.3 | 12.0 / 12.6 | 23.8 / 24.1 | 0.61 | 0.44 | 18,101 | 40 | 40 | 0 | 303 |
| quad-bc7-alu-tile8-street@1300-drizzle | 13.6 / 13.7 | 12.3 / 12.8 | 24.4 / 24.8 | 0.71 | 0.48 | 18,101 | 40 | 40 | 0 | 302 |
| quad-bc7-alu-tile8-street@1300-drizzle/history-off | 13.2 / 13.4 | 12.0 / 12.5 | 23.8 / 24.2 | 0.71 | 0.47 | 18,101 | 40 | 40 | 0 | 302 |
| quad-bc7-two-street@1300-drizzle | 13.9 / 14.0 | 12.4 / 13.0 | 24.7 / 25.1 | 0.67 | 0.46 | 18,101 | 40 | 40 | 0 | 302 |
| quad-bc7-two-street@1300-drizzle/history-off | 13.2 / 13.4 | 12.0 / 12.5 | 23.9 / 24.1 | 0.67 | 0.47 | 18,101 | 40 | 40 | 0 | 302 |
| quad-bc7-two-tile8-street@1300-drizzle | 15.7 / 15.8 | 13.8 / 14.3 | 27.3 / 27.9 | 0.59 | 0.44 | 18,101 | 40 | 40 | 0 | 302 |
| quad-bc7-two-tile8-street@1300-drizzle/history-off | 13.2 / 13.3 | 12.0 / 12.5 | 23.7 / 24.1 | 0.69 | 0.47 | 18,101 | 40 | 40 | 0 | 303 |
| quad-bc7-two-tri-street@1300-drizzle | 13.8 / 14.0 | 12.4 / 13.0 | 24.7 / 25.1 | 0.64 | 0.44 | 18,101 | 40 | 40 | 0 | 302 |
| quad-bc7-two-tri-street@1300-drizzle/history-off | 13.2 / 13.4 | 12.0 / 12.6 | 23.8 / 24.1 | 0.63 | 0.45 | 18,101 | 40 | 40 | 0 | 302 |
| quad-bc7-two-tri-tile8-street@1300-drizzle | 15.7 / 15.9 | 13.9 / 14.2 | 27.2 / 28.0 | 0.64 | 0.45 | 18,101 | 40 | 40 | 0 | 303 |
| quad-bc7-two-tri-tile8-street@1300-drizzle/history-off | 13.2 / 13.4 | 12.0 / 12.6 | 23.7 / 24.2 | 0.67 | 0.47 | 18,101 | 40 | 40 | 0 | 303 |
| quad-bc7-two-nearmip-street@1300-drizzle | 13.8 / 15.5 | 12.5 / 12.9 | 24.6 / 25.1 | 0.62 | 0.44 | 18,101 | 40 | 40 | 0 | 303 |
| quad-bc7-two-nearmip-street@1300-drizzle/history-off | 13.2 / 13.4 | 12.0 / 12.5 | 23.8 / 24.3 | 0.71 | 0.47 | 18,101 | 40 | 40 | 0 | 303 |
| quad-bc7-two-nearmip-tile8-street@1300-drizzle | 15.8 / 16.0 | 14.0 / 14.4 | 27.6 / 28.4 | 0.70 | 0.47 | 18,101 | 40 | 40 | 0 | 303 |
| quad-bc7-two-nearmip-tile8-street@1300-drizzle/history-off | 13.3 / 13.4 | 12.0 / 12.6 | 23.7 / 24.2 | 0.67 | 0.47 | 18,101 | 40 | 40 | 0 | 303 |
| quad-rgba8-street@1300-drizzle | 13.9 / 14.2 | 12.4 / 13.0 | 24.8 / 25.1 | 0.61 | 0.43 | 18,101 | 40 | 40 | 0 | 303 |
| quad-rgba8-street@1300-drizzle/history-off | 13.2 / 13.4 | 12.0 / 12.5 | 23.9 / 24.2 | 0.60 | 0.43 | 18,101 | 40 | 40 | 0 | 304 |
| quad-rgba8-tile8-street@1300-drizzle | 15.7 / 15.9 | 13.8 / 14.3 | 27.3 / 27.8 | 0.65 | 0.44 | 18,101 | 40 | 40 | 0 | 303 |
| quad-rgba8-tile8-street@1300-drizzle/history-off | 13.2 / 13.4 | 12.0 / 12.6 | 23.7 / 24.2 | 0.61 | 0.44 | 18,101 | 40 | 40 | 0 | 303 |
| quad-rgba8-tri-street@1300-drizzle | 13.9 / 14.0 | 12.5 / 13.0 | 24.8 / 25.1 | 0.61 | 0.44 | 18,101 | 40 | 40 | 0 | 304 |
| quad-rgba8-tri-street@1300-drizzle/history-off | 13.2 / 13.4 | 12.0 / 12.6 | 23.8 / 24.1 | 0.59 | 0.44 | 18,101 | 40 | 40 | 0 | 304 |
| quad-rgba8-tri-tile8-street@1300-drizzle | 15.7 / 15.9 | 13.8 / 14.2 | 27.2 / 27.8 | 0.62 | 0.44 | 18,101 | 40 | 40 | 0 | 304 |
| quad-rgba8-tri-tile8-street@1300-drizzle/history-off | 13.2 / 13.4 | 12.0 / 12.6 | 23.7 / 24.2 | 0.61 | 0.42 | 18,101 | 40 | 40 | 0 | 304 |
| quad-rgba8-nearmip-street@1300-drizzle | 13.9 / 14.0 | 12.5 / 13.0 | 24.8 / 25.1 | 0.65 | 0.45 | 18,101 | 40 | 40 | 0 | 305 |
| quad-rgba8-nearmip-street@1300-drizzle/history-off | 13.3 / 13.4 | 12.0 / 12.6 | 23.9 / 24.2 | 0.64 | 0.45 | 18,101 | 40 | 40 | 0 | 305 |
| quad-rgba8-nearmip-tile8-street@1300-drizzle | 15.7 / 15.9 | 13.9 / 14.3 | 27.3 / 28.0 | 0.68 | 0.47 | 18,101 | 40 | 40 | 0 | 305 |
| quad-rgba8-nearmip-tile8-street@1300-drizzle/history-off | 13.2 / 13.4 | 12.0 / 12.5 | 23.7 / 24.2 | 0.65 | 0.44 | 18,101 | 40 | 40 | 0 | 305 |
