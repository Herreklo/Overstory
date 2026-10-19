# Working in the Game Lab

Every session that works here reads this first, then `NOW.md`.

## What this repo is

Overstory: the game and visual lab built on the Understory engine (`Herreklo/Understory`). It finds out what the simulated world should look like and how it should be played. The engine decides what happens; this repo only shows it.

## Start of every session

    git fetch origin && git switch main && git pull --ff-only

Read `NOW.md`. Read `docs/visual-direction.md` before any visual work.

## How work runs

One experiment per session, on its own branch (`lt/1-first-street`), following the `game-lab-workflow` skill:

1. Write the experiment's question and how it will be judged at the top of `docs/experiments.md`. Commit and push.
2. Outline the build; build once agreed.
3. End in something Øystein can judge in Unity: a contact sheet, a render or a playable scene, in `reviews/`.
4. Record what we keep and drop in `docs/experiments.md`; update the design docs to describe the current direction.
5. Merge to main and update `NOW.md`.

## Standing rules

- **The engine decides, Unity draws, Blender builds the parts.** Unity never invents a fact about the world.
- **Understory is never changed from here.** It is a work in progress run from its own project. Never clone it, push to it, or open branches, issues or pull requests on it. Read it only through the GitHub API (`engine-bridge` skill). What the game needs from it goes in `docs/engine-requests.md`.
- **Generators, not single assets** (`blender-generators` skill).
- **Seeded and deterministic** (`unity-conventions` skill): the same building looks the same until its history changes it.
- **Variety must be readable:** every visual difference carries something true.
- **Judged in the engine,** never on concept images.
- **Rule 8:** no homophobic, sexist or racial content.

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
