# The craft of play

How moving through, looking at and acting in the town should feel. It covers the speed of a walk and a climb, and how the eye is led without marks in the painting. It covers how the street hands over to a scene, how time is paused and run, the rhythm of hover, inspect and journal, and how all of it is tested. Øystein asked for master craftsmanship here: "how camera moves, how to show focus, how to navigate narrow streets". Step 1g, the playable greybox of the corner (`docs/plan.md`), takes its feel from this page.

Four studies sit beside it. `camera-and-composition.md` owns the camera (ladder, tilt, lens, collision, springs, comfort, the controls table). `collision-and-navigation.md` owns the way graph, the movers and the walk layer. `interface-and-inspection.md` owns hover, cards, the journal, picking and text. `time-on-screen.md` owns jumps of years. This page owns what lies between them: feel, guidance, rhythm, transitions, time controls, feedback and sound, and playtesting.

Written on Opus, October 2026, with two helper passes: one on movement, tight spaces, crowds and the best role-playing games, one on guidance, attention and playtesting. Claims from a maker's own words, a paper, official documentation or source code are unmarked. Those from reviews, translations, wikis, abstracts or search summaries are marked (secondary), and those nothing confirmed (unverified). Our own arithmetic or reading is marked (our estimate). GDC Vault was down for maintenance throughout, so no GDC slides opened; talks were read through reports and translations (Gaps).

## The bottom line

