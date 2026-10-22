# L5: who owns the materials' shaders

2 run(s) (2 reading(s) a segment); offscreen ms at 2560 by 1440, the median of the runs' medians. A family's cost is bare less flat-<family>; a term's is bare less bare-<term> (all less all-shadow for the shadow sample). Bare is every pass off: no shadow map, SSAO, SSR, MSAA or post.

## Milliseconds

| | 1300-drizzle eye-foot | 1300-drizzle street | 1300-drizzle a-window | 1300-drizzle anchor-door | 1600-low-sun eye-foot | 1600-low-sun street | 1600-low-sun a-window | 1600-low-sun anchor-door | 1750-blue-hour eye-foot | 1750-blue-hour street | 1750-blue-hour a-window | 1750-blue-hour anchor-door |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **all** | 32.5 | 27.2 | 29.3 | 22.6 | 35.0 | 30.0 | 31.2 | 24.5 | 26.8 | 22.0 | 23.4 | 18.1 |
| **bare** | 13.4 | 9.3 | 9.6 | 7.3 | 13.4 | 9.3 | 9.5 | 7.2 | 13.4 | 9.2 | 9.4 | 7.1 |
| **flat** | 2.0 | 2.1 | 2.2 | 1.4 | 2.0 | 2.0 | 2.0 | 1.3 | 2.0 | 1.9 | 2.0 | 1.3 |
| **bare less flat** (the materials' shaders) | 11.3 | 7.2 | 7.4 | 6.0 | 11.4 | 7.3 | 7.5 | 6.0 | 11.5 | 7.3 | 7.5 | 5.9 |
| family *stone*: bare less flat-stone | 6.7 | 2.8 | 2.0 | 0.0 | 6.8 | 2.9 | 2.0 | 0.0 | 6.9 | 2.9 | 1.9 | -0.0 |
| family *street*: bare less flat-street | 3.0 | 4.2 | 5.4 | 5.1 | 3.1 | 4.3 | 5.4 | 5.1 | 3.1 | 4.2 | 5.2 | 4.9 |
| family *water*: bare less flat-water | -0.2 | -0.1 | -0.0 | -0.2 | 0.0 | 0.0 | -0.0 | -0.3 | -0.0 | 0.0 | 0.0 | -0.2 |
| sum of the families | 9.6 | 6.8 | 7.4 | 4.9 | 9.9 | 7.2 | 7.3 | 4.8 | 9.9 | 7.1 | 7.2 | 4.7 |
| term *townsky*: bare less bare-townsky | 2.8 | 2.5 | 3.0 | 2.5 | 2.8 | 2.6 | 2.9 | 2.4 | 2.8 | 2.5 | 2.8 | 2.4 |
| term *clouds*: bare less bare-clouds | 2.4 | 2.1 | 2.4 | 2.1 | 2.5 | 2.2 | 2.4 | 2.1 | 2.5 | 2.2 | 2.3 | 2.1 |
| term *haze*: bare less bare-haze | 0.2 | 0.3 | 0.3 | 0.3 | 0.5 | 0.4 | 0.3 | 0.3 | 0.5 | 0.3 | 0.4 | 0.3 |
| term *lamps*: bare less bare-lamps | -0.1 | -0.0 | 0.1 | 0.1 | 0.1 | 0.1 | 0.1 | 0.1 | 0.1 | 0.1 | 0.1 | 0.1 |
| term *refl*: bare less bare-refl | -0.1 | 0.2 | 0.4 | 0.5 | 0.3 | 0.3 | 0.4 | 0.4 | 0.3 | 0.3 | 0.4 | 0.4 |
| term *brush*: bare less bare-brush | 0.3 | 0.4 | 0.5 | 0.5 | 0.5 | 0.4 | 0.3 | 0.4 | 0.6 | 0.4 | 0.5 | 0.5 |
| term *growth*: bare less bare-growth | 4.6 | 1.5 | 1.0 | 0.0 | 4.7 | 1.6 | 1.0 | -0.0 | 4.7 | 1.6 | 1.1 | -0.0 |
| term *rosettes*: bare less bare-rosettes | 1.0 | 0.4 | 0.3 | 0.0 | 1.2 | 0.5 | 0.3 | -0.0 | 1.2 | 0.5 | 0.3 | -0.0 |
| term *near*: bare less bare-near | 0.1 | 0.0 | 0.1 | 0.0 | 0.3 | 0.1 | 0.0 | 0.0 | 0.3 | 0.1 | 0.0 | -0.0 |
| term *shadow* (the shadow map's sample in the shaders): all less all-shadow | 1.4 | 1.1 | 0.4 | 1.0 | 1.0 | 2.1 | 1.4 | 1.5 | 0.4 | 0.4 | 0.2 | 0.2 |

## Spread between runs (largest less smallest run's difference)

| | 1300-drizzle eye-foot | 1300-drizzle street | 1300-drizzle a-window | 1300-drizzle anchor-door | 1600-low-sun eye-foot | 1600-low-sun street | 1600-low-sun a-window | 1600-low-sun anchor-door | 1750-blue-hour eye-foot | 1750-blue-hour street | 1750-blue-hour a-window | 1750-blue-hour anchor-door |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **bare less flat** (the materials' shaders) | 0.7 | 0.7 | 0.8 | 0.4 | 0.8 | 0.5 | 0.6 | 0.4 | 0.8 | 0.5 | 0.5 | 0.4 |
| family *stone*: bare less flat-stone | 0.3 | 0.2 | 0.1 | 0.1 | 0.4 | 0.1 | 0.1 | 0.0 | 0.4 | 0.2 | 0.2 | 0.0 |
| family *street*: bare less flat-street | 0.3 | 0.5 | 0.5 | 0.3 | 0.3 | 0.2 | 0.3 | 0.4 | 0.6 | 0.4 | 0.6 | 0.4 |
| family *water*: bare less flat-water | 0.0 | 0.1 | 0.1 | 0.1 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| term *townsky*: bare less bare-townsky | 0.2 | 0.4 | 0.2 | 0.1 | 0.2 | 0.1 | 0.3 | 0.2 | 0.3 | 0.2 | 0.4 | 0.2 |
| term *clouds*: bare less bare-clouds | 0.3 | 0.2 | 0.2 | 0.1 | 0.1 | 0.0 | 0.2 | 0.1 | 0.2 | 0.1 | 0.3 | 0.2 |
| term *haze*: bare less bare-haze | 0.3 | 0.1 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.1 | 0.0 | 0.0 |
| term *lamps*: bare less bare-lamps | 0.1 | 0.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.1 | 0.0 | 0.1 |
| term *refl*: bare less bare-refl | 0.3 | 0.3 | 0.1 | 0.1 | 0.0 | 0.0 | 0.1 | 0.0 | 0.1 | 0.2 | 0.0 | 0.1 |
| term *brush*: bare less bare-brush | 0.1 | 0.0 | 0.1 | 0.0 | 0.1 | 0.0 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 |
| term *growth*: bare less bare-growth | 0.3 | 0.2 | 0.1 | 0.0 | 0.4 | 0.1 | 0.0 | 0.0 | 0.4 | 0.2 | 0.1 | 0.1 |
| term *rosettes*: bare less bare-rosettes | 0.3 | 0.2 | 0.1 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.1 | 0.1 | 0.0 |
| term *near*: bare less bare-near | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.1 | 0.0 | 0.1 | 0.0 | 0.0 | 0.1 | 0.0 |
| term *shadow* (the shadow map's sample in the shaders): all less all-shadow | 0.6 | 0.2 | 1.8 | 1.0 | 1.3 | 0.7 | 1.3 | 0.6 | 0.5 | 0.0 | 0.1 | 0.1 |

## The terms

- *townsky*: the town's sky (OS_TownSky: 8 directions x 8 reaches, 64 map reads and 8 atan);
- *clouds*: the clouds' shadow (OS_CloudLight: the seven-noise cloud field);
- *haze*: the air (OS_Atmosphere, the existing OS_HAZE_OFF);
- *lamps*: the lamps' light loop (Forward+ additional lights, look P);
- *refl*: the reflection probes' sample (GlossyEnvironmentReflection, look P);
- *brush*: the brushwork (OS_Brush, look P);
- *growth*: stone's growth layer whole (Growth.hlsl: lichen fields, young rosettes, moss cushions);
- *rosettes*: stone's young lichen rosettes alone (the 3x3 loop lerped away past about 1 cm a pixel);
- *near*: every near mark (OS_Near forced to 0: grain relief, sand, crazing, areoles, crumbs);
- *shadow*: the main light's shadow-map sample and URP's soft filter in the street and stone shaders (the map still drawn).
