# Taxonomy

What the world is made of, the words for it, and where each fact lives. This is the map. A session working on a material, a part, a kind or a change over time reads it after `NOW.md`, then opens the page or data file it points to. How each system works is on its own page; this page says how they fit together.

## In short

- **TX1** A thing is a kind, made by a construction from parts, grown by a habit, or laid down by the land. Its parts are materials, each face in a finish. Anything with its own history is a thing, so things nest. Evidence: LF1, LF3, TR1.
- **TX2** A material family holds the rules; a member, one material from one source, holds every number.
- **TX3** A rock is a member: a knoll and a step can be the same phyllite. A living thing and what it yields are two linked members.
- **TX4** Parts, techniques, growth and coats ask for properties; constructions and records name members.
- **TX5** Six changes: slow, from the date (grows, grows on, worn, weathered); sudden, dated in the record (worked, struck). Evidence: D5.1.
- **TX6** A technique is how something is done in any world, and a new way is a new technique; a construction is how one world's builders did it, and when. Tool marks are history: they come from the recorded technique and the maker's skill. Evidence: LF3.
- **TX7** A world is a pack built on other packs. Members, techniques, constructions and worlds are data; a pack never changes a rule. Evidence: `docs/town-system.md`.
- **TX8** Each fact has one home by its type. Where prose and data disagree, the data is right.
- **TX9** Where does it go places anything new; what it doesn't settle is raised before building.

## The model

```
the system, at the repo root, true in any world
  material family  stone, wood, metal              its rules: fields, finishes, changes
  technique        split along the bed, axed       how something is done: tools, marks, needs
  kind             stair, wall, natural-stone      what a thing is
  change           slow: grows, grows on, worn, weathered; sudden: worked, struck
a pack, one world or place and its years, built on other packs
  member           phyllite, Iddefjord granite     one material from one source, every number
  part             stone/step, coat/paint          a piece made from facts
  construction     block, dry-split-1874           how its builders made a kind: techniques, members, sizes, dates
a thing            one flight in the town: its record (who made it, how skilled, when), and its life at a date;
                   a thing can hold things (a house and its shopfront)
```

One flight in the gully, read through it. It is a stair (the kind), built as `block` steps between walls laid `dry-split-1874` (the constructions). Each step is a `stone/step` part of phyllite, a member of the stone family, split along its bed by hand (the technique). Its finish is split, so its top and bottom are bed faces and its front and ends split faces. Since then the feet in its record have worn it, and lichen and moss have grown on it as its place allows. Water has weathered it, and it was worked when a run was reset.

Watch Knoll is the same phyllite with the natural finish, a `natural-stone` thing laid down by the land. It takes the same lichen and the same rust bands, and it is worn only where the uses in its record walk it.

## The words

Each word has one meaning. Use it for nothing else.

| Word | Means | Never means | Home |
| --- | --- | --- | --- |
| thing | anything with its own history: a flight, a wall, a house, its shopfront, a tree | a part | its record |
| kind | what a thing is: stair, wall, natural-stone, house, tree, lamp | a rock or a species | `kinds/<kind>.json` |
| making | how a thing came to be: a construction, a habit, or the land | a change | the thing's `made` |
| technique | how something is done, true in any world: its tools, the marks it leaves, the finish it gives, what it needs from a member, how skill shows in it | a construction | `techniques/<technique>.json` |
| construction | how a pack's builders made a kind: its techniques, members, parts, sizes, laying rules and dates, and what breaks in it (LF3) | a technique | the stair's in `kinds/stair.json` (`block`, `treadOnRiser`), the walls' in `walling.json` |
| habit | how a species grows: the rules and numbers its timeline follows | a construction | `docs/trees.md`, the species' data |
| part | a piece made by a judged mesh or function from facts; a living member brings its own (bark, twigs) | a whole thing | `packs/<pack>/parts/<path>.json`, code in `blender/parts/` |
| material family | materials that change in the same way: stone, wood, metal | a part family or a shader family | `materials/<family>.json` |
| member | one material from one source, as a pack has it: phyllite, Iddefjord granite, slow-grown pine | | `packs/<pack>/materials/<member>.json`, naming its family |
| finish | the class of face a technique leaves: natural, rough, split, hewn, dressed, sawn for stone; sawn and planed for wood; cast and wrought for iron | a technique | its family |
| skill | how well the maker did it: a fact in the record (`made.by`), shown as each technique says | means (money), which buys the member and the technique | the record |
| property | what a member has that others ask for: how it breaks (in slabs or in blocks), its chemistry (acid or lime) | a number | its family lists them; the member states them |
| change | one of the six ways a thing changes over time | a layer | its design page |
| layer | one entry of `schemas/layers.json`: a channel a change draws through on a surface (polish, lichen, moss) | a change | `schemas/layers.json` |
| record | a thing's facts: made, keepers, uses, works, events | its look | `fixtures/`, later the engine |
| pack | a world or a place and its years; it can build on other packs | code | `packs/<pack>/` |

