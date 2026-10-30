// The growth's tufts (the art-direction page, The growth: heather and grass only where the record puts soil, spiky,
// varied silhouettes, never round blobs): small fans of tapered blades (blender/parts/growth/tufts.py), drawn many at a
// time through the growth's own BatchRendererGroup (Code/Scenes/Growth/GrowthDraw.cs), so DOTS instanced, each level
// crossfaded into the next (LOD_FADE_CROSSFADE), casting no shadows.
//
// Two ways to light them. _GT_SUN (a place lit by the scene's sun, as the street and the Holm tip are): as the house and
// the rock are lit, URP's PBR with the sun and its shadows, the sky from the scene's SH and the screen-space occlusion,
// the clump's dome its normal and its root in its own shade (the occlusion); _GT_Grey 1 draws its value alone (the P
// way, as the finish's P is untinted). Without it, as the painted corner's surface (removed) lit a face, from the page's
// globals: the sky by the normal, calmed toward one value; the lamps' pools, shadowed; each lamp's lit fog; and it
// answers _P_Mode as that surface did (1 the distance, 1, the veil, 1; 2 the slot; 3 the street point). Either way the
// normal is the clump's dome, so a tuft lights as one mass and both faces of a blade alike; dark at its root, its tip
// lighter (Ghost of Tsushima, Bad North). Where the ground's map is given (_GT_GroundOn), a tuft's root is the ground's
// colour under its foot, as Ghost of Tsushima's blades take the terrain's, so the turf and the ground it grows from are
// one mass and no tuft is a mark on it; _GT_UpNormal pulls the dome toward the ground's up (as stylised grass is lit,
// the sward's light the ground's), so a blade in the shade or the overcast is never darker than the ground under it
// but by its root's own shade. Its depth and normals are drawn too, so the screen-space occlusion sees it.
//
// Per instance (unity_RendererUserValue, the generator's): its rank in the low byte (which stay as the far ones thin), its
// hue in the next (one clump from the next, broad), and above them its damp (0 to 255: its tips toward _Damp, where the
// ground stays damp) or, in the corner, its habitat.
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
        _Damp ("Tip where damp (linear)", Color) = (0.11, 0.06, 0.04, 1)
        _Seed ("Seed fluff (linear)", Color) = (0.4, 0.38, 0.35, 1)
        _Hue ("One clump from the next", Float) = 0.05
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "Queue" = "Geometry" "OverstoryPaint" = "Own" }

        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

        CBUFFER_START(UnityPerMaterial)
            float4 _Base, _Tip, _Damp, _Seed;
            float _Hue;
        CBUFFER_END

        // the growth's own (set by the scene's builder, from packs/<pack>/growth.json, tufts)
        float4 _GT_Look;    // x calm (the sky's light toward one value), y the lamps' share, z the veil, w the root's sky
        float4 _GT_Thin;    // x thinning from (m), y the share kept at the far end, z how much the kept ones widen, w the shrink's band (rank)
        float4 _GT_LookB;   // x the tip's lift, y the clump's hue kept past the focus, z the wet share, w a blade's least width (px of a 1440-line frame)
        float _GT_Grey;     // 1: the value alone (the P way)
        float _GT_GroundOn; // 1: the root is the ground map's colour under the foot
        float _GT_UpNormal; // how far the clump's dome leans toward the world's up (0 the dome, 1 up)
        float4 _GT_GroundBox;   // the map's box in the world's x and z: its corner, then 1 over its size
        TEXTURE2D(_GT_GroundMap);
        SAMPLER(sampler_GT_GroundMap);

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
            nointerpolation float3 inst : TEXCOORD4;   // x the clump's hue (-0.5 to 0.5), y the crossfade, z its damp
            nointerpolation half3 root : TEXCOORD5;    // the root's colour (linear)
        };

        Varyings Vert(Attributes input)
        {
            UNITY_SETUP_INSTANCE_ID(input);
            Varyings o;
            uint user = unity_RendererUserValue;
            float rank = (user & 0xffu) / 255.0;
            float hue = ((user >> 8) & 0xffu) / 255.0 - 0.5;
            float damp = ((user >> 16) & 0xffu) / 255.0;
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
            o.normalWS = normalize(lerp(TransformObjectToWorldNormal(input.normalOS), float3(0.0, 1.0, 0.0), _GT_UpNormal));
            o.a = float4(input.uv0, input.uv1);
            o.b = input.uv2;
            float fade = 1.0;
        #if defined(LOD_FADE_CROSSFADE)
            fade = unity_LODFade.x;
        #endif
            o.inst = float3(hue, fade, damp);
            // the ground under the foot, a little blurred (its grain is the ground's own, not the tuft's)
            float2 guv = (pivot.xz - _GT_GroundBox.xy) * _GT_GroundBox.zw;
            o.root = _GT_GroundOn > 0.5 ? (half3)SAMPLE_TEXTURE2D_LOD(_GT_GroundMap, sampler_GT_GroundMap, guv, 3.0).rgb : (half3)_Base.rgb;
            return o;
        }

        // a level crossfading into the next: a stable screen dither (the fade's sign says which side keeps a pixel)
        void GT_Crossfade(Varyings i)
        {
            float f = i.inst.y;
            if (f < 0.999)
            {
                float dz = frac(52.9829189 * frac(dot(i.positionCS.xy, float2(0.06711056, 0.00583715))));
                clip(f > 0.0 ? f - dz : dz + f - 1e-4);
            }
        }
        ENDHLSL

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
            #pragma shader_feature_local _GT_SUN
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE
            #pragma multi_compile_fragment _ _SCREEN_SPACE_OCCLUSION
            #pragma multi_compile _ _ADDITIONAL_LIGHTS
            #pragma multi_compile_fragment _ _ADDITIONAL_LIGHT_SHADOWS
            #pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
            #pragma multi_compile _ _CLUSTER_LIGHT_LOOP
            #pragma multi_compile _ _LIGHT_LAYERS
            #pragma multi_compile_fog
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            // the page's (the painted corner's globals, as its surfaces read them)
            float4 _P_SkyUp, _P_SkySide, _P_SkyDown, _P_SkyKey, _P_SkyKeyDir, _P_Occlusion;
            float4 _P_Wet, _P_Pool, _P_Focus, _P_FocusShape;
            float4 _P_LampPos[8];
            float4 _P_LampFill[8];
            float _P_LampCount;
            float _P_Mode;

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
                GT_Crossfade(i);
                float3 p = i.positionWS;
                half3 n = (half3)normalize(i.normalWS);
                float up = saturate(i.a.y), height = saturate(i.b.y);
                // the blade: dark at its root, its tip lighter (greener where the ground stays damp); a pod its seed
                // fluff toward its tip
                half3 tip = lerp((half3)_Tip.rgb, (half3)_Damp.rgb, (half)i.inst.z);
                half3 albedo = lerp(i.root, tip, (half)pow(saturate(lerp(up, height, 0.5) * _GT_LookB.x), 0.8));
                if (i.b.x > 0.5)
                    albedo = lerp(tip, (half3)_Seed.rgb, (half)smoothstep(0.2, 0.9, up));
            #if defined(_GT_SUN)
                // one clump from the next: its value and warmth a little apart, broad
                albedo *= 1.0h + (half)(i.inst.x * _Hue * 2.0) * half3(1.2h, 1.0h, 0.6h);
                albedo = lerp(albedo, P_Luma(albedo).xxx, (half)_GT_Grey);
                InputData d = (InputData)0;
                d.positionWS = p;
                d.positionCS = i.positionCS;
                d.normalWS = n;
                d.viewDirectionWS = GetWorldSpaceNormalizeViewDir(p);
                d.shadowCoord = TransformWorldToShadowCoord(p);
                d.bakedGI = SampleSH(n);
                d.normalizedScreenSpaceUV = GetNormalizedScreenSpaceUV(i.positionCS);
                d.shadowMask = half4(1, 1, 1, 1);
                d.fogCoord = ComputeFogFactor(i.positionCS.z);
                SurfaceData s = (SurfaceData)0;
                s.albedo = albedo;
                s.smoothness = 0.12h;
                // the root in its own shade: the sky it sees, from the root's share at the foot to all of it at the top
                s.occlusion = lerp((half)_GT_Look.w, 1.0h, (half)height);
                s.alpha = 1;
                s.normalTS = half3(0, 0, 1);
                half4 c = UniversalFragmentPBR(d, s);
                c.rgb = MixFog(c.rgb, d.fogCoord);
                return float4(c.rgb, 1.0);
            #else
                if (_P_Mode > 2.5)
                    return float4(p.x, p.z, p.y, n.y);
                if (_P_Mode > 1.5)
                    return float4(63.0 * 4.0 / 255.0, 10.0 * 16.0 / 255.0, 0.0, 1.0);
                if (_P_Mode > 0.5)
                    return float4(distance(p, _WorldSpaceCameraPos), 1.0, _GT_Look.z, 1.0);

                half detail = 1.0h - (half)smoothstep(_P_Focus.w, _P_FocusShape.x, distance(p, _P_Focus.xyz));
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
            #endif
            }
            ENDHLSL
        }

        Pass
        {
            Name "DepthOnly"
            Tags { "LightMode" = "DepthOnly" }
            Cull Off
            ZWrite On
            ColorMask R

            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex Vert
            #pragma fragment FragDepth
            #pragma multi_compile _ DOTS_INSTANCING_ON
            #pragma multi_compile _ LOD_FADE_CROSSFADE

            half FragDepth(Varyings i) : SV_Target
            {
                GT_Crossfade(i);
                return i.positionCS.z;
            }
            ENDHLSL
        }

        Pass
        {
            Name "DepthNormals"
            Tags { "LightMode" = "DepthNormals" }
            Cull Off
            ZWrite On

            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex Vert
            #pragma fragment FragNormals
            #pragma multi_compile _ DOTS_INSTANCING_ON
            #pragma multi_compile _ LOD_FADE_CROSSFADE
            #pragma multi_compile_fragment _ _GBUFFER_NORMALS_OCT
            #if defined(_GBUFFER_NORMALS_OCT)
                #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/Packing.hlsl"
            #endif

            half4 FragNormals(Varyings i) : SV_Target
            {
                GT_Crossfade(i);
                half3 n = (half3)normalize(i.normalWS);
            #if defined(_GBUFFER_NORMALS_OCT)
                float2 oct = PackNormalOctQuadEncode(n);
                return half4(PackFloat2To888(saturate(oct * 0.5 + 0.5)), 0.0);
            #else
                return half4(n, 0.0);
            #endif
            }
            ENDHLSL
        }
    }
}
