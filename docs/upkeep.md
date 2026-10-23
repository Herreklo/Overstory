# Upkeep

The repair strand of the living fabric (`docs/living-fabric.md`: one record and one runner for every made or planted thing, flow through shared fields, a history budget per view). How a built or planted thing changes after it is made: who keeps it, how well, and what is done to it when it wears, settles, breaks or dies. Every system shares it: stone, walls, paving, quays, houses, roofs, timber and trees (`docs/foundations.md`, The shared surface layers, 6). Its research is `docs/research/repairs.md` (who repaired what, how, with what, and how it looks), with `docs/research/house-changes.md` for houses. Its code is `blender/generators/upkeep.py`, its parts are `blender/parts/repair/`, and its materials are the shaders' own (cement in `Stone.shader`).

## In short

- **UK1** A repair follows its year's practice and materials (lime to about 1910, cement dabs from 1910, concrete casts 1940 to 1965, asphalt on paving everywhere after 1960, stone again from about 1980). After 20 to 40 years one in its own material differs in form and growth, not colour; in another material, for good (disputed). Evidence: `research/repairs.md`. Reopens: none named.
- **UK2** Four ways: left alone, patched, a campaign, renewed. A campaign's scope is its cause's reach; spot work stays under about a quarter of a part, past that the whole part; a reset reuses its own stones (over nine in ten), then depot stone, then new. Evidence: `research/repairs.md`. Reopens: none named.
- **UK3** Starting rates, unverified: a tended public part has a campaign every 30 to 60 years, renewal once in 80 to 150; untended, nothing until it fails; a thirty-step flight up to one quick fix a decade before 1960, one or two after. Evidence: `research/repairs.md`. Reopens: none named.
- **UK4** Keepers, care and works are facts (fixtures until request 6); patchwork drawn from them, seeded, claims no dated event; a repair a story needs is a fact with its cause. Evidence: `facts-contract.md`. Reopens: none named.
- **UK5** A campaign or renewal reaches what its cause reaches, rounded up to the unit people replace together, with one choice of era, technique and style. A repair matches when the keeper can and wants to, and every mix of old and new names its cause. Evidence: `research/house-changes.md`, `research/repairs.md`. Reopens: a true mix no cause explains.

## What we want

- **Real practice.** A repair looks the way the town or an owner of its year would have made it, with what that year had at hand. A step is not new in an old flight because a story wanted a dark band.
- **Spread over the thing and the years.** Repairs follow their causes, and most causes act on a stretch: frost lifts a run of steps, water washes out a bed, a wall bulges along its weak length. So repairs come in runs, and quick fixes are scattered between them. One part different from all the rest needs a cause that touched one part.
- **Readable, never loud.** After twenty to forty years, a repair in the thing's own material differs in form and growth, not colour: a straighter line, fresher joints, smaller lichen, no hollow. A repair in another material (cement, concrete, asphalt, a brick) differs for good.

## Four ways a thing changes (UK2)

1. **Left alone.** It wears, settles, cracks, grows over and loses corners for as long as no one acts. Neglect shows, and it is a fact of who kept the thing and how well.
2. **Patched.** Quick fixes, one at a time, by a lone workman, an owner or a neighbour: a cement dab in a broken corner, cement smeared into a crack, a wedge under a rocking step, an asphalt blob in a sett street, a brick in a stone wall, a tin patch on a board. Cheap, local, made with whatever the decade had, and often laid over an earlier patch, since a patch weakens its own edges.
3. **Worked in a campaign.** A crew over part of the thing, planned and paid for: a flight reset from landing to landing, a wall's bulged length rebuilt, a strip of setts relaid over a new main. The scope is the cause's reach. Spot work stays under about a quarter of a part; past that the crew does the whole part. A campaign reuses the thing's own material where it can (the town's depot of old stone matches in wear and colour) and brings new material only for what is broken.
4. **Renewed.** Made new, whole: a flight recast, a street repaved, a front reclad, a tree replanted in an old row. Its history begins again from that year, in its own material or the era's new one, beside neighbours that kept theirs.

## How a work spreads (UK5)

Every thing follows one logic, so a house reads as one house with a history and never as a patchwork:
1. **No change without a cause.** A part changes only through a work or an event in the record, or as patchwork drawn from its keepers' care (UK4).
2. **A campaign or a renewal reaches what its cause reaches, rounded up to the unit people replace together.** Each kind names its units: a pane, a window, a front's windows, a wall's cladding, a roof plane, a run of steps from landing to landing. Spot work stays under about a quarter of a part; past that the whole part (UK2). A patch stays one piece.
3. **One work, one choice.** Its era, technique, style and member are chosen once for its whole reach.
4. **A repair matches when the keeper can and wants to.** It reuses the old part or a salvaged one (depot stone), or one of the same profile still made, as care, means and protection allow. Otherwise it shows, and the mismatch is a dated fact with its own technique and member (UK1).
5. **A true mix has a cause in the record.** In a two-family house each floor's owner may restore their own floor, so the house shows two window types for years. An original attic window is often left high in the gable. A husmorvindu often replaced two old windows and made the opening smaller, and its surround went with it. Owners bought mass-produced "old style" parts, and neighbours copied the errors. A back wall shows a cheaper colour than the street front (`docs/research/house-changes.md`).

