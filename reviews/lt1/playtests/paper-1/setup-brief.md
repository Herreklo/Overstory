# The setup writer's brief

The lead's brief to the agent that sets up one concept for its runs, with `{slug}` filled in. Game masters, auditors and the lead read it; players never do.

You set up the concept `{slug}` for paper playtest 1 (repo `/Users/oystein/code/Overstory`; paths are relative to `reviews/lt1/playtests/paper-1/` unless they start with `docs/` or `fixtures/`). Don't start other agents and don't commit. Write only in `{slug}/`.

## Read (once; long files in ranges, by their headings)

1. `docs/playtests/paper-1/method.md` in full, then `gm-brief.md` in full: the runs you set up are played by game masters who follow it.
2. The card, `docs/playtests/paper-1/cards/{slug}.md`, in full. It is the design; you instantiate it, and you don't redesign it. Where it can't be played as written from world 9989, set it up as close as the world allows and write the gap in `setup-on.md` under "Gaps".
3. `docs/playtests/paper-1/prereg.md` and `roster.md`, `arms.md`: who plays this concept, in which arm folder, which kind starts cold this wave, and which arm is lives on.
4. The world pack: `world/engine-rules.md` in full; `world/atlas-9989.md`, its "Before you run it" in full and then the sections your card draws on (grep `^#`; "Six corners" and "Casting the corner and its streets" for the players' starts); `world/records-9989.md` by section; for a lives-off arm, `world/world-9989-off.md` in full. Look facts up with `python3 -I world/tools/w9989.py` (person, year, find, chain) and `python3 -I world/tools/lives_off.py person NAME [FROM TO]`.

## Write

1. **`{slug}/setup-on.md`**, and for a concept with two arms **`{slug}/setup-off.md`**: what every run of that arm shares. The start date and what each round covers in dates; the time jump's target; the concept's state at the start (for example the squad and the league, the band and its gigs, the case, the edition's beats, the house and its market); the card's simulated rules instantiated with numbers and tables; the cast every run meets, with person ids and the events that matter, filtered by visibility (who could know what, and from whom); the records available; and **the six starts**, one per player kind (1 to 6): a different household, corner or case-thread for each, so one lucky story doesn't carry the concept (`method.md`, Robustness). Kind k starts the same in both arms.
2. **The lives-off arm is matched.** Same card, same screens' shape and length, same cast's names, jobs, places and households, same starts. Its lives come from the off world only: no causes, no reasons, no history, nothing that carries (`world-9989-off.md`). In `setup-off.md`, list every place where an off-arm screen must differ from its on-arm twin and why. Nothing else may differ.
3. **Each run's opening**, `{slug}/<arm>/<id>/r0-screen.md` for every player who plays this concept: the store-page pitch and the tutorial from the card (none for the cold-start kind), then the first screen in full and concretely (the place, who is there and what they are doing, what is legible, the verbs and interface), 600 to 1,200 words, ending with the line `Write your act file to {slug}/<arm>/<id>/r1-act.md, up to four turns.` X-k and Y-k get the same start, each in its own arm.
4. **Each run's seed files**, in the same folder: `gm.md` (this run's truth: the cast and facts that matter for this start, with event ids and visibility; the state at the start; a Log section with `- R0: opening written by the setup.`) and `ledger.md` (the fact ledger's header and a row for every claim on `r0-screen.md`, in the shape `gm-brief.md` gives).

Plain, concrete English; short sentences; numbers where a game master needs them. Never show a private act nobody witnessed. Rule 8: no homophobic, sexist or racial content; state the run's same-sex couples plainly, as the record does.

## Check before you finish

- Every claim on every opening has a ledger row and a source; nothing private and unwitnessed is on a screen.
- Each off-arm opening differs from its on-arm twin only where `setup-off.md` says.
- The cold-start openings have no pitch or tutorial; the others have both, word for word the same.

Reply in at most 80 words: the files written, the six starts in a phrase each, and any gap between the card and the world.
