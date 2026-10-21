# Wooden town architecture, 1700 to 1989

How the town's buildings were built in the first place, era by era: the houses of the wooden town, the sea houses and warehouses on the quays, the canneries, the masonry of the centre, the churches and public buildings. It is the subject research behind the house generator's era shelves (`blender/resolver/eras.py`, `docs/building-system.md`). What owners changed later is in `house-changes.md`; how kits and generation work in general is in `kits-and-generation.md`. The model is Stavanger, whose city conservator (byantikvaren) has written more about its wooden houses than any other Norwegian town has. Mandal and Trondheim fill in measurements; Bergen adds roofs; Denmark adds windows. Claims taken from search summaries rather than the source itself are marked (secondary). Claims no source confirmed, and our own readings, are marked (unverified).

## The story in short

Stavanger burned often until 1860 and was never made to build in stone, so it stayed a timber town (Kulturminneplan 2010). Almost nothing stands from before about 1750. The herring boom from 1808 grew the town from 2,300 to 25,000 people in sixty years. It filled the slope west of Vågen (Straen, now Gamle Stavanger) with small log houses in a plain classical style. At the same time 200 to 300 sea houses rose wall to wall along the harbour (Kulturminneplan 2010; Sjøhusrekken 1993). After the Holmen fire of 1860 the town made its first rules: straighter streets, broken gables, low eaves. The herring failed in the 1870s and the crash of the 1880s followed. Then canning made Stavanger an industrial town of about 60 factories. The town spread over the plateaus in rings of two-family houses bought half-made: log boxes and machine-made trim from big planing mills (Kulturminneplan 2010; Heng 2015). Each ring carries its decade's style: sveitser, then the local mix of sveitser and jugend, then 1920s classicism and funkis. After the war came row houses, then type houses and oil money. About 8,000 wooden houses of before 1955 still stand (Kulturminneplan 2010). The town reads like the rings of a tree, oldest at the harbour and youngest at the edge (Brochure 2021).

## 1. Styles and eras

Stavanger's own dates come from the city conservator's style guide (Brochure 2021; Stilguide). They lag the national dates (Mørk 2012) by five to fifteen years, because styles came from Europe's masonry architecture "with a small delay" and were translated into wood (Kulturminneplan 2010).

| Style | Stavanger | Norway | Where in the town |
| --- | --- | --- | --- |
| Rococo, Louis seize | rare; before about 1815 | 1760 to 1810 | a few merchants' houses (Skagen 18) |
| Classicism: Louis seize and empire | about 1790 to 1875 | 1770 to 1850 | the centre, Straen (Gamle Stavanger), around Pedersgata |
| Sveitserstil | about 1865 to 1910 | 1850 to 1900 | the first plateau rings: Kampen, Storhaug, Våland |
| Sveitserjugend (local) | about 1905 to 1920 | | Våland, Storhaug; "typical for Stavanger" |
| Jugend | about 1905 to 1925 | 1900 to 1915 | villas on Eiganes; many in brick |
| Nyklassisisme | about 1920 to 1940 | 1920 to 1930 | council housing on Våland around 1920 |
| Funksjonalisme | about 1930 to 1950 | 1930 on | Bjørnøygata, Bokkaskogen |
| Post-war modernism | about 1945 to 1975 | | the outer rings: row houses, then type houses |

### Before 1800

Stavanger has no standing buildings from about 1275 to the middle of the 1700s; fires and demolition took them (Kulturminneplan 2010). The best-kept survivor is the Hansen house, Skagen 18. Its core is from about 1710; it was rebuilt in 1787 with rococo detail and colours, lengthened in 1820, and given wings towards the sea later. Its sea house is from about 1770 (Kulturminneplan 2010). Blidensol (Øvre Strandgate 112) is from the middle of the 1700s. It was rebuilt so often that its outside now reads as empire. Around 1900, 19 people in four families lived in it (Kulturminneplan 2010). For the generator, the 1700s are a rare shelf: a handful of merchants' houses.

### Classicism and empire, about 1790 to 1875: the old town

This is Gamle Stavanger's style and the corner's D and E. Louis seize was a short transition and is rare; almost all the old houses in the centre and on Straen are empire (Kulturminneplan 2010). In simple wooden houses the two styles nearly merge. The difference is the window: panes grow larger and fewer in empire (Kulturminneplan 2010). The marks (Brochure 2021; Stilguide; Kulturminneplan 2010):

- Small, often one and a half storeys, with low storey heights and a low plinth.
- Symmetric fronts: the door in the middle, the same number of windows on each side.
- A gable roof with almost no overhang, at eaves or verges. Øvre Strandgate 90 has none at all.
- Ordinary red single-curved clay tiles.
- Two-sash windows with a mullion. Louis seize sashes have small panes. Empire sashes have three panes each. Bigger houses have cross-post windows with a glazing bar in the lower sashes.
- Double doors, often with square panels and a fanlight, the fanlight often with a curved bar. Door surrounds can be monumental.
- Flat, lightly profiled trim. Single-rebated horizontal cladding (*enkeltfalset*).
- One large square chimney in the middle of the ridge.
- Sometimes an ark: a *Stavanger-ark* is a shed-roofed wall dormer that starts at the ridge and runs flush with the outer wall. Roof raises and arks were often added later, as needed, to make room. Andasmauet 5, a small empire house, held up to 20 people (Kulturminneplan 2010).

Gamle Stavanger itself is mostly small workers' houses and small trade buildings from about 1770 to 1900 (Lokalhistoriewiki). The fires of 1766 and 1768 burned Straen as far as Nedre Strandgate 25, so most of what stands is from after them (Sjøhusrekken 1993). Visit Norway counts 173 houses and describes them as log-built and easy to take down and move (secondary).

### The 1860 rules: broken gables and wide gables

The Holmen fire of 1860 burned 250 buildings, sea houses among them (Sjøhusrekken 1993; the list in Lokalhistoriewiki gives 210). Most buildings and all the sea houses were rebuilt within four years. The fire brought three rules (Kulturminneplan 2010; Sjøhusrekken 1993):

- Many houses built after 1860 have a half-hip (*halvvalm*, *knekt gavl*). It was required after the fire as a fire precaution. Olav Kyrres gate 16 is an empire house with this broken gable, a high plinth and decorative purlin ends under the eaves: the coming sveitser style.
- A house could have only one storey and a loft, with the cornice at most seven ells high (about 4.4 m; an ell is 0.6275 m). The rule said nothing about the roof, so owners built houses with very wide gables to the street to win floor and window area. When these proved no safer than two-storey houses, two storeys were allowed again. From the late 1800s the box house (*kassehus*) with a full hipped roof became common.
- Sea houses had to have their timber frames filled with brick. The brick showed only inside, because the houses were clad anyway.

Holmen north of Valberget was relaid with straighter streets after the fire: the town's first attempt to plan its streets (Kulturminneplan 2010). Whether the half-hip and height rules held town-wide or only in the burned area is not stated (unverified).

### Sveitserstil, about 1865 to 1910, and dragestil

Sveitserstil is a collective name for the timber historicism of about 1840 to 1910. It came to Norway through architects trained in Germany, and local carpenters took it up fast (SNL, sveitserstil). In Stavanger it "rode the land like an epidemic" (Brochure 2021). Even older houses were updated with new windows, trim and cladding (Fargeveileder 2025). Its marks (Brochure 2021; Stilguide; Kulturminneplan 2010):

- Larger houses than before. Rectangular or cross-shaped plans, good storey heights, and sometimes a high plinth.
- Gable roofs, a few hips, and large overhangs with visible, shaped purlins and rafter ends. Slate or flat clay tiles: the roof plane was meant to look as thin and smooth as possible.
- Balconies on several floors and glazed verandas on the larger houses.
- Carved and fretsawn decoration (*snekkerglede*), spires, gable crosses and carved beam ends.
- Tall cross-post windows with four or six lights, and T-post windows. Coloured glass on verandas and over doors.
- Double doors with short and long panels, and a fanlight with vertical bars.
- Decorative cladding: double-rebated beaded boards (*dobbeltfalset staffpanel*).
- Deeper-profiled trim than before, with blocks or brackets under the window heads and sills (below).
- Often two or more chimneys, with a corbelled ring at the top.
- Two or three colours, with structure and ornament picked out.

Mandal's guide adds the key change in section: the sveitser house introduced a knee wall above the ground floor, so the loft became a full storey (Mandal 2007). A one-and-a-half-storey classical house has its eaves just above the ground-floor windows. A one-and-a-half-storey sveitser house has a metre or more of wall above them (unverified as a measure).

In Stavanger the style became a mass product. The city engineer wrote in 1912 that houses had become "a mass article built on speculation" (Heng 2015). Log boxes and decoration were sold almost as kit houses in several models (Kulturminneplan 2010). The biggest timber merchant was H. Øgreid & Sønner (founded 1885, planing mill on Engøy), and O. Bjorheim & Sønner made windows from 1882 (Heng 2015). Hundreds of one-and-a-half-storey houses with their gables to the street went up on Storhaug, Våland and the western plateau, with nearly identical doors, windows, spires and trim (Heng & Windsholt 2020). The typical building of these rings is the horizontally divided two-family house: a two-storey box with a hipped or gable roof, sveitser in form (high plinth, large overhang, profiled beam ends) with jugend windows (Kulturminneplan 2010).

Dragestil, the national-romantic "dragon style" of about 1880 to 1910, mixed log and stave construction with carved dragon motifs (SNL, dragestil). It was for hotels, mountain lodges and villas, and there is little of it in Stavanger (Kulturminneplan 2010). Dragestil houses were tarred or oiled and dark: umber and English red (Bygg og Bevar, villa styles). For us it is an accent for a villa or a tourist hotel.

### Sveitserjugend and jugend, about 1900 to 1925

Sveitserjugend is Stavanger's own folk mix: a sveitser house with jugend windows and a broken gable (Brochure 2021; Kulturminneplan 2010):

- The same main form as simple sveitser houses, often with small winter gardens or other small additions.
- Still a large overhang with decorative purlin and rafter ends, but usually a broken gable. Mansard roofs came in over time.
- Slate or natural red flat tile.
- Many variations on the cross-post window with bars or arches, among them the local *Vålandsbue*, an arch in the middle field.
- Sveitser cladding, with trim simplified as the period went on.
- A tall decorative chimney became common, after one on the villa Breidablikk.

Jugend proper broke with borrowed ornament. Jugend houses are closed and compact, with small eaves and a softer roof that wraps tightly round the house (Brochure 2021; Kulturminneplan 2010):

