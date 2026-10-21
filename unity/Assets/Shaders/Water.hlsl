#ifndef OVERSTORY_WATER_INCLUDED
#define OVERSTORY_WATER_INCLUDED

// Water on surfaces (docs/foundations.md, The shared surface layers: the water layer): one system for every surface
// in the town. Where water lies and runs is each surface's own, baked by its generator from its shape and gravity
// (blender/generators/water.py): rain lands on what faces up, runs to the low edges and joints, drips off copings and
// nosings and streaks down the faces below, gathers in hollows, joints and at every foot, and dries from the crowns
// first. How a material answers it is the material's own, its water profile: dense slate sheds water, glazes and dries
// fast; porous rubble darkens unevenly and dries slower; cement soaks it, stays dark and stains; soil and moss hold it
// longest (the shared materials' profiles are the setting pack's, Overstory.World.WaterPack). The weather is the
// rig's: _OS_Wetness, 0 dry, 1 raining, between them the hours after rain.
//
// A water profile, half4: x how much the material darkens wet (its porosity), y how glossy its wet film gets (0 matt,
// 1 a glaze where it is smooth), z how long it holds water after rain (0 dries at once, 1 stays wet), w how readily
// water running over it leaves a stain.
//
// Include after StreetSurface.hlsl (OS_Noise, _OS_Wetness).

half4 _OS_WaterCement;
half4 _OS_WaterSoil;
half4 _OS_WaterGrowth;      // moss and lichen: they soak it up and stay matt

// How wet a point is now: in rain everything is damp and the runoff paths most; as it dries, only where water lingers
// stays wet, and a material that holds water stays wet longer. water: how much water lies or runs here (the bake).
half OS_WetNow(half water, half up, half holds)
{
    half dries = 0.55h * (1.0h - water) * (1.0h - 0.6h * holds);
    return saturate(((half)_OS_Wetness - dries) / max(1.0h - dries, 0.2h)) * lerp(0.65h, 1.0h, saturate(up * 2.0h));
}

// Run-off streaks: where water runs down a face it leaves a film of algae and grime, long and vertical, strongest
// under the drips, building over the years. q the face's own plane (x along it, y up).
half OS_Streak(float2 q, half water, half up, half years, half seed, half stains)
{
    half facing = 1.0h - saturate(abs(up) * 1.6h);
    half sN = (half)(OS_Noise(float2(q.x * 26.0, q.y * 2.2) + seed * 5.3) * 0.7 + OS_Noise(float2(q.x * 70.0, q.y * 5.0)) * 0.3);
    return smoothstep(0.35h, 0.75h, water * 0.85h + sN * 0.45h - 0.2h) * facing * saturate(years / 25.0h) * stains;
}

// The wet surface: darker by its porosity, glazed by its film as far as it is smooth (polished by feet or hands),
// water standing where it is hollow (held: the bake's water held, 0 to 1).
void OS_Wet(inout half3 albedo, inout half smoothness, inout half3 normal, half wet, half4 profile, half polish,
            half held, half up)
{
    albedo *= 1.0h - 0.5h * profile.x * wet;
    // (a wet film on stone glosses but never mirrors: at 0.85 a trodden landing read as ice; the board, 02: wet slabs
    // dark with a sheen; standing water alone is a mirror)
    half film = lerp(0.3h, 0.62h, polish) * profile.y;
    smoothness = lerp(smoothness, max(smoothness, film), wet);
    half pool = smoothstep(0.5h, 0.85h, held) * saturate((half)_OS_Wetness * 1.5h - 0.4h) * step(0.8h, up);
    albedo = lerp(albedo, albedo * 0.7h, pool);
    smoothness = lerp(smoothness, 0.96h, pool);
    normal = normalize(lerp(normal, half3(0, 1, 0), pool));
}

#endif
