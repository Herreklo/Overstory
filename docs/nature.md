# Nature

How the town's living ground is made: what grows where, and why; how it changes with the seasons, the years and what people do; how it stays alive on screen. Trees are one part of it (`docs/trees.md`); bushes, hedges, grass, moss, flowers, heath, shore plants, gardens, parks, verges, weeds in the paving, farmland and forest are the rest. Like a building, a place's nature has a history: what reads as history (a garden left to go wild since 1986, a field ploughed every spring, a path worn across a lawn) is a fact with a date; what claims nothing (which blade of grass leans which way) is seeded texture. The research behind this is in `docs/research/nature.md` and `docs/research/vegetation.md`.

## Why things grow where they do

Nothing is scattered. Every plant stands where the ground, the weather and people would put it, and the screen should let a viewer read that. Four things decide it, each a field over the land:

- **The ground:** how deep the soil is over the rock (bare on the knolls, deep in the hollows), how wet it is (water gathers down the gullies and in the hollows; ridges and rock run dry), and what it is (rock, earth, sand, made ground on the quays).
- **The light:** which way a slope faces and what shades it: houses (the sky map already knows), trees, the hill. North walls grow moss and ferns; south walls dry out.
- **The weather:** wind and salt from the sea. Exposed rock and the shore get low, tough, wind-shaped plants; sheltered yards grow soft ones. The coast's wind bends trees away from it.
- **People:** what the land is used for and how it is tended, each a dated fact: a garden (tended or not, since when), a lawn (mown how often), a park, a churchyard, a verge (cut by the council), pasture (grazed by what, since and until when), a field (what is sown, when it is ploughed and harvested), a lot left empty, a path walked (the ground-wear field). Use and neglect are among the clearest histories the screen can show.

From these, a place's plant community follows: coastal heath on thin, dry, windy ground that sheep have grazed for centuries; moss and lichen on rock; rushes and bog in the wet hollows; thrift and salt grass on the shore; lawn, lilac, currants, roses and an apple tree in a tended garden; nettles, cow parsley and young birch where a garden has been left; moss between the setts of a quiet lane and none in a busy one; fields, stone walls and hay on the farms.

## Growth on surfaces

What grows on the town's surfaces (lichen, moss, algae, grass in the joints, ferns in a wall) is one system with the
ground cover, and every surface uses it: stone first, then timber walls, roofs, bark and concrete. The causes are the
same everywhere and computed one way (`blender/generators/growth.py`): light (the sky map, which way a face looks),
damp (joints, inside corners, a wall's foot, drips, a north face), the years since the surface was bare (built,
relaid, cleaned, repainted), disturbance (feet, mowing, sweeping) and the surface's chemistry (acid or lime, rich or
poor in nutrients). The surface decides which species win, from the setting pack's lists:

- *Acid rock and stone* (granite, the town's slaty rock): crustose lichens, pale crusts spreading and merging over a
  century (map lichen about 0.7 mm a year); cushion moss (Grimmia) on wall tops; orange Xanthoria where birds perch.
- *Paving and setts*: silver moss and grass in the joints, which stand feet; bare along the walking line; chewing-gum
  lichen (Lecanora muralis) on quiet slabs.
- *Lime mortar*: wall-rue fern and Tortula moss, only where there is lime; a fern in a wall says how it was built.
- *Painted timber and render*: green algae low on north walls where rain splashes, streaks under drips; reset by the
  painter.
- *Roofs*: moss cushions on north slopes and under trees, lichen on old tiles.
- *Bark*: leafy and beard lichens in the clean, humid west-coast air (Hypogymnia, Usnea), Xanthoria on nutrient-rich
  bark, moss on the trunk's wet side and its foot, more with age.
- *Lawn, bog and heath* are not a layer on a surface but plant communities on the ground, placed by the fields below;
  they read the same causes (a shaded, wet lawn goes to moss).

Thin growth (crusts, films, mats) is drawn on the surface by one shared shader layer (`Growth.hlsl`), with the
species' pigments and rates set once for the town by the pack (`GrowthPack`); thick growth (grass tufts, moss
cushions, ferns, weeds) is nature's own parts, placed by the same potentials. Where and how long are each surface's
facts; what reads as history (lichen the size of eighty quiet years, a wall cleaned in 1975) is a fact with a date.

## Variety, with reason

Variety comes from the reasons, not from noise:

- **Gradients:** a community changes along its fields (drier up the knoll, wetter down the gully, wilder with each year since the mowing stopped), so a slope reads as a slope.
- **Edges:** the richest places are where two communities meet (the forest's edge, a lawn against a wall, the heath against a field); they get their own plants.
- **Clusters:** plants grow in patches, clones and drifts, from where a seed fell or a root spread, never in an even scatter.
- **Rarity:** a few accents, placed by reason and seed (a single rowan in red on the heath, foxgloves along a ditch in July), so the eye finds something.
- **Order against disorder:** what people planted stands in rows, hedges and avenues and is cut to shape; what came on its own is irregular. The difference tells who looks after a place.

## Time

Three clocks run over every place: the **season** (from the date and the species: leaf-out, flowering, fruit, autumn colour, leaf fall, snow); the **year's work** (mowing, grazing, ploughing, harvest, pruning, hedge-cutting), each a fact; and **succession** over the years when the work stops (a heath ungrazed goes to juniper and birch; a yard left grows over within a few summers; `docs/research/nature.md`). Like a tree's timeline, a place's ground is grown deterministically from its facts, and read at the date.

## Alive

The ground moves: grass in the wind's gusts, a hedge's leaves, the trees' crowns; leaves fall and drift in October. It is lived in: gulls on the ridges and quays, crows on the fields, sheep on the pasture, a cat on a wall. These carry no history and claim none: seeded and driven by the weather and the hour, never by chance.

## Every city brings its own

A setting pack brings its species, its plant communities and their rules, how its people tend their land (London's pollarded planes and clipped privet; New York's street trees in pits), and the parts that draw them. The fields (ground, light, weather, people) and the clocks are the same everywhere.

## Our style

Painterly realism, as in the rest of the town: plants as structured masses with intent, not soft balls or a uniform carpet; detail where the story is (the garden left to go wild, the worn path) and calm elsewhere; colour in the shade and the light; far ground reading as the colour of what grows on it, so fields, heath and forest make a patchwork from the map. Øystein, 30 October: "Nature HAS to ba as engaging as city life - every part of this world has to feel crafted - lived in, logical, stunning"; its summer is "colors from flowers during summer in gardes, parks, in the wild. lush trees, green fields, mountains in the distance" (references: `docs/references/nature/`).

## Order of work

Trees first, as the first system and its parts (`docs/trees.md`); then the ground cover (grass, moss, heath, flowers) and the fields that place everything; then bushes and hedges; then gardens, verges and weeds in the paving; then farmland and forest. Each part is made against its reference board and judged alone, then in the corner.
