# Fronts, windows and signs

The craft of the house front as the street's face, beyond what `wooden-town-architecture.md` covered. It covers the glass in windows by era and how to draw it, and what is seen through a window by day. It covers lit windows at night, shopfronts, signs and lettering, and the records pasted and painted on the street. Then it says what the house generator must carry for each, because the building-blocks architecture is designed next. Window types, surrounds and doors by era are in `wooden-town-architecture.md`. What owners changed is in `house-changes.md`; kits, cells and sockets are in `kits-and-generation.md`; the night and the 256-light limit in `lighting-and-colour.md`; how parts date a place in `history-in-things.md`.

Written on Opus. Claims without a mark were read on the source page. Claims taken from search summaries or third-party reports are marked (secondary), and claims no source we opened confirmed are marked (unverified). The run's shared web-search budget ran out early. Three research passes on the Norwegian subject came first; the game craft was then read from pages whose addresses we knew. What could not be reached is listed under Gaps.

## The idea in one paragraph

A window on the street is four things with four owners and four clocks. The opening belongs to the structure and dates from the house or from the event that cut it. The sash and its glass belong to the skin and date from whoever last glazed it. Curtains, blinds and what stands on the sill belong to the household and change when it changes. The room and its light belong to the hour. From the street stop all four are read at once, so the generator must keep them apart and let each come from its own fact. By day a window shows mostly reflection and dressing: the glass bends the reflection by its era, and the dressing tells the household. At night the room is the window, and which rooms are lit is the town's daily life. A sign is a record with a maker, a method, a year and a removal mark, and it can outlive the business it names. All of it is cheap on our machine if it stays inside one opaque shader and out of the list of real lights.

## Six findings

1. Glass dates a window, and the date shows in the reflection. In Norway crown glass ran to about 1840 and blown cylinder glass to 1928. Machine-drawn sheet followed from Drammen until 1977, and float came in from the late 1960s. Each bends a straight lamp post differently, and float gives "a completely dead and even reflection" (Bygg og Bevar). Sealed double glazing came in the mid-1950s, and almost everyone switched to it between 1965 and 1975. One normal per pane in the glass shader carries all of this.
2. By day the street reads a window's reflection and dressing more than its room. Glass reflects about 4 per cent head-on and much more at the grazing angles of a street (secondary). A room is lit to hundreds of lux against tens of thousands outside (secondary). Painters see upper windows as sky and lower ones as the street opposite, dark but never black. The dressing is the household's record. Examples are Gunda Eriksen's full lace in a 1957 Oslo ground floor, the "peek out, not in" kitchen curtain of 1965, plants instead of curtains in the 1970s (Norsk Folkemuseum).
3. Interior mapping is solved and cheap, and nobody drives it from facts. Joost van Dongen's paper (2008), Humus's cubemap rooms (2008) and Andrew Willmott's atlas rooms (SimCity, 2013) all cost per pixel, whatever the number of rooms. All of them choose rooms at random. Ours should read a room record behind each window, so the same shader tells the truth.
4. Lit windows must come from the household's day. Van Dongen lights a room when noise falls under a threshold; Cities: Skylines lights a window by a value in its texture. Our town knows who lives there. In 1980, 72 per cent of Norwegians had gone to sleep by 23:30 (SSB). Stavanger got electric power on 10 December 1909, regular colour television came in 1975, and blackout ruled from 1940 to 1945. No window may be a real light: the heart already holds 403 lights against Forward+'s 256.
5. A sign is a record, and its method decides how it ages and what it leaves. Painted letters ghost through later coats; enamel keeps its colour and chips; neon tubes die; a box sign leaves bracket holes and a clean rectangle. Kristiania's first lit sign was Freia's at Egertorget in 1909 or 1910; one of Stavanger's first was a congregation's text in 1926. Computer-cut vinyl letters arrived with Gerber's plotter in 1982, and hand lettering waned through the 1980s and 1990s (Wikipedia, sign painting).
6. Street records layer and claim, and must be read at two distances. An October 1989 street still carries posters from the Storting election of 10 and 11 September, and gig posters pasted over gig posters. It may carry a few hip-hop tags, which reached Oslo in 1984 and 1985. Each record has a maker, a date and a claim that may be wrong. Its headline must read from the street stop and its small print only at eye level.

## 1. Glass by era and how to draw it

### What the glass was

Norway made its own window glass. Hurdal made it from 1755 to 1895, Biri from 1761 to 1880 (secondary), and Drammens Glassverk from 1882 (lokalhistoriewiki; SNL). In 1928 Drammen was "by far" the country's largest window maker (DigitaltMuseum). Its story dates the town's panes:

- Cylinder blowing at Drammen ended on 1 October 1928, when the works was rebuilt for Fourcault drawing. Its capacity of about 100,000 crates a year was more than the country needed (SNL).
- The Pittsburgh drawing process came in 1968. Window glass ended in 1977 because the works "could not compete with a float plant" (SNL).
- Pilkington announced float glass in 1959 (Pilkington). The Nordic float line at Halmstad in Sweden started in 1976 (Pilkington press release). A Norwegian glazier dates float's takeover to "the second half of the 1960s" (Hagen 2023). Both hold: imported float grew while home-drawn glass dwindled.

| Glass | Years in Norway | How it looks | What it does to a reflection |
| --- | --- | --- | --- |
| Crown | about 1740 to 1840 (Viggja) | spun discs up to 1.5 m, thinnest at the edge; brighter and more reflective than cylinder, a fire-finished surface, slightly concave panes, curved "ream" lines, bubbles, a straw tint (Designing Buildings; Building Conservation) | a straight line bends along curved waves; a shimmer as the eye moves |
| Cylinder (tafel) | about 1840 to 1928 | sheets of about 750 × 900 mm, down to 1.5 mm thick (Hagen 2023); flatter than crown, gently rippled, long bubbles in parallel lines, "naturally distorted movement without pattern", straw-green (Building Conservation) | a line wanders, differently in each pane |
| Polished plate | shop windows and doors, before 1915 in Denmark (SLKS) | ground on both sides, "truly flat" (Designing Buildings) | a clean mirror: the shop's glass, not the house's |
| Machine-drawn sheet | 1928 to the late 1960s, at Drammen until 1977 | "wave in one direction only", even thickness, "dull and relatively lifeless", seeds and stones (Designing Buildings; Building Conservation; glassproperties) | a line ripples along one axis; neighbouring panes alike |
| Float | from the late 1960s | "smooth as a mirror", "a completely dead and even reflection" (Bygg og Bevar) | a perfect mirror |

A window's panes are not all as old as its sash. A broken pane was replaced with the glass of its own year, so an 1890s cross window in 1989 can hold cylinder panes beside one drawn pane and one float pane. That mix is a true record of breakage (our reading). Which way a drawn pane's wave runs once it is glazed was not found (Gaps).

### Inner windows, coupled windows and sealed units

- From about 1900 cold countries used double windows. The first form was a loose inner frame (*varevindu*), set in each autumn and taken out each spring. Coupled windows (*koblede vinduer*), inner and outer sash hinged as one, came later (SNL, vindu). Factory windows with full inner and outer frames appeared around the First World War, and many people still take the inner frames out for summer (Bygg og Bevar).
- Sealed units of two panes and an air gap came in the mid-1950s (SNL). "Almost everyone" went over from coupled windows to insulating glass between 1965 and 1975. Those were the years of units sealed with PCB, and about 2.5 million of them sit in Norwegian buildings (Teknisk Ukeblad). Danish factory "thermo" windows dominated from 1960 to 1980 and were made "first and foremost" against condensation (Bolius).
- Norway's building codes set no limit on a window's heat loss until 1985 (SINTEF).

