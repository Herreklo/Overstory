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
// water layer (how much water lies or runs there, 0 to 1); UV3 the bake (x sky, y ground).
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
        _Water ("Its water profile (Water.hlsl): x darkens wet, y wet film's gloss, z holds water, w stains", Vector) = (0.85, 1.0, 0.2, 0.55)
        _Cement ("Cement the day it was struck", Color) = (0.70, 0.69, 0.66, 1)
        _CementOld ("Cement after forty years of weather and grime", Color) = (0.50, 0.50, 0.48, 1)
        _CementFilm ("The algae film on damp cement", Color) = (0.24, 0.27, 0.21, 1)
        _Soil ("The soil a joint holds where its pointing has gone", Color) = (0.17, 0.15, 0.12, 1)
        _Streak ("The film water leaves where it runs down a face: algae and grime", Color) = (0.20, 0.22, 0.18, 1)
        [Toggle] _Grey ("Grey light: every layer's pigment one grey (to judge form)", Float) = 0
        _History ("Debug: show the history as colour (r polish, g lichen years, b moss)", Float) = 0
        _Quiet ("History off: the quiet means (x polish, y lichen years / 200, z moss, w water held)", Vector) = (0, 0, 0, 0)
        _QuietAge ("History off: the quiet means (x years since bare / 200, y the water layer)", Vector) = (0, 0, 0, 0)
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
        half4 _Water;
        half4 _Cement;
        half4 _CementOld;
        half4 _CementFilm;
        half4 _Soil;
        half4 _Streak;
        half _Grey;
        half _History;
        half4 _Quiet;
        float4 _QuietAge;
    CBUFFER_END

    #include "StreetSurface.hlsl"
    #include "Growth.hlsl"
    #include "Water.hlsl"

    TEXTURE2D(_GrainMap); SAMPLER(sampler_GrainMap);
#if defined(OS_R0B)
    // R0b's arms, each 1 to turn it on: the specular through GeometricNormalFiltering, a joint's soil floored to 6 L*
    // under its face, SN7's cut marks off, the mesh alone (one rock colour, no relief), each pixel's kind and piece
    float _OS_R0b_GNF, _OS_R0b_JointFloor, _OS_R0b_CutMarks, _OS_R0b_Flat, _OS_R0b_Kinds;
#endif
#if defined(OS_PATCHES)
    // R2a's stones (reviews/lt1/port/2b/r2a/stones/plan.md, the contract): the face patches (SN6) and L1's lit line
    // (SN8), set by the judging harness (Editor/LT1R2a.cs), every number from data: the patches' array, their size and
    // the arms' slices from their manifest (blender/parts/stone/slate/patches.manifest.json), the chamfer's form from
    // the part's definition; each face's patch, arrises and chamfer width from the mesh (UV6, UV7)
    TEXTURE2D_ARRAY(_OS_PatchMap); SAMPLER(sampler_OS_PatchMap);   // xyz the normal (tangent space; the mips' averages
                                                                    // unnormalised), w the face value's multiplier
    float _OS_PatchPerMetre;    // patches a metre (1 / a patch's size)
    float _OS_PatchShift[8];    // added to a face's slice: the arm judged (all 0: as built)
    float4 _OS_Chamfer;         // x its leg along each face, metres per mm of the code's width; y, z its normal's
                                // shares of the face's normal and of the arris's outward direction (its angle)
    float _OS_PatchFlat;        // debug, 1: the patches flat (the face's normal, value 1), the control
    float _OS_PatchLineOff;     // debug, 1: L1 without its lit line

    // The share of a pixel (a unit box) where a field linear across it lies under t, the field 0 at the pixel's centre
    // and its screen gradient (gx, gy): the box filter of a straight edge, exact (a trapezoid's integral)
    float OS_BoxBelow(float t, float gx, float gy)
    {
        float a = max(max(abs(gx), abs(gy)), 1e-12), b = max(min(abs(gx), abs(gy)), 1e-12);
        float h = 0.5 * (a + b), k = 0.5 * (a - b);
        if (t <= -h)
            return 0.0;
        if (t >= h)
            return 1.0;
        if (t < -k)
            return (t + h) * (t + h) / (2.0 * a * b);
        if (t > k)
            return 1.0 - (h - t) * (h - t) / (2.0 * a * b);
        return 0.5 + t / a;
    }
