# What changed here?

You are taking part in a reading test. You will be shown pictures of one corner of a town in four years: 1989, 2000, 2010 and 2020. They show the change in one particular way, described below. Answer as someone who has lived all their life on streets like this one: you know houses as a neighbour does, not as an expert.

- Read only the files in your folder: {FOLDER}. Do not open, list or search any other file or folder on this computer, and do not use the web.
- Where you are unsure, say so; a confident wrong answer counts against the test more than an honest "unsure". Give each answer a confidence: 1 (a guess), 2 (fairly sure), 3 (sure).

The five houses, A to E, stand on a stepped lane that climbs from a harbour's quay road:
- A: on the quay road at the foot of the stepped lane, on the left of the lane as you look up it.
- B: on the quay road at the foot of the stepped lane, on the right of the lane as you look up it.
- C: halfway up, on the left, beside the landing where the lane turns.
- D: halfway up, on the right, on top of the rock outcrop above the landing.
- E: at the top of the lane, the small house that closes the view up it.

`locator-city.png` shows the corner from above with the houses lettered.

{WAY}

**Task.** For each pair of years (1989 to 2000, 2000 to 2010, 2010 to 2020), list what changed on the five houses: one short claim each, with the house, what changed, why you think it changed if you can tell, and your confidence. List only what you see. Then say in one or two sentences how well this way of showing the change let you see it, and what, if anything, it made you believe that the pictures do not show.

Answer with one JSON block, and nothing after it:

```json
{"changes": {"1989-2000": [{"house": "A", "what": "...", "why": "...", "confidence": 2}], "2000-2010": [...], "2010-2020": [...]},
 "how_well": "...", "believed": ["..."]}
```
