# Frame time: the corner, run 2

2026-10-22 09:18:50, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 393 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| quad-bc7-street@1300-drizzle | 13.8 / 13.9 | 12.4 / 13.0 | 24.7 / 25.0 | 0.37 | 0.35 | 18,101 | 40 | 40 | 0 | 300 |
| quad-bc7-street@1300-drizzle/history-off | 13.2 / 13.3 | 12.0 / 12.6 | 23.8 / 24.1 | 0.36 | 0.35 | 18,101 | 40 | 40 | 0 | 300 |
| quad-bc7-tile8-street@1300-drizzle | 15.6 / 15.9 | 13.7 / 14.2 | 27.0 / 27.6 | 0.36 | 0.34 | 18,101 | 40 | 40 | 0 | 300 |
| quad-bc7-tile8-street@1300-drizzle/history-off | 13.2 / 13.4 | 11.9 / 12.6 | 23.9 / 24.1 | 0.36 | 0.34 | 18,101 | 40 | 40 | 0 | 300 |
| quad-bc7-nearmip-street@1300-drizzle | 13.8 / 14.0 | 12.4 / 13.0 | 24.7 / 25.0 | 0.35 | 0.34 | 18,101 | 40 | 40 | 0 | 300 |
| quad-bc7-nearmip-street@1300-drizzle/history-off | 13.2 / 13.3 | 11.9 / 12.6 | 23.7 / 24.1 | 0.36 | 0.34 | 18,101 | 40 | 40 | 0 | 300 |
| quad-bc7-nearmip-tile8-street@1300-drizzle | 15.6 / 15.8 | 13.7 / 14.2 | 27.1 / 27.7 | 0.36 | 0.34 | 18,101 | 40 | 40 | 0 | 301 |
| quad-bc7-nearmip-tile8-street@1300-drizzle/history-off | 13.2 / 13.3 | 12.0 / 12.6 | 23.9 / 24.1 | 0.36 | 0.35 | 18,101 | 40 | 40 | 0 | 300 |
| quad-bc7-tri-street@1300-drizzle | 13.8 / 14.0 | 12.4 / 13.0 | 24.7 / 25.0 | 0.36 | 0.34 | 18,101 | 40 | 40 | 0 | 302 |
| quad-bc7-tri-street@1300-drizzle/history-off | 13.2 / 13.5 | 11.9 / 12.7 | 23.8 / 24.1 | 0.35 | 0.35 | 18,101 | 40 | 40 | 0 | 301 |
| quad-bc7-tri-tile8-street@1300-drizzle | 15.6 / 15.8 | 13.7 / 14.2 | 27.1 / 27.7 | 0.37 | 0.35 | 18,101 | 40 | 40 | 0 | 302 |
| quad-bc7-tri-tile8-street@1300-drizzle/history-off | 13.2 / 13.3 | 12.0 / 12.6 | 23.8 / 24.1 | 0.36 | 0.34 | 18,101 | 40 | 40 | 0 | 301 |
| quad-bc7-lod-street@1300-drizzle | 13.8 / 13.9 | 12.4 / 13.0 | 24.7 / 25.0 | 0.34 | 0.34 | 18,101 | 40 | 40 | 0 | 302 |
| quad-bc7-lod-street@1300-drizzle/history-off | 13.2 / 13.3 | 12.0 / 12.7 | 23.8 / 24.1 | 0.36 | 0.34 | 18,101 | 40 | 40 | 0 | 301 |
| quad-bc7-lod-tile8-street@1300-drizzle | 15.6 / 15.7 | 13.7 / 14.2 | 27.1 / 27.6 | 0.37 | 0.34 | 18,101 | 40 | 40 | 0 | 301 |
| quad-bc7-lod-tile8-street@1300-drizzle/history-off | 13.2 / 13.4 | 12.0 / 12.7 | 23.9 / 24.2 | 0.36 | 0.34 | 18,101 | 40 | 40 | 0 | 301 |
| quad-bc7-grad-street@1300-drizzle | 14.0 / 14.1 | 12.6 / 13.2 | 25.0 / 25.4 | 0.35 | 0.34 | 18,101 | 40 | 40 | 0 | 302 |
| quad-bc7-grad-street@1300-drizzle/history-off | 13.2 / 13.3 | 12.0 / 12.6 | 23.7 / 24.1 | 0.35 | 0.34 | 18,101 | 40 | 40 | 0 | 301 |
| quad-bc7-grad-tile8-street@1300-drizzle | 16.0 / 16.1 | 14.0 / 14.5 | 27.6 / 28.2 | 0.36 | 0.34 | 18,101 | 40 | 40 | 0 | 303 |
| quad-bc7-grad-tile8-street@1300-drizzle/history-off | 13.2 / 13.3 | 12.0 / 12.6 | 23.9 / 24.1 | 0.36 | 0.34 | 18,101 | 40 | 40 | 0 | 302 |
| quad-bc7-direct-street@1300-drizzle | 13.8 / 13.9 | 12.4 / 13.0 | 24.7 / 25.0 | 0.36 | 0.34 | 18,101 | 40 | 40 | 0 | 303 |
| quad-bc7-direct-street@1300-drizzle/history-off | 13.2 / 13.4 | 12.0 / 12.6 | 23.6 / 24.1 | 0.35 | 0.34 | 18,101 | 40 | 40 | 0 | 302 |
| quad-bc7-direct-tile8-street@1300-drizzle | 15.5 / 15.7 | 13.7 / 14.2 | 27.1 / 27.6 | 0.36 | 0.34 | 18,101 | 40 | 40 | 0 | 302 |
| quad-bc7-direct-tile8-street@1300-drizzle/history-off | 13.2 / 13.3 | 12.0 / 12.6 | 23.9 / 24.2 | 0.34 | 0.34 | 18,101 | 40 | 40 | 0 | 302 |
| quad-bc7-tex2d-street@1300-drizzle | 13.8 / 13.9 | 12.4 / 13.0 | 24.7 / 25.0 | 0.35 | 0.35 | 18,101 | 40 | 40 | 0 | 302 |
| quad-bc7-tex2d-street@1300-drizzle/history-off | 13.2 / 13.3 | 12.0 / 12.7 | 23.7 / 24.1 | 0.35 | 0.35 | 18,101 | 40 | 40 | 0 | 302 |
| quad-bc7-tex2d-tile8-street@1300-drizzle | 15.5 / 15.8 | 13.7 / 14.2 | 27.0 / 27.6 | 0.35 | 0.35 | 18,101 | 40 | 40 | 0 | 303 |
| quad-bc7-tex2d-tile8-street@1300-drizzle/history-off | 13.2 / 13.4 | 11.9 / 12.6 | 23.8 / 24.1 | 0.35 | 0.34 | 18,101 | 40 | 40 | 0 | 302 |
| quad-bc7-alu-street@1300-drizzle | 13.3 / 13.4 | 12.2 / 12.8 | 24.2 / 24.4 | 0.35 | 0.34 | 18,101 | 40 | 40 | 0 | 304 |
| quad-bc7-alu-street@1300-drizzle/history-off | 13.2 / 13.3 | 12.0 / 12.6 | 23.8 / 24.2 | 0.34 | 0.34 | 18,101 | 40 | 40 | 0 | 303 |
| quad-bc7-alu-tile8-street@1300-drizzle | 13.6 / 13.7 | 12.3 / 12.9 | 24.4 / 24.8 | 0.34 | 0.34 | 18,101 | 40 | 40 | 0 | 304 |
| quad-bc7-alu-tile8-street@1300-drizzle/history-off | 13.2 / 13.3 | 11.9 / 12.6 | 23.9 / 24.2 | 0.34 | 0.34 | 18,101 | 40 | 40 | 0 | 303 |
| quad-bc7-two-street@1300-drizzle | 13.8 / 14.0 | 12.4 / 13.1 | 24.7 / 25.0 | 0.35 | 0.35 | 18,101 | 40 | 40 | 0 | 304 |
| quad-bc7-two-street@1300-drizzle/history-off | 13.2 / 13.3 | 12.0 / 12.6 | 23.8 / 24.2 | 0.34 | 0.34 | 18,101 | 40 | 40 | 0 | 303 |
| quad-bc7-two-tile8-street@1300-drizzle | 15.6 / 15.8 | 13.7 / 14.3 | 27.1 / 27.6 | 0.34 | 0.34 | 18,101 | 40 | 40 | 0 | 304 |
| quad-bc7-two-tile8-street@1300-drizzle/history-off | 13.2 / 13.3 | 11.9 / 12.6 | 23.8 / 24.1 | 0.34 | 0.34 | 18,101 | 40 | 40 | 0 | 303 |
| quad-bc7-two-tri-street@1300-drizzle | 13.8 / 13.9 | 12.4 / 13.0 | 24.7 / 25.0 | 0.34 | 0.35 | 18,101 | 40 | 40 | 0 | 304 |
| quad-bc7-two-tri-street@1300-drizzle/history-off | 13.1 / 13.3 | 11.9 / 12.6 | 23.7 / 24.1 | 0.35 | 0.34 | 18,101 | 40 | 40 | 0 | 303 |
| quad-bc7-two-tri-tile8-street@1300-drizzle | 15.6 / 15.7 | 13.8 / 14.3 | 27.3 / 27.7 | 0.35 | 0.34 | 18,101 | 40 | 40 | 0 | 305 |
| quad-bc7-two-tri-tile8-street@1300-drizzle/history-off | 13.2 / 13.3 | 12.0 / 12.6 | 23.9 / 24.1 | 0.35 | 0.34 | 18,101 | 40 | 40 | 0 | 304 |
| quad-bc7-two-nearmip-street@1300-drizzle | 13.8 / 13.8 | 12.4 / 13.0 | 24.7 / 25.0 | 0.34 | 0.34 | 18,101 | 40 | 40 | 0 | 305 |
| quad-bc7-two-nearmip-street@1300-drizzle/history-off | 13.2 / 13.3 | 12.0 / 12.6 | 23.7 / 24.1 | 0.35 | 0.34 | 18,101 | 40 | 40 | 0 | 304 |
| quad-bc7-two-nearmip-tile8-street@1300-drizzle | 15.7 / 15.8 | 13.8 / 14.3 | 27.3 / 27.8 | 0.34 | 0.34 | 18,101 | 40 | 40 | 0 | 305 |
| quad-bc7-two-nearmip-tile8-street@1300-drizzle/history-off | 13.2 / 13.3 | 11.9 / 12.6 | 23.8 / 24.1 | 0.34 | 0.34 | 18,101 | 40 | 40 | 0 | 304 |
| quad-rgba8-street@1300-drizzle | 13.8 / 14.0 | 12.4 / 13.1 | 24.9 / 25.1 | 0.33 | 0.34 | 18,101 | 40 | 40 | 0 | 304 |
| quad-rgba8-street@1300-drizzle/history-off | 13.2 / 13.3 | 12.0 / 12.6 | 23.8 / 24.1 | 0.34 | 0.34 | 18,101 | 40 | 40 | 0 | 304 |
| quad-rgba8-tile8-street@1300-drizzle | 15.6 / 15.7 | 13.7 / 14.3 | 27.1 / 27.6 | 0.35 | 0.34 | 18,101 | 40 | 40 | 0 | 304 |
| quad-rgba8-tile8-street@1300-drizzle/history-off | 13.2 / 13.2 | 12.0 / 12.6 | 23.9 / 24.1 | 0.34 | 0.34 | 18,101 | 40 | 40 | 0 | 305 |
| quad-rgba8-tri-street@1300-drizzle | 13.8 / 13.9 | 12.4 / 13.0 | 24.8 / 25.1 | 0.34 | 0.34 | 18,101 | 40 | 40 | 0 | 305 |
| quad-rgba8-tri-street@1300-drizzle/history-off | 13.2 / 13.4 | 11.9 / 12.6 | 23.7 / 24.1 | 0.34 | 0.34 | 18,101 | 40 | 40 | 0 | 305 |
| quad-rgba8-tri-tile8-street@1300-drizzle | 15.6 / 15.7 | 13.7 / 14.2 | 27.1 / 27.6 | 0.35 | 0.34 | 18,101 | 40 | 40 | 0 | 305 |
| quad-rgba8-tri-tile8-street@1300-drizzle/history-off | 13.2 / 13.3 | 12.0 / 12.6 | 23.8 / 24.2 | 0.34 | 0.34 | 18,101 | 40 | 40 | 0 | 305 |
| quad-rgba8-nearmip-street@1300-drizzle | 13.8 / 13.9 | 12.5 / 13.0 | 24.7 / 25.1 | 0.35 | 0.35 | 18,101 | 40 | 40 | 0 | 305 |
| quad-rgba8-nearmip-street@1300-drizzle/history-off | 13.2 / 13.3 | 11.9 / 12.6 | 23.7 / 24.1 | 0.35 | 0.34 | 18,101 | 40 | 40 | 0 | 305 |
| quad-rgba8-nearmip-tile8-street@1300-drizzle | 15.6 / 15.9 | 13.8 / 14.3 | 27.2 / 27.7 | 0.36 | 0.35 | 18,101 | 40 | 40 | 0 | 305 |
| quad-rgba8-nearmip-tile8-street@1300-drizzle/history-off | 13.2 / 13.4 | 12.0 / 12.6 | 23.9 / 24.2 | 0.35 | 0.34 | 18,101 | 40 | 40 | 0 | 306 |
| quad-bc7-quiet-street@1300-drizzle | 13.2 / 13.3 | 12.0 / 12.6 | 23.9 / 24.2 | 0.35 | 0.34 | 18,101 | 40 | 40 | 0 | 306 |
| quad-bc7-quiet-street@1300-drizzle/history-off | 13.2 / 13.4 | 12.0 / 12.7 | 23.7 / 24.1 | 0.34 | 0.34 | 18,101 | 40 | 40 | 0 | 306 |
| quad-bc7-quiet-tile8-street@1300-drizzle | 13.2 / 13.4 | 12.0 / 12.6 | 23.6 / 24.1 | 0.34 | 0.34 | 18,101 | 40 | 40 | 0 | 308 |
| quad-bc7-quiet-tile8-street@1300-drizzle/history-off | 13.2 / 13.3 | 12.0 / 12.6 | 23.9 / 24.1 | 0.35 | 0.34 | 18,101 | 40 | 40 | 0 | 306 |
| quad-bc7-noisy-street@1300-drizzle | 13.9 / 14.1 | 12.6 / 13.1 | 25.0 / 25.3 | 0.35 | 0.35 | 18,101 | 40 | 40 | 0 | 307 |
| quad-bc7-noisy-street@1300-drizzle/history-off | 13.2 / 13.4 | 12.0 / 12.6 | 23.8 / 24.1 | 0.34 | 0.35 | 18,101 | 40 | 40 | 0 | 306 |
| quad-bc7-noisy-tile8-street@1300-drizzle | 15.4 / 15.7 | 13.6 / 14.2 | 27.0 / 27.4 | 0.35 | 0.35 | 18,101 | 40 | 40 | 0 | 307 |
| quad-bc7-noisy-tile8-street@1300-drizzle/history-off | 13.2 / 13.3 | 12.0 / 12.6 | 23.9 / 24.2 | 0.35 | 0.35 | 18,101 | 40 | 40 | 0 | 306 |
| quad-bc7-two-quiet-street@1300-drizzle | 13.2 / 13.4 | 12.0 / 12.6 | 23.9 / 24.2 | 0.35 | 0.35 | 18,101 | 40 | 40 | 0 | 307 |
| quad-bc7-two-quiet-street@1300-drizzle/history-off | 13.2 / 13.5 | 12.0 / 12.7 | 23.8 / 24.2 | 0.35 | 0.35 | 18,101 | 40 | 40 | 0 | 306 |
| quad-bc7-two-quiet-tile8-street@1300-drizzle | 13.2 / 13.4 | 12.0 / 12.7 | 23.7 / 24.1 | 0.35 | 0.35 | 18,101 | 40 | 40 | 0 | 306 |
| quad-bc7-two-quiet-tile8-street@1300-drizzle/history-off | 13.2 / 13.4 | 12.0 / 12.7 | 23.8 / 24.1 | 0.33 | 0.34 | 18,101 | 40 | 40 | 0 | 306 |
