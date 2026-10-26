"""R2b's switch check: where L1 may stand in for L0 unseen. LT1R2b.Still renders both levels from the same eyes
(-mesh l0=...,l1=... -cams ...); per eye this compares them where the wall is drawn (the pixels its grey and material
looks differ on), as L* box-filtered 3 x 3, and prints the share of those pixels that change by more than 3 L* (seen
side by side) and the 99th percentile. The switch is the nearest eye from which the share stays under 1%.

    python3 tools/r2b_switch.py OUT     (with numpy: Blender's Python)
"""

import glob
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r0b_count import lstar, read_png  # noqa: E402


def box3(a):
    p = np.pad(a, 1, mode="edge")
    return sum(p[1 + dy:p.shape[0] - 1 + dy, 1 + dx:p.shape[1] - 1 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)) / 9.0


def main():
    base = sys.argv[1]
    eyes = sorted({re.match(r".*-l0-(.+)-material\.png$", f).group(1)
                   for f in glob.glob(base + "-l0-*-material.png")}, key=lambda e: float(re.sub(r"[^0-9.]", "", e) or 0))
    print(f"{'eye':>6} {'look':>9} {'wall px':>8} {'>3 L*':>7} {'p99':>6}")
    for eye in eyes:
        wall = np.abs(lstar(read_png(f"{base}-l0-{eye}-grey.png")) - lstar(read_png(f"{base}-l0-{eye}-material.png"))) > 0.5
        for look in ("grey", "material"):
            d = np.abs(box3(lstar(read_png(f"{base}-l0-{eye}-{look}.png"))) - box3(lstar(read_png(f"{base}-l1-{eye}-{look}.png"))))
            w = d[wall]
            print(f"{eye:>6} {look:>9} {w.size:>8} {100 * np.mean(w > 3):>6.2f}% {np.percentile(w, 99):>6.2f}")


if __name__ == "__main__":
    main()
