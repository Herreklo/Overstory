# the round's four sheets: rows overcast and low sun; columns A, B, C at 1:1, then the photo at the same metres a pixel
set -e
cd "$(dirname $0)/../../../.."
r=$1; R=cache/finish/renders/$r; O=reviews/lt1/finish/$r; mkdir -p $O
P9=docs/references/houses/09-pedersgata-81-derelict-1989.jpg; P1=docs/references/houses/01-nedre-strandgate-17-1989.jpg
T=blender/parts/finish/run/montage.py
sheet() { # view crop p9crop p9scale p1crop p1scale; the eye sheet as JPEG, the rest PNG
  /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P $T -- $O/$1.${EXT:-png} $R/$1-overcast-A.png@$2@1@A $R/$1-overcast-B.png@$2@1@B $R/$1-overcast-C.png@$2@1@C $P9@$3@$4@09 / \
     $R/$1-lowsun-A.png@$2@1@A $R/$1-lowsun-B.png@$2@1@B $R/$1-lowsun-C.png@$2@1@C ${5:+$P1@$5@$6@01} 2>&1 | grep montage
}
EXT=jpg sheet eye 950,60,1150,1300 880,440,480,560 2.4
sheet street 1110,500,440,440 880,380,560,600 0.47 380,420,420,470 1.12
sheet raised 1080,420,500,540 880,380,560,600 0.59 380,420,420,470 1.4
sheet high 1180,590,230,230 700,300,760,760 0.2 340,380,520,520 0.49
