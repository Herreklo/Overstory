// The town's horizon, worked out once from its sky map (Overstory.Scenes.SkyMap) for every metre of it, so a surface
// reads how much sky the town leaves it in a few taps instead of marching the map itself (StreetLooks.hlsl,
// OS_TownSky). Pass 0 writes, for one height over each texel's ground, the horizon's angle in four of eight
// directions; pass 1 writes that ground: the lowest open surface within a metre and a quarter, so the texels along a
// wall's foot count from the lane, not from the roof over them. Pass 2 writes, at the same heights, what the rest of the
// town round each texel's own house changes in the ambient light on a face there, from what it hides and how the sun
// lights it (OS_TownLight), again whenever the sun or the ambient changes.
Shader "Hidden/Overstory/TownHorizon"
{
    SubShader
    {
        ZTest Always ZWrite Off Cull Off

        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/Common.hlsl"

        TEXTURE2D(_OS_SkyMap);
        SAMPLER(sampler_OS_SkyMap);
        float4 _OS_SkyMapRect;   // xy the map's corner (world x, z), z 1 / its size, w 1 when v reads from the top
        float4 _OS_HorizonInfo;  // x texels a side, y height levels, z the top level (m over the ground), w on
        float4 _OS_HorizonBuild; // x the height level drawn, y which four directions (0 or 1)

        struct Varyings { float4 positionCS : SV_POSITION; };

        Varyings Vert(uint id : SV_VertexID)
        {
            Varyings o;
            float2 uv = float2((id << 1) & 2, id & 2);
            o.positionCS = float4(uv * 2.0 - 1.0, 0.0, 1.0);
            return o;
        }

        float Height(float2 xz)
        {
            float2 q = (xz - _OS_SkyMapRect.xy) * _OS_SkyMapRect.z;
            q.y = _OS_SkyMapRect.w > 0.5 ? 1.0 - q.y : q.y;
            return SAMPLE_TEXTURE2D_LOD(_OS_SkyMap, sampler_OS_SkyMap, q, 0).r;
        }

        // the texel's middle in world x, z
        float2 Middle(float4 positionCS)
        {
            return _OS_SkyMapRect.xy + positionCS.xy / _OS_HorizonInfo.x / _OS_SkyMapRect.z;
        }

        // the lowest surface within 1.25 m; the sea and anything unmapped (cleared to -1000) count as sea level
        float Ground(float2 xz)
        {
            float g = 1e6;
            [unroll] for (int j = 0; j < 6; j++)
                [unroll] for (int i = 0; i < 6; i++)
                {
                    float h = Height(xz + (float2(i, j) - 2.5) * 0.5);
                    g = min(g, h < -500.0 ? 0.0 : h);
                }
            return g;
        }
        ENDHLSL

        Pass
        {
            Name "Horizon"
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag

            float4 Frag(Varyings input) : SV_Target
            {
                float2 xz = Middle(input.positionCS);
                float t = _OS_HorizonBuild.x / max(_OS_HorizonInfo.y - 1.0, 1.0);
                float y = Ground(xz) + _OS_HorizonInfo.z * t * t;
                const float reach[8] = { 1.0, 2.0, 3.5, 6.0, 10.0, 17.0, 30.0, 56.0 };
                float4 alpha = 0.0;
                [unroll] for (int k = 0; k < 4; k++)
                {
                    float a = (k + 4.0 * _OS_HorizonBuild.y + 0.5) * 0.785398;
                    float2 dir = float2(cos(a), sin(a));
                    float tanMax = 0.0;
                    [unroll] for (int j = 0; j < 8; j++)
                        tanMax = max(tanMax, (Height(xz + dir * reach[j]) - y - 0.2) / reach[j]);
                    alpha[k] = atan(tanMax) / HALF_PI;
                }
                return alpha;
            }
            ENDHLSL
        }

        Pass
        {
            Name "Ground"
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag

            float Frag(Varyings input) : SV_Target
            {
                return Ground(Middle(input.positionCS));
            }
            ENDHLSL
        }

        Pass
        {
            Name "Bounce"
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag

            // what the town is made of, from above (TownHeight.shader, Albedo): each house's wall paint over its
            // footprint, and each surface's own albedo with whose it is (alpha: a house's number, 0 for the ground)
            TEXTURE2D(_OS_TownWall);
            TEXTURE2D(_OS_TownTop);
            SamplerState os_point_clamp_albedo;
            float4 _OS_BounceSun;   // xyz towards the sun (world), w how dark its shadow is (the light's shadow strength)
            float4 _OS_BounceLight; // the sun's light (linear colour times intensity)
            // the trilight (linear): the sky overhead, at the horizon and underfoot, and its ambient on a wall
            float4 _OS_BounceSky, _OS_BounceHorizon, _OS_BounceGround, _OS_BounceWall;

            static const float reach[8] = { 1.0, 2.0, 3.5, 6.0, 10.0, 17.0, 30.0, 56.0 };
            static const float toward[8] = { 0.5, 1.0, 2.0, 3.5, 6.0, 10.0, 17.0, 30.0 };

            struct Targets { float4 t0 : SV_Target0; float4 t1 : SV_Target1; float4 t2 : SV_Target2; float4 t3 : SV_Target3; };

            float2 MapUV(float2 xz)
            {
                float2 q = (xz - _OS_SkyMapRect.xy) * _OS_SkyMapRect.z;
                q.y = _OS_SkyMapRect.w > 0.5 ? 1.0 - q.y : q.y;
                return q;
            }

            float3 Albedo(bool wall, float2 xz)
            {
                return wall ? SAMPLE_TEXTURE2D_LOD(_OS_TownWall, os_point_clamp_albedo, MapUV(xz), 0).rgb
                            : SAMPLE_TEXTURE2D_LOD(_OS_TownTop, os_point_clamp_albedo, MapUV(xz), 0).rgb;
            }

            float Owner(float2 xz)
            {
                return round(SAMPLE_TEXTURE2D_LOD(_OS_TownTop, os_point_clamp_albedo, MapUV(xz), 0).a * 255.0);
            }

            float Luma(float3 c) { return dot(c, float3(0.2126, 0.7152, 0.0722)); }

            // A surface a ray meets at `at`, coming along `dir`, at height hy: its albedo (a wall's paint where the map
            // steps, steeper than about 56 degrees; else the surface's own) and the share of the sun's light on it (its
            // angle to the sun, and whether the town between shades it, marched over the height map toward the sun
            // from half a metre off the face)
            void Surface(float2 at, float2 dir, float hy, float3 sun, out float3 albedo, out float onSun)
            {
                float2 g = float2(Height(at + float2(0.5, 0.0)) - Height(at - float2(0.5, 0.0)),
                                  Height(at + float2(0.0, 0.5)) - Height(at - float2(0.0, 0.5)));
                float gl = length(g);
                bool wall = gl > 1.5;
                float3 nS = wall ? float3(-g.x, 0.0, -g.y) / gl : normalize(float3(-g.x, 1.0, -g.y));
                onSun = saturate(dot(nS, sun));
                float flat = length(sun.xz);
                UNITY_BRANCH if (onSun > 0.0 && flat > 1e-3)
                {
                    float2 sunDir = sun.xz / flat;
                    float rise = sun.y / flat;
                    float3 p = float3(at.x - dir.x * 0.3, hy, at.y - dir.y * 0.3) + nS * 0.5;
                    float shade = 0.0;
                    [unroll] for (int s = 0; s < 8; s++)
                        shade = max(shade, step(p.y + toward[s] * rise + 0.1, Height(p.xz + sunDir * toward[s])));
                    onSun *= 1.0 - _OS_BounceSun.w * shade;
                }
                albedo = Albedo(wall, at + dir * 0.3);
            }

            // In each of the eight directions, what the town other than the texel's own house puts round it (its own
            // house, eaves and all, is in its own bake): the horizon the others make (hidden), the depression down to
            // the foot of the first of them (below it only the ground is seen), and what fills the band above, seen along
            // three rays up it, and what of the band below meets them, seen along four rays down it, each marched to what
            // it meets first: a wall, a roof below the texel, or the ground, which is not theirs (foot: the depression whose
            // band a wall takes as much from as it takes from what of it meets them). Each ray is weighted by what a wall
            // takes from it (cos^2). What they meet gives its albedo and the share of the sun's light on it (a direction
            // with nothing met takes the others' mean), and from those and the trilight, what the town changes in the
            // ambient on a face there.
            Targets Frag(Varyings input)
            {
                float2 xz = Middle(input.positionCS);
                float t = _OS_HorizonBuild.x / max(_OS_HorizonInfo.y - 1.0, 1.0);
                float g = Ground(xz);
                float lift = _OS_HorizonInfo.z * t * t;
                float y = g + lift, y0 = y + 0.2;
                float3 sun = normalize(_OS_BounceSun.xyz);
                // the house the texel is by: the one over it, else the nearest within a metre and a half
                float own = Owner(xz);
                [unroll] for (int r = 1; r <= 3; r++)
                    [unroll] for (int q = 0; q < 8; q++)
                        own = own > 0.5 ? own : Owner(xz + float2(cos(q * 0.785398), sin(q * 0.785398)) * 0.5 * r);

                float4 dirs[8];
                float hidden[8], foot[8];
                bool seen[8];
                float4 sum = 0.0;
                float count = 0.0;
                [loop]
                for (int k = 0; k < 8; k++)
                {
                    float a = (k + 0.5) * 0.785398;
                    float2 dir = float2(cos(a), sin(a));
                    float tanMax = 0.0, near = 0.0, prev = 0.0;
                    [unroll] for (int j = 0; j < 8; j++)
                    {
                        float2 p = xz + dir * reach[j];
                        float h = Height(p);
                        bool other = abs(Owner(p) - own) > 0.5;
                        tanMax = other ? max(tanMax, (h - y0) / reach[j]) : tanMax;
                        bool raised = other && h > g + 0.5;
                        prev = near == 0.0 && !raised ? reach[j] : prev;
                        near = near == 0.0 && raised ? reach[j] : near;
                    }
                    float alpha = atan(tanMax), beta = 0.0, d = 0.0;
                    if (near > 0.0)
                    {
                        float lo = prev, hi = near;
                        [unroll] for (int fb = 0; fb < 4; fb++)
                        {
                            float m = 0.5 * (lo + hi);
                            float2 p = xz + dir * m;
                            bool raised = abs(Owner(p) - own) > 0.5 && Height(p) > g + 0.5;
                            hi = raised ? m : hi;
                            lo = raised ? lo : m;
                        }
                        d = hi;
                        beta = atan(lift / d);
                    }

                    float3 albedo = 0.0;
                    float lit = 0.0, weight = 0.0;
                    if (alpha > 0.01)
                    {
                        [unroll]
                        for (int i = 0; i < 3; i++)
                        {
                            float e0 = alpha * i / 3.0, e1 = alpha * (i + 1) / 3.0;
                            float w = (e1 - e0) * 0.5 + (sin(2.0 * e1) - sin(2.0 * e0)) * 0.25;
                            float te = tan(0.5 * (e0 + e1));
                            // the first reach of the others along the ray, then halved four times toward the last clear
                            float lo = 0.0, hi = 0.0;
                            bool found = false;
                            [unroll] for (int ju = 0; ju < 8; ju++)
                            {
                                float2 p = xz + dir * reach[ju];
                                bool inside = abs(Owner(p) - own) > 0.5 && Height(p) > y0 + reach[ju] * te;
                                hi = !found && inside ? reach[ju] : hi;
                                lo = !found && !inside ? reach[ju] : lo;
                                found = found || inside;
                            }
                            if (found)
                            {
                                [unroll] for (int ub = 0; ub < 4; ub++)
                                {
                                    float m = 0.5 * (lo + hi);
                                    float2 p = xz + dir * m;
                                    bool inside = abs(Owner(p) - own) > 0.5 && Height(p) > y0 + m * te;
                                    hi = inside ? m : hi;
                                    lo = inside ? lo : m;
                                }
                                float3 c;
                                float onSun;
                                Surface(xz + dir * hi, dir, y0 + lo * te, sun, c, onSun);
                                albedo += w * c;
                                lit += w * Luma(c) * onSun;
                                weight += w;
                            }
                        }
                    }
                    if (beta > 0.01)
                    {
                        // the band below, each ray marched to the first thing over it (the ground stops it too)
                        float covered = 0.0;
                        [unroll]
                        for (int il = 0; il < 4; il++)
                        {
                            float e0 = beta * il / 4.0, e1 = beta * (il + 1) / 4.0;
                            float w = (e1 - e0) * 0.5 + (sin(2.0 * e1) - sin(2.0 * e0)) * 0.25;
                            float te = tan(0.5 * (e0 + e1));
                            float lo = 0.0, hi = 0.0;
                            bool found = false;
                            [unroll] for (int jl = 0; jl < 8; jl++)
                            {
                                float2 p = xz + dir * reach[jl];
                                float ow = Owner(p);
                                bool inside = (abs(ow - own) > 0.5 || ow < 0.5) && Height(p) > y - reach[jl] * te;
                                hi = !found && inside ? reach[jl] : hi;
                                lo = !found && !inside ? reach[jl] : lo;
                                found = found || inside;
                            }
                            if (found)
                            {
                                [unroll] for (int lb = 0; lb < 4; lb++)
                                {
                                    float m = 0.5 * (lo + hi);
                                    float2 p = xz + dir * m;
                                    float ow = Owner(p);
                                    bool inside = (abs(ow - own) > 0.5 || ow < 0.5) && Height(p) > y - m * te;
                                    hi = inside ? m : hi;
                                    lo = inside ? lo : m;
                                }
                                float2 p = xz + dir * hi;
                                if (abs(Owner(p) - own) > 0.5 && Height(p) > g + 0.5)
                                {
                                    float3 c;
                                    float onSun;
                                    Surface(p, dir, y - lo * te, sun, c, onSun);
                                    albedo += w * c;
                                    lit += w * Luma(c) * onSun;
                                    weight += w;
                                    covered += w;
                                }
                            }
                        }
                        // the depression whose band a wall takes as much from (beta / 2 + sin 2 beta / 4) as from what met them
                        float eq = covered;
                        [unroll] for (int nb = 0; nb < 4; nb++)
                        {
                            float c2 = cos(eq);
                            eq = clamp(eq - (0.5 * eq + 0.25 * sin(2.0 * eq) - covered) / max(c2 * c2, 0.05), 0.0, beta);
                        }
                        beta = eq;
                    }
                    hidden[k] = alpha;
                    foot[k] = beta;
                    seen[k] = weight > 0.0;
                    // the sun's share weighted by how much each ray's surface gives back, so albedo x share is the band's
                    dirs[k] = seen[k] ? float4(albedo / weight, lit / max(Luma(albedo), 1e-5)) : 0.0;
                    sum += dirs[k];
                    count += seen[k] ? 1.0 : 0.0;
                }
                float4 mean = count > 0.0 ? sum / count : 0.0;
                // what each direction changes for a wall facing it: the bands it hides taken away (the trilight grades from
                // the horizon to the sky above and the ground below) and the light of what fills them put in their place,
                // its albedo times the sun's share on it and the ambient on a wall; and for a face looking up or down
                float3 sky = _OS_BounceSky.rgb, hor = _OS_BounceHorizon.rgb, gnd = _OS_BounceGround.rgb;
                float3 P[8];
                float3 upC = 0.0, downC = 0.0;
                [unroll]
                for (int e = 0; e < 8; e++)
                {
                    float4 v = seen[e] ? dirs[e] : mean;
                    float3 across = max(v.rgb, 0.0) * (_OS_BounceLight.rgb * saturate(v.a) + _OS_BounceWall.rgb);
                    float sa = sin(hidden[e]), ca = cos(hidden[e]), sb = sin(foot[e]), cb = cos(foot[e]);
                    P[e] = (across - hor) * (hidden[e] + sa * ca + foot[e] + sb * cb) / PI
                         - ((sky - hor) * (1.0 - ca * ca * ca) + (gnd - hor) * (1.0 - cb * cb * cb)) * 2.0 / (3.0 * PI);
                    upC += ((across - hor) * sa * sa - (sky - hor) * 2.0 / 3.0 * sa * sa * sa) / 8.0;
                    downC += ((across - hor) * sb * sb - (gnd - hor) * 2.0 / 3.0 * sb * sb * sb) / 8.0;
                }
                // a wall's change facing each of the eight ways, each direction weighted by how much the wall faces it, kept
                // as a mean and a cosine and sine of the way it faces; a face looking up and one looking down each its own
                float3 c0 = 0.0, cx = 0.0, cz = 0.0;
                [unroll]
                for (int m = 0; m < 8; m++)
                {
                    float3 ch = 0.0;
                    float full = 0.0;
                    [unroll] for (int e2 = 0; e2 < 8; e2++)
                    {
                        float f = saturate(cos((e2 - m) * 0.785398));
                        ch += f * P[e2];
                        full += f;
                    }
                    ch /= full;
                    float am = (m + 0.5) * 0.785398;
                    c0 += ch / 8.0;
                    cx += ch * cos(am) / 4.0;
                    cz += ch * sin(am) / 4.0;
                }
                Targets o;
                o.t0 = float4(c0, cx.r);
                o.t1 = float4(cx.gb, cz.rg);
                o.t2 = float4(cz.b, upC);
                o.t3 = float4(downC, 0.0);
                return o;
            }
            ENDHLSL
        }
    }
}
