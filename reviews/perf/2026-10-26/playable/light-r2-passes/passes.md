# The pass budget: what each pass costs on the M4

1 run(s), 2026-10-26 23:16:29, Apple M4 (Metal), 2560x1440, MSAA 4x; 2 rounds of 60 frames a segment and six batches of six offscreen frames.

Milliseconds offscreen (the view drawn into a 2560 by 1440 target back to back, the GPU kept busy; the A/B number). A pass's cost is every pass on less every pass on but that one. 'All' and 'bare' (every pass off) are whole frames. The empty scene is the corner with every renderer hidden but the air's motes: the sky, the lights and post alone.

## The walk's corner in the town

| Pass | 1300-drizzle eye-foot | 1300-drizzle street | 1600-low-sun eye-foot | 1600-low-sun street | 1750-blue-hour eye-foot | 1750-blue-hour street |
| --- | --- | --- | --- | --- | --- | --- |
| **all** | 28.3 | 23.2 | 28.0 | 24.7 | 55.5 | 50.2 |
| sky | -0.1 | -0.8 | -0.9 | 1.6 | 0.6 | 1.7 |
| shadows |  |  |  |  |  |  |
| ssao |  |  |  |  |  |  |
| ssr |  |  |  |  |  |  |
| beams |  |  |  |  |  |  |
| foglights | 0.4 | -0.4 | -0.5 | 1.0 | 21.5 | 21.9 |
| keyblock |  |  |  |  |  |  |
| palette |  |  |  |  |  |  |
| post |  |  |  |  |  |  |
| msaa |  |  |  |  |  |  |
| motes |  |  |  |  |  |  |
| opaquetex |  |  |  |  |  |  |
| depthtex |  |  |  |  |  |  |
| fullscreen | 4.3 | 3.5 | 3.2 | 4.7 | 22.5 | 22.9 |
| sum of the passes | 0.3 | -1.3 | -1.4 | 2.5 | 22.1 | 23.6 |
| **bare** | 8.9 | 5.1 | 9.1 | 5.2 | 19.8 | 14.1 |
| all less bare | 19.4 | 18.1 | 18.9 | 19.6 | 35.7 | 36.1 |

## What each pass is

- *sky*: the sky (Sky.shader), drawn behind everything;
- *shadows*: the sun's shadow map, four cascades of one 4096 map;
- *ssao*: screen-space ambient occlusion (full resolution);
- *ssr*: screen-space reflections;
- *beams*: the sun's beams (SunBeamsQuarter.shader: a quarter of the pixels, 16 steps, one hard tap; the old full pass is the beams-full arm);
- *foglights*: the lamps in the fog (FogLights.shader; the colour copy only, no lamp is lit in these lights);
- *keyblock*: the woodblock print's key block (look D only; the colour copy and an early out here);
- *palette*: the style's colour pass (Palette.shader);
- *post*: post-processing: grade, bloom, grain, vignette, dither;
- *msaa*: MSAA 4x;
- *motes*: the air's motes (low sun only);
- *opaquetex*: the opaque texture the pipeline copies after the opaques (no shader reads it);
- *depthtex*: the depth texture (the screen-space passes still ask for it when they are on);
- *fullscreen*: the four full-screen passes together (beams, fog lights, key block, palette).
