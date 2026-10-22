#!/bin/zsh
# The motion sheets (docs/measuring.md): render the gully along its camera paths at 60 fps as the player sees it, then
# measure the shimmer of every sequence rendered.
#
#     tools/motion.sh [Unity arguments, e.g. -paths still,walk -moments 1300-drizzle -nodither -birch -test crawl]
#
# Sequences go to reviews/motion/current/<moment>/<path>/ (out of git, about 4 MB a frame); the shimmer report and
# sheets to reviews/motion/<date>/. It runs under the Unity lock (tools/unity_lock.py), which waits while the editor or
# another job has unity/ open.
set -u
R=${0:A:h:h}
if [[ ${UNITY_LOCK_REEXEC:-} != $PPID ]]; then      # not yet under its own lock: run again under it
    export UNITY_LOCK_REEXEC=$$                     # (exec keeps the pid, so the wrapper is the run's parent)
    exec python3 $R/tools/unity_lock.py run --purpose "the motion sheets: tools/motion.sh $*" -- zsh ${0:A} "$@"
fi
UNITY=/Applications/Unity/Hub/Editor/6000.6.6f1/Unity.app/Contents/MacOS/Unity
BLENDER=/Applications/Blender.app/Contents/MacOS/Blender
mkdir -p $R/reviews/motion/current
stamp=$R/reviews/motion/current/.started
touch $stamp
$UNITY -batchmode -quit -projectPath $R/unity -executeMethod Overstory.EditorTools.LT1Motion.Sheets "$@" \
    -logFile $R/reviews/motion/current/unity.log
code=$?
git -C $R checkout unity/Assets/Art/Materials/M_Sky.mat 2>/dev/null
grep -E "^\[LT1Motion\]|error CS|Exception" $R/reviews/motion/current/unity.log
[[ $code -ne 0 ]] && exit $code
# the sequences this run wrote (their sequence.json is newer than the start)
seqs=(${(f)"$(find $R/reviews/motion/current -name sequence.json -newer $stamp -exec dirname {} \;)"})
$BLENDER -b --factory-startup --python $R/blender/tools/motion_measure.py -- measure $seqs \
    --out $R/reviews/motion/$(date +%Y-%m-%d) 2>&1 | grep -E "frames|Error"
