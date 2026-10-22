# The docs trim's question test: the score

P5 of the plan review (`docs/research/plan-review-2026-10-22.md`), 22 October. Thirty questions, each hinging on a condition, a number, an exception or a reopen trigger (`questions.md`).

## How it was run

- **Before the trim:** a fresh Opus helper wrote the questions and answered them from the full docs at `a3479d6`, citing source lines (`answers-before.md`).
- **After the trim:** a different fresh Opus helper answered them closed-book. It read only the trimmed `CLAUDE.md`, `NOW.md`, the four skills and the sixteen design docs' In shorts, with no doc bodies, and it never saw `answers-before.md` (`answers-after.md`).
- **Marking:** a third fresh Opus helper marked each answer same, drifted or missing against the reference: strict on what the question hinges on, lenient on wording and side detail (`compare.md`).
- **Fixes and the re-ask:** the nuance behind each drifted or missing answer was restored in its doc's In short. The same answerer was then asked those questions once more (`answers-after-reask.md`), and the same marker re-scored them (`compare.md`, Re-ask after the fixes).

## Score

| | Same | Drifted | Missing |
| --- | --- | --- | --- |
| Before the fixes | 23 | 6 | 1 |
| After the fixes (one re-ask) | **29** | 1 | 0 |

The target was at least 27 of 30.

## What was lost, and where it was restored

| Q | Lost | Restored in |
| --- | --- | --- |
| 12 | the clay town counts as scope, not as a regression; 16.7 ms at every judging view in three lights | `docs/plan.md`, In short P1, P9, P3, P7 |
| 13 | port steps 4 and 5 validate three written records unbuilt; a format changes only where a record fails, and no field is added without one | `docs/plan.md`, a new In short line P8, with P8 tagged in the body |
| 15 | MSAA 4× is kept until port step 5 (3.4) so step 3's A/B changes one thing; STP only once every mover writes motion vectors | `docs/building-blocks.md`, In short S1 |
| 22 | the human test holds one visual task of at most 10 minutes, after the page reading; it fits criterion 1, not 4, which needs its own readers or half seeing the scene first | `docs/engine-requests.md`, a new In short line ER5, tagged in the body |
| 25 | a fog nocturne's 75% holds only if it keeps its one dark and one white; the grey read at one-eighth size comes before colour | `docs/visual-direction.md`, In short VD2 |
| 26 | management screens are studied once the first game is chosen or the greybox needs them | `docs/systems.md`, In short SY4 |
| 30 | the starting record reruns from S on the engine's facts, and a curation pin that contradicts them is dropped and reported | `docs/facts-contract.md`, In short FC1 |

Every In short stays within 200 words. To make room, lines that only repeated another In short or `NOW.md` were cut: the plan's list of the town's other decisions (now BB2, TS1, D6.4 and TP3), the plan's copy of step 1's order, ER4's list of playtest requests, the engine-reading notes in ER2, and the example debts in D2.1. Their bodies are unchanged.

**Q26 after the re-ask:** the first fix said "due before the first game's choice or the greybox's need", which reads as a deadline rather than a trigger. SY4 now says "Management screens: once the first game is chosen or the greybox needs them". The spec allows one re-ask, so this wording was not asked again, and Q26 still counts as drifted.

**Q9, marked same:** the answerer found a tension in `game-lab-workflow`'s older lines, "Send the contact sheet to Øystein… Do not judge beauty yourself". They sit against What goes to Øystein, where the look is ours. This is listed for Friday's reviewer in `disagreements.md` (D) and is not settled here.
