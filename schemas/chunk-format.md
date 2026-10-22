# The chunk format

The binary files the player reads from the disk cache and the shipped heart. Reserved at step 1: no writer or reader exists yet. The first writer and one reader per language come at step 5, tested on one golden file (`fixtures/golden/chunk/`). `chunk.schema.json` is the same layout as JSON, for dumps and tests.

Everything is little-endian. Offsets count from the start of the file (the container) or of the unit's payload (a unit). Every table has a version word, so a reader refuses what it does not know.

## Files

A file is a container of units (decisions §15, S4). Opening a file costs about 0.28 ms on the main thread, so small units share one:

- **A block file**, `bk-<i>-<j>.osc`, holds a 128 m block's records, its things' shells (L3, per 32 m cell), its L4 mesh and its ground. City-wide, block files ship.
- **A near file**, `lc-<i>-<j>.osc`, holds a 64 m land chunk's near levels: L0 and L1 per 4 m chunk, L2 per 32 m cell, and the place and history pages per 16 m page group. Near files are built on demand and cached; only the heart's start date ships them.
- A cell's shell atlas is a pages unit, cached on disk with the near files and never shipped beyond the heart (`maps.json`, `shellBake`).

Unit names and indices are as `naming.md` gives them: `i = floor(x / size)` in the pack's world frame.

## The container

### Header, 64 bytes

| Offset | Type | Field |
| --- | --- | --- |
| 0 | 4 bytes | magic `OSC` and a zero byte |
| 4 | u16 | container version, 1 |
| 6 | u16 | schemaVersion of the contracts it was built under |
| 8 | u64 | rulesetVersion (the kind files and part versions) |
| 16 | u64 | worldSeed |
| 24 | u64 | bakeVersion (`OS_History`, the layer curves, the bakes, the shaders) |
| 32 | u8 | its unit: 4 land chunk, 5 block |
| 33 | 3 bytes | reserved, zero |
| 36 | i32 | unit index i |
| 40 | i32 | unit index j |
| 44 | u32 | index entries |
| 48 | u64 | index offset |
| 56 | u32 | flags, zero |
| 60 | u32 | CRC-32 of bytes 0 to 59 |

A container whose rulesetVersion or bakeVersion differs from the player's is stale as a whole; a unit is stale when its hash key differs from the hash chain's.

### Index, 48 bytes an entry

Sorted by unit kind, i, j, level, then content, so a reader finds a unit by binary search.

| Offset | Type | Field |
| --- | --- | --- |
| 0 | u8 | unit kind: 1 chunk (4 m), 2 page group (16 m), 3 cell (32 m), 4 land chunk (64 m), 5 block (128 m) |
| 1 | u8 | level 0 to 4; 255 when none (records, pages, ground) |
| 2 | u8 | content: 1 records, 2 mesh, 3 pages, 4 shell atlas, 5 ground, 6 collision proxy, 7 caster proxy |
| 3 | u8 | compression: 0 none, 1 deflate (zlib stream), 2 reserved |
| 4 | i32 | unit index i |
| 8 | i32 | unit index j |
| 12 | u32 | reserved, zero |
| 16 | u64 | hash key: the mesh hash per chunk and level for a mesh, the bake hash for pages and atlases, the record hash for records |
| 24 | u64 | offset of the payload |
| 32 | u64 | stored length |
| 40 | u64 | length once decompressed |

**Page compression.** Pages and atlases are stored already block-compressed for the GPU (BC7, BC5, BC4, BC3; `maps.json`), with container compression 0, so a read goes to the GPU without a CPU step. Meshes and records take deflate. The cold read (unknown 4 below) may change either per content without a new container version, since each entry names its own.

## A mesh unit

One per 4 m chunk at L0 and L1, per 32 m cell at L2 and L3, and per block at L4. Positions are Float32 relative to the unit's corner (decisions §6, Precision).

### Unit header, 32 bytes

| Offset | Type | Field |
| --- | --- | --- |
| 0 | 4 bytes | magic `OSU` and a zero byte |
| 4 | u16 | unit version, 1 |
| 6 | u16 | sections |
| 8 | u32 | things |
| 12 | u32 | pieces |
| 16 | u32 | vertices |
| 20 | u32 | indices |
| 24 | u8 | vertex layout: 0 the 44-byte vertex, 1 with uv5, 2 with uv6, 3 with both, 4 the 28-byte shell (`channels.json`) |
| 25 | u8 | index width: 2 or 4 bytes |
| 26 | 6 bytes | reserved, zero |

Then a section table, 12 bytes a section: u16 section id, u16 flags, u32 offset, u32 length. A reader skips a section id it does not know.

### Sections

