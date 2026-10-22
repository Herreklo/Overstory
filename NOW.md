# Now

What is running and what is next, under about 1,100 words. The order, the boxes and this week are in `docs/plan.md`; each decision is in its design doc's In short; history is in `docs/experiments.md` and git.

**Next job:** the walk (1g), W0 to W7, for Friday 23 October: `reviews/lt1/playable/outline.md` §2, with `brief.md` and `premortem.md` (§4's fixes). A session told "go" starts here, on Opus, in its own session.

## Where we are (22 October)

- **LT1, the harbour street in 1989,** on branch `lt/1-harbour-street` (`docs/experiments.md`). `main` takes the branch at milestones Øystein has judged: the corner's stone, then the corner's houses, then LT1's end. Every commit is pushed to the branch meanwhile.
- **Built:**
  - the house generator at test quality (the stress test passing at strong and stronger; Øystein chose stronger);
  - the heart in clay, with its land, ways, light, style and moods; the birches, closed as a look test only;
  - the gully steps and stairs, mid-port: their baseline (stairs `bff7858b698f3efd`, walls `0a3d7db3100df20b`) is still below the bar, with four known faults, and Øystein accepted it as the regression reference only, judged against the target frame;
  - the cheek walls (a first pass, not reviewed); the shared systems; the measuring tools and the Unity lock; 1f, the clay time test.
- **Written and reviewed:** the architecture (`docs/building-blocks.md`) and the other design docs; the craft of fourteen areas (coverage and gaps: `docs/systems.md`).

## The order

From `docs/plan.md` (The order; This week). Answer what comes next from it; changing it takes a written proposal (`CLAUDE.md`, Decide once). Boxes are per cent of the weekly limit; at 1.5 times its box a step stops for a re-plan, written here.
- **Now:** 1g's walk (box 16; its design is done), which Øystein walks on Friday 23 October; 1c's beams A/B on the walk's first whole-scene run (box 3).
- **Then:** 1c in the walked corner (LA, L1 and L2 first; the rest sized from their gap), with the port's 2b beside it; the strict review of port steps 0 to 2; R3 to R7; port steps 4 to 7; 1d; 1e; the setts, kerb and plinths. 1g's play is the milestone after the walk, beside 2b.

## Running now, by line of work

Each session commits its own work; a stopped one resumes from its files. Long work runs in its own session: a cleared chat stops its background agents.

- **The playable corner (1g),** on this branch, in `reviews/lt1/playable/`: `brief.md`, `pick.md` (the case, Before Friday), `outline.md` and `premortem.md`.
  - Øystein cut Phase 2's build (about 16 Opus-days) until cheap tests answer (Øystein: "we need to be more sure what to test - before comitting to something like this"). In its place, a ladder of five tests, about one Opus-day (`outline.md` §3), with the pre-mortem's fixes in `case-spec.md` before it is frozen. The case's build is sized only if the ladder passes, as its own decision with Øystein. Øystein does not read `pick.md` or the case spec, so test 4 stays blind.
  - *Next:* the walk for Friday, then the ladder in its order.
- **The gully port, paused** at a clean point, all pushed: step 1, step 2a (hashes unchanged) and step 3's early rungs, with Fable's verdict in the docs.
  - *Next:* it resumes at 2b inside the playable corner, on the Blender side; what's left, in order, is in `reviews/lt1/port-handover.md`. Before step 4 opens, `reviews/lt1/port/foundation-needs.md`: steps 4 and 5 are each done only when a House A front, a birch chunk and a 64 m land chunk with water validate against their formats.
- **The paper playtests, stopped** (Øystein, 22 October: "Maybe stop playtest, and focus on building?") at 11 of 24 runs. Their outcome is the interim note (`docs/playtests/paper-1/analysis/interim.md`); its two engine requests are filed, and nothing more runs from them.
  - *Next:* the concepts are redesigned from the needs it found (kin, what moves the paper's meters, who found and certified the dead) when people play the greybox; any later AI round starts with the note's four method fixes. Handover: `paper-playtests-paused.md` in the notes folder.
- **Held, on Opus:**
  - the camera and play-craft studies' unread talks and masters, listed in the Limits sections of `docs/research/play-craft.md`, `camera-and-composition.md` and `collision-and-navigation.md`, once the port runs and the weekly allows; read online only, since a download waits for Øystein's OK;
  - a review of the playtest programme (`docs/research/playtesting.md`), when the greybox is close.
- **Housekeeping, the dates:** a "22 October" label on work of 20 or 21 October takes its commit's date (`git blame`), checked by eye; real dates (photos, records, the playtests' files) stay.
- **Inquest,** a stored game idea on the unmerged branch `ideas/inquest`. Its engine requests are numbered 11 to 17, which clash with the numbers in `docs/engine-requests.md`.

## For Friday's reviewer

- `docs/proposals.md`: proposed changes to the plan and the rules (Q1 to Q11), for the next milestone's fresh reviewer. Nothing in it is acted on before then.
- `reviews/docs-trim/disagreements.md`: where the design docs disagree with each other (56), listed and not settled. First: the `game-lab-workflow` skill's "Do not judge beauty yourself" against `CLAUDE.md`, which puts the look with us.

## Waiting for Øystein

What goes to him is in `CLAUDE.md` (How work runs). His decisions stand in their docs' In shorts and are not reopened without him. Open:
- the walk mode at eye level, whether people react to the camera, and the camera's play: settled by testing in the greybox, not by opinion (Øystein: "we have to test this"; `docs/plan.md`, 1g);
- after the port: installing Unity's IL2CPP module to compare the player's rebuild times with Mono (`docs/research/building-blocks-decisions.md` §15). Recommended: yes, when step 5 needs it;
- the reference downloads, approved on 21 October: each file is still listed for him with its source and size first;
- which game comes first: nothing is decided. The interface study's observer case keeps its play choices as defaults (`docs/research/interface-and-inspection.md`, For Øystein);
- the player's place at A (`outline.md` §6): work at Peter's café, or live at A with no trade. Recommended: live at A. Before test 1 freezes;
- the exit criteria in `CLAUDE.md` (What it is for), a draft to agree with him, and the band, proposed as a shared milestone with the engine (`docs/engine-requests.md`).

## Engine

Round 41 is kept. The human test comes after round 42, and homes after round 43 with the front door's part two (read on 21 October). The real run, world 9989, is `fixtures/engine/understory-world-9989.json`: 119 people and 2,635 events from 2026 to 2036, with no buildings, its years starting in 2026 until a setting's start year (#23). Requests and their status: `docs/engine-requests.md`. For the next bundle: 136 event texts and 232 cause labels keep years the shift can't reach, such as "every week (2024)" (`reviews/lt1/playable/premortem.md`).
