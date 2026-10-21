# Interface and inspection

How the player points at, hovers over, inspects and asks about things, people and history, and how the screen answers without passing verdicts or covering the painting. It serves criteria 1, 3 and 4 in `CLAUDE.md`, and through them the overall question: can someone read people and history better from the world on screen than from the engine's page? It takes up what `interface.md` began, and the parts of `time-on-screen.md` and `history-in-things.md` that touch the interface: the why-probe, the journal, comparing years, the history budget and the cause view.

Written on Opus, October 2026. Two helper passes ran beside the main one: one on how shipped games let players read a world, one on highlighting, picking, input, accessibility and text on our stack. Claims from a maker's own words, a paper or official documentation are unmarked. Those from reviews, wikis, abstracts or search summaries are marked (secondary), and those no source confirmed (unverified). Our own arithmetic or reading is marked (our estimate). What would not open is listed under Gaps.

## The bottom line

- **The eye reads the traces; the interface carries everything else.** If the interface says what the picture shows ("this step is newer than its neighbours"), the picture is redundant and the scene turns back into the page. So hover names things and the eye reads their marks. Inspection gives what the eye cannot get: records, accounts, the player's own notes and a field guide to how things age. Describing the traces is an accessibility option.
- **Every claim travels with its source, in the words and in a mark.** About a quarter of the world's languages mark in their grammar how the speaker knows: seen, heard, inferred or reported (Aikhenvald; secondary). The interface does the same: "you saw", "Ruth said", "the Aftenblad reported", "probably". Showing a source beside a claim is not enough on its own: making publishers more prominent changed nothing in a study of about 7,000 readers (secondary). The source must be part of how the claim is read and stored.
- **Counts, not adjectives.** Words like "likely" spread from 55 to 90 per cent between readers (secondary), and counts of cases roughly triple correct reasoning over probabilities (secondary). The engine already says "seen 4 times, once the opposite". The interface keeps the engine's own hunch words for what people believe and uses counts for what the player has seen.
- **The highlight must never read as light.** Every light in the town is a fact, and the art has no drawn outlines. A hover that looks like a patch of sun or a lamp is a false claim. The hover is a small even lift with no direction and no shadow, and the cursor's change carries most of the signal. Inspecting dims the rest of the frame a little, as a painter loses edges away from the focus.
- **Reveal modes take over play.** Rocksteady cut back Arkham's detective mode after players left it on nearly the whole game (secondary). Our rule: marks on the map, never in the painting. The world shows a history unprompted only when the player asks, or across a jump within the history budget.
- **The game should never confirm a reading of a person, and should confirm a fact only when independent sources agree.** Games range from Obra Dinn's batches of three to Pentiment's "there cannot be a right answer". Heaven's Vault confirms a guess only when the word recurs in other contexts. That is the right model for a town that remembers.
- **Two levels, then the journal.** Nielsen warns that more than two levels of disclosure lose people. Paradox's nested tooltips go deeper only because each level is optional and the cursor can travel into it. Ours: hover, then a card; the why-chain opens one step inside the card, and anything deeper lives in the journal.
- **On the M4, keep the hover inside the main pass.** Anything that samples neighbouring pixels (edges, blur, jump-flood outlines) breaks Apple's tile memory and costs a pass with a store and a load. A per-pixel lift keyed to a global id costs one compare per pixel. Picking renders ids for a small region round the cursor only when something moved, and reads them back a few frames late.
- **The building blocks must make every drawn pixel answer "which record, which part?"** This holds at every tier, merged or instanced, with ids stable across dates. They also need label anchors, bounds for snapping, a hierarchy from part to thing to place, and the shared highlight function in every shader.

## 1. How games let players read a world

### Pointing

Point-and-click games show what can be touched in three ways: the cursor changes over a hotspot, the thing lights, or a key reveals every hotspot at once. Ron Gilbert brought the verbs back in *Thimbleweed Park* because adventures had shrunk to a single "use"; hovering highlights the likely verb, and the right button performs it (GamesBeat). The cursor tells the player what will happen before they commit.

*Disco Elysium* marks interactables with small orbs, and on PC the Tab key highlights everything clickable (Steam threads; secondary). An option is reported that highlights things only when the detective is close enough and his skills would notice them (secondary). A reveal limited by perception fits a world that knows what each person could see. The console version is the warning: the player sweeps the right stick until something lights, the selection is not sticky, and nothing highlights by proximity (Can I Play That; secondary). Blizzard solved the same problem in *Diablo II: Resurrected* with a wide cone from the stick. Candidates are ranked by kind and weighted by class, and only one primary target shows; showing them all was overwhelming (Blizzard). Larian's *Baldur's Gate 3* gives the pad direct control and an optional free cursor. A light trigger pull peeks at a menu before committing (PlayStation Blog).

### Inspecting

Inspection in these games comes in four forms.

- **The object in hand.** *Gone Home* lets the player pick up almost anything, turn it and read it; key papers are kept for later (unverified). *What Remains of Edith Finch* writes narration into the scene beside the thing it is about (unverified). *Kentucky Route Zero* gives objects short written descriptions instead of zoom-ins, which keeps a distance (Critical Distance citing John Sharp; secondary).
- **The panel.** RimWorld's inspect pane has tabs for needs, health, social and a log, and an info card breaks every figure into what made it (unverified). The Sims names each moodlet's cause and the time left (wiki; secondary, in `interface.md`). *Victoria 3*'s UX diary added breakdowns that show how a number was calculated and explanations of why something is not connected (Paradox, dev diary 74).
- **The nested tooltip.** In *Crusader Kings III* and *Victoria 3*, highlighted terms in a tooltip open further tooltips, like a wiki beside the cursor (PCGamesN; secondary). A tooltip locks after a hover timer (the default) or on a middle click for experts (a developer quote relayed on a forum; secondary). Paradox moved tooltips so the cursor can travel into a nested one without opening another on the way (dev diary 74).
- **The glossary.** *Pentiment* underlines terms in red in dialogue and descriptions; a key opens an illustrated entry on people, places, customs and history (guides; secondary). At launch the glossary sometimes showed late-game entries in the first chapter (Steam; secondary). A knowledge index that leaks is a spoiler and, for us, a false claim about what the player knows.

