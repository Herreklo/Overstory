# A casebook detective in the living town

An idea, not a decision: no game is chosen (`first-game-options.md`). Øystein, 22 October, on the board games that could become our game: "actual a good idea. this could work very similar as well. The big thing is the story and mystery though, but maybe would could do this in a very clever generative way?"; "something fun for multiplayer stuff would also be nice."

## The model: Sherlock Holmes Consulting Detective

A case, a map of the city, a directory of addresses and the day's newspaper. Each visit to an address costs time and gives a paragraph to read. At the end, questions, scored against how few visits Holmes needed.

Adjusted for our town:
- The town is the map and the directory, and every address is a real simulated household with its history.
- The newspaper is printed from the engine's events, and it can be wrong (perceived information).
- Reading from above and from the street is free. It tells you which doors are worth a visit, and a visit costs days.
- Mastery is solving with fewer visits, as in Return of the Obra Dinn.
- It sharpens option 6, "A death in the town".

## The mystery, generated

- **Simulate, then sift.** The engine runs the town for years. A sifter then searches the record for an event that makes a good case: several people with a motive and an opportunity, and traces spread over the town. The craft is already studied (`docs/research/behaviour-on-screen.md`, section 7: Ryan's story sifting, Kreminski's Felt and its Cozy Mystery Construction Kit, where each witness reads the same events by their own values). Ryan's Talk of the Town and Bad News are the nearest research towns (`first-game-options.md`).
- **Red herrings from true secrets.** Many people hide things unrelated to the case.
- **Fair by machine.** Before a case is offered, a solver checks that the reachable evidence gives one answer, and counts the fewest visits needed: the score to beat.
- **The nearest game is Shadows of Doubt (early access 2023).** It plans each citizen's day and logs every sighting as a fading memory (`behaviour-on-screen.md`). Its generated city is praised and its cases called random in motive (to be checked). Our motives come from developed lives.
- **The city as evidence,** true to the facts (`CLAUDE.md`, five kinds of thing on screen). Where someone grew up decides where they go and what they hide (`docs/town-plan.md`, TP6).

## Multiplayer

- **Co-op:** players split up to cover addresses on a shared clock, then argue the answer.
- **Rival reporters:** two players race on one case. A questioned witness clams up; a tip leaks into tomorrow's paper (option 5).
- **The culprit is a player:** they keep a believable routine among simulated residents while the others investigate.
- **A daily case:** the same seed for everyone; compare visits.

## What it would need from the engine

In `docs/engine-requests.md`: how each holder knows each event, and habits as timetables, so sightings follow routines (1); story sifting (7); records such as the paper, which can be wrong (9). Not yet requested: secrets as facts, who hides what from whom.

Related: the stored idea Inquest, on the unmerged branch `ideas/inquest` (`NOW.md`).
