# The row: 107, 108 and 109 together, the glass as a dark eye (r04)

- Bad: it does not pass. At the street stop in overcast, each of 108's main-floor glazed openings measured whole has:
  - a median of L35–43 (r03 50–53) and a p90 of 73–74, against the wall's 73;
  - at the sheet's quarter scale, a median of 40–47 (r03 49–53).
- What keeps the window grey is its wood, not its glass:
  - The glass is dark: the bare panes are L16–18.5, and the top lights go from 52 to 15.
  - A cross window's sashes, post, transom and bars take 39% of the opening (house.json glassArea 0.61) and are as white as the wall. So no glass can bring the p90 to 65 or under, and at the sheet's scale the white blurs into the dark.
  - Refs 10 and 04 are big single panes of the 1950s and 60s, about 15% frame. 108's windows are the 1901 pattern, remade in 1985.
- Bad: at the sheet's scale, r04 reads as r03: grey windows with white crosses. The dark eyes show only at 1:1 (`r04-close-glass.jpg`).
- Bad: the sheer band is L54, against the 35–45 asked. In scene light it is about 0.27 of the white wall, as a white voile lit through the glass is. The tonemapper's shoulder lifts it on screen, as it lifted the pane before the toe.
- Holds:
  - everything else is unchanged within 0.1 L: 108's wall is L72.9, and 107 (boarded) and 109 (a warehouse) hang no sheers;
  - low sun: 108's windows go from L60–63 to 36–46, against the wall's 86.
- 107's corner is not a bug. Its front boards are lighter than its end wall in every round, measured between window and door and mid end wall: r01 66.6 against 41.6, r03 68.5 against 60.6. The critic's front 44 takes in the four boarded openings and the grime band. The turn shrank from 25 L to 8 L with r02's soft overcast; r01's own key had a 0.85 sun from the street side, shadow 0.35, which held the end wall at 42.

The change is data only: in glass.json, the curtains' share goes from 0.5 to 0.34 and the valance from 0.16 to 0.08. The curtains are drawn back to the sides under a short valance: pale bands along the jambs and the head, with the dark room between. Only 108 hangs them.

Sheets:
- `r04-overcast.jpg` and `r04-lowsun.jpg`: rows eye, street stop, 12 m, high; columns p3 P | r01 P | r02 P | r03 P | r04 P | r04 Pc.
- `r04-close-glass.jpg`: r03 | r04 at the street stop at 1:1, then refs 10 and 04.

These renders carry r03's toe (`packs/stavanger-1989/light/grade.json`). It is still uncommitted and waits for Øystein's yes.

    STREET_ROW="107:cache/street/gen/107h:cache/street/bake/107z4/out-r02 108:cache/street/gen/108u:cache/street/bake/108u/out-r02 109:cache/street/gen/109u:cache/street/bake/109u/out-r02" python3 tools/unity_lock.py run -- bash blender/parts/street/run/render.sh row r04 eye,street,raised,high P,Pc overcast,lowsun

Cost is unchanged from r03 (data only):
- Triangles (near/street/city): 107 24,590/5,459/705; 108 24,832/7,792/778; 109 53,230/9,452/748.
- A row of 50 of 109: street 4.5, raised 4.7, along 5.3 ms; near3 5.2 ms (`cache/street/renders/t06/timing.md`).
- Pages: 21.3, 85.3 and 85.3 MB, the 4 MB ground sky map, and the toe's 0.26 MB lookup table.
