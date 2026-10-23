---
name: game-lab-workflow
description: Use when planning, running, judging or recording a look test or any visual or game experiment in the Game Lab (Unity, Blender, the world view, scenes, characters), and when planning the order of work, briefing agents, choosing models or deciding what goes to Øystein. Holds the order rules in full, what goes to Øystein, and the practice for sessions, agents and tokens.
---

# Running an experiment in the Game Lab

Every piece of visual or game work is an experiment. One experiment per session.

The five steps (from `CLAUDE.md`), one experiment per session on its own branch (`lt/1-first-street`):
1. Write the experiment's question and how it will be judged at the top of `docs/experiments.md`. Commit and push.
2. Outline the build; build once agreed.
3. End in something Øystein can judge in Unity: a contact sheet, a render or a playable scene, in `reviews/`.
4. Record what we keep and drop in `docs/experiments.md`; update the design docs to describe the current direction.
5. Merge to main and update `NOW.md`.

## Before building

Write a short entry at the top of `docs/experiments.md`:

- **Name and number:** `LT1: first street and first scene`.
- **The question:** what we want to find out, in one sentence. "Does soft toon shading read well at three times of day from the neighbourhood camera?"
- **How it is judged:** what Øystein will look at, and what would count as a yes. Name the camera, the times of day and the seeds.
- **What it does not test:** keep the scope honest.

Then outline the build in a few lines and wait for agreement before building anything large. For anything new in the world, the outline's first line places it by `docs/taxonomy.md`: its kind and making, its parts, their members and finishes, and the changes that act on it. Something the taxonomy's six tests don't settle is raised then, not found later.

## Building

- Build generators and parameters, not single assets (see the `blender-generators` skill).
- Follow the Unity conventions (see the `unity-conventions` skill). Everything visual is seeded and deterministic.
- Use fake engine data from `fixtures/` until the engine export exists (see the `engine-bridge` skill).
- Keep the experiment in its own scene and folder: `Assets/Experiments/LT1/`.

## Ending

Every experiment ends in something to judge, made in Unity, never only in Blender or as a concept image:

- **Contact sheet:** a grid of renders from fixed cameras, the same for every variant being compared, saved to `reviews/LT1/`.
- **Variety check, when the experiment generates things:** 30 random items from a fresh seed. Do any two look the same? Does each visual difference say something true (era, wear, wealth, owner)? Does the same seed give the same result after a reload?
- **Light check:** morning, a grey afternoon and evening. The world must look good in ordinary light, not only at sunset.

Send the contact sheet to Øystein and ask for his judgement. Do not judge beauty yourself and call it done.

## Recording

After Øystein has judged, record in `docs/experiments.md`:

- What we keep and what we drop, and why, in a few lines.
- For each reference that came up: what we take from it and what we leave.
- Anything that surprised us or might be new goes under Findings at the top of `docs/experiments.md`: the evidence, what it does not show, and what would disprove it. Tell Øystein about it directly, with how sure we are; do not leave it buried in the log.

Then update `docs/visual-direction.md` so it describes the current direction: only what we now believe, no history. History lives in `docs/experiments.md` and git.

Update `NOW.md`: what is open, what is next.

## Things to push back on

- Judging a style from a single beautiful frame.
- Adding detail everywhere instead of where the story is.
- Dramatic light hiding weak shapes.
- Variety that encodes nothing.
- Anything that would need Unity to decide something the engine should decide.

## What goes to Øystein

The rule is in `CLAUDE.md` (How work runs): scope, play, permissions and the milestones he judges go to him, each with a recommendation; everything else is decided, recorded with its reasons, and shown to him as finished work he can overturn. His words on it (moved here from `NOW.md`):
- **Work runs without waiting for him** (Øystein, 21 October, evening: "I just want you to handle things tonight, unless it is super important, you can just continue working"). Sessions carry the plan on, start the next step when the one before reports, and bring him only what is truly his.
- **The architecture's decisions are delegated** (Øystein, 22 October: "I trust you know how to handle this feedback, and based on a good analysis make the correct decisions moving forward"). Only taste, scope and play go to him.
- **Look and craft questions are ours** (Øystein, 22 October: "You have to figure these things out. As long as we are critical and only aim for high quality, this should answer itself."). They are decided on frames and motion sheets, with strict reviews, and Øystein judges the milestones. This covers, for example, the night sky's colour, lamp glass and the tonemapper; the brush's size by octaves and any boil; and near ground cover as strokes or blades.

## Working in the right order, in full

Moved here from `CLAUDE.md`, which keeps each rule in a line and "Decide once, answer from the plan" in full.

Quality is fixed. Time and tokens are saved by doing the right thing at the right time (Øystein, 22 October: "think about ways to build more efficiently, so we don't waste time and effort on the wrong things at the wrong time"). What has cost most so far:
- polish on foundations that later changed: the stairs took eight rounds, then had to be rebuilt for distance levels and history maps;
- work made before its craft was known: the light's four debts were fixed by guesses, and the trees were built from cut-out cards, which the reference machine draws dearly;
- judging that flattered: stills rendered at twice the size hid shimmer;
- sketches made too fast to keep (20 October).

