# -- --out out.png [--row] path@x0,y0,x1,y1@scale ... : crops stacked (or in a row), padded white, a gap between
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import numpy as np, pio
a = sys.argv[sys.argv.index("--") + 1:]; out = a[a.index("--out") + 1]; row = "--row" in a
items = [x for x in a if "@" in x]; tiles = []
for it in items:
    p, b, k = it.split("@"); x0, y0, x1, y1 = map(int, b.split(",")); k = int(k)
    t = pio.load(p)[y0:y1, x0:x1, :3]; t = np.repeat(np.repeat(t, k, 0), k, 1); tiles.append(t)
if row:
    h = max(t.shape[0] for t in tiles); seq = []
    for t in tiles: seq += [np.pad(t, ((0, h - t.shape[0]), (0, 0), (0, 0)), constant_values=1), np.ones((h, 10, 3))]
    pio.save(out, np.concatenate(seq[:-1], 1))
else:
    w = max(t.shape[1] for t in tiles); seq = []
    for t in tiles: seq += [np.pad(t, ((0, 0), (0, w - t.shape[1]), (0, 0)), constant_values=1), np.ones((10, w, 3))]
    pio.save(out, np.concatenate(seq[:-1], 0))
