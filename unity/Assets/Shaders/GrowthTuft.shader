// The growth's tufts in the painted corner (the art-direction page, The growth: heather and grass only where the record
// puts soil, spiky, varied silhouettes, never round blobs): small fans of tapered blades (blender/parts/growth/tufts.py),
// drawn many at a time through the growth's own BatchRendererGroup (Code/Scenes/Growth/GrowthDraw.cs), so DOTS
// instanced, each level crossfaded into the next (LOD_FADE_CROSSFADE), casting no shadows.
//
// Lit as the painted surface lights a face (ArtDirection/PaintSurface.shader, from the page's globals): the sky by the
// normal, calmed toward one value; the lamps' pools, shadowed; each lamp's lit fog. The normal is the clump's dome, so a
// tuft lights as one mass and both faces of a blade alike; dark at its root, its tip lighter (Ghost of Tsushima, Bad
// North). It answers _P_Mode as PaintSurface does (1 the distance, 1, the veil, 1; 2 the slot; 3 the street point).
//
// Per instance (unity_RendererUserValue, the generator's): its rank in the low byte (which stay as the far ones thin), its
// hue in the next (one clump from the next, broad), its habitat above.
//
// Mesh: uv0 x across the blade (-1 to 1), y up it (0 root, 1 tip); uv1 x how far out from the clump's middle, y the
// blade's seed; uv2 x 0 a blade, 1 a seed pod, y the height over the tuft's height; uv3 xy, uv4 x the point on the
// blade's middle line the vertex stands across from, uv4 y the blade's half width at its root.
Shader "Hidden/Overstory/GrowthTuft"
{
    Properties
    {
        _Base ("Root (linear)", Color) = (0.03, 0.02, 0.016, 1)
        _Tip ("Tip (linear)", Color) = (0.11, 0.06, 0.04, 1)
        _Seed ("Seed fluff (linear)", Color) = (0.4, 0.38, 0.35, 1)
        _Hue ("One clump from the next", Float) = 0.05
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "Queue" = "Geometry" "OverstoryPaint" = "Own" }

        Pass
        {
            Name "GrowthTuft"
            Tags { "LightMode" = "UniversalForward" }
            Cull Off

            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile _ DOTS_INSTANCING_ON
            #pragma multi_compile _ LOD_FADE_CROSSFADE
            #pragma multi_compile _ _ADDITIONAL_LIGHTS
            #pragma multi_compile_fragment _ _ADDITIONAL_LIGHT_SHADOWS
            #pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
            #pragma multi_compile _ _CLUSTER_LIGHT_LOOP
            #pragma multi_compile _ _LIGHT_LAYERS
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            CBUFFER_START(UnityPerMaterial)
                float4 _Base, _Tip, _Seed;
                float _Hue;
            CBUFFER_END

            // the growth's own (LT1CornerGrowth, from packs/<pack>/growth.json, tufts)
            float4 _GT_Look;    // x calm (the sky's light toward one value), y the lamps' share, z the veil, w the root's sky
            float4 _GT_Thin;    // x thinning from (m), y the share kept at the far end, z how much the kept ones widen, w the shrink's band (rank)
            float4 _GT_LookB;   // x the tip's lift, y the clump's hue kept past the focus, z the wet share, w a blade's least width (px of a 1440-line frame)

            // the page's (Paint.json's globals, as PaintSurface reads them)
            float4 _P_SkyUp, _P_SkySide, _P_SkyDown, _P_SkyKey, _P_SkyKeyDir, _P_Occlusion;
            float4 _P_Wet, _P_Pool, _P_Focus, _P_FocusShape;
            float4 _P_LampPos[8];
            float4 _P_LampFill[8];
            float _P_LampCount;
            float _P_Mode;

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv0 : TEXCOORD0;
                float2 uv1 : TEXCOORD1;
                float2 uv2 : TEXCOORD2;
                float2 uv3 : TEXCOORD3;
                float2 uv4 : TEXCOORD4;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float3 normalWS : TEXCOORD1;
                float4 a : TEXCOORD2;   // uv0, uv1
                float2 b : TEXCOORD3;   // uv2
                nointerpolation float2 inst : TEXCOORD4;   // x the clump's hue (-0.5 to 0.5), y the crossfade
            };

            Varyings Vert(Attributes input)
            {
                UNITY_SETUP_INSTANCE_ID(input);
                Varyings o;
                uint user = unity_RendererUserValue;
                float rank = (user & 0xffu) / 255.0;
                float hue = ((user >> 8) & 0xffu) / 255.0 - 0.5;
                float3 pivot = TransformObjectToWorld(float3(0.0, 0.0, 0.0));
                float d = distance(pivot, _WorldSpaceCameraPos);
                // far off only the low ranks stay (GrowthDraw): those kept widen to keep the cover, and each shrinks
                // away as the share kept passes its rank, so none pops
                float keep = d > _GT_Thin.x ? max(_GT_Thin.y, _GT_Thin.x / d) : 1.0;
                float wide = lerp(1.0, _GT_Thin.z, saturate((1.0 - keep) / max(1.0 - _GT_Thin.y, 1e-3)));
                float shrink = saturate((keep - rank) / max(_GT_Thin.w, 1e-3));
                float3 pos = input.positionOS.xyz;
                // a far blade keeps a least width on screen (of a 1440-line frame), widened about its middle line, so
                // its spike holds and never breaks into specks
                float3 mid = float3(input.uv3.x, input.uv3.y, input.uv4.x);
                float scale = length(TransformObjectToWorldDir(float3(1.0, 0.0, 0.0), false));
                float pxm = d * 2.0 / (abs(UNITY_MATRIX_P[1][1]) * 1440.0);
                pos = mid + (pos - mid) * max(1.0, 0.5 * _GT_LookB.w * pxm / max(input.uv4.y * scale, 1e-5));
                pos.xz *= wide;
                pos *= shrink;
                o.positionWS = TransformObjectToWorld(pos);
                o.positionCS = TransformWorldToHClip(o.positionWS);
                o.normalWS = TransformObjectToWorldNormal(input.normalOS);
                o.a = float4(input.uv0, input.uv1);
                o.b = input.uv2;
                float fade = 1.0;
            #if defined(LOD_FADE_CROSSFADE)
                fade = unity_LODFade.x;
            #endif
                o.inst = float2(hue, fade);
                return o;
            }

            half P_Luma(half3 c) { return dot(c, half3(0.2126h, 0.7152h, 0.0722h)); }

            float3 GT_LightPosition(uint lightIndex)
            {
            #if USE_CLUSTER_LIGHT_LOOP
                int li = (int)lightIndex;
            #else
                int li = GetPerObjectLightIndex(lightIndex);
            #endif
            #if USE_STRUCTURED_BUFFER_FOR_LIGHT_DATA
                return _AdditionalLightsBuffer[li].position.xyz;
            #else
                return _AdditionalLightsPosition[li].xyz;
            #endif
            }

            float4 Frag(Varyings i) : SV_Target
            {
                // a level crossfading into the next: a stable screen dither (the fade's sign says which side keeps a pixel)
                float f = i.inst.y;
                if (f < 0.999)
                {
                    float dz = frac(52.9829189 * frac(dot(i.positionCS.xy, float2(0.06711056, 0.00583715))));
                    clip(f > 0.0 ? f - dz : dz + f - 1e-4);
                }
                float3 p = i.positionWS;
                half3 n = (half3)normalize(i.normalWS);
                if (_P_Mode > 2.5)
                    return float4(p.x, p.z, p.y, n.y);
                if (_P_Mode > 1.5)
                    return float4(63.0 * 4.0 / 255.0, 10.0 * 16.0 / 255.0, 0.0, 1.0);
                if (_P_Mode > 0.5)
                    return float4(distance(p, _WorldSpaceCameraPos), 1.0, _GT_Look.z, 1.0);

                half detail = 1.0h - (half)smoothstep(_P_Focus.w, _P_FocusShape.x, distance(p, _P_Focus.xyz));
                float up = saturate(i.a.y), height = saturate(i.b.y);
                // the blade: dark at its root, its tip lighter; a pod its seed fluff toward its tip
                half3 albedo = lerp((half3)_Base.rgb, (half3)_Tip.rgb, (half)pow(saturate(lerp(up, height, 0.5) * _GT_LookB.x), 0.8));
                if (i.b.x > 0.5)
                    albedo = lerp((half3)_Tip.rgb, (half3)_Seed.rgb, (half)smoothstep(0.2, 0.9, up));
                // one clump from the next: its value and warmth a little apart, broad (kept less past the focus)
                half h = (half)(i.inst.x * _Hue * 2.0) * lerp((half)_GT_LookB.y, 1.0h, detail);
                albedo *= 1.0h + h * half3(1.2h, 1.0h, 0.6h);
                // the wet film darkens what the drizzle reaches
                half wetUp = saturate((n.y - (half)_P_Wet.y) / max((half)(_P_Wet.z - _P_Wet.y), 1e-3h));
                albedo *= 1.0h - (half)_P_Wet.w * (half)_P_Wet.x * wetUp * (half)_GT_LookB.z;

                // the sky's light by the clump's normal, calmed toward one value; the root in its own shade
                half calm = (half)_GT_Look.x;
                half3 E = n.y >= 0.0h ? lerp((half3)_P_SkySide.rgb, (half3)_P_SkyUp.rgb, n.y)
                                      : lerp((half3)_P_SkySide.rgb, (half3)_P_SkyDown.rgb, -n.y);
                E += (half3)_P_SkyKey.rgb * pow(saturate(dot((float3)n, _P_SkyKeyDir.xyz) * 0.5 + 0.5), _P_SkyKey.w);
                half3 flat = (half3)_P_SkySide.rgb + (half3)_P_SkyKey.rgb * (half)pow(0.5, _P_SkyKey.w);
                E = lerp(E, flat, calm);
                half sky = lerp((half)_GT_Look.w, 1.0h, (half)height);
                E *= lerp(1.0h, sky, (half)_P_Occlusion.x * (1.0h - calm));

                // the lamps: a compact pool each, shadowed
                half3 lamps = 0.0h;
                InputData inputData = (InputData)0;
                inputData.positionWS = p;
                inputData.normalizedScreenSpaceUV = GetNormalizedScreenSpaceUV(i.positionCS);
            #if defined(_ADDITIONAL_LIGHTS) || defined(_CLUSTER_LIGHT_LOOP)
                uint count = GetAdditionalLightsCount();
                LIGHT_LOOP_BEGIN(count)
                    Light l = GetAdditionalLight(lightIndex, p, half4(1, 1, 1, 1));
                    float3 lp = GT_LightPosition(lightIndex);
                    float3 L = lp - p;
                    float dl = length(L);
                    float3 Ld = L / max(dl, 1e-4);
                    half fall = (half)pow(saturate(1.0 - dl / _P_Pool.w), _P_Pool.x);
                    fall *= (half)saturate((lp.y + _P_Pool.z - p.y) / max(_P_Pool.z, 0.05));
                    half ndl = saturate((dot((float3)n, Ld) + (half)_P_Pool.y) / (1.0h + (half)_P_Pool.y));
                    lamps += l.color * (fall * ndl * l.shadowAttenuation);
                LIGHT_LOOP_END
            #endif
                half3 fill = 0.0h;
                for (int k = 0; k < (int)_P_LampCount; k++)
                {
                    float3 dv = (float3)_P_LampPos[k].xyz - p;
                    float r = max(_P_LampFill[k].w, 1e-3);
                    fill += (half3)_P_LampFill[k].rgb * (half)exp(-dot(dv, dv) / (r * r));
                }
                half B = (half)_GT_Look.y;
                return float4(albedo * (E + fill * B + lamps * B), 1.0);
            }
            ENDHLSL
        }
    }
}
