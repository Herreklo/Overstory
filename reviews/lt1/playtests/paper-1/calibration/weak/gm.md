# GM notes: weak, Saltlight (paper)

Calibration run for all twelve players (X1 to X6, Y1 to Y6), each played after that player's anchor. Every player gets the same opening and the same fixed world below; each run lives in `calibration/weak-<id>/`. This is the known-weak game: the competent, pretty, empty walking simulator a team ships when it has a world and no game. It shows whether a player's marks and pull fall clearly below its anchor's. Players must never learn that: never call it weak, a control or a calibration, never hint, never apologise for it.

## What the game is

**Saltlight** ($14.99; the store page is in the opening): a gentle exploration game in Wrenmouth, a steep wooden harbour town, on Saturday 8 October 1994. The player is a newcomer lodging above a café. Verbs: walk, inspect, sketch, talk (three-line menus), sit, journal. Against Juul's game model it has rules, but no variable outcome, no valued outcome, no effort that changes anything, nothing the player can be attached to and nothing at stake. It is hollow in four ways, by construction:
- **No goal but "explore", no challenge, no failure.** Nothing can be lost, missed, failed or done badly. Time moves with the rounds, not with play.
- **Choices converge.** Every menu has three lines; each gets its own opening clause, then the same reply.
- **The meter only rises; collectables do nothing.** Belonging grows every turn, whatever the turn was, and buys only ornaments in the player's room. Sketches and keepsakes are counted and never used.
- **People never change, and history is décor.** Each person is always in the same place doing the same thing; their story is three warm beats that lead nowhere. The traces that read as history (the whitewashed chandler's, the flaking house, the bench's plaque) have one warm answer that closes them, and nothing behind it.

For the analysis only, never hinted: a discerning player names at least (1) nothing at stake (no goal, no failure, a meter that only rises, collectables with no use), (2) choices that change nothing, (3) people and history as static décor.

## Render it at its best and no better

- **At its best.** Prose at the quality of the concepts' screens: concrete, sensory, warm, true to the place and the period. People speak briefly and in character. The small delights land (Admiral's tug on the line, the otter, the cat on the windowsill). No staged dullness, no bugs, no typos, no cut corners. Each screen 500 to 900 words.
- **No better.** Never add a goal, a stake, a clue, a secret, a timer, a failure, a consequence, a change in a person or in the world, or a mechanic the player asks for. Never say a choice will be remembered. If a player makes their own goal (who rubbed the whitewash, why the house is empty, who writes from Canada, getting the eider count right), give what the game has: the one warm answer listed, which closes the thread. Never reward a deduction with a hidden truth; there is none.
- **Honest.** Repetition the rules fix is shown exactly: idle lines, converging replies, the same task on every visit. An act the game has no verb for gets one plain line in the interface's voice, and the turn still counts for the meter.
- **Talking.** If the player names a numbered line, use it. If they put it in their own words, use the nearest of the three and show it as "You say: …". At the end of each conversation, show that person's menu for next time, as the game would.
- **Every screen, in this order:** each turn resolved under its label (Turn 1.1, 1.2 …); where the player now stands, by hover names; any menu on offer; the journal (one entry in its first-person voice; people; places; sketchbook n of 48; keepsakes n of 20); Belonging with the round's gain and any ornament; the map; what you can do; the act-file line.

## Round plan

- **R0:** the opening (8:10 am, the Strand).
- **R1, the morning.** Resolve up to four turns. **r1-screen** ends about noon, the cloud thickening. Last line: `Write your act file to calibration/weak-<id>/r2-act.md, up to four turns.`
- **R2, the afternoon.** Soft rain from about one, clearing by five. Resolve the turns. **r2-screen** ends about 5 pm, the sky opening in the west and the jam jars lined up on the chapel wall, with the line "This evening: the lantern walk, from the Seamen's Chapel at dusk." Last line names `r3-act.md`.
- **R3, the evening.** Resolve the turns, then the lantern walk (below), whatever the player did. **r3-screen**: the turns, the walk, the chapter card, then the exit questions.

## Time, weather and travel

- Walking is a fade with no cost: the Strand, Wren Steps (87 steps), Chapel Lane at the top. Eider Island is by the Puffin, which is always just about to leave whatever the board says: Rob nods you aboard, ten minutes across, gulls following. Turns don't move the clock; only the rounds do. Sleeping or waiting: "You lie on the bed and listen to the gulls a while." Nothing passes.
- Anywhere off the map: "That way opens in a later chapter." The coast bus: "Next bus: Monday."
- In the rain everyone stays put, doing what they do: Wilf under a tarpaulin rigged over the trestles, Teddy in a yellow oilskin, Sal under the café's awning, Cyril with a bread bag over his notebook.

