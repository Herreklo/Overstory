# Working with Claude: fewer tokens, the same work

Research for the Game Lab, 21 October 2026. Usage is the bottleneck: by Wednesday the weekly limit stood at 83% and Fable's share at 100%. Øystein asked for ways to use fewer tokens without losing any quality of work. Quality is fixed: strict reviews, research before building and judging in the engine all stay. Only waste goes.

Claims from Anthropic's own docs carry no mark. Third-party claims are marked (secondary), and single reports or untested ideas (unverified). Anthropic does not publish how plan limits weigh each kind of token. Anything about that is (unverified) unless quoted.

## In short

- Re-reading the main session is the largest cost. Every request sends the whole context again, and a request happens at every tool call, not once per message. On 20 and 21 October our main sessions averaged 562,000 tokens of context over 2,835 requests. Re-reading that context was a third of all our usage.
- Subagents were nearly half. A study reported as "450,000 tokens" processed 22 to 57 million. The number in a task notification is the agent's final context, not its cost.
- Long sessions cost more and work worse. Anthropic: "LLM performance degrades as context fills." The largest saving, and one that costs no quality, is one job per session, restarted near 200,000 tokens from a short handover.
- Images, logs and research belong in fresh agents that return verdicts, numbers and paths. A fork carries the whole parent context: our 15 forks read 171 million tokens and wrote 16,000.
- Fable shares the weekly pool and may use at most half of it, at 2.5 times Opus's price per token. Spend it on judgement with a lean review packet, not on reading.
- Measure. Use `/usage` and the status line, and keep a one-line log per job.

## 1. Where the tokens go

### How a request is counted

Claude Code sends the whole context with every request: system prompt, tool definitions, CLAUDE.md and memory, every message, every tool result and every image. Prompt caching serves the unchanged start of the request from cache and processes only what is new. The match is exact and by prefix: "a change anywhere in the prefix recomputes everything after it." Every tool call is another request. The session that commissioned this study made 1,622 requests for about 60 messages from Øystein.

List prices per million tokens. We pay a flat plan, so they serve only as a yardstick for weighing one kind of token against another:

| Model | Input | Cache write, 5 min | Cache write, 1 h | Cache read | Output and thinking |
| --- | --- | --- | --- | --- | --- |
| Fable 5.1 | $10 | $12.50 | $20 | $0.25 | $50 |
| Opus 5.5 | $4 | $5 | $8 | $0.20 | $20 |
| Sonnet 5.5 | $2 | $2.50 | $4 | $0.10 | $10 |
| Haiku 5.5 (prompts up to 100k) | $0.10 | $0.125 | $0.20 | $0.01 | $0.50 |

A cache read costs 0.05 of input on Opus and Sonnet 5.5, and 0.025 on Fable 5.1. On Opus a miss at the one-hour rate costs 40 times a hit. Thinking is billed as output.

On plans, Anthropic's help centre says "cached portions count less against your limits than new content". After a long break, "your first message counts that content in full again". The Claude Code docs say a long session "re-reads that history at the cached token rate". So "a one-line question in a session that has been open all day still draws usage for the whole conversation." Anthropic's Claude Code team writes that a high cache hit rate is what lets it offer more generous subscription limits. The exact weights are not published, so treating list prices as the plan's weights is (unverified).

### What we measured

I scanned the local transcripts for 20 and 21 October: about a day and a half, three main sessions (two of them sharing a history) and 111 subagents. Each request's usage was weighted by list price.

| Where | Share of usage | What it was |
| --- | --- | --- |
| Main sessions, re-reading context | 34% | 1.58 billion cached tokens; mean context 562k, peak 967k |
| Main sessions, cache writes | 11% | About half of it went to rebuilds of 400k to 770k tokens |
| Main sessions, output and thinking | 9% | 4.0 million tokens |
| Subagents on Opus | 30% | 61 agents; the long studies were about half |
| Subagents on Fable | 16% | 46 agents, 43 of them looking at images |

