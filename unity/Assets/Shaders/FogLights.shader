// The town's lamps lit in the air round them: each lamp scatters its light into the fog and haze between the camera
// and whatever stands behind, so in sea fog every lamp wears a halo, and in clear air hardly one. After the opaque
// scene and before post-processing, so the glow blooms with the lamps themselves.
//
// For a point light in air of even density, the light scattered towards the camera along a ray is
//     I sigma / h * integral over theta of phase(theta) * T(theta) d theta,
// with h the lamp's distance from the ray, s0 where along the ray it comes closest, and each point of the ray written
// as s = s0 + h tan(theta), so the 1 / distance^2 of the lamp's light cancels into the change of variable and the rest
// is smooth: the integral is taken with a few samples of theta from the camera to the surface. Fog droplets throw
// light forward (Henyey-Greenstein, g about 0.85), so a lamp's halo is tight and bright looking into it and faint from
// the side, as in a real fog; T is what the air takes from the lamp to the point and from the point to the camera.
// The air's density is taken at the lamp's height (the same height fog and low haze as OS_Atmosphere). Lamps come
// from Overstory.Scenes.TownLights, culled to the view each frame (only those whose reach meets it).
//
// At a quarter of the pixels (FogLightsFeature), as the sun's beams are:
//   0 March      at half the width and half the height: each half-size pixel takes the halos for one of its four
//                full-size pixels, the nearest on one checkerboard colour and the farthest on the other, so both
//                sides of an edge are taken nearby; it keeps the ray's length beside the light;
//   1 Composite  at full size, added onto the frame (no copy of it): the four half-size neighbours by bilinear weight
//                and by how near each one's ray length is to this pixel's; where none is near, the nearest one alone.
Shader "Overstory/FogLights"
{
    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" }
        ZWrite Off
        ZTest Always
        Cull Off

        HLSLINCLUDE
        #pragma target 4.5
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
        #include "Packages/com.unity.render-pipelines.core/Runtime/Utilities/Blit.hlsl"
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareDepthTexture.hlsl"

        float4 _OS_FogSize;        // xy the frame's size in pixels, zw the half-size target's
        TEXTURE2D(_OS_FogTex);     // the half-size halos: rgb their light, a the ray's length (m)

        // a full-size pixel's ray: its way and its length, to its surface or far past every lamp for the sky
        float RayLength(uint2 px, float raw, out float3 dir)
        {
            float2 uv = (px + 0.5) / _OS_FogSize.xy;
        #if UNITY_REVERSED_Z
            bool sky = raw <= 1e-6;
        #else
            bool sky = raw >= 1.0 - 1e-6;
        #endif
            float3 ray = ComputeWorldSpacePosition(uv, raw, UNITY_MATRIX_I_VP) - _WorldSpaceCameraPos;
            float len = length(ray);
            dir = ray / max(len, 1e-4);
            return sky ? 4000.0 : len;
        }

        // how far two rays' lengths may differ and still share a halo: none past 30%, nearly full under 5%
        float LengthWeight(float a, float b)
        {
            float rel = abs(a - b) / max(min(a, b), 0.25);
            return saturate(1.0 - (rel * rel) / 0.09);
        }
        ENDHLSL

        Pass
        {
            Name "March"

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag

            StructuredBuffer<float4> _OS_FogLampPos;     // xyz world position, w reach (m): past it a lamp adds nothing
            StructuredBuffer<float4> _OS_FogLampColour;  // rgb its light (linear, intensity in), w unused
            int _OS_FogLampCount;                        // the lamps in view, first in the buffers
            float _OS_FogLampStrength;                   // the rig's halo strength; 0 turns the pass off
            #include "StreetSurface.hlsl"                // the air: its height fog and the haze or bank

            float AirDensity(float3 p)
            {
                return _OS_FogParams.x * exp(-max(_OS_FogParams.y, 1e-4) * (p.y - _OS_FogParams.z)) + OS_HazeDensity(p);
            }

            float4 Frag(Varyings input) : SV_Target
            {
                uint2 lo = (uint2)input.positionCS.xy;
                uint2 last = (uint2)_OS_FogSize.xy - 1;
                // the full-size pixel this one is for: the nearest of its four on one checkerboard colour, the farthest
                // on the other
                bool nearest = ((lo.x + lo.y) & 1u) == 0u;
                uint2 px = min(lo * 2u, last);
                float raw = LoadSceneDepth(px);
                [unroll]
                for (uint k = 1u; k < 4u; k++)
                {
                    uint2 q = min(lo * 2u + uint2(k & 1u, k >> 1u), last);
                    float d = LoadSceneDepth(q);
                #if UNITY_REVERSED_Z
                    bool nearer = d > raw;
                #else
                    bool nearer = d < raw;
                #endif
                    if (nearer == nearest && d != raw)
                    {
                        raw = d;
                        px = q;
                    }
                }
                float3 v;
                float t = RayLength(px, raw, v);
                float3 o = _WorldSpaceCameraPos;

                float3 sum = 0;
                [loop]
                for (int i = 0; i < _OS_FogLampCount; i++)
                {
                    float4 lp = _OS_FogLampPos[i];
                    float3 d = lp.xyz - o;
                    float s0 = dot(d, v);
                    float h2 = max(dot(d, d) - s0 * s0, 0.0225); // no closer than 15 cm: the lamp's own glass
                    float h = sqrt(h2);
                    if (h > lp.w || s0 < -lp.w)
                        continue;
                    float sigma = AirDensity(lp.xyz);
                    float a0 = atan(-s0 / h), a1 = atan((t - s0) / h);
                    const int N = 10;
                    const float g = 0.85, g2 = g * g;
                    float da = (a1 - a0) / N, acc = 0.0;
                    [unroll]
                    for (int k = 0; k < N; k++)
                    {
                        float a = a0 + (k + 0.5) * da;
                        float sa, ca;
                        sincos(a, sa, ca);
                        float s = s0 + h * sa / ca;          // along the ray
                        float r = h / ca;                    // from the lamp
                        float mu = -sa;                      // the light's way on against the way to the camera
                        float hg = (1.0 - g2) / pow(max(1.0 + g2 - 2.0 * g * mu, 1e-4), 1.5);
                        float phase = (0.08 + 0.92 * hg) / (4.0 * PI);
                        acc += phase * exp(-sigma * (s + r));
                    }
                    // soft edge at the reach, so no lamp's glow ends in a line
                    float edge = saturate(1.0 - h / lp.w);
                    sum += _OS_FogLampColour[i].rgb * (sigma / h * acc * da * edge * edge);

                    // light scattered many times on its way to the camera: the lamp's glow spreads wider and dimmer the
                    // more fog lies between, a halo that grows with distance (the air's point-spread)
                    float dl = length(d);
                    if (t > dl - 1.0)
                    {
                        float tau = sigma * dl;
                        float w = 0.012 + 0.09 * min(tau, 3.0);                 // its angular width, radians
                        float theta = acos(clamp(dot(v, d / dl), -1.0, 1.0));
                        float spread = exp(-theta * theta / (2.0 * w * w)) / (2.0 * PI * w * w);
                        sum += _OS_FogLampColour[i].rgb * ((1.0 - exp(-tau)) * exp(-0.35 * tau) * spread / (dl * dl) * 0.35);
                    }
                }
                return float4(sum * _OS_FogLampStrength, t);
            }
            ENDHLSL
        }

        Pass
        {
            Name "Composite"
            Blend One One

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag

            half4 Frag(Varyings input) : SV_Target
            {
                uint2 px = (uint2)input.positionCS.xy;
                float3 v;
                float t = RayLength(px, LoadSceneDepth(px), v);

                // the four half-size neighbours round this pixel's centre
                float2 at = (px + 0.5) * 0.5 - 0.5;
                int2 i0 = (int2)floor(at);
                float2 fr = at - i0;
                int2 last = (int2)_OS_FogSize.zw - 1;
                float3 sum = 0, nearest = 0;
                float weight = 0.0, gap = 1e9;
                [unroll]
                for (int k = 0; k < 4; k++)
                {
                    int2 o = int2(k & 1, k >> 1);
                    float4 s = LOAD_TEXTURE2D(_OS_FogTex, clamp(i0 + o, 0, last));
                    float2 b = lerp(1.0 - fr, fr, (float2)o);
                    float w = b.x * b.y * LengthWeight(s.a, t);
                    sum += s.rgb * w;
                    weight += w;
                    float d = abs(s.a - t);
                    if (d < gap)
                    {
                        gap = d;
                        nearest = s.rgb;
                    }
                }
                return half4(weight > 1e-3 ? sum / weight : nearest, 0.0);
            }
            ENDHLSL
        }
    }
}