- Simple rectangular plans, rarely symmetric, sometimes with small bays (*karnapper*). Doors and windows can be placed asymmetrically on purpose, especially on lesser walls.
- High half-hipped roofs and mansards, hipped mansards among them. Slate or flat tiles; glazed tiles on finer houses. Stavanger's villas often have glazed flat tiles in red, black, blue or green, which give the roof the look of a thin, closed skin.
- Cross-post windows with small panes in the upper sashes, often with a curved middle field. Small hall windows with coloured glass, often with flower motifs. Shutters and leaded glass on some.
- Simple, flat, often broad trim with no brackets. Double-rebated beaded boards, with fields of vertical panel.
- Panelled doors, often with fluted panels, carving and a window. Symmetric double doors, and single doors with narrow side panels; curved lines.
- Decorative chimneys, which can stand partway down the roof.
- Deep colours, but also light and white. Light houses had dark windows.

The jugend years coincide with the national masonry rule after Ålesund burned in 1904, so many jugend houses in Stavanger are brick (Kulturminneplan 2010). Wessels gate 50 is a plain jugend brick house in the brick belt of those years. These brick houses keep the wooden town's plots, structure and styles (Brochure 2021).

**Ålesund.** Ålesund burned on the night of 23 January 1904: 850 buildings were lost, 230 saved, and 10,500 people were left homeless (Lokalhistoriewiki; Bygg og Bevar). It was rebuilt in about three years. More than 320 jugend buildings went up side by side in the centre, in brick and stone, some in rough-hewn natural stone (SNL, jugendstil). Sources differ on the builders: about 50 architects and master builders, or about 20 builders and 30 architects, many trained in Trondheim or Charlottenburg (both secondary). Kaiser Wilhelm II sent ships with materials (secondary). For our setting, Ålesund is the masonry pack's model: a whole centre in one style from one date, which is how a fire reads at the city view.

### Nyklassisisme, about 1920 to 1940

Around 1920 architects rediscovered building before sveitserstil (Brochure 2021; Kulturminneplan 2010):

- Simple, rectangular, symmetric bodies. Gable roofs as in classicism, or strikingly high and pointed ones, or small symmetric houses with half-hips. Some full hips. Little overhang.
- Often flat clay tiles, glazed on finer houses.
- Symmetric small-paned windows, or empire-style ones. Later, three-light windows, some with a middle field without bars. Jørgen Moes gate 8 has six-sash windows with small panes in the top sashes.
- Simple, smooth trim, fluted or symmetrically profiled, with corner blocks.
- Single-rebated cladding, double-rebated beaded boards and vertical panel. Often horizontal in the gable and vertical below, or the reverse.
- Simple panelled doors. On finer houses, columns or half-columns at the door, pediments and classical ornament.
- Simple chimneys after classical models.
- Pastels and white.

The council housing of about 1920 on Våland (Friggs gate, Vidars gate) is in this style (Kulturminneplan 2010). Stavanger's white-and-blue combination, first seen on Skagen 18, spread across the town in these years (Fargeveileder 2025).

### Funkis, about 1930 to 1950

Funkis came partly as a social and hygienic project, partly as a reaction against borrowed ornament (Kulturminneplan 2010; Brochure 2021):

- Rectangular bodies, sometimes asymmetric, sometimes with curved additions. Drawn "from the inside out".
- Flat roofs, mono-pitch roofs or low hips; later also low gable roofs. No dormers. Flat clay tiles were commonest. Some houses had only roofing felt.
- Windows often at the corners. Two- and three-light windows with no bars, square or horizontal in format. Upright stair windows with a grid of panes. Round windows.
- Often no corner boxes: the cladding is mitred at the corners.
- Single-rebated and vertical panel. Sometimes vertical boards between the upper windows, or on one storey only. The changes of board direction are often the only ornament.
- Plain, smooth, often narrow trim.
- Smooth doors with one large panel or geometric divisions, often with a small window.
- Chimneys with horizontal stripes.
- Greenish, greyish, reddish and bluish colours as well as white.

