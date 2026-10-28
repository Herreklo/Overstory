# install the build into the Finish scene and render a round: render.sh <round> <views> [ways, default A,B,C; P painted]; run it
# under tools/unity_lock.py
set -e
cd "$(dirname $0)/../../../.."
F=unity/Assets/Experiments/LT1/Finish; G=cache/finish/gen; L=cache/finish/unity-$1.log
mkdir -p $F/Generated
cp $G/corner-near.fbx $G/corner-street.fbx cache/finish/out/*.png cache/finish/out/scans.json cache/finish/out/unity.json cache/finish/out/paint.json $F/Generated/
/Applications/Unity/Hub/Editor/6000.6.6f1/Unity.app/Contents/MacOS/Unity -batchmode -quit -projectPath $PWD/unity \
  -executeMethod Overstory.EditorTools.LT1Finish.Run -finishRound $1 -finishViews $2 -finishWays ${3:-A,B,C} -logFile $L
grep -n "LT1Finish\]\|error CS\|Exception" $L | tail -40