Three things are called families, so write the full name each time. A material family is stone or wood. A shader family (`stone`, `street`, `tree`) is what draws it. A part family is a part path's first segments, such as `stone` or `window` (`schemas/naming.md`).

The seven surface layers of `docs/foundations.md` are a surface's drawing order: pigment and grain, then the finish, then the changes. "Working" is being retired: it means a finish in some places and a construction in others, and Q19 lists where it is still used.

## Where does it go

These questions place anything new. Ask them before building it.

| Question | The test | Example |
| --- | --- | --- |
| thing or part? | It has its own history (its own works or keepers): a thing. Otherwise a part. | a shopfront refitted in 1972 is a thing in its house; a step is a part of its flight |
| kind, technique or construction? | True of the thing in every world: the kind. How something is done, in any world: a technique. How this world's builders did it, and when: a construction. | level beds are the wall kind's; splitting along the bed is a technique; dry-split walls of 1874 are a construction |
| family or member? | It changes by other rules: a family. The same rules with other numbers: a member. | stone and wood are families; phyllite and granite are members |
| member or finish? | Break it open. Other stuff, or a source that ages differently: a member. The same stuff worked another way: a finish. | Iddefjord and erratic granite are two members; split and dressed granite are one member in two finishes |
| property or name? | Another member could do the same job: ask for the property. | a step asks for a stone that breaks in slabs |
| slow or sudden? | Worked out from the date: slow. A dated act or event: sudden. | lichen is slow; a repair or a storm is sudden |

## Stone, worked through

The stone family holds the rules every member follows:
- its pieces are rigid, placed only by moving and turning (BB3);
- the `stone` shader family draws it, reading the place and history pages P0 and H1;
- worn polishes and hollows it; grows on gives lichen and moss; weathered brings water, stains and cracks; worked repairs it from the era's shelf (UK1); struck chips and breaks it;
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

**Finishes and techniques.** A finish is the class of face; a technique is how it was made. A part's geometry follows the finish: a split step has bed faces and split faces (its face patches in `packs/stavanger-1989/parts/stone/step.json`). Its marks follow the technique and the maker's skill, since tool marks date work and say who did it. A work can change a face's finish, as when a face is re-dressed or rock is cut back for a lane; it resets the layers that face held.

The finishes:
- natural: made by the land's generators, shaped by how the member breaks (phyllite plucks into thin stepped ledges, gneiss and granite into broad whalebacks);
- rough: knocked to size, its faces as they broke;
- split: parted along a bed or a line of wedges; split faces of few facets (SN4);
- hewn: squared with hammer and pick;
- dressed: tooled flat, with arrises;
- sawn: cut by a saw.

Some techniques for stone, each with the finish it gives and the marks it leaves:

| Technique | Gives | Needs | Marks |
| --- | --- | --- | --- |
| split along the bed by hand | split | a member that breaks in slabs | flat beds; split faces of few facets |
| flat wedges in cut slots | split | | long rectangular slots along the split edge |
| plug and feathers in drilled holes | split | | a row of round half-holes along the split edge |
| scrabbled | rough | | irregular projections knocked off |
| axed | dressed | a hard stone, such as granite | the axe's marks |
| boasted | dressed | | parallel lines, level, upright or slanting |
| frame saw | sawn | | the saw's lines |

