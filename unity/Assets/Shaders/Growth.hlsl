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

// Lichen in a surface's own plane (metres), as crustose lichen covers a quiet stone over a century (the board, 06, 05;
// map lichen): crusts a few centimetres to a hand across, lobed, most of them old colonies grown into one another,
// with a few small young ones between; a thin dark rim where a crust meets bare stone (map lichen's prothallus, a
// pigment of the lichen, never a shade). How much is covered grows with the quiet years to about a third of a quiet
// place after a century; none where it is trodden or cleaned, fading with the quiet. Once a pixel covers more than a
// crust it is seen as its mean, as a lens would average it. x coverage, y how old (0 young to 1), z the rim.
half3 OS_LichenAt(float2 q, half years, half seed, float footprint)
{
    // the crusts: a warped field over the plane, its quantile set so the covered share follows the years (its spread
    // as measured: mean 0.5, deviation about 0.14)
    float k = 1.0 / 0.07;
    float2 w = float2(OS_Noise(q * k * 0.6 + seed * 5.1), OS_Noise(q * k * 0.6 + 9.7 + seed * 2.3)) - 0.5;
    float2 qq = q * k + w * 1.8;
    half field = (half)(OS_Noise(qq) * 0.55 + OS_Noise(qq * 2.3 + 4.4) * 0.3 + OS_Noise(qq * 5.1 + 1.3) * 0.15);
    half lobe = (half)(OS_Noise(q * 90.0 + seed * 3.0) - 0.5);
    half share = saturate((years - 10.0h) / 110.0h) * 0.34h * (half)_OS_LichenRate.z / 0.85h;
    half pq = clamp(1.0h - share, 0.002h, 0.998h);
    half th = 0.5h + 0.138h * (half)(log(pq / (1.0h - pq)) / 1.702);
    half f = field + lobe * 0.05h;
    half cover = smoothstep(th - 0.006h, th + 0.006h, f);
    // the rim: a thin band just inside the crust's edge
    half rim = cover * (1.0h - smoothstep(th + 0.006h, th + 0.03h, f));
    // a few young colonies between, a centimetre or less
    const float cell = 0.03;
    float2 p2 = q / cell;
    float2 h2 = OS_GrowthHash2(floor(p2) + seed * 11.3);
    half r2 = saturate(years / 40.0h) * (0.12h + 0.18h * (half)h2.y);
    if (h2.x < share * 0.35h)
    {
        half d2 = (half)length(frac(p2) - 0.5) / max(r2, 1e-3h) + lobe * 0.6h;
        half young = 1.0h - smoothstep(0.8h, 1.0h, d2);
        rim = max(rim, young * smoothstep(0.6h, 0.85h, d2));
        cover = max(cover, young);
    }
    half age = saturate((f - th) / 0.1h) * saturate(years / 100.0h);
    half far = saturate((half)((footprint - 0.002) / 0.008));
    cover = lerp(cover, share, far);
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
    half m = moss * lerp(1.3h, 0.9h, sky);
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
