// The sky: a gradient from the horizon to the zenith, the ground's colour below the horizon, and a
// glow towards the sun. The light rig sets every colour; the horizon matches the colour of the air
// (StreetSurface.hlsl, OS_Atmosphere) so distant things fade into the sky they stand against.
Shader "Overstory/Sky"
{
    Properties
    {
        _Zenith ("Zenith", Color) = (0.55, 0.6, 0.66, 1)
        _Horizon ("Horizon", Color) = (0.7, 0.73, 0.76, 1)
        _Below ("Below the horizon", Color) = (0.3, 0.32, 0.32, 1)
        _Curve ("Gradient curve", Range(0.2, 4)) = 0.6
        _SunGlow ("Sun glow", Color) = (0, 0, 0, 1)
        _SunGlowPower ("Sun glow tightness", Float) = 8
    }

    SubShader
    {
        Tags { "Queue" = "Background" "RenderType" = "Background" "PreviewType" = "Skybox" "RenderPipeline" = "UniversalPipeline" }
        Cull Off
        ZWrite Off

        Pass
        {
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _Zenith, _Horizon, _Below, _SunGlow;
                half _Curve, _SunGlowPower;
            CBUFFER_END
            float4 _OS_SunDir;

            struct Attributes { float4 positionOS : POSITION; };
            struct Varyings { float4 positionCS : SV_POSITION; float3 dir : TEXCOORD0; };

            Varyings Vert(Attributes input)
            {
                Varyings o;
                o.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                o.dir = input.positionOS.xyz;
                return o;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                float3 d = normalize(input.dir);
                half3 c = d.y >= 0 ? lerp(_Horizon.rgb, _Zenith.rgb, pow(saturate(d.y), _Curve))
                                   : lerp(_Horizon.rgb, _Below.rgb, saturate(-d.y * 6.0));
                c += _SunGlow.rgb * pow(saturate(dot(d, _OS_SunDir.xyz)), max(_SunGlowPower, 1.0));
                return half4(c, 1);
            }
            ENDHLSL
        }
    }
}
