# Calibration game master's brief

The lead's brief to each calibration game master, with {id}, {kind} and {model} filled from `roster.md`.

You are the calibration game master for player {id} in Overstory's paper playtests, round 1 (repo `/Users/oystein/code/Overstory`; paths below are relative to `reviews/lt1/playtests/paper-1/`). Do not commit. Write only in `calibration/{id}/` and `calibration/weak-{id}/`. The player's memory file is the player's to write; never touch it.

Read `gm-brief.md` in full and follow its sections "The player" (the spawn, round, exit and new game messages, exactly as written, adding nothing), "Honesty" (its engine rules don't apply: both games are invented worlds; seeded chance does) and "Your files" (keep the log, turns.md, needs.md, scores.md and condensed.md; no ledger). Don't read method.md, the world pack or anything else.

Your player: id {id}, persona {kind} in the brief's list, model {model}.

Game 1, the anchor. The plan is `calibration/{id}/gm.md`; the opening `calibration/{id}/r0-screen.md` is written. Spawn the player and run three rounds as the plan says. The r1 and r2 screens end with the line telling the player where to write its next act (`calibration/{id}/r2-act.md`, then `r3-act.md`). The r3 screen ends with the plan's exit questions, plus "Marks for each turn of round 3, in the usual shape", and the line `Write your exit interview to calibration/{id}/exit.md.` Then send the exit message. Log in the Log section of `calibration/{id}/gm.md`.

Game 2, Saltlight. The plan is `calibration/weak/gm.md`, shared by all twelve runs: never edit it; keep this run's log in `calibration/weak-{id}/log.md`. The opening `calibration/weak-{id}/r0-screen.md` is written. Send the same player the new game message for `calibration/weak-{id}`, then run its three rounds, the exit questions (again plus marks for round 3's turns) and the exit message the same way.

Render each game at its best and no better. In each game's folder keep `turns.md` (mark and surprise from the next act), `needs.md`, `scores.md` (predictions only: what the player predicted and whether the game bore it out) and `condensed.md` (up to 300 words).

When done, reply in at most 60 words: for each game the pull by round and the exit's overall pull, and any problem.
