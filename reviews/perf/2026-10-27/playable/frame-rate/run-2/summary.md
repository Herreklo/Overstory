# Frame time: the walk's corner in the town, run 2

2026-10-27 13:43:14, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 947 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eye-foot@1300-drizzle | 81.4 / 110.0 | 81.0 / 127.2 | 125.1 / 202.5 | 2.43 | 1.95 | 15,938,961 | 130 | 44 | 64 | 242 |
| eye-on@1300-drizzle | 109.2 / 120.9 | 86.8 / 111.3 | 152.5 / 205.4 | 2.56 | 2.36 | 15,659,607 | 127 | 44 | 61 | 242 |
| street@1300-drizzle | 75.7 / 88.8 | 67.2 / 96.6 | 100.9 / 142.5 | 2.48 | 2.31 | 15,246,155 | 128 | 43 | 62 | 242 |
| into12@1300-drizzle | 70.3 / 91.1 | 65.3 / 92.1 | 99.2 / 138.8 | 2.35 | 2.32 | 15,409,781 | 127 | 44 | 63 | 242 |
| high@1300-drizzle | 78.3 / 98.7 | 61.0 / 90.5 | 105.3 / 143.0 | 2.31 | 1.82 | 13,951,317 | 114 | 41 | 50 | 242 |
| a-window@1300-drizzle | 74.3 / 77.5 | 58.7 / 77.7 | 93.6 / 111.1 | 1.44 | 1.47 | 15,351,875 | 136 | 43 | 66 | 242 |
| steps@1300-drizzle | 79.4 / 86.4 | 62.9 / 85.1 | 119.0 / 133.9 | 1.45 | 1.33 | 15,210,791 | 114 | 44 | 56 | 243 |
| row@1300-drizzle | 73.7 / 115.0 | 52.9 / 74.6 | 89.8 / 105.7 | 1.44 | 1.47 | 15,098,229 | 135 | 42 | 65 | 243 |
| anchor-door@1300-drizzle | 68.0 / 71.3 | 53.1 / 67.6 | 91.1 / 104.7 | 1.45 | 1.57 | 11,142,629 | 115 | 42 | 51 | 243 |
| eye-foot@1600-low-sun | 100.1 / 363.0 | 76.4 / 99.4 | 133.6 / 159.4 | 1.55 | 1.50 | 16,259,371 | 137 | 44 | 71 | 243 |
| eye-on@1600-low-sun | 117.3 / 122.0 | 98.9 / 116.3 | 181.5 / 216.5 | 2.57 | 2.27 | 16,217,059 | 133 | 44 | 67 | 243 |
| street@1600-low-sun | 80.6 / 104.7 | 61.0 / 80.4 | 107.7 / 123.8 | 1.69 | 1.74 | 15,288,467 | 132 | 43 | 66 | 243 |
| into12@1600-low-sun | 83.3 / 306.4 | 62.0 / 103.7 | 113.9 / 153.4 | 1.54 | 1.64 | 15,470,381 | 131 | 44 | 67 | 243 |
| high@1600-low-sun | 76.0 / 89.6 | 63.9 / 88.4 | 102.5 / 128.0 | 2.42 | 2.23 | 13,975,769 | 116 | 41 | 52 | 243 |
| a-window@1600-low-sun | 78.8 / 138.9 | 66.7 / 91.2 | 111.2 / 142.5 | 2.35 | 2.16 | 15,376,327 | 138 | 43 | 68 | 243 |
| steps@1600-low-sun | 91.3 / 244.2 | 75.6 / 102.1 | 120.0 / 151.3 | 2.38 | 2.32 | 15,231,115 | 116 | 44 | 58 | 244 |
| row@1600-low-sun | 81.7 / 110.3 | 65.8 / 89.7 | 102.1 / 131.4 | 2.53 | 2.42 | 15,098,229 | 135 | 42 | 65 | 243 |
| anchor-door@1600-low-sun | 73.4 / 81.7 | 61.1 / 77.6 | 102.0 / 122.1 | 3.74 | 3.37 | 11,132,051 | 114 | 42 | 50 | 244 |
| eye-foot@1750-blue-hour | 106.6 / 145.1 | 88.8 / 105.7 | 169.9 / 196.5 | 2.70 | 2.25 | 5,668,789 | 69 | 39 | 0 | 245 |
| eye-on@1750-blue-hour | 120.1 / 123.4 | 103.1 / 123.6 | 195.1 / 226.9 | 2.45 | 2.09 | 5,668,789 | 69 | 39 | 0 | 245 |
| street@1750-blue-hour | 81.7 / 82.0 | 69.9 / 73.4 | 132.8 / 141.2 | 1.56 | 1.69 | 5,668,789 | 69 | 39 | 0 | 246 |
| into12@1750-blue-hour | 70.3 / 106.7 | 59.7 / 62.2 | 113.7 / 120.0 | 1.43 | 1.64 | 5,656,033 | 67 | 39 | 0 | 245 |
| high@1750-blue-hour | 84.7 / 110.3 | 71.8 / 75.6 | 119.2 / 146.1 | 1.51 | 1.71 | 5,656,033 | 67 | 39 | 0 | 246 |
| a-window@1750-blue-hour | 83.2 / 317.9 | 58.8 / 72.1 | 105.5 / 138.4 | 1.59 | 1.70 | 5,717,693 | 73 | 39 | 0 | 245 |
| steps@1750-blue-hour | 87.6 / 88.2 | 75.8 / 78.2 | 144.9 / 152.3 | 1.46 | 1.63 | 5,092,269 | 61 | 39 | 0 | 246 |
| row@1750-blue-hour | 63.2 / 145.4 | 53.7 / 65.7 | 101.0 / 124.8 | 1.43 | 1.66 | 5,717,693 | 73 | 39 | 0 | 245 |
| anchor-door@1750-blue-hour | 77.5 / 79.5 | 66.6 / 137.0 | 128.0 / 242.7 | 2.22 | 1.88 | 3,744,473 | 63 | 37 | 0 | 246 |