The main sessions ran to 967,000 tokens, which is where models with a native one-million window compact by default. Each sat above 450,000 for most of its life.

The fixed baseline. Øystein's `/context` shows about 74,000 tokens before any work: tool definitions 32k, MCP 19k, skills 10k, system prompt 9.5k, memory 3.7k. A fresh subagent's first request carried 55,000 (the median). In this session the skill listing alone is 33,000 characters, about 8,000 tokens. Most of it lists plugin skills this project never uses: Unity Services, ads, in-app purchases, multiplayer, Figma. The deferred MCP tool names take 22,000 characters and the MCP server instructions 10,000. The baseline is re-read on every request of every agent.

Images. Claude sees images in 28-pixel patches: an image costs ⌈width/28⌉ × ⌈height/28⌉ tokens. Fable 5.1, Opus 5.5 and Sonnet 5.5 are on the high-resolution tier: a long edge up to 2576 px and at most 4,784 tokens per image. Larger images are downscaled to fit. Claude Code "resizes and recompresses large images". Once a request holds more than 20 images, a stricter size limit applies, and the API docs advise 2000 px or less per side. Our transcripts hold about 3,100 images, mostly JPEGs near 1900×1000, at a mean of 1,800 to 2,100 tokens. Raw counts mislead: cache reads were 98% of our raw tokens. Users of a GitHub issue thread report 93 to 99.9% in their own logs (secondary).

| Image | Tokens |
| --- | --- |
| 2560×1440 frame | 4,784 (the cap) |
| 2560×2560 sheet | about 4,760, seen at about 1,925 px square |
| 1920×1080 | 2,691 |
| 1568×882 | 1,792 |
| 1280×720 | 1,196 |
| 1000×1000 crop | 1,296 |
| 512×512 crop | 361 |

An image is paid once when seen, then again at the cache rate on every later request while it stays in context. In the main session that can mean hundreds of re-reads.

Thinking. On Opus 5.5, Sonnet 5.5 and Fable, thinking cannot be turned off; the effort level sets how much the model thinks. In our main sessions, output and thinking came to 9% of usage.

## 2. Sessions and context

The cost of a session is roughly its number of requests times its mean context. Both grow as a session goes on, so cost grows with the square of its length. What one Opus request costs at list price:

| Context | Cache hit | Cache miss (one-hour write) |
| --- | --- | --- |
| 75k, a fresh session | $0.015 | $0.60 |
| 150k | $0.03 | $1.20 |
| 310k, the session today | $0.06 | $2.48 |
| 560k, our mean | $0.11 | $4.48 |
| 960k, the compaction point | $0.19 | $7.68 |

A fresh start costs about one baseline write, $0.60, the price of five requests at our mean context.

### What breaks the cache

From the prompt-caching page:
- Switching models. Each model has its own cache, so the next request reads the whole history uncached. A skill whose frontmatter names another model switches for that turn, and so does `opusplan` at every plan-mode toggle.
- Changing effort, except on Opus 5.5, Sonnet 5.5, Haiku 5.5 and Fable 5.1 on a subscription, where the cache stays.
- Turning on fast mode, once per conversation.
- MCP and plugin changes, only when tools load upfront. With tool search, the default, the tool list is fixed for the session.
- Compaction, by design.
- Accumulating images. Near the request limits, Claude Code drops the oldest batch of images, and the conversation is reprocessed from the earliest of those messages.
- An upgrade, at the next session.
- Idling past the cache lifetime. The main conversation gets one hour on a subscription within plan usage. Subagents, forks, compaction and other side requests get five minutes. On usage credits the main conversation drops to five minutes.

Cache-safe: editing files, editing CLAUDE.md (it only applies after `/clear`, `/compact` or a restart), changing permission mode or output style, invoking skills, `/rewind`, `/recap` and spawning a subagent.

### Our misses

