"""The shared palette: one small texture, every kit piece UV-mapped onto its swatches.

Each face's UVs sit on the centre of one swatch, so thousands of buildings share one
material. Swatches are named; generators ask for colours by name, never by value.
The colours are provisional until the art bible fixes them.
"""

import os

GRID = 16  # swatches per row and column
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
    # added for life and the later eras
    "wall_brown": (92, 64, 46),
    "glass_lit": (236, 186, 108),
    "curtain": (206, 200, 186),
    "curtain_warm": (184, 150, 108),
    "flowers_red": (196, 58, 52),
    "flowers_yellow": (230, 190, 70),
    "leaf": (78, 110, 62),
    "metal_gutter": (92, 96, 98),
    # street lamps: posts and their light, by the era they were put up
    "metal_post": (44, 56, 50),
    "metal_galv": (146, 150, 148),
    "lamp_off": (198, 200, 194),
    "lamp_warm": (255, 206, 138),
    "lamp_mercury": (214, 236, 232),
    "lamp_sodium": (255, 164, 72),
    "glass_shop_lit": (240, 196, 124),
    "sign_lit": (250, 236, 206),
    # the street: granite setts in three tones, concrete flags, kerb, quay wall, grass
    "setts_light": (118, 116, 112),
    "setts_mid": (106, 104, 100),
    "setts_dark": (95, 94, 91),
    "joint": (84, 83, 80),
    "flags": (152, 151, 145),
    "kerb": (126, 126, 122),
    "quay_wall": (102, 98, 92),
    "setts_mean": (103, 101, 97),
    "asphalt": (74, 75, 77),
    "gravel": (128, 124, 116),
    "drystone": (116, 112, 104),
    "rock": (88, 88, 84),
    "heath": (68, 74, 56),
    "bark": (74, 66, 58),
    "leaf_birch": (200, 172, 72),
    "leaf_rowan": (172, 70, 42),
    "leaf_sycamore": (196, 128, 54),
    "leaf_spruce": (46, 64, 50),
    "grass": (62, 74, 50),
}

NAMES = list(SWATCHES)
assert len(NAMES) <= GRID * GRID

# Swatches that can glow: (the swatch it looks like unlit, its group). Unity shows each one in
# its unlit colour and adds its own colour as light where the scene's light turns its group on:
# windows (lit rooms, an open shop, a light-box sign) or lamps. The geometry is the same in
# every light.
EMISSIVE = {
    "glass_lit": ("glass", "window"),
    "glass_shop_lit": ("glass_shop", "window"),
    "sign_lit": ("sign", "window"),
    "lamp_warm": ("lamp_off", "lamp"),
    "lamp_mercury": ("lamp_off", "lamp"),
    "lamp_sodium": ("lamp_off", "lamp"),
}
GROUPS = ("window", "lamp")

# Paving: where puddles lie (0.5), and sett paving whose stones and joints a distant camera sees
# as one tone, setts_mean (1.0). Written to palette_glow.png's blue channel.
PAVING = {"flags": 0.5, "asphalt": 0.5, "gravel": 0.5, "setts_light": 1.0, "setts_mid": 1.0, "setts_dark": 1.0, "joint": 1.0, "setts_mean": 1.0}

