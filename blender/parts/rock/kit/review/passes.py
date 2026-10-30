# passes.py -- --out DIR [--views eye,street]: the boulder's normal and position passes from each beside view, as the Unity
# stills see it (kit.json beside; the street stop as faces.py), so a paintover places its strokes on the real planes.
# Writes DIR/<view>-<mesh>-N.exr (world normal *0.5+0.5), -P.exr (house-frame position +50), alpha = coverage.
import bpy, json, sys, math, os
from mathutils import Vector
ROOT = "/Users/oystein/code/Overstory"
a = sys.argv[sys.argv.index("--") + 1:]; arg = dict(zip(a[::2], a[1::2]))
OUT = arg["--out"]; os.makedirs(OUT, exist_ok=True)
K = json.load(open(f"{ROOT}/blender/parts/rock/kit/kit.json")); B = K["beside"]
at = Vector(B["parts"][0]["at"]); w = 7.0
V = {"eye": (at + Vector(B["eye"]["from"]), Vector(B["eye"]["look"]), B["eye"]["fov"]),
     "back": (at + Vector(B["back"]["from"]), Vector(B["back"]["look"]), B["back"]["fov"]),
     "street": (Vector((w/2-9, -19, 1.6)), Vector((w/2, 1, 3)) - Vector((w/2-9, -19, 1.6)), 38),
     "high": (at + Vector(B["high"]["from"]), Vector(B["high"]["look"]), B["high"]["fov"]),
     "iso": (at + Vector(B["iso"]["from"]), Vector(B["iso"]["look"]), B["iso"]["fov"])}
views = arg.get("--views", "eye,street").split(",")
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(f"{ROOT}/cache/rock/kit/gen/boulder/house.blend") as (src, dst):
    dst.objects = [n for n in src.objects if n in ("near_gneiss", "high_gneiss")]
sc = bpy.context.scene
for o in dst.objects:
    sc.collection.objects.link(o); o.location = at
# the turf at z 0 hides what is sunk
bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0)); ground = bpy.context.object
def mat(name, which):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial"); e = nt.nodes.new("ShaderNodeEmission"); g = nt.nodes.new("ShaderNodeNewGeometry")
    mth = nt.nodes.new("ShaderNodeVectorMath")
    if which == "N": mth.operation = "MULTIPLY_ADD"; mth.inputs[1].default_value = (0.5,)*3; mth.inputs[2].default_value = (0.5,)*3; nt.links.new(g.outputs["Normal"], mth.inputs[0])
    else: mth.operation = "ADD"; mth.inputs[1].default_value = (50,)*3; nt.links.new(g.outputs["Position"], mth.inputs[0])
    nt.links.new(mth.outputs[0], e.inputs["Color"]); nt.links.new(e.outputs[0], o.inputs["Surface"]); return m
holdout = bpy.data.materials.new("hold"); holdout.use_nodes = True; nt = holdout.node_tree; nt.nodes.clear()
ho = nt.nodes.new("ShaderNodeHoldout"); oo = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(ho.outputs[0], oo.inputs["Surface"])
ground.data.materials.append(holdout)
sc.render.engine = "CYCLES"; sc.cycles.samples = 1; sc.cycles.use_denoising = False; sc.cycles.pixel_filter_type = "BOX"; sc.cycles.filter_width = 0.01
sc.cycles.max_bounces = 0; sc.render.film_transparent = True; SSP = int(arg.get('--ss', 1)); sc.render.resolution_x, sc.render.resolution_y = 2560 * SSP, 1440 * SSP; sc.render.resolution_percentage = 100
if '--box' in arg:   # x0,y0,x1,y1 in the 2560x1440 frame, top-down: render only that window
    bx = [int(v) for v in arg['--box'].split(',')]; sc.render.use_border = True; sc.render.use_crop_to_border = True
    sc.render.border_min_x, sc.render.border_max_x = bx[0] / 2560, bx[2] / 2560; sc.render.border_min_y, sc.render.border_max_y = 1 - bx[3] / 1440, 1 - bx[1] / 1440
sc.view_settings.view_transform = "Raw"; sc.render.image_settings.file_format = "OPEN_EXR"; sc.render.image_settings.color_depth = "32"
sc.render.image_settings.color_mode = "RGBA"
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.sensor_fit = "VERTICAL"; cam.data.clip_start = 0.05; cam.data.clip_end = 500
for v in views:
    pos, look, fov = V[v]
    cam.location = pos; cam.rotation_euler = look.to_track_quat("-Z", "Y").to_euler(); cam.data.angle_y = math.radians(fov)
    for mesh in ("near_gneiss", "high_gneiss"):
        for o in dst.objects: o.hide_render = o.name != mesh
        for which in ("N", "P"):
            m = mat(mesh + which, which); ob = bpy.data.objects[mesh]; ob.data.materials.clear(); ob.data.materials.append(m)
            sc.render.filepath = f"{OUT}/{v}-{mesh.split('_')[0]}-{which}.exr"; bpy.ops.render.render(write_still=True)
            print("WROTE", sc.render.filepath)
