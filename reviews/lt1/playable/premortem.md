# The playable corner: the pre-mortem

It is April 2027 and the corner has failed. This covers Phase 1 and the ladder; the stories about a Phase 2 build wait for the sizing decision. Ranked by likelihood times cost, and checked against the code and the fixture on 22 October.

## 1. Failure stories

**1. The stills flattered.** Likely. Sixteen days get committed to a clue that does not read.
- 2b poses capsules at the three moments of the climb, with nobody else on the steps.
- Blue hour stands in for 18:00 in November, when it is fully dark.
- A player would watch hours among passers-by; reader A is handed the event. One reader passes both 2b and test 3.
- 2a's line of sight omits the birch at (44.5, 28.0), the stone walls and A's windows.

**2. The tie script measured the export.** Likely. A false kill or a false pass.
- The events start in January 1989, so Hannah's ties are her son, Ben Reed and Agnes.
- The sweep skips the authored hours, which decide who can be reached when.
- Seed B stands on ten years of events, so it is no clean holdout.
- The same script referees test 4, so one bug passes both.

**3. The paper run tested a primed player.** Certain as written.
- Øystein has read both answers (`pick.md`; `docs/experiments.md:55`), so "was the vantage a bet?" has no honest answer.
- Paper turns hours of watching into three stills, so the "watching" kill cannot fire.
- Question 2 prompts the trade-off he must name unprompted.

**4. The walk missed Friday.**
- 1a is 25 to 38 build hours under one lock by Friday.
- Fable's own limit was full on Wednesday, so W7's review may fall to Opus.
- *Sign:* W1 is not done tonight.

**5. The lock and the limit.** Phase 1 is 1.3 to 1.9 weeks of the limit, beside the port's 2b, and L6 is unsized. *Sign:* still unsized by mid-November.

**6. The readers measured hedging.**
- There is one Sonnet reader per arm.
- Hannah lives on the steps below E, so reader B's "tell the neighbours" names her anyway, and the pass turns on the word "unsure".

**7. The facts check found only its list.** It misses whole classes:
- Years that were never shifted: 136 event texts and 232 cause labels, such as "every week (2024)" in e-6400.
- Authored hours against jobs and habits.
- Ages after the shift: Hannah is 74.

## 2. What a lead technical designer would say is missing

- **A hold-out nobody has read.** The run has four deaths; keep one unread for Øystein.
- **Base rates.** A clue counts only when it is found among the town's other movements.
- **Unit tests before a referee.**
- **Each rung's limit stated:** stills say nothing of motion, and paper nothing of the screen.

## 3. The claim check

| Claim | Verdict | Source |
| --- | --- | --- |
| Phase 1: `Stage`, `Views`, `PlantBirch`; `LT1Perf` needs a scene path; the sidecar; beams 64 ms, haze ≤1.5 | True | `LT1Stone.cs:334, 358`; `LT1Perf.cs:84, 164`; `measuring.md:212`; `r2.md:60` |
| `PerfRunner` takes `-perf-scenes playable` | Unclear: its scenes are setups inside the perf build | `PerfRunner.cs:186, 238` |
| The Anchor exists to cast | True (`pl-bar`) | fixture |
| `heart_layout` gives footprints for line of sight | Partly: heights, roofs, ground and retaining walls, but no openings, birch or stone walls; needs Blender's numpy | `heart_layout.py:246, 932` |
| 1989's coworkers rebuild from hired, retired, left | Partly: no place field, only text; "left" means the town; `startover` and `stepdown` missed | fixture |
| Peter owns the café in 1989 | True, but the source is e-6908 ("step down as owner", 1991), not e-6545 or e-7137 | fixture |
| Olive at the Anchor in 1989 | Derived from e-8736's "ten years"; no hire event | fixture |
| The ladder's ties; one café | True | fixture |

## 4. Fixes still open

**Must:**
1. **Test 4 on an unread death,** his account recorded before the questions (0.1 d).
2. **2b unposed** (+0.1 d):
   - fixed clock times across each evening;
   - distractor residents;
   - `LT1Heart.NightRig` for the night;
   - its own reader.
3. **Test 1** (+0.1 d):
   - sweep the hours by an hour either side;
   - report tie counts first;
   - three toy cases before it referees;
   - a fail from thin ties goes to Øystein as an engine question.
4. **Test 5 by class:** every authored field and every showable string (+0.05 d).
5. **Test 3:** a forced first telling with a confidence for each name, three readers per arm (+0.05 d).

**Should:**
- 2a adds the birch, the stone walls and A's real window, and is checked against a 2b still.
- Rosters are parsed from text with tests, labelled derived.
- W3 places the runner.
- W7 notes any review run on Opus.
  - W7's strict review was not run on Fable or Opus: Øystein's own verdict on 22 October replaced it (the frame rate "laggy and jumpy", the climb "a bit boaty", the stairs "very buggy and not nice"; `walk/w7-report.md`).

## 5. Keep

- The freeze.
- Kills as scope questions.
- Tests 5 and 1 first.
- The one-day box.
- Phase 1's fixes as they stand.
