# The playable corner: the brief

Agreed with Øystein on 22 October, waiting to be started from the desktop app (sessions can't be started over Remote Control). Øystein: "lets be creative with how we solve it, and how we solve the greybox testing in a great way. We could also build more of the city if its cheap, and just clay?" and "If we are doing playtesting, we actually need to be able to play - right? not just inspect unfinished blocks". Also: the nice-looking work goes on beside the clay (see the end).

## The task

Build a Mac build Øystein can open and play. It is LT1's harbour town in 1989, in clay, with the corner at today's quality inside it and one short playable case. Start with `CLAUDE.md`, then `NOW.md` and `docs/visual-direction.md`, and follow the `game-lab-workflow`, `unity-conventions`, `blender-generators` and `engine-bridge` skills.

**Unity is not yours yet.** The gully port session is finishing step 2a and a docs pass in this checkout, then writes its handover in `NOW.md` and stops. Until that handover is in `NOW.md` and no Unity, perf-player or Blender batch process runs, do only the design work below and touch nothing under `unity/`. Wait on real pids, never on a `pgrep -f` pattern, which can match the waiting shell or a log watcher. After that, only one process uses Unity at a time.

## Phase 0, design (no Unity)

1. **A wide creative round.** Use fresh Opus agents in roles. Generate many pitches, including ones no reference has done, for two things:
   - **The first case:** 15 to 20 minutes, built from real simulated lives in the engine's published records (read-only, via `engine-bridge`; `fixtures/`), where reading the world is the skill that pays.
   - **How greybox testing works.**

   Treat as constraints:
   - the game rule in `CLAUDE.md`: goals, challenge, stakes, mastery, failure, and decisions that cost something;
   - `docs/ideas/first-game-options.md`, where the panel ranked the paper and a death in the town on top;
   - `docs/playtests/paper-1/analysis/interim.md`: no concept held its players (exit interest about 3 of 10), and the needs it found were kin, what moves the paper's meters, and who found and certified the dead;
   - the "In short" sections of `docs/research/play-craft.md`, `interface-and-inspection.md`, `camera-and-composition.md`, `collision-and-navigation.md`, `playtesting.md` and `ai-playtesting.md`.
2. **Testing design.** One strong option, to weigh, not assume: one deterministic game core, with the rules and facts in code, not in a game-master agent (the paper playtests' game masters leaked and invented facts). Agent players play the real build through a command port. Each turn the build returns the rendered frame the player sees plus the interface text, and takes moves such as go to, look at, ask, note and choose. Personas cross models, every run replays exactly, and telemetry records where players walk and what they look at. Øystein plays the build himself. Humans other than Øystein enter only through the engine's own human test.
3. **The pick.** Fable picks the case and the testing design from a lean packet of the best three or four pitches. Write the experiment's question, how it is judged and what would change our minds at the top of `docs/experiments.md`, then commit and push.
4. **Outline the build, then a pre-mortem.** A fresh reviewer imagines it failed six months on and says what a lead technical designer would say we are missing. Fix the outline, then build.

## Phase 1, the walk (about two working days once Unity is yours)

- The town in clay, across as much of `docs/town-plan.md` as is cheap: land, lanes, steps and plain blocks for houses, from the clay tools that built the heart.
- Inside it, at today's quality:
  - the corner's houses from the house generator at 1989 (test quality, from their diaries);
  - the gully steps and cheek walls at the accepted baseline (stairs `bff7858b698f3efd`, walls `0a3d7db3100df20b`; change neither);
  - the birches, and the light and two or three moods.
- A walker at eye height with collision, and keys for the judging views in `docs/foundations.md`.
- An on-screen frame time, and the harness's whole-scene run at the judging views (`docs/measuring.md`). Name its three biggest costs: they go to the frame-rate gate (`docs/plan.md`), and the port keeps its own order.

## Phase 2, the play

- The picked case in greybox: blockout people at their places from the records, a placeholder interface, a way to win and a way to fail.
- The command port and two or three agent players, as designed.
- A short results note in this folder.

## Rules and done

**Rules:**
- The engine decides facts, so the scene invents no history, and a read of character is shown as someone's fallible account.
- Everything is seeded and deterministic.
- Rough is expected in the clay; polish waits.
- Do a self-check against the core rules, then one strict review on Fable at each phase's end, from a lean packet (a capture and four stills at judged size).
- Use Opus for building and research. Hand over to a fresh session from `NOW.md` near 200k of context.

**Done:**
- the build in `unity/Builds/Playable/` (not tracked);
- a one-minute capture and stills in this folder;
- what we keep and drop in `docs/experiments.md`;
- `NOW.md` updated, saying the port resumes next week inside this scene;
- commits on `lt/1-harbour-street` as `LT1: …`, pushed after each step.

## Beside the clay: the look

The look goes on in the same town, not apart from it. Every real part replaces its clay in place, so the town is both the greybox and the showcase.

- **The light and the air on the clay.** The sky, the haze, the moods and the painted far town are shared systems that no later part change throws away. This is plan step 1c, the light's lasting fix, on the stone's critical path. Interleave it with Phase 1.
- **The stone completed end to end first.** Nothing is complete yet: the birches closed only as a look test, on cards the reference machine draws dearly; the stone is in the port; the houses exist only at test quality. So no new kind starts at quality until the stone is done. Done means the port's steps 0 to 7, the four known faults fixed, the look at the bar against its target frame at every judging view, distance and light, and Øystein's acceptance. The port resumes inside the corner next week. Per-pixel history costs about 0.04 ms (R2c).
- **Then the plan's order:** the birches re-fitted (1e), then House A (step 2). The house-front research done now (`docs/research/house-fronts.md`) feeds the port's shared foundations (materials as pack records, levels, chunks), so they don't come out stone-shaped. It doesn't start the house.