### Knowledge kept

The journal is where reading becomes understanding, and the best ones keep each finding tied to where and how it was found.

- *Outer Wilds* has one progression: what the player knows. Its ship log has a map mode (findings under the place they belong to) and a rumour mode (cards joined by arrows to the places they point at). A place heard of but not visited is a "?" card (Edge; secondary for the visuals). Mobius rebuilt the log into a more visual detective board after playtests, because how it was organised changed how players read the information (Mobius blog, 2017).
- *Return of the Obra Dinn*'s book holds a manifest, sketches, deck plans and chapters. Lucas Pope said the narrative structure was basically the book (Game Developer). Fates are confirmed only three at a time, which stops guessing (secondary).
- *Caves of Qud* generates each sultan's history as events, each giving one account, a "gospel". Shrines, paintings and people each carry one gospel, found in any order and written into the journal sorted by date, so a biography assembles itself. The authors chose to generate accounts from limited perspectives rather than historical logic, and let causes be rationalised after the events (Grinblat and Bucklew, 2017). The delivery suits us; the invented causes do not, except inside records that may be wrong.
- *Her Story*'s whole interface is a search over a police database. Any term returns only the first five matching clips, so asking well matters (PocketGamer.biz; secondary), and Sam Barlow used data on which words were over- or under-used to tune what each query gives up.
- *Firewatch* has no map on screen: Henry takes out a paper map and compass, and routes and circles get drawn onto the map as the story goes (Game Developer; secondary). The "you are here" dot can be turned off (secondary).
- *Shadows of Doubt* opens evidence in movable case-file windows that pin to a corkboard. A string's colour, white to red, shows how incriminating a link is; its width shows how reliable (ColePowered devblog 4).

### Known, guessed and doubted

| Game | How certainty is shown | What it teaches us |
| --- | --- | --- |
| Obra Dinn | confirmed in threes; a confirmed fate becomes print (secondary) | ration confirmation; change the medium when something is settled |
| Heaven's Vault | translations never confirmed by the game; a guess keeps its question mark until the word recurs in other contexts (Ingold; secondary for the mechanics) | confirmation by agreement between sources |
| Golden Idol | a check says when two or fewer answers are wrong, not which (unverified) | partial checks keep certainty earned |
| Paradise Killer | the trial starts when the player feels ready; even a correct belief needs evidence to convict, and the game does not say whether the account is true (Smith and Crabtree, MCV) | believing and proving are different acts |
| Pentiment | no culprit exists to be confirmed (Sawyer, via Shacknews); an alibi system was cut because alibis only rule people out (Game Developer, via GameBanshee) | where the question is whom you blame, nothing confirms |
| Shadows of Doubt | incrimination in colour, reliability in width (ColePowered) | content and reliability on separate channels |
| Disco Elysium | skills speak as named voices inside the dialogue, and can be wrong; a thought's effect stays hidden until it is internalised (Kurvitz, via GameBanshee) | an inner voice is a fallible source with a name |
| Outer Wilds | "?" for heard of but unseen | perceived against seen, on the map |

Pentiment also shows a reading through type. Characters' typefaces mark class and literacy, and a character's face changes as Andreas's view of him changes. Testers were confused at first, then understood (Sawyer, via GameBanshee). A display that carries the viewer's current opinion is a fallible read made visible without a verdict.

### Reveal modes and their trap

Arkham Asylum's detective mode tinted the world blue and outlined everything that mattered. Players left it on for nearly the whole game, and Arkham City cut its navigation help back because it felt like an exploit (Rocksteady, relayed by PlayStation Blog and Digital Trends; secondary). Witcher senses and Horizon's focus draw similar criticism as follow-the-colour play (unverified). *The Last of Us Part II* turned the idea into accessibility. Its High Contrast Display mutes the environment and colours allies, enemies, items and interactables, and its Enhanced Listen Mode pings targets with a pitch for height (Naughty Dog, PlayStation Blog).

The yellow-paint argument is the same trade at the scale of a level. Remedy's Mikael Kasurinen avoided heavy signposting in *Control Resonant* by choice: when the world says "go here", the decision is no longer the player's (Game Developer, September 2026). Developers on the other side point out that many players need the cue (Wikipedia, Know Your Meme; secondary).

### People are not kiosks

Jake Elliott did not want people in *Kentucky Route Zero* to be information vending machines; visited places drop off the map and their conversations cannot be repeated (PC Gamer). *Paradise Killer*'s first builds made players read every biography on a computer before leaving the start; the team called it a bad experience and moved the facts into first meetings (MCV). Knowledge about a person should arrive with the person.

## 2. The theory

### Scent, patches and two levels

Pirolli and Card model people looking for information as foragers. Their patch models decide how long to stay in a cluster of information. Their scent models judge value from nearby cues, such as a link's label, before paying to follow it (Psychological Review, 1999; abstract, secondary). For us the scent is the hover label and the cursor: they must say enough to tell whether inspecting is worth it, and nothing that makes inspecting pointless.

Shneiderman's mantra, "overview first, zoom and filter, then details-on-demand", adds relate, history and extract to its seven tasks (1996; unverified, the paper would not open). The city camera is the overview, the camera's zoom is zoom, the journal's views are filter and relate, the card is details on demand, and the journal itself is history. Nielsen's progressive disclosure puts what is often needed first and the rest one clear step away. He warns that designs with more than two levels lose their users (NN/g, 2006). NN/g adds that a tooltip must never hold what a task needs, must open on keyboard focus as well as hover, and does not exist on touch.

### Diegetic or not

