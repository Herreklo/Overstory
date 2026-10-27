# Now

What is true today and what is next, in under 500 words. History is in `docs/experiments.md` and git; each decision is in its design doc's In short.

## The test (Øystein, 27 October)

Can the town be affected by its people and its environment over the years? Understory tells the inner story (friendships, goals, dreams, personalities). Overstory reflects it, so together they make a living world that can carry different kinds of games. Meanwhile it must look stunning, and stunning can mean many things (`CLAUDE.md`, What it is for).

## Where we are (27 October, evening)

- **All build work is paused** while Øystein reviews the direction. Nothing is running.
- **The research is done:** what Claude has made with Blender and Unity, and how good it looks. The coordinator is writing the review for Øystein: what is realistic, what looks amazing, what we build next. Nothing restarts until he has answered.
- **The style is open again.** The art direction (`reviews/lt1/art-direction/README.md`, painterly realism in Stålenhag's line, stylised hard) was judged from one camera only, so its frame is a stage set, not a proven look. Øystein: "stunning could mean a lot of things".
- **The painted corner:** a hook for elements, a scene (`unity/Assets/Experiments/LT1/Corner/LT1_PaintedCorner.unity`), an app (`unity/Builds/PaintedCorner/`) and a rebuild script (`tools/painted_corner.py`). The app still has half-made elements in it: grass in the sky, a void ground, floating houses. It does not go to Øystein again until it holds from every view.
- **The paused elements,** each at a pushed point and none judged:
  - the houses as hero assets (handover: `reviews/lt1/houses/hero/handover.md`);
  - trees `5074681`;
  - growth `5041e3e`;
  - rock and ground `b56d316`.

## Rules learned this week

- Every element is judged from all four views (eye level, the street stop, 12 m, high), never from one camera.
- Nothing goes to Øystein that the coordinator has not looked at from all four.
- Make, look, fix, with no admin (`CLAUDE.md`, How work runs).

## Held until the direction is set

- **The playable corner's case (1g)**, the zoom test and the camera milestone: `reviews/lt1/playable/`.
- **The gully port at 2b:** the three stones are at v1 (`9600ac4`); what is left is in `reviews/lt1/port-handover.md`.
- **The frame rate:** the eye-on view is over 16.7 ms in every light, with the cures named in `reviews/perf/2026-10-27/frame-rate/README.md`. The full-screen timing runs only when Øystein says the Mac is free.
- **The paper playtests**, stopped at 11 of 24: `docs/playtests/paper-1/analysis/interim.md`.

## Waiting for Øystein

- The review's answer: the direction, and what we build next.
- Installing Unity's IL2CPP module when the port's step 5 needs it. Recommended: yes.
- Which game comes first. Nothing is decided; ideas are in `docs/ideas/README.md`.
- The exit criteria in `CLAUDE.md`, a draft to agree with him.
- Reference images and assets wait for his yes, file by file. Public slides, papers and captions have a standing OK (`docs/research/downloads.md`).

## Engine

Round 41 is kept. The human test comes after round 42, homes after round 43. The real run is `fixtures/engine/understory-world-9989.json` (119 people, 2,635 events, 2026 to 2036). Requests: `docs/engine-requests.md`.
