#!/bin/zsh
# The walk's player (reviews/lt1/playable/outline.md §2, W1 and W2): compose the corner inside the clay town
# (LT1Play.Compose: the gully's hashes checked first, the scene saved into Experiments/LT1/Playable/Generated/ and
# checked again) and build unity/Builds/Playable/OverstoryPlayable.app from it, full screen at 2560 by 1440, MSAA 4x.
#
#     tools/playable.sh                                         (Compose and Build)
#     tools/playable.sh -method Compose [-stills reviews/lt1/playable/walk/w1]   (Compose and its check, and stills)
#
# It runs under the Unity lock (tools/unity_lock.py) and waits while another job or the editor has unity/ open. A build
# rewrites some settings as housekeeping, and the stage writes the sky's material; those that were clean before are put
# back after, as tools/perf.sh does, so nothing in git changes. The log is unity/Builds/Playable/build.log.
set -u
R=${0:A:h:h}
if [[ ${UNITY_LOCK_REEXEC:-} != $PPID ]]; then      # not yet under its own lock: run again under it
    export UNITY_LOCK_REEXEC=$$                     # (exec keeps the pid, so the wrapper is the run's parent)
    exec python3 $R/tools/unity_lock.py run --purpose "the walk's player: tools/playable.sh $*" -- zsh ${0:A} "$@"
fi
UNITY=/Applications/Unity/Hub/Editor/6000.6.6f1/Unity.app/Contents/MacOS/Unity
method=Build
args=()
for ((i = 1; i <= $#; i++)); do
    if [[ ${@[i]} == -method ]]; then method=${@[i+1]}; ((i++)); else args+=(${@[i]}); fi
done
SETTINGS=(unity/Assets/Art/Materials/M_Sky.mat unity/Assets/Settings/DefaultVolumeProfile.asset
          unity/Assets/Settings/PC_RPAsset.asset unity/Assets/Settings/UniversalRenderPipelineGlobalSettings.asset
          unity/ProjectSettings/GraphicsSettings.asset unity/ProjectSettings/ProjectSettings.asset)
clean=()
for f in $SETTINGS; do git -C $R diff --quiet -- $f && clean+=($f); done
mkdir -p $R/unity/Builds/Playable
start=$(date +%s)
$UNITY -batchmode -quit -projectPath $R/unity -executeMethod Overstory.EditorTools.LT1Play.$method $args \
    -logFile $R/unity/Builds/Playable/build.log
code=$?
end=$(date +%s)
[[ ${#clean} -gt 0 ]] && git -C $R checkout -- $clean
# our lines and the indented lines that follow them (the check's rows), compile errors and exceptions
awk '/^\[LT1Play\]/ { p = 1; print; next }  p && /^  [^ ]/ && !/^  at / { print; next }  { p = 0 }
     /error CS|Exception: / && !/^UnityEngine\.|^  at / { print }' $R/unity/Builds/Playable/build.log | head -60
echo "LT1Play.$method: exit $code in $((end - start)) s (Unity started, composed, checked$([[ $method == Build ]] && echo ', built'))"
exit $code
