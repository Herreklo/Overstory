// The key block of the woodblock print (look D): thin lines in indigo ink where forms really have edges
// (silhouettes, rooflines, terraces, window reveals), found from depth and normals, thinning and fading
// into the air with distance. Never black, never even: the research's generic-look trap is "even-width
// black outlines". Off unless _OS_KeyBlock is 1.
Shader "Overstory/KeyBlock"
{
    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" }
        ZWrite Off
        ZTest Always
        Cull Off

        Pass
        {
            Name "KeyBlock"

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.core/Runtime/Utilities/Blit.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareDepthTexture.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareNormalsTexture.hlsl"

            float _OS_KeyBlock;     // 1 draws the key block
            float4 _OS_Ink;         // rgb the key block's ink (linear), a its strength
            float4 _OS_InkFade;     // x distance (m) where lines start to fade, y where they are gone

            float Depth(float2 uv) { return LinearEyeDepth(SampleSceneDepth(uv), _ZBufferParams); }

            half4 Frag(Varyings input) : SV_Target
            {
                float2 uv = input.texcoord;
                half4 colour = SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, uv);
                if (_OS_KeyBlock < 0.5)
                    return colour;

                float2 px = _BlitTexture_TexelSize.xy;
                float d = Depth(uv);
                half3 n = SampleSceneNormals(uv);
                float dEdge = 0;
                half nEdge = 0;
                const float2 offsets[4] = { float2(1, 0), float2(-1, 0), float2(0, 1), float2(0, -1) };
                [unroll]
                for (int k = 0; k < 4; k++)
                {
                    float2 o = uv + offsets[k] * px;
                    float dk = Depth(o);
                    // a jump in depth, relative to how far away it is (so distance alone draws no lines)
                    dEdge = max(dEdge, saturate(((dk - d) / max(d, 1e-3) - 0.025) / 0.03));
                    nEdge = max(nEdge, saturate((0.82h - dot(n, SampleSceneNormals(o))) / 0.12h));
                }
                half edge = max((half)dEdge, nEdge);
                // lines thin and fade into the air: strong close by, gone far off, as a carver would leave them
                half fade = 1.0h - saturate((d - _OS_InkFade.x) / max(_OS_InkFade.y - _OS_InkFade.x, 1.0));
                if (d > 5000.0)
                    fade = 0; // the sky has no edges
                colour.rgb = lerp(colour.rgb, _OS_Ink.rgb, edge * fade * _OS_Ink.a);
                return colour;
            }
            ENDHLSL
        }
    }
}