The rules:
- **Hardest to change comes first.** Data formats, the architecture, the measuring tools and scale come before parts. Look polish comes last, in the ensemble.
- **Biggest risk comes first.** Whatever could invalidate the most work (scale, cost on the reference machine, motion, whether history reads at all) is tested early, at the cheapest fidelity that can answer it.
- **Climb a ladder of fidelity.** A number before a render, grey form before materials, a quick sheet before the town, clay before parts, a still before motion. Move up only when the rung below passes.
- **Test play and ideas in greybox early,** as in normal game development (Øystein, 22 October): clay places, blockout people and placeholder interfaces, played before everything looks finished. The look is developed alongside, never as a gate before play.
- **One thing end to end before many things.** A kind goes through every stage, distance level, view, light and motion before the next kind starts.
- **Write "done" first:** the question, the views, the budget and what would change our minds. A self-check against the core rules and the numbers comes before a strict review, so reviews find what only eyes can.
- **Research just in time,** except the craft that shapes the foundations. Each area is studied right before its step.
- **Decide once, answer from the plan:** in `CLAUDE.md`.
- **Stop when a loop won't converge.** Judge the form in grey light and change one thing at a time.
- **Hold a pre-mortem before every big build** (Øystein, 22 October, on learning the stairs were built before their production craft was known: "that scares me"). A fresh reviewer imagines it is six months later and the work has failed, says why, and names what a lead technical artist at a studio would say we are missing. The blind spot it catches is the one the stairs had.

## Sessions, agents and tokens

Moved here from `CLAUDE.md`, which keeps Øystein's rule (quality first: never a weaker model or less information to save tokens; only waste goes) and the models in a line. Details are in `docs/research/working-with-claude.md`.

**Models.** Choose the model by the kind of work, and say in one line when a step calls for a different one. Helper agents get the model their job needs.
- **Fable 5.1:** decisions that shape the project, and judgement: what an experiment proves, system and fitting rules, art direction, judging renders, checking reviews against the code. It costs the most and has its own weekly limit, so it gets decisions and strict reviews only, from lean packets: a register, digests, a report, chosen crops. Reading, drafting, research and checks go to Opus agents, which hand Fable what it needs.
- **Opus 5.5:** building once designed: generators, the Unity side, debugging, docs; and research.
- **Sonnet 5.5:** mechanical work with a check behind it: batch renders, moves, exports and status that the stress test or a hash proves unchanged.

**Where the usage went,** measured on 20 and 21 October: re-reading the main session's context was a third of all usage (mean context 562k); subagents were nearly half; Fable's reviews were a sixth. A task notification's token count is the agent's final context, not its cost.

**The practice:**
- **One job per session.** Start fresh at a job boundary or near 200k of context, from a short handover in `NOW.md`. `/clear` is free; `/compact` is a large request. Set the model and effort at the start and never switch models mid-session: delegate instead.
- **Keep the main context small.** Images, logs, research and reviews run in fresh agents; the main session gets verdicts, numbers and paths. Batch independent calls.
- **Give each job what it needs, once.** Start from the synthesis or a doc's In short, then read in full every section the decision rests on, and don't re-read what is already known. Read files in ranges and logs by their tail.
- **Fresh agents, not forks.** A brief names the decision, the files and sections, and the output and its length; a report over 500 words goes to a file. The brief says whether the agent may start others.
- **Numbers first, eyes second.** The harness, golden views, hashes and value spreads do the first pass, so reviewers spend their eyes on what only eyes can judge. They see frames at the size they will be judged, with native crops where a judgement is made. A leaner review packet replaces the full set only after a blind test shows it finds the same faults.
- **Research aims at a gap before its step.** A source a decision rests on is read before the decision is built on, like any gap; an unread source names the step it must be read before, never "later", and a whole subject is split across agents so no search allowance runs out partway. Talks are read from their captions with `~/code/overstory-sources/bin/yt-dlp --skip-download --write-auto-subs`; never open a video page in the Browser pane or Chrome, since it plays aloud on Øystein's Mac (22 October). Scout first, keep a shared source list, read each source once, take notes as you go, and hand to a fresh writer once context passes 200k.
- **Øystein's Mac is his.** No agent drives his screen, windows, mouse or keyboard. That means no `osascript` or System Events, no accessibility access and no computer-use tools; checks read rendered files, offscreen. On 22 October a session's System Events call made macOS ask him to let it control his computer. Anything that takes over the screen, such as the harness's full-screen player, runs only when he has said the Mac is free, never while he is using it, which would skew the timing too.
- **Every brief carries this list,** the rules no machine checks (Øystein, 22 October: a rule without a check keeps being broken, "it kills our progress"). Everything checkable runs in `tools/check.py`, which a builder runs before reporting; nothing goes to review until it passes.
  1. Øystein's Mac is his (above).
  2. Commit only your own paths (`git commit -- <paths>`). Never stash, reset or restore another session's files, and never commit another session's scene.
  3. Values that depend on style, era, place or material are data (the pack, a kind, a part's definition), never numbers in code.
  4. Understory is read only, through the GitHub API. Only Øystein accepts a golden baseline. Reference images and assets wait for his yes, file by file.
  5. No video pages in a browser; talks are read from their captions.
  6. No game is chosen; ideas are candidates. The playable corner's case stays blind to Øystein.
- **Rework costs most.** Research the craft, try a quick sheet, measure before judging, decide before building.
- **Check usage at the start of each day,** and log a line per job in `docs/usage-log.md` (`tools/usage_scan.py` reads the transcripts). When usage runs low, stop at a milestone boundary with everything pushed.
