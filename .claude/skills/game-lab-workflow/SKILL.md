---
name: game-lab-workflow
description: Use when planning, running, judging or recording a look test or any visual or game experiment in the Game Lab (Unity, Blender, the world view, scenes, characters).
---

# Running an experiment in the Game Lab

Every piece of visual or game work is an experiment. One experiment per session.

## Before building

Write a short entry at the top of `docs/experiments.md`:

- **Name and number:** `LT1: first street and first scene`.
- **The question:** what we want to find out, in one sentence. "Does soft toon shading read well at three times of day from the neighbourhood camera?"
- **How it is judged:** what Øystein will look at, and what would count as a yes. Name the camera, the times of day and the seeds.
- **What it does not test:** keep the scope honest.

Then outline the build in a few lines and wait for agreement before building anything large.

## Building

- Build generators and parameters, not single assets (see the `blender-generators` skill).
- Follow the Unity conventions (see the `unity-conventions` skill). Everything visual is seeded and deterministic.
- Use fake engine data from `fixtures/` until the engine export exists (see the `engine-bridge` skill).
- Keep the experiment in its own scene and folder: `Assets/Experiments/LT1/`.

## Ending

Every experiment ends in something to judge, made in Unity, never only in Blender or as a concept image:

- **Contact sheet:** a grid of renders from fixed cameras, the same for every variant being compared, saved to `reviews/LT1/`.
- **Variety check, when the experiment generates things:** 30 random items from a fresh seed. Do any two look the same? Does each visual difference say something true (era, wear, wealth, owner)? Does the same seed give the same result after a reload?
- **Light check:** morning, a grey afternoon and evening. The world must look good in ordinary light, not only at sunset.

Send the contact sheet to Øystein and ask for his judgement. Do not judge beauty yourself and call it done.

## Recording

After Øystein has judged, record in `docs/experiments.md`:

- What we keep and what we drop, and why, in a few lines.
- For each reference that came up: what we take from it and what we leave.

Then update `docs/visual-direction.md` so it describes the current direction: only what we now believe, no history. History lives in `docs/experiments.md` and git.

Update `NOW.md`: what is open, what is next.

## Things to push back on

- Judging a style from a single beautiful frame.
- Adding detail everywhere instead of where the story is.
- Dramatic light hiding weak shapes.
- Variety that encodes nothing.
- Anything that would need Unity to decide something the engine should decide.
