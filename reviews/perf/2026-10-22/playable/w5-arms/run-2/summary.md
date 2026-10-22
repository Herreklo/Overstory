# Frame time: the walk's corner in the town, run 2

2026-10-22 20:29:54, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 3 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 338 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eye-foot@1600-low-sun | 39.9 / 40.9 | 32.4 / 42.2 | 46.3 / 59.2 | 1.32 | 0.78 | 16,283,381 | 148 | 55 | 71 | 241 |
| street@1600-low-sun | 32.9 / 34.2 | 29.4 / 36.2 | 42.4 / 50.6 | 1.32 | 0.77 | 15,312,477 | 143 | 54 | 66 | 242 |
| high@1600-low-sun | 31.3 / 46.9 | 27.6 / 33.2 | 43.5 / 51.9 | 1.31 | 0.75 | 13,999,779 | 127 | 52 | 52 | 241 |
| steps@1600-low-sun | 33.7 / 45.6 | 29.3 / 32.3 | 51.7 / 56.4 | 1.28 | 0.77 | 15,255,125 | 127 | 55 | 58 | 242 |
| eye-foot@1600-low-sun/beams-copy | 37.9 / 40.8 | 31.6 / 41.3 | 52.8 / 60.7 | 1.29 | 0.79 | 16,283,382 | 149 | 56 | 71 | 241 |
| street@1600-low-sun/beams-copy | 32.8 / 34.7 | 26.8 / 35.6 | 44.5 / 51.2 | 1.26 | 0.76 | 15,312,478 | 144 | 55 | 66 | 242 |
| high@1600-low-sun/beams-copy | 32.1 / 34.4 | 26.8 / 33.9 | 44.9 / 50.6 | 1.27 | 0.75 | 13,999,780 | 128 | 53 | 52 | 241 |
| steps@1600-low-sun/beams-copy | 35.0 / 36.6 | 28.9 / 38.2 | 47.8 / 54.8 | 1.28 | 0.75 | 15,255,126 | 128 | 56 | 58 | 243 |
| eye-foot@1600-low-sun/beams-nocomposite | 37.1 / 40.6 | 30.9 / 40.1 | 51.9 / 58.7 | 1.25 | 0.74 | 16,283,380 | 147 | 54 | 71 | 242 |
| street@1600-low-sun/beams-nocomposite | 32.0 / 33.1 | 26.1 / 34.6 | 44.6 / 50.3 | 1.26 | 0.73 | 15,312,476 | 142 | 53 | 66 | 243 |
| high@1600-low-sun/beams-nocomposite | 30.8 / 32.1 | 26.1 / 32.1 | 44.9 / 49.8 | 1.24 | 0.69 | 13,999,778 | 126 | 51 | 52 | 242 |
| steps@1600-low-sun/beams-nocomposite | 32.8 / 34.2 | 27.2 / 33.4 | 47.2 / 51.5 | 1.16 | 0.69 | 15,255,124 | 126 | 54 | 58 | 243 |
| eye-foot@1600-low-sun/-beams | 35.7 / 37.8 | 29.4 / 36.9 | 52.5 / 57.3 | 1.18 | 0.68 | 16,283,377 | 144 | 51 | 71 | 242 |
| street@1600-low-sun/-beams | 29.5 / 31.6 | 24.8 / 31.9 | 43.1 / 48.3 | 1.16 | 0.67 | 15,312,473 | 139 | 50 | 66 | 243 |
| high@1600-low-sun/-beams | 30.7 / 33.9 | 24.2 / 30.3 | 43.6 / 47.9 | 1.22 | 0.69 | 13,999,775 | 123 | 48 | 52 | 243 |
| steps@1600-low-sun/-beams | 33.3 / 35.3 | 27.3 / 35.8 | 48.0 / 53.9 | 1.29 | 0.76 | 15,255,121 | 123 | 51 | 58 | 243 |
