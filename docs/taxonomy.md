# Taxonomy

What the world is made of, the words for it, and where each fact lives. This is the map. Read it before working on a material, a part, a kind or a change over time, then open the page or data file it points to. How each system works is on its own page; this page says how they fit together.

## In short

- **TX1** A thing is a kind (stair, outcrop, tree), built by a construction from parts; each part is a material in a finish. Five changes act on every thing. Evidence: SY1, LF1, LF3. Reopens: a thing that fits none.
- **TX2** Materials sit in material families. A family answers once; a member states only where it differs. One level; a member varies within its ranges, by place and seed. Evidence: Why this shape. Reopens: a member needing a value its family can't hold.
- **TX3** A rock is a member and how it was got is a finish, so a knoll and a step can be the same phyllite. A living thing and what it yields are two linked members.
- **TX4** Parts and constructions ask for properties (a stone that parts along its beds), never for named members. Reopens: a choice properties can't state.
- **TX5** Five changes: grows, grows on, worn, weathered, worked. One home each; every family answers all five, "none" included.
- **TX6** A new member, construction or pack is data only. Needing code means the family or part lacks something; fix it there.
- **TX7** Each fact has one home by its type; other places link to it. Where prose and data disagree, the data is right.

## The model

```
pack               a place and its years
  material family  stone, wood, metal ...          answers once for all its members
    member         phyllite, granite ...           states only where it differs
    finish         natural, rough, split, dressed  how the material was got
  part             a piece made from facts         stone/step, stone/wallstone
  construction     how an era built a kind         block steps, dry-laid
  kind             what a thing is                 stair, wall, outcrop, house, tree
thing              one stair in the town: its record (made, keepers, uses, works, events)
                   and its life at a date
changes            grows, grows on, worn, weathered, worked: act on every thing
```

One step in the gully, read through it. The stair is a kind. The town's mason built it as block steps, dry-laid: a construction. Each step is a `stone/step` part, of phyllite (a member of the stone family), split (its finish). Since then the feet in its record have worn it, and lichen and moss have grown on it as its place allows. Water has weathered it, and it was worked when a run was reset.

Watch Knoll is the same phyllite with the natural finish, as an outcrop kind. It takes the same lichen and the same rust bands, and no feet.

## The words

Each word has one meaning. Use it for nothing else.

| Word | Means | Never means | Home |
| --- | --- | --- | --- |
| kind | what a thing is: stair, wall, outcrop, house, tree, lamp | a rock or a species | `kinds/<kind>.json` |
| construction | how an era built a kind: its parts, sizes, laying rules and what breaks in it (LF3) | a finish | the pack's catalogue (`walling.json`, `stairs.json`) |
| part | a piece made by a judged mesh or a judged function from facts | a whole thing | `packs/<pack>/parts/<path>.json`, code in `blender/parts/` |
| material | what a part is made of | its shape or its use | its family and the pack's member |
| material family | materials that change in the same way: stone, wood, metal | a part family or a shader family | the family's file |
| member | one material of a family, as a pack has it: phyllite, Iddefjord granite | | `packs/<pack>/materials/` |
| finish | how a material was got or worked: natural, rough, split, dressed, sawn for stone; sawn and planed for wood; cast and wrought for iron | a construction | its family |
| change | one of the five ways a thing changes over time | one layer | its own page and code |
| layer | one channel a change draws through on a surface: polish, lichen, moss | a change | `schemas/layers.json` |
| record | a thing's facts: made, keepers, uses, works, events | its look | `fixtures/`, later the engine |
| pack | a place and its years | code | `packs/<pack>/` |

Three things are called families, so write the full name each time. A material family is stone or wood. A shader family (`stone`, `street`, `tree`) is what draws it. A part family is a part path's first segments, such as `stone` or `window` (`schemas/naming.md`). "Working" is not used: it meant a finish in some places and a construction in others.

## Stone, worked through

The stone family gives every member the same base:
- rigid pieces, placed only by moving and turning (BB3);
- the `stone` shader family, which reads the place and history pages P0 and H1;
- the layers polish, lichen and moss, and the story layers where a view's budget gives them;
- repairs from the era's shelf (UK1).

