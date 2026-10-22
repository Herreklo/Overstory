# Game ideas tidied: the coverage map

For a fresh checker. Every section of every input page, and where its content now lives. Paths without a folder are in `docs/ideas/`. "Verbatim" means the text is unchanged apart from cross-references (a page name or request number updated) and, where noted, a word such as "option" changed to "idea". Nothing was dropped except where a row says "duplicate of", naming where the original lives.

## In short

- **Inputs:** the ten pages in `docs/ideas/` at `c1bcd4c` (unchanged there since `88e560f`); from branch `origin/ideas/inquest` at `7f90d7d`, five idea pages, `docs/research/game-precedents.md`, and the engine-requests section "For games that read the world" with its case checker paragraph.
- **New pages:** `README.md` (the catalogue), `mysteries.md`, `lives.md`, `groups.md`, `roles.md`, `outlaws.md`, `multiplayer.md`.
- **Copied from the branch:** `inquest.md` (adjusted), `inquest-case-1.md` (unchanged), `moments-in-focus.md` (status line adjusted), `docs/research/game-precedents.md` (unchanged). The branch itself is untouched.
- **Dissolved:** `more-game-types.md`, `worlds-on-screen.md`, `casebook-detective.md`, `old-games-fulfilled.md` (deleted here); the branch's `seven-games.md` and `groups-and-growth.md` (never copied; their content is placed below).
- **Kept and changed:** `first-game-options.md` (option texts moved out, section 7 added), `game-layer-ideas.md` (one section moved out, sections added), `stories-in-the-world.md` (section 6 moved out).
- **Unchanged:** `talent-discovery.md`, `showing-time.md`, `world-map.md`.
- **The branch's `game-layer-ideas.md` and `talent-discovery.md`** are identical to ours (`git diff` empty), so nothing from them needed merging.
- **Engine requests 11 to 17** from the branch are mapped in `game-layer-ideas.md` (What the reading games need from the engine). `docs/engine-requests.md` is unchanged.

## `first-game-options.md` (kept)

| Section | Now |
| --- | --- |
| Title, Status | Same page, verbatim; a paragraph added after it saying what the page now holds and that section 7 gathers the other rankings. |
| What this is for (two tests, Juul's model, the givens, Understory's `WHY.md`, how claims are sourced) | Same page, verbatim. "The town is not decoration" now points to `game-layer-ideas.md` (What each idea asks of Overstory), where the spreadsheet test went. |
| 1. What the games teach: Managers, Lives and generations, Reading and exploring, Watching, Role-playing games, Mysteries, What runs across them | Same page, verbatim. |
| 2. Six options: the criteria list and the cost unit | Same page, verbatim; then one line per option linking to its home. The cost unit and the criteria pointer are also repeated in each family page's opening. |
| Option 1: The club (all subsections) | `groups.md`, The club, The game (option 1). Verbatim. |
| Option 2: The band (all subsections) | `groups.md`, The band, The game (option 2). Verbatim. |
| Option 3: The restorer (the "reshaped from the return" note and all subsections) | `roles.md`, The restorer, The game (option 3). Verbatim. |
| Option 4: A life and its heirs (all subsections) | `lives.md`, A family across generations, A life and its heirs (option 4). Verbatim. |
| Option 5: The paper (all subsections) | `roles.md`, The paper, The game (option 5). Verbatim. |
| Option 6: The game, Dials, Core loop, Time, The game in it | `mysteries.md`, A death in the town, The game on today's engine (option 6). Verbatim; one sentence from `stories-in-the-world.md` section 6 joined to The game. |
| Option 6: What the engine can decide | Same place. Verbatim, with "option" changed to "idea" twice ("So the idea grows in steps"; "filed only if this idea is chosen") and "(28)" written "(request 28)". |
| Option 6: As a game on today's engine; If murder is requested; Rule 8, without sensation | Same place. Verbatim. |
| Option 6: Repeatable without going stale | Same place. Verbatim, merged with `stories-in-the-world.md`'s five guards (Keeping it fresh); see that page below. |
| Option 6: Needs, Only here, Risks, Cost, Criteria, Greybox and paper playtest | Same place. Verbatim. |
| 3. Is there a role-playing game here? | `lives.md`, under option 4 (Is there a role-playing game here?). Verbatim, with "Any of the six" written "Any of the six options". The section here keeps a pointer. |
| 4. Comparison (both tables) | Same page, verbatim. The sentence before the second table now says the Rank column is this page's own, as recorded, and that no game is chosen. |
| 5. Recommendation | Same page, verbatim; a line added before it: recorded, not a decision, and the paper playtests' status. |
| 6. What the greybox should test first (both lists and the hour table) | Same page, verbatim. |
| Sources, Gaps | Same page, verbatim. |
| (new) 7. Other recorded rankings and recommendations | Gathers the rankings below from `more-game-types.md`, `seven-games.md`, `groups-and-growth.md`, `inquest.md` and the paper playtest panels (the panels by link only). |

