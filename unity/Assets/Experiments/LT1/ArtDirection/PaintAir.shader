// The painted corner's air: one full-screen pass over the surfaces' colour and their distance from the eye
// (PaintSurface.shader, _P_Mode 1: r the distance times the coverage, g the coverage). It draws the sky where nothing
// stands, the sea fog in three stepped layers by distance (the near clear, the Landing veiled, the far town a flat
// shape in the fog's colour), each lamp's tight halo where nothing stands before it, and the grade (a soft shoulder for
// the hot heads, a vignette). It reads the distance pass so the edges against the sky stay clean through the
// anti-aliasing. Every value is from Paint.json; the body is PaintAir.hlsl, shared by the two passes:
//     0 "Still": LT1ArtPasses.Paint's (Graphics.Blit, the frame as _MainTex, the distance and camera on the material)
//     1 "Scene": the saved scene's at runtime (PaintAirPass: the frame as _BlitTexture, the distance and camera in a
//       property block)
Shader "Hidden/Overstory/PaintAir"
{
    Properties
    {
        _MainTex ("Colour", 2D) = "black" {}
    }

    SubShader
    {
        ZTest Always Cull Off ZWrite Off

        Pass
        {
            Name "Still"

            CGPROGRAM
            #pragma target 4.5
            #pragma vertex vert_img
            #pragma fragment Frag
            #include "UnityCG.cginc"

            sampler2D _MainTex;
            sampler2D _P_Dist;
            #define P_COLOUR(uv) tex2D(_MainTex, uv)
            #define P_DIST(uv) tex2D(_P_Dist, uv)
            #define P_DIST_LOD(uv) tex2Dlod(_P_Dist, float4(uv, 0, 0))
            #include "PaintAir.hlsl"

            float4 Frag(v2f_img i) : SV_Target
            {
                return P_Air(i.uv, i.pos.xy);
            }
            ENDCG
        }

        Pass
        {
            Name "Scene"

            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex Vert
            #pragma fragment FragScene
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.core/Runtime/Utilities/Blit.hlsl"

            TEXTURE2D(_P_Dist);
            #define P_COLOUR(uv) SAMPLE_TEXTURE2D_X_LOD(_BlitTexture, sampler_PointClamp, uv, 0)
            #define P_DIST(uv) SAMPLE_TEXTURE2D_LOD(_P_Dist, sampler_PointClamp, uv, 0)
            #define P_DIST_LOD(uv) SAMPLE_TEXTURE2D_LOD(_P_Dist, sampler_PointClamp, uv, 0)
            #include "PaintAir.hlsl"

            float4 FragScene(Varyings i) : SV_Target
            {
                return P_Air(i.texcoord, i.positionCS.xy);
            }
            ENDHLSL
        }
    }
}
