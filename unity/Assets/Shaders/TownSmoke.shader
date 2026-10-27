// Smoke from the town's chimneys (LT1Town, Smoke): each puff a soft disc turned to the eye, lit by the sun where its
// shadow map lets the sun reach the puff and brighter looking toward the sun, by the sky everywhere, then seen
// through the town's air as everything else is. The puffs' centres, radii and opacities are the mesh's.
Shader "Overstory/TownSmoke"
{
    Properties
    {
        _Colour ("Colour", Color) = (0.78, 0.77, 0.74, 1)
        _Forward ("Forward scattering", Range(0, 0.9)) = 0.4
    }
    SubShader
    {
        Tags { "Queue" = "Transparent" "RenderType" = "Transparent" "RenderPipeline" = "UniversalPipeline" "IgnoreProjector" = "True" }

        Pass
        {
            Name "Smoke"
            Tags { "LightMode" = "UniversalForward" }
            Blend SrcAlpha OneMinusSrcAlpha
            ZWrite Off
            ZTest LEqual
            Cull Off

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma target 3.5
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE
            #pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
            #pragma multi_compile_fragment _ OS_HAZE_OFF     // the harness's haze-off (OS_Atmosphere)
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #include "StreetSurface.hlsl"

            CBUFFER_START(UnityPerMaterial)
            half4 _Colour;
            half _Forward;
            CBUFFER_END

            struct Attributes
            {
                float3 positionOS : POSITION;   // the puff's centre
                float2 corner : TEXCOORD0;      // -1 to 1
                float2 puff : TEXCOORD1;        // x its radius (m), y its opacity
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 corner : TEXCOORD0;
                float3 centreWS : TEXCOORD1;
                half opacity : TEXCOORD2;
            };

            Varyings Vert(Attributes input)
            {
                Varyings o = (Varyings)0;
                float3 centre = TransformObjectToWorld(input.positionOS);
                float3 right = UNITY_MATRIX_V[0].xyz, up = UNITY_MATRIX_V[1].xyz;
                o.positionCS = TransformWorldToHClip(centre + (right * input.corner.x + up * input.corner.y) * input.puff.x);
                o.corner = input.corner;
                o.centreWS = centre;
                o.opacity = (half)input.puff.y;
                return o;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half disc = saturate(1.0h - (half)dot(input.corner, input.corner));
                disc *= disc;
                float3 c = input.centreWS;
                float3 v = normalize(c - _WorldSpaceCameraPos);
                float g = _Forward, g2 = g * g;

                // the sun, where it reaches the puff, scattered more toward the eye looking into it
                Light sun = GetMainLight(TransformWorldToShadowCoord(c));
                float mu = dot(v, sun.direction);
                float hg = (1.0 - g2) / pow(max(1.0 + g2 - 2.0 * g * mu, 1e-4), 1.5);
                half3 light = sun.color * sun.shadowAttenuation * (half)(0.5 + 0.5 * hg) + SampleSH(half3(0, 1, 0));

                // the air in front of it takes its share, as it does from everything else
                return half4(OS_Atmosphere(_Colour.rgb * light, c), disc * input.opacity);
            }
            ENDHLSL
        }
    }
}
