# Now

What is open and what is next. Update this block when an experiment starts or ends.

- **Open:** LT1, the harbour street in 1989 (`docs/experiments.md`), on branch `lt/1-harbour-street`.
  - *Done:* the building system's Python prototype (`blender/resolver`, `blender/generators`): diaries resolve to plans and plans to meshes, at strengths gentle, strong and stronger. Every building is checked (`validate.py`), and the stress test (`blender/tools/stress.py`) passes on 1,564 random buildings at strong and stronger.
  - *Waiting on Øystein:* strong or stronger, from `reviews/lt1/` (the strong-against-stronger sheet). The choice becomes the default in `blender/resolver/eras.py` and is recorded in `docs/experiments.md`.
  - *Next step:* LT1's Unity part. Create the Unity 6 URP project in `unity/`, import the street (export each fixture building at 1989 as FBX from Blender with the chosen strength), lay the street on a quay with cobbles, lamps and simple water, then build the four looks (A–D), three lights and two cameras described in `docs/experiments.md`. Run it from Claude Code on Øystein's Mac, where Unity and Blender run.
- **First command for a new session:** read this file, `CLAUDE.md` and `docs/experiments.md`, run `blender/tools/stress.py --n 50 --styles strong,stronger` with Blender's Python to confirm the generator works, then start the next step.
- **Next:** the people deep dive, before LT2 (one person, three stylisations; decide on commissioning a stylised base). LT2, a small venue at night with two people talking. LT3, the street through the years, with seasons and weather.
- **Research:** `docs/research/`, including the reality check (`docs/research/reality-check.md`) that sets the order of bets. Game ideas in `docs/ideas/`.
- **Engine:** places are workplaces plus ventures that open new ones; places never close and buildings are not modelled. Tag `rH28` has a read-only front door, showing the truth, for our tools. The engine's order (its `SUMMARY.md`, 21 October) is rounds 42 and 43, then homes (#59) with our front door's part two (#22), then the band for a year; the accounts arc (#20) and the start year (#23) are paused. LT1 and LT2 run on fixtures labelled `authored`. Details in `docs/engine-requests.md`.
- **Shared goal:** `CLAUDE.md` ("What it is for") states Overstory's question and draft exit criteria, to agree with Øystein. The band is proposed as a shared milestone with the engine (`docs/engine-requests.md`, open items).
