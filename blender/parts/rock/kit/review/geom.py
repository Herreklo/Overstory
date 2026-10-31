# geom.py -- --out FILE: the boulder's designed planes, arrises, breaks and structure in the levels' frame (z 0 at the
# turf, as house.blend and house.json), for the paintover
import json, os, sys, math
import numpy as np
sys.argv += [] ; ROOT = "/Users/oystein/code/Overstory"
sys.path.insert(0, f"{ROOT}/blender/parts/rock/kit")
import sculpt as SC
a = sys.argv[sys.argv.index("--") + 1:]; OUT = a[a.index("--out") + 1]
X = next(x for x in SC.MS.M["masses"] if x["id"] == "boulder"); sc = SC.Sculpt(X); sink = X["sinkM"]
fs = sc.ms.faces; lift = np.array([0, 0, sink])
L = lambda p: (np.asarray(p) - lift).tolist()
faces = [dict(key=f[3], n=f[0].tolist(), off=float(f[1] - f[0][2] * sink), kind=f[2]) for f in fs]
edges = [dict(i=i, j=j, a=fs[i][3], b=fs[j][3], P0=L(P0), P1=L(P1), kinds=[fs[i][2], fs[j][2]]) for i, j, P0, P1 in sc.edges()]
rounds = [dict(nA=fs[r["i"]][0].tolist(), nB=fs[r["j"]][0].tolist(), P0=L(r["P0"]), t=r["t"].tolist(), ln=r["ln"], r0=r["w"][0], r1=r["w"][1]) for r in sc.pairs]
breaks = [dict(why=b["why"], f=b["f"].tolist(), of=float(b["of"] - b["f"][2] * sink),
               walls=[(wn.tolist(), float(ow - wn[2] * sink)) for wn, ow in b["walls"]], at=L(b["at"])) for b in sc.breaks]
sets = {name: n.tolist() for name, n in sc.sets}
json.dump(dict(sink=sink, faces=faces, edges=edges, rounds=rounds, breaks=breaks, sets=sets, weather=sc.weather.tolist(),
               spall=X.get("spall")), open(OUT, "w"), indent=1)
print("GEOM", len(faces), "faces", len(edges), "edges", len(breaks), "breaks", {k: [round(x, 3) for x in v] for k, v in sets.items()})
for e in edges: print("EDGE", e["a"], e["b"], e["kinds"], [round(x, 2) for x in e["P0"]], [round(x, 2) for x in e["P1"]])
for b in breaks: print("BREAK", b["why"], [round(x, 2) for x in b["at"]])
