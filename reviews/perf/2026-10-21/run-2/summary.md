# Frame time: the corner, run 2

2026-10-21 19:11:07, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 662 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eye-foot@1300-drizzle | 34.9 / 39.6 | 28.6 / 34.5 | 50.8 / 56.5 | 0.99 | 0.61 | 15,518,343 | 142 | 64 | 66 | 231 |
| eye-on@1300-drizzle | 38.6 / 40.5 | 33.4 / 42.1 | 56.6 / 67.1 | 0.98 | 0.61 | 15,217,280 | 139 | 63 | 63 | 233 |
| street@1300-drizzle | 39.5 / 41.3 | 32.8 / 39.1 | 58.6 / 65.2 | 0.69 | 0.51 | 15,012,472 | 142 | 65 | 66 | 232 |
| into12@1300-drizzle | 39.3 / 40.7 | 33.8 / 40.7 | 59.1 / 69.6 | 1.03 | 0.62 | 15,144,932 | 143 | 66 | 67 | 233 |
| high@1300-drizzle | 43.1 / 44.8 | 36.9 / 42.4 | 67.1 / 73.2 | 1.08 | 0.64 | 13,805,321 | 130 | 59 | 54 | 232 |
| birch12@1300-drizzle | 50.2 / 51.3 | 43.5 / 50.4 | 77.8 / 89.6 | 1.04 | 0.62 | 15,012,472 | 142 | 65 | 66 | 233 |
| eye-foot@1600-low-sun | 97.9 / 99.3 | 83.7 / 89.7 | 160.8 / 166.0 | 1.08 | 0.63 | 15,852,678 | 147 | 67 | 70 | 232 |
| eye-on@1600-low-sun | 103.0 / 104.0 | 88.1 / 94.1 | 168.1 / 175.8 | 1.19 | 0.67 | 15,852,678 | 147 | 67 | 70 | 233 |
| street@1600-low-sun | 101.7 / 103.4 | 86.9 / 92.3 | 167.1 / 173.0 | 1.09 | 0.63 | 15,036,472 | 143 | 66 | 66 | 232 |
| into12@1600-low-sun | 101.4 / 103.3 | 86.1 / 91.1 | 166.2 / 170.5 | 0.62 | 0.49 | 15,168,932 | 144 | 67 | 67 | 233 |
| high@1600-low-sun | 105.0 / 107.3 | 89.5 / 94.4 | 173.6 / 178.9 | 1.00 | 0.61 | 13,829,321 | 131 | 60 | 54 | 232 |
| birch12@1600-low-sun | 113.5 / 116.6 | 96.2 / 101.1 | 185.7 / 191.0 | 1.01 | 0.61 | 15,036,472 | 143 | 66 | 66 | 234 |
| eye-foot@1600-low-sun-nobirch | 95.8 / 97.7 | 81.7 / 87.5 | 157.0 / 163.1 | 1.13 | 0.64 | 15,345,762 | 133 | 53 | 62 | 233 |
| eye-on@1600-low-sun-nobirch | 101.7 / 104.3 | 86.8 / 93.0 | 165.5 / 174.1 | 1.00 | 0.61 | 15,345,762 | 133 | 53 | 62 | 234 |
| street@1600-low-sun-nobirch | 89.1 / 90.7 | 76.3 / 82.1 | 147.1 / 153.1 | 0.99 | 0.58 | 14,529,556 | 129 | 52 | 58 | 233 |
| into12@1600-low-sun-nobirch | 91.2 / 98.8 | 78.9 / 87.8 | 150.8 / 162.2 | 0.99 | 0.61 | 14,662,016 | 130 | 53 | 59 | 234 |
| high@1600-low-sun-nobirch | 89.6 / 90.8 | 76.5 / 81.8 | 148.1 / 154.5 | 1.18 | 0.63 | 13,482,185 | 121 | 50 | 50 | 233 |
| birch12@1600-low-sun-nobirch | 90.1 / 96.3 | 75.6 / 81.0 | 146.3 / 150.9 | 1.08 | 0.63 | 14,529,556 | 129 | 52 | 58 | 234 |
| eye-foot@1750-blue-hour | 29.1 / 30.2 | 26.0 / 28.7 | 47.7 / 53.0 | 1.10 | 0.63 | 5,490,395 | 76 | 50 | 0 | 233 |
| eye-on@1750-blue-hour | 32.9 / 35.8 | 29.7 / 32.6 | 53.0 / 60.4 | 1.04 | 0.60 | 5,490,395 | 76 | 50 | 0 | 234 |
| street@1750-blue-hour | 31.0 / 31.8 | 27.3 / 29.5 | 50.9 / 55.6 | 0.87 | 0.55 | 5,490,395 | 76 | 50 | 0 | 233 |
| into12@1750-blue-hour | 30.7 / 31.2 | 26.9 / 29.0 | 50.4 / 54.7 | 0.94 | 0.57 | 5,490,395 | 76 | 50 | 0 | 234 |
| high@1750-blue-hour | 34.7 / 37.9 | 30.9 / 34.7 | 57.8 / 65.8 | 0.92 | 0.57 | 5,490,395 | 76 | 50 | 0 | 233 |
| birch12@1750-blue-hour | 40.6 / 41.1 | 35.5 / 38.4 | 66.4 / 72.6 | 0.97 | 0.59 | 5,490,395 | 76 | 50 | 0 | 235 |