#endif

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
        half4 water;       // how it answers water (its water profile: the rock's own, cement's, soil's)
    };

    StoneOut OS_StoneSurface(float2 g, half4 hist, half kind, half years, half var, float3 positionWS, half sky,
                             half water, half up
#if defined(OS_PATCHES)
                             , half patchValue    // the face patch's value: it multiplies the face's one value
#endif
                             )
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
#if defined(OS_PATCHES)
        // (SN6: the tiled grain map leaves the stone's faces, its relief and one value the face patch's)
        tone = 0.0h;
        relief = 0.0h;
#endif
        // iron in the rock rusting in sparse spots (the stone's own texture, claiming nothing)
        half rust = smoothstep(0.74h, 0.8h, (half)OS_Noise(q * 9.0 + var * 41.0)) * smoothstep(0.45h, 0.6h, (half)OS_Noise(q * 47.0));
#if defined(OS_R0B)
        if (_OS_R0b_CutMarks > 0.5)
            rust = 0.0h;
#endif
#if defined(OS_PATCHES)
        rust = 0.0h;    // (SN7: rust spots cut)
#endif
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
#if defined(OS_R0B)
        if (_OS_R0b_CutMarks > 0.5)
            tint = half3(1.0h, 1.0h, 1.0h);
#endif
#if defined(OS_PATCHES)
        tint = half3(1.0h, 1.0h, 1.0h);     // (SN7: the per-piece hue bins cut)
#endif
        rock *= lerp(half3(1.0h, 1.0h, 1.0h), tint, (half)_Grain.w);
        // polish: the weathered skin worn off where feet go, the rock beneath darker and smoother
        rock *= 1.0h - (half)_Polish.x * hist.r;
#if defined(OS_PATCHES)
        rock *= patchValue;
#endif
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
#if defined(OS_R0B)
            if (_OS_R0b_CutMarks > 0.5)
                crumb = 0.5h;
#endif
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
#if defined(OS_R0B)
            if (_OS_R0b_CutMarks > 0.5)
                sand = 0.5h;
#endif
            // (on this coast grime and a film come in a few years: half grey by six, near its old grey by twenty)
            half grime = 1.0h - exp(-years / 9.0h);
            half3 cem = lerp(_Cement.rgb, _CementOld.rgb, grime) * (0.9h + 0.2h * sand);
            half film = saturate(hist.b * 1.6h) * grime * smoothstep(0.3h, 0.7h, (half)OS_Noise(q * 12.0 + var * 5.0));
#if defined(OS_R0B)
            if (_OS_R0b_CutMarks > 0.5)
                film = 0.0h;
#endif
            cem = lerp(cem, _CementFilm.rgb, film * 0.7h);
            half craze = smoothstep(0.03h, 0.0h, abs((half)OS_Noise(q * 38.0 + var * 9.0) - 0.5h)) * grime * nearC;
#if defined(OS_R0B)
            if (_OS_R0b_CutMarks > 0.5)
                craze = 0.0h;
#endif
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

        // the water layer (Water.hlsl): this surface's material answers it (the rock's own profile, cement's, a
        // joint's soil); where water runs down a face it leaves streaks of algae film and grime; lichen keeps to the
        // dry places between, moss and algae follow the wet
#if defined(OS_R0B)
        if (_OS_R0b_Flat > 4.5 && _OS_R0b_Flat < 5.5)
            rock = lerp(_Fresh.rgb, _Stone.rgb, saturate(years / _Weather));
#endif
        half4 prof = kind > 5.5h ? _OS_WaterSoil : (kind > 3.5h ? _OS_WaterCement : _Water);
        half streak = OS_Streak(q, water, up, years, var, prof.w);
#if defined(OS_PATCHES)
        streak = 0.0h;  // (SN7: run-off streaks cut)
