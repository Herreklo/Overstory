# The row: 107, 108 and 109 together, the window board inside the glass (r07)

- Bad: 108's own near view at 4.4 m is unchanged from r06, to 0.00 L in both lights, so r06's first bad still stands (`r07-close-glass.jpg`):
  - the main floor's lower sashes stay at L13–18;
  - the room's furniture, which r05 showed, is still lost.

  The board lies under any eye below the window's foot. Its top is 45 mm over the opening's foot, under the lowest glass at about 85 mm, and it runs 168 mm into the room, so from below the frame and the sash's rail hide it. That covers the near view and every street stop. I told the coordinator it would show from the street as a lit lip at the glass's foot. That was wrong.
- Bad: nothing changes at the street stop either, so the dark main floor reads there as it did in r06.
- Bad: the board takes only the sky through the window, never direct sun, so in low sun it has no sun patch. The room behind it ignores direct sun too.
- Limits:
  - 107 is not rebuilt (the rock reads its cache), so it has no board;
  - a house has one board, from the window making most of its openings share;
  - the board's depth and paint are estimates, and versions.json says so. No measured board was found, and the town's interior colours are not documented.
- Holds: from 12 m and from high, each lower pane now has a light foot where it was dark (`r07-board.jpg`). Medians of the changed boxes on 108 alone:

  | View | Overcast | Low sun |
  |---|---|---|
  | 12 m | 56.0–57.5 (r06 29.5–33) | 68.5–69.0 (r06 22–34) |
  | High | 57.4–59.0 (r06 27–38) | 68.6–69.7 (r06 16–44) |

  - The room around the board is L21–24 in overcast and 14–20 in low sun; the wall is 71.4 and 84.4.
  - So the board is lighter than the room and darker than the wall it sits in: light on painted wood, not a glow.
  - Down a column at 12 m it runs from 58.7 near the glass to 54.0 at its nose in overcast, and from 71.6 to 67.1 in low sun.
- Holds: the board needed a fix at the mark's foot.
  - Below the board's top only the mark from afar draws (the true glass starts above it), and it drew the opening's foot as the dark room. Under a lit board, that read at 12 m as a dark, stepped gap.
  - The foot now takes the board's light at the glass, but only where the board shows over at least the foot's height, which happens from 12 m up. Where the board shows less, as for a low window seen from the street, the foot is left as it was.
  - Before this gate, the fix changed 99 px of the street stop by 38–55 L. With the gate, the street stop matches r06.
- Holds: the street stop is the same as r06 to 0.00 L, in both lights, in P and Pc. The row's eye view changes in 3 px: a true sliver of board at the foot of one of 109's ground-floor windows, which sits below eye height.
- Holds: the sheers, the glass, the flash's band, the mark and the threshold are r06's.
- Holds: no pop. On 108's walk from its eye view to its street stop (`r07-walk.jpg`), all 120 frames match r06's to 0.00 L, so the largest frame step stays 1.03× its neighbours'.

How it is made:
- **versions.json.** Each window version has a `board`: reachMm 90 (86 for one-light), noseMm 12 (10), and its paint from paints.json (trim_white_linseed, or trim_white for one-light). It is planed pine laid at the frame's inner foot, level with the frame's clear opening, running reachMm past the frame's inner face, with its front edge rounded over noseMm. What stands on it is a household's, so it is absent unless a fact puts it there.
- **house.py.** `board_digest` writes house.json `glass.board`: the board's top over the opening's foot (frameMm - coverMm), its nose behind the glass (the frame's depth behind the glass plus reachMm), the nose's radius, and the paint as linear sRGB.
- **LT1Street.** Sets `_Board` and `_BoardPaint` on the glass. A house.json from before r07 has no board.
- **OS_Glass, `RoomDay`.**
  - The board is a plane level with the frame's clear opening, from the glass to its nose, within the opening's width.
  - It is lit as the room is: the window above it (the window's form factor at the board) times what it sees through that window, plus the room's bounce. So it is lightest at the glass and dims as the window fills less of its sky.
  - Over its last noseMm the nose turns away from the window.
  - Where the eye meets the board first, the sheers are hidden.
- **Builds:** `cache/street/gen/108g` and `109g`. Only `glass.board` differs from 108f and 109f.

Sheets:
- `r07-overcast.jpg` and `r07-lowsun.jpg`: rows eye, street stop, 12 m, high; columns p3 P | r01 P | r06 P | r07 P | r06 Pc | r07 Pc.
- `r07-close-glass.jpg`: 108's near view at 4.4 m, r05 | r06 | r07, with overcast above and low sun below, then refs 10 (Normanns gate 27) and 04 (Tidegeilen 9).
- `r07-board.jpg`: 108 alone at 12 m (r06 | r07) and from high (r06 | r07), with overcast above and low sun below, then ref 04's window with its board under the plants. The crops are enlarged 3.3× and 2.25×.
- `r07-walk.jpg`: 12 frames of 108's walk from its eye view to its street stop. The 5 s clip is `cache/street/renders/r07w/walk-108.mp4`.

Controls: `r06h2` (108f) and `r05h2` (108m) were rendered with r07's shader. r06h2 matches r06h except for 2 px by 2 L in the eye view.

These renders carry r03's toe (`packs/stavanger-1989/light/grade.json`). It is still uncommitted and waits for Øystein's yes.

    STREET_ROW="107:cache/street/gen/107h:cache/street/bake/107z4/out-r02 108:cache/street/gen/108g:cache/street/bake/108u/out-r02 109:cache/street/gen/109g:cache/street/bake/109u/out-r02" python3 tools/unity_lock.py run -- bash blender/parts/street/run/render.sh row r07 eye,street,raised,high P,Pc overcast,lowsun
    STREET_GEN=cache/street/gen/108g STREET_PAINT=cache/street/bake/108u/out-r02 python3 tools/unity_lock.py run -- bash blender/parts/street/run/render.sh 108 r07h2 eye,street,raised,high P,Pc overcast,lowsun
    STREET_WALK=120 STREET_GEN=cache/street/gen/108g STREET_PAINT=cache/street/bake/108u/out-r02 python3 tools/unity_lock.py run -- bash blender/parts/street/run/render.sh 108 r07w eye,street Pc overcast

Cost: no new geometry and no new draws, only a few instructions and one branch in the glass's fragment.
- Triangles and draws are r06's.
- A row of 50 of 109 runs street 4.6, raised 4.8, along 5.3 and near3 5.7 ms (`cache/street/renders/t09/timing.md`). t08 ran 4.5, 4.6, 5.3 and 5.5.
- So r07 is 0 to 0.2 ms slower. Same-evening runs have differed by up to 0.3 ms (t07 against t07c), so the cost is at the edge of what these runs can tell apart.
- Pages are unchanged.
