# The game master's brief

How a game master runs one player's session in paper playtest 1. Game masters, auditors, analysts and the lead read it; players never do. It adds the operating detail to `docs/playtests/paper-1/method.md`, which you read first, in full. Where they differ, this page is newer (written on resuming, 21 October, evening).

## Your run

Your brief from the lead names: the concept (`<slug>`), the arm folder (`a` or `b`; whether it is lives on or off is in `arms.md`), the player id (X1 to Y6), and so the run folder `reviews/lt1/playtests/paper-1/<slug>/<arm>/<id>/`. Paths below are relative to `reviews/lt1/playtests/paper-1/` unless they start with `docs/` or `fixtures/`; write them in full (`/Users/oystein/code/Overstory/...`) in any message to the player.

Read, once, in ranges where long: `method.md`; this page; the card `docs/playtests/paper-1/cards/<slug>.md`; the setup `<slug>/setup-<on|off>.md`; your run's `gm.md` if the setup seeded one, and your `r0-screen.md` if it is written; `roster.md` (the player's kind, model and whether it starts cold this wave); then the world pack as your run needs it: `world/engine-rules.md` in full, and `world/atlas-9989.md`, `world/records-9989.md` by section. Lives off: `world/world-9989-off.md` in full, and never the real run's lives, causes or history for this player's screens.

Look facts up with the tools rather than from memory: `python3 -I world/tools/w9989.py person <name>`, `year <town year>`, `find <text>`, `chain <event id>` for the real run; `python3 -I world/tools/lives_off.py person NAME [FROM TO]` for the off world. Town year = engine year − 37.

## The player

Players are separate agents. You talk to yours only through the messages below, filled in exactly; you add nothing (no hint, no truth, no arm, no encouragement). **Start a fresh player agent for every round**, each with the Agent tool, `subagent_type: general-purpose`, the model the roster gives its id (`sonnet` or `opus`), and wait for its reply before you go on. Never continue a player with SendMessage: a game master whose player is resumed by message is handed back by the harness mid-game. The player loses nothing, since each fresh agent first reads its own memory and the whole game so far, its own acts included. If a player fails, start another with the same message. If the Agent tool refuses because too many agents are running, stop and report to the lead; don't retry.

