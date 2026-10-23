# Taxonomy

What the world is made of, the words for it, and where each fact lives. This is the map. A session working on a material, a part, a kind or a change over time reads it after `NOW.md`, then opens the page or data file it points to. How each system works is on its own page.

## In short

- **TX1** A thing is a kind, made by a construction from parts, grown by a habit, or laid down by the land. Its parts are materials, each face in a finish. Anything whose kind keeps its own record is a thing, so things nest. Evidence: LF1, LF3, TR1.
- **TX2** A material family holds the rules; a member, one material from one source, holds every number. Reopens: a member needing a rule its family lacks.
- **TX3** A rock is a member: a knoll and a step can be the same phyllite. A living thing and what it yields are two linked members.
- **TX4** Parts, techniques, growth and coats ask for properties; constructions and records name members. Reopens: a choice properties can't state.
- **TX5** Six changes: slow, from the date (grows, grows on, worn, weathered); sudden, dated in the record (worked, struck). Evidence: D5.1.
- **TX6** A technique is how something is done in any world, and a new way is a new technique; a construction is how one world's builders did it, and in which years. Tool marks are history, from the recorded technique and the maker's skill. Evidence: LF3.
- **TX7** A world is a pack. Members, techniques, constructions and worlds are data; a pack never changes a rule. Evidence: `docs/town-system.md`.
- **TX8** Each fact has one home by its type. Where prose and data disagree, the data is right.

## The model

```
the system, true in any world
  material family  stone, wood, metal              its rules: properties, finishes, how each change acts
  technique        split along the bed, axed       how something is done: tools, marks, needs
  kind             stair, wall, natural-stone      what a thing is
  change           slow: grows, grows on, worn, weathered; sudden: worked, struck
a pack, one world or place and its years
  member           phyllite, Iddefjord granite     one material from one source, every number
  part             stone/step, coat/paint          a piece made from facts
  construction     block, dry-split                how its builders made a kind: techniques, members, sizes, years
a thing            one flight in the town: its record, and its life at a date; things nest
```

One flight in the gully, read through it. It is a stair (the kind) of `block` steps between dry-split walls (the constructions). Each step is a `stone/step` part of phyllite, a member of the stone family, split along the bed (the technique), so its faces are bed faces and split faces (the finish). Its record says who built it, how skilled they were and what was spent, and the six changes do the rest. Watch Knoll is the same phyllite with the natural finish, a `natural-stone` thing laid down by the land.

## The words

Each word has one meaning. Use it for nothing else. A home marked *(Q19)* or *(Q21)* is where the fact goes once that proposal lands.

| Word | Means | Never means | Home |
| --- | --- | --- | --- |
| thing | anything whose kind keeps its own record: a flight, a wall, a house, its shopfront (LF1), a tree | a part | its record |
| kind | what a thing is: stair, wall, natural-stone, house, tree, lamp | a rock or a species | `kinds/<kind>.json` |
| making | how a thing came to be: a construction, a habit, or the land | a change | the thing's record |
| construction | how a pack's builders made a kind: its techniques, members, parts, sizes and years, and what breaks in it (LF3) | a technique, or one event | the pack; today the stair's are in `kinds/stair.json` (`block`, `treadOnRiser`) and the walls' in `walling.json` |
| habit | how a species grows: the rules and numbers its timeline follows | a construction | `docs/trees.md`, the species' data |
| technique | how something is done, true in any world: its tools, the marks it leaves, the finish it gives, what it needs, how skill shows | a construction | `techniques/<technique>.json` *(Q21)* |
| part | a piece made by a judged mesh or function from facts; a living member brings its own (bark, twigs) | a whole thing | `packs/<pack>/parts/<path>.json`, code in `blender/parts/` |
| material family | materials that change by the same rules: stone, wood, metal | a part family or a shader family | `families/<family>.json` *(Q19)* |
| member | one material from one source, as a pack has it: phyllite, Iddefjord granite, slow-grown pine | a variant inside a member | `packs/<pack>/materials/<member>.json` *(Q19; today `slate.json`, `granite.json`)* |
| finish | the class of face a technique leaves: natural, rough, split, hewn, dressed, sawn for stone; sawn and planed for wood; crown and plate for window glass | a technique | its family |
| property | what a member has that others ask for: how it breaks (in slabs or in blocks), its chemistry (acid or lime) | a number | its family lists them; the member states them |
| link | `yields`, a living member and what it gives (a spruce and its boards); `madeOf`, a mix and what it is mixed from (mortar of lime and sand) | a property | the member |
| skill, means | how well the maker did it, and the money spent, which buys a skilled hand, a better member and more care | a variant of a part | each making and work in the record *(Q21)* |
| change | one of the six ways a thing changes over time | a layer | its design page |
| layer | one entry of `schemas/layers.json`, a channel a change draws through (polish, lichen, moss) | a change, or the surface stack | `schemas/layers.json` |
| record | a thing's facts: made, keepers, uses, works, events (LF1) | its look | `fixtures/`, later the engine; the schema today has `keepers`, `care`, `use` and `events`, with works as events |
| pack | a world or a place and its years | code | `packs/<pack>/` |

