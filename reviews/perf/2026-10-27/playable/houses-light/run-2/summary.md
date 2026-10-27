# Frame time: the walk's corner in the town, run 2

2026-10-27 08:21:55, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 310 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eye-foot@1300-drizzle | 28.3 / 29.4 | 23.3 / 28.9 | 40.2 / 42.4 | 0.40 | 0.42 | 15,938,969 | 138 | 52 | 64 | 229 |
| eye-on@1300-drizzle | 33.5 / 34.1 | 27.8 / 33.1 | 46.6 / 49.0 | 0.40 | 0.42 | 15,659,615 | 135 | 52 | 61 | 230 |
| street@1300-drizzle | 23.9 / 24.5 | 19.4 / 24.9 | 33.5 / 35.8 | 0.41 | 0.42 | 15,246,163 | 136 | 51 | 62 | 230 |
| into12@1300-drizzle | 24.5 / 25.1 | 19.9 / 25.3 | 34.4 / 36.5 | 0.41 | 0.42 | 15,409,789 | 135 | 52 | 63 | 230 |
| high@1300-drizzle | 24.0 / 24.6 | 19.7 / 24.4 | 34.3 / 36.0 | 0.40 | 0.41 | 13,951,325 | 122 | 49 | 50 | 230 |
| a-window@1300-drizzle | 24.9 / 25.9 | 20.8 / 26.3 | 33.7 / 36.1 | 0.41 | 0.42 | 15,351,883 | 144 | 51 | 66 | 230 |
| steps@1300-drizzle | 25.8 / 26.6 | 21.0 / 26.3 | 36.4 / 38.3 | 0.40 | 0.41 | 15,210,799 | 122 | 52 | 56 | 230 |
| row@1300-drizzle | 23.2 / 23.7 | 18.7 / 24.3 | 32.0 / 34.3 | 0.41 | 0.42 | 15,098,237 | 143 | 50 | 65 | 231 |
| anchor-door@1300-drizzle | 19.1 / 19.6 | 15.9 / 19.5 | 27.4 / 28.6 | 0.37 | 0.40 | 11,142,633 | 119 | 46 | 51 | 231 |
| eye-foot@1600-low-sun | 29.2 / 29.8 | 24.0 / 29.5 | 41.2 / 43.3 | 0.41 | 0.43 | 16,259,379 | 145 | 52 | 71 | 231 |
| eye-on@1600-low-sun | 34.2 / 34.7 | 28.5 / 33.9 | 47.5 / 49.9 | 0.40 | 0.42 | 16,217,067 | 141 | 52 | 67 | 231 |
| street@1600-low-sun | 24.2 / 24.9 | 19.8 / 25.2 | 34.2 / 36.4 | 0.41 | 0.42 | 15,288,475 | 140 | 51 | 66 | 231 |
| into12@1600-low-sun | 24.6 / 25.2 | 20.3 / 25.5 | 34.5 / 36.7 | 0.41 | 0.42 | 15,470,389 | 139 | 52 | 67 | 231 |
| high@1600-low-sun | 23.6 / 24.7 | 19.5 / 24.1 | 33.6 / 35.7 | 0.40 | 0.42 | 13,975,777 | 124 | 49 | 52 | 231 |
| a-window@1600-low-sun | 25.4 / 26.1 | 20.9 / 26.5 | 34.0 / 36.4 | 0.41 | 0.42 | 15,376,335 | 146 | 51 | 68 | 231 |
| steps@1600-low-sun | 26.0 / 26.7 | 21.3 / 26.6 | 36.9 / 38.8 | 0.40 | 0.41 | 15,231,123 | 124 | 52 | 58 | 232 |
| row@1600-low-sun | 23.1 / 23.8 | 19.0 / 24.3 | 32.0 / 34.4 | 0.42 | 0.43 | 15,098,237 | 143 | 50 | 65 | 231 |
| anchor-door@1600-low-sun | 19.5 / 20.0 | 16.5 / 19.8 | 28.1 / 29.4 | 0.39 | 0.40 | 11,132,055 | 118 | 46 | 50 | 232 |
| eye-foot@1750-blue-hour | 35.7 / 36.1 | 31.3 / 32.6 | 59.0 / 62.8 | 0.38 | 0.39 | 5,668,793 | 73 | 43 | 0 | 233 |
| eye-on@1750-blue-hour | 40.6 / 41.1 | 35.5 / 37.0 | 65.9 / 71.4 | 0.38 | 0.39 | 5,668,793 | 73 | 43 | 0 | 233 |
| street@1750-blue-hour | 30.0 / 30.3 | 26.1 / 27.5 | 49.2 / 52.4 | 0.37 | 0.39 | 5,668,793 | 73 | 43 | 0 | 234 |
| into12@1750-blue-hour | 30.7 / 30.9 | 26.7 / 27.8 | 50.5 / 53.6 | 0.36 | 0.39 | 5,656,037 | 71 | 43 | 0 | 233 |
| high@1750-blue-hour | 30.5 / 30.8 | 26.5 / 27.5 | 50.0 / 53.1 | 0.35 | 0.38 | 5,656,037 | 71 | 43 | 0 | 234 |
| a-window@1750-blue-hour | 30.8 / 31.1 | 27.0 / 28.3 | 49.8 / 54.1 | 0.37 | 0.39 | 5,717,697 | 77 | 43 | 0 | 233 |
| steps@1750-blue-hour | 31.3 / 31.5 | 27.3 / 28.3 | 51.6 / 54.8 | 0.36 | 0.38 | 5,092,273 | 65 | 43 | 0 | 234 |
| row@1750-blue-hour | 29.0 / 29.6 | 25.4 / 26.7 | 47.7 / 50.9 | 0.38 | 0.40 | 5,717,697 | 77 | 43 | 0 | 233 |
| anchor-door@1750-blue-hour | 28.3 / 28.7 | 24.8 / 25.2 | 47.4 / 49.7 | 0.38 | 0.38 | 3,744,477 | 67 | 41 | 0 | 234 |
