---
name: game-lab-workflow
description: Use when planning, running, judging or recording any visual or game work in the Game Lab (Unity, Blender, scenes, characters), and when briefing agents, choosing models or deciding what goes to Øystein. Holds the loop (make, look, fix), what goes to Øystein, the models and the rules every brief carries.
---

# Running work in the Game Lab

**Make, look, fix** (Øystein, 23 October: "i do not want to spend all my money on admin"). The money goes to making things. Three stones once took one session of 1,295 messages and 37,793 frames for 17 sheets, then failed on a look that one still beside its reference would have shown.

## The loop

1. **Make** the thing at the cheapest rung that can show it: grey form before materials, one part before many.
2. **Look:** one still beside its reference, at the size it will be seen, in grey and in one light. Judge it critically, as a master would. If it is wrong, fix the part or start it again. Never measure a look that is already wrong.
3. **Repeat** until it holds. Only then the other lights, distances, motion and frame rate, by script (`tools/check.py`), not by an agent reading numbers.
4. **Show:** the stills go to Øystein at a milestone, after one strict review (on Fable, or Opus when Fable is out).

## Keep it small

- One thing per fresh session, on the experiment's branch. Hand off in a few lines at about 300 messages or at the job's end.
- A report is a few lines beside its stills, and a commit is one line. `docs/experiments.md` gets a few lines per outcome.
- No new rule, design doc, proposal, register or reconciling of docs unless Øystein asks for it. When in doubt, cut process.
- Research only what the next thing needs, briefly, in a fresh Opus agent that returns a short note. Learn the rest by building.
- Render frames for a question, never "in case". A measurement used twice becomes a script.
- Keep the main context small: batch calls, and read files in ranges and logs by their tail.
- Check usage at the start of each day, and say what share went to making things.

## Order

Hardest to change first (formats, scale), and polish last, in the ensemble. Biggest risk first, at the cheapest fidelity. Play in greybox early. One thing end to end before many. A loop that won't converge stops: grey light, one change at a time.

## What goes to Øystein

Scope, play, permissions and the milestones he judges go to him, each with a recommendation. He decides in chat, and his decision is recorded in one line where it applies. Everything else, architecture, look and craft included, is decided by looking and shown to him as finished work he can overturn. Work runs on without waiting for him (21 October: "unless it is super important, you can just continue working").

## Models

- **Fable 5.1:** strict reviews before a milestone and the few decisions that shape the project, from a short packet of the stills and a few lines. It has its own weekly limit and can't run on credits.
- **Opus 5.5:** building, research, drafting and checks.
- **Sonnet 5.5:** mechanical work that a hash or check proves unchanged.

Never use a weaker model or give less information to save tokens. Only waste goes.

## Every brief carries these

1. Øystein's Mac is his: no `osascript`, System Events, accessibility or computer-use. Full-screen runs happen only when he says the Mac is free.
2. Commit only your own paths (`git commit -- <paths>`). Never stash, reset or restore another session's files, or commit its scene.
3. Values that depend on style, era, place or material are data, never numbers in code.
4. Understory is read only, through the GitHub API. Only Øystein accepts a golden baseline. Reference images and assets wait for his yes, file by file.
5. No video pages in a browser. Talks are read from their captions (`~/code/overstory-sources/bin/yt-dlp --skip-download --write-auto-subs`).
6. No game is chosen; ideas are candidates. The playable corner's case stays blind to Øystein.
7. Make, look, fix: one still beside the reference before any measuring.
