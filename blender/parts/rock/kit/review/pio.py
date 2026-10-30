# image in and out through Blender (its Python has numpy); arrays are top-down [H, W, C] floats
import bpy, numpy as np
def load(path, linear=False):
    im = bpy.data.images.load(path, check_existing=False)
    if linear or path.endswith(".exr"): im.colorspace_settings.name = "Non-Color"
    a = np.empty(im.size[0] * im.size[1] * 4, np.float32); im.pixels.foreach_get(a)
    a = a.reshape(im.size[1], im.size[0], 4)[::-1].copy(); bpy.data.images.remove(im); return a
def save(path, a):
    a = np.asarray(a, np.float32)
    if a.ndim == 2: a = np.repeat(a[..., None], 3, -1)
    if a.shape[2] == 3: a = np.concatenate([a, np.ones(a.shape[:2] + (1,), np.float32)], -1)
    H, W = a.shape[:2]; im = bpy.data.images.new("o", W, H, alpha=True)
    im.colorspace_settings.name = "Non-Color"
    im.pixels.foreach_set(np.clip(a[::-1], 0, 1).ravel()); im.filepath_raw = path; im.file_format = "PNG"; im.save(); bpy.data.images.remove(im)