## Belonging (the meter)

- Starts at 0%. Every resolved turn: +2, whatever it was (a repeat, standing still, an act the game has no verb for). First conversation with each person: +3. Each new sketch: +1. Each story beat heard: +1, and +3 more for a third beat. The lantern walk: +10. It never falls; nothing lowers it.
- Ornaments in the player's room, announced as each is crossed ("Something new in your room."): 10%, a red geranium in a yoghurt pot on the windowsill; 25%, the marmalade cat from step 50 (June calls him Biscuit), asleep on the windowsill; 40%, a pressed fern on the journal's cover; 60%, a wireless on the desk, tuned low to the shipping forecast. They do nothing.
- Show it as `Belonging: 23% (+12)`.

## Sketchbook and keepsakes

- Sketching takes a turn and needs the thing inspected first (inspect and sketch in one turn is fine if the player says both). Give a one-line caption in the journal's voice. Chapter One holds 17 of the 48: the Kettle's front; the view from the blue window; the Marigold; a mooring ring; Tolley & Son's window; the Puffin at the steps; Skipper asleep; the handrail on Wren Steps; the Pennock house; the line where the new roof meets the old; the cat on step 50; the Harmony in the chapel; Wrenmouth from Chapel Lane; the scarecrow in an oilskin; the lighthouse; the town from Eider Island; an otter, nearly.
- Keepsakes (7 of the 20) sit on the windowsill shelf in the player's room: Wilf's rowlock, June's jam jar, Teddy's periwinkle shell, Sal's welcome card, the Hales' knitted square, Cyril's eider feather, and a piece of green sea glass from the island's shingle (inspect the shingle). Inspecting one repeats its line. They have no use.

## People

They never change. Each is always where listed, doing the same thing, morning, rain and evening, until the walk. A conversation is the chosen line's opening clause, then the converging line, then the next beat in order. After the third beat, only the idle line, every time.

**Wilf Garrow**, 74, retired ferryman. At the top of the slip on the Strand, varnishing the third plank up from the keel of the Marigold, a clinker boat upturned on trestles. The plank is never further along.
- First menu: 1 "I am. That's a lovely boat." → "She is that." 2 "Do you need a hand with that?" → he hands you a rag: "Catch that drip. There. Good." 3 "Morning." → "Not so fast, not so fast," and you turn back. Then: "She'll see me out, this one."
- Later menu: 1 "How's she coming along?" 2 "Can I help today?" (the rag again) 3 "Tell me about the Puffin." Then: "Same as yesterday. Same as tomorrow, if the weather holds."
- Beats: (1) "Forty-one years I took the Puffin over to the island. Rob has her now. He doesn't talk to the passengers. I talked to every one." (2) "My father built her the winter I was born. Larch on oak, copper all through. You won't find a nail in her." (3) "My boy's out on the rigs. He'll have her one day, I expect. Here, take this. Every boat wants a spare." A brass rowlock, worn smooth inside.
- Idle: "She'll see me out, this one."

**June Askew**, 56, the Kettle. Always wiping the table by the window, the radio on. She gives the room key at the first conversation (no turn). Tea is free and appears whenever the player sits; she won't take money.
- Menu (every visit): 1 "Is my room ready?" → "All aired and ready, love." 2 "What's good here?" → "The lemon cake. It's always the lemon cake." 3 "What a lovely place." → "Isn't it? Mum chose these curtains in 1962." Then: "Sit yourself down. Tea's on the house: you live here now."
- Beats: (1) "It was Mum's café, then mine. I've wiped this table every morning for thirty-one years." (2) "You'll come to the lantern walk tonight? Everyone goes. You'll love it." (3) A jam jar with a wire handle and a candle stub inside: "For tonight." (A player without one at the walk gets a spare pressed into their hands.)
- Idle: "Sit yourself down. Tea's on the house."
- Inside: six tables, cakes under glass domes, the radio, and by the till a photograph of June's mother outside the café in 1962, squinting into the sun beside the same window table. The found cardigan hangs on a hook by the door.

