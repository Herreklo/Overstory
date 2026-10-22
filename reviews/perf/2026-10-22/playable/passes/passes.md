# The pass budget: what each pass costs on the M4

1 run(s), 2026-10-22 18:34:20, Apple M4 (Metal), 2560x1440, MSAA 4x; 2 rounds of 60 frames a segment and six batches of six offscreen frames.

Milliseconds offscreen (the view drawn into a 2560 by 1440 target back to back, the GPU kept busy; the A/B number). A pass's cost is every pass on less every pass on but that one. 'All' and 'bare' (every pass off) are whole frames. The empty scene is the corner with every renderer hidden but the air's motes: the sky, the lights and post alone.

## The empty scene

| Pass | 1300-drizzle street | 1600-low-sun street | 1750-blue-hour street |
| --- | --- | --- | --- |
| **all** | 8.6 | 49.1 | 9.2 |
| sky |  |  |  |
| shadows | 0.1 | -0.4 | 0.0 |
| ssao | 0.7 | 0.0 | 0.7 |
| ssr | 2.4 | 2.5 | 2.3 |
| beams | 0.5 | 40.2 | 0.4 |
| foglights |  |  |  |
| keyblock |  |  |  |
| palette |  |  |  |
| post | 1.1 | 1.2 | 1.0 |
| msaa | 1.9 | 1.7 | 1.8 |
| motes |  |  |  |
| opaquetex |  |  |  |
| depthtex |  |  |  |
| fullscreen | 2.8 | 42.0 | 2.7 |
| sum of the passes | 6.7 | 45.1 | 6.2 |
| beams and shadows together | 0.7 | 40.3 | 0.5 |
|   the beams, no shadow map | 0.6 | 40.7 | 0.5 |
|   the shadow map, no beams | 0.1 | 0.1 | 0.1 |
|   only together | -0.1 | -0.5 | -0.1 |
| **bare** | 0.2 | 0.2 | 0.2 |
| all less bare | 8.4 | 48.9 | 9.0 |
| **flat** | 0.2 | 0.2 | 0.2 |
| bare less flat (the materials' shaders) | 0.0 | -0.0 | 0.0 |

## The walk's corner in the town

| Pass | 1300-drizzle eye-foot | 1300-drizzle street | 1300-drizzle a-window | 1300-drizzle anchor-door | 1600-low-sun eye-foot | 1600-low-sun street | 1600-low-sun a-window | 1600-low-sun anchor-door | 1750-blue-hour eye-foot | 1750-blue-hour street | 1750-blue-hour a-window | 1750-blue-hour anchor-door |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **all** | 34.2 | 38.9 | 33.7 | 23.6 | 99.8 | 105.7 | 99.2 | 87.9 | 28.0 | 31.1 | 26.5 | 18.5 |
| sky |  |  |  |  |  |  |  |  |  |  |  |  |
| shadows | 4.3 | 5.3 | 5.2 | 3.4 | 31.3 | 34.1 | 33.0 | 29.6 | -0.9 | -0.3 | -0.0 | -0.1 |
| ssao | 0.5 | 0.0 | 2.8 | 1.0 | 3.8 | 5.2 | 5.6 | 3.7 | 2.8 | 2.8 | 4.7 | 2.1 |
| ssr | 1.0 | 0.5 | 1.5 | 1.8 | 3.6 | 4.9 | 4.4 | 6.3 | 2.7 | 2.8 | 2.9 | 2.9 |
| beams | 0.1 | -2.3 | -1.0 | -0.5 | 64.1 | 65.6 | 65.1 | 64.2 | 0.9 | 0.5 | 0.6 | 0.1 |
| foglights |  |  |  |  |  |  |  |  |  |  |  |  |
| keyblock |  |  |  |  |  |  |  |  |  |  |  |  |
| palette |  |  |  |  |  |  |  |  |  |  |  |  |
| post | 0.1 | -0.4 | 0.6 | 0.9 | 7.2 | 8.1 | 8.0 | 6.8 | 1.3 | 1.3 | 1.4 | 1.1 |
| msaa | 3.3 | 3.4 | 2.2 | 1.8 | 8.7 | 13.3 | 10.9 | 7.9 | 4.4 | 5.7 | 4.0 | 2.7 |
| motes |  |  |  |  |  |  |  |  |  |  |  |  |
| opaquetex |  |  |  |  |  |  |  |  |  |  |  |  |
| depthtex |  |  |  |  |  |  |  |  |  |  |  |  |
| fullscreen | 1.4 | 1.6 | 2.6 | 2.2 | 66.9 | 69.3 | 67.5 | 66.6 | 3.1 | 3.3 | 3.1 | 2.8 |
| sum of the passes | 9.3 | 6.5 | 11.4 | 8.2 | 118.7 | 131.1 | 127.0 | 118.5 | 11.1 | 12.9 | 13.6 | 8.8 |
| beams and shadows together | 5.1 | 6.4 | 6.2 | 4.3 | 71.5 | 73.9 | 72.7 | 69.2 | 0.6 | 0.4 | 0.7 | 0.5 |
|   the beams, no shadow map | 0.8 | 1.2 | 0.9 | 0.9 | 40.2 | 39.8 | 39.6 | 39.6 | 1.5 | 0.7 | 0.8 | 0.7 |
|   the shadow map, no beams | 5.0 | 8.7 | 7.2 | 4.8 | 7.4 | 8.4 | 7.6 | 4.9 | -0.3 | -0.1 | 0.1 | 0.5 |
|   only together | -0.7 | -3.5 | -1.9 | -1.4 | 23.9 | 25.7 | 25.4 | 24.7 | -0.7 | -0.2 | -0.2 | -0.6 |
| **bare** | 14.6 | 15.7 | 11.6 | 7.5 | 13.8 | 14.9 | 11.1 | 7.2 | 13.6 | 14.6 | 11.0 | 7.1 |
| all less bare | 19.6 | 23.1 | 22.1 | 16.1 | 85.9 | 90.8 | 88.1 | 80.7 | 14.5 | 16.4 | 15.5 | 11.4 |
| **flat** | 2.0 | 2.1 | 2.0 | 1.3 | 2.1 | 2.0 | 2.0 | 1.3 | 2.1 | 2.1 | 2.0 | 1.3 |
| bare less flat (the materials' shaders) | 12.6 | 13.6 | 9.6 | 6.2 | 11.8 | 12.9 | 9.1 | 5.9 | 11.5 | 12.6 | 9.0 | 5.8 |

## The birch (low sun, every pass on)

| View | With (ms) | Without (ms) | The birch |
| --- | --- | --- | --- |
| eye-foot | 99.8 | 98.5 | +1.3 |
| street | 105.7 | 94.6 | +11.1 |
| a-window | 99.2 | 95.2 | +4.0 |
| anchor-door | 87.9 | 86.3 | +1.7 |

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