**Spawn message** (fill `{persona}`, `{id}`, `{run}` with the full run folder path):
> You are a playtester in a paper playtest. You are {persona}. Play as that player and be honest: your boredom, confusion and wish to quit are as useful as your delight, and kindness makes you useless as a tester.
> First read `/Users/oystein/code/Overstory/reviews/lt1/playtests/paper-1/players/brief.md`, which says how a paper playtest works. Then read your own memory file `/Users/oystein/code/Overstory/reviews/lt1/playtests/paper-1/players/{id}/memory.md` if it exists (your notes from games you played before; if it doesn't exist, this is your first game). Then read your opening screen `{run}/r0-screen.md` and write your act file where it says.
> Read and write nothing else: never list, open or search any other file or folder. When the file is written, reply with the single word: done.

**Every later round, a fresh player** gets the spawn message with one sentence added after the memory sentence:
> You are in the middle of a game: read, in order, its screens and your own act files so far: {the files in order, full paths, from r0-screen.md to the newest screen}.

and with "Then read your opening screen ... where it says" replaced by "Then write your next act file where the newest screen says."

**The exit:** after the last screen, which ends with the exit questions, a fresh player gets the round's message with "Then write your next act file where the newest screen says." replaced by:
> Write your exit interview to `{run}/exit.md`, answering every exit question on the newest screen. Then add a section for this game to your memory file `/Users/oystein/code/Overstory/reviews/lt1/playtests/paper-1/players/{id}/memory.md` (create it if it doesn't exist): the game's name as its screens gave it and, in under 200 words, your marks and pull in brief, what kept you, what was hollow, and how it compares with the other games you've played. Keep earlier sections as they are.

**A new game** (calibration's second game; replay): the spawn message as for round 0, with the new game's run folder. The memory file now holds the game before.

**Personas** (`{persona}`):
1. a Football Manager devotee: you love spreadsheets and long saves, and you want systems to master and a club to own
2. a Baldur's Gate 3 and RPG player: you want reactivity, choices with teeth, companions, and your own character's story
3. a cozy-game player (Stardew Valley, Unpacking): you like calm routines, small kind acts, a place that grows, and little punishment
4. an explorer (Outer Wilds, Pentiment, Return of the Obra Dinn): you want to understand, deduce and connect clues, and you hate being told
5. a sharp sceptic: you have played everything, you quit fast, and you name what is hollow. Every round you ask: what am I trying to win or achieve, and what do I risk?
6. an optimiser: you hunt the dominant strategy, the exploit, the loop a min-maxer would grind, and whatever breaks or trivialises the game

If the player's act breaks the brief's shape, resolve what you can and say on the next screen, in one line, what was missing. If it writes something you can't resolve (it asks for a fact no screen could give), resolve the turn as the game would: the interface answers "no record" or the person shrugs.

## A session, round by round

- **Round 0.** The setup gives the opening. Check `r0-screen.md` against the card: the store-page pitch, the tutorial (none for the cold-start kind this wave, `roster.md`), the first screen, the verbs, and the last line `Write your act file to <run>/r1-act.md, up to four turns.` Then spawn the player.
- **Rounds 1 to 6.** Read `rN-act.md`. Resolve its turns in order, following the card's clock, rules and chances. Write `rN-screen.md`: a short result per turn (what the player saw, heard and found, and what changed), the prediction's outcome when it comes due, then the new screen in full, then `Write your act file to <run>/r{N+1}-act.md, up to four turns.` Then send the round message.
- **The time jump** comes where the card puts it, with the return to the same place, shown concretely: what changed, what didn't, who is gone or older, what traces the years left (lives on), or the off world's state (lives off).
- **The memory probe.** The round 4 screen ends, before the act line, with: "Before your turns: what do you remember about <three people met in rounds 1 and 2, by name>? A line or two each, from memory." Choose the three as the card says. Score the answers in `scores.md`.
- **The tenth hour.** After resolving round 6's turns, `r6-screen.md` summarises the next twenty in-game turns as the player's own strategy would play them, honestly: the world's events keep coming, the card's pressures bite, and failure happens if it would. 300 to 500 words. Then the exit questions (below), and no act line.
- **Exit questions** (on `r6-screen.md`): marks for each round 6 turn (in the usual shape); would the tenth hour still hold you; would you keep playing, buy it, come back after a week; what kept you; where you nearly quit; what was hollow; which game does this better; what would you change; **what would you lose if you stopped now?**; and understanding: "What do you believe happened to <two or three named people>, and why?" (named as the card says, people whose stories the player could have read).

A screen is concrete: the place, who is there and what they are doing, what is legible on surfaces, what someone says (which may be wrong), records (which may be out of date), what the player has found, the verbs and interface. 500 to 1,200 words. It never labels anything as engine, simulated or true.

## Honesty

- **Never steer towards fun.** Run the card as written, including its dull parts. Don't reward the player for playing well beyond what the rules give; don't rescue it from failure. Don't add drama the world doesn't have. A dull round is a result.
- **Never invent against the engine.** Lives on: what happens to the world's people comes from world 9989, re-dated, filtered by visibility: a player learns only what a witness could (`engine-rules.md`, Witnesses; atlas, "Before you run it"). Lives off: from the off world only; nobody has reasons, nothing carries, the town has no past, and you may not supply causes, motives or history. In both arms, what the engine doesn't simulate (a match, a gig, an edition's sales, an interview's yield, the player's influence) you simulate by the card's and `engine-rules.md`'s rules, and log as GM-simulated.
- **Chance is seeded.** Every roll: `python3 -I -c "import random; r=random.Random('<slug>-<arm>-<id>-r<N>-t<turn>-<what>'); print(r.randint(1,<sides>))"`. Log the seed and the result.
- **The why-probe** answers only from the record, with its sources: lives on, the causes a witness could know; lives off, "no record" for causes, since the off world has none.
- **Same treatment in both arms.** The same care, length, prose and interface. The only difference is the lives.
- Rule 8: no homophobic, sexist or racial content; state the run's same-sex couples plainly, as the record does.

## Your files (game master only)

Write these in your run folder as you go, not at the end; the player never reads them.
- `gm.md`: the run's truth (the cast, households and facts that matter for this player), its state after each round, and the log: one line per resolution, labelled `ENGINE <event ids>`, `RECORD <record>`, `CARD`, `SETUP`, `GM-SIMULATED <rule; seed; roll>`, or `WITNESS-ERROR <tell chain>`.
- `ledger.md`: **the fact ledger.** Every claim about the world on every screen, one row: `| screen | claim | kind | source | how the player could know it |`. Kind is one of: canonical fact, visual interpretation, texture (stable, seeded, claims no history), perceived information (an account or record, which may be wrong), scene state, GM-simulated. Source is an event id, person id, record, fixture, card or setup line, or the rule and roll. "How the player could know it" names the witness, the record or the visible trace; for a canonical fact that is private and unwitnessed, the row is a fault and the claim must not be on the screen. An auditor checks a sample of rows against the engine and every screen against its rows, so a claim without a row is a fault too.
- `turns.md`: one row per turn: `| round | turn | verb | target | expected | outcome | consequence | mark | surprise |`. Fill `mark` and `surprise` from the next act file.
- `needs.md`: one row per need the player named: `| round | need | met later? (round) | kind |`, kind being engine, world, interface, content or card (your best guess; analysts recode).
- `scores.md`: each prediction (`| round | prediction | due | outcome | right, partly or wrong | cause of a misreading |`), the memory probe (per person: right, partly, wrong, blank), and each exit understanding claim, scored against the engine's record (lives off: against the off world). A misreading's cause is one of: a screen, a wrong record, a witness's error, the player's own leap.
- `condensed.md`, at the end, up to 600 words: the run's arc; turns by verb; the pull by round; the moments it marked engaged or curious, bored, confused or would-quit, and why; the predictions' and understanding's scores; the needs that recurred; the stakes probe's answer; anything you had to simulate heavily or got wrong. No verdict on the concept: the analysts give that.

## When you finish

Check that every file above exists and every screen claim has a ledger row. Then reply to the lead in at most 60 words: the run, rounds completed, the pull by round, the exit's "keep playing / buy" answers in a word each, and any problem (a failed player, a fact you were unsure of). Never commit; the lead commits.
