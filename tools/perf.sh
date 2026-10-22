#!/bin/zsh
# The frame-time harness (docs/measuring.md): compose today's corner, build its macOS player with frame timing stats on,
# and run it full screen at 2560 by 1440, twice unless told otherwise; the runs' summaries and how far they agree go to
# reviews/perf/<date>/.
#
#     tools/perf.sh [-runs 2] [-norun] [-out reviews/perf/<date>] [-perf-frames 150] [-perf-warmup 30] [-perf-rounds 2]
#         [-perf-settle 600] [-perf-only street]
#     tools/perf.sh playable [same options]     # the walk's whole scene (LT1Perf.BuildPlayable), into reviews/perf/<date>/playable
#
# The player takes over the screen while it runs (a few minutes a run). It runs under the Unity lock in timing mode
# (tools/unity_lock.py): it waits while the editor or another job has unity/ open, or a Blender batch process runs, and
# writes the machine's background load as machine.json into each run's folder.
# A build rewrites some settings as housekeeping (URP's stripping prefilters, the default volume profile's full list,
# the graphics settings' warm-up fields); those that were clean before are put back after, so nothing in git changes.
set -u
R=${0:A:h:h}
arm=corner
[[ ${1:-} == playable ]] && arm=playable
if [[ ${UNITY_LOCK_REEXEC:-} != $PPID ]]; then      # not yet under its own lock: run again under it
    export UNITY_LOCK_REEXEC=$$                     # (exec keeps the pid, so the wrapper is the run's parent)
    out=reviews/perf/$(date +%Y-%m-%d)
    [[ $arm == playable ]] && out=$out/playable
    for ((i = 1; i < $#; i++)); do [[ ${@[i]} == -out ]] && out=${@[i+1]}; done
    [[ $out == /* ]] || out=$R/$out
    exec python3 $R/tools/unity_lock.py run --purpose "the frame-time harness: tools/perf.sh $*" --timing \
        --out $out --out-runs 'run-*' -- zsh ${0:A} "$@"
fi
method=Build log=build.log
if [[ $arm == playable ]]; then shift; method=BuildPlayable log=build-playable.log; fi
UNITY=/Applications/Unity/Hub/Editor/6000.6.6f1/Unity.app/Contents/MacOS/Unity
SETTINGS=(unity/Assets/Art/Materials/M_Sky.mat unity/Assets/Settings/DefaultVolumeProfile.asset
          unity/Assets/Settings/PC_RPAsset.asset unity/Assets/Settings/UniversalRenderPipelineGlobalSettings.asset
          unity/ProjectSettings/GraphicsSettings.asset unity/ProjectSettings/ProjectSettings.asset)
clean=()
for f in $SETTINGS; do git -C $R diff --quiet -- $f && clean+=($f); done
mkdir -p $R/unity/Builds/Perf
$UNITY -batchmode -quit -projectPath $R/unity -executeMethod Overstory.EditorTools.LT1Perf.$method "$@" \
    -logFile $R/unity/Builds/Perf/$log
code=$?
[[ ${#clean} -gt 0 ]] && git -C $R checkout -- $clean
grep -E "^\[LT1(Perf|Play)\]|error CS|Exception" $R/unity/Builds/Perf/$log
exit $code
