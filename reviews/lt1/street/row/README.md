# The row: 107, 108 and 109 together, the light step (r02)

- Bad: the panes are not near-black at the street stop. 108's open glass is L26 (r01 L24), and ref 10's panes are L6–18. A diagnostic render with no reflection puts the room alone at L19. The reflection adds the rest, though the far shore is already darker than a real one: Barrel Quay and the Holm, at 0.25 of the horizon's light. Under overcast, any front of houses, across a street or across the water, is about 0.3–0.4 of the horizon's light. So ref 10's near-black is mostly its print's toe. The lever left is a toe in the shared tonemapper, which the rock session also uses, so it is not changed here.
- Bad: 109's ox-red is 0.8 L lighter than r01's in overcast (L25.3 against L24.5) and a little cleaner (C15.7 against 12.8).
- Holds beside r01 in overcast, street stop: 108's white boards at L82.8 (r01 82.4); 107's lower boards' clean-to-grime ΔL 35.9 (r01 35.3). Low sun is r01's key, unchanged, within 0.3 L.
- Kept from l06: the overcast's hard band down 108's gable is gone, the key is soft, the ground darkens at each house's foot, and 109's peel falls off board by board.
- Sheers hang only where a household lives and keeps the house (a livedIn type, not boarded): 108. 107 (boarded) and 109 (a warehouse) show the bare room.

Sheets: `r02-overcast.jpg` and `r02-lowsun.jpg` (rows eye, street stop, 12 m, high; columns r01 P | r02 P | r01 Pc | r02 Pc), `r02-close-glass.jpg` (r01 | r02, refs 10 and 04), `r02-close-109.jpg` and `r02-close-108-gable.jpg`. r01 is the floor at the row's framing: each house's accepted paint with `STREET_GROUNDSKY=0`.

    STREET_ROW="107:cache/street/gen/107h:cache/street/bake/107z4/out-r02 108:cache/street/gen/108u:cache/street/bake/108u/out-r02 109:cache/street/gen/109u:cache/street/bake/109u/out-r02" python3 tools/unity_lock.py run -- bash blender/parts/street/run/render.sh row r02 eye,street,raised,high P,Pc overcast,lowsun

Cost:
- Triangles are unchanged (near/street/city): 107 24,590/5,459/705; 108 24,832/7,792/778; 109 53,230/9,452/748.
- A row of 50 of 109: 4.3, 4.6 and 4.8 ms; near3 5.4 ms (`cache/street/renders/t05/timing.md`).
- Pages: 21.3, 85.3 and 85.3 MB, plus one 4 MB ground sky map for the scene.
