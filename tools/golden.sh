#!/bin/zsh
# The golden views (docs/measuring.md): render today's gully at the judging views in the three lights, at the player's
# size and as the player sees it, then compare every frame with the accepted baseline. Exits 1 if any frame fails.
#
#     tools/golden.sh [Unity arguments, e.g. -moments 1600 -views street,high]
#
# Renders go to reviews/golden/current/, the comparison (heat maps, sheets, report.md) to reviews/golden/compare/.
# The Unity editor must not be open on unity/.
set -u
R=${0:A:h:h}
UNITY=/Applications/Unity/Hub/Editor/6000.6.6f1/Unity.app/Contents/MacOS/Unity
BLENDER=/Applications/Blender.app/Contents/MacOS/Blender
mkdir -p $R/reviews/golden/compare
rm -rf $R/reviews/golden/current
$UNITY -batchmode -quit -projectPath $R/unity -executeMethod Overstory.EditorTools.LT1Golden.Views \
    -out reviews/golden/current "$@" -logFile $R/reviews/golden/compare/unity.log
code=$?
git -C $R checkout unity/Assets/Art/Materials/M_Sky.mat 2>/dev/null
if [[ $code -ne 0 ]]; then
    echo "Unity failed ($code): see reviews/golden/compare/unity.log"
    exit $code
fi
partial=()
[[ $# -gt 0 ]] && partial=(--present 1)
$BLENDER -b --factory-startup --python $R/blender/tools/golden_compare.py -- compare \
    $R/reviews/golden/baseline $R/reviews/golden/current $R/reviews/golden/compare $partial 2>&1 | grep -E "^(PASS|FAIL|MISSING|RESIZED|PASSED|FAILED)"
exit ${pipestatus[1]}
