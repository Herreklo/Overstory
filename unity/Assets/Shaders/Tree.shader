// Trees: the bark and the leaves of a grown tree (blender/generators/tree.py), lit exactly as the street is (look P,
// the sky term from the bake, the air), with what only a tree has: each leaf turning and falling in its own seeded
// order through the season, light through the leaves against the sun, a bark that is twig-dark at the tips and white
// on the limbs, and fissured at an old trunk's foot. With _OS_LEAVES on it draws the leaf cards.
//
// Bark: UV0 the bark texture (tiles round and along); UV1 x the branch's radius (m), y its height above the ground (m).
// Leaves: UV0 the spray atlas; UV1 x the card's rank in the season (low goes first), y its own seed. COLOR: the bake
// (sky, ground, openness). The atlas's channels: r each leaf's id (0 the twig), g light within the spray, b thickness,
// a coverage. The leaves' normals are their crown mass's planes, so a crown shades as a few planes, not as cards.
Shader "Overstory/Tree"
{
    Properties
    {
        [Toggle(_OS_LEAVES)] _Leaves ("Leaf cards", Float) = 0
        [Toggle] _AlphaToMask ("Leaves: alpha to coverage (smooth edges under MSAA)", Float) = 0
        _Bark ("Bark (r lightness, g lenticels, b fissured foot)", 2D) = "white" {}
        _BarkLight ("Bark: the white of the limbs", Color) = (0.86, 0.85, 0.82, 1)
        _BarkBand ("Bark: its grey bands and lenticels", Color) = (0.55, 0.53, 0.50, 1)
        _Twig ("Twigs", Color) = (0.20, 0.11, 0.09, 1)
        _TwigRadius ("Twig to bark: x radius all twig, y radius all bark (m)", Vector) = (0.012, 0.045, 0, 0)
        _Foot ("Foot: x trunk radius of a full foot, y its height per metre of radius, z strength", Vector) = (0.16, 6.0, 1.0, 0)
        _FootPlate ("Foot: plates", Color) = (0.36, 0.35, 0.33, 1)
        _FootCrack ("Foot: fissures", Color) = (0.06, 0.055, 0.05, 1)
        _Spray ("Leaf sprays (r id, g light, b thickness, a coverage)", 2D) = "white" {}
        _Twigs ("Bare twigs on the same cards (a coverage)", 2D) = "black" {}
        _Green ("Leaves in summer", Color) = (0.26, 0.38, 0.11, 1)
        _Turned ("Leaves turned", Color) = (0.86, 0.62, 0.12, 1)
        _Late ("Leaves late", Color) = (0.50, 0.32, 0.10, 1)
        _Season ("Season: x turned (0 to 1), y fallen (0 to 1)", Vector) = (0.6, 0.25, 0, 0)
        _Through ("Light through the leaves (rgb tint, a strength)", Color) = (1.0, 0.85, 0.45, 0.9)
        _Cutoff ("Coverage cut", Range(0, 1)) = 0.5
        _Hold ("Leaves: how much of their own hue they hold in dim light (dusk)", Range(0, 1)) = 0.6
        _MassShadow ("Leaves: how far out towards the sun their shadow is read (m)", Float) = 8.0
        _InnerGlow ("Leaves: the light bounced and passed inside a sunlit crown", Range(0, 2)) = 0.0
        _LeafSkyTint ("Leaves: how much of the sky's tint their shade takes", Range(0, 2)) = 0.35
        _SunPale ("Leaves: how far the sun's light pales their colour", Range(0, 1)) = 0.35
    }

    HLSLINCLUDE
    #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

    CBUFFER_START(UnityPerMaterial)
        float4 _Bark_ST;
        half4 _BarkLight;
        half4 _BarkBand;
        half4 _Twig;
        float4 _TwigRadius;
        float4 _Foot;
        half4 _FootPlate;
        half4 _FootCrack;
        float4 _Spray_ST;
        half4 _Green;
        half4 _Turned;
        half4 _Late;
        float4 _Season;
        half4 _Through;
        half _Cutoff;
        half _Hold;
        float _MassShadow;
        half _InnerGlow;
        half _LeafSkyTint;
        half _SunPale;
    CBUFFER_END

    TEXTURE2D(_Bark);  SAMPLER(sampler_Bark);
    TEXTURE2D(_Spray); SAMPLER(sampler_Spray);
    TEXTURE2D(_Twigs); SAMPLER(sampler_Twigs);

    #include "StreetSurface.hlsl"

    // A leaf's place in the season's colour: mostly its clump's rank, so a clump turns as one (as a painter sees it),
    // a little its own id; across the tree the most exposed clumps go first. The same leaves first every year.
    half OS_LeafOrder(half rank, half id)
    {
        return saturate(rank * 0.85h + frac(id * 7.31h) * 0.15h);
    }

    // The leaves' coverage at a point: a clump falls as a whole, by its own order (first inside the crown and low in
    // it; leaf by leaf, at a pixel or two a leaf, reads as speckle); twigs stay.
    half OS_LeafCover(half4 m, float2 card)
    {
        bool leaf = m.r > 0.03h;
        // a card's strokes go over a short span of the season, in their own order, so a lobe thins before it goes;
        // its painted twig goes with its last leaves (bare, a fragment would float: the drawn twigs carry the winter)
        half fall = (half)card.y + frac(m.r * 3.7h) * 0.12h;
        if (!leaf)
            fall = (half)card.y + 0.14h;
        return fall < (half)_Season.y ? 0.0h : m.a;
    }

    // The bare twigs a card carries, shown as its leaves fall: the winter crown's haze, where the foliage was.
    half OS_TwigCover(float2 uv, float2 card)
    {
        half bare = smoothstep((half)card.y, (half)card.y + 0.18h, (half)_Season.y);
        return SAMPLE_TEXTURE2D(_Twigs, sampler_Twigs, uv).a * bare;
    }

    // Cut at the coverage threshold (depth, shadows): returns the atlas sample.
    half4 OS_LeafClip(float2 uv, float2 card)
    {
        half4 m = SAMPLE_TEXTURE2D(_Spray, sampler_Spray, uv);
        clip(max(OS_LeafCover(m, card), OS_TwigCover(uv, card)) - _Cutoff);
        return m;
    }

    StreetSurface OS_TreeSurface(float2 uv, float2 extra, half3 normalWS)
    {
        StreetSurface s;
        s.emission = 0;
        s.metallic = 0;
        s.normalWS = normalWS;
    #if defined(_OS_LEAVES)
        half4 m = SAMPLE_TEXTURE2D(_Spray, sampler_Spray, uv);
        half order = OS_LeafOrder((half)extra.x, m.r);
        // turning: each leaf from green to the species' autumn colour as the season passes its order, the first to
        // turn going on to brown; a seeded touch of hue per card
        half t = smoothstep(order - 0.2h, order + 0.2h, (half)_Season.x);
        half late = smoothstep(order + 0.6h, order + 0.75h, (half)_Season.x);
        half3 c = lerp(lerp(_Green.rgb, _Turned.rgb, t), _Late.rgb, late);
        half k = frac((half)extra.x * 13.7h) - 0.5h;
        c *= 1.0h + half3(0.05h, 0.02h, -0.04h) * k;
        c *= 0.25h + 0.75h * m.g;
        s.albedo = m.r > 0.03h ? c : _Twig.rgb * (0.6h + 0.4h * m.g);
        // where the leaves are gone and the bare twigs show, the twigs' colour
        half leafHere = OS_LeafCover(m, extra);
        if (leafHere < _Cutoff)
            s.albedo = _Twig.rgb;
        s.smoothness = 0.18h;
    #else
        half4 b = SAMPLE_TEXTURE2D(_Bark, sampler_Bark, uv);
        float r = extra.x, z = extra.y;
        // white bark with grey bands and dark lenticels on the limbs and trunk; dark twigs
        half3 bark = lerp(_BarkBand.rgb, _BarkLight.rgb, saturate((b.r - 0.6h) / 0.25h));
        bark = lerp(bark, _BarkBand.rgb * 0.2h, b.g * 0.9h);
        half twig = 1.0h - smoothstep((half)_TwigRadius.x, (half)_TwigRadius.y, (half)r);
        half3 c = lerp(bark, _Twig.rgb, twig);
        // an old trunk's foot: cracked into plates and black fissures, higher on a thicker trunk
        half age = saturate((half)(r / _Foot.x));
        half foot = saturate(1.0h - (half)(z / max(_Foot.y * r, 0.05))) * age * age * (half)_Foot.z;
        half3 footc = lerp(_FootPlate.rgb, _FootCrack.rgb, saturate(b.b * 1.4h));
        c = lerp(c, footc, foot * saturate(0.35h + b.b));
        s.albedo = c;
        s.smoothness = 0.12h;
    #endif
        return s;
    }
    ENDHLSL

    SubShader
    {
        Tags { "RenderType" = "TransparentCutout" "RenderPipeline" = "UniversalPipeline" "Queue" = "AlphaTest" }

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode" = "UniversalForward" }
            Cull Off
            AlphaToMask [_AlphaToMask]

            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex Vert
            #pragma fragment Frag

            #pragma shader_feature_local _OS_LEAVES
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
            #include "StreetLooks.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv : TEXCOORD0;
                float2 extra : TEXCOORD1;
                half4 bake : COLOR;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 positionWS : TEXCOORD1;
                half3 normalWS : TEXCOORD2;
                half4 bake : TEXCOORD3;
                float2 extra : TEXCOORD4;
                half cover : TEXCOORD5;
                UNITY_VERTEX_INPUT_INSTANCE_ID
                UNITY_VERTEX_OUTPUT_STEREO
            };

            Varyings Vert(Attributes input)
            {
                Varyings o = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, o);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
                float3 posOS = input.positionOS.xyz;
                o.cover = 1;
            #if !defined(_OS_LEAVES)
                // a twig thinner than a pixel is drawn a pixel wide and covers only its share of it (alpha to
                // coverage): a faint stroke, as a painter sees fine twigs, never a hard ink line
                float3 ws = TransformObjectToWorld(posOS);
                float pixel = 2.0 * distance(ws, _WorldSpaceCameraPos) / (UNITY_MATRIX_P._m11 * _ScreenParams.y);
                float r = input.extra.x;
                float drawnR = max(r, 0.7 * pixel);
                posOS += normalize(input.normalOS) * (drawnR - r);
                o.cover = saturate(r / drawnR);
            #endif
                VertexPositionInputs p = GetVertexPositionInputs(posOS);
                o.positionCS = p.positionCS;
                o.positionWS = p.positionWS;
                o.normalWS = TransformObjectToWorldNormal(input.normalOS);
                o.uv = input.uv;
                o.extra = input.extra;
                o.bake = input.bake;
                return o;
            }

            void Frag(Varyings input, bool front : SV_IsFrontFace, out half4 outColor : SV_Target0
            #ifdef _WRITE_RENDERING_LAYERS
                , out uint outRenderingLayers : SV_Target1
            #endif
            )
            {
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(input);
            #if defined(_OS_LEAVES)
                half4 m = SAMPLE_TEXTURE2D(_Spray, sampler_Spray, input.uv);
                // coverage sharpened to a pixel's width, for alpha to coverage under MSAA (Castano): crisp edges that
                // do not fizz; without MSAA it falls back to the cut
                half leafCover = OS_LeafCover(m, input.extra);
                half twigCover = OS_TwigCover(input.uv, input.extra);
                half cover = max(leafCover, twigCover);
                // a card seen edge-on is a line, not a lobe: it fades as it turns away (its own face, from the screen)
                float3 faceN = normalize(cross(ddx(input.positionWS), ddy(input.positionWS)));
                half facing = abs(dot(faceN, GetWorldSpaceNormalizeViewDir(input.positionWS)));
                cover *= smoothstep(0.12h, 0.38h, facing);
                half alpha = saturate((cover - _Cutoff) / max(fwidth(cover), 1e-4h) + 0.5h);
                // where only bare twigs are, they are a soft tone: their coverage as it is, dithered over the samples
                if (leafCover < _Cutoff)
                    alpha = saturate(twigCover * 2.4h) * smoothstep(0.12h, 0.38h, facing);
                clip(alpha - 0.06h - 0.1h * OS_Hash(input.positionCS.xy));
                // a card shades as its mass: the same normal seen from either side
                half3 n = normalize(input.normalWS);
            #else
                // a twig deep in the foliage shows from the season its leaves fall (bake alpha; 0 always shown)
                if (input.bake.a > 0.001h)
                    clip((half)_Season.y - input.bake.a - 0.04h * OS_Hash(input.positionCS.xy));
                half3 n = normalize(front ? input.normalWS : -input.normalWS);
            #endif
                StreetSurface s = OS_TreeSurface(input.uv, input.extra, n);

                InputData id = (InputData)0;
                id.positionWS = input.positionWS;
                id.positionCS = input.positionCS;
                id.normalWS = s.normalWS;
                id.viewDirectionWS = GetWorldSpaceNormalizeViewDir(input.positionWS);
            #if defined(MAIN_LIGHT_CALCULATE_SHADOWS)
            #if defined(_OS_LEAVES)
                // the sun's shadow read a little out from the leaves towards the light: what shades a mass is the
                // houses and the other masses, not the next card (card by card it is speckle)
                id.shadowCoord = TransformWorldToShadowCoord(input.positionWS + _OS_SunDir.xyz * _MassShadow);
            #else
                id.shadowCoord = TransformWorldToShadowCoord(input.positionWS);
            #endif
            #endif
                id.normalizedScreenSpaceUV = GetNormalizedScreenSpaceUV(input.positionCS);
                id.shadowMask = half4(1, 1, 1, 1);
                OSBake b = OS_ReadBake(input.bake);
                b.town = OS_TownSky(input.positionWS, s.normalWS);

            #if defined(_OS_LEAVES)
                // leaves lit as a painter lights foliage: from the mass's plane, two families (the sun's and the sky's)
                // with a narrow half-tone where the plane turns from the light, a warm band at the turn, no brush noise;
                // the sun's shadow only from what stands outside the mass (read three metres towards the light)
                half3 colour;
                {
                    Light sun = GetMainLight(id.shadowCoord, id.positionWS, half4(1, 1, 1, 1));
                    half ndl = dot(n, sun.direction);
                    half shadow = sun.shadowAttenuation * OS_CloudLight(input.positionWS, sun.direction);
                    // the mass's turn from the light stepped into three values, soft at their edges: shadow, a
                    // half-tone, lit (a painter's planes on a volume)
                    // within the light family too: the planes facing the sun brightest, those turning from it a step
                    // lower, then the half-tone at the turn, then shade (a painter's four planes on a lit mass)
                    half lit = (smoothstep(-0.32h, -0.14h, ndl) * 0.36h + smoothstep(0.1h, 0.26h, ndl) * 0.34h
                              + smoothstep(0.42h, 0.62h, ndl) * 0.30h) * shadow;
                    // the sky's light on leaves keeps only a little of its tint: under an overcast sky a leaf's own
                    // colour is at its truest (a yellow birch in the rain is yellow, not olive)
                    half3 sky = OS_SkyTerm(b, n);
                    half skyLum = dot(sky, half3(0.2126h, 0.7152h, 0.0722h));
                    sky = max(skyLum + (sky - skyLum) * _LeafSkyTint, 0.0h);
                    // a mass's top takes the sky, its underside is in its own shade: stepped like the sun's planes
                    sky *= lerp(0.5h, 1.15h, smoothstep(-0.35h, -0.1h, n.y) * 0.45h + smoothstep(0.1h, 0.4h, n.y) * 0.55h);
                    // the sky's light by what the card sees of the sky through the crown (baked); the sun's by its own
                    // shadow, a little dimmed deep inside
                    half seen = saturate(b.sky);
                    // in the sun a leaf's colour is lifted towards the light's, not deepened: highlights go paler,
                    // never cadmium (a painter's lit foliage)
                    half3 litAlbedo = lerp(s.albedo, dot(s.albedo, half3(0.2126h, 0.7152h, 0.0722h)).xxx, _SunPale);
                    colour = s.albedo * sky + litAlbedo * sun.color * lit * lerp(0.75h, 1.0h, seen);
                    // the inside of a sunlit crown glows: light bounced leaf to leaf and through the leaves, warm with
                    // their colour, so its shade sits near half the lit side, not a hole (only while the crown has sun)
                    half3 glowc = lerp(s.albedo, dot(s.albedo, half3(0.2126h, 0.7152h, 0.0722h)).xxx, 0.45h);
                    colour += s.albedo * glowc * sun.color * _InnerGlow * shadow * (1.0h - smoothstep(-0.12h, 0.3h, ndl));
                    half turn = saturate(1.0h - abs(ndl - 0.09h) * 9.0h) * shadow * 0.6h;
                    colour += s.albedo * sun.color * _OS_EdgeTint.rgb * _OS_EdgeTint.a * turn;
                    // lamps and lit windows nearby
                #if defined(_ADDITIONAL_LIGHTS)
                    uint count = GetAdditionalLightsCount();
                    InputData inputData = id;
                    half4 shadowMask = half4(1, 1, 1, 1);
                    LIGHT_LOOP_BEGIN(count)
                        Light l = GetAdditionalLight(lightIndex, id.positionWS, shadowMask);
                        colour += s.albedo * l.color * l.distanceAttenuation * saturate(dot(n, l.direction) * 0.5h + 0.5h);
                    LIGHT_LOOP_END
                #endif
                }
            #elif defined(_OS_LOOK_B)
                half3 colour = OS_ShadeB(id, s, b, input.positionWS);
            #elif defined(_OS_LOOK_D)
                half3 colour = OS_ShadeD(id, s, b, input.positionWS);
            #elif defined(_OS_LOOK_P)
                half3 colour = OS_ShadeP(id, s, b, input.positionWS);
            #else
                half3 colour = OS_ShadeA(id, s, b);
            #endif
            #if defined(_OS_LEAVES)
                // light through the leaves: strongest looking into a low sun, through thin, lit leaves
                Light main = GetMainLight(id.shadowCoord, id.positionWS, half4(1, 1, 1, 1));
                half into = saturate(dot(-id.viewDirectionWS, main.direction));
                // the light comes through the whole mass: the side of a mass turned from the sun sits behind the
                // rest of it and glows little; its rim, where the light grazes past, glows most (a backlit crown
                // is a dark body with a burning edge)
                half ndlT = dot(n, main.direction);
                half body = lerp(0.12h, 1.0h, smoothstep(-0.8h, -0.15h, ndlT));
                half through = (into * into * into * 0.8h + 0.2h * saturate(-ndlT)) * body
                             * main.shadowAttenuation * OS_CloudLight(input.positionWS, main.direction);
                half isLeaf = m.r > 0.03h ? 1.0h : 0.0h;
                colour += s.albedo * _Through.rgb * main.color * through * m.b * _Through.a * isLeaf;
                // and the sky's own light through a thin leaf, from the side it does not face: shaded leaves glow a little
                colour += s.albedo * OS_SkyFor(-n) * b.sky * b.town * m.b * 0.35h * isLeaf;
                // a painter's hold on local colour: in dim or strongly coloured light (dusk, deep shade) the leaves
                // keep some of their own hue at the light's brightness, so a yellow birch reads yellow, never as a
                // green summer tree; the more the dimmer
                half lum = dot(colour, half3(0.2126h, 0.7152h, 0.0722h));
                half3 own = s.albedo / max(dot(s.albedo, half3(0.2126h, 0.7152h, 0.0722h)), 1e-3h) * lum;
                // only as the light fails (dusk): by day the shade takes the sky's blue, as a painter's does
                colour = lerp(colour, own, _Hold * (1.0h - saturate(lum * 5.0h)));
            #endif
                colour = OS_Atmosphere(colour, input.positionWS);
            #if defined(_OS_LEAVES)
                outColor = half4(colour, alpha);
            #else
                // a fine twig's share of its pixel, dithered across the samples
                half share = saturate(input.cover * 1.6h);
                clip(share - 0.15h * OS_Hash(input.positionCS.xy));
                outColor = half4(colour, share);
            #endif
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
            Cull Off

            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma shader_feature_local _OS_LEAVES
            #pragma multi_compile_instancing
            #pragma multi_compile_vertex _ _CASTING_PUNCTUAL_LIGHT_SHADOW

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Shadows.hlsl"

            float3 _LightDirection;
            float3 _LightPosition;

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv : TEXCOORD0;
                float2 extra : TEXCOORD1;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct ShadowVaryings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float2 extra : TEXCOORD1;
            };

            ShadowVaryings Vert(Attributes input)
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
                ShadowVaryings o;
                o.positionCS = positionCS;
                o.uv = input.uv;
                o.extra = input.extra;
                return o;
            }

            half4 Frag(ShadowVaryings input) : SV_Target
            {
            #if defined(_OS_LEAVES)
                OS_LeafClip(input.uv, input.extra);
            #endif
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
            Cull Off

            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma shader_feature_local _OS_LEAVES
            #pragma multi_compile_instancing

            struct Attributes
            {
                float4 positionOS : POSITION;
                float2 uv : TEXCOORD0;
                float2 extra : TEXCOORD1;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float2 extra : TEXCOORD1;
                UNITY_VERTEX_OUTPUT_STEREO
            };

            Varyings Vert(Attributes input)
            {
                Varyings o = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
                o.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                o.uv = input.uv;
                o.extra = input.extra;
                return o;
            }

            half Frag(Varyings input) : SV_Target
            {
            #if defined(_OS_LEAVES)
                OS_LeafClip(input.uv, input.extra);
            #endif
                return input.positionCS.z;
            }
            ENDHLSL
        }

        Pass
        {
            Name "DepthNormals"
            Tags { "LightMode" = "DepthNormals" }
            ZWrite On
            Cull Off

            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma shader_feature_local _OS_LEAVES
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
                float2 uv : TEXCOORD0;
                float2 extra : TEXCOORD1;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                half3 normalWS : TEXCOORD1;
                float2 extra : TEXCOORD2;
                UNITY_VERTEX_OUTPUT_STEREO
            };

            Varyings Vert(Attributes input)
            {
                Varyings o = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
                o.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                o.normalWS = TransformObjectToWorldNormal(input.normalOS);
                o.uv = input.uv;
                o.extra = input.extra;
                return o;
            }

            void Frag(Varyings input, bool front : SV_IsFrontFace, out half4 outNormalWS : SV_Target0
            #ifdef _WRITE_RENDERING_LAYERS
                , out uint outRenderingLayers : SV_Target1
            #endif
            )
            {
            #if defined(_OS_LEAVES)
                OS_LeafClip(input.uv, input.extra);
                half3 n = normalize(input.normalWS);
            #else
                half3 n = normalize(front ? input.normalWS : -input.normalWS);
            #endif
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
