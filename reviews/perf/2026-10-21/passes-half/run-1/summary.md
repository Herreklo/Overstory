# Frame time: the corner, run 1

2026-10-21 21:24:20, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 40 frames a segment, each after 15 warm-up, after 300 frames to settle; 191 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eye-foot@1300-drizzle | 19.1 / 19.5 | 27.5 / 33.1 | 48.6 / 53.9 | 0.44 | 0.42 | 15,518,343 | 142 | 64 | 66 | 230 |
| street@1300-drizzle | 20.7 / 21.6 | 31.2 / 36.6 | 55.4 / 61.7 | 0.42 | 0.41 | 15,012,472 | 142 | 65 | 66 | 231 |
| high@1300-drizzle | 22.0 / 22.7 | 34.4 / 39.7 | 63.0 / 69.4 | 0.43 | 0.42 | 13,805,321 | 130 | 59 | 54 | 229 |
| eye-foot@1300-drizzle/bare | 6.1 / 6.5 | 11.3 / 11.9 | 32.8 / 34.8 | 0.24 | 0.09 | 2,744,340 | 20 | 7 | 0 | 229 |
| street@1300-drizzle/bare | 6.5 / 6.8 | 11.9 / 12.7 | 34.4 / 37.1 | 0.24 | 0.09 | 2,744,340 | 20 | 7 | 0 | 230 |
| high@1300-drizzle/bare | 8.2 / 8.8 | 15.4 / 16.2 | 44.4 / 47.6 | 0.26 | 0.09 | 2,744,340 | 20 | 7 | 0 | 229 |
| eye-foot@1300-drizzle/-msaa | 16.8 / 17.9 | 23.3 / 29.2 | 40.3 / 45.6 | 0.49 | 0.45 | 15,518,343 | 142 | 64 | 66 | 229 |
| street@1300-drizzle/-msaa | 18.1 / 18.3 | 26.4 / 31.6 | 45.7 / 51.8 | 0.44 | 0.42 | 15,012,472 | 142 | 65 | 66 | 229 |
| high@1300-drizzle/-msaa | 19.2 / 19.9 | 30.4 / 35.6 | 54.9 / 60.3 | 0.43 | 0.41 | 13,805,321 | 130 | 59 | 54 | 229 |
| eye-foot@1600-low-sun | 40.1 / 42.8 | 80.9 / 87.4 | 149.7 / 163.2 | 0.49 | 0.45 | 15,852,678 | 147 | 67 | 70 | 229 |
| street@1600-low-sun | 42.0 / 44.4 | 84.5 / 90.4 | 158.0 / 169.4 | 0.43 | 0.42 | 15,036,472 | 143 | 66 | 66 | 229 |
| high@1600-low-sun | 44.4 / 44.9 | 87.7 / 92.8 | 169.1 / 175.6 | 0.41 | 0.41 | 13,829,321 | 131 | 60 | 54 | 229 |
| eye-foot@1600-low-sun-nobirch | 40.4 / 41.5 | 80.3 / 85.6 | 153.4 / 160.1 | 0.44 | 0.41 | 15,345,762 | 133 | 53 | 62 | 229 |
| street@1600-low-sun-nobirch | 38.1 / 39.0 | 75.1 / 80.5 | 145.4 / 150.0 | 0.41 | 0.40 | 14,529,556 | 129 | 52 | 58 | 229 |
| high@1600-low-sun-nobirch | 37.4 / 38.6 | 75.6 / 80.2 | 146.9 / 150.9 | 0.44 | 0.41 | 13,482,185 | 121 | 50 | 50 | 229 |
| eye-foot@1600-low-sun/bare | 6.4 / 6.6 | 11.6 / 12.0 | 34.2 / 35.0 | 0.27 | 0.09 | 2,744,340 | 20 | 7 | 0 | 230 |
| street@1600-low-sun/bare | 6.8 / 6.9 | 12.3 / 12.8 | 36.6 / 37.2 | 0.25 | 0.09 | 2,744,340 | 20 | 7 | 0 | 231 |
| high@1600-low-sun/bare | 8.6 / 8.7 | 16.0 / 16.3 | 47.5 / 48.1 | 0.26 | 0.09 | 2,744,340 | 20 | 7 | 0 | 229 |
| eye-foot@1600-low-sun/-msaa | 39.6 / 40.1 | 78.4 / 83.4 | 150.8 / 154.4 | 0.48 | 0.44 | 15,852,678 | 147 | 67 | 70 | 230 |
| street@1600-low-sun/-msaa | 40.3 / 41.1 | 80.7 / 85.4 | 155.5 / 159.2 | 0.43 | 0.42 | 15,036,472 | 143 | 66 | 66 | 230 |
| high@1600-low-sun/-msaa | 41.4 / 42.4 | 84.4 / 89.1 | 164.3 / 168.0 | 0.41 | 0.41 | 13,829,321 | 131 | 60 | 54 | 231 |
| eye-foot@1750-blue-hour | 13.7 / 14.0 | 24.9 / 26.6 | 46.2 / 50.0 | 0.35 | 0.38 | 5,490,395 | 76 | 50 | 0 | 232 |
| street@1750-blue-hour | 14.9 / 15.1 | 27.2 / 28.5 | 51.1 / 54.3 | 0.35 | 0.37 | 5,490,395 | 76 | 50 | 0 | 230 |
| high@1750-blue-hour | 16.6 / 17.0 | 30.3 / 31.4 | 57.2 / 61.0 | 0.35 | 0.37 | 5,490,395 | 76 | 50 | 0 | 231 |
| eye-foot@1750-blue-hour/bare | 6.4 / 6.5 | 11.5 / 12.1 | 34.2 / 35.1 | 0.23 | 0.09 | 2,744,340 | 20 | 7 | 0 | 230 |
| street@1750-blue-hour/bare | 6.8 / 7.1 | 12.2 / 12.6 | 36.3 / 36.8 | 0.23 | 0.09 | 2,744,340 | 20 | 7 | 0 | 230 |
| high@1750-blue-hour/bare | 8.6 / 8.8 | 15.9 / 16.3 | 47.4 / 48.0 | 0.23 | 0.08 | 2,744,340 | 20 | 7 | 0 | 230 |
| eye-foot@1750-blue-hour/-msaa | 11.0 / 11.3 | 20.7 / 22.4 | 38.2 / 41.7 | 0.36 | 0.37 | 5,490,395 | 76 | 50 | 0 | 231 |
| street@1750-blue-hour/-msaa | 11.6 / 11.9 | 22.2 / 23.4 | 40.9 / 44.2 | 0.35 | 0.37 | 5,490,395 | 76 | 50 | 0 | 231 |
| high@1750-blue-hour/-msaa | 13.6 / 13.8 | 26.1 / 27.2 | 48.8 / 52.4 | 0.37 | 0.38 | 5,490,395 | 76 | 50 | 0 | 231 |
