# Behaviour on screen

Draft, for Øystein. How the lives the Understory engine simulates show in what people do on screen, without the screen ever passing a verdict on anyone. Written on Opus while Fable is out, to a lead designer's and a behaviour animator's bar. It sits between two sibling studies: `characters.md` (people as models) and `animation-and-motion.md` (the craft of motion). This page decides what a person does, where, when and how strongly; those decide what the person looks like and how the motion is made.

Claims taken from summaries are marked (secondary); claims we could not confirm are marked (unverified). The web-search budget for this session ran out partway through. Sources after that point were fetched directly from known addresses (papers' abstracts by their PubMed numbers, GDC Vault pages, the Exult source), and what came from memory is marked (unverified). Gaps lists what to check.

## The idea in one paragraph

A person on screen is a witness's view of a life. The engine decides what the person did and why; Overstory decides where and when it is seen, and how it looks. Behaviour runs on three clocks. Years leave traces in things (the living fabric). Days make routines: who is where, when, and with whom. Minutes stage acts. Routine is the canvas, and a change in someone's routine is the strongest true signal the screen can give: the regular who stops coming, the car outside at ten on a weekday. Staged acts are rare, and each one carries its situation with it. How someone moves carries their state far more than their character, and never more character than a real observer could read. Nothing on screen labels anyone. A reading of a person exists only as someone's words, with a source and a count.

## 1. What the engine gives us

Read through the GitHub API at round 41 (21 October). Everything below is in the engine's code today.

| Engine fact | Where | What it can drive on screen |
| --- | --- | --- |
| Acts: 20 families, about 110 expressions, each with an intensity, the traits it reveals, its effect on the bond, and flags (`secret`, `quiet`, `solo`, `needsTarget`) | `families.ts` | The staged acts of section 6 |
| Events: month, who, words, causes with weights, visibility (`private`, `local`, `public`), evidence, and who saw and who heard (`knownBy`) | `world.ts` | What is staged, who could have seen it, and the situation to put in frame |
| Habits: a label ("is at the Anchor every Friday without fail", "swims in the harbour every morning, whatever the weather"), a kind (solo, social, family, practice, work, body), a place, adherence; broken with a cause, and taken up again | `time.ts`, `setting.ts` | Day plans, absences, the feet field |
| Emotions with a cause and an end: grief (longer for the sentimental), in love (6 months), newly married (18), a new baby (12), humiliated after being let go (10), passed over (8), proud of the step up (10), back to square one (4) | `addEmotion` across the engine | The state layer of manner; changes of routine |
| Stress with named sources: "years without a step up", bad terms with the boss, "out of work", grief | `stress.ts` | Tiredness, hours kept, habits dropped |
| A way of being: humour, voice (talk, blunt, dry, warm, formal), quirks from 128 patterns filled from the person's own life, small loves; sore spots, fears, pride and rules from history | `persona.ts` | Habits of hand and routine ("times the shopping for when the shop is empty", "has a back way home") |
| Couples: ways of loving and fighting, tension, rows in two turns, drift ("they were polite with each other, and that was all"), doubts | `love.ts` | Two people at one table across years |
| Manner: what a person shows is the trait plus a mask, read with noise at ordinary-acquaintance accuracy | `social.ts`, `generate.ts` | The cap on what motion may say (section 3) |
| The witness: beliefs as estimates, hunches ("You'd bet", "You're fairly sure", "You have a feeling"), hindsight split into causes seen and unseen | `witness.ts` | Readings as someone's opinion; what belongs in frame |

Three facts about the engine shape everything below.

The engine already models the observer. A manner read is the person's trait plus their presentation plus noise, set so the read correlates with the truth at the level other-ratings reach after ordinary acquaintance (Connelly & Ones 2010): extraversion .45, conscientiousness .35, openness .30, agreeableness .25, emotionality .22, honesty-humility .18. Low sincerity shows a warmer and fairer face than the truth; high anxiety shows less boldness. The witness's "Noticed:" line follows the read, not the truth, so a wrong impression is a wrong line. The screen should agree with this model rather than invent its own.

The engine's human test found the failure we must avoid. In Quiz II's single sitting, the page made a skilled reader worse: a vivid act was read as general character (`docs/STATUS.md`, weakness 9). The next sitting shows each impression with the number of acts behind it ("seen 4 times, once the opposite"), the remedy the halo and dilution research points to (`docs/study.md`).

The engine's people are, if anything, too consistent. A single act predicts the trait behind it at about r = .4, where real people run .1 to .3 (weakness 12). If the screen adds trait-coloured manner on top of trait-coloured acts, it doubles the problem.

Four things are missing for the screen. An act has a month but no place or day. Habits are sentences, not timetables. Quiet acts are never logged, so a person's ordinary rate of acts cannot be shown. Causes are not marked as visible in the moment or inner. Section 8 turns these into requests.

## 2. How games show simulated lives

### Three channels

Games that simulate lives reach the player through one of three channels, and most lean on one.

| Channel | Games | What it gives | What it costs us |
| --- | --- | --- | --- |
| The interface states the inner life | The Sims, RimWorld, Dwarf Fortress, Crusader Kings III | Legible at once | It is the game's verdict. CK3's "Deceitful" is true because the game says so |
| Acts on a schedule | Ultima VII, Shadows of Doubt, Hitman, Red Dead Redemption 2, Assassin's Creed | People who are somewhere for a reason; routines a player can learn | Lifeless without small events inside the routines |
| Staged moments and text | Façade, Pentiment, Disco Elysium, Return of the Obra Dinn, Kentucky Route Zero | Meaning carried by few animations | Hand-made; it needs a selector to scale |

We can use the second and third. The first is closed to us by the core rule, though its data structures are worth keeping.

### Lives shown through the interface

The Sims has needs, smart objects that advertise what they satisfy, and a mood built from named parts with a cause and an end (the moodlet). The Sims 4 added emotions with their own walks, facial expressions and interactions, which critics praised (secondary). The read reaches the player mainly through thought balloons, the plumbob and the mood panel: the game reads the Sim's mind aloud. We keep the structure (a state with a cause and an end, which the engine's emotions already have) and drop the display. The cause and the end decide how long a walk is slower; nothing names the state.

RimWorld turns mood into acts. Below 35% mood a colonist may binge on food, wander sadly, hide in their room or go on an insulting spree. Below 20% comes a tantrum or a daze; below 5%, berserk rage, catatonia, running wild or giving up and leaving. The mean time between breaks falls from about four days to half a day across the tiers, and a break is followed by a catharsis mood lift for three days (wiki, secondary). The acts are right for us: a break is something a person does that others can see. The game still marks each one with an icon over the portrait, and the player loses control of the colonist.

