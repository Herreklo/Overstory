# the corner, its tileables, the scans and the marks, into cache/finish (untracked)
set -e
cd "$(dirname $0)/../../../.."
B=/Applications/Blender.app/Contents/MacOS/Blender; G=cache/finish/gen; mkdir -p $G
$B -b --factory-startup -P blender/parts/finish/corner.py -- --out $G 2>&1 | grep "^\[" || true
$B -b --factory-startup -P blender/parts/finish/tiles.py -- --cache cache/finish 2>&1 | grep "^\[" || true
$B -b --factory-startup -P blender/parts/finish/scans.py -- --gen $G --cache cache/finish 2>&1 | grep "^\[" || true
$B -b --factory-startup -P blender/parts/finish/marks.py -- --gen $G --cache cache/finish 2>&1 | grep "^\[" || true
