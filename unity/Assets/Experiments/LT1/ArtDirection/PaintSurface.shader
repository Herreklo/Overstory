// The painted corner's one surface (LT1ArtPasses.Paint swaps it in for every renderer's own material for the frame):
// painterly realism, stylised hard (reviews/lt1/art-direction/README.md, What matters). Each face takes a designed
// value from what it is (its class, its kind, its mass), never a map or a noise; the light is designed: the sky by the
// face's normal, calmed on the dark masses so their facets are lost; the lamps as compact pools with their shadows;
// the wet film mirroring the sky and each lamp as one long streak. History is the houses' coats (their age), drawn as
// whole shapes. The air is PaintAir.shader's, after. Every value is a global from Paint.json.
//
// _Class: 1 clay, 2 a house, 3 laid stone, 4 a tree, 6 anything else, 7 a lantern's glass, 8 a lantern's metal.
// House meshes (House.shader): UV0 metres along and up; UV1 x the kind, y the house's row; UV3 the bake (x sky);
// UV4 y a lit window's seed; UV5 x the height on a board from its lap edge (0) to its top (1); UV6 x the coat scheme.
// Stone (Stone.shader): UV2 x the face (0 top, 1 rounded edge, 2 split, 3 bed, 4 pointing, 5 dab, 6 soil); UV3 the bake.
// Clay (Street.shader): UV0 the palette, COLOR the bake (r sky, a a lit window's seed under one).
Shader "Hidden/Overstory/PaintSurface"
{
    Properties
    {
        _Class ("Class", Float) = 0
        _Emit ("A lantern's head: how white", Float) = 0
    }

    HLSLINCLUDE
    #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

    CBUFFER_START(UnityPerMaterial)
        float _Class;
        float _Emit;
    CBUFFER_END

    // what a face is: per slot (Paint.json, surfaces) rgb its value (linear) and a its wet share; B x calm, y gloss,
    // z keep (times its coat or palette), w how much of the lamps' light it takes
    float4 _P_Albedo[48];
    float4 _P_SurfB[48];
    float4 _P_Veil[48];       // x the share of the fog's veil past the near layer a face takes (1 by its distance)
    // the masses that need their own value (street boxes): min xyz, w the slot; max xyz, w the class; x y the normal's
    // up it takes
    float4 _P_MassMin[16];
    float4 _P_MassMax[16];
    float4 _P_MassN[16];
    float _P_MassCount;
    // what the frame hides (a stand-in a lantern replaces): min, max xyz, w the class
    float4 _P_HideMin[4];
    float4 _P_HideMax[4];
    float _P_HideCount;

    bool P_In(float3 s, float3 lo, float3 hi)
    {
        return all(s >= lo) && all(s <= hi);
    }

    // whether this point is one the frame hides
    bool P_Hidden(float3 positionWS)
    {
        float3 s = float3(positionWS.x, positionWS.z, positionWS.y);
        int cls = (int)(_Class + 0.5);
        for (int k = 0; k < (int)_P_HideCount; k++)
            if (cls == (int)(_P_HideMax[k].w + 0.5) && P_In(s, _P_HideMin[k].xyz, _P_HideMax[k].xyz))
                return true;
        return false;
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
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile _ _ADDITIONAL_LIGHTS
            #pragma multi_compile_fragment _ _ADDITIONAL_LIGHT_SHADOWS
            #pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
            #pragma multi_compile _ _CLUSTER_LIGHT_LOOP
            #pragma multi_compile _ _LIGHT_LAYERS
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #include "Paint.hlsl"

            TEXTURE2D(_OS_Albedo);
            TEXTURE2D(_OS_Emit);
            TEXTURE2D(_OS_Glow);
            TEXTURE2D(_OS_Surface);
            SAMPLER(s_point_clamp_sampler);

            float4 _P_Coats[64];      // a house's row * 8 + part: its top coat (rgb linear, year); + 5: (its covering's slot, year)
            float4 _P_Clay;           // the clay's slots: x a wall, y the ground, z a roof, w glass
            float4 _P_ClayRoof;       // x y the normal's up a roof takes
            float4 _P_Lantern;        // x its glass's slot, y its metal's
            float4 _P_SkyUp, _P_SkySide, _P_SkyDown, _P_SkyKey, _P_SkyKeyDir, _P_Occlusion;
            float4 _P_Wet, _P_Refl, _P_Streak, _P_StreakB, _P_Pool, _P_Board;
            float4 _P_Focus, _P_FocusShape, _P_Lines, _P_Window, _P_Coat, _P_CoatB;
            float _P_Date;
            float _P_Mode;            // 0 the colour, 1 the distance from the eye (r) and the coverage (g), for the air; 2 the slot; 3 the street point

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv0 : TEXCOORD0;
                float2 uv1 : TEXCOORD1;
                float2 uv2 : TEXCOORD2;
                float2 uv3 : TEXCOORD3;
                float2 uv4 : TEXCOORD4;
                float2 uv5 : TEXCOORD5;
                float2 uv6 : TEXCOORD6;
                half4 color : COLOR;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float3 normalWS : TEXCOORD1;
                float4 a : TEXCOORD2;   // uv0, uv1
                float4 b : TEXCOORD3;   // uv2, uv3
                float4 c : TEXCOORD4;   // uv4, uv5
                float2 e : TEXCOORD5;   // uv6
                half4 color : TEXCOORD6;
            };

            Varyings Vert(Attributes input)
            {
                Varyings o;
                o.positionWS = TransformObjectToWorld(input.positionOS.xyz);
                o.positionCS = TransformWorldToHClip(o.positionWS);
                o.normalWS = TransformObjectToWorldNormal(input.normalOS);
                o.a = float4(input.uv0, input.uv1);
                o.b = float4(input.uv2, input.uv3);
                o.c = float4(input.uv4, input.uv5);
                o.e = input.uv6;
                o.color = input.color;
                return o;
            }

            // the coat schemes (House.shader, OS_PartOf): the painted part a face reads, -1 for none
            int P_PartOf(int scheme)
            {
                return scheme == 1 ? 0 : scheme == 6 ? 1 : scheme == 2 ? 2 : scheme == 3 ? 3 : scheme == 4 ? 4 : -1;
            }

            half P_Luma(half3 c) { return dot(c, half3(0.2126h, 0.7152h, 0.0722h)); }

            float3 P_LightPosition(uint lightIndex)
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

            float4 Frag(Varyings i, bool front : SV_IsFrontFace) : SV_Target
            {
                // the screen's rates first, outside any branch
                float dUp = length(float2(ddx(i.a.y), ddy(i.a.y)));
                float dBoard = length(float2(ddx(i.c.z), ddy(i.c.z)));
                float fwBoard = max(fwidth(i.c.z), 1e-5);
                if (P_Hidden(i.positionWS))
                    discard;
                float3 p = i.positionWS;
                if (_P_Mode > 2.5)
                    return float4(p.x, p.z, p.y, normalize(i.normalWS).y);   // the street point and the normal's up, for checking
                half3 n = (half3)normalize(i.normalWS) * (front ? 1.0h : -1.0h);
                float3 s = float3(p.x, p.z, p.y);
                int cls = (int)(_Class + 0.5);
                float3 V = normalize(_WorldSpaceCameraPos - p);

                // how much detail this place keeps: whole near the focus, gone past its outer radius
                half detail = 1.0h - (half)smoothstep(_P_Focus.w, _P_FocusShape.x, distance(p, _P_Focus.xyz));

                int slot = (int)(_P_Clay.x + 0.5);
                half3 albedo = 0.5h;
                half3 emission = 0.0h;
                half line_ = 0.0h;
                half sky = 1.0h;
                bool coated = false;

                if (cls == 2)
                {
                    int kind = (int)(i.a.z + 0.5);
                    int row = (int)(i.a.w + 0.5);
                    int part = P_PartOf((int)(i.e.x + 0.5));
                    slot = kind;
                    if (kind == 5)
                        slot = (int)(_P_Coats[row * 8 + 5].x + 0.5);
                    albedo = (half3)_P_Albedo[slot].rgb;
                    sky = (half)i.b.z;
                    if (_P_SurfB[slot].z > 0.5 && part >= 0)
                    {
                        // a painted face: its coat's own colour, greyed by the coat's years as a whole
                        float4 coat = _P_Coats[row * 8 + part];
                        albedo *= (half3)coat.rgb;
                        half age = (half)max(0.0, _P_Date - coat.w);
                        albedo *= 1.0h - (half)_P_Coat.x * saturate(age / (half)_P_Coat.y);
                        coated = true;
                        if (kind == 0 || kind == 8)
                        {
                            // the board's height (m) and its own foot: up the wall less its height on the board
                            float boardH = dUp / max(dBoard, 1e-6);
                            boardH = clamp(boardH, 0.08, 0.4);
                            float foot = i.a.y - i.c.z * boardH;
                            // the soiled band at the wall's foot, where the water a wall sheds gathers (paint.json,
                            // weather): whole boards, higher the older the coat
                            float band = _P_CoatB.x * saturate((age - _P_CoatB.y) / max(_P_Coat.w, 1.0));
                            if (foot < band)
                                albedo *= 1.0h - (half)_P_Coat.z;
                            // the lap's shadow line under each board's edge: whole near the focus, lost past it
                            float t = i.c.z;
                            float fw = fwBoard;
                            float w = _P_Lines.x / boardH;
                            float wd = max(w, _P_Lines.z * fw);
                            half cover = (half)saturate(w / fw);
                            line_ = (half)smoothstep(1.0 - wd - 0.5 * fw, 1.0 - wd + 0.5 * fw, t) * (half)_P_Lines.y * detail * cover;
                        }
                    }
                    if (kind == 4 || kind == 10)
                    {
                        if (i.c.y > 0.0)
                        {
                            // a lit room: its light, each window a little its own (its seed, claiming nothing)
                            half k = frac((half)i.c.y * 7.13h);
                            emission = (half3)_P_Window.rgb * (half)_P_Window.w * lerp(0.85h, 1.1h, k);
                            albedo = 0.0h;
                        }
                    }
                }
                else if (cls == 3)
                {
                    int face = clamp((int)(i.b.x + 0.5), 0, 6);
                    slot = 16 + face;
                    albedo = (half3)_P_Albedo[slot].rgb;
                    sky = (half)i.b.z;
                }
                else if (cls == 7)
                {
                    slot = (int)(_P_Lantern.x + 0.5);
                    emission = (half3)_P_Albedo[slot].rgb * (half)_Emit;
                    albedo = 0.0h;
                }
                else if (cls == 8)
                {
                    slot = (int)(_P_Lantern.y + 0.5);
                    albedo = (half3)_P_Albedo[slot].rgb;
                }
                else
                {
                    // the clay: what it is from its palette swatch and its facing, then the masses that need their own
                    half3 pal = 0.5h, emit = 0.0h, grp = 0.0h;
                    half glossy = 0.0h;
                    if (cls == 1)
                    {
                        pal = SAMPLE_TEXTURE2D_LOD(_OS_Albedo, s_point_clamp_sampler, i.a.xy, 0).rgb;
                        emit = SAMPLE_TEXTURE2D_LOD(_OS_Emit, s_point_clamp_sampler, i.a.xy, 0).rgb;
                        grp = SAMPLE_TEXTURE2D_LOD(_OS_Glow, s_point_clamp_sampler, i.a.xy, 0).rgb;
                        glossy = SAMPLE_TEXTURE2D_LOD(_OS_Surface, s_point_clamp_sampler, i.a.xy, 0).r;
                        sky = i.color.r;
                    }
                    if (glossy > 0.85h)
                        slot = (int)(_P_Clay.w + 0.5);
                    else if (n.y > _P_ClayRoof.y || grp.b > 0.25h)
                        slot = (int)(_P_Clay.y + 0.5);
                    else if (n.y > _P_ClayRoof.x)
                        slot = (int)(_P_Clay.z + 0.5);
                    for (int k = 0; k < (int)_P_MassCount; k++)
                    {
                        if (P_In(s, _P_MassMin[k].xyz, _P_MassMax[k].xyz) && n.y >= _P_MassN[k].x && n.y <= _P_MassN[k].y)
                        {
                            slot = (int)(_P_MassMin[k].w + 0.5);
                            break;
                        }
                    }
                    albedo = lerp((half3)_P_Albedo[slot].rgb, pal, (half)_P_SurfB[slot].z);
                    if (max(emit.r, max(emit.g, emit.b)) > 0.02h && grp.r > 0.5h)
                    {
                        half k = frac((half)i.color.a * 7.13h);
                        emission = (half3)_P_Window.rgb * (half)_P_Window.w * lerp(0.8h, 1.1h, k);
                        albedo = 0.0h;
                    }
                }

                // for the air: the distance from the eye, the coverage, and how much of the fog's veil this face takes
                // (a mass of the near curtain stays in the near layer, however deep it runs)
                if (_P_Mode > 0.5 && _P_Mode < 1.5)
                    return float4(distance(p, _WorldSpaceCameraPos), 1.0, _P_Veil[slot].x, 1.0);
                if (_P_Mode > 1.5)
                    return float4(slot * 4.0 / 255.0, cls * 16.0 / 255.0, 0.0, 1.0);   // which slot, for checking
                half4 B = (half4)_P_SurfB[slot];
                half wetUp = saturate((n.y - (half)_P_Wet.y) / max((half)(_P_Wet.z - _P_Wet.y), 1e-3h));
                half wet = (half)_P_Wet.x * wetUp * (half)_P_Albedo[slot].a;
                albedo *= 1.0h - (half)_P_Wet.w * wet;

                // the sky's light by the face's normal, calmed toward one value on the masses whose facets are lost
                // (a board's own tilt and warp are kept from the sky's light: the wall reads as one plane, and a
                // board is found only where a lamp finds it)
                half3 nE = n;
                if (cls == 2 && (slot == 0 || slot == 8))
                    nE = normalize(half3(n.x, n.y * (half)_P_Board.x, n.z));
                half3 E = nE.y >= 0.0h ? lerp((half3)_P_SkySide.rgb, (half3)_P_SkyUp.rgb, nE.y)
                                       : lerp((half3)_P_SkySide.rgb, (half3)_P_SkyDown.rgb, -nE.y);
                E += (half3)_P_SkyKey.rgb * pow(saturate(dot((float3)nE, _P_SkyKeyDir.xyz) * 0.5 + 0.5), _P_SkyKey.w);
                half3 flat = (half3)_P_SkySide.rgb + (half3)_P_SkyKey.rgb * (half)pow(0.5, _P_SkyKey.w);
                E = lerp(E, flat, B.x);
                E *= lerp(1.0h, saturate(sky), (half)_P_Occlusion.x * (1.0h - B.x));   // a calm face is one with its mass: no bake either

                // the lamps: a compact pool each, shadowed, little over its cap; on a wet face its streak
                half3 lamps = 0.0h, streaks = 0.0h;
                InputData inputData = (InputData)0;
                inputData.positionWS = p;
                inputData.normalizedScreenSpaceUV = GetNormalizedScreenSpaceUV(i.positionCS);
            #if defined(_ADDITIONAL_LIGHTS) || defined(_CLUSTER_LIGHT_LOOP)
                // the streak reads the wet face as one calm plane: its normal drawn toward straight up, so a bumpy
                // stone carries one long streak, not glints
                float3 ns = normalize(lerp((float3)n, float3(0.0, 1.0, 0.0), _P_StreakB.x * saturate(n.y * 4.0)));
                float3 along = (float3)V - ns * dot(V, ns);
                along = normalize(along + float3(0.0, 1e-5, 0.0));
                float3 across = cross(ns, along);
                uint count = GetAdditionalLightsCount();
                LIGHT_LOOP_BEGIN(count)
                    Light l = GetAdditionalLight(lightIndex, p, half4(1, 1, 1, 1));
                    float3 lp = P_LightPosition(lightIndex);
                    float3 L = lp - p;
                    float d = length(L);
                    float3 Ld = L / max(d, 1e-4);
                    half fall = (half)pow(saturate(1.0 - d / _P_Pool.w), _P_Pool.x);
                    fall *= (half)saturate((lp.y + _P_Pool.z - p.y) / max(_P_Pool.z, 0.05));
                    half ndl = saturate((dot((float3)n, Ld) + (half)_P_Pool.y) / (1.0h + (half)_P_Pool.y));
                    half sh = l.shadowAttenuation;
                    lamps += l.color * (fall * ndl * sh);
                    if (wet > 0.0h)
                    {
                        float3 H = normalize(Ld + V);
                        float hz = max(dot(H, ns), 1e-3);
                        float tx = dot(H, across) / hz, ty = dot(H, along) / hz;
                        half sk = (half)exp(-(tx * tx) / (_P_Streak.x * _P_Streak.x) - (ty * ty) / (_P_Streak.y * _P_Streak.y));
                        half hold = (half)saturate(1.0 - d / (_P_Pool.w * _P_Streak.w));
                        streaks += l.color * (sk * sqrt(hold) * sh * wet * (half)_P_Streak.z * B.w);
                    }
                LIGHT_LOOP_END
            #endif

                // the wet film (and a glossy face) mirrors the sky, more at a grazing look
                float3 R = reflect(-V, (float3)n);
                half nv = saturate(dot((float3)n, V));
                half F = (half)_P_Refl.x + (1.0h - (half)_P_Refl.x) * pow(1.0h - nv, (half)_P_Refl.z);
                half3 refl = P_Sky(R) * (F * max(wet, B.y * wetUp) * (half)_P_Refl.y);

                // the lap's line is a shadow: it takes the lamp's light whole and the sky's in part (lost in shade)
                half3 lit = albedo * (E * (1.0h - line_ * (1.0h - (half)_P_Lines.w)) + lamps * (B.w * (1.0h - line_)));
                half3 colour = lit + refl + streaks + emission;
                return float4(colour, 1.0);
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
            #pragma multi_compile_vertex _ _CASTING_PUNCTUAL_LIGHT_SHADOW
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Shadows.hlsl"

            float3 _LightDirection;
            float3 _LightPosition;

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
            };

            Varyings Vert(Attributes input)
            {
                Varyings o;
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
                o.positionCS = positionCS;
                o.positionWS = positionWS;
                return o;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                if (P_Hidden(input.positionWS))
                    discard;
                return 0;
            }
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

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
            };

            Varyings Vert(float4 positionOS : POSITION)
            {
                Varyings o;
                o.positionWS = TransformObjectToWorld(positionOS.xyz);
                o.positionCS = TransformWorldToHClip(o.positionWS);
                return o;
            }

            half Frag(Varyings input) : SV_Target
            {
                if (P_Hidden(input.positionWS))
                    discard;
                return input.positionCS.z;
            }
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
            #pragma multi_compile_fragment _ _GBUFFER_NORMALS_OCT
            #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/Packing.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                half3 normalWS : TEXCOORD1;
            };

            Varyings Vert(Attributes input)
            {
                Varyings o;
                o.positionWS = TransformObjectToWorld(input.positionOS.xyz);
                o.positionCS = TransformWorldToHClip(o.positionWS);
                o.normalWS = TransformObjectToWorldNormal(input.normalOS);
                return o;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                if (P_Hidden(input.positionWS))
                    discard;
                half3 n = normalize(input.normalWS);
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
