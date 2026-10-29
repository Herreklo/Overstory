# Street things

Research for the street things in `docs/systems.md`:
- lamps, handrails, quay furniture, fences, and the small marks that date a street in Stavanger's harbour town, 1870 to 2020;
- how games build them as kits, and what each approach costs in Unity 6 URP on the M4.

Written October 2026. Nothing here is decided.

How claims are marked:
- (secondary): from a reprint or a search summary;
- (unverified): no source confirmed it;
- a photo id is our reading of a Stavanger byarkiv picture, at `stavangerbilder.no/fotoweb/archives/5010-Foto/Indeksert/<id>.tif.info`.

## In short

- **Lamps.** The old town of 1989 had three lamp systems side by side: span-wire bells, wall brackets, and gas-era lanterns on dark cast-iron posts, lit by bare bulbs. The quays had 8 to 10 m steel poles. The town owned the lamps; its works kept them until Lyse took over in 1998.
- **Iron in stone.** Iron was set in stone with lead (rails) or with sulphur and sand (bolts), and it rusts first at that joint. Rails of the 1980s stopped with the flight; since 2009 they run on both sides and past the end steps.
- **The quays of 1989.** They were stone block walls of about 1900, with black tyres along the face, low yellow bollards and no railing.
- **Lighting a street.** Spider-Man lights a street with two dynamic lights. Each lamp has a wide baked light, plus a tight runtime light that switches on within 30 m and casts shadows within 15 m.
- **Ageing iron.** Painted iron ages by one value in the games that layer their materials. That value fits our Renderer Shader User Value.
- **Costs.** Unity publishes no timings on Apple GPUs, so every cost below is an estimate until `tools/check.py` measures it.
- **What to test first.** The Landing lantern's reach, built three ways, in one still.

## The subject

### Lamps

