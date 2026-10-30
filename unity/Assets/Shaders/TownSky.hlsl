#ifndef OVERSTORY_TOWN_SKY_INCLUDED
#define OVERSTORY_TOWN_SKY_INCLUDED

// The town round a point (Overstory.Scenes.SkyMap): how much of its sky the town leaves open, and what the town
// gives back in place of the sky it hides. Shared by every surface that takes the town's light: the street's looks
// (StreetLooks.hlsl) and the finished houses (OS_Finish).

// The town's sky map: its height from above. The shade uses it for the sky each point sees (OS_TownSky); the fog for
// where land is under it.
TEXTURE2D(_OS_SkyMap);
SAMPLER(sampler_OS_SkyMap);
float4 _OS_SkyMapRect;  // xy the map's corner (world x, z), z 1 / its size, w 1 when v reads from the top
float _OS_SkyMapOn;
// and the horizon worked out from it once (TownHorizon.shader): each texel's ground, and the horizon's angle in eight
// directions at heights over it
TEXTURE2D(_OS_HorizonGround);
SAMPLER(sampler_OS_HorizonGround);
TEXTURE3D(_OS_Horizon0);
TEXTURE3D(_OS_Horizon1);
float4 _OS_HorizonInfo;  // x texels a side, y height levels, z the top level (m over the ground), w on
// and, at the same texels and heights, what the rest of the town round the house the texel is by changes in the
// trilight's ambient on a face there (TownHorizon.shader, Bounce), worked out for the sun and the ambient as they stand:
// for a wall a mean (0.rgb) and a cosine (0.a 1.rg) and sine (1.ba 2.r) of the way it faces (world x, z), and for a
// face looking up (2.gba) and one looking down (3.rgb)
TEXTURE3D(_OS_TownLight0);
TEXTURE3D(_OS_TownLight1);
TEXTURE3D(_OS_TownLight2);
TEXTURE3D(_OS_TownLight3);
float4 _OS_BounceInfo;  // x on: worked out from the town's facts for the sun as it stands

// The horizon round a point a little off a face: the eight directions' angles (a fraction of a right angle) from the
// horizon map, the four texels round the point each read at the point's own height over that texel's ground, and
// where the bounce map is read for it (the four grounds' mean). False off the map.
bool OS_TownHorizon(float3 o, out half angle[8], out float3 at)
{
    [unroll]
    for (int z = 0; z < 8; z++)
        angle[z] = 0.0h;
    at = 0;
    float2 uv = (o.xz - _OS_SkyMapRect.xy) * _OS_SkyMapRect.z;
    if (any(uv < 0.0) || any(uv > 1.0))
        return false;
    float res = _OS_HorizonInfo.x, levels = _OS_HorizonInfo.y;
    float2 f = uv * res - 0.5;
    float2 i0 = floor(f), b = f - i0;
    half4 a0 = 0.0h, a1 = 0.0h;
    float ground = 0.0;
    [unroll]
    for (int c = 0; c < 4; c++)
    {
        float2 corner = float2(c & 1, c >> 1);
        float2 cuv = (clamp(i0 + corner, 0.0, res - 1.0) + 0.5) / res;
        float g = SAMPLE_TEXTURE2D_LOD(_OS_HorizonGround, sampler_OS_HorizonGround, cuv, 0).r;
        float t = sqrt(saturate((o.y - g) / _OS_HorizonInfo.z));
        float3 uvw = float3(cuv, (t * (levels - 1.0) + 0.5) / levels);
        half w = (half)(lerp(1.0 - b.x, b.x, corner.x) * lerp(1.0 - b.y, b.y, corner.y));
        a0 += w * (half4)SAMPLE_TEXTURE3D_LOD(_OS_Horizon0, sampler_OS_HorizonGround, uvw, 0);
        a1 += w * (half4)SAMPLE_TEXTURE3D_LOD(_OS_Horizon1, sampler_OS_HorizonGround, uvw, 0);
        ground += w * g;
    }
    angle[0] = a0.x; angle[1] = a0.y; angle[2] = a0.z; angle[3] = a0.w;
    angle[4] = a1.x; angle[5] = a1.y; angle[6] = a1.z; angle[7] = a1.w;
    float t = sqrt(saturate((o.y - ground) / _OS_HorizonInfo.z));
    at = float3(uv, (t * (levels - 1.0) + 0.5) / levels);
    return true;
}

