# Inputs 5: buildings, fronts and time

A digest of three studies for the building-blocks architecture (`docs/plan.md`, What the architecture decides). It decides nothing. It sets out the evidence so Monday's Fable session can decide from it.

The studies, and the short names used below:
- *Architecture*: `docs/research/wooden-town-architecture.md`, a subject study;
- *Fronts*: `docs/research/fronts-windows-and-signs.md`, subject and craft;
- *Time*: `docs/research/time-on-screen.md`, craft.

Claims about our code were checked at commit `60f61bd`.

## 1. Wooden town architecture

### In short

- Stavanger stayed timber: clad log boxes, in rings dated by style, oldest at the harbour (The story in short).
- Nine local styles, five to fifteen years behind Norway's dates, each with its marks for body, roof, eaves, windows, trim, cladding, chimney and colour (§1).
- Construction by era: dated cladding profiles, Heng's measured window surrounds (16 to 20 parts), roofs, chimneys, gutters, plinths on the slope (§2).
- Colour from 47 houses scraped back by the 2025 colour guide. The whites were many. Windows were dark to about 1910. Small houses had white fronts over earth-coloured backs. Gamle Stavanger turned white only after 1956 (§3).
- For the generator: eleven era shelves in millimetres, fifteen construction rules, the corner's five houses in their first eras, twelve parts ranked by how much of the read they carry, and changes to `eras.py` (What the house generator should take).

### Against the bar

- **Sources:** primary sources were read where they open: the city conservator's guides, the culture plan, the colour guide, Sjøhusrekken 1993, Heng 2015 and 2020, and the Mandal and Trondheim guides. Marks are used consistently.
- **Concrete:** in millimetres and rules, which suits a subject study. The craft side lives in the kits and materials studies.
- **Its claims about `eras.py` hold:**
  - classical: mansards 30 per cent of the time, a 2850 storey, a 300 eave;
  - chalet: a pitch of 45° to 52° (`eras.py` lines 13 to 33).

  `stronger` multiplies pitch by 1.3 (capped at 62°) and eaves by 1.7 (`building.py` lines 286 to 292). A wrong base is therefore amplified, which is why the study lowers the bases.
- **Thin:**
  - opening sizes, all working values (§2, Windows by era);
  - Stavanger's pitches and eaves (Trondheim and Mandal measures only);
  - storey heights from sveitser on;
  - lettering by decade (§4; superseded by Fronts §5);
  - paint ageing on this coast (search budget ran out);
  - the 1904 masonry zone.
- **Verdict: meets the bar, with gaps that change no architecture decision.**
  - Sizes, pitches and eaves are values in the pack's metrics table, which the architecture makes data (`plan.md`).
  - They do block the first final window part in step 2, because windows rank first and the push scales them.
  - A gap-closing pass belongs before step 2. It measures openings, pitches and eaves per era from Stavanger byarkiv's photographs and Heng's 1:10 poster. Downloads need Øystein's OK.

### Decisions it proposes

| What | Why | Cost | Depends on | Status |
| --- | --- | --- | --- | --- |
| New shelves: rule house, sveitserjugend, nyklassisisme, Tyrolean and colonial, sea house, cannery. Classical with no mansards, eaves near 100 mm and a storey of 2500 to 2600 mm. Chalet pitch 38° to 45° | Proposed changes to `eras.py` | data, plus a fixture hash migration | the metrics table format | open; values unverified |
| Cladding dated by the year it went on, per facade. Fronts were reclad first; gables and yards keep the first skin | rule 2; §2, Cladding | a surface record per facade (today one `cladding` per volume; `resolve.py` line 136) | dated records widened to wall surfaces | open |
| The window surround as its own part with its own era. It usually went with the window | rule 4; parts, rank 1 | one record per opening | Fronts' window records | open; no home yet (§5, 2) |
| Arks, porches, lean-tos and WC additions only from diary events | rule 12 | none | the event vocabulary | follows the fact rule |
| The plinth takes the slope. A stair goes when the door moves down | rules 9 and 10 | reuses stone kinds | the land (1d), stairs | open |
| Status by side. Dark windows to about 1910. Protected streets white after 1956 | §3; rule 5 | the coat stack per facade | the paint-coat stack | open; 1956 is a town-system fact |
| Twelve parts ranked: windows and surrounds, roofs, eaves, cladding, chimneys, doors, plinths, coats, A's shopfront, gutters, additions, ornament | Parts for plan step 2 | none | none | orders step 2 |
| A in timber or rendered brick. E with an ark and a white front | The corner's five houses | a fixture edit | none | addressed to Øystein. They are authored facts, likely ours now (`NOW.md`, Decided) |

