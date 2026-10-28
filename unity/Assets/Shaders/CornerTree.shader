// The walked corner's trees (blender/parts/trees/corner.py): a crown as a few masses, never leaves
// (reviews/lt1/art-direction/README.md, the trees). _Part 0 the bark, 1 the crown's mass cards, 2 a solid silhouette
// (the spruce), 3 a shadow proxy. The cards turn to the eye round their pivots; each carries its mass's one smooth
// normal, so a mass takes three values (its lit cap, its side, its shaded underside), each card one value, its hue its
// own. Matte. The crown loses itself upward into the air.
//
// Two lights: the heart's (the street's sky term, sun, lamps and air: StreetLooks.hlsl) and, with CT_PAINTED, the
// painted corner's (its globals, ArtDirection/Paint.hlsl; the corner that set them, and its air, are removed). Every
// value is a material property set from data (LT1CornerTrees.cs).
//
// Mesh: COLOR r the sky the point sees, g its height in the crown (0 its foot, 1 its top), b its lobe's up (wood: the
// foliage's shade round it), a its seed.
// Cards: UV0 the atlas, UV1 (mass, seed), UV2 the corner's offset in the view plane (m). Bark: UV0 tiles round and
// along, UV1 (radius, height above the foot).
Shader "Overstory/CornerTree"
{
    Properties
    {
        _Part ("Part: 0 bark, 1 crown cards, 2 solid, 3 shadow proxy", Float) = 0
        _Grey ("1: one matte grey, to judge form and light alone", Float) = 0
        _Cards ("Mass cards (r depth in, g leaf seed, a coverage)", 2D) = "white" {}
        _Cutoff ("Coverage cut", Range(0, 1)) = 0.45
        [Toggle] _AlphaToMask ("Alpha to coverage", Float) = 1
        _Albedo ("Albedo (linear)", Color) = (0.2, 0.18, 0.08, 1)
        _Albedo2 ("Albedo: the other end of the cards' hues (linear)", Color) = (0.2, 0.15, 0.06, 1)
        _Bands ("Mass values: x cap's split (normal up), y underside's split, z softness, w each card's own stray", Vector) = (0.45, -0.2, 0.08, 0.25)
        _Values ("Mass values: x cap, y side, z underside, w the sun's share on the shade side", Vector) = (1, 0.62, 0.32, 0)
        _Lost ("Lost upward: x from the crown's height share, y how far into the air at the top", Vector) = (0.7, 0.6, 0, 0)
        _Foot ("Bark's foot: x the dark foot's height (m), y how dark, z contact shade's height (m), w how dark", Vector) = (0.9, 0.55, 0.35, 0.6)
        _FootColour ("Bark's foot (linear)", Color) = (0.08, 0.075, 0.07, 1)
        _Marks ("Bark's marks: x cells round, y cell height (m), z share marked, w darkness", Vector) = (3, 0.32, 0.35, 0.75)
        _MarkReach ("Bark's marks: gone past (m)", Float) = 12
        _BarkTile ("Bark's UV0 tile: x round (m), y along (m) (tree.py's PARTS bark)", Vector) = (0.3, 0.6, 0, 0)
        _TwigColour ("Twigs' colour, below the white limbs (linear)", Color) = (0.07, 0.05, 0.045, 1)
        _TwigR ("Twigs: x radius below which a stem is all twig, y above which all limb (m)", Vector) = (0.015, 0.05, 0, 0)
        _Lamp ("Lamp-lit side: x reach (m), y strength, z wrap, w its band's softness", Vector) = (14, 0.5, 0.25, 0.2)
        _LampColour ("Lamp-lit side: the lamp's colour (linear)", Color) = (1, 0.6, 0.3, 1)
        _LampPos ("Lamp-lit side: the lamp's head (world)", Vector) = (0, -1000, 0, 0)
        _Veil ("Painted: the share of the fog's veil it takes", Float) = 1
        _Near ("Near trees darker: x from (m), y to (m), z the value at x and nearer", Vector) = (12, 40, 1, 0)
    }

    HLSLINCLUDE
    #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

    CBUFFER_START(UnityPerMaterial)
        float4 _Cards_ST;
        float _Part;
        float _Grey;
        float _Cutoff;
        half4 _Albedo;
        half4 _Albedo2;
        float4 _Bands;
        float4 _Values;
        float4 _Lost;
        float4 _Foot;
        half4 _FootColour;
        float4 _Marks;
        float _MarkReach;
        float4 _BarkTile;
        half4 _TwigColour;
        float4 _TwigR;
        float4 _Lamp;
        half4 _LampColour;
        float4 _LampPos;
        float _Veil;
        float4 _Near;
    CBUFFER_END

    TEXTURE2D(_Cards); SAMPLER(sampler_Cards);

    // A card turned to the eye: its vertex is its pivot, its offset laid along the view's right and up.
    float3 CT_CardWS(float3 positionOS, float2 offset, float3 right, float3 up)
    {
        float3 pivot = TransformObjectToWorld(positionOS);
        float s = length(float3(UNITY_MATRIX_M._m00, UNITY_MATRIX_M._m10, UNITY_MATRIX_M._m20));
        return pivot + (right * offset.x + up * offset.y) * s;
    }

    float3 CT_Position(float3 positionOS, float2 offset)
    {
        if (_Part > 0.5 && _Part < 1.5)
            return CT_CardWS(positionOS, offset, UNITY_MATRIX_V[0].xyz, UNITY_MATRIX_V[1].xyz);
        return TransformObjectToWorld(positionOS);
    }

    // The card's coverage, cut: only the crown's cards are cut
    half CT_Cover(float2 uv)
    {
        half a = SAMPLE_TEXTURE2D(_Cards, sampler_Cards, uv).a;
        half cards = (half)(step(0.5, _Part) * step(_Part, 1.5));
        a = lerp(1.0h, a, cards);
        clip(a - (half)_Cutoff * cards);
        return a;
    }
    ENDHLSL

    SubShader
    {
        Tags { "RenderType" = "TransparentCutout" "RenderPipeline" = "UniversalPipeline" "Queue" = "AlphaTest" "OverstoryPaint" = "Own" }

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
            #pragma multi_compile_fragment _ OS_HAZE_OFF
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE
            #pragma multi_compile _ _ADDITIONAL_LIGHTS
            #pragma multi_compile_fragment _ _ADDITIONAL_LIGHT_SHADOWS
            #pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
            #pragma multi_compile_fragment _ _SCREEN_SPACE_OCCLUSION
            #pragma multi_compile _ _LIGHT_LAYERS
            #pragma multi_compile _ _CLUSTER_LIGHT_LOOP
            #pragma multi_compile_instancing
            #pragma multi_compile_local_fragment _ CT_PAINTED
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #include "StreetSurface.hlsl"
            #include "StreetLooks.hlsl"
            #include "Assets/Experiments/LT1/ArtDirection/Paint.hlsl"

            // the painted corner's globals this reads under CT_PAINTED
            float4 _P_SkyUp, _P_SkySide, _P_SkyDown;
            float4 _P_LampPos[8];
            float _P_LampCount;
            float _P_Mode;

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv0 : TEXCOORD0;
                float2 uv1 : TEXCOORD1;
                float2 uv2 : TEXCOORD2;
                half4 color : COLOR;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv0 : TEXCOORD0;
                float2 uv1 : TEXCOORD1;
                float3 positionWS : TEXCOORD2;
                half3 normalWS : TEXCOORD3;
                half4 color : TEXCOORD4;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            Varyings Vert(Attributes input)
            {
                Varyings o = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, o);
                o.positionWS = CT_Position(input.positionOS.xyz, input.uv2);
                o.positionCS = TransformWorldToHClip(o.positionWS);
                o.normalWS = TransformObjectToWorldNormal(input.normalOS);
                o.uv0 = input.uv0;
                o.uv1 = input.uv1;
                o.color = input.color;
                return o;
            }

            half CT_Luma(half3 c) { return dot(c, half3(0.2126h, 0.7152h, 0.0722h)); }

            // a mass's three values by where its normal points: its lit cap, its side, its shaded underside; each card
            // turns at its own height on the mass (seeded), so the edge between values follows the cards' shapes
            half CT_MassValue(half up, half seed)
            {
                half j = (seed - 0.5h) * (half)_Bands.w;
                half cap = smoothstep((half)(_Bands.x - _Bands.z), (half)(_Bands.x + _Bands.z), up + j);
                half side = smoothstep((half)(_Bands.y - _Bands.z), (half)(_Bands.y + _Bands.z), up + j);
                return lerp((half)_Values.z, lerp((half)_Values.y, (half)_Values.x, cap), side);
            }

            // the bark's few bold marks: dark lenses across the stem, pointed at their ends, a few to a turn round it
            // and one to a cell along it, gone past _MarkReach
            half CT_BarkMarks(float2 uv, float r, float dist)
            {
                float2 m = uv * _BarkTile.xy;                          // metres round and along
                float turn = 6.2832 * max(r, 0.01);
                float2 c = float2(m.x / turn * _Marks.x, m.y / max(_Marks.y, 0.05));
                float2 cell = floor(c);
                float2 f = frac(c) - 0.5;
                float h = OS_Hash(cell * 1.37 + 3.1);
                float2 q = f - (float2(OS_Hash(cell + 7.7), OS_Hash(cell + 1.3)) - 0.5) * float2(0.25, 0.4);
                float w = 0.18 + 0.16 * OS_Hash(cell + 5.1), hgt = 0.05 + 0.06 * OS_Hash(cell + 9.4);
                float lens = hgt * saturate(1.0 - (q.x / w) * (q.x / w));
                half mark = (half)(smoothstep(lens, lens * 0.7, abs(q.y)) * step(0.001, lens) * step(h, _Marks.z));
                mark *= (half)saturate((r - 0.03) / 0.04);
                mark *= (half)(1.0 - smoothstep(_MarkReach * 0.75, _MarkReach, dist));
                return mark * (half)_Marks.w;
            }

            void Frag(Varyings input, bool front : SV_IsFrontFace, out half4 outColor : SV_Target0)
            {
                UNITY_SETUP_INSTANCE_ID(input);
                half a = CT_Cover(input.uv0);
                // a sharpened coverage for alpha to coverage: the card's edge stays a leaf's, never a blur
                half cover = saturate((a - (half)_Cutoff) / max(fwidth(a), 1e-3h) + 0.5h);
                cover = lerp(1.0h, cover, (half)(step(0.5, _Part) * step(_Part, 1.5)));
                float3 p = input.positionWS;
                float dist = distance(p, _WorldSpaceCameraPos);

                half3 n = normalize(input.normalWS);
                int part = (int)(_Part + 0.5);
                if (part == 0 && !front)
                    n = -n;
                half seed = input.color.a;
                half hs = input.color.g;

                // what it is
                half3 albedo;
                half value = 1.0h;
                if (part == 0)
                {
                    float r = input.uv1.x, z = input.uv1.y;
                    // white limbs, dark twigs: a birch's fine shoots are a dark red-brown
                    albedo = lerp(_TwigColour.rgb, _Albedo.rgb, (half)smoothstep(_TwigR.x, _TwigR.y, r));
                    half foot = 1.0h - smoothstep(0.0h, (half)_Foot.x, (half)z);
                    albedo = lerp(albedo, _FootColour.rgb, foot * (half)_Foot.y * saturate((half)(r / 0.12)));
                    albedo = lerp(albedo, _FootColour.rgb, CT_BarkMarks(input.uv0, r, dist));
                    // contact shade where it meets the ground
                    value = 1.0h - (half)_Foot.w * (1.0h - smoothstep(0.0h, (half)_Foot.z, (half)max(z, 0.0)));
                    // the stem in two broad values: lit and turned from the sky, never a gradient's noise
                    value *= lerp(0.72h, 1.0h, smoothstep(-0.2h, 0.2h, n.y + 0.15h));
                }
                else
                {
                    // one hue to a mass (the cards' own only a touch of it), so a mass reads as one shape
                    half hue = part == 1 ? (half)frac(input.uv1.x * 0.618 + 0.17) * 0.85h + seed * 0.15h : frac(seed * 7.31h);
                    albedo = lerp(_Albedo.rgb, _Albedo2.rgb, hue);
                    value = CT_MassValue(n.y, seed);
                }
                // near trees darker (the art direction): a value push by distance, the air does the rest far off
                value *= lerp((half)_Near.z, 1.0h, (half)smoothstep(_Near.x, _Near.y, dist));
                if (_Grey > 0.5)
                    albedo = 0.42h;

                half3 colour;
            #if defined(CT_PAINTED)
                {
                    // the painted corner's light: the sky by the mass's normal (up, side, down), its three values
                    // a crown is lit by the sky all round it (its form is its values'); bark and solid by their normal
                    half up = part == 0 ? n.y : 0.5h;
                    half3 sky = lerp(lerp((half3)_P_SkyDown.rgb, (half3)_P_SkySide.rgb, smoothstep(-1.0h, 0.0h, up)),
                                     (half3)_P_SkyUp.rgb, smoothstep(0.0h, 1.0h, up));
                    // wood: the foliage's shade round it (b; its facing is the sky's own term); cards: the sky they see
                    colour = albedo * sky * value * (part == 0 ? input.color.b : lerp(0.6h, 1.0h, input.color.r));
                    // one lamp-lit side: the faces turned to the lamp within its reach
                    float3 Ld = _LampPos.xyz - p;
                    float dl = length(Ld);
                    Ld /= max(dl, 1e-3);
                    half ndl = smoothstep((half)(-_Lamp.z), (half)(-_Lamp.z + _Lamp.w), dot(n, (half3)Ld));
                    half fall = (half)pow(saturate(1.0 - dl / max(_Lamp.x, 0.1)), 2.0);
                    colour += albedo * _LampColour.rgb * (half)_Lamp.y * ndl * fall;
                    // lost upward: the crown's top in the air's own colour
                    half lost = smoothstep((half)_Lost.x, 1.0h, hs) * (half)_Lost.y * (part == 0 ? 0.5h : 1.0h);
                    colour = lerp(colour, P_Fog(normalize(p - _WorldSpaceCameraPos)), lost);
                }
            #else
                {
                    // the heart's light: the street's sky term by the mass's normal, its three values; the sun in
                    // two values on the lit side; the lamps on the side turned to them
                    // a crown is lit by the sky all round it (its form is its values'); bark and solid by their normal
                    half3 nl = part == 0 ? n : normalize(half3(n.x * 0.5h, 0.85h, n.z * 0.5h));
                    OSBake b;
                    b.sky = part == 0 ? input.color.r : lerp(0.55h, 1.0h, input.color.r);
                    b.ground = (half)(0.3 * saturate(-nl.y));
                    b.open = 1.0h;
                    b.town = OS_TownSky(p, nl);
                    half3 sky = OS_SkyTerm(b, nl);
                    half skyLum = CT_Luma(sky);
                    sky = max(skyLum + (sky - skyLum) * _OS_ShadowChroma, 0.0h);
                    colour = albedo * sky * value;
                    float4 sc = TransformWorldToShadowCoord(p);
                    Light sun = GetMainLight(sc, p, half4(1, 1, 1, 1));
                    half ndl = dot(n, sun.direction);
                    half shadow = sun.shadowAttenuation * OS_CloudLight(p, sun.direction);
                    half lit = smoothstep(0.05h, 0.25h, ndl) * shadow;
                    colour += albedo * sun.color * lit * lerp((half)_Values.w, 1.0h, value);
                #if defined(_ADDITIONAL_LIGHTS)
                    uint count = GetAdditionalLightsCount();
                    InputData inputData = (InputData)0;
                    inputData.positionWS = p;
                    inputData.normalizedScreenSpaceUV = GetNormalizedScreenSpaceUV(input.positionCS);
                    half4 shadowMask = half4(1, 1, 1, 1);
                    LIGHT_LOOP_BEGIN(count)
                        Light l = GetAdditionalLight(lightIndex, p, shadowMask);
                        half w = smoothstep((half)(-_Lamp.z), (half)(-_Lamp.z + _Lamp.w), dot(n, l.direction));
                        colour += albedo * l.color * l.distanceAttenuation * w;
                    LIGHT_LOOP_END
                #endif
                    half lost = smoothstep((half)_Lost.x, 1.0h, hs) * (half)_Lost.y * (part == 0 ? 0.5h : 1.0h);
                    half3 air = OS_Atmosphere(half3(0, 0, 0), _WorldSpaceCameraPos + normalize(p - _WorldSpaceCameraPos) * 400.0);
                    colour = lerp(colour, air, lost);
                    colour = OS_Atmosphere(colour, p);
                }
            #endif
                outColor = half4(colour, cover);
            #if defined(CT_PAINTED)
                // the painted corner's other passes: distance from the eye (for its air), the page's class, the position
                if (_P_Mode > 0.5)
                    outColor = _P_Mode < 1.5 ? float4(dist, 1.0, _Veil, 1.0)
                             : _P_Mode < 2.5 ? float4(63.0 * 4.0 / 255.0, 4.0 * 16.0 / 255.0, 0.0, 1.0)
                             : float4(p.x, p.z, p.y, normalize(input.normalWS).y);
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
                // the crown's cards cast nothing (its masses' proxies do)
                if (_Part > 0.5 && _Part < 1.5)
                    positionCS = float4(0, 0, -10, 1);
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
            Cull Off

            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_instancing

            struct Attributes
            {
                float4 positionOS : POSITION;
                float2 uv0 : TEXCOORD0;
                float2 uv2 : TEXCOORD2;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv0 : TEXCOORD0;
            };

            Varyings Vert(Attributes input)
            {
                UNITY_SETUP_INSTANCE_ID(input);
                Varyings o;
                o.positionCS = TransformWorldToHClip(CT_Position(input.positionOS.xyz, input.uv2));
                if (_Part > 2.5)
                    o.positionCS = float4(0, 0, -10, 1);
                o.uv0 = input.uv0;
                return o;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                CT_Cover(input.uv0);
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
            #pragma multi_compile_instancing

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv0 : TEXCOORD0;
                float2 uv2 : TEXCOORD2;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv0 : TEXCOORD0;
                half3 normalWS : TEXCOORD1;
            };

            Varyings Vert(Attributes input)
            {
                UNITY_SETUP_INSTANCE_ID(input);
                Varyings o;
                o.positionCS = TransformWorldToHClip(CT_Position(input.positionOS.xyz, input.uv2));
                if (_Part > 2.5)
                    o.positionCS = float4(0, 0, -10, 1);
                o.uv0 = input.uv0;
                o.normalWS = TransformObjectToWorldNormal(input.normalOS);
                return o;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                CT_Cover(input.uv0);
                return half4(NormalizeNormalPerPixel(input.normalWS), 0.0);
            }
            ENDHLSL
        }
    }
}