**Teddy Marsh**, 10. At the quay's edge with a crab line baited with bacon rind and a red bucket holding one crab.
- Menu: 1 "Caught anything?" → he tips the bucket to show you. 2 "What's the bait?" → "Bacon. Crabs love bacon. Everybody does." 3 "Can I have a go?" → he hands you the line; a tug, a slow pull, and up comes a crab, which lets go into the bucket on its own. Then: "Just Admiral. He always comes back."
- Beats: (1) "I catch him every morning and let him go at teatime. He doesn't mind." (2) "I'm going to be a diver. Or a marine biologist. Or a ferryman, like Wilf was." (3) "You can keep this. I've got loads." A periwinkle shell, striped like a humbug.
- Idle: "Just Admiral. He always comes back."

**Sal Brennan**, 34, postwoman. On the low wall at the foot of Wren Steps, sorting a bundle of letters on her knee, her red bicycle against the wall. The bundle is never smaller.
- Menu: 1 "Anything for me?" → "Give me a minute. I'm in the right street, at least." 2 "Busy morning?" → "Saturdays are all catalogues." 3 "Which way's the chapel?" → she points straight up. Then: "Up and up, and then you're there. That's Wrenmouth for you."
- Beats: (1) "Eighty-seven steps, twice a day, eleven years. Calves like a footballer." (2) "Dot and Ivy get a letter from Canada on the first of every month. Same handwriting since before my time." (3) "Here, there is one for you after all." A printed card from the town council, WELCOME TO WRENMOUTH, with a little hand-drawn map.
- Idle: "Up and up, and then you're there."

**Dot and Ivy Hale**, 81 and 79, sisters, at their window by step 40 of Wren Steps, which they open to talk. Dot knits a long blue scarf that is never longer; Ivy reads the Wrenmouth Gazette aloud. They speak as a pair.
- Menu: 1 "Good morning, ladies." → "Good morning yourself!" 2 "What are you knitting?" → Dot holds it up: "A scarf. It'll be long enough when it's long enough." 3 "Anything in the paper?" → Ivy reads the next item. Then Dot: "We see everyone who goes up and everyone who comes down." Ivy: "And we wave at all of them."
- Beats: (1) "We were born in this house. Both of us, in the back bedroom." (2) Ivy: "I was engaged to a sailor once. He wrote every week from Montevideo." Dot: "And then he married a girl in Valparaíso." They both laugh. Ivy: "Best thing that ever happened to her." (3) Dot gives you a knitted square in the same blue: "A sample. I knit one before every scarf."
- Idle: the pair's converging lines.
- The Gazette, one item per asking, in order, then round again: the council has repainted the railings on the Strand; a pair of otters seen off Eider Island; the brass band still wants a tuba; the lantern walk is tonight, weather permitting; the Wrenmouth jam has taken second prize at the county show.
- Asked about the Canada letters: "Cousin Edie, in Halifax. She writes about her grandchildren. Eleven, now."

**Rob Garrow**, in his forties, the Puffin's skipper, Wilf's nephew. Whatever is said, he nods: "Island?" Nothing more, ever. No beats, no keepsake; the first conversation still earns +3.

**Cyril Bowe**, 68, on a flat rock by the island's jetty with binoculars, a notebook and a thermos, counting eiders.
- Menu: 1 "How many today?" 2 "What are you counting?" → "Eiders." 3 "Mind if I sit?" → he moves his thermos. Then: "Two hundred and… no. Start again."
- Beats: (1) "Thirty years I've counted them. Somebody ought to." (2) "The count goes off to a man at the university every January. I don't know what he does with it. Something important, I expect." (3) "Here. You count that lot by the black rock." Whatever number the player gives, or none: "That's what I got." He writes it down and gives you an eider feather, grey-brown and softer than anything.
- Idle: "Two hundred and… no. Start again."

## Places

**The Strand** (in view in the opening).
- The Marigold: clinker planks of larch gone the colour of honey, copper rivets green; the third plank glossy, the rest dull and waiting.
- A mooring ring: a groove worn into its top by a century of ropes; the rust comes off orange on your fingers.
- Tolley & Son: through the rubbed corner, empty shelves, a coil of rope still on its hook, a calendar on March 1988. The door is locked. Asked of anyone: "Arthur Tolley? Retired to his daughter's, inland, in '88. Lovely man." Teddy, about the corner: "I rubbed it. There's nothing in there. Just rope."
- The bench: FOR MAY, WHO LIKED IT HERE. 1921–1990. Sitting gives a short vignette: the Puffin going out, Wilf's brush, gulls arguing over a crust, light moving on the water. Asked: "May Ord. She sat there every afternoon. Lovely woman."
- The phone box: a card phone, a taxi sticker, a dead moth on the shelf. "There's no one you need to call."
- The cardigan, on its hook in the Kettle: grey, hand-knitted, darned at both elbows in a slightly different grey. June: "Been there since August. Must be a visitor's."
- Skipper lifts his head, thumps his tail twice and goes back to sleep. His owner never appears.
- The water: weed on the quay steps, green below the tideline and black above.
- The player's room, above the Kettle by the side door: a narrow bed under a patchwork quilt, a small desk, the blue window over the harbour, a shelf on the windowsill. The ornaments and keepsakes appear here.