| Id | Section | Entry |
| --- | --- | --- |
| 1 | string table | u32 count, then each a u16 length and UTF-8 bytes: record ids, fill ids, part paths, act kinds |
| 2 | thing table | 24 bytes: u32 record id (string), u16 atlas rectangle x, y, w, h in the shell atlas's texels (zero below L3), u32 facts-buffer index, u16 part-slot base, 6 bytes reserved |
| 3 | part table | 8 bytes: u32 part path (string), u32 part version |
| 4 | piece table | 32 bytes: u64 seed, u32 fill id (string), u16 thing, u16 part, four u16 resets (placed, disturbed, cleaned, reserved), u16 variation, u8 age brought (whole years), u8 inherited polish (/255), u8 material class, u8 flags (bit 0 walked, bit 1 lifted by hands, bit 2 reclaimed), 2 bytes reserved. UV3's piece index addresses it; its GPU entry is below |
| 5 | vertices | the layout named in the header |
| 6 | indices | u16 or u32 |
| 7 | draws | 12 bytes: u16 shader family index (into the string table), u16 material class, u32 first index, u32 index count |
| 8 | invalidation table | 24 bytes per act kind: u32 act kind (string), u32 flags (bit 0 the mesh dirty, bit 1 the collision proxy dirty, bit 2 the caster proxy dirty), u32 page list offset, u32 page count, u32 instance list offset, u32 instance count; then the lists as u32 page and instance indices |
| 9 | collision proxy | u32 vertices, u32 triangles, Float32x3 positions, u32 indices, u8 per triangle: 0 solid, 1 walkable |
| 10 | affordances | 20 bytes: u32 slot id (string), u8 kind (0 tread, 1 landing, 2 walking line, 3 handrail, 4 sit, 5 lean, 6 sill, 7 grip), u8 walkable, u16 reserved, u32 from year and month (year × 16 + month), u32 to (0 while it stands), u32 polyline offset in section 12 |
| 11 | motion | 12 bytes per moving element: u32 piece, u8 class (0 still, 1 hinged, 2 swinging, 3 flexible, 4 floating, 5 emitting), u8 deform (0 none, 1 card, 2 skinned), u16 reserved, u32 anchor offset in section 12 |
| 12 | geometry pool | Float32 triples for affordance polylines and motion anchors |
| 13 | breaklines | u32 count, then pairs of vertex indices: edges a level must keep |

The thing table's atlas rectangle is reserved now for the painted far town: each thing's place in its cell's shell atlas, so a thing's atlas is rebaked alone when the change query names it.

### The piece table's clocks

A piece's resets are its history's clocks (`layers.json`; decisions D5.1, D5.4). Each is a u16 of year × 16 + month, counted from the pack's first year (`pack.json`'s `firstYear`). Months run 1 to 12, and a date known only to the year takes month 1, so it decodes to the whole year as the date global does (January is the year itself); 0 is never a date and means none.

- **placed:** when the piece was laid. Polish and the hollow run from it.
- **disturbed:** when its bed was last relaid, or it was lifted. Lichen at the hands' reach runs from it where the piece is flagged lifted by hands, and moss at the bed reach from the later of it and bare.
- **cleaned:** when a works campaign last cleaned it. Lichen and moss never run from before it.
- **reserved:** zero until a kind needs a fifth clock.

Bare is not stored: it is placed less the age the piece brought (a reclaimed stone's years in the heap), in whole years. The inherited polish is the floor a reused stone's polish never falls under.

### The piece table on the GPU, 16 bytes

The draw needs where a piece's pages are and its clocks, not its ids. Each chunk's piece table goes to a global `StructuredBuffer` of 16-byte entries, read in the vertex stage by UV3's piece index and passed flat to the fragment (`Shaders/History.hlsl`):

| Offset | Type | Field |
| --- | --- | --- |
| 0 | u16 | its page group's first slice in the page arrays |
| 2 | u16 | variation |
| 4 | u16 | placed |
| 6 | u16 | disturbed |
| 8 | u16 | cleaned |
| 10 | u16 | reserved reset, zero |
| 12 | u8 | age brought, whole years |
| 13 | u8 | inherited polish (/255) |
| 14 | u16 | flags, as on disk (bit 0 walked, bit 1 lifted by hands, bit 2 reclaimed) |

The seed, ids, thing, part and material class stay on disk: the draw's material gives its class.

## A pages unit

One per 16 m page group (and one per 32 m cell for the shell atlas). Header 32 bytes: magic `OSP` and a zero byte, u16 version 1, u16 pages, u32 rectangles, u32 page width, u32 page height, 12 bytes reserved. Then per page 16 bytes: u32 map id (string), u8 GPU format (0 none, 1 BC7, 2 BC5, 3 BC4, 4 BC3, 5 R8G8), u8 mips, u16 reserved, u32 data offset, u32 data length. Then per rectangle 16 bytes: u32 chunk or thing index, u16 x, y, w, h, u16 texel in mm, u16 flags. Then the string table and the page data.

## Unknowns

1. **The GPU block encoder** (`maps.json`'s `gpu-encoder`). It fixes nothing here: pages are stored in their GPU format whichever encoder made them. Learned when it is timed, before any page bakes in the player (before step 5).
2. **The place bake's cost per house.** No field here. Learned in the spike before step 5.
3. **The shell atlas's bake cost per cell.** The input is decided (L2, `maps.json`'s `shellBake`); the cost is learned before step 5.
4. **The cold read** (purge, then a district loaded on workers). It may change the compression per content and the size of the near file. Both are per-entry or per-file choices, so neither changes this layout. Learned before 3.4.