In the session that commissioned this study, five rebuilds of 420,000 to 690,000 tokens came 6 to 30 seconds after the previous request. Each read only the first 42,000 to 50,000 tokens from cache, so something early in the conversation had changed. Dropped images or cleared old tool results are the documented causes; which one it was here is (unverified). A sixth came after 151 minutes idle. Across the main sessions, rebuilds like these were about half the cache-write cost. `/usage` now shows a "Prompt cache (main)" line that names the likely cause of the last miss.

### Practice

- One job per session. Start fresh at a job boundary, or when context passes about 200,000 tokens, whichever comes first. Write the handover first: decisions, paths, open items, the next step. A fresh session costs five requests' worth; the next hundred requests each cost a quarter of what they would at our mean.
- `/clear` costs nothing. `/compact` is a large request of its own, and the Claude Code team puts its summary at about 20,000 tokens. Use it when continuity matters more than a clean start. To abandon a failed path, use `/rewind`, which returns to a prefix already cached.
- As a backstop, `/autocompact 500k` makes the automatic pass run at half a million instead of 967,000. It is a net, not the rule.
- Set model and effort at the start. Never switch models mid-session. For a Fable judgement inside an Opus session, start a fresh Fable agent with a brief. Anthropic's Claude Code team gives the same advice: change models through a subagent, with a hand-off message. Shrivu Shankar works the same way, writing plan and progress to a file, clearing, and resuming from it (secondary).
- Don't resume a big session after an hour away. The first request re-processes everything. Start fresh from the handover instead.
- Fewer round trips. Put independent reads and checks in one message, and have one script print a short summary instead of running five commands. At our mean context every request saved is 560,000 tokens not re-read.
- Ask side questions with `/btw`: "The answer never enters conversation history."

Quality gains from this, not loses. Anthropic's best-practices page: "When the context window is getting full, Claude may start 'forgetting' earlier instructions or making more mistakes." It also says: "If you've corrected Claude more than twice on the same issue in one session, the context is cluttered with failed approaches. Run `/clear` and start fresh with a more specific prompt."

## 3. Subagents and fan-outs

When they save. A subagent reads, searches and looks at images in its own context, and only its result returns. Anthropic: subagents may use tens of thousands of tokens exploring and return condensed summaries, often "1,000-2,000 tokens". The saving is real when the parent would otherwise carry those tokens through many later requests. In a long main session, that is almost always.

When they multiply. Each fresh agent starts with the 55,000-token baseline and re-reads it on every request. Anthropic's research system measured agents at about four times the tokens of a chat, and multi-agent systems at about fifteen times. Vague briefs make agents duplicate each other: in Anthropic's example, two subagents researched the same 2025 supply chains. Running three or four agents at once doesn't change the total; it only fills the five-hour window faster. The levers are fewer agents and smaller ones.

Forks. A fork inherits the parent's system prompt, tools, model and whole conversation. Its first request reads the parent's cache, so it starts cheaply, but every later request re-reads the parent's full context. `CLAUDE_CODE_FORK_SUBAGENT` is on by default, which "lets Claude start forks on its own". Our 15 forks read 171 million tokens and produced 16,000 tokens of output. Fork only when no brief could carry the context and the parent is small (under about 100,000 tokens). Otherwise start a fresh agent with a brief.

Briefs. Anthropic's lead agents give each subagent an objective, an output format, guidance on tools and sources, and clear boundaries. For us that means:
- the decision the work serves, and what is already known;
- the files to read, by section or line range, and the ones not to read;
- the output and its length: at most about 500 words back, with anything longer written to a file and its path returned;
- whether it may start agents of its own, and how many;
- the model, chosen for the job.

The parent re-reads a report on every later request. A 3,000-word report is about 4,000 tokens; read back over 500 later requests, it costs 2 million.

