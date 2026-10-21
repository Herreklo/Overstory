# The pass budget: what each pass costs on the M4

1 run(s), 2026-10-21 21:19:27, Apple M4 (Metal), 2560x1440, MSAA 4x; 2 rounds of 60 frames a segment and six batches of six offscreen frames.

Milliseconds offscreen (the view drawn into a 2560 by 1440 target back to back, the GPU kept busy; the A/B number). A pass's cost is every pass on less every pass on but that one. 'All' and 'bare' (every pass off) are whole frames. The empty scene is the corner with every renderer hidden but the air's motes: the sky, the lights and post alone.

## The empty scene

| Pass | 1300-drizzle street | 1300-drizzle high | 1600-low-sun street | 1600-low-sun high | 1750-blue-hour street | 1750-blue-hour high |
| --- | --- | --- | --- | --- | --- | --- |
| **all** | 8.5 | 7.0 | 49.0 | 46.7 | 9.2 | 7.0 |
| sky | 1.5 | -0.1 | 2.4 | 0.0 | 2.2 | -0.0 |
| shadows | -0.0 | -0.0 | 0.1 | 0.0 | 0.0 | -0.0 |
| ssao | 0.6 | 0.7 | 0.7 | 0.6 | 0.7 | 0.6 |
| ssr | 2.3 | 2.2 | 2.4 | 2.2 | 2.3 | 2.2 |
| beams | 0.5 | 0.4 | 40.2 | 40.1 | 0.4 | 0.5 |
| foglights | 0.5 | 0.5 | 0.5 | 0.5 | 0.4 | 0.5 |
| keyblock | 0.5 | 0.4 | 0.5 | 0.5 | 0.4 | 0.4 |
| palette | 0.7 | 0.7 | 0.9 | 0.8 | 0.8 | 0.8 |
| post | 0.9 | 0.9 | 1.2 | 1.1 | 1.0 | 0.8 |
| msaa | 1.8 | 1.8 | 1.4 | 1.4 | 1.8 | 1.8 |
| motes |  |  | 0.1 | 0.0 |  |  |
| opaquetex | -0.0 | 0.0 | 0.1 | -0.0 | 0.0 | -0.0 |
| depthtex | -0.0 | -0.0 | 0.1 | 0.0 | -0.0 | -0.0 |
| fullscreen | 2.7 | 2.6 | 41.9 | 41.7 | 2.7 | 2.6 |
| sum of the passes | 9.3 | 7.5 | 50.5 | 47.3 | 10.0 | 7.4 |
| **bare** | 0.2 | 0.2 | 0.2 | 0.2 | 0.2 | 0.2 |
| all less bare | 8.4 | 6.8 | 48.8 | 46.5 | 9.0 | 6.8 |

## The corner

