# build the tip's block-in and render a round in Unity: render.sh <round> [views] [lights]; run it under tools/unity_lock.py
set -e
cd "$(dirname $0)/../../../.."
N=unity/Assets/Experiments/LT1/Nature; G=cache/rock/gen; L=cache/rock/unity-$1.log
mkdir -p $G $N/Generated
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P blender/parts/rock/blockin.py -- \
  --out $G --render none --fbx $G/holm-tip.fbx --digest $G/unity.json 2>&1 | grep "^\[blockin\]"
cp $G/holm-tip.fbx $G/unity.json $N/Generated/
/Applications/Unity/Hub/Editor/6000.6.6f1/Unity.app/Contents/MacOS/Unity -batchmode -quit -projectPath $PWD/unity \
  -executeMethod Overstory.EditorTools.LT1Nature.Run -natureRound $1 ${2:+-natureViews $2} ${3:+-natureLights $3} -logFile $L
grep -n "LT1Nature\]\|error CS\|Exception" $L | tail -30