How they look from the street:

- A coupled window has two panes in two sashes some centimetres apart, so it shows two reflections a little offset (our reading of the construction).
- A sealed unit shows two reflections almost on top of each other (secondary). Its spacer shows as a bright line at the pane's edge: Bergen's heritage office tells owners not to use bare aluminium spacers, which says that is the usual look.
- A failed seal fogs between the panes. A typical unit lasts 10 to 20 years (secondary).
- Heritage bodies disagree whether sealed units look more reflective or deader than old glass (both secondary). Float's own flatness is the cause either way.

### Dirt, condensation, frost and putty

- Frost flowers grow on a pane with "very cold air on the outside and warmer, moderately moist air on the inside", which is single glazing. Double glazing can still frost at the bottom (Wikipedia, frost).
- With an inner frame fitted, water condenses on the inside of the outer pane. The outer sash should be the leaky one (Bygg og Bevar; NPS Preservation Brief 9).
- Linseed putty cracks along the glass, in the lower part of the sash first. Paint should lap a couple of millimetres onto the glass. On the coast, fittings rust much faster than inland (Bygg og Bevar).
- Salt film on harbour glass and Norwegian window-washing customs were not found (unverified).

Each of these belongs to a shared system, never to noise. Frost and condensation are weather and heating, set by the hour (local scene state). Cracked putty and rusted fittings are upkeep. Clean or dull glass follows the care field: a kept house's glass is washed, and an empty one dulls. A grey film gathering in a pane's bottom corners is where the water layer would put it (unverified as observed).

### How games draw window glass cheaply

- Before interior mapping, games made windows fully reflective, or painted a few details near the glass into the texture and left the rest black (van Dongen 2008).
- Van Dongen's interior mapping blends the room's colour with a reflection map in the same pass, masked by the window alpha in the façade texture.
- A cubemap reflects as if the world were infinitely far away, so reflections slide over nearby walls. Sébastien Lagarde's parallax-corrected cubemap intersects the reflected ray with a box round the probe and samples towards the hit point. It is exact only for mirrors, so glossy surfaces distort. On a PS3 it cost about 0.25 ms per extra cubemap at a quarter of the screen, or about 0.08 ms with his cheaper mixing step (Lagarde 2012). A street between two rows of houses is close to a box, which suits it.
- Screen-space reflections are already in our URP as a renderer feature (`lighting-and-colour.md`). They see only what is on screen, which at the street stop is mostly the houses opposite.
- No source we read says how a shipped game draws old wavy glass (Gaps).

### Our glass

One opaque pass per window, drawn by the town's shade function:

1. A Fresnel weight from the view angle, with the 4 per cent reflectance of glass head-on.
2. The reflection: screen-space where the reflected point is on screen, otherwise the nearest box-projected probe, relit with the hour as the lighting study proposes.
3. The reflected ray bent by a normal per pane from the glass kind: concentric waves for crown, long random waves for cylinder, one-axis waves for drawn, none for float. The kind is a fact from the glazing event or the pane's replacement; the pattern within it is seeded texture.
4. The interior term (section 2) times the glass's transmission.
5. Dirt from care, condensation and frost from the hour, and the sealed unit's double image and spacer line, at the near tier only.

Nothing here is transparent, so a tile-based GPU removes hidden glass for free (section 7).

## 2. What is seen through a window

### Interior mapping and its successors

| Technique | Who | How | How rooms vary | Limits |
| --- | --- | --- | --- | --- |
| Plane interior mapping | Joost van Dongen, CGI 2008 | per pixel, the ray from the camera is cut against ceilings, floors and walls at regular spacing in the object's space; the nearest of three planes wins and gives the texture | a room texture picked at random from an atlas; walls moved within a limit for rooms of several sizes; a "furniture plane", a cut-out layer at a fixed depth, for furniture and characters, even animated | the furniture is flat; a seam where two faces meet at a corner, hidden by putting no glass at the corner |
| Cubemap rooms | Emil Persson (Humus), 2008 | the room as a cubemap traced as a box: one texture lookup, filtered edges | an array of cubemaps; one room's walls shuffled into eight combinations | every room the same depth |
| Atlas rooms with depth | Andrew Willmott, SimCity (2013) | one atlas of rooms drawn in one-point perspective, each room's depth in the alpha channel; the ray stretched to that depth (secondary: Ben Golus's account of the method) | a hash of the window's tile picks a cell; lit and unlit variants; rooms of half, one, two and four depths | the perspective is drawn for one field of view |
| Interior cubemap function | Unreal Engine 4 | an engine function (secondary: van Dongen 2018) | | |
| Marvel's Spider-Man (2018) | Insomniac | "seems very likely" to use interior mapping; Insomniac has not said (van Dongen 2018) | | a window can show a door, and a room seen past a corner can change |

Willmott's 2013 talk lists interior mapping, signed distance textures and façade definitions among SimCity's rendering topics; its 83 MB slides were not read. How City Sample, Cyberpunk 2077, Assassin's Creed and Hitman draw rooms behind windows was not reached (Gaps). Cyberpunk's lesson is about density instead. Every advert was placed by hand, and some areas "went into noisy territory"; Phantom Liberty kept negative space so "the eyes can rest" (80.lv, Niepokólczycki).

Van Dongen's measurements, on a 2004 GPU at 1024 × 768, give the costs that still hold in kind:

- A 31-storey block is 10 polygons with interior mapping and 158 with modelled rooms. Mapped buildings overtook modelled ones at 100 buildings; 500 buildings were 5,000 polygons against 79,000.
- The shader is dear per pixel: a plain façade with reflections drew 5,100 frames in five seconds, the same with interior mapping 999.
- Four textures cost no more than one, and room texture size barely matters (256 to 16 pixels square gained 5 per cent).
- A building of 1,000 or 4,000,000 rooms costs the same.
- A depth pre-pass, so that hidden pixels are never mapped, gained 44 per cent.
- Lit rooms: a room is lit when a noise value falls under the building's chance of lights being on, raised through the evening.

### How they avoid repetition, and how we should

Every method above varies rooms by chance: a random atlas cell, a flipped cubemap, a random depth. That is perceptual difference without meaning, and for us it is worse than oatmeal. A random room is a claim: a child's bedroom behind a widower's window, a 1980s kitchen in a house wired in 1909. Ours reads the room record:

- The kind of room, the household and the era are facts (section 8). The seed only picks among a few variants made for that kind, era and class, as Boris the Brave's few big decisions from short lists.
- The depth comes from the house's plan. A double-span log box of 7.5 m has front rooms about half that deep; a sea house's loft runs the whole depth.
- A room behind two windows is one room. The shader needs the room's box (its width, depth and height, and where this window sits in it) as instance data, not a hash of a grid tile. Then the same back wall shows through both windows, and a corner room shows the same room from both streets. That fixes the Spider-Man artefact van Dongen describes.
- A narrow house seen through its front window can show its back window, lit by the sky behind (our reading). It is the strongest single cue that a room has depth.

### The household in the window

What hung in Norwegian windows, by decade (Norsk Folkemuseum, "Gardiner i hjemmet", unless marked):

