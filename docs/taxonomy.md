# Taxonomy

What the world is made of, the words for it, and where each fact lives. This is the map. A session working on a material, a part, a kind or a change over time reads it after `NOW.md`, then opens the page or data file it points to. How each system works is on its own page; this page says how they fit together.

## In short

- **TX1** A thing is a kind, built by a construction from parts, grown by its species' habit, or laid down by the land; its pieces are materials in finishes. Evidence: SY1, LF1, LF3, TR1. Reopens: a thing made none of these ways.
- **TX2** A material family holds the rules (required fields, finishes, how each change acts); a member, one material from one source, holds every number. Evidence: the stone reads every number from data. Reopens: a member needing a rule its family lacks.
- **TX3** A rock is a member and a finish is how a face was got: a knoll and a step can be the same phyllite. A living thing and what it yields are two linked members.
- **TX4** Parts, growth and coats ask for properties; constructions and records name members. Evidence: growth by chemistry (`docs/nature.md`). Reopens: a choice properties can't state.
- **TX5** Five changes act on every thing: grows, grows on, worn, weathered, worked. Each family says how each acts on it, "none" included.
- **TX6** A new member, construction or pack is data only. Needing code means the family or part lacks something; fix it there.
- **TX7** Each fact has one home by its type; others link to it. Where prose and data disagree, the data is right and the prose is fixed.

## The model

```
the system, at the repo root, for any place
  material family  stone, wood, metal              its rules: fields, finishes, changes
  kind             stair, wall, natural-stone      what a thing is
  change           grows, grows on, worn, weathered, worked
the pack, one place and its years
  member           phyllite, Iddefjord granite     one material from one source, every number
  part             stone/step, coat/paint          a piece made from facts
  construction     block, dry-split-1874           how its builders made a kind
a thing            one flight in the town: its record, and its life at a date
```

One flight in the gully, read through it. It is a stair (the kind), built as `block` steps between walls laid `dry-split-1874` (the constructions). Each step is a `stone/step` part of phyllite, a member of the stone family. Its finish is split, so its top and bottom are bed faces and its front and ends split faces. Since then the feet in its record have worn it, and lichen and moss have grown on it as its place allows. Water has weathered it, and it was worked when a run was reset.

Watch Knoll is the same phyllite with the natural finish, a `natural-stone` thing laid down by the land. It takes the same lichen and the same rust bands, and it is worn only where the uses in its record walk it.

## The words

Each word has one meaning. Use it for nothing else.

| Word | Means | Never means | Home |
| --- | --- | --- | --- |
| kind | what a thing is: stair, wall, natural-stone, house, tree, lamp | a rock or a species | `kinds/<kind>.json` |
| construction | how a pack's builders made a kind: its parts, sizes, laying rules and what breaks in it (LF3) | a finish | the stair's in `kinds/stair.json` (`block`, `treadOnRiser`), the walls' in `walling.json` |
| habit | how a species grows: the rules and numbers its timeline follows | a construction | `docs/trees.md`, the species' data |
| part | a piece made by a judged mesh or function from facts; a living member brings its own (bark, twigs) | a whole thing | `packs/<pack>/parts/<path>.json`, code in `blender/parts/` |
| material family | materials that change in the same way: stone, wood, metal | a part family or a shader family | `materials/<family>.json` |
| member | one material from one source, as a pack has it: phyllite, Iddefjord granite, slow-grown pine | | `packs/<pack>/materials/<member>.json`, naming its family |
| finish | how a face was got: natural, rough, split, hewn, dressed, sawn for stone; sawn and planed for wood; cast and wrought for iron | a construction | its family |
| property | what a member has that others ask for: how it breaks (in slabs or in blocks), its chemistry (acid or lime) | a number | its family lists them; the member states them |
| change | one of the five ways a thing changes over time | a layer | its design page |
| layer | one entry of `schemas/layers.json`: a channel a change draws through on a surface (polish, lichen, moss) | a change | `schemas/layers.json` |
| record | a thing's facts: made, keepers, uses, works, events | its look | `fixtures/`, later the engine |
| pack | a place and its years | code | `packs/<pack>/` |

Three things are called families, so write the full name each time. A material family is stone or wood. A shader family (`stone`, `street`, `tree`) is what draws it. A part family is a part path's first segments, such as `stone` or `window` (`schemas/naming.md`).

The seven surface layers of `docs/foundations.md` are a surface's drawing order: pigment and grain, then the finish, then the changes. "Working" is being retired: it means a finish in some places and a construction in others, and Q19 lists where it is still used.

## Stone, worked through

The stone family holds the rules every member follows:
- its pieces are rigid, placed only by moving and turning (BB3);
- the `stone` shader family draws it, reading the place and history pages P0 and H1;
- worn polishes and hollows it; grows on gives lichen and moss; weathered brings water, stains and cracks; worked repairs it from the era's shelf (UK1);
- its finishes, and what each needs from a member;
- the numbers every member must state.

