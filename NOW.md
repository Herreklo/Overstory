# Now

What is open and what is next. Update this block when an experiment starts or ends.

- **Open:** LT1, the harbour street in 1989 (`docs/experiments.md`), on branch `lt/1-harbour-street`.
  - *Done:* the building system's Python prototype (`blender/resolver`, `blender/generators`): diaries resolve to plans and plans to meshes, at strengths gentle, strong and stronger. Every building is checked (`validate.py`), and the stress test (`blender/tools/stress.py`) passes on 1,564 random buildings at strong and stronger.
  - *Shape step done:* Øystein picked stronger. It is `DEFAULT_STYLE` in `blender/resolver/eras.py`.
  - *Unity step, under way:* the project, export, street, quay, look A, the drizzle light and both cameras stand. The checkpoint frames are in `reviews/lt1/checkpoint/`. To rebuild: run `blender/tools/export_street.py`, then `LT1Setup.Project` (once), `LT1Setup.Scene` and `LT1Render.Checkpoint` in Unity batch mode (see the scripts' headers).
  - *Waiting on Øystein:* the checkpoint, and whether surface materials (texture, wear) come before looks B–D.
  - *Then:* looks B–D, the winter-sun and blue-hour lights, the blind contact sheet with camera moves, then the variety check.
- **First command for a new session:** read this file, `CLAUDE.md` and `docs/experiments.md`, run `blender/tools/stress.py --n 50` (default strength) with Blender's Python to confirm the generator works, then start the next step. Close the Unity editor on `unity/` before running it in batch mode.
- **Next:** the people deep dive, before LT2 (one person, three stylisations; decide on commissioning a stylised base). LT2, a small venue at night with two people talking. A research pass before LT3: what owners did to houses from 1900 to 1989, decade by decade, which becomes the diary's event vocabulary and the era shelves. LT3, the street through the years, with seasons and weather; the bar is in `docs/experiments.md`.
- **Research:** the Project's `research/` docs, including the reality check that sets the order of bets.
- **Engine:** places are workplaces plus ventures that open new ones; places never close and buildings are not modelled. Tag `rH28` has a read-only front door, showing the truth, for our tools. The engine's order is housekeeping, then the accounts arc (#20), then our items (#22, then #23). LT1 and LT2 run on fixtures labelled `authored`. Details in `docs/engine-requests.md`.
- **Shared goal:** `CLAUDE.md` ("What it is for") states Overstory's question and draft exit criteria, to agree with Øystein. The band is proposed as a shared milestone with the engine (`docs/engine-requests.md`, open items).
