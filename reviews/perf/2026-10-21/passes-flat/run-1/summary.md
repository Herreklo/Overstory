# Frame time: the corner, run 1

2026-10-21 21:35:58, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 40 frames a segment, each after 15 warm-up, after 300 frames to settle; 30 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eye-foot@1300-drizzle/bare | 12.9 / 13.2 | 10.8 / 11.5 | 32.2 / 32.9 | 0.24 | 0.09 | 2,744,340 | 20 | 7 | 0 | 225 |
| street@1300-drizzle/bare | 13.7 / 14.0 | 11.5 / 11.9 | 34.1 / 34.4 | 0.24 | 0.09 | 2,744,340 | 20 | 7 | 0 | 226 |
| high@1300-drizzle/bare | 17.5 / 17.6 | 14.9 / 15.3 | 44.1 / 44.7 | 0.26 | 0.09 | 2,744,340 | 20 | 7 | 0 | 226 |
| eye-foot@1300-drizzle/flat | 1.9 / 2.0 | 1.7 / 1.9 | 2.1 / 2.4 | 0.21 | 0.08 | 2,744,340 | 20 | 2 | 0 | 227 |
| street@1300-drizzle/flat | 2.0 / 2.5 | 1.8 / 2.1 | 2.2 / 2.5 | 0.22 | 0.07 | 2,744,340 | 20 | 2 | 0 | 225 |
| high@1300-drizzle/flat | 1.8 / 1.9 | 1.6 / 2.0 | 1.9 / 2.3 | 0.21 | 0.07 | 2,744,340 | 20 | 2 | 0 | 226 |
| eye-foot@1600-low-sun/bare | 12.8 / 13.0 | 10.8 / 11.2 | 32.1 / 32.5 | 0.24 | 0.09 | 2,744,340 | 20 | 7 | 0 | 225 |
| street@1600-low-sun/bare | 13.7 / 13.9 | 11.5 / 12.0 | 34.0 / 34.7 | 0.24 | 0.09 | 2,744,340 | 20 | 7 | 0 | 226 |
| high@1600-low-sun/bare | 17.4 / 17.7 | 14.9 / 15.4 | 44.3 / 44.8 | 0.25 | 0.09 | 2,744,340 | 20 | 7 | 0 | 225 |
| eye-foot@1600-low-sun/flat | 1.9 / 2.0 | 1.7 / 2.1 | 2.1 / 2.5 | 0.22 | 0.08 | 2,744,340 | 20 | 2 | 0 | 226 |
| street@1600-low-sun/flat | 1.9 / 2.0 | 1.7 / 2.0 | 2.2 / 2.5 | 0.21 | 0.07 | 2,744,340 | 20 | 2 | 0 | 225 |
| high@1600-low-sun/flat | 1.8 / 1.9 | 1.6 / 1.9 | 1.9 / 2.3 | 0.21 | 0.07 | 2,744,340 | 20 | 2 | 0 | 226 |
| eye-foot@1750-blue-hour/bare | 12.8 / 13.0 | 10.8 / 11.3 | 31.9 / 32.6 | 0.23 | 0.08 | 2,744,340 | 20 | 7 | 0 | 226 |
| street@1750-blue-hour/bare | 13.7 / 13.8 | 11.5 / 11.8 | 34.1 / 34.7 | 0.25 | 0.09 | 2,744,340 | 20 | 7 | 0 | 226 |
| high@1750-blue-hour/bare | 17.6 / 18.0 | 14.9 / 15.5 | 44.2 / 45.5 | 0.23 | 0.09 | 2,744,340 | 20 | 7 | 0 | 226 |
| eye-foot@1750-blue-hour/flat | 1.9 / 2.0 | 1.7 / 2.0 | 2.1 / 2.4 | 0.21 | 0.07 | 2,744,340 | 20 | 2 | 0 | 227 |
| street@1750-blue-hour/flat | 1.9 / 2.0 | 1.7 / 2.1 | 2.2 / 2.6 | 0.22 | 0.07 | 2,744,340 | 20 | 2 | 0 | 226 |
| high@1750-blue-hour/flat | 1.8 / 1.9 | 1.6 / 2.0 | 1.9 / 2.3 | 0.21 | 0.07 | 2,744,340 | 20 | 2 | 0 | 227 |