A member states all of its numbers. They are its pigment and ranges, with its variants by place, and its grain. Then come how it breaks, its hardness (`wearUmPerCentury`), how readily it cracks and how its corners break, and its porosity (how dark it goes wet, how long it holds water). Last are its chemistry, which decides what grows on it, and how it stains. A new member starts as a copy of its nearest sibling, with the numbers that differ changed.

The first pack's members:

| Member | What it is | Finishes here | Where in the town | In data |
| --- | --- | --- | --- | --- |
| phyllite | the bedrock: fine, laminated, banded grey-green to graphite-black, rusty in bands; breaks in slabs | natural (knolls, ledges), rough (rubble), split (steps, slabs, wall stones) | the old town's walls and steps; Watch Knoll | `slate.json` |
| mica schist | the bedrock too, alternating with phyllite over metres to centimetres; coarser, its mica visible | natural, split | the same ground | not yet |
| gneiss | banded and hard; breaks in blocks | natural (boulders), rough (walls, rough steps) | erratics on the heath and in Tower Wood; some walls | not yet |
| Iddefjord granite | light grey, massive and hard, brought in from about 1870 | dressed (kerbs, setts, quay stone, the better flights) | streets and quays | `granite.json` |
| erratic granite | boulders from the moraine, foreign to the bedrock | natural | the heath, Tower Wood; cleared ones in walls and cairns | not yet |

Larvikite and concrete join the same way when the pack needs them. The rock is from `docs/research/land-rock-and-water.md` and `docs/stone.md`.

**Finishes.** A finish is how a face was got. A part made in a finish has that finish's faces: a split step has bed faces and split faces (its face patches in `packs/stavanger-1989/parts/stone/step.json`). A work can change a face's finish, as when a face is re-dressed or rock is cut back for a lane; it resets the layers that face held. Each finish says what it needs from a member and what it leaves on the face:
- natural: any member, made by the land's generators and shaped by how the member breaks (phyllite plucks into thin stepped ledges, gneiss and granite into broad whalebacks);
- rough: any member, knocked to size, its faces as they broke;
- split: a member that breaks in slabs; flat beds, split faces of few facets (SN4);
- hewn: any member, squared with hammer and pick;
- dressed: a member that breaks in blocks; tooled faces and arrises;
- sawn: any member, from the year a construction names.

Each member and finish has its own face patches (SN6), made by the finish's rules with the member's numbers. So mica schist costs one member file, its patches for natural and split, and a variety sheet. The step part asks for a stone that breaks in slabs, so mica schist steps work the day the file lands.

## In the data

The shape Q19 moves the data to. The values are left out here, since they live in the data.

`materials/stone.json`, the family:

```json
{
  "family": "stone",
  "shaderFamily": "stone",
  "rigid": true,
  "properties": { "breaks": ["slabs", "blocks"], "chemistry": ["acid", "lime"] },
  "finishes": {
    "natural": {}, "rough": {}, "hewn": {}, "sawn": {},
    "split": { "needs": { "breaks": "slabs" } },
    "dressed": { "needs": { "breaks": "blocks" } }
  },
  "changes": {
    "grows": "none",
    "growsOn": ["lichen", "moss"],
    "worn": ["polish", "contact", "hollow"],
    "weathered": ["wash", "deposit", "splash", "carrier", "soot", "salt"],
    "worked": "upkeep"
  },
  "requires": ["wearUmPerCentury", "cracksPerMille", "breaks", "chemistry"]
}
```

`packs/stavanger-1989/materials/phyllite.json`, a member:

```json
{
  "material": "phyllite",
  "family": "stone",
  "source": "the town's bedrock",
  "breaks": "slabs",
  "chemistry": "acid",
  "finishes": ["natural", "rough", "split"],
  "wearUmPerCentury": "…",
  "cracksPerMille": "…"
}
```

A part asks for properties and names its finish:

```json
{ "part": "stone/step", "takes": { "family": "stone", "breaks": "slabs" }, "finish": "split" }
```

## The other families

| Material family | First members | How it differs |
| --- | --- | --- |
| binder | lime mortar, cement, concrete, asphalt | mortar is `madeOf` lime and sand |
| earth | soil, sand, gravel | |
| wood | by source: slow-grown pine, spruce | sawn, planed; joinery timber is a member of its own (`docs/research/house-fronts.md`) |
| metal | cast and wrought iron, zinc, steel | rusts on its own (weathered) |
| glass | window glass | its finishes by how it was made: crown, plate |
| ceramic | brick, roof tile | |
| coat | oil paint, limewash | no body of its own: applied by the `coat/paint` part (`madeAs: layer`) to a host |
| water | the sea, fresh water | the sea, a stream or the Basin is a thing of this family; a puddle or a wet face is the weathered change's water |
| tree | downy and silver birch, Norway spruce, rowan, Scots pine, sycamore | grown by habit (TR1); brings its own parts |
| ground cover | grass, heather, ferns and the weeds of the joints, as species | mixed into communities by place (heath, a verge; `docs/nature.md`) |
| surface growth | lichen, moss, algae, as species | drawn as layers, and as placed parts where a cushion is big enough |

