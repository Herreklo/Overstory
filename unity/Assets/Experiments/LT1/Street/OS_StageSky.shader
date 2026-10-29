// The street stage's sky under cloud (LT1Street, a light row's `drawn` "cie-overcast"): the CIE overcast sky, (1 + 2 sin e) / 3
// of its zenith at elevation e, three times brighter overhead than at the horizon, at the radiance of the light it casts
// (LT1Street sets the zenith from the hemisphere's light on level ground, 7/9 of the zenith's). Under the horizon, where
// the stage's ground ends, it keeps the horizon's value. Drawn first on a sphere round the camera, writing no depth.
Shader "Overstory/LT1/StageSky"
{
    Properties
    {
        _SkyZenith ("The zenith's radiance (linear rgb)", Vector) = (1, 1, 1, 0)
    }

    SubShader
    {
        Tags { "Queue" = "Background" "RenderType" = "Background" "RenderPipeline" = "UniversalPipeline" }
        Cull Front
        ZWrite Off

        Pass
        {
            Tags { "LightMode" = "UniversalForward" }
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                float4 _SkyZenith;
            CBUFFER_END

            struct Attributes { float4 positionOS : POSITION; };
            struct Varyings { float4 positionCS : SV_POSITION; float3 dir : TEXCOORD0; };

            Varyings Vert(Attributes input)
            {
                Varyings o;
                float3 ws = TransformObjectToWorld(input.positionOS.xyz);
                o.positionCS = TransformWorldToHClip(ws);
                o.dir = ws - _WorldSpaceCameraPos;
                return o;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                float e = max(normalize(input.dir).y, 0.0);
                return half4((half3)_SkyZenith.rgb * (half)((1.0 + 2.0 * e) / 3.0), 1.0h);
            }
            ENDHLSL
        }
    }
}