# How each swatch's surface behaves: (smoothness, metallic, porosity), 0-1. Porosity is how
# much rain darkens it and how little it shines when wet: stone and flags soak, glazed tiles
# and glass shed it. Swatches not named here are painted timber.
PAINTED = (0.22, 0.0, 0.35)
SURFACE = {
    "glass": (0.92, 0.0, 0.0), "glass_shop": (0.92, 0.0, 0.0), "glass_lit": (0.92, 0.0, 0.0),
    "glass_shop_lit": (0.92, 0.0, 0.0),
    "sign": (0.45, 0.0, 0.05), "sign_lit": (0.45, 0.0, 0.05), "lamp_off": (0.55, 0.0, 0.0),
    "lamp_warm": (0.55, 0.0, 0.0), "lamp_mercury": (0.55, 0.0, 0.0), "lamp_sodium": (0.55, 0.0, 0.0),
    "metal_galv": (0.45, 0.85, 0.0), "metal_dark": (0.38, 0.0, 0.05), "metal_post": (0.38, 0.0, 0.05),
    "metal_gutter": (0.40, 0.0, 0.05),
    "roof_black": (0.55, 0.0, 0.05), "roof_red": (0.16, 0.0, 0.7), "roof_red_dark": (0.18, 0.0, 0.65),
    "roof_slate": (0.35, 0.0, 0.1), "roof_ridge": (0.3, 0.0, 0.3),
    "stone": (0.18, 0.0, 0.45), "stone_dark": (0.18, 0.0, 0.45), "kerb": (0.2, 0.0, 0.45),
    "setts_light": (0.2, 0.0, 0.65), "setts_mid": (0.2, 0.0, 0.65), "setts_dark": (0.2, 0.0, 0.65),
    "joint": (0.1, 0.0, 0.6), "setts_mean": (0.2, 0.0, 0.65), "asphalt": (0.3, 0.0, 0.3),
    "gravel": (0.08, 0.0, 0.7), "drystone": (0.15, 0.0, 0.55), "rock": (0.15, 0.0, 0.85), "heath": (0.06, 0.0, 1.0), "bark": (0.12, 0.0, 0.6),
    "leaf_birch": (0.15, 0.0, 0.9), "leaf_rowan": (0.15, 0.0, 0.9), "leaf_sycamore": (0.15, 0.0, 0.9), "leaf_spruce": (0.12, 0.0, 0.9), "flags": (0.12, 0.0, 0.65), "quay_wall": (0.15, 0.0, 0.55),
    "brick": (0.12, 0.0, 0.6), "render_white": (0.1, 0.0, 0.55), "ground": (0.08, 0.0, 0.7),
    "grass": (0.05, 0.0, 1.0), "wood": (0.15, 0.0, 0.6), "shadow": (0.05, 0.0, 0.5),
    "curtain": (0.1, 0.0, 0.0), "curtain_warm": (0.1, 0.0, 0.0),
    "flowers_red": (0.15, 0.0, 0.2), "flowers_yellow": (0.15, 0.0, 0.2), "leaf": (0.15, 0.0, 0.2),
}


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


def save_maps(out_dir):
    """Write the palette for Unity: palette_albedo.png (every swatch as it looks unlit),
    palette_emit.png (the light of the swatches that can glow, black elsewhere) and
    palette_glow.png (which group each glowing swatch belongs to: red windows, green lamps; blue is
    paving, see PAVING) and
    palette_surface.png (smoothness, metallic and porosity in red, green and blue).
    Plain PNGs, no dependencies, so Blender's Python can write them."""
    import struct
    import zlib

    size = GRID * CELL

    def colour(name, kind):
        if kind == "emit":
            return SWATCHES[name] if name in EMISSIVE else (0, 0, 0)
        if kind == "glow":
            group = EMISSIVE[name][1] if name in EMISSIVE else None
            return tuple(255 if g == group else 0 for g in GROUPS) + (int(round(PAVING.get(name, 0.0) * 255)),)
        if kind == "surface":
            return tuple(int(round(v * 255)) for v in SURFACE.get(name, PAINTED))
        return SWATCHES[EMISSIVE[name][0]] if name in EMISSIVE else SWATCHES[name]

    def write(path, kind):
        rows = []
        for y in range(size):  # PNG rows go top first; swatch row 0 is the top
            row = bytearray([0])
            for x in range(size):
                i = (y // CELL) * GRID + x // CELL
                row += bytes(colour(NAMES[i], kind) if i < len(NAMES) else (0, 0, 0))
            rows.append(bytes(row))

        def chunk(tag, data):
            return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

        with open(path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n")
            f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)))
            f.write(chunk(b"IDAT", zlib.compress(b"".join(rows), 9)))
            f.write(chunk(b"IEND", b""))

    os.makedirs(out_dir, exist_ok=True)
    write(os.path.join(out_dir, "palette_albedo.png"), "albedo")
    write(os.path.join(out_dir, "palette_emit.png"), "emit")
    write(os.path.join(out_dir, "palette_glow.png"), "glow")
    write(os.path.join(out_dir, "palette_surface.png"), "surface")


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
