# Frame time: the walk's corner in the town, run 1

2026-10-27 08:16:34, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 308 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eye-foot@1300-drizzle | 28.0 / 28.9 | 22.8 / 28.7 | 39.8 / 41.6 | 0.42 | 0.42 | 15,938,969 | 138 | 52 | 64 | 229 |
| eye-on@1300-drizzle | 33.3 / 33.7 | 27.2 / 32.9 | 46.4 / 48.1 | 0.42 | 0.43 | 15,659,615 | 135 | 52 | 61 | 229 |
| street@1300-drizzle | 23.7 / 24.3 | 19.2 / 24.8 | 33.2 / 35.6 | 0.42 | 0.43 | 15,246,163 | 136 | 51 | 62 | 229 |
| into12@1300-drizzle | 24.3 / 24.6 | 19.6 / 25.1 | 33.9 / 36.1 | 0.41 | 0.42 | 15,409,789 | 135 | 52 | 63 | 230 |
| high@1300-drizzle | 23.4 / 24.0 | 19.5 / 24.0 | 33.7 / 35.4 | 0.39 | 0.41 | 13,951,325 | 122 | 49 | 50 | 229 |
| a-window@1300-drizzle | 25.0 / 25.5 | 20.4 / 26.2 | 33.7 / 36.1 | 0.41 | 0.42 | 15,351,883 | 144 | 51 | 66 | 229 |
| steps@1300-drizzle | 25.5 / 26.0 | 20.6 / 26.1 | 35.7 / 37.4 | 0.41 | 0.42 | 15,210,799 | 122 | 52 | 56 | 230 |
| row@1300-drizzle | 22.8 / 23.2 | 18.5 / 24.0 | 31.5 / 33.9 | 0.41 | 0.42 | 15,098,237 | 143 | 50 | 65 | 230 |
| anchor-door@1300-drizzle | 18.6 / 19.4 | 15.6 / 19.2 | 26.8 / 28.1 | 0.39 | 0.41 | 11,142,633 | 119 | 46 | 51 | 230 |
| eye-foot@1600-low-sun | 28.8 / 29.5 | 23.5 / 29.2 | 40.3 / 42.5 | 0.41 | 0.42 | 16,259,379 | 145 | 52 | 71 | 230 |
| eye-on@1600-low-sun | 33.7 / 34.3 | 27.8 / 33.6 | 47.0 / 48.8 | 0.42 | 0.43 | 16,217,067 | 141 | 52 | 67 | 230 |
| street@1600-low-sun | 23.8 / 24.6 | 19.7 / 25.2 | 33.8 / 36.4 | 0.40 | 0.42 | 15,288,475 | 140 | 51 | 66 | 230 |
| into12@1600-low-sun | 24.1 / 24.9 | 19.7 / 25.2 | 33.9 / 36.1 | 0.41 | 0.42 | 15,470,389 | 139 | 52 | 67 | 230 |
| high@1600-low-sun | 23.1 / 23.7 | 19.1 / 23.9 | 33.0 / 35.0 | 0.40 | 0.42 | 13,975,777 | 124 | 49 | 52 | 230 |
| a-window@1600-low-sun | 25.1 / 25.7 | 20.6 / 26.4 | 33.8 / 36.3 | 0.40 | 0.42 | 15,376,335 | 146 | 51 | 68 | 230 |
| steps@1600-low-sun | 25.5 / 26.3 | 21.0 / 26.3 | 36.2 / 37.9 | 0.40 | 0.42 | 15,231,123 | 124 | 52 | 58 | 231 |
| row@1600-low-sun | 22.6 / 23.4 | 18.9 / 24.1 | 31.5 / 33.9 | 0.40 | 0.42 | 15,098,237 | 143 | 50 | 65 | 230 |
| anchor-door@1600-low-sun | 19.2 / 19.8 | 16.1 / 19.5 | 27.5 / 28.9 | 0.40 | 0.42 | 11,132,055 | 118 | 46 | 50 | 231 |
| eye-foot@1750-blue-hour | 34.7 / 35.5 | 30.6 / 32.1 | 57.5 / 61.4 | 0.36 | 0.39 | 5,668,793 | 73 | 43 | 0 | 232 |
| eye-on@1750-blue-hour | 39.9 / 40.3 | 35.0 / 36.4 | 64.7 / 70.2 | 0.38 | 0.40 | 5,668,793 | 73 | 43 | 0 | 232 |
| street@1750-blue-hour | 29.5 / 29.9 | 25.6 / 27.1 | 48.3 / 51.5 | 0.37 | 0.39 | 5,668,793 | 73 | 43 | 0 | 233 |
| into12@1750-blue-hour | 30.3 / 30.5 | 26.3 / 27.4 | 49.8 / 52.9 | 0.37 | 0.40 | 5,656,037 | 71 | 43 | 0 | 232 |
| high@1750-blue-hour | 30.0 / 30.3 | 26.1 / 27.2 | 49.3 / 52.3 | 0.37 | 0.39 | 5,656,037 | 71 | 43 | 0 | 233 |
| a-window@1750-blue-hour | 30.4 / 30.5 | 26.6 / 28.0 | 49.2 / 53.4 | 0.36 | 0.39 | 5,717,697 | 77 | 43 | 0 | 232 |
| steps@1750-blue-hour | 30.9 / 31.4 | 26.9 / 28.0 | 50.9 / 53.9 | 0.37 | 0.39 | 5,092,273 | 65 | 43 | 0 | 233 |
| row@1750-blue-hour | 28.7 / 29.2 | 25.2 / 26.4 | 47.1 / 50.5 | 0.37 | 0.39 | 5,717,697 | 77 | 43 | 0 | 232 |
| anchor-door@1750-blue-hour | 27.9 / 28.2 | 24.5 / 24.9 | 46.9 / 49.1 | 0.39 | 0.39 | 3,744,477 | 67 | 41 | 0 | 233 |
