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
float4 _OS_LichenRate;   // x growth (m a year), y the size of a patch (m), z how much of a quiet surface it takes
half4 _OS_Moss;          // rgb fresh moss
half4 _OS_MossOld;       // rgb moss grown old, browner

float2 OS_GrowthHash2(float2 p)
{
    return float2(OS_Hash(p), OS_Hash(p + 19.19));
}

// Lichen in a surface's own plane (metres), as crustose lichen covers a quiet stone or board: map-like patches that
// spread and merge with the years, the bare surface showing through between them in winding channels. How much is
// covered grows with the quiet years (none where it is trodden or cleaned), so an old quiet surface is mostly crust
// and a young one a few scattered spots; edges ragged by a finer field; an old patch greyer in its middle. Once a
// pixel covers more than a patch it is seen as its mean, as a lens would average it. x coverage, y how old.
half2 OS_LichenAt(float2 q, half years, half seed, float footprint)
{
    float k = 1.0 / _OS_LichenRate.y;
    float2 w = float2(OS_Noise(q * k * 0.7 + seed * 5.1), OS_Noise(q * k * 0.7 + 9.7 + seed * 2.3)) - 0.5;
    float2 qq = q * k + w * 1.6;
    half field = (half)(OS_Noise(qq) * 0.55 + OS_Noise(qq * 2.1 + 4.4) * 0.3 + OS_Noise(qq * 4.7 + 1.3) * 0.15);
    half fine = (half)(OS_Noise(q * 70.0 + seed * 3.0) * 0.6 + OS_Noise(q * 160.0) * 0.4) - 0.5h;
    half share = saturate((years - 8.0h) / 140.0h) * (half)_OS_LichenRate.z;
    half th = 1.0h - share;
    half f = field + fine * 0.08h;
    half cover = smoothstep(th - 0.02h, th + 0.02h, f);
    // young colonies: a few small spots ahead of the patches
    float2 p2 = q / 0.03;
    float2 h2 = OS_GrowthHash2(floor(p2) + seed * 11.3);
    half r2 = 0.25h + 0.2h * (half)h2.y;
    if (h2.x < share * 0.12h)
        cover = max(cover, 1.0h - smoothstep(0.75h, 1.0h, (half)length(frac(p2) - 0.5) / r2 + fine * 0.4h));
    half age = saturate((f - th) / 0.12h) * saturate(years / 90.0h);
    half far = saturate((half)((footprint - 0.004) / 0.02));
    cover = lerp(cover, share * 0.9h, far);
    return half2(cover, age * (1.0h - far));
}

struct OSGrowth
{
    half3 albedo;      // the surface's pigment with its growth on it
    half smoothness;
    half height;       // what the growth adds to the surface's relief (in the surface's own units)
};

// The thin growth on a surface: its pigment and smoothness in, the same with lichen and moss on it out. q the
// surface's own plane (metres); lichenYears the years lichen has grown here (0 to 200); moss the baked moss potential
// (0 to 1); sky what the point sees of the sky in the town (moss takes more where it is hidden); seed per piece.
OSGrowth OS_GrowthLayer(half3 albedo, half smoothness, float2 q, half lichenYears, half moss, half sky, half seed,
                        float3 positionWS)
{
    OSGrowth g;
    float footprint = max(length(ddx(positionWS)), length(ddy(positionWS)));
    half2 li = OS_LichenAt(q, lichenYears, seed, footprint);
    half3 lich = lerp(_OS_Lichen.rgb, _OS_LichenOld.rgb, li.y) * (0.92h + 0.16h * (half)OS_Noise(q * 40.0));
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
    return g;
}

#endif
