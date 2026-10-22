# Now

What is running and what is next, under about 1,100 words. The order, the boxes and this week are in `docs/plan.md`; each decision is in its design doc's In short; history is in `docs/experiments.md` and git.

**Next job:** 1c's LA, L1 and L2 and the port's 2b (the stones redrawn), each in its own session beside the other, in the walked corner. Then the camera's zoom test (1g's camera milestone, below). The walk (1g Phase 1a) closed on 22 October: W5 `da250bb`, the walk without its birch `421e831`, W7 `f2cc838`; W6 was cut; Øystein's own verdict replaced W7's strict review (`docs/experiments.md`, LT1g).

## Where we are (22 October)

- **LT1, the harbour street in 1989,** on branch `lt/1-harbour-street` (`docs/experiments.md`). `main` takes the branch at milestones Øystein has judged: the corner's stone, then the corner's houses, then LT1's end. Every commit is pushed to the branch meanwhile.
- **Built:**
  - the house generator at test quality (the stress test passing at strong and stronger; Øystein chose stronger);
  - the heart in clay, with its land, ways, light, style and moods; the birches, closed as a look test only;
  - the gully steps and stairs, mid-port: their baseline (stairs `bff7858b698f3efd`, walls `0a3d7db3100df20b`) is the regression reference only, to be redrawn in 2b;
  - the cheek walls (a first pass, not reviewed); the shared systems; the measuring tools and the Unity lock; 1f, the clay time test; 1g's walk.
- **Written and reviewed:** the architecture (`docs/building-blocks.md`) and the other design docs; the craft of fourteen areas (coverage and gaps: `docs/systems.md`).

## The order

From `docs/plan.md` (The order; This week). Answer what comes next from it; changing it takes a written proposal (`CLAUDE.md`, Decide once). Boxes are per cent of the weekly limit; at 1.5 times its box a step stops for a re-plan, written here.
- **Now:** 1c in the walked corner (LA, L1 and L2 first; the rest sized from their gap), with the port's 2b beside it.
- **Then:** 1g's camera milestone, the zoom test (below); the strict review of port steps 0 to 2; R3 to R7; port steps 4 to 7; 1d; 1e; the setts, kerb and plinths. 1g's play is the milestone after the walk, beside 2b.

## Running now, by line of work

Each session commits its own work; a stopped one resumes from its files. Long work runs in its own session: a cleared chat stops its background agents.

- **The playable corner (1g),** in `reviews/lt1/playable/` (`brief.md`, `pick.md`, `outline.md`, `premortem.md`).
  - Phase 2's build is cut until a ladder of five cheap tests answers (`outline.md` §3; Øystein: "we need to be more sure what to test"); the case's build is sized only if it passes, with Øystein. He does not read `pick.md` or the case spec, so test 4 stays blind.
  - *The walk, closed (22 October):* the app is `unity/Builds/Playable/OverstoryPlayable.app` (keys and baseline: `reviews/lt1/playable/walk/w7-report.md`). Øystein judged it from stills and a capture: scale "nice"; the climb "a bit boaty"; the frame rate "laggy and jumpy". The beams now cost about 1 ms (from 62); the birch is out until 1e. The gate's baseline is 27 to 60 fps (`docs/plan.md`). The walker's feel waits for the game.
  - *Next, the case:* the ladder's tests 5, 1 and 2a are done (`reviews/lt1/playable/ladder/`, not for Øystein). Before the ladder's test 2b (stills on the walk's build), the case's two fixes: from test 1, seed A's first telling becomes when to tell Olive (the named lines' ranking flips in 7 of 24 sweeps); from test 2a, Hannah's authored home or the vantage moves so one vantage sees both doors. The player lives at A with no trade (Øystein). Left from the cut W6, for the next heart rebuild: `heart_layout.py` casts A as a café, and a rebuild moves D's way into the golden views.
  - *The camera:* 1g's camera milestone, after the walk and beside the port's 2b, holds whatever the game becomes (Øystein: "we just need to figure out if it is possible to make something where navigating over the city as well as moving trough the streets is nice"): is one continuous zoom, eye to city camera as `camera-and-composition.md` designs it, pleasant at both scales, and does it hold its frame rate at the top? What the player controls and the camera's play tuning wait for the game.
- **The gully port,** resumed at 2b: step 1, step 2a (hashes unchanged) and step 3's early rungs are done, with Fable's verdict in the docs.
  - *Next:* 2b, the stones redrawn (Øystein: "very buggy and not nice"; Q15), running in its own session inside the playable corner; what's left, in order, is in `reviews/lt1/port-handover.md`. Steps 4 and 5 are done only as `reviews/lt1/port/foundation-needs.md` says.
- **The paper playtests, stopped** at 11 of 24 runs (Øystein: "Maybe stop playtest, and focus on building?"). Outcome and next: `docs/playtests/paper-1/analysis/interim.md`; the concepts are redesigned from its needs when people play the greybox.
- **Held, on Opus:** the camera and play-craft studies' unread talks and masters (their Limits sections), each read before the step that rests on it; a review of the playtest programme when the greybox is close.
- **Housekeeping:** a "22 October" label on older work takes its commit's date (`git blame`).
- **Inquest,** a stored game idea on the unmerged branch `ideas/inquest`. Its engine requests are numbered 11 to 17, which clash with the numbers in `docs/engine-requests.md`.

## For Friday's reviewer

- `docs/proposals.md`: proposed changes to the plan and the rules (Q1 to Q17), for the next milestone's fresh reviewer. Nothing in it is acted on before then.
- `reviews/docs-trim/disagreements.md`: 56 places where the design docs disagree, not settled.

## Waiting for Øystein

What goes to him is in `CLAUDE.md` (How work runs). His decisions stand in their docs' In shorts and are not reopened without him. Open:
- re-blessing golden's five low-sun frames after W5's beams (0.002 to 0.07 levels mean; the sheet is `reviews/lt1/playable/walk/w5/golden-sheet-gully-1600-low-sun.png`). Recommended: yes;
- an optional 10 to 15 minute walk of the app, whenever suits him;
- installing Unity's IL2CPP module when the port's step 5 needs it (`docs/research/building-blocks-decisions.md` §15). Recommended: yes;
- downloads: public slides, papers and talk captions have a standing OK, logged in `docs/research/downloads.md` (its rules there); reference images and assets are still listed for him file by file;
- which game comes first: nothing is decided. The interface study's observer case keeps its play choices as defaults (`docs/research/interface-and-inspection.md`, For Øystein);
- the exit criteria in `CLAUDE.md` (What it is for), a draft to agree with him, and the band, proposed as a shared milestone with the engine (`docs/engine-requests.md`).

## Engine

Round 41 is kept; the human test comes after round 42, homes after round 43. The real run is `fixtures/engine/understory-world-9989.json` (119 people, 2,635 events, 2026 to 2036). Requests: `docs/engine-requests.md`; for the next bundle, the event texts whose years the shift can't reach (`reviews/lt1/playable/premortem.md`).
