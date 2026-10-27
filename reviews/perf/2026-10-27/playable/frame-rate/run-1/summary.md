# Frame time: the walk's corner in the town, run 1

2026-10-27 13:26:59, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 593 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eye-foot@1300-drizzle | 72.6 / 92.1 | 42.6 / 63.5 | 65.2 / 97.5 | 0.61 | 0.58 | 15,938,961 | 130 | 44 | 64 | 241 |
| eye-on@1300-drizzle | 59.1 / 84.7 | 42.7 / 65.6 | 77.6 / 117.5 | 0.60 | 0.60 | 15,659,607 | 127 | 44 | 61 | 241 |
| street@1300-drizzle | 39.1 / 56.8 | 31.0 / 45.2 | 49.3 / 69.3 | 0.64 | 0.71 | 15,246,155 | 128 | 43 | 62 | 241 |
| into12@1300-drizzle | 43.6 / 60.8 | 32.7 / 48.5 | 55.8 / 76.2 | 0.56 | 0.57 | 15,409,781 | 127 | 44 | 63 | 242 |
| high@1300-drizzle | 43.2 / 77.1 | 31.7 / 50.9 | 51.6 / 81.8 | 0.52 | 0.54 | 13,951,317 | 114 | 41 | 50 | 241 |
| a-window@1300-drizzle | 50.2 / 55.2 | 32.1 / 49.7 | 49.2 / 77.0 | 0.52 | 0.52 | 15,351,875 | 136 | 43 | 66 | 242 |
| steps@1300-drizzle | 57.0 / 63.5 | 34.7 / 53.8 | 63.1 / 97.7 | 0.51 | 0.49 | 15,210,791 | 114 | 44 | 56 | 242 |
| row@1300-drizzle | 44.7 / 51.0 | 31.0 / 42.6 | 48.0 / 60.8 | 0.50 | 0.51 | 15,098,229 | 135 | 42 | 65 | 242 |
| anchor-door@1300-drizzle | 36.2 / 47.7 | 28.5 / 42.7 | 48.5 / 68.5 | 0.54 | 0.58 | 11,142,629 | 115 | 42 | 51 | 242 |
| eye-foot@1600-low-sun | 63.0 / 80.9 | 40.4 / 60.1 | 67.3 / 102.2 | 0.49 | 0.48 | 16,259,371 | 137 | 44 | 71 | 242 |
| eye-on@1600-low-sun | 83.2 / 118.7 | 45.2 / 62.9 | 81.4 / 115.9 | 0.48 | 0.46 | 16,217,059 | 133 | 44 | 67 | 242 |
| street@1600-low-sun | 54.2 / 64.3 | 44.5 / 62.0 | 66.0 / 92.3 | 1.22 | 0.87 | 15,288,467 | 132 | 43 | 66 | 242 |
| into12@1600-low-sun | 50.5 / 53.1 | 36.2 / 53.8 | 62.0 / 98.8 | 0.61 | 0.62 | 15,470,381 | 131 | 44 | 67 | 242 |
| high@1600-low-sun | 47.4 / 59.7 | 35.2 / 57.0 | 51.7 / 85.3 | 0.52 | 0.50 | 13,975,769 | 116 | 41 | 52 | 242 |
| a-window@1600-low-sun | 49.4 / 60.3 | 33.7 / 54.6 | 57.8 / 88.2 | 0.55 | 0.55 | 15,376,327 | 138 | 43 | 68 | 242 |
| steps@1600-low-sun | 59.0 / 72.6 | 37.4 / 53.0 | 58.7 / 84.2 | 0.47 | 0.46 | 15,231,115 | 116 | 44 | 58 | 243 |
| row@1600-low-sun | 47.3 / 63.0 | 33.3 / 93.3 | 54.9 / 168.2 | 0.59 | 0.58 | 15,098,229 | 135 | 42 | 65 | 242 |
| anchor-door@1600-low-sun | 47.9 / 73.1 | 38.4 / 57.8 | 58.0 / 92.8 | 0.99 | 0.80 | 11,132,051 | 114 | 42 | 50 | 243 |
| eye-foot@1750-blue-hour | 90.7 / 127.3 | 62.9 / 81.8 | 89.4 / 156.1 | 1.11 | 0.80 | 5,668,789 | 69 | 39 | 0 | 244 |
| eye-on@1750-blue-hour | 95.7 / 117.8 | 83.3 / 103.9 | 150.2 / 196.2 | 1.56 | 1.09 | 5,668,789 | 69 | 39 | 0 | 244 |
| street@1750-blue-hour | 73.4 / 103.2 | 53.4 / 65.3 | 75.7 / 124.7 | 1.22 | 0.92 | 5,668,789 | 69 | 39 | 0 | 245 |
| into12@1750-blue-hour | 50.7 / 100.7 | 55.4 / 68.0 | 73.4 / 130.5 | 1.07 | 0.78 | 5,656,033 | 67 | 39 | 0 | 244 |
| high@1750-blue-hour | 57.0 / 90.7 | 53.0 / 68.3 | 71.3 / 130.6 | 0.98 | 0.75 | 5,656,033 | 67 | 39 | 0 | 245 |
| a-window@1750-blue-hour | 61.2 / 73.3 | 48.8 / 65.4 | 67.3 / 121.9 | 0.95 | 0.75 | 5,717,693 | 73 | 39 | 0 | 244 |
| steps@1750-blue-hour | 59.0 / 87.7 | 57.6 / 68.8 | 74.9 / 129.3 | 1.13 | 0.80 | 5,092,269 | 61 | 39 | 0 | 245 |
| row@1750-blue-hour | 56.4 / 72.9 | 48.9 / 57.9 | 63.7 / 110.5 | 1.04 | 0.78 | 5,717,693 | 73 | 39 | 0 | 244 |
| anchor-door@1750-blue-hour | 50.0 / 77.6 | 45.8 / 55.9 | 70.1 / 108.4 | 1.03 | 0.76 | 3,744,473 | 63 | 37 | 0 | 246 |
