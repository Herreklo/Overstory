#ifndef OVERSTORY_STREET_LOOKS_INCLUDED
#define OVERSTORY_STREET_LOOKS_INCLUDED

// How each look lights the shared surface (StreetSurface.hlsl). Everything a look may not change is
// here too and shared: the sky term (a hemisphere light from the rig's sky, horizon and ground
// colours, weighted by what each face sees, baked into the parts), screen-space occlusion, glossy
// reflections with screen-space reflections, emission and the air. A look changes only how light
// turns into colour. (docs/research/colour-and-shading.md, "The first look test".)

// the light rig's hemisphere light (linear, intensity included)
float4 _OS_SkyAmb;      // what the open sky gives a face that looks straight up
float4 _OS_HorizonAmb;  // what it gives a face that looks at the horizon
float4 _OS_GroundAmb;   // what the ground bounces back up
float4 _OS_SunSideAmb;  // what the horizon on the sun's side gives a wall facing it (a 0: the same all round)
float4 _OS_TownBounce;  // what the town's walls and ground give back, in place of the sky they hide
float4 _OS_SunBounce;   // the sun's light bounced up from lit ground (linear), for faces that see the ground

// The town's sky map (Overstory.Scenes.SkyMap) is declared with the air, in StreetSurface.hlsl

// How much of a face's open sky the town leaves open, 0 to 1: the horizon the town makes round it, found in eight
// directions out to about 60 m, each weighted by how much the face looks that way. A lane's floor at the foot of
// two walls keeps a strip of sky; a wall's foot in a yard keeps less; a roof or the open quay keeps it all.
half OS_TownSky(float3 positionWS, half3 n)
{
    if (_OS_SkyMapOn < 0.5)
        return 1.0h;
    float3 o = positionWS + n * 0.6; // off the face, so a wall does not hide itself
    float2 uv = (o.xz - _OS_SkyMapRect.xy) * _OS_SkyMapRect.z;
    if (any(uv < 0.0) || any(uv > 1.0))
        return 1.0h;
    half up = abs(n.y);
    float2 nh = n.xz / max(length(n.xz), 1e-4);
    const float reach[8] = { 1.0, 2.0, 3.5, 6.0, 10.0, 17.0, 30.0, 56.0 };
    half open = 0.0h, full = 0.0h;
    [unroll]
    for (int k = 0; k < 8; k++)
    {
        float a = (k + 0.5) * 0.785398;
        float2 dir = float2(cos(a), sin(a));
        half w = saturate(up + (1.0h - up) * dot(dir, nh));
        float tanMax = 0.0;
        [unroll]
        for (int j = 0; j < 8; j++)
        {
            float2 q = uv + dir * reach[j] * _OS_SkyMapRect.z;
            q.y = _OS_SkyMapRect.w > 0.5 ? 1.0 - q.y : q.y;
            float h = SAMPLE_TEXTURE2D_LOD(_OS_SkyMap, sampler_OS_SkyMap, q, 0).r;
            tanMax = max(tanMax, (h - o.y - 0.2) / reach[j]);
        }
        float alpha = atan(tanMax);
        // the sky left over the town's horizon: cos^2 for a face looking up, the vertical case for a wall
        half flat = (half)(cos(alpha) * cos(alpha));
        half wall = (half)(1.0 - (2.0 * alpha + sin(2.0 * alpha)) / PI);
        open += w * lerp(wall, flat, up);
        full += w;
    }
    return full > 1e-3 ? open / full : 1.0h;
}

float _OS_ShadowChroma; // look D: how strongly shade takes the sky's colour (1 as the light gives it)

// How much sun reaches a point through the clouds: 1 in a break, low under a cloud.
half OS_CloudLight(float3 positionWS, half3 toSun)
{
    if (_OS_Clouds.x <= 0.001)
        return 1.0h;
    // follow the sun's ray up to the cloud layer
    float up = max(toSun.y, 0.05);
    float2 p = positionWS.xz + toSun.xz * ((_OS_Clouds.w - positionWS.y) / up);
    return lerp(1.0h, 0.12h, OS_CloudCover(OS_CloudField(p, 0.0), 0.0));
}

