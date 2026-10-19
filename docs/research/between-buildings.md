# Between the buildings

The street, the square, the quay, the yard: how the space between buildings is generated so that it carries history and connects everything. Part of the Game Lab research.

## Rules from urbanism

**Life gathers where life already is.** Jan Gehl splits outdoor activity into necessary (errands), optional (only when the place is good) and social (which grows from the other two). Activity feeds itself: "Something happens because something happens because something happens." When the number of children doubled, play rose fourfold. People take the edges of a space first, facing the flow. *Rule:* traces of staying (worn seats, chairs set out, cigarette ends, a smoothed ledge) appear only where the engine records people staying, edges facing the flow first, and they grow faster than linearly with activity.

**People attract people.** William Whyte: "What attracts people most… is other people." Food draws people; steps get sat on if they don't block the way; blank walls kill street life. *Rule:* sittable edges next to food or a doorway collect wear and litter; blank fronts collect none.

**Movement comes first.** Bill Hillier's space syntax: how connected a street is predicts how many people walk it, and "movement attracts land use". *Rule:* wear, litter and sign density follow footfall per street segment, which the engine provides. The game never guesses footfall.

**Compose views as here and there.** Gordon Cullen's serial vision: a town is experienced as a series of reveals, an enclosed HERE with a glimpse of a THERE. *Rule:* staged scene views frame a near space (an arch, a gap between houses) with a partly hidden view beyond.

**Squares keep their centre free.** Camillo Sitte: monuments and kiosks stand at the edges; irregular squares show their history. *Rule:* irregularity comes from the plot history, never from noise.

**The city must read.** Kevin Lynch's five elements: paths, edges, districts, nodes, landmarks. *Rule:* the raised view is checked for all five. The quay is the obvious edge; landmarks stay few; each district gets a material signature from its history.

## The street has a diary

- Paving. Oslo adopted small cube setts in 1912; the arch pattern was the main town surface from about 1910 to 1950; asphalt replaced stone gradually after 1950. Every pipe or cable job leaves a straight patch of fresher asphalt that fades over the years and may later settle and crack.
- Street lamps. Gas from 1848 in Oslo, electric from 1890 (Hammerfest) and 1892 (Kristiania), then mercury (blue-green white), low-pressure sodium (almost pure orange), high-pressure sodium (golden), and now LED. Each lamp carries its era's fixture and light colour. A plausible 1989 mix is sodium on main roads and older lamps on side streets (not verified for Norway).
- Trams. Bergen ran trams 1897 to 1965 and Trondheim 1901 to 1988. A closed line leaves rails and patch strips.
- Phone kiosks. The red Norwegian kiosk from a 1932 competition, present in 1989, removed gradually from the 1990s.
- Trees. Each tree has a planting year; trunk size follows from age and crown from trunk, using growth curves like the USDA Urban Tree Database's. A tree planted in 1960 is big in 1989.

## Everything connects

Every element has a cause and a connection. Water runs roof → gutter → downpipe → drain, and downhill. Moss follows shade × wetness × years since cleaning, not the compass. Chimneys exist because of stoves. Lit signs need cables. Every door has a path to a street. A street lamp's colour depends on when it was installed. Renovation may spread between neighbours, though the evidence is mixed (Baltimore found an effect, Boston did not), so contagion is an engine decision; the game shows only the renovations and their dates.

## Desire paths

Helbing et al. (Nature, 1997) give a simple model: each footstep raises a patch of ground's "comfort", unused ground recovers over time, and walkers balance the straight line against nearby existing trails. One parameter decides whether people take direct routes or share a minimal network. About 15 passes make a trail visible. Run yearly on lawns, gravel and heath from the engine's trips, every worn path is a true fact.

## Clutter and set dressing

- No anonymous clutter. Harvey Smith and Matthias Worch: "Every anonymous environmental storytelling moment wastes the opportunity." Every prop traces back to an engine fact or habit.
- Clusters with rests between them. Night City's dressers found that too much density became noise, so clutter was grouped with gaps "where the eyes can rest". Overgrowth is the inverse of use: sparse where people pass, heavy where they don't.
- Junction detail from context. Townscaper decorates after the structure, based on the free space around each piece.
- Sparse beats dense from above. art of rally's flat, minimal assets read richly from a raised camera.

