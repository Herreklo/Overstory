// The passes a style frame is painted over (reviews/lt1/art-direction/, tools/style_frame.py), drawn by
// LT1ArtPasses in place of every renderer's own material for one frame. Each value is written so the 8-bit sRGB
// still holds it exactly (decoded from sRGB before the target encodes it):
//   _OS_ArtPass 1  the world normal in street axes (x east, y north, z up), * 0.5 + 0.5
//   _OS_ArtPass 2  distance: R log2(1 + d) / 13 coarse, G its fraction at 1/256, B the renderer's class / 255
//   _OS_ArtPass 3  street position, coarse: (x, y, z + 32) / 256
//   _OS_ArtPass 4  street position, fine: frac of each in metres
//   _OS_ArtPass 5  what the surface is: clay R G its palette UV; a house R its kind / 64, G 1 for a lit pane
Shader "Hidden/Overstory/ArtPasses"
{
    Properties
    {
        _Class ("Class", Float) = 0
    }
    SubShader
    {
        Tags { "RenderPipeline" = "UniversalPipeline" "RenderType" = "Opaque" }
        Pass
        {
            Name "ArtPasses"
            Tags { "LightMode" = "UniversalForward" }
            Cull Off
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            float _Class;
            float _OS_ArtPass;

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv0 : TEXCOORD0;
                float2 uv1 : TEXCOORD1;
                float2 uv4 : TEXCOORD4;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float3 normalWS : TEXCOORD1;
                float4 uv : TEXCOORD2;
            };

            Varyings vert(Attributes input)
            {
                Varyings o;
                o.positionWS = TransformObjectToWorld(input.positionOS.xyz);
                o.positionCS = TransformWorldToHClip(o.positionWS);
                o.normalWS = TransformObjectToWorldNormal(input.normalOS);
                o.uv = float4(input.uv0, input.uv1.x, input.uv4.y);
                return o;
            }

            float3 Store(float3 v)
            {
                v = saturate(v);
                return lerp(v / 12.92, pow((v + 0.055) / 1.055, 2.4), step(0.04045, v));
            }

            half4 frag(Varyings input, bool front : SV_IsFrontFace) : SV_Target
            {
                float3 n = normalize(input.normalWS) * (front ? 1.0 : -1.0);
                float3 p = input.positionWS;
                float3 street = float3(p.x, p.z, p.y);
                float3 v;
                if (_OS_ArtPass < 1.5)
                    v = float3(n.x, n.z, n.y) * 0.5 + 0.5;
                else if (_OS_ArtPass < 2.5)
                {
                    float c = log2(1.0 + distance(p, _WorldSpaceCameraPos)) / 13.0;
                    v = float3(floor(c * 255.0) / 255.0, frac(c * 255.0), _Class / 255.0);
                }
                else if (_OS_ArtPass < 3.5)
                    v = (street + float3(0.0, 0.0, 32.0)) / 256.0;
                else if (_OS_ArtPass < 4.5)
                    v = frac(street);
                else
                    v = _Class > 1.5 && _Class < 2.5 ? float3(input.uv.z / 64.0, input.uv.w > 0.0 ? 1.0 : 0.0, 0.0)
                                                     : float3(frac(input.uv.xy), 0.0);
                return half4(Store(v), 1.0);
            }
            ENDHLSL
        }
    }
}
