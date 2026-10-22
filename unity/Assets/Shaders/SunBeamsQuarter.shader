// Shafts of sun in the haze at a quarter of the pixels (W5; docs/research/performance-craft.md, item 1). The same
// light as SunBeams.shader, which stays as the full-size reference (SunBeamsFeature.fullSize): for each view ray the air
// is marched, and at each step the sun's shadow map says whether sunlight reaches that point; lit air scatters the
// sun's light towards the camera, shadowed air does not. Only the cost changes:
//   0 CloudMap   the cloud layer's field once into a small map over the town (512², 8 m a texel on a fixed world grid,
//                drawn again only when its square or the clouds change), so a step reads one texel, not seven noises;
//   1 March      at half the width and half the height: 16 steps a ray, one hard shadow tap a step (the softness comes
//                from the march and the blur, not from a filter at every step), each pixel's steps offset by a 4×4
//                ordered pattern; each half-size pixel marches through one of its four full-size pixels, the nearest on
//                one checkerboard colour and the farthest on the other, so both sides of an edge are marched nearby;
//   2, 3 Blur    across, then down, five taps [1 2 2 2 1]/8: every 4×4 tile of the pattern weighs each of its 16 offsets
//                the same, so the march acts as 256 stratified steps and the pattern cancels exactly where the ray's
//                length is smooth; taps weighed down by how much the ray's length differs, so no beam crosses an edge;
//   4 Composite  at full size, added onto the frame (no copy of it): the four half-size neighbours by bilinear weight
//                and by how near each one's ray length is to this pixel's; where none is near (a thin pole against the
//                sky), the nearest one alone. The phase is evaluated here, per full-size pixel.
// The pattern is fixed to the screen and the same every frame: nothing here changes with time, so a still camera draws
// a still image (no temporal accumulation, which this pipeline has none of).
Shader "Overstory/SunBeamsQuarter"
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

        float4 _OS_BeamSize;     // xy the frame's size in pixels, zw the half-size target's
        TEXTURE2D(_OS_BeamTex);  // the half-size beams: r the in-scattered light (before phase, colour and strength), g the ray's length (m)

        // the march's length for a full-size pixel: to its surface, or the march's reach for the sky and anything past it
        float RayLength(uint2 px, float raw, float reach, out float3 dir)
        {
            float2 uv = (px + 0.5) / _OS_BeamSize.xy;
        #if UNITY_REVERSED_Z
            bool sky = raw <= 1e-6;
        #else
            bool sky = raw >= 1.0 - 1e-6;
        #endif
            float3 ray = ComputeWorldSpacePosition(uv, raw, UNITY_MATRIX_I_VP) - _WorldSpaceCameraPos;
            float len = length(ray);
            dir = ray / max(len, 1e-4);
            return sky ? reach : min(len, reach);
        }

        // how far two rays' lengths may differ and still share a beam: none past 30%, nearly full under 5%
        float LengthWeight(float a, float b)
        {
            float rel = abs(a - b) / max(min(a, b), 0.25);
            return saturate(1.0 - (rel * rel) / 0.09);
        }
        ENDHLSL

        Pass
        {
            Name "CloudMap"

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "StreetSurface.hlsl"   // the cloud layer

            float4 _OS_CloudMapRect;   // xy the map's corner on the layer (world x, z), z 1 / its side (m), w its side in texels

            float Frag(Varyings input) : SV_Target
            {
                float texel = 1.0 / (_OS_CloudMapRect.z * _OS_CloudMapRect.w);
                return OS_CloudField(_OS_CloudMapRect.xy + input.positionCS.xy * texel, 0.0);
            }
            ENDHLSL
        }

        Pass
        {
            Name "March"

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE
            // no _SHADOWS_SOFT*: one hard tap a step (the hardware's 2×2 compare), not the 16-tap filter
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Shadows.hlsl"
            #include "StreetSurface.hlsl"   // the air's parameters, the cloud layer

            float4 _OS_SunBeams;       // x strength (0 off), y how far the march reaches (m), z forward scattering g, w beam haze
            float4 _OS_CloudMapRect;   // xy the map's corner on the layer (world x, z), z 1 / its side (m), w its side in texels; 0 no map
            TEXTURE2D(_OS_CloudMap);

            float AirDensity(float3 p)
            {
                return _OS_FogParams.x * exp(-max(_OS_FogParams.y, 1e-4) * (p.y - _OS_FogParams.z)) + OS_HazeDensity(p);
            }

            // how much sun reaches a point through the cloud layer (the same pattern whose shadows lie on the town), from
            // the point's place on the layer q: the field from the map between texel centres, computed where the map does
            // not reach (rays high over the town)
            float CloudLight(float2 q)
            {
                float2 uv = (q - _OS_CloudMapRect.xy) * _OS_CloudMapRect.z;
                float edge = 0.5 / max(_OS_CloudMapRect.w, 1.0);
                float c;
                [branch]
                if (_OS_CloudMapRect.w > 0.0 && all(uv >= edge) && all(uv <= 1.0 - edge))
                    c = SAMPLE_TEXTURE2D_LOD(_OS_CloudMap, sampler_LinearClamp, uv, 0).r;
                else
                    c = OS_CloudField(q, 0.0);
                return lerp(1.0, 0.12, OS_CloudCover(c, 0.0));
            }

            // The sun's shadow along a straight ray o + v s. A directional light's shadow coordinate is affine in s, so
            // each cascade's start and slope are found once a ray, and so is each cascade sphere's distance as a
            // quadratic in s; a step then picks its cascade (the first sphere it is inside, as URP's ComputeCascadeIndex)
            // and takes one hard tap, with no matrix and no square root a step.
            struct ShadowRay
            {
                float3 c0[4];
                float3 dc[4];
                float4 a, b;   // |o - centre|², 2 v·(o - centre), a sphere each
            };

            ShadowRay StartShadowRay(float3 o, float3 v)
            {
                ShadowRay r;
                float4 centre[4] = { _CascadeShadowSplitSpheres0, _CascadeShadowSplitSpheres1, _CascadeShadowSplitSpheres2, _CascadeShadowSplitSpheres3 };
                [unroll]
                for (int k = 0; k < 4; k++)
                {
                    r.c0[k] = mul(_MainLightWorldToShadow[k], float4(o, 1.0)).xyz;
                    r.dc[k] = mul((float3x3)_MainLightWorldToShadow[k], v);
                    float3 oc = o - centre[k].xyz;
                    r.a[k] = dot(oc, oc);
                    r.b[k] = 2.0 * dot(v, oc);
                }
                return r;
            }

            float ShadowAt(ShadowRay r, float s)
            {
            #if defined(_MAIN_LIGHT_SHADOWS_CASCADE)
                bool4 inside = (r.a + s * (r.b + s)) < _CascadeShadowSplitSphereRadii;
                float3 c = inside.x ? r.c0[0] + r.dc[0] * s
                         : inside.y ? r.c0[1] + r.dc[1] * s
                         : inside.z ? r.c0[2] + r.dc[2] * s
                         : inside.w ? r.c0[3] + r.dc[3] * s
                         : float3(0.0, 0.0, -1.0);   // past the last cascade: lit, as URP's no-op matrix
            #else
                float3 c = r.c0[0] + r.dc[0] * s;
            #endif
                return MainLightRealtimeShadow(float4(c, 0.0));
            }

            static const float Bayer[16] = { 0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5 };

            float2 Frag(Varyings input) : SV_Target
            {
                uint2 lo = (uint2)input.positionCS.xy;
                uint2 last = (uint2)_OS_BeamSize.xy - 1;
                // the full-size pixel this one marches for: the nearest of its four on one checkerboard colour, the
                // farthest on the other
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
                float t = RayLength(px, raw, _OS_SunBeams.y, v);
                float3 o = _WorldSpaceCameraPos;
                float3 toSun = _OS_SunDir.xyz;
                ShadowRay shadow = StartShadowRay(o, v);
                // the ray's place on the cloud layer, along the sun from each point: also affine in s
                bool clouds = _OS_Clouds.x > 0.001;
                float2 sunRun = toSun.xz / max(toSun.y, 0.05);
                float2 q0 = o.xz + sunRun * (_OS_Clouds.w - o.y);
                float2 dq = v.xz - sunRun * v.y;

                // 16 steps over [0, t], spaced closer near the camera (s = t f²), each at its own offset in its stretch
                const int N = 16;
                float jitter = (Bayer[(lo.y & 3u) * 4u + (lo.x & 3u)] + 0.5) / 16.0;
                float sum = 0.0, depth = 0.0;
                [loop]
                for (int i = 0; i < N; i++)
                {
                    float f = (i + jitter) / N;
                    float s = t * f * f;
                    float ds = t * (2.0 * i + 1.0) / (N * N);
                    float sigma = AirDensity(o + v * s);
                    float lit = ShadowAt(shadow, s);
                    if (clouds)
                        lit *= CloudLight(q0 + dq * s);
                    depth += sigma * ds;
                    // what the air scatters for beams can be more than what it hides: a set is hazed for the light
                    sum += exp(-depth) * sigma * _OS_SunBeams.w * lit * ds;
                }
                return float2(sum, t);
            }
            ENDHLSL
        }

        Pass
        {
            Name "BlurAcross"

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag

            float2 Frag(Varyings input) : SV_Target
            {
                int2 p = (int2)input.positionCS.xy;
                int2 last = (int2)_OS_BeamSize.zw - 1;
                float2 c = LOAD_TEXTURE2D(_OS_BeamTex, p).rg;
                float sum = 0.0, weight = 0.0;
                [unroll]
                for (int k = -2; k <= 2; k++)
                {
                    float2 s = LOAD_TEXTURE2D(_OS_BeamTex, clamp(p + int2(k, 0), 0, last)).rg;
                    float w = (abs(k) == 2 ? 1.0 : 2.0) * LengthWeight(s.g, c.g);
                    sum += s.r * w;
                    weight += w;
                }
                return float2(sum / weight, c.g);
            }
            ENDHLSL
        }

        Pass
        {
            Name "BlurDown"

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag

            float2 Frag(Varyings input) : SV_Target
            {
                int2 p = (int2)input.positionCS.xy;
                int2 last = (int2)_OS_BeamSize.zw - 1;
                float2 c = LOAD_TEXTURE2D(_OS_BeamTex, p).rg;
                float sum = 0.0, weight = 0.0;
                [unroll]
                for (int k = -2; k <= 2; k++)
                {
                    float2 s = LOAD_TEXTURE2D(_OS_BeamTex, clamp(p + int2(0, k), 0, last)).rg;
                    float w = (abs(k) == 2 ? 1.0 : 2.0) * LengthWeight(s.g, c.g);
                    sum += s.r * w;
                    weight += w;
                }
                return float2(sum / weight, c.g);
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

            float4 _OS_SunBeams;   // x strength (0 off), y how far the march reaches (m), z forward scattering g, w beam haze
            float4 _OS_SunCol;     // the sun's light (linear, intensity in)
            float4 _OS_SunDir;     // xyz: towards the sun

            half4 Frag(Varyings input) : SV_Target
            {
                uint2 px = (uint2)input.positionCS.xy;
                float3 v;
                float t = RayLength(px, LoadSceneDepth(px), _OS_SunBeams.y, v);

                // the four half-size neighbours round this pixel's centre
                float2 at = (px + 0.5) * 0.5 - 0.5;
                int2 i0 = (int2)floor(at);
                float2 fr = at - i0;
                int2 last = (int2)_OS_BeamSize.zw - 1;
                float sum = 0.0, weight = 0.0, nearest = 0.0, gap = 1e9;
                [unroll]
                for (int k = 0; k < 4; k++)
                {
                    int2 o = int2(k & 1, k >> 1);
                    float2 s = LOAD_TEXTURE2D(_OS_BeamTex, clamp(i0 + o, 0, last)).rg;
                    float2 b = lerp(1.0 - fr, fr, (float2)o);
                    float w = b.x * b.y * LengthWeight(s.g, t);
                    sum += s.r * w;
                    weight += w;
                    float d = abs(s.g - t);
                    if (d < gap)
                    {
                        gap = d;
                        nearest = s.r;
                    }
                }
                float scatter = weight > 1e-3 ? sum / weight : nearest;

                float mu = dot(v, _OS_SunDir.xyz);
                float g = _OS_SunBeams.z, g2 = g * g;
                float hg = (1.0 - g2) / pow(max(1.0 + g2 - 2.0 * g * mu, 1e-4), 1.5);
                float phase = (0.25 + 0.75 * hg) / (4.0 * PI);
                return half4(_OS_SunCol.rgb * (scatter * phase * _OS_SunBeams.x), 0.0);
            }
            ENDHLSL
        }
        // (the A/B arm "copy": the same composite over a copy of the frame, written whole)
        Pass
        {
            Name "CompositeOver"

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag

            float4 _OS_SunBeams;   // x strength (0 off), y how far the march reaches (m), z forward scattering g, w beam haze
            float4 _OS_SunCol;     // the sun's light (linear, intensity in)
            float4 _OS_SunDir;     // xyz: towards the sun

            TEXTURE2D(_OS_FrameTex);

            half4 Frag(Varyings input) : SV_Target
            {
                uint2 px = (uint2)input.positionCS.xy;
                half4 frame = LOAD_TEXTURE2D(_OS_FrameTex, px);
                float3 v;
                float t = RayLength(px, LoadSceneDepth(px), _OS_SunBeams.y, v);

                // the four half-size neighbours round this pixel's centre
                float2 at = (px + 0.5) * 0.5 - 0.5;
                int2 i0 = (int2)floor(at);
                float2 fr = at - i0;
                int2 last = (int2)_OS_BeamSize.zw - 1;
                float sum = 0.0, weight = 0.0, nearest = 0.0, gap = 1e9;
                [unroll]
                for (int k = 0; k < 4; k++)
                {
                    int2 o = int2(k & 1, k >> 1);
                    float2 s = LOAD_TEXTURE2D(_OS_BeamTex, clamp(i0 + o, 0, last)).rg;
                    float2 b = lerp(1.0 - fr, fr, (float2)o);
                    float w = b.x * b.y * LengthWeight(s.g, t);
                    sum += s.r * w;
                    weight += w;
                    float d = abs(s.g - t);
                    if (d < gap)
                    {
                        gap = d;
                        nearest = s.r;
                    }
                }
                float scatter = weight > 1e-3 ? sum / weight : nearest;

                float mu = dot(v, _OS_SunDir.xyz);
                float g = _OS_SunBeams.z, g2 = g * g;
                float hg = (1.0 - g2) / pow(max(1.0 + g2 - 2.0 * g * mu, 1e-4), 1.5);
                float phase = (0.25 + 0.75 * hg) / (4.0 * PI);
                return half4(frame.rgb + _OS_SunCol.rgb * (scatter * phase * _OS_SunBeams.x), frame.a);
            }
            ENDHLSL
        }
    }
}
