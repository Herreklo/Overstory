# Usage log

What each job used and what it left behind, by kind of work, so the plan can be sized in per cent of the weekly limit per finished kind (the pre-mortem's second failure story, `docs/research/pre-mortem.md`). Read it when planning a week's budget (`CLAUDE.md`, Using tokens well).

How it is made: `python3 tools/usage_scan.py jobs --from 2026-10-20 --to 2026-10-22` reads this project's transcripts and prints one row per job, the shares by kind, the unit costs and the app's plan readings found in the transcripts (`--md` prints rows for this table). Tokens are weighted by list price; the weights are relative and unverified as plan weights. Dates and times are the transcripts' clock, Oslo time: Wednesday was 21 October.

Kinds: build (code and assets), measure (renders, harness, stress tests), review, research, docs, and orchestration (the main session's own turns). A subagent's kind comes from words in its description, then from the tools it used. A main session counts as orchestration, and is also split by what each of its requests did: running Blender or Unity or editing code is build, renders and checks are measure, opening images is review, web reading is research, writing Markdown is docs, and the rest is orchestration.

## Readings

| Date | Reading |
| --- | --- |
| 21 Oct 16:47 | Weekly limit 82%, Fable's 100%, 5-hour window 50% (the app, read in the main session) |
| 21 Oct 18:17 | Weekly limit 87%, Fable's 100%. From 16:47, with Fable spent and only Opus running, 5 points matched $87 of weight: $17 a point. Over the week since Monday 14:00, 87 points matched $1,003: $11.5 a point |

## Jobs, 20 Oct 08:29 to 21 Oct 18:32

One line per job of 0.5% or more; series of reviews and a study's helpers are summed. Tokens are processed tokens: input / cache read / cache write / output. Weighted is list-price dollars, with the share of the window's $1,027 (145 jobs).

| Date | Job | Kind | Model | Tokens | Weighted (share) | Produced |
| --- | --- | --- | --- | --- | --- | --- |
| 20 Oct | Main session "Visual direction and beauty corner setup", 08:29 to 21:46: the corner set up, the first birches | orchestration | Opus | 2k / 682M / 6.0M / 1.9M | 222 (21.6%) | 67 commits: 177 assets, 46 code, 19 docs, 326 images |
| 20 Oct | Tree and town research: tree systems in games, reference images, placement and flora, Stavanger's park trees, harbour topography (5 jobs) | research | Opus | 1k / 88M / 1.3M / 11k | 24 (2.4%) | reports of 1,700 to 5,200 words |
| 20-21 Oct | Main session "Building Overstory", from 21:49: the birch loop, stone, stairs, the research wave, the plan | orchestration | Opus | 4k / 949M / 7.5M / 2.3M | 296 (28.9%) | 139 commits: 71 assets, 51 docs, 36 code, 308 images |
| 20-21 Oct | Strict reviews of the birch and trunk, rounds 1 to 34, 19:00 to 05:00 (34 jobs) | review | Fable | 11k / 44M / 6.7M / 303k | 110 (10.7%) | verdicts of 460 to 1,100 words |
| 21 Oct | Stone research: the reference board, how stone is drawn, Norwegian stone steps (3) | research | Opus | 0k / 37M / 1.0M / 14k | 13 (1.2%) | `docs/references/stone/` |
| 21 Oct | Strict reviews of the gully steps, rounds 1 to 6 (6) | review | Fable | 2k / 8.4M / 1.3M / 73k | 22 (2.2%) | verdicts |
| 21 Oct | Town and people studies: owners' changes, people, repairs, town change 1945 on, city types, forces, urban form (7, and 3 cut off when Fable's limit ran out) | research | Opus | 1k / 72M / 2.1M / 264k | 31 (3.0%) | 7 docs in `docs/research/` |
| 21 Oct | Design: the living fabric system | docs | Fable | 0k / 1.9M / 500k / 39k | 9 (0.8%) | `docs/ideas/living-fabric.md` |
| 21 Oct | Strict reviews of stairs as a kind (3 on Opus; a first on Fable cut off) | review | Opus | 1k / 25M / 817k / 58k | 12 (1.1%) | verdicts |
| 21 Oct | Synthesis: the town system | docs | Opus | 0k / 12M / 337k / 70k | 6 (0.5%) | `docs/town-system.md` |
| 21 Oct | Craft study: how great worlds get built | research | Opus | 0k / 21M / 362k / 63k | 7 (0.7%) | `materials-at-scale.md` |
| 21 Oct | Craft study: performance and QA at scale, with 4 helpers | research | Opus | 0k / 34M / 1.1M / 36k | 13 (1.3%) | `performance-at-scale.md` |
| 21 Oct | Craft study: kits and procedural generation, with 4 helpers | research | Opus | 1k / 67M / 1.3M / 43k | 21 (2.0%) | `kits-and-generation.md` |
| 21 Oct | Craft study: history in things | research | Opus | 0k / 30M / 402k / 32k | 9 (0.8%) | `history-in-things.md` |
| 21 Oct | Craft study: animation and motion | research | Opus | 0k / 39M / 425k / 48k | 11 (1.1%) | `animation-and-motion.md` |
| 21 Oct | Craft study: lighting and colour | research | Opus | 0k / 41M / 422k / 37k | 11 (1.1%) | `lighting-and-colour.md` |
| 21 Oct | Craft study: land, rock and water | research | Opus | 0k / 57M / 496k / 45k | 15 (1.4%) | `land-rock-and-water.md` |
| 21 Oct | Craft study: wooden town architecture by era | research | Opus | 0k / 30M / 499k / 38k | 9 (0.9%) | `wooden-town-architecture.md` |
| 21 Oct | Craft study: behaviour on screen | research | Opus | 0k / 43M / 422k / 32k | 11 (1.1%) | `behaviour-on-screen.md` |
| 21 Oct | Craft study: characters, faces, clothing, ageing, with 4 helpers (forks) | research | Opus | 0k / 44M / 814k / 114k | 15 (1.5%) | `characters.md` |
| 21 Oct | Craft study: showing time on screen, with 4 helpers | research | Opus | 1k / 78M / 1.3M / 35k | 23 (2.2%) | `time-on-screen.md` |
| 21 Oct | Craft study: windows, glass and signs, with 3 helpers | research | Opus | 1k / 47M / 1.2M / 15k | 16 (1.5%) | `fronts-windows-and-signs.md` |
| 21 Oct | Craft study: painted marks in motion, with 4 helpers | research | Opus | 1k / 58M / 1.2M / 20k | 18 (1.8%) | `painted-marks-in-motion.md` |
| 21 Oct | Craft study: ground cover and plants, with 3 helpers | research | Opus | 1k / 46M / 1.1M / 25k | 15 (1.5%) | `ground-cover-and-plants.md` |
| 21 Oct | Three later studies: working with Claude (the token study), interface and inspection, where generation runs, with 5 helpers | research | Opus | 1k / 42M / 1.5M / 57k | 16 (1.6%) | 3 docs in `docs/research/` |
| 21 Oct | Digests of the studies for the architecture (5) | research | Opus | 0k / 26M / 1.4M / 130k | 15 (1.4%) | `docs/research/inputs/` 1 to 5 |
| 21 Oct | Build the measuring tools (still running) | build | Opus | 0k / 37M / 1.3M / 42k | 15 (1.5%) | 2 commits: 12 code, 3 assets, 15 images |
| 21 Oct | 1f: the core idea tested in clay (still running) | build | Opus | 0k / 32M / 377k / 31k | 9 (0.9%) | 2 commits: 11 code, 3 docs, 1 asset |
| 21 Oct | The architecture's decision register | docs | Opus | 0k / 21M / 611k / 83k | 9 (0.9%) | `docs/research/building-blocks-inputs.md` |
| 21 Oct | Pre-mortem, engine requests, facts contract (3) | docs | Opus | 0k / 26M / 639k / 50k | 9 (0.9%) | `pre-mortem.md`, `engine-requests.md`, `facts-contract.md` |
| 21 Oct | The evening's jobs, still running: camera, play and feel, collision, the playtest, the far backdrop, the first game's options, this log (17) | research | Opus | 1k / 30M / 1.5M / 39k | 14 (1.4%) | - |

## Summary

Share of usage by kind of work. "By job" counts the main sessions as orchestration; "by request" splits them by what each request did.

| Kind | Jobs | By job | By request | Active hours, main sessions + agents |
| --- | --- | --- | --- | --- |
| Build | 2 | 2% | 19% | 8.1 + 1.7 |
| Measure | 0 | 0% | 5% | 3.3 + 0 |
| Review | 46 | 14% | 23% (8% of it the main session opening frames) | 2.7 + 4.2 |
| Research | 85 | 29% | 30% | 0.1 + 22.5 |
| Docs | 9 | 3% | 7% | 1.4 + 1.7 |
| Orchestration | 2 main sessions | 51% | 17% | 13.5 + 0 |

By stretch of work: the first day to 18:30 on 20 Oct, 16%; the birch loop to 05:15 on 21 Oct, 34% ($344: the main session $234 over 1,298 requests at a mean context of 599k, the 34 reviews $110); stone, the gully steps and the stairs to 15:05, 21%; the research wave, digests and plan since, 30%.

Unit costs. Per cent of the weekly limit is given at $17 a point (Opus alone) and $11.5 a point (the week's average); see below for why both.

| Unit | Weighted | Tokens processed | Weekly limit |
| --- | --- | --- | --- |
| Finished craft study, with its helpers (14) | median $14, $7 to $23 | median 44M, 22M to 80M | 0.8 to 1.2% each; all 14, 11 to 17% |
| Other finished study (10, mostly without helpers) | median $4, $3 to $9 | median 10M, 6M to 23M | 0.2 to 0.3% |
| Digest of studies (5) | median $3 | median 5M | 0.2 to 0.3% |
| Strict review on Fable (42) | median $3, $2 to $6 | median 1.5M, 0.6M to 2.9M | Fable's own limit: spent by Wednesday 16:47 |
| Strict review on Opus (3) | median $3 | median 8.8M | 0.2 to 0.3% |
| A birch review round, all in: rework in the main session and the review (34) | $10 | 24M | 0.6 to 0.9% |
| Hour of building, active (9.7 h) | $20 | 59M | 1.2 to 1.7% |
| Hour of building in the main session (8.1 h) | $22 | 62M | 1.3 to 1.9% |
| Hour of building in a fresh build agent (1.7 h) | $14 | 42M | 0.8 to 1.2% |

## What the weights can't tell us

- How the plan weighs cache reads, cache writes and output, or Fable against Opus. Anthropic doesn't publish it; list price is our proxy.
- The meter disagrees with the proxy. With only Opus running, a point of the weekly limit matched $17 of weight; over the whole week, $11.5. Either usage these transcripts don't hold counted (chats, other projects or machines, Monday afternoon before the first transcript), or Fable or some kind of token counts for more than its list price. The readings are whole per cent, so the $17 rests on 5 points and is good to about a fifth.
- Where Fable's $149 sits. Fable has its own weekly limit, full by Wednesday afternoon, and the scan cannot place its weight within either limit.
- What work needs in a fresh context. A request's cost is mostly the re-reading of its context, so "by request" says what a session was doing when it paid, not what that work costs on its own. Building cost $14 an hour in a fresh agent and $22 in the main session: the difference is the context, not the building.
- Anything outside this project on this Mac. The side session `3e0ad50d` repeats 524 requests of the first main session and is counted once; the token study's scan counted it twice. A message is written over several lines, and its first line carries an early output count, so the scan takes the largest: subagents' output was 1.8M tokens, not the 0.2M the first lines show.

## What the numbers say

The budget goes to loops and to context, not to writing: docs were 3 to 7% of usage and building itself about a fifth, while research, review and docs together took 59% by request, past the pre-mortem's warning of half. The birch alone, 34 Fable rounds overnight, was a third of the window and three quarters of the Fable use that filled Fable's weekly limit, and two thirds of each $10 round was the main session re-reading a 600k context between reviews, not the review. The fourteen craft studies were a fifth, at about 1% of the week each; their contexts peaked at 280k to 530k, and where a study had helpers, they fed it reports with a median of 3,700 words that were re-read on every later request. Three changes follow, and none weakens a model or withholds information. First, run each part's build, render and review loop in its own fresh session or build agent, restarted from a handover near 200k, with reviews as fresh agents as now: the same frames and the same bar, at the fresh agent's $14 an hour instead of $22. Second, every study brief carries the 500-word rule to its helpers: full notes go to a file the study reads once while writing, and the study's context carries only the summary and path. Third, budget Fable in rounds per part, since it is the scarcest unit; name each job's kind at the start of its description (Build, Measure, Review, Research, Docs) so the log is exact; and run the scan each morning, so that by 13 November the plan is sized at about 1% of the week per craft study, 0.6 to 0.9% per review round and 1.2 to 1.7% per hour of building.