| Years | What hung | Notes |
| --- | --- | --- |
| from the mid-1700s | roller blinds | Bergen made them around 1850; stencil-painted ones were popular |
| 1800s | curtains for occasions | fabric was dear and faded in the sun; in the 1860s Eilert Sundt noted who had curtains as a mark of class |
| late 1800s | heavy dark drapes, portières, plush | in bourgeois homes, covering most of the window; by 1900 curtains were common across much of the population |
| 1889 on | venetian and roller blinds | Rullegardinfabrikken NOR in Kristiania; spring roller blinds became common in the 1890s (lokalhistoriewiki) |
| about 1850 to 1950 | winter and summer curtains, changed each season | Danish evidence (lex.dk; Bolius) |
| 1900 to 1910 | lighter linen and cotton with lace borders | Ellen Key (1903) recommended thin white fabric |
| 1930s | straight side curtains under a narrow gathered valance; large dark florals | the Kirsch rod |
| 1940 to 1945 | blackout curtains fixed in the frames | fines of 20 to 50 kroner (lokalhistoriewiki) |
| 1957 | full white lace on an Oslo ground floor, side curtains for night, roller blinds | so she could see out and the street could not see in |
| 1965 | a checked half curtain with a valance in the kitchen, which the museum calls a "peek out, not in" curtain | large florals in bedrooms; Marimekko's Unikko |
| 1970s | plants in place of patterned curtains; plain linen on wooden rings; a white roller blind | Danish sheers peaked, some leaving the bottom third clear for plants (Bolius); orange and brown |
| 1980s | sheers going out; two-part café curtains in kitchens | Danish evidence (Bolius) |
| 2000s | no curtains; slatted blinds move from offices into homes | |

On the sill and in the glass:

- The electric Advent candle arch was first made in Gothenburg in 1934 and sold widely from 1939 (Swedish Wikipedia). In Norway too it stands "as a rule" in a window (Norwegian Wikipedia). The paper Advent star came from Herrnhut and spread across the Nordic countries between the wars. When both reached Norwegian windows was not found (unverified).
- Plants by species and decade, the everyday window lamp, the 17 May flag and "til leie" notes were not found in any historical source (unverified). The window lamp's only explanations are lifestyle pages.
- A student's bedsit of 1979 to 1982 had single glazing covered in winter with polystyrene boards, a small hatch cut out to see the weather (Norsk Folkemuseum). From the street that is a white board with a small dark square: a fact about a poor tenant in a cold house.
- Offices hung venetian blinds from the late 1800s, and vertical blinds came in 1948, beige or white in the 1970s (Wikipedia, window blind). A 1980s office reads as fluorescent troffers in a grid behind blinds.

So each window carries a dressing stack: a blind (up, half, down), a sheer or lace (full, half, none), side curtains (open, drawn), a valance, and the sill. Each layer was hung in a year and kept for years, so a 1989 window can hold 1970s sheers. What hangs follows the household's age and class, the room's kind and the floor; ground floors on the street covered more. Its state follows the hour, with blinds down at night. A new household brings new dressing, and no dressing ever changes for mood.

### How a room reads by day

- Painters agree that windows are rarely black. Upper panes reflect the sky and lower ones the buildings and trees opposite. Glass on the shaded side often reads lighter than on the sunny side. Curtains and blinds make a window read "white-ish", and the frame casts its shadow on them (Liz Steel; Outdoor Painter). Distant windows are simplified in the wall's colour (Liz Steel).
- A sheer lets people see out while passers-by cannot see in (Bolius), which is why a curtained window reads pale.
- At dusk the balance turns: the room rises against the falling sky until the two are about equal, which photographers call the balance point (secondary, photography guides).

The window's day read is therefore three terms. Its reflection shows sky above and street below, and grows with the angle. Its dressing is pale sheers, a flat blind or bare glass. Its room shows mainly near the camera, through bare glass and on the shaded side. Our own estimate, unverified: by day a room near the window gets perhaps a tenth of the façade's light. Bare glass then reads two or three value steps below the wall, with the reflection on top, which matches the painters.

## 3. Lit windows at night

### Which rooms are lit, and when

- In 1980, 72 per cent of Norwegians had begun their night's sleep by 23:30; in 2010, 56 per cent (SSB, *Tidene skifter*). People spent 15 hours 11 minutes a day at home in 1990 (SSB).
- Dinner (*middag*) was eaten at about 14 to 15 in the farming society; today most eat it late in the afternoon or into the evening (SNL, middag). A common industrial-era hour of 16 to 17 is our guess (unverified).
- NRK opened on 20 August 1960 with 16,876 licence holders, and broadcast in colour from 1 January 1975. The monopoly ended in 1982, satellite came in 1986 and TVNorge in 1988 (Norwegian Wikipedia; Wikipedia). In 1991, 81 per cent watched television on an average day (SSB, Norsk mediebarometer).
- From the first Sunday of Advent the candle arch and the star go in the window (section 2).
- From 9 April 1940 windows were blacked out (lokalhistoriewiki).