## 2. Fronts, windows and signs

### In short

- A street window is four records, each with its own owner and clock: the opening (structure), the sash and glass (skin), the dressing (household), and the room and its light (the hour) (The idea; §8).
- Glass dates by its reflection: crown, cylinder to 1928, drawn to the late 1960s, then float. One normal per pane carries it (§1).
- Interior mapping is cheap and solved, but every game picks rooms at random. Ours reads a room record with a box from the plan (§2).
- Lit windows follow the household's day, and none is a real light. Their spill comes from a tile-binned buffer (§3; §7).
- A sign is a record: method, maker, year, coats, a removal mark. Street records layer and may be wrong. Text has a headline for the street stop and a body for eye level (§5; §6).

### Against the bar

- **Sources:**
  - read in full: van Dongen 2008 with its numbers, Humus, Lagarde 2012, Courrèges, Green 2007, the Unity 6 decal docs;
  - read: the Norwegian museum, SSB and SNL pages, and Oslo's 2012 sign guide;
  - secondary: Willmott's SimCity method, known only through Golus.
- **Concrete:** opaque only for the M4's tile GPU, Forward+'s cap, decals on tile GPUs, and text in pixels at 1440p (§6; §7). Frame costs are estimates ("to be measured"). The 1 ms budget is a proposal.
- **Thin:**
  - how shipped open-world games draw rooms, signs and old glass (Gaps);
  - SSB's hourly tables;
  - Norwegian dates for the Advent arch, kitchen tubes and cut vinyl;
  - shopfronts (§4).
- **One claim needs care.** "The heart already holds 403 lights against Forward+'s 256" (six findings, 4). But 256 caps the lights each camera sees, and how many each camera sees is unmeasured (`lighting-and-colour.md` lines 75 and 232). The proposal stands, because windows will number in thousands.
- **Overturned:** the Norwegian-signs recommendation (§6, last paragraph; For Øystein 2). Signs and street text are in English (`NOW.md`, Decided).
- **Verdict: meets the bar, with gaps that change no architecture decision.**
  - The architecture needs the records and what parts carry, not the shader technique.
  - The missing games would choose between atlas, cubemap and plane interiors in step 2, and all three read the same room box.
  - A gap-closing pass belongs before step 2. It reads Willmott's slides, City Sample's interior docs, one shipped account of wavy glass, and SSB Statbank 14320.

### Decisions it proposes

