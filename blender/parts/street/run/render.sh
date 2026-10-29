# install a house's build into the Street scene and render a round: render.sh <house> <round> [views] [ways] [lights]
# [planeShadow] [roofFlatUp]; with STREET_TIMING=<n> set, also a row of n such houses timed offscreen (timing.md); STREET_COMPRESS=0
# keeps the page uncompressed (BC7 by default); STREET_PAINT=<dir> takes the paint from there (paint.py --out), not the bake's out;
# run it under tools/unity_lock.py
set -e
cd "$(dirname $0)/../../../.."
h=$1; F=unity/Assets/Experiments/LT1/Street/Generated/$h; L=cache/street/unity-$2.log
mkdir -p $F
cp cache/street/gen/$h/house-near.fbx cache/street/gen/$h/house-street.fbx cache/street/gen/$h/house.json $F/
O=${STREET_PAINT:-cache/street/bake/$h/out}
cp $O/*.png $O/paint.json $F/
/Applications/Unity/Hub/Editor/6000.6.6f1/Unity.app/Contents/MacOS/Unity -batchmode -quit -projectPath $PWD/unity \
  -executeMethod Overstory.EditorTools.LT1Street.Run -streetHouse $h -streetRound $2 -streetViews ${3:-eye,street} \
  -streetWays ${4:-P,Pc} -streetLights ${5:-overcast,lowsun} ${6:+-streetPlaneShadow $6} ${7:+-streetRoofFlatUp $7} ${STREET_TIMING:+-streetTiming $STREET_TIMING} ${STREET_COMPRESS:+-streetCompress $STREET_COMPRESS} -logFile $L
grep -n "LT1Street\]\|error CS\|Exception" $L | tail -40
