# Frame time: the walk's corner in the town, run 1

2026-10-22 20:53:06, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 3 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 855 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eye-foot@1600-low-sun | 35.2 / 37.7 | 31.8 / 33.9 | 47.3 / 58.7 | 1.14 | 0.72 | 16,283,381 | 148 | 55 | 71 | 242 |
| eye-on@1600-low-sun | 40.0 / 45.0 | 34.5 / 37.6 | 61.9 / 65.4 | 1.19 | 0.76 | 16,241,069 | 144 | 55 | 67 | 243 |
| street@1600-low-sun | 30.6 / 37.0 | 24.5 / 33.6 | 43.7 / 47.0 | 1.11 | 0.71 | 15,312,477 | 143 | 54 | 66 | 242 |
| into12@1600-low-sun | 31.1 / 33.4 | 27.6 / 38.3 | 42.1 / 52.2 | 1.11 | 0.72 | 15,494,391 | 142 | 55 | 67 | 243 |
| high@1600-low-sun | 29.8 / 31.3 | 24.4 / 30.9 | 34.2 / 46.1 | 1.04 | 0.66 | 13,999,779 | 127 | 52 | 52 | 242 |
| a-window@1600-low-sun | 31.1 / 32.6 | 26.2 / 31.2 | 36.4 / 46.9 | 1.04 | 0.67 | 15,400,337 | 149 | 54 | 68 | 243 |
| steps@1600-low-sun | 31.1 / 33.8 | 27.6 / 28.8 | 42.3 / 51.1 | 1.10 | 0.70 | 15,255,125 | 127 | 55 | 58 | 242 |
| row@1600-low-sun | 30.2 / 32.8 | 24.9 / 27.5 | 45.5 / 48.3 | 1.17 | 0.72 | 15,122,239 | 146 | 53 | 65 | 243 |
| anchor-door@1600-low-sun | 26.3 / 27.6 | 21.8 / 27.1 | 29.1 / 40.1 | 1.05 | 0.67 | 11,156,057 | 121 | 49 | 50 | 243 |
| eye-foot@1600-low-sun/beams-full | 96.8 / 103.9 | 83.8 / 93.8 | 158.0 / 172.4 | 1.12 | 0.71 | 16,283,379 | 146 | 53 | 71 | 244 |
| eye-on@1600-low-sun/beams-full | 101.2 / 105.2 | 86.9 / 93.1 | 165.2 / 173.9 | 0.97 | 0.62 | 16,241,067 | 142 | 53 | 67 | 243 |
| street@1600-low-sun/beams-full | 90.1 / 101.5 | 75.3 / 82.3 | 142.3 / 152.7 | 0.82 | 0.55 | 15,312,475 | 141 | 52 | 66 | 244 |
| into12@1600-low-sun/beams-full | 92.4 / 105.1 | 76.9 / 87.5 | 144.8 / 167.9 | 1.04 | 0.67 | 15,494,389 | 140 | 53 | 67 | 243 |
| high@1600-low-sun/beams-full | 89.4 / 101.2 | 76.4 / 81.8 | 141.4 / 153.3 | 1.01 | 0.64 | 13,999,777 | 125 | 50 | 52 | 245 |
| a-window@1600-low-sun/beams-full | 93.7 / 103.7 | 79.0 / 86.1 | 149.8 / 158.1 | 1.16 | 0.72 | 15,400,335 | 147 | 52 | 68 | 244 |
| steps@1600-low-sun/beams-full | 98.2 / 105.3 | 83.1 / 95.0 | 153.9 / 175.2 | 1.22 | 0.78 | 15,255,123 | 125 | 53 | 58 | 245 |
| row@1600-low-sun/beams-full | 96.3 / 100.8 | 82.0 / 91.8 | 149.8 / 169.6 | 1.22 | 0.78 | 15,122,237 | 144 | 51 | 65 | 244 |
| anchor-door@1600-low-sun/beams-full | 93.4 / 96.1 | 79.4 / 85.8 | 147.3 / 162.7 | 1.22 | 0.77 | 11,156,055 | 119 | 47 | 50 | 245 |
| eye-foot@1600-low-sun/-beams | 36.1 / 38.3 | 30.3 / 38.3 | 52.7 / 58.9 | 1.24 | 0.76 | 16,283,377 | 144 | 51 | 71 | 244 |
| eye-on@1600-low-sun/-beams | 40.7 / 42.9 | 34.5 / 42.3 | 60.5 / 68.1 | 1.18 | 0.74 | 16,241,065 | 140 | 51 | 67 | 244 |
| street@1600-low-sun/-beams | 29.0 / 31.3 | 24.2 / 31.5 | 41.9 / 47.5 | 1.12 | 0.70 | 15,312,473 | 139 | 50 | 66 | 244 |
| into12@1600-low-sun/-beams | 30.2 / 32.0 | 24.8 / 31.9 | 44.0 / 49.4 | 1.05 | 0.66 | 15,494,387 | 138 | 51 | 67 | 244 |
| high@1600-low-sun/-beams | 28.7 / 30.8 | 23.6 / 30.1 | 40.8 / 47.2 | 1.08 | 0.65 | 13,999,775 | 123 | 48 | 52 | 245 |
| a-window@1600-low-sun/-beams | 29.7 / 33.2 | 25.2 / 32.8 | 43.3 / 50.6 | 1.14 | 0.71 | 15,400,333 | 145 | 50 | 68 | 244 |
| steps@1600-low-sun/-beams | 30.7 / 33.2 | 25.0 / 32.8 | 43.8 / 49.8 | 1.11 | 0.69 | 15,255,121 | 123 | 51 | 58 | 245 |
| row@1600-low-sun/-beams | 28.1 / 30.4 | 23.5 / 30.4 | 40.9 / 46.8 | 1.12 | 0.70 | 15,122,235 | 142 | 49 | 65 | 245 |
| anchor-door@1600-low-sun/-beams | 23.3 / 25.6 | 19.7 / 24.9 | 34.4 / 40.2 | 1.02 | 0.65 | 11,156,053 | 117 | 45 | 50 | 245 |