| Years | Light | Form | Owner, keeper |
| --- | --- | --- | --- |
| to 1866 | oil | a few lanterns at the quay edge of the square | the town (secondary) |
| 1866 to about 1918 | gas: open flame, then mantles | four-sided lanterns on cast-iron posts, about 3 to 3.5 m high (the lighters' ladder was 3.5 m); 150 in 1866, 362 in 1900 | Stavanger Gascompani, then the town by 1900; the town's lamplighters walked rounds (secondary) |
| from 1909 | incandescent | the same posts, wall brackets, span wires; 2,000 in 1931, 18,723 in 1986 (secondary) | the town's Elektrisitetsverk |
| about 1945 to 2015 | mercury, greenish | road fittings (secondary) | |
| from the 1980s | high-pressure sodium, about 2,200 K (secondary) | grey poles of 8 to 10 m with short arms on the quays (BySt020_Ud_0380, _0387, 1989) | Lyse from 1998 |
| 2017 to 2020 | LED, dimmable | 6,500 Stavanger lamps renewed (secondary) | |

**The old town, 1981 to 1989.** What the photos show:
- bell fittings on span wires over Øvre Holmegate (BySt015_sefrak_031_012);
- a wrought-iron bracket holding a lantern at first-floor height (Kirkegata 6, _028_024);
- a swan-neck bracket holding a bare bulb (Urgata 8, _035_037);
- tapered lanterns on cast-iron posts with ladder bars, each with a bare bulb inside (BySt020_Ud_0490, _0241).

We could not find out what lamp the span-wire bells held.

**Keeping.**
- Time clocks switched the lamps on and off (1960, unread).
- In 2012, three dark lamps in a row in the centre had to be mended within a day. A single dark lamp could wait four weeks (secondary).

So a dark lamp tells you something about its keeper and its street.

### Handrails

- **Wrought to cast.** Cast iron replaced wrought iron through the later 1800s (secondary).
- **How rails were fixed.** Rails were cast into the stone with lead. Lead stays tight, allows a little movement and takes some of the rust's pressure. Rust starts at the joint, and goes faster where the steps are salted. A repair resets the rail in lead and gives it three coats of red lead. The source is Danish; we could not confirm the same practice in Norway. For what follows a loose rail, see `stone.md`.
- **The 1980s.** The public stair by Rosenkildehuset had slim black round rails: one down the middle, and a top rail and a mid rail along the wall tops. All of them stopped where the flight stopped (BySt020_Ud_4019). A stair-lane photographed in 1989 had no rail (_sefrak_165_013).
- **Since 2009 (TEK17 §8-9).** Rails run on both sides of the whole flight, carry on past the first and last step to a rounded end, and sit 0.9 m above the nosing.
- **Stavanger's 2022 street norm.** Public metalwork is black in the centre and grey or green in the wooden town. The norm states these colours for bike racks; applying them to rails is our inference.

### Quay furniture

- **Before 1876.** The quays did not yet exist (BySt1983_11_068).
- **About 1900 to 1910.** Skagenkaien was built by filling the harbour, with blocks laid off a barge (BySt1984_2_0005).
- **Later.** A concrete deck was added in the 1930s, and a new deck in 2004 to 2005 (secondary).
- **The 1970s and 80s** (BySt020_Ud_0354, _0421): black tyres hung tight along the face; low yellow mushroom bollards, set back from the edge; a yellow edge strip; no railing; cars parked up to the edge.
- **Who kept them.** Stavanger Havnevesen, then Stavangerregionen Havn from 2000 (secondary).
- **Mooring rings in bare rock.** These were the state's. The lighthouse service set them from 1841, painted black-and-white rings beside them, and stopped keeping them in the 1960s. Bolts from 1880 to 1920 were set in molten sulphur and sand (secondary).

### Fences and gates

- **Byantikvaren.** In the central districts, low walls, hedges and picket fences dominate. Byantikvaren warns against solid fences and concrete walls. Ordinary fences follow the ground.
- **The 2023 plan.** In the oldest parts: slate slabs, plank fences and stone walls only. Original fences and gates are kept.
- **Picket fences.** They arrived after 1850, painted white or green (secondary).
- **Gates.** 1910 to 1930: arched gates. 1925 to 1935: square-cut boards on hidden posts (secondary).
- **Wrought iron.** Villa fences and gates in wrought iron date from 1880 to 1930 (secondary).
- **Concrete posts.** We found no date for slatted fences on concrete posts. Øystein's reference is the only evidence.

### Small marks that date a street

- **Letterboxes.** A 1952 law made every household put up its own. Posten sold green steel boxes from 1958.
- **Phone kiosks.** The "Riks" kiosk was made from 1933 to 1995 and went dead by 2016.
- **Manhole covers.** Standard Ulefos covers.
- **From photos of the 1980s.** A white timber bench, a black bin, and a small dark enamel house number.

The first three are secondary (SNL, Aftenbladet, lokalhistoriewiki).

## The craft

**Which games, and why.**
- Spider-Man: lamps.
- The Order: 1886, The Last of Us Part I, Uncharted 4, Gears 4 and The Division 2: wear.
- Inside (Unity): faked light and contact.
- The Assassin's Creed games: instancing and kits.
- Townscaper: junctions.

**Left out.**
- Disco Elysium needs a fixed camera.
- Tiny Glade's many lights need a denoiser.
- Dishonored 2, Hitman and The Witcher 3 left no technical sources on street furniture.

**Modular parts.**
- Spider-Man swaps materials on one lamp mesh per district.
- Insomniac's trim sheet bakes its bevels into a standard UV layout, so any material keeps its edges.
- AC Odyssey builds "Lego kits ... with logic and data", so nothing wrong can be assembled.
- The Last of Us Part I models only a railing's frame and fills it with a parallax plane.
- AC Unity drew ten times the instances with far fewer draw calls.

**Lamps without a light each.**
- **Spider-Man:** a wide baked light for bounce, plus a tight runtime light near the camera. Fog hides the moment the runtime light switches on.
- **Inside:** scalable pill-shaped bounce lights.
- **Far tiers:** see `lighting-and-colour.md` §11.

**Painted iron by upkeep.**
- **The Order: 1886** blends up to four layers per vertex in "incremental steps of wear".
- **Uncharted 4** moves a surface through wetness phases by one value. Age could move paint the same way: fresh, chalky, chipped, rusted.
- **The Division 2** chips edges by curvature, from each object's state.

**Contact.** Inside multiplies "AO decals" at every contact. No game source models lead or base plates.

## Costs in Unity 6 URP on the M4

These apply to Unity 6000.6 with Forward+.

- **Kit meshes.**
  - The GPU Resident Drawer adds little CPU and slightly more GPU.
  - It rules out MaterialPropertyBlocks, so an object's age goes in the Renderer Shader User Value.
  - 200 lamps and rails come to about 0.1 to 0.2 million triangles (estimate).
- **Real lights.**
  - Forward+ allows 256 lights per camera.
  - A shadowed spot redraws its shadow map every frame, which might cost tenths of a millisecond (estimate).
  - The frame is already over 16.7 ms.
- **Cookies.** One texture tap per lit pixel. Unity suggests cookies instead of shadows for static lights.
- **Decals.**
  - Screen Space decals suit tile GPUs. DBuffer decals need a prepass.
  - Emission decals ignore the ground's colour, which breaks VD2.
- **Probes.** Adaptive Probe Volumes bake a lamp's bounce at no runtime cost, but blend only probe data between scenarios, so a lamp switched by circuit needs another path.

## Approaches worth prototyping

1. **Two lights per lamp.** A wide, unshadowed term from our lamp buffer, plus a tight spot for the nearest lamps only. *Test:* the Landing lantern at 17:50 in sea fog: the spot alone, the wide term alone, then both, each timed.
2. **The lamp's reach as a drawn shape.** Each kind of luminaire gets a cookie drawn from its form: a lantern's bars, a bell's cut-off. *Test:* the same still, with the cookie beside a real shadow.
3. **Iron on one clock.** One material, moved through phases by its upkeep. Hands polish the rail's top bare (`foundations.md`), and a lead collar at the foot leaves rust behind it. *Test:* one rail post in grey clay at three ages. It passes if a cold reader puts them in order.

## Gaps

- The 1960 jubilee book (NB, pp. 273 to 276).
- When span-wire lighting started and ended.
- When sodium lamps arrived.
- Bollard makers.
- Concrete fence posts.
- Unity's timings on Apple GPUs.

## Sources

[Mortepumpen 3/2020](https://www.stavanger.kommune.no/siteassets/kultur-og-fritid/senior-i-stavanger/mortepumpen-3-2020.pdf) · [Lnett](https://www.l-nett.no/om-oss/om-lnett/historie) · [Borghammer](https://historier.no/historier/gatebelysningen-i-gamle-dager/) · [TU 2015](https://www.tu.no/artikler/2015-kan-bli-morkt-120-000-lysarmaturer-ma-skiftes-ut/225408) · [Aftenblad 2012](https://www.aftenbladet.no/lokalt/i/AX055/lyse-satser-paa-gatelys) · [NRK 2017](https://www.nrk.no/rogaland/stavanger-oppgraderer-til-led-belysning-1.13486687) · [SLKS stairs](https://slks.dk/fileadmin/user_upload/kulturarv/publikationer/emneopdelt/bygninger/Bygningsbevaring/6.3_Reparation_og_omsaetning_af_stentrapper.pdf) · [TEK17 §8-9](https://dibk.no/regelverk/byggteknisk-forskrift-tek17/8/8-9) · [Gatenorm](https://www.stavanger.kommune.no/vei-og-trafikk/veinorm-for-stavanger/) · [Byantikvaren](https://www.stavanger.kommune.no/bolig-og-bygg/byantikvaren/rad-regler-og-tips-om-eldre-hus/) · [Grimstad](https://lokalhistoriewiki.no/wiki/Varpepåler_og_fortøyningsringer_(Grimstad)) · [Kårbøvågen](https://lokalhistoriewiki.no/wiki/Maritime_kulturminner_i_kårbøvågen) · [Spider-Man](https://www.youtube.com/watch?v=RgUaPmDJ2r4) · [Inside](https://www.youtube.com/watch?v=RdN06E6Xn9E) · [The Order](https://history.siggraph.org/wp-content/uploads/2022/10/2015-Talks-Phail-Liff_Crafting-Victorian-London-The-Environment-Art-and-Material-Pipelines-of-The-Order-1886.pdf) · [Uncharted 4](https://advances.realtimerendering.com/other/2016/naughty_dog/index.html) · [AC Unity](https://advances.realtimerendering.com/s2015/aaltonenhaar_siggraph2015_combined_final_footer_220dpi.pdf) · [User Value](https://docs.unity.com/en-us/engine/current/manual/materials-and-shaders/shaders/renderer-shader-user-value/intro)