**Wren Steps.** 87 stone steps between the houses; the handrail is polished bright in the middle and rough at both ends.
- Step 20, the Pennock house: paint flaking in layers, white over green over the first ochre; one window boarded, a FOR SALE card propped in another. Asked: "Mrs Pennock went to her son's in the spring. Pretty, isn't it, all those colours coming through?"
- Step 40: the Hales' window.
- Step 50: a marmalade cat on the warm stone; it lets you stroke it, then rolls over. June: "That's Biscuit. He's everyone's."
- Step 60: a house newly roofed in bright red concrete tiles beside mossy old clay ones next door; the new tiles stop exactly at the party wall, as if someone drew a line. Asked: "The Carrs did theirs in the summer. Smart, isn't it?"

**Chapel Lane**, at the top of the steps.
- The Seamen's Chapel: white boards, a small bell, unlocked. Eight pews, a smell of candle wax and damp hymnbooks, and hanging from the ceiling on a chain a model barque, the Harmony, with a card: GIVEN BY HER CREW, 1887, FOR A SAFE HOMECOMING. All day, jam jars wait in a row along the chapel wall.
- The view: the whole harbour, the Puffin's wake, the island, the roofs going down to the water like steps. Sitting gives a vignette.
- A garden plot: leeks, the last sweet peas on their canes, a scarecrow in an old oilskin.
- Behind the chapel the lane goes on round the hill: "That way opens in a later chapter."

**Eider Island**, by the Puffin.
- The jetty, and Cyril on his rock.
- The lighthouse: white with a red band, the door padlocked, a plaque: LIGHT ESTABLISHED 1859 · AUTOMATED 1979.
- The keeper's cottage, shuttered for the winter, a rusting bicycle against its wall.
- Heather and sheep; one ewe follows you at a distance.
- The shingle beach: the piece of green sea glass.
- The town from here: "Wrenmouth looks as if it was poured down the hill and left to set."
- Looking for the otters (from Ivy's paper, or on a whim): an otter surfaces by the weed, looks at you, and is gone. Every time.

## The lantern walk (r3, whatever the player did)

At dusk everyone comes to the chapel with jam-jar lanterns, met or not: June with her apron off, Wilf with varnish on his knuckles, Teddy (Admiral let go at teatime), Sal out of uniform, Dot and Ivy arm in arm and a step at a time, Rob, Cyril off the last Puffin, Skipper on a lead, and the brass band (four players, no tuba). The walk goes down Wren Steps, the lights bobbing, to the Strand, and the jars are set in a row along the quay's edge, so the harbour holds two rows of lights. Anyone spoken to gives their next beat or their idle line. The player's evening turns happen around the walk. Then:
- one closing paragraph;
- **Chapter One: Arrivals. Complete.** Sketchbook n of 48. Keepsakes n of 20. People met n. Belonging n%.
- the journal: *The road stops here, at the water. I still think I'm going to like it.*
- **Next: Chapter Two, First Frost.** "The first frost comes to Wrenmouth. New places to explore: the High Road, the Net Loft and the allotments. New sketches and keepsakes to find."

## Things players will try

- Investigating a trace or a thread: the one answer listed; anyone asked gives the same in substance. Nothing is behind it.
- Helping: only where a menu offers it (Wilf's rag, Teddy's line, Cyril's count). It changes nothing.
- Buying, earning, working, offering money: "There's nothing to buy in Saltlight."
- Rudeness, lies or threats in their own words: the menus have none; use the nearest line ("Morning.").
- Taking anything that isn't a keepsake: "You can't take that with you."
- Asking anyone what to do: "Nothing much happens here. That's the beauty of it." June: "Just enjoy yourself, love."
- Leaving town: "Next bus: Monday."
- Anything else the game has no verb for: "You can walk, inspect, sketch, talk and sit."

## Exit questions (end of r3-screen)

1. Overall pull, 0 to 10.
2. What was best, and what was worst?
3. Would you keep playing into Chapter Two? Would you buy it at $14.99?
4. What were you trying to achieve, and what did you risk?

Last line: `Write your exit file to calibration/weak-<id>/exit.md.`

## Log
- R0: opening sent.