The common folk version, with a low gable roof, is called *byggmesterfunkis* (builder's funkis; Tordenskjolds gate 78A; Kulturminneplan 2010). Nationally, a "skirt and blouse house" had a concrete ground floor and a timber upper floor (Bygg og Bevar, villa styles).

### Post-war, 1945 to 1975

After the war Stavanger had a housing shortage and few materials. The two-family house was given up for denser types: a few blocks, and above all the row house. The first row-house estates came in the early 1950s (Tasta, Våland slope, Tjensvoll), drawn by Retzius and Bjoland, Thv. Solheim and city architect Torleiv Våland. Over 1,200 row-house flats were built from 1950 to 1965 (Kulturminneplan 2010). The style guide's marks for 1945 to 1975 (Brochure 2021; Stilguide; Kulturminneplan 2010):

- Bodies broken into two or more volumes, often horizontal and asymmetric, so you can guess the living room from outside.
- Gable and hipped roofs with low pitches, mono-pitch and flat roofs; a wide range of roof coverings.
- Plain windows and doors. Big living-room windows against small windows elsewhere. Large panes, sometimes horizontal; no bars. Single windows with a mullion, later top-hung tilting windows (Bygg og Bevar, villa styles).
- Vertical cladding becomes popular, but horizontal stays common.
- Brick walls set against timber walls. In the 1960s often black and white, the white being the masonry.
- Large chimneys, sometimes showing along the whole gable.
- Marked use of colour: pastel green, pink and yellow, dark reds, and from now blue houses (Fargeveileder 2025).

**Gjenreisning.** Finnmark, North Troms and the bombed towns (Kristiansund, Molde, Bodø) were rebuilt to type drawings from 1945. Every house had a gable roof; about two thirds were built to type drawings; over a hundred types were used (Bygg og Bevar, Finnmark; secondary). The typical house is compact, nearly square in plan, one and a half storeys, with a steep gable roof (about 45° on one example) and little overhang. It has two- or three-light windows and horizontal cladding or Eternit sheets (secondary). Gjenreisning houses and the Swedish gift houses (*svenskehus*) of about 1945 to 1955 had weatherboard with zig-zag corners. Their walls were strong colours (English red, a Stavern yellow, mid-green) or white and grey-white, with white frames and sashes coloured blue, red or grey-green (Bygg og Bevar, villa styles). Stavanger was not rebuilt this way; for us gjenreisning is a shelf for other towns and a source of single type houses.

**1960s to 1980s.** Timber firms sold pre-approved drawing sets from the early 1950s. These grew into catalogues: Block Watne (founded in Sandnes in 1872; Jærmuseet), Moelven, Mesterhus and others (Bygg og Bevar, ferdighus). The Bygg og Bevar article gives the decades' looks:

- 1950 to 1975: flat or low roofs, mixed horizontal and vertical stained panel, large windows in bands, white-painted concrete plinths, unpainted brick, paint names like *eføy*, *barkebrunt*, *halmgult*.
- 1955 to 1990: the split-level plinth house (*sokkelhus*) on sloping sites.
- About 1970 to 1985: the Tyrolean house (*tyrolerhus*), with steep roofs, deep eaves, prominent rafter ends, small-paned windows with shutters, arches, and brown, red or ochre walls.
- 1980s: the colonial house (*kolonistil*), with hipped roofs, sometimes with a kick at the eaves, small-paned windows, shutters, big stone or brick chimneys, and more and more all-white.

### Masonry in the centre

Stavanger tried masonry rules after its fires without success (Kulturminneplan 2010). Building in wood was much cheaper and land was plentiful, so even housing stayed timber far into the post-war years. Brick went to commercial buildings, hotels and public buildings (Artemisia, secondary). Dated masonry in the centre:

- The cathedral (about 1125, choir later).
- The old customs house, Nedre Strandgate 51 (1840; C. H. Grosch per Sjøhusrekken 1993).
- Valbergtårnet, the stone fire-watch tower (1850 to 1853).
- The old prison (1862).
- St. Petri church (1864 to 1866, von der Lippe).
- Rogaland teater (1883), Stavanger museum (1893), the hospital (1897).
- Victoria Hotel (1900), the customs house in Skansegata (1904 to 1906).
- The post office (1911). It was demolished in 1974 by a narrow vote (Stavangeren 1/2016).
- St. Johannes church (1909, Sparre), St. Svithun school (1918 to 1919).
- The 1920s classical monuments: Filmteatret (1924), Kunstforeningen (1925), Folkets hus (1926).
- 1930s funkis institutions: Sjømannshjemmet (1932 to 1933), Handelens hus (1935), Solvang old people's home (1937).
- Post-war: Atlantic Hotel (1952), the library (1960), the savings bank (1961), Norges Bank (1964). Then the swimming hall (1971, brutalism), Sølvberget (1987) and Skagen Brygge Hotel (1988), the last a free reading of the sea houses.

(Kulturminneplan 2010; Artemisia, secondary.)

Trondheim's brick houses of before 1925 give the type's measures: brick, rendered, three or four storeys, inner ceiling heights 270 to 290 cm, roof pitches 34 to 40°. T-post windows sit half a brick back in the wall, and simple bands run in the render (Trondheim). Two hybrids matter for Stavanger. Some timber houses in the centre are rendered over the wood (*murpussede trehus*; Brannplan; one source). Some sea-house fronts were rendered on wire lath (*rabbitspuss*) while the timber sea house stands intact behind (Østervåg 19; Sjøhusrekken 1993). A render front is therefore not proof of a brick house.

### Sea houses and warehouses

The sea houses are, with the cathedral and the Valberg tower, the strongest mark in Stavanger's plan (Sjøhusrekken 1993). At the height of the herring years 200 to 300 stood almost wall to wall from Sandvigå to Strømsteinen. About 60 remain, many rebuilt, and most now stand well inland behind later quays (Kulturminneplan 2010). The 1993 survey counted 60 on the stretch: 56 timber-framed (three with log parts), one stud-framed, and three houses built to the sea with sea-house ground floors (Sjøhusrekken 1993). Most were built between 1810 and 1870, some in the late 1700s.

- **Use.** Storage and work: salt, herring, dried fish, grain, nets, sails, rigging. Herring salting, coopers, sailmakers and block makers. Later the first canneries, then wholesalers, then warehouses for pallets and trucks. Offices came with oil, and restaurants from 1973 (Dickens) and 1978 (Skagen 18's sea house) (Sjøhusrekken 1993; Kulturminneplan 2010).
- **The unit.** The sea house stood on the water. A linking building and a small yard joined it to the dwelling behind, which faced the street. Across the street the property's terraced garden climbed the slope. Nedre Strandgate 17 and 19 keep the whole section. No. 17 turns its long side to the street, no. 19 its gable, which is commoner in west-coast towns (Sjøhusrekken 1993; Kulturminneplan 2010). Shore plots were narrow so that as many as possible reached the water. Public landings (*allmenninger*) at the ends of streets gave others access (Sjøhusrekken 1993).
- **Structure.** Stavanger's sea houses are built in *bindingsverk*, a timber frame. Posts about 80 cm apart are tenoned into a sill and capped by a top sill, braced with diagonals and naturally curved knees fixed with treenails. Each storey is a closed system stacked on the one below (German *Geschossbau*). Joists span wall to wall in small houses, or rest on one to four rows of posts and girders: one-span to four-span houses. Curved knees in all four directions are typical of Stavanger and the south and west coasts. Bergen's and Trondheim's sea houses are log, and Ålesund's and Kristiansund's have straight braces (Sjøhusrekken 1993, after Schjelderup 1991). Before 1700 the larger sea houses were probably log (Sjøhusrekken 1993).
- **Floors and foundations.** Heavy timber floors from the ground floor up, often sloping towards the sea for the brine. Foundations of dry stone or dressed stone (Sjøhusrekken 1993).
- **Roof.** A west-country rafter roof, braced only by the roof boarding: horizontal lapped boards nailed straight to the rafters in the oldest. Boarding with battens over joints came between 1840 and 1860. The roofs were clay tile (Sjøhusrekken 1993).
- **Cladding.** Lapped west-country cladding, or *tømmermannskledning* of unedged boards where the face did not matter (Sjøhusrekken 1993).
- **The hoist.** A big hand-turned winding wheel sat in the loft, its axle through the gable wall, hung in and protected by a small ark. Ropes ran down through every floor, so the hoist could be worked from any storey. This is why the houses stand gable to the sea. Houses with their long side to the sea needed a separate roof structure for the hoist. Stavanger had two forms: a projecting gable, as elsewhere on the west coast, and a shed-roofed one, the Stavanger-ark, found mostly in this district (Sjøhusrekken 1993, after Schjelderup 1991).
- **The face.** A strict, symmetric gable front with large plain walls. Stacked loading doors run up the middle under the hoist ark, with small windows placed pragmatically at the sides. Eaves are scant and detail is sparse, limited to the trim and the bottom board of the hoist ark. Sveitser facades were sometimes applied later, as at Østervåg 19 around 1900 (Sjøhusrekken 1993).
- **Colour.** In 1856 a Norwegian paper described the town's "white-painted and well-kept" packing houses as looking splendid from the sea (Sjøhusrekken 1993). The 2025 colour guide warns that sea houses which look white in old photographs are not white beside a sail (Fargeveileder 2025). In Mandal, outhouses and sea sheds were traditionally English red or ochre (Mandal 2007). Today Stavanger's row is mostly white, with the red sea houses at Nedre Holmegate 20 (unverified as a count). Our reading: a merchant's warehouse facing the harbour was painted light as a show of wealth; lesser sheds and the backs were red or ochre (unverified).

### The cannery

Canning began in 1873 in Øvre Strandgate 38, smoking sprats and packing them in olive oil. By the early 1900s Stavanger was one of Norway's biggest industrial towns (Stavangeren 1/2016):

- The first canners used what stood empty after the crash of the 1880s: houses, sea houses, any room that could be rebuilt. Bjelland's first own factory (1894) was fitted into two old sea houses (secondary).
- From the late 1890s purpose-built brick factories went up, and old wooden houses came down for them. They ranged from plain to grand. They are plain historicist industrial architecture after Danish or German warehouses (Sjøhusrekken 1993).
- Every factory had a tall chimney rising from the smokehouse. The smokehouse often stood in a small annex in the back yard or in a side building (Stavangeren 1/2016). The east of the town was "a forest of chimneys".
- There were 60 to 70 factories at the peak, 38 in 1960 and 13 in 1968 (Kulturminneplan 2010; Stavangeren 1/2016). In 2015, 23 purpose-built canneries still stood, 16 buildings that once held canning, and at least 52 had been demolished. Only three chimneys remain (Stavangeren 1/2016).
- Canneries have good ceiling heights and light, unlike sea houses (Stavangeren 1/2016).
- Around them stood box makers, tin works, printers of labels, workers' houses, cooperatives, nurseries and prayer houses (Stavangeren 1/2016).

The canning museum in Gamle Stavanger shows a typical 1920s factory (Wikipedia, secondary).

### Churches and public buildings

Stavanger was founded as a church centre and built no new churches between the Middle Ages and the 1800s. Then came Frue kirke (1854), St. Petri (1866) and St. Johannes (1909) (Kulturminneplan 2010). The lay movements built many prayer houses (*bedehus*). Nygatens forsamlingshus (1846) is the oldest active one in Norway. Bethania (1875 to 1876) was the town's biggest hall until the 1950s, and nearly 15 prayer houses and free churches clustered round Bergelandsgata in the east (Kulturminneplan 2010). Schools were the big brick landmarks of the early 1900s. Kongsgård's timber main building (1759) stands on medieval walls (Kulturminneplan 2010). Building material per prayer house is not recorded (unverified).

## 2. Construction

### Walls: log, stud frame, timber frame

- **Log (*laft*).** The houses of the old town are log boxes clad in boards. Their ground floor or plinth storey is a mix of masonry, log or stud frame (Brannplan). The regulated plateau rings are log too, with wider streets and gaps (Brannplan). Most were simple log boxes bought half-made and fitted to the plot by their foundations and plinths (Kulturminneplan 2010). Trondheim measures the log box: single-span boxes 4.5 to 5.5 m wide, double-span (with an inner log wall) 6.5 to 7.5 m, and 7.0 to 9.5 m for the 1890s houses (Trondheim). Stavanger's old-town houses measure a median 9.8 × 7.5 m in plan (`stavanger-centre.md`): a double-span log box.
- **Stud frame (*reisverk*) and timber frame (*bindingsverk*).** These became commoner towards the late 1800s (SNL, sveitserstil). Outbuildings in the old town's blocks are stud-framed, and many were later joined to the houses (Brannplan). Sea houses are timber-framed (above).
- **Post-war.** Gjenreisning used machine-made log planks (about 7 × 15 cm, double tongue and groove, sealed with felt) or heavy timber frames, with studs of 10 × 10 and 5 × 10 cm. Some houses were prefabricated in elements (Bygg og Bevar, Finnmark; secondary). Mineral wool came into common use in the late 1950s (`house-changes.md`).
- **Cladding over log.** The cladding stands about 5 cm off the log wall, the space later used for insulation (Detaljkrav).

### Plinths, cellars and the slope

Classical houses have low plinths. A high plinth was a sign of the coming sveitser style, and sveitser houses often have high ones (Kulturminneplan 2010; Brochure 2021). Mandal's old plinths are stone laid in lime mortar and rough-cast. Many were later rendered in cement and painted, and some plinth storeys facing the street are stud-framed and rendered in lime or clad in wood (Mandal 2007). Trondheim's plinths are usually rendered grey (Trondheim). On a slope the plinth takes up the fall: low on the uphill side, a storey high on the downhill side. That lower storey held a cellar, wash-house, store, workshop or shop, and its windows show which (Mandal 2007). Plinths and stairs kept their material colour: bare stone, lime render or untreated cement render; some render was painted grey later (Mandal 2007).

### Cladding by era

Mandal's guide dates the profiles. Stavanger's style guide names the same profiles per style and fits Mandal's dates (Brochure 2021).

| Profile | Norwegian | Years | Where |
| --- | --- | --- | --- |
| Single-rebated horizontal boards | enkeltfalset | 1740 to 1850 (Mandal); classicism (Stavanger) | larger houses, often battened out from the log |
| Lapped horizontal boards with drip edge | supanel | 1740 to 1850 | as above |
| Vertical board-and-batten, plain or profiled battens | tømmermannskledning | 1700 to 1850, to the 1860s | small houses; sea houses (unedged boards); Trondheim's empire houses |
| Lapped vertical "west-country" cladding | suet vestlandskledning | sea houses | sea houses (Sjøhusrekken 1993) |
| Double-rebated horizontal boards | dobbeltfalset | most common 1830 to 1880; general from 1850 | street fronts first; old houses reclad |
| Beaded tongue-and-groove boards | pløyd staffpanel, pølsekledning | 1860 to 1930 | sveitser, sveitserjugend, jugend; old houses reclad |
| Vertical beaded boards | stående staffpanel | 1860 to 1930 | sveitser knee walls and second storeys |
| Single-rebated with vertical fields | | 1930 to 1950 | funkis; direction changes as ornament |
| Vertical panel, horizontal still common | | 1945 to 1975 | post-war; stained rather than painted |
| Eternit sheets; plastic | | 1950 to 1978; 1975 to 1989 | recladding (`house-changes.md`) |

Rules the cladding follows:

- **Boards were planed** until the 1960s and 70s. Unplaned boards are the post-1960 norm, and they hold dirt, damp and mould (Kulturminneplan 2010; Detaljkrav).
- **Old boards are 1 to 1¼ inches thick** (25 to 32 mm), of slow-grown pine. Corner boards and boards over the log corners are a little wider and thicker than the panel (Mandal 2007).
- **Widths vary on one wall**, to fit window openings and their trim. It gives the face more life than identical boards (Kulturminneplan 2010; Mandal 2007).
- **Fronts were reclad before backs.** A house reclad in the late 1800s often kept its first cladding on the gable, towards the yard or in the alley. The "sausage" beaded board on an old house is usually its newest skin, not its oldest (Mandal 2007).
- **Windows sit at different depths.** In board-and-batten walls the bottom board is often nailed on as a sill piece. In lapped or single-rebated walls the window sits deeper (Mandal 2007).

### Corners, trims and window surrounds

Log corners are boxed in corner boards (*hjørnekasser*). Funkis and later houses have no corner boxes; their boards are mitred (Brochure 2021; Detaljkrav). Michael Heng measured Stavanger's window surrounds from 1860 to 1915 over five years (Heng 2015; Heng & Windsholt 2020). His findings are the most exact measures we have for any part:

- **After 1860.** Still close to empire: flat, little projection, a tight elegant look. Yet a common surround has as many as six profiles. Both water boards are profiled. A profiled strip of about 5 × 10 cm sits under the lower water board, and another under the upper. The profiles run round the corners into the end grain. The main board is mitred at the corners like inside trim. A cove of about 30 × 30 mm draws the window about 30 mm in from the wall face. On single-rebated walls the trim is scribed into the boards. Some have a panel under the upper water board that lifts it high over the window (Nedre Strandgate 27).
- **System 1, late 1800s.** The main board becomes a chamfered board whose chamfer stops short of the sills and brackets. The upper water board rests on brackets beside the side boards. Spilderhauggata 14 (1895) has 16 parts per window:
  - two blocks about 180 mm high, 125 wide and 50 thick under the lower water board, with a fretted board between them;
  - side boards about 25 mm thick;
  - a dentil strip and an 80 mm cove over the head;
  - brackets 480 mm long, 125 mm deep and 50 mm thick under the upper water board;
  - an upper water board projecting 180 mm from the wall and 45 mm past the brackets; the lower one projects about 120 mm;
  - both water boards about 30 mm thick with a cove under the edge.

  A lily carved at the top of the side board is a Stavanger peculiarity Heng has not seen elsewhere.
- **System 2, about 1900 to 1915.** Mass-produced: band-sawn blocks identical across whole streets. The upper block sits on top of the side board, not beside it, and up to 20 parts make a window:
  - side boards 120 to 125 mm wide (140 to 150 on big houses), about 25 mm thick, plain or with two or three flutes;
  - the commonest lower bracket about 230 mm long and 60 mm thick, ogee-shaped, cut at about 20° to the wall;
  - about 250 mm from the frame to the upper water board, often filled with upturned cladding boards or a dentil board. A head set too close to the window is the commonest restoration error;
  - water boards at 20°, or 15° on the boxed crown Heng calls V1.

  Fretted boards between the lower brackets belong to pure sveitser houses, not to sveitserjugend.
- Mandal's water boards are 1¼ inches thick and slope 25 to 28° (17° today; Mandal 2007).
- **Trim by style** (Brochure 2021; Stilguide):
  - classicism: flat, lightly profiled;
  - sveitser: deeply profiled and carved, with blocks or brackets;
  - sveitserjugend: the same, simplified over time;
  - jugend: flat, broad, plain, no brackets;
  - nyklassisisme: smooth, fluted or symmetrically profiled, with corner blocks;
  - funkis: plain and narrow;
  - post-war: simple.

### Eaves and verges

- **Classicism and early houses.** Overhangs were originally very small at both gable and eaves. Old barge boards were heavier than today's, 28 to 34 mm thick and 195 to 220 mm wide, cut plumb at the apex. Thin barge boards on an old house usually date from after 1940 (Mandal 2007). Stavanger's classical houses have gable roofs with almost no overhang (Brochure 2021). A restored classical house (Tidegeilen 9) has a moderate overhang and at most two slim barge boards (Brochure 2021).
- **Sveitser.** Larger overhangs came with the style, about 1860 to 1870, on new houses and modernised old ones (Mandal 2007). They have visible shaped purlins and rafter ends (Brochure 2021). The purlin ends were often only decoration (Kulturminneplan 2010). Sveitser fascia and eave boards meet at a right angle behind the gutter (Detaljkrav).
- **Jugend and nyklassisisme.** Small overhangs (Brochure 2021).
- **Funkis.** Low roofs, plain eaves (Brochure 2021).
- **Post-war Tyrolean.** Deep eaves and prominent rafter ends (Bygg og Bevar, ferdighus).

### Windows by era

The window is, with the form of the house, its most important feature (Kulturminneplan 2010).

| Era | Type | Panes | Colour of sash |
| --- | --- | --- | --- |
| 1700s (Mandal) | one-sash, 12 panes (imitating an English sash); two-sash, 6 or 8 panes each | small | dark |
| Louis seize, to about 1815 | two-sash with mullion | small panes | dark |
| Empire, about 1810 to 1865 | two-sash with mullion; cross-post on bigger houses | three upright panes per sash; a bar in the lower sashes of cross-posts | dark: grey, brown, green |
| Sveitser, about 1860 to 1910 | tall cross-post with four or six lights; T-post | no bars, or one bar in the top light (Trondheim) | brown, dark; coloured glass on verandas |
| Sveitserjugend, 1905 to 1920 | cross-post variants | bars or arches; the Vålandsbue | green, black, dark |
| Jugend, 1905 to 1925 | cross-post | small panes in the upper sashes; curved middle field; coloured hall windows | dark on light houses |
| Nyklassisisme, 1920 to 1940 | symmetric small-paned; six-sash with small panes at top; three-light | small panes; later a plain middle field | white, or oiled wood with white and blue |
| Funkis, 1930 to 1950 | two- and three-light; corner windows; round windows | none | white or contrast |
| Post-war, 1945 to 1975 | big living-room window or band, small windows elsewhere; single with mullion; tilting | none; large, sometimes horizontal | white, teak, stained |
| Replacement, 1930 to 1959 | funkis windows in old houses | none | |
| Replacement, 1955 to 1989 | *husmorvindu*: one sash pivoting through 180° | none; one often replaced two; openings shrunk | white |

Sources: Brochure 2021; Stilguide; Kulturminneplan 2010; Mandal 2007; Trondheim; Bygg og Bevar; `house-changes.md`. The husmorvindu is Norway's best-known window type, an "H window" whose hinge lets it turn right round so it can be washed from inside. It was still being made in 1987 (secondary).

- **Old windows were dark.** In the 1700s and early 1800s window frames were dark even when the trim was near white, to make the small-paned window look bigger. Large glass was dear (Fargeveileder 2025). Windows were often a colour other than white; white is the default only for new windows today (Kulturminneplan 2010). Light houses in jugend had dark windows (Stilguide).
- **Proportions.** Empire panes are upright: three per sash in two tall sashes (Trondheim). Sveitser windows are tall (Brochure 2021). Funkis windows are square or horizontal (Kulturminneplan 2010).
- **Size.** No source gave measured opening sizes per era (see Gaps). Working values, to be checked on reference photographs (all unverified):
  - empire: 0.75 to 0.85 m wide by 1.2 to 1.35 m high;
  - sveitser cross-post: 0.95 to 1.1 by 1.6 to 1.9 m;
  - funkis three-light: 1.4 to 1.8 by 1.1 to 1.3 m;
  - husmorvindu replacing a pair: 0.9 to 1.2 by 1.0 to 1.2 m.
- **Glass.** Crown glass (about 1740 to 1840) was spun into a disc, thinner at the edge, with circular waves. Cylinder glass (about 1840 to 1930) was blown as a long cylinder and opened flat. Sealed insulating glass came from the 1950s (Viggja). Danish windows add drawn glass and, from about 1970, float glass. Float is uniform and "dead"; older glass bends the reflection of a straight lamp post or downpipe (SLKS). Old windows also hold plate glass in doors and large shop windows before 1915 (SLKS). The bend in a reflection is a true era cue in glass, which the shader can carry.
- **Hardware.**
  - Hinges: stacked hinges before about 1880, hinges with a "Norway knob" (*norgesknopp*) until about 1930, rounded ends until about 1970.
  - Corner irons on the sashes; glass set in putty.
  - Hinges and corner irons painted in the window colour.

  (Detaljkrav.)

### Doors, porches and stairs

- **Doors by era** (Brochure 2021; Stilguide; Mandal 2007):
  - Classicism: double doors with three or four panels in height, square or slightly pyramid-shaped, and a fanlight or sidelights.
  - Later 1800s: doors with glass in the top of the leaf.
  - Sveitser: double doors with short and long panels, a fanlight with vertical bars.
  - Jugend: panelled doors with fluted panels and windows; single doors with narrow side panels.
  - Nyklassisisme: simple panelled doors with classical surrounds.
  - Funkis: smooth with one panel or geometric divisions and a small window.
  - Post-war: smooth or geometric, with glass side panels.
- **Single doors with wide side panels.** Between 1930 and 1950 many street doors were replaced by single doors with wide side panels, to fit the old double-door openings (Mandal 2007).
- **Doors opened inward** in houses built before about 1980 (Detaljkrav; Kulturminneplan 2010). Doors were almost always painted (Kulturminneplan 2010). Many panelled doors were covered with boards in a 1930s-to-50s modernisation and survive under them (Kulturminneplan 2010).
- **Door colours.** Doors were usually a colour other than the walls: blue-black, red, brown, and above all green, from green-black to purer greens (Mandal 2007). A mass-produced standard door gives a sad first impression and often needs replacing within a few years (Brochure 2021).
- **Porches.** The *bislag* is a small closed entrance porch with its own roof. Sveitser houses have fretwork on the porch (Heng & Windsholt 2020). Glazed verandas belong to the larger sveitser houses, and balconies and *altaner* to sveitser and funkis, not to empire (Kulturminneplan 2010).
- **Stairs to the door.**
  - Stavanger: a stone stair with slate treads and a wrought-iron railing, as restored at Tidegeilen 9 (Brochure 2021).
  - Trondheim: a rendered masonry base, thick slate treads with a chamfered edge, and wrought-iron railings. The landing is often one thick self-supporting slate slab cantilevered over a window, a cellar door or a store below (Trondheim).
  - Mandal: was known for big outside stairs, some in two flights, of rubble later rendered. Treads are granite or imported sandstone, with bar-iron railings whose handrails end in a prism-shaped cup. Many stairs were removed when the door moved down to street level (Mandal 2007).

### Roofs and roofing

| Era | Form | Pitch | Overhang | Covering |
| --- | --- | --- | --- | --- |
| Classicism to 1860 | gable; later a quarter-hip or broken gable | 30 to 34° (Trondheim empire, "deliberately low"); 38 to 45° (Mandal) | almost none | red single-curved clay tile |
| After 1860 | half-hip required; wide-gabled 1-storey-and-loft houses; later 2-storey boxes with full hips | | small | red tile; flat tile from the late 1800s |
| Sveitser | gable; few hips; cross gables | about 40° (Trondheim, 1890s) | large; visible purlins, rafter ends | slate or flat tile, the plane thin and smooth |
| Sveitserjugend | as sveitser with broken gable; mansards later | | large | slate or natural red flat tile |
| Jugend | hip, half-hip, mansard, hipped mansard | high | small | slate, flat tile; glazed flat tile (red, black, blue, green) on villas |
| Nyklassisisme | gable as classicism or high and pointed; half-hip; full hip | high | small | flat tile, glazed on finer houses |
| Funkis | flat; mono-pitch; low hip; later low gable | low | plain | flat tile; some felt |
| Post-war | low gable, hip, mono-pitch, flat | low | moderate | all kinds; concrete tile from the 1950s |
| 1970s to 80s | steep Tyrolean; hipped colonial | | deep (Tyrolean) | concrete tile common |

Sources: Brochure 2021; Stilguide; Kulturminneplan 2010; Mandal 2007; Trondheim; Bergen roofs.

- **Red single-curved tile.** After the fire of 1702, red single-curved tiles came to dominate Bergen. They were almost the only roofing there until the late 1800s and stayed in common use through the 1960s. Only the grandest buildings had costly imported Dutch tiles, often glazed black (Bergen roofs). In Mandal almost every house was roofed with single-curved tile, with a lath spacing of about 30 cm and tiles about 36 to 40 cm long (read from a drawing). A few had flat tile laid in bond, some slate, and the grand ones black glazed tile. Outbuildings had felt or corrugated iron (Mandal 2007).
- **Local tile.** Jæren's blue clay fed Sandnes Teglverk from 1783. It stood alone until the 1850s; seven tile works and perhaps 40 potteries followed in the next decades. The last closed in 1994 (Jærmuseet). The red tile of the town's roofs is local.
- **Slate.** Drop-shaped slate (*dråpeskifer*) became the favoured roofing of sveitser and jugend in Bergen, once the Voss railway (1883) and steamers could carry it (Bergen roofs). Slate dominates in Trondheim's 1890s blocks (Trondheim).
- **Concrete tile.** It came when tile works could not keep up after the war (Bergen roofs). In Stavanger it replaced old tile and slate roofs from the 1960s to the 1990s (Kulturminneplan 2010; Heng & Windsholt 2020).
- **Roof windows.** These were originally small cast-iron frames with single glass. A few lofts were lit with glass tiles instead (Mandal 2007).
- **Dormers.** Mandal's old houses had no dormers or roof additions, before or after its fire of 1810; they appeared there only in the late 1800s (Mandal 2007). Stavanger's shed-roofed ark is the local exception: added as needed, from early on (Kulturminneplan 2010).

### Chimneys

- **Classicism.** One large square chimney in the middle of the ridge.
- **Sveitser.** Two or more, with a corbelled ring at the top.
- **Sveitserjugend.** One tall, decorative chimney.
- **Jugend.** Decorative, sometimes standing down the roof.
- **Nyklassisisme.** Simple, after classical models.
- **Funkis.** Horizontal stripes.
- **Post-war.** Large, sometimes showing the whole length of the gable.

(Brochure 2021; Stilguide.)

Construction: brick, rendered where needed, with lead flashing pointed into the joints and a zinc or slate cap. Full metal cladding is not allowed today (Detaljkrav). Trondheim's chimneys have a heavier base and crown than the flue between (Trondheim). Mandal's are capped with slabs, little vaults, pyramids or thin bent iron plates (Mandal 2007).

### Gutters and downpipes

Old houses had no gutters or flashing at first; the earliest was a short gutter over the door (Mandal 2007). Zinc gutters came later and were painted (Mandal 2007).

- **Stavanger.** Zinc gutters are painted in the house colour, hung high on hooks, with downpipes bent in straight angles, not curves. Funkis houses may have square gutters and pipes (Detaljkrav).
- **Trondheim.** Two kinds: a plain metal gutter with its underside and the downpipe painted in the wall colour; and the *karnissrenne*, a metal gutter hidden in a wooden moulded box on brackets. The brackets often outlive the box (Trondheim).
- **Plastic.** PVC gutters came into common use in the 1960s (Bergen roofs).

## 3. Colour and paint

### Paints by era

- **Earth colours, late 1600s to 1700s.** Fronts began to be painted when log walls began to be clad, from the late 1600s. The first paints were iron oxide and ochre dug locally: English red, *dodenkopf* (a deep purple-brown), ochres, umbers (Westman).
- **Herring-oil paint.** Simple houses in Stavanger were probably painted with herring-oil paint (*sildoljemaling*) in yellows, ochres and reds (Fargeveileder 2025).
- **Lead white, then cheaper whites.** Lead white was expensive: white meant status. Finer houses were white; small houses might have a white front and a red or yellow back (Fargeveileder 2025; Westman). White grew cheaper around 1850 and became a common house colour (Stilguide; Kulturminneplan 2010). Zinc white came, then titanium white, which made white chalk-white in 1910 to 1940 (Fargeveileder 2025).
- **Linseed-oil paint.** It was the wooden town's main paint (Fargeveileder 2025). From the late 1800s to about 1950, bare wood was primed with raw or boiled oil and a little ochre (*okre huset*). This caused crazing, flaking and blistering in later coats (Brænne 2017).
- **Alkyd.** In Denmark alkyd replaced linseed from the 1930s, though linseed was kept for priming windows until about 1970 (SLKS). In Norway alkyd paints and synthetic pigments spread after the war and made colours clearer and stronger (Fargeveileder 2025; Bygg og Bevar, ferdighus). Houses painted only in alkyd date from after about 1965 (Brænne 2017).
- **Stain, acrylic, impregnated wood.** The 1950s-to-70s houses were stained rather than painted (Bygg og Bevar, ferdighus). Water-borne acrylic paints replaced alkyd in Denmark from 1976 (SLKS); in Norway acrylic is the paint of the postmodern houses of 1985 to 2010 (Bygg og Bevar, ferdighus; when it began here is unverified).
- **The same colour, three looks.** Distemper, linseed and acrylic in the same colour look different: the binder matters as much as the hue (Fargeveileder 2025, after Egersund 2018).

### Colours by era and status

Stavanger's 2025 colour guide scraped back the coats on 47 houses of all ages, layer by layer, to the late 1700s (Fargeveileder 2025). It is the best colour evidence we have.

| Period | Walls | Trim | Windows | Doors and examples |
| --- | --- | --- | --- | --- |
| Herring town, about 1700 to 1850 (rococo, classicism) | white only on finer houses; simple houses yellow, ochre, red; a white front with a red or yellow back | sometimes near white | dark | Skagen 18 (1770): yellow, white trim, red windows. Andasmauet 10 (1838): ochre, brown trim, windows and door. Blidensolstredet 13 (1837): all red. Øvre Strandgate 90 (1836): sand, white trim, grey windows, black door |
| Sailing-ship town, about 1850 to 1884 (late classicism, sveitser) | muted masonry colours on small houses; white on villas; ochres and browns, also white and grey; greens appear | contrasting, lighter or darker | dark | Øvre Strandgate 103 (1860): ochre, red windows and door. Skagen 44 (1860): white, ochre trim, brown windows. Haakon VII's gate 4 (1862): grey, white trim, brown windows |
| Industrial town, about 1884 to 1910 (sveitser, sveitserjugend, jugend) | white and greyish shades | same as wall or low contrast | often dark, sometimes white | Peder Klows gate 1: ochre, white trim, brown windows. Kong Carls gate 66 (1911): grey, white trim, black windows |
| Growing town, about 1910 to 1940 | light panel; green popular; white with *Stavangerblå*; red and yellow with white trim | olive and deep green | oiled wood, green, white | Muségata 55 (1911): ochre, green windows. Hafrsfjordgata 37 (1913): grey, white trim, green windows |
| The "new" town, about 1945 to 1955 | pastel green, pink, yellow; dark red; blue houses popular | white | white | stronger colours with alkyd |

- **"Everything white" was never the whole truth.** Early-1900s Våland was called dull in its day because "all" the houses were white. The whites were many: grey-white, pearl grey, beige, sand, putty, cream. Windows stayed dark, and trims were often a contrast (Fargeveileder 2025).
- **Local colours.** *Stavangerblå* was probably a Prussian blue. City conservator Hedén later used NCS 6515-B under that name. *Bergesengrønn* is a light green said to come from leftover ship paint from the Bergesen tankers (Fargeveileder 2025).
- **Gamle Stavanger was not white.** It was painted white only after 1956. Øvre Strandgate 60 "has never been white" (Fargeveileder 2025). The old town's whiteness is a fact of 1956 and later, which our diaries can carry: protected streets turn white after 1956.
- **The national story agrees.** Sveitser houses were first painted ochre to imitate new wood, with the structure and windows picked out in brown. All-white houses came only with 1900s neoclassicism. Funkis brought back English red and ochre, then grey-greens, pale yellows and light blues. The 1960s and 70s brought nature colours: the *Måke* palette for the coast, the *Hare* palette for inland. The 70s were brown, the 80s off-white and pastel (Westman).
- **Status and side.** In the classical era, white on the street front and earth colours behind (Westman; Fargeveileder 2025). Mandal kept this into the present: walls to gardens and narrow alleys stay unpainted or English red or ochre, and outhouses and sea sheds are red or ochre (Mandal 2007).

### How paint ages on this coast

- **Linseed.** Linseed paint gets a fine "snakeskin" craze after about ten years and holds for 30 to 40 years before it breaks (SLKS). It dulls evenly, so a whole street of linseed paint on red or slate roofs matched without anyone planning it (Fargeveileder 2025).
- **Colour drift.** Light colours drift greyer, yellower or pinker; dark colours fade (Fargeveileder 2025). Breidablikk was repainted "ochre with brown trim" for a century. When it was examined in 2016 the colours had grown stronger coat by coat, partly through the change from linseed with earth pigments to alkyd with synthetic ones. Fine black-brown lines that sharpened the decoration had been lost (Fargeveileder 2025).
- **Mould.** Old lead-white layers act as a fungicide and hold back black mould (*svertesopp*, small black dots) (Brænne 2017).
- Failures:
  - ochre-primed coats craze and flake (Brænne 2017);
  - plastic paint over oil flakes in sheets (`house-changes.md`);
  - thick paint that sits on the surface falls off in flakes (Kulturminneplan 2010).
- **Where it fails first.** The wall and boards under window sills rot first from the water off the sill (Mandal 2007). In Mandal the north-east walls take the worst weather (Mandal 2007). Which walls weather worst in Stavanger is not documented; driving rain from the south-west is our guess (unverified).
- **Mismatched coats.** Mixing paint types gives trouble at the next repaint (Kulturminneplan 2010), so an owner's change of paint shows as patchy failure years later (unverified as a visible rule).

## 4. Shopfronts, signs and lettering

- **Shops in houses.** In the old centre the ground floor along the main streets is trade and the upper floor dwelling (Brannplan; Kulturminneplan 2010). People lived and traded in the same house or the same *bygård* (Kulturminneplan 2010). In plinth storeys the window type tells the use: cellar, wash-house, store, workshop or shop (Mandal 2007). Norem Baade in Kirkegata began as a small house early in the 1800s. Around 1850 it was lengthened to open a shop (Stavangeren 1/2016).
- **Before about 1890.** The first shopfronts in Oslo's brick blocks had windows about as wide as the windows above, sometimes set lower towards the plinth: a calm, whole front. After about 1890, with larger glass, the ground floor opened up with windows as big as possible and doors in the same opening, sometimes recessed (Bygg og Bevar, shopfronts). Plate glass in large shop windows dates from before 1915 in Denmark (SLKS).
- **Jugend shopfronts.** Kirkegata 26, a house of the 1860s, has a jugend shopfront of 1916 with one of the finest entrances in town. "Many" of Stavanger's shopfronts were jugend (Kulturminneplan 2010).
- **1930s to 1960s: funkis fronts.** The 1930s were the great period of change for shopfronts. The typical new front had a recessed door, large glass, often teak frames, and glass in the side panel too (Bygg og Bevar, shopfronts). Several wooden houses in Stavanger's centre had their shopfronts modernised in funkis style between the 1930s and 60s (Kirkegata 19, the old Hygea pharmacy; Norem Baade, Kirkegata 22; Kulturminneplan 2010). Norem Baade was made "hypermodern" with black toughened-glass panels in 1958 (Kulturminneplan 2010; Stavangeren 1/2016 says the 1950s). It was a patchwork of nearly 200 years of forms when it was sold to a chain store in 2010 and, after a fight over its 1950s front, replaced (Stavangeren 1/2016).
- **Lit signs.** One of Stavanger's first lit signs went up in 1926, a text put up by the Apostolic Faith congregation; the sign there now is from the 1970s (Kulturminneplan 2010). Neon tubes date from Paris in 1910 and reached the United States in 1923 (Wikipedia, neon sign). When neon and back-lit plastic box signs reached Stavanger's shops is not documented. Plastic box signs belong to the 1960s and 70s (unverified).
- **Control.** Plan 681 of 1974 held the centre to its streets and heights and controlled colours, light fittings and signs (`town-change.md`).
- **Late century.** Sea houses became restaurants from 1973 (Kulturminneplan 2010). From the 1980s many small shops in Oslo's brick blocks were turned into flats: windows replaced doors and granite steps were removed (Bygg og Bevar, shopfronts).
- **Lettering by decade.** Our working order, for the shopfront shelf, is unverified for Stavanger:
  - 1900s to 1920s: hand-painted lettering on a fascia board or straight on the boarding; gilded or shaded letters on glass; enamel advertising plates.
  - 1930s: applied metal or wooden letters on a fascia, black glass, the first neon.
  - 1950s: neon script, black glass, aluminium frames.
  - 1960s and 70s: back-lit plastic boxes.
  - 1980s: painted "old-style" boards as nostalgia.

  The corner's A already follows this (painted 1931, lit box 1962; `living-fabric.md`). How a sign changes hands is the shop diary's job: the band is repainted over the ghost, the box is taken down and leaves fixing holes, and the lettering ghosts through the next coat (`living-fabric.md`).

## 5. Plots, building rules and the slope

### Fires and rules

| Year | Event | What it left |
| --- | --- | --- |
| 1633 | about three quarters of the town burned | |
| 1684 | 149 buildings | the last great fire on Skagen; the sea houses after it may have changed from log to frame |
| 1716 | Østervåg, 89 buildings | |
| 1766, 1768 | Straen, 35 and 53 buildings | Gamle Stavanger rebuilt after them |
| 1795 | Østervåg, 26 larger buildings | |
| 1833 | Holmen, 60 buildings | |
| 1860 | Østervåg, Valberget and Holmen, 210 to 250 buildings | half-hips; one storey and loft, cornice at most seven ells; brick-nogged sea houses; Holmen's straighter streets; waterworks from 1863 |
| 1896 | national building law | timber houses at most two storeys and under 300 m²; a fire gable or at least 5 m between buildings |
| 1904 | Ålesund burns; national masonry rule | brick in Stavanger's brick belt; the law was narrower than proposed |
| 1956 | Gamle Stavanger's conservation plan | white repaint; stone kept |

Sources: Lokalhistoriewiki (fires); Sjøhusrekken 1993; Kulturminneplan 2010; Bygg og Bevar (murtvang).

When and how far the 1904 rule was relaxed, and where its zone in Stavanger ran, are not documented here (unverified).

### Building lines, gardens and yards

- **In the oldest districts** houses stand right on the pavement, with small "secret" gardens behind (Brochure 2021). The streets on Straen have lain where they are since at least the 1600s or 1700s (Kulturminneplan 2010).
- **In the planned rings** a strip of garden a couple of metres wide runs round the whole house. A hundred years ago these gardens had picket fences (*stakitt*) to the street rather than hedges, winding gravel paths, perennial beds, berry bushes and roses, and climbers or fruit trees on the walls (Brochure 2021). Mandal's pickets end in one symmetric point and are narrow and widely spaced so they can be painted (Mandal 2007).
- **Yards** between the old houses are paved with Hardanger slabs (Kulturminneplan 2010). The oldest districts have slate slabs, plank fences and natural-stone walls, and cast surfaces and asphalt are not allowed (Kulturminneplan 2010). In Mandal, pavements and yards were laid with unworked cobbles (Mandal 2007).
- **Distances** between buildings in the old town are mostly under 8 m (Brannplan). In the regulated rings, streets and gaps are wider (Brannplan).
- **The bygård.** The merchant's property is the dwelling on the street, the sea house on the water, a linking building and a small yard, and a terraced garden climbing the slope across the street (Sjøhusrekken 1993).

### Houses on the slope

The old town grew without plans on broken ground with large differences in level (Brannplan). The plinth takes up the slope and holds a cellar or work room on the downhill side (above). Building on the rock rather than levelling it is what the fixtures already assume (`docs/experiments.md`, the corner). We have no source for how far owners blasted or built up (unverified).

### Outbuildings and additions

- **Additions in the old town.** Roof raises and arks were built on as families grew (Kulturminneplan 2010).
- **WC additions.** In the two-family houses of the rings, small WC additions (*dotilbygg*) were built on the back as WCs came in. Today the additions are balconies (Kulturminneplan 2010).
- **Outbuildings.** Stud-framed outbuildings in the old blocks were later fitted out as rooms or joined to the houses (Brannplan). Trondheim's back buildings held stores, animals and privies (Trondheim).
- **Lofts.** Few cold lofts remain in the old town: they are fitted out, or only a small space is left at the ridge (Brannplan).

## 6. How a house reads its era at a glance

A viewer dates a house from a few cues, and the cues change with distance. Window and trim carry the street stop; roof, overhang and chimney carry 12 m and above (`house-changes.md`, What shows).

| Era | At the street stop | From 12 m and above |
| --- | --- | --- |
| Classicism, before 1860 | small symmetric front, door in the middle; two-sash windows of three panes per sash, dark; flat trim; low plinth; corner boxes | low eaves just above the windows; no overhang; red curved tile; one fat chimney mid-ridge; maybe a shed-roofed ark from the ridge |
| 1860s rules | a wide low gable to the street; half-hipped gable | broken gable ends; low cornice line with a tall roof |
| Sveitser | tall cross-post windows in surrounds with brackets and big heads; beaded boards; high plinth; a glazed veranda or porch | deep eaves with purlin ends; slate or flat tile; spires; two or more chimneys; cross gables |
| Sveitserjugend | sveitser body with small-paned or arched upper lights; simpler trim | half-hipped gable; deep eaves; one tall decorative chimney |
| Jugend | compact, asymmetric; small panes in the upper sashes; flat broad trim; a bay; coloured hall window | hipped mansard or high half-hip tight to the walls; glazed flat tile with a sheen; chimney partway down the roof |
| Nyklassisisme | symmetric; small-paned windows; columns or pediment at the door; light or pastel | high plain gable or half-hip; flat tile |
| Funkis | corner windows; two- or three-light windows, no bars; mitred corners; direction changes in the boards | flat or low hip; no dormers; striped chimney |
| Post-war | big living-room window beside small ones; mixed panel, stained; brick against timber | low broken volumes; low roofs; concrete tile |
| Tyrolean, colonial | small-paned windows with shutters; arches | steep deep-eaved roof, or a hip with a kick |

Two cues reach every distance: the depth of the eave shadow (none, then deep, then tight again) and the colour of the roof. Red curved tile is warm and ridged. Slate is grey-blue and smooth. Glazed tile has a dark sheen. Concrete is flat brown-grey. The roof is what the city camera reads; the window is what the street stop reads (unverified as a test result; to be judged with cold readers).

## What the house generator should take

### Era shelves

The shelves below replace and extend `eras.py`. Lengths are millimetres. Values marked (u) are working values, not sourced, to check on references.

| Shelf | Years | Body | Storey (floor to floor) | Plinth | Roof | Eave / verge | Windows | Cladding | Chimney |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rococo | 1700 to 1800 | merchants' houses only | 2600 (u) | low | gable, curved tile | none | two-sash, 6 to 8 small panes per sash | single-rebated, supanel | one, central |
| classical (empire) | 1790 to 1875 | 1½ storeys, double-span log box about 9.8 × 7.5 m; symmetric | 2500 to 2600 (inside 2200 to 2400) | 300 to 600 (uphill) | gable 30 to 45°; quarter-hip or half-hip after 1860; ark | 0 to 150 / 0 to 100 | two-sash, 3 upright panes per sash; cross-post on big houses | single-rebated or board-and-batten; corner boxes | one large square at mid-ridge |
| rule house | 1860 to 1885 | 1 storey and loft, cornice ≤ 4400; wide gable to street; then 2-storey hipped box | 2600 to 2800 (u) | 500 to 900 | half-hip; then full hip | 150 to 300 (u) | empire, then cross-post | double-rebated | one or two |
| sveitser | 1865 to 1910 | 1½ storeys with knee wall about 1000 (u), or 2; gable to street; cross plans on villas | 2900 to 3100 (u) | 600 to 1200 | gable 38 to 45° (u); slate or flat tile | 500 to 900 (u), purlin ends | cross-post 4 or 6 lights; T-post; Heng system 1, then 2 | double-rebated; beaded boards; vertical on knee walls | two or more, corbelled crown |
| sveitserjugend | 1905 to 1920 | as sveitser; winter gardens | 2900 (u) | 600 to 1100 | half-hipped gable; mansard later; slate or red flat tile | 500 to 800 (u) | cross-post with bars or arches; Vålandsbue | beaded boards | one tall decorative |
| jugend | 1905 to 1925 | compact, asymmetric; bays | 2900 to 3000 (u) | 500 to 900 | hipped mansard, half-hip, high; glazed flat tile on villas | 200 to 400 (u) | cross-post with small upper panes, arched middle; coloured hall windows | beaded boards with vertical fields | decorative, may stand down the roof |
| neoclassical | 1920 to 1940 | symmetric box; small houses with half-hips | 2800 (u) | 400 to 800 | high gable, half-hip, hip; flat tile, glazed on finer | 150 to 300 | small-paned, six-sash, three-light | single-rebated; horizontal in gable, vertical below (or reverse) | simple classical |
| funkis | 1930 to 1950 | box, asymmetric; curved additions | 2700 | 300 to 500 | flat, mono-pitch, low hip 15 to 25°; later low gable; flat tile or felt | 200 to 300 | two/three-light, no bars; corner; round | single-rebated with vertical fields; mitred corners | striped |
| post-war | 1945 to 1975 | two or more volumes; row houses | 2600 | 300 to 600 | low gable, hip, mono, flat; concrete tile | 300 to 500 | big living-room window; single with mullion; tilting | vertical, stained; brick panels | large, may show along gable |
| tyrolean / colonial | 1970 to 1990 | ferdighus | 2500 | 200 to 400 | steep deep-eaved; hip with kick | 600+ / 400 | small-paned with shutters | stained or painted | big stone or brick |
| sea house | 1770 to 1870 | timber frame, posts 800 apart; 1- to 4-span; gable to water | 2400 to 2800 (u) | dry stone on the quay | gable, steep (u); curved tile; hoist ark (gable or shed form) | almost none | small, at the sides | lapped vertical or board-and-batten | none |
| cannery | 1895 to 1930 | brick, plain historicist | 3500+ (u) | low | gable or low | small | large iron-framed (u) | brick | one tall factory chimney from a back-yard smokehouse |

Colours per shelf come from the colour guide's table above, weighted by status. Small classical houses are white on the front only, with earth colours behind. Windows are dark to about 1910. Trims contrast in the sailing-ship years and turn green from 1910 to 1940; pastels and blue follow from 1945 to 1955.

### Construction rules the generator follows

1. Walls are log boxes clad in boards for houses to the 1940s. Spans give the depth: about 5 m single, about 7 to 7.5 m double. Corners are boxed until funkis, then mitred.
2. Boards follow the cladding table by the year they went on, not the year the house was built. Fronts are reclad first; the original cladding survives on gables, towards yards and in alleys. This is a free history cue and a fact the diary already holds (`reclad` with a scope).
3. Board widths vary a little along a wall, fitted to the openings: seeded texture, no history.
4. Windows carry their own era and their surround's. A window replaced without its surround keeps the old head and brackets round a smaller opening only if the owner was careful. Usually the trim went with the window (`house-changes.md`). Heng's measures set the surrounds' sizes.
5. Windows are dark until about 1910 unless the diary paints them. Hinges, corner irons and putty take the window colour.
6. The overhang is the era's strongest silhouette cue: none in classicism, deep in sveitser, tight in jugend and nyklassisisme, plain in funkis.
7. Roof covering is chosen per volume by era and wealth. Curved red tile is the default to about 1880. Slate and flat tile go on sveitser and jugend. Glazed flat tile goes on rich jugend and neoclassical houses. Concrete tile comes as a later event, 1955 to 1995.
8. One chimney mid-ridge for classical houses, more for sveitser. Chimneys are brick, rendered or bare, capped with slate, zinc or iron.
9. The plinth takes the slope: low on the uphill side, a storey on the downhill side with a cellar door or a shop. It is stone in lime, later cement-rendered and painted grey.
10. Stairs to raised doors are slate treads on a rendered or rubble base, with a wrought-iron rail. They are removed when a door moves to street level.
11. No gutters before about 1850 (u); zinc after, painted in the wall colour, with angled bends; plastic from 1960.
12. Arks. A Stavanger-ark is a shed-roofed wall dormer from the ridge, flush with the wall. It is placed asymmetrically and added by a diary event, never at random. Sea houses have a hoist ark centred on the gable to the water.
13. After 1860 (in the town's regulated area) new houses take a half-hip and the cornice limit until about 1885.
14. Masonry after 1904 inside the zone the town system draws, in the period styles of the wooden town around it. A render front over timber is possible and does not mean brick.
15. Doors open inward until 1980; street doors are double until 1930, single with wide side panels after a 1930-to-50 replacement.

### The corner's five houses in their original eras

What each house was when built, from the sources above, to go into its diary and its first coats.

**A (104, 1912, jugend, a cannery owner's house, two storeys, mansard; shop 1931; café 1988).** A Stavanger jugend villa of the Eiganesveien kind:

- Body: compact and rectangular, with a small bay on the lane side.
- Roof: a high hipped mansard, tight to the walls with small eaves, in glazed flat tile (black or red).
- Windows: cross-post with small panes in the upper sashes and an arched middle field on the main front, and one coloured-glass hall window.
- Trim and walls: broad flat trim with no brackets; beaded boards with fields of vertical panel.
- Chimney: decorative, partway down the roof.
- Door: a panelled double door with fluted panels and a window.
- Colour: light walls with dark green or brown windows (Kulturminneplan 2010; Brochure 2021; Fargeveileder 2025).
- The 1931 shopfront: two bays of large glass in a funkis-era frame, a recessed door and a fascia for painted lettering (Bygg og Bevar, shopfronts; Kulturminneplan 2010).
- A choice for Øystein: built in timber, as the town system now places it, or in rendered brick, as many of Stavanger's jugend houses of the masonry-rule years are.

**B (105, 1936, funkis, rebuilt after a fire, two storeys; repainted 1987).** A Stavanger funkis house of the Bjørnøygata kind:

- Body: a two-storey box with a low hipped roof in flat tile.
- Windows: a corner window on the lane corner; two- and three-light windows, square or horizontal, with no bars; perhaps a round window at the stair.
- Walls: mitred corners with no corner boxes; single-rebated horizontal boards with vertical fields between the upper windows; thin plain trim.
- Door: smooth, with one panel and a small window.
- Chimney: banded.
- Plinth: low, rendered.
- Colour: originally greenish or greyish (Stilguide) or English red (Westman), with white trim. The 1987 coat is crisp, in the decade's off-white or pastel.
- A free history cue the diary may add: the old house's stone plinth reused under the new house (unverified as common practice).

**C (1203, 1879, a cooper's sveitser house, 1½ storeys, bislag; cheap windows 1971).** An early, modest sveitser house of the sailing-ship years:

- Body: a log box of 1½ storeys with a knee wall, gable to the lane.
- Roof and eaves: moderate eaves with visible purlin ends; red curved tile rather than slate for a cooper (u).
- Windows: four-light cross-post windows in the post-1860 or system 1 surrounds.
- Walls: double-rebated boards with corner boxes.
- Entrance: a bislag with its own small gable over the door.
- Chimneys: one or two.
- Colour: ochre walls, brown windows and trim, the trims picked out (Fargeveileder 2025; Westman).
- In 1971 the street windows become husmorvinduer: smaller openings, thin flat trim, the old heads gone. The small attic window high in the gable keeps its surround (Heng 2015; Brochure 2021).

**D (1107, 1828, a fisherman's empire house, 1½ storeys; lean-to 1950; street windows 1965; boarded 1986).** A small empire house of Straen:

- Body: a log box of about 7 × 7 m with low storeys.
- Front: symmetric, the door in the middle; two-sash windows with three upright panes per sash, dark; flat trim.
- Walls: single-rebated or board-and-batten, with corner boxes.
- Roof: a gable roof with almost no overhang, in red curved tile, with one big square chimney mid-ridge.
- Plinth: a low plinth uphill and a tall dry-stone plinth built onto the rock downhill.
- Colour: herring-oil ochre or red. A fisherman would rarely afford a lead-white front (Fargeveileder 2025).

**E (304, 1826, the oldest and smallest; street windows 1965).** The same type as D, smaller:

- One storey and a loft, its plain gable closing the lane: two windows below, a small loft window above, no verge overhang.

D and E are the same type and date, so the diaries must make them differ. Two proposals for Øystein. First, E gets a Stavanger-ark on its eave side, added in the herring years when the household grew (a fact with a date). Second, E's front is white over a red back (a richer fisherman, or a later owner), while D stays ochre all round.

### Parts for plan step 2, ranked by how much each carries the read

1. Windows with their surrounds, by era and as replacements: empire two-sash; sveitser cross-post in Heng's system 1 and 2; jugend small-paned upper sashes; funkis two- and three-light and corner; husmorvindu with the shrunken opening and infill. They read at the street stop and carry every change of owner. Make the surround a part of its own (heads, brackets, side boards, sills, cove), fitted to Heng's measures.
2. Roof covering and form: red single-curved tile; slate; glazed flat tile; concrete tile. Gable, half-hip, hipped mansard, low hip, flat. They read from 12 m and the city camera, and the covering is the main history cue from above.
3. Eaves and verges: none; deep with purlin and rafter ends; tight. Barge boards at their sizes. This is the silhouette at every view.
4. Cladding profiles and corners: single-rebated, double-rebated, beaded, board-and-batten, vertical funkis fields, corner boxes and mitres. They read as rhythm and shadow at the street stop and as texture at 12 m. The cladding also carries the gable-versus-front history.
5. Chimneys: classical square mid-ridge, sveitser with corbelled crown, decorative jugend, striped funkis; caps and flashing. They read from 12 m and above.
6. Doors and the entrance: empire double door with fanlight; sveitser door; jugend door; funkis door; 1930-50 single door with side panels; the bislag; the slate stair with iron rail. They read at the street stop.
7. Plinths and cellar openings on the slope: stone, rendered, painted grey. They join the stone already built.
8. Paint coats per era (the coatings layer), with dark windows and status sides.
9. A's shopfront: 1931 display bays, recessed door, fascia; then the 1962 box and the 1988 patch (`living-fabric.md`).
10. Gutters and downpipes: zinc with angled bends, plastic. They are small, but a strong 1960s cue up close.
11. Additions: Stavanger-ark, bislag, lean-to, WC addition.
12. Ornament: spires, gable crosses, brackets, the lily. These are few on the corner's modest houses, rich on the context villas.

### Proposed changes to `eras.py`

- Classical:
  - roof: gable about 85%, half-hip about 15% after 1860, no mansard (no source shows mansards on Stavanger's classical houses);
  - eave: 300 down to about 100, gable overhang to about 50;
  - storey: 2850 down to 2500 to 2600;
  - walls: weight earth colours and a white front over an earth back before 1850; white after 1850.
- Add shelves: rule house (1860 to 1885), sveitserjugend (1905 to 1920), nyklassisisme (1920 to 1940; already proposed in `house-changes.md`), Tyrolean and colonial (1970 to 1990), sea house, cannery.
- Chalet: pitch 45 to 52° down to about 38 to 45° as the real base (Trondheim, Mandal; Stavanger unverified), leaving the push to the style dial. Roofs mostly slate and flat tile, with curved red tile for modest early houses.
- Jugend: add glazed flat tiles in red, black, blue and green for villas.
- Functionalist: roofs mostly flat clay tile, some felt, rather than all black; add mitred corners as a rule.

## Gaps

- **Measured window and door sizes per era.** No source here gave opening sizes; the shelves above use working values. Next: measure them from Stavanger byarkiv's photographs and from Heng's poster, whose 1:10 drawings are free at the museum and the city's service centre. The book *Gamle trehus* (Drange, Aanensen and Brænne) is the other source.
- **Stavanger's roof pitches and eave depths per era.** We have Trondheim and Mandal measures only.
- The 1904 masonry rule in Stavanger: its zone, and when and how it was relaxed. Not found.
- The 1860 rules' extent: town-wide, or only the burned area.
- Shop signs and lettering by decade in Norway: enamel, painted fascias, neon, box signs. Only a few dated facts (1926, 1958). The NTNU thesis, Stavanger byarkiv's photographs and DigitaltMuseum's sign collections are the next reads. Downloading images needs Øystein's OK.
- **Sola's thesis** (*Vern og hvite løgner i Stavanger*, NTNU 2025) in full: the colour guide is drawn from it, but the thesis may date the white repaint street by street.
- Paint failure on this coast: which walls weather worst in Stavanger, how fast oil and alkyd fail in salt air, a repaint cycle. Not found (`house-changes.md` names the same gap).
- Glass: drawn glass and float dates for Norway (only Danish dates here).
- Gjenreisning and post-war type houses: only secondary sources; the roof pitch rests on one example.
- Dragestil, prayer houses and schools: materials and colours in Stavanger not checked.
- **Search budget.** This study's web search budget ran out before it could check paint ageing and the Sandnes tile works' products. A follow-up pass can close those.

## Sources

- Stavanger kommune, *Ta vare på sjelå* (2021), the style brochure (Brochure 2021): https://www.stavanger.kommune.no/siteassets/bolig-og-bygg/byantikvaren/trehusbykampanje-2021/trehusbyen-brosjyre-2021.pdf
- Stavanger kommune, *Hvilken stil er mitt hus?* (Stilguide): https://www.stavanger.kommune.no/bolig-og-bygg/byantikvaren/hvilken-stil-er-mitt-hus/
- Stavanger kommune, *Regulert vern betyr strengere detaljkrav* (draft; Detaljkrav): https://www.stavanger.kommune.no/bolig-og-bygg/byantikvaren/regulert-vern-betyr-strengere-detaljkrav/
- Stavanger kommune, *Kommunedelplan for kulturminner 2010-2025* (Kulturminneplan 2010): https://www.stavanger.kommune.no/siteassets/samfunnsutvikling/planer/kommunedelplaner/kulturminner/kulturminneplan-stavanger-2010-2025-tekstdel.pdf
- Stavanger kommune, *Forveden på farger? Fargeveileder for trehusbyen* (2025, reprint 2026; Fargeveileder 2025): https://www.stavanger.kommune.no/siteassets/bolig-og-bygg/byantikvaren/fargeveileder/hefte-fargeveileder-opptrykk-2026.pdf and https://www.stavanger.kommune.no/bolig-og-bygg/byantikvaren/fargeveileder/
- Stavanger kommune, *Sjøhusrekken i Stavanger* (1993, quoting Schjelderup, Stavanger Museum årbok 1991; Sjøhusrekken 1993): https://www.stavanger.kommune.no/siteassets/skjema-a-a/samfunnsutvikling/reguleringsplan/sjohusrekken-1993.pdf
- Stavanger kommune, *Brannsikkerhetsplan for trehusbebyggelsen i Stavanger* (Brannplan): https://www.Stavanger.kommune.no/siteassets/bolig-og-bygg/brann-og-feiing/brannsikkerhetsplan-for-trehusbebyggelsen-i-stavanger.pdf
- Heng 2015, *Vindusomramming på sveitserhus i Stavanger*, Museum Stavanger årbok 125: https://www.stavanger.kommune.no/siteassets/bolig-og-bygg/byantikvaren/detaljkrav/vindusomramming-pa-sveitserhus-i-stavanger-av-michael-heng-2015.pdf
- Heng & Windsholt 2020, *Rehabilitering i trehusbyen*, Museum Stavanger årbok 130: https://www.museumstavanger.no/uploads/arbok/2020/2020-MICHAEL-HENG-OG-HANNE-WINDSHOLT-Rehabilitering-i-trehusbyen.pdf
- *Stavangeren* 1/2016, Byhistorisk forening (canneries, Norem Baade, the post office): https://byhistoriskforening.org/wp-content/uploads/2022/01/Stavangeren-1-2016-web.pdf
- Mandal kommune 2007, *Veileder for bevaringsområdene* (Mandal 2007): https://www.dibk.no/globalassets/byggeskikk/lokale-byggeskikkveiledere/mandal---veileder-for-bevaringsomradene.pdf
- Trondheim kommune, Byantikvaren, *Veileder for Møllenberg, Kirkesletten og Rosenborg* (Trondheim): https://www.trondheim.kommune.no/globalassets/10-bilder-og-filer/10-byutvikling/miljoenheten/byantikvaren/veileder-mollenberg/-veileder-for-mollenberg-rosenborg-og-kirkesletten-.pdf
- Bergen kommune, *Renovering av tak* (Bergen roofs): https://www.bergen.kommune.no/hvaskjer/tema/kulturminner-i-bergen/istandsetting-og-vedlikehold/renovering-av-tak
- Mørk 2012, *Stilarter i arkitekturen*, NTNU (SINTEF Byggforsk's style dates): https://www.ntnu.no/documents/20658136/1241076138/Stilarter_i_arkitekturen-bygningsvern_2012_M_I_M%C3%B8rk.pdf/83a7fe86-c53d-4c11-a6b5-8b3c6f1d565c
- SNL:
  - sveitserstil: https://snl.no/sveitserstil
  - dragestil: https://snl.no/dragestil
  - jugendstil: https://snl.no/jugendstil
  - Chr. Bjelland & Co (secondary): https://snl.no/Chr._Bjelland_&_Co
- Bygg og Bevar:
  - *Norske trehus og murtvang*: https://byggogbevar.no/pusse-opp/brann/artikler/norske-trehus-og-murtvang/
  - *Hvorfor brannsikring av trehusbebyggelse vant over murtvang*: https://byggogbevar.no/pusse-opp/brann/artikler/hvorfor-brannsikring-av-trehusbebyggelse-vant-over-murtvang-i-norge/
  - *Farger, form og ferdighus*: https://byggogbevar.no/pusse-opp/maling/artikler/farger-form-og-ferdighus/
  - *Hvilken stil har din villa?*: https://byggogbevar.no/pusse-opp/byggeskikk/hvilken-stil-har-din-villa/
  - *Murbyens butikkfasader*: https://byggogbevar.no/inspirasjon/artikler/murbyens-butikkfasader
  - *Gjenreisningen av en landsdel* (secondary): https://byggogbevar.no/inspirasjon/artikler/gjenreisningen-av-en-landsdel/
- Lokalhistoriewiki:
  - *Liste over bybranner*: https://lokalhistoriewiki.no/wiki/Liste_over_bybranner
  - *Bakken (Stavanger)*: https://lokalhistoriewiki.no/wiki/Bakken_(Stavanger)
  - *Gamle Stavanger*: https://lokalhistoriewiki.no/wiki/Gamle_Stavanger
- Westman, *Fargebruken gjennom tidene*, ifi.no: https://www.ifi.no/artikkel/445998/last-ned
- Brænne 2017, *Praktisk malerarbeid på eldre trehus*: https://karmoy.kommune.no/_f/i97c5bec3-4a30-4c8d-93bf-bc378b92a320/2017-praktisk-malerarbeid.pdf
- Slots- og Kulturstyrelsen, *Datering af vinduer 1700-1950* (SLKS): https://slks.dk/fileadmin/user_upload/SLKS/Omraader/Kulturarv/Bygningsfredning/Gode_raad_om_vedligeholdelse/5.4_Datering_af_vinduer_1700-1950.pdf
- Nor, *Restaurering av vinduer og dører* (Viggja; glass types): https://www.trondheim.kommune.no/globalassets/10-bilder-og-filer/10-byutvikling/miljoenheten/byantikvaren/seminar---a-reparere-en-fasade/14_jarle-nor.pdf
- Jærmuseet (Sandnes tile works; the yearbook PDF linked from the page): https://www.jaermuseet.no/samlingar/?p=551
- NTNU, Sola 2025, *Hvite løgner* (thesis page): https://www.ntnu.no/masterutstilling-arkitektur/hvite-logner
- Norwegian Wikipedia, *Bordkledning*: https://no.wikipedia.org/wiki/Bordkledning
- Wikipedia (secondary):
  - *Gamle Stavanger*: https://en.wikipedia.org/wiki/Gamle_Stavanger
  - *Neon sign*: https://en.wikipedia.org/wiki/Neon_sign
  - *Ålesund*: https://en.wikipedia.org/wiki/%C3%85lesund
- Visit Norway, Gamle Stavanger (173 houses; the Stavanger ark; secondary): https://www.visitnorway.no/listings/gamle-stavanger/14660/
- Artemisia, *Fra Stavangers murarkitektur* (list of masonry buildings; secondary): https://www.artemisia.no/arc/historisk/stavanger/stavanger.html
- Life in Norway, *The story of the Ålesund fire* (secondary): https://www.lifeinnorway.net/alesund-city-fire/
- Repo cross-references: `house-changes.md`, `town-change.md`, `stavanger-centre.md`, `city-types.md`, `docs/town-plan.md`, `docs/building-system.md`, `docs/living-fabric.md`, `fixtures/lt1-corner.json`.
