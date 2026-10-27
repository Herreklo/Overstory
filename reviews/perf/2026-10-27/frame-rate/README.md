# Frame rate: the walked corner towards 60 fps (27 October)

Four cuts, each A/B'd offscreen in one run (`LT1Perf.Offscreen`, the arms taken in turn) and proven on stills of the same views. Grain and dither move every pixel by up to 7/255 between any two renders, so stills are compared as 4x4 means, where two renders of the same frame differ by at most 1/255 (p99.9).

| Change | Saves offscreen | The look |
| --- | --- | --- |
| The fog bank from a camera-ray volume once a frame (`HazeVolume.compute`), not a 12-step march at every pixel | blue hour 24 to 32%: eye-on 57.5 to 43.5 ms, street 34.6 to 24.6, anchor-door 33.3 to 22.7 | within 7/255 per pixel, mean under 1, mean colour equal (`haze-volume/`); the near haze's lift of dark surfaces is unchanged |
| The palette and key block drawn without a copy, and the key block only in look D (`StylePassFeature`); no opaque copy (nothing reads it) | 2 to 3% | identical (the grain's floor) |
| AO at half size | about 10% in every light | p99.9 2 to 4/255 at creases, max 14; not visible at 1x beside the reference |
| The sun's beams not drawn where they cannot reach (`SunBeamsFeature.Weight` under 0.17) | 8 to 12% by day in 8 of the 9 walked views | every view at the grain's floor; at the Anchor's door, facing the sun, they are drawn as before |

The machine was loaded through the day (Understory, Blender, macOS media analysis), so the milliseconds above are from the calmest run; the shares hold across runs. The full-screen run (`../playable/frame-rate/`, 13:16 to 14:05) is not a measurement: its two runs disagree by 20 to 75% (acceptance 3%), with mediaanalysisd at 57% of a core on average and Blender at work beside it. Its screenshots are the look's proof in the player: against this morning's (`../playable/houses-light/`), every view of every light is within p99.9 1 to 6/255 on 4x4 means, the changes all at AO creases (the a-window recess the most, not visible at 1x). The full-screen numbers wait for a quiet Mac; from the shares, eye-on would be about 21 ms in drizzle, 22 in low sun and 23.5 at blue hour (from 27.5, 28.2 and 35.3), the Anchor's door about 12.5 by day.

What is left, by day at eye-on (offscreen shares, `split/offscreen.md`): the sun's shadows 15% (40% of it the soft filter), MSAA 10%, SSR 7%, post 6%, and the materials (town sky and growth, L5). Cures: cache the sun's shadow map, since the town is static and each light's sun fixed (redraw the cascades only when the camera moves a texel); shade the town's sky term once per chunk until history changes (L5); the stone's growth only where seen. The houses' new work is not yet in the playable; its panes' reflected sky still marches at blue hour (cure: a sky-haze map by direction).