| What | Why | Cost | Depends on | Status |
| --- | --- | --- | --- | --- |
| The window as four records. The opening is never deleted. The fills are a list, with the inner window and each pane's glass kind and year. Dressing carries the year hung. The room is a reference | §8; What we should do, 1 | 2 to 3 days in the resolver plus a hash migration; overlaps kits item 4 | dated cells | open; the core input |
| A room record: building, floor, box in mm, its windows, kind, household or business, year fitted, lamps. Split by rule per era until step 8 | §8, The room behind each window | inside the above | homes (#59) | open; `derived` until homes come |
| A sign record with its own events (`sign_put_up`, `sign_relettered`, `sign_taken_down`), apart from the business. It holds socket, method, maker, text, letter style, light and hours, coats, removal mark and claims | §8, The sign; §5 | inside item 1 | dated sockets; the words layer | open; the text is now English |
| Street records as a coat stack, each with maker, date and claims | §8 | about 2 days | engine request 9 | open |
| No window or shop is a real light. Spill comes from a tile-binned buffer or decals | §3; What we should do, 2 | about 2 days | lighting item 8 | open; clashes with `TownLights.cs` |
| One opaque window shader: Fresnel, SSR then a box probe, a bend per pane, the interior from the room box, dressing layers, emission by lamp kind | §1, Our glass; What we should do, 3 | 4 to 6 days | the room box as instance data | step 2 |
| The household's day as rules. `lit` per room and per hour | §3; What we should do, 4 | 1 to 2 days | habits (#22) | open; per floor today (`lt1-street.json` line 1432) |
| Readable text only from records. Elsewhere, marks, not words | §6; §8 | none | none | follows the fact rule |

For Øystein 1, 3 and 4 (how much room shows, how strong old glass is, the television's flicker) are look questions, now ours (`NOW.md`).

## 3. Time on screen

### In short

- **Change is found only where something jumps.** An aligned toggle shows a change in under a second. A blank, a cut, a dissolve or a time-lapse hides it (bottom line; §6).
- **Hold everything but the year.** Viewers find three or four changes at a time, the meaningful ones first (§2; §6).
- **A cut invites a cause.** A frame where everything is new is the commonest period lie. Readers date parts, not pictures (§4; §6).
- **Eleven rules,** and a table of transitions scored against criteria 1, 3 and 4 (§7).
- **What the architecture needs** (§7, What the building blocks must carry):
  - the drawing as a hashed function of the record, the date and the view;
  - the date as an input;
  - lives as dated intervals;
  - lifespans;
  - a change query;
  - separate clocks;
  - seeds stable for a part's life.

### Against the bar

- **Sources:**
  - read in full: the perception papers (Rensink 1997, Simons and Levin 1998, Pomplun 2001, Heer and Robertson 2007, Martin 2023, Palermo 2012, Brockhoff 2016), the conservation charters and the Kenilworth plans;
  - secondary, and marked: art and games (§1; §5);
  - not read: Lynch, Tversky 2002, Suma 2011 (Gaps).
- **Concrete:** a date uniform; bakes storing the reset year and a rate; intervals from the yearly runner; `changes(scope, t0, t1)`; hash-based checks. It gives no figure for the memory of keeping an earlier chunk resident: "the memory is bounded" (§7, must carry 4).
- **Its own readings, marked as such:** the transitions table, and carrying the one, two, three budget across a jump.
- **Changed by later decisions:** its play recommendations (For Øystein 1 to 3) are now constraints on a creative exploration (`NOW.md`). The third, never marking the player's acts, is reopened.
- **Verdict: meets the bar; its gaps change no architecture decision.** The architecture items rest on a decided rule (`town-system.md`, For Øystein 2) and on primary perception findings. The gaps (swipes, cuts, changes per stylised view) bear on the exploration and on 1f, which measure them.

### Decisions it proposes

| What | Why | Cost | Depends on | Status |
| --- | --- | --- | --- | --- |
| The drawing = f(record, fabric date, light moment, weather, view, tier), hashed | must carry 1; rule 1 | inside the framework | the plan hasher, golden views | implements a decided rule |
| The date as a global. Bakes store the reset year and a rate per point | must carry 2 | 1 to 2 days, with the layer law | history maps; `history-in-things.md` | follows a decision; clashes with design docs (§5, 4) |
| Lives as dated intervals, written offline | must carry 3 | about 2 days | `life()` in `living-fabric.md` | open |
| Parts with lifespans. A comparison draws the shared instances plus the few parts alive at one date only | must carry 4 | inside the above | chunks and streaming (the scale test) | open; memory unknown |
| `changes(scope, t0, t1)`: cause, actor, provenance, precision, weight, parts, region per view; drift as magnitudes | must carry 5 | about 2 days | lifespans; picking | open |
| Separate clocks: fabric year, day of year, the hour as the sun's position, weather | must carry 6 | about 1 day (`LT1Years`) | the sky model (1c) | open; `LT1Years` does not exist yet |
| Seeds by part id, a new id when a part is replaced. A diff check fails any pixel outside the change list | must carry 7 | about 1 day | stable ids | open |
| Watched or jumped: step month by month to a date, jump there once, compare hashes | must carry 1; What we should do, 5 | about 1 day | the above | tests a decided rule |
| An actor and a precision on every event; the age mix measured per frame | must carry 9; rule 8 | hours, plus an engine request | the engine | open |

## 4. What every part or thing must carry

**Buildings** (Architecture):
- the era shelf and the installing event (both exist per part today);
- its material and covering, by era and wealth, with source and working;
- for cladding: profile, year applied, facade or scope, and corner type (boxed or mitred);
- for a window: its surround as a separate dated part;
- for a roof: form, pitch, eaves and verges, and covering; a change of covering is an event;
- coats per facade, with the front-and-back status rule;
- for the plinth: its height on each side of the slope;
- its fit, and what removing it leaves.

**Fronts** (§8; `kits-and-generation.md` §5):
- the opening: facade, cell, size, year and cause;
- the fills as a list: sash era, event and fit; the inner window; each pane's glass kind and year;
- the dressing stack, each layer with the year hung and its state for the hour;
- a room reference that resolves to a box, kind, household, year fitted and lamps, as instance data that survives merging;
- whether each room is lit at each hour, its lamp kind and the television; a spill entry and a light socket (`lighting-and-colour.md` line 203);
- for a sign: socket, method, maker, event, English text, letter style, light and hours, coats, state, removal mark and claims;
- for a socket: accepted parts, its edge reference, and its history of parts and the marks they left;
- a provenance, one of the five kinds (Fronts §8, table).

**Time** (§7):
- a stable part id and seed for its whole life, and a new id on replacement;
- a lifespan: made and removed, each with its event;
- life intervals: construction, material, origin, reset years and rates;
- history as a reset year and a rate per point, never as years since;
- an actor and a precision on its events, and the weights the budget reads;
- its region in each named view;
- a pick id that survives merging and instancing (`plan.md`);
- the same tier and seed at both dates of a comparison unless the record changed it.

## 5. Conflicts and overlaps

1. **The resolver deletes openings; all three studies say never delete.**
   - `_shop_fitted` filters window cells out of `plan["cells"]` (`resolve.py` line 427).
   - Kits: "`_shop_fitted` stops deleting cells" (item 4). Fronts: the opening is "never deleted by a later event" (§8). Time: parts carry lifespans.
   - The code also keeps one `original` only (lines 387 and 388), so a window replaced twice forgets the middle. And the sign has no record: `business_closed` moves the business into `ghosts` (line 82).
   - Kits' dated cells, Fronts' window records and Time's lifespans are one structure seen three ways.
2. **The surround has no home.** Architecture makes it a part (rule 4); Fronts' four layers omit it. House C in 1971: "the old heads gone. The small attic window high in the gable keeps its surround."
3. **Wall surfaces are not dated.** Architecture: "the original cladding survives on gables, towards yards and in alleys" (rule 2). The code has one `cladding` per volume. Neither kits nor Fronts dates surface regions.
4. **The date is baked in today's design docs.**
   - Time: "the living fabric bakes the life into city-tier vertex data ... pass the fabric date as a global" (§7, must carry 2).
   - `living-fabric.md` (Tiers and performance) bakes into vertex data.
   - `building-system.md` (Resolution, 5) says the shader reads "years since it was applied".
   - The plan's "history as a function of the record and the date" agrees with Time.
5. **Two budgets, the same numbers.**
   - `living-fabric.md` budgets "one ... two ... three", provisional "until the corner's years sheet sets them".
   - Time applies the same numbers across a jump.
   - The corner's 1960-to-1989 pair already holds about seven changes (§6), so 1f tests the rule to split or coarsen.
6. **Lights.** `TownLights.cs` makes every lit shop a spot light (lines 75 to 81). Fronts' spill buffer and the lighting study's light sockets ("windows (spill position, direction, cookie)") are one record that needs one definition.
7. **Language.** Fronts: "Norwegian signs stay Norwegian ... Fonts must carry æ, ø and å" (§6). The decision is English, but its reach is unstated:
   - the fixtures' business names are Norwegian ("Vik Jernvare", "Larsen Kolonial", "Kaffebrenneriet");
   - Fronts' 1989 chains are real firms (§5);
   - street names carry ø.
8. **The player's mark.** Time: "Nothing in the world marks it as the player's" (§7). `NOW.md` reopens this. The guard stays, because it follows the decided rule: "the fabric's condition never depends on whether anyone watched".
9. **Repetition.** The rule is "nothing repeats unless it was factory-made" (`NOW.md`).
   - Heng's System 2 surrounds were factory-made, "identical across whole streets", so they may repeat.
   - Fronts' room atlas is "a few rooms per kind, era and class", and rooms are not factory-made. How many variants keep the rule is open.
10. **A seeded roof claims history.** Classical houses roll a mansard 30 per cent of the time (`eras.py` line 16). Architecture says "no source shows mansards on Stavanger's classical houses". On D or E it would read as a roof raise the record does not hold.
11. **One id for three needs.** The plan's picking ("pickable back to its record, even when merged or instanced"), Fronts' room box and Time's regions all need it. The interface study is not yet in.

## 6. Unknowns, and what step 1f needs

| Unknown | Learned where |
| --- | --- |
| Opening sizes; Stavanger's pitches and eaves | archive photographs before step 2 (Øystein's OK) |
| The window shader's cost on the M4 | the harness, the heart at night (Fronts, look test 6) |
| How many lights each camera stop sees | the harness |
| The memory of two chunk versions in a comparison | the scale test, then step 4 |
| How many changes a stylised view carries | the gully's years strip, and 1f |
| Whether a toggle or a swipe reads in motion | people only, in the engine's human test |
| Whether clay dates at all (it keeps windows, roofs and the shopfront, and loses coats and colour) | 1f |
| Households and lit rooms | engine #59 and #22; `derived` until then |

### The corner's five houses

| House | Fixture | Diary | 1935 / 1960 / 1989 / 2020 |
| --- | --- | --- | --- |
| A, 104 | `lt1-corner.json` | 1912 jugend; shop and ironmonger 1931; repainted 1949; closed 1974; café 1988 | ironmonger / repainted / café / no change |
| B, 105 | `lt1-street.json` only | 1936 funkis; repainted 1987 | nothing recorded / new / repainted / no change |
| C, 1203 | `lt1-corner.json` | 1879 chalet; windows 1971 | no change / no change / husmorvinduer / no change |
| D, 1107 | `lt1-corner.json` | 1828 classical; lean-to 1950; street windows 1965; boarded and neglected 1986 | no change / lean-to / windows, boarded / no change |
| E, 304 | `lt1-corner.json` | 1826 classical; street windows 1965 | no change / no change / windows / no change |

What the diaries lack for a time test:
- **B** is missing from the corner fixture. Its fire (`docs/experiments.md` line 106) has no earlier house, and there is no fire event in the vocabulary. A 1935 frame with an empty plot is a claim.
- **Nothing after 1988.** D stands boarded through 2020. `town-system.md` (For Øystein, 3) asks for "a handful of items".
- **No reversal.** Time says 1960 "matters most as the third point, where reversals show", but none of the five holds one.
- **Uneven changes.** There are three from 1935 to 1960 and about seven from 1960 to 1989.
- **No sign record.** A's sign comes from `plan["business"]` (`building.py` lines 604 to 626).
- **Check D's and E's roofs** for a seeded mansard (conflict 10).
- **No households** (`"lit": []`). The fabric-only arm needs none.

### Constraints on any way of showing time

From Time §7, rules 1 to 11, now constraints:
1. Every pixel difference comes from the record.
2. Hold the camera, tier, day of year, sun and weather; name any change of season.
3. A cut, dissolve, fade or time-lapse is followed by an aligned comparison at the spot.
4. Every jump is dated at the record's precision.
5. Point at no more than the budget, from the change query, never from a picture difference.
6. No cause by juxtaposition, and no morph between unrelated things.
7. Every year is mostly older than itself; measure the age mix.
8. Light of the date, never a grade for the era.
9. Something recurs across every jump.
10. Absence must be true too.
11. Watched or jumped, the town draws the same (decided).

### Controls and pass marks

From Time §7, The corner through the years:
- **Tasks:** order and date the frames; say what changed and why; say what happened here.
- **Controls:** another season, the camera half a metre off, a false cause, and the shuffled-facts and layers-off controls of `docs/foundations.md`.
- **Pass when:**
  - four readers in five order every view right;
  - frames are dated within a decade where a dated part is in view;
  - two of three budgeted changes are found per pair at the street stop;
  - the controls draw fewer than one false change per frame;
  - the direction is right between every pair.
- **Tools:** named cameras as data; fabric year and moment as separate inputs (`LT1Years`, not yet built).
- **The readers' key** could start as a diff of plans resolved at two years, since `resolve()` already reads a diary up to a year.
- Model readers see stills only.

## Across the three

**Before the first final house part,** the generator must carry everything in §4. The urgent core is 2 to 3 days in the resolver with one fixture migration (Fronts, What we should do, 1; kits item 4):
- openings never deleted;
- fills as lists, with surrounds and panes;
- dated sockets and signs;
- dated wall surfaces.

Next come room boxes, part ids with lifespans, and actor and precision on events. Then the `eras.py` corrections and the measured opening sizes.

**How the houses should start.** The studies point to this order:
1. 1f in clay on today's generator, after the fixture gaps above are closed (B and its fire, events after 1989, one reversal at least).
2. The records.
3. The measured sizes.
4. The window and its surround as the first final part (Architecture, Parts for plan step 2).

The plan's House A is the hardest test of the records: a shop over openings, a sign, a ghost and a lit shop. C or D tests the windows with the fewest records.

**The three questions for Fable:**
1. **One dated record.** Are kits' dated cells, Fronts' window with its surround, Architecture's dated surfaces and Time's lifespans one structure? If so, at what grain: opening, surface region, socket or pane? It fixes the migration and every part's definition.
2. **The date as input.** Does history live as a reset year and a rate per texel, read against a global date at every tier? That replaces the vertex and years-since bakes in `living-fabric.md` and `building-system.md`. And how does a comparison hold both versions of a changed chunk? That half waits on the scale test.
3. **What a drawn piece keeps after merging.** It needs a record id for picking and for change regions, and the windows need a room box, glass per pane and lit state. Which of these is instance data and which is texture, at each tier? Fronts, Time and the interface meet the distance levels here.