// look B, the painted ramp
float4 _OS_Ramp;        // x edge, y softness, z shadow floor, w stroke (how far the world-fixed stroke nudges the ramp)
float4 _OS_EdgeTint;    // rgb extra colour at the shadow edge, a its strength
float4 _OS_Rim;         // rgb rim colour (from the sky), a strength

// The bake: r sky, g ground, b openness. Generated ground carries its own (open sky).
struct OSBake
{
    half sky;
    half ground;
    half open;
    half town;  // the share of that sky the town round it leaves open (OS_TownSky), 1 for the part alone
};

OSBake OS_ReadBake(half4 c)
{
    OSBake b;
    b.sky = c.r;
    b.ground = c.g;
    b.open = c.b;
    b.town = 1.0h;
    return b;
}

// The sky colour a face sees: the zenith for roofs; for walls the horizon, warm on the sun's side and cool away.
half3 OS_SkyFor(half3 n)
{
    half3 horizon = _OS_HorizonAmb.rgb;
    float2 h = n.xz;
    float hl = length(h);
    if (_OS_SunSideAmb.a > 0.5 && hl > 1e-3)
    {
        float2 sun = _OS_SunDir.xz / max(length(_OS_SunDir.xz), 1e-4);
        half toward = (half)(dot(h / hl, sun) * 0.5 + 0.5);
        horizon = lerp(_OS_HorizonAmb.rgb, _OS_SunSideAmb.rgb, toward * toward);
    }
    return lerp(horizon, _OS_SkyAmb.rgb, saturate(n.y));
}

// The shared sky term, unshaped: what reaches a face from the sky the town leaves open, from the town itself where it
// hides the sky, and from open ground, plus a little for crevices. Look A uses it as is; look B shapes the split
// between sky and ground with its ramp.
half3 OS_SkyTerm(OSBake b, half3 n)
{
    half3 light = b.sky * (b.town * OS_SkyFor(n) + (1.0h - b.town) * _OS_TownBounce.rgb) + b.ground * (_OS_GroundAmb.rgb + _OS_SunBounce.rgb);
    return light * lerp(0.55h, 1.0h, b.open);
}

// -- look A: plain URP Lit, fed the shared sky term --------------------------------------------------

half3 OS_ShadeA(InputData id, StreetSurface s, OSBake b)
{
    SurfaceData sd = (SurfaceData)0;
    sd.albedo = s.albedo;
    sd.metallic = s.metallic;
    sd.smoothness = s.smoothness;
    sd.normalTS = half3(0, 0, 1);
    sd.occlusion = 1;
    sd.emission = s.emission;
    sd.alpha = 1;
    id.bakedGI = OS_SkyTerm(b, id.normalWS);
    return UniversalFragmentPBR(id, sd).rgb;
}

// -- look B: the painted ramp ------------------------------------------------------------------------

// One global ramp: a soft step from the shadow floor to full light, the edge broken by a stroke.
half OS_Ramp(half x)
{
    return lerp(_OS_Ramp.z, 1.0h, smoothstep(_OS_Ramp.x - _OS_Ramp.y, _OS_Ramp.x + _OS_Ramp.y, x));
}

// A little extra colour where light turns to shadow, as painters put a warmer, stronger line there.
half OS_EdgeBand(half x)
{
    half d = abs(x - _OS_Ramp.x) / max(_OS_Ramp.y * 1.6h, 1e-3h);
    return saturate(1.0h - d * d);
}

// A stroke fixed to the world, never to the screen, so it never swims: value noise on the plane the
// face mostly lies in, stretched along it like a brush.
half OS_Stroke(float3 p, half3 n)
{
    half3 a = abs(n);
    float2 q = a.y > max(a.x, a.z) ? p.xz : (a.x > a.z ? p.zy : p.xy);
    return (half)(OS_Noise(q * float2(1.6, 5.0)) * 0.65 + OS_Noise(q * float2(4.1, 11.0) + 7.3) * 0.35) - 0.5h;
}

