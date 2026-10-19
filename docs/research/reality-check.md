# Reality check

What is possible, for whom, and in what order. Every part of the plan is rated against what others have shipped and what this team can do: Øystein as designer and judge, with AI agents doing most of the building. Ambition is the default; this document decides the order of the bets, so the hard ones are tested early instead of discovered late.

## The ratings

- Proven: others have shipped it; we follow a known method.
- Doable: a clear method exists and fits our size.
- Hard: possible, but a big effort or a real risk to quality.
- Research: no proven path at our quality bar; experiments decide.
- Needs a person: depends on a skill the agents don't have.
- Out of reach for now.

## The map

| Area | Rating | Why | Biggest risk | Cheapest test |
| --- | --- | --- | --- | --- |
| Building system (diary → plan → parts) | Doable | Shape grammars (CGA, Instant Architecture) and Townscaper prove the method | The shapes are correct but not beautiful | LT1 shape step |
| Coat stack, wear, ghost signs | Doable | Layered surfaces and decals are standard in URP | Wear reads as noise, not history | One building shown in three years |
| One roof over joined volumes | Hard | Straight-skeleton roofs fail on awkward shapes (Kelly & Wonka admit it) | Broken roofs on odd footprints | 200 random footprints; count failures; fall back to one roof per volume |
| A distinctive look in URP | Hard, and core | Sable shipped a distinctive look in Unity; the hard part is taste, not tech | Ending up with a nice but generic look | LT1's four looks, judged blind |
| Atmosphere, sky and mood manager | Doable | SEASON and Firewatch show the method; URP needs our own full-screen passes | Time spent on tooling before beauty | Drizzle and blue hour on one street |
| Shaded sky light and fake bounce | Doable | TF2's ambient cube; written into parts by the generator | Flat drizzle scenes | Part of LT1 |
| Harbour water | Doable | Stylised water is well trodden; Unity's Boat Attack demo is a reference | Water that looks like a stock asset | A quay at three lights |
| Wet streets reflecting lit windows | Hard | URP has no screen-space reflections; options are planar reflection on water, probes, or our own pass | The blue-hour signature looks fake | One wet street at blue hour |
| Haze and light beams at gigs | Doable | An MIT-licensed URP volumetric package exists | Cost on the Mac mini | One stage with haze |
| Street layer (paving, lamps, trees, desire paths) | Doable | Clear rules and models (Helbing) | Too much clutter | Part of the street step |
| Nature with history | Doable as a system; Hard to make beautiful | Deussen's model is simple; beautiful foliage is an art problem | Generic stylised trees | One forest edge with a path through it |
| Generating the past (fabric pass) | Hard, and owned by the engine project | Methods exist (Emilien 2012), but nobody owns it yet; it should read the same setting timeline as the engine's economy (proposed on #23) | Waiting on another project | Hand-written diaries for LT1 to LT3; a stand-alone prototype the engine can adopt later |
| Engine export and bridge | Doable technically; depends on the engine project | Tag `rH28` has a read-only front door showing the truth, fit for tools; the player-facing export is #22 | Timing | Fixtures until #22; tools against `rH28` |
| Interiors | Doable as a system; Hard by volume | Shadows of Doubt proves the method; furniture kits for every era are a lot of content | Empty-feeling rooms | One flat in three decades |
| Venue ladder and stage light | Doable | Light history and methods are documented | Canned-feeling gigs | LT2 and later |
| People: base body and stylisation | Needs a person | Agents are weak at organic sculpting, faces and hands; CC0 bases exist (MakeHuman, Anny, Blender base meshes) | People are the weakest part of the whole world | One person, three stylisations, before any crowd |
| People: variety and ageing | Doable once a base exists | Archetype blending and Anny's age axis | Same-face syndrome | The 50-silhouette sheet |
| Animation | Hard | A small library (Mixamo, Quaternius) plus procedural layers can carry it; stepped timing hides a small budget | Stiff or floaty movement | Two people talking, in the bar |
| Crowds | Doable | Tiers as in Assassin's Creed Unity; baked GPU animation | Cost of building GPU animation ourselves | A gig crowd of 500 |
| One wind for everything | Doable | Ghost of Tsushima's method; a gust texture computed from the clock | Motion that reads as noise | A street in a gust, stepped on twos |
| Vehicles and boats as owner facts | Doable as a system; Hard by volume | Ownership and routines come from the engine; every era needs its own models | Too few models, so streets repeat | A 1989 street with 30 parked cars from fixtures |
| Sound systems | Doable | Ambience by time, weather and place; layered crowds | | |
| Sound assets | Needs a person | Agents can't record; CC0 libraries help; field recordings in Stavanger would make it ours | Generic stock sound | Øystein records the harbour, rain, a bar |
| Music for a music game | Needs a person | Agents can't compose or produce music; the band's songs are core to that game | The game's heart sounds borrowed | Decide early: composer, local musicians, or licensing |
| Interface | Doable | Øystein's field; clear precedents (nested reasons, ranges, rumour maps) | Too much on screen | A paper prototype of a "why?" chain |
| Determinism and tests | Doable | Integer hashes, plan hasher, shuffled-order checks | Seeding that breaks when Unity changes runtime | The plan hasher, first tool built |
| Performance on the Mac mini | Doable with care | Unity 6's GPU Resident Drawer and chunked meshes | Unknown until measured | The performance harness |
| Many eras of parts | Hard by volume | Each decade needs its own shelf; generators make families cheaply | Running out of time before running out of decades | Build eras only for the window a game needs |
| Players actually reading history | Research | Studies show players read meaning into anything; whether they read *our* meaning needs testing | Beautiful history nobody notices | LT3 time-lapse shown to people who know nothing about it |
| The time origin: a 1989 game | Doable; depends on the engine project | The setting pack sets the start year (#23), so a 1989 world starts its people in 1959; a timeline of world events (canning, oil, the 1986 crash) follows it | A static economy, so thirty years of history change nothing | Look tests use `authored` fixtures until #23 and the timeline land |
| Two clocks: monthly social life, hourly scenes | Research | Nobody has defined who owns scene schedules or what gets committed | Scenes that contradict the month's facts | One monthly event and one hourly encounter that overlap, checked for agreement |
| Player actions back to the engine | Hard | Needs commands, acceptance or refusal, stable ids, versioned saves | A one-way renderer mistaken for a game | One small two-way action: invite someone to a rehearsal; the engine accepts or refuses |
| Driving Unity from agents | Doable, with friction | No Unity MCP yet; batch mode and a command-file runner work | Slow iteration | Set up in the first Unity session |

## Out of reach for now

Photoreal anything. Hand-painted textures at Arcane's level across a whole town. Real-time global illumination (URP's needs precomputation, and our places change). Water that physically reacts to boats and storms. Motion-capture quality animation. Beautiful faces without a character artist. Generated music.

## What only people can supply

- A character artist for the stylised base body, head and archetype shapes. Probably the most valuable single commission.
- A composer or musicians for the music game.
- Field recordings and reference photos: Øystein in Stavanger, in drizzle, low sun and blue hour.
- Cold readers and playtesters, as the engine uses, to check that history reads.
- Øystein's judgement. Agents can make, measure and compare, but they don't decide what is beautiful. His time is the real bottleneck, so every step must end in something quick to judge.

## The order of bets

1. The look (LT1). Everything else is wasted if the town isn't beautiful. Shape language first, then the four shadings, judged blind.
2. Shape robustness. Roofs and massing over hundreds of footprints, with failures counted.
3. Blue hour. Wet streets, lit windows, reflections: the signature moment and the hardest technical one.
4. People. One person, three stylisations, and the commissioning decision, before LT2 depends on it.
5. History that reads (LT3). The time-lapse in front of people who know nothing about it.
6. The engine link. Requests in good time, fixtures until then.
7. Sound and music. Decide who makes the music while the music game is still an idea.

## How this stays honest

Each look test records what we keep and drop in `docs/experiments.md`, and updates this map when a rating changes. A rating moves up only on evidence: a render, a measurement, a reaction from someone who didn't build it.
