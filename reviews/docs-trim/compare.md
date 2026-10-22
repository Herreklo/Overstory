# Question test for the docs trim: before and after compared

Method: each after answer, written only from the trimmed packet, was marked against the before answer, written from the full docs at `a3479d6`. A mark is strict on the nuance each question hinges on and lenient on wording and side detail.

**Score: 23 same, 6 drifted, 1 missing, out of 30.**

| Q | Mark | What differs (for drifted or missing: the exact nuance lost, and where the reference found it) |
| --- | --- | --- |
| 1 | same | Adds the command's counts (last five comments, newest three files); otherwise identical. |
| 2 | same | All limits and the on-arrival rule are kept. |
| 3 | same | Adds the mass-production rule for libraries (D6.4), which is true and extra. |
| 4 | same | |
| 5 | same | |
| 6 | same | |
| 7 | same | Leaves out what reviewers see until the blind test passes, which is a side detail. |
| 8 | same | |
| 9 | same | The rule is right. The after helper found `game-lab-workflow`'s older wording, "only taste, scope and play go to him", and the Ending's "send the contact sheet, don't judge beauty", both of which clash with delegating the look. Worth fixing in the skill. |
| 10 | same | |
| 11 | same | Leaves out "with what still waits" from the state line, which is a side detail. |
| 12 | drifted | Loses the exception: the clay town counts as scope, not as a regression. It also loses that the 16.7 ms must hold at every judging view in each of three lights. Reference: `docs/plan.md:109-112` (the frame-rate gate); the In short P1/P9 does not carry it. |
| 13 | drifted | Loses the rule for changing a format: it changes only where a written record fails to fit, and no field is added without a record. It also loses that the three records validate without being built. Reference: `docs/plan.md:130-135` (steps 4 and 5); `NOW.md` and the In shorts give only the three records. |
| 14 | same | |
| 15 | drifted | It puts the choice of filter at step 5 where the reference has step 3.4. It loses why MSAA 4× stays until then (so step 3's history A/B changes one thing), STP's condition (only once every mover writes motion vectors), FSR 1 as the fallback and the single re-acceptance of the baselines. Reference: `docs/building-blocks.md:306-307`. The After answer took "step 5" from the In short S1, so the body and the In short may disagree, and one of them is stale. |
| 16 | same | |
| 17 | same | Keeps "the real output, never a stand-in" and the 2.2 ms after the draw. Leaves out the quad's +0.05 ms against +2.2 ms, which is a side detail. |
| 18 | same | |
| 19 | same | Leaves out where marks cluster (edges, junctions, the walking line, the drip line) and the choice by weight, both side details. |
| 20 | same | |
| 21 | same | |
| 22 | missing | Says the packet does not give it. Lost: one visual task of at most 10 minutes, run after the page reading, which fits criterion 1. It cannot test criterion 4, since readers already know what happened, so criterion 4 needs its own readers or an order where half see the scene first. Reference: `docs/engine-requests.md:14`; no In short (ER or F2) carries it. |
| 23 | same | |
| 24 | same | |
| 25 | drifted | Loses the condition on the exception: a fog nocturne may take up to three quarters, in a narrow middle band, only as long as it keeps its one darkest dark and its one white. It also loses that the greyscale read at one-eighth size comes before colour is judged. Reference: `docs/visual-direction.md:57`; the In short VD2 states the 75% without the condition. |
| 26 | drifted | Gives "due before the first game", where the reference has "studied once the first game is chosen or the greybox needs it, rather than before a numbered plan step". The greybox trigger is lost. Reference: `docs/systems.md:108`; the In short SY4 compresses it. |
| 27 | same | |
| 28 | same | |
| 29 | same | Gives the order of material as own stones, then the depot, then new, which carries the reference's "new only for what is broken" in effect. Adds the era practice, which is true and extra. |
| 30 | drifted | Keeps "the engine wins and is redrawn". Loses that the starting record reruns from the people's start year S (1959 for a game shown in 1989) on the engine's facts, and that a curation pin which contradicts them is dropped and reported. Reference: `docs/facts-contract.md:15` and `:41`; the In shorts FC1 and FC3 lack both. |

## Re-ask after the fixes

The same closed-book answerer answered the six drifted questions and the missing one again from the fixed In shorts (`answers-after-reask.md`). Each new answer was marked against `answers-before.md` by the same standard. For Q15, the reference's "step 3.4" and the packet's "port step 5" name the same step (`docs/building-blocks.md:3`, "3.4 its step 5 (levels)"), so the name does not count as drift.

| Q | Mark | What differs (for drifted: the exact nuance lost, and where the reference found it) |
| --- | --- | --- |
| 12 | same | Now has the clay counting as scope, an unscoped rise stopping the step, and holding or falling until under 16.7 ms at every judging view in three lights. The box rule comes across as "1.5 times a box forces a re-plan" rather than "stops the step, as overrunning its box does", which is a side detail. |
| 13 | same | Now has the three records validated unbuilt, a format changing only where a record fails it, and no field without a record. |
| 15 | same | Now has STP only once every mover writes motion vectors, MSAA 4× kept until step 5 so step 3's A/B stays clean, and the filter chosen on levelled geometry by shimmer and the golden views. Still leaves out FSR 1 as the fallback, the MSAA 2× and 4× arms and the single re-acceptance of the baselines, all side details. |
| 22 | same | Now has one visual task of at most 10 minutes after the page reading, which fits criterion 1. It says criterion 4 cannot be tested and needs its own readers or half seeing the scene first. It does not give the reason (page readers already know what happened), which the question does not ask for. |
| 25 | same | Now has the nocturne's 75% on condition it keeps its one darkest dark and its one white, and the read in grey at one-eighth size before colour. Leaves out "in a narrow middle band", a side detail. |
| 26 | drifted | Says the management screens are studied "before the first game's choice or the greybox's need, whichever comes first". The reference has "once the first game is chosen or the greybox needs it, rather than before a numbered plan step". The fix turned "wait for the choice" into a deadline before it. Reference: `docs/systems.md:108`. The fixed In short SY4 should read "once the first game is chosen, or when the greybox needs it". |
| 30 | same | Now has the span from S rerunning on the engine's facts, and a contradicting curation pin dropped and reported. Leaves out S's value (1959 for a game shown in 1989), a side detail. |

**New total: 29 same, 1 drifted (Q26), 0 missing, out of 30.** The other 23 keep their first marks.
