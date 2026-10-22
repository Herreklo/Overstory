// The history quad (step 3, R2): a full-screen grid of 4,096 pieces reading three synthetic pages (P0, P1, H1)
// through the real include (Shaders/History.hlsl), so the include's cost is measured on the harness before any real
// shader is ported (Overstory.EditorTools.LT1History; docs/measuring.md, the harness's quad scenes). Each cell is a
// piece: UV3.x its index into the piece table, read in the vertex stage and passed flat; UV1 its chart in the pages.
// Positions are clip space, so the grid covers the frame whatever the camera. "On" reads every layer of the three
// pages and the piece's clocks; "off" is OS_HISTORY_OFF, every layer its quiet mean.
//
// R2b (the step-3 verdict's decision 7): OS_QUAD_TWO_PAGES, a local keyword the harness sets on the quad's material,
// reads P0 and H1 only, as the stone will (P1's two layers are then not sampled). The minified arms change the mesh,
// not this shader (LT1History.QuadMesh(tile)).
//
// R2c (why a minified page costs): one local arm keyword at a time replaces the include's page sample through its
// measuring hook (OS_PAGE_SAMPLE); none is the include's own path. The quad's UVs never wrap (no frac: a tiled
// cell's UVs run on across the page), so its derivatives are continuous within a cell.
// - OS_QUAD_NEARMIP: the inline sampler_LinearClamp (bilinear from the nearest mip, no anisotropy);
// - OS_QUAD_TRI: the inline sampler_TrilinearClamp (two mips blended, no anisotropy);
// - OS_QUAD_LOD: SampleLevel at a LOD computed once a pixel from the UV's derivatives, the array's own sampler;
// - OS_QUAD_GRAD: SampleGrad with the UV's derivatives computed once a pixel, the array's own sampler;
// - OS_QUAD_DIRECT: the array's own sampler at a constant slice (the page's index): no slice from the piece;
// - OS_QUAD_TEX2D: three plain Texture2Ds (the BC7 array's slices, its sampler settings) instead of the array;
// - OS_QUAD_ALU: no sample: the UV and the slice in a little arithmetic, so the include's other work stays;
// - OS_QUAD_QUIET: the include's own samples, but the output flat: a constant colour with the samples added a hundred
//   thousand times below the target's step (they stay live and change no pixel);
// - OS_QUAD_NOISY: no sample: the page's structure made in arithmetic (a value a chart and grain a texel, at the texel
//   the UV lands on), so the output is as busy as a minified page's without a texture read.
Shader "Hidden/Overstory/HistoryQuad"
{
    Properties
    {
        _OS_QuietP0 ("History off: P0's quiet means (feet, water held, sky seen, ground seen)", Vector) = (0.1, 0.2, 0.7, 0.3)
        _OS_QuietP1 ("History off: P1's quiet means (openness, weather exposure, reserved, reserved)", Vector) = (0.6, 0.5, 0, 0)
        _OS_QuietH1 ("History off: H1's quiet means (polish, lichen, moss, onset)", Vector) = (0.1, 0.2, 0.15, 0)
        [NoScaleOffset] _OS_QuadP0 ("R2c's plain-texture arm: P0", 2D) = "black" {}
        [NoScaleOffset] _OS_QuadP1 ("R2c's plain-texture arm: P1", 2D) = "black" {}
        [NoScaleOffset] _OS_QuadH1 ("R2c's plain-texture arm: H1", 2D) = "black" {}
    }

    HLSLINCLUDE
    #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

    CBUFFER_START(UnityPerMaterial)
        half4 _OS_QuietP0;
        half4 _OS_QuietP1;
        half4 _OS_QuietH1;
    CBUFFER_END

    // the pack's first year, from which the piece table counts its dates (history-pages.md, 3: 1850 to 2050)
    #define OS_FIRST_YEAR 1850.0
    // the grid's depth in clip space (between the near and far planes either way round)
    #define OS_QUAD_DEPTH 0.5

    float4 OS_QuadPosition(float3 positionOS) { return float4(positionOS.xy, OS_QUAD_DEPTH, 1.0); }
    ENDHLSL

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "Queue" = "Geometry" }
        Cull Off

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode" = "UniversalForward" }

            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile _ OS_HISTORY_OFF
            #pragma multi_compile_local_fragment _ OS_QUAD_TWO_PAGES
            #pragma multi_compile_local_fragment _ OS_QUAD_NEARMIP OS_QUAD_TRI OS_QUAD_LOD OS_QUAD_GRAD OS_QUAD_DIRECT OS_QUAD_TEX2D OS_QUAD_ALU OS_QUAD_QUIET OS_QUAD_NOISY

            // R2c's arms (the header): each defines the include's measuring hook, OS_PAGE_SAMPLE(a, page)
            // the pages' size (LT1History.W, H), for the LOD arm's texels a pixel
            #define OS_QUAD_PAGE float2(1024.0, 512.0)
            // the UV's derivatives and its LOD, computed once a pixel at the top of Frag (the LOD and gradient arms)
            static float2 os_QuadDdx, os_QuadDdy;
            static float os_QuadLod;

            TEXTURE2D(_OS_QuadP0);
            TEXTURE2D(_OS_QuadP1);
            TEXTURE2D(_OS_QuadH1);
            SAMPLER(sampler_OS_QuadP0);

            // the plain-texture arm: a page from its own Texture2D (page is a constant after inlining: one sample)
            half4 OS_QuadPlain(float2 uv, uint page)
            {
                if (page == 0u)
                    return SAMPLE_TEXTURE2D(_OS_QuadP0, sampler_OS_QuadP0, uv);
                if (page == 1u)
                    return SAMPLE_TEXTURE2D(_OS_QuadP1, sampler_OS_QuadP0, uv);
                return SAMPLE_TEXTURE2D(_OS_QuadH1, sampler_OS_QuadP0, uv);
            }

            // the noisy arm: the synthetic page's structure (LT1History.Content: a value a 16 by 8 chart, grain a texel)
            uint OS_QuadHash(uint h)
            {
                h ^= h >> 16; h *= 0x7feb352du; h ^= h >> 15; h *= 0x846ca68bu; h ^= h >> 16;
                return h;
            }

            float4 OS_QuadNoise(float2 uv, uint slice)
            {
                uint2 t = (uint2)(uv * OS_QUAD_PAGE);
                uint2 chart = t / uint2(16u, 8u);
                uint hc = OS_QuadHash(chart.x + chart.y * 64u + slice * 4096u);
                uint ht = OS_QuadHash(t.x + t.y * 1024u + slice * 524288u + 0x9e3779b9u);
                float4 piece = float4(hc & 255u, (hc >> 8) & 255u, (hc >> 16) & 255u, hc >> 24) / 255.0;
                float4 grain = float4(ht & 255u, (ht >> 8) & 255u, (ht >> 16) & 255u, ht >> 24) / 255.0 - 0.5;
                return 0.1 + 0.55 * piece + 0.04 * grain;
            }

            #if defined(OS_QUAD_NEARMIP)
                #define OS_PAGE_SAMPLE(a, page) SAMPLE_TEXTURE2D_ARRAY(_OS_PagesRGBA, sampler_LinearClamp, (a).uv, (a).piece.slice + (page))
            #elif defined(OS_QUAD_TRI)
                #define OS_PAGE_SAMPLE(a, page) SAMPLE_TEXTURE2D_ARRAY(_OS_PagesRGBA, sampler_TrilinearClamp, (a).uv, (a).piece.slice + (page))
            #elif defined(OS_QUAD_LOD)
                #define OS_PAGE_SAMPLE(a, page) SAMPLE_TEXTURE2D_ARRAY_LOD(_OS_PagesRGBA, sampler_OS_PagesRGBA, (a).uv, (a).piece.slice + (page), os_QuadLod)
            #elif defined(OS_QUAD_GRAD)
                #define OS_PAGE_SAMPLE(a, page) SAMPLE_TEXTURE2D_ARRAY_GRAD(_OS_PagesRGBA, sampler_OS_PagesRGBA, (a).uv, (a).piece.slice + (page), os_QuadDdx, os_QuadDdy)
            #elif defined(OS_QUAD_DIRECT)
                #define OS_PAGE_SAMPLE(a, page) SAMPLE_TEXTURE2D_ARRAY(_OS_PagesRGBA, sampler_OS_PagesRGBA, (a).uv, (page))
            #elif defined(OS_QUAD_TEX2D)
                #define OS_PAGE_SAMPLE(a, page) OS_QuadPlain((a).uv, (page))
            #elif defined(OS_QUAD_ALU)
                #define OS_PAGE_SAMPLE(a, page) (float4((a).uv, (a).uv.yx) * 0.5 + (float)((a).piece.slice + (page)) * 0.01)
            #elif defined(OS_QUAD_NOISY)
                #define OS_PAGE_SAMPLE(a, page) OS_QuadNoise((a).uv, (a).piece.slice + (page))
            #endif

            #include "Assets/Shaders/History.hlsl"

            struct Attributes
            {
                float3 positionOS : POSITION;
                float2 uv1 : TEXCOORD1;
                float2 uv3 : TEXCOORD3;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv1 : TEXCOORD0;
                nointerpolation uint4 piece : TEXCOORD1;
            };

            Varyings Vert(Attributes input)
            {
                Varyings o;
                o.positionCS = OS_QuadPosition(input.positionOS);
                o.uv1 = input.uv1;
                o.piece = OS_PackPiece(OS_Piece((uint)input.uv3.x));
                return o;
            }

            half4 Frag(Varyings input) : SV_Target
            {
            #if !defined(OS_HISTORY_OFF) && (defined(OS_QUAD_LOD) || defined(OS_QUAD_GRAD))
                // (R2c: once a pixel, from the UV as interpolated, before any indirection)
                os_QuadDdx = ddx(input.uv1);
                os_QuadDdy = ddy(input.uv1);
                float2 tx = os_QuadDdx * OS_QUAD_PAGE, ty = os_QuadDdy * OS_QUAD_PAGE;
                os_QuadLod = 0.5 * log2(max(dot(tx, tx), dot(ty, ty)));
            #endif
                OSAddress a = OS_Address(input.uv1, input.piece);
                half feet = OS_HistoryAt(a, OS_LAYER_FEET);
                half held = OS_HistoryAt(a, OS_LAYER_WATER_HELD);
                half sky = OS_HistoryAt(a, OS_LAYER_SKY_SEEN);
                half ground = OS_HistoryAt(a, OS_LAYER_GROUND_SEEN);
            #if defined(OS_QUAD_TWO_PAGES)
                // (P0 and H1 only: P1 is not sampled)
                half open = 0.0h;
                half exposure = 0.0h;
            #else
                half open = OS_HistoryAt(a, OS_LAYER_OPENNESS);
                half exposure = OS_HistoryAt(a, OS_LAYER_EXPOSURE);
            #endif
                OSLayer pl = OS_History(a, OS_LAYER_POLISH);
                half polish = OS_HistoryLaw(pl, OS_LAYER_POLISH, _OS_Date);
                half lichen = OS_HistoryAt(a, OS_LAYER_LICHEN);
                half moss = OS_HistoryAt(a, OS_LAYER_MOSS);
                // the piece's clocks as the law will read them (R4): years since its first reset at the date, its age
                float since = _OS_Date.x - (OS_FIRST_YEAR + (pl.piece.resets & 0xFFFFu) / 16.0) + (pl.piece.age & 0xFFFFu) / 16.0;
                half3 c = half3(polish * 0.5h + feet * 0.3h + held * 0.2h,
                                lichen * 0.5h + sky * 0.3h + open * 0.2h,
                                moss * 0.5h + ground * 0.3h + exposure * 0.2h) + pl.onset * 0.1h;
            #if defined(OS_QUAD_QUIET) && !defined(OS_HISTORY_OFF)
                // (R2c: every sample kept, the output flat: their sum is far below the target's step)
                c = (half3)(float3(0.3, 0.4, 0.5) + 1e-5 * float3(polish + feet + held, lichen + sky + open, moss + ground + exposure + pl.onset));
            #endif
                return half4(c, (half)saturate(since / 200.0));
            }
            ENDHLSL
        }

        Pass
        {
            Name "DepthOnly"
            Tags { "LightMode" = "DepthOnly" }
            ZWrite On
            ColorMask R

            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex Vert
            #pragma fragment Frag

            float4 Vert(float3 positionOS : POSITION) : SV_POSITION { return OS_QuadPosition(positionOS); }
            half Frag(float4 positionCS : SV_POSITION) : SV_Target { return positionCS.z; }
            ENDHLSL
        }

        Pass
        {
            Name "DepthNormals"
            Tags { "LightMode" = "DepthNormals" }
            ZWrite On

            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex Vert
            #pragma fragment Frag

            float4 Vert(float3 positionOS : POSITION) : SV_POSITION { return OS_QuadPosition(positionOS); }
            half4 Frag(float4 positionCS : SV_POSITION) : SV_Target { return half4(0, 0, -1, 0); }
            ENDHLSL
        }
    }
}
