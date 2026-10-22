# Studios whose worlds are stone: stairs and walls

Research for the port's step 2b, 22 October: FromSoftware, Bluepoint, Ninja Theory, Warhorse and Asobo, read from talk captions, studio diaries and the artists' own posts. Marks: (secondary) means from a report or summary; (unverified) means my own inference.

## In short

1. **No source in this group gives a chamfer size, joint width or depth, texel density, triangle count per step or wall module, or LOD distance.** The numbers gap in `stone.md` stands. What these studios give is method, plus the ratios in findings 3 and 7.
2. **Masonry is rigid sculpted blocks from one shared kit.**
   - Bluepoint kitbashes pre-textured blocks so that every column looks "mined from the same quarry" (House, GDC 2019, 21:00).
   - Its tiling materials were assembled from a sculpted block kit (Wagner).
   - Shadow of the Colossus used 88 sculpted rocks for the whole world (Via).
3. **Delete buried faces, then reduce: about five to one, with no visible loss.** A kitbashed pillar went from 10,000 polygons to about 2,000 that "looks basically the same". Its collision mesh has about 150 (House, 22:32 and 23:30).
4. **Joints are filled by a tool that knows the bond.** Bricks are placed to match the tileable sculpt's 0–1 UV layout (House, 30:32). Houdini breaks walls at brick boundaries and generates "in-between filler" (Noclip 2021, 49:30).
5. **Light makes the shape and shadow makes the cracks.**
   - Shadow of the Colossus vertex- and alpha-blends five complete materials into one (80.lv).
   - Demon's Souls grows tessellated bricks where artists paint blend channels.
   - Screen-space shadows darken its cracks and block specular there.
   - Without light and shadow, shape does not read (Digital Foundry 2020, 29:31, 56:31, 57:30).
6. **FromSoftware's restraint (secondary), from CEDEC+KYUSHU 2021:**
   - two or three wall or fence assets, damaged and blended to hide repetition;
   - straight lines read as polygons;
   - detailed floors on unremarkable maps add little;
   - light only where damage should be seen;
   - big, medium and small objects.
7. **Most detail is never seen.** Ninja Theory cut many Nanite meshes by 50% "with no visible difference". Memory is "the new poly count", and from the game camera "you're missing 90% of that detail" (Digital Foundry 2024, 7:01–8:31). For the first Hellblade, the goal was 95% reusable assets, with one environment artist (diary 4, 2014, 3:30–4:00).
8. **Far versions come after near ones.** Bluepoint built everything high-poly first, then efficient versions and low-poly impostors of distant levels (Noclip, 18:30–19:31). Its LOD system was automated and non-destructive (80.lv). No distances are given.
9. **Warhorse fixes sizes for play.** Doors are "always 1 by 2 meters", although real ones varied (Holík, 2020, 24:00). Props share one atlas, varied by HSL and blend maps (Svojša).
10. **Asobo:** no primary breakdown was found.

## Evidence by studio

**Bluepoint.**
- **House, GDC 2019** (EjkQv8L3z4s). House is a Bluepoint technical artist. His Houdini asset culls occluded points before reducing. His collision is built as a VDB, snapped to a grid, then dissolved.
- **Digital Foundry, 2020** (9O--CnN056E). The team "did not really set very strict polygon limits" and relied instead on "a very good LOD system". A boss in Shadow of the Colossus had about 250,000 triangles (27:30).
- **Noclip, 2021** (hCBJ2fiiUXk). An impostor could be built only once its level was final (18:30).
- **80.lv on Shadow of the Colossus:**
  - rock walls are "many singular rock instances, each sculpted in ZBrush";
  - a world-projected material ties the walls together;
  - decals tie the walls into the ground;
  - a level holds over 50,000 objects;
  - steps were rescaled "to be in tune with Wander's height".
- **80.lv on Demon's Souls:**
  - "a modular asset set" for each of four sub-themes;
  - "Seldom did we use full Megascan materials", using masks and decals instead;
  - texel density was held through the masking setup, with no value given;
  - beams have identical end rings, so instances snap together.
- **ArtStation:**
  - Via's kits for Latria and Shrine of Storms (mD0vg1, Xn3dOD);
  - Wagner thanks Via "for sculpting the block kit";
  - Villapando's "Shared Material Method" (OoXBrk).

**FromSoftware.**
- **CEDEC+KYUSHU 2021**, a talk by three artists from the Fukuoka studio, read in 4Gamer's and Famitsu's reports (secondary):
  - assets are damaged and blended (gallery No. 028);
  - ivy hides seams in the wall textures;
  - few lights, aimed at fracture faces (No. 030–031);
  - walls are clearly too high to climb, never "mid-height";
  - no numbers, and no stairs.
- **CGWorld's GCC '19 report on Sekiro:** unread, the site was down.
- **Elden Ring and Dark Souls:** no artist's own stone breakdown was found.

**Ninja Theory.**
- **Hellblade diary 4:** read through IGN's mirror, as the original is age-restricted.
- **PC Gamer, 2015** (secondary): a tower built from one set of blocks; details "recycled and resized".
- **Hellblade II diary 01, 2023:** drone photogrammetry at about 7 cm a pixel, against the 2 m elevation model (1:30–2:00).
- **Xbox Wire, 20 May 2024:** "over 370 pieces of photogrammetry", against one in the first game (Attwell). Rocks made by hand look too perfect.

**Warhorse.**
- **Höschl, 2024** (1:30): more stone towards Kuttenberg's centre, poorer streets near the wall. Material follows a fact.
- **Game World Art, 2026** (secondary): a former Rockstar artist reads the wireframes (14:00–16:00).
  - Roads are vertex-painted, with extra cuts supporting the paint.
  - Decals sit on a second UV layer of the same mesh.

