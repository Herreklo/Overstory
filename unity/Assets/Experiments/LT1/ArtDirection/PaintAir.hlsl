// The painted corner's air (PaintAir.shader), one body for both its passes: the still's (LT1ArtPasses.Paint, the frame
// as _MainTex) and the scene's (PaintAirPass, the frame as _BlitTexture). The pass defines how the frame and the
// distance pass are read before it includes this:
//     P_COLOUR(uv)     the surfaces' colour
//     P_DIST(uv)       the distance pass (PaintSurface.shader, _P_Mode 1): r the distance times the coverage, g the
//                      coverage, b the veil times the coverage
//     P_DIST_LOD(uv)   the same, at its top level, from inside a loop
// Every value is a global from Paint.json, or the camera's (the still's material, the scene's property block).
#ifndef OS_PAINT_AIR_INCLUDED
#define OS_PAINT_AIR_INCLUDED

#include "Paint.hlsl"

float4 _P_Dist_TexelSize;
float4 _P_Rim;                                          // x strength, y the band (share of the frame's height), z the sky it mirrors (elevation, deg), w the gap behind (m)
float4 _P_ContactB;                                     // x the least angle (cosine) that counts: a board's lap is no junction
float4 _P_Contact;                                      // x strength, y the reach (m), z the curve, w the most the reach may span (share of the frame's height)
float _P_ContactTurns;                                  // 4: each pixel averages the pattern's four turns (the scene, drawn at 1x); else each pixel of a 2x2 block takes one (the still, averaged by its 2x downsample)
float4 _P_CamPos, _P_CamFwd, _P_CamRight, _P_CamUp;     // right and up scaled by the half view's tangent
float4 _P_FogD, _P_FogW, _P_FogA;
float4 _P_Grade;                                        // x vignette, y exposure, z the shoulder's start
float4 _P_HaloShape;                                    // x the wide part's share, y the depth margin (m)
float4 _P_LampPos[8];                                   // xyz the head (world), w the core's radius (m)
float4 _P_LampHalo[8];                                  // rgb its light, w the wide part's radius (m)
float _P_LampCount;

float P_Step(float d, float at, float w)
{
    return smoothstep(at - w, at + w, d);
}

float3 P_Shoulder(float3 x, float k)
{
    float3 over = max(x - k, 0.0);
    float s = max(1.0 - k, 1e-3);
    return min(x, k) + s * (1.0 - exp(-over / s));
}

// the point a pixel of the distance pass sees (world), and whether anything stands there
float3 P_PointAt(float2 q, out float there)
{
    float3 o = P_DIST_LOD(q).rgb;
    float oc = saturate(o.y);
    there = oc > 0.5 ? 1.0 : 0.0;
    float od = oc > 1e-3 ? o.x / oc : 1e4;
    float3 dr = normalize(_P_CamFwd.xyz + (q.x * 2.0 - 1.0) * _P_CamRight.xyz + (q.y * 2.0 - 1.0) * _P_CamUp.xyz);
    return _P_CamPos.xyz + dr * od;
}

// one turn of the contact pattern (ip: which quarter turn)
float P_ContactTurn(float2 uv, float3 P, float3 n, float2 span, float R, int2 ip)
{
    float turn = (ip.x + 2 * ip.y) * 1.5708 + 0.39;
    float sum = 0.0;
    const int N = 12;
    [unroll] for (int j = 0; j < N; j++)
    {
        float a = j * 2.39996 + turn;
        float r = (j + 0.5 + 0.25 * (ip.x + 2 * ip.y)) / (N + 1.0);
        float2 q = uv + float2(cos(a), sin(a)) * span * r;
        float ok;
        float3 S = P_PointAt(q, ok);
        float3 v = S - P;
        float vv = dot(v, v);
        float o = saturate(dot(v, n) * rsqrt(max(vv, 1e-8)) - _P_ContactB.x) * saturate(1.0 - vv / (R * R));
        sum += o * ok;
    }
    float ao = saturate(1.0 - _P_Contact.x * 2.0 * sum / N);
    return pow(ao, max(_P_Contact.z, 0.1));
}

