#ifndef OVERSTORY_STREET_SURFACE_INCLUDED
#define OVERSTORY_STREET_SURFACE_INCLUDED

// The surface every look shares: what a point of the street is made of, how wet it is, whether it
// glows, and how the air between it and the camera changes it. Looks differ only in how they light
// this surface (StreetLooks.hlsl), never in what it is.
//
// Everything comes from the shared palette (one texel per swatch, sampled point-filtered) and from
// globals set by the scene's light rig, so every building, kit piece and stone uses one material.

// the palette, written by blender/generators/palette.py
TEXTURE2D(_OS_Albedo);   // each swatch as it looks unlit (sRGB)
TEXTURE2D(_OS_Emit);     // the light of swatches that can glow, black elsewhere (sRGB)
TEXTURE2D(_OS_Glow);     // which group a glowing swatch belongs to: r windows, g lamps; b paving (linear)
TEXTURE2D(_OS_Surface);  // r smoothness, g metallic, b porosity (linear)

// the light rig (Overstory.Scenes.LightRig)
float _OS_Wetness;       // 0 dry, 1 after hours of drizzle
float _OS_WindowGlow;    // how bright lit windows are (0 by day)
float _OS_LampGlow;      // how bright lamp glass is (0 while the lamps are off)
float _OS_Time;          // the scene's own clock, in seconds: never frame time, so a still is repeatable
float4 _OS_FogColor;     // rgb: the colour of the air close by (linear)
float4 _OS_FogMid;       // rgb: the colour of the air at middle distance (linear), a: that distance
float4 _OS_FogFar;       // rgb: the colour of the air far off (linear), a: the distance at which it takes over
float4 _OS_FogParams;    // x density per metre at the base height, y falloff per metre of height, z base height, w most it may hide
float4 _OS_FogSun;       // rgb: extra colour towards the sun (linear), w: how tight that glow is
float4 _OS_Haze;         // x the low haze's density per metre at sea level, y the height over which it thins to a third
float4 _OS_HazeColor;    // rgb: its colour (linear)
float4 _OS_SunDir;       // xyz: towards the sun
float4 _OS_PavingMeanUV; // xy: the palette UV of setts_mean, the tone a sett pavement averages to
float _OS_Clay;          // 1: every surface one matte grey, to judge shape and composition alone
float _OS_Debug;         // passes for a paintover: 1 palette UV, 2 normal, 3 position mod 8 m, 4 distance; 0 the picture
float _OS_AirBands;      // 0: the air thickens smoothly; n: in n flat bands (look D's graded wipe, or a style's layers)
float _OS_AirBandSoft;   // how soft each band's edge is (0 hard, 1 smooth); 0 reads as look D's 0.2

struct StreetSurface
{
    half3 albedo;
    half3 emission;
    half smoothness;
    half metallic;
    half3 normalWS;
};

