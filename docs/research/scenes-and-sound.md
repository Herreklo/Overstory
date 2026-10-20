# Scenes, venues, light and sound

How staged scenes, interiors, the venue ladder and sound are generated so they look designed and stay true. Part of the Game Lab research. Some items rest on general knowledge and are marked unverified.

## Interiors

**Rooms by importance.** Shadows of Doubt places rooms in order of importance (living room first, then bathroom), scoring each candidate spot on floor area, simple shape and windows. Rules control which rooms may connect; a bathroom gets one door; a hallway is added when the entrance is far from a corner, because "without them you tend to generate a bunch of rooms that are only ever accessed via each other." Our rooms derive from the facade grid, so windows and rooms always agree.

**Palettes matched to people.** Shadows of Doubt scores each interior palette on four axes (modern, clean, loud, warm or cold) and matches them to the resident: richer people get more modern decor, extroverts louder rooms. A separate dirt map shows neglect. Our version gives each room its own fit-out year, so a kitchen renovated in 1979 sits next to a 1950s parlour.

**Furniture that follows design rules.** Merrell et al. (2011) encode seven interior-design guidelines (clearance, circulation, pairs, conversation, balance, alignment, a focal point) and sample layouts fast; professional designers preferred the generated layouts in 4 of 5 rooms. Yu et al. (2011) learn the same from example rooms. Our version: a seeded optimiser using those terms, weighted by facts (taste picks the focal point, a record player or a TV; money sets how much there is), with priors learned from a few hand-made rooms per era and class. Language-model layout tools are non-deterministic and stay out of the game.

**Rooms reveal people.** Smith and Worch: the player infers the story from what sits together; environments reveal who lived there; "Players get value when they see that their acts are persistent in the world."

## The venue ladder

| Rung | Capacity | Light by era | Crowd | Sound | Outside |
| --- | --- | --- | --- | --- | --- |
| Pub back room | Under 350 (Music Venue Trust "small"), often far fewer | House tungsten, a few coloured PAR cans | Individuals, talking over the band | Dry room, bar chatter on top, small PA | A lane, harbour sounds, music leaking out |
| Local venue or club | 351 to 650 ("medium") | Bars of PAR cans, a followspot, smoke; a few moving lights from the late 1980s | Dense front, talkers at the back | Short reverb, crowd bed and close voices | A queue, taxis, posters |
| Bigger hall | 651 and up ("large"); about 1,000 to 3,000 (unverified) | Trusses, moving lights from the 1980s and 90s, haze to show the beams | Waves of reaction, chants | Long reverb, chants and applause layered | Tour bus, merchandise, police |
| Arena | About 10,000 to 20,000 (unverified) | Moving-light rigs from 1981; video screens from the early 1990s; giant LED walls from 1997 | A mass, a few hero fans | Huge reverb, crowd recorded at several sizes | Car parks, coaches, crowds streaming in |

Light history: Vari-Lite moving lights debuted on a Genesis tour in 1981 with 55 fixtures; the VL4, the first practical wash light, came in 1988; U2's PopMart tour (1997) had an LED screen about 50 m wide. Haze is what makes a big rig read: without it "the patterns created over and around the musicians would not be visible" (Moody and Dexter). A useful era tell from 1997: early moving-light users "flashed the lights up, down, and all around, simply because they could."

Escalation is a bundle: rig size, haze, video, transport and crowd together, not just a bigger room. Rock Band gated bigger venues by fans and transport (van, bus, jet); our facts already say who came.

## Staging and camera

- Kentucky Route Zero builds sets like plywood theatre flats: scene changes happen as walls "dissolve… and the lights drop"; framing is "preconceived, purposeful, and done with rigid restraint"; in one act the player chooses where to watch a performance from. *Take:* lights dropping as transitions, on-stage audiences, choosing your vantage point at a gig.
- The Virtual Cinematographer (He, Cohen & Salesin, 1996) encodes film idioms ("three actors conversing") as small state machines that choose shots and cuts and nudge actors into frame. This is the pattern for procedural but designed cameras: one idiom each for two people talking, a group, a performer and crowd, an entrance.
- Fixed cameras show "exactly what the developers wanted them to see", at the cost of player control.
- Versu (Evans & Short, 2014) models recurring social situations as practices: a dinner, a greeting, a negotiation, each with roles, expectations and suggested actions. Every agent keeps the final choice, and several practices can run at once. *Take:* the practice is the unit of a scene. Each practice (a rehearsal, a gig, an interview, a dinner) gets one staging idiom in the Virtual Cinematographer's sense, so a new kind of scene starts as a new practice and a new idiom.

