// Growth in the painted corner: lichen and moss over a surface's albedo. PaintSurface.shader (ArtDirection) calls it for
// laid stone (class 3) and for every element's own surface (class 10), after the surface's own albedo and before the
// wet film and the light. The growth session owns this file: it calls the growth's painted layer
// (Shaders/GrowthPaint.hlsl, its values set as globals by the growth element, Code/Editor/Corner/LT1CornerGrowth.cs),
// so no art-direction file changes for growth.
//
//     albedo      the surface's albedo (linear), its own value from the page
//     cls         3 laid stone, 10 an element's own surface
//     uv0         the mesh's UV0 (stone: metres along and up)
//     lichen      UV4.y: the lichen's years / 200 (0 none)
//     moss        UV5.x: the moss (0 none)
//     sky         UV3.x: the sky bake (1 open sky; an own surface without a bake reads 0)
//     positionWS  the point (world); its street point is (x, z, y)
//     normalWS    the face's normal (world, towards the eye)
//     detail      how much detail this place keeps: 1 near the focus, 0 past its outer radius (_P_Focus)
//     footprint   the metres one pixel covers there
// A mesh without UV4 and UV5 reads 0 in both, and must come back unchanged.
#ifndef OS_CORNER_GROWTH_INCLUDED
#define OS_CORNER_GROWTH_INCLUDED

#include "Assets/Shaders/GrowthPaint.hlsl"

half3 CornerGrowth(half3 albedo, int cls, float2 uv0, float lichen, float moss, float sky, float3 positionWS, half3 normalWS, half detail, float footprint)
{
    return OS_PaintGrowth(albedo, uv0, lichen, moss, sky, positionWS, normalWS, detail, footprint);
}

#endif
