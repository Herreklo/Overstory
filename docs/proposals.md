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
