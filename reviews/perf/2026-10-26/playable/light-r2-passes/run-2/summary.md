# Frame time: the walk's corner in the town, run 2

2026-10-26 23:16:29, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 60 frames a segment, each after 20 warm-up, after 600 frames to settle; 237 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eye-foot@1300-drizzle | 28.3 / 28.5 | 22.0 / 28.7 | 30.8 / 40.9 | 0.40 | 0.42 | 15,938,971 | 140 | 54 | 64 | 233 |
| street@1300-drizzle | 23.2 / 23.6 | 19.4 / 24.5 | 30.1 / 35.8 | 0.40 | 0.42 | 15,246,165 | 138 | 53 | 62 | 233 |
| eye-foot@1300-drizzle/haze-off | 27.1 / 29.1 | 23.2 / 24.4 | 41.5 / 42.7 | 0.43 | 0.43 | 15,938,971 | 140 | 54 | 64 | 233 |
| street@1300-drizzle/haze-off | 23.9 / 24.5 | 18.8 / 25.5 | 34.0 / 35.7 | 0.40 | 0.42 | 15,246,165 | 138 | 53 | 62 | 233 |
| eye-foot@1300-drizzle/-foglights | 27.9 / 28.8 | 22.8 / 28.5 | 39.0 / 41.7 | 0.41 | 0.41 | 15,938,969 | 138 | 52 | 64 | 233 |
| street@1300-drizzle/-foglights | 23.6 / 24.2 | 19.0 / 24.7 | 32.6 / 34.9 | 0.40 | 0.41 | 15,246,163 | 136 | 51 | 62 | 233 |
| eye-foot@1300-drizzle/-sky | 28.5 / 29.0 | 21.9 / 29.5 | 40.5 / 41.5 | 0.41 | 0.42 | 15,937,291 | 139 | 53 | 64 | 233 |
| street@1300-drizzle/-sky | 24.0 / 24.3 | 17.6 / 25.3 | 27.5 / 33.5 | 0.39 | 0.41 | 15,244,485 | 137 | 52 | 62 | 233 |
| eye-foot@1300-drizzle/-fullscreen | 24.0 / 24.9 | 19.1 / 25.6 | 34.6 / 39.0 | 0.37 | 0.35 | 15,938,960 | 129 | 43 | 64 | 233 |
| street@1300-drizzle/-fullscreen | 19.7 / 20.3 | 16.1 / 21.9 | 27.7 / 29.9 | 0.37 | 0.35 | 15,246,154 | 127 | 42 | 62 | 233 |
| eye-foot@1300-drizzle/bare | 8.9 / 9.1 | 7.7 / 8.1 | 22.7 / 23.5 | 0.21 | 0.08 | 2,821,540 | 19 | 4 | 0 | 233 |
| street@1300-drizzle/bare | 5.1 / 5.3 | 4.3 / 4.6 | 12.4 / 13.0 | 0.23 | 0.08 | 2,821,540 | 19 | 4 | 0 | 233 |
| eye-foot@1600-low-sun | 28.0 / 30.0 | 23.8 / 25.0 | 42.7 / 43.7 | 0.42 | 0.43 | 16,259,381 | 147 | 54 | 71 | 233 |
| street@1600-low-sun | 24.7 / 25.1 | 19.6 / 26.1 | 35.1 / 36.9 | 0.42 | 0.43 | 15,288,477 | 142 | 53 | 66 | 234 |
| eye-foot@1600-low-sun/haze-off | 29.0 / 29.5 | 22.1 / 29.6 | 31.2 / 41.2 | 0.41 | 0.42 | 16,259,381 | 147 | 54 | 71 | 235 |
| street@1600-low-sun/haze-off | 24.3 / 24.7 | 18.1 / 25.7 | 27.2 / 34.2 | 0.41 | 0.41 | 15,288,477 | 142 | 53 | 66 | 233 |
| eye-foot@1600-low-sun/-foglights | 28.5 / 29.5 | 23.3 / 29.2 | 40.0 / 42.1 | 0.40 | 0.41 | 16,259,379 | 145 | 52 | 71 | 234 |
| street@1600-low-sun/-foglights | 23.8 / 24.5 | 19.3 / 25.1 | 33.5 / 35.8 | 0.40 | 0.41 | 15,288,475 | 140 | 51 | 66 | 234 |
| eye-foot@1600-low-sun/-sky | 28.9 / 29.1 | 22.3 / 29.4 | 31.4 / 41.5 | 0.40 | 0.42 | 16,257,701 | 146 | 53 | 71 | 235 |
| street@1600-low-sun/-sky | 23.2 / 23.6 | 19.2 / 24.5 | 29.3 / 35.3 | 0.40 | 0.42 | 15,286,797 | 141 | 52 | 66 | 234 |
| eye-foot@1600-low-sun/-fullscreen | 24.7 / 25.7 | 19.8 / 26.3 | 35.8 / 40.5 | 0.38 | 0.35 | 16,259,370 | 136 | 43 | 71 | 234 |
| street@1600-low-sun/-fullscreen | 20.1 / 20.7 | 16.5 / 22.2 | 28.7 / 30.8 | 0.37 | 0.34 | 15,288,466 | 131 | 42 | 66 | 234 |
| eye-foot@1600-low-sun/bare | 9.1 / 9.2 | 7.8 / 8.1 | 23.0 / 23.5 | 0.23 | 0.08 | 2,821,540 | 19 | 4 | 0 | 235 |
| street@1600-low-sun/bare | 5.2 / 5.2 | 4.4 / 4.7 | 12.7 / 13.1 | 0.23 | 0.08 | 2,821,540 | 19 | 4 | 0 | 234 |
| eye-foot@1750-blue-hour | 55.5 / 55.9 | 48.3 / 49.8 | 93.3 / 97.4 | 0.39 | 0.38 | 5,668,793 | 73 | 43 | 0 | 235 |
| street@1750-blue-hour | 50.2 / 50.5 | 43.7 / 45.0 | 84.1 / 87.7 | 0.38 | 0.38 | 5,668,793 | 73 | 43 | 0 | 234 |
| eye-foot@1750-blue-hour/haze-off | 44.5 / 45.8 | 39.4 / 40.8 | 74.2 / 79.7 | 0.38 | 0.38 | 5,668,793 | 73 | 43 | 0 | 235 |
| street@1750-blue-hour/haze-off | 41.3 / 42.0 | 36.1 / 37.6 | 69.2 / 72.5 | 0.37 | 0.38 | 5,668,793 | 73 | 43 | 0 | 234 |
| eye-foot@1750-blue-hour/-foglights | 34.0 / 34.4 | 29.6 / 30.7 | 55.7 / 59.6 | 0.35 | 0.37 | 5,668,791 | 71 | 41 | 0 | 234 |
| street@1750-blue-hour/-foglights | 28.3 / 28.6 | 24.6 / 25.8 | 46.3 / 49.9 | 0.36 | 0.36 | 5,668,791 | 71 | 41 | 0 | 234 |
| eye-foot@1750-blue-hour/-sky | 54.8 / 55.2 | 47.7 / 49.1 | 92.0 / 95.9 | 0.38 | 0.38 | 5,667,113 | 72 | 42 | 0 | 235 |
| street@1750-blue-hour/-sky | 48.5 / 48.9 | 42.3 / 43.7 | 81.8 / 85.3 | 0.37 | 0.38 | 5,667,113 | 72 | 42 | 0 | 234 |
| eye-foot@1750-blue-hour/-fullscreen | 33.0 / 33.4 | 28.5 / 30.3 | 54.1 / 57.9 | 0.34 | 0.34 | 5,668,786 | 66 | 36 | 0 | 234 |
| street@1750-blue-hour/-fullscreen | 27.3 / 27.6 | 23.6 / 25.4 | 44.8 / 48.3 | 0.35 | 0.34 | 5,668,786 | 66 | 36 | 0 | 234 |
| eye-foot@1750-blue-hour/bare | 19.8 / 20.0 | 16.9 / 17.3 | 50.4 / 51.1 | 0.24 | 0.08 | 2,821,540 | 19 | 4 | 0 | 235 |
| street@1750-blue-hour/bare | 14.1 / 14.4 | 12.1 / 12.2 | 35.8 / 36.1 | 0.23 | 0.08 | 2,821,540 | 19 | 4 | 0 | 234 |