Which model. The order is: the model passed with the call, the agent's frontmatter, `CLAUDE_CODE_SUBAGENT_MODEL`, then the main model. The built-in Explore agent is read-only and skips CLAUDE.md, but runs on the main model (on Opus when the main model is Fable). For broad searches, pass `model: haiku`. Of our 111 subagents, 61 ran on Opus, 46 on Fable, and one each on Sonnet and Haiku. CLAUDE.md already gives Sonnet the mechanical work; in practice it hardly ever got any.

Agents that wait. Subagents keep their cache for five minutes. An agent that waits through a six-minute Blender build comes back to an expired cache and rewrites its whole context. Our fresh agents had 17 such rebuilds, 2 million tokens: small. `subagentPromptCacheTtl: "1h"` would keep their cache, but one-hour writes cost twice the input price against 1.25 times, so it pays only when long waits are common (unverified for us).

## 4. Reading

- Ceilings, not targets. A single Read returns at most 25,000 tokens; files over 256 KB are refused. Bash output is cut at 30,000 characters. MCP output warns at 10,000 tokens and stops at 25,000.
- Grep, then read the range. `grep -n` to find the place, then Read with an offset and limit, or `sed -n`. Logs by their tail.
- Design docs as the entry point. Start from the synthesis or a study's "In short", then open only the section a decision needs. This is already the rule; it stays.
- CLAUDE.md is 102 lines, about 2,500 tokens, inside Anthropic's target of under 200 lines. For each line, the docs ask: "Would removing this cause Claude to make mistakes?" `@imports` load at launch and "don't reduce its context cost", so splitting CLAUDE.md with imports saves nothing.
- Memory. The first 200 lines or 25 KB of `MEMORY.md` load every session; topic files load only when read. Ours is 3 KB: fine.
- NOW.md isn't loaded automatically, but every session and many agents read it. It is 24 KB, about 6,000 tokens. Cut to about 1,500 tokens (state, next step, open blockers and links), it saves 4,500 tokens per reader, re-read on every later request. The long plan and "Running things" can live in the docs that `NOW.md` links to.
- Skills. Until a skill is invoked, only its description loads. Once invoked, its body stays in context for the rest of the session, and after compaction up to 5,000 tokens of it come back. Keep `SKILL.md` short, put the most important instructions at the top, and move detail into linked files, which load only when needed.
- Web pages. A WebFetch of an HTML page returns an answer shaped by the prompt. Short docs pages served as markdown came back whole, about 9,000 to 10,000 tokens each, whatever the prompt. Fetch each page once and put its quotes in the notes straight away.

## 5. Images and reviews

Strict reviews look at many frames and crops, and Fable did most of them: 43 of its 46 agents looked at images. The aim is the same rigour from fewer, better-chosen pixels.

1. Numbers first. The harness, golden views, hashes and value spreads take the first pass, and a reviewer looks only where numbers can't decide. This is already the rule.
2. One overview at 1568 px or less on the long edge for layout, silhouette and the ensemble: about 1,800 tokens. A 2560 px sheet costs about 4,760 and is downscaled to about 1,925 px before Claude sees it, so the extra pixels never arrive.
3. Native-resolution crops of 1000 px or less where a judgement is made: material, edges and marks at the near tier. A 1000×1000 crop costs 1,296 tokens and shows every pixel. The same patch inside a downscaled full frame shows far fewer.
4. A/B in one image. Put the pair side by side at the same scale, labelled. The reviewer compares within one picture instead of across turns.
5. A named packet. The brief lists the frames and crops, says what is judged in each, and asks for each to be viewed once. Twelve images (one sheet and eleven crops) cost about 16,000 tokens; ten 1440p frames cost 48,000 and show less of the detail.
6. Reviews in fresh agents. The main session receives the verdict and the paths, not the pictures. On 20 and 21 October the main sessions held about 680 images, each one re-read on every later request until it was dropped, and the dropping itself caused rebuilds.

