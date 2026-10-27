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
        _Glass ("Window glass: rgb an unlit room through it (linear), a its smoothness", Vector) = (0, 0, 0, 0)
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
        _Weather ("Paint weather: x south, y foot (m), z foot, w lap (paint.json)", Vector) = (0, 1, 0, 0)
        _WeatherB ("Paint weather: x how far one board's paint runs ahead of or behind another's (paint.json)", Vector) = (0, 0, 0, 0)
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
        float4 _Weather;
        float4 _WeatherB;
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
    #define K_TILE 5
    #define K_STONE 6
    #define K_RENDER 7
    #define K_BOARDING 8
    #define K_DOOR 9
    #define K_ROOM 10
    #define K_METAL 11
    #define K_ENDGRAIN 12
    #define K_MORTAR 13

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
            half3 OS_Room(Varyings input, half3 n, half k, float3 t)
            {
                float3 d = normalize(input.positionWS - _WorldSpaceCameraPos);
                float3 rd = float3(dot(d, t), d.y, max(-dot(d, (float3)n), 0.02));
                float3 ro = float3(input.uv.x, input.uv.y, 0.0);
                float hw = input.place.x, hh = input.place.y;
                float sill = _RoomFloor.a, height = _RoomShape.x;
                float3 lo = float3(-_RoomCeiling.a, -sill, 0.0), hi = float3(_RoomCeiling.a, height - sill, _RoomWall.a);
                float3 tb = (float3(rd.x > 0.0 ? hi.x : lo.x, rd.y > 0.0 ? hi.y : lo.y, hi.z) - ro) / rd;
                float th = min(min(tb.x, tb.y), tb.z);
                float3 h = ro + rd * th;
                half3 albedo = _RoomWall.rgb;
                float3 nf = float3(0.0, 0.0, -1.0);
                if (th == tb.x)
                    nf = float3(-sign(rd.x), 0.0, 0.0);
                else if (th == tb.y)
                {
                    albedo = rd.y > 0.0 ? _RoomCeiling.rgb : _RoomFloor.rgb;
                    nf = float3(0.0, -sign(rd.y), 0.0);
                }
                // furniture along the back wall up to its height (a sofa, a sideboard), where the seed puts it
                float sx = (frac(k * 5.31) - 0.5) * 2.0 * _RoomCeiling.a;
                if (th == tb.z && h.y + sill < _RoomFurniture.a && abs(h.x - sx) < _RoomFurniture2.x)
                    albedo = _RoomFurniture.rgb;
                float3 lamp = float3((frac(k * 13.7) - 0.5) * 2.0 * _RoomShape.w, height - sill - _RoomShape.z, 0.5 * _RoomWall.a);
                float3 l = lamp - h;
                float l2 = dot(l, l);
                // the room's corners and edges see less of it
                float3 e = min(h - lo, hi - h) / _RoomFurniture2.y;
                float edge = th == tb.z ? min(e.x, e.y) : th == tb.x ? min(e.y, e.z) : min(e.x, e.z);
                half ao = (half)lerp(_RoomFurniture2.z, 1.0, saturate(edge));
                half3 room = albedo * ao * (half)(_Room.a * saturate(dot(nf, l) * rsqrt(l2)) / (_RoomFurniture2.w + l2) + _RoomShape.y);
                // the lamp's shade, where the ray passes it, glowing with the light inside it
                float3 oc = ro - lamp;
                float bq = dot(oc, rd), cq = dot(oc, oc) - _RoomShade.x * _RoomShade.x;
                if (bq * bq - cq > 0.0 && -bq > 0.0 && -bq < th)
                    room = _RoomShade.yzw;
                // the curtains: a sheer cloth gathered in folds, lit through from the room
                float3 pc = ro + rd * (_CurtainB.y / rd.z);
                float side = smoothstep(hw * (1.0 - _Curtain.a) - 0.02, hw * (1.0 - _Curtain.a) + 0.02, abs(pc.x));
                float top = smoothstep(hh * (1.0 - _CurtainB.z) - 0.02, hh * (1.0 - _CurtainB.z) + 0.02, pc.y);
                float fold = 0.75 + 0.25 * sin(pc.x * _CurtainB.w * 6.2832);
                float3 lc = lamp - pc;
                float c2 = dot(lc, lc);
                half3 cloth = _Curtain.rgb * (half)(_Room.a * saturate(lc.z * rsqrt(c2)) / (1.0 + c2) + _RoomShape.y);
                room = lerp(room, cloth, (half)(saturate(max(side, top)) * _CurtainB.x * fold));
                // the glass passes what it does not reflect (Schlick, glass's 0.04)
                half f = 0.04h + 0.96h * pow(1.0h - (half)saturate(rd.z), 5.0h);
                return room * _Room.rgb * (1.0h - f);
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
                if (kind == K_BOARD)
                {
                    e *= 1.0h + (half)_Weather.z * saturate(1.0h - (half)(input.uv.y / _Weather.y));
                    half lap = 1.0h - input.place.x;
                    e *= 1.0h + (half)_Weather.w * lap * lap * lap;
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
                gloss = lerp((half)glossP.y, (half)glossP.x, exp2(-ea / max(0.5h, (half)glossP.z)));
                loss = saturate((ea - (half)peelP.x) / max(1.0h, (half)peelP.y));
                if (loss <= 0.0h)
                    return c;
                // what lies under: the older coat, as chalked as the top would be at twice its years, else wood
                half3 below = input.under.a > 0.5h ? lerp(input.under.rgb, lerp((half3)chalkP.y, input.under.rgb,
                    (half)chalkP.z), saturate(2.0h * chalk)) : OS_Bare(age, seed);
                half3 wood = OS_Bare(age, seed);
                float2 q = float2(input.uv.x / (peelP.z * peelP.w), input.uv.y / peelP.z) + seed * 17.0;
                float h = 0.65 * OS_Noise(q) + 0.35 * OS_Noise(q * 2.7 + 5.1);
                h = saturate((h - 0.2) / 0.6);
                // flakes are marks centimetres across, so they hold to twice the distance of the fine marks
                // (Detail.hlsl), and by the street stop are the coat's painted shape: its mean
                float footprint = max(length(ddx(input.positionWS)), length(ddy(input.positionWS)));
                half near = OS_Near(0.5 * footprint);
                half off = (half)step(h, loss);
                half deep = (half)step(h, loss * 0.3);
                half lifted = (half)(step(h, loss + 0.03) - off) * 0.25h;
                half3 flaked = lerp(lerp(c * (1.0h - lifted), below, off), wood, deep);
                half3 mean = lerp(lerp(c, below, loss), wood, loss * 0.3h);
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
                    // glass: dark and glossy; a lit room behind it gives its light, each window a little different
                    // in brightness and warmth (its seed, claiming nothing)
                    s.albedo = _Glass.rgb;
                    s.smoothness = _Glass.a;
                    half k = input.bake.w;
                    if (k > 0.0h)
                    {
                        half warm = frac(k * 7.13h);
                        s.emission = OS_Room(input, n, k, tangentWS) * _OS_WindowGlow * lerp(0.7h, 1.2h, k)
                                     * lerp(half3(1.0h, 0.92h, 0.82h), half3(1.0h, 1.0h, 1.0h), warm);
                    }
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
                    water = lerp((half4)_OS_PaintWater[(int)(input.info.x + 0.5h)], _WaterPine, loss * 0.3h);
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
                else if (kind == K_MORTAR)
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