## `more-game-types.md` (dissolved)

| Section | Now |
| --- | --- |
| Title and intro (ideas, 21 October; candidates for round 2 of the paper playtests, `docs/plan.md` 1f+, beside the first seven, listed) | `first-game-options.md`, section 7 (Candidates for a second round of paper playtests), with the list of the first seven verbatim. |
| What the world has that others don't (the four, and "A game type is strong here when…") | `README.md`, How ideas are judged. Verbatim. |
| Candidates table: Postal carrier | `mysteries.md`, The round, The postal carrier. Every cell verbatim, as labelled lines. |
| Restorer | `roles.md`, The restorer, The restorer, as a candidate for round 2. Verbatim. |
| Town photographer and archivist | `roles.md`, The observer, the photographer and the archivist, The town photographer and archivist. Verbatim. |
| The Courier's editor or the Anchor's landlord | `roles.md`, The paper, The Courier's editor or the Anchor's landlord. Verbatim. |
| Councillor or planner | `roles.md`, The town's politics, The councillor or planner. Verbatim. |
| Town doctor | `roles.md`, The town doctor. Verbatim. |
| Café owner | `groups.md`, The venture, The café owner. Verbatim. |
| A child growing up | `lives.md`, A child growing up. Verbatim. |
| The house itself | `lives.md`, The house itself. Verbatim. |
| Not a fit | `README.md`, Not a fit. Verbatim. |
| Øystein's read (21 October) | `README.md`, Combinations and connections. Verbatim, quote and date kept. Its last sentence (the Courier's editor stays a standalone candidate) is repeated in `roles.md` (The Courier's editor), and its verdict quote in the cards for the round, the restorer and the photographer. |
| Recommended for round 2 (the four, and the two hybrids) | `first-game-options.md`, section 7. Verbatim. The two hybrids are also the second and first bullets of Øystein's read in `README.md`. |

## `worlds-on-screen.md` (dissolved)

| Section | Now |
| --- | --- |
| Title and status (Overstory's reading of the open notebook, 20 October 2026) | `game-layer-ideas.md`, What each idea asks of Overstory: the notebook sentence. "This note keeps what Overstory carries" is implicit in the catalogue; nothing else was in it. |
| The test | `game-layer-ideas.md`, What each idea asks of Overstory, first paragraph. Verbatim. Summarised in `README.md` (How ideas are judged, the spreadsheet test). |
| Ideas that pass: the restoration architect | `roles.md`, The restorer, The restoration architect. Verbatim. |
| The town archivist | `roles.md`, The observer, the photographer and the archivist, The town archivist. Verbatim. |
| Social archaeology | `roles.md`, The observer, the photographer and the archivist, Social archaeology. Verbatim. |
| The many-lives anthology | `lives.md`, The anthology and the relay. Verbatim. |
| The scene builder | `groups.md`, The scene builder. Verbatim. |
| The counterfactual observatory | `game-layer-ideas.md`, What if, shown: the counterfactual observatory. Verbatim. |
| "The detective in the forest is already in the research" | `README.md`, Where other ideas sit (`docs/research/nature.md`). |
| What each asks of Overstory (the table, its key and the read-across) | `game-layer-ideas.md`, What each idea asks of Overstory. Verbatim. One sentence added: the festival and the hotel appear only in this table. |
| Records follow the world's rules (four bullets) | `game-layer-ideas.md`, Records follow the world's rules. Verbatim; a fifth bullet added from `docs/research/game-precedents.md` rule 2 (the six ways records go wrong), cited. |
| Open questions | `game-layer-ideas.md`, Open questions. Verbatim. |

## `game-layer-ideas.md` (kept)

| Section | Now |
| --- | --- |
| Status | Same page; extended to say where the later sections come from. |
| Promises; Chemistry; The rehearsal room; Legendary without successful; People become important; What fun must feel like; The test that matters | Same page, verbatim. |
| A first playable slice: the first gig | `groups.md`, The band, A first playable slice: the first gig. Verbatim. This page keeps a pointer. |
| (new) In short; What if, shown; Records follow the world's rules; What each idea asks of Overstory; Games that read a finished history; What the reading games need from the engine; Open questions | From `worlds-on-screen.md`, the branch's `seven-games.md` and engine requests, as mapped in their rows. |

## `talent-discovery.md`, `showing-time.md`, `world-map.md` (unchanged)

All sections unchanged. Catalogued in `README.md`: talent discovery as a shared mechanic; the other two as ideas for the world.

## `casebook-detective.md` (dissolved)

| Section | Now |
| --- | --- |
| Title, status and Øystein's two quotes (22 October) | `mysteries.md`, The casebook (verbatim, with date). Also in `README.md`, the card A death in the town (Status); the second quote also opens `multiplayer.md`. |
| The model: Sherlock Holmes Consulting Detective, and Adjusted for our town | `mysteries.md`, The casebook. Verbatim; "It sharpens option 6" written "It sharpens the death in the town above". |
| The mystery, generated (five bullets) | `mysteries.md`, The casebook. Verbatim. |
| Multiplayer: co-op; rival reporters | `mysteries.md`, The casebook. Verbatim ("(option 5)" written "(the paper, `roles.md`)"). |
| Multiplayer: the culprit is a player | `multiplayer.md`, One of them is a player. Verbatim. |
| Multiplayer: a daily case | `multiplayer.md`, The daily case. Verbatim. |
| What it would need from the engine | `mysteries.md`, The casebook. Verbatim. "Secrets as facts" is also listed in `game-layer-ideas.md`. |
| Related: Inquest, on the unmerged branch | Replaced by the link to `inquest.md` from `mysteries.md` (Inquest: the ghost who closes a hole), since Inquest is now on this branch. |

## `old-games-fulfilled.md` (dissolved)

| Section | Now |
| --- | --- |
| Title, status, Øystein's three quotes (22 October) | First quote ("i feel like there are so much more ideas…"): `README.md`, Combinations and connections. Second ("is there a jones…"): `lives.md`, Up the Hill, and the card A family across generations (Status). Third ("Now look at connections…"): `README.md`, Combinations and connections, and `mysteries.md`, The long inquest. All verbatim with date. |
| "Each idea starts from an older game…"; "A town of developing people…"; "Details of the old games are from memory…" | `README.md`, How ideas are judged (Claims about other games); the *(old game)* marker and the memory note also open `mysteries.md` and `lives.md`, and stand with the movement, casing and one of them is a player. |
| The research note (balance, difficulty, engagement; "we can do it later") | `README.md`, How ideas are judged (Before any idea is chosen). Verbatim. |
| 1. The Week | `mysteries.md`, The Week. Verbatim. |
| 2. Shenmue, fulfilled | `mysteries.md`, Shenmue, fulfilled. Verbatim. |
| 3. The acorn | `lives.md`, The acorn. Verbatim; a pointer to the venture added. |
| 4. The movement | `roles.md`, The town's politics, The movement. Verbatim. |
| 5. Casing | `outlaws.md`, Casing. Verbatim. |
| 6. Class of '89 | `lives.md`, Up the Hill (Class of '89, its simple form). Verbatim. |
| 7. The paper round | `mysteries.md`, The round, The paper round. Verbatim. |
| 8. One of them is a player | `multiplayer.md`, One of them is a player. Verbatim. |
| 9. Up the Hill (seven bullets) | `lives.md`, Up the Hill. Verbatim. |
| Connections: intro sentence | `README.md`, Combinations and connections (each connection listed with its home). |
| The long inquest | `mysteries.md`, The long inquest. Verbatim. |
| Relay | `lives.md`, The anthology and the relay. Verbatim. |
| The Week, together | `mysteries.md`, The Week. Verbatim. |
| The living board | `lives.md`, Up the Hill (The living board). Verbatim. |
| The youth team | `groups.md`, The club, The youth team. Verbatim. |
| The ghost | `inquest.md`, Other ghosts, The ghost who cannot act. Verbatim. |
| What the strongest share | `README.md`, Combinations and connections. Verbatim. |

## `stories-in-the-world.md` (kept)

| Section | Now |
| --- | --- |
| Title, Dates, The bottom line, sections 1 to 5, section 7, Sources | Same page, unchanged. |
| 6. Potentials for play, Four games: the murder mystery row | `mysteries.md`, option 6: the loop sentence joined to The game; What carries it. Verbatim. |
| The journalist row | `roles.md`, The journalist, from the real run. Verbatim. |
| The observer row | `roles.md`, The observer, the photographer and the archivist, The observer. Verbatim. |
| The family saga row | `lives.md`, The family saga, followed. Verbatim. |
| The paragraph after the table (observer cheapest; journalist fits the institutions; family saga needs homes) | Split, verbatim: `roles.md` (The observer; The journalist, from the real run) and `lives.md` (The family saga, followed). |
| 6, A death that is a mystery (six needs, the pre-mortem warning, Andy Shaw's death) | `mysteries.md`, What a murder would need, in full. Verbatim. |
| 6, Keeping it fresh: the opening sentence | Duplicate of option 6's opening of Repeatable without going stale (`mysteries.md`); its phrase "its cases come from templates and its documents repeat" was added there. |
| 6, Keeping it fresh: the five guards | `mysteries.md`, Repeatable without going stale. "Cases come from chains" joined to "the case is a life"; "Count kinds, fold repeats" and "Let some cases end in ?" as their own bullets; "The town ages under the cases" joined to "the town ages between cases"; "The player's own traces" as its own bullet, citing `docs/research/time-on-screen.md` (The player's own traces) instead of "`NOW.md`, Decided", which no longer exists. |
| Section 6's heading | Kept; the section is now a list of pointers to the new homes. |

## Branch `ideas/inquest`: `inquest.md` (copied, adjusted)

| Section | Now |
| --- | --- |
| Status | Extended: a form of the death in the town; why request numbers were mapped. |
| In one line; What it should feel like; How it plays (the case, the model, phase one, phase two); What makes it ours | Verbatim. |
| Generating a case | Verbatim; step 3's reference now names request 9 and `game-layer-ideas.md`. |
| Multiplayer | Verbatim; one sentence added linking the Traitors with the town as host. |
| Other shapes it could take | Verbatim. |
| (new) Other ghosts | The ghost in the cemetery (`seven-games.md` 2) and the ghost who cannot act (`old-games-fulfilled.md`). |
| Precedents; Has it been done?; Risks; The first two tests | Verbatim. |
| Is it possible? | Verbatim; the engine-made row's numbers mapped: deaths with a moment (not yet requested), records as accounts (9), branching (not yet requested), things in events (partly 17 and 20), the case checker (Overstory's own). |

## Branch: `inquest-case-1.md`, `docs/research/game-precedents.md` (copied unchanged)

Every section unchanged. `game-precedents.md` was copied because `inquest.md` and the seven games cite it.

## Branch: `moments-in-focus.md` (copied, adjusted)

| Section | Now |
| --- | --- |
| Status | Rewritten for the numbering: "item 17" is not yet requested (17 is now goods as things); nearest requests 1 and 28; LW2. The request wording is in `game-layer-ideas.md`. |
| The idea; How it works; The rule that keeps it honest; Why it matters; Open questions | Verbatim. |

## Branch: `seven-games.md` (dissolved)

| Section | Now |
| --- | --- |
| Status (ranking basis; none built or played; precedents) | `first-game-options.md`, section 7 (Seven games built on reading a world). |
| Intro (two read a finished history; five need player actions, rated Hard; request numbers) | `game-layer-ideas.md`, Games that read a finished history. The numbers are mapped wherever they appear. |
| 1. The Traitors, with the town as host | `multiplayer.md`, The Traitors, with the town as host. Verbatim; Engine line mapped (archive per source: not yet requested; records as accounts: 9). |
| 2. The ghost in the cemetery | `inquest.md`, Other ghosts. Verbatim; Engine line mapped (both not yet requested). |
| 3. The forger | `outlaws.md`, The forger. Verbatim; Engine line mapped (liar's ledger: not yet requested; records as accounts: 9). |
| 4. The smuggler on the prohibition coast | `outlaws.md`, The smuggler. Verbatim; liar's ledger mapped. |
| 5. Columbo in a town that remembers | `mysteries.md`, Columbo. Verbatim; records as accounts mapped to 9. |
| 6. The band | `groups.md`, The band, As a group game. Merged with `groups-and-growth.md`'s band row: both pitches, both moments and both weaknesses kept side by side; Why it works, Engine (8) and Cheapest test verbatim. |
| 7. Heirs | `lives.md`, The anthology and the relay (Heirs). Verbatim; "the longest path of all seven" written "the longest path of the seven games built on reading a world". |

## Branch: `groups-and-growth.md` (dissolved)

| Section | Now |
| --- | --- |
| Status (games about assembling people; ranked by fit with the engine; the band is the recommendation) | `groups.md`, In short; the ranking and the recommendation in `first-game-options.md`, section 7. |
| The ceiling of the genre | `groups.md`, What every group game here shares. Verbatim. |
| Our edge | Same place. Verbatim. |
| Decide monthly, watch the evenings | Same place. Verbatim. |
| Five concepts: the band | `groups.md`, The band, As a group game (merged; see `seven-games.md` 6). |
| The club | `groups.md`, The club, As a group game. Verbatim. |
| The crew | `groups.md`, The crew. Verbatim. |
| The venture | `groups.md`, The venture, As a group game. Verbatim. |
| The family | `lives.md`, The family, as a group across a century. Verbatim; "overlaps the heirs in `seven-games.md`" written "overlaps Heirs (below)". |
| The recommendation and the mark | `groups.md`, The band (The groups round's recommendation, labelled recorded, not a decision). Verbatim. |
| Multiplayer: a band is a hidden-role game | `groups.md`, The band. Verbatim. |
| The risk | `groups.md`, What every group game here shares. Verbatim. |
| The first test | `groups.md`, The band. Verbatim. |

## Branch: `docs/engine-requests.md`, For games that read the world, and the case checker

| Section | Now |
| --- | --- |
| Intro (where they come from; most rest on the accounts arc) | `game-layer-ideas.md`, What the reading games need from the engine. Verbatim apart from the source list. |
| 11 to 17, each with what the player would see | Same section, "The needs in their own words". Verbatim, without their numbers; 13 gains the name "the liar's ledger" used by the seven games. The mapping table gives each old number its current request or "not yet requested". |
| "A case checker is ours too" (Overstory's own) | Same section, verbatim, with one sentence tying it to Inquest's checker and the casebook's solver. |
| The branch's change to `NOW.md` (an engine status line of its day) | Not an idea; not carried. The current `NOW.md` has a newer engine status. |

## Edits outside `docs/ideas/`

- `NOW.md`: the Inquest bullet replaced by one line pointing to `docs/ideas/README.md`. Nothing else changed.
- `CLAUDE.md`: the Docs table's `docs/ideas/` cell names the catalogue.
- Links updated: `docs/research/fun.md` (Sources, `more-game-types.md`), `docs/research/playtesting.md` (option 6 now also names `mysteries.md`), `docs/playtests/paper-1/method.md` (the restorer, now also `roles.md`), `docs/research/time-on-screen.md` (two links to `worlds-on-screen.md`).
- Left as it is: `docs/notes/2026-10-21-6-overstory-to-understory.md` names `more-game-types` as part of a note already sent; it is a record. Links from `reviews/` reach only `first-game-options.md` and `stories-in-the-world.md`, which still exist.

## Fresh check (23 October)

A fresh checker compared every input page with its new home, sentence by sentence. Content was complete; these losses of nuance were repaired in place:
- `game-layer-ideas.md`: the reviews' provenance covers every section from Promises to The test that matters (not "the first six"); its In short keeps "may be tested years later" and "causal events and relationships"; four needs are not yet requested and two only in part (not five); Inquest is "more reachable than it looks" (its own words), not "reachable".
- `mysteries.md`: the sifter "should prefer" chains of many kinds (it was "prefers"); the five guards' source, the real run, is named again.
- `inquest.md`: the ghost who cannot act was labelled "new" in its round, not *(old game)*; the marker is removed.
- `README.md`: Inquest's "no right answer" restored (it read "No change is the right answer"); the mystery playtest's solve gap keeps its cause (three facts with "nothing on record"; the other seven tied) and the unaudited ledgers; a role "with a body in the town" applies to the six options, not any idea (also in `roles.md`); the paper "could be" the death's second role; only the six options are rated on the criteria; the research note's round is named; the house itself's risk is no longer under Status.
- `first-game-options.md`, section 7: the nine round-2 candidates and "Recommended for round 2" restored.
- The open notebook's ideas that pass the spreadsheet test (the restoration architect, the archivist, social archaeology, the anthology, the scene builder, the counterfactual observatory) keep that verdict and its date; the first gig keeps its source.
- `multiplayer.md`: the engine as referee is the Traitors' point, not all three ideas'.

Links: no live link reaches a dissolved page; the only mentions are this map and the sent note above. The blind rule: no new or changed page describes the playable corner's case.
