---
name: engine-bridge
description: Use when the game needs to know what the Understory engine simulates, when designing or reading the data the engine exports (places, people, events), when writing fixtures, or when the game needs something the engine does not provide yet.
---

# The bridge to the Understory engine

## What the engine is

Understory (`Herreklo/Understory`) is a deterministic simulation of people, written in TypeScript. It decides everything that happens: who people are, what they choose and why, who knows whom, what places exist. Every decision carries its reasons. It runs a small town in full and is being extended to a city of 100,000, where neighbourhoods in focus run month by month and the rest in the background.

The game only shows what the engine decides. The engine never depends on the game.

## Never change it

Understory is a work in progress run from its own project. From here:

- **Never clone it.** A local copy loads the engine's own instructions into the session and gives something to push from.
- **Never push, branch, or open issues or pull requests on it.** Never run its rounds or scripts. Comments on its issues labelled `overstory` are allowed when Øystein asks.
- **Read it only through the GitHub API**, which cannot write:

      gh api repos/Herreklo/Understory/contents/NOW.md -H "Accept: application/vnd.github.raw"
      gh api repos/Herreklo/Understory/contents/src -q '.[].name'

- **What the game needs goes in `docs/engine-requests.md`** in this repo: what is needed, why the game needs it, and what the player would see. Øystein takes it to the engine project.

## Reading it

- Its current state first: `NOW.md`, `docs/STATUS.md`, `docs/ARCHITECTURE.md`; for the city, `docs/scale/level-of-detail.md`.
- Then the code you need: `src/world.ts` (world and person state, time), `src/setting.ts` (places and setting content), `src/projects.ts` (ventures that open places), `src/life.ts` (the month).
- **Do not trust memory of the engine.** It changes every round. Check the code.

## What it knows today

- **Time** runs in months (`t`). Today the simulated past starts in 1996 (`YEAR0`); the present begins thirty years later. The start year is to come from the setting pack (#23), so a world shown in 1989 starts its people in 1959. Buildings older than the people come from the fabric pass, not from the engine.
- **Places** are workplaces with string ids (`'mill'`, `'harbour'`), each with a kind, capacity, staff and a leader. Every neighbourhood has one of each kind the setting has. A venture (a café in the old bank) opens a new place in its founder's neighbourhood.
- **Buildings** are not modelled: a place has no building, era, extensions or condition.
- **The setting** is a placeholder coastal town with English names. Names and kinds of place are setting content and can be swapped.

## The front door

- **Tag `rH28`** has the engine's read-only front door (`src/boundary.ts`). Its reads show the truth, so they serve our tools (the diary inspector, the bridge schema), never anything a player sees.
- **Part two (#22)** will add the places of a neighbourhood at a month, people as the player could know them, habits, and the first player command. Until it lands:
- The draft format lives in `docs/engine-contract.md`: places (building and business), people present, and recent events, each with ids that stay stable.
- Fixtures in `fixtures/*.json` follow the draft exactly, with every record labelled `authored`. Every field in a fixture that the engine does not produce today is listed in `docs/engine-requests.md`.
- Keep the draft small: only what an experiment actually uses.

## How the game will run with the engine

The engine runs beside Unity as its own process. Unity asks for a snapshot of a neighbourhood and recent events, and sends player actions back as commands the engine can accept or refuse. A save holds the engine and ruleset version, checkpoints and the player's commands. Unity never holds the truth about the world.
