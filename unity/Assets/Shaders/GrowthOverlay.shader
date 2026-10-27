// The growth laid over the painted corner (LT1CornerGrowth), until the corner's hook draws it in the surfaces
// themselves: the same rock and stone meshes drawn again, after the painted surfaces, through the growth's own
// BatchRendererGroup (Code/Scenes/Growth/GrowthDraw.cs), multiplying the colour by the albedo's ratio the growth makes
// (Shaders/GrowthPaint.hlsl). Only in the colour pass (_P_Mode 0): the air's passes are the surfaces' own.
//
// _Source 0: a mesh on the Stone contract (UV0 metres in its own plane, UV3.x its sky, UV4.y the lichen's years / 200,
// UV5.x the moss): the gully's stones, and the rock once it is built. 1: the clay knuckle (a stand-in until the rock and
// ground's rock lands): its potentials from on_rock's rules here, per pixel, inside _StandBox only.
Shader "Hidden/Overstory/GrowthOverlay"
{
    Properties
    {
        _Source ("0 the Stone contract, 1 the clay stand-in", Float) = 0
        _StandMin ("Stand-in: the box's min (world)", Vector) = (0, 0, 0, 0)
        _StandMax ("Stand-in: the box's max (world)", Vector) = (0, 0, 0, 0)
        _StandFloor ("Stand-in: x the street's ground under (world y), y a floor's normal up, z the soil on top over (world y)", Vector) = (0, 1, 1000, 0)
        _StandRule ("Stand-in: x overhang, y full rain, z the sky's power, w the lichen's years / 200", Vector) = (-0.35, 0.1, 0.7, 0)
        _StandFoot ("Stand-in: x the foot (world y), y z lichen from to full (m), w moss gone (m)", Vector) = (0, 0.15, 0.45, 0.4)
        _StandMoss ("Stand-in: x the foot's moss", Float) = 0.8
        _StandOpen ("Stand-in: the lichen thins below the crest: full to y m under the top, z of it from x m under", Vector) = (0.5, 8, 0.5, 0)
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "Queue" = "Geometry+10" "OverstoryPaint" = "Own" }

        Pass
        {
            Name "GrowthOverlay"
            Tags { "LightMode" = "UniversalForward" }
            ZWrite Off
            ZTest LEqual
            Offset -1, -1
            Cull Back
            Blend DstColor Zero

            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile _ DOTS_INSTANCING_ON
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Assets/Shaders/GrowthPaint.hlsl"

            CBUFFER_START(UnityPerMaterial)
                float _Source;
                float4 _StandMin, _StandMax, _StandFloor, _StandRule, _StandFoot, _StandOpen;
                float _StandMoss;
            CBUFFER_END

            float _P_Mode;
            float4 _P_Focus, _P_FocusShape;

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv0 : TEXCOORD0;
                float2 uv3 : TEXCOORD3;
                float2 uv4 : TEXCOORD4;
                float2 uv5 : TEXCOORD5;
                half4 color : COLOR;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float3 normalWS : TEXCOORD1;
                float2 uv0 : TEXCOORD2;
                float4 g : TEXCOORD3;   // x the sky, y the lichen, z the moss
            };

            Varyings Vert(Attributes input)
            {
                UNITY_SETUP_INSTANCE_ID(input);
                Varyings o;
                o.positionWS = TransformObjectToWorld(input.positionOS.xyz);
                o.positionCS = TransformWorldToHClip(o.positionWS);
                o.normalWS = TransformObjectToWorldNormal(input.normalOS);
                o.uv0 = input.uv0;
                o.g = _Source > 0.5 ? float4(input.color.r, 0, 0, 0) : float4(input.uv3.x, input.uv4.y, input.uv5.x, 0);
                return o;
            }

            float GP_Ramp(float x, float a, float b) { return saturate((x - a) / (b - a)); }

            half4 Frag(Varyings i) : SV_Target
            {
                if (_P_Mode > 0.5)
                    discard;
                float3 p = i.positionWS;
                float3 n = normalize(i.normalWS);
                float lichen = i.g.y, moss = i.g.z;
                float2 q = i.uv0;
                if (_Source > 0.5)
                {
                    // the clay knuckle, a stand-in: on_rock's rules per pixel (no joints: the clay has none), its own
                    // plane from the way it faces
                    if (any(p < _StandMin.xyz) || any(p > _StandMax.xyz))
                        discard;
                    // the street's ground below it and the soil on its top (D's yard) take none
                    if (n.y > _StandFloor.y && (p.y < _StandFloor.x || p.y > _StandFloor.z))
                        discard;
                    // the crusts in the plane of the face the clay's facets make up: a sloping facet takes its wall's
                    // plane, so a crust runs on across the fold (only a near-flat top takes its own)
                    float3 a = abs(n);
                    q = a.y > 0.8 ? p.xz : (a.x >= a.z ? p.zy : p.xy);
                    float foot = p.y - _StandFoot.x;
                    // the clay is flat-shaded, so a facet's tilt jumps at its edge: only an overhang sheds the rain
                    // here (on the rock, the rule's whole ramp, per vertex)
                    float washed = GP_Ramp(n.y, _StandRule.x, _StandRule.x + 0.25) * GP_Ramp(foot, _StandFoot.y, _StandFoot.z);
                    // the clay's sky bake is coarse (a value a facet): the crest is the open, dry, clean part, and the
                    // lichen thins down the face toward the street (splashed, shaded, touched)
                    float open = lerp(_StandOpen.z, 1.0, 1.0 - GP_Ramp(_StandFloor.z - p.y, _StandOpen.y, _StandOpen.x));
                    lichen = _StandRule.w * (0.35 + 0.65 * pow(saturate(i.g.x), _StandRule.z)) * washed * open;
                    moss = _StandMoss * (1.0 - GP_Ramp(foot, 0.0, _StandFoot.w));
                    lichen *= 1.0 - 0.8 * moss;
                }
                half detail = 1.0h - (half)smoothstep(_P_Focus.w, _P_FocusShape.x, distance(p, _P_Focus.xyz));
                float pxm = length(fwidth(p)) * 0.7;
                half3 r = GP_GrowthRatio(lichen, moss, q, detail, pxm);
                return half4(r, 1.0h);
            }
            ENDHLSL
        }
    }
}
