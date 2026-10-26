"""R2b's contact sheet: a set of LT1R2b.Still's frames (OUT-moment-cam-look.png) in a grid, a row per moment and a
column per eye, each frame box-filtered down to a quarter.

    python3 tools/r2b_sheet.py OUT LOOK moment,moment,... cam,cam,...   (writes OUT-LOOK-sheet.png)
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r0b_count import read_png, write_png  # noqa: E402


def main():
    out, look, moments, cams = sys.argv[1], sys.argv[2], sys.argv[3].split(","), sys.argv[4].split(",")
    rows = []
    for m in moments:
        row = []
        for c in cams:
            a = read_png(f"{out}-{m}-{c}-{look}.png").astype(np.float32)
            h, w = a.shape[0] // 4 * 4, a.shape[1] // 4 * 4
            row.append(a[:h, :w].reshape(h // 4, 4, w // 4, 4, 3).mean(axis=(1, 3)))
            row.append(np.full((h // 4, 4, 3), 255.0))
        rows.append(np.concatenate(row[:-1], 1))
        rows.append(np.full((4, rows[-1].shape[1], 3), 255.0))
    write_png(f"{out}-{look}-sheet.png", np.concatenate(rows[:-1], 0))


if __name__ == "__main__":
    main()
