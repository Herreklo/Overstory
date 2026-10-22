# Facts contract (draft)

**Draft, 21 October 2026, on Opus 5.5.** The architecture session (Fable, from 26 October) confirms or changes it. It decides nothing beyond itself.

For every kind of fact the town shows, it says whose it is. It answers the pre-mortem's third story, "Overstory became the engine" (`docs/research/pre-mortem.md`): our rules grow the past and set owners and care, and will clash with the engine's households when homes land (#59).

## In short

- **FC1** The engine decides that and why, our rules how it looks, the seed which exactly. History is a fact with one owner; the engine's wins: what was drawn from ours is redrawn, the span from S reruns on its facts, a contradicting curation pin dropped and reported. Care never comes from character (Rule 8); patchwork, texture, land and era parts stay ours. Evidence: The rule. Reopens: the engine's facts.
- **FC2** People start at S (1959 for 1989, #23); before S, our curated starting record, never rendered. From 1989 only engine events, accepted player commands included, change it; we derive only its gaps. Evidence: Two years. Reopens: #23.
- **D3.3** Four labels (21 October): `simulated`, `generated-past`, `derived` (no readable year unless a story pins it), `authored`; `engine` retired (disputed). Evidence: `building-blocks-decisions.md` §4. Reopens: none named.
- **FC3** Hand-off checks: each household addressed at S; one owner a plot; no `authored` or `derived` after S where the engine has it; every 1989 business housed; replacements logged. Evidence: Checks. Reopens: none named.
- **36** The real run: unedited, `simulated`, drawn at 1989 by our rules; a broken rule changes ours, never the engine (disputed). Evidence: A frame. Reopens: none named.

## The rule

- The engine decides that a thing happened and why (FC1). Our rules decide how it looks. The seed decides which exactly (`docs/living-fabric.md`).
- Anything that reads as history is a fact with one owner below.
- When the engine has a fact, it wins. Ours is replaced, what was drawn from it is drawn again, and no visual claim survives that contradicts it.

## Two years

- **The people's start year** (FC2; S: 1959 for a game shown in 1989, #23). Before S lies the starting record: made once by our rules, curated, never rendered. From S the engine decides people, owners, care and works, as far as it models them (`docs/town-system.md`, §3).
- **The show year** (1989). From here only the engine's events change the record, the player's accepted commands among them. Our rules derive only what the engine does not model. The corner fixture's events after 1989 are test stand-ins.

Both sides write the years from S to 1989 today. That span is the seam.

## Labels

As in `docs/engine-contract.md` and `docs/town-system.md` (D3.3). Some notes say `engine` for `simulated`; the architecture picks one word.
- `simulated`: decided by the engine.
- `generated-past`: form written once from the pack's script (units, plots, first buildings, fires, plans); kept if the engine's fabric pass takes it over.
- `derived`: an actor's decision made by our rule. It shows no year a player can read unless a story pins it as a fact.
- `authored`: by hand: the pack, fixtures, curation.

## Whose each fact is

Bare numbers are requests in `docs/engine-requests.md`; #n are engine issues.

| Fact | Owner now | Owner when the engine has it | Label now | Hand-off | When the engine disagrees |
| --- | --- | --- | --- | --- | --- |
| **People:** birth, death, kin, work, money, habits | engine; fixture people stand in | engine | `authored` | S; builders before S are roles ("a cooper"), not persons | The engine's person replaces ours; the appearance seed follows its id |
| **Households:** members, address, flat, own or rent | members implied by the engine; address and tenure ours | engine (#59, 15) | `authored`, `derived` | S, when homes land | It takes the address; lit rooms, cars and emptiness are drawn again, and a house it fills loses our neglect |
| **Owners:** kind, horizon, sales, inheritance | ours: by rule in the grown past, by hand on the corner | engine (24) | `derived`, `authored` | S | It replaces ours from the year they differ; care and works after it are derived again |
| **Keepers and care** | keeper: the owner or a department; care by our rule from money, presence, age and dated events, not character (pre-mortem story 11, proposed) | keeper: engine. Care: our rule on its facts, unless 19 adopts it | `derived` | keeper at S | Care is recomputed; coats, patches and neglect from the old care go |
| **Works and repairs:** campaigns, renewals, alterations | ours: by hand on the corner, by rule elsewhere (`stair_facts.py`) | engine: decisions with reasons (14), or our rules in its fabric pass (19) | `authored`, `derived` | S | They replace ours from S; the life reruns. Patchwork stays ours: it claims no dated event |
| **Ventures and shops:** opening, closing, hours, building | opening: engine. Building: our rule (cheapest fitting vacancy near the founder). Closing: ours. Hours: the pack's | engine (4, 5, 21) | `authored`, `derived` | openings at S; closings with 4 | A shop the engine lacks is stripped or never fitted. A sign or ghost stays only for a business the record holds |
| **Made year and construction:** buildings, ways, walls, trees, lamps | ours: by hand on the corner, grown elsewhere | before S ours, or the engine's fabric pass (6, 22); after S the engine's (5, 14) | `authored`, `generated-past` | S, for things made after it | The engine's wins; the thing is made again, with nothing of the old era on it |
| **The 1989 town's starting record** | ours: made once, curated, regenerable | before S ours, unless the engine's past replaces it; from S the engine's | `generated-past`, `derived`, `authored` | S | The span from S reruns on the engine's facts. A curation pin that contradicts it is dropped and reported |
| **Land and plots** | land: the pack. Units and plots: grown from its script | land ours for good; units the engine's founding acts (22) and addresses (25), laid out by our library | `authored`, `generated-past` | land never; units at S | The engine's acts and addresses win; plots are laid again to hold them |
| **Plans and building rules** | the pack's script; each claim's fate by our rule | engine (23) | `authored`, `generated-past`, `derived` | S | They replace ours from S; scars are derived again |
| **Materials and parts by era** (the pack) | ours | ours for good; the timeline is one list both read (3) | `authored` | never | It states no event. Where the shared timeline dates an era differently, the timeline wins |
| **Wear, growth, weather, light** | ours: rules from facts; footfall and storms by hand | rules ours for good; inputs the engine's (feet 16, storms 18) | inputs `authored` | inputs with 16 and 18 | The rules rerun on the engine's inputs; a mark whose cause it lacks goes |
| **Seeded texture:** grain, a lean, where a slab cracked | ours | ours for good | none | never | It claims no history. Texture that reads as history becomes a fact or is quietened |
| **Records and signs** (perceived) | signs ours, from their business; posters and the paper from a pack catalogue | records that can be wrong: engine (9); signs ours | `derived`, `authored` | with 9 | A record may be wrong about the world. The engine's record replaces ours; a sign follows its business |
| **Scene state:** bins, open windows, puddles, who is where tonight | ours, from the engine's facts and the hour | ours; what matters goes back as engine events | never stored | open with the engine (two clocks) | It yields at once. What would matter later is committed to the engine or dropped |
| **The player's acts** | none yet; fixtures stand in | engine: commands it accepts or refuses, held in the save | `authored` | the first command (#22) | A refused act leaves nothing. An accepted one is drawn like anyone's |

## Checks at the hand-off (draft)

From the pre-mortem (FC3): every engine household has an address at S; no plot has two owners at once; no `authored` or `derived` fact after S where the engine has one for the same thing; every business the engine has in 1989 stands in a building; every replacement is logged, so drift shows.

## A frame from a real engine run

Request 10 in `docs/engine-requests.md` (one real run). One corner frame is drawn from it before plan step 2.

**The fixture asked for:** a small world from an actual run, exported unedited through the front door (`r41` or later): its tag, ruleset, seed and start year (the engine's own until #23); people with ids, births, deaths, kin, jobs and money; households as the engine implies them; places and ventures with their opening months; events to 1989 with ids, months, who and causes.

**What we do with it** (36):
1. Commit it under `fixtures/` as it came, labelled `simulated`.
2. Map it onto the corner: ventures take buildings and households take addresses by our rules (`derived`); the engine has no buildings or homes yet.
3. Replace every corner fact the run decides, and draw the corner at 1989 with the share of `simulated` facts counted.
4. Record each disagreement. Where the run breaks a rule of ours, the rule or this page changes, never the engine.