Effect on quality: none lost. Composition is judged at the size Claude would see it anyway, and detail is judged at full resolution, which a full frame never gives. To check: re-run one past strict review with the lean packet, blind to the old findings, and compare what each catches.

## 6. Tools and MCP

- Deferred tools still cost. Tool search keeps MCP schemas out until used, but tool names and server instructions still load: 19,000 tokens in our main session. Anthropic's advice: "Disable unused servers."
- This project could turn off the iOS simulator, Claude in Chrome, Google Drive, docs connector and Figma servers. The same goes for the Figma and design plugins, and the Unity plugin, whose 30 skills are mostly services, ads and purchases. Which are needed is Øystein's call. `/mcp` toggles are saved per project, and `/plugin` turns plugins off. Make these changes between sessions, since they take effect at the next start anyway.
- CLI over MCP. Blender and Unity already run in batch mode through Bash, and `gh` and the GitHub API need no server. The docs: CLI tools "are the most context-efficient way to interact with external services."
- Background runs, read by the tail. A background command writes its output to a file. Read the last 40 lines, or grep for errors, rather than the whole log. A wrapper that prints only errors, warnings and our own markers would make Unity batch logs short every time. A PreToolUse hook can rewrite a command the same way; the docs' example filters test output down to failures.
- Structured, small results. Blender MCP calls should return small dicts, not scene dumps. Anthropic's tool-writing post found a concise response format used 72 tokens where the detailed one used 206.

## 7. Model and effort

| Job | Model | Effort |
| --- | --- | --- |
| Judgement: art direction, judging renders, strict reviews, checking reviews against code | Fable 5.1 | high |
| Building: generators, Unity, shaders, debugging, docs | Opus 5.5 | medium (default); high for hard bugs |
| Mechanical work with a check: batch renders, exports, moves, status | Sonnet 5.5 | low or medium |
| Search, listing, scanning files, scouting sources | Haiku 5.5 | low |

- Fable on Max draws "from your plan's regular weekly usage limits and use[s] them faster than other Claude models", up to "50% of your weekly usage limits". It is no separate allowance: every Fable token also comes out of the shared week. At list price it costs 2.5 times Opus for input, writes and output.
- Thinking is billed as output. Effort is the dial. The docs say `max` "tends to overthink". On these models a change of effort keeps the cache, so one hard step can run at high and the next drop back.
- The advisor tool lets an Opus session consult Fable at decision points without switching models. Each call, though, reads the whole transcript uncached at Fable's input price: about $3 at list for a 300,000-token session. Worth testing only in short sessions (unverified).
- Haiku 5.5 costs a fortieth of Opus per token. Whether it is good enough for our scans is untested, so give it only work that a check can verify.

## 8. Research agents

Our fourteen studies each made about 150 requests and grew to 300,000 to 530,000 tokens of context. Each processed 22 to 57 million tokens, nearly all of it cache reads. Every fetched page stays in context and is re-read on each later request. A 4,000-word doc written in twenty small edits at 450,000 tokens re-reads 9 million tokens just to write.

The same depth for less:
1. Scout, then read. Anthropic's research agents start with short, broad queries, see what is there, then narrow. A scout on Sonnet or Haiku searches and writes a source list, one line per source. The deep reader fetches only the chosen ones.
2. A shared source list. One file of primary sources already read, with the doc that cites them and their key numbers. Agents check it before searching, so no two agents run the same search.
3. Read each source once. Quote numbers and short passages into the notes as you read. Never fetch a page twice.
4. Parallel calls. Several searches or fetches in one message make one request, not several.
5. Write from notes, in few large writes. Once the reader's context passes about 200,000 tokens, hand the notes to a fresh writer. It starts near 60,000 tokens instead of 400,000. The notes keep exact quotes and numbers, so the writer loses nothing it needs.
6. No forks inside a study, and at most two fresh helpers with briefs.

Expected: a study at 15 to 25 million tokens instead of 22 to 57 million, from the same sources.

