---
name: unity-conventions
description: Use when writing C#, shaders or scenes in the Game Lab's Unity project: folder layout, URP settings, determinism and seeding, assembling places from the kit, the world view and scene views, lighting and the shading model.
---

# Unity conventions for the Game Lab

## Setup

- Unity 6, Universal Render Pipeline (URP). Not HDRP, not the Built-in pipeline.
- Linear colour space. Shaders in Shader Graph or HLSL; custom render passes through URP renderer features.
- For editor work use the Unity skills (`unity-cli`, `urp-postprocessing`, `shader-graph-create-custom-node`, `validate-urp-render-graph-renderer-feature`) and the Unity MCP server when it is connected.

## Folders

```
Assets/
  Art/Kit/<family>/        exported kit pieces (from blender-generators)
  Art/Palette/             the shared palette texture and its materials
  Code/World/              reading engine data, the world view
  Code/Assembly/           building places from the kit
  Code/Scenes/             scene views: staging, cameras, interaction
  Code/Characters/         bodies, faces, animation layers
  Shaders/                 the shading model and post effects
  Experiments/<LTn>/       one folder and scene per experiment
fixtures/                  fake engine data (JSON) until the export exists
reviews/<LTn>/             contact sheets and renders
```

## Determinism

The same world, seed and history must always give the same picture.

- Never use `UnityEngine.Random` or `System.Random` for anything visible. Use the project's own hash (`Code/Core/Hash.cs`: a fixed 64-bit hash such as SplitMix64) so results cannot change between Unity or .NET versions.
- Seed every visual choice from stable ids: `Hash(worldSeed, buildingId, version, "facade")`. `version` increases only when the building's history changes it (a new owner, a renovation, a closure).
- No visual choice may depend on frame time, load order or what the camera saw first.

## Unity never decides

Unity reads engine facts and draws them. It never invents a fact (who is in the bar, whether a shop is open, how a gig went). Player actions go back to the engine as events. If something needs a fact the engine does not have, add a line to `docs/engine-requests.md` and use a clearly marked fixture value meanwhile.

## Assembling a place

A building and the business in it are separate:

- **Building:** footprint, storeys, era of construction, later extensions (each with its own era), condition.
- **Business:** kind, owner, opening year, state (thriving, struggling, closed), sign, fit-out.

The assembler picks kit pieces slot by slot (footprint, facade, roof, shopfront, sign, props, wear) from these facts, through one mapping table (`Code/Assembly/PlaceGrammar.cs`, which follows `docs/place-grammar.md`). Every mapping must say which engine fact drives it. A slot with no driving fact uses the seed only, and is marked as such.

## Views

- **World view:** a raised, free camera over a neighbourhood; LOD1 pieces; characters simple and instanced.
- **Scene view:** a bounded, walkable set; LOD0 pieces; a staged camera (fixed angles or a rail), composed and lit per kind of scene. Moving between views is a cut or a short move through a doorway, never a seamless zoom.

## Light and shading

- The look lives in our own shading model, not in engine defaults: light ramps, gradient fog by distance, a ground-bounce colour, and a colour script per time of day and weather.
- One shade rule for every surface (`StreetLooks.hlsl`): shade is the surface's own pigment times the light falling on it (the sky term, the sun, bounce, lamps), and how much of the sky's colour shade takes is the light's setting (`_OS_ShadowChroma`, from the stage and style), never a material's. No per-material shadow tint, no shade hue shifted per object, no colour held against the light at dusk (SEASON's lesson, `docs/research/colour-and-shading.md`, rule 1). A material sets its pigment and its form; the light sets everything else. Mud on grey days is answered by the pigment's own strength and by value, never by a tint. Test any light or colour change in drizzle, low sun and blue hour.
- It must not depend on true real-time global illumination. URP's real-time GI is a preview; if it becomes stable it is an extra layer on top.
- No baked lightmaps for generated places: they change.
- Every look is checked in morning, grey afternoon and evening light.

## Performance

- One palette material for most of the kit, GPU instancing, static batching only for what never changes.
- Crowds: full characters only near the camera or when they matter to the story; the rest instanced with animation baked into textures.