#endif
        rock = lerp(rock, _Streak.rgb, streak * 0.6h);
        half lichenYears = hist.g * 200.0h * (1.0h - 0.85h * saturate(water * 1.2h - 0.1h));
        moss = saturate(moss * (0.7h + 0.6h * water));

        // growth: nature's thin layer (Growth.hlsl), from where and how long the stone's facts give
#if defined(OS_R0B)
        half3 rockBare = rock;
        if (_OS_R0b_Flat > 5.5 && _OS_R0b_Flat < 6.5)
            lichenYears = 0.0h;
        if (_OS_R0b_Flat > 6.5)
            moss = 0.0h;
#endif
        OSGrowth gr = OS_GrowthLayer(rock, smooth, q, lichenYears, moss, sky, var, positionWS);
        rock = gr.albedo;
#if defined(OS_R0B)
        if (_OS_R0b_Flat > 3.5 && _OS_R0b_Flat < 4.5)
            rock = rockBare;
#endif
        smooth = gr.smoothness;
        h += gr.height * (half)(_Relief.y / max(_Relief.x, 1e-5));

        o.albedo = rock;
        o.smoothness = smooth;
        o.height = h;
        o.growth = gr.cover;
        // (growth on it answers water as growth does: it soaks it up and never glazes)
        o.water = lerp(prof, _OS_WaterGrowth, gr.cover);
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
            // the harness's arms (docs/measuring.md): history off, every quantity the pages and the piece table will
            // carry (R1: polish, lichen, moss, water held, the water layer, years since bare) held at the material's
            // quiet mean, and the history interpolator gone; haze off, OS_Atmosphere skipped
            #pragma multi_compile _ OS_HISTORY_OFF
            #pragma multi_compile_fragment _ OS_HAZE_OFF
            // R0b's arms (reviews/lt1/port/2b/design.md, The ladder; Editor/LT1R0b.cs): only in the editor, never in a
            // player (a shader_feature no material sets); without it the pass is as it was
            #pragma shader_feature_fragment _ OS_R0B
            // R2a's stones (r2a/stones/plan.md; Editor/LT1R2a.cs): the face patches and L1's lit line, read from UV6 and
            // UV7 in the vertex stage; a shader_feature only the judging runs' unsaved materials set
            #pragma shader_feature_local _ OS_PATCHES
            // L5's term arms (the harness's bare-<term> and all-shadow, docs/measuring.md): each skips one term, off in the game
            #pragma multi_compile_fragment _ OS_L5_TOWNSKY OS_L5_CLOUDS OS_L5_LAMPS OS_L5_BRUSH OS_L5_SHADOW OS_L5_REFL OS_L5_GROWTH OS_L5_ROSETTES OS_L5_NEAR
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
            #if defined(OS_PATCHES)
                float2 uv6 : TEXCOORD6;     // (d0, d1)
                float2 uv7 : TEXCOORD7;     // (d2, code)
            #endif
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 positionWS : TEXCOORD1;
                half3 normalWS : TEXCOORD2;
            #if !defined(OS_HISTORY_OFF)
                half4 history : TEXCOORD3;
            #endif
                float4 piece : TEXCOORD4;    // x years / 200, y seed, z face, w variation
                float2 bake : TEXCOORD5;
            #if defined(OS_PATCHES)
                float3 edge : TEXCOORD6;     // the distance in metres to each of the triangle's three edges
                nointerpolation float code : TEXCOORD7;    // slice + 8 mask + 64 chamfer width in mm, one per face
            #endif
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
            #if !defined(OS_HISTORY_OFF)
                o.history = half4(input.uv4, input.uv5);
            #endif
                o.piece = float4(input.uv1, input.uv2);
                o.bake = input.uv3;
            #if defined(OS_PATCHES)
                o.edge = float3(input.uv6, input.uv7.x);
                o.code = input.uv7.y;
            #endif
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
            #if defined(OS_HISTORY_OFF)
                half4 history = _Quiet;
                float4 piece = float4(_QuietAge.x, input.piece.y, input.piece.z, _QuietAge.y);
            #else
                half4 history = input.history;
                float4 piece = input.piece;
            #endif
                half years = (half)piece.x * 200.0h;
                half town = OS_TownSky(input.positionWS, n);
                half water = (half)piece.w;
