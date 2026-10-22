# Frame time: the walk's corner in the town, run 2

2026-10-22 20:18:10, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 690 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eye-foot@1600-low-sun | 35.8 / 37.7 | 32.4 / 36.1 | 49.7 / 60.4 | 1.16 | 0.69 | 16,293,941 | 154 | 55 | 75 | 243 |
| eye-on@1600-low-sun | 40.3 / 43.0 | 36.3 / 39.2 | 61.5 / 66.8 | 1.14 | 0.69 | 16,251,629 | 150 | 55 | 71 | 244 |
| street@1600-low-sun | 29.6 / 34.5 | 25.5 / 32.5 | 36.9 / 46.9 | 1.16 | 0.70 | 15,323,037 | 149 | 54 | 70 | 243 |
| into12@1600-low-sun | 30.5 / 32.5 | 24.7 / 32.9 | 44.2 / 46.6 | 1.25 | 0.73 | 15,504,951 | 148 | 55 | 71 | 244 |
| high@1600-low-sun | 28.8 / 34.3 | 25.0 / 31.6 | 36.0 / 44.4 | 1.17 | 0.69 | 14,006,819 | 131 | 52 | 54 | 244 |
| a-window@1600-low-sun | 33.0 / 35.3 | 28.8 / 34.9 | 42.1 / 50.5 | 1.26 | 0.74 | 15,409,137 | 154 | 54 | 71 | 245 |
| steps@1600-low-sun | 33.3 / 35.0 | 29.7 / 32.3 | 44.4 / 53.8 | 1.26 | 0.74 | 15,255,125 | 127 | 55 | 58 | 244 |
| row@1600-low-sun | 29.6 / 33.7 | 27.3 / 29.5 | 45.0 / 51.4 | 1.26 | 0.73 | 15,131,039 | 151 | 53 | 68 | 245 |
| anchor-door@1600-low-sun | 24.7 / 28.4 | 21.7 / 28.4 | 33.7 / 42.4 | 1.25 | 0.70 | 11,161,337 | 124 | 49 | 51 | 244 |
| eye-foot@1600-low-sun-nobirch | 36.7 / 40.5 | 30.0 / 40.2 | 54.4 / 57.2 | 1.32 | 0.75 | 16,283,381 | 148 | 55 | 71 | 245 |
| eye-on@1600-low-sun-nobirch | 41.8 / 45.3 | 36.9 / 45.4 | 51.5 / 64.8 | 1.24 | 0.74 | 16,241,069 | 144 | 55 | 67 | 244 |
| street@1600-low-sun-nobirch | 31.7 / 33.9 | 28.7 / 32.8 | 42.1 / 50.8 | 1.22 | 0.73 | 15,312,477 | 143 | 54 | 66 | 245 |
| into12@1600-low-sun-nobirch | 32.0 / 32.3 | 28.0 / 31.9 | 47.5 / 51.9 | 1.19 | 0.72 | 15,494,391 | 142 | 55 | 67 | 244 |
| high@1600-low-sun-nobirch | 30.3 / 33.0 | 25.6 / 32.7 | 35.6 / 47.4 | 1.22 | 0.72 | 13,999,779 | 127 | 52 | 52 | 245 |
| a-window@1600-low-sun-nobirch | 31.7 / 37.4 | 27.4 / 37.1 | 41.0 / 50.1 | 1.30 | 0.75 | 15,400,337 | 149 | 54 | 68 | 244 |
| steps@1600-low-sun-nobirch | 33.2 / 36.2 | 27.1 / 37.1 | 49.6 / 51.8 | 1.29 | 0.77 | 15,255,125 | 127 | 55 | 58 | 246 |
| row@1600-low-sun-nobirch | 30.6 / 33.3 | 26.4 / 33.4 | 37.7 / 47.4 | 1.19 | 0.73 | 15,122,239 | 146 | 53 | 65 | 245 |
| anchor-door@1600-low-sun-nobirch | 25.8 / 26.6 | 22.9 / 25.1 | 32.6 / 42.3 | 1.16 | 0.69 | 11,156,057 | 121 | 49 | 50 | 245 |
| eye-foot@1600-low-sun/beams-full | 98.3 / 104.4 | 84.9 / 94.0 | 160.5 / 172.0 | 1.29 | 0.72 | 16,293,939 | 152 | 53 | 75 | 245 |
| eye-on@1600-low-sun/beams-full | 103.8 / 110.0 | 89.3 / 97.5 | 167.6 / 179.9 | 1.30 | 0.74 | 16,251,627 | 148 | 53 | 71 | 246 |
| street@1600-low-sun/beams-full | 93.4 / 102.9 | 81.0 / 89.2 | 151.8 / 165.7 | 1.24 | 0.72 | 15,323,035 | 147 | 52 | 70 | 245 |
| into12@1600-low-sun/beams-full | 91.9 / 99.7 | 78.4 / 89.8 | 149.9 / 166.7 | 1.19 | 0.70 | 15,504,949 | 146 | 53 | 71 | 246 |
| high@1600-low-sun/beams-full | 89.2 / 90.7 | 75.6 / 80.9 | 145.7 / 151.9 | 1.16 | 0.65 | 14,006,817 | 129 | 50 | 54 | 245 |
| a-window@1600-low-sun/beams-full | 89.0 / 92.4 | 77.8 / 84.4 | 146.7 / 156.3 | 1.05 | 0.63 | 15,409,135 | 152 | 52 | 71 | 246 |
| steps@1600-low-sun/beams-full | 91.8 / 93.0 | 78.4 / 85.3 | 149.9 / 157.5 | 1.21 | 0.71 | 15,255,123 | 125 | 53 | 58 | 245 |
| row@1600-low-sun/beams-full | 89.2 / 91.5 | 76.3 / 82.3 | 145.3 / 152.5 | 1.21 | 0.71 | 15,131,037 | 149 | 51 | 68 | 247 |
| anchor-door@1600-low-sun/beams-full | 85.1 / 86.9 | 71.9 / 75.7 | 139.3 / 143.7 | 1.19 | 0.68 | 11,161,335 | 122 | 47 | 51 | 246 |
| eye-foot@1600-low-sun/-beams | 33.4 / 34.6 | 27.7 / 34.4 | 49.1 / 53.9 | 1.13 | 0.68 | 16,293,937 | 150 | 51 | 75 | 247 |
| eye-on@1600-low-sun/-beams | 38.3 / 39.1 | 32.2 / 38.6 | 56.5 / 62.9 | 1.12 | 0.67 | 16,251,625 | 146 | 51 | 71 | 246 |
| street@1600-low-sun/-beams | 28.2 / 29.0 | 22.7 / 28.9 | 40.6 / 44.7 | 0.97 | 0.61 | 15,323,033 | 145 | 50 | 70 | 246 |
| into12@1600-low-sun/-beams | 28.1 / 28.9 | 23.1 / 28.5 | 40.2 / 44.8 | 1.00 | 0.61 | 15,504,947 | 144 | 51 | 71 | 246 |
| high@1600-low-sun/-beams | 26.0 / 26.9 | 21.3 / 26.3 | 38.0 / 41.8 | 1.01 | 0.59 | 14,006,815 | 127 | 48 | 54 | 246 |
| a-window@1600-low-sun/-beams | 29.7 / 30.6 | 24.8 / 30.6 | 42.8 / 48.7 | 1.15 | 0.69 | 15,409,133 | 150 | 50 | 71 | 246 |
| steps@1600-low-sun/-beams | 29.6 / 31.0 | 24.4 / 30.4 | 43.5 / 47.9 | 1.13 | 0.67 | 15,255,121 | 123 | 51 | 58 | 247 |
| row@1600-low-sun/-beams | 27.5 / 28.4 | 22.3 / 28.2 | 39.2 / 43.5 | 0.99 | 0.61 | 15,131,035 | 147 | 49 | 68 | 246 |
| anchor-door@1600-low-sun/-beams | 22.8 / 23.4 | 19.1 / 22.9 | 34.3 / 37.3 | 0.96 | 0.59 | 11,161,333 | 120 | 45 | 51 | 246 |
