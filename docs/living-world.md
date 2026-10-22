# The living world

Status: direction, not yet tested. How the game shows a world that the Understory engine simulates.

## In short

- **LW1** The engine runs as its own process; player acts are commands it accepts or refuses; a save holds engine and ruleset versions, checkpoints and commands. Evidence: `facts-contract.md`. Reopens: none named.
- **LW2** Two clocks: the engine's months; scenes' minutes and hours, scheduled from facts, committing back only consequential outcomes. Who owns what across a month boundary is open. Evidence: D12.6 (`research/building-blocks-decisions.md`). Reopens: settled with the engine, plan step 8.
- **LW3** A building and a business are separate; the screen never confuses facts, traces, fallible records, beliefs and discoveries; control, influence and knowledge are dials per game, role and scene. Evidence: `research/interface-and-inspection.md`. Reopens: none named.
- **LW4** Scenes are written, not voiced; voices only as the town's murmur. Motion: free libraries (MPFB's rig, CMU, 100STYLE; Mixamo once its terms are checked), hand-edited against video, from footage only where licensed; no motion-capture sessions. Øystein's (22 October). Procedural layers follow state, traits only what strangers can read. Evidence: `research/behaviour-on-screen.md`. Reopens: smooth or stepped, judged on frames.
- **LW5** People are blockout figures until their own research step settles how they are drawn; MPFB and painted faces are direction until then (disputed). Øystein's. Evidence: `plan.md`, Leaner 7. Reopens: that step.

## The loop

People create people. People create places. Places create memories and events. Memories and events change people. Every step is decided by the engine, deterministic and explainable, so the world writes its own history and can say why.

Two things keep the loop alive:
- **Something always pulls back.** A popular place gets crowded, its owner ages, fashions fade. Without it, every city ends up the same.
- **Deterministic, not predictable.** The same seed gives the same world, but chance stays inside the loop, so people still surprise.

## Who does what

- **The engine decides.** Who people are, what they do, which places exist, what happened.
- **Unity draws.** It reads the engine's facts and shows them. It never invents one.
- **Blender builds the parts.** Generators make families of kit pieces before the game ships. Nothing is modelled at runtime.

The engine runs beside Unity as its own process (LW1). Player actions go to the engine as commands it can accept or refuse; what it accepts becomes events. A save holds the engine and ruleset version, checkpoints and the player's commands, so a save survives changes to the rules.

**Two clocks** (LW2). The engine moves social life month by month. Scenes run in minutes and hours: who walks where, who is in the bar tonight, the weather this evening. Scene detail is scheduled deterministically from the engine's facts; only consequential outcomes (a promise, a meeting, a booking) are committed back as events. Which side owns what, and what happens when a scene crosses a month boundary, is an open design question to settle with the engine project.

## Places

Each place has three layers:
1. **What it is** (engine): kind, owner, crowd, founding year, condition, history.
2. **What it is called** (words): name, sign, menu, seeded from the place's id so they never change between sessions.
3. **What it looks like** (Unity): assembled from kit pieces, slot by slot, each slot driven by an engine fact.

**A building and a business are separate.** The building has an era, extensions in later eras and a condition. A business occupies it for a time. When the business closes, the building stays: boarded up, then reopened as something else, with the old name fading above the new sign. Streets look varied because they are layers of history.

