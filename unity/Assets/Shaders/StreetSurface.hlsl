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
float4 _OS_FogColor;     // rgb: the colour of the air (linear)
float4 _OS_FogParams;    // x density per metre at the base height, y falloff per metre of height, z base height, w most it may hide
float4 _OS_FogSun;       // rgb: extra colour towards the sun (linear), w: how tight that glow is
float4 _OS_SunDir;       // xyz: towards the sun
float4 _OS_PavingMeanUV; // xy: the palette UV of setts_mean, the tone a sett pavement averages to

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

    // Once a pixel covers more than a stone, a sett pavement is seen as one tone: its stones, joints
    // and bevels average out as a lens would average them, instead of breaking into speckle.
    float footprint = max(length(ddx(positionWS)), length(ddy(positionWS)));
    half far = saturate((footprint - 0.015) / 0.045) * step(0.75h, paving);
    albedo = lerp(albedo, SAMPLE_TEXTURE2D(_OS_Albedo, sampler_PointClamp, _OS_PavingMeanUV.xy).rgb, far);
    n = normalize(lerp(n, half3(0, 1, 0), far));

    // Rain wets what faces the sky; walls a little, undersides (eaves, soffits) not at all. Porous
    // stone darkens and stays matt; glazed tile and paint shed it and shine.
    half up = n.y;
    half wet = _OS_Wetness * saturate((up + 0.1h) / 0.6h);
    albedo *= lerp(1.0h, 1.0h - 0.5h * porosity, wet);
    smoothness = lerp(smoothness, max(smoothness, lerp(0.85h, 0.45h, porosity)), wet);

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
    return s;
}

// Aerial perspective and height fog: the air thickens with distance and thins with height, and glows
// towards the sun. Applied the same way to every look, to water and to emissive light.
half3 OS_Atmosphere(half3 colour, float3 positionWS)
{
    float3 v = positionWS - _WorldSpaceCameraPos;
    float d = length(v);
    float k = max(_OS_FogParams.y, 1e-4);
    float a = exp(-k * (_WorldSpaceCameraPos.y - _OS_FogParams.z));
    float kdh = k * v.y;
    float meanDensity = abs(kdh) > 1e-3 ? a * (1.0 - exp(-kdh)) / kdh : a;
    float hidden = min(1.0 - exp(-_OS_FogParams.x * d * meanDensity), _OS_FogParams.w);
    half sun = pow(saturate(dot(v / max(d, 1e-4), _OS_SunDir.xyz)), max(_OS_FogSun.w, 1.0));
    half3 air = _OS_FogColor.rgb + _OS_FogSun.rgb * sun;
    return lerp(colour, air, hidden);
}

#endif