## 9. Measuring

- `/usage` shows the plan bars, and for the last 24 hours or 7 days, which skills, subagents, plugins and MCP servers used what. It recommends changes worth 10% or more. Its "Prompt cache (main)" line gives the hit share, the misses and their likely cause, and whether the cache is warm.
- `/context` shows what fills the window now.
- The status line can show `context_window.used_percentage`, `prompt_cache.hit_ratio` and `rate_limits.seven_day.used_percentage`. Context size on screen keeps the restart rule honest. Whether the desktop app's Code tab shows a status line is (unverified).
- Task notifications report `subagent_tokens`, the agent's final context. Its real cost is in its transcript.
- The transcripts (`~/.claude/projects/<project>/<session>.jsonl`, with subagents under `<session>/subagents/`) record each request's cache reads, writes and output. The scan for this study is a short Python script; it should become a project tool.
- Keep a log, one line per job: date, kind of job, model, agents, requests, peak context, list-price cost, weekly % before and after. After two weeks we will know what a study, a review, a generator pass and a session day each cost.

## What we should do

Ranked by tokens saved. Savings are shares of our measured usage on 20 and 21 October, weighted by list price, so how they translate to plan limits is (unverified).

| # | Change | Expected saving | Effect on quality | How we check |
| --- | --- | --- | --- | --- |
| 1 | One job per session; start fresh near 200k from a handover; `/autocompact 500k` as a backstop | 25 to 30%: mean main context from 562k to about 150k, and rebuilds shrink with it | Better: less context rot. The risk is knowledge lost at the handover, which the handover note covers | The scan: main mean context under 200k; weekly % per working day |
| 2 | Research by scout, shared source list, notes and a fresh writer | About 7%: a study at about half its tokens | None: the same sources, with quotes and numbers kept in the notes | The next study made this way, compared by Fable with an older one for depth and errors |
| 3 | Images, logs and reviews out of the main session | About 5%, overlapping with 1 | None: the reviewer sees the same images | Image blocks in main transcripts near zero |
| 4 | Lean review packets: numbers first, one sheet at 1568 px or less, native crops | About 5%, and the Fable half lasts longer | Same or better: detail is judged at full resolution | One past strict review re-run blind with the packet; compare findings |
| 5 | Fewer round trips in big contexts: batched calls, scripts that print summaries | Up to 5% (unverified) | None | Requests per message in the scan |
| 6 | The cheapest model that passes the check: Haiku for search, Sonnet for mechanical work | 3 to 5% (unverified) | None where a check exists: hash, stress test, diff | The check passes; spot audits of Haiku results |
| 7 | Fresh agents, not forks; reports of 500 words or less, longer ones to a file | About 4% | None: the brief carries the context | No subagent whose first request is over 60k |
| 8 | Unused MCP servers and plugins off for this project | About 3%: 15k to 20k fewer tokens on every request | None: tools we don't use | `/context` before and after |
| 9 | `NOW.md` down to about 1,500 tokens | Under 1% | None, if the plan is one link away | Its size at each update |
| 10 | Status line and a one-line log per job | None directly; it keeps 1 to 9 honest | None | Two weeks of log lines |

## Proposed "Using tokens well" for CLAUDE.md

