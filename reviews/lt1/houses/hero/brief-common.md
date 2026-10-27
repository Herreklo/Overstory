# Houses as hero assets: what both builders share (27 October, the elements lead)

Overstory (`/Users/oystein/code/Overstory`, branch `lt/1-harbour-street`) builds a 1989 Stavanger harbour street in Unity 6 URP, from Blender generators run by script. The walked corner's houses C (chalet 1879, white, slate), D (classical 1828, empty and boarded, pantiles) and E (classical 1826, in the fog above) are being rebuilt as hero assets.

**The bar** (Øystein): "I want us to make houses like the best games does it (the best in our range). like very very well made 3d assets - still using our style, our economy etc." Judge every still as a top art director: is it true (to the facts and the archive), and is it outstanding beside the best-made games of our range (Lake, Tiny Glade, Dishonored 2's facades, Firewatch's restraint)? Never accept a still you have not looked at.

## Read first
- `CLAUDE.md`; the shared brief `/Users/oystein/Library/Application Support/Claude/side-session-notes/local_0e3ca6d7-2c63-47bd-84ff-694d8f731ac7/corner-elements-brief.md` (the loop, the facts rule, Unity and Blender, the rules every brief carries).
- `reviews/lt1/houses/hero/handover.md`, `reviews/lt1/houses/hero/craft.md` (how the best small teams build houses; its "For us" list is binding).
- `reviews/lt1/art-direction/README.md`: "What matters", "Every element", "The houses". The frame: `reviews/lt1/art-direction/engine/street-1750-sea-fog.png`.
- References: `docs/references/houses/` (archive photos: 01, 07, 09 especially), `docs/references/games/` (11 Lake, 01 Dishonored 2, 14b Kentucky Route Zero lit house).
- The skills `.claude/skills/blender-generators/SKILL.md` and `unity-conventions/SKILL.md`.

## Where it is judged: the painted corner
The corner is judged in the painted corner, where `ArtDirection/PaintSurface.shader` replaces every material. Its values (Paint.json) and shaders are the art direction's: never edit `LT1ArtPasses.cs`, `Paint.json`, anything in `unity/Assets/Experiments/LT1/ArtDirection/`, the hook files, `M_Sky.mat` or `LT1_Heart.unity`. What the houses control is **form** (geometry, normals, real depth) and the **mesh's channels**, which PaintSurface reads (its header lists them): UV1 x kind (soup.KINDS), UV2 x a piece's seed, UV3 the bake (x sky), UV4 y a lit window's seed, UV5 x the height on a board from its lap edge (0) to its top (1), UV6 x the coat scheme, UV7 x a sill's run-off. It lights a face by its normal (up light, side mid, down dark), draws the board's lap line itself, and makes trims the found edges. So depth reads where a face turns: a sill's top against its dark underside, a cap's shadow band, a casing's side, a corner board's proud edge. Push depth, not size (timber.json `push`).

**Four views, every round** (the coordinator, after Øystein opened the app: "Wow, why do everything look so bad???"): eye-foot, street, into12 and high, plus your close view; a round that breaks in any of them is not accepted. The app and `tools/painted_corner.py` draw one tier for every view (Paint.json "street") until per-distance levels land, so the street tier must hold at eye level too. Build the city tier as well.

Baseline painted stills of the current hero build (untracked, look at them first, resized to about 1400 px with `sips -Z 1400`): `reviews/lt1/houses/hero/painted/p00-1750-sea-fog-{street,eye-foot,c-east,c-wide,d-west,d-win}.png`, each with `-grey` and `-eighth`.

## Commands
- **Build** into your own folder (Blender's Python; numpy is only there), about 10 s:
  `/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python tools/houses.py -- --houses C,D,E --out cache/houses-<you> --tiers near,street`
- **Painted stills** (through the Unity lock, one run at a time; three element agents share it, so batch views in one run):
  `python3 tools/unity_lock.py run --owner "houses <you>" --purpose "<what>" -- /Applications/Unity/Hub/Editor/6000.6.6f1/Unity.app/Contents/MacOS/Unity -batchmode -quit -projectPath $PWD/unity -executeMethod Overstory.EditorTools.LT1Houses.Painted -mesh cache/houses-<you> -into reviews/lt1/houses/hero/<you>/<round> -views c-east,eye-foot -tier near -moment 1750-sea-fog -elements none -size 1920x1080 -data <your scratch>/paint.json -logFile <your scratch>/painted.log`
  Views: LT1Houses.Views (c-east, c-back, d-west, c-win, d-win, e-win, c-wide, c-eave, c-roof, d-roof, d-eave, e-roof...) and LT1Stone.Views (eye-foot, street). The street view takes `-tier street`. Read the log's first `error CS` or exception after every run.
- **Grey form** (House.shader, raking light; good for judging form): `-executeMethod Overstory.EditorTools.LT1Houses.Still -mesh cache/houses-<you> -out reviews/lt1/houses/hero/<you>/<round> -houses C,D,E -moment 1300-drizzle,1600-low-sun -view c-win,c-east -looks grey` (delete the `*-grey-grey.png` duplicates).
- **Budgets:** `python3 tools/check.py --houses cache/houses-<you>`: a house at most 40,000 triangles near and 8,000 street. Today C 45.2k / 8.0k, D 56.6k / 8.4k, E 40.6k / 6.6k: all but E's street fail.
- Look at a still at about 1400 px wide (a full 1920 still costs a lot of context); crop with `sips -c H W --cropOffset Y X` to judge a part close.

## Rules
- Facts drive history: anything that reads as history comes from the record (`fixtures/lt1-corner.json`) or the coat data (`blender/parts/house/coats.py`, `packs/stavanger-1989/paint.json`). Seeded irregularity claims no history and is seeded through `blender/resolver/hashing.py`. Sizes and pushes are data in `packs/stavanger-1989/timber.json`, never numbers in code.
- Two builders work at once on separate files (below). Re-read a shared file just before you edit it, edit only your own keys or region, and keep every file importable after each edit. If the build fails in the other builder's file, wait a minute and retry; never edit their region.
- Never touch the other elements' files: `blender/parts/trees/`, `blender/generators/growth.py`, `growth.json`, `blender/generators/bedrock.py`, `tools/corner_site.py`, `unity/Assets/Experiments/LT1/Corner/`, `unity/Assets/Code/Editor/Corner/`.
- Commit only your own paths (`git commit -m "LT1: houses: <what>" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <paths>`), small stills only (resize to 1600 px), and push to `lt/1-harbour-street` (if rejected: `git pull --no-rebase --no-edit`, then push). Never stash, reset, restore or switch branches. Generated meshes stay out of git.
- No new rule, design doc or proposal. Øystein's Mac is his: no osascript or computer-use.
- At about 250 messages, stop at a pushed point with a few lines in `reviews/lt1/houses/hero/<you>-handover.md`.

## Your report (your last message)
The final stills' paths (painted c-east and eye-foot or your part's close view in blue hour; the grey form view; one drizzle still), what holds and what does not yet as a strict reviewer would say it, the budgets as measured, your commits.
