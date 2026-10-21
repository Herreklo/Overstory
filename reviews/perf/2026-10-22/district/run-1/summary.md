# Frame time: the corner, run 1

2026-10-22 00:44:49, Apple M4 (Metal), 2560x1440 FullScreenWindow, MSAA 4x, render scale 1, quality PC, vsync 0; 2 rounds of 40 frames a segment, each after 15 warm-up, after 600 frames to settle; 616 s measuring.

Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.

The district: 2048 m square, 8,960 plots in 1024 chunks of 64 m (2112 meshes), 708 MB on disk, loaded in 0.7 s (964 MB/s); a chunk 0.31 ms (95th 3.98, worst 9.87), a core chunk 5.64 ms (95th 9.12); triangles: L0 9,193,684, shells 119,266, ground 2,097,152; resident memory 382 MB before, 662 MB after.

Rebuilding c_18_14.bin (264,820 triangles, 553,476 vertices, 1384 parts): placed in C# 24.20 ms, as a Burst job 1.80 ms (Burst on), uploaded 1.56 ms. A 1024 by 512 history page: drawn 0.71 ms, read back 0.68 ms, compressed to DXT5 8.7 ms (fast 5.3 ms).

| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| district-near-street@1300-drizzle | 27.1 / 27.6 | 23.6 / 26.6 | 41.2 / 45.8 | 0.59 | 0.58 | 7,165,955 | 1017 | 46 | 33 | 258 |
| district-near-into12@1300-drizzle | 29.8 / 30.3 | 26.0 / 29.5 | 45.0 / 50.5 | 0.68 | 0.63 | 7,585,987 | 1011 | 46 | 37 | 259 |
| district-near-high@1300-drizzle | 18.7 / 19.2 | 16.9 / 17.6 | 31.8 / 33.4 | 0.45 | 0.38 | 2,048,457 | 62 | 42 | 10 | 259 |
| district-near-city@1300-drizzle | 30.9 / 31.7 | 26.4 / 29.8 | 48.1 / 52.9 | 0.63 | 0.59 | 4,166,477 | 958 | 43 | 2 | 258 |
| district-near-over@1300-drizzle | 29.7 / 30.4 | 23.5 / 29.4 | 43.4 / 50.1 | 1.08 | 1.16 | 3,158,897 | 2926 | 50 | 0 | 260 |
| district-near-street@1300-drizzle/-beams | 26.5 / 27.4 | 23.0 / 26.1 | 40.5 / 44.3 | 0.57 | 0.55 | 7,165,953 | 1015 | 44 | 33 | 259 |
| district-near-into12@1300-drizzle/-beams | 28.8 / 29.6 | 25.1 / 28.2 | 43.5 / 48.5 | 0.55 | 0.56 | 7,585,985 | 1009 | 44 | 37 | 260 |
| district-near-high@1300-drizzle/-beams | 18.1 / 18.8 | 16.2 / 16.9 | 30.4 / 32.1 | 0.41 | 0.36 | 2,048,455 | 60 | 40 | 10 | 259 |
| district-near-city@1300-drizzle/-beams | 30.5 / 31.2 | 25.7 / 29.6 | 47.2 / 51.7 | 0.65 | 0.59 | 4,166,475 | 956 | 41 | 2 | 260 |
| district-near-over@1300-drizzle/-beams | 29.7 / 30.2 | 23.3 / 28.5 | 41.9 / 48.7 | 1.13 | 1.23 | 3,158,895 | 2924 | 48 | 0 | 259 |
| district-l0-street@1300-drizzle | 34.6 / 35.1 | 28.7 / 35.5 | 48.1 / 54.8 | 0.59 | 0.59 | 12,858,397 | 1017 | 46 | 33 | 260 |
| district-l0-into12@1300-drizzle | 37.4 / 38.2 | 31.1 / 38.2 | 52.4 / 59.9 | 0.59 | 0.59 | 13,042,319 | 1011 | 46 | 37 | 260 |
| district-l0-high@1300-drizzle | 18.7 / 19.4 | 16.9 / 17.6 | 31.6 / 33.5 | 0.41 | 0.37 | 2,166,765 | 62 | 42 | 10 | 261 |
| district-l0-city@1300-drizzle | 54.7 / 56.1 | 43.4 / 55.3 | 78.2 / 88.1 | 0.63 | 0.61 | 15,508,813 | 958 | 43 | 2 | 245 |
| district-l0-over@1300-drizzle | 48.8 / 51.0 | 36.2 / 50.7 | 60.4 / 67.9 | 1.30 | 1.52 | 21,524,173 | 2926 | 50 | 0 | 244 |
| district-l0-street@1300-drizzle/-beams | 33.6 / 34.5 | 28.2 / 34.6 | 46.7 / 53.9 | 0.61 | 0.58 | 12,858,395 | 1015 | 44 | 33 | 245 |
| district-l0-into12@1300-drizzle/-beams | 36.5 / 38.0 | 30.4 / 37.5 | 51.4 / 58.6 | 0.59 | 0.57 | 13,042,317 | 1009 | 44 | 37 | 244 |
| district-l0-high@1300-drizzle/-beams | 18.2 / 19.0 | 16.3 / 16.8 | 30.4 / 32.1 | 0.38 | 0.35 | 2,166,763 | 60 | 40 | 10 | 245 |
| district-l0-city@1300-drizzle/-beams | 53.9 / 56.0 | 43.5 / 54.0 | 76.6 / 84.6 | 0.63 | 0.59 | 15,508,811 | 956 | 41 | 2 | 244 |
| district-l0-over@1300-drizzle/-beams | 46.1 / 49.1 | 31.5 / 51.1 | 55.1 / 67.6 | 1.33 | 1.50 | 21,524,171 | 2924 | 48 | 0 | 245 |
| district-shells-street@1300-drizzle | 17.5 / 18.1 | 15.6 / 16.4 | 29.3 / 31.2 | 0.61 | 0.61 | 1,059,673 | 1013 | 46 | 31 | 244 |
| district-shells-into12@1300-drizzle | 19.1 / 19.8 | 17.0 / 17.9 | 31.9 / 34.4 | 0.56 | 0.56 | 1,039,823 | 1011 | 46 | 37 | 245 |
| district-shells-high@1300-drizzle | 15.7 / 16.4 | 14.5 / 15.1 | 27.7 / 29.2 | 0.39 | 0.36 | 20,495 | 62 | 42 | 10 | 244 |
| district-shells-city@1300-drizzle | 24.1 / 24.9 | 21.0 / 22.2 | 38.7 / 41.9 | 0.63 | 0.59 | 1,028,971 | 958 | 43 | 2 | 244 |
| district-shells-over@1300-drizzle | 29.8 / 30.9 | 23.7 / 29.8 | 43.4 / 50.1 | 1.08 | 1.21 | 3,158,897 | 2926 | 50 | 0 | 245 |
| district-shells-street@1300-drizzle/-beams | 17.1 / 17.5 | 15.1 / 15.8 | 28.4 / 30.1 | 0.57 | 0.55 | 1,059,671 | 1011 | 44 | 31 | 245 |
| district-shells-into12@1300-drizzle/-beams | 18.4 / 19.2 | 16.4 / 17.3 | 30.6 / 33.1 | 0.61 | 0.56 | 1,039,821 | 1009 | 44 | 37 | 244 |
| district-shells-high@1300-drizzle/-beams | 15.3 / 15.9 | 13.9 / 14.5 | 26.6 / 28.0 | 0.37 | 0.34 | 20,493 | 60 | 40 | 10 | 245 |
| district-shells-city@1300-drizzle/-beams | 23.2 / 24.2 | 20.4 / 21.6 | 37.3 / 41.1 | 0.57 | 0.54 | 1,028,969 | 956 | 41 | 2 | 244 |
| district-shells-over@1300-drizzle/-beams | 29.3 / 30.0 | 23.3 / 28.5 | 42.0 / 48.3 | 1.19 | 1.28 | 3,158,895 | 2924 | 48 | 0 | 246 |
| district-near-street@1600-low-sun | 87.7 / 93.7 | 78.2 / 83.8 | 144.6 / 157.1 | 0.63 | 0.61 | 8,983,865 | 1046 | 47 | 61 | 244 |
| district-near-into12@1600-low-sun | 90.7 / 95.5 | 79.9 / 85.2 | 147.0 / 161.0 | 0.61 | 0.61 | 9,121,861 | 1045 | 47 | 70 | 244 |
| district-near-high@1600-low-sun | 82.2 / 82.4 | 70.4 / 72.0 | 136.1 / 141.0 | 0.89 | 0.56 | 3,107,707 | 72 | 43 | 19 | 244 |
| district-near-city@1600-low-sun | 93.9 / 95.2 | 80.8 / 84.4 | 156.9 / 161.8 | 0.91 | 0.77 | 3,994,097 | 958 | 44 | 1 | 246 |
| district-near-over@1600-low-sun | 70.2 / 71.7 | 59.7 / 66.6 | 113.4 / 122.6 | 1.11 | 1.17 | 3,182,897 | 2927 | 51 | 0 | 245 |
| district-near-street@1600-low-sun/-beams | 28.8 / 29.6 | 24.7 / 28.9 | 42.7 / 46.9 | 0.60 | 0.57 | 8,983,863 | 1044 | 45 | 61 | 246 |
| district-near-into12@1600-low-sun/-beams | 30.4 / 32.0 | 26.5 / 30.3 | 44.8 / 50.7 | 0.71 | 0.64 | 9,121,859 | 1043 | 45 | 70 | 245 |
| district-near-high@1600-low-sun/-beams | 18.0 / 18.7 | 16.0 / 17.1 | 29.3 / 31.1 | 0.39 | 0.35 | 3,107,705 | 70 | 41 | 19 | 246 |
| district-near-city@1600-low-sun/-beams | 29.9 / 30.9 | 25.4 / 29.1 | 46.5 / 51.3 | 0.60 | 0.57 | 3,994,095 | 956 | 42 | 1 | 245 |
| district-near-over@1600-low-sun/-beams | 29.5 / 30.3 | 23.4 / 28.7 | 42.3 / 48.7 | 1.23 | 1.37 | 3,182,895 | 2925 | 49 | 0 | 245 |
| district-l0-street@1600-low-sun | 100.2 / 101.8 | 84.0 / 92.4 | 157.5 / 166.8 | 0.70 | 0.63 | 15,353,621 | 1046 | 47 | 61 | 245 |
| district-l0-into12@1600-low-sun | 103.3 / 103.9 | 87.7 / 95.7 | 164.1 / 172.1 | 0.66 | 0.63 | 15,522,235 | 1046 | 47 | 71 | 246 |
| district-l0-high@1600-low-sun | 82.8 / 83.1 | 71.5 / 72.5 | 140.5 / 141.5 | 0.45 | 0.39 | 3,470,465 | 72 | 43 | 19 | 245 |
| district-l0-city@1600-low-sun | 118.7 / 120.8 | 98.7 / 111.4 | 187.9 / 199.2 | 0.69 | 0.63 | 15,336,433 | 958 | 44 | 1 | 245 |
| district-l0-over@1600-low-sun | 87.6 / 89.9 | 68.9 / 86.9 | 127.1 / 136.9 | 1.46 | 1.75 | 21,548,173 | 2927 | 51 | 0 | 245 |
| district-l0-street@1600-low-sun/-beams | 36.0 / 37.2 | 30.5 / 37.5 | 49.6 / 56.2 | 1.07 | 0.88 | 15,353,619 | 1044 | 45 | 61 | 246 |
| district-l0-into12@1600-low-sun/-beams | 39.2 / 40.9 | 32.5 / 40.8 | 53.3 / 60.9 | 0.90 | 0.73 | 15,522,233 | 1044 | 45 | 71 | 245 |
| district-l0-high@1600-low-sun/-beams | 18.7 / 19.3 | 16.4 / 17.5 | 30.0 / 31.7 | 0.42 | 0.37 | 3,470,463 | 70 | 41 | 19 | 246 |
| district-l0-city@1600-low-sun/-beams | 53.9 / 55.6 | 43.4 / 55.3 | 77.4 / 85.0 | 1.13 | 0.88 | 15,336,431 | 956 | 42 | 1 | 245 |
| district-l0-over@1600-low-sun/-beams | 46.7 / 49.5 | 32.8 / 52.2 | 56.4 / 68.7 | 1.37 | 1.53 | 21,548,171 | 2925 | 49 | 0 | 247 |
| district-shells-street@1600-low-sun | 81.5 / 81.8 | 70.3 / 71.0 | 138.1 / 140.7 | 0.64 | 0.60 | 1,089,469 | 1043 | 47 | 60 | 245 |
| district-shells-into12@1600-low-sun | 83.0 / 83.5 | 71.8 / 72.4 | 141.4 / 143.2 | 0.73 | 0.63 | 1,070,165 | 1044 | 47 | 69 | 246 |
| district-shells-high@1600-low-sun | 78.3 / 78.5 | 67.9 / 68.4 | 134.9 / 135.8 | 0.42 | 0.38 | 46,273 | 71 | 43 | 18 | 245 |
| district-shells-city@1600-low-sun | 87.2 / 87.7 | 75.2 / 76.3 | 147.3 / 150.5 | 0.63 | 0.60 | 1,052,705 | 958 | 44 | 1 | 246 |
| district-shells-over@1600-low-sun | 69.8 / 71.2 | 58.6 / 64.7 | 113.1 / 119.9 | 1.16 | 1.26 | 3,182,897 | 2927 | 51 | 0 | 246 |
| district-shells-street@1600-low-sun/-beams | 17.1 / 17.3 | 15.1 / 15.8 | 28.8 / 30.0 | 0.59 | 0.56 | 1,089,467 | 1041 | 45 | 60 | 246 |
| district-shells-into12@1600-low-sun/-beams | 18.4 / 18.7 | 16.4 / 17.1 | 30.8 / 32.6 | 0.62 | 0.57 | 1,070,163 | 1042 | 45 | 69 | 245 |
| district-shells-high@1600-low-sun/-beams | 14.2 / 14.5 | 12.7 / 13.4 | 24.7 / 25.4 | 0.43 | 0.37 | 46,271 | 69 | 41 | 18 | 246 |
| district-shells-city@1600-low-sun/-beams | 22.5 / 22.9 | 19.6 / 20.7 | 36.4 / 39.0 | 0.58 | 0.55 | 1,052,703 | 956 | 42 | 1 | 246 |
| district-shells-over@1600-low-sun/-beams | 30.0 / 30.3 | 23.4 / 28.8 | 42.2 / 48.8 | 1.16 | 1.23 | 3,182,895 | 2925 | 49 | 0 | 247 |
| district-near-street@1750-blue-hour | 21.7 / 22.0 | 19.3 / 21.0 | 34.7 / 38.7 | 0.51 | 0.56 | 3,890,145 | 984 | 42 | 0 | 246 |
| district-near-into12@1750-blue-hour | 23.7 / 23.9 | 21.1 / 22.7 | 37.5 / 42.1 | 0.49 | 0.55 | 4,089,193 | 974 | 42 | 0 | 246 |
| district-near-high@1750-blue-hour | 15.0 / 15.2 | 13.6 / 14.5 | 26.5 / 27.6 | 0.37 | 0.35 | 910,933 | 52 | 40 | 0 | 245 |
| district-near-city@1750-blue-hour | 25.9 / 26.3 | 22.1 / 25.1 | 40.3 / 44.7 | 0.53 | 0.56 | 3,740,129 | 956 | 42 | 0 | 246 |
| district-near-over@1750-blue-hour | 29.3 / 30.2 | 23.4 / 29.3 | 42.9 / 49.0 | 1.08 | 1.18 | 3,158,897 | 2926 | 50 | 0 | 246 |
| district-near-street@1750-blue-hour/-beams | 20.8 / 21.2 | 18.4 / 19.7 | 32.8 / 37.0 | 0.52 | 0.55 | 3,890,143 | 982 | 40 | 0 | 246 |
| district-near-into12@1750-blue-hour/-beams | 23.0 / 23.7 | 20.1 / 21.3 | 36.0 / 40.4 | 0.61 | 0.61 | 4,089,191 | 972 | 40 | 0 | 246 |
| district-near-high@1750-blue-hour/-beams | 14.5 / 14.8 | 13.1 / 13.9 | 25.5 / 26.6 | 0.35 | 0.34 | 910,931 | 50 | 38 | 0 | 246 |
| district-near-city@1750-blue-hour/-beams | 25.0 / 25.5 | 21.2 / 23.6 | 38.4 / 42.7 | 0.55 | 0.55 | 3,740,127 | 954 | 40 | 0 | 246 |
| district-near-over@1750-blue-hour/-beams | 28.9 / 29.6 | 22.8 / 28.1 | 41.1 / 45.9 | 1.18 | 1.28 | 3,158,895 | 2924 | 48 | 0 | 246 |
| district-l0-street@1750-blue-hour | 27.1 / 27.7 | 23.4 / 28.1 | 40.4 / 46.4 | 0.51 | 0.55 | 8,126,001 | 984 | 42 | 0 | 246 |
| district-l0-into12@1750-blue-hour | 29.5 / 30.1 | 25.2 / 29.8 | 43.9 / 50.3 | 0.55 | 0.57 | 8,200,961 | 974 | 42 | 0 | 247 |
| district-l0-high@1750-blue-hour | 15.0 / 15.2 | 13.6 / 14.5 | 26.4 / 27.6 | 0.36 | 0.35 | 910,933 | 52 | 40 | 0 | 246 |
| district-l0-city@1750-blue-hour | 46.8 / 48.1 | 37.8 / 49.2 | 66.5 / 74.2 | 0.60 | 0.59 | 15,082,465 | 956 | 42 | 0 | 246 |
| district-l0-over@1750-blue-hour | 48.6 / 51.1 | 35.8 / 50.8 | 60.1 / 65.4 | 1.36 | 1.57 | 21,524,173 | 2926 | 50 | 0 | 246 |
| district-l0-street@1750-blue-hour/-beams | 26.1 / 26.8 | 21.8 / 25.7 | 37.6 / 44.2 | 0.54 | 0.55 | 8,125,999 | 982 | 40 | 0 | 247 |
| district-l0-into12@1750-blue-hour/-beams | 28.6 / 28.9 | 23.9 / 27.7 | 41.0 / 47.5 | 0.57 | 0.57 | 8,200,959 | 972 | 40 | 0 | 246 |
| district-l0-high@1750-blue-hour/-beams | 14.4 / 14.6 | 12.9 / 13.7 | 25.3 / 26.3 | 0.36 | 0.33 | 910,931 | 50 | 38 | 0 | 247 |
| district-l0-city@1750-blue-hour/-beams | 45.5 / 46.6 | 35.7 / 45.6 | 61.8 / 73.5 | 0.64 | 0.61 | 15,082,463 | 954 | 40 | 0 | 246 |
| district-l0-over@1750-blue-hour/-beams | 46.0 / 48.8 | 31.8 / 51.4 | 55.1 / 67.8 | 1.38 | 1.53 | 21,524,171 | 2924 | 48 | 0 | 248 |
| district-shells-street@1750-blue-hour | 15.8 / 16.1 | 14.1 / 14.7 | 26.4 / 28.6 | 0.53 | 0.57 | 1,054,213 | 982 | 42 | 0 | 246 |
| district-shells-into12@1750-blue-hour | 16.8 / 17.4 | 15.2 / 15.9 | 28.0 / 30.7 | 0.51 | 0.55 | 1,033,341 | 974 | 42 | 0 | 247 |
| district-shells-high@1750-blue-hour | 13.2 / 13.7 | 12.0 / 12.7 | 23.3 / 24.7 | 0.37 | 0.34 | 19,053 | 52 | 40 | 0 | 246 |
| district-shells-city@1750-blue-hour | 19.9 / 20.1 | 17.5 / 18.7 | 32.4 / 35.2 | 0.53 | 0.56 | 1,028,425 | 956 | 42 | 0 | 247 |
| district-shells-over@1750-blue-hour | 29.2 / 30.5 | 23.3 / 29.3 | 43.0 / 49.0 | 1.09 | 1.20 | 3,158,897 | 2926 | 50 | 0 | 247 |
| district-shells-street@1750-blue-hour/-beams | 15.0 / 15.4 | 13.3 / 13.8 | 25.0 / 26.9 | 0.53 | 0.55 | 1,054,211 | 980 | 40 | 0 | 247 |
| district-shells-into12@1750-blue-hour/-beams | 16.2 / 16.6 | 14.3 / 15.0 | 26.8 / 29.2 | 0.53 | 0.55 | 1,033,339 | 972 | 40 | 0 | 246 |
| district-shells-high@1750-blue-hour/-beams | 12.6 / 12.9 | 11.4 / 12.0 | 22.4 / 23.4 | 0.34 | 0.33 | 19,051 | 50 | 38 | 0 | 247 |
| district-shells-city@1750-blue-hour/-beams | 19.3 / 19.6 | 16.8 / 17.7 | 30.8 / 33.6 | 0.55 | 0.56 | 1,028,423 | 954 | 40 | 0 | 246 |
| district-shells-over@1750-blue-hour/-beams | 29.3 / 29.7 | 22.9 / 28.0 | 41.2 / 48.0 | 1.12 | 1.23 | 3,158,895 | 2924 | 48 | 0 | 248 |