Fagerholt and Lorentzon (2009) sort interface by two questions: is it part of the fiction, and does it sit in the game's space? That gives diegetic, non-diegetic, spatial and meta interface. Marcus Andrews, reviewing their work, found *Far Cry 2* "nearly hopeless" to make fully diegetic. *Dead Space*'s in-world map was so poor for navigation that a line projected on the floor was added. His rule: keep every function and translate it into the world where you can (Game Developer, 2010).

Our camera has no body to hold a map, so Firewatch's answer is closed to us. What stays open is the world's own media shown as themselves: a poster, a clipping, a ledger page, a photograph held up at its spot. Beside them sits a quiet non-diegetic layer for what the player knows.

### Signposting and attention

People hold about four chunks in mind at once (Cowan 2001; abstract, secondary), and find three or four changes in a scene before they stop (`time-on-screen.md`). Labels that cover a view fail the same limit. Museums learned it with text. Across 110 exhibitions, visitors stopped at about a third of the elements, and the longer a label, the less it was read (Serrell; Bitgood; secondary). A common rule caps a block of text at about 75 words (AAM; secondary).

### Sources, certainty and memory

- Many languages mark in their grammar where a statement comes from. Tariana has four terms: seen, sensed otherwise, inferred and reported (Aikhenvald; secondary). Those four, plus "written" for records, are the kinds the interface needs.
- The Admiralty code rates a source's reliability (A to F) apart from the information's credibility (1 to 6), so a good source can still pass on something improbable. Its 1 is "confirmed by other sources" (Wikipedia; secondary). A 2025 study is reported to find that raters align the two anyway (secondary).
- Words for chance are vague. In a survey of about 1,700 people, "likely" covered 55 to 90 per cent and "real possibility" 20 to 80 (Mauboussin and Mauboussin, HBR 2018; secondary).
- Counts beat probabilities: natural frequencies raised correct Bayesian answers from about 16 to 46 per cent (Gigerenzer and Hoffrage 1995; secondary).
- People do not store a tag saying where they learned something. They judge the source later from the memory's detail, and get it wrong (Johnson, Hashtroudi and Lindsay, 1993; secondary). A label beside a claim is not enough: making publishers prominent did not change whether about 7,000 readers believed or would share headlines (Dias, Pennycook and Rand, 2020; secondary).
- Corrections need an alternative. In the warehouse-fire studies, people who remembered a retraction still used the retracted cause, unless another causal account replaced it (Johnson and Seifert 1994; Nyhan and Reifler; secondary).
- Explanations are contrastive and selected. People ask why this rather than that, pick a few causes, prefer abnormal ones and expect the answer to suit the asker (Miller 2019; secondary). They prefer explanations with fewer causes, and a simple unlikely one inflates belief in its cause (Lombrozo 2007; abstract, secondary).
- Hand-drawn wobble on a line read as uncertainty as readily as blur (Boukhelifa and colleagues, 2012; secondary). A painterly world can draw what is conjectured looser, as the conservation charters ask (`time-on-screen.md`, section 3).

The engine already speaks this way. Its witness holds beliefs as hunches ("You'd bet", "You're fairly sure", "You have a feeling") and splits hindsight into causes seen and unseen. Its next human test shows each impression with its count: "seen 4 times, once the opposite" (`behaviour-on-screen.md`, section 1).

## 3. Pointing in a painted world

### Highlight styles against our rules

`docs/visual-direction.md` rules out drawn outlines, makes every light a fact, and gives each frame one focal point where the strongest value contrast meets the hardest edge. A highlight must work inside those rules or be legible as interface rather than world.

| Style | Keeps the painting | Can be read as a fact | Cost on the M4 | Verdict |
| --- | --- | --- | --- | --- |
| Outline (hull, stencil or edge pass) | no: a drawn line | rarely | hull or stencil stays in the pass; an edge pass breaks it | accessibility mode only |
| Jump-flood halo | partly, as a soft lost edge | as glow or fog | about log2(width) passes; roughly 150 MB a frame at 1440p unless scissored (our estimate) | only scissored, only if frames ask for it |
| Rim or fresnel lift | partly | as backlight | free in the shader | no: reads as light |
| Even value lift on the thing | yes, if small | as a sunlit patch if warm or directional | free in the shader | yes, for hover |
| Dim and desaturate the rest | yes: the painter's focus | as dusk or a mood if strong | one per-pixel step, foldable into the post pass | yes, gently, for inspect |
| Cursor change and label only | yes | no | none | always, as the main signal |

So the hover is three things together: the cursor changes, a name appears after a short dwell, and the thing lifts evenly by a small amount with no hue and no direction. Inspecting adds a gentle focus: the rest of the frame loses a little value range and chroma, as a painter leaves edges soft away from the focus. Both are judged on frames in the three lights, at one-eighth and in greyscale, and cold readers must never report them as light, weather or mood (Tests).

### The cursor

The cursor is the cheapest honest signal. It carries the default act, as Thimbleweed's verbs do: look at a thing, read a record, listen to a person, enter a door. Four shapes are enough, each different in silhouette, not only in colour. It is drawn as a small painted mark, not a system arrow.

### Pad, trackpad and touch

Apple asks every Mac game to support keyboard and pointer even when pads are supported, recommends single-key commands and rebinding, and sets touch targets of 44 points for frequent controls (Apple HIG). A Mac trackpad has hover; touch does not.

- With a mouse or trackpad, hover names and a click inspects. Two-finger scroll zooms. Pinch is not relied on, since Unity's support for it on macOS is unconfirmed (unverified).
- On a pad, the camera moves on the sticks, and the pick is the nearest pickable thing to the screen's centre within a cone, as in D2R. It sticks with hysteresis, the shoulder buttons cycle candidates, and a free cursor is one button away, as in Baldur's Gate 3. The bubble cursor is the evidence: growing the active area to the nearest target cut errors from 2.98 to 1.58 per cent. A huge bubble distracts, so its radius is capped (Grossman and Balakrishnan, 2005).
- On touch, later, a tap does what hover does and a second tap inspects.

