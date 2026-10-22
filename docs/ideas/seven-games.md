# Idea: seven games built on reading a world

Status: ideas, not decisions. Ranked by whether anyone would want to play them, then by how cleverly they use the engine. None has been built or played. The precedents and rules behind them are in `docs/research/game-precedents.md`.

Two of the seven only read a finished history, so they can start on a snapshot once the front door's part two (#22) lands: the Traitors and Columbo. The other five need player actions to go back into the engine, which `docs/research/reality-check.md` rates Hard. The request numbers below refer to `docs/engine-requests.md`.

## 1. The Traitors, with the town as host

**Pitch.** Three to five friends investigate one death in a seeded town. Each holds a different true archive: the graves and parish register, the newspaper and police file, the letters and diaries, the streets themselves. One player is secretly the Traitor, whose archive is just as true, and whose job is to steer the group to the wrong person at the round table.

**The moment.** The Traitor reads out a gravestone that is entirely true and entirely misleading, and nobody catches it until another player's diary contradicts the date. After the vote, the engine replays what happened.

**Why it works.** The Traitors' public round table, The Past Within's split knowledge and Blood on the Clocktower's referee who holds the truth, joined. The engine is the referee, so every archive comes from one TRUTH and nobody writes four consistent dossiers by hand. Players do the lying, so no generated character has to be believed as a deliberate liar.

**Engine.** Now: a TRUTH snapshot (#22). Grow toward: an archive per source (12), records as accounts (11).

**Weakness.** Social deduction lives on the friend group, and role balance is fragile.

**Cheapest test.** Four printed archives cut from one seeded town, one secret Traitor, 45 minutes. Work out by hand first that the case is solvable only by pooling. It dies if honest players win without reading, or the Traitor cannot mislead without inventing facts.

## 2. The ghost in the cemetery

**Pitch.** A ghost with no memory of its own death. The graves speak, and their epitaphs contradict each other. Enter a grave, return to the day that person died, change one small thing. Each return costs energy you cannot get back. Your own death is the last case, and only the lives you changed can solve it.

**The moment.** You save a fisherman. When you come back, his grave is still there, with a later date and a different cause, and his daughter's grave has appeared beside it.

**Why it works.** Spoon River Anthology's dead who speak and disagree, Ghost Trick's minutes before death, and Russian Doll's ending, where the loop breaks only when two people save each other. Every grave is a true fact, so the cemetery is a level select made of causes. A saved life changes its grave rather than erasing it, which keeps death from becoming trivial (Our Town's third act: returning to a life should hurt).

**Engine.** The engine already draws each person's choices from their own stream, so one change moves others only through real causes. Deaths already carry their reasons, and a wish to make things right becomes a regret on the record: the mourners' murmurs exist. Grow toward: deaths with a moment someone could change (14), and branching a world from a checkpoint (15).

**Weakness.** Today's deaths come from age and illness; few have a moment worth returning to.

**Cheapest test.** Branch one fixture world at one death, change one decision, and diff the two cemeteries thirty years on. It dies if the change reaches everything (noise) or nothing (no game).

## 3. The forger

**Pitch.** You fake records: a will, a deed, a letter of recommendation. The town checks them against what people remember. Every lie must survive a world that knows the truth.

**The moment.** A forged alibi holds for two years, until a widow remembers that her husband was at sea that week.

**Why it works.** It turns "who could contradict this?" into the whole game. Papers, Please inverted: you make the documents, the town inspects them.

**Engine.** The liar's ledger (13), records as accounts (11), and player commands back to the engine.

**Weakness.** Needs the two-way channel, and lies must be checked fairly, or failures feel arbitrary.

**Cheapest test.** On paper: one forged document against a printed list of who knew what. Can a player predict who will catch it?

## 4. The smuggler on the prohibition coast

**Pitch.** Norway's prohibition years, 1916 to 1927. Run spirits along the fjords while the town watches: who suddenly has money, whose boat is out at night, which grave is too deep.

**The moment.** Your neighbour's new car is what gives you away, not anything you did.

**Why it works.** Wealth and routine already read from the street (`research/what-moves.md`). Here they become suspicion.

**Engine.** A 1920s setting pack and timeline (#23), habits (#22), the liar's ledger (13), player commands.

**Weakness.** A second era pack, off the 1989 path.

**Cheapest test.** One street's habits printed for one month; can a player spot the smuggler from traces alone?

## 5. Columbo in a town that remembers

**Pitch.** You watch the death happen. Then you prove it, from a town where every witness has an account and every account has a source.

**The moment.** The proof turns on a trace nobody thought about: worn steps that say someone came every night.

**Why it works.** Inverted detection fits a simulation that always knows the truth. Knox and Van Dine's fair-play rules become a check that a generated case is fair.

**Engine.** Now: a TRUTH snapshot (#22). Grow toward: accounts (#20), records as accounts (11).

**Weakness.** Players say they prefer hand-made mysteries. The case must prove it is fair.

**Cheapest test.** One printed case from a fixture death: shown the culprit, can a player build the proof from the archive in 30 minutes?

## 6. The band

**Pitch.** Find a band in a small town, keep it together and make the promises that will be tested years later (`ideas/game-layer-ideas.md`, `ideas/talent-discovery.md`).

**The moment.** A retrospective, in the style of Behind the Music, generated from what happened, and you recognise the night it started to fall apart.

**Why it works.** Moneyball scouting, scene histories (the Bergen Wave) and remembered promises.

**Engine.** The band for a year (8), accounts (#20), player commands.

**Weakness.** The music itself needs people.

**Cheapest test.** The first player command (#22): an invitation the engine accepts or refuses, and whether the refusal reads as a person.

## 7. Heirs: friends inherit one town

**Pitch.** Friends take turns playing one town, each a generation later, and inherit what the last player did. Each heir's first act is to walk the town and read what changed.

**The moment.** You find your friend's broken promise in your grandmother's diary.

**Why it works.** Boatmurdered's handover, where each player blamed the last, made true by the engine.

**Engine.** Saves that carry the player's history, player commands, generations.

**Weakness.** The longest path of all seven.

**Cheapest test.** Two players, one fixture town, one handover with a written note. Is the second player's walk interesting?