**Variety comes from combination and history,** not from more models: a few hundred pieces give hundreds of thousands of buildings. Every visual difference carries something true (era, wealth, wear, the owner's character), so the player can read places the way they read people. `blender/tools/trace_check.py` checks the plan side of this: every part a plan shows names the diary event that put it there.

## What the player can know (LW3)

**The record has four layers,** and the screen never confuses them:
1. **Facts:** what happened, decided by the engine.
2. **Traces and records.** Traces are what happening leaves behind without meaning to: wear, a ghost sign, a later window. They cannot lie. Records are made to tell: a gig poster, a newspaper report, a deed, a phone-book entry, a shop sign, a photograph. Each has a maker, a date and a purpose, and can be wrong, partial or out of date: the sign says "Bakery" over a shop that closed two years ago. Records age like any surface: posters paste over posters, and the wall by a venue becomes a coat stack of its gigs.
3. **Beliefs:** what each person thinks happened, from the engine's accounts.
4. **Discoveries:** what the player has found, and where.

**Three dials, set per game, role and scene:** control (what the player commands), influence (what they can try to change, which the engine accepts or refuses) and knowledge (what they are allowed to see). A manager, a detective and an observer in the same town differ mostly in knowledge; the world under them is the same.

## Two kinds of view

- **The world view:** an illustrated map at city scale, showing only what the player knows; a live 3D neighbourhood seen from above, where people move and places visibly change.
- **Scene views:** where things happen: a conversation, a gig, a match, a lab, a forest. Scenes are not only interiors: a forest clearing, a farmyard, a quay at night, a beach bonfire, a boat on the bay, a bunker on the ridge are scenes as much as a kitchen or a bar. Most are walkable point-and-click spaces, bounded, with a staged camera, composed and lit like a film set. Moving between views is a cut or a short move through a doorway.

Each kind of scene is a social practice: a rehearsal, a dinner, a gig, an interview, each with roles and expectations, while every person in it still makes their own choices. The choices are the engine's; each practice gets a staging idiom from Overstory (`docs/research/scenes-and-sound.md`). Whether the engine or the scene holds the practice itself belongs to the two-clocks question above. Each kind of scene is also a small production of its own. Cheap ones come first (a conversation in a bar); expensive ones (a full match) come when a game needs them.

## People (LW5)

**Until their own step, people are blockout figures** (Øystein: people are their own research project, with great care): grey bodies with readable silhouettes and simple motion. Gameplay and ideas are tested with them early, as in normal game development, before everything looks finished (Øystein, 22 October). How people are drawn and stylised is not settled by any shortcut; it is studied and tested in its own step, and what follows is the direction until then.

**One good base, many parameters.** One free base body and skeleton (MPFB, built on in-house; no commissions), its machinery kept and its surface replaced (`docs/research/characters.md`). Everything else is generated:
- **Body:** height, build, posture and ageing set from the person's own values, inherited from parents, so children look like their parents.
- **Clothes:** a few modular pieces per slot, chosen by money, work, era and taste. Clothes are evidence the player learns to read.
- **Faces:** painted rather than rigged; expressions are swapped textures the engine's emotional state can choose.
- **Voices** (LW4): scenes are written, not voiced (Øystein, 22 October). Faces carry expression and never lip-sync. Voices are heard only as the town's murmur, never as words.

**Animation:** a small library on the shared skeleton, with procedural layers on top: how upright someone stands, how big their gestures are, how much they fidget, where they look, how close they stand. The layers are driven mostly by the person's state now (tired, hurried, carrying, grieving). Traits take only the share strangers can truly read, since motion mapped straight from a trait hands the player a verdict (`docs/research/behaviour-on-screen.md`). Few animations, thousands of distinct people, and posture becomes evidence.

The motion comes from free libraries: MPFB's game rig, CMU, 100STYLE, and Mixamo once its terms are checked. It is edited by hand against video of people doing the same thing. There are no motion-capture sessions (Øystein, 22 October: there are thousands of videos of people doing things). Videos are studied as reference; motion is lifted from footage only where its licence allows. Whether people move smoothly or stepped is judged on frames. The research favours smooth motion with the style in the poses (`docs/research/animation-and-motion.md`). Scenes are staged like theatre, so less walking needs animating.

## Crowds

**Simulate the few, show the many, and let film language do the rest.**
- **The crowd is the simulation's output.** The engine knows who came and why. People who matter are full characters; the rest are cheap instances that become full characters when the camera comes close.
- **The crowd is one organism.** One signal from the engine (how the gig is going) ripples through it, and the player reads the night from the crowd.
- **Moments, not minutes.** The engine picks the moments that matter; the scene stages them as short framed vignettes.
- **Darkness and focus hide what is not there.** Silhouettes against stage light, players lost in depth of field under floodlights.
- **Sound carries half the scale.**
- **Only the people nearest the player give way.**

## Technology

Unity 6 with URP. The look lives in our own shading model: light ramps, gradient fog by distance, a ground-bounce colour and a colour script per time of day and weather. It does not depend on true real-time global illumination; generated places change, so nothing is baked.
