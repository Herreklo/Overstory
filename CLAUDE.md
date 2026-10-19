# Working in the Game Lab

Every session that works here reads this first, then `NOW.md`.

## What this repo is

Overstory: the game and visual lab built on the Understory engine (`Herreklo/Understory`). It finds out what the simulated world should look like and how it should be played. The engine decides what happens; this repo only shows it.

## What it is for

Understory asks what a persistent world of developing people makes possible (its `WHY.md`). Overstory's part of that question: **can someone read people and history better from the world on screen than from the engine's page?** Beauty serves that. A look that is stunning but tells nothing true has failed; a world that is consistent but feels empty has failed too.

When Overstory is good enough to build a game on (draft, to agree with Øystein):
1. A building's history reads at a glance: a viewer can say which parts are old, changed or neglected, and is right.
2. A person is recognisable across scenes and years.
3. A scene shows a consequence the page does not make obvious.
4. In a blind test, viewers prefer the scene to the page for understanding what happened, and are not misled by it.
5. A street at city scale holds its look and its frame rate.

Each experiment moves one of these, or it does not run. Its question, how it is judged and what would change our minds are written before it is built.

## Start of every session

    git fetch origin && git switch main && git pull --ff-only

Read `NOW.md`. If it names an open experiment's branch, switch to that branch and pull it: an experiment's work lives there until it is merged. Read `docs/visual-direction.md` before any visual work.

## How work runs

One experiment per session, on its own branch (`lt/1-first-street`), following the `game-lab-workflow` skill:

1. Write the experiment's question and how it will be judged at the top of `docs/experiments.md`. Commit and push.
2. Outline the build; build once agreed.
3. End in something Øystein can judge in Unity: a contact sheet, a render or a playable scene, in `reviews/`.
4. Record what we keep and drop in `docs/experiments.md`; update the design docs to describe the current direction.
5. Merge to main and update `NOW.md`.

## Standing rules

- **The engine decides, Unity draws, Blender builds the parts.** Unity never invents a fact about the world.
- **Understory is never changed from here.** It is a work in progress run from its own project. Never clone it, push to it, or open branches, issues or pull requests on it. Read it only through the GitHub API (`engine-bridge` skill). What the game needs from it goes in `docs/engine-requests.md`. Comments on engine issues labelled `overstory` are allowed when Øystein asks.
- **Generators, not single assets** (`blender-generators` skill).
- **Seeded and deterministic** (`unity-conventions` skill): the same building looks the same until its history changes it.
- **Visuals may elaborate world facts, but may not contradict them or falsely claim a causal history.** Five kinds of thing are on screen: canonical facts (from the engine), visual interpretations of facts (a shabby front from age and upkeep), non-semantic texture (stable, seeded, claims no history: woodgrain, a lean, minor clutter), perceived information (a person's account, which may be wrong), and local scene state (committed back to the engine only when it matters). Anything that reads as history must be a fact.
- **Judged in the engine,** never on concept images.
- **Evidence, not verdicts.** The screen shows what was seen and heard. A read of someone's character is someone's opinion, shown as fallible, never as the game's truth: a vivid act read as a whole character makes readers worse (Understory's human test).
- **The setting is a pack.** The harbour town, its era content and its look sit on top of the engine; the engine stays general and assumes no country.
- **Rule 8:** no homophobic, sexist or racial content.

## Models

Choose the model by the kind of work, and say in one line when a step calls for a different one. Helper agents get the model their job needs.
- **Fable 5.1:** decisions that shape the project, and judgement: what an experiment proves, system and fitting rules, art direction, judging renders, checking reviews against the code.
- **Opus 5.5:** building once designed: generators, the Unity side, debugging, docs.
- **Sonnet 5.5:** mechanical work with a check behind it: batch renders, moves, exports and status that the stress test or a hash proves unchanged.

## Docs

`docs/` describes the current design: how it works and why. History lives in `docs/experiments.md` and git. No rejected alternatives.

| File | What it holds |
| --- | --- |
| `docs/visual-direction.md` | The current visual direction |
| `docs/living-world.md` | How places, people and history are shown |
| `docs/building-system.md` | How buildings are generated from dated diaries |
| `docs/experiments.md` | Every experiment: question, outcome, what we keep and drop |
| `docs/engine-contract.md` | The draft format of the engine's data for the game |
| `docs/engine-requests.md` | What the game needs from the engine |

Skills for this repo live in `.claude/skills/` and change with the design: `game-lab-workflow`, `blender-generators`, `unity-conventions`, `engine-bridge`.

## Practical

- Unity project in `unity/`, Blender generators in `blender/generators/`, fixtures in `fixtures/`, contact sheets in `reviews/`.
- Large binary files (renders, FBX) go through Git LFS.
- Commit messages: `<experiment>: <what changed>`, e.g. `LT1: shopfront generator, 1930s set`.
