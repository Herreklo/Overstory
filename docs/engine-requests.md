# What the game needs from the engine

Each request: what is needed, why the game needs it, and what the player would see. Øystein takes these to the engine project; this repo never changes the engine.

## Open

1. **Places that come and go.** Ventures already open new places with an owner (a café in the old bank). The game needs every kind of place to work that way: born from someone's venture, changing over time, closing, and reopening as something else. The player would see a street with its own history: a bar that became a café, a ghost sign above a new shopfront.
2. **Buildings separate from businesses.** A building with its construction era, extensions and condition, and a business that occupies it for a time. The player would see the same building across owners.
3. **A building stock older than the simulation.** The engine's history starts in 1996, but a street is mostly older than that. Each neighbourhood needs buildings with eras before 1996, generated once from the seed, so that what happens after 1996 lands on a street that already has a past. The player would see 1890s houses next to a 1970s infill, before the story starts.
4. **A calendar each game can set.** One world, many games, each a window onto it: a murder mystery may span a year, a band's story decades. Every window lies between the past and the present; the world never runs into the future. A game needs to set the year its story starts (LT1 uses 1989), with the generated past before it. The player would see the era they are in: its shopfronts, cars, clothes and music.
5. **An export for the game.** A snapshot of a neighbourhood (places, the people present, recent events) with stable ids, and a way to send player actions back as events.