#if defined(OS_PATCHES)
                // the face's patch (SN6): its slice from UV7's code, moved to the arm judged, sampled at the face's
                // metres; its bands filtered away by the mips as they shrink, and its relief and value taken to the
                // patch's mean (its last mip) by footprint, as every near mark is (OS_Near, Detail.hlsl)
                float code = round(input.code);
                float slice = fmod(code, 8.0);
                float maskBits = fmod(floor(code / 8.0), 8.0);
                float chamferMm = floor(code / 64.0);
                bool patched = slice < 6.5;
                float3 dpx = ddx(input.positionWS), dpy = ddy(input.positionWS);
                float2 duvx = ddx(input.uv), duvy = ddy(input.uv);
                float4 patch = float4(0.0, 0.0, 1.0, 1.0);
                if (patched && _OS_PatchFlat < 0.5)
                {
                    float layer = slice + _OS_PatchShift[(uint)slice];
                    float2 uvP = input.uv * _OS_PatchPerMetre;
                    float4 fine = SAMPLE_TEXTURE2D_ARRAY_GRAD(_OS_PatchMap, sampler_OS_PatchMap, uvP, layer,
                                                              duvx * _OS_PatchPerMetre, duvy * _OS_PatchPerMetre);
                    uint pw, ph, pe, levels;
                    _OS_PatchMap.GetDimensions(0, pw, ph, pe, levels);
                    float4 mean = SAMPLE_TEXTURE2D_ARRAY_LOD(_OS_PatchMap, sampler_OS_PatchMap, uvP, layer, levels - 1);
                    patch = lerp(mean, fine, (float)OS_Near(max(length(dpx), length(dpy))));
                }
                float patchLen = max(length(patch.xyz), 1e-4);
                half3 patchN = (half3)(patch.xyz / patchLen);
#endif
                StoneOut so = OS_StoneSurface(input.uv, history, (half)piece.z, years, (half)piece.y,
                                              input.positionWS, town, water, n.y
#if defined(OS_PATCHES)
                                              , (half)patch.w
#endif
                                              );
#if defined(OS_R0B)
                // (1 the mesh alone: one rock colour and no relief; 2 the colour alone; 3 the relief alone; 4 and 5,
                // the growth's colour and the rock's own, are in OS_StoneSurface)
                if (_OS_R0b_Flat > 0.5 && _OS_R0b_Flat < 2.5)
                    so.albedo = lerp(_Fresh.rgb, _Stone.rgb, saturate(years / _Weather));
                if (_OS_R0b_Flat > 0.5 && (_OS_R0b_Flat < 1.5 || (_OS_R0b_Flat > 2.5 && _OS_R0b_Flat < 3.5)))
                    so.height = 0.0h;
#endif
#if defined(OS_PATCHES)
                half3 nGeo = n;     // the face's own normal: the patch's frame and the lit line's
                if (patched)
                {
                    // the patch's normal on the face, in the frame of UV0's screen derivatives (Schüler's cotangent
                    // frame: UV0 is metres in the face's plane, so the frame is orthonormal, a mirror in u included)
                    float3 dp2perp = cross(dpy, (float3)n), dp1perp = cross((float3)n, dpx);
                    float3 T = dp2perp * duvx.x + dp1perp * duvy.x;
                    float3 B = dp2perp * duvx.y + dp1perp * duvy.y;
                    float invmax = rsqrt(max(max(dot(T, T), dot(B, B)), 1e-30));
                    n = (half3)normalize((T * patchN.x + B * patchN.y) * invmax + (float3)n * patchN.z);
                }
#endif
                n = OS_BumpStone(input.positionWS, n, so.height * (half)_Relief.x);

                StreetSurface s;
                s.albedo = _Grey > 0.5 ? half3(0.42h, 0.42h, 0.42h) : so.albedo;
#if defined(OS_PATCHES)
                // (the patch's value is the face's form: in grey light too, as patches.md measures a face)
                if (_Grey > 0.5)
                    s.albedo *= (half)patch.w;