Each member states only its own numbers. They are its pigment and ranges, with its variants by place, and its grain. They say how it parts: along its beds if it is foliated, in blocks if it is massive. Then its hardness, how readily it cracks and how its corners break, and its porosity (how dark it goes wet, how long it holds water). Last, what grows on it and how it stains.

The first pack's members:

| Member | What it is | Finishes here | Where in the town | State |
| --- | --- | --- | --- | --- |
| phyllite | the bedrock: fine, laminated, banded grey-green to graphite-black, rusty in bands; parts along its beds | natural (knolls, ledges), split (steps, slabs, wall stones) | the old town's walls and steps; Watch Knoll | in data as `slate.json` |
| mica schist | the bedrock too, alternating with phyllite over metres to centimetres; coarser, its mica visible | natural, split | the same ground | research only (`docs/research/land-rock-and-water.md`) |
| gneiss | darker, banded and hard; breaks in blocks | natural (boulders), rough (walls, rough steps) | erratics on the heath and in Tower Wood; some walls | research only |
| granite | Iddefjord granite: light grey, massive, hard, brought in from about 1870 | dressed (kerbs, setts, quay stone, the better flights), natural (boulders) | streets and quays | in data as `granite.json` |

Larvikite and concrete join the same way when the pack needs them.

**Finishes.** A finish belongs to the family. It says what it needs from a member and what it leaves on the face:
- natural: any member, made by the land's generators, shaped by how the member parts (phyllite plucks into thin stepped ledges, gneiss and granite into broad whalebacks);
- rough: any member, knocked to size, its faces as they broke;
- split: a member that parts along its beds; flat beds, split faces of few facets (SN4);
- dressed: a massive member; tooled faces and arrises;
- sawn: any member, from the year a construction names.

Each member and finish has its own face patches (SN6), made by the finish's rules with the member's numbers. So mica schist costs one member file, its patches for natural and split, and a variety sheet. The step part asks for a stone that parts along its beds, so mica schist steps work the day the file lands.

## The other families

| Material family | First members | State |
| --- | --- | --- |
| stone | above | phyllite and granite built |
| binder | lime mortar, cement, concrete, asphalt | cement built; the rest planned |
| earth | soil, sand, gravel | joint soil built; ground planned |
| wood | the timber of the houses, fences and quays | planned, with the houses |
| metal | cast and wrought iron, zinc, steel | planned |
| glass | window glass by era | planned, with the houses |
| ceramic | brick, roof tile | planned |
| coat | paint, limewash: a coat on a host, with no body of its own (`madeAs: layer`) | planned |
| water | the sea, fresh water | planned |
| tree | downy and silver birch, Norway spruce, rowan, Scots pine, sycamore | birch built |
| ground cover | grass, heath, ferns, weeds | designed (`docs/nature.md`) |
| surface growth | lichen, moss, algae | lichen and moss built |

The state of every system, with where its code lives, is in `docs/systems.md`. Each family's finishes are designed with the family.

## Links between things

Four links join members. Each is a field naming the other member.
- `yields`: a living member and the material it gives. A spruce yields spruce boards; felling is a worked change on the tree and the made fact of the boards.
- `growsOn`: a surface growth on a host, such as lichen on phyllite or on birch bark. The host's answer says how readily.
- `coats`: a coat on a host, such as paint on boards, iron or render. Each keeps its own clock, so a new coat resets the paint's fading and leaves the wood's rot under it.
- `madeOf`: a mixed member and what it is mixed from, such as mortar of lime and sand.

## The five changes

| Change | What it covers | Home | What a material answers |
| --- | --- | --- | --- |
| grows | a living thing's growth, age, seasons and death | `docs/trees.md`, `docs/nature.md` | its habit and its seasons |
| grows on | lichen, moss, algae and weeds settling on a host | `blender/generators/growth.py`, `Growth.hlsl`; layers lichen and moss | how readily each grows on it; the species' rates are the pack's (`GrowthPack.cs`) |
| worn | contact of use: feet, hands, boots, wheels, sitting | `blender/generators/wear.py`; layers polish and contact; the hollow | how fast it wears, and whether it polishes |
| weathered | water and what it carries (wash, deposit, splash, rust runs, salt, soot); its own ageing (cracks, settling, fading, rust, rot); the weather's second clock (wet, frost, snow, leaves) | `blender/generators/water.py`, `WaterPack.cs`, `blender/generators/upkeep.py`; the layers from wash to salt | its porosity, how dark it goes wet, how it cracks, stains and ages on its own |
| worked | what people do: build, cut, fell, prune, clean, patch, rework, renew, paint | `docs/upkeep.md` (UK2), `docs/living-fabric.md` (LF3); the record's works and events | which repairs its era used, and how each ages |

