# install a house's build into the Street scene and render a round: render.sh <house> <round> [views] [ways] [lights];
# run it under tools/unity_lock.py
set -e
cd "$(dirname $0)/../../../.."
h=$1; F=unity/Assets/Experiments/LT1/Street/Generated/$h; L=cache/street/unity-$2.log
mkdir -p $F
cp cache/street/gen/$h/house-near.fbx cache/street/gen/$h/house-street.fbx cache/street/gen/$h/house.json $F/
cp cache/street/bake/$h/out/*.png cache/street/bake/$h/out/paint.json $F/
/Applications/Unity/Hub/Editor/6000.6.6f1/Unity.app/Contents/MacOS/Unity -batchmode -quit -projectPath $PWD/unity \
  -executeMethod Overstory.EditorTools.LT1Street.Run -streetHouse $h -streetRound $2 -streetViews ${3:-eye,street} \
  -streetWays ${4:-P,Pc} -streetLights ${5:-overcast,lowsun} -logFile $L
grep -n "LT1Street\]\|error CS\|Exception" $L | tail -40
