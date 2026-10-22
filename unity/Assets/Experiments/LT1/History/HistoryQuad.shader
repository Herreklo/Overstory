// The history quad (step 3, R2): a full-screen grid of 4,096 pieces reading three synthetic pages (P0, P1, H1)
// through the real include (Shaders/History.hlsl), so the include's cost is measured on the harness before any real
// shader is ported (Overstory.EditorTools.LT1History; docs/measuring.md, the harness's quad scenes). Each cell is a
// piece: UV3.x its index into the piece table, read in the vertex stage and passed flat; UV1 its chart in the pages.
// Positions are clip space, so the grid covers the frame whatever the camera. "On" reads every layer of the three
// pages and the piece's clocks; "off" is OS_HISTORY_OFF, every layer its quiet mean.
Shader "Hidden/Overstory/HistoryQuad"
{
    Properties
    {
        _OS_QuietP0 ("History off: P0's quiet means (feet, water held, sky seen, ground seen)", Vector) = (0.1, 0.2, 0.7, 0.3)
        _OS_QuietP1 ("History off: P1's quiet means (openness, weather exposure, reserved, reserved)", Vector) = (0.6, 0.5, 0, 0)
        _OS_QuietH1 ("History off: H1's quiet means (polish, lichen, moss, onset)", Vector) = (0.1, 0.2, 0.15, 0)
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
                OSAddress a = OS_Address(input.uv1, input.piece);
                half feet = OS_HistoryAt(a, OS_LAYER_FEET);
                half held = OS_HistoryAt(a, OS_LAYER_WATER_HELD);
                half sky = OS_HistoryAt(a, OS_LAYER_SKY_SEEN);
                half ground = OS_HistoryAt(a, OS_LAYER_GROUND_SEEN);
                half open = OS_HistoryAt(a, OS_LAYER_OPENNESS);
                half exposure = OS_HistoryAt(a, OS_LAYER_EXPOSURE);
                OSLayer pl = OS_History(a, OS_LAYER_POLISH);
                half polish = OS_HistoryLaw(pl, OS_LAYER_POLISH, _OS_Date);
                half lichen = OS_HistoryAt(a, OS_LAYER_LICHEN);
                half moss = OS_HistoryAt(a, OS_LAYER_MOSS);
                // the piece's clocks as the law will read them (R4): years since its first reset at the date, its age
                float since = _OS_Date.x - (OS_FIRST_YEAR + (pl.piece.resets & 0xFFFFu) / 16.0) + (pl.piece.age & 0xFFFFu) / 16.0;
                half3 c = half3(polish * 0.5h + feet * 0.3h + held * 0.2h,
                                lichen * 0.5h + sky * 0.3h + open * 0.2h,
                                moss * 0.5h + ground * 0.3h + exposure * 0.2h) + pl.onset * 0.1h;
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
