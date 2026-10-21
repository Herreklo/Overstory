# Frame time: the corner, run 1

2026-10-21 18:59:45, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 657 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eye-foot@1300-drizzle | 33.5 / 35.4 | 28.0 / 34.1 | 49.6 / 54.8 | 0.94 | 0.58 | 15,518,343 | 142 | 64 | 66 | 231 |
| eye-on@1300-drizzle | 38.2 / 39.4 | 31.7 / 37.7 | 55.9 / 62.3 | 0.99 | 0.61 | 15,217,280 | 139 | 63 | 63 | 232 |
| street@1300-drizzle | 39.0 / 39.9 | 32.3 / 37.9 | 58.0 / 63.1 | 0.83 | 0.54 | 15,012,472 | 142 | 65 | 66 | 232 |
| into12@1300-drizzle | 38.8 / 39.8 | 32.1 / 37.7 | 58.4 / 62.2 | 0.87 | 0.56 | 15,144,932 | 143 | 66 | 67 | 233 |
| high@1300-drizzle | 43.0 / 47.4 | 35.9 / 41.0 | 66.2 / 70.5 | 1.04 | 0.62 | 13,805,321 | 130 | 59 | 54 | 232 |
| birch12@1300-drizzle | 50.4 / 51.8 | 42.3 / 48.0 | 77.4 / 82.5 | 0.99 | 0.59 | 15,012,472 | 142 | 65 | 66 | 233 |
| eye-foot@1600-low-sun | 97.8 / 99.0 | 84.0 / 89.8 | 161.1 / 166.9 | 0.99 | 0.59 | 15,852,678 | 147 | 67 | 70 | 232 |
| eye-on@1600-low-sun | 102.1 / 103.1 | 87.5 / 93.2 | 166.3 / 173.6 | 0.69 | 0.51 | 15,852,678 | 147 | 67 | 70 | 233 |
| street@1600-low-sun | 102.0 / 102.6 | 86.7 / 91.7 | 166.8 / 172.3 | 0.77 | 0.52 | 15,036,472 | 143 | 66 | 66 | 232 |
| into12@1600-low-sun | 101.2 / 102.0 | 86.5 / 92.7 | 166.9 / 172.8 | 1.04 | 0.61 | 15,168,932 | 144 | 67 | 67 | 233 |
| high@1600-low-sun | 105.3 / 107.1 | 89.6 / 94.7 | 173.5 / 178.7 | 1.03 | 0.63 | 13,829,321 | 131 | 60 | 54 | 232 |
| birch12@1600-low-sun | 113.4 / 115.2 | 96.3 / 101.5 | 185.7 / 191.7 | 0.80 | 0.52 | 15,036,472 | 143 | 66 | 66 | 233 |
| eye-foot@1600-low-sun-nobirch | 95.7 / 97.3 | 81.5 / 87.3 | 156.7 / 162.6 | 1.07 | 0.62 | 15,345,762 | 133 | 53 | 62 | 232 |
| eye-on@1600-low-sun-nobirch | 101.7 / 103.1 | 86.8 / 92.6 | 165.5 / 173.2 | 1.07 | 0.62 | 15,345,762 | 133 | 53 | 62 | 233 |
| street@1600-low-sun-nobirch | 89.3 / 90.3 | 76.5 / 82.0 | 147.5 / 152.8 | 1.10 | 0.64 | 14,529,556 | 129 | 52 | 58 | 232 |
| into12@1600-low-sun-nobirch | 91.4 / 99.4 | 77.8 / 83.1 | 150.0 / 155.3 | 0.89 | 0.55 | 14,662,016 | 130 | 53 | 59 | 234 |
| high@1600-low-sun-nobirch | 89.5 / 89.9 | 76.5 / 81.5 | 148.1 / 153.0 | 0.98 | 0.56 | 13,482,185 | 121 | 50 | 50 | 233 |
| birch12@1600-low-sun-nobirch | 88.8 / 89.6 | 75.6 / 80.6 | 146.2 / 151.0 | 0.91 | 0.54 | 14,529,556 | 129 | 52 | 58 | 234 |
| eye-foot@1750-blue-hour | 27.2 / 32.6 | 25.3 / 29.4 | 46.2 / 54.2 | 0.83 | 0.52 | 5,490,395 | 76 | 50 | 0 | 233 |
| eye-on@1750-blue-hour | 32.1 / 32.7 | 28.9 / 31.9 | 51.4 / 60.0 | 0.69 | 0.46 | 5,490,395 | 76 | 50 | 0 | 234 |
| street@1750-blue-hour | 31.2 / 32.7 | 27.0 / 29.0 | 50.4 / 54.8 | 0.94 | 0.58 | 5,490,395 | 76 | 50 | 0 | 233 |
| into12@1750-blue-hour | 30.7 / 31.3 | 26.6 / 28.1 | 50.0 / 53.6 | 0.94 | 0.57 | 5,490,395 | 76 | 50 | 0 | 234 |
| high@1750-blue-hour | 34.6 / 35.2 | 30.5 / 31.9 | 57.4 / 61.6 | 0.92 | 0.56 | 5,490,395 | 76 | 50 | 0 | 233 |
| birch12@1750-blue-hour | 40.1 / 40.8 | 34.8 / 36.1 | 65.5 / 70.4 | 0.84 | 0.52 | 5,490,395 | 76 | 50 | 0 | 234 |
