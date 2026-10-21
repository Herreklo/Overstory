# The scale test: the district's numbers

From `blender/cache/scale-district`: 2048 m square (4.19 km²), 8,960 plots in 1024 chunks of 64 m; 8,519 houses built, 441 plots empty in 1989; the core 512 m square (0.26 km²) at full detail (789 houses), every house as a shell. About 34 streets across it and cross streets every 160 m: 94 km of street, so 90 houses a kilometre (both sides).

## A house

Triangles a house at full detail (test quality): median 10,800, 95th percentile 21,436, worst 32,044; surface 1563 m² a house. The core holds 9,193,684 triangles at L0, 35.1 million a km² and 561 in a 4 m chunk on average.

## Generation (Blender's Python, one process)

| Stage | Seconds (all processes) | Milliseconds a house |
| --- | --- | --- |
| resolve | 2 | 0.2 |
| build | 807 | 94.8 |
| bake (789 houses baked) | 732 | 928.4 |
| extract | 42 | 4.9 |
| shell | 19 | 2.3 |
| ground (a chunk) | 1 | 1.0 a chunk |
| write (a chunk) | 2 | 2.2 a chunk |
| **all** | 1611 | 189.1 |

A core chunk (64 m, built, baked, at L0 and as shells) took 12.3 s (95th 20.1 s); one outside it (shells only, but every house still built) 0.7 s.
The whole district took 222 s of wall time in 8 processes: 38.3 houses a second, 67.9 km² an hour.

## The cache

| What | Total (MB) | Per km² of its area (MB) | Per km of street (MB) |
| --- | --- | --- | --- |
| L0 meshes (core only) | 546 | 2082 | 93 |
| shells (every house) | 7 | 1.6 | 0.07 |
| ground (2 m grid) | 156 | 37.2 | 1.66 |
| records (the diaries, JSON) | 2.6 | 0.61 | 0.027 |
| **chunk files** | 708 | | |

L0 mesh is 2,309 times its records' bytes: 708 KB a house against 315 bytes of diary.

Maps the core's surface would carry (four base pages at a byte a texel, BC7, mips a third more; packing waste 15 %):

| Texel | Per house (MB) | Per km² of town like the core (MB) | Per km of street (MB) |
| --- | --- | --- | --- |
| 2 cm | 22.9 | 68,813 | 3,064 |
| 4 cm | 5.7 | 17,203 | 766 |
| 8 cm | 1.4 | 4,301 | 191 |

## Loading and building a chunk on the M4

The player loaded 1024 chunk files (708 MB) in 0.7 s, 964 MB/s on the main thread: a chunk 0.31 ms (95th 3.98, worst 9.9), a core chunk 5.6 ms (95th 9.1); reading the file 0.27 ms of it. Resident memory 383 MB before, 663 MB after (708 MB of vertices and indices).
A chunk's load time fits 0.28 ms + 0.63 ms a MB.

Rebuilding c_18_14.bin (264,820 triangles in 1384 parts): placing its parts took 24.2 ms in plain C# and 1.80 ms as a Burst job (9.1 and 0.68 ms a 100,000 triangles), uploading it 1.6 ms. A 1024 by 512 history page: drawn and waited for 0.71 ms, read back 0.68 ms, compressed on the CPU to DXT5 9 ms (5 ms fast).

## What the camera's movement asks for

Units a second coming into each level's reach (in 3D, from the eye), moving steadily across the grid; and the units within reach at once, which a jump (a map click, a cut) asks for in one go. Building blocks' reaches: L0 and L1 to 20 m, L2 to 80 m, L3 to 200 m, the streaming radius 300 m, L4 to 1.5 km.

| Unit | Reach | walk | run | drive (50 km/h) | city camera pan, 150 m up | At once |
| --- | --- | --- | --- | --- | --- | --- |
| L0 and L1, 4 m chunks | 20 m | 4.3 | 11.6 | 39.9 | 0.0 | 88 |
| L2, 32 m cells | 80 m | 0.2 | 0.7 | 2.7 | 0.0 | 32 |
| L3 shells, 32 m cells | 200 m | 0.6 | 1.8 | 6.0 | 90.1 | 148 |
| streaming, 64 m chunks | 300 m | 0.2 | 0.7 | 2.3 | 44.5 | 88 |
| L4 blocks, 128 m | 1500 m | 0.0 | 0.8 | 2.6 | 58.0 | 484 |

Main-thread time a second those rates cost, if each unit loads from the cache at the measured rate (0.28 ms + 0.63 ms a MB), its bytes from the core's density (34 KB a 4 m chunk at L0, 41 KB a 32 m cell of shells and ground):

| Unit | walk | run | drive (50 km/h) | city camera pan, 150 m up |
| --- | --- | --- | --- | --- |
| L0 and L1, 4 m chunks (0.30 ms each) | 1.3 | 3.5 | 12.0 | 0.0 |
| L2, 32 m cells (0.31 ms each) | 0.1 | 0.2 | 0.8 | 0.0 |
| L3 shells, 32 m cells (0.31 ms each) | 0.2 | 0.5 | 1.8 | 27.5 |
| streaming, 64 m chunks (0.38 ms each) | 0.1 | 0.3 | 0.9 | 16.9 |
| L4 blocks, 128 m (0.68 ms each) | 0.0 | 0.5 | 1.8 | 39.5 |

At 60 fps a frame has 1.5 ms for streaming (building blocks), 90 ms a second.
