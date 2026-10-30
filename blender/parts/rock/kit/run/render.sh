# install the street's 107 (kit.json beside: gen, paint) and the kit's parts (kit.json beside) into HolmTip and render a round: render.sh <round> [views]
# [ways] [lights]; TIP_GREY=1 also installs the tip's grey-box (tip.py) and draws it in place of the parts; TIP_JUDGE=1 draws each part
# alone in stage 2's grey (its judge.json; views front,back,side,near, ways N with its baked normal, M without);
# TIP_SUN=<degrees> turns the low sun (LT1HolmTip -tipSunOff); run it under tools/unity_lock.py
set -e
cd "$(dirname $0)/../../../../.."
D=unity/Assets/Experiments/LT1/Nature/HolmTip/Generated; L=cache/rock/kit/unity-$1.log
H=$(python3 -c "import json;print(json.load(open('blender/parts/rock/kit/kit.json'))['beside']['house'])")
P=$(python3 -c "import json;print(' '.join(p['part'] for p in json.load(open('blender/parts/rock/kit/kit.json'))['beside']['parts']))")
install() { mkdir -p $D/$1; cp $2/house-near.fbx $2/house-street.fbx $2/house-city.fbx $2/house.json $D/$1/;
  if [ -f $2/judge.json ]; then cp $2/judge.json $D/$1/; fi; if [ -f $2/foot.fbx ]; then cp $2/foot.fbx $2/foot.json $D/$1/; fi
  cp $3/*.png $3/paint.json $D/$1/; }
install $H $(python3 -c "import json;b=json.load(open('blender/parts/rock/kit/kit.json'))['beside'];print(b['gen'],b['paint'])")
for p in $P; do install $p cache/rock/kit/gen/$p cache/rock/kit/bake/$p/out; done
[ -n "$TIP_GREY" ] && { mkdir -p $D/tip; cp cache/rock/kit/gen/tip/tip.fbx cache/rock/kit/gen/tip/tip.json $D/tip/;
  cp cache/rock/kit/gen/tip/*.png $D/tip/ 2>/dev/null || true; }
/Applications/Unity/Hub/Editor/6000.6.6f1/Unity.app/Contents/MacOS/Unity -batchmode -quit -projectPath $PWD/unity \
  -executeMethod Overstory.EditorTools.LT1HolmTip.Run -tipRound $1 -tipViews ${2:-eye,street} -tipWays ${3:-P,Pc} \
  -tipLights ${4:-overcast,lowsun} ${TIP_GREY:+-tipGrey $TIP_GREY} ${TIP_JUDGE:+-tipJudge $TIP_JUDGE} ${TIP_SUN:+-tipSunOff $TIP_SUN} -logFile $L
grep -n "LT1HolmTip\]\|LT1Street\]\|error CS\|Exception" $L | tail -40
