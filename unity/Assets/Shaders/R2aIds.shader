// R2a's id and normal render (reviews/lt1/port/2b/r2a/stones/plan.md, The measures; Editor/LT1R2a.cs): unlit and
// exact, what the judged stone's mesh is at each pixel, against which a line in the frame is a mesh edge or floats
// (SN9). Drawn into a linear 8-bit target, no MSAA, post and the renderer features off; never in the game.
//   _Mode 0, ids:     r the piece's seed (UV1 y), g its face's patch slice (UV7's code: slice 0 to 7 as 32 slice + 16,
//                     so never 0 on a stone), b its face's kind (UV2 x, as 32 kind + 16)
//   _Mode 1, normals: rgb the face's own normal (the mesh's, world space) as n / 2 + 1/2
//   _Mode 2, blank:   black, for everything else in the frame (it still hides what lies behind it)
Shader "Overstory/R2aIds"
{
    Properties
    {
        _Mode ("0 ids, 1 normals, 2 blank", Float) = 0
    }

    HLSLINCLUDE
    #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

    CBUFFER_START(UnityPerMaterial)
        float _Mode;
    CBUFFER_END
    ENDHLSL

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "Queue" = "Geometry" }

        Pass
        {
            Name "Ids"
            Tags { "LightMode" = "UniversalForward" }

            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_instancing

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv1 : TEXCOORD1;
                float2 uv2 : TEXCOORD2;
                float2 uv7 : TEXCOORD7;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 normalWS : TEXCOORD0;
                nointerpolation float3 id : TEXCOORD1;    // seed, slice, kind
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            Varyings Vert(Attributes input)
            {
                Varyings o = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, o);
                o.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                o.normalWS = TransformObjectToWorldNormal(input.normalOS);
                float code = round(input.uv7.y);
                o.id = float3(frac(input.uv1.y), fmod(code, 8.0), input.uv2.x);
                return o;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);
                if (_Mode > 1.5)
                    return half4(0, 0, 0, 1);
                if (_Mode > 0.5)
                    return half4(normalize(input.normalWS) * 0.5 + 0.5, 1);
                return half4(input.id.x, (input.id.y * 32.0 + 16.0) / 255.0, (round(input.id.z) * 32.0 + 16.0) / 255.0, 1);
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
            #pragma target 3.5
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_instancing

            struct Attributes
            {
                float4 positionOS : POSITION;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            float4 Vert(Attributes input) : SV_POSITION
            {
                UNITY_SETUP_INSTANCE_ID(input);
                return TransformObjectToHClip(input.positionOS.xyz);
            }

            half Frag(float4 positionCS : SV_POSITION) : SV_Target { return positionCS.z; }
            ENDHLSL
        }

        Pass
        {
            Name "DepthNormals"
            Tags { "LightMode" = "DepthNormals" }
            ZWrite On

            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_instancing

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                half3 normalWS : TEXCOORD0;
            };

            Varyings Vert(Attributes input)
            {
                Varyings o;
                UNITY_SETUP_INSTANCE_ID(input);
                o.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                o.normalWS = TransformObjectToWorldNormal(input.normalOS);
                return o;
            }

            half4 Frag(Varyings input) : SV_Target0 { return half4(normalize(input.normalWS), 0.0); }
            ENDHLSL
        }
    }
}
