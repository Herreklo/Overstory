# Interface for a deep simulation

How to make a simulation of thousands of people readable and playable without turning it into a spreadsheet. Part of the Game Lab research. A few games could not be checked and are listed at the end.

## Principles for our world

1. The player sees what they know, not what is true. The engine already splits FELT (what a witness could know) from TRUTH. The distance between them is the game.
2. Every number has a reason one hover away. No figure appears that can't be explained, and the engine logs a reason for every decision.
3. Sources and reliability are shown as clearly as facts.
4. Curate, don't dump. A few threads up front, the whole archive behind them.
5. Time is visible. Every person and place has a dated past; changes are shown with their dates.
6. The world's own media come first: notebook, newspaper, phone book, map, radio. Abstract overlays only for detail.
7. One grammar, many skins. Type roles, colour meanings and motion rules stay the same across games; each game changes only the surface.
8. The plainest version is always available: readable, scalable, never colour alone.

## How others expose depth

- Crusader Kings III and Victoria 3: nested tooltips. Highlighted words open further tooltips; holding still keeps a tooltip open so you can go a level deeper; an encyclopedia sits behind them. The aim, in Paradox's words: "to allow you to learn even the most advanced concepts the game is based on as you play". Victoria 3's UX diary adds: put what matters higher in the hierarchy, explain why something is blocked, and lay out panels so moving toward a nested tooltip doesn't open another; it also cut notifications by about half. *Take:* our engine's reasons drive this directly ("why did she leave?" opens to the value, the relationship, the event).
- Tynan Sylvester, "The Simulation Dream": "anything in the Game Model that doesn't copy into the Player Model is worthless", and big simulations become "a gigantic hairball of complexity". Rate every piece of visible depth by whether it reaches the player's head.
- The Sims' moodlets: a mood is built from named parts, each with a cause and an end. Break feelings into readable causes.
- Disco Elysium: skills speak as voices in the dialogue; the Thought Cabinet hides a thought's effect until it has been "internalised". A trait can speak, and a belief can reveal itself over time.
- Citizen Sleeper: segmented clocks that fill as effort and pressure build, "exposing the variables to the player". Our plans, debts and threats as clocks.
- Dwarf Fortress on Steam: Tarn Adams said a UX person reviewed it too late. Bring UX in early.
- Curating the log. James Ryan: emergent narrative "works more like nonfiction than fiction", and raw traces "will almost always lack story structure". Winnow (2021) flags stories while they are still unfolding. Chronicles (2022) documents a world as a wiki with designed entry points and a "subjective mode" showing only what the character knows.

## Uncertainty and partial knowledge

- Football Manager shows attributes of little-known players as ranges ("between 11 and 16") that narrow as knowledge grows, hides some attributes behind a scout's pros and cons, and gives star ratings as a named staff member's opinion. (Source is a fan site.) This fits talent scouting in the music game and the football game exactly.
- Return of the Obra Dinn records events automatically; the player fills in names and causes and gets confirmation only three at a time, to stop guessing. Right for the murder mystery.
- Heaven's Vault never confirms translations. Jon Ingold: "If we'd confirmed the player's translations, then players would have brute-forced them." Right for reading people: the game never tells you you've understood someone.
- Shadows of Doubt (early design) linked evidence on a cork board with strings whose colour showed how incriminating a link was and whose width showed how reliable. Reliability shown separately from content.
- Research on uncertainty: animating individual possible outcomes beats error bars when people compare quantities (Hullman et al. 2015); leaving uncertainty out erodes trust. Show a witness's account as one of several retellings, not as a percentage, and mark "unknown" visibly.

## Time and history

- Dwarf Fortress Legends: cross-linked pages for people, places and events. Take the links; leave the unstructured lists.
- Crusader Kings II's Chronicle: a summarised history written as play goes on.
- Pentiment's mural: in the last act the player paints the town's history and chooses what to include. History as a retelling the player makes, which is strong for Recognition.
- Obra Dinn's chapters were added because deaths shown out of order confused testers. Group a timeline into named episodes.

## In-world interfaces

