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

        // What each surface is made of, seen from above as the height is: each house's wall paint over its footprint
        // (target 0) and each surface's own albedo with whose it is (target 1, alpha: a house's number over 255, 0 for
        // the ground), linear, from the town's facts (SkyMap.albedo), for the light the rest of the town gives back to
        // each house (TownHorizon.shader, Bounce)
        Pass
        {
            Name "Albedo"
            Cull Off
            ZWrite On
            ZTest LEqual

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            float4x4 _OS_HeightVP;
            float4 _OS_DrawWall, _OS_DrawTop;

            struct Attributes { float4 positionOS : POSITION; };
            struct Varyings { float4 positionCS : SV_POSITION; };
            struct Targets { float4 wall : SV_Target0; float4 top : SV_Target1; };

            Varyings Vert(Attributes input)
            {
                Varyings o;
                o.positionCS = mul(_OS_HeightVP, float4(TransformObjectToWorld(input.positionOS.xyz), 1.0));
                return o;
            }

            Targets Frag(Varyings input)
            {
                Targets t;
                t.wall = float4(_OS_DrawWall.rgb, 1.0);
                t.top = _OS_DrawTop;
                return t;
            }
            ENDHLSL
        }
    }
}