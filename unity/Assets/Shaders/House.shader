// House: the town's timber houses (tools/houses.py, blender/parts/house/), lit exactly as the street is (look P, the
// sky term from the bake, the town's sky map, the air). Each face says what it is (its kind) and which house it
// belongs to; the house's coats and care are read against the date (_OS_Date), never stored on its vertices.
//
// Vertex data (blender/parts/house/soup.py): UV0 the surface's own metres (along its grain, up it); UV1 x the kind
// (soup.KINDS), y the house's row; UV2 x the piece's seed, y the year it was put up; UV3 the bake (x sky, y ground);
// UV4 x openness, y a lit window's own seed (0 unlit); UV5 x the height on a board from its lap edge (0) to its top
// (1), y how sheltered it is; UV6 x the coat scheme (soup.SCHEMES), y the storey band; UV7 spare.
Shader "Overstory/House"
{
    Properties
    {
        _Room ("A lit room's lamp: rgb its light (linear), a its power (glass.json, room)", Vector) = (0, 0, 0, 0)
        _RoomWall ("The room's walls: rgb (linear), a its depth behind the glass (m)", Vector) = (0, 0, 0, 3)
        _RoomCeiling ("The room's ceiling: rgb (linear), a the room's half width (m)", Vector) = (0, 0, 0, 1.5)
        _RoomFloor ("The room's floor: rgb (linear), a the sill's height over it (m)", Vector) = (0, 0, 0, 0.8)
        _RoomShape ("The room: x its height (m), y the light it has besides the lamp, z the lamp's drop (m), w its swing (m)", Vector) = (2.4, 0, 0.5, 0)
        _RoomFurniture ("The room's furniture: rgb (linear), a its height (m)", Vector) = (0, 0, 0, 0)
        _RoomFurniture2 ("The room: x the furniture's half length (m), y the corners' reach (m), z their light, w the lamp's softness (m2)", Vector) = (1, 0.5, 0.6, 0.3)
        _RoomShade ("The lamp's shade: x its radius (m), yzw its glow (linear)", Vector) = (0, 0, 0, 0)
        _Curtain ("Curtains: rgb (linear), a the share of the window's half width each covers", Vector) = (0, 0, 0, 0)
        _CurtainB ("Curtains: x opacity, y depth behind the glass (m), z the valance's share of the height, w folds a metre", Vector) = (0, 0.06, 0, 10)
        _Glass ("Window glass: a its smoothness", Vector) = (0, 0, 0, 0)
        _GlassDay ("An unlit room by day: x its light at the glass, y at its back wall, z the ceiling's share, w the curtains' (glass.json, daylight)", Vector) = (0.3, 0.04, 0.5, 0.5)
        _GlassWave ("Old glass's waves: x their tilt (radians), y z waves a metre, least and most (glass.json, wave)", Vector) = (0, 4, 9, 0)
        _PineNew ("Bare pine: rgb new (linear), a years to weather half way", Vector) = (0, 0, 0, 1)
        _PineOld ("Bare pine: rgb weathered (linear), a smoothness", Vector) = (0, 0, 0, 0)
        _Stone ("Fieldstone: rgb its mean (linear), a value spread", Vector) = (0, 0, 0, 0)
        _StoneB ("Fieldstone: x warm spread, y smoothness", Vector) = (0, 0, 0, 0)
        _Mortar ("Lime mortar: rgb (linear), a smoothness", Vector) = (0, 0, 0, 0)
        _Render ("Chimney render: rgb (linear), a smoothness", Vector) = (0, 0, 0, 0)
        _WaterPine ("Bare pine's water profile (Water.hlsl): x darkens wet, y wet film's gloss, z holds water, w stains", Vector) = (0, 0, 0, 0)
        _WaterStone ("Fieldstone's water profile", Vector) = (0, 0, 0, 0)
        _WaterMortar ("Lime mortar's water profile", Vector) = (0, 0, 0, 0)
        _WaterRender ("Chimney render's water profile", Vector) = (0, 0, 0, 0)
        _Joint ("The share of the light a mortar joint's back sees between its stones (lime-mortar.json)", Float) = 1
        _JointFar ("The share a joint shows as one face where no stone sides are drawn (lime-mortar.json)", Float) = 1
        _Weather ("Paint weather: x south, y foot (m), z foot, w lap (paint.json)", Vector) = (0, 1, 0, 0)
        _WeatherB ("Paint weather: x how far one board's paint runs ahead of or behind another's (paint.json)", Vector) = (0, 0, 0, 0)
        _Soil ("Soiling: x share a decade at full weather, y most, z its share on the open wall (paint.json, soil)", Vector) = (0, 0, 0, 0)
        _SoilColour ("Soiling: its colour (linear)", Color) = (0.4, 0.42, 0.36, 1)
        _Boarding ("Bare boarding: x, y how much slower or faster a board greys (pine.json, greySpread), z a nail's stain down (m), w its most", Vector) = (1, 1, 0, 0)
        _Nails ("Bare boarding: rgb the nails' stain (linear), a the nails' distance from a board's top (m)", Vector) = (0.3, 0.22, 0.16, 0.07)
        _BoardingB ("Bare boarding: x the nails' distance either side of a board's middle (m), y the stain's width at the nail, z at its end (m), w each board's value apart (share)", Vector) = (0.03, 0.009, 0.02, 0)
        _WeatherC ("Paint weather: x a sill's run-off, y end grain, z the rain's side, w the rain's bearing (rad) (paint.json)", Vector) = (0, 0, 0, 0)
        [Toggle] _Grey ("Grey light: every pigment one grey (to judge form)", Float) = 0
        _Debug ("Debug: 1 the kind as colour, 2 the bake, 3 the normal, 4 the coat's age, 5 its loss, 6 a pane: its facing, its window half width and height, 7 its room unlit by the air", Float) = 0
    }

    HLSLINCLUDE
    #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

    CBUFFER_START(UnityPerMaterial)
        half4 _Room;
        float4 _RoomWall;
        float4 _RoomCeiling;
        float4 _RoomFloor;
        float4 _RoomShape;
        float4 _RoomFurniture;
        float4 _RoomFurniture2;
        float4 _RoomShade;
        half4 _Curtain;
        float4 _CurtainB;
        half4 _Glass;
        half4 _GlassDay;
        float4 _GlassWave;
        half4 _PineNew;
        half4 _PineOld;
        half4 _Stone;
        half4 _StoneB;
        half4 _Mortar;
        half4 _Render;
        half4 _WaterPine;
        half4 _WaterStone;
        half4 _WaterMortar;
        half4 _WaterRender;
        half _Joint;
        half _JointFar;
        float4 _Weather;
        float4 _WeatherB;
        float4 _WeatherC;
        float4 _Soil;
        float4 _SoilColour;
        float4 _Boarding;
        float4 _Nails;
        float4 _BoardingB;
        half _Grey;
        half _Debug;
    CBUFFER_END

    // The houses buffer (LT1Houses, from cache/houses/houses.json): OS_HOUSE_ROWS rows a house, by the house's row on
    // its vertices. For each painted part (OS_PART_*) three rows: its top coat (rgb linear, the year it went on), the
    // coat under it (rgb, 1 when there is one, 0 on bare wood) and (its paint's index, the coats on the wood); then
    // the roof: (its covering's index, the year it was laid).
    #define OS_HOUSE_ROWS 16
    #define OS_PART_BODY 0
    #define OS_PART_BACK 1
    #define OS_PART_TRIM 2
    #define OS_PART_WINDOW 3
    #define OS_PART_DOOR 4
    StructuredBuffer<float4> _OS_Houses;
    // each paint (materials/paint-*.json, by the index houses.json lists them in): chalk (per decade, toward value,
    // keep chroma), gloss (new, old, half years), peel (onset years, span years, flake m, along grain)
    float4 _OS_PaintChalk[4];
    float4 _OS_PaintGloss[4];
    float4 _OS_PaintPeel[4];
    float4 _OS_PaintWater[4];   // its water profile (Water.hlsl)
    // each roof covering (materials/clay-pantile.json, roof-slate.json): new (rgb linear, smoothness), old (rgb, years)
    float4 _OS_CoverNew[4];
    float4 _OS_CoverOld[4];
    float4 _OS_CoverWater[4];
    float4 _OS_Date;

    #include "StreetSurface.hlsl"
    #include "Water.hlsl"

    // the kinds (soup.KINDS)
    #define K_BOARD 0
    #define K_UNDERSIDE 1
    #define K_TRIM 2
    #define K_SASH 3
    #define K_GLASS 4
    // the share of a smooth face's reflection the look's shade adds (StreetLooks.hlsl: look P softens it like paint)
    #if defined(_OS_LOOK_P)
        #define OS_REFL_SHARE 0.85h
    #else
        #define OS_REFL_SHARE 1.0h
    #endif
    #define K_TILE 5
    #define K_STONE 6
    #define K_RENDER 7
    #define K_BOARDING 8
    #define K_DOOR 9
    #define K_ROOM 10
    #define K_METAL 11
    #define K_ENDGRAIN 12
    #define K_MORTAR 13
    #define K_JOINT 14      // the mortar's bed where a level draws no stone sides: the slot between them as one face

    // the coat schemes (soup.SCHEMES) and the painted part each reads, -1 for none
    int OS_PartOf(int scheme)
    {
        return scheme == 1 ? OS_PART_BODY : scheme == 6 ? OS_PART_BACK : scheme == 2 ? OS_PART_TRIM
             : scheme == 3 ? OS_PART_WINDOW : scheme == 4 ? OS_PART_DOOR : -1;
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
            #pragma target 4.5
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #define OS_OCCLUSION 0.35h
            #include "StreetLooks.hlsl"
            #include "Detail.hlsl"
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_fragment _ _OS_LOOK_B _OS_LOOK_D _OS_LOOK_P
            #pragma multi_compile_fragment _ OS_HAZE_OFF
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
                float2 uv6 : TEXCOORD6;
                float2 uv7 : TEXCOORD7;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 positionWS : TEXCOORD1;
                half3 normalWS : TEXCOORD2;
                nointerpolation float4 piece : TEXCOORD3;    // x kind, y house, z seed, w year
                half4 bake : TEXCOORD4;                     // x sky, y ground, z open, w lit seed
                half4 place : TEXCOORD5;                    // x lap height, y shelter, z scheme, w band
                nointerpolation float4 coat : TEXCOORD6;    // the top coat: rgb, the year; a roof's covering: rgb, its smoothness
                nointerpolation half4 under : TEXCOORD7;    // the coat under it: rgb, 1 if any
                nointerpolation half4 info : TEXCOORD8;     // x the paint's index (-1 unpainted), y the coats, z a covering's index
                half2 marks : TEXCOORD9;                    // x a sill's run-off over it, y how near its end grain
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
                o.piece = float4(input.uv1, input.uv2);
                o.bake = half4(input.uv3, input.uv4);
                o.place = half4(input.uv5, input.uv6);
                o.marks = (half2)input.uv7;
                // the house's coat for this part, or its roof's covering as weathered on the date
                int kind = (int)(input.uv1.x + 0.5);
                int row = (int)(input.uv1.y + 0.5) * OS_HOUSE_ROWS;
                int part = OS_PartOf((int)(input.uv6.x + 0.5));
                o.info = half4(-1, 0, 0, 0);
                if (kind == K_TILE)
                {
                    float4 r = _OS_Houses[row + 15];
                    int c = (int)(r.x + 0.5);
                    float k = 1.0 - exp2(-max(0.0, _OS_Date.x - r.y) / max(1.0, _OS_CoverOld[c].a));
                    o.coat = float4(lerp(_OS_CoverNew[c].rgb, _OS_CoverOld[c].rgb, k), _OS_CoverNew[c].a);
                    o.info.z = c;
                }
                else if (part >= 0)
                {
                    o.coat = _OS_Houses[row + 3 * part];
                    o.under = (half4)_OS_Houses[row + 3 * part + 1];
                    o.info = (half4)_OS_Houses[row + 3 * part + 2];
                }
                return o;
            }

            // weathered bare wood, from its years in the weather and its seed
            // A lit room seen through a pane (interior mapping): the ray from the eye through the glass meets a box room
            // behind the window, lit by one lamp hung under its ceiling, with sheer curtains at the window's sides and a
            // valance over it just behind the glass. The glass gives the window's own frame: uv metres from its centre
            // and foot, place x its half width and y its height. The lamp's swing and each window's brightness are its
            // seed's, claiming nothing; every size and colour is the pack's (glass.json, room).
            struct RoomHit
            {
                half3 albedo;   // the room's face the ray meets (wall, ceiling, floor or furniture)
                float3 h, lo, hi, rd, ro, pc;
                half ao;        // its corners' and edges' share
                half ceiling;   // 1 on the ceiling
                half cloth;     // how much of it the curtains cover, where the ray passes them
                half fold;      // the light on the cloth's folds there
                half f;         // what the glass reflects (Schlick, glass's 0.04)
                float th, tz;
                float3 nf;
            };

            // The room behind a pane (interior mapping): the ray from the eye through the glass meets a box room behind
            // the window, its furniture along the back wall, sheer curtains at the window's sides and a valance over it
            // just behind the glass. The glass gives the window's own frame: uv metres from its centre and foot, place x
            // its half width and y its height. Where the furniture stands is the seed's, claiming nothing; every size and
            // colour is the pack's (glass.json, room).
            RoomHit OS_RoomRay(Varyings input, half3 n, half k, float3 t)
            {
                RoomHit r;
                float3 d = normalize(input.positionWS - _WorldSpaceCameraPos);
                r.rd = float3(dot(d, t), d.y, max(-dot(d, (float3)n), 0.02));
                r.ro = float3(input.uv.x, input.uv.y, 0.0);
                float hw = input.place.x, hh = input.place.y;
                float sill = _RoomFloor.a, height = _RoomShape.x;
                r.lo = float3(-_RoomCeiling.a, -sill, 0.0);
                r.hi = float3(_RoomCeiling.a, height - sill, _RoomWall.a);
                float3 tb = (float3(r.rd.x > 0.0 ? r.hi.x : r.lo.x, r.rd.y > 0.0 ? r.hi.y : r.lo.y, r.hi.z) - r.ro) / r.rd;
                r.th = min(min(tb.x, tb.y), tb.z);
                r.tz = tb.z;
                r.h = r.ro + r.rd * r.th;
                r.albedo = _RoomWall.rgb;
                r.ceiling = 0.0h;
                r.nf = float3(0.0, 0.0, -1.0);
                if (r.th == tb.x)
                    r.nf = float3(-sign(r.rd.x), 0.0, 0.0);
                else if (r.th == tb.y)
                {
                    r.albedo = r.rd.y > 0.0 ? _RoomCeiling.rgb : _RoomFloor.rgb;
                    r.ceiling = r.rd.y > 0.0 ? 1.0h : 0.0h;
                    r.nf = float3(0.0, -sign(r.rd.y), 0.0);
                }
                // furniture along the back wall up to its height (a sofa, a sideboard), where the seed puts it
                float sx = (frac(k * 5.31) - 0.5) * 2.0 * _RoomCeiling.a;
                if (r.th == tb.z && r.h.y + sill < _RoomFurniture.a && abs(r.h.x - sx) < _RoomFurniture2.x)
                    r.albedo = _RoomFurniture.rgb;
                // the room's corners and edges see less of the light
                float3 e = min(r.h - r.lo, r.hi - r.h) / _RoomFurniture2.y;
                float edge = r.th == tb.z ? min(e.x, e.y) : r.th == tb.x ? min(e.y, e.z) : min(e.x, e.z);
                r.ao = (half)lerp(_RoomFurniture2.z, 1.0, saturate(edge));
                // the curtains: a sheer cloth gathered in folds
                r.pc = r.ro + r.rd * (_CurtainB.y / r.rd.z);
                float edgeX = hw * (1.0 - _Curtain.a) + 0.012 * sin(r.pc.y * 9.0 + k * 40.0);
                float side = smoothstep(edgeX - 0.006, edgeX + 0.006, abs(r.pc.x));
                float top = smoothstep(hh * (1.0 - _CurtainB.z) - 0.02, hh * (1.0 - _CurtainB.z) + 0.02, r.pc.y);
                float fold = sin(r.pc.x * _CurtainB.w * 6.2832 + 1.7 * sin(r.pc.x * _CurtainB.w * 2.1));
                r.cloth = (half)(saturate(max(side, top)) * _CurtainB.x * (0.8 + 0.2 * fold));
                // its folds turn to and from the window's light: the cloth's ridges lighter, its hollows darker
                r.fold = (half)(1.0 + 0.35 * fold * side);
                r.f = 0.04h + 0.96h * pow(1.0h - (half)saturate(r.rd.z), 5.0h);
                return r;
            }

            // A lit room: one lamp hung under its ceiling (its swing the seed's), its shade glowing, the curtains lit
            // through from the room; returned as the light the pane gives out.
            half3 OS_Room(Varyings input, half3 n, half k, float3 t)
            {
                RoomHit r = OS_RoomRay(input, n, k, t);
                float sill = _RoomFloor.a, height = _RoomShape.x;
                float3 lamp = float3((frac(k * 13.7) - 0.5) * 2.0 * _RoomShape.w, height - sill - _RoomShape.z, 0.5 * _RoomWall.a);
                float3 l = lamp - r.h;
                float l2 = dot(l, l);
                half3 room = r.albedo * r.ao * (half)(_Room.a * saturate(dot(r.nf, l) * rsqrt(l2)) / (_RoomFurniture2.w + l2) + _RoomShape.y);
                // the lamp's shade, where the ray passes it, glowing with the light inside it
                float3 oc = r.ro - lamp;
                float bq = dot(oc, r.rd), cq = dot(oc, oc) - _RoomShade.x * _RoomShade.x;
                if (bq * bq - cq > 0.0 && -bq > 0.0 && -bq < r.th)
                    room = _RoomShade.yzw;
                float3 lc = lamp - r.pc;
                float c2 = dot(lc, lc);
                half3 cloth = _Curtain.rgb * r.fold * (half)(_Room.a * saturate(lc.z * rsqrt(c2)) / (1.0 + c2) + _RoomShape.y);
                room = lerp(room, cloth, r.cloth);
                // the glass passes what it does not reflect
                return room * _Room.rgb * (1.0h - r.f);
            }

            // An unlit room by day: the same room, lit only by the light that comes in at its window, the most near
            // the glass and less to the back, the ceiling less than the walls and floor; the curtains at the glass lit
            // from outside. Returned as the share of the light on the pane's face that comes back out through the
            // glass, so the shade lights it by the light outside the window (glass.json, daylight).
            half3 OS_RoomDay(Varyings input, half3 n, half k, float3 t)
            {
                RoomHit r = OS_RoomRay(input, n, k, t);
                half deep = (half)saturate(r.h.z / max(_RoomWall.a, 0.1));
                half3 room = r.albedo * r.ao * lerp(_GlassDay.x, _GlassDay.y, deep) * lerp(1.0h, _GlassDay.z, r.ceiling);
                room = lerp(room, _Curtain.rgb * _GlassDay.w * r.fold, r.cloth);
                return room * (1.0h - r.f);
            }

            // The town's horizon toward a direction (its elevation, radians): the town's horizon map (TownHorizon.shader)
            // read as OS_TownSky reads it, at the point's own height, between the two of its eight directions round it.
            half OS_HorizonToward(float3 positionWS, half3 n, float3 dir)
            {
                if (_OS_SkyMapOn < 0.5 || _OS_HorizonInfo.w < 0.5)
                    return 0.0h;
                float3 o = positionWS + n * 0.6;
                float2 uv = (o.xz - _OS_SkyMapRect.xy) * _OS_SkyMapRect.z;
                if (any(uv < 0.0) || any(uv > 1.0))
                    return 0.0h;
                float res = _OS_HorizonInfo.x, levels = _OS_HorizonInfo.y;
                float2 f = uv * res - 0.5;
                float2 i0 = floor(f), b = f - i0;
                half4 a0 = 0.0h, a1 = 0.0h;
                [unroll]
                for (int c = 0; c < 4; c++)
                {
                    float2 corner = float2(c & 1, c >> 1);
                    float2 cuv = (clamp(i0 + corner, 0.0, res - 1.0) + 0.5) / res;
                    float g = SAMPLE_TEXTURE2D_LOD(_OS_HorizonGround, sampler_OS_HorizonGround, cuv, 0).r;
                    float tt = sqrt(saturate((o.y - g) / _OS_HorizonInfo.z));
                    float3 uvw = float3(cuv, (tt * (levels - 1.0) + 0.5) / levels);
                    half w = (half)(lerp(1.0 - b.x, b.x, corner.x) * lerp(1.0 - b.y, b.y, corner.y));
                    a0 += w * (half4)SAMPLE_TEXTURE3D_LOD(_OS_Horizon0, sampler_OS_HorizonGround, uvw, 0);
                    a1 += w * (half4)SAMPLE_TEXTURE3D_LOD(_OS_Horizon1, sampler_OS_HorizonGround, uvw, 0);
                }
                half angle[8] = { a0.x, a0.y, a0.z, a0.w, a1.x, a1.y, a1.z, a1.w };
                float a = atan2(dir.z, dir.x);
                float kf = frac(a / 6.283185 + 1.0) * 8.0 - 0.5;
                float k0 = floor(kf);
                int i = (int)(k0 + 8.0) % 8, j = (i + 1) % 8;
                return (half)(lerp(angle[i], angle[j], kf - k0) * HALF_PI);
            }

            half3 OS_Bare(half years, half seed)
            {
                half k = 1.0h - exp2(-years / max(0.1h, _PineNew.a));
                return lerp(_PineNew.rgb, _PineOld.rgb, k) * (1.0h + 0.08h * (seed * 2.0h - 1.0h));
            }

            // A painted face's colour (and its smoothness through gloss), from its top coat and the paint's record:
            // its exposure (unsheltered, facing south, near the wall's foot, at a board's lap edge) runs its years
            // faster; it chalks toward a flat, paler value and loses its gloss; past the paint's onset it is lost in
            // flakes (a grain-long noise against the share lost), showing the coat under it, or the wood where it
            // goes deepest. Further off the face takes the mean of the two (OS_Near).
            half3 OS_Coat(Varyings input, half3 n, int kind, out half gloss, out half age, out half loss)
            {
                int p = (int)(input.info.x + 0.5h);
                float4 chalkP = _OS_PaintChalk[p], glossP = _OS_PaintGloss[p], peelP = _OS_PaintPeel[p];
                age = (half)max(0.0, _OS_Date.x - input.coat.w);
                half e = 1.0h - input.place.y;
                e *= 1.0h + (half)_Weather.x * saturate(-n.z);
                // the side the rain is driven at (x east, z north; its bearing from north, clockwise)
                e *= 1.0h + (half)_WeatherC.z * saturate(dot(n.xz, half2(sin(_WeatherC.w), cos(_WeatherC.w))));
                // how much more water works in here than on the open wall: dirt gathers by this (soil, below)
                half water = 1.0h;
                if (kind == K_BOARD)
                {
                    // where water works in: under a sill's run-off, and the end grain at the board's ends
                    water *= (1.0h + (half)_WeatherC.x * input.marks.x) * (1.0h + (half)_WeatherC.y * input.marks.y);
                    water *= 1.0h + (half)_Weather.z * saturate(1.0h - (half)(input.uv.y / _Weather.y));
                    half lap = 1.0h - input.place.x;
                    water *= 1.0h + (half)_Weather.w * lap * lap * lap;
                    e *= water;
                    // each board its own: one takes paint better than the next (its seed, claiming nothing)
                    e *= 1.0h + (half)_WeatherB.x * (frac((half)input.piece.z * 7.77h) * 2.0h - 1.0h);
                }
                half ea = age * e;
                half seed = (half)input.piece.z;
                // the top coat, each piece a hair different (its seed), chalked by its weathered years
                half3 top = (half3)input.coat.rgb * (1.0h + 0.03h * (seed * 2.0h - 1.0h));
                half chalk = 1.0h - exp(-(half)chalkP.x * ea / 10.0h);
                half3 toward = lerp((half3)chalkP.y, top, (half)chalkP.z);
                half3 c = lerp(top, toward, chalk);
                // dirt and green growth gather where water runs and stands, more each year the coat is up, and only a
                // little on the open wall (paint.json, soil)
                half wet = age * (1.0h - input.place.y) * (water - 1.0h + (half)_Soil.z);
                c = lerp(c, (half3)_SoilColour.rgb, (1.0h - exp(-(half)_Soil.x * wet / 10.0h)) * (half)_Soil.y);
                gloss = lerp((half)glossP.y, (half)glossP.x, exp2(-ea / max(0.5h, (half)glossP.z)));
                loss = saturate((ea - (half)peelP.x) / max(1.0h, (half)peelP.y));
                if (loss <= 0.0h)
                    return c;
                // what lies under: the older coat, as chalked as the top would be at twice its years, else wood
                half3 below = input.under.a > 0.5h ? lerp(input.under.rgb, lerp((half3)chalkP.y, input.under.rgb,
                    (half)chalkP.z), saturate(2.0h * chalk)) : OS_Bare(age, seed);
                half3 wood = OS_Bare(age, seed);
                float2 q = float2(input.uv.x / (peelP.z * peelP.w), input.uv.y / peelP.z) + seed * 17.0;
                float h = 0.45 * OS_Noise(q) + 0.25 * OS_Noise(q * 2.7 + 5.1) + 0.3 * OS_Noise(q * 0.31 + 2.3);
                h = saturate((h - 0.2) / 0.6);
                // flakes are marks centimetres across, so they hold to twice the distance of the fine marks
                // (Detail.hlsl), and by the street stop are the coat's painted shape: its mean
                float footprint = max(length(ddx(input.positionWS)), length(ddy(input.positionWS)));
                half near = OS_Near(0.5 * footprint);
                half off = (half)step(h, loss);
                // a flake goes to the wood as often as the paint lets go of it there, not of the coat under (glossP.w)
                half deep = (half)step(h, loss * glossP.w);
                // round a flake the film has let go: a dark line where it stands off the wood, then its lifted edge
                half shadow = (half)(step(h, loss + 0.012) - off);
                half lifted = (half)(step(h, loss + 0.045) - off) - shadow;
                half3 flaked = lerp(lerp(c * (1.0h - 0.45h * shadow + 0.1h * lifted), below, off), wood, deep);
                half3 mean = lerp(lerp(c, below, loss), wood, loss * (half)glossP.w);
                return lerp(mean, flaked, near);
            }

            void Frag(Varyings input, out half4 outColor : SV_Target0
            #ifdef _WRITE_RENDERING_LAYERS
                , out uint outRenderingLayers : SV_Target1
            #endif
            )
            {
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(input);
                half3 n = NormalizeNormalPerPixel(input.normalWS);
                int kind = (int)(input.piece.x + 0.5);
                // the face's own along-axis in the world (uv.x's direction), from the derivatives outside any branch
                float3 tangentWS = normalize(cross(float3(0.0, 1.0, 0.0), (float3)n) + float3(1e-5, 0.0, 0.0));
                float3 dpx = ddx(input.positionWS), dpy = ddy(input.positionWS);
                tangentWS *= dot(dpx, tangentWS) * ddx(input.uv.x) + dot(dpy, tangentWS) * ddy(input.uv.x) < 0.0 ? -1.0 : 1.0;

                StreetSurface s;
                s.albedo = half3(0.42h, 0.42h, 0.42h);
                s.emission = 0;
                s.metallic = 0;
                s.smoothness = 0.2h;
                s.normalWS = n;
                half age = 0.0h, loss = 0.0h;
                half seed = (half)input.piece.z;
                half4 water = 0;    // its water profile (Water.hlsl); glass and the room take none
                if (kind == K_GLASS)
                {
                    // glass: the room behind it, by day lit by the light at its window (OS_RoomDay); where a room is
                    // lit, its lamp's light too, each window a little different in brightness and warmth (its seed,
                    // claiming nothing)
                    half k = input.bake.w;
                    s.albedo = OS_RoomDay(input, n, k > 0.0h ? k : seed, tangentWS);
                    s.smoothness = _Glass.a;
                    if (k > 0.0h)
                    {
                        half warm = frac(k * 7.13h);
                        s.emission = OS_Room(input, n, k, tangentWS) * _OS_WindowGlow * lerp(0.7h, 1.2h, k)
                                     * lerp(half3(1.0h, 0.92h, 0.82h), half3(1.0h, 1.0h, 1.0h), warm);
                    }
                    // old glass is drawn, never flat: waves across the pane, a few a metre, each pane its own (its
                    // seed, claiming nothing), bend what it reflects (glass.json, wave)
                    float fr = lerp(_GlassWave.y, _GlassWave.z, frac(seed * 3.71));
                    float ph = seed * 43.7;
                    half tilt = (half)(_GlassWave.x * sin((input.uv.y * fr + ph) * 6.2832));
                    half lean = (half)(0.5 * _GlassWave.x * sin((input.uv.x * fr * 0.6 + ph * 1.3) * 6.2832));
                    half3 up = normalize(half3(0.0h, 1.0h, 0.0h) - n * n.y + half3(0.0h, 1e-3h, 0.0h));
                    s.normalWS = normalize(n + up * tilt + (half3)tangentWS * lean);
                    // it reflects the sky where the town leaves it open and the town's walls and ground where they hide
                    // it, both from the light: the shade adds the sky's reflection in one face; added here, the second
                    // face's, and the town in place of the sky it hides (seen from the probe's horizon, as bright as
                    // the town's bounce is beside the horizon's light)
                    float3 v = GetWorldSpaceNormalizeViewDir(input.positionWS);
                    float3 r = reflect(-v, (float3)s.normalWS);
                    float3 rh = normalize(float3(r.x, 0.0, r.z) + float3(1e-4, 0.0, 0.0));
                    half hidden = saturate(((half)OS_HorizonToward(input.positionWS, n, r) - (half)asin(clamp(r.y, -1.0, 1.0))) / 0.06h + 0.5h);
                    float2 suv = GetNormalizedScreenSpaceUV(input.positionCS);
                    half rough = 1.0h - s.smoothness;
                    half3 sky = GlossyEnvironmentReflection((half3)r, input.positionWS, rough, 1.0h, suv);
                    half3 skyH = GlossyEnvironmentReflection((half3)rh, input.positionWS, rough, 1.0h, suv);
                    half3 lum = half3(0.2126h, 0.7152h, 0.0722h);
                    // the sky as the eye would see it that way: through the air (StreetSurface.hlsl, OS_Atmosphere)
                    half3 skySeen = OS_Atmosphere(sky, _WorldSpaceCameraPos + r * 3000.0);
                    half3 town = (half3)_OS_TownBounce.rgb * dot(skyH, lum) / max(dot(OS_SkyFor((half3)rh), lum), 1e-4h);
                    half f1 = 0.04h + 0.96h * pow(1.0h - saturate(dot(s.normalWS, (half3)v)), 5.0h);
                    half f2 = 2.0h * f1 / (1.0h + f1);
                    s.emission += s.smoothness * s.smoothness * (f2 * lerp(skySeen, town, hidden) - OS_REFL_SHARE * f1 * sky);
                }
                else if (kind == K_ROOM)
                {
                    s.albedo = half3(0.03h, 0.03h, 0.03h);
                    s.smoothness = 0.0h;
                }
                else if (input.info.x >= 0.0h)
                {
                    // a painted face: its top coat chalked and dulled by its years in the weather, and where the
                    // weather has worn it through, the coat under it, then the wood (OS_Coat)
                    s.albedo = OS_Coat(input, n, kind, s.smoothness, age, loss);
                    water = lerp((half4)_OS_PaintWater[(int)(input.info.x + 0.5h)], _WaterPine,
                                 loss * (half)_OS_PaintGloss[(int)(input.info.x + 0.5h)].w);
                    if (kind == K_ENDGRAIN)
                        s.albedo *= 0.78h;
                    if (kind == K_METAL)
                        s.smoothness = max(s.smoothness, 0.35h);
                }
                else if (kind == K_TILE)
                {
                    // the covering as weathered since it was laid, each course a little different (its seed)
                    s.albedo = (half3)input.coat.rgb * (1.0h + 0.10h * (seed * 2.0h - 1.0h));
                    s.smoothness = (half)input.coat.a;
                    water = (half4)_OS_CoverWater[(int)(input.info.z + 0.5h)];
                }
                else if (kind == K_STONE)
                {
                    // each fieldstone its own: lighter or darker, warmer or cooler, by its seed
                    half v = 1.0h + _Stone.a * (frac(seed * 13.7h) * 2.0h - 1.0h);
                    half w = _StoneB.x * (frac(seed * 31.3h) * 2.0h - 1.0h);
                    s.albedo = _Stone.rgb * v * half3(1.0h + w, 1.0h, 1.0h - w);
                    s.smoothness = _StoneB.y;
                    water = _WaterStone;
                }
                else if (kind == K_MORTAR || kind == K_JOINT)
                {
                    s.albedo = _Mortar.rgb;
                    s.smoothness = _Mortar.a;
                    water = _WaterMortar;
                }
                else if (kind == K_RENDER)
                {
                    s.albedo = _Render.rgb * (1.0h + 0.06h * (seed * 2.0h - 1.0h));
                    s.smoothness = _Render.a;
                    water = _WaterRender;
                }
                else
                {
                    // bare wood (the boarding nailed over an empty house's openings, and anything unpainted): pale
                    // when put up, grey in a few years in the weather
                    age = (half)max(0.0, _OS_Date.x - input.piece.w);
                    s.albedo = OS_Bare(age, seed);
                    if (kind == K_BOARDING)
                    {
                        // reused boards of mixed stock: each greys at its own pace and is its own value (its seed); the
                        // rust of its two nails at its head runs down the grain, longer with its years up (place x: its
                        // distance from its top, m)
                        s.albedo = OS_Bare(age / lerp((half)_Boarding.x, (half)_Boarding.y, frac(seed * 7.31h)), seed)
                                 * (1.0h + (half)_BoardingB.w * (2.0h * frac(seed * 3.17h) - 1.0h));
                        half below = (half)input.place.x - (half)_Nails.a;
                        half across = abs(abs((half)input.uv.y) - (half)_BoardingB.x);
                        half run = (half)_Boarding.z * saturate(age / 6.0h);
                        half width = 0.5h * lerp((half)_BoardingB.y, (half)_BoardingB.z, saturate(below / max(run, 0.01h)));
                        half stain = saturate(1.0h - across / width) * saturate(below / 0.01h + 1.0h)
                                   * saturate(1.0h - below / max(run, 0.01h)) * (half)_Boarding.w;
                        s.albedo = lerp(s.albedo, (half3)_Nails.rgb, stain);
                    }
                    s.smoothness = _PineOld.a;
                    water = _WaterPine;
                }
                if (_Grey > 0.5h && kind != K_GLASS && kind != K_ROOM)
                    s.albedo = half3(0.42h, 0.42h, 0.42h);
                // the weather (Water.hlsl): rain reaches what the eaves leave open, the most on what faces up; on a
                // wall it runs down the boards and stands longest on their lap edges and at the wall's foot, where
                // the paint weathers first (the paint's weather, _Weather); each material answers it by its profile,
                // a smooth coat glazing as far as its gloss
                if (water.x + water.y > 0.0h)
                {
                    half rain = 1.0h - input.place.y;
                    half lies = lerp(0.5h, 1.0h, saturate(n.y));
                    if (kind == K_BOARD)
                    {
                        half lap = 1.0h - input.place.x;
                        lies *= (1.0h + (half)_Weather.z * saturate(1.0h - (half)(input.uv.y / _Weather.y)) * 0.5h)
                              * (1.0h + (half)_Weather.w * lap * lap * lap * 0.5h);
                    }
                    half wet = OS_WetNow(saturate(lies * rain), n.y, water.z) * rain;
                    OS_Wet(s.albedo, s.smoothness, s.normalWS, wet, water, saturate(s.smoothness * 1.6h), 0.0h, n.y);
                }
                // a joint's back sees only a share of the sky and of a lamp between its stones: all its light, less;
                // a centimetre's mark, it goes to the plinth's mean with the flakes (OS_Near)
                if (kind == K_MORTAR)
                    s.albedo *= lerp(1.0h, _Joint, OS_Near(0.5 * max(length(ddx(input.positionWS)), length(ddy(input.positionWS)))));
                // where no sides are drawn the bed stands for the whole slot, its sides' shade with it, at every distance
                else if (kind == K_JOINT)
                    s.albedo *= _JointFar;

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
                OSBake b = OS_ReadBake(half4(input.bake.x, input.bake.y, input.bake.z, 1.0h));
                b.town = OS_TownSky(input.positionWS, n);
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
                if (_Debug > 6.5)
                    colour = kind == K_GLASS && input.bake.w > 0.0h ? OS_Room(input, n, input.bake.w, tangentWS) * 0.25h : half3(0.0h, 0.0h, 0.0h);
                else if (_Debug > 5.5)
                    colour = kind == K_GLASS ? half3(saturate(dot(normalize(_WorldSpaceCameraPos - input.positionWS), (float3)n)),
                                                     input.place.x * 0.5h, input.place.y * 0.5h) : half3(0.0h, 0.0h, 0.0h);
                else if (_Debug > 4.5)
                    colour = half3(loss, loss, loss);
                else if (_Debug > 3.5)
                    colour = half3(saturate(age / 30.0h), saturate(age / 10.0h), input.info.x >= 0.0h ? 0.2h : 0.0h);
                else if (_Debug > 2.5)
                    colour = n * 0.5h + 0.5h;
                else if (_Debug > 1.5)
                    colour = half3(input.bake.x, input.bake.y, input.bake.z);
                else if (_Debug > 0.5)
                    colour = half3(frac(kind * 0.37h), frac(kind * 0.61h), frac(kind * 0.83h));
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
