#ifndef OVERSTORY_HISTORY_INCLUDED
#define OVERSTORY_HISTORY_INCLUDED

// History read from pages against the date (docs/building-blocks.md, History; docs/research/history-pages.md; schemas
// maps.json, layers.json and chunk-format.md). Every shader reads a place or history layer through
// OS_History(address, layer) here, and nowhere else. The pages hold inputs (rates, amplitudes, the texel's age offset,
// the place's light inputs), never years since; the date is one global (_OS_Date, Overstory.World.FabricDate), so a
// jump in time costs one uniform.
//
// Binding (history-pages.md, 1): one Texture2DArray per GPU format, bound globally. _OS_PagesRGBA holds P0, P1 and H1
// of every page group, a slice per group and page (RGBA8, or BC7 from EditorUtility.CompressTexture). The piece table
// is a global StructuredBuffer (_OS_Pieces), read in the vertex stage by UV3's piece index; its entry passes flat to
// the fragment. No material property, no extra draw or SRP batch. Needs #pragma target 4.5.
//
// The law (a layer's inputs and the date to its value) is not written: R1's numbers settle the encoding and R4
// writes it in OS_HistoryLaw. Until then the stub passes the stored input through.
//
// OS_HISTORY_OFF (a measuring arm: the harness's history-off, docs/measuring.md): no page is sampled and no piece read;
// every layer is its material's quiet mean, as a page group without the layer's page reads it (D5.9). A shader that
// reads OS_History declares the quiet means in its UnityPerMaterial, one half4 a page, each channel the layer's value
// (not its input): _OS_QuietP0, _OS_QuietP1, _OS_QuietH1. It may name its own by defining OS_QUIET_PAGE first.

// ------------------------------------------------------------------------------------------------- the date

// x the year with the month as a fraction (float32, never half: a half holds 1989.5 as 1990), y the day of the year,
// z the hour, w reserved
float4 _OS_Date;

// ------------------------------------------------------------------------------------------------- pages and layers

// The shared pages every page group has, by their slice after the group's first. H2 and H3 are story pages
// (layers.json, budget "story"): their slices come with the history budget (step 4), not at a fixed stride.
#define OS_PAGE_P0 0
#define OS_PAGE_P1 1
#define OS_PAGE_H1 2

// A layer is its page × 4 + its channel (maps.json's channels).
#define OS_LAYER_FEET 0          // p0.r
#define OS_LAYER_WATER_HELD 1    // p0.g
#define OS_LAYER_SKY_SEEN 2      // p0.b
#define OS_LAYER_GROUND_SEEN 3   // p0.a
#define OS_LAYER_OPENNESS 4      // p1.r
#define OS_LAYER_EXPOSURE 5      // p1.g (p1.b and p1.a reserved)
#define OS_LAYER_POLISH 8        // h1.r
#define OS_LAYER_LICHEN 9        // h1.g
#define OS_LAYER_MOSS 10         // h1.b
#define OS_ONSET 11              // h1.a: not a layer, the texel's age offset for every h layer (layers.json, notLayers)

#ifndef OS_QUIET_PAGE
#define OS_QUIET_PAGE(page) ((page) == OS_PAGE_P0 ? _OS_QuietP0 : ((page) == OS_PAGE_P1 ? _OS_QuietP1 : _OS_QuietH1))
#endif

// ------------------------------------------------------------------------------------------------- the piece table

// One entry a piece, 16 bytes: the GPU form of chunk-format.md's piece table (24 bytes on disk). The GPU needs where
// the piece's pages are and its clocks, not its ids. Resets and the age are u16s of year × 16 + month from the pack's
// first year (history-pages.md, 3). Which resets a piece keeps (placed, bare, bed, lifted) is R1's to settle.
struct OSPiece
{
    uint slice;     // its page group's first slice in the page arrays (P0; P1 and H1 follow)
    uint resets;    // two u16 reset dates
    uint resets2;   // two more
    uint age;       // low u16 the piece's age offset (reclaimed stone), high u16 flags
};

StructuredBuffer<OSPiece> _OS_Pieces;

// The unit's base in the table: the renderer's user value is the pick index, and its unit slot will give the base
// (history-pages.md, 1). Step 3 has one table: base 0.
#ifndef OS_PIECE_BASE
#define OS_PIECE_BASE 0u
#endif

// A piece's entry, in the vertex stage (UV3's piece index). History off reads nothing.
OSPiece OS_Piece(uint index)
{
#if defined(OS_HISTORY_OFF)
    return (OSPiece)0;
#else
    return _OS_Pieces[OS_PIECE_BASE + index];
#endif
}

// The entry passed flat from the vertex to the fragment (a nointerpolation uint4).
uint4 OS_PackPiece(OSPiece p) { return uint4(p.slice, p.resets, p.resets2, p.age); }

OSPiece OS_UnpackPiece(uint4 v)
{
    OSPiece p;
    p.slice = v.x;
    p.resets = v.y;
    p.resets2 = v.z;
    p.age = v.w;
    return p;
}

// ------------------------------------------------------------------------------------------------- reading a layer

TEXTURE2D_ARRAY(_OS_PagesRGBA);
SAMPLER(sampler_OS_PagesRGBA);

// Where a fragment reads its history: its texel in its group's pages (UV1) and its piece.
struct OSAddress
{
    float2 uv;
    OSPiece piece;
};

OSAddress OS_Address(float2 uv1, uint4 piece)
{
    OSAddress a;
    a.uv = uv1;
    a.piece = OS_UnpackPiece(piece);
    return a;
}

// A page's four channels at the texel (trilinear, clamped; the array's own sampler). History off: the material's
// quiet means for that page.
half4 OS_HistoryPage(OSAddress a, uint page)
{
#if defined(OS_HISTORY_OFF)
    return (half4)OS_QUIET_PAGE(page);
#else
    return (half4)SAMPLE_TEXTURE2D_ARRAY(_OS_PagesRGBA, sampler_OS_PagesRGBA, a.uv, a.piece.slice + page);
#endif
}

// A layer's stored inputs.
struct OSLayer
{
    half input;      // the layer's channel at the texel: a rate or an amplitude (R1 settles which, layer by layer)
    half onset;      // an h layer's age offset at the texel (h1.a, as stored: R1 settles its bias and scale); 0 for p
    OSPiece piece;   // the piece's clocks, its resets and age (R1 settles which a layer takes)
    bool quiet;      // the material's quiet mean: input is then the layer's value, and the law passes it through
};

// The layer's stored inputs at the address (one sample a page: the compiler shares a page's sample between its layers).
OSLayer OS_History(OSAddress a, uint layer)
{
    uint page = layer >> 2;
    half4 p = OS_HistoryPage(a, page);
    OSLayer l;
    l.input = p[layer & 3u];
    l.onset = page == OS_PAGE_H1 ? p.a : 0.0h;
    l.piece = a.piece;
#if defined(OS_HISTORY_OFF)
    l.quiet = true;
#else
    l.quiet = false;
#endif
    return l;
}

// THE LAW, A STUB until R4: a layer's value at the date from its stored inputs, its piece's clocks and its material's
// curve (D5.1; history-pages.md, 3: polish and moss an amplitude times a saturating curve, lichen a rate after a
// delay). Until then it passes the stored input through, so a page reads as it was baked. A quiet layer is already
// its value.
half OS_HistoryLaw(OSLayer l, uint layer, float4 date)
{
    return l.input;
}

// A layer's value at the fabric's date.
half OS_HistoryAt(OSAddress a, uint layer)
{
    return OS_HistoryLaw(OS_History(a, layer), layer, _OS_Date);
}

#endif
