# Frame time: the walk's corner in the town, run 2

2026-10-22 18:12:50, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 943 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eye-foot@1300-drizzle | 35.9 / 38.6 | 29.9 / 36.9 | 52.9 / 58.6 | 1.09 | 0.64 | 16,365,995 | 150 | 64 | 70 | 284 |
| eye-on@1300-drizzle | 39.9 / 43.9 | 33.7 / 40.3 | 58.4 / 65.9 | 1.09 | 0.66 | 16,016,023 | 146 | 63 | 66 | 284 |
| street@1300-drizzle | 41.0 / 47.4 | 35.6 / 43.7 | 62.3 / 72.4 | 0.88 | 0.57 | 15,753,079 | 150 | 65 | 70 | 284 |
| into12@1300-drizzle | 40.9 / 45.4 | 33.3 / 39.9 | 60.5 / 64.7 | 0.99 | 0.60 | 15,916,705 | 149 | 66 | 71 | 284 |
| high@1300-drizzle | 44.7 / 45.8 | 37.5 / 44.5 | 68.8 / 74.2 | 1.01 | 0.60 | 14,298,461 | 132 | 59 | 54 | 285 |
| a-window@1300-drizzle | 35.0 / 36.1 | 29.4 / 36.0 | 51.4 / 57.2 | 0.57 | 0.47 | 15,778,909 | 156 | 63 | 72 | 285 |
| steps@1300-drizzle | 31.2 / 32.4 | 25.5 / 32.7 | 45.3 / 50.5 | 0.91 | 0.57 | 15,210,799 | 122 | 52 | 56 | 285 |
| row@1300-drizzle | 33.3 / 37.3 | 28.7 / 37.5 | 49.8 / 58.6 | 0.94 | 0.60 | 15,525,263 | 155 | 62 | 71 | 285 |
| anchor-door@1300-drizzle | 23.7 / 24.2 | 20.7 / 25.8 | 36.7 / 42.8 | 0.84 | 0.54 | 11,382,303 | 125 | 52 | 53 | 285 |
| eye-foot@1600-low-sun | 101.7 / 102.8 | 86.1 / 94.9 | 164.2 / 173.2 | 1.08 | 0.62 | 16,790,295 | 160 | 67 | 79 | 285 |
| eye-on@1600-low-sun | 104.7 / 111.8 | 89.7 / 97.7 | 169.4 / 179.8 | 1.03 | 0.62 | 16,747,983 | 156 | 67 | 75 | 285 |
| street@1600-low-sun | 105.9 / 113.9 | 90.2 / 98.6 | 172.5 / 181.6 | 1.09 | 0.63 | 15,819,391 | 155 | 66 | 74 | 285 |
| into12@1600-low-sun | 102.2 / 106.2 | 87.6 / 94.3 | 167.9 / 176.3 | 1.01 | 0.61 | 16,001,305 | 154 | 67 | 75 | 285 |
| high@1600-low-sun | 106.5 / 107.8 | 91.1 / 97.0 | 175.5 / 182.9 | 1.09 | 0.65 | 14,346,913 | 135 | 60 | 56 | 285 |
| a-window@1600-low-sun | 97.9 / 99.6 | 83.6 / 89.3 | 159.7 / 166.4 | 1.06 | 0.60 | 15,827,361 | 159 | 64 | 74 | 285 |
| steps@1600-low-sun | 94.2 / 99.4 | 80.0 / 86.0 | 153.7 / 160.0 | 1.05 | 0.60 | 15,255,123 | 125 | 53 | 58 | 286 |
| row@1600-low-sun | 97.2 / 99.2 | 86.0 / 95.5 | 158.7 / 179.2 | 1.05 | 0.62 | 15,549,263 | 156 | 63 | 71 | 286 |
| anchor-door@1600-low-sun | 87.5 / 91.8 | 75.4 / 79.0 | 145.2 / 151.3 | 1.08 | 0.62 | 11,395,725 | 125 | 53 | 52 | 286 |
| eye-foot@1600-low-sun-nobirch | 96.3 / 97.9 | 83.4 / 90.1 | 158.9 / 168.6 | 0.97 | 0.57 | 16,283,379 | 146 | 53 | 71 | 286 |
| eye-on@1600-low-sun-nobirch | 101.7 / 103.7 | 87.0 / 93.1 | 164.6 / 173.3 | 0.99 | 0.57 | 16,241,067 | 142 | 53 | 67 | 286 |
| street@1600-low-sun-nobirch | 91.9 / 93.5 | 78.2 / 84.5 | 150.5 / 156.8 | 1.02 | 0.59 | 15,312,475 | 141 | 52 | 66 | 286 |
| into12@1600-low-sun-nobirch | 91.5 / 94.8 | 80.2 / 86.5 | 153.9 / 162.1 | 1.06 | 0.61 | 15,494,389 | 140 | 53 | 67 | 286 |
| high@1600-low-sun-nobirch | 91.4 / 94.0 | 77.5 / 83.4 | 149.9 / 156.3 | 1.08 | 0.61 | 13,999,777 | 125 | 50 | 52 | 286 |
| a-window@1600-low-sun-nobirch | 95.4 / 96.6 | 80.7 / 87.2 | 153.4 / 161.8 | 1.19 | 0.65 | 15,400,335 | 147 | 52 | 68 | 286 |
| steps@1600-low-sun-nobirch | 96.8 / 100.9 | 80.4 / 87.2 | 153.2 / 161.6 | 0.83 | 0.52 | 15,255,123 | 125 | 53 | 58 | 286 |
| row@1600-low-sun-nobirch | 91.3 / 95.1 | 78.4 / 85.2 | 150.2 / 159.5 | 1.09 | 0.62 | 15,122,237 | 144 | 51 | 65 | 287 |
| anchor-door@1600-low-sun-nobirch | 85.9 / 88.7 | 73.6 / 77.6 | 143.3 / 147.7 | 0.68 | 0.50 | 11,156,055 | 119 | 47 | 50 | 287 |
| eye-foot@1750-blue-hour | 28.7 / 29.4 | 25.7 / 28.2 | 47.5 / 52.5 | 0.40 | 0.40 | 5,832,151 | 80 | 50 | 0 | 287 |
| eye-on@1750-blue-hour | 32.6 / 34.4 | 29.6 / 32.1 | 52.6 / 60.4 | 0.57 | 0.44 | 5,832,151 | 80 | 50 | 0 | 287 |
| street@1750-blue-hour | 31.7 / 34.2 | 28.5 / 31.3 | 52.1 / 58.4 | 0.43 | 0.44 | 5,832,151 | 80 | 50 | 0 | 287 |
| into12@1750-blue-hour | 32.1 / 33.8 | 27.7 / 29.5 | 51.7 / 56.3 | 0.46 | 0.42 | 5,819,395 | 78 | 50 | 0 | 287 |
| high@1750-blue-hour | 36.7 / 37.1 | 32.0 / 33.7 | 60.1 / 64.9 | 0.59 | 0.45 | 5,819,395 | 78 | 50 | 0 | 287 |
| a-window@1750-blue-hour | 28.0 / 28.7 | 24.6 / 26.6 | 44.9 / 49.5 | 0.48 | 0.43 | 5,881,055 | 84 | 50 | 0 | 287 |
| steps@1750-blue-hour | 25.5 / 25.8 | 22.5 / 24.4 | 41.7 / 45.6 | 0.42 | 0.40 | 5,068,275 | 66 | 44 | 0 | 287 |
| row@1750-blue-hour | 26.6 / 27.2 | 23.5 / 26.0 | 43.4 / 47.6 | 0.83 | 0.54 | 5,881,055 | 84 | 50 | 0 | 287 |
| anchor-door@1750-blue-hour | 19.6 / 20.1 | 17.5 / 18.3 | 32.5 / 35.0 | 0.75 | 0.49 | 3,880,259 | 72 | 46 | 0 | 287 |
