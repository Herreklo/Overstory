# Frame time: the walk's corner in the town, run 1

2026-10-22 20:24:06, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 3 rounds of 150 frames a segment, each after 30 warm-up, after 600 frames to settle; 310 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eye-foot@1600-low-sun | 34.4 / 35.9 | 28.8 / 35.8 | 51.2 / 53.2 | 0.71 | 0.52 | 16,283,381 | 148 | 55 | 71 | 240 |
| street@1600-low-sun | 29.4 / 31.6 | 24.6 / 31.0 | 42.7 / 45.0 | 0.96 | 0.61 | 15,312,477 | 143 | 54 | 66 | 242 |
| high@1600-low-sun | 28.9 / 31.6 | 27.3 / 29.0 | 32.2 / 44.6 | 0.43 | 0.43 | 13,999,779 | 127 | 52 | 52 | 241 |
| steps@1600-low-sun | 30.9 / 31.9 | 27.0 / 30.6 | 38.4 / 49.3 | 0.46 | 0.44 | 15,255,125 | 127 | 55 | 58 | 242 |
| eye-foot@1600-low-sun/beams-copy | 34.6 / 37.3 | 29.8 / 36.2 | 50.8 / 55.0 | 0.97 | 0.61 | 16,283,382 | 149 | 56 | 71 | 241 |
| street@1600-low-sun/beams-copy | 30.0 / 35.7 | 24.8 / 30.9 | 42.6 / 46.2 | 0.44 | 0.44 | 15,312,478 | 144 | 55 | 66 | 242 |
| high@1600-low-sun/beams-copy | 29.0 / 30.3 | 24.7 / 29.8 | 43.1 / 45.7 | 1.04 | 0.64 | 13,999,780 | 128 | 53 | 52 | 241 |
| steps@1600-low-sun/beams-copy | 31.3 / 32.6 | 26.5 / 33.0 | 45.5 / 50.0 | 0.47 | 0.46 | 15,255,126 | 128 | 56 | 58 | 242 |
| eye-foot@1600-low-sun/beams-nocomposite | 34.6 / 35.5 | 28.4 / 35.1 | 49.5 / 53.2 | 0.53 | 0.47 | 16,283,380 | 147 | 54 | 71 | 241 |
| street@1600-low-sun/beams-nocomposite | 30.1 / 31.5 | 24.4 / 31.0 | 41.8 / 46.6 | 0.79 | 0.53 | 15,312,476 | 142 | 53 | 66 | 243 |
| high@1600-low-sun/beams-nocomposite | 29.5 / 32.3 | 24.0 / 29.6 | 41.8 / 46.1 | 0.90 | 0.57 | 13,999,778 | 126 | 51 | 52 | 242 |
| steps@1600-low-sun/beams-nocomposite | 31.2 / 32.7 | 25.9 / 32.4 | 44.3 / 49.1 | 1.00 | 0.61 | 15,255,124 | 126 | 54 | 58 | 243 |
| eye-foot@1600-low-sun/-beams | 33.3 / 34.4 | 27.5 / 33.9 | 49.1 / 53.8 | 0.44 | 0.42 | 16,283,377 | 144 | 51 | 71 | 242 |
| street@1600-low-sun/-beams | 27.8 / 29.5 | 23.0 / 29.0 | 40.5 / 45.2 | 0.45 | 0.42 | 15,312,473 | 139 | 50 | 66 | 242 |
| high@1600-low-sun/-beams | 27.4 / 28.5 | 22.5 / 27.6 | 40.3 / 44.4 | 0.42 | 0.40 | 13,999,775 | 123 | 48 | 52 | 242 |
| steps@1600-low-sun/-beams | 29.6 / 30.9 | 24.3 / 30.7 | 43.6 / 48.2 | 0.41 | 0.39 | 15,255,121 | 123 | 51 | 58 | 242 |
