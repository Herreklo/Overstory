# Naming

Every name the records, kinds, packs and caches use, on one page. The regexes at the end are the grammar: `tools/naming.py` reads them from this file for the validator and writes them into the schemas (`--render`), and the validator fails when a schema's pattern drifts from its regex here. Names are lowercase ASCII. A name says what a thing is and where, never how it looks today, so it survives every change but a rule change. Seeds are drawn from ids (`blender/resolver/hashing.py`), so renaming an id re-seeds what it names: a rule change that renames ships a migration and a new baseline.

## Ids

An id is a path. After the record come segments, each a name (`tr-3`, `bed`) or a count (`0`, `12`). A name is a slot; a count after a slot is a fill of it; a name after a fill is a slot that fill holds (the crack in that stone). A piece ends a fill's id with `#<i>`.

| Level | Form | Example | Minted by |
| --- | --- | --- | --- |
| Record | `<prefix>-<token>` | `bld-104`, `st-gully`, `p-812` | its owner: the engine for its records; the pack script for `generated-past` (a counter from the world seed and plan unit); by hand for `authored` |
| Event | `<record>/<n>`, from 1 | `bld-104/9` | the owner, appended, never renumbered |
| Slot | `<record>/<name>[/<name> or /<fill>/<name>...]` | `bld-104/op-f0-0`, `st-gully/fl-0/tr-3/sl-1` | the plan stage, by the kind's rule below |
| Fill | `<slot>/<n>`, from 0 | `st-gully/fl-0/tr-3/sl-1/0` (the stone as laid) | appended with its event, never renumbered |
| Piece | `<fill>#<i>`, from 0 | `st-gully/fl-0/tr-3/sl-1/0#1` (a cracked stone's second half) | the geometry stage; never stored in a record |

- Every count in an id starts at 0, as the generators count: flights, steps, positions, bays, storeys (the ground storey is 0), fills and pieces. Event numbers start at 1, as their owners mint them (`docs/engine-contract.md`).
- Fills of one slot count in date order; fills placed by one event follow the kind's role order.
- A slot's place and size are fixed when it is made. A later change of place or size closes it and makes a new slot; a new slot whose name would repeat an older one's takes `-g<n>` (the second generation is `-g1`).
- A name that only groups others (a flight, a tread, a wall's panel) is a slot of type `group`: it holds slots, no fills.
- Ids are written in full in files. A second pack's ids take `<pack>:` in front when loaded, never in files.
- **Seed keys** (`hashing.py`): an id alone seeds the part function that makes its thing; every other draw adds its purpose, words and integers saying what it decides (`"lay"`, `"crack", "gap"`, `"campaign", 1961`). A purpose never stands for a thing: what can be replaced, picked or pinned has a slot. A tread's slabs and a row's setts are keyed on their fill and its pieces, so a stone laid anew draws anew; the other stones on their slot, which stands for its first fill until upkeep gives it a second.
- A record's token is minted, never made from a display name. `stone.py` and `wall.py` still fall back to the lane's name when a stair's facts carry no id, and eight of the plan's stairs come out with `--`, which the record rule refuses: three passages at a negative x (`st-passage-at--172`) and five ways whose names hold a comma or brackets (`st-the-way-to-d--1107--empty-since-1986`). They are a defect, minted afresh at step 2b's re-baseline.

**Record prefixes.** Engine-owned: `p` person, `h` household, `pl` place, `v` venture, `g` group, `e` engine event. Ours: `bld` building, `st` stair or flight of steps, `wl` wall, `way` street, lane, square or quay, `plot`, `unit` plan unit, `lamp`, `tree`, `plant` other planted thing, `sign`, `room`, `doc` poster, paper or deed, `photo`, `item` carried thing or garment, `trace` social trace, `org` a keeper that is not a person (a department, a firm), `ug` underground run, `rock` natural stone, `act` ground act, `ci` a lamp circuit (a street's lamps switched together: `ci-street-photocell`). A new prefix is added here before its first record.

## The stair's slots

As the generators name them since step 0b (`stone.py`, `upkeep.py`). Flights count from the foot; steps from the foot of their flight; positions across a step from the left, looking up the stair.

| Slot | Form under the stair | Type |
| --- | --- | --- |
| Flight; the landing at its start after a turn | `fl-<n>`; `fl-<n>/turn` | group |
| Step (its tread) | `fl-<n>/tr-<i>` | group |
| Slab, riser stone, kerb stone | `<step>/sl-<k>`, `<step>/rs-<k>`, `<step>/kb-<k>` | socket |
| Joint left of slab k; its pointing; its front | `<step>/jt-<k>`, `<step>/jt-<k>/pt`, `<step>/jt-<k>/front` | socket |
| The step's bed; its pointing | `<step>/bed`, `<step>/bed/pt` | socket |
| The setts of a step; their bed; a row (the setts are the pieces of its fill) | `<step>/sets`, `<step>/sets/bed`, `<step>/sets/rw-<r>` | group, socket, socket |
| A landing behind a step; its rows; their slabs and joints | `<step>/ld`, `<landing>/rw-<r>`, `<row>/sl-<k>`, `<row>/jt-<k>` | group, group, socket, socket |
| A stone's crack; a dab of cement on it | `<slab fill>/ck`, `<slab fill>/dab` | socket |
| A crack's pointing; its front | `<slab fill>/ck/pt`, `<slab fill>/ck/front` | socket |
| The walking line; a handrail | `walk`, `fl-<n>/hr-<l or r>` | affordance |

## The wall's slots

As `wall.py` names them since step 0b. A panel is the wall's length beside one flight on one side; courses count from the foot; a stone's place counts along its course; the hearting a fallen stone shows counts by rows from the foot, then along each row. The wall's heads (its closed ends) have no slots yet: a head's stones are keyed on their course with `"head"`, the end (0 the foot, 1 the far end) and their count across it, and its backing on the panel with `"head"` and the end. They take slots at step 2b's re-baseline.

| Slot | Form under the wall | Type |
| --- | --- | --- |
| Panel | `fl-<n>/<l or r>` | group |
| Course; a stone's place in it | `<panel>/co-<k>`, `<course>/sp-<j>` | group, socket |
| A hearting stone, seen where the face stone has fallen | `<place>/ht-<m>` | socket |
| Backing cell; coping | `<panel>/bk-<j>-<0 or 1>`, `<panel>/cp-<c>` | socket |

## The house's slots

Faces are the house's own: `f` front (to the way it is addressed from), `b` back, `l` left and `r` right as seen from outside facing the front; an addition's faces take its count first (`a0f`). Compass faces would rename every slot when a plan is laid again. Storeys count from the ground storey, 0 (the cellar is `m1`); bays from the left seen from outside, 0.

| Slot | Form | Example | Type |
| --- | --- | --- | --- |
| Opening, over one bay or several | `op-<face><storey>-<bay>`, `op-<face><storey>-<first>-<last>` | `op-f0-0`, `op-f0-0-1` (the 1931 shop opening) | opening |
| A window's pane | `<opening>/<fill>/pn-<n>`, left to right, top to bottom | `op-f0-2/0/pn-3` | pane |
| A socket at an opening; on a face | `<opening>/sk-<name>`, `sk-<face>-<name>-<n>` | `op-f0-1/sk-sill`, `sk-f-downpipe-0` | socket |
| An affordance at an opening | `<opening>/af-<name>` | `op-f0-3/af-step` | affordance |
| Surface region: a face; its plinth, gable, or one storey's band | `sf-<face>`, `-pl`, `-gb`, `-s<storey>` | `sf-f`, `sf-l-pl` | surface |
| Roof plane, by the face it falls to; a mansard's lower and upper | `rf-<face>`, `-lo`, `-up` | `rf-f-lo` | surface |
| Dormer | `dm-<face>-<bay>` | `dm-f-1` | opening |
| Works (a scaffold's phases are its fills) | `wk-<face>`, `wk-site` | `wk-f` | works |

Each kind's rule is written here before its kind file.

## Other names

- **Part paths** are the part's place under `blender/parts/`, two to four segments, hyphens in names: `stone/slate/slab`, `window/cross-arch`. Code turns hyphens into underscores. A part's definition is `packs/<pack>/parts/<path>.json`. A **family** is a part path or its first segments (`window`, `stone/slate`, `window/cross-arch`): kinds and sockets admit parts by family, and a part's definition is the narrowest family, one path with its variants.
- **Kinds** (`house`, `stair`, `natural-stone`), **materials** (`slate`, `pine-board`), **eras** (`jugend`), **event kinds** (`shop-fitted`), **rules** (`upkeep.patchwork`: the module, then the rule), **shader families** (`street`, `stone`, `tree`) and **packs** (`stavanger-1989`) are words with hyphens.
- **Units** are named by their index in the pack's world frame (x east, y north, millimetres from the pack's origin): `<unit>-<i>-<j>` with `i = floor(x / size)`, a negative index written with `m` (`ch-12-m3`). `ch` is the 4 m draw chunk, `pg` the 16 m page group, `ce` the 32 m cell, `lc` the 64 m land and streaming chunk, `bk` the 128 m block. Every size is a power of two from one origin, so the index fixes the corner. The level is its own field (`l0` to `l4`), never part of a unit's name.
- **Container files** are `<unit>.osc`: one a block (`bk-3-m1.osc`: records, shells, L4, ground) and one a land chunk for near levels (`lc-6-m2.osc`).
- **Maps** (`p0`, `p1`, `h1`, `h2`, `h3`, `bent-normal`, `litter`, `shell-albedo`), **layers** (`polish`, `lichen`) and **fields** (`wind-salt`, `sun-dose`) are short words; a page is `<page group or cell>/<map>`: `pg-3-m1/p0`. The map of leaves and litter is `litter`, since `deposit` is a layer.
- **Face classes** are `street`, `yard`, `roof` and `ground` (`schemas/maps.json`).

## The grammar

`{name}` stands for the regex named above it, as a group `(?:...)` when it holds a `|` outside brackets. Each pattern matches a whole name. The kinds' rules match a slot's path after `<record>/`.

```regex
word: [a-z]+(-[a-z0-9]+)*
count: 0|[1-9][0-9]*
ordinal: [1-9][0-9]*
prefix: bld|st|wl|way|plot|unit|lamp|tree|plant|sign|room|doc|photo|item|trace|org|ug|rock|act|p|h|pl|v|g|e
record: {prefix}-[a-z0-9]+(-[a-z0-9]+)*
event: {record}/{ordinal}
slot-path: {word}(/({count}/)?{word})*
slot: {record}/{slot-path}
fill: {slot}/{count}
piece: {fill}#{count}
engine-person: (p|h)-[a-z0-9]+(-[a-z0-9]+)*
part-path: [a-z][a-z0-9]*(-[a-z0-9]+)*(/[a-z][a-z0-9]*(-[a-z0-9]+)*){1,3}
family: [a-z][a-z0-9]*(-[a-z0-9]+)*(/[a-z][a-z0-9]*(-[a-z0-9]+)*){0,3}
kind: [a-z]+(-[a-z]+)*
rule: {word}(\.{word})*
pack: [a-z]+(-[a-z0-9]+)*
unit-index: 0|m?[1-9][0-9]*
unit: (ch|pg|ce|lc|bk)-{unit-index}-{unit-index}
container-unit: (lc|bk)-{unit-index}-{unit-index}
level: l[0-4]
map: [a-z][a-z0-9]*(-[a-z0-9]+)*
page: (pg|ce)-{unit-index}-{unit-index}/{map}
generation: (-g{ordinal})?
stair-flight: fl-{count}
circuit: ci-[a-z0-9]+(-[a-z0-9]+)*
term: {word}(\.{word})*
stair-turn: {stair-flight}/turn
stair-step: {stair-flight}/tr-{count}
stair-landing: {stair-step}/ld
stair-row: ({stair-landing}|{stair-turn})/rw-{count}
stair-slab: ({stair-step}|{stair-row})/sl-{count}
stair-riser: {stair-step}/rs-{count}
stair-kerb: {stair-step}/kb-{count}
stair-joint: ({stair-step}|{stair-row})/jt-{count}
stair-joint-part: {stair-joint}/(pt|front)
stair-bed: {stair-step}/(bed|bed/pt|sets/bed)
stair-setts: {stair-step}/sets
stair-sett-row: {stair-setts}/rw-{count}
stair-flaw: {stair-slab}/{count}/(ck|dab)
stair-flaw-part: {stair-slab}/{count}/ck/(pt|front)
stair-affordance: walk|{stair-flight}/hr-[lr]
wall-panel: fl-{count}/[lr]
wall-course: {wall-panel}/co-{count}
wall-stone: {wall-course}/sp-{count}
wall-hearting: {wall-stone}/ht-{count}
wall-backing: {wall-panel}/bk-{count}-[01]
wall-coping: {wall-panel}/cp-{count}
house-face: (a{count})?[fblr]
house-storey: m1|{count}
house-opening: op-{house-face}{house-storey}-{count}(-{count})?{generation}
house-pane: {house-opening}/{count}/pn-{count}
house-opening-socket: {house-opening}/sk-{word}
house-face-socket: sk-{house-face}-{word}-{count}{generation}
house-affordance: {house-opening}/af-{word}
house-surface: sf-{house-face}(-(pl|gb|s{house-storey}))?{generation}
house-roof: rf-{house-face}(-(lo|up))?{generation}
house-dormer: dm-{house-face}-{count}{generation}
house-works: wk-({house-face}|site)
```