| Pass | 1300-drizzle eye-foot | 1300-drizzle street | 1300-drizzle into12 | 1300-drizzle high | 1600-low-sun eye-foot | 1600-low-sun street | 1600-low-sun into12 | 1600-low-sun high | 1750-blue-hour eye-foot | 1750-blue-hour street | 1750-blue-hour into12 | 1750-blue-hour high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **all** | 32.0 | 37.3 | 37.1 | 41.2 | 97.7 | 102.1 | 101.6 | 105.4 | 26.7 | 30.0 | 29.7 | 34.2 |
| sky | -0.5 | 0.0 | -0.1 | 0.0 | 0.2 | 0.3 | 0.2 | 0.2 | -0.7 | -1.3 | -0.3 | -0.3 |
| shadows | 5.1 | 7.1 | 7.4 | 7.1 | 31.1 | 32.4 | 32.5 | 31.9 | -1.0 | -0.5 | -0.2 | -0.1 |
| ssao | 1.9 | 2.8 | 2.7 | 2.7 | 3.9 | 4.3 | 5.5 | 4.3 | 2.5 | 2.4 | 3.7 | 4.0 |
| ssr | 1.6 | 2.0 | 2.4 | 2.4 | 3.8 | 3.9 | 5.3 | 5.7 | 2.7 | 3.2 | 3.6 | 3.8 |
| beams | -1.2 | -0.4 | -0.4 | -0.6 | 63.6 | 64.3 | 64.2 | 64.1 | 0.4 | 1.0 | 1.5 | 1.9 |
| foglights | -1.0 | -0.5 | -0.4 | -0.6 | 1.0 | 1.3 | 1.8 | 1.0 | 0.7 | 0.9 | 1.0 | 1.6 |
| keyblock | -1.1 | -0.4 | -0.4 | -0.5 | 1.1 | 1.4 | 0.8 | 0.9 | 0.4 | 0.9 | 1.2 | 1.4 |
| palette | -0.5 | -0.4 | -0.5 | -0.4 | 0.4 | 1.1 | 1.5 | 1.7 | 0.6 | 0.8 | 1.0 | 1.4 |
| post | 0.1 | 0.3 | 0.2 | 0.1 | 2.8 | 3.6 | 4.7 | 3.0 | 0.8 | 1.2 | 1.2 | 1.5 |
| msaa | 3.7 | 4.9 | 3.4 | 3.7 | 5.4 | 6.5 | 5.6 | 5.1 | 4.0 | 5.4 | 4.6 | 5.0 |
| motes |  |  |  |  | 0.7 | 1.0 | 1.5 | 0.8 |  |  |  |  |
| opaquetex | -1.6 | -1.1 | -1.1 | -1.4 | 0.7 | 0.9 | 1.0 | 0.6 | -0.0 | 0.2 | 0.3 | 0.6 |
| depthtex | -1.6 | -1.5 | -1.4 | -1.6 | 1.2 | 0.5 | 1.6 | 0.6 | -0.5 | -0.2 | 0.0 | 0.2 |
| fullscreen | 1.5 | 1.7 | 1.8 | 1.7 | 65.3 | 66.0 | 66.5 | 66.7 | 2.4 | 2.6 | 2.8 | 3.2 |
| sum of the passes | 4.9 | 12.7 | 11.8 | 11.0 | 115.9 | 121.5 | 126.2 | 119.9 | 9.9 | 14.1 | 17.8 | 20.8 |
| **bare** | 13.6 | 14.6 | 15.7 | 18.9 | 13.4 | 14.3 | 15.3 | 18.3 | 13.4 | 14.5 | 15.6 | 18.7 |
| all less bare | 18.4 | 22.6 | 21.5 | 22.3 | 84.4 | 87.8 | 86.3 | 87.1 | 13.3 | 15.4 | 14.1 | 15.5 |

## The birch (low sun, every pass on)

| View | With (ms) | Without (ms) | The birch |
| --- | --- | --- | --- |
| eye-foot | 97.7 | 95.3 | +2.4 |
| street | 102.1 | 89.5 | +12.6 |
| into12 | 101.6 | 91.6 | +10.0 |
| high | 105.4 | 89.8 | +15.6 |

## What each pass is

- *sky*: the sky (Sky.shader), drawn behind everything;
- *shadows*: the sun's shadow map, four cascades of one 4096 map;
- *ssao*: screen-space ambient occlusion (full resolution);
- *ssr*: screen-space reflections;
- *beams*: the sun's beams (SunBeams.shader: 40 shadow-map taps a pixel);
- *foglights*: the lamps in the fog (FogLights.shader; the colour copy only, no lamp is lit in these lights);
- *keyblock*: the woodblock print's key block (look D only; the colour copy and an early out here);
- *palette*: the style's colour pass (Palette.shader);
- *post*: post-processing: grade, bloom, grain, vignette, dither;
- *msaa*: MSAA 4x;
- *motes*: the air's motes (low sun only);
- *opaquetex*: the opaque texture the pipeline copies after the opaques (no shader reads it);
- *depthtex*: the depth texture (the screen-space passes still ask for it when they are on);
- *fullscreen*: the four full-screen passes together (beams, fog lights, key block, palette).
