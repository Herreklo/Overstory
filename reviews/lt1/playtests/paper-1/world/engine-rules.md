# The engine's rules, for game masters

What Understory simulates and how, so a game master can run real lives and fill the gaps without breaking its logic. Read on 21 October 2026 from Understory `main` at `69cbc1d` (round 41), through the GitHub API, read-only. Claims cite Understory files; Overstory files are marked (Overstory).

## The world and its clock

- **A town of about 80 people,** run for thirty years of past and ten present years (`docs/STATUS.md`, What Understory is). Overstory's town has a few hundred buildings, so most people on screen have no engine life. Never give them one that reads as history.
- **One step is a month** (`docs/ARCHITECTURE.md`, A month). Order: body (illness, then deaths), work, social (contact, friendships, gossip, telling), situations, then pursuits, habits, groups, rivalries, plans, couples, births, then stress, money, migration and the yearly pass. Nothing happens at a finer grain than a month: no days, hours or alibis.
- **Each person meets at most one situation a month,** the weightiest first (`docs/STATUS.md`, Decisions).
- **Places:** the sawmill, the harbour fleet, the garage, the clinic, the school, the Courier (the paper), the Anchor (the bar), the council office, and one kind of venture, a café in the old bank; one cause, a summer festival on the quay (`src/setting.ts`).

## What an event carries

An event (`src/world.ts`, `Event`) has:

- a month, a type, and who was involved (the subject first);
- its text;
- **causes**, each with a kind (event, trait, value, state, belief, bond, want) and a **weight**, its share of the explanation;
- **visibility** (private, local or public);
- the evidence it gives about character;
- a **notability** from 0 to 3;
- for a decision, the options with their odds and the one chosen;
- **who knows it**, marked as seen or heard.

The bracket after each pack line is the reasons. A trait is said as a motive. "Though…" marks a reason that argued against the act (`docs/STATUS.md`, Decisions). A decision's top reason is checked: without it, the odds of the choice must halve.

**The packs are the truth,** not a townsperson's view. They print secret acts with their private reasons ("took a little from the trip money [thought nobody would notice]"). A player sees only what a witness could know.

## What it simulates, and how