Each family's finishes and properties are designed with the family. The state of every family and system, with where its code lives, is in `docs/systems.md`. Names in use with no member file yet: `pine-board`, `crown-glass`, `plate-glass` and `oil-paint` in the parts, and `rubble` in `docs/systems.md`.

## Links between things

Two links name a member:
- `yields`: a living member and the material it gives. A spruce yields spruce boards; felling is a worked change on the tree and the made fact of the boards.
- `madeOf`: a mixed member and what it is mixed from, such as mortar of lime and sand.

Growth and coats choose their hosts by properties, as parts do. Lichens and mosses follow the host's chemistry: crusts on acid rock, wall-rue and Tortula only where there is lime (`docs/nature.md`). A coat names the families it goes on. A new coat resets every layer whose reset names a new coat in `schemas/layers.json`, and the host's own ageing goes on under it: repainting a board leaves its rot.

## The five changes

| Change | What it covers | Design page | Code | What a family says |
| --- | --- | --- | --- | --- |
| grows | a living thing's growth, age, seasons and death | `docs/trees.md`, `docs/nature.md` | `blender/generators/tree_growth.py` | the habit's numbers each species states |
| grows on | lichen, moss, algae and weeds settling on a host | `docs/nature.md` (Growth on surfaces) | `blender/generators/growth.py`, `Growth.hlsl` | which growth it takes, by chemistry |
| worn | contact of use: feet, hands, boots, wheels, sitting | `docs/foundations.md` (The shared surface layers) | `blender/generators/wear.py`; layers polish and contact; the hollow | whether it hollows and polishes; members state how fast |
| weathered | water and what it carries (wash, deposit, splash, rust runs, salt, soot); its own ageing (cracks, settling, fading, rust, rot); the weather's second clock (wet, frost, snow, leaves) | `docs/foundations.md` (The shared surface layers), `docs/upkeep.md` (damage) | `blender/generators/water.py`, `WaterPack.cs`, `blender/generators/upkeep.py`; layers wash, deposit, splash, carrier, soot, salt | which of these act; members state porosity and rates |
| worked | what people do: build, cut, fell, prune, clean, patch, rework, renew, paint | `docs/upkeep.md` (UK2), `docs/living-fabric.md` (LF3) | `blender/generators/upkeep.py`; the record's works and events | which repairs its era used, and how each ages |

One file of code can serve two changes: `upkeep.py` draws both damage and repairs. A thing left alone (UK2's first way) is worn, weathered and grown on. Being worked resets what the work touches and nothing else (`docs/stone.md`, How time works). The pack's growth rates sit in `GrowthPack.cs` and the stone's history constants in `schemas/layers.json` today; Q19 moves both into the members.

## Adding something

| To add | Write | It then works with | Cost |
| --- | --- | --- | --- |
| a member (mica schist) | its file, copied from its nearest sibling with the numbers that differ; face patches for each finish it takes | every part that asks for its properties; every change | data and patches |
| a finish (sawn stone) | its entry in the family, and the rules that make its faces | every member that can take it | one function |
| a part (a kerb) | its definition and part function, asking for properties | every member that has them | one function |
| a kind (a quay wall) | its kind file and stages | existing parts, members and changes | its stages |
| a construction (a mortared wall) | its entry in the pack | the kind it builds | data |
| a material family (metal) | its file: properties, finishes, how each change acts, required numbers, shader family | everything above | the biggest step; every member after it is data |
| a change (soot) | its layers, its design page, and each family's answer | every thing | one system |
| a pack (London) | its members, constructions and part definitions | everything above | data; each system's foreign part proves it (`docs/foundations.md`, Packs and facts) |

## Where each fact lives

| Fact | Home | Example |
| --- | --- | --- |
| a number or a list | its data file; its meaning once, in its schema | phyllite's wear is `wearUmPerCentury` in its member file |
| a rule and its reason | the design page for its system | a stone is rigid: BB3 in `docs/building-blocks.md` |
| the map and the words | this page | |
| evidence, sources and measurements | `docs/research/`, `reviews/` | why this shape: `docs/research/taxonomy-precedents.md` |
| what happened and who said what | `docs/experiments.md`, git | a review round |
| how to do a job | its skill in `.claude/skills/` | making a part: `blender-generators` |
| what is open now | `NOW.md`, `docs/plan.md` | |

Read a system's In short first and its data next. Page bodies, research and reviews are opened to reopen a decision or to find a rule's reason. A design page names a field and leaves its value to the data.

The stone members are in `packs/stavanger-1989/materials/slate.json` (phyllite) and `granite.json` today, with no family file, and parts name members (`"materials": ["slate"]`). Proposal Q19 moves the data to this shape, and Q20 gives every fact one home (`docs/proposals.md`).