**Asobo.**
- The artists' ArtStation posts list only their roles.
- Two French videos would not load (YouTube rate limit).
- The GDC 2023 session is unread, as GDC Vault was in maintenance.

## What this means for our redraw

- **Our way is theirs, without the stretching.** Bluepoint's block kit and shared materials are the primary example that `stone.md` claim 6 lacked. Each of our blocks is still cut to its fact size.
- **Deletion and reduction alone miss the budget.** Five to one takes 962,000 triangles to about 190,000. That is still two to three times the production note's 69,000–139,000 (unverified).
- **Joints are filler generated from the layout, never a slot.** Material and light set a joint's value, not a dark gap.
- **Restraint by count:** two or three variants a run, one lit accent where damage should be seen, and a calm walking surface. This matches `stone.md` In short 10.
- **Test half the triangles before fixing L0.** Run an A/B of each step at half its triangles, at eye level and at the street stop (unverified without Nanite).
- **Cracks:** block specular there, from the joint mask, without darkening the joints (unverified).

## Claims confirmed, corrected or unread

| Claim | Where | Verdict |
| --- | --- | --- |
| Shared sculpted faces on light blocks; Star Citizen "med poly" (secondary) | stone.md 6; production 3 | Method confirmed by a primary source, Bluepoint's block kit (Wagner, Via, House). Star Citizen unread |
| 20–120 triangles a wall stone, 150–400 a step (unverified) | stone.md 8; production 4 | Unread. Nearest primary figures: a pillar cut from 10,000 to 2,000 polygons, and a 150-polygon collision mesh |
| 240 MB; 4 MB a m²; 11 MB a face kind (unverified) | stone.md 6; Making | Unread. Ninja Theory confirms memory as the binding budget, but gives no figure |
| Three-slicing (unverified) | Making | Unread. Bluepoint's beams snap together whole; nothing is lengthened |
| Vertices added where vertex paint changes | Making | Supported (secondary) by KCD2's road cuts |
| Texture array, not atlas (unverified) | production 4.7 | Unread. Warhorse uses an atlas for props, with nothing said on mips |
| Bogaert; Schreibt; Arm's ten fragments; fragile custom normals (secondary); proxy shadows (unverified) | production | Not touched |
| No breakdown for Sekiro, Elden Ring or Hellblade | stone.md Gaps | Narrowed: FromSoftware's method (secondary) and Hellblade's numbers (primary). Still no stair or wall breakdown |
| Restraint sources from games are secondary, with no numbers per stone | stone.md Gaps | Stands. FromSoftware adds "two or three" (secondary) |

## Gaps

- No primary figure for chamfers, joints, texel density, triangles or LOD distances.
- Sources unread:
  - Bluepoint's and Asobo's GDC Vault sessions;
  - CGWorld's Sekiro report (503);
  - Adobe's article on Bluepoint (it redirects);
  - Warhorse's modding wiki (a bot check, not bypassed);
  - two French Plague Tale videos (429);
  - the CEDEC+KYUSHU 2021 slides.

## Downloads

All files are English captions, saved to `~/code/overstory-sources/studios-stone-worlds/`. Each source URL is `youtube.com/watch?v=` plus the file's id. Nothing else was saved.

| date | file | source URL | size | read for |
| --- | --- | --- | --- | --- |
| 22 Oct | -2vHPB1kj4I.en.vtt | watch?v=-2vHPB1kj4I | 128,584 B | Warhorse: IGN, KCD2 city tour |
| 22 Oct | 0jdoXC_T5j0.en.vtt | watch?v=0jdoXC_T5j0 | 17,708 B | Warhorse: CRYENGINE; nothing on stone |
| 22 Oct | 9O--CnN056E.en.vtt | watch?v=9O--CnN056E | 636,960 B | Bluepoint: Digital Foundry |
| 22 Oct | EjkQv8L3z4s.en.vtt | watch?v=EjkQv8L3z4s | 293,648 B | Bluepoint: House, GDC 2019 |
| 22 Oct | HgiOcDhWziU.en.vtt | watch?v=HgiOcDhWziU | 718,310 B | Ninja Theory: BAFTA Guru; nothing on stone |
| 22 Oct | QbXAJVtW9HY.en.vtt | watch?v=QbXAJVtW9HY | 281,498 B | Warhorse: Game World Art (secondary) |
| 22 Oct | hCBJ2fiiUXk.en.vtt | watch?v=hCBJ2fiiUXk | 562,257 B | Bluepoint: Noclip |
| 22 Oct | pYZVKI-j0YM.en.vtt | watch?v=pYZVKI-j0YM | 76,719 B | Ninja Theory: Hellblade II diary 01 |
| 22 Oct | rpSJLHOHGPA.en.vtt | watch?v=rpSJLHOHGPA | 214,001 B | Warhorse: Holík stream |
| 22 Oct | u-zmFVzUmPc.en.vtt | watch?v=u-zmFVzUmPc | 371,253 B | Ninja Theory: Digital Foundry |
| 22 Oct | urldhIiRmS8.en.vtt | watch?v=urldhIiRmS8 | 49,185 B | Ninja Theory: Hellblade diary 4 |
| 22 Oct | wH0wOBsvxMc.en.vtt | watch?v=wH0wOBsvxMc | 27,809 B | Warhorse: CRYENGINE; nothing on stone |
| 22 Oct | yUA54vD0P1k.en.vtt | watch?v=yUA54vD0P1k | 634,222 B | Bluepoint: lead lighting artist; nothing on stone |
