# Experiments

Newest first. Each entry: the question, how it is judged, then the outcome: what we keep, what we drop, and for each reference that came up, what we take and what we leave.

---

## LT1: the harbour street, 1989

**Status:** open.

**The question:** which of three looks makes a west-coast harbour street beautiful in ordinary light, at street level and from above?

**The setting:** a fictional harbour town rooted in the Norwegian west coast, in 1989: three years after the oil-price crash, a boom town in a slump. White timber houses, quay warehouses, cobbles, 1980s shopfronts and streetlamps, some shops empty.

**What is built:**
- The building system's first version (`docs/building-system.md`): building diaries from fixtures, a resolver, and era shelves of parts for timber houses and a quay warehouse. Stylisation (proportions, lean, sag, irregularity, bevels, trim size) is a set of parameters.
- A street in Unity from fixture diaries: about eight houses and two warehouses on a quay, cobbles, street lamps and simple harbour water.
- Four looks on the same geometry, differing only in the shading function and lines: A plain URP Lit (control), B painted ramp, C soft toon, D graphic (hard steps and fading edge lines). Everything else is shared: palette, light rig per weather, shadows, ambient occlusion, fog, Neutral tonemapping, one grade, bright window emissives.
- Three lights: grey drizzle with wet ground, low winter sun, blue hour with lit windows.
- Two cameras: street level and the raised neighbourhood view.

**How it is judged:**
1. *Shape step, in Blender:* houses resolved from diaries at several strengths of stylisation, and one building shown in three years. Øystein picks a strength; it becomes the shape language for the street.
2. *Contact sheet, in Unity:* 24 frames (4 looks × 3 lights × 2 cameras), each also in greyscale and at one-eighth size, plus a five-second camera move per look. Judged blind, labelled A to D, with drizzle counting most. A yes is one look Øystein wants to keep looking at in grey drizzle, that reads at both distances and can go from moody to cozy on the same street.
3. *Variety check:* the generator on 30 fresh diaries. No two alike; everything that reads as history traces to a diary entry, and seeded texture claims none; the same diary gives the same building after a reload.

**What it does not test:** people, interiors, history over time, snow and seasons, the final palette.

**Shape step, so far (19 October):**
- Øystein picked strong over gentle.
- Wild is dropped. Its proportions were the attraction; its deformation (a lean of up to 4.5°, up to half a metre of sag, bowing walls) read as caricature and broke construction: walls stood outside roofs.
- Stronger is added: wild's proportions with strong's deformation. Strong and stronger are compared on the same street.
- The first wild sheet went out with a known fault. Since then, building checks and a stress test gate every sheet: 1,564 random buildings at strong and stronger pass, and the street fixtures pass in every year.
- A blind reviewer found what the checks could not see: floating ridge caps, merged double chimneys, window heads hidden by deep eaves, dangling barge ends, and bays that hit porches, cross-gables and the eave. Each became a rule (`docs/building-system.md`, Fitting), and bays became checked parts.
