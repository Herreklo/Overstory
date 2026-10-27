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
        _WeatherB ("Paint weather: x how far one board's paint runs ahead of or behind another's, y how far a patch of wall's, z the patches' size (m) (paint.json)", Vector) = (0, 0, 1, 0)
        _Soil ("Soiling: x share a decade at full weather, y most, z its share on the open wall (paint.json, soil)", Vector) = (0, 0, 0, 0)
        _SoilColour ("Soiling: its colour (linear)", Color) = (0.4, 0.42, 0.36, 1)
        _WoodHeart ("Softwood (pine.json, source): rgb heartwood new (linear), a the most heart a board has", Vector) = (0.5, 0.3, 0.15, 0.8)
        _WoodBrown ("Softwood weathering: rgb browned by the sun (linear), a its half years", Vector) = (0.3, 0.17, 0.08, 0.4)
        _WoodSilver ("Softwood weathering: rgb silvered (linear), a years at full weather when it begins", Vector) = (0.4, 0.4, 0.36, 5)
        _WoodDamp ("Softwood weathering: rgb dark where it stays wet (linear), a its most", Vector) = (0.1, 0.09, 0.07, 0.5)
        _WoodKnot ("Softwood source: rgb a knot (linear), a knots a metre of board", Vector) = (0.1, 0.05, 0.03, 1)
        _WoodA ("Softwood: x the least heart, y years when silvered whole, z the damp's reach up from a foot (m), w years to its most", Vector) = (0, 12, 0.22, 8)
        _WoodB ("Softwood grain: x, y rings a metre, z latewood darker (new), w the grain's contrast weathered", Vector) = (250, 550, 0.16, 0.22)
        _WoodC ("Softwood grain: x years to weather the grain, y z streaks along it new and old, w checks a board at most", Vector) = (12, 0.05, 0.12, 3)
        _WoodD ("Softwood: x years before checks open, y cupping, z w a knot across, least and most (m)", Vector) = (4, 0.18, 0.012, 0.03)
        _WoodE ("Softwood: x y how much slower or faster a board greys (greySpread), z the reach of a head's shelter down a board (m), w a greyed knot's value, a share of the wood round it", Vector) = (0.5, 2.5, 0.14, 0.62)
        _WoodStock ("The boarding's stock (pine.json, stocks): x y its years in the weather before, z each board's value apart, w the share of boards with a cement film", Vector) = (0, 0, 0.1, 0)
        _WoodFilm ("The boarding's stock: rgb its film (linear), a the most of a board it covers", Vector) = (0.45, 0.43, 0.39, 0)
        _WoodSaw ("Sawing (pine.json, sawings): x the boarding's fibre, y its arrises' wear (m); z w the cladding's", Vector) = (0.09, 0.007, 0.02, 0.002)
        _Rust ("Nail rust (pine.json, nailRust): rgb (linear), a its most", Vector) = (0.16, 0.06, 0.02, 0.7)
        _RustIron ("Nail rust: rgb the iron-black at the nail (linear), a its reach round it (m)", Vector) = (0.025, 0.023, 0.022, 0.009)
        _RustB ("Nail rust: x its run a year (m), y its longest (m), z its width at the nail, w at its tail (m)", Vector) = (0.035, 0.42, 0.011, 0.004)
        _NailsAt ("The boarding's nails (timber.json, boarding): x y from a board's end, least and most (m), z either side of its middle (m)", Vector) = (0.022, 0.04, 0.03, 0)
        _WeatherC ("Paint weather: x a sill's run-off, y end grain, z the rain's side, w the rain's bearing (rad) (paint.json)", Vector) = (0, 0, 0, 0)
        [Toggle] _Grey ("Grey light: every pigment one grey (to judge form)", Float) = 0
        _Debug ("Debug: 1 the kind as colour, 2 the bake, 3 the normal, 4 the coat's age, 5 its loss, 6 a pane: its facing, its window half width and height, 7 its room unlit by the air, 8 the dry albedo, 9 the place (x lap or from the top, y shelter)", Float) = 0
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
        half4 _WoodHeart;
        half4 _WoodBrown;
        half4 _WoodSilver;
        half4 _WoodDamp;
        half4 _WoodKnot;
        float4 _WoodA;
        float4 _WoodB;
        float4 _WoodC;
        float4 _WoodD;
        float4 _WoodE;
        float4 _WoodStock;
        half4 _WoodFilm;
        float4 _WoodSaw;
        half4 _Rust;
        half4 _RustIron;
        float4 _RustB;
        float4 _NailsAt;
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

            // bare wood where paint has gone from it: greyed by the rain in its first years, silvered with more
            // (pine.json, weathering), each piece a hair different (its seed)
            half3 OS_Bare(half years, half seed)
            {
                half k = 1.0h - exp2(-years / max(0.1h, _PineNew.a));
                half sv = saturate((years - _WoodSilver.a) / max(0.5h, (half)_WoodA.y - _WoodSilver.a));
                return lerp(lerp(_PineNew.rgb, _PineOld.rgb, k), _WoodSilver.rgb, sv) * (1.0h + 0.08h * (seed * 2.0h - 1.0h));
            }

            // Unpainted softwood in the weather (materials/pine.json), from its facts: its source (heart and sap,
            // rings, knots), its sawing (a rough face's fibre, worn arrises), its stock (reused boards' years in the
            // weather before, their mixed value, a cement film on some) and its exposure over its years: browned by
            // the sun in months, greyed where the rain washes it, silvered where sun and rain both work, dark where
            // water stays (at its foot on a sill), browner at its top where a head keeps the rain off. A board's own
            // frame: along its length from its top (m), across from its middle (m), its half width and its length.
            // Its seed draws only what claims nothing: its heart, where the pith lay, its knots and checks. Marks too
            // fine for a pixel give way to their mean (the grain to its long streaks).
            half3 OS_Wood(float along, float across, float halfW, float len, float seed, half years, half rain,
                          half sun, float footprint, float2 saw, out half cup)
            {
                float r1 = frac(seed * 7.31), r2 = frac(seed * 3.17), r3 = frac(seed * 13.7), r4 = frac(seed * 29.3);
                float r5 = frac(seed * 51.9), r6 = frac(seed * 71.3), r7 = frac(seed * 97.1), r8 = frac(seed * 113.7);
                // reused stock was in the weather before it went up
                years += (half)lerp(_WoodStock.x, _WoodStock.y, r4);
                // the sun browns it; the rain washes the brown to grey, each board at its own pace, less at its top
                // under the head; sun and rain together silver it
                half wet = rain * (1.0h - 0.75h * (half)saturate(1.0 - along / max(_WoodE.z, 0.01)));
                half pace = (half)lerp(_WoodE.x, _WoodE.y, r1);
                half3 fresh = lerp(_PineNew.rgb, _WoodHeart.rgb, (half)lerp(_WoodA.x, _WoodHeart.a, r2));
                half brown = 1.0h - exp2(-years * (0.4h + 0.6h * sun) / max(0.05h, _WoodBrown.a));
                half grey = 1.0h - exp2(-years * wet / max(0.1h, _PineNew.a * pace));
                half silver = saturate((years * wet * (0.5h + 0.5h * sun) / pace - _WoodSilver.a)
                                       / max(0.5h, (half)_WoodA.y - _WoodSilver.a));
                half3 c = lerp(fresh, _WoodBrown.rgb, brown);
                c = lerp(c, _PineOld.rgb, grey);
                c = lerp(c, _WoodSilver.rgb, silver);
                // mixed stock: each board its own value; a film of cement in patches on some
                c *= 1.0h + (half)_WoodStock.z * (half)(2.0 * r3 - 1.0);
                if (r5 < _WoodStock.w)
                {
                    float fm = OS_Noise(float2(along * 3.0, across * 14.0) + seed * 31.0);
                    c = lerp(c, _WoodFilm.rgb, (half)smoothstep(0.6, 0.68, fm) * _WoodFilm.a * (1.0h - 0.5h * saturate(years / 20.0h)));
                }
                // the grain: the rings of a log sawn through (the pith off to one side, under the face), their latewood
                // darker, more so as the earlywood wears from between them; finer than a pixel they give way to the
                // long streaks along the grain, which hold it from afar
                half old = saturate(years / (half)_WoodC.x);
                float rpm = lerp(_WoodB.x, _WoodB.y, r6);
                float px = (r7 - 0.5) * 0.5, pd = 0.02 + 0.12 * r8;
                float x = across - px;
                float rr = sqrt(x * x + pd * pd) + 0.006 * along + 0.004 * (OS_Noise(float2(along * 1.7, across * 9.0) + seed * 5.0) - 0.5);
                float fw = rpm * footprint * max(abs(x) / max(rr, 1e-3), 0.15);
                half late = (half)(smoothstep(0.55, 0.95, frac(rr * rpm)) * saturate(1.0 - fw * 1.2));
                float st = 0.65 * OS_Noise(float2(along * 1.8, across * 55.0) + seed * 17.0)
                         + 0.35 * lerp(0.5, OS_Noise(float2(along * 4.1, across * 130.0) + seed * 3.0), saturate(1.0 - footprint * 100.0));
                c *= (1.0h - lerp((half)_WoodB.z, (half)_WoodB.w, old) * (late - 0.25h))
                   * (1.0h + lerp((half)_WoodC.y, (half)_WoodC.z, old) * (half)(2.0 * st - 1.0));
                // a rough face's fibre, close up only
                c *= 1.0h + (half)(saw.x * (2.0 * OS_Noise(float2(along * 45.0, across * 700.0) + seed * 13.0) - 1.0) * saturate(1.0 - footprint * 500.0));
                // checks open along the grain with the years, a few hairlines a board, each over a stretch of it
                half checks = 0.0h;
                [unroll]
                for (int i = 0; i < 3; i++)
                {
                    float due = frac(seed * (23.1 + 7.7 * i));
                    float open = saturate((years - _WoodD.x) / max(_WoodD.x, 0.5)) * _WoodC.w / 3.0;
                    if (due < open)
                    {
                        float cx = (frac(seed * (5.3 + 3.1 * i)) - 0.5) * 1.6 * halfW;
                        float cy = len * frac(seed * (2.9 + 1.3 * i));
                        float ch = len * (0.1 + 0.25 * frac(seed * (4.3 + 2.1 * i)));
                        float cw = 0.0015, wd = max(cw, footprint);
                        checks = max(checks, (half)(saturate(1.0 - abs(across - cx) / wd) * (cw / wd)
                                                   * saturate((ch - abs(along - cy)) / 0.02)));
                    }
                }
                c *= 1.0h - 0.6h * checks;
                // knots: dark, oval along the grain, the wood round them darker; weathered, they grey a little
                half knot = 0.0h, halo = 0.0h;
                [unroll]
                for (int k = 0; k < 2; k++)
                {
                    if (frac(seed * (41.7 + 19.3 * k)) < _WoodKnot.a * len * 0.5)
                    {
                        float ky = len * frac(seed * (3.7 + 5.1 * k));
                        float kx = (frac(seed * (8.9 + 2.3 * k)) - 0.5) * 1.4 * halfW;
                        float kr = 0.5 * lerp(_WoodD.z, _WoodD.w, frac(seed * (6.1 + 4.7 * k)));
                        float dd = length(float2((across - kx) / kr, (along - ky) / (kr * 1.8)));
                        float dh = length(float2((across - kx) / kr, (along - ky) / (kr * 4.0)));
                        knot = max(knot, (half)saturate((1.0 - dd) * kr / max(footprint, 0.002) + 0.5));
                        halo = max(halo, (half)(saturate(1.0 - (dh - 1.0) / 1.2) * 0.12));
                    }
                }
                c *= 1.0h - halo;
                c = lerp(c, lerp(_WoodKnot.rgb, c * (half)_WoodE.w, grey), knot);
                // where water stays: up from its foot on the sill, blotched, darker over the years
                half damp = (half)(pow(saturate(1.0 - (len - along) / max(_WoodA.z, 0.01)), 1.5) * saturate(years / max(_WoodA.w, 0.5)))
                          * _WoodDamp.a * (half)(0.6 + 0.8 * OS_Noise(float2(along * 9.0, across * 25.0) + seed * 11.0));
                c = lerp(c, _WoodDamp.rgb, saturate(damp));
                // its arrises worn round, darker
                c *= 1.0h - 0.25h * (half)(saturate((abs(across) - (halfW - saw.y)) / max(saw.y, footprint)) * saturate(saw.y / footprint));
                // a weathered board cups across its width: its face turns away toward its edges
                cup = (half)_WoodD.y * old * (half)(across / max(halfW, 0.01));
                return c;
            }

            // Steel nails at a board's ends (timber.json, boarding: nails), their rust run down the grain below each,
            // longer with the years and wicking unevenly, the head and the wood round it iron-black (pine.json, nailRust)
            half3 OS_NailRust(half3 c, float along, float across, float halfW, float len, float seed, half years, float footprint)
            {
                float run = min(_RustB.y, _RustB.x * years);
                float ax = min(_NailsAt.z, max(halfW - 0.015, 0.0));
                half rust = 0.0h, iron = 0.0h;
                [unroll]
                for (int i = 0; i < 4; i++)
                {
                    float ny = lerp(_NailsAt.x, _NailsAt.y, frac(seed * (13.1 + 7.9 * i)));
                    ny = i >= 2 ? len - ny : ny;
                    float nx = ((i & 1) ? ax : -ax) + (frac(seed * (5.7 + 3.3 * i)) - 0.5) * 0.012;
                    float dy = along - ny, dx = across - nx;
                    iron = max(iron, (half)(saturate(1.0 - length(float2(dx, dy)) / max(_RustIron.a, footprint)) * saturate(years / 2.0)));
                    if (dy > 0.0 && dy < run)
                    {
                        float t = dy / run;
                        float meander = 0.003 * (OS_Noise(float2(dy * 9.0, i * 5.3 + seed * 7.0)) - 0.5);
                        float w = 0.5 * lerp(_RustB.z, _RustB.w, t) * (0.7 + 0.6 * OS_Noise(float2(dy * 25.0, i * 3.1 + seed * 9.0)));
                        float wd = max(w, footprint);
                        rust = max(rust, (half)(saturate(1.5 * (1.0 - abs(dx - meander) / wd)) * (w / wd) * exp(-1.6 * t)));
                    }
                }
                c = lerp(c, _Rust.rgb, rust * _Rust.a);
                return lerp(c, _RustIron.rgb, iron);
            }

            // A painted face's colour (and its smoothness through gloss), from its top coat and the paint's record:
            // its exposure (unsheltered, facing south, on the rain's side) chalks it toward a flat, paler value and
            // dulls its gloss; water working in (under a sill's run-off, at end grain, the wall's foot, a board's lap
            // edge) gathers dirt and makes it fail sooner; past the paint's onset it is lost in flakes, showing the coat
            // under it, or the wood where it goes deepest. On a board the flakes break along the grain in bands across
            // its face, each its own, and start from its lap edge. Further off the face takes the mean (OS_Near).
            half3 OS_Coat(Varyings input, half3 n, int kind, float footprint, float boardH, out half gloss, out half age, out half loss,
                          out half bare)
            {
                bare = 0.0h;
                int p = (int)(input.info.x + 0.5h);
                float4 chalkP = _OS_PaintChalk[p], glossP = _OS_PaintGloss[p], peelP = _OS_PaintPeel[p];
                age = (half)max(0.0, _OS_Date.x - input.coat.w);
                half e = 1.0h - input.place.y;
                e *= 1.0h + (half)_Weather.x * saturate(-n.z);
                // the side the rain is driven at (x east, z north; its bearing from north, clockwise)
                e *= 1.0h + (half)_WeatherC.z * saturate(dot(n.xz, half2(sin(_WeatherC.w), cos(_WeatherC.w))));
                half seed = (half)input.piece.z;
                // how much more water works in here than on the open wall: a sill's run-off, which runs down from it
                // in streaks; the end grain at a board's ends; the wall's foot; a board's lap edge, where it drips
                half water = 1.0h, drinks = 1.0h;
                if (kind == K_BOARD)
                {
                    float sx = input.uv.x + input.piece.y * 13.1 + 0.012 * OS_Noise(float2(input.uv.y * 4.0, input.piece.y));
                    half streaks = (half)(0.15 + 0.85 * smoothstep(0.5, 0.8, 0.65 * OS_Noise(float2(sx * 30.0, 4.7)) + 0.35 * OS_Noise(float2(sx * 80.0, 9.1))));
                    // end grain drinks water only centimetres in from the cut (its mark falls off as its cube)
                    half endg = input.marks.y * input.marks.y * input.marks.y;
                    drinks = 1.0h + (half)_WeatherC.y * endg;
                    water *= (1.0h + (half)_WeatherC.x * input.marks.x * streaks) * drinks;
                    water *= 1.0h + (half)_Weather.z * saturate(1.0h - (half)(input.uv.y / _Weather.y));
                    half lap = 1.0h - input.place.x;
                    water *= 1.0h + (half)_Weather.w * lap * lap * lap;
                    // each board its own: one takes paint better than the next (its seed, claiming nothing)
                    e *= 1.0h + (half)_WeatherB.x * (frac(seed * 7.77h) * 2.0h - 1.0h);
                }
                half ea = age * e;
                half ew = ea * water;
                // a wall's paint holds better in some stretches than others (how well each coat took; claims nothing):
                // a broad patchwork over the wall, so the failure gathers into patches and leaves the rest whole
                if (kind == K_BOARD)
                    ew *= 1.0h + (half)_WeatherB.y * (half)(2.0 * OS_Noise(float2(input.uv.x, input.uv.y) / max(_WeatherB.z, 0.1) + input.piece.y * 7.3) - 1.0);
                // the top coat, each piece a hair different (its seed), chalked by its weathered years
                half3 top = (half3)input.coat.rgb * (1.0h + 0.03h * (seed * 2.0h - 1.0h));
                half chalk = 1.0h - exp(-(half)chalkP.x * ea / 10.0h);
                half3 toward = lerp((half3)chalkP.y, top, (half)chalkP.z);
                half3 c = lerp(top, toward, chalk);
                // dirt and green growth gather where water runs and stands, more each year the coat is up, and only a
                // little on the open wall (paint.json, soil)
                // (end grain drinks water in but holds none on the face, so it fails the paint without gathering dirt)
                half wet = age * (1.0h - input.place.y) * (water / drinks - 1.0h + (half)_Soil.z);
                half grown = (half)_Soil.x * wet / 10.0h;
                c = lerp(c, (half3)_SoilColour.rgb, (1.0h - exp(-grown * grown)) * (half)_Soil.y);
                gloss = lerp((half)glossP.y, (half)glossP.x, exp2(-ea / max(0.5h, (half)glossP.z)));
                loss = saturate((ew - (half)peelP.x) / max(1.0h, (half)peelP.y));
                if (loss <= 0.0h)
                    return c;
                // what lies under: the older coat, as chalked as the top would be at twice its years, else wood, bare
                // for part of the coat's years
                // the paint here let go when its weathered years reached the onset, so the wood has been bare since;
                // where water works in it stays wet under the film's edges and darkens (pine.json, weathering: damp)
                half since = max(0.0h, age - (half)peelP.x / max(e * water, 0.1h));
                half3 wood = OS_Bare(since, seed);
                wood = lerp(wood, _WoodDamp.rgb, _WoodDamp.a * saturate(water - 1.0h) * saturate(since / max((half)_WoodA.w, 0.5h)));
                half3 below = input.under.a > 0.5h ? lerp(input.under.rgb, lerp((half3)chalkP.y, input.under.rgb,
                    (half)chalkP.z), saturate(2.0h * chalk)) : wood;
                float flake = peelP.z, run = peelP.z * peelP.w;
                float h;
                if (kind == K_BOARD)
                {
                    // the film breaks along the grain: in bands across the board's face as wide as its flakes, each
                    // band a run of losses along the grain, every board its own (its face and seed bound them); it
                    // lets go first at the lap edge, where water drips from the board, and works up from there
                    float nb = clamp(boardH / (0.6 * flake), 2.0, 24.0);
                    float bf = input.place.x * nb + 0.7 * (OS_Noise(float2(input.uv.x * 3.0, seed * 37.0)) - 0.5);
                    float band = floor(bf);
                    h = 0.72 * OS_Noise(float2(input.uv.x / run, band * 7.13 + seed * 91.7))
                      + 0.28 * OS_Noise(float2(input.uv.x / (0.25 * run), bf * 2.7 + seed * 13.0));
                    h *= lerp(0.6, 1.0, saturate(input.place.x * 1.8));
                    h = saturate((h - 0.18) / 0.6);
                }
                else
                {
                    float2 q = float2(input.uv.x / run, input.uv.y / flake) + seed * 17.0;
                    h = 0.45 * OS_Noise(q) + 0.25 * OS_Noise(q * 2.7 + 5.1) + 0.3 * OS_Noise(q * 0.31 + 2.3);
                    h = saturate((h - 0.2) / 0.6);
                }
                // flakes are marks centimetres across, so they hold to twice the distance of the fine marks
                // (Detail.hlsl), and by the street stop are the coat's painted shape: its mean
                half near = OS_Near(0.5 * footprint);
                half off = (half)step(h, loss);
                // a flake goes to the wood as often as the paint lets go of it there, not of the coat under (glossP.w)
                half deep = (half)step(h, loss * glossP.w);
                // round a flake the film has let go: a dark line where it stands off the wood, then its lifted edge
                half shadow = (half)(step(h, loss + 0.012) - off);
                half lifted = (half)(step(h, loss + 0.045) - off) - shadow;
                half3 flaked = lerp(lerp(c * (1.0h - 0.45h * shadow + 0.1h * lifted), below, off), wood, deep);
                half3 mean = lerp(lerp(c, below, loss), wood, loss * (half)glossP.w);
                bare = lerp(loss * (half)glossP.w, deep, near);
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
                // a pixel's size on the surface (m), and a board's height on the wall (its up metres a lap's whole)
                float footprint = max(length(dpx), length(dpy));
                float boardH = length(float2(ddx(input.uv.y), ddy(input.uv.y))) / max(length(float2(ddx(input.place.x), ddy(input.place.x))), 1e-5);

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
                    // only where the wood is bare does it drink the rain as bare wood does
                    half bare;
                    s.albedo = OS_Coat(input, n, kind, footprint, boardH, s.smoothness, age, loss, bare);
                    water = lerp((half4)_OS_PaintWater[(int)(input.info.x + 0.5h)], _WaterPine, bare);
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
                        // unpainted boards of the boarding's stock and sawing, weathered by their years on the wall
                        // (OS_Wood): the rain they take (unsheltered, on the rain's side) and the sun (facing south)
                        half side = saturate(dot(n.xz, half2(sin(_WeatherC.w), cos(_WeatherC.w))));
                        half rain = (1.0h - input.place.y) * (1.0h + (half)_WeatherC.z * side) / (1.0h + (half)_WeatherC.z);
                        half sun = saturate(0.5h - 0.5h * n.z);
                        half cup;
                        s.albedo = OS_Wood(input.place.x, input.uv.y, input.marks.x, input.marks.y, input.piece.z, age,
                                           rain, sun, footprint, _WoodSaw.xy, cup);
                        s.albedo = OS_NailRust(s.albedo, input.place.x, input.uv.y, input.marks.x, input.marks.y,
                                               input.piece.z, age, footprint);
                        s.normalWS = normalize(n + (half3)tangentWS * cup);
                    }
                    s.smoothness = _PineOld.a;
                    water = _WaterPine;
                }
                if (_Grey > 0.5h && kind != K_GLASS && kind != K_ROOM)
                    s.albedo = half3(0.42h, 0.42h, 0.42h);
                half3 dry = s.albedo;
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
                    s.albedo *= lerp(1.0h, _Joint, OS_Near(0.5 * footprint));
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
                if (_Debug > 8.5)
                    colour = half3(input.place.x, input.place.y, 0.0h);
                else if (_Debug > 7.5)
                    colour = dry;
                else if (_Debug > 6.5)
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
