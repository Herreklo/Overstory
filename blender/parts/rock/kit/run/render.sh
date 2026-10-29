# install the street's 107 (kit.json beside: gen, paint) and the kit's parts (kit.json beside) into HolmTip and render a round: render.sh <round> [views]
# [ways] [lights]; run it under tools/unity_lock.py
set -e
cd "$(dirname $0)/../../../../.."
D=unity/Assets/Experiments/LT1/Nature/HolmTip/Generated; L=cache/rock/kit/unity-$1.log
H=$(python3 -c "import json;print(json.load(open('blender/parts/rock/kit/kit.json'))['beside']['house'])")
P=$(python3 -c "import json;print(' '.join(p['part'] for p in json.load(open('blender/parts/rock/kit/kit.json'))['beside']['parts']))")
install() { mkdir -p $D/$1; cp $2/house-near.fbx $2/house-street.fbx $2/house-city.fbx $2/house.json $D/$1/; cp $3/*.png $3/paint.json $D/$1/; }
install $H $(python3 -c "import json;b=json.load(open('blender/parts/rock/kit/kit.json'))['beside'];print(b['gen'],b['paint'])")
for p in $P; do install $p cache/rock/kit/gen/$p cache/rock/kit/bake/$p/out; done
/Applications/Unity/Hub/Editor/6000.6.6f1/Unity.app/Contents/MacOS/Unity -batchmode -quit -projectPath $PWD/unity \
  -executeMethod Overstory.EditorTools.LT1HolmTip.Run -tipRound $1 -tipViews ${2:-eye,street} -tipWays ${3:-P,Pc} \
  -tipLights ${4:-overcast,lowsun} -logFile $L
grep -n "LT1HolmTip\]\|LT1Street\]\|error CS\|Exception" $L | tail -40