## Light for mood

Pixar's colour scripts: Ralph Eggleston painted small pastels of every scene, and "the colors got more intense when the emotions were more intense." Our version: one value per scene from the facts (tension or warmth) drives colour strength, contrast and how hard the light is. Every light in a scene comes from a real source (a lamp, a window, a stage light), so the lighting is true by construction.

## Sound

**Soundscape.** R. Murray Schafer (1977): every place has keynote sounds (the background that defines it), signals (sounds you listen to) and soundmarks (unique to that place). A hi-fi soundscape lets single sounds stand out; a lo-fi one masks them. *Rule:* each place gets a keynote, a few signals and at most one soundmark. Over the decades the town drifts from hi-fi to lo-fi as traffic grows, so history is audible.

**Ambience systems.** Ghost of Tsushima's small audio team built ambience driven by time, weather and region for a world 14 times larger than their previous one. Cyberpunk 2077 used dynamic reverb and in-world radio.

**Crowds.** Planet Coaster builds crowd audio in three layers: a bed limited by distance, a quiet "pure mood" loop, and about ten close emitters on the nearest people; indoors the crowd drops and footsteps rise so it sounds hollow; reactions are rationed to avoid fatigue. FIFA uses separate layers rather than loops ("Loops aren't a compelling way for anybody to have an atmosphere"), reactions that depend on context, crowd recordings at several sizes, and ducking (applause ducks chants, chants duck the bed). Assassin's Creed Unity drew up to 10,000 crowd figures through tiers of detail.

## Pitfalls

- Interiors reached only through other rooms, furniture with no focal point, one palette for a whole life.
- Looping crowd chatter, reactions that ignore what happened, a rig that does too much for its era.
- Mood chosen by scene type instead of by facts, and staging that promises actions the game can't do.

## Sources

[Shadows of Doubt devblog 13](https://colepowered.com/shadows-of-doubt-devblog-13-creating-procedural-interiors/) · [Devblog 14](https://colepowered.com/?p=34717) · [Merrell et al. 2011](https://graphics.stanford.edu/projects/furniture/) · [Yu et al. 2011](https://ww3.math.ucla.edu/camreport/cam11-49.pdf) · [Holodeck](https://export.arxiv.org/abs/2312.09067) · [Smith & Worch](https://gdcvault.com/play/1012647/What-Happened-Here-Environmental) · [Music Venue Trust definition](https://www.musicvenuetrust.com/resources/grassroots-music-venue-gmvs-definition/) · [History of moving lights](https://blog.etcconnect.com/2020/09/history-of-moving-lights) · [PAR cans](https://www.livedesignonline.com/lighting/monday-musings-parcans) · [Rock lighting history](https://www.livedesignonline.com/mag/all-glitters-looking-ever-changing-face-rock-and-roll) · [PopMart](https://en.wikipedia.org/wiki/PopMart_Tour) · [Concert Lighting](https://oreilly.com/library/view/concert-lighting-3rd/9780240806891/Text/028_9781136082696_chapter19.html) · [Rock Band](https://en.wikipedia.org/wiki/Rock_Band_(video_game)) · [Kentucky Route Zero scenography](https://gdcvault.com/play/1020596/Scenography-of-Kentucky-Route) · [Theatrical spaces](https://bulletpointsmonthly.com/2020/03/18/theatrical-spaces) · [Fixed cameras](https://unwinnable.com/?p=60323) · [Virtual Cinematographer](https://www.microsoft.com/en-us/research/?p=150986) · [Versu](https://cs.uky.edu/~sgware/reading/papers/evans2014versu.pdf) · [Pixar colour scripts](https://www.moma.org/audio/playlist/192/2581) · [Soundscape](https://en.wikipedia.org/wiki/Soundscape) · [Ghost of Tsushima ambience](https://gdcvault.com/play/1026976/Big-World-Small-Team-Designing) · [Night City audio](https://gdcvault.com/play/1029310/Sounds-of-Night-City-Audio) · [AC Unity crowds](https://gdcvault.com/play/1022141/Massive-Crowd-on-Assassin-s) · [Planet Coaster crowd audio](https://audiokinetic.com/en/planet-coaster-crowd-audio-additional-layers-part-3) · [FIFA crowds](https://blog.soundparticles.com/how-paul-boechler-created-live-stadium-crowds-from-fifa-recordings)
