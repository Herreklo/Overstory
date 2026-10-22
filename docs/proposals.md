# Proposals for the next milestone

Proposals wait here for the next milestone's fresh reviewer, who sees the plan and this page, not the chat. Each one gives its evidence, what it changes, its standing cost (every always-read line costs every session), and what would change our minds. A decided proposal leaves this page and goes into the doc it changes.

## Evidence for Q1 to Q5 (measured 22 October)

- The repo's history starts on 19 October. Since then there have been 378 commits, and 228 of them (60%) touch only docs and reviews.
- There are about 440,000 words in `docs/` and 835,000 in `reviews/`, against about 34,000 lines of code (21,000 Blender, 13,000 Unity). That is about 40 words for every line of code.
- `reviews/lt1/playable/pitches.md` holds about 20,000 words for one pick.
- The paper test took about 14% of a week for 11 runs and gave no verdict.
- The playable corner's Phase 2 was sized at about 16 Opus-days before anyone knew what it had to test. Øystein cut it: "we need to be more sure what to test - before comitting to something like this".
- The cause behind all of it: ideas, plans, rules and documents are nearly free for models to make, while building, playing and looking cost. The work drifts toward the cheap side.

## Q1. Output budgets for each kind of job

- **Change:** each kind of output gets a size, and a brief states it:
  - pitches: at most six, 300 words each;
  - a research study: an In short plus a body of at most 3,000 words, with the sources in a list;
  - a report: at most 500 words;
  - a strict review: at most 800 words.
  A `tools/` check prints any new file over its budget at commit time.
- **Standing cost:** one line in `CLAUDE.md`, and the check.
- **What would change our minds:** a study or review whose decision needed more than its budget. Raise that kind's budget; don't drop the rule.

## Q2. One game concept in test at a time

- **Change:**
  - One concept is in test at a time (today, "Before Friday").
  - New game ideas go to `docs/ideas/parking.md`, one line each, with no new idea doc until the current test answers.
  - Every test starts at the cheapest rung that answers its riskiest assumption, takes about a day, and ends in kill or continue.
- **Standing cost:** none in the always-read files beyond one line.
- **What would change our minds:** a parked idea whose test would answer a question the current concept can't.

## Q3. Rules become tools, and retire

- **Change:**
  - Each rule in `CLAUDE.md` names the failure it prevents.
  - At each milestone, a rule that a tool now enforces leaves the prose. The hashes already enforce determinism, and the Unity lock enforces one Unity at a time.
  - A new rule replaces or merges with an old one.
- **Standing cost:** negative; `CLAUDE.md` shrinks.
- **What would change our minds:** a retired rule's failure coming back with the tool in place.

## Q4. Briefs end in a thing

- **Change:**
  - Every brief's "done" is a render, a number, a walkable build or a played session. A document is a by-product, under Q1's budget.
  - Every report opens with what changed on screen or in play, and if nothing did, it says so first.
- **Standing cost:** one line in the `game-lab-workflow` skill.
- **What would change our minds:** a step whose only honest output is a decision, such as a pick. Its "thing" is then the decision's record, under budget.

## Q5. Two numbers beside Friday's walk

- **Change:** Friday's walk lists what changed on screen since the last one. Beside it go two numbers from a script:
  - the share of the week's commits that touched only docs;
  - the words added to `docs/` that week.
  Work missing from the walk is named as not landed.
- **Standing cost:** a script, and two lines in Friday's note.
- **What would change our minds:** the numbers falling while the walk doesn't improve. Then they measure the wrong thing.

## Q6. The format check covers the whole range of places

- **Evidence:**
  - Øystein, 22 October: "we need to build for the future. do one thing right one time, instead of medium many many times."
  - The plan review's biggest pre-mortem finding was that seven formats are already shaped around stone.
  - P8 checks port steps 4 and 5 against three written records: a House A front, a birch chunk, and a land chunk with water. None of them is a dense city block or a wood.
- **Change:** two written records join P8's three: a dense city block (many fronts, shared walls, many lamps) and a chunk of mixed wood. The light's LA already does this for the light record (`reviews/lt1/playable/outline.md`, 1b).
- **Standing cost:** none in the always-read files. About half an Opus-day before port step 4 opens.
- **What would change our minds:** the two records showing nothing that the three didn't already show.

## Evidence for Q7 to Q11 (22 October)

- Øystein, on making every asset ourselves: "it is very expensive", and he is "still a bit unsure it will look as good as i hope".
- Øystein, on the style: "the key is the balance between enough detail to tell a story, and simplicity without look cheap or boring. This game HAS to look stunning, but not be heavy or slow - very important."
- People already start from free bases: MPFB's CC0 MakeHuman body and Mixamo's clips (`docs/research/characters.md`). Scans are kept for study and form, never as surfaces, since their colour carries the photo's light (`docs/research/land-rock-and-water.md`).
- A post on Opus making 3D took four top-tier plans running for two weeks for one detailed model; its author put photogrammetry into Blender as a 3D reference layer.
- This Mac, the reference machine's class, is an M4 with 24 GB.

## Q7. Free meshes as starting forms for props

- **Change:** before plan step 3, a half-day scout of CC0 and CC-BY meshes for props (lamps, bollards, boats, crates, rope, cast iron): licence, tier budget, and how much fitting each needs to our part contract. A chosen mesh is a starting form, re-fitted or measured and rebuilt by our generator, painted by our materials, judged like any part. Placeholders for greybox play (Kenney, CC0) when a test needs an object not yet made. Never whole buildings, and never a finished look.
- **Standing cost:** none in the always-read files.
- **What would change our minds:** fitting a free mesh costing as much as making the part.

## Q8. Scans as references, found with each step's subject research

- **Change:** each step's subject research includes a search for scans and measured surfaces that match its kind, recorded with source, licence, scale and size: ambientCG's and Poly Haven's height maps for setts and paving, Sketchfab's CC0 and CC-BY heritage scans for steps, walls and kerbs, Kartverket's laser data for the land (1d), DigitaltMuseum's photographs for eras. A generator measures from them; they never appear on screen. Downloads wait for Øystein's OK; Google Earth is looked at, never extracted. Øystein's own phone scans come last, where nothing matches. Poly Haven's CC0 sky HDRIs serve as the sky model's ground truth (L6).
- **Standing cost:** one line in the `game-lab-workflow` skill.
- **What would change our minds:** scans of the wrong kind teaching the wrong wear.

## Q9. Detail where the story is, measured

- **Change:** a tool maps a frame's fine contrast and compares it with where its history facts are. A surface busier than its story fails, and so does a story point too quiet to read. It joins the eighth-size value read (VD2) in every target frame (L2) and strict review, before eyes.
- **Standing cost:** a tool, and a line in `docs/measuring.md`.
- **What would change our minds:** frames that pass it and still read as busy or empty to the strict reviewer.

## Q10. Vision models for the checks, later

- **Change:** after the light (1c), a test of SAM 3 and DINOv3 for segmenting renders, so each material's value spread and detail map are measured without hand masks. Licences checked and downloads approved first.
- **Standing cost:** none until adopted.
- **What would change our minds:** hand masks from the generators' own ids doing the same job.

## Q11. Local models, only if the mechanical share is large

- **Change:** `tools/usage_scan.py` measures what share of usage is mechanical work a check proves (renders, exports, hashes). Only if it is large does a local model for that work become a proposal, run when no frame time is being measured.
- **Standing cost:** one measurement.
- **What would change our minds:** the share being small, as the 20 and 21 October measurements suggest (context re-reading a third, helpers nearly half, Fable a sixth).
