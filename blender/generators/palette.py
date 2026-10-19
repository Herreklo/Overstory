"""The shared palette: one small texture, every kit piece UV-mapped onto its swatches.

Each face's UVs sit on the centre of one swatch, so thousands of buildings share one
material. Swatches are named; generators ask for colours by name, never by value.
The colours are provisional until the art bible fixes them.
"""

import os

GRID = 8  # swatches per row and column
CELL = 16  # pixels per swatch

# name: (r, g, b) in sRGB 0-255. Order fixes each swatch's place in the texture.
SWATCHES = {
    # walls: painted timber
    "wall_white": (236, 232, 222),
    "wall_cream": (232, 220, 188),
    "wall_yellow": (226, 196, 120),
    "wall_ochre": (196, 150, 82),
    "wall_grey": (176, 178, 172),
    "wall_green": (168, 184, 160),
    "wall_oxred": (140, 62, 48),
    "wall_blue": (150, 170, 182),
    # trims, doors
    "trim_white": (244, 242, 236),
    "trim_cream": (226, 216, 190),
    "trim_dark": (62, 60, 56),
    "door_green": (52, 84, 66),
    "door_blue": (52, 72, 98),
    "door_brown": (96, 64, 44),
    "door_red": (128, 48, 40),
    "door_grey": (110, 112, 108),
    # roofs
    "roof_red": (164, 74, 52),
    "roof_red_dark": (128, 56, 42),
    "roof_black": (46, 46, 50),
    "roof_slate": (88, 92, 98),
    "roof_ridge": (70, 66, 64),
    # stone, brick, glass, metal
    "stone": (138, 136, 130),
    "stone_dark": (98, 96, 92),
    "brick": (146, 72, 56),
    "render_white": (222, 220, 214),
    "glass": (38, 48, 58),
    "glass_shop": (52, 64, 74),
    "metal_dark": (54, 56, 58),
    "sign": (226, 222, 210),
    "wood": (120, 92, 66),
    "ground": (120, 122, 118),
    "shadow": (20, 20, 22),
}

NAMES = list(SWATCHES)
assert len(NAMES) <= GRID * GRID


def uv(name):
    """UV coordinate at the centre of a swatch."""
    i = NAMES.index(name)
    col, row = i % GRID, i // GRID
    return ((col + 0.5) / GRID, 1.0 - (row + 0.5) / GRID)


def pixels():
    """Flat RGBA float list (bottom row first, as Blender stores images), sRGB 0-1."""
    size = GRID * CELL
    out = [0.0] * (size * size * 4)
    for i, name in enumerate(NAMES):
        r, g, b = (c / 255.0 for c in SWATCHES[name])
        col, row = i % GRID, i // GRID
        for py in range(CELL):
            y = size - 1 - (row * CELL + py)
            for px in range(CELL):
                x = col * CELL + px
                k = (y * size + x) * 4
                out[k : k + 4] = (r, g, b, 1.0)
    return out


def material(save_dir=None):
    """The one palette material (image texture, closest sampling). Saves palette.png if save_dir is given."""
    import bpy

    mat = bpy.data.materials.get("palette")
    if mat:
        return mat
    size = GRID * CELL
    img = bpy.data.images.get("palette.png") or bpy.data.images.new("palette.png", size, size, alpha=False)
    img.pixels[:] = pixels()
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        img.filepath_raw = os.path.join(save_dir, "palette.png")
        img.file_format = "PNG"
        img.save()
    mat = bpy.data.materials.new("palette")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.8
    return mat