## Materials

Not every old building is timber. Material is chosen per volume from era, purpose, wealth and local rules, and each material ages its own way:
- Rules: after fires, towns required masonry in the centre (Stavanger from 1904), giving a brick belt inside the wooden town.
- Purpose: canneries purpose-built in brick from the late 1890s, with tall chimneys and painted logos; banks, churches and post offices in stone or brick; granite quay edges.
- Era: rendered concrete in 1930s functionalism; post-war concrete; oil-era concrete and glass.
- Wealth: a merchant's brick house beside a fisherman's timber one.
- Ageing: wood peels and gets repainted; brick takes soot and salt bloom; concrete streaks and spalls; render cracks and is patched in a slightly different colour.

## Street-layer cheat sheet

| Element | Era tells | Cause | Over time |
| --- | --- | --- | --- |
| Paving | Setts in arch pattern c.1910 to 1950; asphalt after 1950; patch strips | Paving programmes; utility works | Patches fade, settle, crack |
| Street lamp | Gas, incandescent, mercury, sodium, LED | Era and street class | Replaced by programme |
| Tram traces | Rails and patch strips | A line opened or closed | Paved over in patches |
| Phone kiosk | Red 1932 design | Telecom network | Fades, removed from the 1990s |
| Desire path | Bare strip across grass | Repeated shortcuts | Deepens with use, recovers without |
| Moss | Green on shaded, wet faces | Shade, drips, no cleaning | Spreads yearly; reset by cleaning |
| Empty lot | Willowherb, then willow scrub, then trees | Demolition or abandonment | Staged by years since disturbance |
| Street tree | Crown size from planting year | Planting programme | Grows on a curve |
| Staying traces | Worn edges, chairs, cigarette ends | Recorded stays | Grow with activity; vanish when the business closes |

## Sources

[Gehl, Life Between Buildings](https://ebooks.umu.ac.ug/librarian/books-file/Life%20Between%20Buildings_%20Using%20P%20-%20Jan%20Gehl.pdf) · [Whyte (PPS)](https://www.pps.org/article/wwhyte) · [Cullen, Concise Townscape](https://ebooks.umu.ac.ug/librarian/books-file/Concise%20Townscape%20-%20Gordon%20Cullen.pdf) · [Sitte](https://www.theamericanconservative.com/meet-the-austrian-who-invented-placemaking/) · [Hillier summary](https://theccd.org/spotlight-research/cities-as-movement-economies/) · [Helbing et al. 1997](https://ar5iv.labs.arxiv.org/html/cond-mat/9805158) · [Desire paths](https://en.wikipedia.org/wiki/Desire_path) · [SNL gatebelysning](https://snl.no/gatebelysning) · [SNL brolegging](https://snl.no/brolegging) · [Sodium lamps](https://en.wikipedia.org/wiki/Sodium-vapor_lamp) · [Norwegian tramways](https://en.wikipedia.org/wiki/List_of_town_tramway_systems_in_Norway) · [Telenor kiosks](https://www.telenor.com/who-we-are/history/an-architectural-icon/) · [Urban Tree Database](https://www.fs.usda.gov/rds/archive/catalog/RDS-2016-0005) · [Moss](https://www.mentalfloss.com/article/56243/does-moss-really-only-grow-north-side-trees) · [Boston Fed on renovation](https://www.bostonfed.org/publications/community-development-issue-briefs/2013/is-home-maintenance-contagious-evidence-from-boston.aspx) · [Smith & Worch](https://niemanstoryboard.org/2011/01/14/harvey-smith-on-environmental-storytelling-and-embedding-narrative/) · [Night City](https://80.lv/articles/interview-how-cyberpunk-2077-s-night-city-was-built-almost-entirely-by-hand/) · [Townscaper](https://www.gamedeveloper.com/game-platforms/how-townscaper-works-a-story-four-games-in-the-making) · [art of rally](https://jalopnik.com/how-a-small-change-in-camera-angle-completely-transform-1849152549)