#endif
                s.emission = 0;
                s.metallic = 0;
                s.smoothness = so.smoothness;
                s.normalWS = n;
                // the weather, through the water layer (Water.hlsl): wet where the water lies and runs and as long as
                // this material holds it, darker by its porosity, glazed where feet or hands polished it, water
                // standing in the hollows
                half up = n.y;
                half wet = OS_WetNow(water, up, so.water.z);
                OS_Wet(s.albedo, s.smoothness, s.normalWS, wet, so.water, history.r, history.a, up);
#if defined(OS_R0B)
                // (the gloss filtered by the shading normal's screen-space variance, HDRP's defaults 0.1 and 0.2)
                if (_OS_R0b_GNF > 0.5)
                    s.smoothness = (half)GeometricNormalFiltering(s.smoothness, s.normalWS, 0.1, 0.2);
#endif
#if defined(OS_PATCHES)
                // the gloss filtered by the shading normal's variance (SN6; Tokuyoshi and Kaplanyan, with HDRP's
                // defaults 0.1 and 0.2 as R0b's arm): its change across the screen, and where the patch's mips
                // averaged it, the averaged normal's shortening
                s.smoothness = (half)NormalFiltering(s.smoothness, GeometricNormalVariance(s.normalWS, 0.1)
                                                                   + TextureNormalVariance(patchLen), 0.2);
#endif

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
#if defined(OS_PATCHES)
                // L1's lit line (SN8): where the mesh marks an arris L0 chamfers (UV7's mask), L0's chamfer drawn in the
                // shading on the arris itself (UV6 and UV7's edge distances), its form the part's (its angle from the
                // part's definition, its width from the code), shaded as L0's is (its own kind, the town's one light),
                // and laid over the face by the share of the face's part of the pixel it covers (the strip's edge
                // box-filtered: no shimmer, and it fades as it thins)
                if (maskBits > 0.5 && _OS_PatchLineOff < 0.5)
                {
                    float leg = chamferMm * _OS_Chamfer.x;
                    float3 dEx = ddx(input.edge), dEy = ddy(input.edge);
                    float3 r1 = cross(dpy, (float3)nGeo), r2 = cross((float3)nGeo, dpx);
                    float sgn = dot(dpx, r1) < 0.0 ? -1.0 : 1.0;
                    uint bits = (uint)maskBits;
                    float3 eSum = 0.0;
                    float cSum = 0.0, keep = 1.0;
                    // (the other face at the arris, from the chamfer's angle and its equal legs: at twice the angle)
                    float3 V = GetWorldSpaceNormalizeViewDir(input.positionWS);
                    float vA = max(dot((float3)nGeo, V), 1e-4);
                    float cos2 = _OS_Chamfer.y * _OS_Chamfer.y - _OS_Chamfer.z * _OS_Chamfer.z;
                    float sin2 = 2.0 * _OS_Chamfer.y * _OS_Chamfer.z;
                    [unroll]
                    for (int k = 0; k < 3; k++)
                    {
                        if (((bits >> k) & 1u) == 0u)
                            continue;
                        float d = input.edge[k];
                        // the arris's outward direction in the face: down the distance's surface gradient
                        float3 grad = sgn * (dEx[k] * r1 + dEy[k] * r2);
                        float3 eK = -grad * rsqrt(max(dot(grad, grad), 1e-30));
                        // how much of the strip L0's chamfer fills on screen: all of it while the other face is seen;
                        // where the other face turns away (the arris a silhouette), only the strip's inner part, by the
                        // projected widths (the chamfer's is the two strips' sum), and none once the chamfer turns away
                        // too. The outer part is the box's own excess over L0 (L0 shows what lies beyond the stone
                        // there): it keeps the chamfer's shade by the share the chamfer fills, so a seen chamfer's band
                        // still reaches the silhouette as L0's does, and a chamfer turned away draws no line at all
                        float fill = saturate(1.0 + dot(cos2 * (float3)nGeo + sin2 * eK, V) / vA);
                        // (the share of the pixel beyond the arris is not this face's: the strip's share is of the rest)
                        float beyond = OS_BoxBelow(-d, dEx[k], dEy[k]);
                        float inner = OS_BoxBelow(leg * (1.0 - fill) - d, dEx[k], dEy[k]);
                        float c = saturate((OS_BoxBelow(leg - d, dEx[k], dEy[k]) - (1.0 - fill) * inner - fill * beyond)
                                           / max(1.0 - beyond, 1e-4));
                        eSum += c * eK;
                        cSum += c;
                        keep *= 1.0 - c;
                    }
                    float cover = 1.0 - keep;
                    // (where two strips meet at a corner, their directions blend by share: a mitre)
                    float3 e = eSum / max(cSum, 1e-6);
                    half3 nC = (half3)normalize((float3)nGeo * _OS_Chamfer.y + e * _OS_Chamfer.z);
                    StoneOut sc = OS_StoneSurface(input.uv, history, 1.0h, years, (half)piece.y, input.positionWS,
                                                  town, water, nC.y, 1.0h);
                    if (cover > 1.0 / 1024.0)
                    {
                        StreetSurface sC;
                        sC.albedo = _Grey > 0.5 ? half3(0.42h, 0.42h, 0.42h) : sc.albedo;
                        sC.emission = 0;
                        sC.metallic = 0;
                        sC.smoothness = sc.smoothness;
                        sC.normalWS = nC;
                        half wetC = OS_WetNow(water, nC.y, sc.water.z);
                        OS_Wet(sC.albedo, sC.smoothness, sC.normalWS, wetC, sc.water, history.r, history.a, nC.y);
                        InputData idC = id;
                        idC.normalWS = sC.normalWS;
                        // (the chamfer's sky by the loose stones' bake rule, the contract's UV3: 0.5 + 0.5 n up)
                        OSBake bC = OS_ReadBake(half4((half)(input.bake.x + 0.5 * (nC.y - nGeo.y)), (half)input.bake.y,
                                                      1.0h, 1.0h));
                        bC.town = OS_TownSky(input.positionWS, nC);
                    #if defined(_OS_LOOK_B)
                        half3 colourC = OS_ShadeB(idC, sC, bC, input.positionWS);
                    #elif defined(_OS_LOOK_D)
                        half3 colourC = OS_ShadeD(idC, sC, bC, input.positionWS);
                    #elif defined(_OS_LOOK_P)
                        half3 colourC = OS_ShadeP(idC, sC, bC, input.positionWS);
                    #else
                        half3 colourC = OS_ShadeA(idC, sC, bC);
                    #endif
                        colour = lerp(colour, colourC, (half)cover);
                    }
                }