Each member and technique has its own face patches (SN6), made by the technique's rules with the member's numbers. So mica schist costs one member file, its patches for the techniques it takes, and a variety sheet. The step part asks for a stone that breaks in slabs, so mica schist steps work the day the file lands.

**Techniques over time.** A technique is fixed once written; a new way of doing something is a new technique, and the old one stays. A world's technology is when each technique arrives, dated in the pack's timeline (frame-sawn granite from one year, cement from another). Builders then move from the old way to the new at their own pace: a construction names the years it was used, means and tradition decide who takes the new way first (LF3), and a maker works the way they learned. So a 1960s repair on an 1874 wall shows its own decade's technique beside the old one (UK1), and the town shows when each way of working reached it. Old and new stand side by side only where a work's reach puts them, by UK5's logic (`docs/upkeep.md`): never one window from another era without a cause in the record.

**Skill and means.** Every making and every work in the record says who did it, how skilled they were, and what money was spent (LF3: craft and means). Money buys a skilled hand, a better member and more care; an owner who builds his own shed brings his own skill. Each technique says how skill shows. For a wall it is the regularity, the bridged joints and a true line, and means shows as thickness, dressing and the stone's grade. For a board shed it would be how square and plumb it stands, how even its boards and nail lines run, and whether its roof is flashed.

Skill is an input, never a variant: the same parts and the same assembler make every shed. Most of it sets how the assembler places the pieces (square, plumb, the gaps, the spacing, which pieces it picks), once for every part; a little sets a part's own inputs (a cut end square or ragged). Two houses of the same parts differ because their facts differ, and a seed picks only texture.

Skill shows twice: in the form when the thing is made, and in how it ages. A badly flashed roof lets water in, so its boards rot sooner (weathered). Low skill is drawn as a maker's real mistakes, the same ones across the whole thing (out of square by one amount, a line of nails that wanders), never as noise, since marks from one cause are one shape (`docs/living-fabric.md`). The pieces are still placed only by moving and turning (BB3). A skilled repair on a poorly built shed shows both makers, and the junction is where the history reads (LF3).

## In the data

The shape Q19 moves the data to. The values are left out here, since they live in the data.

`materials/stone.json`, the family:

```json
{
  "family": "stone",
  "shaderFamily": "stone",
  "rigid": true,
  "properties": { "breaks": ["slabs", "blocks"], "chemistry": ["acid", "lime"] },
  "finishes": ["natural", "rough", "split", "hewn", "dressed", "sawn"],
  "changes": {
    "grows": "none",
    "growsOn": ["lichen", "moss"],
    "worn": ["polish", "contact", "hollow"],
    "weathered": ["wash", "deposit", "splash", "carrier", "soot", "salt"],
    "worked": "upkeep",
    "struck": "upkeep"
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
  "wearUmPerCentury": "…",
  "cracksPerMille": "…"
}
```

`techniques/split-along-bed.json`, a technique:

