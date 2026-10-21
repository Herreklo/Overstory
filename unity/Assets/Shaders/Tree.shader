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
        [Toggle(_OS_MARKS)] _MarksOn ("Bark marks", Float) = 0
        _Marks ("Bark marks (g lightness, a coverage)", 2D) = "white" {}
        _MarkDark ("Marks: their darkest", Color) = (0.07, 0.065, 0.06, 1)
        _MarkLight ("Marks: their lightest (old wood)", Color) = (0.42, 0.40, 0.37, 1)
        _Relief ("Relief: x the bark's depth (m), y a mark's", Vector) = (0.006, 0.01, 0, 0)
        _Lichen ("Lichen on the bark (rgb its pigment, a how much)", Color) = (0.6, 0.63, 0.52, 0)
        [Toggle] _AlphaToMask ("Leaves: alpha to coverage (smooth edges under MSAA)", Float) = 0
        _Bark ("Bark (r lightness, g lenticels, a relief)", 2D) = "white" {}
        _BarkLight ("Bark: the white of the limbs", Color) = (0.86, 0.85, 0.82, 1)
        _BarkBand ("Bark: its grey bands and lenticels", Color) = (0.55, 0.53, 0.50, 1)
        _Twig ("Twigs", Color) = (0.20, 0.11, 0.09, 1)
        _TwigRadius ("Twig to bark: x radius all twig, y radius all bark (m)", Vector) = (0.012, 0.045, 0, 0)
        _Foot ("Foot: x trunk radius of a full foot, y its height per metre of radius, z strength, w fissures", Vector) = (0.16, 6.0, 1.0, 1.0)
        _FootPlate ("Foot: plates", Color) = (0.36, 0.35, 0.33, 1)
        _FootCrack ("Foot: fissures", Color) = (0.06, 0.055, 0.05, 1)
        _Spray ("Leaf sprays (r id, g light, b thickness, a coverage)", 2D) = "white" {}
        _Twigs ("Bare twigs on the same cards (a coverage)", 2D) = "black" {}
        _Green ("Leaves in summer", Color) = (0.26, 0.38, 0.11, 1)
        _Turned ("Leaves turned", Color) = (0.86, 0.62, 0.12, 1)
        _Late ("Leaves late", Color) = (0.50, 0.32, 0.10, 1)
        _Season ("Season: x turned (0 to 1), y fallen (0 to 1)", Vector) = (0.6, 0.25, 0, 0)
        _Through ("Light through the leaves (a strength; its colour is the light's and the leaf's)", Color) = (1, 1, 1, 0.9)
        _Cutoff ("Coverage cut", Range(0, 1)) = 0.5
        _MassShadow ("Leaves: how far out towards the sun their shadow is read (m)", Float) = 8.0
        _InnerGlow ("Leaves: the light bounced and passed inside a sunlit crown", Range(0, 2)) = 0.0
        _SunPale ("Leaves: how far the sun's light pales their colour", Range(0, 1)) = 0.35
        _Scatter ("Leaves: light passed leaf to leaf into a sunlit crown's shade", Range(0, 2)) = 0.6
        _SkyThrough ("Leaves: the sky's light through them from behind (an overcast day's glow)", Range(0, 2)) = 0.35
        _UnderFloor ("Leaves: the sky's light on a mass's underside, as a share of its top's", Range(0, 1)) = 0.5
        _MassSplit ("Leaves: where a mass turns from its lit top to its shaded underside (its normal's height)", Range(-1, 1)) = -0.05
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
        float _MassShadow;
        half _InnerGlow;
        half _SunPale;
        half _Scatter;
        half _SkyThrough;
        half _UnderFloor;
        half _MassSplit;
        half4 _MarkDark;
        half4 _MarkLight;
        float4 _Relief;
        half4 _Lichen;
    CBUFFER_END

    TEXTURE2D(_Bark);  SAMPLER(sampler_Bark);
    TEXTURE2D(_Spray); SAMPLER(sampler_Spray);
    TEXTURE2D(_Twigs); SAMPLER(sampler_Twigs);
    TEXTURE2D(_Marks); SAMPLER(sampler_Marks);

    #include "StreetSurface.hlsl"

    // The normal bent by a relief (height in metres) without tangents: Mikkelsen's surface gradient from the screen
    // derivatives of the position and the height. The bark's rings and a mark's torn lip catch the light by it.
    half3 OS_Bump(float3 positionWS, half3 n, float height)
    {
        float3 dpdx = ddx(positionWS), dpdy = ddy(positionWS);
        float dhdx = ddx(height), dhdy = ddy(height);
        float3 r1 = cross(dpdy, n), r2 = cross(n, dpdx);
        float det = dot(dpdx, r1);
        float3 grad = (det < 0 ? -1.0 : 1.0) * (dhdx * r1 + dhdy * r2);
        return normalize(abs(det) * n - grad);
    }

    // An old trunk's foot: the bark darkening downward. x how much a point is in a dark fissure, y how far the bark
    // there has greyed. Fissures run up the stem, each its own length, so the dark climbs higher in a few and the
    // white bark between them greys as it nears the ground: never a band with a top edge (a pot the tree stands in).
    // _Foot.w the fissures' strength (the silver's deep and black, the downy's only a greying). Noise anchored in the
    // world round the trunk, never the bark's tile.
    half3 OS_TreeFoot(float3 positionWS, float r, float z)
    {
        float u = positionWS.x + positionWS.z;
        half up = saturate(1.0h - (half)(z / max(_Foot.y * r, 0.05)));          // 1 at the ground, 0 at its top
        half age = saturate((half)(r / _Foot.x));
        half reach = (half)OS_Noise(float2(u * 2.3, 0.0)) * 0.6h + (half)OS_Noise(float2(u * 9.0 + 2.7, 0.0)) * 0.4h;
        half f = (half)(OS_Noise(float2(u * 16.0, positionWS.y * 2.4)) * 0.6 + OS_Noise(float2(u * 34.0 + 3.1, positionWS.y * 6.0)) * 0.4);
        // torn edges: a fine jag where the white bark ends
        f += 0.07h * ((half)OS_Noise(float2(u * 120.0, positionWS.y * 60.0)) - 0.5h);
        // the threshold falls towards the ground and with each fissure's own reach: more of the bark dark lower down,
        // never all of it
        half t = 0.95h - 0.5h * up - 0.3h * (reach - 0.5h);
        half dark = smoothstep(t - 0.02h, t + 0.02h, f) * smoothstep(0.02h, 0.12h, up);
        // broken across by bands of the white bark left (the reference's plates, never long spikes)
        half breaks = smoothstep(0.7h, 0.74h, (half)OS_Noise(float2(u * 6.0 + 9.3, positionWS.y * 11.0))) * (1.0h - up);
        dark *= 1.0h - breaks;
        // the greying begins at its own height round the stem (never a horizontal seam, a sock)
        half grey = smoothstep(0.1h, 0.9h, saturate(up + 0.35h * (reach - 0.5h) + 0.15h * (f - 0.5h)));
        half k = age * age * (half)_Foot.z;
        return half3(dark * k * (half)_Foot.w, grey * k, 0.0h);
    }

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

    // Cut at the coverage threshold (depth): returns the atlas sample.
    half4 OS_LeafClip(float2 uv, float2 card)
    {
        half4 m = SAMPLE_TEXTURE2D(_Spray, sampler_Spray, uv);
        clip(max(OS_LeafCover(m, card), OS_TwigCover(uv, card)) - _Cutoff);
        return m;
    }

    // Cut for the sun's shadow: an open crown's coverage, averaged over a shadow texel, falls mostly under any fixed
    // cut, so an autumn crown would cast a bare winter skeleton. Each shadow texel is kept with the chance of the
    // leaves' coverage there (read at a fixed level, 128 texels a card), so the shadow filter softens it into the
    // dappled tone a half-open crown casts
    void OS_LeafClipShadow(float2 uv, float2 card, float2 pixel)
    {
        half4 m = SAMPLE_TEXTURE2D_LOD(_Spray, sampler_Spray, uv, 2);
        half bare = smoothstep((half)card.y, (half)card.y + 0.18h, (half)_Season.y);
        half twig = SAMPLE_TEXTURE2D_LOD(_Twigs, sampler_Twigs, uv, 2).a * bare;
        clip(max(OS_LeafCover(m, card), twig) - (0.08h + 0.84h * (half)OS_Hash(pixel)));
    }

    StreetSurface OS_TreeSurface(float2 uv, float2 extra, half3 normalWS, float3 positionWS)
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
        half3 bark = lerp(_BarkBand.rgb, _BarkLight.rgb, saturate((b.r - 0.62h) / 0.3h));
        // lichen where it grows (its pigment and how much the species carries): patches of several sizes, broader
        // round the stem than along it, from noise anchored round the trunk (never the bark's tile, which repeats)
        {
            float lu = positionWS.x + positionWS.z;
            half ln = (half)(OS_Noise(float2(lu * 4.0, positionWS.y * 2.6)) * 0.55 + OS_Noise(float2(lu * 11.0 + 1.7, positionWS.y * 7.0)) * 0.3
                          + OS_Noise(float2(lu * 29.0 + 4.1, positionWS.y * 19.0)) * 0.15);
            half lichen = smoothstep(0.53h, 0.6h, ln) * saturate((half)((r - 0.02) / 0.05));
            bark = lerp(bark, _Lichen.rgb, lichen * _Lichen.a);
        }
        bark = lerp(bark, _BarkBand.rgb * 0.2h, b.g * 0.9h);
        half twig = 1.0h - smoothstep((half)_TwigRadius.x, (half)_TwigRadius.y, (half)r);
        half3 c = lerp(bark, _Twig.rgb, twig);
        // an old trunk's foot: dark, higher on a thicker trunk, its top edge ragged, a few lighter islands in it
        half3 foot = OS_TreeFoot(positionWS, r, z);
        // the bark greying towards the ground, and the fissured plates dark in it, rough within
        c = lerp(c, _FootPlate.rgb, foot.y);
        // two values in the dark plates: rough, lighter where a plate's face catches the light
        half rough = (half)OS_Noise(float2((positionWS.x + positionWS.z) * 30.0, positionWS.y * 12.0));
        c = lerp(c, _FootCrack.rgb * (0.75h + 0.6h * smoothstep(0.45h, 0.6h, rough)), foot.x);
        // a cut face: pale fresh wood weathering to grey over the years, the rings faintly, the callus rolling in
        // from the bark round its edge
        if (uv.x < -0.5)
        {
            half out_ = saturate((half)uv.x + 2.0h);
            half years = saturate((half)uv.y * 50.0h / 12.0h);
            half3 wood = lerp(half3(0.80h, 0.68h, 0.50h), half3(0.46h, 0.43h, 0.40h), years);
            wood *= 0.94h + 0.06h * sin(out_ * 40.0h);
            half callus = smoothstep(0.72h, 0.95h, out_) * saturate((half)uv.y * 50.0h / 4.0h);
            c = lerp(wood, _BarkBand.rgb * 0.8h, callus);
        }
        s.albedo = c;
    #if defined(_OS_MARKS)
        // a mark of the tree's history (a chevron over a branch, a shed branch's scar): its own pigment, lit as the
        // bark it lies on
        half4 mk = SAMPLE_TEXTURE2D(_Marks, sampler_Marks, uv);
        // the dark under the torn bark, and the torn lip, the bark's own white
        s.albedo = lerp(_MarkDark.rgb, _BarkLight.rgb * 1.04h, mk.g);
    #endif
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
            #pragma shader_feature_local _OS_MARKS
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
                float2 uv2 : TEXCOORD2;          // a bark mark's weathering (x)
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
                float2 uv2 : TEXCOORD6;
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
            #if !defined(_OS_LEAVES) && !defined(_OS_MARKS)
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
                o.uv2 = input.uv2;
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
            #if defined(_OS_MARKS)
                clip(SAMPLE_TEXTURE2D(_Marks, sampler_Marks, input.uv).a - 0.5h);
                // a mark on an old trunk's dark foot is lost in it
                half3 footM = OS_TreeFoot(input.positionWS, input.extra.x, input.extra.y);
                clip(0.4h - footM.x);
                clip(0.25h - footM.y);
                // and one round the wood's edge as seen is never drawn past its outline (a shard in the air)
                clip(abs(dot(normalize(input.normalWS), GetWorldSpaceNormalizeViewDir(input.positionWS))) - 0.3h);
            #endif
                // a twig deep in the foliage shows from the season its leaves fall (bake alpha; 0 always shown)
                if (input.bake.a > 0.001h)
                    clip((half)_Season.y - input.bake.a - 0.04h * OS_Hash(input.positionCS.xy));
                half3 n = normalize(front ? input.normalWS : -input.normalWS);
                // nothing is flat: the bark's relief (its rings, its grain, the lenticels sunk in, an old foot's
                // plates and fissures) and a mark's torn lip bend the light
            #if defined(_OS_MARKS)
                n = OS_Bump(input.positionWS, n, SAMPLE_TEXTURE2D(_Marks, sampler_Marks, input.uv).b * _Relief.y);
            #else
                if (input.extra.x > _TwigRadius.y)
                {
                    half4 bk = SAMPLE_TEXTURE2D(_Bark, sampler_Bark, input.uv);
                    // the dark foot is rough: deeper relief, its islands (the white bark left) raised as plates
                    half3 foot = OS_TreeFoot(input.positionWS, input.extra.x, input.extra.y);
                    // the relief belongs to wide wood seen face on, its depth with the wood's width: on a limb the
                    // bark's rings at their real spacing are ridges as big as the limb (a corrugated hose, a
                    // herringbone), and at the outline a bump steps it
                    half wide = saturate((half)(input.extra.x / 0.25));
                    half face = smoothstep(0.15h, 0.45h, abs(dot(n, GetWorldSpaceNormalizeViewDir(input.positionWS))));
                    half roughH = (half)OS_Noise(float2((input.positionWS.x + input.positionWS.z) * 30.0, input.positionWS.y * 12.0));
                    half h = bk.a * (1.0h + foot.y) - foot.x * (1.0h - 0.9h * roughH);
                    n = OS_Bump(input.positionWS, n, h * _Relief.x * wide * face);
                }
            #endif
            #endif
                StreetSurface s = OS_TreeSurface(input.uv, input.extra, n, input.positionWS);
            #if defined(_OS_MARKS)
                // an old mark greys towards the bark as it weathers; a fresh one is dark
                // an old mark weathers to a step below the bark (never paler: a pale lens reads as an eye)
                s.albedo = lerp(s.albedo, _BarkBand.rgb * 0.8h, (half)input.uv2.x);
            #endif

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
                // what a card sees of the sky, flattened to two values: a mass's skin open, its core one darker
                // interior (Oga's dark inner mass behind the lit ones, never a hollow)
                b.sky = lerp(0.58h, 1.0h, smoothstep(0.42h, 0.56h, b.sky));
            #endif

            #if defined(_OS_LEAVES)
                // leaves lit as a painter lights foliage: from the mass's plane, two families (the sun's and the sky's)
                // with a narrow half-tone where the plane turns from the light, a warm band at the turn, no brush noise;
                // the sun's shadow only from what stands outside the mass (read three metres towards the light)
                half3 colour;
                // where the card sits on its mass: its top (1) or its underside (0), with a narrow soft edge between
                half top = smoothstep(_MassSplit - 0.06h, _MassSplit + 0.06h, n.y);
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
                    // the sky term, shade in the sky's colour, by the same rule as every surface in the town: how much
                    // of the sky's tint shade takes is the light's (the rig's), never the object's (SEASON's lesson:
                    // per-object shadow tints break whenever the light changes)
                    half3 sky = OS_SkyTerm(b, n);
                    half skyLum = dot(sky, half3(0.2126h, 0.7152h, 0.0722h));
                    sky = max(skyLum + (sky - skyLum) * _OS_ShadowChroma, 0.0h);
                    // a mass's top takes the sky, its underside is in its own shade: two flat values with a narrow soft
                    // edge between (Firewatch's two values a form), decided by where the card sits on its mass, never
                    // leaf by leaf
                    sky *= lerp(_UnderFloor, 1.1h, top);
                    // the sky's light by what the card sees of the sky through the crown (baked); the sun's by its own
                    // shadow, a little dimmed deep inside
                    half seen = saturate(b.sky);
                    // in the sun a leaf's colour is lifted towards the light's, not deepened: highlights go paler,
                    // never cadmium (a painter's lit foliage)
                    half3 litAlbedo = lerp(s.albedo, dot(s.albedo, half3(0.2126h, 0.7152h, 0.0722h)).xxx, _SunPale);
                    // and lit from within: in a sunlit crown light passes leaf to leaf, so the shade side of a mass
                    // glows with the leaves' own colour times the sun's (only while the crown has sun)
                    half3 scatter = s.albedo * s.albedo * sun.color * _Scatter * shadow * (1.0h - saturate(lit));
                    colour = s.albedo * sky + scatter + litAlbedo * sun.color * lit * lerp(0.75h, 1.0h, seen);
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
                // light through a leaf takes its colour twice, as through stained glass: deeper, clearer, never greyer
                half lumLeaf = max(dot(s.albedo, half3(0.2126h, 0.7152h, 0.0722h)), 1e-3h);
                half3 glass = lerp(s.albedo, s.albedo * s.albedo / lumLeaf, 0.25h);
                colour += glass * _Through.rgb * main.color * through * m.b * _Through.a * isLeaf;
                // and the sky's own light through a thin leaf, from the side it does not face: on a grey day the whole
                // crown is lit from behind by the bright sky, which is why a yellow birch glows in the rain
                half3 behind = OS_SkyFor(-id.viewDirectionWS);          // the sky beyond the leaf, seen through it
                // strongest through a mass's lit skin, weaker under it, so the glow never flattens the mass's two values
                colour += glass * behind * b.sky * b.town * m.b * _SkyThrough * lerp(0.4h, 1.0h, top) * isLeaf;
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
            #pragma shader_feature_local _OS_MARKS
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
                OS_LeafClipShadow(input.uv, input.extra, input.positionCS.xy);
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
            #pragma shader_feature_local _OS_MARKS
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
            #if defined(_OS_MARKS)
                // a mark's strip is cut to its shape here too, or its whole rectangle hides the bark behind it
                clip(SAMPLE_TEXTURE2D(_Marks, sampler_Marks, input.uv).a - 0.5h);
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
            #pragma shader_feature_local _OS_MARKS
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
            #if defined(_OS_MARKS)
                clip(SAMPLE_TEXTURE2D(_Marks, sampler_Marks, input.uv).a - 0.5h);
            #endif
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