Left alone, a thing is worn, weathered and grown on. Being worked resets what the work touches and nothing else (`docs/stone.md`, How time works).

## Adding something

| To add | Write | It then works with | Cost |
| --- | --- | --- | --- |
| a member (mica schist) | its file, copied from its nearest sibling, changing only the numbers that differ; face patches for each finish it takes | every part that asks for its properties; every change | data and patches |
| a finish (sawn stone) | its entry in the family, and the rules that make its faces | every member that can take it | one function |
| a part (a kerb) | its definition and part function, asking for properties | every member that has them | one function |
| a kind (a quay wall) | its kind file and stages | existing parts, members and changes | its stages |
| a construction (a mortared wall) | its entry in the pack's catalogue | the kind it builds | data |
| a material family (metal) | its file answering all five changes, its shader family and its finishes | everything above | the biggest step; every member after it is data |
| a change (soot) | its layer, its home, and each family's answer | every thing | one system |
| a pack (London) | its members, constructions and parts | everything above | data, and one foreign member per family as proof (`docs/foundations.md`) |

## Where each fact lives

| Fact | Home | Example |
| --- | --- | --- |
| a number or a list | its data file; its meaning once, in its schema | phyllite's wear is `wearUmPerCentury` in its member file |
| a rule and its reason | the design page for its system | a stone is rigid: BB3 in `docs/building-blocks.md` |
| the map and the words | this page | |
| evidence, sources and measurements | `docs/research/`, `reviews/` | a stair's frame times |
| what happened and who said what | `docs/experiments.md`, git | a review round |
| how to do a job | its skill in `.claude/skills/` | making a part: `blender-generators` |
| what is open now | `NOW.md`, `docs/plan.md` | |

A session reads `CLAUDE.md`, `NOW.md` and this page, then the In short of its system's page, then the data. Page bodies, research and reviews are opened to reopen a decision or to find a rule's reason. A design page names a field and leaves its value to the data.

Today the stone members are `packs/stavanger-1989/materials/slate.json` (phyllite, split) and `granite.json`, with no family file. Parts name members (`"materials": ["slate"]`), and `walling.json` calls its constructions workings. Proposal Q19 moves the data to this shape, and Q20 gives every fact one home (`docs/proposals.md`).

## Why this shape

- RimWorld defines a building once and lets it be made of any "stuff" in the categories it accepts (stony, woody, metallic), and the chosen stuff changes the result (TX4).
- Dwarf Fortress builds each stone from a shared stone template and places it by geological layer. A tree's wood is a material in the tree's own entry, so felling it gives logs "made of this material" (TX2, TX3).
- Unity's Material Variants inherit from a parent material and change only what differs: the same rule in our own engine (TX2).
- Substance 3D Painter's edge wear is worked out from the shape (curvature, occlusion), so one generator serves every material (TX5).
- Anthropic's guidance for Claude models is to keep always-read files light, load detail when it is needed, and remove repeated or conflicting instructions (TX7).

## Sources

- RimWorld Wiki, [Stuff](https://rimworldwiki.com/wiki/Stuff)
- Dwarf Fortress Wiki, [Inorganic material definition token](https://www.dwarffortresswiki.org/index.php/v0.34:Inorganic_material_definition_token) and [Plant token](https://dwarffortresswiki.org/index.php/Plant_token)
- Unity Manual, [Material Variant inheritance](https://docs.unity3d.com/Manual/materialvariant-tasks.html)
- Adobe, [Metal Edge Wear generator](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/effects/generators/metal-edge-wear)
- Anthropic, [The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)
- NGU on Stavanger's bedrock, as cited in `docs/research/land-rock-and-water.md`
