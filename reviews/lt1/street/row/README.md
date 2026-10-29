# The row: 107, 108 and 109 together, the light step (l06)

- Bad: the panes read light grey at the street stop, lighter than ref 10's near-black ones, and lightest in 108's upper rows. The room behind them is now lit only through its window, so the open glass is darker (L45 to L37 at 108's ground floor). But the sheers fill about half of each pane at L56, and both faces of the glass mirror the overcast sky, about a tenth of a white wall. This reads like ref 04's lace-lit windows, not ref 10's dark ones. Not passed.
- Bad: overcast is soft and true now, but paler and flatter than the floor's. 109's red still reads brick-orange in low sun, as the floor's does. Its paint no longer adds to that: its age washes stay red-brown. The rest is the 18° sun's own tint (no sheen: L40 C30 h44).
- Fixed: the overcast key's hard band down 108's gable is gone (`l06-close-108-gable.jpg`). The ground darkens softly at each house's foot by the sky the house hides, so the houses stand on it from 12 m and above.
- Fixed: 109's peel no longer ladders down under its windows. The first lap under a sill takes the most water, so each board below peels less, and the peel stops two to five boards down (`l06-close-109.jpg`).

Sheets: `l06-overcast.jpg` and `l06-lowsun.jpg` have one row per view (eye, street stop at 20 m, 12 m, high). The columns are r01 P | l06 P | r01 Pc | l06 Pc. `l06-floor.jpg` is p3 and each house's accepted still, above the row at the street stop. The `l06-close-*` sheets are crops at the street stop.

r01 is the floor at the row's framing: each house's accepted paint, which carries the old light key, with `STREET_GROUNDSKY=0`. Only its glass room is the new one.

    STREET_ROW="107:cache/street/gen/107h:cache/street/bake/107z4/out-l06 108:cache/street/gen/108u:cache/street/bake/108u/out-l06 109:cache/street/gen/109u:cache/street/bake/109u/out-l06" python3 tools/unity_lock.py run -- bash blender/parts/street/run/render.sh row l06 eye,street,raised,high P,Pc overcast,lowsun

Cost:
- Triangles are unchanged: near/street/city 24,590/5,459/705 (107), 24,832/7,792/778 (108) and 53,230/9,452/748 (109).
- A row of 50 of 109, after the glass change: 4.3, 4.6 and 4.8 ms (street, raised, along); near3 5.4 ms (`cache/street/renders/t05/timing.md`). Before the change it was 4.5, 4.6, 5.2 and 5.5 ms.
- Pages: 21.3, 85.3 and 85.3 MB. The ground's sky map is one 1024² RGBA32 texture for the scene, 4 MB.