- Feel is response first. Steve Swink puts game feel mostly in how the game shapes input over time, then in the spaces it moves through, with polish last. We keep the first two and take polish from the world: a tread's sound, a door's weight, a person turning to look. Shake, squash and particles are out.
- Three ways of moving. The free camera roams (`docs/visual-direction.md`). A walk mode at eye level feels the climb (the collision study's proposal). Staged scenes are point and click.
- Walk at a person's pace, slower on stairs. People walk at about 1.33 m/s and climb at about half that along the ground; games run two to three times faster. Our walk starts at 1.4 m/s and slows to about 55 per cent on a flight. The climb is felt through speed, tilt and sound, never bob.
- Guide with facts, never with marks. Every lure that works in the best games is a fact of the world (a lit window, a moving person, a sound, a landmark) or an interface signal outside the painting. Breath of the Wild replaced lines between towers with "gravity", places worth reaching. Naughty Dog treats painted cues as a "fallback plan".
- Being taught narrows play. Children shown one function of a toy explored less and found fewer hidden ones. Guidance says that something exists, never how.
- Move inside the world, cut at its thresholds. A move that would be fast becomes a cut. Doors are where cuts belong: ease to the door, hold, cut inside.
- Time controls are a budget. Life sims run normal speed at 60 to 86 times real time, let the player act while paused, and slow for what the player cares about. A jump of years is a chapter, never a speed.
- Answer every input within 100 ms; animate nothing the player waits on for more than about 300 ms.
- Calm is the periphery at work. Calm technology moves "from the periphery of our attention, to the center, and back" (Weiser and Brown). The town is the periphery; the interface comes to the centre when asked.
- Feel is tested by watching people. Valve values what players do over what they say. Model readers cannot feel, but they can check paths and salience and replay a session exactly.

## 1. Moving through the town

### What the masters do

| Game | How the player moves | What it gives | What it costs |
| --- | --- | --- | --- |
| Pentiment | walks on tracks through flat scenes; no camera control | framing always composed; Kennedy: tracks gave "more control over the camera framing" | long tracks are "very time-consuming to walk along", so every path needed content; paths up into the frame were hard to read |
| Disco Elysium | click to move in a painted isometric frame; the camera cannot pan (secondary) | the frame designed "as if it was a painting" (Rostov, secondary) | one view per place |
| Kentucky Route Zero | click to move on stage-like sets | theatre framing; staging by light (`scenes-and-sound.md`) | no free looking |
| Firewatch | first person; a walk and a slightly faster jog (secondary) | the slow pace reads as character and makes you look (secondary) | long walks between beats |
| Journey | direct control; sand-surfing downhill | plain walking was not engaging, and a jump button would make players hop (secondary) | needs a reason to move beyond walking |
| Assassin's Creed | direct control in crowds; low and high profile | the crowd ignores you unless you run or jump (Tremblay); a hold-to-push through dense streets (secondary) | a hero's speed through a historical city |
| Hitman (2016 on) | direct control; disguises; watching routines | a level learned by watching | the scale was "incomprehensible" to first players (secondary) |
| Cities: Skylines, Tiny Glade, Manor Lords | free camera, zoom to the cursor | the whole town under the hand | no sense of a body |

Baldur's Gate 3 and the other role-playing games are in section 4. For free cameras, Tan, Robertson and Czerwinski (CHI 2001) lifted and tilted the camera as it sped up, keeping the flow on screen about constant. Fourteen of 17 users preferred it, and it cut the distance travelled on tasks from about 630 m to 230 m. The camera study already ties speed to height.

### Three ways of moving

`docs/visual-direction.md` decides that "the player moves through the town as this free camera, not as a person they walk". The collision study adds a walk mode at eye level as a toggle, for Øystein to confirm (`NOW.md`). The jobs sort like this:

| Mode | For | Feels like | Owned by |
| --- | --- | --- | --- |
| Roam | finding, watching, comparing, reaching any place fast | a city builder's camera that comes down into the lanes | camera study |
| Walk | feeling the climb, the narrowness, the light in a lane | a person on foot, at a person's pace | this page, with the collision study's walk layer |
| Stage | a scene: a conversation, a gig, an interview | a composed set, point and click | `living-world.md`, `scenes-and-sound.md` |

Click-to-move belongs to roam (the camera study's double-click "go there") and to staged scenes, as in Disco Elysium and Kentucky Route Zero. Walk is direct control only, since its point is the feel of each step.

### Speed, acceleration and stopping

Swink's model has six parts: input, response, context, polish, metaphor and rules. Mario beat Donkey Kong because Mario's response changed with time, with buttons held together, and between ground and air. An earlier Gamasutra article, probably his, adds that zooming in raises the impression of speed and a raised view lowers it (unverified authorship). So a lane at eye level feels fast at a pace that would crawl from 12 m. Book excerpts put the thresholds at 50 ms for instant, 100 ms for noticeable and 240 ms for the end of real-time control (secondary). They follow Card, Moran and Newell's 100 ms perceptual cycle. Nielsen's limits agree: 0.1 s feels instant, 1 s keeps the flow of thought.

| Measure | Value | Source |
| --- | --- | --- |
| Preferred walking speed | about 1.33 m/s at 112 steps a minute | gait studies (secondary) |
| Social force model's desired speed | 1.34 ± 0.26 m/s, relaxation time 0.5 s | Helbing and Molnár 1995 (secondary) |
| Reaching steady speed from rest | one to three steps, about 0.5 to 1.6 s | gait initiation studies (secondary) |
| Stairs, up and down, horizontal | mean 0.63 and 0.73 m/s on a 30° stair; the level's mode 1.23 m/s | Pouw, Corbetta and colleagues 2024 |
| Half-Life 2 | walk 150, run 190, sprint 320 units/s, about 2.1 player-heights a second | Valve wiki (secondary) |
| Unity's third-person starter | move 2.0 m/s, sprint 5.3 m/s, speed change in about 0.1 s | the starter script (secondary) |

Games run faster than people because their distances are compressed. Ours are not: the heart is a real town at real scale, and a lane's interest is in its walls. So the walk keeps a person's pace, and roam covers distance (our estimate).

Every smoothing uses Daniel Holden's critically damped spring, set by a half-life, exact at any frame rate and continuous in velocity, as the camera study already does. No studio publishes what makes motion heavy or floaty. Long attacks and releases feel like "running on ice", very short ones mechanical (secondary). People take 0.5 to 1.6 s to reach their pace, which would feel slow to answer in a game. So response starts within a frame and full speed builds over about a third of a second (our estimate).

### Lanes and stairs

Most games put an invisible ramp under the steps and let the feet find the treads (secondary); the collision study does the same. The view is the hard part. After a step up, Quake lifts the eye at a fixed rate, at most 12 units behind, so a step never jolts. That is about 0.37 m at our scale (our estimate). Nesky says to ignore brief vertical motion and to look ahead and average the slope (secondary). The camera study follows a ground line smoothed over 2 m, looked ahead half a second, and leans its tilt by half the slope.

Head bob is out by default. Microsoft's guideline 117 asks to "avoid the use of camera shake, camera bobbing effects, motion blur", or let players turn them off. The eye's motion without the body's makes people sick. So the climb is carried three other ways:
- *Speed.* The walk slows to the measured share of level speed on a flight and recovers on the landing.
- *Tilt.* The view leans up the flight and levels on the landing, as the camera study gives it.
- *Sound.* One footfall per tread, timed to the tread table, its timbre from the stone and its wear. Footsteps that change with the ground carry place; Breath of the Wild changes them by material (secondary).

### Crowds and other people in lanes

Assassin's Creed Unity gave full behaviour to at most 40 people within 12 m; figures beyond were pushed aside without reacting (secondary). The 2007 game's crowd ignored the player "as long as you weren't holding the triggers to run or jump". Hitman's crowd reacts by zones, the most severe reaction winning (secondary). In all of them only the nearest people respond.

Our people never react to the camera (collision study, For Øystein, 2), and the walker is the camera on foot. Passing through a person looks wrong at eye level, so the walker yields. It slows, sidesteps within the way's free width, and stops behind someone on a flight under 1.3 m wide (our estimate). The people never move for the walker; the walker moves for them.

## 2. Showing focus and guiding the eye

### How the masters guide

Fujibayashi and Yonezu's CEDEC 2017 talk on Breath of the Wild's field design is the clearest account of guidance built from the world (Famitsu's report, quoting the speakers; secondary). Heat maps from several hundred testers showed that in an early build almost everyone kept to the roads, and towers joined by lines split players into followers and refusers. The fix was "gravity": places worth reaching, drawing the player as "insects drawn to light". A landmark's pull depends on its size, the player's goal and the hour, and each destination reveals the next. Yonezu's triangles make the player choose over or around, hide what lies behind until it is rounded, and lead the eye to the tip. The team tested by walking the field, and set its spacing from real rulers: how far one sees in Kyoto, how densely post boxes are spread.

Every one of those lures is a fact of the world. A town has its triangles already: a lane that turns, a gable that hides the tower until the corner, a stair whose top is out of sight. The town plan lists its reveals (`docs/town-plan.md`, after Cullen's serial vision).

At Naughty Dog, Emilia Schatz sorts affordances into explicit, defined, cultural and inferred: "Explicit and Defined messaging break immersion and so should be considered a fallback plan." Stairways "communicate the existence of vertically leading paths". Robert Yang's half of the GDC 2018 level design workshop, shared with Naughty Dog's David Shaver, lights by hierarchy: "a main entrance deserves more lighting than a sneaky side exit". One practice is closed to us. Lighting artist Boon Cotter moves the sun and moon "ALL THE TIME" for the picture (secondary). Our sun is computed, so we choose only which hour and weather a scene is staged in, from the record.

Jonathan Blow, on The Witness: "If something grabs your attention, it had better be important." The island's art cut colour and detail to the least an object needs (secondary). For us, non-semantic texture (woodgrain, a lean, clutter) must stay low in salience, or players will read history into it.

In Journey the mountain is visible from the start (secondary), and Matt Nava saved blue skies for the end "as a reward".

In Hitman (2016), user research late in development found "the learning curve was way too steep", and a linear guidance layer went over the sandbox (secondary). Hannes Seifert called the opportunity alert information, not guidance: it says something can be done, not how. It can be switched off, because "hardcore players will turn it off right away" (Destructoid). Overheard talk is the usual way in, and back stages reward the player with information (Andersen, 2019; secondary). In our terms that is perceived information: a fair lure that may be wrong.

Ghost of Tsushima replaced the waypoint with a guiding wind and animals that lead (Nate Fox, Press Start). Our wind and animals come from the record, so that trick is closed to us.

### Attention, gaze and sound

- One point of motion takes every eye. In Tim Smith's eye-tracking of *There Will Be Blood*, faces held most of the gaze, a head turn sent eyes after it, and with one point of motion "all viewers will look at the motion".
- People follow gaze. In Gallup and colleagues' study of 3,325 pedestrians, the chance of looking up grew with the size of the group already looking, then saturated. Following happened mostly within about 2 m. Milgram's 1969 sidewalk study is the classic version (figures unverified).
- Goals beat salience in 3D games: contrast and motion draw the eye, but search for a goal dominates (El-Nasr and Yan; secondary). About two thirds of fixation time fell in the screen's central ninth in one 3D game study (secondary).
- Sound and moving light steer attention in cinematic VR; static lights alone did not (Rothe and Hußmann; secondary).
- Valve's Half-Life lesson: "Letting players see other characters make mistakes that they'll need to avoid is an effective way to explain your puzzles" (Birdwell).

### What our rules allow

| Lure | Allowed | Example in the town |
| --- | --- | --- |
| A landmark seen from afar | yes: a fact | the tower on Watch Knoll; the crane on the quay; the Anchor's sign |
| A place worth reaching | yes: a fact | a lit shop at dusk; a market day on the square; a bench in the sun |
| A turn, a gable, a stair's hidden top | yes: the town's own shape | the gully's upper flight bending out of sight |
| A lit window, a lamp, a shop's light | yes, where the record lights it | the loft lit on rehearsal nights |
| A person moving, a door opening, smoke | yes: scene state from the record | the woman in the green coat crossing the Landing at four |
| People looking at something | yes, when the engine's event gives them a cause | a crowd at the Anchor's door looking up the lane |
| A sound: a voice, music through a wall, a bang | yes, from occupancy and events | the band heard from the loft; a quarrel through a window |
| The hour and weather a scene is staged in | yes, chosen from the record's options | a conversation staged at dusk when the windows are lit |
| The grade: chroma richest at the focus | yes: the camera's look, not light (`visual-direction.md`) | a mood that keeps colour in the focus and drains the rest |
| Inspect's gentle dimming | yes: interface, read as the camera | the frame softens round a card |
| A thread marked on the journal's map | yes: interface, outside the painting | "?" on the Holm for a place heard of |
| A switchable notice that something exists | yes: interface | "Voices at the Landing" in the margin, never an arrow |
| Yellow paint, a painted ledge or handhold | no: a mark that is not a fact | |
| A moved sun or moon, a light with no source | no: a false fact | |
| A glow, rim light or outline on what matters | no in the painting; an accessibility mode at most (interface study) | |
| Wind or birds bent to the goal | no: weather and animals come from the record | |
| A tinted reveal mode over the world | no (interface study: the Arkham trap) | |

### Depth of field and dimming

The camera study rules out depth-of-field blur from raised views, since it turns a town into a miniature. The interface study dims the frame a little on inspect. How much either guides is barely measured. Su and Takahashi's "semantic" depth of field cut the time to first fixation on warning signs from 6.15 s to 4.95 s, in one scene with ten viewers. Shallow focus raised central looking in free exploration but not during search (secondary). Brief flicker in the periphery also pulls gaze (Bailey and colleagues; secondary), but a flicker in the painting is a mark. So focus comes from the inspect dimming, natural depth of field at eye level and in staged scenes only, and the camera's "frame this".

### Discovery, not instruction

Bonawitz and colleagues (2011) gave 85 preschoolers a toy with hidden functions. Children shown one function played for 119 s and tried 4.0 kinds of action; children left alone played for 206 s and tried 6.2. Even overhearing another child being taught narrowed play: "pedagogy promotes efficient learning but at a cost." Blow wants "opportunities", since "you can't force people to have an experience". Alex Beachum built Outer Wilds so that "the sole purpose of exploration is to answer questions about the world you're in".

Guidance feels like discovery when the player could have noticed the cue unaided, and the cue was there anyway. Say that something exists, never how, and let each find lead to the next.

## 3. Transitions and rhythm

### Cuts and continuous moves

Film hides cuts by attention: a third of match-action cuts went unnoticed in one detection task, against a tenth of cuts between scenes (Smith and Henderson 2008; secondary). Cory Barlog built God of War (2018) without a cut, since cuts are film's vocabulary and "games are different" (secondary). Nesky's game rules: keep the input's meaning across a cut, show a landmark after it, never flip 180°, and cut rather than make a fast move (secondary).

So the camera never cuts while the player roams or walks, and the town stays one place. A cut belongs at a threshold, where the world changes (outside to inside, street to staged set), and across a jump of years (`time-on-screen.md`).

### Entering a house or a scene

A threshold is a short sequence, each beat with a job:

| Beat | Time | What happens | Why |
| --- | --- | --- | --- |
| Commit | at the click's release | the cursor confirms; the door's own sound starts | the act answers within 100 ms |
| Approach | 0.6 to 1 s | the camera eases to the threshold's outside pose, the front in frame (camera study) | the place is seen before it is left, as Ozu cut to the building first |
| The door | 0.3 to 0.5 s | the door opens on its hinge side, or someone opens it | the house's own act, not a fade |
| Cut | one frame | to the inside pose; the street's sound held under the room's | sound carries across the cut |
| Settle | 0.4 to 0.8 s | the room's sound rises, the street's falls away; control returns | the ear finds the room as the eye does |

Leaving reverses it: a cut to the outside pose facing into the street, the room held a moment under the street's sound. Kentucky Route Zero's dissolving walls belong to staged scenes, where the frame already says theatre (`scenes-and-sound.md`). Yakuza 6 dropped its loading doors, so any room is entered "without loading" (Nagoshi, via GamingBolt); our door beat is kept for meaning, not to hide a load.

### Time controls

| Game | Speeds | Pause | What we take |
| --- | --- | --- | --- |
| The Sims 4 | normal (a game minute a real second), fast, ultra; keys 1 to 3, P to pause (secondary) | acting while paused | 60 times real time as the base |
| RimWorld | 1×, 3×, 6× (15× in dev mode); a game hour takes 41.7 s at 1× | acting while paused; a forced slowdown on raids that players mod away (secondary) | slow down for what matters, but let the player turn it off |
| Crusader Kings III | five speeds; events pop up and pause (secondary) | the whole game is playable paused | decisions made in pause |
| Football Manager | continue to the next event; match highlights as key, extended, comprehensive or full, with a speed slider (secondary) | the game waits for you | the player chooses how much of an event to watch |
| Cities: Skylines II | each day and night stands for a month of simulation (secondary) | | a visual clock and a record clock can differ |

Normal speed runs 60 to 86 times real time, so a day is a sitting (Stardew Valley's is about 86 times; section 4). The player may act while time is stopped. Time slows for what the player cares about, which players resent when it is forced. Football Manager lets the player choose how much of a big event to watch. Our two clocks fit this (`docs/living-world.md`): the scene clock runs hours and minutes and takes speeds; the record clock runs months and years and never does.

### The rhythm of hover, inspect and journal

The interface study set the dwell before a name (about 250 ms), the move to a neighbour (about 100 ms) and label fades (200 to 300 ms). Material Design's motion tokens give a tested scale from 50 ms to 1 s. Its rule for curves: things entering decelerate, cubic-bezier(0.05, 0.7, 0.1, 1); things leaving accelerate, (0.3, 0, 0.8, 0.15). Its fades run 150 ms in and 75 ms out for small elements. Those are phone conventions, but the scale and the asymmetry carry over. A thing arrives a little slower than it goes, and nothing the player waits on takes longer than about 300 ms. Camera moves are travel, governed by their springs.

### Restraint

"Juice it or lose it" (Jonasson and Purho, 2012) wanted a game that "responds to everything you do". Its means were tweens, squash, particles and shake. Folmer Kelly answered in 2014 that such polish costs immersion (secondary). We keep the first half as law: every input is answered. The answer comes from the world and a quiet interface: the door's weight, the tread's sound, the cursor, the card.

Weiser and Brown's calm technology names the balance. The periphery is "what we are attuned to without attending to explicitly". In the town it is the murmur, the lit windows, people crossing, the sea; the centre is the card, the journal, a scene. Nothing in the interface pulses or calls for attention unasked.

## 4. What the best role-playing games teach

In Baldur's Gate 3 a click on the ground moves; WASD pans, Q and E turn; holding Alt outlines nearby things in yellow, red where taking them is theft (secondary). Its best idea for us is perception: a hidden thing appears only when a character's roll notices it, with a dice sound and a note in the corner (secondary). The mark follows a fact, "this person noticed this", as our witness model does. A cinematic dialogue starts with the player's character alone. Companions who come close may join, and the rest of the party keeps acting, even pickpocketing the speaker (Larian, Community Update 6). The cinematic director called it "taking that camera down from being above the players, and down into the drama". Early access had planned a camera "quite far away", and the team grew from about 120 to 400 people, much of it for cinematics (PC Gamer). The hand-over's timings were not found.

Divinity: Original Sin 2 has the same Alt key, and players complain it misses things (secondary). An incomplete highlight teaches players to distrust their eyes.

In The Witcher 3, held senses draw tracks and clues in red or yellow over a dimmed world (secondary). CD Projekt's Paweł Sasko says they "kind of overcooked it" (TheGamer), and doors that never open still glow (secondary). That is the failure our rule prevents: a mark advertising a non-fact.

Kingdom Come: Deliverance II runs nearly 2,400 persistent people on daily schedules (Labuť's 2024 abstract), with routines there "for you to work with them" (Warhorse). In Hardcore mode the map shows no position, and players ask travellers the way and steer by landmarks (Deep Silver).

Pathologic 2 gives "only 12 days" and "lose-lose" choices (Ice-Pick Lodge). Its narrative designer wanted a clock "of indifference, of the world living on its own" (EGM). The plague shows in the street as facts, not on a map: miasma in infected districts, boils on walls, bells on the third evening (secondary).

Persona spends after-school and evening slots on people or places (secondary). Katsura Hashino keeps "about 60 to 70 percent" of the context familiar, and says a time limit gives a journey "a beginning and end" (Inverse).

Yakuza's Kamurocho is small but "densely populated and it's deep" (Nagoshi; secondary), rebuilt for each era with research into how the 1980s looked (secondary). One dense place across decades is our case.

Stardew Valley runs about 86 times real time, a day in about 14 minutes (secondary). Each villager's day is a list of times and places, picked by a priority of keys: festival, date, rain, weekday, season (secondary). So routines repeat by weekday and season, with named exceptions. Our day plans should be as learnable.

## 5. Narrow streets

The camera study covers the camera in lanes: it slides along walls, keeps a 1 m standoff and crosses roofs only from above. It cuts nothing away, because a hole in a wall reads as damage. The collision study covers passing on flights and the 1.3 m width two people need. What remains is what each height is for in play:

| Height | Reads well | Play it serves |
| --- | --- | --- |
| Eye level, walking | treads, wear, doors, signs, faces at a few metres | feeling the climb; reading a house's front; overhearing |
| Street stop, 2.8 m | a lane's length, who is in it, shop fronts, posters | watching a routine; following a person; most inspection |
| 12 m | a lane in its block, yards over walls, who goes where | seeing where people go; choosing the next place |
| City | the town's shape, landmarks, crowds as marks | going far; the journal's map |

Doors carry most of a lane's play, so they must say what they are. Schatz: doorways "invite players to move through them". The rule cited from Arkane is that doors you can use look different from doors you cannot (secondary). Our doors are facts, so their state shows as a fact: open, shut, boarded, a light behind the glass, a worn sill on a door in daily use. A door the player can enter as a scene is told by the cursor (interface study), never by a glow. Witcher's glowing dead doors are the warning.

## 6. Feedback and feel without noise

### Confirmation, selection and errors

- Every input is answered within 100 ms, by the cursor, a sound or the world. Interface study timings stand: the hover lift at once, the name after 250 ms.
- Activation on release, so a click can be cancelled by moving away first (Microsoft's guideline 107).
- Selection is the dimming and the card, never a colour on the thing (interface study).
- An act the engine refuses (`docs/living-world.md`: commands it accepts or refuses) answers with its reason in words, in the person's voice where there is one. No buzzer, no red, no shake.
- A place the walk cannot go is a soft stop: the walk slows over the last half metre and holds. No bump, no sound of failure.

### What play needs from sound

Sound is a gap (`docs/systems.md`). Play needs these from it, whoever designs it:
1. *Footfalls by surface and wear,* one per tread on flights, timed from the tread table, so the climb is heard.
2. *A keynote per place* (Schafer, in `scenes-and-sound.md`): the lane's close reverb, the square's openness, the quay's water and gulls.
3. *Leaks from occupancy:* music from the loft, a radio, voices through a window, each from a fact of who is in. These are lures.
4. *Overheard words* as text where sound would carry them, since scenes are written, not voiced: the murmur is heard and the words read.
5. *Thresholds:* each door's sound, and the outside held under the inside across the cut.
6. *The interface's own few sounds,* soft and dry: hover on a person, open a card, a journal entry kept, pause. Off by a switch.
7. *Pause and speed:* the world's sound thins to a room tone on pause; it never stops dead.

### Accessibility for play

The interface study set text, contrast, the plain face, the outline mode and the reveal key; the camera study set the camera's comfort options. Play adds:
- *Motion:* no bob, shake or motion blur by default; a field-of-view setting; automatic camera motion can be turned off (guideline 117).
- *Input:* every action remappable, as actions rather than keys; keyboard alone can play the whole game; no hold over about 2 seconds without a toggle; no simultaneous presses; analog sensitivity adjustable by at least 50 per cent either way (guideline 107). Wasteland 2's single click to move is the guideline's own example for players who cannot hold and drag.
- *Time:* pause anywhere, at any time, including in scenes. The guideline lists slowing the game as an aid to players who need more time.
- *Guidance:* the switchable notice layer doubles as an aid. Describing traces stays an option (interface study).

## 7. Playtesting the feel

### How studios do it

Valve's Mike Ambinder (GDC 2009): "Game designs are hypotheses / Playtests are experiments." Watch what people do, "not what they say"; think-aloud explains why but makes play artificial; "averages hide extreme examples". Eye tracking measures attention but "can lead to costly over analysis". Ken Birdwell's Half-Life team ran one outside player at a time from the third month, the designers silent behind them. Each session gave about a hundred action items, and the first twenty or thirty were "absolutely critical". Microsoft ran 25 to 35 players a playtest and about 8 for usability. In Halo, players fought at longer range than intended, so the reticle and enemies changed and a retest confirmed it (Davis, Steury and Pagulayan, 2005). EA's SEED trains agents to find where players get stuck (secondary). No studio account of A/B-testing movement or camera numbers was found.

### Extending our readers to play

Model readers see stills, so they cannot feel (`docs/foundations.md`). They can still do four things for play:
1. *Read paths.* The camera study's motion-sheet paths and sweeps, read for whether a lane, a landmark and the next place stay legible along the way.
2. *Check salience.* A saliency model run on the judging views names the strongest pulls in each frame. The intended lure (a lit window, a moving person) should rank first, and non-semantic texture never should: Blow's conservation of attention as a measure (our proposal).
3. *Replay sessions.* Positions are functions of the plan and the clock (collision study), so a logged session replays exactly, and readers can read its frames at each decision.
4. *Play on paper.* The paper playtests already run concepts with agent players (`docs/playtests/paper-1/`). The greybox gives them real frames.

What only people can test: comfort, responsiveness, whether a lure is found, whether guidance feels like discovery, the pad. Øystein plays first, then first-time players, Valve's way: silent observers, a log, one question after.

## 8. The proposal

The evidence above decides this section, as first values to be tuned by playing; only the four questions under For Øystein are his.

### Controls

The camera study's controls table stands. Play adds these, and moves one key:

| Act | Mouse and keyboard | Gamepad |
| --- | --- | --- |
| Walk mode on and off | V | click the left stick (remappable) |
| Walk | WASD; mouse look raw, never smoothed | left stick with an S-curve; right stick looks |
| Brisk pace | Shift, hold or toggle | left trigger, hold or toggle (height is fixed while walking) |
| Pause and resume | Space | d-pad left past the slowest speed; the menu also pauses |
| Clock slower, faster | minus and plus | d-pad left and right |
| Skip to an hour or the next followed act | U, then pick | from the clock's panel |
| Follow a person | from the person's card | from the card |
| Journal | J or Tab | X |

Space moves from the camera study's "hold" to pause, which is where Paradox, RimWorld and Cities players look for it (unverified); hold moves to H. Number keys stay the camera's stops.

### Walk mode, with numbers to start from

| Value | Start | Range to try | From |
| --- | --- | --- | --- |
| Walking speed | 1.4 m/s | 1.3 to 1.8 | gait studies; Helbing |
| Brisk pace | 2.2 m/s | 2.0 to 2.6 | the camera's eye-level pan |
| Speed rising to input (spring half-life) | 0.12 s | 0.08 to 0.2 | Holden; Swink's response |
| Speed falling to a stop | 0.08 s | 0.05 to 0.15 | stopping takes a step |
| Up a flight, share of level speed | 0.55 | 0.5 to 0.65 | Pouw and colleagues; Fruin |
| Down a flight | 0.6 | 0.55 to 0.7 | the same |
| Change at a flight's foot or landing | over one stride, about 0.5 s | | |
| Eye height, view line, tilt on a flight | the camera's eye stop, smoothed ground line and half-slope lean | | camera study |
| Head bob | none; a slider from 0 | | guideline 117 |
| Footfalls | one per tread on flights; about two a second on the level | | the tread table |
| Meeting a person on a way under 1.3 m wide | slow from 2 m, stop 0.8 m behind | | collision study's widths |
| A drop edge or wall | slow over the last 0.5 m, hold | | |

Every first value is tuned by playing, one change at a time.

### The guidance toolkit

The table in section 2 is the toolkit. Three rules govern it:
1. *One pull per frame.* The visual direction already asks for one focal point per frame. When a game wants the player somewhere, the pull is chosen by staging from the record (the hour, the weather, who is out), never added.
2. *Pull, then name.* The world pulls; the interface names only what the player has met, and its notices say that something exists, never where to stand or what it means.
3. *Lures are budgeted like histories.* The interface study's budget per view (one, two, three) holds for notices and highlights too.

### Transitions and time controls

- Inside the town the camera never cuts. Doors and staged scenes cut, by the threshold sequence in section 3.
- The scene clock has a pause and four speeds. They are 1× (real time, for scenes and watching an act), 60× (an hour a minute), 360× (an hour in ten seconds), and a skip to a chosen hour or the next act of someone followed. Changes ease over 0.3 s, so nobody jumps.
- Everything can be read and inspected while paused.
- An option slows the clock to 60× when someone the player follows begins something, with a notice.
- The record clock is never a speed. A jump of years is a chapter, held and compared as `time-on-screen.md` says.

### The rhythm, with timings

| Event | First response | Duration and curve |
| --- | --- | --- |
| Cursor over a thing | lift at once (the id comes back 33 to 50 ms late) | lift in over 80 ms, out over 120 ms |
| Its name | after 250 ms of dwell; 100 ms to a neighbour | fade in 200 ms decelerating, out 150 ms |
| Click to inspect | card within 100 ms of release | in over 150 ms decelerating; dimming in over 300 ms |
| Card closes | at once | out over 100 ms accelerating; dimming out over 200 ms |
| Something kept in the journal | a soft sound; a mark on the journal key | mark in over 200 ms; no pop-up |
| Journal opens, closes | at once | 250 ms, 200 ms |
| Frame this | the camera starts within a frame | springs; a move of over two zoom stops or 40 m cuts instead |
| Pause | the clock stops in the same frame | sound thins to room tone over 300 ms |
| A command refused | its reason within a second, in words | as a card |

The constants live in one table in code, so the greybox tunes them in one place.

### What the building blocks must carry for play

The camera, collision and interface studies list hulls, tubes, thresholds, the way graph, ids and anchors. Play adds:
1. *Lures as facts.* Each record's light, sound and motion, with the hours it is on, so a view's pulls can be listed and checked against its focal point.
2. *Sound data.* A footfall class per walk surface (stone tread, wet stone, timber, setts, gravel) with its wear; an acoustic class per open space; a sound per door; a leak per occupied room, from who is in.
3. *Doors as dated states.* Open, shut, locked by the hour, boarded, and whether a scene lies behind.
4. *Points of interest from the record.* The change query's weights, the routine stations (sit and stand points) and the records (posters, signs) in one index. It feeds the journal, the notices and the reveal key, never the painting.
5. *Landmark sight lines.* From each vantage and each threshold's outside pose, which landmarks show, so a cut can always end on one.
6. *Pause-safe motion.* Everything that moves is a function of the clock (collision study). Anything that is not, such as cloth or smoke, freezes and resumes without a pop.

### Testing and tuning in the greybox

- *Logs.* The camera's pose log, plus every input with its time, every hover and inspect, speed changes, pauses, notices shown and followed. From them, heat maps of where the camera stood and what sat at the screen's centre, a fair proxy for gaze since fixations crowd the central ninth.
- *One change at a time.* Pairs such as walking at 1.4 against 1.8 m/s, a speed rise of 0.08 against 0.2 s, a name after 250 against 400 ms, notices on against off.
- *Tasks.* The camera study's four, plus: find the Anchor from the quay unaided; learn one person's routine in three evenings; enter the loft and come out; pause and compare two hours.
- *Measures.* Time per task, moments of fighting the controls, lures found unaided against after a notice, a comfort rating after fifteen minutes, and one question at the end: what did you notice?
- *People.* Øystein first, then rounds of five to eight first-time players, each seen once, watched in silence.

### What each first-game option changes

The options are in `docs/ideas/first-game-options.md`.

| Option | Moving | Guidance | Time | Feel to tune first |
| --- | --- | --- | --- | --- |
| The club | roam at 12 m and the middle stop; walk on match day | the ground's lights, players' routines | weeks, then "continue"; match moments at a chosen depth | the match-day hand-over |
| The band | roam, and walk at night | sound from the loft and the venues | evenings as slots; jumps of years | sound and thresholds |
| The restorer | walk and eye level | the traces themselves, the field guide | months per project; much reading in pause | close looking and inspecting |
| A life and its heirs | walk with a body | family and home as the pull | a calendar of evenings; acts years apart | the body and the calendar |
| The paper | roam the whole town | overheard talk | a weekly deadline | following and notices |
| A death in the town | roam and walk; watching | routines, accounts, people's gaze | days to the inquest, running | the clock's pressure; following |

## What we should do

Ranked by what each buys for 1g. Costs are Opus days, on top of the camera and collision studies' own items.

1. *Walk mode's feel:* the numbers above, yielding, soft stops, footfalls on the treads. Half a day on the collision study's walk layer.
2. *The scene clock:* pause, four speeds, easing, the skip, the slow-down option, pause-safe motion. A day.
3. *The rhythm table* in code, applied to hover, cards and journal. Half a day.
4. *Placeholder sound* from free libraries: footfalls for stone and timber, a lane keynote, the loft's leak, door sounds, the threshold's held sound. A day.
5. *One threshold* on the corner to a placeholder room, with the sequence and its sound, shared with the camera study's item 9. Half a day.
6. *Logs and heat maps* beside the camera's pose log, with exact replay. Half a day.
7. *The salience check* on the judging views. A day.
8. *The first playtest* with Øystein, then a round of first-time players. Half a day each, plus their time.
9. *The notice layer,* once the greybox shows players get lost. Half a day.
10. *Write the rules where they apply:* the rhythm and the threshold into `docs/research/interface.md` and `docs/living-world.md`, the sound needs into `docs/systems.md`. Not done here, by instruction.

## For Øystein to decide

1. *Walk mode's body (play).* Recommended: in 1g the walker is the camera on foot, with no body, and people never react to it. A visible body comes only with a game that makes the player a person (a life and its heirs).
2. *Does the clock run while the player reads? (play)* Recommended: yes. It runs while roaming and while a card is open; the journal pauses it; pause is always one key away. In a game with a deadline, running time is the pressure, as in Pathologic.
3. *Slowing for followed acts (play).* Recommended: on by default, and switchable.
4. *Notices (play).* Recommended: on for a game's first hours, saying only that something exists ("Voices at the Landing"), switchable; never an arrow, a distance or a mark in the painting.

## Gaps

- GDC Vault was down for the whole study. Not read: Designing Journey, Nesky's slides (read through a translation), Hitman's level design and crowd talks, Assassin's Creed Unity's crowds, Lemarchand's "Attention, Not Immersion", Larian's GDC 2024 talks, Jane Ng's Firewatch talk.
- No developer source was found for walking speeds in Firewatch, Kingdom Come, Yakuza or Disco Elysium; for Disco Elysium's area transitions; for Baldur's Gate 3's hand-over into dialogue or its Lower City roofs; or for The Witcher 3's choice of red.
- Swink's book text was not reached; its thresholds are secondary.
- Smith's continuity paper and So's study of navigation speed and sickness would not open.
- No study measures how much camera lag or acceleration players prefer, and no studio's A/B tests of movement were found.
- Nothing measures how fast a free camera at eye level should move in a lane; the camera study's cap from optic flow is our estimate.
- Feel, comfort and discovery can only be tested with people.

## Sources

Movement and feel: [Swink, Game Feel: The Secret Ingredient](https://www.gamedeveloper.com/design/game-feel-the-secret-ingredient) · [Principles of Virtual Sensation](https://www.gamedeveloper.com/design/principles-of-virtual-sensation) · [Liz England's review of Game Feel](https://lizengland.com/blog/review-game-feel-by-steve-swink/) · [Pomona course notes on movement](https://cs.pomona.edu/classes/cs181g/notes/movement.html) · [Holden, Spring-It-On](https://theorangeduck.com/page/spring-roll-call) · [Quake's view.c](https://raw.githubusercontent.com/id-Software/Quake/master/WinQuake/view.c) · [Unity CharacterController](https://docs.unity3d.com/Manual/class-CharacterController.html) · [Pouw, Corbetta and colleagues, stair speeds](https://arxiv.org/html/2307.15609) · [Helbing and Molnár, social force](https://arxiv.org/abs/cond-mat/9805244) · [Tan, Robertson and Czerwinski 2001](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/chi2001navtechs.doc) · [Haigh-Hutchinson, Real-Time Cameras excerpt](https://gamedeveloper.com/design/real-time-cameras---navigation-and-occlusion) · [Cinemachine Deoccluder](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineDeoccluder.html) · [Nesky, translated, part 1](https://habr.com/en/articles/272401/) and [part 2](https://habr.com/en/articles/272825/) · [Nesky, Game Developer](https://gamedeveloper.com/design/video-50-common-game-camera-mistakes----and-how-to-fix-them)

Games: [Pentiment's art, Game Developer](https://www.gamedeveloper.com/art/deep-dive-the-art-of-pentiment) · [Firewatch world, 80.lv](https://80.lv/articles/creating-the-world-of-firewatch) · [Designing Journey, Adventure Gamers](https://adventuregamers.com/article/designing_journey) · [Designing Journey, Game Watch](https://game.watch.impress.co.jp/docs/news/593897.html) · [Nava, Journey retrospective](https://mattnava.com/Journey-10th-Anniversary-Behind-the-Scenes-Retrospective) · [Kentucky Route Zero interview](https://funambulism.com/2013/07/23/interview-cardboard-computer-on-kentucky-route-zero/) · [The making of Assassin's Creed](https://www.timeextension.com/features/the-making-of-assassins-creed-ubisofts-original-open-world-epic) · [AC Unity crowds, Game Watch](https://game.watch.impress.co.jp/docs/news/20150307_691715.html) · [The AI of Hitman (2016)](https://www.gamedeveloper.com/design/the-ai-of-hitman-2016-) · [Seifert, Destructoid](https://www.destructoid.com/hitman-studio-just-wants-to-get-back-to-hitman/) · [Hitman as social spaces, Game Watch](https://game.watch.impress.co.jp/docs/news/1175738.html) · [BG3 cutout, 80.lv](https://80.lv/articles/artist-recreated-baldur-s-gate-3-occlusion-cutout-effect) · [BG3 Community Update 6](https://baldursgate3.game/news/community-update-6-multiplayer-cinematics_5) · [BG3 panel, PC Gamer via Yahoo](https://www.yahoo.com/entertainment/baldurs-gate-3-devs-considered-012944305.html) · [BG3 controls, Shacknews](https://www.shacknews.com/article/136508/pc-controller-buttons-baldurs-gate-3) · [BG3 perception, wiki](https://bg3.wiki/wiki/Passive_Perception) · [Vincke, Shacknews](https://shacknews.com/article/137186/larian-studios-ceo-interview-bg3-2023?amphtml=1) · [BG3 GDC 2024 sessions, GameAnim](https://www.gameanim.com/?p=121655) · [Disco Elysium, Can I Play That](https://caniplaythat.com/2020/07/27/indie-spotlight-disco-elysium/) · [Sasko on Witcher senses, TheGamer](https://www.thegamer.com/the-witcher-3-wild-hunt-cd-projekt-red-admits-it-overused-witcher-sense-detective-vision-mechanic-defense/) · [Design lessons from The Witcher 3](https://www.gamedeveloper.com/design/design-lessons-from-the-witcher-3) · [KCD2 talks, Game Developers Session 2024](https://2024.gdsession.com/index.php?action=kcd) · [KCD2 Hardcore mode, Deep Silver](https://www.deepsilver.com/games/kingdom-come-deliverance-ii/news/this-is-hardcore-adventuring-inside-a-brutal-new-bohemia) · [Vávra, 80.lv](https://80.lv/articles/kingdom-come-deliverance-an-interview-with-daniel-vavra) · [Warhorse, Press Start](https://press-start.com.au/features/2024/12/05/we-spoke-to-the-kingdom-come-deliverance-2-team-about-the-brutal-combat-and-living-world/) · [Pathologic 2, Ice-Pick Lodge](https://ice-pick.com/pathologic-2/) · [Pathologic 2, EGM](https://egmnow.com/a-russian-crucible-pathologic-2-and-the-problem-of-video-game-difficulty/) · [Pathologic plague, wiki](https://pathologic.wiki.gg/wiki/Plague) · [Persona 4, Siliconera](https://www.siliconera.com/behind-the-design-of-persona-4/) · [Hashino, Inverse](https://www.inverse.com/gaming/katsura-hashino-game-changers-persona-metaphor) · [Hosokawa, GameRevolution](https://www.gamerevolution.com/originals/556537-kazuki-hosokawa-judgment-interview-e3-2019) · [Nagoshi on Yakuza 6, GamingBolt](https://gamingbolt.com/ps4-exclusive-yakuza-6-wont-have-any-loading-screens-toshihiro-nagoshi-confirms) · [Barone, Kotaku](https://kotaku.com/the-past-present-and-future-of-stardew-valley-1766238624) · [Stardew schedules, wiki](https://wiki.stardewvalley.net/Modding:Schedule_data) · [Fox on Ghost of Tsushima, Press Start](https://press-start.com.au/features/2020/05/22/ghost-of-tsushima-interview-weapon-upgrades-crafting-length-waypoints-and-more/) · [RimWorld time, wiki](https://rimworldwiki.com/wiki/Time) · [Football Manager highlights, GGRecon](https://ggrecon.com/guides/football-manager-2024-change-highlights) · [Cities: Skylines II, Wikipedia](https://en.wikipedia.org/wiki/Cities:_Skylines_II) · [Barlog's single shot, VideoGamer](https://www.videogamer.com/?p=105432) · [Juicy Breakout](https://github.com/grapefrukt/juicy-breakout) · [Kelly on juice, Game Developer](https://gamedeveloper.com/design/video-indies-resist-the-urge-to-juice-it-or-lose-it-)

Guidance and attention: [BotW at CEDEC 2017, Famitsu](https://www.famitsu.com/news/201708/31140870.html) · [Nintendo Everything translation](http://nintendoeverything.com/nintendo-on-the-behind-the-scenes-creation-of-zelda-breath-of-the-wild/) · [Gigazine](https://gigazine.net/gsc_news/en/20171004-breath-of-the-wild-design-secret) · [Zelda Universe](https://zeldauniverse.net/2017/10/09/a-deep-dive-into-nintendos-development-of-breath-of-the-wild/) · [Schatz, environment language](https://80.lv/articles/defining-environment-language-for-video-games/) · [Uncharted 4's art, Game Informer](https://gameinformer.com/b/features/archive/2015/01/21/the-secret-depth-of-uncharted-4-s-art-design) · [Moving the sun, TheSixthAxis](https://www.thesixthaxis.com/2020/07/10/uncharted-4-last-of-us-part-ii-shift-the-sun-moon-guides/) · [Yang, How to light a level](https://www.blog.radiator.debacle.us/2018/03/gdc-2018-how-to-light-level-slides-and.html) · [Shaver's talks](https://davidshaver.net/speaking.html) · [Blow, PlayStation Blog](https://blog.playstation.com/?p=162465) · [The art of The Witness](https://www.gamedeveloper.com/design/-i-the-witness-i-artist-reminds-us-to-keep-it-simple-stupid) · [Smith on There Will Be Blood](https://www.davidbordwell.net/blog/2011/02/14/watching-you-watch-there-will-be-blood/) · [Gallup and colleagues 2012](https://kops.uni-konstanz.de/entities/publication/4a4d492d-963f-4c68-ab88-952c60e7e902/full) · [Su and Takahashi 2010](https://scitepress.org/PublishedPapers/2010/28257/pdf/index.html) · [Surrey on depth of field in games](https://www.ias.surrey.ac.uk/?p=7136) · [Bonawitz and colleagues 2011](https://cocosci.dreamhosters.com/Liz/Bonawitzetal11.pdf) · [Beachum on Outer Wilds](https://gamedeveloper.com/design/road-to-the-igf-alex-beachum-s-i-outer-wilds-i-) · [Ueda, glitterberri](https://glitterberri.com/ico/unused-dialogue-and-retranslation/) · [Weiser and Brown, Designing Calm Technology](https://calmtech.com/papers/designing-calm-technology)

Interface, accessibility and testing: [Nielsen, response times](https://www.nngroup.com/articles/response-times-3-important-limits/) · [Material motion tokens](https://github.com/material-components/material-components-android/blob/master/docs/theming/Motion.md) · [Xbox guideline 117](https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/117) · [Xbox guideline 107](https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/107) · [Ambinder, Valve's approach to playtesting](https://cdn.fastly.steamstatic.com/apps/valve/2009/GDC2009_ValvesApproachToPlaytesting.pdf) · [Birdwell, The Cabal](https://www.jmeiners.com/shamans/papers/art/half_life_design.pdf) · [Davis, Steury and Pagulayan 2005](https://gamestudies.org/0501/davis_steury_pagulayan) · [Halo 3 testing](https://www.neurosciencemarketing.com/?p=216) · [EA SEED, Gillberg and colleagues 2023](https://arxiv.org/abs/2307.11105v1)