### Accessibility

The floor comes from Microsoft's Xbox Accessibility Guidelines (XAG) and the Game Accessibility Guidelines.

- Text: 18 px body height at 1080p on PC, so 24 px at 1440p (our estimate), scalable to 200 per cent, lines under 80 characters, line spacing 1.5 (XAG 101). On a 13-inch Mac at its default scaling that is about 15 to 16 points, above Apple's 13-point default (our estimate).
- Contrast: 4.5 to 1 for text against the lowest-contrast patch behind it, 3 to 1 for large text, and a high-contrast mode at 7 to 1 (XAG 102). Over a painted frame that means a plate behind text.
- Never colour alone; a plain-font option; hold or toggle for every hold; no pulsing by default; a key that reveals what can be picked nearby.
- No dyslexia font: OpenDyslexic gave no gain in a small study (Wery and Diliberto, 2017), and Dyslexie's benefit came from its spacing (secondary). Letter spacing is the setting.
- The strong options, as in The Last of Us Part II: an outline mode, speech for cards, and an option that describes the traces in words.

### Cost on the M4

Apple's GPUs work tile by tile, loading and storing each attachment at the start and end of a pass. Memoryless attachments live only in tile memory, and programmable blending lets several passes merge into one (WWDC20, session 10602). Unity's render graph merges passes that read only the current pixel through framebuffer fetch, on Metal and Vulkan (Unity manual). So:

- The hover lift is a compare of a global id against the part's id in the lit shader. No pass, no material swap, and it works with merged chunks.
- The focus dimming is a stencil mask drawn after the opaques (one draw of the selected thing, colour writes off) and a stencil test in the existing post pass.
- Anything that reads neighbouring pixels needs its own pass. A jump-flood halo is about five passes for a 32-pixel spread; scissored to the selected thing's box it costs a small fraction of that (our estimate).
- Under the GPU Resident Drawer, instances take no per-instance property blocks; only transform, layer and rendering-layer mask vary (Unity manual). Ids for instanced parts must come from instance data we control or from position (section 6).

## 4. Inspecting history and people

### What the eye reads and what the interface carries

The five kinds of thing on screen (`CLAUDE.md`) and the record's four layers (`docs/living-world.md`) decide where each piece of knowledge lives.

| On screen | Read by | The interface shows |
| --- | --- | --- |
| Traces: wear, a patch, a later window, a ghost sign | the eye | the thing's name; the field guide's general entry ("float glass came in from the late 1960s"); a description of the trace only as an accessibility option |
| Canonical facts | the eye, where they show; otherwise records | only what a record, an account or the role's knowledge dial gives |
| Records: a sign, a poster, a deed, the paper | the eye at eye level; the card at a distance | the record as itself, quoted, with maker, date and purpose |
| Accounts: what a person says | the scene | the words, with who said them, when, and the engine's hunch word |
| Non-semantic texture | nobody | nothing; it is not pickable as a history |
| Local scene state: a blind drawn, the chairs out | the eye | nothing beyond the name |
| The player's own notes and guesses | the player | the journal, in the player's own type |

This split is the study's main decision. Criterion 1 asks whether a viewer reads a building's history from the picture. If the card reads it for them, the test measures reading, not seeing, and criterion 4 compares the page with the page. The field guide teaches the rule; the player applies it to the thing in front of them.

### "What happened here?"

A place's card shows what the player knows about it in date order, each line with its source. A timeline is chronological and must look unlike a chain of causes, because readers fill in a cause between two events placed together (`time-on-screen.md`, rule 7). Gaps are shown as gaps: "built ?", "before 1935", "a sign was here; what it said is unknown". Outer Wilds' "?" works because it invites the next step: the archive, a neighbour, an earlier photograph.

### The why-probe

"Why does this look like this?" is a contrastive question, so the probe states its contrast: why this step rather than its neighbours, why this front rather than its own front in 1960. The contrast comes from what the player pointed at and what sits beside it, or from the earlier year in a comparison.

- It gives one or two causes first, abnormal ones first, and the count of the rest one step away. People reject long lists and over-believe short ones (Miller; Lombrozo).
- It lists only causes the record links. An event in the same year without a link is not listed, not even as "also that year"; it belongs to the timeline.
- Every link carries its source: "The town's works ledger, 1911: lower run relaid after frost." A link the player has no source for shows as "?", with where such a thing might be learned.
- The role decides the depth. Where a game's knowledge dial includes the record, the probe can answer from it, marked as the record. In the observer game it answers only from what the player has found. The cause view (`docs/living-fabric.md`, section 5) stays a maker's tool.

### Provenance, in words and marks

| Mark | Words | From | Example |
| --- | --- | --- | --- |
| Seen | "you saw" | the camera witnessed it; a trace in view | "You saw her lock the shop at four, three Fridays running." |
| Heard | "you heard" | overheard, not addressed to the player | "You heard a man at the quay say the cannery is selling." |
| Told | "X said", with the engine's hunch word | an account | "Ruth said she's fairly sure the roof was redone after the storm." |
| Written | "the Aftenblad reported", "the sign says" | a record: maker, date, purpose | "Gig poster, 1989: the Anchor, Friday 13 October." |
| Inferred | "probably", with a decade | a rule from facts (`derived`), or the player's own note | "Patched, probably in the 1960s." |
| The record | "the record" | engine truth, only where the dial allows | "The record: laid 1874." |
| Unknown | "?" | nothing found | "Built: ?" |

Each mark differs in shape and word, never in colour alone. Two independent sources that agree earn "two sources agree"; two that disagree are shown side by side, and the game does not choose. Independence must be real: two people who heard it from the same teller count once, which needs the engine's chain of who told whom (`docs/engine-requests.md`). When a later source contradicts a claim, the journal keeps the claim, marks it disputed and shows what the contradicting source says, since a bare retraction leaves the old cause in place.