half3 OS_ShadeB(InputData id, StreetSurface s, OSBake b, float3 positionWS)
{
    InputData inputData = id; // URP's Forward+ light loop looks lights up through a variable of this name
    half3 n = id.normalWS;
    half3 v = id.viewDirectionWS;
    half stroke = OS_Stroke(positionWS, n) * _OS_Ramp.w;
    AmbientOcclusionFactor ao = CreateAmbientOcclusionFactor(id.normalizedScreenSpaceUV, 1.0h);
    half4 shadowMask = half4(1, 1, 1, 1);

    // the sky term, shaped by the same ramp: how much of what a face sees is sky rather than ground
    half seen = max(b.sky + b.ground, 1e-3h);
    half skyShare = OS_Ramp(b.sky / seen + stroke);
    half3 skyLight = lerp(_OS_GroundAmb.rgb, OS_SkyFor(n), skyShare) * seen * lerp(0.55h, 1.0h, b.open);
    half3 colour = s.albedo * skyLight * ao.indirectAmbientOcclusion;

    // the sun (or the brightest sky at dusk): half-Lambert through the ramp, times the light's colour
    Light main = GetMainLight(id.shadowCoord, id.positionWS, shadowMask);
    main.shadowAttenuation *= OS_CloudLight(positionWS, main.direction);
    half lit = (dot(n, main.direction) * 0.5h + 0.5h) * lerp(0.5h, 1.0h, main.shadowAttenuation) + stroke;
    lit = lit * lerp(0.35h, 1.0h, main.shadowAttenuation); // a cast shadow always reads as shadow
    half r = OS_Ramp(lit);
    colour += s.albedo * main.color * r * ao.directAmbientOcclusion;
    colour += main.color * _OS_EdgeTint.rgb * _OS_EdgeTint.a * OS_EdgeBand(lit) * s.albedo;

    // lamps and other lights: the same soft step on N.L, their falloff left smooth so light pools
    half3 specular = 0;
    #if defined(_ADDITIONAL_LIGHTS)
    uint count = GetAdditionalLightsCount();
    #if USE_CLUSTER_LIGHT_LOOP
    [loop] for (uint lightIndex = 0; lightIndex < min(URP_FP_DIRECTIONAL_LIGHTS_COUNT, MAX_VISIBLE_LIGHTS); lightIndex++)
    {
        CLUSTER_LIGHT_LOOP_SUBTRACTIVE_LIGHT_CHECK
        Light l = GetAdditionalLight(lightIndex, id.positionWS, shadowMask);
        half x = saturate(dot(n, l.direction)) * l.shadowAttenuation;
        colour += s.albedo * l.color * l.distanceAttenuation * smoothstep(0.0h, 0.3h, x + stroke * 0.5h);
    }
    #endif
    LIGHT_LOOP_BEGIN(count)
        Light l = GetAdditionalLight(lightIndex, id.positionWS, shadowMask);
        half x = saturate(dot(n, l.direction)) * l.shadowAttenuation;
        half3 radiance = l.color * l.distanceAttenuation;
        colour += s.albedo * radiance * smoothstep(0.0h, 0.3h, x + stroke * 0.5h);
        // a lamp's highlight on wet stone and glass: the blue hour's signature
        half3 h = normalize(l.direction + v);
        half power = exp2(3.0h + 8.0h * s.smoothness);
        specular += radiance * pow(saturate(dot(n, h)), power) * s.smoothness * s.smoothness * s.smoothness * step(0.0h, x - 1e-3h);
    LIGHT_LOOP_END
    #endif

    // reflections (with screen-space reflections) where the surface is smooth: wet stone, glass, water
    half perceptualRoughness = 1.0h - s.smoothness;
    half3 reflection = GlossyEnvironmentReflection(reflect(-v, n), id.positionWS, perceptualRoughness, ao.indirectAmbientOcclusion, id.normalizedScreenSpaceUV);
    half fresnel = 0.04h + 0.96h * pow(1.0h - saturate(dot(n, v)), 5.0h);
    colour += reflection * fresnel * s.smoothness * s.smoothness + specular;

    // rim light only, no lines: a thin lift of sky colour on the silhouette's lit side
    half rim = pow(1.0h - saturate(dot(n, v)), 4.0h) * saturate(n.y * 0.5h + 0.6h);
    colour += _OS_Rim.rgb * _OS_Rim.a * rim * s.albedo;

    return colour + s.emission;
}


