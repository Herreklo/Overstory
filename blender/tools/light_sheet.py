"""Sheets for judging the light on the heart: each camera across the hours, and the value check for all of them.

    python blender/tools/light_sheet.py   (needs numpy and Pillow)

Reads the Unity stills (LT1Heart.Frames for the flat clay, LT1Heart.LightFrames for the hours) and writes:
- reviews/lt1/heart/light/sheet-<camera>.png: the flat clay, then each hour; colour above, greyscale below;
- reviews/lt1/heart/light/sheet-values.png: every camera at every hour in greyscale at one-eighth size, the size at
  which near, middle and far must still separate;
- reviews/lt1/heart/night/sheet-<camera>.png: blue hour in sea fog, neutral and in each mood (LT1Heart.NightFrames),
  colour above, greyscale below, for the cameras the moods are rendered from;
- reviews/lt1/heart/night/sheet-neutral.png: every camera at blue hour in sea fog, neutral.
Nothing is changed in the frames; the sheets only lay them side by side.
"""

import os

from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HEART = os.path.join(ROOT, "reviews", "lt1", "heart")
CAMERAS = ["1-over-the-roofs", "2-along-high-terrace", "3-street-gully-steps", "4-middle", "5-far",
           "6-from-the-roads", "7-from-lookout-park", "8-watch-knoll", "9-harbour-row-quay"]
MOODS = ["neutral", "hopeless", "sad", "gritty", "hopeful", "grand", "success"]
NIGHT = os.path.join(HEART, "night")
HOURS = [("0930-morning", "09:30 morning"), ("1300-drizzle", "13:00 drizzle"), ("1600-low-sun", "16:00 low sun"),
         ("1750-blue-hour", "17:50 blue hour")]
CELL = (480, 270)
LABEL = 22


def grey(im):
    return im.convert("L").convert("RGB")


def frame(hour, camera, kind=""):
    if hour is None:
        path = os.path.join(HEART, "clay", f"heart-clay-{camera}{kind}.png")
    else:
        path = os.path.join(HEART, "light", hour, f"heart-{hour}-{camera}{kind}.png")
    return Image.open(path).convert("RGB") if os.path.exists(path) else None


def camera_sheet(camera):
    cols = [(None, "flat clay (before)")] + HOURS
    sheet = Image.new("RGB", (CELL[0] * len(cols), (CELL[1] + LABEL) * 2), (24, 24, 26))
    draw = ImageDraw.Draw(sheet)
    for i, (hour, label) in enumerate(cols):
        im = frame(hour, camera)
        if im is None:
            continue
        g = frame(hour, camera, "-grey") if hour else grey(im)
        x = i * CELL[0]
        draw.text((x + 8, 4), label, fill=(230, 230, 230))
        sheet.paste(im.resize(CELL, Image.LANCZOS), (x, LABEL))
        sheet.paste((g or grey(im)).resize(CELL, Image.LANCZOS), (x, LABEL * 2 + CELL[1]))
    out = os.path.join(HEART, "light", f"sheet-{camera}.png")
    sheet.save(out)
    return out


def values_sheet():
    w, h = 240, 135
    cols = [(None, "flat clay")] + HOURS
    sheet = Image.new("RGB", (w * len(cols), (h + 16) * len(CAMERAS) + 16), (24, 24, 26))
    draw = ImageDraw.Draw(sheet)
    for i, (hour, label) in enumerate(cols):
        draw.text((i * w + 6, 2), label, fill=(230, 230, 230))
        for j, camera in enumerate(CAMERAS):
            im = frame(hour, camera, "-eighth")
            if im is None:
                continue
            sheet.paste(grey(im).resize((w, h), Image.NEAREST), (i * w, 16 + j * (h + 16)))
            if i == 0:
                draw.text((6, 16 + j * (h + 16) + h + 1), camera, fill=(180, 180, 180))
    out = os.path.join(HEART, "light", "sheet-values.png")
    sheet.save(out)
    return out


def night(mood, camera, kind=""):
    path = os.path.join(NIGHT, mood, f"heart-night-{mood}-{camera}{kind}.png")
    return Image.open(path).convert("RGB") if os.path.exists(path) else None


def night_sheet(camera):
    cols = [m for m in MOODS if night(m, camera) is not None]
    if len(cols) < 2:
        return None
    sheet = Image.new("RGB", (CELL[0] * len(cols), (CELL[1] + LABEL) * 2), (24, 24, 26))
    draw = ImageDraw.Draw(sheet)
    for i, mood in enumerate(cols):
        im = night(mood, camera)
        g = night(mood, camera, "-grey") or grey(im)
        x = i * CELL[0]
        draw.text((x + 8, 4), mood, fill=(230, 230, 230))
        sheet.paste(im.resize(CELL, Image.LANCZOS), (x, LABEL))
        sheet.paste(g.resize(CELL, Image.LANCZOS), (x, LABEL * 2 + CELL[1]))
    out = os.path.join(NIGHT, f"sheet-{camera}.png")
    sheet.save(out)
    return out


def night_overview():
    shots = [c for c in CAMERAS if night("neutral", c) is not None]
    if not shots:
        return None
    cols = 3
    rows = (len(shots) + cols - 1) // cols
    w, h = 640, 360
    sheet = Image.new("RGB", (w * cols, (h + LABEL) * rows), (24, 24, 26))
    draw = ImageDraw.Draw(sheet)
    for k, camera in enumerate(shots):
        x, y = (k % cols) * w, (k // cols) * (h + LABEL)
        draw.text((x + 8, y + 4), camera, fill=(230, 230, 230))
        sheet.paste(night("neutral", camera).resize((w, h), Image.LANCZOS), (x, y + LABEL))
    out = os.path.join(NIGHT, "sheet-neutral.png")
    sheet.save(out)
    return out


if __name__ == "__main__":
    import sys
    if "night" in sys.argv[1:]:
        for c in CAMERAS:
            out = night_sheet(c)
            if out:
                print(out)
        print(night_overview())
    else:
        for c in CAMERAS:
            print(camera_sheet(c))
        print(values_sheet())
