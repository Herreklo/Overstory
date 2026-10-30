# Frame time: the walk's corner in the town, run 2

2026-10-26 23:12:08, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 376 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eye-foot@1300-drizzle | 26.4 / 28.7 | 23.1 / 25.4 | 40.2 / 41.5 | 0.43 | 0.43 | 15,938,971 | 140 | 54 | 64 | 235 |
| eye-on@1300-drizzle | 33.4 / 33.6 | 27.3 / 33.2 | 46.6 / 48.2 | 0.43 | 0.43 | 15,659,617 | 137 | 54 | 61 | 234 |
| street@1300-drizzle | 24.2 / 24.4 | 17.7 / 25.1 | 29.2 / 33.7 | 0.42 | 0.42 | 15,246,165 | 138 | 53 | 62 | 235 |
| into12@1300-drizzle | 24.6 / 24.8 | 18.7 / 25.6 | 30.5 / 34.4 | 0.42 | 0.42 | 15,409,791 | 137 | 54 | 63 | 234 |
| high@1300-drizzle | 23.5 / 24.3 | 18.4 / 24.3 | 28.4 / 34.5 | 0.40 | 0.41 | 13,951,327 | 124 | 51 | 50 | 235 |
| a-window@1300-drizzle | 24.3 / 25.0 | 20.7 / 25.1 | 33.5 / 35.6 | 0.40 | 0.42 | 15,351,885 | 146 | 53 | 66 | 234 |
| steps@1300-drizzle | 23.9 / 25.7 | 20.8 / 21.9 | 37.3 / 38.1 | 0.41 | 0.42 | 15,210,801 | 124 | 54 | 56 | 235 |
| row@1300-drizzle | 23.3 / 23.4 | 18.4 / 24.3 | 32.3 / 34.5 | 0.41 | 0.42 | 15,098,239 | 145 | 52 | 65 | 234 |
| anchor-door@1300-drizzle | 19.3 / 19.4 | 14.9 / 19.8 | 21.1 / 27.5 | 0.39 | 0.40 | 11,142,635 | 121 | 48 | 51 | 235 |
| eye-foot@1600-low-sun | 28.9 / 29.0 | 21.7 / 29.1 | 30.6 / 40.6 | 0.40 | 0.42 | 16,259,381 | 147 | 54 | 71 | 235 |
| eye-on@1600-low-sun | 33.5 / 34.0 | 27.2 / 33.8 | 36.9 / 48.3 | 0.41 | 0.42 | 16,217,069 | 143 | 54 | 67 | 236 |
| street@1600-low-sun | 23.1 / 23.5 | 19.8 / 22.6 | 30.8 / 35.8 | 0.41 | 0.42 | 15,288,477 | 142 | 53 | 66 | 235 |
| into12@1600-low-sun | 23.5 / 24.9 | 19.8 / 21.1 | 36.3 / 36.9 | 0.42 | 0.42 | 15,470,391 | 141 | 54 | 67 | 236 |
| high@1600-low-sun | 23.6 / 23.8 | 17.7 / 24.0 | 25.5 / 33.5 | 0.40 | 0.41 | 13,975,779 | 126 | 51 | 52 | 235 |
| a-window@1600-low-sun | 25.8 / 26.0 | 20.8 / 26.9 | 28.6 / 34.4 | 0.41 | 0.42 | 15,376,337 | 148 | 53 | 68 | 236 |
| steps@1600-low-sun | 25.7 / 26.2 | 19.5 / 26.6 | 28.6 / 36.7 | 0.40 | 0.41 | 15,231,125 | 126 | 54 | 58 | 235 |
| row@1600-low-sun | 22.6 / 23.0 | 18.9 / 23.6 | 29.8 / 33.8 | 0.41 | 0.42 | 15,098,239 | 145 | 52 | 65 | 236 |
| anchor-door@1600-low-sun | 18.7 / 19.9 | 16.3 / 17.0 | 29.0 / 29.8 | 0.39 | 0.41 | 11,132,057 | 120 | 48 | 50 | 235 |
| eye-foot@1750-blue-hour | 54.0 / 54.7 | 47.2 / 48.6 | 90.5 / 95.2 | 0.37 | 0.38 | 5,668,793 | 73 | 43 | 0 | 236 |
| eye-on@1750-blue-hour | 58.7 / 59.1 | 51.1 / 52.5 | 97.6 / 102.9 | 0.38 | 0.38 | 5,668,793 | 73 | 43 | 0 | 235 |
| street@1750-blue-hour | 48.9 / 49.3 | 42.5 / 43.8 | 81.9 / 85.6 | 0.37 | 0.38 | 5,668,793 | 73 | 43 | 0 | 237 |
| into12@1750-blue-hour | 48.9 / 49.5 | 42.6 / 43.8 | 82.2 / 85.9 | 0.37 | 0.38 | 5,656,037 | 71 | 43 | 0 | 236 |
| high@1750-blue-hour | 48.7 / 49.3 | 42.6 / 43.6 | 81.9 / 85.4 | 0.37 | 0.38 | 5,656,037 | 71 | 43 | 0 | 237 |
| a-window@1750-blue-hour | 49.9 / 50.3 | 43.4 / 44.7 | 83.1 / 87.5 | 0.37 | 0.38 | 5,717,697 | 77 | 43 | 0 | 236 |
| steps@1750-blue-hour | 49.6 / 50.3 | 43.4 / 44.3 | 83.6 / 87.2 | 0.37 | 0.37 | 5,092,273 | 65 | 43 | 0 | 237 |
| row@1750-blue-hour | 47.9 / 48.5 | 41.8 / 43.1 | 80.3 / 83.9 | 0.37 | 0.38 | 5,717,697 | 77 | 43 | 0 | 236 |
| anchor-door@1750-blue-hour | 50.7 / 51.6 | 44.5 / 45.3 | 86.3 / 89.8 | 0.38 | 0.37 | 3,744,477 | 67 | 41 | 0 | 237 |