// -- look D: the woodblock print ---------------------------------------------------------------------
// Light is cut into a few flat ink plates in the light's own colour (each plate one exposure step),
// their edges broken by a carving fixed to the world; the darkest plate is opened up by white-line
// carving that follows the land and the courses of the walls, wider where more light falls. The key
// block's lines are drawn after, in a full-screen pass (KeyBlock.shader). Everything is driven by light
// or fixed to the world: nothing swims, nothing is painted per object.

float4 _OS_Plates;   // x stops per plate, y carving amount (stops), z white-line spacing (m), w white-line strength

// A gouge pattern fixed to the world: stretched along the surface, like the grain a carver follows.
half OS_Carve(float3 p, half3 n)
{
    half3 a = abs(n);
    float2 q = a.y > max(a.x, a.z) ? p.xz : (a.x > a.z ? p.zy : p.xy);
    float2 g = a.y > max(a.x, a.z) ? q * float2(0.25, 0.8) : q * float2(0.35, 1.6);
    return (half)(OS_Noise(g) * 0.75 + OS_Noise(g * 2.3 + 3.1) * 0.25) - 0.5h;
}

half3 OS_ShadeD(InputData id, StreetSurface s, OSBake b, float3 positionWS)
{
    InputData inputData = id; // URP's Forward+ light loop looks lights up through a variable of this name
    half3 n = id.normalWS;
    half3 v = id.viewDirectionWS;
    AmbientOcclusionFactor ao = CreateAmbientOcclusionFactor(id.normalizedScreenSpaceUV, 1.0h);
    half4 shadowMask = half4(1, 1, 1, 1);

    // all the light a point receives, unshaped: sky term, sun, lamps
    // shade takes the sky's colour, pushed: violet, teal and deep blue, never grey
    half3 sky = OS_SkyTerm(b, n) * ao.indirectAmbientOcclusion;
    half skyLum = dot(sky, half3(0.2126h, 0.7152h, 0.0722h));
    half3 light = max(skyLum + (sky - skyLum) * _OS_ShadowChroma, 0.0h);
    Light main = GetMainLight(id.shadowCoord, id.positionWS, shadowMask);
    light += main.color * saturate(dot(n, main.direction)) * main.shadowAttenuation * OS_CloudLight(positionWS, main.direction);
    half3 specular = 0;
    #if defined(_ADDITIONAL_LIGHTS)
    uint count = GetAdditionalLightsCount();
    #if USE_CLUSTER_LIGHT_LOOP
    [loop] for (uint lightIndex = 0; lightIndex < min(URP_FP_DIRECTIONAL_LIGHTS_COUNT, MAX_VISIBLE_LIGHTS); lightIndex++)
    {
        CLUSTER_LIGHT_LOOP_SUBTRACTIVE_LIGHT_CHECK
        Light l = GetAdditionalLight(lightIndex, id.positionWS, shadowMask);
        light += l.color * l.distanceAttenuation * saturate(dot(n, l.direction)) * l.shadowAttenuation;
    }
    #endif
    LIGHT_LOOP_BEGIN(count)
        Light l = GetAdditionalLight(lightIndex, id.positionWS, shadowMask);
        half3 radiance = l.color * l.distanceAttenuation * l.shadowAttenuation;
        light += radiance * saturate(dot(n, l.direction));
        half3 h = normalize(l.direction + v);
        specular += radiance * pow(saturate(dot(n, h)), exp2(3.0h + 8.0h * s.smoothness)) * s.smoothness * s.smoothness * s.smoothness;
    LIGHT_LOOP_END
    #endif
    half3 reflection = GlossyEnvironmentReflection(reflect(-v, n), id.positionWS, 1.0h - s.smoothness, ao.indirectAmbientOcclusion, id.normalizedScreenSpaceUV);
    half fresnel = 0.04h + 0.96h * pow(1.0h - saturate(dot(n, v)), 5.0h);
    half3 colour = s.albedo * light + reflection * fresnel * s.smoothness * s.smoothness + specular;

    // the ink plates: cut the light into exposure steps, hue kept, edges carved
    half lum = max(dot(colour, half3(0.2126h, 0.7152h, 0.0722h)), 1e-5h);
    half carve = OS_Carve(positionWS, n) * _OS_Plates.y;
    float e = log2(lum) / _OS_Plates.x + carve;
    float plate = floor(e);
    float within = e - plate;                      // where the point lies inside its plate, 0..1
    float aa = max(fwidth(e) * 0.75, 1e-3);
    float stepped = plate + smoothstep(1.0 - aa, 1.0, within); // a hard cut, antialiased at the edge
    half plated = exp2(stepped * _OS_Plates.x + _OS_Plates.x * 0.5h);
    half3 ink = colour * (plated / lum);

    // white-line carving in the darks: lines that follow height (contours on the land, courses on the
    // walls), wider where more light falls inside the plate, opening the dark to the next plate's colour
    float spacing = _OS_Plates.z * exp2(round(log2(max(1.0, fwidth(positionWS.y) * 22.0 / _OS_Plates.z))));
    float t = positionWS.y / spacing + carve * 2.0;
    float distToLine = abs(frac(t) - 0.5) * 2.0;   // 0 on the line's centre, 1 between lines
    float width = saturate(within) * 0.3;
    float lineAA = fwidth(t) * 2.0;
    half cut = (1.0h - smoothstep(width - lineAA, width + lineAA, 1.0 - distToLine)) * step(0.01, width);
    half darkest = 1.0h - smoothstep(0.0h, 0.12h, plated / max(dot(_OS_SkyAmb.rgb, half3(0.2126h, 0.7152h, 0.0722h)), 1e-4h) - 0.25h);
    half3 paper = s.albedo * OS_SkyFor(n) * 0.9h + OS_SkyFor(n) * 0.15h;
    ink = lerp(ink, max(ink * exp2(_OS_Plates.x * 2.0h), paper), cut * darkest * _OS_Plates.w);

    return ink + s.emission;
}


