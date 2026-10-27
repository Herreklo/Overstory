// The town at the city tier (Code/Editor/Town/LT1Town.cs, Light): each mass one colour from the pack, times its vertex
// colour where the mass carries one (the ground's cover, a tree's crown, a boat's paint), lit and aired exactly as the
// street is (StreetLooks.hlsl, StreetSurface.hlsl): the same sun, sky, shade, brush, rain and air, its own colours. A
// pane (_Pane 1) gives out its room's light where its vertex alpha says the room is lit, as bright as the rig's windows.
// Water (_Water 1) is opaque: its colour baked in its vertex colours, its vertex alpha its distance from the nearest
// waterline (-1 to 3 m), from which one light line is drawn round everything standing in it, crisp at any distance.
Shader "Overstory/Town"
{
    Properties
    {
        _BaseColor ("Colour", Color) = (1, 1, 1, 1)
        _Tinted ("Times the vertex colour (0 or 1)", Float) = 0
        _Smoothness ("Smoothness", Range(0, 1)) = 0.08
        _Porosity ("Porosity: how far rain darkens it and keeps it matt", Range(0, 1)) = 0.5
        _Ground ("The share of the ground's light a face sees (the bake's green)", Range(0, 1)) = 0.35
        _Pane ("A window's pane: lit by its vertex alpha (0 or 1)", Float) = 0
        [HDR] _PaneLit ("A lit room's light through its pane, at a window glow of 1", Color) = (1, 0.7, 0.4, 1)
        _Water ("Water: baked colour, a light line by its vertex alpha (0 or 1)", Float) = 0
        _LineColor ("The light line at every waterline", Color) = (0.85, 0.86, 0.82, 1)
        _LineWidth ("The light line's width (m)", Float) = 0.45
        _WaveScale ("Wave scale (per metre)", Float) = 0.35
        _WaveStrength ("Wave strength", Float) = 0.1
        _WaveStretch ("Crests' length over their spacing", Float) = 4
        _WaveWobble ("How far a crest wavers along its length (radians)", Float) = 3
        _Brush ("Share of the look's brushwork", Float) = 1
        _Laps ("Weatherboards' exposure or a roof's courses as they rise (m), 0 for none", Float) = 0
        _Contact ("Walls: the sky hidden under the eaves and at the foot, from the vertex colour (0 or 1)", Float) = 0
        _Card ("Leaf cards: each turned to the eye about its centre by its corner in uv (0 or 1)", Float) = 0
        _CardEdge ("A card full below the facing y, shut above x", Vector) = (0.6, 0.15, 0, 0)
    }

    HLSLINCLUDE
    #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

    CBUFFER_START(UnityPerMaterial)
        half4 _BaseColor;
        half _Tinted;
        half _Smoothness;
        half _Porosity;
        half _Ground;
        half _Pane;
        half4 _PaneLit;
        half _Water;
        half4 _LineColor;
        half _LineWidth;
        half _WaveScale;
        half _WaveStrength;
        half _WaveStretch; half _WaveWobble;
        half _Brush;
        half _Laps;
        half _Contact;
        half _Card;
        float4 _CardEdge;
    CBUFFER_END
    float4 _OS_Laps;    // the laps' line: x full within, y gone by (m), z its shade, w its share of a board
    float4 _OS_Contact; // the sky a wall loses: x under the eaves within (m), y its share there, z above the foot within, w its share

    #include "StreetSurface.hlsl"

    // a leaf card's corner: laid out about the card's centre p across a view with axes right and up, open in full where
    // the crown turns from the eye (its normal n across the line to the eye, toEye) and shut where it faces the eye, so
    // the cards break the crown's outline and its seams with the sky and never its lit face
    float3 OS_CardCorner(float3 p, float3 n, float2 corner, float3 right, float3 up, float3 toEye)
    {
        float open = smoothstep(_CardEdge.x, _CardEdge.y, dot(n, toEye));
        return p + (right * corner.x + up * corner.y) * open;
    }

    // where a vertex stands, a card's corner turned to the camera
    float3 OS_TownPosition(float3 positionOS, float3 normalOS, float2 corner)
    {
        float3 p = TransformObjectToWorld(positionOS);
        if (_Card > 0.5)
            p = OS_CardCorner(p, TransformObjectToWorldNormal(normalOS), corner, UNITY_MATRIX_V[0].xyz, UNITY_MATRIX_V[1].xyz,
                              normalize(GetCameraPositionWS() - p));
        return p;
    }

    // sunlit: how much of the sun reaches the point (1 where shadows are not drawn)
    StreetSurface OS_TownSurface(half4 tint, half3 normalWS, float3 positionWS, half sunlit)
    {
        StreetSurface s;
        if (_Water > 0.5)
        {
            s = OS_WaterSurface(positionWS, half4(tint.rgb, 1), _Smoothness, _WaveScale, 0);
            // the harbour's swell at this tier: parallel crests along the quay, a little wavering along their length, so
            // the mirror breaks into bands across the view and never into glitter; its steepest slope _WaveStrength
            float2 q = positionWS.xz * _WaveScale + float2(0.0, 0.04 * _OS_Time);
            const float e = 0.03;
            #define OS_SWELL(r) (sin(6.2832 * (r).y + _WaveWobble * OS_Noise(float2((r).x / _WaveStretch, (r).y * 0.5))) / 6.2832)
            float sx = OS_SWELL(q + float2(e, 0)) - OS_SWELL(q - float2(e, 0));
            float sz = OS_SWELL(q + float2(0, e)) - OS_SWELL(q - float2(0, e));
            #undef OS_SWELL
            s.normalWS = normalize(half3(-sx * _WaveStrength, 2.0 * e, -sz * _WaveStrength));
            float d = tint.a * 4.0 - 1.0;
            float aa = max(fwidth(d), 1e-3);
            // the light line only where the sun strikes the water at the foot of a thing, never in its shade
            half rim = (half)(1.0 - smoothstep(_LineWidth - aa, _LineWidth + aa, d)) * sunlit;
            s.albedo = lerp(_OS_Clay > 0.5 ? half3(0.10h, 0.10h, 0.10h) : tint.rgb, _LineColor.rgb, rim);
            s.smoothness = lerp(_Smoothness, 0.1h, rim);
            s.normalWS = normalize(lerp(s.normalWS, half3(0, 1, 0), rim));
            return s;
        }
        half3 albedo = _BaseColor.rgb * lerp(half3(1, 1, 1), tint.rgb, _Tinted);
        if (_Laps > 0 && abs(normalWS.y) < 0.95h)
        {
            // weatherboards and roof courses near only: the shadow each board's or course's lower edge lays on the one
            // below, as a line
            float f = frac(positionWS.y / _Laps);
            float aa = max(fwidth(positionWS.y / _Laps), 1e-4);
            half lap = (half)smoothstep(1.0 - _OS_Laps.w - aa, 1.0 - _OS_Laps.w + aa, f);
            half near = 1.0h - (half)smoothstep(_OS_Laps.x, _OS_Laps.y, distance(positionWS, GetCameraPositionWS()));
            // and gone where the boards are finer than a few pixels
            near *= 1.0h - (half)smoothstep(0.15, 0.3, aa);
            albedo *= 1.0h - _OS_Laps.z * lap * near;
        }
        half smoothness = _Smoothness;
        if (_OS_Clay > 0.5)
        {
            albedo = 0.42h;
            smoothness = 0.12h;
        }
        // rain wets what faces the sky, as on the street: porous things darken and stay matt, sealed ones shine
        half wet = _OS_Wetness * saturate((normalWS.y + 0.1h) / 0.6h);
        albedo *= lerp(1.0h, 1.0h - 0.5h * _Porosity, wet);
        smoothness = lerp(smoothness, max(smoothness, lerp(0.85h, 0.2h, _Porosity * _Porosity)), wet);
        s.albedo = albedo;
        s.emission = _Pane > 0.5 ? _PaneLit.rgb * tint.a * _OS_WindowGlow : 0;
        s.smoothness = smoothness;
        s.metallic = 0;
        s.normalWS = normalWS;
        return s;
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
            #pragma multi_compile_fragment _ OS_HAZE_OFF

            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE
            #pragma multi_compile _ _ADDITIONAL_LIGHTS
            #pragma multi_compile_fragment _ _ADDITIONAL_LIGHT_SHADOWS
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BLENDING
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BOX_PROJECTION
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_ATLAS
            #pragma multi_compile_fragment _ _SCREEN_SPACE_REFLECTION
            #pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
            #pragma multi_compile_fragment _ _SCREEN_SPACE_OCCLUSION
            #pragma multi_compile_fragment _ _LIGHT_COOKIES
            #pragma multi_compile _ _LIGHT_LAYERS
            #pragma multi_compile _ _CLUSTER_LIGHT_LOOP
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/RenderingLayers.hlsl"
            #pragma multi_compile_instancing

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #define OS_BRUSH_SHARE _Brush
            #include "StreetLooks.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                half4 color : COLOR;
                float2 corner : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                half3 normalWS : TEXCOORD1;
                half4 color : TEXCOORD2;
                UNITY_VERTEX_INPUT_INSTANCE_ID
                UNITY_VERTEX_OUTPUT_STEREO
            };

            Varyings Vert(Attributes input)
            {
                Varyings o = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, o);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
                o.positionWS = OS_TownPosition(input.positionOS.xyz, input.normalOS, input.corner);
                o.positionCS = TransformWorldToHClip(o.positionWS);
                o.normalWS = TransformObjectToWorldNormal(input.normalOS);
                o.color = input.color;
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
            #if defined(MAIN_LIGHT_CALCULATE_SHADOWS)
                half sunlit = MainLightRealtimeShadow(TransformWorldToShadowCoord(input.positionWS));
            #else
                half sunlit = 1;
            #endif
                StreetSurface s = OS_TownSurface(input.color, NormalizeNormalPerPixel(input.normalWS), input.positionWS, sunlit);

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
                // no bake at this tier: every face sees its whole sky and a share of the ground
                OSBake b = OS_ReadBake(half4(1, _Ground, 1, 1));
                b.town = OS_TownSky(input.positionWS, s.normalWS);
                if (_Contact > 0.5)
                {
                    // a wall's sky, hidden under its eaves by the overhang and at its foot by the ground and its
                    // neighbours: its height above the foot and depth below the eaves in its vertex colour (LT1Town)
                    half h = input.color.g * 10.0h, d = input.color.b * 10.0h;
                    b.sky *= (1.0h - _OS_Contact.y * (1.0h - smoothstep(0.0h, (half)_OS_Contact.x, d)))
                           * (1.0h - _OS_Contact.w * (1.0h - smoothstep(0.0h, (half)_OS_Contact.z, h)));
                }

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
            Cull Back

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
                float2 corner : TEXCOORD0;
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
                if (_Card > 0.5)
                {
                    // a card turned to the light, so the crown's shadow has the fringe's broken edge
                    float3 right = normalize(cross(abs(lightDirectionWS.y) > 0.99 ? float3(1, 0, 0) : float3(0, 1, 0), lightDirectionWS));
                    positionWS = OS_CardCorner(positionWS, normalWS, input.corner, right, cross(lightDirectionWS, right), lightDirectionWS);
                }
                float4 positionCS = TransformWorldToHClip(ApplyShadowBias(positionWS, normalWS, lightDirectionWS));
            #if UNITY_REVERSED_Z
                positionCS.z = min(positionCS.z, UNITY_NEAR_CLIP_VALUE);
            #else
                positionCS.z = max(positionCS.z, UNITY_NEAR_CLIP_VALUE);
            #endif
                return positionCS;
            }

            half4 Frag() : SV_Target
            {
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
            Cull Back

            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_instancing

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 corner : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                UNITY_VERTEX_OUTPUT_STEREO
            };

            Varyings Vert(Attributes input)
            {
                Varyings o = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
                o.positionCS = TransformWorldToHClip(OS_TownPosition(input.positionOS.xyz, input.normalOS, input.corner));
                return o;
            }

            half Frag(Varyings input) : SV_Target
            {
                return input.positionCS.z;
            }
            ENDHLSL
        }

        // normals for the occlusion and, with smoothness in alpha, for screen-space reflections
        Pass
        {
            Name "DepthNormals"
            Tags { "LightMode" = "DepthNormals" }
            ZWrite On
            Cull Back

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
                half4 color : COLOR;
                float2 corner : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                half3 normalWS : TEXCOORD0;
                half4 color : TEXCOORD1;
                float3 positionWS : TEXCOORD2;
                UNITY_VERTEX_OUTPUT_STEREO
            };

            Varyings Vert(Attributes input)
            {
                Varyings o = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
                o.positionWS = OS_TownPosition(input.positionOS.xyz, input.normalOS, input.corner);
                o.positionCS = TransformWorldToHClip(o.positionWS);
                o.normalWS = TransformObjectToWorldNormal(input.normalOS);
                o.color = input.color;
                return o;
            }

            void Frag(Varyings input, out half4 outNormalWS : SV_Target0
            #ifdef _WRITE_RENDERING_LAYERS
                , out uint outRenderingLayers : SV_Target1
            #endif
            )
            {
                StreetSurface s = OS_TownSurface(input.color, normalize(input.normalWS), input.positionWS, 1);
            #if defined(_GBUFFER_NORMALS_OCT)
                float2 oct = PackNormalOctQuadEncode(s.normalWS);
                outNormalWS = half4(PackFloat2To888(saturate(oct * 0.5 + 0.5)), 0.0);
            #else
                outNormalWS = half4(s.normalWS, 0.0);
            #endif
            #if defined(_WRITE_SMOOTHNESS)
                outNormalWS.a = s.smoothness;
            #endif
            #ifdef _WRITE_RENDERING_LAYERS
                outRenderingLayers = EncodeMeshRenderingLayer();
            #endif
            }
            ENDHLSL
        }
    }
}
