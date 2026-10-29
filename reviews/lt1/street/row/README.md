# The row: 107, 108 and 109 together, the windows step (r03)

- Bad: the panes are darker but they are not ref 10's dark eyes. At the street stop in overcast, 108's glass goes from L26.4 (r02) to 16.1 (r03). That is inside ref 10's L6–18, but at its top. At 1:1, 108's white bars and its sheers keep each window light: the sheers are L46 and cover half of each pane.
- Bad: in low sun, 109's roof is a black mass with no detail in every round (r01 L5.9, r03 5.1).
- Bad: 108's long side wall at eye level in overcast is L70, against r01's 51. The gable front is L69.2, against 67.4, which is within 2 L. r01's overcast was a directional sun; under a CIE overcast every vertical face sees the same sky, so r02 and r03 are truer. But the turn of 108's corner barely reads, and that is a question for the light key, which is not changed here.
- Holds:
  - the whites stay at L82.8;
  - 107's clean-to-grime ΔL goes from 35.9 to 39.7;
  - 109's ox-red goes from L25.3, C 15.7, h 36 to L22.1, C 16.3, h 35: darker and a little richer, not muddy (r01 is L24.5);
  - the roofs' spread of values widens;
  - at most 3.2% of any frame falls below L5;
  - the rock's grey frames barely move (`r03-rock-toe.jpg`, the toe applied offline with the same curve, within 0.2 L of the engine).

Two changes, each beside r02:
- r03a, the room. A single-glazed, putty-glazed pane has two faces: 108's cross windows of 1985 and 109's casements of 1850; no sealed pane is seen. The room is now lit by what its window sees, the street's view out, through the glass's share of the opening (108 0.61, 109 0.47). Its bounce follows the BRE internally reflected component (Digest 310) for a shallow front room with dark old furniture. The room alone goes from L19 to 8 at the street stop. The pane is now mostly its reflection: in the light it is 1/31 of the white wall (Fresnel 0.077 × a far shore at 0.25 of the horizon). On screen, though, it showed at 1/19, because the Neutral tonemapper has a shoulder and no toe.
- r03, the toe. It is one shared grade curve after the tonemapper (`packs/stavanger-1989/light/grade.json`, `LT1Street.Grade`, a 32³ user lookup table): deepest near L20, and none at black or white. **It is not committed: the grade is shared, and it waits for the coordinator's yes.**

Sheets:
- `r03-overcast.jpg` and `r03-lowsun.jpg`: rows eye, street stop, 12 m, high; columns p3 P | r01 P | r02 P | r03a P | r03 P | r03 Pc.
- `r03-close-glass.jpg`: r02 | r03a | r03, then refs 10 and 04.
- `r03-rock-toe.jpg`: t02 grey water, overcast and low sun, before and after the toe.

    STREET_ROW="107:cache/street/gen/107h:cache/street/bake/107z4/out-r02 108:cache/street/gen/108u:cache/street/bake/108u/out-r02 109:cache/street/gen/109u:cache/street/bake/109u/out-r02" python3 tools/unity_lock.py run -- bash blender/parts/street/run/render.sh row r03 eye,street,raised,high P,Pc overcast,lowsun

Cost:
- Triangles are unchanged (near/street/city): 107 24,590/5,459/705; 108 24,832/7,792/778; 109 53,230/9,452/748.
- A row of 50 of 109, with the room and the toe: street 4.5, raised 4.7 and along 5.3 ms (r02 4.3, 4.6 and 4.8); near3 5.2 ms (5.4). Along's batches spread from 4.6 to 5.3 ms. See `cache/street/renders/t06/timing.md`.
- Pages: 21.3, 85.3 and 85.3 MB, one 4 MB ground sky map, and the toe's 0.26 MB lookup table.
