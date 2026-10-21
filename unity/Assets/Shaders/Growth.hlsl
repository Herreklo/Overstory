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

float _OS_NearForce;     // debug: 0 by distance, 1 painted everywhere, 2 the near detail everywhere

// How near a pixel is, for the detail it can carry: true up close, painted from afar (docs/visual-direction.md). 1
// within a couple of metres at eye level (a pixel about a millimetre on the surface), 0 by about seven (four), so
// by the street stop every mark is its painted shape.
half OS_Near(float footprint)
{
    half n = 1.0h - saturate((half)((footprint - 0.0012) / 0.0028));
    return _OS_NearForce > 1.5 ? 1.0h : (_OS_NearForce > 0.5 ? 0.0h : n);
}

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
    // (colonies a few centimetres across, merging into fields: at 0.7 mm a year a century's rosette is about 8 cm)
    float k = 1.0 / 0.05;
    float2 w = float2(OS_Noise(q * k * 0.6 + seed * 5.1), OS_Noise(q * k * 0.6 + 9.7 + seed * 2.3)) - 0.5;
    float2 qq = q * k + w * 1.8;
    half field = (half)(OS_Noise(qq) * 0.55 + OS_Noise(qq * 2.3 + 4.4) * 0.3 + OS_Noise(qq * 5.1 + 1.3) * 0.15);
    // the edge: lobed at a centimetre and crumbling at a millimetre or two (a smooth threshold read as spilt paint)
    half lobe = (half)(OS_Noise(q * 90.0 + seed * 3.0) - 0.5);
    half crumb = (half)(OS_Noise(q * 330.0 + seed * 7.0) - 0.5);
    // how much each stone carries is its own (its skin, its tilt to the rain), about a third either way
    half share = saturate((years - 10.0h) / 110.0h) * 0.34h * (half)_OS_LichenRate.z / 0.85h
               * (0.65h + 0.7h * frac(seed * 7.31h));
    half pq = clamp(1.0h - share, 0.002h, 0.998h);
    half th = 0.5h + 0.138h * (half)(log(pq / (1.0h - pq)) / 1.702);
    // true up close, painted from afar: near, the crust as it grows (a lobed edge crumbling at a millimetre or two, a
    // dark line where colonies crowd and meet, a few young colonies between); further off, the same field painted as
    // a soft spot with one pale value (crumbs, lines and flecks read as speckle from the street stop)
    half near = OS_Near(footprint);
    half fr = field + lobe * 0.06h + crumb * 0.035h;
    half coverNear = smoothstep(th - 0.004h, th + 0.004h, fr);
    half crowd = smoothstep(0.55h, 0.72h, (half)OS_Noise(q * 6.0 + seed * 1.7));
    // (a faint darker rim on every lobed edge, stronger where colonies crowd and meet: the board, 06)
    half rim = coverNear * (1.0h - smoothstep(th + 0.004h, th + 0.018h, fr)) * lerp(0.25h, 0.6h, crowd);
    const float cell = 0.03;
    float2 p2 = q / cell;
    float2 h2 = OS_GrowthHash2(floor(p2) + seed * 11.3);
    half r2 = saturate(years / 40.0h) * (0.12h + 0.18h * (half)h2.y);
    if (h2.x < share * 0.18h)
    {
        half d2 = (half)length(frac(p2) - 0.5) / max(r2, 1e-3h) + lobe * 1.2h + crumb * 0.8h;
        coverNear = max(coverNear, 1.0h - smoothstep(0.85h, 1.0h, d2));
    }
    half f = field + lobe * 0.04h;
    half cover = lerp(smoothstep(th - 0.05h, th + 0.04h, f), coverNear, near);
    rim *= near;
    // further still (12 m and up), the same lichen as a few large soft fields where colonies are dense, at about half
    // the contrast: a low-pass of its own field, never its spots (hundreds of small pale spots read as speckle)
    half big = (half)OS_Noise(q * k * 0.28 + seed * 3.9);
    half thB = 0.5h + 0.18h * (half)(log(pq / (1.0h - pq)) / 1.702);
    half coverBig = smoothstep(thB - 0.1h, thB + 0.1h, big) * 0.65h;
    half mid = saturate((half)((footprint - 0.005) / 0.006));
    cover = lerp(cover, coverBig, mid);
    half age = saturate((f - th) / 0.1h) * saturate(years / 100.0h);
    // (only once a colony is smaller than a pixel: from the street stop and 12 m the fields still show as soft pale
    // shapes where they are; faded to a mean earlier, the old run's lichen vanished and the history read inverted)
    half far = saturate((half)((footprint - 0.025) / 0.03));
    cover = lerp(cover, share * 0.65h, far);
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
    // near, the crust cracked into tiny plates (areoles) a millimetre or two across, greyer in places, a few dark
    // fruiting dots; further off one pale value, older and greyer towards a colony's middle, broadly
    half near = OS_Near(footprint);
    half mottle = (half)OS_Noise(q * 9.0 + seed * 2.1);
    half3 lich = lerp(_OS_Lichen.rgb, _OS_LichenOld.rgb, saturate(li.y * 0.8h + (mottle - 0.5h) * 0.4h));
    if (near > 0.01h)
    {
        half areole = (half)OS_Noise(q * 700.0 + seed * 3.3);
        half mot = (half)OS_Noise(q * 28.0 + seed * 2.1);
        half dots = smoothstep(0.87h, 0.9h, (half)OS_Noise(q * 140.0 + seed * 5.3));
        half3 crust = lerp(_OS_Lichen.rgb, _OS_LichenOld.rgb, saturate(li.y + (mot - 0.5h) * 0.8h)) * (0.96h + 0.06h * areole);
        crust *= 1.0h - 0.3h * dots;
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
}

#endif