Tynan Sylvester's essay "The Simulation Dream" gives the principle behind both games: the designer's Game Model matters only as far as it reaches the Player Model in the player's head. In his words, "Anything in the Game Model that doesn't copy into the Player Model is worthless." Players project intention and feeling onto simple motion (apophenia), so a designer can show something as plain as moving balls and let players supply the rest. And a designer should choose the smallest model that still supports the stories wanted.

Dwarf Fortress keeps its richest read on a thoughts screen. Emotions add stress, and strong ones become long-term memories that are revisited and keep stress up. Short-term excess shows as tantrums, depression or stumbling about obliviously, and a stressed dwarf flashes a red arrow (wiki, secondary). The text carries the inner life and the dwarf only acts.

Crusader Kings III raises a character's stress when they act against their own traits, and turns a threshold into a mental break the player answers by choice, often gaining a coping trait. Only the player's stress is shown; AI characters' stress is hidden (wiki, secondary). Portraits change with lineage, age, lifestyle and illness (developer diary, secondary). Hiding the stress of everyone else is close to our rule: the player sees what others do. Its trait icons are the opposite.

### Lives shown through routines

Ultima VII (1992) gave every person in a town a day. Its schedules, as the Exult project recreates them, use 35 activity types: sleep, eat, eat at the inn, tend shop, farm, bake, sew, preach, kid games, loiter, wander, shy, street maintenance and more. Each change is keyed to a three-hour block, with a place and a mask of days (Exult source, `schedule.h`). The lesson is the scale: a few dozen activities, each tied to a place. Three-hour blocks are too coarse for a street stop; the vocabulary is about right.

Shadows of Doubt plans each citizen's day before it starts: four to ten journeys (home, café, work, lunch, after work, home). The whole city of hundreds is planned in 10 to 15 seconds, and only a handful are re-routed live, such as one who finds a body and runs late. Citizens see each other and into lit windows, and each sighting is logged as a memory that fades and can be lied about (ColePowered devblog). Plan the day ahead from facts; simulate live only for the few in view; treat every sighting as evidence someone holds.

Hitman (2016) gave each of the roughly 300 people in a level a routine of its own, and players learn targets by following them and overhearing conversations. When playtesters called the levels lifeless, the team added subplots and "opportunities" that bend a routine (secondary). Routines make a place learnable; life comes from small stories inside them. Ours come from the engine's events, not from designers.

Assassin's Creed Unity drew about 10,000 crowd figures with up to 40 full AI agents and 120 high-resolution models, swapping figures between low and high resolution as the camera moved (GDC 2015, Cournoyer). Our town is small enough that every figure can be a person of the simulation, as `docs/living-world.md` already says.

Red Dead Redemption 2 has witnesses who report crimes and an Honor meter that rises and falls with the player's acts and changes dialogue and the ending (secondary). Honor is the game judging its hero: the verdict we do not give. Oblivion's Radiant AI gave people broad goals (eat at a certain place at 2 pm) rather than scripts, and the stories of people killing for what their goals needed are told widely (unverified). Goals without reasons produce acts players read as madness. The engine gives ours reasons.

Watch Dogs: Legion lets the player recruit almost anyone; recruits keep their job and lifestyle (drinking at a pub) and hold opinions shaped by what the player did to people they like. Critics found the characters lacking personality and noted they do not meaningfully interact with one another (secondary). Its predecessor's profiler gave every passer-by a generated one-line private fact (unverified). A label on a stranger is the purest verdict, and strangers who never act on each other feel empty however many facts they carry.

Animal Crossing and Stardew Valley keep small towns alive with routines keyed to the hour, the weekday, the season, the weather and friendship (unverified detail). Animal Crossing's villagers come in a handful of fixed personality types, which in the earlier games followed the villager's sex (unverified). Routines tied to weather and season make a town feel kept; fixed types are the stereotype trap.

### Drama, social simulation and selection

Façade staged a marriage falling apart in one evening, with beats chosen by a drama manager. When its parser failed, Trip and Grace stared, and players read the stare as attitude; let's-play videos turned these misreadings into memes (secondary). A system that fails to respond reads as a person who chose not to. Our default behaviour must be neutral texture that claims nothing.

Versu models social practices (a dinner, a greeting) with roles, and every agent still chooses (`docs/research/scenes-and-sound.md`). Prom Week let players see which social rules made an exchange succeed or fail (unverified detail). Showing why is possible when the reasons exist, and our engine logs them for every decision.

