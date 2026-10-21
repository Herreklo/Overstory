# Frame time: the corner, run 1

2026-10-21 21:34:38, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 40 frames a segment, each after 15 warm-up, after 300 frames to settle; 171 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eye-foot@1300-drizzle | 32.0 / 33.9 | 27.2 / 32.9 | 47.2 / 53.5 | 0.41 | 0.40 | 15,518,343 | 142 | 64 | 66 | 229 |
| street@1300-drizzle | 35.6 / 37.7 | 30.4 / 36.0 | 53.7 / 59.7 | 0.43 | 0.42 | 15,012,472 | 142 | 65 | 66 | 230 |
| high@1300-drizzle | 39.6 / 42.3 | 34.0 / 39.1 | 61.6 / 67.8 | 0.40 | 0.41 | 13,805,321 | 130 | 59 | 54 | 229 |
| eye-foot@1300-drizzle/bare | 12.6 / 13.4 | 10.9 / 11.6 | 31.6 / 33.7 | 0.24 | 0.09 | 2,744,340 | 20 | 7 | 0 | 229 |
| street@1300-drizzle/bare | 13.2 / 14.1 | 11.4 / 12.2 | 33.4 / 35.5 | 0.24 | 0.09 | 2,744,340 | 20 | 7 | 0 | 230 |
| high@1300-drizzle/bare | 17.7 / 18.5 | 15.2 / 15.9 | 44.6 / 46.8 | 0.23 | 0.09 | 2,744,340 | 20 | 7 | 0 | 229 |
| eye-foot@1600-low-sun | 95.1 / 96.1 | 80.6 / 86.8 | 154.3 / 161.6 | 0.40 | 0.41 | 15,852,678 | 147 | 67 | 70 | 229 |
| street@1600-low-sun | 99.2 / 100.1 | 84.5 / 89.7 | 162.9 / 167.6 | 0.45 | 0.43 | 15,036,472 | 143 | 66 | 66 | 230 |
| high@1600-low-sun | 103.2 / 104.1 | 87.7 / 92.4 | 171.1 / 175.1 | 0.43 | 0.42 | 13,829,321 | 131 | 60 | 54 | 229 |
| eye-foot@1600-low-sun-nobirch | 93.6 / 94.0 | 79.7 / 85.6 | 154.3 / 158.9 | 0.40 | 0.40 | 15,345,762 | 133 | 53 | 62 | 229 |
| street@1600-low-sun-nobirch | 87.4 / 88.9 | 74.0 / 79.9 | 144.1 / 148.0 | 0.41 | 0.39 | 14,529,556 | 129 | 52 | 58 | 229 |
| high@1600-low-sun-nobirch | 87.8 / 88.9 | 75.1 / 79.7 | 146.1 / 150.0 | 0.41 | 0.39 | 13,482,185 | 121 | 50 | 50 | 230 |
| eye-foot@1600-low-sun/bare | 13.3 / 13.6 | 11.3 / 11.7 | 33.4 / 33.8 | 0.23 | 0.09 | 2,744,340 | 20 | 7 | 0 | 229 |
| street@1600-low-sun/bare | 13.9 / 14.1 | 11.8 / 12.4 | 34.9 / 36.0 | 0.23 | 0.09 | 2,744,340 | 20 | 7 | 0 | 229 |
| high@1600-low-sun/bare | 18.4 / 18.5 | 15.7 / 16.1 | 46.6 / 47.2 | 0.23 | 0.08 | 2,744,340 | 20 | 7 | 0 | 229 |
| eye-foot@1750-blue-hour | 27.6 / 27.9 | 24.6 / 26.1 | 46.0 / 49.3 | 0.36 | 0.38 | 5,490,395 | 76 | 50 | 0 | 230 |
| street@1750-blue-hour | 30.4 / 30.6 | 26.5 / 27.8 | 49.8 / 53.1 | 0.35 | 0.38 | 5,490,395 | 76 | 50 | 0 | 230 |
| high@1750-blue-hour | 34.2 / 34.4 | 30.0 / 31.0 | 56.6 / 60.2 | 0.36 | 0.37 | 5,490,395 | 76 | 50 | 0 | 230 |
| eye-foot@1750-blue-hour/bare | 13.3 / 13.5 | 11.3 / 11.6 | 33.3 / 33.8 | 0.24 | 0.09 | 2,744,340 | 20 | 7 | 0 | 230 |
| street@1750-blue-hour/bare | 13.9 / 14.3 | 11.8 / 12.2 | 34.8 / 35.3 | 0.23 | 0.09 | 2,744,340 | 20 | 7 | 0 | 230 |
| high@1750-blue-hour/bare | 18.3 / 18.4 | 15.6 / 15.9 | 46.4 / 47.1 | 0.24 | 0.09 | 2,744,340 | 20 | 7 | 0 | 230 |
