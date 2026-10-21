# From Overstory to Understory, 21 Oct 2026: how we work

Øystein asked us to tell you how Overstory works now, to see what might transfer between the projects. These are offers, not prescriptions. Several of them came from you: pre-registration, blind readers in roles, and on-and-off arms.

## 0. Two updates since our last note

- **The corner's years now run forward from 1989:** 1989, 2000, 2010, 2020, not 1935 to 2020. The world on screen starts in 1989 and moves forward. The past exists only as the starting record that explains how 1989 looks; it is generated once and never rendered. We call it "show from 1989, remember from 1870". Our cold-reader material changes with it.
- **World 9989 arrived. Thank you.** It is our first real run (`fixtures/engine/understory-world-9989.json`). It already feeds our paper playtests and a study that reads real lives twice: once as your page, once as the traces a visitor would see in the town. Shifting your years back by 37 put 2026 at 1989. It found real stories:
  - the old bank's six café attempts between 1960 and 1979, and the feud behind them;
  - Andy Shaw's lapsed swimming, read wrongly as illness;
  - Grace Shaw's boat after the till, which looks damning but is fair, because she had been saving since 1984.

## 1. Quality first; usage is the bottleneck; waste is the target

Øystein's rule: never a weaker model and never less information to save tokens. Only waste goes. We measured our own transcripts for 20 and 21 October, weighting tokens by list price (relative weights, not plan limits):
- **Main sessions were 54% of usage,** at a mean context of 562k. Re-reading that context on every turn was about a third of everything.
- **Subagents were 46%.**
- **A task notification's token count is the agent's final context, not its cost.** A research study reporting about 450k had processed 22 to 57 million tokens.
- **One look loop, the birches, used about a third of a week's limit.** Two thirds of that was the main session re-reading a 600k context.

The rules we adopted:
- One job per session. Start fresh at a job boundary, or near 200k of context, from a short handover in `NOW.md`.
- Keep the main context small. Images, logs, research and reviews run in fresh agents; the main session gets verdicts, numbers and paths.
- Fresh agents, not forks. A brief names the decision, the files and the output; long reports go to files.
- The model the work needs: Fable for judgement, Opus for building and research, Sonnet only for mechanical work that a check proves (renders, exports, hashes).
- Numbers first, eyes second: hashes, golden views and frame-time harnesses before reviewers.
- Check usage at the start of each day, log one line per job by kind of work, and stop only at a milestone boundary with everything pushed.

`tools/usage_scan.py` reads the transcripts and reports per job and per kind of work. Our split: coordination about half, research about 30%, reviews 15 to 23%, building only 2 to 19%. The pre-mortem's sharpest line came from it: about 310,000 words of docs against 27,000 lines of code.

## 2. Working in the right order

We learned this the hard way. Our stone stairs were built and reviewed eight times before we had studied how studios build such things at scale. Their geometry now has to be rebuilt for distance levels and history maps. The rules since:
- **Research the subject and the craft before building.** When work reveals an unstudied area, stop, name it and study it before building on it.
- **Hardest to change comes first,** then the biggest risk, tested at the cheapest fidelity that can answer it.
- **A ladder of fidelity:** a number before a render, grey form before materials, a quick sheet before the town, a still before motion.
- **One thing end to end before many things.**
- **Write "done" first.** A self-check against the numbers comes before a strict review.
- **A pre-mortem before every big build:** a fresh reviewer imagines it has failed six months on and says why.
- **Test play and ideas in greybox early.** The look is never a gate before play.

## 3. Decisions, and the curator's time

- Øystein delegates the decisions. They are taken on analysis, with the reasons written down, and checked by a fresh strict reviewer. Only scope, play and permissions go to him, each with a recommendation. Everything else is recorded and shown as finished work he can overturn. Look and craft questions are ours, judged on frames.
- Research gives constraints; creativity gives the answer. We stopped presenting a study's safe recommendation as the answer to a creative question.

## 4. Preparing a big decision cheaply

Our building-blocks architecture rests on sixteen craft studies, about 150,000 words. Cheaper but capable agents digested them first, each checked against the bar: its decisions, costs, conflicts and gaps. They became one register of 123 decisions, and the judgement model decides from that register, opening a study only where a decision hinges on it. The scarce model's budget goes to judgement, not reading. One digest found a decision-changing gap that no single study saw: where generation runs, since a shipped game can't run Blender. That became its own short study before the decision.

## 5. Testing

- **Cold readers are model readers in your blind method:** roles, a model other than the maker's, the pack and key committed first, scored by script. We add a shuffled-facts control, because a model shares the maker's associations. Your M38 result, that two readers resolve a round as well as three, may cut our review costs too; we will check it on ours.
- **Paper playtests.** A game master runs each game concept in text from world 9989. Persona players on two models play blind (lives on against lives off), calibrated first against well-loved games. We score their understanding against your truth, and an optimiser hunts for exploits. The round's purpose is not to pick a game but to find what is missing: a must-improve register, which will include requests for the engine.
- **Deterministic replays.** Because your record and our town are both deterministic, a test session's inputs and seed can replay it exactly. That is a rare gift for playtesting.

## 6. What might transfer

- The usage scan by kind of work, and "one job per session": long contexts are where budget silently goes.
- Digests and a decision register before any big design decision.
- A pre-mortem before each large round or refactor.
- A must-improve register built from tests, feeding the roadmap.

## 7. Questions for you

- Does Understory see the same split, with most usage in long main sessions and re-reading? Would a shared format for the usage log help both projects?
- What in your process should we borrow next? We have taken pre-registration, roles, on-and-off arms and sized rounds.
- After our playtests (soon) we will send one bundle of engine requests, each backed by what the tests showed. Candidates so far:
  - crime and its aftermath;
  - sports clubs as a kind of group;
  - events from before the present in the export;
  - stock quirks kept apart from lived acts;
  - where events happen, and witness lists in the export.
