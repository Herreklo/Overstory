# Frame time: the walk's corner in the town, run 2

2026-10-22 21:07:56, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 3 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 870 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eye-foot@1600-low-sun | 38.3 / 41.1 | 30.9 / 41.4 | 44.7 / 57.8 | 1.24 | 0.77 | 16,283,381 | 148 | 55 | 71 | 242 |
| eye-on@1600-low-sun | 42.5 / 45.5 | 35.6 / 45.1 | 49.4 / 64.1 | 1.11 | 0.72 | 16,241,069 | 144 | 55 | 67 | 243 |
| street@1600-low-sun | 30.6 / 32.8 | 25.0 / 33.4 | 37.8 / 46.9 | 1.12 | 0.71 | 15,312,477 | 143 | 54 | 66 | 242 |
| into12@1600-low-sun | 31.5 / 33.2 | 26.0 / 33.1 | 38.6 / 48.5 | 1.16 | 0.74 | 15,494,391 | 142 | 55 | 67 | 243 |
| high@1600-low-sun | 29.0 / 31.5 | 26.5 / 27.8 | 40.8 / 49.5 | 1.28 | 0.76 | 13,999,779 | 127 | 52 | 52 | 242 |
| a-window@1600-low-sun | 32.4 / 35.3 | 26.5 / 29.2 | 47.9 / 50.0 | 1.26 | 0.76 | 15,400,337 | 149 | 54 | 68 | 243 |
| steps@1600-low-sun | 34.4 / 35.2 | 26.9 / 36.2 | 39.5 / 50.7 | 1.15 | 0.73 | 15,255,125 | 127 | 55 | 58 | 242 |
| row@1600-low-sun | 31.7 / 32.8 | 25.2 / 34.2 | 39.1 / 47.0 | 1.18 | 0.75 | 15,122,239 | 146 | 53 | 65 | 244 |
| anchor-door@1600-low-sun | 25.9 / 26.9 | 22.5 / 26.5 | 30.0 / 40.2 | 1.07 | 0.68 | 11,156,057 | 121 | 49 | 50 | 243 |
| eye-foot@1600-low-sun/beams-full | 90.3 / 96.5 | 79.8 / 88.0 | 148.7 / 162.4 | 0.75 | 0.51 | 16,283,379 | 146 | 53 | 71 | 243 |
| eye-on@1600-low-sun/beams-full | 102.0 / 105.6 | 84.1 / 92.9 | 155.7 / 172.2 | 0.99 | 0.63 | 16,241,067 | 142 | 53 | 67 | 243 |
| street@1600-low-sun/beams-full | 85.1 / 101.6 | 76.6 / 84.8 | 141.5 / 155.6 | 1.06 | 0.66 | 15,312,475 | 141 | 52 | 66 | 244 |
| into12@1600-low-sun/beams-full | 87.6 / 113.2 | 76.1 / 118.5 | 142.3 / 204.5 | 1.15 | 0.71 | 15,494,389 | 140 | 53 | 67 | 243 |
| high@1600-low-sun/beams-full | 87.9 / 121.6 | 77.4 / 133.6 | 145.3 / 217.2 | 1.23 | 0.72 | 13,999,777 | 125 | 50 | 52 | 244 |
| a-window@1600-low-sun/beams-full | 94.0 / 118.5 | 79.2 / 140.7 | 145.4 / 213.3 | 1.22 | 0.72 | 15,400,335 | 147 | 52 | 68 | 243 |
| steps@1600-low-sun/beams-full | 93.4 / 113.2 | 82.0 / 129.4 | 151.2 / 208.8 | 1.27 | 0.77 | 15,255,123 | 125 | 53 | 58 | 244 |
| row@1600-low-sun/beams-full | 95.4 / 105.8 | 78.1 / 92.4 | 144.8 / 199.4 | 1.26 | 0.73 | 15,122,237 | 144 | 51 | 65 | 243 |
| anchor-door@1600-low-sun/beams-full | 92.7 / 106.8 | 77.3 / 97.0 | 139.4 / 194.5 | 1.18 | 0.70 | 11,156,055 | 119 | 47 | 50 | 245 |
| eye-foot@1600-low-sun/-beams | 35.7 / 39.3 | 29.5 / 38.5 | 51.7 / 59.0 | 1.15 | 0.70 | 16,283,377 | 144 | 51 | 71 | 244 |
| eye-on@1600-low-sun/-beams | 42.1 / 45.5 | 35.2 / 44.3 | 57.8 / 70.4 | 1.23 | 0.73 | 16,241,065 | 140 | 51 | 67 | 244 |
| street@1600-low-sun/-beams | 31.1 / 32.8 | 24.8 / 34.4 | 42.8 / 50.2 | 1.25 | 0.73 | 15,312,473 | 139 | 50 | 66 | 244 |
| into12@1600-low-sun/-beams | 32.0 / 33.7 | 26.1 / 34.3 | 42.4 / 51.3 | 1.18 | 0.73 | 15,494,387 | 138 | 51 | 67 | 244 |
| high@1600-low-sun/-beams | 29.7 / 31.6 | 24.4 / 31.7 | 42.4 / 49.4 | 1.21 | 0.70 | 13,999,775 | 123 | 48 | 52 | 244 |
| a-window@1600-low-sun/-beams | 32.3 / 34.8 | 26.4 / 34.4 | 43.8 / 52.5 | 1.20 | 0.73 | 15,400,333 | 145 | 50 | 68 | 244 |
| steps@1600-low-sun/-beams | 32.5 / 34.5 | 26.2 / 34.7 | 45.2 / 52.5 | 1.21 | 0.76 | 15,255,121 | 123 | 51 | 58 | 244 |
| row@1600-low-sun/-beams | 28.8 / 33.3 | 24.2 / 32.1 | 41.1 / 48.0 | 1.17 | 0.73 | 15,122,235 | 142 | 49 | 65 | 244 |
| anchor-door@1600-low-sun/-beams | 24.1 / 28.2 | 20.7 / 26.2 | 35.7 / 41.7 | 1.17 | 0.70 | 11,156,053 | 117 | 45 | 50 | 244 |
