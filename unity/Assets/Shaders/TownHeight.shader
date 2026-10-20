// The town's height seen from straight above, for its sky map (Overstory.Scenes.SkyMap): each texel holds the
// height in metres of the highest surface over it. Drawn with the map's own view and projection, outside the
// render pipeline, so it can be redrawn whenever the town changes.
Shader "Hidden/Overstory/TownHeight"
{
    SubShader
    {
        Tags { "RenderType" = "Opaque" }
        Pass
        {
            Cull Off
            ZWrite On
            ZTest LEqual

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            float4x4 _OS_HeightVP;

            struct Attributes { float4 positionOS : POSITION; };
            struct Varyings { float4 positionCS : SV_POSITION; float height : TEXCOORD0; };

            Varyings Vert(Attributes input)
            {
                Varyings o;
                float3 w = TransformObjectToWorld(input.positionOS.xyz);
                o.positionCS = mul(_OS_HeightVP, float4(w, 1.0));
                o.height = w.y;
                return o;
            }

            float Frag(Varyings input) : SV_Target
            {
                return input.height;
            }
            ENDHLSL
        }
    }
}