> ## Using tokens well
>
> Usage is a bottleneck, but quality is never traded for it; only waste goes. Measured on 20 and 21 October: re-reading the main session's context was a third of all usage (mean context 562k), subagents nearly half, Fable reviews a sixth. A task notification's token count is the agent's final context, not its cost. Details: `docs/research/working-with-claude.md`.
>
> - One job per session. Start fresh at a job boundary or near 200k context, from a short handover in `NOW.md`. `/clear` is free; `/compact` is a large request. Set model and effort at the start and never switch models mid-session: delegate instead.
> - Keep the main context small. Images, logs, research and reviews run in fresh agents; the main session gets verdicts, numbers and paths. Batch independent calls.
> - Read the least that decides: the synthesis or a study's "In short" first, then only the section a decision needs; files in ranges, logs by their tail.
> - Fresh agents, not forks. A brief names the decision, the files and sections, and the output and its length; over 500 words goes to a file. It says whether the agent may start others.
> - The cheapest model that passes the check: Haiku for search, Sonnet for mechanical work, Opus for building, Fable for judgement. Fable shares the weekly pool and may use half of it.
> - Numbers first, eyes second. The harness, golden views, hashes and value spreads do the first pass; reviewers get one sheet at 1568 px or less and native crops where a judgement is made.
> - Research aims at a gap before its step: scout first, a shared source list, each source read once, notes as you go, and a fresh writer once context passes 200k.
> - Rework costs most: research the craft, try a quick sheet, measure before judging, decide before building.
> - Check `/usage` at the start of each day and log a line per job. When usage runs low, stop at a milestone boundary with everything pushed.

## Gaps

- Plan weights. Anthropic does not publish how plan limits weigh cache reads, writes, output, or Fable against Opus. List prices are our proxy.
- The mid-session rebuilds. Their cause, dropped images or cleared tool results, is unconfirmed. The `/usage` cache line will name it.
- Effort and Haiku. Neither has been tested on our work. Run one A/B on a generator pass and one on a scan before relying on either.
- The desktop app. Whether the Code tab offers the status line, `/autocompact` and the full `/usage` breakdown is (unverified).
- Thin outside evidence. Practitioners report no measured image costs and no controlled effort tests; most numbers here are ours.
- A short sample. A day and a half of transcripts. Two weeks of the log will firm up the shares.
- The one-hour subagent cache. Its net effect for agents that wait on builds is unmeasured.

## Sources

Anthropic docs:
- Manage costs effectively: https://code.claude.com/docs/en/costs
- How Claude Code uses prompt caching: https://code.claude.com/docs/en/prompt-caching
- Explore the context window: https://code.claude.com/docs/en/context-window
- Model configuration: https://code.claude.com/docs/en/model-config
- The advisor tool: https://code.claude.com/docs/en/advisor
- Subagents: https://code.claude.com/docs/en/sub-agents
- Best practices: https://code.claude.com/docs/en/best-practices
- MCP, memory, skills, hooks, status line, tools reference and environment variables, read through a helper: https://code.claude.com/docs/en/mcp and the pages beside it
- Pricing: https://platform.claude.com/docs/en/about-claude/pricing
- Vision: https://platform.claude.com/docs/en/build-with-claude/vision
- Claude Fable models on your plan: https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan
- Usage limit best practices: https://support.claude.com/en/articles/9797557-usage-limit-best-practices

Anthropic engineering:
- Lessons from building Claude Code: prompt caching is everything: https://claude.com/blog/lessons-from-building-claude-code-prompt-caching-is-everything
- How we built our multi-agent research system: https://www.anthropic.com/engineering/multi-agent-research-system
- Effective context engineering for AI agents: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Writing effective tools for agents: https://www.anthropic.com/engineering/writing-tools-for-agents

Practitioners (secondary, used as cross-checks):
- Shrivu Shankar, "How I use every Claude Code feature": about 20,000 tokens of baseline in a fresh session; "Document & Clear" instead of `/compact`. https://blog.sshh.io/p/how-i-use-every-claude-code-feature
- Claude Code issue #24147: cache reads were 93 to 99.9% of raw tokens in users' own logs (ours: 98%). https://claudeissues.com/issue/24147-cache-read-tokens-consume-99-93-of-usage-quota-architectural-scaling-issue-with
- Eric Cheng: parallel subagents drained a plan about twice as fast (unverified). https://dev.to/onlineeric/claude-code-sub-agents-burn-out-your-tokens-4cd8

Our measurement: the local transcripts for 20 and 21 October 2026, scanned per request for cache reads, cache writes and output, weighted by list price.
