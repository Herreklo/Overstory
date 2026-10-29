# install a house's build into the Street scene and render a round: render.sh <house> <round> [views] [ways] [lights]
# [planeShadow] [roofFlatUp]; with STREET_TIMING=<n> set, also a row of n such houses timed offscreen (timing.md); STREET_COMPRESS=0
# keeps the page uncompressed (BC7 by default); STREET_PAINT=<dir> takes the paint from there (paint.py --out), not the bake's out;
# STREET_GEN=<dir> the build from there; STREET_LEVEL=<level> draws every view at that level (an A/B of levels);
# STREET_CITYONE=0 keeps the city level a material a piece (one material and one draw by default); STREET_FARSHADOW=cast
# lets a timed house too far for its shadow to reach the shadowed distance cast all the same (none by default); STREET_SRPB=0
# turns the pipeline's SRP Batcher off for the run (an A/B of the batcher's draw path);
# run it under tools/unity_lock.py
set -e
cd "$(dirname $0)/../../../.."
h=$1; F=unity/Assets/Experiments/LT1/Street/Generated/$h; L=cache/street/unity-$2.log
mkdir -p $F
G=${STREET_GEN:-cache/street/gen/$h}
cp $G/house-near.fbx $G/house-street.fbx $G/house-city.fbx $G/house.json $F/
O=${STREET_PAINT:-cache/street/bake/$h/out}
cp $O/*.png $O/paint.json $F/
/Applications/Unity/Hub/Editor/6000.6.6f1/Unity.app/Contents/MacOS/Unity -batchmode -quit -projectPath $PWD/unity \
  -executeMethod Overstory.EditorTools.LT1Street.Run -streetHouse $h -streetRound $2 -streetViews ${3:-eye,street} \
  -streetWays ${4:-P,Pc} -streetLights ${5:-overcast,lowsun} ${6:+-streetPlaneShadow $6} ${7:+-streetRoofFlatUp $7} ${STREET_TIMING:+-streetTiming $STREET_TIMING} ${STREET_COMPRESS:+-streetCompress $STREET_COMPRESS} ${STREET_LEVEL:+-streetLevel $STREET_LEVEL} ${STREET_CITYONE:+-streetCityOne $STREET_CITYONE} ${STREET_FARSHADOW:+-streetFarShadow $STREET_FARSHADOW} ${STREET_SRPB:+-streetSrpBatcher $STREET_SRPB} -logFile $L
grep -n "LT1Street\]\|error CS\|Exception" $L | tail -40
