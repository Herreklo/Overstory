// Stone: the town's laid stone (blender/generators/stone.py; docs/stone.md), lit exactly as the street is (look P,
// the sky term from the bake, the town's sky map, the air), drawn by the history layers each from its fact: the
// rock's own pigment and grain, its weathering with the years, the polish and hollow its footfall wore, lichen grown
// for as many years as a place has been quiet and moss where it is damp and sheltered (nature's growth layer,
// Growth.hlsl, the species the pack's), and the weather (wet stone dark
// and glossy, water standing where it is hollow).
//
// Vertex data (stone.py): UV4 x polish, y lichen years / 200; UV5 x moss, y water held; UV0 the grain (the top in
// metres, the split faces round and up); UV1 x years since its surface was bare (laid, cast) / 200, y a seed for the
// piece; UV2 x the face (0 top, 1 rounded edge, 2 split face, 3 bed; 4 cement pointing, 5 a cement dab, 6 a joint's soil), y the
// slab's variation; UV3 the bake (x sky, y ground).
Shader "Overstory/Stone"
{
    Properties
    {
        _Stone ("The rock's pigment, weathered (eye colour)", Color) = (0.36, 0.37, 0.39, 1)
        _Fresh ("The rock freshly split, unweathered", Color) = (0.25, 0.27, 0.30, 1)
        _Edge ("Its split faces: the laminae, a little warmer", Color) = (0.38, 0.37, 0.36, 1)
        _GrainMap ("The rock's painted grain (r a bedding plane's lightness, g its relief, b a split face's lightness, a its relief; a metre a tile)", 2D) = "grey" {}
        _Grain ("Grain: x the bedding plane's contrast, y the split face's, z per-piece value, w per-piece hue", Vector) = (1.0, 1.0, 0.10, 0)
        _Weather ("Years for the rock to weather to its pigment", Float) = 60
        _Polish ("Polish: x how much darker the worn skin, y its smoothness", Vector) = (0.18, 0.42, 0, 0)
        _Relief ("Relief: x the grain's depth (m), y lichen's crust (m)", Vector) = (0.0015, 0.0012, 0, 0)
        _Porosity ("How much the rock darkens wet (0 to 1)", Range(0, 1)) = 0.55
        _Cement ("Cement the day it was struck", Color) = (0.70, 0.69, 0.66, 1)
        _CementOld ("Cement after forty years of weather and grime", Color) = (0.50, 0.50, 0.48, 1)
        _CementFilm ("The algae film on damp cement", Color) = (0.24, 0.27, 0.21, 1)
        _Soil ("The soil a joint holds where its pointing has gone", Color) = (0.17, 0.15, 0.12, 1)
        [Toggle] _Grey ("Grey light: every layer's pigment one grey (to judge form)", Float) = 0
        _History ("Debug: show the history as colour (r polish, g lichen years, b moss)", Float) = 0
    }

    HLSLINCLUDE
    #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

    CBUFFER_START(UnityPerMaterial)
        half4 _Stone;
        half4 _Fresh;
        half4 _Edge;
        float4 _Grain;
        float _Weather;
        float4 _Polish;
        float4 _Relief;
        half _Porosity;
        half4 _Cement;
        half4 _CementOld;
        half4 _CementFilm;
        half4 _Soil;
        half _Grey;
        half _History;
    CBUFFER_END

    #include "StreetSurface.hlsl"
    #include "Growth.hlsl"

    TEXTURE2D(_GrainMap); SAMPLER(sampler_GrainMap);

    // The light bent by a height on the surface (the surface gradient, from screen derivatives).
    half3 OS_BumpStone(float3 positionWS, half3 n, float height)
    {
        float3 dpdx = ddx(positionWS), dpdy = ddy(positionWS);
        float dhdx = ddx(height), dhdy = ddy(height);
        float3 r1 = cross(dpdy, n), r2 = cross(n, dpdx);
        float det = dot(dpdx, r1);
        float3 grad = (det < 0 ? -1.0 : 1.0) * (dhdx * r1 + dhdy * r2);
        return normalize(abs(det) * n - grad);
    }

    struct StoneOut
    {
        half3 albedo;
        half smoothness;
        half height;       // for the bump
        half growth;       // how much growth covers it (stays matt when wet)
    };

    StoneOut OS_StoneSurface(float2 g, half4 hist, half kind, half years, half var, float3 positionWS, half sky)
    {
        StoneOut o;
        half face = step(1.5h, kind) * step(kind, 2.5h);
        // the grain: on a bedding plane a soft mottle and a faint streak; on a split face thin stacked laminae
        float2 q = g;
        // the grain, painted at our scale (blender/parts/stone/slate/paint.py): a bedding plane's or a split face's
        // lightness and relief, in the piece's own plane at its own offset and turn
        half4 gm = SAMPLE_TEXTURE2D(_GrainMap, sampler_GrainMap, q);
        half tone = lerp((gm.r - 0.5h) * (half)_Grain.x, (gm.b - 0.5h) * (half)_Grain.y, face);
        half relief = lerp(gm.g, gm.a, face) - 0.5h;
        // iron in the rock rusting in sparse spots (the stone's own texture, claiming nothing)
        half rust = smoothstep(0.74h, 0.8h, (half)OS_Noise(q * 9.0 + var * 41.0)) * smoothstep(0.45h, 0.6h, (half)OS_Noise(q * 47.0));
        half3 rock = lerp(_Stone.rgb, _Edge.rgb, face * 0.7h);
        // weathering: fresh rock dark and blue, weathered to its paler grey skin over the years
        rock = lerp(_Fresh.rgb, rock, saturate(years / _Weather));
        rock *= saturate(1.0h + tone * 2.0h + ((half)var - 0.5h) * (half)_Grain.z * 2.0h);
        rock = lerp(rock, rock * half3(1.18h, 0.98h, 0.80h), rust * 0.6h);
        // each piece its own hue where the stone is mixed (rubble: rusty, greenish, blue-grey; a quarry's chosen slabs
        // stay one rock, w = 0)
        half hp = frac((half)var * 7.13h);
        half3 tint = hp < 0.25h ? half3(1.12h, 0.99h, 0.86h) : (hp < 0.5h ? half3(0.96h, 1.02h, 0.95h)
                   : (hp < 0.75h ? half3(0.95h, 0.98h, 1.05h) : half3(1.0h, 1.0h, 1.0h)));
        rock *= lerp(half3(1.0h, 1.0h, 1.0h), tint, (half)_Grain.w);
        // polish: the weathered skin worn off where feet go, the rock beneath darker and smoother
        rock *= 1.0h - (half)_Polish.x * hist.r;
        half smooth = lerp(0.14h, (half)_Polish.y, hist.r);
        // relief: the painted grain's, smoothed where feet have polished it
        // (a split face is rough: its plates stand proud by several millimetres, so raking light breaks it into small
        // lights and shadows; as shallow as a bedding plane, the block fronts read as smooth wooden planks)
        // (the grain's relief is near detail: from the street stop up it read as sandpaper over every face)
        half nearS = OS_Near(max(length(ddx(positionWS)), length(ddy(positionWS))));
        half h = relief * (1.0h - hist.r * 0.7h) * lerp(0.3h, 1.0h, nearS);

        // cement, a repair's own material and date (kind 4 pointing, 5 a dab; upkeep.py, docs/upkeep.md): pale and
        // warm the day it was struck, its sand showing; greyer with grime over the years, a film of algae where it
        // stays damp, fine crazing; pointing crumbling out of its joint with the years, the soil behind showing (and
        // the moss taking it) where it has gone
        half moss = hist.b;
        if (kind > 5.5h)
        {
            // a joint's filling (kind 6): soil washed in and held there, damp, the moss's own ground
            half crumb = (half)OS_Noise(q * 90.0 + var * 13.0);
            rock = _Soil.rgb * (0.8h + 0.4h * crumb);
            smooth = 0.12h;
            h = (crumb - 0.5h) * 0.6h;
            moss = saturate(hist.b * 1.3h);
        }
        else if (kind > 3.5h)
        {
            // near, its sand and its fine crazing; further off its value and its age only (they speckle from afar)
            half nearC = OS_Near(max(length(ddx(positionWS)), length(ddy(positionWS))));
            half sand = lerp(0.5h, (half)OS_Noise(q * 260.0 + var * 17.0), nearC);
            // (on this coast grime and a film come in a few years: half grey by six, near its old grey by twenty)
            half grime = 1.0h - exp(-years / 9.0h);
            half3 cem = lerp(_Cement.rgb, _CementOld.rgb, grime) * (0.9h + 0.2h * sand);
            half film = saturate(hist.b * 1.6h) * grime * smoothstep(0.3h, 0.7h, (half)OS_Noise(q * 12.0 + var * 5.0));
            cem = lerp(cem, _CementFilm.rgb, film * 0.7h);
            half craze = smoothstep(0.03h, 0.0h, abs((half)OS_Noise(q * 38.0 + var * 9.0) - 0.5h)) * grime * nearC;
            cem *= 1.0h - 0.25h * craze;
            half lost = 0.0h;
            if (kind < 4.5h)
            {
                half share = saturate((years - 6.0h) / 60.0h) * 0.6h;
                half nz = (half)(OS_Noise(q * 11.0 + var * 3.0) * 0.65 + OS_Noise(q * 37.0 + var) * 0.35);
                lost = 1.0h - smoothstep(share - 0.03h, share + 0.03h, nz);
            }
            rock = lerp(cem, _Soil.rgb, lost);
            smooth = 0.1h;
            h = (sand - 0.5h) * 0.3h - craze * 0.4h - lost * 0.8h;
            moss = saturate(hist.b * (0.5h + 1.2h * lost));
        }

        // growth: nature's thin layer (Growth.hlsl), from where and how long the stone's facts give
        OSGrowth gr = OS_GrowthLayer(rock, smooth, q, hist.g * 200.0h, moss, sky, var, positionWS);
        rock = gr.albedo;
        smooth = gr.smoothness;
        h += gr.height * (half)(_Relief.y / max(_Relief.x, 1e-5));

        o.albedo = rock;
        o.smoothness = smooth;
        o.height = h;
        o.growth = gr.cover;
        return o;
    }
    ENDHLSL

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "Queue" = "Geometry" }

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode" = "UniversalForward" }

            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_fragment _ _OS_LOOK_B _OS_LOOK_D _OS_LOOK_P
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE
            #pragma multi_compile _ _ADDITIONAL_LIGHTS
            #pragma multi_compile_fragment _ _ADDITIONAL_LIGHT_SHADOWS
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BLENDING
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BOX_PROJECTION
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_ATLAS
            #pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
            #pragma multi_compile_fragment _ _SCREEN_SPACE_OCCLUSION
            #pragma multi_compile _ _LIGHT_LAYERS
            #pragma multi_compile _ _CLUSTER_LIGHT_LOOP
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/RenderingLayers.hlsl"
            #pragma multi_compile_instancing

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            // a third of the screen's occlusion (its reach is set for walls: in a flight of 17 cm rises it darkened every
            // riser and every tread's back to near black); the stone's own shade under a nosing is baked
            #define OS_OCCLUSION 0.2h
            #include "StreetLooks.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv : TEXCOORD0;
                float2 uv1 : TEXCOORD1;
                float2 uv2 : TEXCOORD2;
                float2 uv3 : TEXCOORD3;
                float2 uv4 : TEXCOORD4;
                float2 uv5 : TEXCOORD5;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 positionWS : TEXCOORD1;
                half3 normalWS : TEXCOORD2;
                half4 history : TEXCOORD3;
                float4 piece : TEXCOORD4;    // x years / 200, y seed, z face, w variation
                float2 bake : TEXCOORD5;
                UNITY_VERTEX_INPUT_INSTANCE_ID
                UNITY_VERTEX_OUTPUT_STEREO
            };

            Varyings Vert(Attributes input)
            {
                Varyings o = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, o);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
                VertexPositionInputs p = GetVertexPositionInputs(input.positionOS.xyz);
                o.positionCS = p.positionCS;
                o.positionWS = p.positionWS;
                o.normalWS = TransformObjectToWorldNormal(input.normalOS);
                o.uv = input.uv;
                o.history = half4(input.uv4, input.uv5);
                o.piece = float4(input.uv1, input.uv2);
                o.bake = input.uv3;
                return o;
            }

            void Frag(Varyings input, out half4 outColor : SV_Target0
            #ifdef _WRITE_RENDERING_LAYERS
                , out uint outRenderingLayers : SV_Target1
            #endif
            )
            {
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(input);
                half3 n = normalize(input.normalWS);
                half years = (half)input.piece.x * 200.0h;
                half town = OS_TownSky(input.positionWS, n);
                StoneOut so = OS_StoneSurface(input.uv, input.history, (half)input.piece.z, years, (half)input.piece.w,
                                              input.positionWS, town);
                n = OS_BumpStone(input.positionWS, n, so.height * (half)_Relief.x);

                StreetSurface s;
                s.albedo = _Grey > 0.5 ? half3(0.42h, 0.42h, 0.42h) : so.albedo;
                s.emission = 0;
                s.metallic = 0;
                s.smoothness = so.smoothness;
                s.normalWS = n;
                // the weather: rain wets what faces the sky, the rock darkening by its porosity and glossing; water
                // stands where it is hollow and in the back corners
                half up = n.y;
                half wet = (half)_OS_Wetness * saturate((up + 0.1h) / 0.6h);
                // moss and lichen soak it up: darker a little, never glossy
                s.albedo *= lerp(1.0h, 1.0h - 0.5h * lerp(_Porosity, _Porosity * 0.9h, so.growth), wet);
                // wet slate glosses where feet polished it; its rough skin elsewhere only a little
                s.smoothness = lerp(s.smoothness, max(s.smoothness, lerp(0.3h, 0.85h, input.history.r)), wet * (1.0h - so.growth));
                half pool = smoothstep(0.5h, 0.85h, input.history.a) * saturate((half)_OS_Wetness * 1.5h - 0.4h) * step(0.8h, up);
                s.albedo = lerp(s.albedo, s.albedo * 0.7h, pool);
                s.smoothness = lerp(s.smoothness, 0.96h, pool);
                s.normalWS = normalize(lerp(s.normalWS, half3(0, 1, 0), pool));

                InputData id = (InputData)0;
                id.positionWS = input.positionWS;
                id.positionCS = input.positionCS;
                id.normalWS = s.normalWS;
                id.viewDirectionWS = GetWorldSpaceNormalizeViewDir(input.positionWS);
            #if defined(MAIN_LIGHT_CALCULATE_SHADOWS)
                id.shadowCoord = TransformWorldToShadowCoord(input.positionWS);
            #endif
                id.normalizedScreenSpaceUV = GetNormalizedScreenSpaceUV(input.positionCS);
                id.shadowMask = half4(1, 1, 1, 1);
                OSBake b = OS_ReadBake(half4((half)input.bake.x, (half)input.bake.y, 1.0h, 1.0h));
                b.town = town;
            #if defined(_OS_LOOK_B)
                half3 colour = OS_ShadeB(id, s, b, input.positionWS);
            #elif defined(_OS_LOOK_D)
                half3 colour = OS_ShadeD(id, s, b, input.positionWS);
            #elif defined(_OS_LOOK_P)
                half3 colour = OS_ShadeP(id, s, b, input.positionWS);
            #else
                half3 colour = OS_ShadeA(id, s, b);
            #endif
                colour = OS_Atmosphere(colour, input.positionWS);
                if (_History > 2.5)
                    colour = normalize(input.normalWS) * 0.5h + 0.5h;
                else if (_History > 1.5)
                    colour = so.albedo * 0.6h;
                else if (_History > 0.5)
                    colour = input.piece.z > 3.5 ? half3(0.9h, 0.45h, 0.0h)
                                                 : half3(input.history.r, input.history.g * 2.0h, input.history.b) * 0.5h;
                outColor = half4(colour, 1);
            #ifdef _WRITE_RENDERING_LAYERS
                outRenderingLayers = EncodeMeshRenderingLayer();
            #endif
            }

            ENDHLSL
        }

        Pass
        {
            Name "ShadowCaster"
            Tags { "LightMode" = "ShadowCaster" }
            ZWrite On
            ZTest LEqual
            ColorMask 0

            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_instancing
            #pragma multi_compile_vertex _ _CASTING_PUNCTUAL_LIGHT_SHADOW
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Shadows.hlsl"

            float3 _LightDirection;
            float3 _LightPosition;

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            float4 Vert(Attributes input) : SV_POSITION
            {
                UNITY_SETUP_INSTANCE_ID(input);
                float3 positionWS = TransformObjectToWorld(input.positionOS.xyz);
                float3 normalWS = TransformObjectToWorldNormal(input.normalOS);
            #if _CASTING_PUNCTUAL_LIGHT_SHADOW
                float3 lightDirectionWS = normalize(_LightPosition - positionWS);
            #else
                float3 lightDirectionWS = _LightDirection;
            #endif
                float4 positionCS = TransformWorldToHClip(ApplyShadowBias(positionWS, normalWS, lightDirectionWS));
            #if UNITY_REVERSED_Z
                positionCS.z = min(positionCS.z, UNITY_NEAR_CLIP_VALUE);
            #else
                positionCS.z = max(positionCS.z, UNITY_NEAR_CLIP_VALUE);
            #endif
                return positionCS;
            }

            half4 Frag() : SV_Target { return 0; }
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
            #pragma multi_compile _ _WRITE_SMOOTHNESS
            #pragma multi_compile_fragment _ _GBUFFER_NORMALS_OCT
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/RenderingLayers.hlsl"
            #pragma multi_compile_instancing
            #if defined(_GBUFFER_NORMALS_OCT)
                #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/Packing.hlsl"
            #endif

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

            void Frag(Varyings input, out half4 outNormalWS : SV_Target0
            #ifdef _WRITE_RENDERING_LAYERS
                , out uint outRenderingLayers : SV_Target1
            #endif
            )
            {
                half3 n = normalize(input.normalWS);
            #if defined(_GBUFFER_NORMALS_OCT)
                float2 oct = PackNormalOctQuadEncode(n);
                outNormalWS = half4(PackFloat2To888(saturate(oct * 0.5 + 0.5)), 0.0);
            #else
                outNormalWS = half4(n, 0.0);
            #endif
            #if defined(_WRITE_SMOOTHNESS)
                outNormalWS.a = 0.15;
            #endif
            #ifdef _WRITE_RENDERING_LAYERS
                outRenderingLayers = EncodeMeshRenderingLayer();
            #endif
            }
            ENDHLSL
        }
    }
}