#endif
#if defined(OS_R0B)
                // (a joint's soil no darker than 6 L* under the face's rock in the same light, by its albedo's share)
                if (_OS_R0b_JointFloor > 0.5 && piece.z > 5.5)
                {
                    half3 faceRock = lerp(_Fresh.rgb, _Stone.rgb, saturate(years / _Weather));
                    float ratio = dot((float3)faceRock, float3(0.2126, 0.7152, 0.0722)) / max(dot((float3)so.albedo, float3(0.2126, 0.7152, 0.0722)), 1e-3);
                    float y = max(dot((float3)colour, float3(0.2126, 0.7152, 0.0722)), 1e-6);
                    float lFace = 116.0 * pow(y * max(ratio, 1.0), 1.0 / 3.0) - 16.0;
                    float yMin = pow(max(lFace - 6.0 + 16.0, 0.0) / 116.0, 3.0);
                    colour *= (half)max(1.0, yMin / y);
                }
#endif
                colour = OS_Atmosphere(colour, input.positionWS);
                if (_History > 2.5)
                    colour = normalize(input.normalWS) * 0.5h + 0.5h;
                else if (_History > 1.5)
                    colour = so.albedo * 0.6h;
                else if (_History > 0.5)
                    colour = piece.z > 3.5 ? half3(0.9h, 0.45h, 0.0h)
                                           : half3(history.r, history.g * 2.0h, history.b) * 0.5h;
#if defined(OS_R0B)
                if (_OS_R0b_Kinds > 0.5)
                    colour = half3((half)piece.z / 8.0h, (half)frac(piece.y), b.ground);
#endif
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
