# Frame time: the walk's corner in the town, run 1

2026-10-22 17:56:39, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 964 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eye-foot@1300-drizzle | 36.4 / 39.0 | 30.2 / 38.0 | 52.5 / 59.7 | 1.13 | 0.70 | 16,365,995 | 150 | 64 | 70 | 285 |
| eye-on@1300-drizzle | 38.8 / 42.7 | 33.1 / 39.4 | 56.9 / 65.1 | 1.03 | 0.66 | 16,016,023 | 146 | 63 | 66 | 285 |
| street@1300-drizzle | 42.5 / 47.8 | 34.6 / 41.3 | 59.9 / 70.9 | 1.08 | 0.67 | 15,753,079 | 150 | 65 | 70 | 285 |
| into12@1300-drizzle | 40.7 / 45.0 | 33.7 / 42.3 | 59.6 / 67.8 | 1.11 | 0.69 | 15,916,705 | 149 | 66 | 71 | 285 |
| high@1300-drizzle | 43.2 / 47.0 | 36.7 / 43.3 | 66.2 / 73.9 | 1.14 | 0.70 | 14,298,461 | 132 | 59 | 54 | 285 |
| a-window@1300-drizzle | 36.2 / 39.2 | 30.3 / 38.4 | 52.0 / 61.8 | 1.10 | 0.67 | 15,778,909 | 156 | 63 | 72 | 285 |
| steps@1300-drizzle | 30.7 / 34.9 | 25.9 / 33.5 | 45.8 / 51.8 | 1.08 | 0.65 | 15,210,799 | 122 | 52 | 56 | 285 |
| row@1300-drizzle | 33.9 / 36.0 | 28.8 / 36.0 | 50.0 / 57.3 | 1.09 | 0.67 | 15,525,263 | 155 | 62 | 71 | 285 |
| anchor-door@1300-drizzle | 24.8 / 26.9 | 21.0 / 25.2 | 37.6 / 41.5 | 1.02 | 0.64 | 11,382,303 | 125 | 52 | 53 | 285 |
| eye-foot@1600-low-sun | 104.1 / 108.3 | 88.0 / 96.5 | 164.8 / 178.1 | 1.19 | 0.72 | 16,790,295 | 160 | 67 | 79 | 285 |
| eye-on@1600-low-sun | 104.8 / 110.5 | 93.7 / 103.5 | 171.3 / 195.2 | 1.16 | 0.69 | 16,747,983 | 156 | 67 | 75 | 286 |
| street@1600-low-sun | 104.0 / 111.3 | 92.5 / 100.3 | 169.9 / 187.9 | 0.98 | 0.64 | 15,819,391 | 155 | 66 | 74 | 286 |
| into12@1600-low-sun | 102.3 / 113.6 | 91.1 / 98.5 | 167.2 / 185.4 | 0.91 | 0.61 | 16,001,305 | 154 | 67 | 75 | 286 |
| high@1600-low-sun | 108.1 / 119.4 | 96.6 / 105.6 | 179.2 / 199.5 | 1.12 | 0.72 | 14,346,913 | 135 | 60 | 56 | 286 |
| a-window@1600-low-sun | 98.3 / 109.8 | 87.7 / 95.3 | 161.0 / 180.3 | 1.11 | 0.71 | 15,827,361 | 159 | 64 | 74 | 286 |
| steps@1600-low-sun | 104.3 / 114.1 | 86.8 / 103.6 | 165.3 / 197.3 | 1.16 | 0.75 | 15,255,123 | 125 | 53 | 58 | 286 |
| row@1600-low-sun | 101.2 / 109.5 | 88.5 / 97.2 | 164.1 / 182.0 | 1.13 | 0.72 | 15,549,263 | 156 | 63 | 71 | 286 |
| anchor-door@1600-low-sun | 85.9 / 87.1 | 74.3 / 79.0 | 143.4 / 150.6 | 1.10 | 0.72 | 11,395,725 | 125 | 53 | 52 | 286 |
| eye-foot@1600-low-sun-nobirch | 93.0 / 105.9 | 80.8 / 88.6 | 149.3 / 163.9 | 1.08 | 0.69 | 16,283,379 | 146 | 53 | 71 | 286 |
| eye-on@1600-low-sun-nobirch | 97.8 / 111.0 | 90.8 / 101.6 | 161.1 / 190.4 | 1.12 | 0.68 | 16,241,067 | 142 | 53 | 67 | 286 |
| street@1600-low-sun-nobirch | 92.6 / 102.1 | 83.2 / 91.9 | 150.9 / 170.4 | 1.15 | 0.67 | 15,312,475 | 141 | 52 | 66 | 287 |
| into12@1600-low-sun-nobirch | 91.7 / 106.0 | 83.1 / 91.7 | 146.4 / 171.3 | 1.12 | 0.68 | 15,494,389 | 140 | 53 | 67 | 287 |
| high@1600-low-sun-nobirch | 88.3 / 101.0 | 84.2 / 93.4 | 148.5 / 174.7 | 1.19 | 0.68 | 13,999,777 | 125 | 50 | 52 | 287 |
| a-window@1600-low-sun-nobirch | 90.7 / 102.4 | 83.4 / 92.5 | 148.6 / 173.4 | 1.17 | 0.68 | 15,400,335 | 147 | 52 | 68 | 287 |
| steps@1600-low-sun-nobirch | 90.8 / 102.9 | 82.2 / 93.9 | 149.5 / 175.6 | 1.19 | 0.69 | 15,255,123 | 125 | 53 | 58 | 287 |
| row@1600-low-sun-nobirch | 90.8 / 96.6 | 82.2 / 90.2 | 149.1 / 168.7 | 1.14 | 0.67 | 15,122,237 | 144 | 51 | 65 | 287 |
| anchor-door@1600-low-sun-nobirch | 87.0 / 94.0 | 78.9 / 84.8 | 140.3 / 162.6 | 1.13 | 0.65 | 11,156,055 | 119 | 47 | 50 | 287 |
| eye-foot@1750-blue-hour | 31.2 / 33.9 | 26.5 / 29.4 | 48.9 / 54.5 | 1.09 | 0.66 | 5,832,151 | 80 | 50 | 0 | 287 |
| eye-on@1750-blue-hour | 34.5 / 35.8 | 31.6 / 36.0 | 56.1 / 66.3 | 1.11 | 0.64 | 5,832,151 | 80 | 50 | 0 | 287 |
| street@1750-blue-hour | 34.2 / 35.8 | 29.8 / 33.2 | 54.9 / 61.8 | 0.97 | 0.62 | 5,832,151 | 80 | 50 | 0 | 287 |
| into12@1750-blue-hour | 31.7 / 33.6 | 28.7 / 31.0 | 52.3 / 59.9 | 0.95 | 0.60 | 5,819,395 | 78 | 50 | 0 | 287 |
| high@1750-blue-hour | 36.4 / 37.2 | 31.7 / 33.7 | 59.4 / 64.3 | 0.92 | 0.59 | 5,819,395 | 78 | 50 | 0 | 288 |
| a-window@1750-blue-hour | 27.9 / 30.6 | 24.7 / 27.0 | 44.4 / 50.0 | 1.01 | 0.63 | 5,881,055 | 84 | 50 | 0 | 287 |
| steps@1750-blue-hour | 25.4 / 28.1 | 22.6 / 25.4 | 41.7 / 47.8 | 1.01 | 0.62 | 5,068,275 | 66 | 44 | 0 | 288 |
| row@1750-blue-hour | 25.8 / 27.7 | 22.8 / 25.2 | 41.7 / 46.8 | 0.92 | 0.60 | 5,881,055 | 84 | 50 | 0 | 288 |
| anchor-door@1750-blue-hour | 19.7 / 21.2 | 17.2 / 19.2 | 31.6 / 37.0 | 0.97 | 0.61 | 3,880,259 | 72 | 46 | 0 | 288 |
