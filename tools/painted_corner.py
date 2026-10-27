#!/usr/bin/env python3
"""The painted corner rebuilt: the scene Øystein opens and the small Mac app (Code/Editor/Corner/LT1PaintedCorner.cs),
or the frame's still. Any element session runs it after its element lands.

    tools/painted_corner.py                  the scene (saved, checked, its still), then the app
    tools/painted_corner.py --scene          the scene only (saved, checked, its still)
    tools/painted_corner.py --paint          the frame's still only (LT1ArtPasses.Paint, supersampled), to
                                             unity/Builds/PaintedCorner/stills/{view}-{moment} unless -out says where
    tools/painted_corner.py ... -- -elements trees,growth     arguments after -- go to Unity (-elements none: no elements;
                                             -view eye-foot, -moment 1300-drizzle, -out reviews/lt1/<element>/...;
                                             -still <path> for the scene's still)

The scene is unity/Assets/Experiments/LT1/Corner/LT1_PaintedCorner.unity (its meshes and materials in Corner/Generated/,
with greybox.txt), the app unity/Builds/PaintedCorner/PaintedCorner.app, the scene's still
unity/Builds/PaintedCorner/corner-scene.png; none of them is tracked. The page's own frame
(reviews/lt1/art-direction/engine/street-1750-sea-fog) is written only when -out names it. Unity runs in batch mode under
the Unity lock (tools/unity_lock.py), and waits while another job or the editor has unity/ open. The stage writes the
sky's material and a build rewrites some settings as housekeeping: every one of those files is copied before Unity runs
and put back as it was after, if it changed, so other sessions' edits in them stay. The log is
unity/Builds/PaintedCorner/build.log.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import unity_lock  # noqa: E402

UNITY = "/Applications/Unity/Hub/Editor/6000.6.6f1/Unity.app/Contents/MacOS/Unity"
GUARDED = [
    "unity/Assets/Art/Materials/M_Sky.mat",
    "unity/Assets/Experiments/LT1/Heart/LT1_Heart.unity",
    "unity/Assets/Settings/DefaultVolumeProfile.asset",
    "unity/Assets/Settings/PC_RPAsset.asset",
    "unity/Assets/Settings/PC_Renderer.asset",
    "unity/Assets/Settings/UniversalRenderPipelineGlobalSettings.asset",
    "unity/ProjectSettings/GraphicsSettings.asset",
    "unity/ProjectSettings/ProjectSettings.asset",
    "unity/ProjectSettings/EditorBuildSettings.asset",
]
METHODS = {
    "build": "Overstory.EditorTools.Corner.LT1PaintedCorner.Build",
    "scene": "Overstory.EditorTools.Corner.LT1PaintedCorner.Scene",
    "paint": "Overstory.EditorTools.LT1ArtPasses.Paint",
}
OURS = re.compile(r"^\[(LT1PaintedCorner|Corner|LT1ArtPasses|LT1Perf)\]")
TROUBLE = re.compile(r"error CS\d+|Exception: |\[Corner\] element .* (failed|must be)")


def read(path):
    with open(path, "rb") as f:
        return f.read()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    which = ap.add_mutually_exclusive_group()
    which.add_argument("--scene", action="store_true", help="the scene only (saved, checked, its still)")
    which.add_argument("--paint", action="store_true", help="the frame's still only (LT1ArtPasses.Paint)")
    ap.add_argument("unity_args", nargs="*", help="after --: arguments for Unity (e.g. -elements none)")
    a = ap.parse_args()
    method = METHODS["scene" if a.scene else "paint" if a.paint else "build"]
    unity_args = list(a.unity_args)
    if a.paint and "-out" not in unity_args:
        def arg(name, default):
            return unity_args[unity_args.index(name) + 1] if name in unity_args[:-1] else default
        unity_args += ["-out", f"unity/Builds/PaintedCorner/stills/{arg('-view', 'street')}-{arg('-moment', '1750-sea-fog')}"]
    log_dir = os.path.join(REPO, "unity/Builds/PaintedCorner")
    os.makedirs(log_dir, exist_ok=True)
    log = os.path.join(log_dir, "build.log")
    cmd = [UNITY, "-batchmode", "-quit", "-projectPath", os.path.join(REPO, "unity"), "-executeMethod", method,
           *unity_args, "-logFile", log]

    start = time.time()
    with unity_lock.held(purpose=f"the painted corner: tools/painted_corner.py {' '.join(sys.argv[1:])}") as lk:
        backup = tempfile.mkdtemp(prefix="painted_corner_")
        before = {}
        for rel in GUARDED:
            src = os.path.join(REPO, rel)
            if os.path.exists(src):
                before[rel] = read(src)
                shutil.copy2(src, os.path.join(backup, rel.replace("/", "__")))
        try:
            proc = subprocess.Popen(cmd)
            lk.set_child(proc.pid)
            code = proc.wait()
        finally:
            restored = []
            for rel, data in before.items():
                path = os.path.join(REPO, rel)
                if not os.path.exists(path) or read(path) != data:
                    shutil.copy2(os.path.join(backup, rel.replace("/", "__")), path)
                    restored.append(rel)
            shutil.rmtree(backup, ignore_errors=True)

    lines = []
    if os.path.exists(log):
        with open(log, errors="replace") as f:
            for line in f:
                line = line.rstrip("\n")
                if OURS.match(line) or (TROUBLE.search(line) and not line.startswith("  at ")):
                    lines.append(line)
    for line in lines[-80:]:
        print(line)
    if restored:
        print("put back as they were: " + ", ".join(restored))
    print(f"{method.rsplit('.', 1)[-1]}: exit {code} in {time.time() - start:.0f} s (log: {os.path.relpath(log, REPO)})")
    return code


if __name__ == "__main__":
    sys.exit(main())
