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

#include "Detail.hlsl"

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
// pigment of the lichen, never a shade). How much is covered grows with the quiet years to most of a quiet place
// after a century (the pack's share), the rock showing through in gaps and the crust flecked dark with its fruit
// (references 10, 06: a pale crust with dark specks); none where it is trodden or cleaned, fading with the quiet. Once a pixel covers more than a
// crust it is seen as its mean, as a lens would average it. x coverage, y how old (0 young to 1), z the rim.
half3 OS_LichenAt(float2 q, half years, half seed, half spread, float footprint)
{
    // how much of a quiet surface it covers after its years: on a century's quiet stone the crust is the surface and
    // the rock shows through it (references 10, 06), each stone its own (its skin, its tilt to the rain), spread either way
    half share = saturate(saturate((years - 10.0h) / 110.0h) * (half)_OS_LichenRate.z
               * (1.0h + spread * (frac(seed * 7.31h) * 2.0h - 1.0h)));
    // the colonies: crustose lichen grows as rosettes, each from a point in its own year, spreading about a third of a
    // millimetre a year (a century's rosette a few centimetres across), merging where they meet and stopping at a
    // stone's edge; so a stone carries round colonies of many ages and sizes (a noise field's meandering edge read as
    // camouflage). Scattered over cells five centimetres across, as many as the covered share needs.
    half near = OS_Near(footprint);
    half lobe = (half)(OS_Noise(q * 90.0 + seed * 3.0) - 0.5);
    half crumb = (half)(OS_Noise(q * 330.0 + seed * 7.0) - 0.5) * near;
    // the old colonies, begun in the stone's first decades, have grown into one another: fields a hand to a forearm
    // across with ragged lobed edges (the board, 06), from a warped field whose covered share follows the years; round
    // rosettes everywhere read as polka dots
    half cover = 0.0h, rim = 0.0h, age = 0.0h;
    half soft = lerp(0.06h, 0.012h, near);      // (crisp near; at the street stop painted soft)
    {
        float k = 1.0 / 0.09;
        float2 w = float2(OS_Noise(q * k * 0.5 + seed * 5.1), OS_Noise(q * k * 0.5 + 9.7 + seed * 2.3)) - 0.5;
        float2 qq = q * k + w * 2.2;
        half field = (half)(OS_Noise(qq) * 0.55 + OS_Noise(qq * 2.3 + 4.4) * 0.3 + OS_Noise(qq * 5.1 + 1.3) * 0.15);
        half shareOld = share * 0.85h;
        half pq = clamp(1.0h - shareOld, 0.002h, 0.998h);
        half th = 0.5h + 0.138h * (half)(log(pq / (1.0h - pq)) / 1.702);
        half f = field + lobe * 0.05h + crumb * 0.03h;
        cover = smoothstep(th - soft, th + soft, f);
        age = saturate((f - th) / 0.1h) * saturate(years / 100.0h);
        // (a faint darker line just inside the edge, stronger where fields meet: the board, 06)
        rim = cover * (1.0h - smoothstep(th + soft, th + 0.025h, f)) * 0.4h * near;
    }
    // the young colonies between, few and small, each a rosette from its own year
#if !defined(OS_L5_ROSETTES)    // (L5's arm, bare-rosettes: the young colonies' loop skipped)
    {
        float cell = 0.04;
        float2 pc = q / cell + seed * 18.8;
        float2 ci = floor(pc);
        half density = saturate(share * 0.6h);
        for (int j = -1; j <= 1; j++)
        {
            for (int i = -1; i <= 1; i++)
            {
                float2 c = ci + float2(i, j);
                float2 h = OS_GrowthHash2(c + 31.7);
                if (h.x > density)
                    continue;
                half ageC = years * (half)OS_Hash(c + 11.3) * 0.5h;
                half r = clamp(ageC * 0.0005h, 0.002h, 0.02h) / (half)cell;
                float2 ctr = c + 0.15 + 0.7 * float2(h.y, OS_Hash(c + 10.1));
                half lobeC = (half)(OS_Noise(pc * 3.1 + h * 17.0) - 0.5) * 0.3h;
                half d = (half)length(pc - ctr) / max(r, 1e-3h) + lobeC + crumb * 0.25h;
                half cv = (1.0h - smoothstep(1.0h - soft * 3.0h, 1.0h, d)) * 0.7h;
                if (cv > cover)
                {
                    cover = cv;
                    age = saturate(ageC / 100.0h);
                    rim = 0.0h;
                }
            }
        }
    }
#endif
    // further off (by the street stop), each stone's lichen as a film over it, as much as its own years and
    // quiet give: a wall reads by its stones and a flight by its quiet ends, never by blobs that cross the joints
    half mid = saturate((half)((footprint - 0.003) / 0.004));
    cover = lerp(cover, share, mid);
    return half3(cover, age * (1.0h - mid), rim * (1.0h - mid));
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
OSGrowth OS_GrowthLayer(half3 albedo, half smoothness, float2 q, half lichenYears, half moss, half sky, half seed, half spread,
                        float3 positionWS)
{
    OSGrowth g;
#if defined(OS_L5_GROWTH)
    // (L5's arm, bare-growth: the whole layer skipped, the surface bare)
    g.albedo = albedo;
    g.smoothness = smoothness;
    g.height = 0.0h;
    g.cover = 0.0h;
    return g;
#else
    float footprint = max(length(ddx(positionWS)), length(ddy(positionWS)));
    half3 li = OS_LichenAt(q, lichenYears, seed, spread, footprint);
    // near, the crust cracked into tiny plates (areoles) a millimetre or two across, greyer in places, its fruit a
    // few black discs a millimetre or two across where it is old (an even fleck everywhere reads as granite); further
    // off one pale value, older and greyer towards a colony's middle
    half near = OS_Near(footprint);
    half mottle = (half)OS_Noise(q * 9.0 + seed * 2.1);
    half3 lich = lerp(_OS_Lichen.rgb, _OS_LichenOld.rgb, saturate(li.y * 0.8h + (mottle - 0.5h) * 0.4h));
    if (near > 0.01h)
    {
        half areole = (half)OS_Noise(q * 700.0 + seed * 3.3);
        half mot = (half)OS_Noise(q * 28.0 + seed * 2.1);
        half dots = smoothstep(0.86h, 0.89h, (half)OS_Noise(q * 160.0 + seed * 5.3)) * saturate(li.y * 1.5h);
        half3 crust = lerp(_OS_Lichen.rgb, _OS_LichenOld.rgb, saturate(li.y + (mot - 0.5h) * 0.8h)) * (0.96h + 0.06h * areole);
        crust = lerp(crust, _OS_LichenRim.rgb, dots * 0.8h);
        lich = lerp(lich, crust, near);
    }
    lich = lerp(lich, _OS_LichenRim.rgb, li.z);
    albedo = lerp(albedo, lich, li.x);
    smoothness = lerp(smoothness, 0.08h, li.x);
    half h = li.x * 0.8h;
    // moss: where the surface stays damp and is not trodden, more where the town hides the sky; in cushions a few
    // centimetres across that crowd into a line where it is dampest (a noise field read as a flat olive tint), each
    // a low dome whose top the light finds (its relief, never a darker pigment), fresher on top, older and browner
    // at its edges
    half m = moss * lerp(1.3h, 0.9h, sky);
    float2 cq = q * 28.0 + seed * 3.7;
    float2 ci = floor(cq);
    half dome = 0.0h;
    half fresh = 0.0h;
    for (int j = -1; j <= 1; j++)
    {
        for (int i = -1; i <= 1; i++)
        {
            float2 cell = ci + float2(i, j);
            float2 hh = OS_GrowthHash2(cell);
            float2 pt = cell + 0.15 + 0.7 * hh;
            // (cushions crowd and merge into a mat with an uneven edge: alone and round they read as polka dots)
            half r = 0.75h + 0.5h * (half)OS_Hash(cell + 7.7);
            half d = (half)length(cq - pt) / r + ((half)OS_Noise(q * 95.0 + cell * 0.37) - 0.5h) * 0.5h;
            half dm = saturate(1.0h - d * d);
            if (dm > dome) { dome = dm; fresh = (half)hh.y; }
        }
    }
    half cover = smoothstep(0.3h, 0.5h, m * (0.5h + 0.8h * dome));
    half3 mossc = lerp(_OS_MossOld.rgb, _OS_Moss.rgb, saturate(dome * 1.3h - 0.1h) * (0.6h + 0.4h * fresh));
    albedo = lerp(albedo, mossc, cover);
    smoothness = lerp(smoothness, 0.05h, cover);
    h += cover * lerp(0.3h + 0.8h * dome, 0.6h + 1.8h * dome, near);
    g.albedo = albedo;
    g.smoothness = smoothness;
    g.height = h;
    g.cover = saturate(max(li.x, cover));
    return g;
#endif
}

#endif
