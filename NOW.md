# Now

What is true today and what is next, in under 500 words. History is in `docs/experiments.md` and git; each decision is in its design doc's In short.

## The test (Øystein, 27 October)

Can the town be affected by its people and its environment over the years, and look stunning meanwhile (`CLAUDE.md`, What it is for)?

## Where we are (28 October)

- **The town failed, then one house (109) did not reach the bar.** Light and air could not carry box houses (r34–r36), and 109's three rounds read as CAD.
- **Øystein's decision (28 October): start the building completely from scratch, keeping the learnings.** "You keep on adding too many triangles ... the finishing you can not do." The old house code, the painted corner and the town's code left HEAD; git keeps them. What they taught is in `docs/research/house-lessons.md`; how games build a house is in `docs/research/house-asset-craft.md`.
- **Now: the finishing test.** One corner of house 107 (1828, boarded and left in 1986), built the games' way (mid-poly, real chamfers, at most 3,000 triangles) and finished three ways: our own procedural marks, CC0 scans pushed into our style, and both. Judged in clay beside `docs/references/houses/09-pedersgata-81-derelict-1989.jpg` from all four views; the coordinator looks at every round. If one way holds, 107 is built that way, alone in its own scene. None held after three rounds (the blind critic: "far", `reviews/lt1/finish/r03/critic.md`; the mesh and light hold, the marks don't). Øystein, 28 October: one more round, A with a small library of authored marks (a ply face, a flake atlas) placed by the baked masks, the sheet first. Round 4: far again ("a freshly clad white shed", `reviews/lt1/finish/r04/critic.md`); the model holds, the photo-matched surfaces don't. **Øystein, 28 October: keep the model, paint the surfaces** (a few broad designed value shapes by `reviews/lt1/art-direction/README.md`, judged blind against the painted references and the story), one round. P's critic: far ("a clean CG clapboard kiosk"; this approach can reach Firewatch and Dredge, not Stålenhag by UV marks); Øystein: "the best thing you have made". Round p2 builds on P with the critic's one change, and ends with one colour still (Øystein, 28 October: a single exception to clay-first). Øystein, 28 October: our own look ("firewatch and dredge ... already exist"), "use color and light in a stunning way", and "build a system that is easy to expand on". Next, after p2 (Øystein, 28 October: "Yes"): a short street, 107, 108 and 109 built from their facts by one system, in colour and one designed light with clay twins, to prove the recipe expands with no hand-tuning per house. Session: "Painted finish: house 107's corner".
- **Clay first, colour last (Øystein, 28 October).** Every kind is made in clay, each material at its own lightness in grey with real relief and gloss. Colour goes on everything in one pass once a clay ensemble holds from all four views (two houses, a tree, ground with rock, the quay with water).
- **The style stays** (`reviews/lt1/art-direction/README.md`, painterly realism in Stålenhag's line, stylised hard).
- **The paused elements,** each at a pushed point and none judged: trees `5074681`, growth `5041e3e`, rock and ground `b56d316`. With the corner gone, rock, ground and growth have no Unity scene until the clay ensemble hosts them.

## Held until the direction is set

- **The playable corner's case (1g)**, the zoom test and the camera milestone: `reviews/lt1/playable/`.
- **The gully port at 2b:** the three stones are at v1 (`9600ac4`); what is left is in `reviews/lt1/port-handover.md`.
- **The frame rate:** the eye-on view is over 16.7 ms in every light, with the cures named in `reviews/perf/2026-10-27/frame-rate/README.md`. The full-screen timing runs only when Øystein says the Mac is free.
- **The paper playtests**, stopped at 11 of 24: `docs/playtests/paper-1/analysis/interim.md`.

## Waiting for Øystein

- Installing Unity's IL2CPP module when the port's step 5 needs it. Recommended: yes.
- Which game comes first. Nothing is decided; ideas are in `docs/ideas/README.md`.
- The exit criteria in `CLAUDE.md`, a draft to agree with him.
- Reference images and assets wait for his yes, file by file. Public slides, papers and captions have a standing OK (`docs/research/downloads.md`).

## Engine

Round 41 is kept. The human test comes after round 42, homes after round 43. The real run is `fixtures/engine/understory-world-9989.json` (119 people, 2,635 events, 2026 to 2036). Requests: `docs/engine-requests.md`.
