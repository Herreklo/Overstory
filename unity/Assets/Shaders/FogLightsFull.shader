// The town's lamps lit in the air round them: each lamp scatters its light into the fog and haze between the camera
// and whatever stands behind, so in sea fog every lamp wears a halo, and in clear air hardly one. Full-screen, after
// the opaque scene and before post-processing, so the glow blooms with the lamps themselves.
//
// For a point light in air of even density, the light scattered towards the camera along a ray is
//     I sigma / h * integral over theta of phase(theta) * T(theta) d theta,
// with h the lamp's distance from the ray, s0 where along the ray it comes closest, and each point of the ray written
// as s = s0 + h tan(theta), so the 1 / distance^2 of the lamp's light cancels into the change of variable and the rest
// is smooth: the integral is taken with a few samples of theta from the camera to the surface. Fog droplets throw
// light forward (Henyey-Greenstein, g about 0.85), so a lamp's halo is tight and bright looking into it and faint from
// the side, as in a real fog; T is what the air takes from the lamp to the point and from the point to the camera.
// The air's density is taken at the lamp's height (the same height fog and low haze as OS_Atmosphere). Lamps come
// from Overstory.Scenes.TownLights.
//
// The full-size reference (FogLightsFeature.fullSize, the harness's 'foglights-full' arm): every lit lamp at every
// pixel, over a copy of the frame, as it was drawn before the halos went to a quarter of the pixels (FogLights.shader).
Shader "Overstory/FogLightsFull"
{
    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" }
        ZWrite Off
        ZTest Always
        Cull Off

        Pass
        {
            Name "FogLightsFull"

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma target 4.5
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.core/Runtime/Utilities/Blit.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareDepthTexture.hlsl"

            StructuredBuffer<float4> _OS_FogLampPos;     // xyz world position, w reach (m): past it a lamp adds nothing
            StructuredBuffer<float4> _OS_FogLampColour;  // rgb its light (linear, intensity in), w unused
            int _OS_FogLampCount;
            float _OS_FogLampStrength;                   // the rig's halo strength; 0 turns the pass off
            #include "StreetSurface.hlsl"                // the air: its height fog and the haze or bank

            float AirDensity(float3 p)
            {
                return _OS_FogParams.x * exp(-max(_OS_FogParams.y, 1e-4) * (p.y - _OS_FogParams.z)) + OS_HazeDensity(p);
            }

            half4 Frag(Varyings input) : SV_Target
            {
                float2 uv = input.texcoord;
                half4 colour = SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, uv);
                if (_OS_FogLampStrength <= 0.0 || _OS_FogLampCount <= 0)
                    return colour;

                float raw = SampleSceneDepth(uv);
            #if UNITY_REVERSED_Z
                bool sky = raw <= 1e-6;
            #else
                bool sky = raw >= 1.0 - 1e-6;
            #endif
                float3 world = ComputeWorldSpacePosition(uv, raw, UNITY_MATRIX_I_VP);
                float3 o = _WorldSpaceCameraPos;
                float3 toSurface = world - o;
                float t = sky ? 4000.0 : length(toSurface);
                float3 v = toSurface / max(length(toSurface), 1e-4);

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
                colour.rgb += sum * _OS_FogLampStrength;
                return colour;
            }
            ENDHLSL
        }
    }
}