```json
{
  "technique": "split-along-bed",
  "family": "stone",
  "gives": "split",
  "needs": { "breaks": "slabs" },
  "tools": ["hammer", "wedge"],
  "marks": "flat beds; split faces of few facets",
  "skill": ["regularity", "a true line"]
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

## The six changes

The slow changes are worked out from the record and the date, so a jump in time costs nothing to draw. The sudden ones are dated entries in the record, each resetting the clocks of what it touches (D5.1).

| Change | What it covers | Design page | Code | What a family says |
| --- | --- | --- | --- | --- |
| grows (slow) | a living thing's growth, age, seasons and death | `docs/trees.md`, `docs/nature.md` | `blender/generators/tree_growth.py` | the habit's numbers each species states |
| grows on (slow) | lichen, moss, algae and weeds settling on a host | `docs/nature.md` (Growth on surfaces) | `blender/generators/growth.py`, `Growth.hlsl` | which growth it takes, by chemistry |
| worn (slow) | contact of use: feet, hands, boots, wheels, sitting | `docs/foundations.md` (The shared surface layers) | `blender/generators/wear.py`; layers polish and contact; the hollow | whether it hollows and polishes; members state how fast |
| weathered (slow) | water and what it carries (wash, deposit, splash, rust runs, salt, soot); its own ageing (cracks, settling, fading, rust, rot); the weather's second clock (wet, frost, snow, leaves) | `docs/foundations.md` (The shared surface layers), `docs/upkeep.md` (damage) | `blender/generators/water.py`, `WaterPack.cs`, `blender/generators/upkeep.py`; layers wash, deposit, splash, carrier, soot, salt | which of these act; members state porosity and rates |
| worked (sudden) | what people do: build, cut, fell, prune, clean, patch, rework, renew, paint | `docs/upkeep.md` (UK2, UK5), `docs/living-fabric.md` (LF3) | `blender/generators/upkeep.py`; the record's works | which repairs its era used, and how each ages |
| struck (sudden) | what happens to it without anyone choosing it: a storm, a fire, a flood, a fall, a lorry at the gate, a pipe burst | `docs/living-fabric.md` (LF1, events), `docs/upkeep.md` (damage) | the record's events | how it breaks, and what is left |

One file of code can serve two changes: `upkeep.py` draws both damage and repairs. A thing left alone (UK2's first way) is worn, weathered and grown on. Being worked resets what the work touches and nothing else (`docs/stone.md`, How time works). The pack's growth rates sit in `GrowthPack.cs` and the stone's history constants in `schemas/layers.json` today; Q19 moves both into the members.

## Adding something

| To add | Write | It then works with | Cost |
| --- | --- | --- | --- |
| a member (mica schist) | its file, copied from its nearest sibling with the numbers that differ; face patches for each finish it takes | every part that asks for its properties; every change | data and patches |
| a technique (plug and feathers) | its file: tools, marks, the finish it gives, what it needs, how skill shows; face patches per member that can take it | every construction that names it, in any world | data and patches |
| a finish (sawn stone) | its entry in the family, and the rules that make its faces | every technique that gives it | one function |
| a part (a kerb) | its definition and part function, asking for properties | every member that has them | one function |
| a kind (a quay wall) | its kind file and stages | existing parts, members and changes | its stages |
| a construction (a mortared wall) | its entry in the pack | the kind it builds | data |
| a material family (metal) | its file: properties, finishes, how each change acts, required numbers, shader family | everything above | the biggest step; every member after it is data |
| a change (soot) | its layers, its design page, and each family's answer | every thing | one system |
| a world (a medieval town, London) | a pack built on the library: its sources, constructions with their dates, land and records | everything above | data; each system's foreign part proves it (`docs/foundations.md`, Packs and facts) |

## Other worlds

A world is a pack, and a pack builds on other packs (`buildsOn`). The library pack holds what is real anywhere: real rocks, woods and metals as members, and real techniques. A world adds only its own: where its stone comes from, which techniques its builders knew and from when, its constructions, its land and its records. Its look is the drawing's, kept apart from all of this (Q18).

Granite in a medieval world:
1. The pack builds on the library and takes its granite. If its granite comes from a source that looks or ages differently, it adds a member copied from the library's.
2. Its constructions name what its masons used and when: granite split with wedges and dressed with the axe, walls of rubble in lime mortar with dressed corners, no sawn granite.
3. Its things use the system's kinds. A kind it lacks, such as a spiral stair or a vault, is added to the system once, and every world has it.
4. Its records say who built each thing, how skilled they were, and when. The six changes then give it centuries of lichen and hollowed steps.

None of this needs code. The first town needs the same, since its cathedral of about 1125 and the monastery ruin on Gull Island are medieval stone (`docs/town-plan.md`).

An invented world works the same way. An invented stone or technique is a member or technique with its own numbers. A pack never changes a rule (`docs/town-system.md`). If an invention needs one, such as a stone that heals, the rule joins the system once, as a family or a change, and every world can use it.

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

The stone members are in `packs/stavanger-1989/materials/slate.json` (phyllite) and `granite.json` today, with no family file, and parts name members (`"materials": ["slate"]`). Proposal Q19 moves the data to this shape, Q20 gives every fact one home, Q21 adds techniques, the library pack and histories longer than 256 years, and Q22 places each piece at the step that needs it (`docs/proposals.md`).
