# Painted finish, round p2 (way P), step 1

Step 1 is the critic's one change (`../p1/critic.md`): three unequal value planes, and one failed-paint shape that follows the water.

**Stills:**
- `step1-street.png`: the street stop, overcast and low sun, beside 09, Hopper and Stålenhag.
- `step1-eye.jpg`: eye level, overcast and low sun, beside Stålenhag and 09.
- `step1-tongue.png`: the tongue close up, at the street stop (×4) and at eye level.

## Bad first

1. **The upper wall is still clean white.** At the street stop the tongue is the only story mark below the sill. Above the sill, only the eave band, the battens' darks and the window carry the wall.
2. **The near brushwork still reads as blocks** at eye level. It is step 2's.
3. **Left for step 2:**
   - The plinth's dark band and wavy light top, and the drip board's bright top, are now the loudest horizontal lines at the foot.
   - The laps still step and alias at the street stop.
   - The roof is the loudest thing from the street.
4. **The peel reads clearly up close.** At the street stop it is a few light flecks inside the wash.

## What changed

- **One gradient down the whole wall,** the same round the corner:
  - light under a soft eave band, darkening steadily to the foot (`wall`: +8 to −26 L*, power 1.15);
  - the foot band, the trims' foot zone and the corner board's foot are gone.
- **The window is the dark shape.** Boarding `c` keeps b's battens on a dark sheet (L 32).
- **The tongue** (`tongue`, `paint.py` `tongue()`). It runs board by board off the leaking horn to the plinth, with a shorter one off the dry horn and a narrow one down beside the casing from the head.
  - **The wash** is soft and darker. On each board it spreads toward the drip edge, and the board below takes it a little narrower, with its own offset, so it breaks at every lap.
  - **The peel** is hard and lighter: dry fibre (bare L 76) that takes only 12 % of the wash. Its strips run along the grain up from each board's drip edge, their tops torn in steps.
  - It is highest at the butt joint under the leaking horn (x 0.984).
  - The cladding carries no nails in the facts, so none are drawn.
- **The blobs are deleted.** So are the rim, the drags down the washes (they crossed the laps) and the old straight washes.
- **The peel's edge** is the shader's `fwidth` edge on a per-board signed distance. The strokes are gone by the street stop (`edge.fadeLod` [2, 3.4]), so far off the edge is the field's smooth contour, with no stair steps.

## Measured

Rendered L* at the street stop, overcast, with low sun in brackets:

| Region | L* |
| --- | --- |
| Wall, upper | 78 (87) |
| Wall, middle | 75 (85) |
| Wall, low | 68 (79) |
| Wall, foot | 60 (72) |
| Gable, at the same heights | 67, 64, 54 (49) |
| Window sheet | 36 (47) |
| Tongue's wash core | 49 against 64–67 |

At eye level, overcast: the wash is 46–48, the paint beside it 61 and the peel 64–67.

**Unchanged:**
- the mesh: 2,731 and 793 triangles;
- the textures: `hist-p2` R now holds the tongue's wash;
- P's lights and clay.

A still reproduces: `hist-a.png` and `geo.png` are byte-identical.
