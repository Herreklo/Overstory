# 107's roof: baked course planes beside every tile

`sheet.jpg`: baked planes on the left, every course tile by tile (the floor) on the right. Rows are eye level looking up the roof (near level), the street stop and 12 m (street level). Grey Cycles, one sun; the 12 m row is from before the verge fix. `verge.jpg`: the street stop's gable, before the verge fix, after it, and all tiles.

**Bad first**
- The planes read darker and more gridded than real tiles. This test multiplies the baked occlusion over Cycles' own, so the engine's shader is the judge.
- Near is now 24,318 triangles, 700 under the cap.

**What changed:** the planes sit on the tiles' crests, so there is no ledge where the real courses stop. Each plane course has real tiles at both verges, so the rake draws their rolls against the sky. The ridge shares one chart at both levels, so the street ridge is baked.