- Fagerholt and Lorentzon sort game interface on two questions: is it part of the fiction, and does it sit in the game's space?
- Her Story: the whole interface is a search over video clips, written so that "whatever the order you discover the pieces in, there's always a bunch of different ways to view them". Searching the engine's log could be a mystery mechanic.
- Outer Wilds' ship log files each finding under its place; a clue about somewhere unvisited makes a "?" entry joined by a line. A rumour map.
- For 1989: address books, the phone book, newspapers, letters and local radio are natural carriers (our suggestion).

## Maps

A 2025 study of Lynch's elements in open-world games (small: three players fully analysed) found players navigate mostly by landmarks, paths are rarely named, NPCs act as navigation anchors, and a rotating camera makes compass directions hard. *Take:* landmarks first, people as anchors, a fixed north, named streets. Sunless Sea shuffles most map tiles within rules and places some landmarks by hand.

## Type, colour and accessibility

- Pentiment has five typefaces (from scribe to printer to peasant) that signal a person's education and standing, writes text stroke by stroke, changes a character's typeface as the player gets to know them, and offers one plain face for accessibility. Testers were confused at first; afterwards "People just understood what it meant."
- Xbox Accessibility Guidelines give a floor: body text at least 26 px on console and 18 px on PC at 1080p, scaling to 200%, lines of 80 characters or fewer, line spacing at least 1.5, a plain alternative to any stylised font, left-aligned text.

## Not verified

Frostpunk, Kentucky Route Zero's interface, Civilization replays, Disco Elysium's map, the Dead Space talk's lessons, how Shadows of Doubt's strings finally shipped, and Football Manager's scouting from a primary source.

## Sources

[Victoria 3 nested tooltips](https://www.pcgamesn.com/victoria-3/nested-tooltip-system) · [Victoria 3 dev diary 74](https://www.paradoxinteractive.com/games/victoria-3/news/dev-diary-74-ux-improvements) · [Dwarf Fortress on Steam](https://www.gamedeveloper.com/programming/how-tarn-adams-upgraded-and-optimized-dwarf-fortress-for-its-official-steam-release) · [The Simulation Dream](https://gamedeveloper.com/design/the-simulation-dream) · [Moodlets](https://sims.fandom.com/wiki/Moodlet) · [Thought Cabinet](https://gamebanshee.com/39hc9) · [Citizen Sleeper](https://howtomakeanrpg.com/r/a/case-study-citizen-sleeper.html) · [Ryan via Emily Short](https://emshort.blog/2019/05/21/curating-simulated-storyworlds-james-ryan/) · [Winnow](https://ojs.aaai.org/index.php/AIIDE/article/view/18903) · [Chronicles](https://www.jonathanlessard.net/?p=313) · [FM attributes](https://www.passion4fm.com/football-manager-player-attributes/) · [Obra Dinn](https://en.wikipedia.org/wiki/Return_of_the_Obra_Dinn) · [Heaven's Vault](https://gamedeveloper.com/business/road-to-the-igf-inkle-s-i-heaven-s-vault-i-) · [Shadows of Doubt devblog 4](https://colepowered.com/?p=33958) · [Hypothetical outcome plots](https://idl.uw.edu/papers/hops) · [Uncertainty survey](https://arxiv.org/pdf/2301.07687) · [CK2 Chronicle](https://www.dualshockers.com/charlemagne-expansion-for-crusader-kings-ii-lands-october-14th-new-developer-diary-video-released/) · [Pentiment mural](https://bobsthoughtcloud.substack.com/p/pentiments-third-act-emphasizes-the) · [Beyond the HUD](http://publications.lib.chalmers.se/records/fulltext/111921.pdf) · [Her Story](https://gamedeveloper.com/audio/road-to-the-igf-sam-barlow-s-i-her-story-i-) · [Outer Wilds](https://scientificgamer.com/thoughts-outer-wilds) · [Lynch in open worlds](https://cs.wellesley.edu/~pmwh/mvmap/papers/open_world_elements/open_world_elements.html) · [Sunless Sea map](https://www.failbettergames.com/news/mapping-the-sunless-sea-geography-spoilers) · [Pentiment fonts](https://lettermatic.com/custom/pentiment) · [Sawyer on fonts](https://www.gamebanshee.com/96xr8) · [Xbox accessibility 101](https://devdocs.xbox.com/build/game-principles/accessibility/xag-deep-dives/xag-101-text-display.md)