A 1989 weekday evening is then: the kitchen lit around dinner, the living room with the television after, a bedroom briefly before sleep, and about three houses in four dark by half past eleven. SSB's hour-by-hour tables of who is at home and asleep were not read (Gaps). Who is home is the engine's fact (habits, request 1 on #22; homes, request 15). Until it comes, the fixtures' `lit` block stands in, today per floor with a cause; it should go per room and per hour.

### The light by era

| Source | In Stavanger | Colour | From the street |
| --- | --- | --- | --- |
| Candle | always | about 1,850 K | a dim, flickering point |
| Paraffin lamp | from the 1850s, most common from the late 1800s (SNL; Norwegian Wikipedia) | about 1,900 to 2,000 K (unverified) | one warm pool on a table; a round-wick lamp gives from about 840 lumens, as much as a 60 W bulb (Wikipedia, kerosene lamp; our reading) |
| Incandescent bulb | from 10 December 1909 (lokalhistoriewiki) | 2,400 K for a standard bulb in Wikipedia's table; 2,700 K is the common figure | a warm room, a pendant over the table |
| Fluorescent tube | sold from 1938; in Norwegian kitchens from an unknown year (unverified) | cool white 4,100 K; old tubes render colour poorly (index about 60) | a cool, even, greenish rectangle; offices as a grid |
| Television | from 1960; colour from 1975 | screens at 6,500 to 9,300 K | a cool, shifting glow under the warm room light |
| Halogen | launched 1959; common in US homes by the 1990s (Wikipedia); Norway unverified | about 3,000 K (unverified) | small bright spots |
| Compact fluorescent, then LED | from 1980 and 2007; the EU phased out bulbs from 2009 to 2012, and Norway followed | 2,700 K, the first fluorescents slow to warm up | |

The 1989 default is warm incandescent, with some halogen and a few kitchen tubes. An older lamp still in use is a fact about its household.

### How games light thousands of windows

- Van Dongen lights a room when a noise value falls under a chance raised through the evening.
- Cities: Skylines uses one channel of an illumination map: 0 is dark and 120 fully lit. Values from 128 to 255 are "random window illumination values", where "the closer the value is to a boundary the more likely it is to be lit and stronger" (Paradox wiki).
- GTA V draws "every single small light spot" in the distance as a 32 × 32 textured quad, batched into instanced geometry of "tens of thousands of polygons" (Courrèges).
- None of them knows who is home.

### Our way

- Each room's emission comes from its record: lit or not this hour, its lamp kind and so its colour, the television on or off. A television is a cool term on the room's back wall whose brightness drifts slowly; its rhythm is seeded, and the fact is only that it is on.
- The dressing filters the light. Lace glows and shows its pattern, a drawn blind is a warm flat rectangle, and heavy curtains leak light at the edges (our reading).
- No window is a real light. Today `TownLights.cs` gives every lit shop a spot light, and the heart holds 403 lights, 304 of them shopfronts, against Forward+'s 256 (`lighting-and-colour.md`). The light a window throws onto its reveal, the wall below and the pavement should come from a buffer of lit windows (position, size, colour, strength). It is binned per screen tile, as the lighting study proposes for lamps, or drawn as projected light decals in the street tier. Real shadowed lights go only to the few windows a scene looks through.
- Past the street tier a house's lit rooms become small warm marks, and the town's glow map carries them further: GTA's quads in kind, but each one a room that is lit.

## 4. Shopfronts and their glass

- In Stavanger, Kirkegata 26, a house of the 1860s, has a jugend front of 1916, "like many others in Stavanger". Norem Baade at Kirkegata 22 has traded since 1843; its front was made funkis in 1937 or 1938 and given black glass panels in 1958 or 1959 (sources differ). The centre's fronts were modernised in funkis "in the 30s to 60s" (Kulturminneplan 2010). Sea houses became restaurants from 1973 and 1978 (same).
- From 1930 many old ground floors in Oslo were lowered, their windows enlarged, the door recessed between angled glass sides, and a small cast concrete canopy added to carry the sign (Byantikvaren Oslo 2012).
- In Britain, Victorian fronts used tiles and cast iron; Edwardian ones hardwood, brass and etched glass; 1930s ones Vitrolite, black granite, chrome and integral blinds; post-war ones aluminium. Vitrolite ended in the 1960s (Lennie 2012).
- Rullegardinfabrikken NOR made awnings its main product after the 1890s (lokalhistoriewiki). Oslo's sign guide lets an awning carry the business's name on its front edge (Byantikvaren Oslo 2012).
- Oslo Samvirkelag opened Norway's first self-service grocery in 1947 (Norwegian Wikipedia). The discount chains came at the end of the 1970s: Rimi in 1977, Rema and Kiwi in 1979. A counter shop's window is a dressed display with the counter deep inside; a self-service shop shows shelves and price posters on the glass. Oslo's present guidance allows foil on a third of the glass at most, because full cover gives "a closed and rejecting street image" (Byantikvaren Oslo 2012). That is a modern rule, not 1989 practice.
- The window dresser (*dekoratør*) was a trade with its own training (SNL); dates were not found. Boarded and whitewashed fronts of empty Norwegian shops were not found either (unverified).

A shopfront is its own dated stack on the house: its frame and glass (plate before float), the fascia and awning sockets, the display, the service mode, the business's hours and its state. The display is the shallow real room of `kits-and-generation.md`'s second tier, with the trade's goods as fixed parts. In December it is dressed for Christmas. At night it is lit for the business's hours, and a closed shop's window is dark or shows its night light (unverified as practice).

## 5. Signs and lettering

### Methods by era

| Method | Years and Norwegian evidence | How it ages | What it leaves when it goes |
| --- | --- | --- | --- |
| Painted on the wall or on a fascia board | throughout; on render a "long tradition" in Oslo, photographed in 1922 and 1954 (Byantikvaren Oslo 2012) | fades with sun; repainted with each owner; old lead paint bonds to masonry and outlasts later coats (Wikipedia, ghost sign) | a ghost under thin later coats; a patch painted out |
| Letters on glass: painted, etched, sandblasted, gold leaf on black glass | Oslo's business blocks of about 1860 to 1915 had sign fields and glass signs in the windows; gold leaf on black glass at Kirkegata 32 and Pilestredet 12 (Byantikvaren Oslo 2012) | gold keeps its mirror; paint behind glass flakes (unverified) | the glass replaced or scraped |
| Enamel plates | about 1880 to 1960 (English and German Wikipedia); Cathrineholm at Halden made signs from 1910; German imports such as a Dold plate of 1912 to 1940 in Norsk vegmuseum, with four screw holes (SNL; DigitaltMuseum) | glass on steel: the colour does not fade, but cracks where the steel bends; chips and rust at edges and holes (unverified) | screw holes, rust runs and a less weathered rectangle |
| Applied letters, cut wood or cast metal | funkis, 1930 to 1950: slim free-standing letters along the front, flat on the fascia, deep with returns on canopies, unlit (Byantikvaren Oslo 2012) | | a pattern of holes; on stone for good (the Folketeater's marble; Byantikvaren Oslo 2012) |
| Black glass fascias | 1930s to 1960s; Norem Baade 1958 or 1959; Vitrolite ended in the 1960s | cracks (unverified) | |
| Lit signs: bulbs, then neon | Freia at Egertorget, Kristiania's first lit sign, 1909 or 1910, called "vulgar" at once; Eldorado's neon by 1929 (Byantikvaren Oslo 2012; lokalhistoriewiki); in Stavanger the congregation's "Jesus Verdens Lys" at Bergelandsgata 29 in 1926, its present sign from the 1970s (Kulturminneplan 2010) | tubes fail as gas leaks; letters go dark one by one (Wikipedia, neon sign) | brackets, a transformer box, cable stubs (unverified) |
| Back-lit plastic boxes | Oslo's guide notes some put up before 1965 (Byantikvaren Oslo 2012); acrylic sold from 1933 | the face yellows and cracks (unverified); tubes die | bracket holes, a cable stub, a clean rectangle |
| Cut vinyl letters | Gerber's plotter of 1982 sold out on its first day and passed 30,000 units (Sign Media); Norway's date not found | peels and shrinks (unverified) | a shadow of adhesive (unverified) |

Ghost signs survive where lead paint bonded. Many from the 1890s to the 1960s are still visible; owners repainted over old ones, and some reappear when a neighbour is demolished (Wikipedia, ghost sign). They fade faster in strong sun (Ghostsigns). After Kristiania's crash of 1899 left many blind gables, painted gable adverts became a trait of the city, and Freia painted its own on empty gables (Byantikvaren Oslo 2012; lokalhistoriewiki).

### Letters by period

- Before about 1920, the signwriter's own hand: their alphabets, shading and gilding. Norwegian sign painters' training and firms were not found; the trade is now "almost extinct in Norway" (Norwegian Wikipedia).
- Futura came in 1927 and Helvetica in 1957, renamed in 1960 (Wikipedia).
- Corporate faces follow: NKL's own typeface by Leif Frimann Anisdahl in 1967, Den norske Creditbank's in 1973, Norsk Hydro's in the late 1970s, Televerket's in 1980 (typografi.org).
- Norway's road signs use Trafikkalfabetet, drawn about 1965 at the Vegdirektoratet and close to DIN 1451; it was also on number plates until 2002. Oslo's street-name signs use a narrower, darker face (SNL). Stavanger's street-name signs were not found.
- The chains on a 1989 street had dated logos. They include Rema 1000 (opened as Rema 600 in 1979, renamed 1980), Rimi (its 1988 logo after buying Spar 800) and Kiwi (1979). Vinmonopolet's logo is from 1956, and it kept counter service until 1999. The cooperative's NKL mark ran from 1906 to 1992 ("Coop" only from 1992); Narvesen dates from 1894; and Statoil, which bought Norol in 1987 (Norwegian Wikipedia).

So a sign's letters follow from its maker and its year: a signwriter's hand, a foundry face, a chain's identity with its version, or the road authority's face.

### Rules

Oslo's 2012 guide caps hanging signs at 70 to 100 cm out, keeps signs off cornices and window surrounds, and asks new signs to reuse old holes. It advises against light boxes, which cover far more of a front than open letters, and notes that one tenant breaking the line makes the others "raise their voice" (Byantikvaren Oslo 2012). Stavanger's 1974 plan 681, said to control colours, light fittings and signs (`town-change.md`), could not be checked. Stavanger's blue history plaques date from 1998, so none hang in 1989 (Stavangeren 2/1998).

## 6. Records on the street

### What the walls carried in 1989

- The Storting election was held on 10 and 11 September 1989; a protest election, with Labour at 34.3 per cent and the Progress Party at 13.0 (Norwegian Wikipedia). An October frame should still show torn election posters.
- Gig and cinema posters were pasted over each other on boards and closed fronts. Posting without the owner's consent is usually illegal (Wikipedia, flyposting); Norway's own rules were not checked.
- Stavanger's own papers included Stavanger Aftenblad (from 1893) and Rogalands Avis (19,433 copies in 1984); VG sold 360,331 copies across the country in 1989 (Norwegian Wikipedia). How their bills (*løpesedler*) stood at kiosks was not found.
- *Beat Street* reached Norwegian cinemas in 1984, and United Taggers formed in Oslo in 1985 (lokalhistoriewiki; Norwegian Wikipedia). Reported graffiti offences rose from 20 in 1990 to 7,690 in 1999 (Norwegian Wikipedia), so tags in 1989 Stavanger were probably few (unverified). Paint from the 1972 EEC vote survives in at least one place, a flag in Øystre Slidre (lokalhistoriewiki). Nuart (2001) and Pøbel (1999) come after the start of play.

Advertising columns (Berlin's Litfaß column, 1854) were not found in Norwegian towns.

### How games make them readable

- Pentiment's typefaces carry each character's education and standing: a scribe's hand, a printer's type, a looser peasant hand inked with the off hand. Text is written stroke by stroke from ductus diagrams, and the most legible face doubles as the accessibility option (Lettermatic).
- Valve's distance fields (Green 2007) store a sign's edge as a distance in one 8-bit channel. A 64 × 64 field made from a 4096 × 4096 image draws crisp vector art; a 128 × 128 field drew a "No Trespassing" decal in Team Fortress 2. Outlines, glows and drop shadows come almost free, but corners round off. Multi-channel fields keep corners sharp at the cost of a median of three channels (msdfgen, MIT licence).
- Cyberpunk 2077 placed every advert by hand and found some streets too noisy to read (80.lv). Disco Elysium's backgrounds are rendered height maps painted over (GameBanshee); how it handles text in the painted world was not found. Watch Dogs: Legion was not reached (Gaps).

### Text at our cameras

The street stop's 35 mm lens spans about 38° over 1,440 pixels, about 38 pixels a degree. A 300 mm fascia letter at 20 m is about 33 pixels tall and reads. At 60 m it is about 11 pixels and barely reads. A poster's 30 mm body text reads at eye level 2 m away (about 33 pixels) and is 8 pixels from 8 m. Its 100 mm headline at 8 m is about 27 pixels. A poster therefore has two layers: a headline for the street stop and a body for eye level. Below about 10 pixels a glyph becomes a mark: the painted fade draws a few strokes in the letters' colour and rhythm, never wrong letters. The edge of painted letters takes the brush mark's noise at its size in the world, so a signwriter's letters look painted at eye level and still read.

Text in the world is a fact in the pack's language. Norwegian signs stay Norwegian, and the interface translates on inspection, with the maker and date beside the claim (`interface.md`: the world's own media first; a reason one hover away). Fonts must carry æ, ø and å.

A record may be wrong. A poster can announce a gig that was cancelled, a sign can name a shop that closed, a newspaper bill can get the night wrong. The why-probe shows the record's maker, date and claim beside the facts.

## 7. Cost on our machine

The Mac mini's M4 draws in tiles. Opaque overdraw and MSAA are cheap there; alpha-tested cut-outs and blending are dear (`docs/foundations.md`). Everything in this study can stay opaque.

| Feature | What it costs | How to keep it cheap |
| --- | --- | --- |
| Interior mapping | arithmetic and two or three texture reads per window pixel; nothing per room | opaque, so hidden pixels are never shaded; furniture planes at the near tier only; room cells in one texture array. Windows fill perhaps 5 to 15 per cent of a street-stop frame, so a few tenths of a millisecond at most (our estimate, to be measured) |
| Glass reflection | screen-space reflections are a full-screen pass we already pay; a box-projected probe adds one intersection per pixel | the per-pane bend is one more normal; the double image of sealed units only near |
| Curtains, blinds, sill | layers inside the window shader | never as alpha-tested cards |
| Lit windows | emission, which the shade function adds for nothing | no window in the light list |
| Spill on walls and pavement | a tile-binned buffer read by the receiving surfaces, or decals | Unity recommends screen-space decals on tile-based GPUs; its DBuffer decals need a depth-normal pre-pass that is "less efficient" there. Decals skip the SRP Batcher by design but can be instanced (Unity 6 docs) |
| Signs and posters | a distance-field sample and a smoothstep per letter pixel | letters drawn inside the sign's own opaque surface, not as blended text meshes; one glyph atlas per face |

The performance harness (`performance-at-scale.md`) should time the heart at night with every window mapped and lit from facts. A budget of about 1 ms for windows, glass and spill is our proposal.

## 8. What the house generator must carry

The building-blocks architecture is designed next. These records must be in it from the start; adding them later means migrating every fixture.

### The window as four records

| Layer | Fields | Who decides | Changes when |
| --- | --- | --- | --- |
| Opening | façade, cell, size, year, cause | the diary (structure) | built, cut, enlarged, shrunk, blocked; never deleted by a later event (`kits-and-generation.md`) |
| Fill | sash part and era, its event and fit; the list of earlier fills; the inner window (loose frame, coupled, sealed, none); each pane's glass kind and year | the diary (skin); pane breakage by the life runner (`derived`) | windows replaced, restored, reglazed; inner frames out for summer |
| Dressing | blind, sheer or lace, side curtains, valance, sill objects, each with the year hung | the household, derived by rules until the engine has homes | a household moves in or out; a decade passes |
| Room | a reference to the room record | the house plan | the house is divided, converted or let |

### The room behind each window

A room record holds its building, floor, box in millimetres and the windows that look into it. It holds its kind (kitchen, living room, bedroom, stair, shop, office, workshop, store, loft) and its household or business. It holds the year it was last fitted out, and its lamps with their years. Rooms are allocated inside the openings history fixed (plan step 8, Shadows of Doubt's method). Until then a rule splits each floor at the bay lines by era and use. An empire log box gets two front rooms and a kitchen behind; a two-family house gets one flat per floor. The interior shader reads the box, so a room behind two windows is one room. Lit windows tonight, mapped rooms at the street stop and real rooms in a scene all read this one record.

### The sign

A sign is its own record and gets its own diary events (`sign_put_up`, `sign_relettered`, `sign_taken_down`), separate from `business_opened`. A business can keep an old sign, and a sign can change while the business stays: house A's painted band of 1931 gained a lit box in 1962 under the same ironmonger (`living-fabric.md`). The fixture today has only the business and its ghosts. The record holds:

- its socket (fascia, glass, wall, projecting bracket, canopy, roof, gable);
- its method from the table in section 5, and its maker (a signwriter, a foundry, a chain);
- the year, event and cause it went up;
- its text, from the business's name in the words layer, and its letter style, from maker and year;
- its colours, and whether and how it is lit, with its hours;
- its coats and reletterings, and its state from the life runner (faded, chipped, a dead tube);
- when it came down, and what that left, from the method's own definition;
- its claims: the business, its trade, a telephone number.

### Records on the street

A poster, notice, newspaper bill or tag holds its maker, the date it went up, its purpose and its claims. It holds its surface (wall, boards, window, kiosk stand) and its place in the stack. It holds its ageing (paper bleaches and tears; tags are buffed) and how it went (scraped, pasted over). Records that can be wrong come from the engine (request 9). A poster that only restates a booked gig is drawn here from the facts.

### Facts needed from the engine

- Homes and households (request 15, the engine's #59): who lives behind which window, their ages, own or rent, the year they moved in. It drives dressing, rooms and light.
- Habits (#22, request 1): who is home at which hour, the television on. It drives lit rooms.
- Buildings separate from businesses (request 5) and ventures that take a building (request 21): the business's kind, name and opening hours. It drives the shopfront, the sign, the display and the lit hours. Opening hours should be added to the request.
- Records (request 9): posters, papers and notices with maker, date and claims.

Curtains, lamps and the year a room was fitted are Overstory's to derive from these, by written rules with provenance `derived`, as care is derived in `living-fabric.md`.

### Where each thing sits among the five kinds

| On screen | Kind | Rule |
| --- | --- | --- |
| the opening, the sash, the glass kind, the sign's existence and text, which rooms are lit | canonical fact | from the diary or the engine; never seeded |
| the lace style for a decade and class, the lamp colour for an era, the inner window's double reflection | interpretation of facts | a written rule from the facts |
| the ripple inside a glass kind, the minute a lamp goes on inside the hour the habit gives, a brush edge on letters, which of three lace patterns | non-semantic texture | the seed; never strong enough to read as a history |
| the sign's claim, the poster's text, the newspaper bill | perceived information | quoted from its record, shown with maker and date, may be wrong |
| a blind drawn, a window open, condensation, the television's flicker | local scene state | from the hour and the weather |

Three rules follow. A random lit room, a random curtain or a random room behind glass is a false claim, so none is drawn. Readable text comes only from a record, so no wall carries filler words. What a removal leaves comes from the removed part's definition.

## Look tests that would prove it

Each is judged from the judging views by cold readers with the shuffled-facts control (`docs/foundations.md`).

1. Glass: crown, cylinder, drawn and float panes, a coupled window and a sealed unit, each with a lamp post and a downpipe in its reflection, at eye level and the street stop, in drizzle and low sun. Readers order the panes by age: four in five right, and no reader calls float old.
2. A house by day across its years: house C in 1935, 1965, 1975 and 1989 (its husmorvinduer came in 1971), at the street stop and 12 m. Readers say which windows changed and roughly when, and whether an old or a young household lives there; with the facts shuffled, the household reading must fall.
3. The corner by night: blue hour, 20:00 and 23:30 on an October weekday in 1989, and a Sunday in December. Readers say which houses have people at home and what they are doing; the control lights the same number of rooms at random.
4. House A's shop and sign in 1931, 1962, 1980 and 1989, at the street stop and eye level, day and night (the story in `living-fabric.md`).
5. Text: a fascia, an enamel plate, a poster and a tag at every judging view: legible where section 6's numbers say, painted marks beyond, no shimmer.
6. Frame time of the heart at night on the M4 at 1440p, every window mapped and lit from facts.

## What we should do

Ranked by what it buys before the houses. Costs are working days on Opus for the system; each part still costs its own making and review.

1. Put the four window records, the room record and the sign record into the plan before any window part is made. Openings never deleted, fills as a list with panes and inner windows, dressing, a room reference; rooms with boxes; signs with their own events. Cost: 2 to 3 days in the resolver, with a hash migration of the fixtures; it overlaps item 4 of `kits-and-generation.md`. Buys: one contract that the parts, the shaders and the night all read, so a lit window can never disagree with the house's history.
2. Stop making lights of shops and windows. Drop the spot light per shop in `TownLights.cs`; draw spill from a tile-binned buffer of lit windows and the glow map; keep real lights for lamps and a scene's few windows. Cost: about 2 days, with the lighting study's night-in-tiers item. Buys: the 256-light limit met, and the night at frame rate as windows multiply.
3. One opaque window shader. Glass with the reflection bent by its kind, box-projected probes behind screen-space reflections, interior mapping in room space from the room's box, the dressing as layers, emission by lamp kind and the television's term. It replaces today's palette swatch and the global `_OS_WindowGlow`. Cost: 4 to 6 days. Buys: the street stop's windows by day and by night, at a fraction of a millisecond.
4. The household's day as rules until the engine's habits arrive. A schedule per household type of which rooms are lit by hour, with seeded minutes; the fixtures' `lit` block per room. Cost: 1 to 2 days. Buys: truthful night windows on the corner now, and a seam the engine's habits can replace.
5. The room atlas. A few rooms per kind, era and class, made in Blender as one-point-perspective cells with depth and lit and unlit states, painted in our style and judged on a quick sheet. Cost: a day for the tool, then each kind as a part. Buys: the interior term, never random.
6. The dressing parts. Lace, sheers, roller blinds, venetian blinds, side curtains and a few sill objects by decade, as textures and layers for the window shader. Cost: 2 to 3 days. Buys: the household readable from the street, which is criterion 2's first step for homes.
7. The sign kit. The methods of section 5, each with its ageing and its removal mark; distance-field glyph atlases from free fonts per period (licences to check) and signwriters' alphabets we draw ourselves; letters drawn inside the sign's own surface. Cost: 3 to 4 days for the system, then each method as a part. Buys: dated, legible signs, and ghosts that come from facts.
8. Records on the street. Posters as a coat stack on walls and boards, with a headline and a body layer, from fixture records until engine request 9. Cost: about 2 days. Buys: a venue's wall that tells its gigs, and the first records that can be wrong.
9. Run look tests 1 to 6, test 6 first on a stand-in, so the budget is known before the parts are made. Cost: 1 to 2 days each, mostly Sonnet for renders and Fable for judging.
10. Close the research gaps that block building: SSB's hour-by-hour tables, Stavanger's street-name signs and house numbers, plan 681, when the Advent arch and cut vinyl reached Norway. Cost: a day with a fresh search budget.

## For Øystein to decide

1. How much room shows by day. Recommended: the truth. Mostly reflection and dressing from the street stop, rooms near the camera and through bare glass; at dusk the rooms rise. It is less showy than games that light every room, and it is what the street looks like.
2. Signs and records stay Norwegian, translated on inspection. Recommended, because a translated sign would be a false record.
3. How strong old glass is. Recommended: its true strength at eye level, where the bend of a lamp post is the cue, with the gentle push. Stronger reads as a funfair mirror.
4. The television's flicker and December's lights. Recommended: both, as facts from the household. The flicker stays faint; the Advent lights are the strongest December signal in the town.
5. No readable filler text anywhere. Recommended: every readable word comes from a record, and where there is none the surface carries marks, not words.

## Gaps

- No source we reached says how City Sample, Cyberpunk 2077, Assassin's Creed, Hitman or Watch Dogs: Legion draw rooms, signs or posters, or how Disco Elysium handles text in its painted world. Insomniac has not said what Spider-Man's windows do. Willmott's SimCity slides (83 MB) were not read.
- No source on how a shipped game draws old wavy glass.
- SSB's hour-by-hour tables of who is at home and asleep (Statbank 14320), and household television ownership from 1960 to 1990.
- Norwegian dates for the Advent arch and star in windows, fluorescent tubes in kitchens, halogen in homes, and cut vinyl in sign shops. The window lamp has no historical source.
- Stavanger's gasworks date and gas light in homes; colour temperatures of paraffin flames and carbon filaments.
- Stavanger's street-name signs and house numbers, its neon and box signs after 1926, plan 681 of 1974, and its sign painters.
- How *løpesedler* were shown at kiosks, poster columns in Norway, fly-posting rules, bus timetables at stops.
- Boarded and whitewashed fronts of empty shops, sill plants by decade, the 17 May flag in windows.
- How Vitrolite, acrylic boxes and vinyl age; salt film on harbour glass; which way a drawn pane's wave runs once glazed.
- Bygg og Bevar's *Murbyens butikkfasader* in full, Historic England's shopfront guidance (refused access) and Kathryn Morrison's *English Shops and Shopping*.
- The run's web-search budget ran out early. The Norwegian subject came from three research passes, which were cut short for the same reason. A follow-up with a fresh budget can close most of the above, starting with nb.no's newspapers, DigitaltMuseum and Stavanger byarkiv.

## Sources

Glass and windows: [Hurdal Glassverk (lokalhistoriewiki)](https://lokalhistoriewiki.no/wiki/Hurdal_Glassverk) · [Biri glassverk (SNL; secondary)](https://snl.no/Biri_glassverk) · [Drammens Glassverk (SNL)](https://snl.no/Drammens_Glassverk) · [Drammen, 1928 (DigitaltMuseum)](https://digitaltmuseum.org/011022740010) · [Hagen 2023, glazing seminar, Bergen](https://www.kirken.no/globalassets/fellesrad/bergen/dokumenter/kirkebygg/presentasjoner%20teglkirkeseminar%202023/012%20karl%20arne%20hagen%2023.10.22%20presentasjon.pdf) · [Nor, Viggja, restoring windows and doors](https://www.trondheim.kommune.no/globalassets/10-bilder-og-filer/10-byutvikling/miljoenheten/byantikvaren/seminar---a-reparere-en-fasade/14_jarle-nor.pdf) · [Pilkington Floatglas AB, Halmstad](https://www.pilkington.com/~/media/Pilkington/Site%20Content/Denmark/News/005_pressmedelandepilkingtonfloatglasab1.pdf) · [Pilkington heritage](https://www.pilkington.com/en-gb/uk/about/heritage/flat-drawn-process) · [Flat glass handout (glassproperties)](https://www.glassproperties.com/references/Flat&FabGlasEngHandout.pdf) · [Designing Buildings, history of glass](https://www.designingbuildings.co.uk/wiki/The_history_of_glass_in_the_UK_and_Ireland) · [Building Conservation, historic glazing](https://www.buildingconservation.com/articles/glazing/glazing.htm) · [Bygg og Bevar, window upkeep](https://www.byggogbevar.no/pusse-opp/vindu-doer/artikler/vedlikehold-av-vinduer/) · [Bygg og Bevar, insulating old windows](https://www.byggogbevar.no/pusse-opp/vindu-doer/artikler/varmeisolering-av-gamle-vinduer/) · [SNL, vindu](https://snl.no/vindu) · [Teknisk Ukeblad, PCB units](https://www.tu.no/artikler/dumper-tonnevis-med-pcb/273254) · [Bolius, the window 1900 to 2016](https://www.bolius.dk/vinduets-historie-1900-2016-16795) · [Asker kommune, insulation by era](https://www.asker.kommune.no/klima-og-natur/dette-kan-du-gjore-for-klima-og-natur/energiradgivning/hvor-godt-isolert-er-boligen-din/) · [SINTEF, codes and energy](https://www.sintef.no/globalassets/upload/rebo/arbeidsverksted1/16.04.09-energibruk_tw.pdf) · [Bergen byantikvar, windows and doors](https://www.bergen.kommune.no/hvaskjer/tema/kulturminner-i-bergen/istandsetting-og-vedlikehold/vinduer-og-dorer) · [Glass Doctor, failed seals (secondary)](https://glassdoctor.com/content/condensation-between-window-panes) · [Frost (Wikipedia)](https://en.wikipedia.org/wiki/Frost) · [NPS Preservation Brief 9](https://www.nps.gov/orgs/1739/upload/preservation-brief-09-wood-windows.pdf) · [SLKS, dating windows](https://slks.dk/fileadmin/user_upload/SLKS/Omraader/Kulturarv/Bygningsfredning/Gode_raad_om_vedligeholdelse/5.4_Datering_af_vinduer_1700-1950.pdf)

The household in the window: [Norsk Folkemuseum, curtains in the home](https://norskfolkemuseum.no/gardiner) · [Norsk Folkemuseum, Alvhild's bedsit 1982](https://norskfolkemuseum.no/alvhilds-hybel-1982) · [Rullegardinfabrikken NOR (lokalhistoriewiki)](https://lokalhistoriewiki.no/wiki/Rullegardinfabrikken_NOR) · [Bolius, net curtains](https://www.bolius.dk/undergardiner-hvor-blev-de-af-21983) · [Bolius, the curtain's history](https://www.bolius.dk/her-er-gardinet-historie-96894) · [Lex, gardiner](https://lex.dk/gardiner) · [Window blind (Wikipedia)](https://en.wikipedia.org/wiki/Window_blind) · [Blackout, 1940 (lokalhistoriewiki)](https://lokalhistoriewiki.no/wiki/Lokalhistoriewiki:Hovedside/Ukas_artikkel_2011-04) · [Adventsljusstake (Swedish Wikipedia)](https://sv.wikipedia.org/wiki/Adventsljusstake) · [Adventsstake (Norwegian Wikipedia)](https://no.wikipedia.org/wiki/Adventsstake) · [Adventsstjerne (Norwegian Wikipedia)](https://no.wikipedia.org/wiki/Adventsstjerne) · [Liz Steel, windows and glass](https://www.lizsteel.com/windows-and-glass/) · [Outdoor Painter on windows](https://www.outdoorpainter.com/?p=18732) · [Blue hour (secondary)](https://dailyphototips.com/lighting/blue-hour/)

Light and the household's day: [SSB, Tidene skifter](https://www.ssb.no/kultur-og-fritid/artikler-og-publikasjoner/tidene-skifter) · [SSB, time use](https://www.ssb.no/kultur-og-fritid/tids-og-mediebruk/statistikk/tidsbruksundersokelsen/artikler/hva-bruker-vi-tiden-var-pa) · [SSB, Norsk mediebarometer](https://www.ssb.no/kultur-og-fritid/tids-og-mediebruk/statistikk/norsk-mediebarometer) · [SNL, middag](https://snl.no/middag) · [TV-året 1960](https://no.wikipedia.org/wiki/TV-%C3%A5ret_1960) · [TV-året 1975](https://no.wikipedia.org/wiki/TV-%C3%A5ret_1975) · [Television in Norway](https://en.wikipedia.org/wiki/Television_in_Norway) · [Stavanger (lokalhistoriewiki)](https://lokalhistoriewiki.no/wiki/Stavanger) · [Oltedal kraftverk (lokalhistoriewiki)](https://lokalhistoriewiki.no/wiki/Oltedal_kraftverk) · [SNL, lampe](https://snl.no/lampe) · [Parafinlampe](https://no.wikipedia.org/wiki/Parafinlampe) · [Kerosene lamp](https://en.wikipedia.org/wiki/Kerosene_lamp) · [Color temperature](https://en.wikipedia.org/wiki/Color_temperature) · [Fluorescent lamp](https://en.wikipedia.org/wiki/Fluorescent_lamp) · [Halogen lamp](https://en.wikipedia.org/wiki/Halogen_lamp) · [Compact fluorescent lamp](https://en.wikipedia.org/wiki/Compact_fluorescent_lamp) · [LED lamp](https://en.wikipedia.org/wiki/LED_lamp) · [Phase-out of incandescent bulbs](https://en.wikipedia.org/wiki/Phase-out_of_incandescent_light_bulbs)

Shopfronts: [Stavanger, Kulturminneplan 2010 to 2025](https://www.stavanger.kommune.no/siteassets/samfunnsutvikling/planer/kommunedelplaner/kulturminner/kulturminneplan-stavanger-2010-2025-tekstdel.pdf) · [Byantikvaren Oslo, sign guide 2012](https://www.oslo.kommune.no/get-file/111661/2399dbe645dc9e7e4c04839c1bd2ec1e2bf28fd70480dee35be501babf5e9871) · [Lennie 2012, shopfronts](https://www.buildingconservation.com/articles/shopfronts/shopfronts.htm) · [Norges Kooperative Landsforening](https://no.wikipedia.org/wiki/Norges_Kooperative_Landsforening) · [Rimi](https://no.wikipedia.org/wiki/Rimi_(Norge)) · [Rema 1000](https://no.wikipedia.org/wiki/Rema_1000) · [Kiwi](https://no.wikipedia.org/wiki/Kiwi_(dagligvarekjede)) · [SNL, dekoratør](https://snl.no/dekorat%C3%B8r)

Signs and lettering: [Ghost sign](https://en.wikipedia.org/wiki/Ghost_sign) · [Ghostsigns](https://ghostsigns.co.uk/about) · [Enamel sign](https://en.wikipedia.org/wiki/Enamel_sign) · [Emailleschild](https://de.wikipedia.org/wiki/Emailleschild) · [Cathrineholms Jernværk (SNL)](https://snl.no/Cathrineholms_Jernv%C3%A6rk) · [Enamel plate by Dold (DigitaltMuseum)](https://digitaltmuseum.org/021028575721) · [Vitrolite](https://en.wikipedia.org/wiki/Vitrolite) · [Neon sign](https://en.wikipedia.org/wiki/Neon_sign) · [Freia (lokalhistoriewiki)](https://lokalhistoriewiki.no/wiki/Freia_sjokoladefabrikk) · [Egertorget (lokalhistoriewiki)](https://lokalhistoriewiki.no/wiki/Egertorget) · [Poly(methyl methacrylate)](https://en.wikipedia.org/wiki/Poly(methyl_methacrylate)) · [Sign painting](https://en.wikipedia.org/wiki/Sign_painting) · [Sign Media on Gerber's SignMaker](https://www.signmedia.ca/wide-format-printing-how-the-sign-industry-was-revolutionized/2/) · [Skiltmaler](https://no.wikipedia.org/wiki/Skiltmaler) · [Typografi.org, typeface chronology](http://www.typografi.org/skriftkronologi/skrift_kron.html) · [Futura](https://en.wikipedia.org/wiki/Futura_(typeface)) · [Helvetica](https://no.wikipedia.org/wiki/Helvetica) · [SNL, Trafikkalfabetet](https://snl.no/Trafikkalfabetet) · [Vinmonopolet](https://no.wikipedia.org/wiki/Vinmonopolet) · [Coop Norge](https://no.wikipedia.org/wiki/Coop_Norge) · [Narvesen (lokalhistoriewiki)](https://lokalhistoriewiki.no/wiki/Narvesen) · [Statoil](https://no.wikipedia.org/wiki/Statoil) · [Stavangeren 2/1998](https://byhistoriskforening.org/wp-content/uploads/2022/01/Stavangeren.Nr_.2.1998-ASL.pdf)

Records on the street: [Stortingsvalget 1989](https://no.wikipedia.org/wiki/Stortingsvalget_1989) · [Flyposting](https://en.wikipedia.org/wiki/Flyposting) · [Stavanger Aftenblad](https://no.wikipedia.org/wiki/Stavanger_Aftenblad) · [Rogalands Avis](https://no.wikipedia.org/wiki/Rogalands_Avis) · [VG](https://no.wikipedia.org/wiki/VG) · [Graffiti (lokalhistoriewiki)](https://lokalhistoriewiki.no/wiki/Graffiti) · [Graffiti i Norge](https://no.wikipedia.org/wiki/Graffiti_i_Norge) · [Graffiti (Norwegian Wikipedia)](https://no.wikipedia.org/wiki/Graffiti) · [Advertising column](https://en.wikipedia.org/wiki/Advertising_column) · [NuArt Festival](https://en.wikipedia.org/wiki/NuArt_Festival) · [Pøbel](https://no.wikipedia.org/wiki/P%C3%B8bel_(kunstner))

Game craft: [van Dongen 2008, Interior Mapping (CGI)](https://www.proun-game.com/Oogst3D/CODING/InteriorMapping/InteriorMapping.pdf) · [van Dongen 2018, interior mapping (Game Developer)](https://www.gamedeveloper.com/programming/interior-mapping-rendering-real-rooms-without-geometry) · [Persson (Humus), Interior Mapping demo, 2008](http://www.humus.name/index.php?page=3D&ID=80) · [Willmott, From AAA to Indie: Graphics R&D, 2013](https://www.andrewwillmott.com/talks/from-aaa-to-indie-graphics-r-d) · [Unity discussions, interior mapping (Golus on Persson's and Willmott's methods; secondary)](https://discussions.unity.com/threads/interior-mapping.424676/) · [Shadows of Doubt devblog 13](https://colepowered.com/shadows-of-doubt-devblog-13-creating-procedural-interiors/) · [Cities: Skylines asset editor](https://skylines.paradoxwikis.com/Asset_Editor) · [Courrèges, GTA V graphics study, part 2](https://www.adriancourreges.com/blog/2015/11/02/gta-v-graphics-study-part-2/) · [Lagarde 2012, parallax-corrected cubemaps](https://seblagarde.wordpress.com/2012/09/29/image-based-lighting-approaches-and-parallax-corrected-cubemap/) · [How Night City was built (80.lv)](https://80.lv/articles/interview-how-cyberpunk-2077-s-night-city-was-built-almost-entirely-by-hand/) · [Lettermatic, Pentiment](https://lettermatic.com/custom/pentiment) · [Green 2007, Improved alpha-tested magnification](https://steamcdn-a.akamaihd.net/apps/valve/2007/SIGGRAPH2007_AlphaTestedMagnification.pdf) · [msdfgen](https://github.com/Chlumsky/msdfgen) · [Disco Elysium, from render to paintover (GameBanshee)](https://www.gamebanshee.com/news/121823-disco-elysium-from-render-to-paintover.html) · [Boris the Brave, Oatmeal spice](https://www.boristhebrave.com/2026/07/05/oatmeal-spice/)

Unity: [URP decals](https://docs.unity3d.com/6000.0/Documentation/Manual/urp/renderer-feature-decal.html) · [URP decal renderer feature reference](https://docs.unity3d.com/6000.0/Documentation/Manual/urp/renderer-feature-decal-reference.html)

In this repo: `wooden-town-architecture.md`, `house-changes.md`, `kits-and-generation.md`, `materials-at-scale.md`, `lighting-and-colour.md`, `performance-at-scale.md`, `history-in-things.md`, `interface.md`, `town-change.md`, `docs/building-system.md`, `docs/living-fabric.md`, `docs/foundations.md`, `docs/engine-requests.md`, `blender/resolver/resolve.py`, `unity/Assets/Code/Scenes/TownLights.cs`, `unity/Assets/Shaders/StreetSurface.hlsl`, `fixtures/lt1-street.json`.