| System | The rules | Source |
| --- | --- | --- |
| Households and couples | Dating, marriage, children. A row has two turns: the start (criticise, contempt, raise it gently, let it go) and the answer (defend, go silent, hit back, a repairing joke, hear them out). Drift, and doubts that build. A married partner decides to leave only after a year of serious doubt. A household leaves together, or one person is left behind. | `docs/STATUS.md` Couples; `src/love.ts`; `src/migration.ts` |
| Work | Hiring, promotion on the stronger record, being passed over, dismissal, retirement from 62. Accidents at the sawmill, garage and harbour about 0.45% a month each: they injure, never kill. Fishers go out into storms for the money. | `src/work.ts`; `src/situations/danger.ts`, `risk.ts` |
| Ventures and causes | The owner asks the people they regard most; each answer is that person's own decision. Whoever is threatened may fight it. The council's chief officer decides. A café that opens is a new place with jobs. When a plan fails, the owner holds a grudge, brings the plan back two years later, or lets it go. | `src/projects.ts`; `docs/STATUS.md` Plans |
| Friendships | Contact through habits, work, home, circles, groups and school. Liking follows shared values and warmth; recent contact halves in about six months, and friends who stop meeting lose touch. Friendships end in a quarrel or by losing touch. | `src/social.ts`; `docs/STATUS.md` Social fabric |
| Death and grief | Mortality follows a Gompertz curve (0.5% a year at 60, 1.6% at 70, 5% at 80), raised by poor health and illness. There are **four causes only**: a long illness (if ill), liver failure (a drinker under 72), in their sleep (over 79), a sudden heart attack (otherwise). A death is public, notability 3. Grief lasts 30 months for a partner, 14 for a child, 36 for a parent, 8 for a friend. Savings are split among the children. A want to make things right becomes "never made things right". A child living away may come home for the funeral and stay. | `src/body.ts`; `src/migration.ts` |
| Habits | Fifteen routines (the garden every morning, two pints most evenings, cards on Tuesdays, the choir, running the coast road…), taken up, lapsed, come back. | `src/time.ts`; `src/setting.ts` |
| Money | Savings in units: pay by workplace, living costs, children, drink. Debt has a floor. People ask family or friends for money, and the hat goes round at the Anchor for anyone hit by illness or loss. | `src/money.ts`; `src/situations/collection.ts` |
| Promises | About 1.5% of people a month promise a friend, partner or circle member something (the roof, the day, paying it back, the kids or garden, a word put in), due in 1 to 4 months. It is kept or broken. | `src/situations/obligation.ts` |
| Secrets | About 1.2% of working adults a month meet temptation: skimming the place's money (the till, the catch, the trip money, the medicine cupboard), covering up a mistake, or letting a coworker take the blame. Secret acts are private. A holder faces confiding 8% of months, and confides their latest secret. The friend keeps it, tells it (up to three others learn it), or confronts them. If told, half the time it gets back, and the friendship ends. Someone can be found out. | `src/situations/temptation.ts`, `discovery.ts`; `src/effects.ts` |
| Witnesses | Those involved see an act. For any act that is not private, partners and coworkers see it too. Public news reaches the whole town faintly. Local news reaches people whose work is with people (the Anchor, the clinic, the school, the Courier) by chance. | `src/world.ts` `witnessesOf`, `broadcast` |
| How news travels | **Gossip:** an act seen in the last two months may be passed to friends and a partner (25% × sociability). **Telling:** a weighty act (a decision of notability 0.8 or more, not texture, not private) may be told once by the person it was done to or someone who saw it. It goes to the friend or partner they like most who knows the person it is about. That hearer may tell it once more, less surely. Telling bends: a teller who likes the person softens it, and one who dislikes them, or is insincere, hardens it. An insincere teller (sincerity under −0.8) names the wrong person 15% of the time. **Telling stops when the person it is about is dead or away.** | `src/social.ts`; `src/telling.ts` (on since round 40: `SUMMARY.md`; the file's header still says off) |
| Wrong beliefs | Beliefs are estimates that strengthen with evidence. A liked person gets the benefit of the doubt. Others' failures read as character. A wrong belief that someone dislikes you can make itself true ("believed Amelia disliked him (wrongly)"). The witness's reads ("Noticed: …") include wrong ones. | `src/world.ts` `observeAs`; `src/social.ts`; `docs/STATUS.md` The witness |
| How people change | Plasticity falls with age (about 1.7 at 18, 0.3 at 65). Weighty and public events leave marks (sore spots, fears, rules to live by) that fade. The month after a blow (a death close to them, a break-up, being passed over, found out, shamed in public, a want failing), the person decides once: start again at work, take up a routine, keep away from someone, or carry on. Events open new wants. Thirty years move how someone chooses only about 3%. | `docs/STATUS.md` People, A way of being; `src/aftermath.ts`; `SUMMARY.md` |
| Drink | Drinking starts as a way to go numb under strain or after a blow, more often for the imprudent. It costs money, weakens the work record, nearly doubles the risk of illness, and leads to liver failure under 72. People stop, too. | `src/families.ts` `numb`; `src/body.ts`; `src/money.ts`; `src/work.ts`; `src/stress.ts` |
| Music | Bands, the only kind of group: songs, gigs at the Anchor, the open night, songs claimed by others, a member asked to go after three rows in three years. | `src/group.ts`; `src/setting.ts` |

## What it does not simulate

When a concept needs any of these, the game master simulates it and labels it **GM-simulated**.

- **Killing, violent or accidental death, suicide, drowning.** None. The four natural causes are all there are (`src/body.ts`). Accidents and storms leave people hurt and ill for 2 to 6 months (`src/situations/danger.ts`). A death while ill is worded "after a long illness".
- **Crime beyond small dishonesty:** no police, courts, inquests, autopsies or wills. Hostile acts are words and coldness: shouting, snapping, contempt, dressing down, whispering (`src/families.ts`). There is no physical violence.
- **Sport.** None. Bands are the only group kind (`src/setting.ts`).
- **Buildings and homes:** no addresses, owners, rent or repairs. "A house of their own" is a want bought with savings, without a place (`src/setting.ts`; NOW.md (Overstory); engine issue #59).
- **Places closing.** Workplaces never close; ventures only open (NOW.md (Overstory); `src/projects.ts`). The corner's shops are `authored`.
- **Records and media:** nothing written. The Courier prints nothing; there are no posters, letters or registers (`docs/facts-contract.md` (Overstory), request 9).
- **Weather** beyond "a storm came in"; time below a month.
- **People away:** frozen. Only people in town fall ill, die or meet anyone (`src/life.ts`, `src/scale.ts` `town`).
- **The player:** the engine has no commands yet (#22 paused, `SUMMARY.md`).
- **Class and upbringing** (`docs/STATUS.md`, weakness 8); religion and politics are absent from the setting pack (`src/setting.ts`). Rule 8 applies.

## Rules for GM-simulated outcomes

1. **Order of authority:** engine lines, then the fixture (`authored`), then the game master. Never contradict a pack line. Where the engine has a fact, it wins over the fixture (`docs/facts-contract.md` (Overstory)).
2. **Simulate in months, at the engine's rates:** a promise 1.5% a month, a temptation 1.2%, confiding 8% of months while carrying a secret, an accident 0.45% per workplace, mortality on the curve above. Keep rare things rare.
3. **Who knows follows the witness rules,** then gossip and telling. Talk about the dead or the absent is GM-simulated, but give it telling's shape: it starts with someone who saw or was wronged, goes to one close hearer, may pass second hand once, and is bent by liking.
4. **Decide from character as the page shows it.** The reasons on a person's page are the evidence. Someone who "lets things go" usually does, not always.
5. **No new causes of death, no violence, no crime the engine lacks,** unless the card requires it. If it does, label the whole thread GM-simulated fiction outside the engine.
6. **Evidence, not verdicts.** A character's read of someone is an opinion and may be wrong.
7. **Worlds don't meet.** A pack page is one person in one version of one world. Two pages share a world only when their events show it (the A/B letter is dealt per pair). Names repeat across worlds as different people.
8. **Label every outcome in the log:** `engine` (file, P-number, version), `authored`, `GM-simulated` (with the rule above it follows), `re-dated` (the shift), `swapped` (an anachronism replaced). Screens carry no labels.

## How to re-date

The packs run from 2026 to 2035; the town on screen starts in 1989.

- **One shift per world: −40.** 2026 becomes 1986, 2029 becomes 1989, 2035 becomes 1995. Every year in a line or its reasons shifts with it: "(b. 1956)" becomes "(b. 1916)", "since 2017" becomes "since 1977". Ages and spans stay ("after 13 years", "aged 46").
- **1986 to 1988 become the starting record** (the past before the screen). 1989 to 1995 play on screen. After 1995 the packs are silent: anything later is GM-simulated, or comes from a fresh engine run (the export tool merged on 21 October, `src/tools/fixture.ts`, #68).
- **Anachronisms:** the packs are nearly period-neutral. A scan found no mobile phones, apps or internet, with one exception:
  - "the plan to go online and stop the Saturday print" becomes "the plan to go over to computer typesetting and stop the Saturday edition" `[swapped]`.
  - Phone lines read as landlines ("sounded like a stranger on the phone").
  - Television, cancer, stroke, surgery, adoption and head office all fit 1986 to 1995.
- **Don't shift the fixture.** Its years are real years (`authored`). Where a re-dated engine fact clashes with a corner event, the engine wins, the event is redrawn, and the change is logged.
- A world may take another shift (say −39) to meet the corner, but only one shift per world, logged once.
