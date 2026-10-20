"""The bare tree as the assembler reads it (timeline plus sag) and as Unity draws it in January, side-on at the street
stop's scale, beside the Oslo birch and Dahl: a fast way to judge a habit change before building and rendering it.

    python blender/tools/tree_sketch.py <out.png> <seed> <exposure> <planted|self-seeded> "<variant>" ["<variant>" ...]
    (needs numpy and Pillow)

Each variant is a row: a dict of overrides to the birch's habit (tree_growth.SPECIES), with an optional 'sag' for the
assembler (tree.PARTS), e.g. "{}" for the current habit, "{'setpoint': ((90, 90), (66, 38), (30, 0), (0, -20),
(-15, -30), (-20, -35)), 'sag': 0.12}". Each row shows the tree at 30 and 60 years. Branches thinner than a pixel are
drawn a pixel wide in a share of their ink, as the tree shader draws them. A habit change rewrites the timeline cache.
"""

import ast
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "blender", "generators"))
import tree as T  # noqa: E402
import tree_growth as G  # noqa: E402

REFS = ("03-downy-and-silver-birch-oslo-19-sep.jpg", "14-dahl-birch-in-a-storm-1849.jpg")
PAPER, INK = (226, 224, 220), (58, 46, 44)


def main():
    out, seed, exposure, origin = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
    variants = [ast.literal_eval(v) for v in sys.argv[5:]] or [{}]
    W, H = 760, 1100
    refs = [Image.open(os.path.join(ROOT, "docs", "references", "trees", f)).convert("RGB") for f in REFS]
    for r in refs:
        r.thumbnail((360, H // 2))
    img = Image.new("RGB", (W * 2 + 380, H * len(variants)), PAPER)
    d = ImageDraw.Draw(img)
    habit, parts = dict(G.SPECIES["birch"]), dict(T.PARTS["birch"])
    for row, over in enumerate(variants):
        over = dict(over)
        sag = over.pop("sag", None)
        G.SPECIES["birch"] = dict(habit, **over)
        T.PARTS["birch"] = dict(parts) if sag is None else dict(parts, sag=sag)
        for col, age in enumerate((30, 60)):
            tl = T.read("birch", seed, age, 1.0, (), exposure, origin)
            height = float(tl["end"][tl["alive"]][:, 2].max())
            px = 1080 / (2 * 1.55 * height * 0.424)  # the street stop's frame height for a tree of this height
            winter = min(T.PARTS["birch"]["winter_tips"], T.drawn_tips(T.PARTS["birch"], height))
            for i in np.argsort(tl["r"]):
                if not tl["alive"][i] or tl["tips"][i] < winter:
                    continue
                w = 2 * tl["r"][i] * px
                cov = min(w, 1.0)
                ink = tuple(int(p + (k - p) * cov) for k, p in zip(INK, PAPER))
                a, b = tl["start"][i], tl["end"][i]
                x0, y0 = col * W + W / 2, (row + 1) * H - 10
                d.line([(x0 + a[0] * px, y0 - a[2] * px), (x0 + b[0] * px, y0 - b[2] * px)], fill=ink, width=max(1, int(round(w))))
            d.text((col * W + 6, row * H + 4), f"{age} y {height:.1f} m  sag {T.PARTS['birch']['sag']} {str(over)[:70]}", fill=(30, 30, 30))
        img.paste(refs[0], (W * 2, row * H))
        img.paste(refs[1], (W * 2, row * H + H // 2))
    img.save(out)
    img.resize((img.width * 2 // 5, img.height * 2 // 5)).save(out.replace(".png", "-s.png"))
    print(out)


if __name__ == "__main__":
    main()
