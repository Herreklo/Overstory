// The finishing test's one surface (blender/parts/finish): every material of 107's corner, in clay, for all its
// ways (_OS_PAINT: way P, painted). UV0 reads the material's tileable (way A's made here, ways B and C's from scans), UV1 the corner's page:
// its history (paint lost, dirt, water, each board's value) and its geometry (occlusion, cavity, arris). Lightness is
// worked in CIE L*, as the marks were made, and only then turned to grey albedo: no hue anywhere, but way Pc's, which
// lays a hue of luminance 1 on each of way P's values.
Shader "Overstory/Finish"
{
    Properties
    {
        _Tile ("Tileable: R under L*, G surface L*, B breakup, A height", 2D) = "grey" {}
        _TileN ("Tileable normal xy, B smoothness offset", 2D) = "grey" {}
        _TileScale ("UV0 scale to the tileable", Vector) = (1, 1, 0, 0)
        _Hist ("History page: R loss share, G dirt, B water, A board value", 2D) = "black" {}
        _Geo ("Geometry page: R occlusion, G cavity/arris, B sky, A arris", 2D) = "white" {}
        _StreetN ("Street level's laps (page normal)", 2D) = "grey" {}
        _Flake ("Paint's flake atlas: R breakup, G its halo, B a run's cores", 2D) = "grey" {}
        _FlakeScale ("UV0 scale to the flake atlas (0: the tileable's own breakup)", Float) = 0
        _HaloL ("The chalked paint round a loss, lighter by L*", Float) = 0
        _HaloW ("How far the halo reaches past the loss, as a share of the loss", Float) = 0
        _HaloDull ("The halo's lost gloss", Float) = 0
        _RunBody ("A run between its cores, as a share of its darkness", Range(0, 1)) = 1
        [Toggle] _Painted ("Painted", Float) = 0
        [Toggle(_OS_STREET)] _Street ("Street level", Float) = 0
        _PaintSmooth ("Paint smoothness", Range(0, 1)) = 0.3
        _UnderSmooth ("Under smoothness", Range(0, 1)) = 0.12
        _NormalScale ("Tile normal strength", Float) = 1
        _PaintFlat ("Tile normal kept under paint", Range(0, 1)) = 0.45
        _BoardScale ("Board value", Float) = 1
        _DirtL ("Dirt, L*", Float) = 16
        _WaterL ("Water, L*", Float) = 14
        _CavityL ("Cavity, L*", Float) = 8
        _ArrisL ("Worn arris lift, L*", Float) = 4
        _AOStrength ("Page occlusion", Range(0, 1)) = 1
        _LapDark ("Occlusion where a board meets the butt above", Range(0, 1)) = 0.65
        _LapCore ("How far below the butt it is darkest, m", Float) = 0.005
        _LapReach ("How far below the butt it reaches, m", Float) = 0.02
        _LipL ("A flake's curled lip, lighter by L*", Float) = 6
        _CrackL ("The gap under its edge, darker by L*", Float) = 25
        _StainL ("A stain, darker by L* (bare faces: page R is the wetness)", Float) = 0
        _TideW ("How far into a stain its dried rim fades, in the breakup's units", Range(0, 1)) = 0
        _StainMottleL ("The stain mottled by the face's breakup, L*", Float) = 0
        _TideL ("The tide line where a stain's front dried, darker by L*", Float) = 0
        _IslandW ("Deep in a stain: page R from, to", Vector) = (2, 3, 0, 0)
        _IslandL ("What the breakup leaves dry deep in a stain, lighter than the stain by L*", Float) = 0
        _GrainMip ("The tileable's mip its fine detail eases to with distance", Float) = 0
        _GrainFade ("How much of the tileable's fine detail is gone once far", Range(0, 1)) = 0
        _LapScale ("Vertex alpha's metres (corner.json lapReach)", Float) = 0.25
        _LapPage ("The street page's metres for its lap distance (geo B)", Float) = 0.064
        _LapStep ("How far a butt stands proud of the board under it, m", Float) = 0.013
        _DirtDull ("Dirt dulls gloss", Float) = 0.1
        [Toggle(_OS_PAINT)] _Paint ("Way P: painted", Float) = 0
        _Stroke ("Way P's strokes: R the peel's edge, G the stain's, B the lap grime's, A the boards' long strokes", 2D) = "grey" {}
        _StrokeScale ("UV1 scale to the strokes", Float) = 8
        _EdgeAmp ("How far a stroke moves a shape's edge, in its field", Float) = 0.5
        _StrokeFade ("The strokes' mip from which they fade, and by which they are gone", Vector) = (3, 5.5, 0, 0)
        _BrushL ("The long strokes' reach either side, L*", Float) = 0
        _BrushFade ("The long strokes' mip from which they fade, and by which they are down to _BrushFar", Vector) = (1.5, 2.8, 0, 0)
        _BrushFar ("What the long strokes keep far", Range(0, 1)) = 0
        _Hist2 ("Way P's second page: R the long washes, 0 to 1 of _WashL", 2D) = "black" {}
        _WashL ("The darkest long wash, L*", Float) = 0
        _BareWash ("How much of the long washes bare wood takes", Range(0, 1)) = 1
        _DragL ("The brush's drags down a wash, L* either side", Float) = 0
        _DragScale ("The drags' size, the long strokes' turned upright and shrunk by", Float) = 1.5
        _DLRange ("The page's value shift, L* either side of G's half", Float) = 40
        _StainEdge ("How much of the strokes' break a stain's edge takes", Range(0, 1)) = 1
        _FlatUp ("How far the light's normal is drawn up, so a face's own small forms are lit as one mass", Float) = 0
        _RimL ("The broken paint's edge, lighter by L*", Float) = 0
        _RimW ("How far the rim reaches from the edge, in the field", Float) = 0.04
        _RimFar ("What the rim keeps far", Range(0, 1)) = 0
        _RimBreak ("Where along its length the rim breaks: the stain strokes' value from, to", Vector) = (0, 0, 0, 0)
        _BareShift ("How much of the page's value shift bare wood takes", Range(0, 1)) = 1
        _PaintL ("The material's value, L*", Float) = 80
        _BareL ("Bare wood where paint is lost, L*", Float) = 40
        _UnderL ("The under layer vertex colour B forces (mortar), L*", Float) = 20
        _StainDL ("A stain, darker by L*", Float) = 0
        _StainSmooth ("A stain's smoothness", Range(0, 1)) = 0.1
        _LapGrimeL ("The lap's grime at its darkest, L*", Float) = 0
        _LapGrimeReach ("How far below the butt the grime reaches, m", Float) = 0.045
        _LapGrimeBreak ("How far the strokes move the grime's lower edge, as a share of its reach", Float) = 0.5
        _Tint ("Way Pc: the paint's hue, linear, of luminance 1", Vector) = (1, 1, 1, 0)
        _BareTint ("Way Pc: the bare fibre's hue", Vector) = (1, 1, 1, 0)
        _UnderTint ("Way Pc: the under layer's hue", Vector) = (1, 1, 1, 0)
        _StainTint ("Way Pc: a stain's hue", Vector) = (1, 1, 1, 0)
        _WashTint ("Way Pc: the long washes' hue", Vector) = (1, 1, 1, 0)
    }

    HLSLINCLUDE
    #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

    CBUFFER_START(UnityPerMaterial)
        float4 _Tile_ST;
        float4 _TileScale;
        float _Painted, _Street, _PaintSmooth, _UnderSmooth, _NormalScale, _PaintFlat, _BoardScale;
        float _DirtL, _WaterL, _CavityL, _ArrisL, _AOStrength, _DirtDull, _LapDark, _LapCore, _LapReach, _LapScale, _LapPage, _LapStep, _LipL, _CrackL;
        float _StainL, _TideW, _StainMottleL, _TideL, _IslandL, _GrainMip, _GrainFade;
        float4 _IslandW;
        float _FlakeScale, _HaloL, _HaloW, _HaloDull, _RunBody;
        float _Paint, _StrokeScale, _EdgeAmp, _RimL, _RimW, _BareShift, _PaintL, _BareL, _UnderL, _StainDL, _StainSmooth;
        float _LapGrimeL, _LapGrimeReach, _LapGrimeBreak, _BrushL, _FlatUp, _StainEdge, _BrushFar, _DragL, _DragScale;
        float _DLRange, _RimFar, _WashL, _BareWash;
        float4 _RimBreak;
        float4 _StrokeFade, _BrushFade;
        float4 _Tint, _BareTint, _UnderTint, _StainTint, _WashTint;
    CBUFFER_END
    ENDHLSL

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "Queue" = "Geometry" }

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode" = "UniversalForward" }

            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma shader_feature_local _OS_STREET
            #pragma shader_feature_local _OS_PAINT
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE
            #pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
            #pragma multi_compile_fragment _ _SCREEN_SPACE_OCCLUSION
            #pragma multi_compile _ _CLUSTER_LIGHT_LOOP
            #pragma multi_compile_fog
            #pragma multi_compile_instancing
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            TEXTURE2D(_Tile); SAMPLER(sampler_Tile);
            TEXTURE2D(_TileN); SAMPLER(sampler_TileN);
            TEXTURE2D(_Hist); SAMPLER(sampler_Hist);
            TEXTURE2D(_Hist2);
            TEXTURE2D(_Geo); SAMPLER(sampler_Geo);
            SamplerState os_point_clamp_lap;
            TEXTURE2D(_StreetN); SAMPLER(sampler_StreetN);
            TEXTURE2D(_Flake); SAMPLER(sampler_Flake);
            TEXTURE2D(_Stroke); SAMPLER(sampler_Stroke);

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float4 tangentOS : TANGENT;
                float2 uv0 : TEXCOORD0;
                float2 uv1 : TEXCOORD1;
                float4 color : COLOR;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float3 normalWS : TEXCOORD1;
                float4 tangentWS : TEXCOORD2;
                float4 uv : TEXCOORD3;
                float4 color : TEXCOORD4;
                float fog : TEXCOORD5;
            };

            Varyings Vert(Attributes v)
            {
                Varyings o;
                UNITY_SETUP_INSTANCE_ID(v);
                VertexPositionInputs p = GetVertexPositionInputs(v.positionOS.xyz);
                VertexNormalInputs n = GetVertexNormalInputs(v.normalOS, v.tangentOS);
                o.positionCS = p.positionCS;
                o.positionWS = p.positionWS;
                o.normalWS = n.normalWS;
                o.tangentWS = float4(n.tangentWS, v.tangentOS.w * GetOddNegativeScale());
                o.uv = float4(v.uv0 * _TileScale.xy, v.uv1);
                o.color = v.color;
                o.fog = ComputeFogFactor(p.positionCS.z);
                return o;
            }

            // CIE L* (0..100) to relative luminance
            float LToY(float L)
            {
                return L > 8.0 ? pow((L + 16.0) / 116.0, 3.0) : L / 903.3;
            }

            // the lap's band (whole for its core, easing out by its reach) summed from the butt to x metres below it
            float LapInt(float x)
            {
                x = max(x, 0.0);
                float w = max(_LapReach - _LapCore, 1e-5);
                float u = saturate((x - _LapCore) / w);
                return min(x, _LapCore) + w * (u - u * u * u + 0.5 * u * u * u * u);
            }

            // way P's lap grime, (1 - x / r)^2 below the butt, summed from the butt to x metres below it
            float GrimeInt(float x, float r)
            {
                float u = saturate(max(x, 0.0) / r);
                return r / 3.0 * (1.0 - (1.0 - u) * (1.0 - u) * (1.0 - u));
            }

            half4 Frag(Varyings i) : SV_Target
            {
                float4 hist = SAMPLE_TEXTURE2D(_Hist, sampler_Hist, i.uv.zw);
                float4 geo = SAMPLE_TEXTURE2D(_Geo, sampler_Geo, i.uv.zw);
                // how far below the butt above: the near boards' own corners carry it (vertex alpha), exact across
                // a planar face. The street level's wall is a plane, so its page carries the signed distance to the
                // nearest butt, read at full size (a mip would average it across the butt into a mark of nothing)
            #if defined(_OS_STREET)
                float lapB = SAMPLE_TEXTURE2D_LOD(_Geo, os_point_clamp_lap, i.uv.zw, 0).b;
                float lapD = (lapB - 0.5) * 2.0 * _LapPage;
                float hasLap = step(lapB, 0.99);
            #else
                float lapD = i.color.a * _LapScale;
                float hasLap = step(i.color.a, 0.999);
            #endif
                // band and shadow are summed over the pixel's reach down the wall, so a lap keeps its whole darkness
                // when it is narrower than a pixel
                float3 nG = normalize(i.normalWS);
                float3 upF = normalize(float3(0, 1, 0) - nG * nG.y);
                float up = dot(i.positionWS, upF);
                float fw = max(length(float2(ddx(up), ddy(up))), 1e-4);
                float lo = lapD - 0.5 * fw, hi = lapD + 0.5 * fw;

            #if defined(_OS_PAINT)
                // way P, painted: each material one value, shifted only by the page's designed shapes (R the peel's
                // field and B the stain's, each edge at 0.5; G a value shift, 0.5 + dL*/(2 _DLRange); A the lap grime's
                // strength). Near, the authored strokes move each edge by up to _EdgeAmp of its field, so the edge is
                // the brush's; with distance they go and each shape keeps its own soft contour
                float2 suv = i.uv.zw * _StrokeScale;
                float4 st = SAMPLE_TEXTURE2D(_Stroke, sampler_Stroke, suv);
                float lodS = CALCULATE_TEXTURE2D_LOD(_Stroke, sampler_Stroke, suv);
                float nearP = 1.0 - saturate((lodS - _StrokeFade.x) / max(_StrokeFade.y - _StrokeFade.x, 1e-3));
                float brush = _EdgeAmp * nearP;
                float tP = hist.r - 0.5 + brush * (st.r - 0.5);
                float wP = max(fwidth(tP), 1e-3);
                float peel = _Painted * smoothstep(-wP, wP, tP);
                // the paint's broken edge, its clean lip lighter than the paint around it, in pieces along its length;
                // some of it holds far
                float rim = _Painted * (1.0 - peel) * smoothstep(-wP - _RimW, -wP, tP) * lerp(_RimFar, 1.0, nearP)
                    * smoothstep(_RimBreak.x, _RimBreak.y, st.g);
                float tS = hist.b - 0.5 + _StainEdge * brush * (st.g - 0.5);
                float wS = max(fwidth(tS), 1e-3);
                float stain = smoothstep(-wS, wS, tS);
                float L = lerp(lerp(_PaintL, _BareL, peel), _UnderL, saturate(i.color.b));
                // the washes, the foot's dirt and the junctions' darks are the paint's; silvered bare wood takes only
                // some of them
                float shift = (hist.g - 0.5) * 2.0 * _DLRange - _StainDL * stain;
                L += shift * lerp(1.0, _BareShift, peel);
                L = lerp(L, _PaintL + shift + _RimL, rim);
                // the long washes darken the paint, soft and translucent; the bare fibre the paint has lost stays
                // dry and lighter, a hard mark of its own
                float wash = SAMPLE_TEXTURE2D(_Hist2, sampler_Hist, i.uv.zw).r;
                L -= _WashL * wash * lerp(1.0, _BareWash, peel);
                // the lap's grime: darkest under the butt, easing down the board to a lower edge the strokes break,
                // summed over the pixel's reach down the wall as the band is
                float gr = _LapGrimeReach * (1.0 + _LapGrimeBreak * nearP * 2.0 * (st.b - 0.5));
                L -= hasLap * hist.a * _LapGrimeL * (GrimeInt(hi, gr) - GrimeInt(lo, gr)) / fw;
                // near, long soft strokes along the boards let the plane breathe, and down a wash the brush drags;
                // by the street stop a trace of both
                float nearB = lerp(_BrushFar, 1.0, 1.0 - saturate((lodS - _BrushFade.x) / max(_BrushFade.y - _BrushFade.x, 1e-3)));
                float drag = SAMPLE_TEXTURE2D(_Stroke, sampler_Stroke, suv.yx * _DragScale).a;
                L += (_BrushL * 2.0 * (st.a - 0.5) + _DragL * wash * 2.0 * (drag - 0.5)) * nearB;
                float Y = LToY(clamp(L, 2.0, 98.0));
                // the colour still: each mark's own hue laid on its value, every tint of luminance 1 so the albedo
                // keeps the clay's; white in clay
                float3 tint = lerp(lerp(_Tint.rgb, _BareTint.rgb, peel), _UnderTint.rgb, saturate(i.color.b));
                tint = lerp(lerp(tint, _Tint.rgb, rim), _StainTint.rgb, stain);
                tint = lerp(tint, _WashTint.rgb, saturate(wash * lerp(1.0, _BareWash, peel)));
                float3 nT = float3(0, 0, 1);
                float smooth = lerp(_PaintSmooth, _StainSmooth, stain);
            #else
                float4 tile = SAMPLE_TEXTURE2D(_Tile, sampler_Tile, i.uv.xy);
                float4 tn = SAMPLE_TEXTURE2D(_TileN, sampler_TileN, i.uv.xy);

                // paint is lost where the page's share meets the breakup (the flake atlas's, finer, on painted faces
                // of way A; else the tileable's); the edge anti-aliased to a pixel. Once the breakup's plates are
                // under a pixel its mips average to a half and would lose every loss, so with distance the loss
                // becomes the page's share itself: the same mean, as soft painted marks
                float useF = step(1e-4, _FlakeScale);
                float2 fuv = i.uv.xy * max(_FlakeScale, 1e-4);
                float4 fl = SAMPLE_TEXTURE2D(_Flake, sampler_Flake, fuv);
                float lod = lerp(CALCULATE_TEXTURE2D_LOD(_Tile, sampler_Tile, i.uv.xy),
                                 CALCULATE_TEXTURE2D_LOD(_Flake, sampler_Flake, fuv) - 0.5, useF);
                float far = saturate((lod - 1.5) / 2.0);
                // a bare face's fine grain eases with distance to its own broad mottle, its value, relief and the
                // breakup a stain's front meets alike, so no thin outlier along the grain rules a line across a
                // sheet or shimmers once it is under a pixel
                float gf = _GrainFade * far;
                float4 tileLo = SAMPLE_TEXTURE2D_LOD(_Tile, sampler_Tile, i.uv.xy, max(_GrainMip, lod));
                tile.rgb = lerp(tile.rgb, tileLo.rgb, gf);
                tn.rg = lerp(tn.rg, 0.5, gf);
                float t = hist.r + lerp(tile.b, fl.r, useF) - 1.0;
                float w = max(fwidth(t), 1e-3);
                float lost = _Painted * lerp(smoothstep(-w, w, t), hist.r, far);
                float under = max(lost, saturate(i.color.b));

                float L = lerp(tile.g, tile.r, under) * 100.0;
                L += (hist.a - 0.5) * 80.0 * _BoardScale;
                // a lifted flake: its curled lip catches light on the paint's side, the gap under it is dark on the
                // wood's, each a pixel or two across; gone once the loss becomes the page's soft mark
                float e = t / w;
                float edge = _Painted * (1.0 - far);
                L += edge * (_LipL * saturate(1.0 - abs(e + 1.5) / 1.5) - _CrackL * saturate(1.0 - abs(e - 0.75)));
                // the paint round a loss has chalked and lost its hold: lighter and dull, in a ring the atlas's
                // blurred breakup draws past the loss, widened by its halo; none where nothing is lost
                float tH = hist.r * (1.0 + _HaloW) + fl.g - 1.0;
                float halo = useF * _Painted * (1.0 - lost) * (1.0 - far) * smoothstep(-1.0, 1.0, tH / max(fwidth(tH), 1e-3));
                L += _HaloL * halo;
                // a bare face's stains (the boarding's sheet): the page's coarse wetness meets the face's own fine
                // breakup as paint loss does, but stays a sharp threshold at every distance, the breakup's mips
                // easing to its middle so far off the front is the wetness's own contour. Deepest toward its source,
                // mottled by the breakup, a tide line a pixel inside the front where it dried. Deep inside, the wood
                // is damp throughout: what the breakup leaves dry there is only a little lighter, with no rim
                float stain = (1.0 - _Painted) * smoothstep(-w, w, t);
                float deep = (1.0 - _Painted) * smoothstep(_IslandW.x, _IslandW.y, hist.r);
                float tide = stain * (1.0 - smoothstep(0.0, _TideW + w, t)) * (1.0 - far) * (1.0 - deep);
                float sd = max(stain, deep * (1.0 - _IslandL / max(_StainL, 1e-3)));
                L -= sd * (_StainL + _StainMottleL * (tile.b - 0.5)) + _TideL * tide;
                float cav = saturate((0.5 - geo.g) * 2.0);
                float lift = saturate((geo.g - 0.5) * 2.0);
                // bare stuff soaks unevenly, by its own breakup; paint sheds water and keeps a stain even
                float soak = lerp(0.35 + 1.3 * tile.b, 1.0, _Painted * (1.0 - lost));
                // a run keeps to narrow tracks down a painted board, darkest along them; one soft mark once they
                // are under a pixel
                float run = lerp(1.0, lerp(_RunBody, 1.0, fl.b), useF * (1.0 - far));
                L += lift * _ArrisL - hist.g * _DirtL - saturate(hist.b * soak) * _WaterL * run - cav * _CavityL;
                float Y = LToY(clamp(L, 2.0, 98.0));

                float2 nxy = (tn.rg * 2.0 - 1.0) * _NormalScale * lerp(_PaintFlat, 1.0, max(lost, 1.0 - _Painted));
                float3 nT = float3(nxy, sqrt(saturate(1.0 - dot(nxy, nxy))));
                float smooth = saturate(lerp(_PaintSmooth, _UnderSmooth, under) + (tn.b - 0.5) - hist.g * _DirtDull - halo * _HaloDull);
            #endif
            #if defined(_OS_STREET)
                float3 nP = SAMPLE_TEXTURE2D(_StreetN, sampler_StreetN, i.uv.zw).xyz * 2.0 - 1.0;
                nT = normalize(float3(nP.xy + nT.xy, nP.z * nT.z));
            #endif
                float3 bit = i.tangentWS.w * cross(i.normalWS, i.tangentWS.xyz);
                float3x3 tbn = float3x3(i.tangentWS.xyz, bit, i.normalWS);
                float3 nWS = normalize(mul(nT, tbn));
            #if defined(_OS_PAINT)
                // a mass painted as one: its small forms (the pantiles' rolls) lit nearly alike
                nWS = normalize(nWS + _FlatUp * float3(0, 1, 0));
            #endif

                SurfaceData s = (SurfaceData)0;
            #if defined(_OS_PAINT)
                s.albedo = Y * tint;
            #else
                s.albedo = Y.xxx;
            #endif
                s.metallic = 0;
                s.specular = 0;
                s.smoothness = saturate(smooth);
                s.normalTS = nT;
                // the sky's light is shut out of the lap's mouth: dark for its core, easing out by its reach
                float lap = 1.0 - hasLap * _LapDark * (LapInt(hi) - LapInt(lo)) / fw;
                s.occlusion = lerp(1.0, geo.r, _AOStrength) * lap;
                s.alpha = 1;

                InputData d = (InputData)0;
                d.positionWS = i.positionWS;
                d.positionCS = i.positionCS;
                d.normalWS = nWS;
                d.viewDirectionWS = GetWorldSpaceNormalizeViewDir(i.positionWS);
            #if defined(MAIN_LIGHT_CALCULATE_SHADOWS)
                d.shadowCoord = TransformWorldToShadowCoord(i.positionWS);
            #endif
                d.fogCoord = i.fog;
                d.bakedGI = SampleSH(nWS);
                d.normalizedScreenSpaceUV = GetNormalizedScreenSpaceUV(i.positionCS);
                d.shadowMask = half4(1, 1, 1, 1);

                half4 c = UniversalFragmentPBR(d, s);
                // the butt's own shadow in the key light, exact for a straight edge at any size on screen: the step
                // throws it down the face as far as the light's rise over its fall onto the wall
                Light ml = GetMainLight(d.shadowCoord, d.positionWS, d.shadowMask);
                float ln = dot(ml.direction, nG);
                float ds = _LapStep * max(dot(ml.direction, upF), 0.0) / max(ln, 1e-3);
                float shut = hasLap * step(0.0, ln) * saturate((min(hi, ds) - max(lo, 0.0)) / fw);
                if (shut > 0.0)
                {
                    BRDFData brdf;
                    half alpha = 1;
                    InitializeBRDFData(s.albedo, s.metallic, s.specular, s.smoothness, alpha, brdf);
                    half3 direct = LightingPhysicallyBased(brdf, ml, nWS, d.viewDirectionWS);
                #if defined(_SCREEN_SPACE_OCCLUSION)
                    direct *= CreateAmbientOcclusionFactor(d, s).directAmbientOcclusion;
                #endif
                    c.rgb -= direct * shut * GetMainLightShadowStrength();
                }
                c.rgb = MixFog(c.rgb, d.fogCoord);
                return half4(c.rgb, 1);
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
            #pragma target 4.5
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
            #pragma target 4.5
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
            #pragma target 4.5
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
                outNormalWS.a = 0.2;
            #endif
            #ifdef _WRITE_RENDERING_LAYERS
                outRenderingLayers = EncodeMeshRenderingLayer();
            #endif
            }
            ENDHLSL
        }
    }
}
