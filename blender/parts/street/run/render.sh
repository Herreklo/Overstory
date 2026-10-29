# install a house's build into the Street scene and render a round: render.sh <house> <round> [views] [ways] [lights]
# [planeShadow] [roofFlatUp]; with STREET_TIMING=<n> set, also a row of n such houses timed offscreen (timing.md); STREET_COMPRESS=0
# keeps the page uncompressed (BC7 by default); STREET_PAINT=<dir> takes the paint from there (paint.py --out), not the bake's out;
# STREET_GEN=<dir> the build from there; STREET_LEVEL=<level> draws every view at that level (an A/B of levels);
# STREET_CITYONE=0 keeps the city level a material a piece (one material and one draw by default); STREET_FARSHADOW=cast
# lets a timed house too far for its shadow to reach the shadowed distance cast all the same (none by default); STREET_SRPB=0
# turns the pipeline's SRP Batcher off for the run (an A/B of the batcher's draw path); STREET_SHADOWTWO=0 casts the
# house's shadows one-sided (two-sided by default); STREET_ROW="<house>:<gen dir>:<paint dir> ..." installs each house
# and draws them together on their plots from the row's views (the <house> argument is then ignored; stills row-*);
# STREET_GROUNDSKY=0 leaves the ground open to the sky at the houses' feet (an A/B of the ground's own sky);
# STREET_WALK=<n> also draws n frames walking from the eye view back to the street stop (stills *-walkNNN-*, for a clip);
# run it under tools/unity_lock.py
set -e
cd "$(dirname $0)/../../../.."
h=$1; L=cache/street/unity-$2.log
install() {  # <house> <gen dir> <paint dir>
  F=unity/Assets/Experiments/LT1/Street/Generated/$1
  mkdir -p $F
  cp $2/house-near.fbx $2/house-street.fbx $2/house-city.fbx $2/house.json $F/
  cp $3/*.png $3/paint.json $F/
}
if [ -n "$STREET_ROW" ]; then
  H=""
  for e in $STREET_ROW; do IFS=: read k g o <<< "$e"; install $k $g $o; H=${H:+$H,}$k; done
else
  install $h ${STREET_GEN:-cache/street/gen/$h} ${STREET_PAINT:-cache/street/bake/$h/out}
fi
/Applications/Unity/Hub/Editor/6000.6.6f1/Unity.app/Contents/MacOS/Unity -batchmode -quit -projectPath $PWD/unity \
  -executeMethod Overstory.EditorTools.LT1Street.Run -streetHouse $h ${H:+-streetHouses $H} -streetRound $2 -streetViews ${3:-eye,street} \
  -streetWays ${4:-P,Pc} -streetLights ${5:-overcast,lowsun} ${6:+-streetPlaneShadow $6} ${7:+-streetRoofFlatUp $7} ${STREET_TIMING:+-streetTiming $STREET_TIMING} ${STREET_COMPRESS:+-streetCompress $STREET_COMPRESS} ${STREET_LEVEL:+-streetLevel $STREET_LEVEL} ${STREET_CITYONE:+-streetCityOne $STREET_CITYONE} ${STREET_FARSHADOW:+-streetFarShadow $STREET_FARSHADOW} ${STREET_SRPB:+-streetSrpBatcher $STREET_SRPB} ${STREET_SHADOWTWO:+-streetShadowTwo $STREET_SHADOWTWO} ${STREET_GROUNDSKY:+-streetGroundSky $STREET_GROUNDSKY} ${STREET_WALK:+-streetWalk $STREET_WALK} -logFile $L
grep -n "LT1Street\]\|error CS\|Exception" $L | tail -40