// How much of a face's open sky the town leaves open, 0 to 1: the horizon the town makes round it, found in eight
// directions out to about 60 m, each weighted by how much the face looks that way. A lane's floor at the foot of
// two walls keeps a strip of sky; a wall's foot in a yard keeps less; a roof or the open quay keeps it all. The
// horizon is read from the town's horizon map, worked out once from its sky map (TownHorizon.shader): the four
// texels round the point, each at the point's own height over that texel's ground.
half OS_TownSky(float3 positionWS, half3 n)
{
#if defined(OS_L5_TOWNSKY)
    return 1.0h;    // (L5's arm, the harness's bare-townsky: the term skipped, the value with no sky map)
#else
    if (_OS_SkyMapOn < 0.5 || _OS_HorizonInfo.w < 0.5)
        return 1.0h;
    float3 o = positionWS + n * 0.6; // off the face, so a wall does not hide itself
    half angle[8];
    float3 at;
    if (!OS_TownHorizon(o, angle, at))
        return 1.0h;
    half up = abs(n.y);
    float2 nh = n.xz / max(length(n.xz), 1e-4);
    half open = 0.0h, full = 0.0h;
    [unroll]
    for (int k = 0; k < 8; k++)
    {
        float a = (k + 0.5) * 0.785398;
        float2 dir = float2(cos(a), sin(a));
        half w = saturate(up + (1.0h - up) * dot(dir, nh));
        float alpha = angle[k] * HALF_PI;
        // the sky left over the town's horizon: cos^2 for a face looking up, the vertical case for a wall
        half flat = (half)(cos(alpha) * cos(alpha));
        half wall = (half)(1.0 - (2.0 * alpha + sin(2.0 * alpha)) / PI);
        open += w * lerp(wall, flat, up);
        full += w;
    }
    return full > 1e-3 ? open / full : 1.0h;
#endif
}

// What the rest of the town round a face changes in the light rig's ambient on it (the trilight, as SampleSH gives it):
// the sky and ground its neighbours hide taken away and the light of what hides them put in their place, its albedo
// times the sun as far as it reaches it and the rig's ambient on a wall. Its own house is in its own bake, so only the
// others count. Worked out once for the sun and the ambient as they stand (TownHorizon.shader, Bounce) and read here at
// the point a little off the face, for its normal: a wall's by the way it faces, blended toward a level face's as it
// tilts. Zero off the map and without the town's facts.
half3 OS_TownLight(float3 positionWS, half3 n)
{
    if (_OS_SkyMapOn < 0.5 || _OS_HorizonInfo.w < 0.5 || _OS_BounceInfo.x < 0.5)
        return 0.0h;
    float3 o = positionWS + n * 0.6; // off the face, as OS_TownSky
    float2 uv = (o.xz - _OS_SkyMapRect.xy) * _OS_SkyMapRect.z;
    if (any(uv < 0.0) || any(uv > 1.0))
        return 0.0h;
    float levels = _OS_HorizonInfo.y;
    float g = SAMPLE_TEXTURE2D_LOD(_OS_HorizonGround, sampler_OS_HorizonGround, uv, 0).r;
    float t = sqrt(saturate((o.y - g) / _OS_HorizonInfo.z));
    float3 at = float3(uv, (t * (levels - 1.0) + 0.5) / levels);
    half4 t0 = (half4)SAMPLE_TEXTURE3D_LOD(_OS_TownLight0, sampler_OS_HorizonGround, at, 0);
    half4 t1 = (half4)SAMPLE_TEXTURE3D_LOD(_OS_TownLight1, sampler_OS_HorizonGround, at, 0);
    half4 t2 = (half4)SAMPLE_TEXTURE3D_LOD(_OS_TownLight2, sampler_OS_HorizonGround, at, 0);
    half4 t3 = (half4)SAMPLE_TEXTURE3D_LOD(_OS_TownLight3, sampler_OS_HorizonGround, at, 0);
    half2 h = (half2)(n.xz / max(length(n.xz), 1e-4));
    half3 wall = t0.rgb + half3(t0.a, t1.rg) * h.x + half3(t1.ba, t2.r) * h.y;
    return wall * (1.0h - abs(n.y)) + t2.gba * saturate(n.y) + t3.rgb * saturate(-n.y);
}

#endif
