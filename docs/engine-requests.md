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
6. **The fabric pass.** Streets, plots and building diaries generated from the seed and the timeline, older than the people and running alongside them. The player would see 1890s houses next to 1970s infill before the story starts, and every change after that with its cause. Nobody owns this yet; until it exists, Overstory writes building diaries by hand, and the LT1 fixture's `street` block (pavement, carriageway, quay, lamps by era, bollards, the ground behind) stands in for its streets.
7. **Story sifting.** Patterns over the event log that find storyful sequences while they unfold (on the engine's own list). The game uses them to choose where the camera goes and which scenes are worth playing: simulate the few, show the many. The player would see the evenings that matter, not random ones.
8. **The band, as a shared milestone.** The engine's planned experiment of five people forming a band for a year, shown by Overstory in the rehearsal loft of a quay warehouse, with the first player command (#22) between them. It tests both projects on the origin they share.

## Later, for the engine

9. **Vacancy, rent and cheap space.** How long a building has stood empty, what it costs to rent, and who takes cheap space (bands, artists, bars) and who pushes them out when the area changes. The player would see a rehearsal room in an old warehouse, and the venue that closes when flats go up next door.
10. **Vehicles and boats with owners.** Who owns which car or boat, when they bought it, new or used. The player would read wealth, age and routine from the cars on a street.
11. **Several places in one world** (`docs/ideas/world-map.md`): towns and cities as setting packs side by side, routes between them with travel time, and people who move between them. An idea for after the starter town, not a request yet.

## Overstory's own

These are presentation, built here from the engine's facts: how a building diary looks, trips and footfall at street level (worn steps, parked cars outside homes where people are in), and hourly weather, heating and lit rooms inside a scene. What they need from the engine is in the front door's habits (#22). Until then the LT1 fixture's `lit` block says which floors are lit at blue hour, and why.
