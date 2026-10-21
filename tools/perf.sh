#!/bin/zsh
# The frame-time harness (docs/measuring.md): compose today's corner, build its macOS player with frame timing stats on,
# and run it full screen at 2560 by 1440, twice unless told otherwise; the runs' summaries and how far they agree go to
# reviews/perf/<date>/.
#
#     tools/perf.sh [-runs 2] [-norun] [-out reviews/perf/<date>] [-perf-frames 150] [-perf-warmup 30] [-perf-rounds 2]
#         [-perf-settle 600] [-perf-only street]
#
# The player takes over the screen while it runs (a few minutes a run). The Unity editor must not be open on unity/.
# A build rewrites some settings as housekeeping (URP's stripping prefilters, the default volume profile's full list,
# the graphics settings' warm-up fields); those that were clean before are put back after, so nothing in git changes.
set -u
R=${0:A:h:h}
UNITY=/Applications/Unity/Hub/Editor/6000.6.6f1/Unity.app/Contents/MacOS/Unity
SETTINGS=(unity/Assets/Art/Materials/M_Sky.mat unity/Assets/Settings/DefaultVolumeProfile.asset
          unity/Assets/Settings/PC_RPAsset.asset unity/Assets/Settings/UniversalRenderPipelineGlobalSettings.asset
          unity/ProjectSettings/GraphicsSettings.asset unity/ProjectSettings/ProjectSettings.asset)
clean=()
for f in $SETTINGS; do git -C $R diff --quiet -- $f && clean+=($f); done
mkdir -p $R/unity/Builds/Perf
$UNITY -batchmode -quit -projectPath $R/unity -executeMethod Overstory.EditorTools.LT1Perf.Build "$@" \
    -logFile $R/unity/Builds/Perf/build.log
code=$?
[[ ${#clean} -gt 0 ]] && git -C $R checkout -- $clean
grep -E "^\[LT1Perf\]|error CS|Exception" $R/unity/Builds/Perf/build.log
exit $code
