// A window's glass (blender/parts/street/house.py, window): the room behind it by day, seen through the pane (interior
// mapping) and lit by the light on the window's face, and the street's light it reflects, bent by the waves of its
// kind of glass, the sky over the far shore only as a flash down from the opening's head. The pane gives its window's frame: uv0 metres from the window's centre and foot; vertex colour R the
// glass's kind (its integer part x 4) and the window's seed (the fraction: where the room's furniture stands), G the
// pane's seed (its waves), B the window's width / 4 m, A its height / 3 m. UV1 reads the house's page for the frame's
// and reveal's occlusion. Every size and colour is the pack's (glass.json), passed by LT1Street. With _OS_MARK it draws
// a window's mark from afar instead (house.py, window): the whole opening as one dark eye where the sash falls small
// on screen, blended over the true window, its post and transom left open as a light cross.
Shader "Overstory/Glass"
{
    Properties
    {
        _Geo ("Geometry page: R occlusion", 2D) = "white" {}
        _Gloss ("The glass's smoothness (glass.json gloss)", Range(0, 1)) = 0.92
        _RoomWall ("The room's walls: rgb (linear), a its depth behind the glass (m)", Vector) = (0.7, 0.6, 0.4, 3.6)
        _RoomCeiling ("The room's ceiling: rgb (linear), a the room's half width (m)", Vector) = (0.85, 0.8, 0.7, 1.8)
        _RoomFloor ("The room's floor: rgb (linear), a the sill's height over it (m)", Vector) = (0.26, 0.15, 0.06, 0.8)
        _RoomShape ("The room: x its height (m), y its corners' reach (m), z their light", Vector) = (2.4, 0.6, 0.45, 0)
        _RoomFurniture ("The room's furniture: rgb (linear), a its height (m)", Vector) = (0.1, 0.06, 0.04, 0.85)
        _RoomFurniture2 ("The room's furniture: x its half length (m)", Vector) = (0.9, 0, 0, 0)
        _Curtain ("Curtains: rgb (linear), a the share of the window's half width each covers", Vector) = (0.9, 0.84, 0.72, 0.5)
        _CurtainB ("Curtains: x opacity, y depth behind the glass (m), z the valance's share of the height, w folds a metre", Vector) = (0.6, 0.07, 0.16, 11)
        _GlassDay ("An unlit room by day: x the glass's transmittance, y the room's own bounce (a share of the light on the face, a square metre of glass), z the glass's share of the opening, w the curtains' share", Vector) = (0.85, 0.011, 1, 0.55)
        _Opposite ("What the panes face (paint.json light.reflect): x the far shore's skyline (sin of its rise), y its value against the horizon's sky, z the water's, w the pane's surfaces", Vector) = (0, 1, 0.7, 1)
        _Kind0 ("Glass kind 0: x its waves' tilt (radians), y z waves a metre, least and most, w its shape (0 rings, 1 waves, 2 one way, 3 flat)", Vector) = (0, 1, 1, 3)
        _Kind1 ("Glass kind 1", Vector) = (0, 1, 1, 3)
        _Kind2 ("Glass kind 2", Vector) = (0, 1, 1, 3)
        _Kind3 ("Glass kind 3", Vector) = (0, 1, 1, 3)
        _Mark ("From afar (glass.json fromAfar): x the sash's sightline (px) under which the mark shows, y the fade either side (px), z the cross's width (px)", Vector) = (4, 0.6, 1.5, 0)
        _Flash ("The sky's flash (glass.json flash): x its band's most depth (a share of the opening's height, 0 the whole pane's sky), y the rise over the skyline (sin) at which it is reached, z its lower edge's softness, w its cap (a share of the light on the face)", Vector) = (0, 0.08, 0.04, 0.45)
        _Board ("The window board (house.json glass.board, from the window's making): x its top over the opening's foot (m), y its nose behind the glass (m, 0 none), z the nose's radius (m)", Vector) = (0, 0, 0, 0)
        _BoardPaint ("The window board's paint: rgb (linear)", Vector) = (0.75, 0.73, 0.68, 0)
        [HideInInspector] _SrcBlend ("", Float) = 1
        [HideInInspector] _DstBlend ("", Float) = 0
        [HideInInspector] _ZWrite ("", Float) = 1
    }

    HLSLINCLUDE
    #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

    CBUFFER_START(UnityPerMaterial)
        float4 _Geo_ST;
        float _Gloss;
        float4 _RoomWall, _RoomCeiling, _RoomFloor, _RoomShape, _RoomFurniture, _RoomFurniture2;
        float4 _Curtain, _CurtainB, _GlassDay, _Opposite;
        float4 _Kind0, _Kind1, _Kind2, _Kind3;
        float4 _Mark, _Flash, _Board, _BoardPaint;
    CBUFFER_END
    ENDHLSL

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "Queue" = "Geometry" }

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode" = "UniversalForward" }
            Blend [_SrcBlend] [_DstBlend]
            ZWrite [_ZWrite]

            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE
            #pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
            #pragma multi_compile_fragment _ _SCREEN_SPACE_OCCLUSION
            #pragma multi_compile_fog
            #pragma multi_compile_instancing
            #pragma shader_feature_local_fragment _OS_MARK
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            TEXTURE2D(_Geo); SAMPLER(sampler_Geo);

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float4 tangentOS : TANGENT;
                float2 uv0 : TEXCOORD0;
                float2 uv1 : TEXCOORD1;
                float2 uv2 : TEXCOORD2;
                float2 uv3 : TEXCOORD3;
                float4 color : COLOR;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float3 normalWS : TEXCOORD1;
                float3 tangentWS : TEXCOORD2;
                float4 uv : TEXCOORD3;
                float4 color : TEXCOORD4;
                float fog : TEXCOORD5;
                float4 mark : TEXCOORD6;
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
                o.tangentWS = n.tangentWS;
                o.uv = float4(v.uv0, v.uv1);
                o.color = v.color;
                o.mark = float4(v.uv2, v.uv3);
                o.fog = ComputeFogFactor(p.positionCS.z);
                return o;
            }

            // How much of a point's sky the window fills, for a surface facing m: the form factor of the window's
            // rectangle (x within hw of its middle, y from the sill up hh) by Lambert's formula for a polygon.
            float WindowSeen(float3 p, float3 m, float hw, float hh)
            {
                float3 v0 = normalize(float3(-hw, 0.0, 0.0) - p), v1 = normalize(float3(hw, 0.0, 0.0) - p);
                float3 v2 = normalize(float3(hw, hh, 0.0) - p), v3 = normalize(float3(-hw, hh, 0.0) - p);
                float s = acos(clamp(dot(v0, v1), -1.0, 1.0)) * dot(normalize(cross(v0, v1) + 1e-6), m)
                        + acos(clamp(dot(v1, v2), -1.0, 1.0)) * dot(normalize(cross(v1, v2) + 1e-6), m)
                        + acos(clamp(dot(v2, v3), -1.0, 1.0)) * dot(normalize(cross(v2, v3) + 1e-6), m)
                        + acos(clamp(dot(v3, v0), -1.0, 1.0)) * dot(normalize(cross(v3, v0) + 1e-6), m);
                return abs(s) / (2.0 * PI);
            }

            // what the glass reflects: the scene's own ambient (its trilight) for the sky, brighter up to the zenith; what
            // the street faces (_Opposite): the far shore's skyline across the harbour, a band of buildings up to x at y of
            // the horizon's sky, stepped a block at a time (seeded texture, claiming nothing), and under the horizon the
            // water, mirroring the sky at z, easing into the ground, with every edge kept sharp as a mirror keeps it; with
            // _Opposite's defaults, the trilight alone
            float Rise(float3 r)
            {
                float block = floor(atan2(r.x, r.z) * 40.0);
                return _Opposite.x * (0.55 + 0.45 * frac(sin(block * 12.9898) * 43758.5453));
            }

            half3 Reflected(float3 r)
            {
                half3 sky = SampleSH(float3(0.0, 1.0, 0.0));
                half3 eq = SampleSH(normalize(float3(r.x, 0.0, r.z) + float3(1e-4, 0.0, 0.0)));
                half3 ground = SampleSH(float3(0.0, -1.0, 0.0));
                float rise = Rise(r);
                half3 above = r.y < rise ? eq * (half)_Opposite.y : lerp(eq, sky, (half)smoothstep(0.0, 0.6, r.y));
                return r.y >= 0.0 ? above : lerp(eq * (half)_Opposite.z, ground, (half)smoothstep(0.0, 0.25, -r.y));
            }

            // The room behind the pane by day (interior mapping): the ray from the eye through the glass meets a box
            // room behind the window, its furniture along the back wall, sheer curtains at the window's sides and a
            // valance over it just behind the glass; lit only by the light that comes in at its window: each surface
            // by how much of its sky the window fills (the floor just inside most, the side walls and ceiling by the
            // glass little, as they see it edge on) and by what it sees through it (the street's view out, Reflected,
            // against the light on the pane's face: a back wall sees the far shore and the water, the floor just inside
            // the sky), and the room's own bounce, as its glass lets in, its corners less again; all of it only through the glass, the frame,
            // the post and the bars taking the rest of the opening (_GlassDay.z); through the glass in and out. Returned as the share of the light on the pane's face that comes back out through the
            // glass. Where the furniture stands is the window's seed's, claiming nothing. The window board of the window's
            // making (_Board) lies at the glass's foot, lit as the room is.
            half3 RoomDay(float3 d, float3 t, float3 n, float2 uv, float hw, float hh, float k, half3 shN)
            {
                float3 rd = float3(dot(d, t), d.y, max(dot(d, -n), 0.02));
                float3 ro = float3(uv, 0.0);
                float sill = _RoomFloor.a, height = _RoomShape.x;
                float3 lo = float3(-_RoomCeiling.a, -sill, 0.0);
                float3 hi = float3(_RoomCeiling.a, height - sill, _RoomWall.a);
                float3 tb = (float3(rd.x > 0.0 ? hi.x : lo.x, rd.y > 0.0 ? hi.y : lo.y, hi.z) - ro) / rd;
                float th = min(min(tb.x, tb.y), tb.z);
                float3 h = ro + rd * th;
                half3 albedo = (half3)_RoomWall.rgb;
                if (th == tb.y)
                    albedo = rd.y > 0.0 ? (half3)_RoomCeiling.rgb : (half3)_RoomFloor.rgb;
                float sx = (frac(k * 5.31) - 0.5) * 2.0 * _RoomCeiling.a;
                if (th == tb.z && h.y + sill < _RoomFurniture.a && abs(h.x - sx) < _RoomFurniture2.x)
                    albedo = (half3)_RoomFurniture.rgb;
                float3 e = min(h - lo, hi - h) / _RoomShape.y;
                float edge = th == tb.z ? min(e.x, e.y) : th == tb.x ? min(e.y, e.z) : min(e.x, e.z);
                half ao = (half)lerp(_RoomShape.z, 1.0, saturate(edge));
                float3 m = th == tb.z ? float3(0.0, 0.0, -1.0) : th == tb.x ? float3(-sign(rd.x), 0.0, 0.0) : float3(0.0, -sign(rd.y), 0.0);
                half seen = (half)WindowSeen(h, m, hw, hh);
                float3 wo = float3(-h.x, 0.5 * hh - h.y, -h.z);
                half3 view = Reflected(normalize(t * wo.x + float3(0.0, wo.y, 0.0) - n * wo.z)) / max(shN, (half3)1e-3);
                half3 room = albedo * ao * (half)_GlassDay.x * (half)_GlassDay.z * ((half)_GlassDay.x * seen * view + (half)_GlassDay.y * (half)(2.0 * hw * hh));
                // the window board (_Board): level with the frame's clear opening, from the glass to its nose, so seen only
                // from above it; lit as the room is, by the window over it (the window from the board's top up) and what
                // it sees through it, so lightest at the glass and less as the window fills less of its sky; its nose
                // rounding over toward the room, turning from the window. Under the board's top only the mark from afar
                // looks (the true glass begins above it), where the opening's foot is the frame and the sash's rail:
                // painted wood at the glass, taken as the board's light there where the board itself shows over at least
                // the foot's height (from 12 m and higher), so the foot does not read as a dark gap under it; where the
                // board shows less (a low window seen from the street) the mark's foot is left as it was
                float zb = 1e5;
                half bon = 0.0h;
                if (_Board.y > 0.0 && rd.y < 0.0)
                {
                    float3 hb = ro.y > _Board.x ? ro + rd * ((_Board.x - ro.y) / rd.y) : float3(ro.x, _Board.x, 0.0);
                    hb.z = max(hb.z, 0.002);
                    bon = ro.y > _Board.x ? 1.0h : (half)smoothstep(0.5 * _Board.x, _Board.x, _Board.y * -rd.y / rd.z);
                    if (hb.z < _Board.y && abs(hb.x) < hw && bon > 0.0h)
                    {
                        zb = hb.z;
                        half bseen = (half)WindowSeen(float3(hb.x, 0.0, hb.z), float3(0.0, 1.0, 0.0), hw, hh - _Board.x);
                        float3 wb = float3(-hb.x, 0.5 * hh - hb.y, -hb.z);
                        half3 bview = Reflected(normalize(t * wb.x + float3(0.0, wb.y, 0.0) - n * wb.z)) / max(shN, (half3)1e-3);
                        half turn = (half)(1.0 - saturate((hb.z - _Board.y + _Board.z) / max(_Board.z, 1e-4)));
                        room = lerp(room, (half3)_BoardPaint.rgb * (half)_GlassDay.x * (half)_GlassDay.z * ((half)_GlassDay.x * bseen * bview * turn + (half)_GlassDay.y * (half)(2.0 * hw * hh)), bon);
                    }
                }
                // the curtains: a sheer cloth gathered in folds, lit from the window
                float3 pc = ro + rd * (_CurtainB.y / rd.z);
                float edgeX = hw * (1.0 - _Curtain.a) + 0.004 * sin(pc.y * 3.1 + k * 40.0);
                // a sheer's gathered edge thins out over its last few centimetres, not a line
                float side = smoothstep(edgeX - 0.01, edgeX + 0.06, abs(pc.x));
                float top = smoothstep(hh * (1.0 - _CurtainB.z) - 0.02, hh * (1.0 - _CurtainB.z) + 0.02, pc.y);
                float fold = sin(pc.x * _CurtainB.w * 6.2832 + 1.7 * sin(pc.x * _CurtainB.w * 2.1));
                half cloth = (half)(saturate(max(side, top)) * _CurtainB.x * (0.8 + 0.2 * fold));
                // the sheers hang down to the board, so where the eye meets the board first they are hidden
                cloth = zb < _CurtainB.y ? cloth * (1.0h - bon) : cloth;
                half lit = (half)(1.0 + 0.35 * fold * side);
                // the cloth lit as the room is, by the window it faces from just behind the glass
                half cseen = (half)WindowSeen(pc, float3(0.0, 0.0, -1.0), hw, hh);
                half3 sheer = (half3)_Curtain.rgb * (half)_GlassDay.w * lit * (half)_GlassDay.x * ((half)_GlassDay.x * cseen + (half)_GlassDay.y);
                return lerp(room, sheer, cloth);
            }

            // The pane's waves, by its kind: crown glass in rings about the disc's centre (off the pane, where its seed
            // puts it), cylinder glass in long waves both ways, drawn glass in waves one way, float glass flat. Each
            // pane its own phase and spacing (its seed, claiming nothing). Returns the normal they turn.
            float3 Waves(float3 n, float3 t, float2 uv, float4 kd, float seed)
            {
                float shape = kd.w;
                if (shape > 2.5 || kd.x <= 0.0)
                    return n;
                float3 up = normalize(float3(0.0, 1.0, 0.0) - n * n.y + float3(0.0, 1e-3, 0.0));
                float fr = lerp(kd.y, kd.z, frac(seed * 3.71));
                float ph = seed * 43.7;
                float2 tilt;
                if (shape < 0.5)
                {
                    float2 c = (float2(frac(seed * 7.13), frac(seed * 3.37)) - 0.5) * 1.6;
                    float2 dv = uv - c;
                    float rr = length(dv);
                    tilt = dv / max(rr, 1e-3) * kd.x * sin((rr * fr + ph) * 6.2832);
                }
                else if (shape < 1.5)
                    tilt = kd.x * float2(0.5 * sin((uv.x * fr * 0.6 + ph * 1.3) * 6.2832), sin((uv.y * fr + ph) * 6.2832));
                else
                    tilt = float2(kd.x * sin((uv.x * fr + ph) * 6.2832), 0.0);
                return normalize(n + t * tilt.x + up * tilt.y);
            }

            // how much of a pixel `p` wide, `d` from a band's middle, a band `w` either side of it covers
            float Band(float d, float w, float p)
            {
                return saturate((min(d + 0.5 * p, w) - max(d - 0.5 * p, -w)) / p);
            }

            half4 Frag(Varyings i) : SV_Target
            {
                half a = 1.0h;
            #if defined(_OS_MARK)
                // the mark from afar: the window's metres a pixel across it and up it, the sash's sightline (i.mark.z) on
                // screen by whichever is larger, the mark faded in under _Mark.x px; where it shows, the post (i.mark.x
                // across) and the transom (i.mark.y up) are left open _Mark.z px wide, never wider than the wood under
                // them (i.mark.w), so the true window's own wood is the cross
                float pu = max(length(float2(ddx(i.uv.x), ddy(i.uv.x))), 1e-6);
                float pv = max(length(float2(ddx(i.uv.y), ddy(i.uv.y))), 1e-6);
                half on = (half)(1.0 - smoothstep(_Mark.x - _Mark.y, _Mark.x + _Mark.y, i.mark.z / min(pu, pv)));
                clip(on - 0.002h);
                float post = i.mark.x > -50.0 ? Band(i.uv.x - i.mark.x, min(0.5 * _Mark.z * pu, 0.5 * i.mark.w), pu) : 0.0;
                float transom = i.mark.y > -50.0 ? Band(i.uv.y - i.mark.y, min(0.5 * _Mark.z * pv, 0.5 * i.mark.w), pv) : 0.0;
                a = on * (half)(1.0 - max(post, transom));
            #endif
                float4 c = i.color;
                float k4 = c.r * 4.0;
                int kind = (int)floor(k4 + 1e-3);
                float wseed = saturate((frac(k4 + 1e-3) - 0.05) / 0.9);
                float4 kd = kind == 0 ? _Kind0 : kind == 1 ? _Kind1 : kind == 2 ? _Kind2 : _Kind3;
                float hw = c.b * 2.0, hh = c.a * 3.0;
                float3 n = normalize(i.normalWS);
                float3 t = normalize(i.tangentWS - n * dot(i.tangentWS, n));
                float3 d = normalize(i.positionWS - _WorldSpaceCameraPos);
                float3 v = -d;

                half3 shN = SampleSH(n);
                half3 albedo = RoomDay(d, t, n, i.uv.xy, hw, hh, wseed, shN);
                float3 nw = Waves(n, t, i.uv.xy, kd, c.g);
                float ao = SAMPLE_TEXTURE2D(_Geo, sampler_Geo, i.uv.zw).r;

                BRDFData brdf;
                half alpha = 1;
                InitializeBRDFData(albedo, 0.0h, half3(0.0h, 0.0h, 0.0h), (half)_Gloss, alpha, brdf);
                float4 sc = TransformWorldToShadowCoord(i.positionWS);
                Light ml = GetMainLight(sc, i.positionWS, half4(1, 1, 1, 1));
                half3 direct = LightingPhysicallyBased(brdf, ml, (half3)nw, (half3)v);
                half nv = saturate(dot(nw, v));
                half3 envD = brdf.diffuse * shN;
                // a pane reflects at both its faces: 2R / (1 + R) for single glazing (_Opposite.w surfaces)
                half3 fr = EnvironmentBRDFSpecular(brdf, Pow4(1.0h - nv));
                fr = fr * (half)_Opposite.w / (1.0h + ((half)_Opposite.w - 1.0h) * fr);
                float3 rv = reflect(d, nw);
                half3 envS = Reflected(rv) * fr;
                // the sky's flash (_Flash): where the pane mirrors sky over the far shore, the sky shows only in a band
                // down from the opening's head, the deeper the higher the reflection rises over the skyline, its lower
                // edge soft above that line, never brighter than _Flash.w of the light on the face; below it the pane
                // mirrors the far shore. The mark from afar shares the opening's frame, so it draws the same band
                float over = rv.y - Rise(rv);
                if (_Flash.x > 0.0 && over > 0.0)
                {
                    float depth = _Flash.x * saturate(over / _Flash.y);
                    half band = (half)smoothstep(0.0, _Flash.z, depth - (1.0 - i.uv.y / hh));
                    half3 shore = SampleSH(normalize(float3(rv.x, 0.0, rv.z) + float3(1e-4, 0.0, 0.0))) * (half)_Opposite.y * fr;
                    envS = lerp(shore, min(envS, (half)_Flash.w * shN), band);
                }
                half aoD = 1.0h, aoI = 1.0h;
            #if defined(_SCREEN_SPACE_OCCLUSION)
                AmbientOcclusionFactor so = GetScreenSpaceAmbientOcclusion(GetNormalizedScreenSpaceUV(i.positionCS));
                aoD = so.directAmbientOcclusion;
                aoI = so.indirectAmbientOcclusion;
            #endif
                half3 col = direct * aoD + (envD + envS) * (half)ao * aoI;
                col = MixFog(col, i.fog);
                return half4(col, a);
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
                outNormalWS.a = 0.92;
            #endif
            #ifdef _WRITE_RENDERING_LAYERS
                outRenderingLayers = EncodeMeshRenderingLayer();
            #endif
            }
            ENDHLSL
        }
    }
}
