# Played together

Ideas, not decisions: no game is chosen (`NOW.md`). Every idea is catalogued in `README.md`; this page holds the full detail of the multiplayer ideas that stand alone, and lists where the others are.

Øystein, 22 October, on the casebook: "something fun for multiplayer stuff would also be nice."

## In short

- **The Traitors, with the town as host:** friends investigate one death from different true archives, and one of them steers the group wrong with true evidence.
- **One of them is a player:** one player lives as a resident among simulated ones; the others hunt them.
- **The daily case:** one seed a day for everyone, compared.
- In the Traitors the engine is the referee: it holds the truth, so players do the lying with true evidence and nobody writes consistent dossiers by hand. The rules taken from precedents (split knowledge forces talk; narrow channels between players) are in `docs/research/game-precedents.md`.

## The Traitors, with the town as host

**Pitch.** Three to five friends investigate one death in a seeded town. Each holds a different true archive: the graves and parish register, the newspaper and police file, the letters and diaries, the streets themselves. One player is secretly the Traitor, whose archive is just as true, and whose job is to steer the group to the wrong person at the round table.

**The moment.** The Traitor reads out a gravestone that is entirely true and entirely misleading, and nobody catches it until another player's diary contradicts the date. After the vote, the engine replays what happened.

**Why it works.** The Traitors' public round table, The Past Within's split knowledge and Blood on the Clocktower's referee who holds the truth, joined. The engine is the referee, so every archive comes from one TRUTH and nobody writes four consistent dossiers by hand. Players do the lying, so no generated character has to be believed as a deliberate liar.

**Engine.** Now: a TRUTH snapshot (#22). Grow toward: an archive per source (not yet requested; it extends request 1's people as the player could know them to sources) and records as accounts (request 9). Both are in `game-layer-ideas.md` (What the reading games need from the engine). The case checker that proves a case solvable only by pooling is Overstory's own (the same place).

**Weakness.** Social deduction lives on the friend group, and role balance is fragile.

**Cheapest test.** Four printed archives cut from one seeded town, one secret Traitor, 45 minutes. Work out by hand first that the case is solvable only by pooling. It dies if honest players win without reading, or the Traitor cannot mislead without inventing facts.

It was first of the seven games built on reading a world (`first-game-options.md`, section 7). Inquest's round table is the same game on a ghost's case: split archives, a Traitor called the Tide who wins if the inquiry records the wrong cause or commits a change that fails, and one shared budget of returns (`inquest.md`, Multiplayer).

## One of them is a player *(old game)*

From *Space Station 13* (2003). One player lives as a resident among hundreds of simulated ones, keeping a believable routine, while the others hunt them with the casebook (`mysteries.md`, The casebook). The details of the old game are from memory and are checked before the idea is built on.

The same seat appears in other ideas:
- in the casebook, the culprit is a player: they keep a believable routine among simulated residents while the others investigate;
- in The Week, together, one player causes Sunday, loops too and learns too, as the invader does in *Deathloop* (2021): cat and mouse across loops (`mysteries.md`, The Week);
- in Inquest, Fate against the inquiry: one player is Fate, moving through the past to keep the holes lined up, while the others close them (`inquest.md`, Other shapes);
- casing, where one side plays the police (`outlaws.md`).

Before the engine has crime, the prototype "a human culprit" puts Øystein or a second tester in this seat (`docs/research/playtesting.md`, section 10).

## The daily case

In the casebook, a daily case is the same seed for everyone; players compare visits. Inquest's share codes do the same with no servers: a case is a seed and a record of choices, so a group can play the same case and compare their futures (`inquest.md`, Multiplayer). The prototype "the daily street" tries one seed a day, one question and a score to compare (`docs/research/playtesting.md`, section 10).

## Multiplayer in other ideas

| Idea | Its multiplayer | Where |
| --- | --- | --- |
| The casebook | co-op on a shared clock; rival reporters | `mysteries.md` |
| The long inquest | two investigators in different decades | `mysteries.md` |
| The Week, together | two to four residents pool the notebook between loops | `mysteries.md` |
| The band | a hidden-role game: each friend plays a member with a private ambition | `groups.md` |
| Up the Hill, Class of '89 | two to four families, orders given at the same time | `lives.md` |
| The living board | a legacy campaign over game nights | `lives.md` |
| Relay, Heirs | friends each play a decade or a generation and pass the town on | `lives.md` |
| The movement | rival candidates | `roles.md` |
| Casing | a crew, or one side plays the police | `outlaws.md` |
| Inquest | split archives, the Tide, shared returns, share codes | `inquest.md` |
