# The pass budget: what each pass costs on the M4

1 run(s), 2026-10-22 21:50:20, Apple M4 (Metal), 2560x1440, MSAA 4x; 2 rounds of 60 frames a segment and six batches of six offscreen frames.

Milliseconds offscreen (the view drawn into a 2560 by 1440 target back to back, the GPU kept busy; the A/B number). A pass's cost is every pass on less every pass on but that one. 'All' and 'bare' (every pass off) are whole frames. The empty scene is the corner with every renderer hidden but the air's motes: the sky, the lights and post alone.

## The empty scene

| Pass | 1300-drizzle street | 1600-low-sun street | 1750-blue-hour street |
| --- | --- | --- | --- |
| **all** | 8.2 | 10.3 | 8.7 |
| sky |  |  |  |
| shadows | 0.2 | -0.1 | 0.1 |
| ssao | 0.8 | 0.6 | 0.6 |
| ssr | 2.4 | 2.2 | 2.3 |
| beams | 0.0 | 1.2 | -0.2 |
| foglights |  |  |  |
| keyblock |  |  |  |
| palette |  |  |  |
| post | 1.1 | 0.7 | 1.0 |
| msaa | 1.8 | 1.8 | 1.5 |
| motes |  |  |  |
| opaquetex |  |  |  |
| depthtex |  |  |  |
| fullscreen | 2.4 | 2.9 | 2.2 |
| sum of the passes | 6.3 | 6.4 | 5.3 |
| beams and shadows together | 0.2 | 1.2 | 0.0 |
|   the beams, no shadow map | -0.0 | 1.3 | -0.0 |
|   the shadow map, no beams | 0.2 | -0.0 | 0.2 |
|   only together | 0.1 | -0.1 | -0.1 |
| **bare** | 0.2 | 0.2 | 0.2 |
| all less bare | 8.0 | 10.2 | 8.5 |
| **flat** | 0.2 | 0.2 | 0.2 |
| bare less flat (the materials' shaders) | 0.0 | -0.0 | -0.0 |

## The walk's corner in the town

| Pass | 1300-drizzle eye-foot | 1300-drizzle street | 1300-drizzle a-window | 1300-drizzle anchor-door | 1600-low-sun eye-foot | 1600-low-sun street | 1600-low-sun a-window | 1600-low-sun anchor-door | 1750-blue-hour eye-foot | 1750-blue-hour street | 1750-blue-hour a-window | 1750-blue-hour anchor-door |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **all** | 32.9 | 27.2 | 29.1 | 22.5 | 35.6 | 30.6 | 33.3 | 24.6 | 26.4 | 21.6 | 23.6 | 18.0 |
| sky |  |  |  |  |  |  |  |  |  |  |  |  |
| shadows | 5.9 | 5.7 | 5.7 | 4.4 | 5.2 | 5.2 | 7.2 | 4.0 | -0.6 | 0.0 | 0.4 | -0.1 |
| ssao | 2.5 | 1.4 | 3.3 | 1.6 | 2.4 | 1.9 | 4.4 | 0.7 | 2.2 | 0.9 | 4.1 | 1.9 |
| ssr | 1.6 | 0.8 | 1.2 | 2.4 | 3.1 | 2.8 | 3.6 | 2.4 | 1.5 | 1.4 | 2.9 | 2.7 |
| beams | 0.5 | -0.1 | -0.2 | 0.1 | -0.0 | 2.1 | 3.0 | 0.5 | -0.0 | -0.3 | -0.1 | -0.0 |
| foglights |  |  |  |  |  |  |  |  |  |  |  |  |
| keyblock |  |  |  |  |  |  |  |  |  |  |  |  |
| palette |  |  |  |  |  |  |  |  |  |  |  |  |
| post | 1.8 | 1.1 | 1.6 | 1.3 | 2.0 | 1.9 | 3.8 | 1.2 | 1.2 | 1.1 | 1.8 | 1.3 |
| msaa | 4.8 | 4.2 | 3.5 | 2.3 | 4.8 | 4.7 | 4.2 | 2.2 | 4.1 | 3.2 | 3.2 | 2.4 |
| motes |  |  |  |  |  |  |  |  |  |  |  |  |
| opaquetex |  |  |  |  |  |  |  |  |  |  |  |  |
| depthtex |  |  |  |  |  |  |  |  |  |  |  |  |
| fullscreen | 2.7 | 1.1 | 2.1 | 1.4 | 4.7 | 4.3 | 6.0 | 3.7 | 2.0 | 2.1 | 2.7 | 2.3 |
| sum of the passes | 17.0 | 13.1 | 15.0 | 12.0 | 17.4 | 18.4 | 26.2 | 10.9 | 8.3 | 6.4 | 12.3 | 8.2 |
| beams and shadows together | 6.4 | 5.5 | 5.3 | 3.9 | 6.9 | 6.5 | 9.1 | 6.1 | -0.2 | -0.1 | -0.1 | -0.0 |
|   the beams, no shadow map | 0.6 | -0.2 | -0.4 | -0.6 | 1.8 | 1.4 | 2.0 | 2.1 | 0.5 | -0.1 | -0.5 | 0.1 |
|   the shadow map, no beams | 6.0 | 5.6 | 5.5 | 3.8 | 6.9 | 4.4 | 6.2 | 5.6 | -0.1 | 0.2 | -0.0 | -0.0 |
|   only together | -0.1 | 0.1 | 0.2 | 0.6 | -1.8 | 0.7 | 1.0 | -1.6 | -0.5 | -0.2 | 0.4 | -0.1 |
| **bare** | 14.2 | 9.6 | 10.0 | 7.5 | 13.3 | 9.3 | 9.4 | 7.1 | 13.3 | 9.1 | 9.5 | 7.2 |
| all less bare | 18.6 | 17.5 | 19.0 | 15.0 | 22.3 | 21.4 | 23.9 | 17.4 | 13.1 | 12.5 | 14.1 | 10.8 |
| **flat** | 2.1 | 2.1 | 2.3 | 1.3 | 2.0 | 1.9 | 1.9 | 1.3 | 2.3 | 2.4 | 2.3 | 1.3 |
| bare less flat (the materials' shaders) | 12.2 | 7.6 | 7.7 | 6.2 | 11.2 | 7.4 | 7.5 | 5.9 | 11.0 | 6.7 | 7.1 | 5.9 |

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