// A hash and value noise with no sine, so they agree across GPUs as closely as floats allow.
float OS_Hash(float2 p)
{
    float3 p3 = frac(float3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return frac((p3.x + p3.y) * p3.z);
}

float OS_Noise(float2 p)
{
    float2 i = floor(p);
    float2 f = frac(p);
    float2 u = f * f * (3.0 - 2.0 * f);
    return lerp(lerp(OS_Hash(i), OS_Hash(i + float2(1, 0)), u.x),
                lerp(OS_Hash(i + float2(0, 1)), OS_Hash(i + float2(1, 1)), u.x), u.y);
}

StreetSurface OS_StreetSurface(float2 uv, float3 positionWS, half3 normalWS)
{
    StreetSurface s;
    half3 albedo = SAMPLE_TEXTURE2D(_OS_Albedo, sampler_PointClamp, uv).rgb;
    half3 props = SAMPLE_TEXTURE2D(_OS_Surface, sampler_PointClamp, uv).rgb;
    half3 emit = SAMPLE_TEXTURE2D(_OS_Emit, sampler_PointClamp, uv).rgb;
    half3 glow = SAMPLE_TEXTURE2D(_OS_Glow, sampler_PointClamp, uv).rgb;
    half2 group = glow.rg;
    half paving = glow.b; // 0.5 paving where puddles lie, 1.0 sett paving
    half smoothness = props.r, metallic = props.g, porosity = props.b;
    half3 n = normalWS;

    // Clay: every surface one matte grey, to judge shape and light alone; but glass stays dark and glossy, what
    // glows still glows, and the weather still wets what it wets, for those are facts.
    bool clay = _OS_Clay > 0.5;
    if (clay)
    {
        half glass = step(0.85h, smoothness);
        albedo = lerp(0.42h, 0.045h, glass).xxx;
        smoothness = lerp(0.12h, 0.9h, glass);
        metallic = 0.0h;
    }

    // Once a pixel covers more than a stone, a sett pavement is seen as one tone: its stones, joints
    // and bevels average out as a lens would average them, instead of breaking into speckle.
    float footprint = max(length(ddx(positionWS)), length(ddy(positionWS)));
    half far = saturate((footprint - 0.015) / 0.045) * step(0.75h, paving);
    if (!clay)
        albedo = lerp(albedo, SAMPLE_TEXTURE2D(_OS_Albedo, sampler_PointClamp, _OS_PavingMeanUV.xy).rgb, far);
    n = normalize(lerp(n, half3(0, 1, 0), far));

    // Rain wets what faces the sky; walls a little, undersides (eaves, soffits) not at all. Porous
    // stone darkens and stays matt; glazed tile and paint shed it and shine.
    half up = n.y;
    half wet = _OS_Wetness * saturate((up + 0.1h) / 0.6h);
    albedo *= lerp(1.0h, 1.0h - 0.5h * porosity, wet);
    // wet shine falls with the square of porosity: stone glistens, heath and grass stay matt
    smoothness = lerp(smoothness, max(smoothness, lerp(0.85h, 0.2h, porosity * porosity)), wet);

    // Puddles lie in the hollows of the paving. Where they lie is weather, seeded by place, and
    // claims nothing about the street's history.
    if (_OS_Wetness > 0.0 && up > 0.9h && paving > 0.25h)
    {
        float2 p = positionWS.xz;
        float m = 0.6 * OS_Noise(p * 0.7) + 0.4 * OS_Noise(p * 2.3 + 17.3);
        half puddle = smoothstep(0.69, 0.73, m) * saturate(_OS_Wetness * 1.5 - 0.5);
        albedo = lerp(albedo, albedo * 0.75h, puddle); // water shows as sheen more than as darkening
        smoothness = lerp(smoothness, 0.97h, puddle);
        metallic = lerp(metallic, 0.0h, puddle);
        n = normalize(lerp(n, half3(0, 1, 0), puddle));
    }

    s.albedo = albedo;
    s.emission = emit * (group.r * _OS_WindowGlow + group.g * _OS_LampGlow);
    s.smoothness = smoothness;
    s.metallic = metallic;
    s.normalWS = n;
    return s;
}

// The harbour: dark water with a chop that the scene's clock moves, never frame time.
StreetSurface OS_WaterSurface(float3 positionWS, half4 colour, half smoothness, half scale, half strength)
{
    float2 p = positionWS.xz * scale;
    float t = _OS_Time;
    // the chop flattens with distance, as a lens would average it: no glitter far off
    strength /= 1.0 + 0.02 * distance(positionWS, _WorldSpaceCameraPos);
    const float e = 0.07;
    float2 drift = float2(0.031, 0.017) * t;
    #define OS_WAVE(q) (OS_Noise((q) * float2(1.0, 2.3) + drift) + 0.5 * OS_Noise((q) * 2.7 - drift * 1.7 + 5.1))
    float hx = OS_WAVE(p + float2(e, 0)) - OS_WAVE(p - float2(e, 0));
    float hz = OS_WAVE(p + float2(0, e)) - OS_WAVE(p - float2(0, e));
    #undef OS_WAVE
    StreetSurface s;
    s.albedo = colour.rgb;
    s.emission = 0;
    s.smoothness = smoothness;
    s.metallic = 0;
    s.normalWS = normalize(half3(-hx * strength, 2.0 * e, -hz * strength));
    if (_OS_Clay > 0.5)
        s.albedo = 0.10; // dark and as glossy as water, so in clay it still reads as water under the sky
    return s;
}

// Leaf cards (blender/generators/tree.py): a tree's crown is cards whose second UV carries their own
// coordinates offset by one (1 to 2). Each is cut into a soft, ragged cluster of leaves, fixed to the world so
// it never swims. Nothing else is ever cut: a mesh without a second UV gets its first in its place (Unity's
// stand-in for a missing channel), and palette UVs lie between 0 and 1.
void OS_CardClip(float2 card, float3 positionWS)
{
    if (card.x < 0.999 || card.y < 0.999)
        return;
    float2 c = card - 1.0;
    float r = length(c - 0.5) * 2.0;
    float n = OS_Noise(c * 4.5 + positionWS.xz * 0.31) * 0.6 + OS_Noise(c * 10.0 - positionWS.y * 0.43) * 0.4;
    clip(1.0 - r + (n - 0.5) * 0.9 - 0.18);
}

// The weather's cloud layer, one pattern for the sky and for the shadows it casts on the town.
float4 _OS_Clouds;      // x cover (0 none, 1 overcast), y feature size (m), z softness, w layer height (m)
float4 _OS_CloudDrift;  // xy how far the wind has moved the layer (m), from the scene's clock
float _OS_CloudThrough;  // the share of the sun's light that comes through the cloud (the cloud kind's)

// The field drawn once into a map over the town (Overstory.Scenes.SunBeamsFeature, CloudMapPass) on the layer's own
// grid, which drifts with the wind: drawn again only when the camera or the wind carries the point it is read at a
// quarter of the way to its edge, so the shadows and the beams read one texel where they computed seven noises
TEXTURE2D(_OS_CloudMap);
SAMPLER(sampler_OS_CloudMap);
float4 _OS_CloudMapRect;  // xy the map's corner on the drifting layer (m), z 1 / its side (m), w its side in texels; 0 none

// Cloud density at a point on the drifting layer (world xz plus the wind's drift, metres), 0..1, before cover is
// applied. Shaped as a painter simplifies a sky: big billows (the field warped by a slower one), stretched along the
// wind so the layer reads as bands foreshortening to the horizon, a little finer detail at their edges. The same
// field casts the shadows.
float OS_CloudFieldOn(float2 drifted, float detail)
{
    float2 q = drifted / max(_OS_Clouds.y, 1.0);
    q = float2(dot(q, float2(0.906, 0.423)), dot(q, float2(-0.423, 0.906)) * 2.2);
    float2 w = float2(OS_Noise(q * 0.5 + 11.3), OS_Noise(q * 0.5 - 7.1)) - 0.5;
    q += w * 1.1;
    float c = 0.5 * OS_Noise(q) + 0.28 * OS_Noise(q * 2.07 + 5.3) + 0.14 * OS_Noise(q * 4.3 - 2.7) + 0.08 * OS_Noise(q * 8.9 + 1.3);
    return c + detail * (OS_Noise(q * 17.0 + 3.7) - 0.5) * 0.06;
}

// The same at a point on the layer (world xz, metres)
float OS_CloudField(float2 layerXZ, float detail)
{
    return OS_CloudFieldOn(layerXZ + _OS_CloudDrift.xy, detail);
}

// The field without its finest detail, from the map between texel centres where it reaches, computed where it does not
float OS_CloudFieldMapped(float2 layerXZ)
{
    float2 drifted = layerXZ + _OS_CloudDrift.xy;
    float2 uv = (drifted - _OS_CloudMapRect.xy) * _OS_CloudMapRect.z;
    float edge = 0.5 / max(_OS_CloudMapRect.w, 1.0);
    [branch]
    if (_OS_CloudMapRect.w > 0.0 && all(uv >= edge) && all(uv <= 1.0 - edge))
        return SAMPLE_TEXTURE2D_LOD(_OS_CloudMap, sampler_OS_CloudMap, uv, 0).r;
    return OS_CloudFieldOn(drifted, 0.0);
}

// How much cloud there is at a point on the layer, 0 clear to 1 cloud, with the rig's cover and softness.
half OS_CloudCover(float c, float extraSoft)
{
    float soft = _OS_Clouds.z + extraSoft;
    return (half)smoothstep(1.0 - _OS_Clouds.x - soft, 1.0 - _OS_Clouds.x + soft, c);
}

// The town's sky map (Overstory.Scenes.SkyMap): its height from above. The shade uses it for the sky each point
// sees (StreetLooks.hlsl, OS_TownSky); the fog for where land is under it.
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

// The town's glow (Overstory.Scenes.TownLights): its lamps and lit shops summed and spread on a map from above,
// so fog over lit streets glows from below
TEXTURE2D(_OS_GlowMap);
SAMPLER(sampler_OS_GlowMap);
float4 _OS_GlowRect;    // xy the map's corner (world x, z), z 1 / its size
float4 _OS_GlowParams;  // x strength (0 none), y how high the glow reaches into the fog (m)

// The fog as a bank: x 1 on, y its density over land against over water, z how strongly wisps break it, w their size (m)
float4 _OS_Bank;

// 1 over land or buildings, 0 over water, from the sky map; water where there is no map
float OS_LandUnder(float2 xz)
{
    if (_OS_SkyMapOn < 0.5)
        return 0.0;
    float2 uv = (xz - _OS_SkyMapRect.xy) * _OS_SkyMapRect.z;
    if (any(uv < 0.0) || any(uv > 1.0))
        return 0.0;
    uv.y = _OS_SkyMapRect.w > 0.5 ? 1.0 - uv.y : uv.y;
    float h = SAMPLE_TEXTURE2D_LOD(_OS_SkyMap, sampler_OS_SkyMap, uv, 0).r;
    return smoothstep(0.3, 2.0, h);
}

float3 OS_GlowAt(float3 p)
{
    float2 uv = (p.xz - _OS_GlowRect.xy) * _OS_GlowRect.z;
    if (_OS_GlowParams.x <= 0.0 || any(uv < 0.0) || any(uv > 1.0))
        return 0;
    return SAMPLE_TEXTURE2D_LOD(_OS_GlowMap, sampler_OS_GlowMap, uv, 0).rgb * (_OS_GlowParams.x * exp(-max(p.y - 4.0, 0.0) / max(_OS_GlowParams.y, 1.0)));
}

// The low haze's density at a point: thinning with height; as a bank, thicker over the water than the land, broken
// by slow wisps that the scene's clock moves
float OS_HazeDensity(float3 p)
{
    float base = _OS_Haze.x * exp(-max(p.y, 0.0) / max(_OS_Haze.y, 1.0));
    if (_OS_Bank.x < 0.5)
        return base;
    float2 q = p.xz / max(_OS_Bank.w, 1.0) + float2(0.013, 0.007) * _OS_Time;
    float wisp = 1.0 + _OS_Bank.z * ((OS_Noise(q) * 2.0 - 1.0) + 0.5 * (OS_Noise(q * 2.7 + 3.1) * 2.0 - 1.0));
    return base * lerp(1.0, _OS_Bank.y, OS_LandUnder(p.xz)) * max(wisp, 0.15);
}

// The haze along a ray: its optical depth, and the town's glow it scatters towards the camera
void OS_HazeMarch(float3 o, float3 dir, float dist, out float tau, out float3 glow)
{
    const int N = 12;
    tau = 0.0;
    glow = 0;
    float prev = 0.0;
    [loop]
    for (int i = 0; i < N; i++)
    {
        float f = (i + 0.5) / N;
        float s = dist * f * f;
        float ds = dist * ((i + 1.0) * (i + 1.0) - i * i) / (N * N);
        float3 p = o + dir * s;
        float sigma = OS_HazeDensity(p);
        glow += exp(-tau) * sigma * OS_GlowAt(p) * ds;
        tau += sigma * ds;
        prev = s;
    }
}

// The mean density along a straight path through air that thins exponentially with height (k per metre, from the
// base height), relative to the density at the base.
float OS_MeanDensity(float3 v, float k, float base)
{
    float a = exp(-k * (_WorldSpaceCameraPos.y - base));
    float kdh = k * v.y;
    return abs(kdh) > 1e-3 ? a * (1.0 - exp(-kdh)) / kdh : a;
}

// Aerial perspective and height fog: the air thickens with distance and thins with height, and glows
// towards the sun; a low haze lies on the water and thins quickly up the hill. Applied the same way to
// every look, to water and to emissive light. OS_HAZE_OFF (the harness's haze-off, docs/measuring.md, declared by
// each caller's pass) skips it: the surface as lit.
half3 OS_Atmosphere(half3 colour, float3 positionWS)
{
#if defined(OS_HAZE_OFF)
    return colour;
#else
    float3 v = positionWS - _WorldSpaceCameraPos;
    float d = length(v);
    float tauAir = _OS_FogParams.x * d * OS_MeanDensity(v, max(_OS_FogParams.y, 1e-4), _OS_FogParams.z);
    float tauHaze;
    float3 glow = 0;
    if (_OS_Bank.x > 0.5)
        OS_HazeMarch(_WorldSpaceCameraPos, v / max(d, 1e-4), min(d, 3000.0), tauHaze, glow);
    else
        tauHaze = _OS_Haze.x * d * OS_MeanDensity(v, 1.0 / max(_OS_Haze.y, 1.0), 0.0);
    float hidden = min(1.0 - exp(-(tauAir + tauHaze)), _OS_FogParams.w);
    if (_OS_AirBands > 0.5)
    {
        // distance laid in flat layers, each a step of air, the edges soft like a wiped block
        float hb = hidden * _OS_AirBands;
        float soft = _OS_AirBandSoft > 0.0 ? _OS_AirBandSoft : 0.2;
        hidden = (floor(hb) + smoothstep(1.0 - soft, 1.0, frac(hb))) / _OS_AirBands;
    }
    half sun = pow(saturate(dot(v / max(d, 1e-4), _OS_SunDir.xyz)), max(_OS_FogSun.w, 1.0));
    // the air changes colour with distance, in layers, never one grey (Firewatch, Sable)
    // a designed ramp, as Firewatch's fog: near, middle and far each the colour the hour gives them
    half3 air = lerp(_OS_FogColor.rgb, _OS_FogMid.rgb, smoothstep(0.0, max(_OS_FogMid.a, 1.0), d));
    air = lerp(air, _OS_FogFar.rgb, smoothstep(_OS_FogMid.a, max(_OS_FogFar.a, _OS_FogMid.a + 1.0), d));
    air = lerp(air, _OS_HazeColor.rgb, tauHaze / max(tauAir + tauHaze, 1e-5)) + _OS_FogSun.rgb * sun;
    return lerp(colour, air, hidden) + glow;
#endif
}

#endif
