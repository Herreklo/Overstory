# Three stylings for the walked corner

27 October. The street camera in blue hour with sea fog, three ways that differ in how the world is drawn, not only in value plan. Each is designed from the geometry and id passes (`../passes/`), with no surface detail from our renders. Per direction: `-eighth.png` (values at one-eighth), `-key.png` (colour at a quarter, with its inks), `-detail.png` (half size, round the Landing). Made by `tools/style_dir.py street 1750-sea-fog` from [styles.json](../styles.json).

## Print: the corner as a colour woodcut

**Idea.** The corner printed from seven inks on fog-paper: the near world cut in deep blocks, each layer up the gully printing fewer inks the farther it lies, and the lamps the only warm block.

- **Values.** Mid key. The rock and near walls one deep ink (10); C the palest built block (68); the sky one graded ink, 38 to 66; the far town pale paper tints.
- **Surfaces.** Flat inks, one or two per mass, chosen by the light: no gradient inside a block, no texture. The sky is the one graded ink.
- **Edges.** Hard everywhere near, made by ink meeting ink, never a drawn outline. The white-line cuts are the only lines: the tread noses and copings, carved out where a wet edge faces the sky, and only within about 40 m.
- **Detail.** Detail comes from modelled form only: lap boards print as bands only near, the stair as a ladder of cuts. Lamps print as small stepped rings.
- **Air.** In steps, not a fade. Each layer up the gully prints one ink nearer the paper, so depth reads as stacked flats.
- **History.** Whole shapes in another ink. A board with a fresh coat prints paper-white, an old coat one ink down, and bare weathered pine the silver-grey wood ink. Repairs and neglect read as patches of whole boards, never as noise.
- **People.** Flat silhouettes in their clothes' own inks.
- **Real time.** One lit shader per surface kind maps the light to an ink sheet: a 64×8 texture per light, with rows by kind and columns by value, and band edges antialiased with `fwidth`. The cuts come from an edge channel that the generator writes into the vertices (noses, sills, copings). The stepped air is today's distance-by-height lookup, snapped, in the existing post pass. No albedo or normal maps, so it should cost less than today.
- **Other lights.** In drizzle, fewer inks and wet cuts brightest. In low sun, a gold block on lit faces and one violet shade ink.

## Silver: drawn only in light

**Idea.** A dark wet town drawn only in light: calm planes with no marks, and every edge the rain has wet catching the sky or a lamp as a thin line. The line is sharp where the edge is sharp and new, soft or broken where it is worn.

- **Values.** Low key, a nocturne. The planes sit at 7 to 42 and C is the lightest built plane. The sky runs 32 to 54. The lines lift 30 to 55 above their plane, and the lamps are the whites.
- **Surfaces.** Calm planes with a gentle gradation and no texture.
- **Edges.** The drawing is all edges, and every line is light: the sky reflected in a wet bevel, as bright as the sky the bevel turns the eye towards. Tread noses, copings, sills, eaves and the gable's verge shine. Stone joints and lap boards mostly do not, because their bevels face sideways or down. Silhouettes on the sky get a thin wet rim.
- **Detail.** Lines only. They thin and fade with distance (full within 12 m, gone by 75 m), so the far town is soft planes in the air.
- **Air.** A continuous pearl veil, lit warm over the gully's top.
- **History.** The age of an edge is drawn by its line:
  - A new board's edge is crisp and thin.
  - A worn one is soft and wide.
  - A failed board, a chipped nose or a missing slate breaks the line.
  - A repair is a run of crisp line inside a soft one.
- **People.** Rim lines and lamp-lit faces. Their silhouette and gait carry them, and colour is weak, so this is a risk at blue hour.
- **Real time.**
  - The generator writes each edge's bevel into a vertex channel: its direction, and a radius from age, about 1 mm new and 15 mm worn.
  - The shader draws a sky-reflection highlight across that bevel, at least 1 px wide (`fwidth`), fading with distance.
  - Silhouette rims come from one half-size depth and normal edge pass, about 0.3 ms.
  - There are no maps.
- **Other lights.** In drizzle, it is in its element, with every wet edge silver on grey. In low sun, lit edges gold and shade edges cool. The planes lift, so the lines matter less there.

## Two inks: the hour and the hand

**Idea.** The hour prints the town in two inks on paper, its sky's blue and its lamps' amber, and the white houses are left as paper. Only what people paint and keep shows its own colour, and that colour drains into the hour's inks as it is let go.

- **Values.** High key under an ink sky:
  - C is paper (90).
  - The fog is pale (76).
  - The sky is the deep field (32 to 52).
  - The rock and walls are dense overprint (12 to 20).
- **Surfaces.** Continuous tints of two inks with no texture. The darks are both inks overprinted, so they are rich and never grey.
- **Edges.** None are drawn. Shapes come from ink density alone, and the stair's noses are paper.
- **Detail.** Colour carries the detail. A painted thing that people keep (D's pantiles, a door, a coat, clothes) shows its own colour, and everything else is the hour's two inks.
- **Air.** The far town fades towards paper and the warm glow.
- **History.** Colour is upkeep. A fresh coat is full colour. A neglected one drains towards the hour's inks, board by board, by coat age. A repair shows as a patch of true colour in a drained wall.
- **People.** Their clothes are their own colour, so they are the most colourful things in any scene and recognisable across scenes.
- **Real time.**
  - Each material writes its lit value, its warmth (the share of warm light) and its kept weight (from the coat age in the houses buffer).
  - One full-screen pass maps (value, warmth) through a 64×16 two-ink table per light (about 0.2 ms) and blends in the material's own colour by its kept weight.
  - No maps.
- **Other lights.** The inks change with the hour:
  - drizzle: slate and rust;
  - low sun: violet and gold;
  - blue hour: ultramarine and amber.