James Ryan argues that emergent narrative works more like nonfiction than fiction, and that raw simulation output almost never has the structure of a story, so it must be curated (Emily Short's reading of his thesis). Story sifting is that curation: picking the events that make a story out of a chronicle. Felt (Kreminski, Dickinson and Wardrip-Fruin 2019) writes sifting patterns as queries over the event log. It adds reflection actions, in which characters visibly act on their history, so the player can see the sifting at work. It names the Tale-Spin effect, rich inner process that never surfaces, as the failure to avoid. In its Cozy Mystery Construction Kit, each character holds values, and sifting lets each one reinterpret the same events by those values. Sifting can find a story, and it can also find each witness's reading of it.

Caves of Qud generates events first and their explanations afterwards (Grinblat, GDC 2018). We cannot: a cause written after the fact is a falsely claimed history.

Pentiment has 157 rigged characters, with facial expressions hand-drawn per character and budgeted late, once the team knew each one's story moments (Kennedy, Game Developer). Its acts jump years; the town remembers whom the player blamed, and the accused's absence is felt (Sawyer, TheGamer). Meals with households are where much of the talk happens (unverified detail). Two lessons: decide expressions per moment, not per character; and revisit one town across years so change reads as change.

Disco Elysium voices the protagonist's skills as inner readers of other people, and they can be wrong (unverified detail), while the figures in the world act plainly. A reading can be on screen if it belongs to someone and can be wrong.

Return of the Obra Dinn shows each death as a frozen tableau after a few seconds of sound, for the 60 people aboard. Fates are confirmed only three at a time, to stop guessing (secondary). Players deduce who is who from poses, places and who stands near whom (unverified detail). One pose can hold an act. Kentucky Route Zero builds its scenes from theatre stagecraft and slow cinema, balancing mood against the mundane (Kemenczy, GDC 2014).

### What players do with it

Players read minds into anything that moves. In Heider and Simmel's 1944 film, viewers described a few triangles and a circle as chasing, fighting and comforting, and gave them intentions and personalities (secondary). In a study of a generated archaeology game, 187 players interpreted its ruins, and a glitch was read as an in-world sandstorm (Smith Nicholls & Cook 2023); `docs/research/world-that-remembers.md` already draws the rule from it. The question for us is never whether players will read character into our people. They will. It is whether what they read is true.

## 3. Reading people

### What a stranger can read

People judge others from very little, and partly correctly. Ambady and Rosenthal's meta-analysis of 38 results found judgements from under five minutes of behaviour predicted outcomes at about r = .39, and slices under 30 seconds did no worse than four to five minutes (secondary). Carney, Colvin and Hall (2007) had 334 judges rate 30 people from 5 to 300 seconds of video. Negative affect, extraversion, conscientiousness and intelligence were judged moderately well after five seconds; positive affect, neuroticism, openness and agreeableness needed longer. Extraversion was judged best of all and agreeableness worst, and 60 seconds gave the best accuracy for the time.

How well someone is known matters more. Connelly and Ones (2010) pooled 263 samples and 44,178 people. Agreement between a person's own ratings and an observer's:

| Trait | Stranger | Work colleague | Friend | Family |
| --- | --- | --- | --- | --- |
| Extraversion | .22 | .24 | .40 | .48 |
| Conscientiousness | .13 | .18 | .38 | .42 |
| Openness | .12 | .20 | .37 | .43 |
| Agreeableness | .09 | .23 | .29 | .37 |
| Emotional stability | .08 | .14 | .33 | .43 |

Mean observed correlations, from their Table 5. Seeing someone more often helps a little; big gains need intimacy, and intimacy helps hidden traits such as emotional stability most and evaluative traits such as agreeableness least.

Funder's realistic accuracy model says why: an accurate read needs behaviour relevant to the trait, available to the judge, detected and correctly used (secondary). Traces follow other rules. Gosling and colleagues (2002) had observers judge 69 offices and 78 bedrooms. Rooms showed openness (distinctive decoration) and conscientiousness (neatness) well, the reverse of photo and video studies, where extraversion and agreeableness read best. Where valid cues were scarce, observers fell back on guesses from the occupant's gender and race (APA Monitor, secondary).

For us: a figure seen in passing can truthfully say a little about how outgoing someone is, and almost nothing about how kind, honest or steady they are. Those show through acts and their consequences over time, through what others say, and, for openness and conscientiousness, through things: the yard, the room, the boat kept up. That is the living fabric's work, not the walk's.

### How readers go wrong

Correspondence bias is the tendency to infer someone's lasting character from behaviour the situation fully explains (Gilbert & Malone 1995). They name four causes: lack of awareness of the situation, unrealistic expectations of behaviour, inflated categorisation of the act, and incomplete correction. The first is the one a screen controls.

Trait inference is automatic. People infer a trait from one described act, bind it to the actor's face within two seconds, do it while busy with something else, and still show it a week later (Todorov & Uleman 2002 to 2004, secondary). Every act we stage becomes a trait on that face whether we mean it or not. Situational inferences arise as well when the situation is there to read: "She got an A" makes people think both "smart" and "easy" (Ham & Vonk 2003, secondary). When attention is pointed at one cause, people infer only that one.

Bad acts weigh more than good ones in judgements of morality; in judgements of ability it runs the other way (Skowronski & Carlston 1989, secondary). Ordinary information softens extreme judgements: adding non-diagnostic detail about a person makes predictions from a diagnostic act less extreme (the dilution effect: Nisbett, Zukier & Lemley 1981, secondary). Context makes a neutral face read as an emotion. A careful replication of Kuleshov's film experiment, with 36 viewers, found the effect real and strongest for sadness (Barratt et al. 2016, secondary).

People cannot see lies. Across 206 studies and 24,483 judges, lie detection averaged 54%: 47% of lies and 61% of truths judged correctly. Lies were caught better by ear than by eye, and judges tended to see their partners as honest (Bond & DePaulo 2006).

For us: a vivid act shown alone will be read as the person's character, quickly and lastingly, and a cruel one most of all. Showing the situation, and showing the person's ordinary life around the act, are the two remedies the research supports. The engine's Quiz II is the same finding in our own world.

### Bodies, distance and gaze

Emotion can be read from movement alone. Ten actors portrayed five emotions with their faces covered; viewers recognised them even from point-light displays. Exaggeration helped recognition for every emotion but sadness, and intensity was judged from movement more than from still form (Atkinson et al. 2004). From headless walks, observers named sadness 94% of the time, anger 90%, happiness 74% and pride 56%. Sad walks had less arm swing, angry ones were heavy-footed, happy ones faster, and proud and angry ones took longer strides (Montepare et al. 1987, via a 2020 review). These are posed emotions. Our inference, not a finding: a real person's grief on a wet street is quieter than an actor's portrayal of it.

Character is read from movement with confidence and agreement, not accuracy. Viewers agree on what a walk says, but the impressions do not match the walkers' real personalities (Thoresen et al. 2012, in `people.md`). Bigger, higher gestures read as extraverted (Smith & Neff 2017). The famous claim that "power poses" change hormones and risk-taking failed a large replication (Ranehill et al. 2015). A body cue that viewers agree on but that is not valid is a verdict if we bind it to a trait.

Distance carries relationship. Hall's zones run from intimate (to about 0.45 m) through personal (0.45 to 1.2 m) and social (1.2 to 3.7 m) to public (beyond 3.7 m). Across 8,943 people in 42 countries, the preferred distance was about 135 cm to a stranger, 92 cm to an acquaintance and 32 cm to a close person (Sorokowska et al. 2017). People in colder countries kept farther from strangers. Women kept farther from strangers and acquaintances, and older people from those they know. Norway's own value is in a figure we did not extract. People in conversation hold a shared space between them, Kendon's F-formation: face to face, in an L, side by side or in a circle (unverified detail). Strangers in public give each other a glance and then look away, Goffman's civil inattention. Most commuters in Milgram's study recognised at least one "familiar stranger" they had never spoken to, about four each (secondary).

By Gehl's account, people are seen as people at about 100 m, and their sex, age and what they are doing at 70 to 100 m. Their moods read only within about 25 m (unverified, from Life Between Buildings). The people deep dive puts a figure at 46 to 122 pixels from the city camera. There, activity, company, posture and speed carry everything; gesture and face carry nothing.

### Fairness

Viewers' biases run through bodies and faces. Given the same situational information, people labelled women's emotional faces as "emotional" (a trait) and men's as "having a bad day" (a situation) (Barrett & Bliss-Moreau 2009). White participants higher in implicit prejudice saw anger linger longer, and arrive sooner, in Black faces than in White ones (Hugenberg & Bodenhausen 2003). Gosling's observers fell back on gender and race when cues were scarce. Faces are read for character with confidence and little accuracy (Todorov et al. 2008, in `people-deep-dive.md`).

We cannot remove these biases from viewers. We can refuse to feed them. The same act gets the same body language for everyone, and the same expression the same intensity. Resting faces are neutral for every face shape and skin. A swap test measures whether a reading moves when only the body changes.

### Six rules from the research

1. Cap what motion says about character at what real observers can read: some extraversion, little else.
2. Put the situation in frame whenever an act is staged.
3. Show the person's ordinary life around the vivid act, at its true rate.
4. Let every reading belong to someone, with a source and a count.
5. Let familiarity come before judgement: people are seen on ordinary days before they are seen in a moment that matters.
6. Same act, same body, for everyone.

## 4. Routines and the life of a street

Jan Gehl splits outdoor life into necessary activities (going to work, shopping), optional ones (a walk, sitting in the sun) and social ones that follow from people being near each other. Necessary activity happens in almost any weather and place; optional activity rises with the quality of the place, the weather and the season, and social activity follows (unverified, from Life Between Buildings). People go where other people are. William H. Whyte, filming New York's plazas over 16 years, came to the same point: what draws people most is other people (Project for Public Spaces). People stop to talk in the middle of the flow and at corners, and sit where there is something to sit on (unverified detail).

Jane Jacobs described her Hudson Street as a daily ballet of known people at known hours: shopkeepers opening, children leaving for school, workers out for lunch, the evening at the bars. Public characters on it knew everyone (unverified detail). Torsten Hägerstrand's time geography gives the structure for scheduling it. Each life is a path through space and time, held by three kinds of constraint. Capability is what a body and its tools allow. Coupling is being at a place at a time with other people: work, school, the Friday at the Anchor. Authority is who controls a place and when: opening hours, school rules.

The town's own rhythm is partly in `docs/research/what-moves.md`: grocers closed at 17:00 on weekdays and 13:00 on Saturdays in 1985, the town emptied on Saturday afternoon, and the shared holiday took the last three weeks of July. Norway's early main meal after the working day and the evening news hour are general knowledge we have not checked against Statistics Norway's time-use surveys (unverified).

What this means for us:

- Sparse is right. A harbour town on a wet Tuesday afternoon has few people out, and every one is out for a reason. `what-moves.md`'s rule holds for people: if nothing has happened, nobody moves. No filler.
- Routine is the canvas. Players come to know the town's people as familiar strangers: the woman who swims at seven, the man at the Anchor every Friday. Hitman's players learn targets the same way.
- A change in routine is the signal. Absence, lateness, a new route, a new companion, a lit window at three in the morning. These are true, they come from the engine's habit breaks with their causes, and they leave the reading to the player.
- Stopping and staying belong to places: edges, steps, benches, a sunny wall, the shop door. Acts happen where people stay. The town plan's places must carry them.
- Weather and season move optional life, not necessary life. Drizzle empties the benches, not the walk to work.
- The year has a routine too, from the setting pack's calendar: school terms, the shared holiday in July, 17 May, Christmas lights house by house, the dark winter afternoons. Day plans read it, so a viewer can tell the season from who is out.

## 5. Small acts and staging

Acting for animation starts from objectives. Ed Hooks's teaching for animators holds that thinking leads to conclusions and emotion to action, that a character plays an action until it reaches its objective or meets an obstacle, and that acting is reacting (secondary). Keith Johnstone's improvisers play status rather than own it: stillness, a steady gaze and taking space read high; small fidgets, touching the face and a gaze that breaks and returns read low (Impro, 1979; secondary). Both point the same way. A small act reads through what the body is trying to do, how it uses space and gaze, and how the other person answers. A face is not required.

Games that carry meaning with few animations choose one pose or one beat. Obra Dinn holds a whole act in a frozen pose. Kentucky Route Zero stages scenes like a theatre with the lights dropping between them (`scenes-and-sound.md`). Film shows a relationship changing by repeating one scene across years; the breakfast-table sequence in Citizen Kane, where husband and wife sit farther apart each time, is the textbook case (unverified detail). Pentiment returns to the same town after years. A fixed vantage revisited is the cheapest and truest way to show a person changing: the change reads as change, not as character.

The Virtual Cinematographer (He, Cohen & Salesin 1996) encodes film idioms as small state machines that choose shots and cuts, and EMOTE (Chi et al. 2000) applies Laban's effort qualities to existing motion (both in our earlier research). Between them, a small set of act shapes, each with an effort and a camera idiom, can stage most of the engine's acts.

Kuleshov's effect is the staging risk. A cut from a closed till to a face makes the face guilty. A cut from a coffin to a face makes it grieve. A cut may only join what the record joins.

## 6. From engine facts to behaviour

### Three clocks

| Clock | Comes from | Shows as | Kind of thing on screen |
| --- | --- | --- | --- |
| Years | keepers, care, goods, household, age | traces in things; clothes worn and mended; the body ageing | facts and their interpretations |
| Days | habits, work, household, school, state | who is where, when, with whom; absences; lit windows; cars outside | facts (the habit); derived (the hour) |
| Minutes | events, emotions, bonds, the scene | staged acts; manner; greetings | facts, interpretations, texture |

The five kinds of thing from `CLAUDE.md` sort it. An act from the record is a canonical fact. A slower walk during the months of an engine emotion is a visual interpretation of a fact. A person's own gait and idle set is non-semantic texture. A neighbour's account of why someone stopped coming is perceived information. Tonight's seating at the Anchor is local scene state.

### States over time

How the engine's states show, by clock. "Never" is what would turn the read into a verdict.

| Engine state | Days | Minutes | Years | Never |
| --- | --- | --- | --- | --- |
| Grief (`grief`, its months scaled by sentimentality; family habits break half as often, all others 3.5 times as often) | Missing from the Friday at the Anchor, with the engine's "is no longer at the Anchor every Friday" and its cause; Sunday dinner kept; home more | A slightly slower walk with less arm swing for the emotion's months, at low amplitude; visitors only where the engine logs `visit` or `show` | Care drifts where the dead person kept the house; the boat sold where the engine says so | A grey grade on the person, rain on cue, a label, tears at a distance |
| Money trouble (low savings, "out of work", a want lost, extra work as the way to a want) | The café habit dropped; extra shifts; the car sold | Tiredness from stress, nothing more | Paint and garden go over years (care) | Shabby clothes overnight; a furtive manner; any tell for `skim` |
| New love (`love`, 6 months; habits other than family ones break 2.5 times as often) | Time at the partner's; walks together; a new café | Closer distance, gaze, walking in step | A second name by the door; moving in | Hearts, glow, a music cue |
| Grudge or rivalry (rivalry heat; `avoid`, `coolto`, `cold`, `needle`, `holdagainst`) | The back way round; the shared habit dropped | No greeting between familiars; opposite edges of a group; a back turned | A fence or hedge where the engine records the act (request 20) | A villain's walk; a colour |
| Strain at work (named sources) | First in, last out; the office window lit late | A flatter, faster tempo, few idles, at low amplitude | | A stress bar |
| Drink (`drinks`; `numb`) | More nights at the bar, later home; habits break twice as often | A sway only after drinks tonight (scene state) | Bottles in the bin | A drunk's walk in daylight as a trait |
| A couple drifting ("polite with each other, and that was all") | Separate routines; arriving apart | Less talk at table, parallel tasks; the same table revisited across years | | A cold grade on the house |
| Out of work (`jobless`; work habits end at once; `gaveup`) | Home on weekdays; the car outside at ten | Walks at odd hours | The yard | Idleness without its cause: the closed works stays in the story |
| A want pursued (a boat; extra work) | Evenings at the boatyard | | The boat at the mooring | |
| Let go ("humiliated", 10 months) | Keeps away from the old workplace where the engine logs `keepaway` | | | |
| A step up ("proud", 10 months) | New hours; a new place at work | Where the role puts them: the head of the table at work | A better coat, from money | Swagger |

Grief is the hardest case and the clearest. Sadness gains least from exaggeration (Atkinson), the Kuleshov effect is strongest for it, and the engine already makes grief break habits. So grief shows mainly as absence: the chair at the Anchor that stays empty on Fridays. A player who knows the town notices, and may find the cause on the churchyard's new stone or in what a neighbour says.

### Acts as staged shapes

The engine's 110 or so expressions collapse into about sixteen shapes, each staged with an effort, a distance, a gaze and a camera idiom. The engine's words for the act (in quotes) guide the staging.

| Shape | Engine expressions | Staged with | Reaction and trace |
| --- | --- | --- | --- |
| Speak at | `shout`, `snap`, `dressdown`, `needle`, `criticise` ("you always"), `rake`, `straighttalk` | a step in, raised voice, strong and sudden effort; others' civil inattention breaks | the other still or stepping back; the room quiet; the target's answer where the engine queues one (a hostile act becomes a situation for its target) |
| Mock | `sarcasm` ("and nobody laughed"), `contempt` ("rolled eyes and talked over") | to a group; talking over is overlapping speech; the eye roll needs the face tier | nobody laughs: the group's silence is the read |
| Speak with | `confide`, `askwhat`, `hearout`, `soften`, `admit`, `ask`, `heed`, `call` | close, side by side or in an L, low voice, long hold | the talk ends with both still there |
| Take aside | `quietword`, `confrontsecret`, `makepeace` | lead to the edge of the group, backs to the room | the return to the group, apart |
| Hand over | `give`, `grudging`, `chipin`, `quietgive` (the folded note), `token`, `nowallet`, `putin` | an object passes, or does not; `quietgive` is unseen by the room | the object stays with the receiver (a thing with an owner) |
| Refuse | `refuse`, `excuse`, `decline`, `notthemoney`, `notthetime`, `shyaway` | a head or hand turned, distance kept | the asker leaves first |
| Withhold | `cold`, `coolto`, `brushoff`, `stonewall` ("went silent with the other still talking"), `lookaway`, `sulk` | a pattern across scenes more than a beat: no greeting, a shoulder turned, stillness | the next meeting, the same again |
| Avoid | `avoid`, `keepaway`, `skip`, `stopgoing`, `shutout` | a changed route or a missed habit | absence |
| Come | `visit` ("every week"), `show` ("dropped everything"), `keep`, `welcome`, `congratulate`, `apologise`, `cheer` | arrival at a door or a table, often at a routine hour | the door opened |
| Fail to come | `absent`, `slip`, `late` | the other person waiting; an empty place | the waiting person leaves |
| Leave | `walkout`, `quitgroup`, `endit`, `startover` | an exit with a door | the room after |
| Stay | `stayfor`, `stayon`, `swallow` | stillness held after a blow | |
| Work | `work` ("buried in work"), `outwork`, `allnighter`, `deliver`, `redo`, `rough` | hours kept, a lit window, a bench | the work itself, done or rough |
| Perform | `backsong`, `resentsong`, `claimsong` | how a song is played on stage | the room's answer |
| Act in danger | `rescue`, `froze`, `go`, `hangback` | rare set pieces | others' accounts afterwards |
| Not staged | `skim`, `liecover`, `blame`, `whisper`, `allfine` | secret: on screen only if the player's role witnessed it | consequences, accounts, records |

Four acts are quiet in the engine (`straight`, `keepquiet`, `carryon`, `letslide`): never logged, effects applied. They are the ordinary life the dilution research asks for, and the screen cannot see them yet (request B4).

### Never a verdict

- No icon, balloon, aura, name colour, mood bar or music sting attached to anyone's character or inner state.
- No trait label on a person. A reading appears only as someone's account, with a source and a count.
- No act that claims history without an event: no slammed door, tear or stare the engine did not record.
- No body-language tell for a secret act. People catch lies at about chance by eye, and the engine keeps `skim` and `liecover` secret.
- No motion or expression style that varies by sex, ethnicity, body type, disability or orientation as a carrier of character.
- No cut, framing or sound bridge joining two things the record does not join.
- No replay of a vivid bad act beyond its one occurrence.
- No figure on screen who is not a person of the simulation doing what their life says.

## 7. The behaviour layer

The proposal, concretely. It follows `docs/living-fabric.md` in shape: records the engine decides, rules Overstory writes down, seeds for which exactly, provenance on everything.

### The records

| Record | Per | Holds | Provenance |
| --- | --- | --- | --- |
| `person_behaviour` | person, year | a motion seed (gait, tempo, idle set: identity and texture); manner channels (rules 3 and 4 below); the state layer (emotions, stress, illness, drink, age, load, cold); greetings toward those they know, from bonds | derived from the engine's person and bonds |
| `day_plan` | person, day | stays: place, from, to, activity, with whom; each deviation from the usual week names its cause (a habit break, an emotion, an event) or is texture | habits and work are facts; hours derived until request B2 |
| `moment` | staged act | event id; shape; place and time; participants and the witnesses who could see it; the visible situation to frame; effort, distance, gaze, sound; the reaction (the engine's next event, or a neutral one that claims nothing); the trace left; duration | the act is a fact; place and hour derived until request B1 |
| `trace` | thing | social traces: an empty mooring, a chair outside, a gift kept | the fabric's record (`living-fabric.md`) |
| `account` | holder, subject | a reading with its source, count and confidence | the engine's beliefs and hunches; records (request 9) |

### The rules

1. Provenance. Every staged act names an event; every routine change names a habit break, a state or an event; texture claims nothing. A checker in the spirit of `blender/tools/trace_check.py` (`act_check`) fails a scene where a staged act has no event behind it.
2. Knowledge. The camera is a witness with a place. It shows what someone there could see. Secret acts never appear unless the player's role saw them; private acts only inside the home a scene is in; local acts on the street. The engine's `vis` and `knownBy` decide, under each game's knowledge dial (`living-world.md`).
3. The lens cap. Each manner channel mixes a share of the trait the person shows (truth plus the engine's presentation mask) with the person's own seed, the way `persona.ts` builds humour and voice. Starting caps, to be measured: talk, gesture size and tempo from extraversion at about .4; fidgeting and checking from anxiety at about .2; nothing in the body from agreeableness, honesty or fairness. Conscientiousness and openness show through things and timekeeping, not gait. A lens audit over 1,000 generated people checks the correlations the rule produces. A player who learns these cues becomes a good judge, never an oracle, and agrees with the engine's own witness about what manner can tell.
4. State before trait. States move manner more than traits do, each has a cause and an end in the engine, and their amplitude is low, because real feeling is quieter than the posed feeling research uses. This is rule 6 of `people-deep-dive.md`, still waiting for Øystein's view.
5. The situation in frame. When an act is staged, its visible causes appear before it or in the same shot: the foreman in the doorway, the rain, the notice on the cannery gate. Request B3 marks which causes are visible.
6. Ordinary life around the vivid act. A person's first staged moment comes after the player has seen them on ordinary days, and each vivid act sits among that person's ordinary acts at their true rate. Wherever a reading is shown, it carries its count.
7. Cuts only along causes. A cut, framing or sound bridge joins two things only where the record links them (a cause reference, a shared event, a habit shared).
8. Bad acts between people need an event. Greetings and warmth may be derived from bonds (familiarity and liking are facts), as interpretation. A cold shoulder, an avoidance or a stare reads as history, so it needs the engine's act. Bad acts weigh more in readers' judgements of character, so they get the stricter rule.
9. Same act, same body. Shapes, efforts, expressions and their intensities never vary by sex, ethnicity, body type, age beyond the body's own capability, or orientation. Every couple is staged by the same rules. Differences come only from the engine's acts and states. The swap test checks it.
10. No labels, anywhere in the world view or the scenes.

### What the camera picks

The history budget of `living-fabric.md` has a twin for behaviour:

| View | What behaviour tells | What stays calm |
| --- | --- | --- |
| City camera | who is out, where, with whom (clusters), the flows of the day, absences over days, lit windows | gait style, gesture, faces |
| Street stop | gait identity, pace and load, groups and their formations, greetings and avoidance; at most two non-routine acts in view | faces, small gestures |
| Scene | the moment in focus: its situation, the act, the reaction, the trace | everyone else, on ordinary business |

At the city camera, at most one non-routine act per street (someone standing outside a shop that has closed). Story sifting (request 7) chooses the moments, with two rules of its own. It looks for chains, an act with its cause and consequence, rather than single vivid acts, since chains are what the engine's readers reward and single acts are what made Quiz II's reader worse. And it keeps a ledger per person: nobody's first moment on screen is their worst.

### The two clocks

The engine moves by the month. Overstory places each act on a day and hour that fits the day plans of everyone in it. Where a habit brought them together, the act takes the habit's slot: a row at the Anchor happens on a Friday evening. No act is staged at a place where a participant's plan says they were not. Day plans are seeded from the person's id and the date. The same day gives the same street, and a jump to any hour shows the same people where they were. The scene's own choices (who sits where tonight) are scene state, committed to the engine only when they matter, as `living-world.md` already says.

### How it meets the other systems

| System | Gives the behaviour layer | Takes from it |
| --- | --- | --- |
| Characters (`characters.md`) | identity anchors, body, age, clothes as evidence | nothing that changes identity: behaviour never re-rolls a face or a build |
| Animation (`animation-and-motion.md`) | the clip library, procedural layers (gaze, foot planting, posture offsets), stepped timing | per figure and moment: activity, shape, effort, posture offsets, gaze targets, walk speed, idle set, seed |
| Living fabric (`living-fabric.md`) | traces as the years' evidence; care | the feet field: the sum of the year's day plans over the paths, so the worn step and the people walking on it agree; acts on things (request 20) |
| Scenes and sound (`scenes-and-sound.md`) | practices and staging idioms; crowd signal; sound layers | who fills each role and what they do; voice level from the act's effort |
| Interface (`interface.md`) | accounts, records, the journal | nothing on the bodies; readings live in the world's own media |

Cost: the city camera needs only day plans and positions; the street tier adds gait and the manner channels; the near tier adds shapes, gaze and the face. Day plans for the starter town are computed ahead for a week and cached, as Shadows of Doubt plans a day before it starts.

### Checks

- `act_check`: every staged act has an event; every routine change has a cause.
- The lens audit: manner channels against traits over 1,000 generated people, against the caps.
- The swap test: the same moment rendered with bodies swapped across sex, skin tone, age and build; readers' trait ratings must not move (section 9).
- The cut check: every cut in a sequence has a link in the record.
- The behaviour budget: non-routine acts per view, counted.
- Determinism: day plans hashed per person and day, compared on a second run in shuffled order, as the life hasher does for things.

## 8. What the engine must provide

In the voice of `docs/engine-requests.md`. Labelled B1 to B5 here; they get item numbers when added there. Until they land, fixtures carry these fields, labelled `authored`, and the screen labels what it places `derived`.

- **B1. Where and when an act happened.** Each event between people names the setting it happened in: a place, or the habit, work or situation that brought them together. Where the engine knows it, the event also names the week or the time of day. The screen stages an act where it happened; today an event has only a month, and the place must be guessed. The player would see the row at the Anchor on the Friday it happened, and Hal missing the Friday after.
- **B2. Habits as timetables.** Each habit with its days and hours as data, beside its words, with its place and who shares it; breaks and returns already exist. It extends the habits in the front door's part two (#22). Day plans and the feet field are built from it. The player would see the swimmer at seven every morning, and notice the morning she is not there.
- **B3. Which causes a bystander could see.** For each decision, each cause marked as in the room (a circumstance others present could see: the foreman watching, the rain, the empty till) or inner (a trait, a memory, a want). The witness already splits causes into seen and unseen (`hindsight` in `witness.ts`); exported per viewpoint, it lets the screen put the visible situation in frame, the remedy the research names for reading one act as a whole character. The player would see the act with its circumstance, and could be right that it was the circumstance.
- **B4. Ordinary acts in proportion.** A count per person and month of the acts they made by family, the quiet ones included (`straight`, `keepquiet`, `carryon`, `letslide`), so the screen can show someone's ordinary life at its true rate around the one vivid act. It is the dilution the human test's next sitting builds into the page with evidence counts. The player would see the man who snapped once let a dozen other slights go.
- **B5. Rites with who came.** Funerals, weddings, christenings, confirmations and the town's own days as events with a place and the list of who attended. Who comes is the clearest public evidence of ties, and the rite is where a private state becomes public. The player would see who stood at the graveside, and who did not.

Two items already on the lists serve behaviour directly: small acts on things (20) and records (9). One item on the engine's own proposed work matters more to the screen than any of these: a situational reason to act out of character, weighed in the decision and said as the reason (STATUS, proposed work 2). An act that runs against someone's usual way, in a situation the player can see, is the best teacher against the verdict.

## 9. The cold reader's test

Criteria 3 and 4 of `CLAUDE.md`: a scene shows a consequence the page does not make obvious; viewers prefer the scene to the page for understanding what happened, and are not misled. The engine's human-test readers can join, but criterion 4 needs half of them to see the scene first (`engine-requests.md`).

**Material.** Twelve chains from a fixture (later, from the engine): an event and its consequences over months, each with a fixed vantage revisited (the Anchor on Fridays, the gully steps at eight, a kitchen table at six). Some chains carry a second-order consequence the page states only as two separate lines: when Ruth stopped coming on Fridays, Hal and Per stopped sitting together. A quarter of the chains turn on a vivid act whose top cause in the engine was the situation, not the trait.

**Two arms.** Each reader meets six chains as scenes and six as pages, the order dealt so half begin with scenes, and no chain seen both ways by one reader. The page arm uses the engine's page with evidence counts.

**What is measured.**

| Measure | How | Bar |
| --- | --- | --- |
| Consequence found (criterion 3) | "What changed, for whom, since when?", scored against the record | Scenes find more second-order consequences than pages; overall no worse |
| Preference (criterion 4) | Which helped you understand what happened? | Lower bound of the share preferring scenes above 50% |
| Facts right | Who did what, where, when | Scenes within 5 points of pages, or better |
| Misled by the screen | Answers marked "sure" that claim an act, place or cause the record does not hold | No more often than with pages; the aim is none |
| Over-reading | On the vivid-act chains, the share naming the person's character as the cause when the record names the situation | Lower with scenes than with pages |
| Calibration | "Sure" right more often than "guessing" | Holds in both arms |
| Swap | The same moment with bodies swapped across sex, skin tone, age and build; trait ratings compared | Shift under 0.3 on a five-point scale, shown by an equivalence test |
| Prediction | The engine's study protocol (`study.md`): pick the next act, base rate shown, with scenes in place of the page | Scenes no worse than the page |

**Two kinds of misled.** Being misled by the screen is a failure: an act staged without an event, a cut that implies a cause, a cue stronger than real observers could read. Being misled by a person is the world working: a warm manner over low sincerity, which the engine models and its witness also misreads. The questions about acts must come out right; the questions about character may come out wrong only in the ways the engine's own witness is wrong, and no more confidently than the evidence allows.

**Readers.** Ten to forty people who have not seen either project, with a spread of backgrounds for the swap test (the people deep dive's rule 7). Beside them, an in-house panel of model readers reads each round, as the engine reads its pages.

**What would change our minds.** If scenes lose to pages on facts, the staging is unclear and the shapes or the budget are wrong. If scenes over-read more than pages, the situation is not reaching the frame, and B3 and rule 5 need a second look. If the swap test fails, the act library carries a bias, and it is fixed in the library before anything else is built on it.

## What we should do

Ranked.

1. Write the behaviour contract into the draft in `docs/engine-contract.md` and into the fixtures: `day_plan` and `moment` with provenance, and B1 to B5 as `authored` fields, so LT2 and the gully steps' night scene start from data, not hand placement.
2. Build day plans for the corner's people from a fixture: a dozen people over two weeks with habits, work and households, rendered from the street stop and the city camera at fixed hours. Judged: a viewer who watches three days can say who lives where and who is missing on the fourth, and why they might be. The same plans give the corner's feet field (`living-fabric.md`, step 4).
3. Run the lens audit and the swap-test harness before any act animation is made. Both are cheap and stop a bias from being built in.
4. Stage the first moments in LT2: two people talking in a bar, from three engine acts (`confide`, `cold`, `repairjoke`), each with its situation in frame and the ordinary evening around it. Then the first cold readers on that one scene.
5. Write `act_check` and the cut check beside `trace_check.py`.
6. Take B1 to B5 to the engine, with B3 and B4 first: they are the two remedies for the Quiz II failure, and the engine's own human test needs them too.
7. Add the sifter's two rules (chains before single acts; nobody's first moment is their worst) to request 7.
8. Run the full cold reader test once the corner through the years exists (`living-fabric.md`, step 7), with people in it.

### For Øystein to decide

- State before trait (rule 4; rule 6 of `people-deep-dive.md`): states drive most of how someone moves, traits only a capped share. Recommended.
- What "not misled" means: misled by the screen is a failure; misled by a person who presents warmer than they are is the world working. Recommended, with the test separating the two.
- Bad acts between people need an engine event, while greetings may be derived from bonds (rule 8). Recommended.
- The camera as a witness with a place, so secret acts never show, for the look tests and LT2. A detective game may set the knowledge dial differently later.
- Era and fairness: 1989 public manners (smoking, drinking, how openly couples touch) come from the setting pack and apply to everyone alike. Any difference between people comes from the engine's acts, never from their sex, ancestry or who they love.

## Gaps

- The search budget ran out partway. Known only from summaries or from memory: The Sims 4's emotion animations, Red Dead Redemption 2's schedules and numbers, Animal Crossing's and Stardew Valley's schedule data, Watch Dogs' profiler, Prom Week, Versu's paper, Talk of the Town and Bad News, Wildermyth, Kenshi, Disco Elysium's readings, and Pentiment's meals. Each is marked where used; Wildermyth and Kenshi are not used.
- Gehl's distances and activity types, Whyte's triangulation and Jacobs's Hudson Street are from memory; the Gehl scan we found has no text layer.
- No study found on how well people read grief, debt or strain in strangers at a distance in daily life. The emotion studies use posed portrayals.
- Norway: the preferred distances (in Sorokowska's figure), display norms, and the 1980s daily rhythm from Statistics Norway's time-use surveys are still to fetch.
- The engine's two clocks: who owns the day and place of an act (B1) is still the open question in `living-world.md`.
- The starting caps of rule 3 are judgements from the accuracy tables, not measurements of motion. The lens audit and the first cold readers set them.
- Group sizes and walking speeds are in `animation-and-motion.md` (Moussaïd et al. 2010; Bohannon 1997). How the pace of a small town differs from a city's was not reached.

## Sources

Engine (read through the GitHub API, round 41): `src/families.ts`, `src/world.ts`, `src/social.ts`, `src/generate.ts`, `src/time.ts`, `src/setting.ts`, `src/persona.ts`, `src/love.ts`, `src/stress.ts`, `src/body.ts`, `src/witness.ts`, `src/boundary.ts`, `docs/STATUS.md`, `docs/ARCHITECTURE.md`, `docs/study.md`, `docs/method/reading.md`, `docs/method/prior-art.md`, `SUMMARY.md`, `WHY.md` in [Herreklo/Understory](https://github.com/Herreklo/Understory).

Games: [Sylvester, The Simulation Dream](https://tynansylvester.com/2013/06/the-simulation-dream/) · [RimWorld wiki, mental breaks](https://rimworldwiki.com/wiki/Mental_break) (secondary) · [Dwarf Fortress wiki, stress](https://dwarffortresswiki.org/index.php/DF2014:Stress) (secondary) · [CK3 wiki, stress](https://ck3.paradoxwikis.com/Stress) (secondary) · [CK3 portraits diary](https://www.thesixthaxis.com/2020/07/31/crusader-kings-3-developer-diary-contracts-portraits/) (secondary) · [The Sims 4](https://en.wikipedia.org/wiki/The_Sims_4) (secondary) · [Exult, Ultima VII schedules](https://raw.githubusercontent.com/exult/exult/master/schedule.h) · [Shadows of Doubt, citizens' routines](https://colepowered.com/?p=34142) · [Shadows of Doubt, the evidence board](https://colepowered.com/?p=33958) · [Hitman (2016)](https://en.wikipedia.org/wiki/Hitman_(2016_video_game)) (secondary) · [Massive Crowd on Assassin's Creed Unity](https://gdcvault.com/play/1022141/Massive-Crowd-on-Assassin-s) · [Red Dead Redemption 2](https://en.wikipedia.org/wiki/Red_Dead_Redemption_2) (secondary) · [Radiant AI](https://en.wikipedia.org/wiki/Radiant_AI) (secondary) · [Watch Dogs: Legion](https://en.wikipedia.org/wiki/Watch_Dogs:_Legion) (secondary) · [Façade](https://en.wikipedia.org/wiki/Fa%C3%A7ade_(video_game)) (secondary) · [Emily Short on Ryan's Curating Simulated Storyworlds](https://emshort.blog/2019/05/21/curating-simulated-storyworlds-james-ryan/) · [Kreminski et al., Felt](https://mkremins.github.io/publications/Felt_SimpleStorySifter.pdf) · [Grinblat, Procedurally Generating History in Caves of Qud](https://gdcvault.com/play/1024990/Procedurally-Generating-History-in-Caves) · [Kennedy, the art of Pentiment](https://www.gamedeveloper.com/art/deep-dive-the-art-of-pentiment) · [Sawyer on Pentiment](https://www.thegamer.com/interview-obsidian-josh-sawyer-pentiment/) · [Return of the Obra Dinn](https://en.wikipedia.org/wiki/Return_of_the_Obra_Dinn) (secondary) · [Kemenczy, Scenography of Kentucky Route Zero](https://gdcvault.com/play/1020596/Scenography-of-Kentucky-Route) · [Smith Nicholls & Cook, That Darned Sandstorm](https://arxiv.org/abs/2304.08293) · Versu, the Virtual Cinematographer and EMOTE as cited in `scenes-and-sound.md` and `people.md`.

Reading people: [Carney, Colvin & Hall 2007, thin slices](https://business.columbia.edu/sites/default/files-efs/pubfiles/3102/slices.preprint.pdf) · Ambady & Rosenthal 1992, Psychological Bulletin 111:256 (secondary) · [Connelly & Ones 2010](https://people.ict.usc.edu/~gratch/CSCI534/Readings/ConnellyOnes-personality2010.pdf) · Funder 1995, Psychological Review 102:652 (secondary) · [Gosling et al. 2002, in the APA Monitor](https://www.apa.org/monitor/mar02/officebetray) (secondary) · [Gilbert & Malone 1995](https://www.ebi.ac.uk/europepmc/webservices/rest/article/MED/7870861?resultType=core&format=json) · [Todorov & Uleman, trait inferences bound to faces](https://collaborate.princeton.edu/en/publications/spontaneous-trait-inferences-are-bound-to-actors-faces-evidence-f-2/) (secondary) · Ham & Vonk 2003, JESP 39:434 (secondary) · Skowronski & Carlston 1989, Psychological Bulletin (secondary) · [Nisbett, Zukier & Lemley 1981, the dilution effect](https://deepblue.lib.umich.edu/handle/2027.42/24406) (secondary) · [Barratt et al. 2016, the Kuleshov effect](https://pubmed.ncbi.nlm.nih.gov/27056181/) (secondary) · Heider & Simmel 1944, American Journal of Psychology 57:243 (secondary) · [Bond & DePaulo 2006](https://www.ebi.ac.uk/europepmc/webservices/rest/article/MED/16859438?resultType=core&format=json) · [Atkinson et al. 2004](https://www.ebi.ac.uk/europepmc/webservices/rest/article/MED/15330366?resultType=core&format=json) · Montepare, Goldstein & Clausen 1987, via [a review of emotion from gait](https://arxiv.org/abs/2003.11461) · Roether et al. 2009, Journal of Vision 9(6) (not read) · [Ranehill et al. 2015](https://www.ebi.ac.uk/europepmc/webservices/rest/article/MED/25810452?resultType=core&format=json) · Thoresen et al. 2012, Smith & Neff 2017 and Todorov et al. 2008, as cited in `people.md` and `people-deep-dive.md` · [Proxemics, Hall's zones](https://en.wikipedia.org/wiki/Proxemics) (secondary) · [Sorokowska et al. 2017](https://wrap.warwick.ac.uk/100226) · [Civil inattention](https://en.wikipedia.org/wiki/Civil_inattention) (secondary) · [Familiar stranger](https://en.wikipedia.org/wiki/Familiar_stranger) (secondary) · [Barrett & Bliss-Moreau 2009](https://www.ebi.ac.uk/europepmc/webservices/rest/article/MED/19803587?resultType=core&format=json) · [Hugenberg & Bodenhausen 2003](https://www.ebi.ac.uk/europepmc/webservices/rest/article/MED/14629699?resultType=core&format=json).

Streets and staging: Gehl, Life Between Buildings (1971; English 1987) (unverified, from memory) · [Whyte at Project for Public Spaces](https://www.pps.org/article/wwhyte) · Jacobs, The Death and Life of Great American Cities (1961) (unverified, from memory) · Goffman, Behavior in Public Places (1963) · [Time geography](https://en.wikipedia.org/wiki/Time_geography) (secondary) · Hooks, Acting for Animators (secondary) · Johnstone, Impro (1979) (secondary) · `what-moves.md` for opening hours and holidays.
