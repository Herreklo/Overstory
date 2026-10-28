# 107 alone (s01): the whole house from its record, beside the p3 corner

- Bad: at the street stop it is a plain white box on empty ground, not yet stunning. The wear doesn't carry: p3's runs read under every window, while 107's are faint and its peel sits at the foot. The roof's patches mottle, and the chimney is a pale stub.
- Bad: the boarded openings are flat planes behind blue-grey battens that read as painted, with no sash, glass or leaf behind them (leaves are step 3). The low sun grazes the front, so the street stop in that light is flat.
- Holds: it reads as a 1½-storey house of 1828 with a 1950 lean-to, not a kiosk. Trims, steps, plinth corner, verges and roof are all whole, nothing is tuned per house, and the counts are near 24,318 / 25k and street 6,155 / 8k triangles.

`sheet.jpg`: top row is the p3 floor, then the street stop (20 m) in clay and colour, overcast. Bottom row is p3 in colour, then eye level in clay overcast and in colour under low sun. The stills come from Unity, from `blender/parts/street/run/render.sh 107 s01` at 9496a88.

## s03: p3's rules ported, roof seam A/B (29 October)

- Bad: the roof seam still shows at the street stop and from 12 m. It is not geometry. The baked page differs between courses 1–2 (baked from the near tiles) and 3 up (carried onto the planes from the bake level): occlusion 0.62 against 0.80, cavity 0.34 against 0.43, with identical normals. The planes' microshadow (`_OS_PLANE`, in `s03-seam.jpg`: 0 left, 1 right) adds dark dashes, not rolls, so it stays at 0.
- Bad: at p3's own cameras (`s03-floor.jpg`: p3 left, 107 right) the marks under 107's first window have p3's character (the tongue, runs, peel at the foot) but read weaker. The page is 90 px/m against p3's 128, and the camera frames the corner wider than p3's, so the corner's origin differs from p3's.
- Holds: p3 is unchanged by the shader change. All 16 of p3-final3's stills re-rendered pixel-identical (maximum difference 0). The paint is now p3's own runoff, tongue and peel, with no recalibration: the front is p3's and the other walls only lower.