// contact shade: how much of the open half round a point the things beside it close off, within a short
// reach (m), so every junction (a wall's foot, under a coping's lip, a riser's back) takes a little shade.
// Each pixel of a 2x2 block turns the pattern a quarter, and the still's 2x downsample averages them: no noise.
// The scene, drawn at 1x, averages the four turns in each pixel instead (_P_ContactTurns 4).
float P_Contact(float2 uv, float d, float2 pix)
{
    float there;
    float3 P = P_PointAt(uv, there);
    float2 px = _P_Dist_TexelSize.xy;
    float t0, t1, t2, t3;
    float3 Pr = P_PointAt(uv + float2(px.x, 0), t0), Pl = P_PointAt(uv - float2(px.x, 0), t1);
    float3 Pu = P_PointAt(uv + float2(0, px.y), t2), Pd = P_PointAt(uv - float2(0, px.y), t3);
    float3 dx = dot(Pr - P, Pr - P) < dot(P - Pl, P - Pl) ? Pr - P : P - Pl;
    float3 dy = dot(Pu - P, Pu - P) < dot(P - Pd, P - Pd) ? Pu - P : P - Pd;
    float3 n = normalize(cross(dx, dy) + 1e-7);
    if (dot(n, _P_CamPos.xyz - P) < 0.0)
        n = -n;
    float R = _P_Contact.y;
    float tanX = length(_P_CamRight.xyz), tanY = length(_P_CamUp.xyz);
    float2 span = float2(1.0 / (2.0 * tanX), 1.0 / (2.0 * tanY)) * (R / max(d, 0.1));
    span *= min(1.0, _P_Contact.w / max(span.y, 1e-6));
    if (_P_ContactTurns > 1.5)
        return 0.25 * (P_ContactTurn(uv, P, n, span, R, int2(0, 0)) + P_ContactTurn(uv, P, n, span, R, int2(1, 0))
                     + P_ContactTurn(uv, P, n, span, R, int2(0, 1)) + P_ContactTurn(uv, P, n, span, R, int2(1, 1)));
    return P_ContactTurn(uv, P, n, span, R, int2(pix) & 1);
}

float4 P_Air(float2 uv, float2 pix)
{
    float3 colour = P_COLOUR(uv).rgb;
    float3 dc = P_DIST(uv).rgb;
    float c = saturate(dc.y);
    float d = c > 1e-3 ? dc.x / c : 0.0;
    float veil = c > 1e-3 ? dc.z / c : 1.0;
    float3 dir = normalize(_P_CamFwd.xyz + (uv.x * 2.0 - 1.0) * _P_CamRight.xyz + (uv.y * 2.0 - 1.0) * _P_CamUp.xyz);

    // the sky where nothing stands; the fog's layers over what does
    float3 sky = P_Sky(dir);
    float3 surf = c > 1e-3 ? colour / c : 0.0;
    if (c > 0.5 && _P_Contact.x > 0.0)
        surf *= P_Contact(uv, d, pix);
    float a = _P_FogA.x + veil * (
          (_P_FogA.y - _P_FogA.x) * P_Step(d, _P_FogD.x, _P_FogW.x)
        + (_P_FogA.z - _P_FogA.y) * P_Step(d, _P_FogD.y, _P_FogW.y)
        + (_P_FogA.w - _P_FogA.z) * P_Step(d, _P_FogD.z, _P_FogW.z));
    // the near curtain's top edges found: a wet arris mirrors the bright band of the sky over the fog where
    // the curtain meets something behind it (the clay has no arris; the edge is drawn where it stands)
    if (c > 0.5 && veil < 0.05 && _P_Rim.x > 0.0)
    {
        float band = _P_Rim.y;
        float found = 0.0;
        [unroll] for (int j = 1; j <= 8; j++)
        {
            float2 q = uv + float2(0.0, band * j / 8.0);
            float3 o = P_DIST_LOD(q).rgb;
            float oc = saturate(o.y);
            float od = oc > 1e-3 ? o.x / oc : 1e4;
            float ov = oc > 1e-3 ? o.z / oc : 1.0;
            bool behind = oc < 0.5 || (ov > 0.05 && od > d + _P_Rim.w);
            if (behind && found == 0.0)
                found = 1.0 - (j - 1.0) / 8.0;
        }
        float3 flat = normalize(float3(dir.x, 0.0, dir.z) + 1e-5);
        float e = radians(_P_Rim.z);
        float3 rd = normalize(flat * cos(e) + float3(0.0, sin(e), 0.0));
        surf += P_Sky(rd) * (_P_Rim.x * found * found);
    }
    float3 fogged = lerp(surf, P_Fog(dir), saturate(a));
    float3 result = c * fogged + (1.0 - c) * sky;

    // each lamp's halo: a tight core and a little of a wider glow, hidden by what stands before the head
    float3 halo = 0.0;
    for (int k = 0; k < (int)_P_LampCount; k++)
    {
        float3 L = _P_LampPos[k].xyz - _P_CamPos.xyz;
        float ld = length(L);
        float t = dot(L, dir);
        if (t <= 0.0)
            continue;
        float x = length(L - t * dir);
        float m = max(_P_HaloShape.y, 0.05);
        float vis = lerp(1.0, saturate((d - ld + m) / m), c);
        float core = max(_P_LampPos[k].w, 1e-3), wide = max(_P_LampHalo[k].w, 1e-3);
        float g = exp(-(x * x) / (core * core)) + _P_HaloShape.x * exp(-(x * x) / (wide * wide));
        halo += _P_LampHalo[k].rgb * (g * vis);
    }
    result += halo;

    result *= _P_Grade.y;
    result = P_Shoulder(result, _P_Grade.z);
    float2 q = (uv - 0.5) * 2.0;
    result *= 1.0 - _P_Grade.x * saturate(dot(q, q) * 0.5);
    return float4(result, 1.0);
}

#endif
