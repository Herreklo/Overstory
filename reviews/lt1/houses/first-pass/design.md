# The walked corner's houses: design (first pass)

**In short.** A house is assembled from its facts by fitted parts; the pack's records give every value that depends on era, place or material. Its coats are walked from its dated events by the pack's care rule, and the shader ages them on the date. Nothing reads as history unless a fact put it there. The research behind it is in `research-subject.md` (the subject) and `research-craft.md` (the craft).

## The parts

All are in `blender/parts/house/`; `house.build` chooses, fits and places them, and `tools/houses.py` writes and bakes them.

| Part | Kind | Driven by |
| --- | --- | --- |
| Cladding: courses, boards, gable halves (`carpentry.clad`, `gable_half`, `story_pole`) | fitted | the wall's frame and length, its storeys and gable (plan); the era's working (single- or double-rebated, exposure, board lengths); the seed (each course's width, joints) |
| Trims: corner boards, drip board, casings, reveals | fitted | the era's working; casings are lost where `windows_replaced` put in husmor windows |
| Windows and boarding (`windows.window`, `glass`, `boarded`) | fitted | the era's window, or the year's (`windowsByYear`) after `windows_replaced`; boards nailed over them while `boarded` and before `unboarded` |
| Roof: covering, ridge, soffits, fascia, gutter, bargeboards, rafter tails, chimney | fitted | the house's span, length, eave and pitch; the era's eaves, verge, cover and chimney |
| Plinth (`plinth.plinth`) | fitted | the ground under the wall (carved terrain), from below it to the sill; laid by the town's mason (`tools/r2b_wall.lay`), each fieldstone placed and turned, never bent |
| Coats (`coats.coats`) | rule | `built`, `wealth`, and the events `repainted`, `restored`, `windows_replaced`, `neglected`, `boarded`, `unboarded`; the period's colours drawn by the seed |

## What is data

- `packs/stavanger-1989/timber.json`: each era's working (cladding, corners, drip board, casings, eaves, verge, openings, roof, chimney, plinth), the windows and when each came in, lost trims, boarding. A missing key is an error.
- `packs/stavanger-1989/paint.json`: the colours (NCS and sRGB), the colours each period chose for each part, the paint system by year, the care rule (repaint interval from wealth, its jitter), and the weather's exposure factors (south, the wall's foot, the lap edge).
- `packs/stavanger-1989/materials/*.json`: how each paint ages (chalk, gloss, peel), the pine bare and weathered, the roof coverings new and old, the fieldstone, mortar (and how much light a joint sees), render and glass, and each material's water profile for the town's water layer.

Code holds only rules true everywhere: exposure runs a coat's years faster; it chalks toward a flat value and loses gloss; past its onset it flakes along the grain, showing the coat under it and then the wood; marks fade to their mean with distance (`OS_Near`); water darkens and glazes by the material's profile (`Water.hlsl`). The shade is the town's (`StreetLooks.hlsl`), unchanged.

**Proof:** `variant/paint-red.json` with one new record (`materials/paint-slam.json`) paints the same three houses red in slam paint with white trims, with no code changed (`variant/red-sheet.png`).

## History on the front

- **Facts:** which windows are in which holes, the patched boards where a larger opening was made smaller, boarding, the coat's colour after a dated repaint or restoration.
- **Interpretations of facts:** a coat's age on the date, from the care rule walked over the events (a neglected or boarded house misses its repaints), drawn as chalk, lost gloss and flaking. The care rule's repaints show no year a player can read.
- **Non-semantic texture:** board widths, stone sizes, the colour drawn from the period's list, each piece's hair of difference. All are seeded and claim nothing.

## Open

- The street (8,000) and city (1,500) tiers are not built; only the near tier is (C 34,799, D 32,244, E 12,555 of 40,000).
- Not built: doors and C's bislag, D's lean-to (`extended` 1950), the pantile's wave, glass waviness, run-off streaks under sills.
- Not the houses' to fix: the lamps' bounce fill under C's eave (the lamps element) and the gable's blue in blue hour (the light).
