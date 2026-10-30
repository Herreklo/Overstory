#!/bin/zsh
# The golden views (docs/measuring.md): render the street as its own test last built it (LT1Golden.Views: Street.unity,
# its judging views in its two lights, way Pc), at the player's size and as the player sees it, then compare every
# frame with the accepted baseline. Exits 1 if any frame fails, 2 if there is no baseline yet.
#
#     tools/golden.sh [Unity arguments, e.g. -lights lowsun -views street,high]
#
# Renders go to reviews/golden/current/street/<light>/<view>.png, the comparison (heat maps, sheets, report.md) to
# reviews/golden/compare/. Only Øystein accepts a baseline (golden_compare.py accept reviews/golden/current
# reviews/golden/baseline, once he has judged the frames).
# It runs under the Unity lock in timing mode (tools/unity_lock.py): it waits while the editor or another job has unity/
# open, or a Blender batch process runs, and writes the machine's background load to reviews/golden/compare/machine.json.
set -u
R=${0:A:h:h}
if [[ ${UNITY_LOCK_REEXEC:-} != $PPID ]]; then      # not yet under its own lock: run again under it
    export UNITY_LOCK_REEXEC=$$                     # (exec keeps the pid, so the wrapper is the run's parent)
    exec python3 $R/tools/unity_lock.py run --purpose "the golden views: tools/golden.sh $*" --timing \
        --out $R/reviews/golden/compare -- zsh ${0:A} "$@"
fi
UNITY=/Applications/Unity/Hub/Editor/6000.6.6f1/Unity.app/Contents/MacOS/Unity
BLENDER=/Applications/Blender.app/Contents/MacOS/Blender
mkdir -p $R/reviews/golden/compare
rm -rf $R/reviews/golden/current
$UNITY -batchmode -quit -projectPath $R/unity -executeMethod Overstory.EditorTools.LT1Golden.Views \
    -out reviews/golden/current "$@" -logFile $R/reviews/golden/compare/unity.log
code=$?
if [[ $code -ne 0 ]]; then
    echo "Unity failed ($code): see reviews/golden/compare/unity.log"
    exit $code
fi
if [[ -z $(find $R/reviews/golden/baseline -name '*.png' -print -quit 2>/dev/null) ]]; then
    echo "NO BASELINE: reviews/golden/baseline has no frames; today's are in reviews/golden/current. Accept them with"
    echo "golden_compare.py -- accept reviews/golden/current reviews/golden/baseline when Øystein has judged them."
    exit 2
fi
partial=()
[[ $# -gt 0 ]] && partial=(--present 1)
$BLENDER -b --factory-startup --python $R/blender/tools/golden_compare.py -- compare \
    $R/reviews/golden/baseline $R/reviews/golden/current $R/reviews/golden/compare $partial 2>&1 | grep -E "^(PASS|FAIL|MISSING|RESIZED|PASSED|FAILED)"
exit ${pipestatus[1]}
