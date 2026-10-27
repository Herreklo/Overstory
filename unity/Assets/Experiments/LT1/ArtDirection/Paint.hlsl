// The painted corner's shared terms (Paint.json, LT1ArtPasses.Paint): the designed sky and the lit fog in it, read by
// the surfaces (what a wet face mirrors) and by the air (the sky itself, the fog's colour). Every value is a global
// set from Paint.json; nothing here holds a look value of its own.
#ifndef OS_PAINT_INCLUDED
#define OS_PAINT_INCLUDED

float4 _P_SkyZenith;    // rgb linear
float4 _P_SkyHorizon;
float4 _P_SkyShape;     // x the gradient's curve, y the height (sine) under which the sky is all horizon: the fog bank's top
float4 _P_Glow;         // rgb, w its strength in the sky
float4 _P_GlowDir;      // xyz unit (world)
float4 _P_GlowShape;    // x half width (rad), y up, z down, w its share in the fog
float4 _P_FogColour;

// How much of the lit fog's glow lies along a direction (unit, world): a lobe round its direction, wide sideways,
// tight above, looser below.
half P_GlowAt(float3 d)
{
    float3 g = _P_GlowDir.xyz;
    float az = atan2(d.x, d.z) - atan2(g.x, g.z);
    az = az - 6.2831853 * round(az / 6.2831853);
    float el = asin(clamp(d.y, -1.0, 1.0)) - asin(clamp(g.y, -1.0, 1.0));
    float w = max(_P_GlowShape.x, 1e-3);
    float h = el > 0.0 ? max(_P_GlowShape.y, 1e-3) : max(_P_GlowShape.z, 1e-3);
    return (half)exp(-(az * az) / (w * w) - (el * el) / (h * h));
}

// The sky along a direction: horizon to zenith on its curve, the lit fog's glow over it.
half3 P_Sky(float3 d)
{
    float t = pow(saturate((d.y - _P_SkyShape.y) / max(1.0 - _P_SkyShape.y, 1e-3)), max(_P_SkyShape.x, 0.05));
    half3 c = (half3)lerp(_P_SkyHorizon.rgb, _P_SkyZenith.rgb, t);
    return lerp(c, (half3)_P_Glow.rgb, saturate(P_GlowAt(d) * (half)_P_Glow.w));
}

// The fog's colour seen along a direction: the hour's colour, warmed where the glow lies behind it.
half3 P_Fog(float3 d)
{
    return lerp((half3)_P_FogColour.rgb, (half3)_P_Glow.rgb, saturate(P_GlowAt(d) * (half)(_P_Glow.w * _P_GlowShape.w)));
}

#endif
