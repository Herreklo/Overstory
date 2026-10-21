# What the game needs from the engine

Each request: what is needed, why the game needs it, and what the player would see. Øystein takes these to the engine project; this repo never changes the engine. Engine issues labelled `overstory` track the filed ones.

## What we can use now

- **Tag `rH28`**, the engine's front door (`src/boundary.ts`). Its reads show the truth, so they serve debugging tools such as the diary inspector and the bridge schema, never anything a player sees. It has no player command.
- Until the items below land, LT1 and LT2 run on fixtures labelled `authored`.

## Filed

1. **The front door, part two (#22).**
   - The places of a neighbourhood at a month. Today places never close, and the export says so rather than inventing closings.
   - Two people as the player could know them: what a witness could know, not the truth.
   - People's habits as data, so the game can show who is at the bar tonight, whose car is outside and which windows are lit.
   - The first player command: inviting a musician to a rehearsal in the quay warehouse loft, which the engine accepts or refuses. It depends on the accounts arc (#20), because "she remembers being asked" is an account.
2. **The start year from the setting pack (#23).** A world shown in 1989 starts its people in 1959, so play begins with thirty years of lived history.

## Proposed on #23, for the setting timeline that follows it

3. **One timeline for the economy and the fabric.** The setting pack's timeline is one dated list of world events, each with a cause: the canning years, the arrival of oil, the 1986 crash. The economy reads it, and so does the fabric pass that generates streets, plots and building diaries. One list means the buildings on screen can never disagree with the economy. Our era tables feed it. The player would see a cannery built, emptied and converted for the same reasons that cost its workers their jobs.
4. **Places that close, arriving with the timeline.** Ventures open places; closing is the other half of the same lifecycle. The player would see the crash as empty shops and fallow lots, and cheap old buildings taken over by new uses, such as the band's rehearsal loft above a closed business.

## Open, not yet filed

5. **Buildings separate from businesses.** A building with its construction era, extensions and condition, and a business that occupies it for a time. The player would see the same building across owners.
6. **The fabric pass.** Streets, plots and building diaries generated from the seed and the timeline (a street's paving, steps, walls and quays with their dated building, repairs and cleaning: `docs/stone.md`; and each thing's upkeep, who kept it and how well decade by decade, with its campaigns and renewals: `docs/upkeep.md`), older than the people and running alongside them. The player would see 1890s houses next to 1970s infill before the story starts, and every change after that with its cause. Nobody owns this yet; until it exists, Overstory writes building diaries by hand, and the LT1 fixture's `street` block (pavement, carriageway, quay, lamps by era, bollards, the ground behind) stands in for its streets.
7. **Story sifting.** Patterns over the event log that find storyful sequences while they unfold (on the engine's own list). The game uses them to choose where the camera goes and which scenes are worth playing: simulate the few, show the many. Wildermyth found that deeper simulation alone did not give coherent plots, and pairs its characters' histories with events chosen for the moment; sifting is our version of that choice, and it never rewrites a fact. The player would see the evenings that matter, not random ones.
8. **The band, as a shared milestone.** The engine's planned experiment of five people forming a band for a year, shown by Overstory in the rehearsal loft of a quay warehouse, with the first player command (#22) between them. It tests both projects on the origin they share.
9. **Records.** Documents the world makes about its events: a gig poster, a newspaper report, a deed, a phone-book entry, a shop sign, a photograph. Each record has a maker, a date, a purpose and the facts it claims; it can be wrong, partial or out of date, and it stays until something removes it. A report is an account written down, so this builds on the accounts arc (#20). A poster that only restates a booked gig is presentation Overstory draws from the facts; a record that can be wrong belongs to the engine. The player would see the posters of a venue's gigs layered on the wall outside, a sign outliving its business, and the town's paper getting the night wrong, and could find out why.

## Later, for the engine

10. **Vacancy, rent and cheap space.** How long a building has stood empty, what it costs to rent, and who takes cheap space (bands, artists, bars) and who pushes them out when the area changes. The player would see a rehearsal room in an old warehouse, and the venue that closes when flats go up next door.
11. **Vehicles and boats with owners.** Who owns which car or boat, when they bought it, new or used. The player would read wealth, age and routine from the cars on a street.
12. **Several places in one world** (`docs/ideas/world-map.md`): towns and cities as setting packs side by side, routes between them with travel time, and people who move between them. An idea for after the starter town, not a request yet.

## For the living fabric (`docs/living-fabric.md`, agreed 22 October)

How the lives the engine runs reach the town's physical fabric: keepers and their care, works as decisions, homes, feet, goods, the weather that matters, the fabric's rules adopted, small acts on things, and the building a venture takes.

13. **Keepers and care.** Every home, workplace and public thing has a keeper (an owner, a tenant, the council's road department, the harbour), and the keeper's care by decade, read from the engine's own quantities: money, whether they live there or let it, age, and the kind of person they are. The fabric's repairs, repaints and gardens follow it. The player would read from a street which households are flush, absent or failing, and be right.
14. **Works as decisions.** A repair or alteration above patchwork is a keeper's decision with reasons: the owner reclads, the council widens the road (its own plans already say so), the harbour rebuilds a quay. Plans carried out in part leave the scar. The player would see the road widened at one end and could ask why it stopped.
15. **Homes.** A household lives at an address: moved in when, own or rent, who else lives there. Today people have jobs and habits with a place but no home. The player would see who lives behind which door, and moving in and out.
16. **Feet.** From habits, work, school, the shop and the venue: how many trips a month over each path segment. The player would see the worn line on the steps, the path across the lawn, the shop whose step is polished, and the one whose step is not.
17. **Goods as things.** The house, boat and car people save for become things with an owner, a year, new or used, and a place (a mooring, a drive). Item 11 already asks it for vehicles.
18. **Weather that matters.** Monthly weather and the storms, floods and hard winters that count, as dated events the hourly weather fits inside. The player would see the limb the January gale took, and the quay's flood line.
19. **Derived works adopted.** Overstory's life rules written as a portable library the fabric pass can run, so patchwork becomes record; provenance `derived` until then. The engine's own weakness, that events lead nowhere, meets this: the fabric is where consequences land and stay visible.
20. **Small acts on things.** Some of the engine's small acts (a grudge carried, care shown, a favour) may be acts on a thing: a hedge planted, a fence raised, a sign torn down, a step swept for a neighbour, a widow's wall mended by the street's hands. Each a fact with its reason, so a feeling leaves a trace by an act and never by a verdict. The player would see the fence and could ask who built it and why.
21. **Ventures take a building.** A venture that opens names its space, chosen by the engine from the fabric pass's vacancy (cheap, fitting, near the founder) with its reason, so the shop stands where the engine put it. The player would see the café open in the empty ironmonger's and learn it was cheap after the crash.

## Overstory's own

These are presentation, built here from the engine's facts: how a building diary looks, trips and footfall at street level (worn steps, parked cars outside homes where people are in), and hourly weather, heating and lit rooms inside a scene. What they need from the engine is in the front door's habits (#22). Until then the LT1 fixture's `lit` block says which floors are lit at blue hour, and why.
