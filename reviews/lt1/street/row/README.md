# The row: 107, 108 and 109 together, the window painted from afar (r05)

- Bad: at the street stop in overcast, 108's upper floor measured whole is L36.5–40.7. Those panes look up about 8°, over the far shore's skyline, and take the sky in reflection (r03's Reflected), so the mark is right and the eye is grey. The main floor below is 17.6–20.1. From 12 m and high, the upper floor is dark too (23–36).
- Bad: the row's eye view is not unchanged from r04. 108 stands 18 to 24 m from it, so its windows take the mark there (L34–40, the grazing glass's Fresnel). 108's own near view, 4.4 m off, is unchanged: no pixel moves by more than 4 L against r04.
- Bad: 108 alone, at its own street stop (20 m, the stile about 4.5 px), sits inside the fade: medians 36–47 against r04's 44–56, a half-and-half still. In the row it stands where the street stop is meant to be and is past the fade.
- Bad: at the sheet's scale the high view is 39–45. At about 10 px a window, the reduction blurs the white casing into the opening. The street stop is 25–31 and 12 m is 30–37.
- Holds, at the street stop at 1:1 (`r05-close-glass.jpg`):
  - 108's main floor measured whole: medians 17.6–20.1 (r04 39–46), p90 56–60;
  - dark eyes in a white wall, with a thin, crisp light cross at the post and the transom, the top lights under the transom, and the sheers as soft bands at L61 (r04 61.8);
  - it reads as a cross window, never a single pane: the sashes and the bars go into the dark, and the cross stays at the version's own places;
  - low sun: 108's main floor goes from 39–48 to 20–22.
- Holds: the casing, the head with its pediment, and the sill are still true geometry and white. The wall is L73.0, and the glass in the mark is L15.8.
- Holds: no pop. Walking from 108's eye view to its street stop (120 frames, `r05-walk.jpg`), the largest frame step is 1.02× its neighbours'. The walk crosses both the near-to-street level change at 10 m and the mark's fade. The row's own walk is within 1.05×; there 108 carries the mark from its first frame.

How it is made:
- house.py lays one quad over each window's opening, 2 mm in front of the frame, at the near and street levels.
- Its two further UV layers carry the post's place, the transom's place, the stile and the narrowest band.
- OS_Glass (`_OS_MARK`) fades it in where the stile falls under 4 px across or up, over ±0.6 px. It leaves the post and transom open 1.5 px wide, never wider than the wood beneath, so the true window's wood shows through as the cross. It blends over the true window, writes no depth and casts no shadow.
- The values are glass.json `fromAfar`. A 40 mm stile falls under 4 px about 15 m off through an eye view's 52–55° lens, and about 21 m off at the street stop's 38°.
- A window of more than two sashes stops the build: the mark draws one post.
- bake.py leaves the marks out of the page.

Sheets:
- `r05-overcast.jpg` and `r05-lowsun.jpg`: rows eye, street stop, 12 m, high; columns p3 P | r01 P | r04 P | r05 P | r04 Pc | r05 Pc.
- `r05-close-glass.jpg`: r04 | r05 at the street stop at 1:1, then refs 10 and 04.
- `r05-walk.jpg`: 12 frames of 108's walk, from its eye view to its street stop. The 5 s clips are `cache/street/renders/r05h/walk-108.mp4` and `r05w/walk-row.mp4`.

These renders carry r03's toe (`packs/stavanger-1989/light/grade.json`). It is still uncommitted and waits for Øystein's yes.

    STREET_ROW="107:cache/street/gen/107h:cache/street/bake/107z4/out-r02 108:cache/street/gen/108m:cache/street/bake/108u/out-r02 109:cache/street/gen/109m:cache/street/bake/109u/out-r02" python3 tools/unity_lock.py run -- bash blender/parts/street/run/render.sh row r05 eye,street,raised,high P,Pc overcast,lowsun
    STREET_WALK=120 STREET_GEN=cache/street/gen/108m STREET_PAINT=cache/street/bake/108u/out-r02 python3 tools/unity_lock.py run -- bash blender/parts/street/run/render.sh 108 r05h eye,street Pc,P overcast

Cost: one quad a window, one draw per house per level.
- Triangles (near/street/city): 108 24,868/7,828/778 (36 more at near and street); 109 53,248/9,470/748 (18 more); 107 unchanged at 24,590/5,459/705.
- A row of 50 of 109 with the mark against the same build without it, run the same evening:
  - street 5.0 against 4.7 ms; raised 5.0 against 5.1; along 5.8 against 5.7; near3 6.0 against 6.1;
  - within the batches' own spread of 0.3–0.5 ms;
  - 4 to 6 more draws in view;
  - `cache/street/renders/t07/timing.md` and `t07c`. The machine ran about 0.2 ms slower than for t06.
- Pages unchanged: 21.3, 85.3 and 85.3 MB.