// -- look P: painterly realism ------------------------------------------------------------------------
// Stålenhag, Hopper, Hammershøi, Disco Elysium: a real place painted by someone who leaves out what
// doesn't matter. Light wraps softly round forms; shade takes the sky's colour; a gentle warm-to-cool
// turn where light becomes shade gives form without lines; the base colours are muted so the light
// carries the colour; grime gathers where a surface sees the ground; and a brush texture fixed to the
// world breaks colour and light a little, as brushwork does. No outlines, no plates.

float4 _OS_Paint;      // x wrap (how far light wraps round a form), y muting (0 none, 1 grey), z grime, w brush strength
float4 _OS_Grime;      // rgb the colour dirt and damp lend a wall near the ground (linear)

// Brushwork fixed to the world: in each patch, strokes in one seeded direction, so a wall reads as
// laid-in paint, not noise. Returns -0.5..0.5.
half OS_Brush(float3 p, half3 n)
{
    half3 a = abs(n);
    float2 q = a.y > max(a.x, a.z) ? p.xz : (a.x > a.z ? p.zy : p.xy);
    q *= 1.4; // strokes about 70 cm long close by
    float2 cell = floor(q);
    float ang = OS_Hash(cell) * 3.14159;
    float2 dir = float2(cos(ang), sin(ang));
    float2 local = float2(dot(q, dir), dot(q, float2(-dir.y, dir.x)));
    float s = OS_Noise(local * float2(1.2, 7.0) + cell * 3.7);           // long strokes across the patch
    float t = OS_Noise(q * 0.35 + 11.0);                                 // patches of a slightly different mix
    return (half)(s * 0.65 + t * 0.35) - 0.5h;
}

