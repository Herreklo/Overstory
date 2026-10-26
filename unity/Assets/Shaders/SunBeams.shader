// Shafts of sun in the haze: for each pixel the view ray is marched through the air, and at each step the sun's
// shadow map says whether sunlight reaches that point; lit air scatters the sun's light towards the camera, shadowed
// air does not. So beams fall exactly where light passes between roofs, down lanes and through gaps in the cloud, and
// the air in a shaded lane stays dark. This replaces the unshadowed glow of the sun in the air (OS_Atmosphere's sun
// term), which the stage turns off while the beams are on. Full-screen, after the opaque scene, before post.
//
// The air's density is OS_Atmosphere's (height fog and low haze); the phase is forward scattering (Henyey-Greenstein,
// g about 0.7, haze), so beams are brightest looking towards the sun. Steps are spaced closer near the camera and
// jittered per pixel; the stills' supersampling smooths the jitter.
Shader "Overstory/SunBeams"
{
    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" }
        ZWrite Off
        ZTest Always
        Cull Off

        Pass
        {
            Name "SunBeams"

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma target 4.5
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.core/Runtime/Utilities/Blit.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareDepthTexture.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Shadows.hlsl"
            #include "StreetSurface.hlsl"   // the air's parameters, the cloud layer

            float4 _OS_SunBeams;   // x strength (0 off), y how far the march reaches (m), z forward scattering g, w beam haze
            float4 _OS_SunCol;     // the sun's light (linear, intensity in)

            float AirDensity(float3 p)
            {
                return _OS_FogParams.x * exp(-max(_OS_FogParams.y, 1e-4) * (p.y - _OS_FogParams.z)) + OS_HazeDensity(p);
            }

            // how much sun reaches a point through the cloud layer (the same pattern whose shadows lie on the town)
            float CloudLight(float3 p, float3 toSun)
            {
                if (_OS_Clouds.x <= 0.001)
                    return 1.0;
                float up = max(toSun.y, 0.05);
                float2 q = p.xz + toSun.xz * ((_OS_Clouds.w - p.y) / up);
                return lerp(1.0, _OS_CloudThrough, OS_CloudCover(OS_CloudField(q, 0.0), 0.0));
            }

            half4 Frag(Varyings input) : SV_Target
            {
                float2 uv = input.texcoord;
                half4 colour = SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, uv);
                if (_OS_SunBeams.x <= 0.0 || _OS_SunCol.r + _OS_SunCol.g + _OS_SunCol.b <= 0.001)
                    return colour;

                float raw = SampleSceneDepth(uv);
            #if UNITY_REVERSED_Z
                bool sky = raw <= 1e-6;
            #else
                bool sky = raw >= 1.0 - 1e-6;
            #endif
                float3 world = ComputeWorldSpacePosition(uv, raw, UNITY_MATRIX_I_VP);
                float3 o = _WorldSpaceCameraPos;
                float3 ray = world - o;
                float t = sky ? _OS_SunBeams.y : min(length(ray), _OS_SunBeams.y);
                float3 v = ray / max(length(ray), 1e-4);
                float3 toSun = _OS_SunDir.xyz;

                float mu = dot(v, toSun);
                float g = _OS_SunBeams.z, g2 = g * g;
                float hg = (1.0 - g2) / pow(max(1.0 + g2 - 2.0 * g * mu, 1e-4), 1.5);
                float phase = (0.25 + 0.75 * hg) / (4.0 * PI);

                const int N = 40;
                float jitter = frac(52.9829189 * frac(dot(input.positionCS.xy, float2(0.06711056, 0.00583715))));
                float sum = 0.0, depth = 0.0, prev = 0.0;
                [loop]
                for (int i = 0; i < N; i++)
                {
                    float f = (i + jitter) / N;
                    float s = t * f * f;                    // closer steps near the camera
                    float ds = s - prev;
                    prev = s;
                    float3 p = o + v * s;
                    float sigma = AirDensity(p);
                    float lit = MainLightRealtimeShadow(TransformWorldToShadowCoord(p)) * CloudLight(p, toSun);
                    depth += sigma * ds;
                    // what the air scatters for beams can be more than what it hides: a set is hazed for the light
                    sum += exp(-depth) * sigma * _OS_SunBeams.w * lit * ds;
                }
                colour.rgb += _OS_SunCol.rgb * (sum * phase * _OS_SunBeams.x);
                return colour;
            }
            ENDHLSL
        }
    }
}
