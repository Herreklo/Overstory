# Frame time: the walk's corner in the town, run 1

2026-10-22 20:06:20, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 687 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eye-foot@1600-low-sun | 36.3 / 38.6 | 29.9 / 38.3 | 54.0 / 57.9 | 1.22 | 0.71 | 16,293,941 | 154 | 55 | 75 | 243 |
| eye-on@1600-low-sun | 41.1 / 44.3 | 37.1 / 44.2 | 49.0 / 64.7 | 1.18 | 0.71 | 16,251,629 | 150 | 55 | 71 | 244 |
| street@1600-low-sun | 31.7 / 33.4 | 27.1 / 33.2 | 37.4 / 48.2 | 1.18 | 0.70 | 15,323,037 | 149 | 54 | 70 | 243 |
| into12@1600-low-sun | 30.2 / 31.9 | 26.6 / 32.9 | 39.6 / 48.8 | 1.22 | 0.72 | 15,504,951 | 148 | 55 | 71 | 244 |
| high@1600-low-sun | 28.5 / 30.8 | 24.5 / 29.7 | 43.6 / 47.1 | 1.20 | 0.70 | 14,006,819 | 131 | 52 | 54 | 243 |
| a-window@1600-low-sun | 31.8 / 35.1 | 27.8 / 34.1 | 41.9 / 48.6 | 1.20 | 0.71 | 15,409,137 | 154 | 54 | 71 | 245 |
| steps@1600-low-sun | 33.9 / 35.4 | 27.6 / 34.5 | 49.4 / 54.4 | 1.24 | 0.71 | 15,255,125 | 127 | 55 | 58 | 244 |
| row@1600-low-sun | 30.7 / 32.2 | 25.4 / 33.5 | 38.2 / 47.2 | 1.23 | 0.72 | 15,131,039 | 151 | 53 | 68 | 245 |
| anchor-door@1600-low-sun | 26.3 / 27.2 | 22.4 / 25.4 | 31.0 / 40.5 | 1.17 | 0.68 | 11,161,337 | 124 | 49 | 51 | 244 |
| eye-foot@1600-low-sun-nobirch | 36.1 / 49.7 | 32.3 / 37.8 | 50.7 / 59.3 | 1.24 | 0.72 | 16,283,381 | 148 | 55 | 71 | 245 |
| eye-on@1600-low-sun-nobirch | 42.7 / 44.5 | 36.0 / 42.8 | 63.2 / 65.8 | 1.26 | 0.73 | 16,241,069 | 144 | 55 | 67 | 244 |
| street@1600-low-sun-nobirch | 32.3 / 32.9 | 26.8 / 32.8 | 41.9 / 50.5 | 1.24 | 0.72 | 15,312,477 | 143 | 54 | 66 | 245 |
| into12@1600-low-sun-nobirch | 33.1 / 34.1 | 26.4 / 33.2 | 47.3 / 51.8 | 1.20 | 0.70 | 15,494,391 | 142 | 55 | 67 | 244 |
| high@1600-low-sun-nobirch | 30.5 / 31.4 | 25.3 / 31.0 | 34.2 / 46.0 | 1.16 | 0.67 | 13,999,779 | 127 | 52 | 52 | 245 |
| a-window@1600-low-sun-nobirch | 32.5 / 35.3 | 29.4 / 33.7 | 43.5 / 50.1 | 1.19 | 0.71 | 15,400,337 | 149 | 54 | 68 | 244 |
| steps@1600-low-sun-nobirch | 32.0 / 34.7 | 27.2 / 32.3 | 47.7 / 51.2 | 1.21 | 0.71 | 15,255,125 | 127 | 55 | 58 | 245 |
| row@1600-low-sun-nobirch | 31.0 / 34.2 | 26.0 / 34.3 | 38.5 / 47.4 | 1.28 | 0.74 | 15,122,239 | 146 | 53 | 65 | 244 |
| anchor-door@1600-low-sun-nobirch | 25.4 / 31.8 | 21.7 / 29.0 | 34.4 / 43.4 | 1.24 | 0.70 | 11,156,057 | 121 | 49 | 50 | 246 |
| eye-foot@1600-low-sun/beams-full | 97.6 / 102.1 | 83.2 / 91.8 | 158.9 / 168.5 | 1.33 | 0.71 | 16,293,939 | 152 | 53 | 75 | 245 |
| eye-on@1600-low-sun/beams-full | 98.1 / 107.9 | 86.9 / 93.8 | 163.2 / 174.3 | 1.23 | 0.70 | 16,251,627 | 148 | 53 | 71 | 246 |
| street@1600-low-sun/beams-full | 88.4 / 92.8 | 75.7 / 84.8 | 142.8 / 157.4 | 1.07 | 0.63 | 15,323,035 | 147 | 52 | 70 | 245 |
| into12@1600-low-sun/beams-full | 86.5 / 88.2 | 74.0 / 79.6 | 141.4 / 148.1 | 0.62 | 0.48 | 15,504,949 | 146 | 53 | 71 | 246 |
| high@1600-low-sun/beams-full | 85.1 / 86.5 | 72.8 / 78.7 | 139.6 / 147.7 | 1.11 | 0.63 | 14,006,817 | 129 | 50 | 54 | 245 |
| a-window@1600-low-sun/beams-full | 89.5 / 96.1 | 77.3 / 85.9 | 144.0 / 158.0 | 1.24 | 0.68 | 15,409,135 | 152 | 52 | 71 | 246 |
| steps@1600-low-sun/beams-full | 89.2 / 95.0 | 78.5 / 86.0 | 144.9 / 158.1 | 1.13 | 0.65 | 15,255,123 | 125 | 53 | 58 | 245 |
| row@1600-low-sun/beams-full | 85.7 / 96.0 | 76.7 / 84.7 | 141.0 / 154.8 | 1.22 | 0.67 | 15,131,037 | 149 | 51 | 68 | 246 |
| anchor-door@1600-low-sun/beams-full | 85.1 / 91.5 | 73.2 / 79.4 | 136.3 / 151.3 | 1.17 | 0.66 | 11,161,335 | 122 | 47 | 51 | 245 |
| eye-foot@1600-low-sun/-beams | 34.0 / 37.4 | 28.8 / 36.4 | 50.3 / 57.6 | 1.13 | 0.66 | 16,293,937 | 150 | 51 | 75 | 247 |
| eye-on@1600-low-sun/-beams | 39.8 / 45.6 | 34.4 / 42.9 | 59.7 / 68.7 | 1.26 | 0.72 | 16,251,625 | 146 | 51 | 71 | 246 |
| street@1600-low-sun/-beams | 29.5 / 30.6 | 24.5 / 31.2 | 42.2 / 48.1 | 1.20 | 0.70 | 15,323,033 | 145 | 50 | 70 | 246 |
| into12@1600-low-sun/-beams | 29.1 / 30.8 | 23.9 / 30.7 | 41.8 / 47.0 | 1.16 | 0.69 | 15,504,947 | 144 | 51 | 71 | 246 |
| high@1600-low-sun/-beams | 27.3 / 29.2 | 22.6 / 28.6 | 39.9 / 45.0 | 1.20 | 0.69 | 14,006,815 | 127 | 48 | 54 | 246 |
| a-window@1600-low-sun/-beams | 30.5 / 32.4 | 26.6 / 34.5 | 44.0 / 55.9 | 1.17 | 0.70 | 15,409,133 | 150 | 50 | 71 | 246 |
| steps@1600-low-sun/-beams | 30.9 / 33.3 | 25.1 / 32.4 | 44.3 / 49.5 | 1.18 | 0.69 | 15,255,121 | 123 | 51 | 58 | 246 |
| row@1600-low-sun/-beams | 28.7 / 30.5 | 24.1 / 31.3 | 41.5 / 47.9 | 1.21 | 0.70 | 15,131,035 | 147 | 49 | 68 | 246 |
| anchor-door@1600-low-sun/-beams | 23.9 / 25.5 | 20.2 / 24.5 | 36.0 / 40.3 | 1.17 | 0.67 | 11,161,333 | 120 | 45 | 51 | 246 |