### Dates

A date shows at the record's precision: a year for a dated fact, a decade for a derived one, a season or month where the record holds it. In-world dates are written as people wrote them ("Friday 13 October 1989"); the year a record was made is kept apart from the year it describes ("a 1974 photograph of the 1931 sign").

### People across years

- Description comes before a name. Until the player has heard or read a name, a person is what the camera saw: "a woman of about sixty in a green coat, seen four times at the quay, mornings". It uses clothes, what they carry, what they do and where; never skin, body or features. The same words apply to everyone (`behaviour-on-screen.md`, rule 9).
- Counts, never traits. The card lists acts the player saw with counts, and accounts with their holders. A trait word appears only inside someone's quoted words.
- Recognition across a jump needs something that recurs (`time-on-screen.md`, rule 10). The journal keeps a strip of small captures from each sighting, so the player can hold a face from 1960 beside one from 1989.
- Asking again opens the account already heard.

### The history budget as an interface rule

The budget per view (one history per thing at the city camera, two at 12 m, three at the street stop) governs labels and highlights too. A reveal key shows which things can be picked, never their histories. Labels are placed by weight, and a view never carries more of them than its budget. Across a jump, highlights come only from the change query and within the same budget (`time-on-screen.md`, rules 5 and 6). Everything else waits to be asked.

## 5. Type and the look of the interface

The world's own lettering is a record: signs and posters in English, lettered in each era's styles (`NOW.md`, decided 22 October). The interface must never be mistaken for it, and it must not compete with it. Three type roles follow, as in Pentiment, where type itself carries meaning.

- The interface's voice is one plain face for what the game says about what the player knows. It is a serif made for screen reading or a humanist sans with a large x-height, under the SIL Open Font License (OFL): Literata, Source Serif 4 or IBM Plex, say. Its plain alternative is Atkinson Hyperlegible Next (OFL).
- Records appear as themselves: a poster, a sign or a ledger page as a facsimile in its own era's letters, with maker and date in the interface's voice beside it, never on it.
- The player's notes take a second face, so the journal separates "found" from "thought" at a glance.

