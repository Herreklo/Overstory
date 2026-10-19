// Light rays: sunlight streaming past rooftops, through trees and between hills towards the camera when
// it looks towards a low sun (Firewatch, SEASON, Ori). Screen-space: where the sky shows, its light is
// blurred radially away from the sun's place on screen, so whatever stands in front of the sky casts rays.
// Off when the sun is behind the camera or the rig's strength is zero.
Shader "Overstory/LightShafts"
{
    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" }
        ZWrite Off
        ZTest Always
        Cull Off

        Pass
        {
            Name "LightShafts"

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.core/Runtime/Utilities/Blit.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareDepthTexture.hlsl"

            float4 _OS_SunScreen;  // xy the sun's place in the viewport (0..1), z 1 when in front of the camera
            float4 _OS_Shafts;     // x strength, y reach (share of the screen), z decay, w how bright the sky must be to cast
            float4 _OS_ShaftColour; // rgb the light's colour (linear)

            half3 SkyLight(float2 uv)
            {
                float raw = SampleSceneDepth(uv);
            #if UNITY_REVERSED_Z
                bool sky = raw <= 1e-5;
            #else
                bool sky = raw >= 1.0 - 1e-5;
            #endif
                if (!sky)
                    return 0;
                half3 c = SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, uv).rgb;
                half l = dot(c, half3(0.2126h, 0.7152h, 0.0722h));
                return c * saturate((l - _OS_Shafts.w) * 4.0h);
            }

            half4 Frag(Varyings input) : SV_Target
            {
                float2 uv = input.texcoord;
                half4 colour = SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, uv);
                if (_OS_Shafts.x <= 0.001 || _OS_SunScreen.z < 0.5)
                    return colour;

                const int N = 64;
                float2 toSun = _OS_SunScreen.xy - uv;
                float2 stepUV = toSun * (_OS_Shafts.y / N);
                // a little jitter per pixel, fixed to the screen grid, breaks the banding of the steps
                float jitter = frac(52.9829189 * frac(dot(input.positionCS.xy, float2(0.06711056, 0.00583715))));
                float2 p = uv + stepUV * jitter;
                half3 sum = 0;
                half weight = 1.0h;
                [loop]
                for (int i = 0; i < N; i++)
                {
                    sum += SkyLight(p) * weight;
                    weight *= _OS_Shafts.z;
                    p += stepUV;
                }
                sum /= N;
                // strongest looking into the sun, gone when it is far off screen
                float near = saturate(1.2 - length((uv - _OS_SunScreen.xy) * float2(_ScreenParams.x / _ScreenParams.y, 1.0)) * 0.9);
                colour.rgb += sum * _OS_ShaftColour.rgb * _OS_Shafts.x * (0.35 + 0.65 * near);
                return colour;
            }
            ENDHLSL
        }
    }
}