The house's resolver picks a work's cells by this reach (BS2). A machine check holds it: a part whose era or technique differs from the rest of its unit names the work that put it there, and a work smaller than its unit names why.

## Who keeps it, and how well

A thing's upkeep is a fact, decade by decade: who kept it (the town's road department, the harbour, a utility, an owner, a cooperative) and how much they cared. The town's care follows its budgets. Oslo cut its paving to almost nothing after the 1899 crash, and after about 1960 patched its setts with asphalt instead of keeping them. An owner's care follows money and whether they live there. The same flight is kept differently in the 1930s and the 1970s, and it shows in what was patched and with what.

## Materials by era (UK1)

What a crew or an owner had at hand (research, Materials by era):

| Years | Pointing and patches | Bigger work |
| --- | --- | --- |
| to about 1910 | lime mortar, tar, a stone wedge | the thing's own stone |
| 1910 to 1930 | cement for dabs and cracks; pointing still lime | depot stone, concrete slabs |
| 1930 to 1965 | lime and cement, drawn as cement | depot stone; concrete casts and steps 1940 to 1965 |
| 1965 to 1989 | masonry cement; asphalt for paving, everywhere after 1960 | concrete, asphalt; stone again from about 1980 |

## How each repair looks and ages

Each repair is its own material with its own date, aged by the same layers as everything else: weathering from its year, grime and film, lichen from its own bare years, moss in its joints from when its bed was disturbed.

- **A reset part** is the same stone with its own hollow and lichen, bedded level again: a straighter line, fresh joints in the crew's mortar, moss in the joints restarted, lichen torn where hands gripped its edges.
- **Depot stone** is weathered, so it matches in tone. Its lichen is partly kept from the heap, its polish is old and even, and its hollow does not follow the flight's walking line.
- **Cement**, struck the day of the repair, is pale and warm with its sand showing. On this coast it is half grey within six years and near its old grey by twenty. It takes an algae film where it stays damp, crazes finely, and is lost from joints with the years, so the soil and moss behind it show. A cement dab's shape is the trowel's: it fills the break to the broken edge, skins thinly onto the stone round it, and has a rounded shoulder.
- **Lime pointing** washes out in a few decades, leaving soil and moss.
- **Asphalt**, when paving comes, is black and sharp-edged when new, greys as its binder oxidises, and cracks and settles at its edges first.

## Per system

- **Steps** (built): settling and frost, cracks across long slabs, corners off the nosings where loads are dropped and people go; campaigns reset runs; quick fixes dab corners, smear cracks and wedge rocking steps.
- **Walls**: bulges along a weak length; a rebuilt panel in fresher stone with other coursing, cement pointing (light, smeared, the stone beside it decaying), a concrete cap or footing on a road's wall, a brick in a gap.
- **Paving**: utility trenches (relaid in their own setts, nearly invisible; in new setts or asphalt, they show), asphalt blobs over sunken patches, kerbs reset or swapped.
- **Quays**: spot pointing, a concrete toe against scour, a fallen stretch rebuilt in concrete.
- **Houses** (`docs/research/house-changes.md`): a gable reclad on one side, render patched in its era's mix, windows changed floor by floor in a two-family house, a cement fillet where a roof meets a chimney.
- **Roofs and timber**: odd tiles and slates in another colour, a board replaced and fresher than its neighbours, a tin patch, a fillet that cracks within years.
- **Trees**: pruning cuts and their callus, a lopped limb, a pollarding campaign along a street, a cable or a stake, a young tree replanted where an old one fell (its cause a fact).

## How it is made

- **The life.** `upkeep.py` runs a thing's parts decade by decade from its facts: damage by cause, patchwork at the research's rates (a public flight of about thirty steps: up to one quick fix a decade before 1960, one or two after), the facts' campaigns and renewals in their years. It returns each part's state now, and the generator writes it into the part's record (`unity/Assets/Art/Stone/stone_gully.json`, each step's `life`), so anything that shows the thing reads the same history.
- **The parts.** A repair's own shape is a part in `blender/parts/repair/`, fitted by the generator to what it repairs: cement dabs fitted to a slab's broken outline, pointing struck along a joint to the stone's top.
- **The drawing.** Each repair material is a kind the surface's shader draws with its own pigment and ageing (cement as kinds 4, pointing, and 5, a dab, in `Stone.shader`), under the same light and growth as everything else.
- **Facts and interpretation** (UK4). Who kept a thing, how well, and the works done on it are facts: from the engine's fabric pass when it comes (`docs/engine-requests.md`, 6), authored in fixtures until then. Patchwork is drawn from those facts, seeded, as a shabby front is drawn from age and upkeep: it claims that the thing was kept this way, never a dated event of its own. A repair a story needs (a step replaced after a fall) is a fact with its cause.

## Rates and rules (starting values, unverified; UK3)

- A campaign's scope is its cause's reach: from landing to landing, or the lower run where water gathers; a wall's bulged length, 2 to 6 m; a sett relay over a block's width.
- A tended public part gets a campaign every 30 to 60 years and full renewal once in 80 to 150; an untended one gets nothing until it fails.
- Quick fixes go to what shows most: a corner gone from the walking line first, then an open crack, then a step that rocks.
- A reset reuses the part's own stones (more than nine in ten); broken ones come from the depot, and only failing that new stone, or concrete from 1940 to 1965.