Nothing in the interface imitates 1989. It sits outside the fiction (Fagerholt and Lorentzon's non-diegetic layer), and its period flavour would blur the line between record and interface. Apple asks for a shaded plate behind game labels over 3D scenes (HIG). Ours are paper-and-ink plates with a soft painted edge, no blur (blur samples neighbours and costs a pass). Their value follows the frame's exposure so a card at night does not glare, while text keeps 4.5 to 1 against the plate. The look of plates and type is decided on frames in the three lights with a strict review, like any look question.

Text is 24 px body at 1440p by default, up to 200 per cent. Cards keep lines under 80 characters and hold about 50 to 75 words: three claims at most, then "more in the journal". Labels are one line. Screen-space labels keep their pixel size, where text drawn in the world shrinks below the minimum with distance. They are placed on a 32-pixel grid by greedy priority, as Mapbox places map labels. They are re-placed every 100 to 150 ms, not every frame, and fade over 200 to 300 ms with hysteresis so they do not blink (Mapbox GL Native wiki).

## 6. What the building blocks must carry

The architecture is designed next week. For the interface it needs these, each also serving the cause view, the change query and the cold readers' keys.

1. Every drawn pixel answers "which record, which part?", at every tier. Merged chunks keep a chunk-local index in a vertex channel and a lookup table per chunk. Instanced kit pieces need an instance index in data we control. The GPU Resident Drawer allows no per-instance properties, so either those pieces go through our own batch renderer group or the id is resolved from depth and position through a spatial index (our estimate; a spike decides). Skinned people, alpha-tested leaves, terrain and decals such as posters each need a picking path, and a poster stack picks the top sheet and exposes the ones beneath.
2. Ids stay stable across dates and rebuilds. A part keeps its id for its whole life and a replaced part gets a new one (`time-on-screen.md`, building blocks 7). Locks keep ids through regeneration, so a journal entry still points at the right step.
3. A hierarchy of part, thing, group (the flight, the house, the block) and place. Hover picks the level that suits the distance: a step at eye level, the steps at the street stop, the lane at the city camera. Keys or scroll move along it, and merged far tiers resolve to the thing, never to a stone.
4. The shared highlight function sits in every shader of the shared surface layers. It compares two global ids (hover and selected) with the part's id and applies the lift.
5. Any thing's meshes and transforms can be found from its id, so the selected thing alone can be drawn into the focus mask.
6. Each record has a label anchor, a screen-space bound for snapping and decluttering, and for people a head anchor, all following the record's lifespan.
7. People, signs, posters and doors also sit in a CPU list with bounds, so the bubble snap finds a figure 50 pixels tall without reading the GPU.
8. Every record and change carries the change query's weight, so labels and highlights obey the budget.
9. Every fact the interface may show carries provenance and precision, and text is data: a sign's words come from the words layer, so the world, the card and speech agree.
10. A knowledge store sits between the record and the screen. The interface reads what the role has seen, heard, been told and read, never the engine's truth; the engine's front door shows the truth and serves debugging tools only (`docs/engine-requests.md`). The store needs from the engine what a role could know (`knownBy`, the accounts arc) and the chain of who told whom.

Picking costs little per frame. When the cursor or the camera moves, render ids (32-bit, chunk or record index plus part index) for about 64 by 64 pixels round the cursor without antialiasing, and read them back asynchronously. The answer arrives two or three frames late, about 33 to 50 ms, which is fine for hover (our estimate). A full 1440p id target every frame would store 14.7 MB a frame, about 0.9 GB/s; the small region costs almost nothing (our estimate). The harness measures both.

## 7. The proposal

### The observer game

The observer roams the town as the camera, controls no one and influences little. They know what a stranger with a library card could know: what the camera has seen, what people have said to them or near them, and the town's public records. The game has five verbs.

1. **Look.** The cursor finds things, and a thing under it lifts slightly at once. After about 250 ms of dwell its name appears in one line, in the plainest public words: "steps", "a sign: the Anchor", "a woman in a green coat". Moving to a neighbour shows the next name within about 100 ms. The cursor's shape says what a click will do. Nothing about history appears on hover.
2. **Inspect.** A click opens a card beside the thing, never over it, and the rest of the frame softens a little. The card holds at most three claims, each with its mark, plus field-guide terms underlined. A record is shown as itself. The card stays while the cursor travels into it and closes when the player looks away.
3. **Ask why.** Where the player holds a linked cause, the card offers "why?". The answer names its contrast, gives one or two sourced causes and the count of others, and shows unknown links as "?".
4. **Compare.** Where the player holds an earlier image of the place (an archive photograph found, or one they took), holding a key shows it in place, aligned, and releasing returns to now. Changes are pointed at only from the change query and within the budget (`time-on-screen.md`).
5. **Keep.** Everything inspected goes into the journal by itself, with source, place and date. The journal has four views: by place (a map, with threads marked on it rather than in the painting), by person, by thread (what leads to what, with "?" for places heard of), and by time (filtered, never one long list). The player can write notes and name strangers. A photograph, if the game has one, is the observer's own record.

Hover answers "what is it?", inspection "what is known about it, and from whom?", the probe "why this rather than that?", comparison "what changed?", and the journal "what do I know?".

### Other games: the three dials

| Game | Knowledge | What the interface adds | What stays |
| --- | --- | --- | --- |
| Detective | witnesses and records only | a case board with incrimination and reliability on separate channels; checks that confirm facts only (who bought the ticket), never character; a trial that judges the case, not the truth | marks, counts, no verdicts |
| Manager (the band) | their own people deeply, the town thinly | commands the engine accepts or refuses, with its reasons; clocks for plans and debts | no trait labels, even for one's own band |
| Archivist, restorer | records and traces | phase views from conservation practice: a colour per period, a dashed outline for what is gone, no colour for the undated (`time-on-screen.md`, section 3); conjecture drawn looser | records can be wrong |
| Anthology | per character | the journal marks what was learned in another life | the town remembers; the player's acts are never marked in the world |
| Sandbox, or after the end | the record | answers from the record, marked as such | character still shown as acts with counts |

### Rules

1. Nothing readable unless something backs it: a record, an account, the pack's field guide or the player's own note. A check in the spirit of `trace_check.py` fails any label without a source id.
2. Every claim carries its source in its words and its mark.
3. Precision as recorded: no year where the record holds a decade.
4. No verdicts. No trait word in the game's own voice; character words only inside quotes, with holder and count.
5. The eye reads traces. The interface names them only as an accessibility option.
6. Marks on the map, not in the painting. The world points at a history only when asked, or across a jump within the budget.
7. The budget governs labels and highlights.
8. Causes only along the record's links, in lists as in cuts.
9. Unknown is shown as "?", never as a blank or a guess.
10. A contradiction keeps the claim, marks it disputed and shows the alternative.
11. The highlight is never light: no hue, no direction, no shadow.
12. Strangers are described by clothes, acts and places, the same way for everyone.
13. The field guide and the journal show only what the player has met.

### Tests

Model readers see stills and text; hover timing, the pad and the toggle need people, in the engine's human test.

1. The highlight is not light. Frames with hover and focus on and off, three lights, three headings. Readers describe the light; any reader who reports the highlight as sun, lamp, weather or mood fails it. The highlighted thing must be found at one-eighth size.
2. Scene and interface against the page (criterion 4). Three arms: the page, the scene alone, the scene with its cards. Score true claims, false claims and confidence, half the readers seeing the scene first.
3. Source memory. Readers read a set of cards with seen, told and written claims, some of them wrong, then say for each claim whether it is true and where it came from. Compare marks alone, words alone and both. Pass, provisionally: the source named right in four cases of five, and no wrong claim held with high confidence.
4. No verdict leaks. Readers describe a person from cards; a coder counts trait words against an arm without counts, as the engine's Quiz II did.
5. Legibility. Screenshots at 1440p and at a 13-inch laptop's size, cut into tiles at the player's pixel size; a script measures contrast against the lowest patch behind every text.
6. Picking. For random screen points, the id resolved must name the same record as a raycast against full meshes: every point at the near tier, logged misses at the city tier.
7. Cost and budget. The harness measures frame time with picking and labels off, on, and at 30 labels, and counts labels per view against the budget.

## What we should do

Ranked by what each buys for criteria 1, 3 and 4 and for the architecture. Costs are working days on Opus.

1. **Write the interface's needs into the architecture** (section 6). Ids for every part at every tier, stable across dates and rebuilds; the hierarchy; anchors, bounds and proxies; the shared highlight function; the knowledge store. Cost: half a day inside Monday's architecture. Buys: nothing to retrofit, and the cause view, the change query and the readers' keys share the same ids.
2. **A picking spike on the gully's port.** An id channel in merged chunks and instanced pieces, the scissored id render with asynchronous readback, test 6 and the harness's cost. Cost: one to one and a half days. Buys: the id contract proved on real data before the town is built on it.
3. **The highlight look test.** The even lift and the soft focus on the corner, three lights, three headings, a strict review, then test 1 with cold readers. Cost: a day. Buys: a hover that keeps the painting and claims nothing.
4. **A card prototype on fixtures.** Labels, cards with marks and a why-probe on the gully's and the corner's facts, rendered as stills; tests 2, 3 and 4. Cost: two days. Buys: the first measure of criterion 4 with the interface, and the provenance design chosen on evidence.
5. **The knowledge store and the label check** (rules 1 and 13), with the provenance kinds, on `authored` fixtures. Cost: a day. Buys: nothing readable without backing; the observer's dial as data.
6. **Engine requests.** Ask for what a role could know: who saw or heard each event, the player's character included, with place and month. Ask too for the chain of who told whom, and records with ids (request 9). Cost: an hour. Buys: corroboration, the observer's knowledge from the engine, and dates at their true precision.
7. **Type and plates.** The three type roles and paper-and-ink plates on frames, with test 5. Cost: a day. Buys: a legible interface that never passes for a record.
8. **The field guide** from the research's era tables (glass, signs, paving, lamps). Cost: a day, when the first game needs it. Buys: players who learn to read traces for themselves.
9. **Input and accessibility.** The pad's bubble pick, the trackpad, text scaling, the plain face, the outline mode, the reveal key, speech for cards. Cost: two days, once a scene is playable. Buys: the floor every player needs.
10. **Write the rules where they apply.** The rules go into `docs/living-world.md` and the needs into the building-blocks page; `interface.md` points here. Not done here, by instruction. Cost: half a day. Buys: every game starts from the same rules.

## For Øystein to decide

1. **The photograph (play).** Recommended: the observer carries a 1989 camera. Photos become their own records, the anchors for comparing years in place, and the strip that helps recognise a person across a jump. It keeps the comparison inside the world's own media, as recommended in `time-on-screen.md`.
2. **Whether the observer ever sees the record (play).** Recommended: not during play. Optionally after a chapter or at the end, clearly marked as the record. Seeing truth during play would make every account worthless.
3. **Confirmation (play).** Recommended: the game never confirms a reading of a person. A fact counts as confirmed only when two independent sources agree. Detective games may add rationed checks on facts, as Obra Dinn does.
4. **Naming strangers (play).** Recommended: yes. The player can name people they have not heard named, and the journal keeps both the player's name and the one they hear later.

## Gaps

- Fagerholt and Lorentzon's thesis would not parse; it is read through Andrews' review. Shneiderman's paper would not open. Ben Golus's article on wide outlines was blocked, so the jump-flood figures are secondary.
- Miller, Lombrozo, Cowan, Pirolli and Card, Gigerenzer and Hoffrage, Mauboussin, and the misinformation studies were read through abstracts and summaries.
- No primary source was found for Obra Dinn's three-at-a-time rule, Disco Elysium's Tab key and detective option, Outer Wilds' log visuals, Golden Idol's partial check, or the RimWorld and Sims panels.
- No game was found that marks the source of each claim the way evidential grammar does. Our marks are a design to be tested, not a borrowed one.
- No measured cost of any highlight on Apple silicon was found, and nothing public on how Cities: Skylines II, Manor Lords or Anno pick objects.
- Unconfirmed in Unity: `SV_PrimitiveID` on Metal, per-instance custom data under the GPU Resident Drawer, and trackpad pinch on macOS.
- Hover delays come from operating-system toolkits, not from games. People must set them.
- Model readers see stills, so hover, the pad, the toggle and the journal can only be tested with people.

## Sources

Games: [Thimbleweed Park, Gilbert, GamesBeat](https://gamesbeat.com/ron-gilbert-on-thimbleweed-park-what-made-adventure-games-great-and-vr-skepticism/) · [Disco Elysium UI, 80.lv](https://80.lv/articles/disco-elysium-working-on-ui-design) · [Thought Cabinet, GameBanshee](https://www.gamebanshee.com/39hc9) · [Disco Elysium, Can I Play That](https://caniplaythat.com/2021/03/31/disco-elysium-the-final-cut-can-i-play-that-accessibility-review/) · [Pentiment fonts, GameBanshee](https://www.gamebanshee.com/96xr8) · [Pentiment alibis, GameBanshee](https://www.gamebanshee.com/9xdaf) · [Sawyer, Shacknews](https://www.shacknews.com/article/146276/pentiment-josh-sawyer-no-correct-answer) · [Pentiment glossary](https://progameguides.com/pentiment/what-do-red-underlined-words-mean-in-pentiment/) · [Pope, Game Developer](https://www.gamedeveloper.com/design/for-lucas-pope-i-return-of-the-obra-dinn-i-was-a-bunch-of-appealing-design-problems) · [Obra Dinn, Wikipedia](https://en.wikipedia.org/wiki/Return_of_the_Obra_Dinn) · [Mobius, Planet Progress](https://www.mobiusdigitalgames.com/news/planet-progress) · [Ingold, TheSixthAxis](https://www.thesixthaxis.com/2018/04/27/interview-talking-with-inkles-about-deciphering-ancient-language-in-heavens-vault/) · [Her Story, PocketGamer.biz](https://www.pocketgamer.biz/feature/62104/making-of-her-story/) · [Paradise Killer, MCV](https://www.mcvuk.com/business-news/we-never-wanted-to-force-our-beliefs-and-our-stories-on-you-make-your-own-one-up-theres-so-much-more-power-in-the-imagination-behind-the-development-of-paradise-killer/) · [Shadows of Doubt devblog 4](https://colepowered.com/?p=33958) · [Golden Idol, Game Developer](https://www.gamedeveloper.com/road-to-igf-2023/-the-case-of-the-golden-idol-i-used-frequent-testing-to-improve-its-mystery-solving) · [Kentucky Route Zero, PC Gamer](https://www.pcgamer.com/uk/welcome-to-the-zero-the-making-of-kentucky-route-zeros-open-road) · [Kentucky Route Zero, Critical Distance](https://critical-distance.com/2019/09/26/kentucky-route-zero/) · [Firewatch UI, Game Developer](https://www.gamedeveloper.com/design/how-firewatch-s-ui-enhances-player-immersion) · [Victoria 3 nested tooltips, PCGamesN](https://www.pcgamesn.com/victoria-3/nested-tooltip-system) · [Victoria 3 dev diary 74](https://www.paradoxinteractive.com/games/victoria-3/news/dev-diary-74-ux-improvements) · [Caves of Qud, Grinblat and Bucklew 2017](https://www.freeholdgames.com/papers/Generation_of_mythic_biographies_in_Cavesofqud.pdf) · [TLOU2 accessibility, PlayStation Blog](https://blog.playstation.com/2020/06/09/the-last-of-us-part-ii-accessibility-features-detailed) · [Kasurinen on yellow paint, Game Developer](https://www.gamedeveloper.com/design/control-resonant-director-lays-out-case-for-avoiding-excessive-yellow-paint-) · [Yellow paint debate, Wikipedia](https://en.wikipedia.org/wiki/Yellow_paint_debate) · [D2R controller, Blizzard](https://news.blizzard.com/en-us/article/23722094) · [Baldur's Gate 3 on DualSense, PlayStation Blog](https://blog.playstation.com/2023/09/05/how-baldurs-gate-3-adapts-its-expansive-rpg-gameplay-for-your-dualsense-controller/)

Theory: [Pirolli and Card 1999, record](https://demo.kerko.whiskyechobravo.com/bibliography/FSB6DCE8) · [Shneiderman 1996](https://www.cs.umd.edu/~ben/papers/Shneiderman1996eyes.pdf) (did not open) · [Progressive disclosure, NN/g](https://www.nngroup.com/articles/progressive-disclosure/) · [Tooltip guidelines, NN/g](https://www.nngroup.com/articles/tooltip-guidelines/) · [Beyond the HUD](http://publications.lib.chalmers.se/records/fulltext/111921.pdf) · [Andrews, Game UI Discoveries](https://www.gamedeveloper.com/design/game-ui-discoveries-what-players-want) · [Cowan 2001](https://www.cambridge.org/core/journals/behavioral-and-brain-sciences/article/magical-number-4-in-shortterm-memory-a-reconsideration-of-mental-storage-capacity/44023F1147D4A1D44BDC0AD226838496) · [Deadly Sins Revisited, Bitgood](https://informalscience.org/research/deadly-sins-revisited-review-exhibit-label-literature/) · [Visitor time, Serrell](https://archive.informalscience.org/sites/default/files/VSA-a0a2e7-a_5730.pdf) · [Well-chosen words, AAM](https://aam-us.org/wp-content/uploads/2024/04/10Wellchosenwords_Bartlettexhfall2014-9.pdf) · [Aikhenvald, Evidentiality in grammar](https://researchonline.jcu.edu.au/9362/) · [Admiralty code](https://en.wikipedia.org/wiki/Admiralty_code) · [How likely is likely, Collins on Mauboussin](https://www.jasoncollins.blog/posts/how-likely-is-likely) · [Natural frequencies, Frontiers](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2015.00642/full) · [Johnson, Hashtroudi and Lindsay 1993](https://doi.org/10.1037/0033-2909.114.1.3) · [Dias, Pennycook and Rand 2020](https://misinforeview.hks.harvard.edu/article/emphasizing-publishers-does-not-reduce-misinformation/) · [Lewandowsky et al. 2012](https://dornsife.usc.edu/norbert-schwarz/wp-content/uploads/sites/231/2023/11/12_pspi_lewandowsky_et_al_misinformation.pdf) · [Nyhan and Reifler, causal corrections](https://sites.dartmouth.edu/nyhan/files/2021/03/nyhan-reifler-causal-corrections.pdf) · [Miller 2019](https://arxiv.org/abs/1706.07269) · [Lombrozo 2007](https://pubmed.ncbi.nlm.nih.gov/17097080/) · [Boukhelifa et al. 2012](https://tobias.isenberg.cc/p/Boukhelifa2012ESV)

Rendering, input and accessibility: [WWDC20 10602, Metal on Apple silicon Macs](https://developer.apple.com/wwdc20/10602) · [Framebuffer fetch, Unity](https://docs.unity3d.com/Manual/urp/render-graph-framebuffer-fetch.html) · [Render Objects, Unity](https://docs.unity3d.com/Manual/urp/renderer-features/renderer-feature-render-objects.html) · [GPU Resident Drawer compatibility, Unity](https://docs.unity3d.com/cn/current/Manual/urp/make-object-compatible-gpu-rendering.html) · [BatchRendererGroup picking, Unity](https://docs.unity3d.com/ScriptReference/Rendering.BatchRendererGroup.SetPickingMaterial.html) · [AsyncGPUReadback, Unity](https://docs.unity3d.com/ScriptReference/Rendering.AsyncGPUReadback.html) · [Apple tech talk 10858](https://developer.apple.com/videos/play/tech-talks/10858) · [Unreal HHitProxy](https://docs.unrealengine.com/4.26/API/Runtime/Engine/HHitProxy) · [Bubble cursor, Grossman and Balakrishnan 2005](https://dgp.toronto.edu/~ravin/papers/chi2005_bubblecursor.pdf) · [JFA outlines, Unity forum](https://discussions.unity.com/t/flood-fill-outline-render-feature-mac-vs-pc-gpus/1639981) · [Apple HIG, game controls](https://developer.apple.com/design/human-interface-guidelines/game-controls) · [Apple HIG, typography](https://developer.apple.com/design/human-interface-guidelines/typography) · [Steam Deck compatibility](https://partner.steamgames.com/doc/steamdeck/compat) · [XAG 101, text](https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/101) · [XAG 102, contrast](https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/102) · [Game Accessibility Guidelines](https://gameaccessibilityguidelines.com/full-list) · [Wery and Diliberto 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5629233/) · [Kuster et al., Dyslexie](https://link.springer.com/article/10.1007/s11881-016-0127-1) · [UI Toolkit text, Unity](https://docs.unity3d.com/6/Documentation/Manual/UIE-advanced-text-generator.html) · [msdfgen](https://github.com/Chlumsky/msdfgen) · [Mapbox collision detection](https://github.com/mapbox/mapbox-gl-native/wiki/Collision-Detection) · [Atkinson Hyperlegible](https://en.wikipedia.org/wiki/Atkinson_Hyperlegible)