The material families are stone, binder, earth, wood, metal, glass, ceramic, coat and water, and the living ones broadleaf and conifer trees, ground cover and surface growth. Their members and state are in `docs/systems.md`.

Three things are called families, so write the full name each time. A material family is stone or wood. A shader family (`stone`, `street`, `tree`) is what draws it. A part family is a part path's first segments, such as `stone` or `window` (`schemas/naming.md`). The seven surface layers of `docs/foundations.md` are the surface stack, a surface's drawing order. "Working" is being retired, since it means a construction in some places and a finish or a technique in others (Q19).

## Where does it go

These questions place anything new. Ask them before building it; something they don't settle is raised first.

| Question | The test | Example |
| --- | --- | --- |
| thing or part? | Its kind keeps a record of its own (keepers, works): a thing. Otherwise a part. | a house and its shopfront are things (LF1); a window is a part of its house |
| kind, technique or construction? | True of the thing in every world: the kind. How something is done, in any world: a technique. How this world's builders did it, and when: a construction. | level beds are the wall kind's; splitting along the bed and dry-stone walling are techniques; the town's dry-split walls are a construction |
| family or member? | It changes by other rules: a family. The same rules with other numbers: a member. | stone and wood are families; phyllite and granite are members |
| member or finish? | Break it open. Other stuff, or a source that ages differently: a member. The same stuff worked another way: a finish. | Iddefjord and erratic granite are two members; split and dressed granite are one member in two finishes |
| property or name? | Another member could do the same job: ask for the property. | a step asks for a stone that breaks in slabs |
| slow or sudden? | Worked out from the date: slow. A dated act or event: sudden. | lichen is slow; a repair or a storm is sudden |

## The six changes

The slow changes are worked out from the record and the date, so a jump in time costs nothing to draw. The sudden ones are dated entries in the record, each resetting the clocks of what it touches (D5.1). Every family says how each acts on it, "none" included.

| Change | What it covers | Design page |
| --- | --- | --- |
| grows (slow) | a living thing's growth, age, seasons and death | `docs/trees.md`, `docs/nature.md` |
| grows on (slow) | lichen, moss, algae and weeds settling on a host, by its chemistry | `docs/nature.md` (Growth on surfaces) |
| worn (slow) | contact of use: feet, hands, boots, wheels, sitting | `docs/foundations.md` (The shared surface layers) |
| weathered (slow) | water and what it carries (wash, deposit, splash, rust runs, salt, soot); a material's own ageing (cracks, settling, fading, rust, rot); the weather's second clock (wet, frost, snow, leaves) | `docs/foundations.md` (The shared surface layers), `docs/upkeep.md` (damage) |
| worked (sudden) | what people do: build, cut, fell, prune, clean, patch, rework, renew, paint | `docs/upkeep.md` (UK2, UK5), `docs/living-fabric.md` (LF3) |
| struck (sudden) | what happens without anyone choosing it: a storm, a fire, a flood, a fall, a lorry at the gate, a pipe burst | `docs/living-fabric.md` (LF1, events), `docs/upkeep.md` (damage) |

## Where each fact lives

| Fact | Home | Example |
| --- | --- | --- |
| a number or a list | its data file; its meaning once, in its schema | phyllite's wear is `wearUmPerCentury` in its member file |
| a size | a piece's own making in its part's params; how a construction lays it in the construction; a standard many kinds share (openings, boards, storeys) in the pack's `metrics.json`. A kind holds rules, not sizes | a chamfer in `parts/stone/step.json`; a course height in the walls' construction |
| a rule and its reason | the design page for its system | a stone is rigid: BB3 in `docs/building-blocks.md` |
| the map and the words | this page | |
| state, and where code lives | `docs/systems.md` | |
| evidence, sources and measurements | `docs/research/`, `reviews/` | why this shape: `docs/research/taxonomy-precedents.md` |
| what happened and who said what | `docs/experiments.md`, git | a review round |
| how to do a job | its skill in `.claude/skills/` | what adding each thing costs: `game-lab-workflow` |
| what is open now | `NOW.md`, `docs/plan.md` | |

Read a system's In short first and its data next. Page bodies, research and reviews are opened to reopen a decision or to find a rule's reason. A design page names a field and leaves its value to the data.

Where the model goes deeper: stone's members, finishes and techniques in `docs/stone.md`; techniques over time, skill and means in `docs/living-fabric.md` (LF3); other worlds in `docs/foundations.md` (Packs and facts); how a work spreads in `docs/upkeep.md` (UK5). The data shape is proposal Q19, techniques and skill in the data Q21, and when each piece lands Q22 (`docs/proposals.md`).
