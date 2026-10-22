"""The plan's face-class function (docs/building-blocks.md, What a part carries; decisions §15, S3).

A surface region's face class sets the texel of its pages: street faces take their material's texel on every floor,
yard faces take it to 2 m above the ground they meet and 8 cm above, roofs and the ground 8 cm. The class comes from
what the face is and what it looks onto, by the table in schemas/maps.json and nothing else, so the plan stage and
tools/validate_record.py read one rule. Pure integers and words; runs in Blender's Python and in the venv.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAPS = os.path.join(ROOT, "schemas", "maps.json")

_tables = {}


def _registry(path=MAPS):
    if path not in _tables:
        with open(path, encoding="utf-8") as f:
            _tables[path] = json.load(f)
    return _tables[path]


def face_class(facing, looks_onto, path=MAPS):
    """The face class of a region facing `facing` (wall, roof, walked, ground) that looks onto `looks_onto`.
    Raises ValueError for a combination the table does not hold."""
    for row in _registry(path)["faceClasses"]["table"]:
        if row["facing"] == facing and looks_onto in row["looksOnto"]:
            return row["faceClass"]
    raise ValueError("no face class for a %s facing onto %s (schemas/maps.json, faceClasses)" % (facing, looks_onto))


def texel_mm(face_class_name, facing, finest_mark_mm=None, path=MAPS):
    """The region's texel: (mm, below_mm, above_texel_mm). The last two are None except for a yard face, which takes
    mm up to below_mm above the ground it meets and above_texel_mm over it. finest_mark_mm is the smallest feature among its
    parts' marks; a mark's texel is half of it, and the coarser (larger) texel wins."""
    texel = _registry(path)["texel"]
    rule = texel["byFaceClass"][face_class_name]
    mm = texel["materialMm"][facing] if rule["mm"] == "material" else rule["mm"]
    if finest_mark_mm is not None:
        mm = max(mm, finest_mark_mm // 2)
    if "belowMm" in rule:
        return mm, rule["belowMm"], max(rule["aboveTexelMm"], mm)
    return mm, None, None
