"""A quick look at an assembled tree in Blender (a check that the assembler works, not a judgement: trees are judged in
Unity, in our light).

    blender -b --factory-startup --python blender/tools/tree_preview.py -- <species> <seed> <age> <out.png> [quality]

Builds the tree (blender/generators/tree.py), gives it plain materials (the bark's lightness, the leaf atlas cut by
its coverage, leaves tinted by their rank from green to autumn yellow), and renders it side-on in EEVEE against a grey
sky, with a two-metre figure for scale.
"""

import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "generators"))
import tree  # noqa: E402

UNITY = os.path.join(HERE, "..", "..", "unity")


def material_leaves(species):
    m = bpy.data.materials.new("leaves")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(os.path.join(UNITY, "Assets", "Art", "Trees", species, f"{species}_leaves.png"))
    tex.image.colorspace_settings.name = "Non-Color"
    tex.interpolation = "Closest"
    uv = nt.nodes.new("ShaderNodeUVMap")
    uv.uv_map = "uv0"
    rank = nt.nodes.new("ShaderNodeUVMap")
    rank.uv_map = "uv1"
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    sepc = nt.nodes.new("ShaderNodeSeparateColor")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.72, 0.55, 0.10, 1)
    ramp.color_ramp.elements[1].color = (0.25, 0.36, 0.10, 1)
    mul = nt.nodes.new("ShaderNodeMixRGB")
    mul.blend_type = "MULTIPLY"
    mul.inputs[0].default_value = 1.0
    nt.links.new(uv.outputs[0], tex.inputs[0])
    nt.links.new(rank.outputs[0], sep.inputs[0])
    nt.links.new(sep.outputs[0], ramp.inputs[0])
    nt.links.new(tex.outputs[0], sepc.inputs[0])
    nt.links.new(ramp.outputs[0], mul.inputs[1])
    nt.links.new(sepc.outputs[1], mul.inputs[2])
    nt.links.new(mul.outputs[0], bsdf.inputs["Base Color"])
    nt.links.new(tex.outputs[1], bsdf.inputs["Alpha"])
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    m.blend_method = "CLIP" if hasattr(m, "blend_method") else m.blend_method
    if hasattr(m, "surface_render_method"):
        m.surface_render_method = "DITHERED"
    m.use_backface_culling = False
    return m


def material_bark():
    m = bpy.data.materials.new("bark")
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.78, 0.76, 0.72, 1)
    bsdf.inputs["Roughness"].default_value = 0.9
    return m


def preview(species, seed, age, out, quality=1.0):
    info = tree.build(species, seed, age, quality, unity=None)
    scene = bpy.context.scene
    obs = [o for o in scene.objects if o.type == "MESH"]
    for o in obs:
        o.data.materials.append(material_leaves(species) if o.name.endswith("_leaves") else material_bark())
    H = info["height"]
    # a figure for scale, two metres off the trunk
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=1.8, location=(2.2, 0, 0.9))
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    scene.collection.objects.link(cam)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = H * 1.25
    cam.location = (0, -60, H * 0.5)
    cam.rotation_euler = (math.radians(90), 0, 0)
    scene.camera = cam
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    scene.collection.objects.link(sun)
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(55), 0, math.radians(30))
    world = bpy.data.worlds.new("w")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.58, 0.62, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    scene.world = world
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = 900, 1100
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print("PREVIEW", out, info)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:]
    preview(argv[0], int(argv[1]), int(argv[2]), argv[3], float(argv[4]) if len(argv) > 4 else 1.0)
