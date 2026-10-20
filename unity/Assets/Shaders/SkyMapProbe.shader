// Reads the town's sky map at one point exactly as the street shader does (StreetLooks.hlsl, OS_TownSky), so a check
// can prove the map lies the right way round on this graphics API (LT1Heart.CheckSkyMap).
Shader "Hidden/Overstory/SkyMapProbe"
{
    SubShader
    {
        Pass
        {
            ZTest Always
            ZWrite Off
            Cull Off

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct Attributes { float4 positionOS : POSITION; };
            struct Varyings { float4 positionCS : SV_POSITION; };

            Varyings Vert(Attributes input)
            {
                Varyings o;
                o.positionCS = TransformObjectToHClip(input.positionOS.xyz); // Graphics.Blit's quad covers the 1 x 1 target
                return o;
            }

            TEXTURE2D(_OS_SkyMap);
            SAMPLER(sampler_OS_SkyMap);
            float4 _OS_SkyMapRect;
            float4 _Probe; // xy the point (world x, z)

            float4 Frag(Varyings input) : SV_Target
            {
                float2 uv = (_Probe.xy - _OS_SkyMapRect.xy) * _OS_SkyMapRect.z;
                uv.y = _OS_SkyMapRect.w > 0.5 ? 1.0 - uv.y : uv.y;
                return float4(SAMPLE_TEXTURE2D_LOD(_OS_SkyMap, sampler_OS_SkyMap, uv, 0).r, uv.x, uv.y, 1.0);
            }
            ENDHLSL
        }
    }
}
