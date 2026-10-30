# Frame time: the walk's corner in the town, run 1

2026-10-26 23:01:16, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 402 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eye-foot@1300-drizzle | 28.3 / 29.0 | 21.9 / 28.7 | 30.7 / 40.1 | 0.40 | 0.39 | 15,938,971 | 140 | 54 | 64 | 235 |
| eye-on@1300-drizzle | 32.8 / 33.1 | 26.8 / 32.1 | 36.1 / 47.5 | 0.41 | 0.40 | 15,659,617 | 137 | 54 | 61 | 234 |
| street@1300-drizzle | 22.9 / 23.5 | 20.1 / 21.9 | 30.7 / 36.4 | 0.39 | 0.38 | 15,246,165 | 138 | 53 | 62 | 234 |
| into12@1300-drizzle | 26.4 / 31.0 | 21.1 / 24.6 | 38.2 / 43.6 | 1.26 | 0.75 | 15,409,791 | 137 | 54 | 63 | 234 |
| high@1300-drizzle | 24.4 / 29.8 | 20.5 / 29.0 | 31.0 / 38.8 | 1.26 | 0.67 | 13,951,327 | 124 | 51 | 50 | 234 |
| a-window@1300-drizzle | 27.4 / 32.2 | 21.8 / 32.3 | 33.8 / 39.4 | 1.07 | 0.70 | 15,351,885 | 146 | 53 | 66 | 234 |
| steps@1300-drizzle | 26.9 / 31.6 | 22.7 / 31.5 | 34.8 / 42.1 | 1.45 | 0.81 | 15,210,801 | 124 | 54 | 56 | 234 |
| row@1300-drizzle | 22.9 / 27.7 | 21.6 / 25.8 | 32.5 / 38.8 | 1.12 | 0.71 | 15,098,239 | 145 | 52 | 65 | 235 |
| anchor-door@1300-drizzle | 18.5 / 23.8 | 16.1 / 18.6 | 28.6 / 33.3 | 1.03 | 0.65 | 11,142,635 | 121 | 48 | 51 | 236 |
| eye-foot@1600-low-sun | 30.3 / 35.5 | 23.4 / 35.0 | 41.2 / 46.0 | 1.37 | 0.84 | 16,259,381 | 147 | 54 | 71 | 235 |
| eye-on@1600-low-sun | 39.5 / 40.8 | 29.8 / 40.2 | 42.8 / 53.9 | 1.30 | 0.77 | 16,217,069 | 143 | 54 | 67 | 235 |
| street@1600-low-sun | 26.5 / 29.2 | 23.3 / 30.8 | 34.2 / 39.3 | 1.19 | 0.72 | 15,288,477 | 142 | 53 | 66 | 235 |
| into12@1600-low-sun | 25.1 / 29.4 | 21.8 / 28.5 | 33.2 / 39.7 | 1.10 | 0.71 | 15,470,391 | 141 | 54 | 67 | 236 |
| high@1600-low-sun | 23.8 / 27.7 | 21.9 / 23.4 | 33.8 / 40.1 | 1.08 | 0.68 | 13,975,779 | 126 | 51 | 52 | 236 |
| a-window@1600-low-sun | 25.1 / 30.8 | 23.1 / 25.6 | 41.1 / 43.5 | 1.37 | 0.78 | 15,376,337 | 148 | 53 | 68 | 237 |
| steps@1600-low-sun | 26.8 / 32.2 | 21.2 / 32.0 | 37.9 / 41.5 | 1.33 | 0.85 | 15,231,125 | 126 | 54 | 58 | 237 |
| row@1600-low-sun | 23.9 / 29.7 | 19.1 / 29.5 | 31.7 / 36.7 | 1.23 | 0.75 | 15,098,239 | 145 | 52 | 65 | 238 |
| anchor-door@1600-low-sun | 20.0 / 23.4 | 17.3 / 23.6 | 26.7 / 31.9 | 1.34 | 0.82 | 11,132,057 | 120 | 48 | 50 | 236 |
| eye-foot@1750-blue-hour | 59.1 / 66.1 | 50.1 / 52.9 | 91.8 / 102.6 | 1.24 | 0.70 | 5,668,793 | 73 | 43 | 0 | 236 |
| eye-on@1750-blue-hour | 64.4 / 66.0 | 55.0 / 58.0 | 100.7 / 112.8 | 1.32 | 0.69 | 5,668,793 | 73 | 43 | 0 | 237 |
| street@1750-blue-hour | 50.2 / 54.9 | 45.2 / 47.9 | 84.5 / 92.8 | 1.10 | 0.65 | 5,668,793 | 73 | 43 | 0 | 237 |
| into12@1750-blue-hour | 49.9 / 53.6 | 44.3 / 47.8 | 83.9 / 92.6 | 0.98 | 0.58 | 5,656,037 | 71 | 43 | 0 | 237 |
| high@1750-blue-hour | 49.7 / 53.9 | 44.7 / 47.5 | 84.2 / 92.1 | 1.04 | 0.62 | 5,656,037 | 71 | 43 | 0 | 237 |
| a-window@1750-blue-hour | 53.3 / 57.2 | 46.2 / 49.4 | 85.2 / 95.1 | 1.11 | 0.62 | 5,717,697 | 77 | 43 | 0 | 237 |
| steps@1750-blue-hour | 50.6 / 55.1 | 45.7 / 48.5 | 85.3 / 94.4 | 1.08 | 0.62 | 5,092,273 | 65 | 43 | 0 | 238 |
| row@1750-blue-hour | 49.0 / 53.0 | 44.3 / 47.2 | 82.2 / 91.2 | 1.04 | 0.61 | 5,717,697 | 77 | 43 | 0 | 237 |
| anchor-door@1750-blue-hour | 51.9 / 55.9 | 45.8 / 48.5 | 87.9 / 95.6 | 1.18 | 0.61 | 3,744,477 | 67 | 41 | 0 | 237 |
