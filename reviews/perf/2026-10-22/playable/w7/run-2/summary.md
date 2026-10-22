# Frame time: the walk's corner in the town, run 2

2026-10-22 21:37:47, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 326 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eye-foot@1300-drizzle | 33.4 / 37.0 | 27.4 / 35.4 | 48.7 / 55.5 | 1.18 | 0.68 | 15,938,967 | 136 | 50 | 64 | 242 |
| eye-on@1300-drizzle | 38.2 / 41.2 | 33.5 / 44.1 | 55.3 / 66.9 | 1.20 | 0.70 | 15,659,613 | 133 | 50 | 61 | 243 |
| street@1300-drizzle | 28.3 / 29.9 | 23.1 / 29.9 | 40.8 / 45.7 | 1.11 | 0.66 | 15,246,161 | 134 | 49 | 62 | 242 |
| into12@1300-drizzle | 29.8 / 31.1 | 24.1 / 30.2 | 43.0 / 47.2 | 1.13 | 0.67 | 15,409,787 | 133 | 50 | 63 | 243 |
| high@1300-drizzle | 29.0 / 30.3 | 23.4 / 29.5 | 43.1 / 46.8 | 1.15 | 0.66 | 13,951,323 | 120 | 47 | 50 | 242 |
| a-window@1300-drizzle | 30.2 / 31.8 | 25.5 / 31.9 | 42.8 / 49.7 | 1.11 | 0.66 | 15,351,881 | 142 | 49 | 66 | 243 |
| steps@1300-drizzle | 30.1 / 32.2 | 24.7 / 31.4 | 43.6 / 49.5 | 1.15 | 0.68 | 15,210,797 | 120 | 50 | 56 | 242 |
| row@1300-drizzle | 30.5 / 33.2 | 23.6 / 30.9 | 40.8 / 49.3 | 1.17 | 0.69 | 15,098,235 | 141 | 48 | 65 | 244 |
| anchor-door@1300-drizzle | 24.0 / 26.6 | 21.2 / 26.6 | 36.5 / 43.6 | 1.17 | 0.67 | 11,142,631 | 117 | 44 | 51 | 243 |
| eye-foot@1600-low-sun | 37.9 / 40.4 | 30.4 / 39.5 | 43.2 / 56.8 | 1.17 | 0.71 | 16,283,381 | 148 | 55 | 71 | 244 |
| eye-on@1600-low-sun | 41.2 / 41.9 | 37.3 / 44.5 | 49.8 / 63.7 | 1.15 | 0.70 | 16,241,069 | 144 | 55 | 67 | 243 |
| street@1600-low-sun | 30.3 / 30.8 | 24.5 / 31.9 | 35.6 / 45.7 | 1.09 | 0.67 | 15,312,477 | 143 | 54 | 66 | 244 |
| into12@1600-low-sun | 30.8 / 31.3 | 25.8 / 29.4 | 37.3 / 47.4 | 1.08 | 0.66 | 15,494,391 | 142 | 55 | 67 | 243 |
| high@1600-low-sun | 28.5 / 29.6 | 25.7 / 26.9 | 45.9 / 49.0 | 1.15 | 0.66 | 13,999,779 | 127 | 52 | 52 | 244 |
| a-window@1600-low-sun | 31.7 / 32.6 | 26.1 / 31.5 | 44.6 / 47.0 | 0.78 | 0.53 | 15,400,337 | 149 | 54 | 68 | 243 |
| steps@1600-low-sun | 31.7 / 32.3 | 25.6 / 32.3 | 34.6 / 47.0 | 0.67 | 0.50 | 15,255,125 | 127 | 55 | 58 | 244 |
| row@1600-low-sun | 29.8 / 31.6 | 24.2 / 30.9 | 33.8 / 43.9 | 1.12 | 0.67 | 15,122,239 | 146 | 53 | 65 | 243 |
| anchor-door@1600-low-sun | 24.7 / 25.4 | 21.0 / 24.1 | 29.3 / 38.0 | 0.94 | 0.59 | 11,156,057 | 121 | 49 | 50 | 245 |
| eye-foot@1750-blue-hour | 26.7 / 27.2 | 23.2 / 24.8 | 43.0 / 47.0 | 0.94 | 0.54 | 5,644,793 | 72 | 42 | 0 | 244 |
| eye-on@1750-blue-hour | 31.6 / 32.1 | 27.5 / 29.1 | 50.2 / 56.1 | 0.89 | 0.51 | 5,644,793 | 72 | 42 | 0 | 245 |
| street@1750-blue-hour | 21.7 / 22.3 | 18.8 / 20.8 | 34.6 / 38.1 | 0.90 | 0.53 | 5,644,793 | 72 | 42 | 0 | 244 |
| into12@1750-blue-hour | 22.4 / 23.1 | 19.6 / 21.2 | 36.4 / 39.8 | 0.94 | 0.54 | 5,632,037 | 70 | 42 | 0 | 245 |
| high@1750-blue-hour | 21.9 / 23.6 | 19.2 / 20.8 | 35.3 / 39.2 | 0.80 | 0.49 | 5,632,037 | 70 | 42 | 0 | 244 |
| a-window@1750-blue-hour | 23.1 / 24.8 | 20.5 / 22.6 | 37.0 / 41.6 | 0.90 | 0.54 | 5,693,697 | 76 | 42 | 0 | 245 |
| steps@1750-blue-hour | 23.1 / 23.4 | 20.5 / 21.9 | 37.8 / 41.3 | 0.94 | 0.54 | 5,068,273 | 64 | 42 | 0 | 244 |
| row@1750-blue-hour | 21.0 / 21.9 | 18.1 / 19.7 | 33.3 / 36.8 | 0.91 | 0.53 | 5,693,697 | 76 | 42 | 0 | 245 |
| anchor-door@1750-blue-hour | 17.8 / 18.3 | 15.9 / 16.8 | 29.5 / 32.5 | 1.06 | 0.59 | 3,720,477 | 66 | 40 | 0 | 244 |
