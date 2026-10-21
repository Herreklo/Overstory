#ifndef OVERSTORY_GROWTH_INCLUDED
#define OVERSTORY_GROWTH_INCLUDED

// Growth on surfaces (docs/nature.md, Growth on surfaces): the thin growth every surface in the town draws the same
// way, whatever it is (stone now; timber, roofs, bark, concrete next): crustose lichen spreading and merging with its
// years, moss filling the damp places. Where and for how long come from the surface's own facts, baked by its
// generator (blender/generators/growth.py); which species, their pigments and growth rates are the setting pack's,
// set once for the town (Overstory.World.GrowthPack). Pigments only: a joint's dark is its occlusion, the light's,
// never a darker moss (SEASON's lesson). Thick growth (grass in joints, moss cushions, ferns) is nature's parts,
// placed by its fields from the same potentials.
//
// Include after StreetSurface.hlsl (OS_Hash, OS_Noise).

half4 _OS_Lichen;        // rgb the crust's pigment
half4 _OS_LichenOld;     // rgb an old patch's centre
half4 _OS_LichenRim;     // rgb the dark rim where a colony meets bare stone or a neighbour
float4 _OS_LichenRate;   // x growth (m a year), y the size of a patch (m), z how much of a quiet surface it takes
half4 _OS_Moss;          // rgb fresh moss
half4 _OS_MossOld;       // rgb moss grown old, browner

float2 OS_GrowthHash2(float2 p)
{
    return float2(OS_Hash(p), OS_Hash(p + 19.19));
}

// Lichen in a surface's own plane (metres), as crustose lichen colonises a quiet stone (the board, 06; map lichen):
// colonies seeded across the surface, each a disc whose diameter is its growth rate times its own years (a colony
// starts a few years after the next), its edge a little ragged; a thin dark rim where a colony meets bare stone or
// a neighbour (map lichen's black prothallus, a pigment of the lichen, not a shade); young colonies a few millimetres,
// old ones merging into patches. How many colonies settle grows with the quiet years and the pack's share; none
// where it is trodden or cleaned. Once a pixel covers more than a colony it is seen as its mean cover, as a lens would
// average it. x coverage, y how old (0 young to 1), z the rim (0 to 1).
half3 OS_LichenAt(float2 q, half years, half seed, float footprint)
{
    const float cell = 0.03;
    float2 p = q / cell;
    float2 i = floor(p);
    // (at most a third of a quiet place covered after a century: denser, it read as terrazzo)
    half presence = saturate(years / 90.0h) * 0.28h * (half)_OS_LichenRate.z;
    half rag = (half)(OS_Noise(q * 160.0 + seed * 7.0) - 0.5);
    half cover = 0.0h, age = 0.0h, rim = 0.0h, inside = 0.0h;
    half meanc = 0.0h;
    [unroll] for (int y = -1; y <= 1; y++)
    [unroll] for (int x = -1; x <= 1; x++)
    {
        float2 c = i + float2(x, y);
        float2 h = OS_GrowthHash2(c + seed * 31.7);
        half own = max(years - 6.0h - 30.0h * (half)h.y, 0.0h);
        // radius in cells: half the diameter its years grew, a colony at most a hand across before it merges
        half r = (half)min(_OS_LichenRate.x * own * 0.5 / cell, 2.2);
        if (x == 0 && y == 0)
            meanc = presence * saturate(3.14h * r * r);
        if (h.x > presence || r < 0.04h)
            continue;
        float2 centre = c + OS_GrowthHash2(c + 7.3);
        half d = (half)length(p - centre) / r + rag * 0.35h;
        half inC = 1.0h - smoothstep(0.94h, 1.0h, d);
        // the rim: the last few hundredths of the radius, and where this colony's crust meets one already laid
        // (thin, and only on an old colony or where two meet: on every disc it read as a leopard's spots)
        half edge = smoothstep(0.88h, 0.94h, d) * inC * saturate(r - 0.6h) + inside * inC * 0.6h;
        rim = max(rim, saturate(edge));
        inside = max(inside, inC);
        if (inC > cover)
        {
            cover = inC;
            age = saturate(r * cell / 0.03h) * (1.0h - smoothstep(0.0h, 0.8h, d));
        }
    }
    half far = saturate((half)((footprint - 0.002) / 0.008));
    cover = lerp(cover, saturate(meanc * 1.6h), far);
    return half3(cover, age * (1.0h - far), rim * (1.0h - far));
}

struct OSGrowth
{
    half3 albedo;      // the surface's pigment with its growth on it
    half smoothness;
    half height;       // what the growth adds to the surface's relief (in the surface's own units)
    half cover;        // how much of the surface the growth covers (moss and lichen stay matt in the rain)
};

// The thin growth on a surface: its pigment and smoothness in, the same with lichen and moss on it out. q the
// surface's own plane (metres); lichenYears the years lichen has grown here (0 to 200); moss the baked moss potential
// (0 to 1); sky what the point sees of the sky in the town (moss takes more where it is hidden); seed per piece.
OSGrowth OS_GrowthLayer(half3 albedo, half smoothness, float2 q, half lichenYears, half moss, half sky, half seed,
                        float3 positionWS)
{
    OSGrowth g;
    float footprint = max(length(ddx(positionWS)), length(ddy(positionWS)));
    half3 li = OS_LichenAt(q, lichenYears, seed, footprint);
    // the crust: cracked into tiny plates (areoles) a millimetre or two across
    half areole = (half)OS_Noise(q * 700.0 + seed * 3.3);
    half3 lich = lerp(_OS_Lichen.rgb, _OS_LichenOld.rgb, li.y) * (0.9h + 0.16h * areole);
    lich = lerp(lich, _OS_LichenRim.rgb, li.z);
    albedo = lerp(albedo, lich, li.x);
    smoothness = lerp(smoothness, 0.08h, li.x);
    half h = li.x * 0.8h;
    // moss: where the surface stays damp and is not trodden; more where the town hides the sky
    half m = moss * lerp(1.15h, 0.7h, sky);
    half tuft = (half)(OS_Noise(q * 24.0 + 3.0) * 0.6 + OS_Noise(q * 70.0) * 0.4);
    half cover = smoothstep(0.42h, 0.58h, m * (0.55h + 0.6h * tuft));
    half3 mossc = lerp(_OS_MossOld.rgb, _OS_Moss.rgb, saturate(tuft * 1.4h - 0.1h));
    albedo = lerp(albedo, mossc, cover);
    smoothness = lerp(smoothness, 0.05h, cover);
    h += cover * 0.8h;
    g.albedo = albedo;
    g.smoothness = smoothness;
    g.height = h;
    g.cover = saturate(max(li.x, cover));
    return g;
}

#endif
