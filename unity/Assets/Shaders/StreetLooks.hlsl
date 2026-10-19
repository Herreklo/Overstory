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
};

OSBake OS_ReadBake(half4 c)
{
    OSBake b;
    b.sky = c.r;
    b.ground = c.g;
    b.open = c.b;
    return b;
}

// The sky colour a face sees: the horizon for walls, the zenith for roofs.
half3 OS_SkyFor(half3 n)
{
    return lerp(_OS_HorizonAmb.rgb, _OS_SkyAmb.rgb, saturate(n.y));
}

// The shared sky term, unshaped: what reaches a face from open sky and open ground, plus a little
// for crevices. Look A uses it as is; look B shapes the split between sky and ground with its ramp.
half3 OS_SkyTerm(OSBake b, half3 n)
{
    half3 light = b.sky * OS_SkyFor(n) + b.ground * _OS_GroundAmb.rgb;
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

#endif
