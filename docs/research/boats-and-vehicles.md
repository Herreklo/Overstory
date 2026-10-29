# Boats and vehicles

Stavanger's harbour and streets, 1870 to 2020 (1989 in most detail), and how games make boats sit and cars park and drive cheaply, costed on the M4. 29 October 2026. It builds on `what-moves.md` (the 1980s fleet, sjark, snekke), `animation-and-motion.md` (hull points, tide) and `land-rock-and-water.md` §3, and does not repeat them. Lamps, quay fittings, fences and animals have their own notes. Marks: (unverified) means no source confirmed it; (secondary) means a forum, guide or summary; (ours) means our own arithmetic.

## In short

1. **The harbour changes kind by decade, and each change is dated.** DSD's white boats with yellow funnels came from 1948, the hydrofoil in 1960 and the Tau car ferry from 1961 to 2019. The England boat ran until 2008 and a small-boat guest harbour opened in the late 1980s. In 2019 there were 234 cruise calls, and a plan moves the big ships out of the inner harbour by 2030. One view of the Basin across the years is the test.
2. **The 1989 street is old cars, with their rust left on the road.** Periodic inspection began only in 1998. The buses started and ended their routes at the square. Electric cars in Stavanger went from 2,398 in 2016 to 10,758 in 2020. Parking history, liveries and 1980s boat brands are not online.
3. **In a 0.1–0.3 m basin a moored boat hardly heaves.** Its hull points average out waves shorter than the boat (ours). What reads is the boat swinging on its lines in the wind, the tide lifting it along the quay wall, and the boats rocking as a ferry's wake passes. All three are facts computed from the clock.
4. **Shipped games move boats and cars without physics.** Boats sample the drawn wave sum at a few points (Boat Attack, Assassin's Creed III). Cars follow their lanes, with wheel angle = distance / radius. Both are exact at any time jump.
5. **Well under 2 ms, if three rules hold.** Draw them through the Resident Drawer, with the user value instead of property blocks. Cast shadows only from coarse levels, near. At night, use real lights for the nearest two cars and sprites beyond that (GTA V). Cities: Skylines II spent 40 of its 88 ms on shadows.

## Boats, 1870 to 2020

| Year | On the water | Source |
| --- | --- | --- |
| 1855–1948 | DSD founded in 1855; its mark from 1903 is three red rings on the funnel; from 1948 "the white fleet", white hulls with yellow funnels | no.wiki |
| 1920 | Fishing boats carry a mark on each side of the bow: county letter, number, municipality letters (N64Ø). Rogaland is R (unverified); Stavanger's letters were not found | lokalhistoriewiki |
| 1954–1970 | Glass fibre: Ancas from 1954, Fjord Plast from 1960 (over 2,000 Fjordling 17s from 1962); around 1970 southern Norway was Europe's largest maker of plastic boats | lokalhistoriewiki |
| 1960, 1961 | Hydrofoil *Vingtor*, Norway's first fast-boat route; the first Tau car ferry | no.wiki |
| 1986 | Oil at $8, hard for every shipowner; laid-up supply ships near Stavanger not found | [secondary](https://www.shipsandoil.co.uk/storfonn) |
| late 1980s | A guest harbour for small boats at the Basin's head | [secondary](https://www.geocaching.com/geocache/GC1W8JV) |
| 1989 | Norway Line's *Jupiter*, Bergen–Stavanger–Newcastle | en.wiki |
| 1990 | TBT antifouling first banned; by 2001 banned on boats under 25 m | Miljødirektoratet; TU |
| 2003, 2014 | An aluminium catamaran car ferry; gas ferries on the Tau route | no.wiki |
| 2008 | The England boat ends | en.wiki |
| 2019 | 61,466 calls: 85% ferries and fast boats, 11% supply and cargo; 234 cruise calls. Offshore traffic uses the outer bases, not the Basin. The Tau ferry ends with the Ryfylke tunnel | SNL; Storting |
| 2024–2030 | Cruise ships moved out of the inner harbour: at most 2 calls a day and 7 a week; shore power by 2027 | Stavanger havn |

**At the berth.** A boat at the quay tells where its owner is: the fisher's trips, a ferry's timetable, a leisure boat's summer. World 9989 already has "a boat of her own" with its date, "is out on the boat every weekend", and "the harbour fleet" with six fishers. Kind, size, berth and new or used are still requests 11 and 17. In 2022, 26.1% of households owned a leisure boat; 1989 was not found. Common practice, not found online (unverified): working boats alongside on fenders with slack lines for the tide; small boats bow-to a pontoon with a stern buoy, or on a swing mooring; open boats laid up ashore under tarpaulins in autumn and painted in spring. A hull ashore shows its antifouling and tells the season; a sagging tarpaulin over years is upkeep made visible.

## Vehicles in the streets

- **Cars.** Periodic inspection began on 1 January 1998 (EEA; Storting 1993–94). Until then rust low on the body is a true 1989 sight; it thins after 1998 (ours). Vans and lorries (VW T3, Transit, HiAce, Volvo F, Scania) are unverified.
- **Buses.** Five trolleybuses ran from 1947 to 1963. S.O.T., formed in 1975, had 110 buses in 1985. The buses long started and ended their routes at the square (lokalhistoriewiki, undated). Kolumbus was founded in 2002. Liveries were not found.
- **Streets.** Kirkegata was announced in 1960 as Norway's first pedestrian street (secondary). Market trade on the square was cut back in the 1980s, and the square was rebuilt between 1999 and 2008 toward its pre-1960s look. Øvre Holmegate, the real Holm Street, closed to cars in autumn 2005. Skagenkaien closes to traffic in summer (secondary). When the quays were car parks was not found.
- **Bicycles.** DBS bikes were made by Øglænd in nearby Sandnes. The name dates from 1932 and the millionth bike from 1952; Monark took over in 1990 (SNL; Jærmuseet). The local bicycle of 1989 is a DBS.
- **2016 to 2020.** Electric cars in Stavanger rose from 2,398 to 5,656 to 10,758, and public charging points from 148 to 193 to 492 (SSB). 54% of Norway's new cars in 2020 were electric.

## How games do it, and what it costs here

**Distances (ours).** At 35 mm and 1440p a metre is about 2,490/d pixels at distance d. At 120 m a Golf is about 83 px and a 9 m sjark about 190 px; at 35 m a car is about 285 px. A far car needs a true silhouette, not a card.

- **Boat Attack** (URP). Its non-physical `BuoyantObject` mode takes height from one sample and tilts toward the wave normal, with no forces; its heights come from CPU jobs. That is our moored boat, with three or four points.
- **Assassin's Creed III** (fxguide). Four buoyancy spheres per side, split by side for roll; gunwale probes fire spray on moving ships; the wake is a cheap particle reveal.
- **Dredge** (Unity talk). Gerstner crests "launched" the boat, so the team used sines, which give exact height at (x, z). On our Gerstner sum, iterate, or accept an error of about Q·A: centimetres.
- **Sea of Thieves** (SIGGRAPH 2018): contact foam from a depth comparison where the hull cuts the water; the rest is oversized here.
- **Open hulls.** HDRP hides the water inside a boat with an excluder mesh. In URP, decked hulls are sealed at the deck for free. Open boats get an invisible cap at the gunwale that writes stencil before the opaque water: one mask pass for all of them.
- **GTA V** (Courrèges). Distant headlights are instanced 32×32 quads: a far car is "two lights". LODs switch at about 15, 30, 70 and 140 m (secondary).
- **Cities: Skylines II** (Huhtala). It draws through BatchRendererGroup and sank on casters, because every object cast, and on props without LODs.
- **Deterministic cars (ours, unsourced).** Wheel angle = s/r. Roll ∝ v²κ from the lane's curvature, pitch from the scheduled dv/dt. Smoothing uses a fixed window (t, t−0.1 s, t−0.2 s), never a spring, so a time jump lands on the same pose. Parked cars are static, with their wheels baked in.

**Unity 6.6.** The Resident Drawer is off today and planned on (`docs/building-blocks.md`). It breaks under a MaterialPropertyBlock. So paint, wear and owner go through the user value into the facts buffer and history pages, as for kit parts, and wheels and roll go into child transforms for the ten or so moving cars. LOD Group's animated cross-fade does not fade under the Drawer (UUM-92402), so use Mesh LOD, dithered.

| View (estimates, unmeasured) | Triangles, main + casters | Draws, Drawer on / off | CPU ms | GPU ms |
| --- | --- | --- | --- | --- |
| The Basin: 60 moored + 4 moving boats, lines, fenders, caps | ~100k + 40k | ~70 / 280 | 0.2–0.3 (10k sines in Burst + transforms) | 0.4–0.8 |
| A street: 80 parked + 8 moving cars + 2 buses | ~250k + 60k | ~100 / 280 | 0.1–0.2 | 0.5–1.0 |

**Our tiers (ours).** At most 5–6k triangles at L0, 1–1.5k mid, 200–600 far, enforced by the export tool. Mooring lines are 16–24-triangle strips bent in the vertex shader. Car glass stays opaque and dark so it instances. The risk is close glossy bodies on a frame already over budget: judge by the harness's delta, not triangles.

## Worth prototyping

1. **The berth, moved by facts.** One sjark and one færing at the quay in grey. Hull points sample the water's own sum. They yaw on slack lines in the shared wind, and the tide lifts them along the wet band. A passing ferry's wake is a packet added to the sum, and the boats rock in turn as it reaches them. *First test:* a Burst job and two box-blocked hulls. Two 10-second clips at the street stop and 35 m, beside a harbour reference: does it float, and does the wake read as a cause? Then 60 instances on the harness, with the Drawer on and off.
2. **The parked street from records.** Kerb slots as sockets on the street of 107–109. Each car comes from a record (owner, purchase year, wealth, garaged or not): one blocked 1989 car family, worn by age and salt through the history pages. *First test:* one grey still with six cars, at the street stop and 120 m. Two cold readers say who is home, who has money and who bought after 1986, scored against the records.
3. **Timetabled movers at night.** The Penny Ferry and one bus, each posed from its timetable and the clock. Lamps are emissive. A glint card on the wet street is stretched toward the camera and scaled by wetness. The nearest two cars get a real unshadowed spot, and sprites take over beyond 50 m. *First test:* one blue-hour still of the quay road with a car and the ferry; ±10 minutes must give identical frames; time the delta on the harness.

## Gaps

Not online (probably in the town archive, *Stavangeren* and digitaltmuseum captions): boats selling at the fish market, Stavanger's boat letters, a 1986 lay-up of supply ships, pontoons, bus liveries, parking on the quays, the 1980s plastic boats, lay-up practice. Every cost here is unmeasured.

## Sources

[DSD](https://no.wikipedia.org/wiki/Det_Stavangerske_Dampskibsselskab) · [Ryfast, Storting](https://stortinget.no/globalassets/pdf/innstillinger/stortinget/2023-2024/inns-202324-386s-vedlegg.pdf) · [England boat](https://en.wikipedia.org/wiki/Newcastle%E2%80%93Bergen%E2%80%93Stavanger_ferry) · [SNL, the port](https://snl.no/Stavangerregionen_havn_IKS) · [Cruise plan](https://www.stavangerhavn.no/wp-content/uploads/Handlingsplan-cruiseanlop-Stavanger-sentrum-2022-2030_Godkjent-av-styret-i-SRH-21.06.23.pdf) · [Vessel marks](https://lokalhistoriewiki.no/wiki/Registreringsnummer_for_fartøy) · [Fjord Plast](https://lokalhistoriewiki.no/wiki/Fjord_Plast) · [TBT](https://www.miljodirektoratet.no/nye-temasider---ansvarsomrader/ny---miljogifter-og-andre-prioriterte-stoffer/ny---tbt-og-andre-organiske-tinnforbindelser/) · [TU](https://www.tu.no/artikler/bunnstoff-sparer-liv/272758) · [Boat survey 2023](https://www.statsforvalteren.no/contentassets/392d676416b3418ebe8c8dc7904d0126/nasjonal_rapport_batlivundersokelsen_2023.pdf) · [Torget](https://lokalhistoriewiki.no/wiki/Torget_(Stavanger)) · [Trolleybuses](https://en.wikipedia.org/wiki/Stavanger_Buss-Selskap) · [S.O.T.](https://no.wikipedia.org/wiki/Stavanger_og_Omegn_Trafikkselskap) · [Øvre Holmegate](https://www.fjordnorway.com/no/attraksjoner/fargegaten---ovre-holmegate) · [Kirkegata, secondary](https://voicemap.me/tour/stavanger/storied-stavanger-a-walking-tour-through-the-old-town/sites/mauritzengarden-and-kirkegata) · [Inspection, Storting](https://stortinget.no/no/Saker-og-publikasjoner/Publikasjoner/Innstillinger/Odelstinget/1993-1994/inno-199394-029/2/) · [Øglænd](https://snl.no/Jonas_Øglænd_A/S) · [SSB, electric cars](https://www.ssb.no/transport-og-reiseliv/landtransport/artikler/19-elbiler-per-ladepunkt/tabell-1.elbiler-og-allment-tilgjengelige-ladepunkt.personbiler.hele-landet-og-utvalgte-kommuner.2020-2018-og-2016) · [Boat Attack](https://github.com/Unity-Technologies/BoatAttack/blob/master/Packages/com.verasl.water-system/Scripts/BuoyantObject.cs) · [AC3](https://www.fxguide.com/?p=38193) · [Dredge](https://unity.com/resources/crafting-dredge-cozy-atmospheric-horror) · [Sea of Thieves](https://history.siggraph.org/?p=84316) · [Water Excluder](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@15.0/manual/WaterSystem-waterexcluder.html) · [GTA V](https://www.adriancourreges.com/blog/2015/11/02/gta-v-graphics-study-part-2/) · [GTA LODs, secondary](https://www.modding-forum.com/guide/1-lod-models/) · [CS2](https://blog.paavo.me/cities-skylines-2-performance/) · [Resident Drawer](https://docs.unity3d.com/6000.2/Documentation/Manual/urp/make-object-compatible-gpu-rendering.html) · [UUM-92402](https://issuetracker.unity.com/issues/15625/the-lod-group-crossfade-animate-cross-fading-feature-does-not-fade-when-the-gpu-resident-drawer-is-enabled)
