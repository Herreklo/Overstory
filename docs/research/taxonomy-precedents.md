# Taxonomy: precedents

The evidence behind the shape of `docs/taxonomy.md`: how other games and tools keep materials, forms and ageing apart so that each new thing is cheap to add.

## In short

- The construction industry keeps an element (a wall), the system that builds it, the products in it and their materials in separate tables (Uniclass). IFC attaches materials to an element's parts and type. That is TX1's kind, construction, part and material.
- A thing defined once and made of any material that has the right properties (RimWorld) is TX4.
- Shared templates for materials, and a living thing that carries the material it yields (Dwarf Fortress), are TX2 and TX3.
- A parent material with variants that change only what differs is in our own engine (Unity's Material Variants), for TX2.
- Wear worked out from the shape, so one generator serves every material (Substance 3D Painter), is TX5.
- Light always-read files, detail loaded when needed, and no repeated or conflicting instructions (Anthropic's guidance for Claude 5 models) is TX7.

## What each shows

**Uniclass (NBS).** The UK's classification for the built environment keeps separate tables for Elements/functions ("general elements like walls, decks, and roofs"), Systems ("collections of products brought together to operate as systems"), Products ("individual products used across the built environment, including those assembled to create systems"), and a proposed Materials table ("terracotta, Portland cement, white pine"). What we take: kind, construction, part and member as four separate things (TX1). What we leave: the tables for projects, roles and drawings, which a game doesn't need.

**IFC (buildingSMART).** Materials attach to an element type or to an occurrence, and "the material associated to the element occurrence overrides the material associated to the element type". Doors and windows assign materials to named parts (lining, framing, glazing) through a constituent set. What we take: materials belong to parts, and the thing in the town can differ from its type (TX1, TX4). What we leave: the override. Our constructions and records name the member outright.

**RimWorld.** A building or item can be made of a material chosen before it is made, and "the stats of the chosen material affect the stats of the end product". The building lists the categories it accepts (Stony, Woody, Metallic, Fabric, Leathery), and any material in them can be used: stony blocks include granite, limestone, marble, sandstone and slate. A new stone works in every stone building with no change to the buildings. What we take: parts ask for properties (TX4). What we leave: categories alone are too coarse for us, since a split step needs a stone that breaks in slabs, so we ask for properties within a family.

**Dwarf Fortress.** Inorganic materials (stones, gems, metals) are defined in raw files and placed in the world by geological layer: sedimentary, metamorphic, igneous intrusive or extrusive, and soils. A tree's wood is a material defined in the tree's own entry, and cutting the tree down "will yield logs made of this material". What we take: a rock belongs to the ground it comes from, and a living thing names what it yields (TX3). What we leave: materials defined inside the living thing; we keep the tree and its boards as two members joined by `yields`, since they change in different ways.

**Unity Material Variants.** A variant "inherits properties from a parent material", and a parent can have many children. What we take: one family and many members (TX2). What we leave: inherited numbers. A member states all its numbers, so no value is hidden in its parent.

**Substance 3D Painter.** The Metal Edge Wear generator finds edges from the baked curvature map and keeps wear out of occluded places with the ambient occlusion map. It reads the shape, so one generator serves every model and material. What we take: a change is written once and reads the thing's shape and facts (TX5); our wear reads the record's feet and hands as well.

**Anthropic, on context for Claude 5 models.** Keep `CLAUDE.md` light and use "a tree of files that can be loaded at the right time". Remove conflicting or excessive instructions, since a model spends effort reconciling them. What we take: the map, In shorts first, data last, one home per fact (TX7, Q20).

## Sources

- NBS, [Uniclass tables explained](https://www.thenbs.com/knowledge/uniclass-tables-explained)
- buildingSMART, [IfcRelAssociatesMaterial (IFC 4.3)](https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcRelAssociatesMaterial.htm)
- RimWorld Wiki, [Stuff](https://rimworldwiki.com/wiki/Stuff)
- Dwarf Fortress Wiki, [Inorganic material definition token](https://www.dwarffortresswiki.org/index.php/v0.34:Inorganic_material_definition_token) and [Plant token](https://dwarffortresswiki.org/index.php/Plant_token)
- Unity Manual, [Material Variant inheritance](https://docs.unity3d.com/Manual/materialvariant-tasks.html)
- Adobe, [Metal Edge Wear generator](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/effects/generators/metal-edge-wear)
- Anthropic, [The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)