half3 OS_ShadeP(InputData id, StreetSurface s, OSBake b, float3 positionWS)
{
    InputData inputData = id; // URP's Forward+ light loop looks lights up through a variable of this name
    half3 n = id.normalWS;
    half3 v = id.viewDirectionWS;
    AmbientOcclusionFactor ao = CreateAmbientOcclusionFactor(id.normalizedScreenSpaceUV, 1.0h);
    half4 shadowMask = half4(1, 1, 1, 1);
    half brush = OS_Brush(positionWS, n) * _OS_Paint.w;

    // the base: muted so light carries the colour, broken a little by the brush, darker and damper
    // where a surface looks at the ground
    half3 albedo = s.albedo;
    half lumA = dot(albedo, half3(0.2126h, 0.7152h, 0.0722h));
    albedo = lerp(albedo, lumA.xxx, _OS_Paint.y);
    albedo *= 1.0h + brush * 0.35h;
    half grime = saturate((b.ground - 0.25h) * 2.2h) * _OS_Paint.z;
    albedo = lerp(albedo, albedo * _OS_Grime.rgb * 2.0h, grime);

    // the sky term, shade in the sky's colour
    half3 sky = OS_SkyTerm(b, n) * ao.indirectAmbientOcclusion;
    half skyLum = dot(sky, half3(0.2126h, 0.7152h, 0.0722h));
    sky = max(skyLum + (sky - skyLum) * _OS_ShadowChroma, 0.0h);
    half3 colour = albedo * sky;

    // the sun: wrapped softly, through the clouds; a warm band where it turns to shade
    Light main = GetMainLight(id.shadowCoord, id.positionWS, shadowMask);
    half w = _OS_Paint.x;
    half ndl = dot(n, main.direction);
    half wrapped = saturate((ndl + w) / (1.0h + w) + brush * 0.12h);
    half shadow = main.shadowAttenuation * OS_CloudLight(positionWS, main.direction);
    half lit = wrapped * wrapped * shadow;
    // the edge between light and shade: where the form turns from the light, the light itself goes warmer (a
    // painter's warm turn), never colour added on top of it, which on every round surface (a trunk, a lamp post)
    // makes a saturated stripe brighter than the light itself
    half turn = saturate(1.0h - abs(ndl) * 4.0h) * shadow;
    half3 warm = _OS_EdgeTint.rgb / max(dot(_OS_EdgeTint.rgb, half3(0.2126h, 0.7152h, 0.0722h)), 1e-3h);
    // (the style's strength was set when the turn was colour added on top: as a shift of the light, half of it)
    colour += albedo * main.color * lerp(half3(1, 1, 1), warm, 0.5h * _OS_EdgeTint.a * turn) * lit * ao.directAmbientOcclusion;

    // lamps and lit rooms: soft pools, and their glints in wet stone
    half3 specular = 0;
    #if defined(_ADDITIONAL_LIGHTS)
    uint count = GetAdditionalLightsCount();
    #if USE_CLUSTER_LIGHT_LOOP
    [loop] for (uint lightIndex = 0; lightIndex < min(URP_FP_DIRECTIONAL_LIGHTS_COUNT, MAX_VISIBLE_LIGHTS); lightIndex++)
    {
        CLUSTER_LIGHT_LOOP_SUBTRACTIVE_LIGHT_CHECK
        Light l = GetAdditionalLight(lightIndex, id.positionWS, shadowMask);
        colour += albedo * l.color * l.distanceAttenuation * l.shadowAttenuation * saturate((dot(n, l.direction) + w) / (1.0h + w));
    }
    #endif
    LIGHT_LOOP_BEGIN(count)
        Light l = GetAdditionalLight(lightIndex, id.positionWS, shadowMask);
        half3 radiance = l.color * l.distanceAttenuation * l.shadowAttenuation;
        colour += albedo * radiance * saturate((dot(n, l.direction) + w) / (1.0h + w));
        half3 h = normalize(l.direction + v);
        specular += radiance * pow(saturate(dot(n, h)), exp2(3.0h + 8.0h * s.smoothness)) * s.smoothness * s.smoothness * s.smoothness;
    LIGHT_LOOP_END
    #endif

    // reflections where it is wet or glazed, softened like paint
    half3 reflection = GlossyEnvironmentReflection(reflect(-v, n), id.positionWS, 1.0h - s.smoothness, ao.indirectAmbientOcclusion, id.normalizedScreenSpaceUV);
    half fresnel = 0.04h + 0.96h * pow(1.0h - saturate(dot(n, v)), 5.0h);
    colour += reflection * fresnel * s.smoothness * s.smoothness * 0.85h + specular;

    return colour + s.emission;
}

#endif
