# Frame time: the walk's corner in the town, run 1

2026-10-22 21:32:09, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 339 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eye-foot@1300-drizzle | 33.4 / 37.1 | 28.3 / 36.0 | 48.6 / 57.2 | 1.12 | 0.64 | 15,938,967 | 136 | 50 | 64 | 242 |
| eye-on@1300-drizzle | 39.5 / 46.2 | 32.5 / 40.6 | 55.3 / 66.1 | 1.09 | 0.62 | 15,659,613 | 133 | 50 | 61 | 243 |
| street@1300-drizzle | 30.7 / 33.7 | 24.6 / 32.5 | 40.0 / 49.6 | 1.11 | 0.62 | 15,246,161 | 134 | 49 | 62 | 242 |
| into12@1300-drizzle | 30.1 / 36.4 | 26.1 / 35.1 | 43.8 / 53.6 | 1.19 | 0.67 | 15,409,787 | 133 | 50 | 63 | 243 |
| high@1300-drizzle | 29.6 / 34.8 | 25.3 / 33.5 | 43.2 / 52.5 | 1.24 | 0.64 | 13,951,323 | 120 | 47 | 50 | 242 |
| a-window@1300-drizzle | 32.4 / 37.9 | 26.0 / 33.4 | 45.2 / 52.0 | 1.18 | 0.66 | 15,351,881 | 142 | 49 | 66 | 244 |
| steps@1300-drizzle | 32.6 / 34.4 | 27.8 / 36.8 | 48.3 / 56.3 | 1.20 | 0.65 | 15,210,797 | 120 | 50 | 56 | 243 |
| row@1300-drizzle | 29.9 / 34.3 | 25.3 / 33.7 | 43.7 / 53.1 | 1.11 | 0.62 | 15,098,235 | 141 | 48 | 65 | 244 |
| anchor-door@1300-drizzle | 24.4 / 24.9 | 20.1 / 24.3 | 36.3 / 40.2 | 1.04 | 0.59 | 11,142,631 | 117 | 44 | 51 | 243 |
| eye-foot@1600-low-sun | 36.8 / 38.3 | 30.1 / 38.3 | 41.7 / 56.3 | 1.02 | 0.62 | 16,283,381 | 148 | 55 | 71 | 244 |
| eye-on@1600-low-sun | 41.9 / 43.9 | 35.5 / 41.5 | 45.7 / 62.8 | 1.04 | 0.65 | 16,241,069 | 144 | 55 | 67 | 243 |
| street@1600-low-sun | 31.2 / 32.2 | 27.1 / 29.3 | 41.7 / 49.7 | 1.10 | 0.65 | 15,312,477 | 143 | 54 | 66 | 244 |
| into12@1600-low-sun | 31.6 / 35.2 | 26.9 / 29.4 | 49.1 / 52.7 | 1.23 | 0.69 | 15,494,391 | 142 | 55 | 67 | 243 |
| high@1600-low-sun | 32.2 / 34.1 | 26.4 / 33.9 | 39.1 / 49.5 | 1.18 | 0.68 | 13,999,779 | 127 | 52 | 52 | 244 |
| a-window@1600-low-sun | 36.5 / 39.6 | 30.7 / 39.0 | 43.1 / 54.7 | 1.16 | 0.69 | 15,400,337 | 149 | 54 | 68 | 243 |
| steps@1600-low-sun | 34.0 / 34.4 | 27.3 / 34.5 | 36.7 / 51.0 | 0.97 | 0.60 | 15,255,125 | 127 | 55 | 58 | 245 |
| row@1600-low-sun | 29.9 / 30.6 | 26.9 / 31.5 | 40.6 / 46.2 | 1.03 | 0.64 | 15,122,239 | 146 | 53 | 65 | 244 |
| anchor-door@1600-low-sun | 25.2 / 25.7 | 22.2 / 23.3 | 34.0 / 41.8 | 1.05 | 0.62 | 11,156,057 | 121 | 49 | 50 | 245 |
| eye-foot@1750-blue-hour | 28.0 / 31.1 | 24.5 / 26.2 | 45.4 / 50.0 | 1.02 | 0.57 | 5,644,793 | 72 | 42 | 0 | 244 |
| eye-on@1750-blue-hour | 33.6 / 34.7 | 29.7 / 32.9 | 53.7 / 60.7 | 1.05 | 0.57 | 5,644,793 | 72 | 42 | 0 | 245 |
| street@1750-blue-hour | 22.9 / 23.9 | 20.2 / 22.1 | 36.7 / 40.8 | 1.09 | 0.59 | 5,644,793 | 72 | 42 | 0 | 244 |
| into12@1750-blue-hour | 23.7 / 24.5 | 20.8 / 21.9 | 38.5 / 41.9 | 1.00 | 0.56 | 5,632,037 | 70 | 42 | 0 | 245 |
| high@1750-blue-hour | 22.8 / 25.2 | 20.2 / 21.8 | 37.2 / 41.7 | 1.03 | 0.57 | 5,632,037 | 70 | 42 | 0 | 244 |
| a-window@1750-blue-hour | 24.7 / 25.4 | 21.8 / 23.9 | 39.2 / 44.5 | 1.11 | 0.60 | 5,693,697 | 76 | 42 | 0 | 245 |
| steps@1750-blue-hour | 24.5 / 24.9 | 21.9 / 24.2 | 40.5 / 45.0 | 1.14 | 0.62 | 5,068,273 | 64 | 42 | 0 | 244 |
| row@1750-blue-hour | 22.1 / 22.4 | 19.3 / 20.7 | 35.2 / 39.0 | 1.05 | 0.61 | 5,693,697 | 76 | 42 | 0 | 245 |
| anchor-door@1750-blue-hour | 19.5 / 21.4 | 17.0 / 18.0 | 31.3 / 34.6 | 1.06 | 0.58 | 3,720,477 | 66 | 40 | 0 | 244 |
