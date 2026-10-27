#!/usr/bin/env python3
"""LT1's harbour town: runs a method of Code/Editor/Town/LT1Town.cs in Unity's batch mode under the Unity lock
(tools/unity_lock.py), and puts back the shared files a render rewrites as housekeeping (the sky's material and the
pipeline's settings), so other sessions' edits in them stay.

    python3 tools/town.py grey -- -out reviews/lt1/town/r01 [-views mid,midhigh]

The fixture (fixtures/lt1-harbour-town.json) is regrown first by blender/tools/grow_harbour.py: it is deterministic and
untracked. The log goes to unity/Builds/Town/unity.log (untracked); the lines that matter are printed.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNITY = "/Applications/Unity/Hub/Editor/6000.6.6f1/Unity.app/Contents/MacOS/Unity"
GUARDED = [
    "unity/Assets/Art/Materials/M_Sky.mat",
    "unity/Assets/Settings/PC_RPAsset.asset",
    "unity/Assets/Settings/PC_Renderer.asset",
    "unity/Assets/Settings/DefaultVolumeProfile.asset",
    "unity/ProjectSettings/GraphicsSettings.asset",
    "unity/ProjectSettings/ProjectSettings.asset",
    "unity/ProjectSettings/EditorBuildSettings.asset",
]
METHODS = {"grey": "Grey", "compose": "Compose", "stills": "Stills", "build": "Build"}


def main(argv):
    method = METHODS[argv[0]]
    extra = argv[argv.index("--") + 1:] if "--" in argv else []
    subprocess.check_call([sys.executable, os.path.join(REPO, "blender", "tools", "grow_harbour.py")],
                          stdout=subprocess.DEVNULL)
    log = os.path.join(REPO, "unity", "Builds", "Town", "unity.log")
    os.makedirs(os.path.dirname(log), exist_ok=True)
    keep = tempfile.mkdtemp()
    for p in GUARDED:
        shutil.copy2(os.path.join(REPO, p), os.path.join(keep, p.replace("/", "_")))
    try:
        cmd = [sys.executable, os.path.join(REPO, "tools", "unity_lock.py"), "run", "--owner", "town",
               "--purpose", method, "--", UNITY, "-batchmode", "-quit", "-projectPath", os.path.join(REPO, "unity"),
               "-executeMethod", f"Overstory.EditorTools.Town.LT1Town.{method}", "-logFile", log] + extra
        rc = subprocess.call(cmd)
    finally:
        for p in GUARDED:
            src = os.path.join(keep, p.replace("/", "_"))
            dst = os.path.join(REPO, p)
            if open(src, "rb").read() != open(dst, "rb").read():
                shutil.copy2(src, dst)
        shutil.rmtree(keep)
    for line in open(log, errors="replace"):
        if re.search(r"^\[LT1Town\]|error CS\d+|Exception: ", line):
            print(line.rstrip())
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
