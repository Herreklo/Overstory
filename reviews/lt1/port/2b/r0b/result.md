# R0b: whose are the gully's one-pixel lines and specks

Port step 2b, rung R0b, 22 October: today's gully mesh, one shading change at a time, six views, three lights, 2560 by 1440, one sample a pixel, MSAA 4×.

`tools/r0b_count.py` counts in a mask of the gully's stone, and was checked by eye in all three lights:

- **Lines:** px length of top-hats over 4 L*, longer than 10 px and thinner than 2 px.
- **Specks:** blobs of 1 to 4 px, 8 L* off their 5×5 median.

## In short

1. **The pipeline makes none.** Bloom, its clamp, shadow bias and SSAO each move them −1 to +1% (SSAO off adds 5% specks), within the noise: the baseline again (A2) moves ±2% summed, ±5% per view.
2. **The stone's named terms make almost none:** GNF 1%, joint floor 2 to 3%, cut marks 0%; all six together −1%.
3. **The rest is the stone's, so the redraw's.** Growth's colour (moss's lines, lichen's specks) makes half the lines and three quarters of the specks. The rock's own colour and relief make none. The mesh keeps 48% of lines and 27% of specks, on joints and nosings.
4. **The reopen (90% gone on today's mesh) does not fire:** the redraw keeps its scope; nothing goes to 1c.

## Counts

Lines (px) / specks; share rows: removed, over the views. `all`: the six, bloom off; `all-clamp`: the clamp instead. Other `all-` configs add one change: `flat` (one colour, no relief), its halves `onecolour` and `norelief`, `nogrowth`, `onerock` (the rock's own colour as one value), `nolichen`, `nomoss`. `sheet.png`, low sun, eye-foot over street, native crops: A, all, all-flat, then A's and all-flat's marks (bright lines red, dark blue, specks yellow).

| light | view | A | gnf | jointfloor | cutmarks | bloom-off | bloom-clamp | bias02 | ssao-off | all | all-clamp | all-flat | all-onecolour | all-norelief | all-nogrowth | all-onerock | all-nolichen | all-nomoss | A2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| low sun | eye-foot | 5113/859 | 5178/859 | 5143/872 | 5009/864 | 5185/884 | 5153/876 | 5142/873 | 4915/940 | 5013/895 | 4862/887 | 3161/586 | 3053/606 | 4943/892 | 2939/559 | 5295/889 | 4822/775 | 2726/611 | 5172/872 |
| low sun | eye-on | 8076/865 | 8061/875 | 8139/880 | 7922/872 | 8084/870 | 7848/891 | 7956/874 | 7541/870 | 7303/816 | 7437/831 | 4389/485 | 4349/507 | 7397/819 | 4982/508 | 7234/937 | 6734/716 | 4420/518 | 7945/852 |
| low sun | eye-down | 4468/391 | 4524/380 | 4387/374 | 4393/396 | 4543/381 | 4530/381 | 4340/396 | 4701/366 | 4730/385 | 4793/386 | 1472/79 | 1313/81 | 4619/311 | 3132/187 | 4632/317 | 4543/274 | 2431/258 | 4543/394 |
| low sun | street | 2407/654 | 2353/652 | 2468/659 | 2416/659 | 2535/653 | 2419/648 | 2448/667 | 2371/637 | 2324/610 | 2268/627 | 1146/220 | 1165/206 | 2231/625 | 2122/361 | 2070/645 | 2199/591 | 1904/283 | 2460/643 |
| low sun | into12 | 3975/1164 | 4038/1186 | 3812/1098 | 3978/1199 | 3936/1179 | 3828/1166 | 4027/1167 | 3587/1178 | 3719/1145 | 3854/1140 | 589/154 | 570/154 | 3982/1184 | 1506/595 | 3691/1039 | 3853/1169 | 1112/490 | 3959/1181 |
| low sun | high | 2248/746 | 2272/732 | 2017/633 | 2219/753 | 2289/767 | 2270/754 | 2283/743 | 2301/737 | 2141/656 | 2142/642 | 135/130 | 114/130 | 2250/644 | 909/381 | 2241/603 | 1963/534 | 860/384 | 2220/726 |
| drizzle | eye-foot | 6258/1614 | 6444/1566 | 6169/1579 | 6450/1586 | 6250/1605 | 6619/1595 | 6565/1639 | 6561/1748 | 6888/1664 | 6815/1664 | 3540/366 | 3642/374 | 6920/1602 | 4447/508 | 6245/1673 | 5677/571 | 5339/1506 | 6436/1624 |
| drizzle | eye-on | 10263/2102 | 9901/2100 | 9830/2056 | 9854/2064 | 10158/2083 | 9879/2122 | 10190/2108 | 10911/2370 | 10199/2266 | 10324/2283 | 6681/373 | 6693/376 | 10222/2094 | 5333/412 | 11309/2562 | 7197/496 | 8272/2191 | 10096/2133 |
| drizzle | eye-down | 2651/1205 | 2523/1198 | 2465/1179 | 2651/1176 | 2649/1205 | 2605/1200 | 2546/1187 | 2901/1210 | 2830/1162 | 2846/1148 | 1829/37 | 1777/74 | 2793/1035 | 1530/105 | 2685/1154 | 2079/150 | 2309/1231 | 2584/1194 |
| drizzle | street | 5005/462 | 4957/464 | 4908/462 | 5114/466 | 4963/474 | 4979/472 | 4935/469 | 5243/514 | 4941/473 | 5320/490 | 3191/350 | 3252/347 | 5278/475 | 3302/338 | 4606/569 | 3593/392 | 4512/412 | 5060/480 |
| drizzle | into12 | 6564/958 | 6620/963 | 6313/930 | 6719/976 | 6520/965 | 6575/971 | 6445/967 | 6769/998 | 7156/1008 | 7077/1004 | 1101/189 | 1182/193 | 7216/997 | 2738/428 | 6947/1160 | 4158/472 | 3894/496 | 6325/964 |
| drizzle | high | 2864/458 | 2981/469 | 2964/410 | 2964/472 | 2953/467 | 2883/464 | 3006/462 | 2919/474 | 2753/443 | 2718/420 | 966/110 | 1086/109 | 2689/423 | 813/208 | 3167/454 | 2506/273 | 803/208 | 2995/460 |
| blue hour | eye-foot | 4400/722 | 4358/709 | 4233/702 | 4517/709 | 4346/692 | 4364/685 | 4338/709 | 4355/757 | 4714/762 | 4634/731 | 3763/293 | 3690/288 | 4718/761 | 3168/356 | 4458/585 | 4389/526 | 3016/557 | 4345/700 |
| blue hour | eye-on | 8789/784 | 8420/739 | 8789/744 | 8734/772 | 8857/768 | 8539/765 | 8515/758 | 7952/820 | 8048/810 | 7703/810 | 5358/238 | 5017/229 | 8093/798 | 5167/337 | 7877/777 | 6634/466 | 5555/596 | 8372/795 |
| blue hour | eye-down | 3387/353 | 3477/350 | 3420/342 | 3651/357 | 3428/346 | 3437/335 | 3466/344 | 3847/384 | 4099/381 | 4162/397 | 1360/41 | 1204/39 | 4117/353 | 2870/148 | 3558/241 | 3773/229 | 2748/323 | 3508/358 |
| blue hour | street | 2747/532 | 2734/520 | 2609/505 | 2688/520 | 2842/522 | 2697/522 | 2760/499 | 2684/508 | 2680/517 | 2698/533 | 1497/92 | 1572/89 | 2666/521 | 1668/216 | 2544/480 | 2139/368 | 2291/238 | 2703/518 |
| blue hour | into12 | 4461/849 | 4324/816 | 4054/794 | 4527/844 | 4116/824 | 4082/843 | 4231/840 | 4578/924 | 4930/908 | 5004/927 | 698/164 | 648/155 | 4944/895 | 1815/494 | 4561/851 | 3542/685 | 2225/568 | 4286/832 |
| blue hour | high | 3110/526 | 3129/511 | 2991/498 | 3413/551 | 3211/519 | 3075/536 | 3254/517 | 3166/527 | 3344/521 | 3198/522 | 481/135 | 521/132 | 3231/543 | 1148/270 | 2875/533 | 2456/392 | 1339/346 | 3212/531 |

| light | metric | gnf | jointfloor | cutmarks | bloom-off | bloom-clamp | bias02 | ssao-off | all | all-clamp | all-flat | all-onecolour | all-norelief | all-nogrowth | all-onerock | all-nolichen | all-nomoss | A2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| low sun | lines (A 26287) | -1% | +1% | +1% | -1% | +1% | +0% | +3% | +4% | +4% | +59% | +60% | +3% | +41% | +4% | +8% | +49% | -0% |
| low sun | specks (A 4679) | -0% | +3% | -1% | -1% | -1% | -1% | -1% | +4% | +4% | +65% | +64% | +4% | +45% | +5% | +13% | +46% | +0% |
| drizzle | lines (A 33605) | +1% | +3% | -0% | +0% | +0% | -0% | -5% | -3% | -4% | +48% | +48% | -5% | +46% | -4% | +25% | +25% | +0% |
| drizzle | specks (A 6799) | +1% | +3% | +1% | +0% | -0% | -0% | -8% | -3% | -3% | +79% | +78% | +3% | +71% | -11% | +65% | +11% | -1% |
| blue hour | lines (A 26894) | +2% | +3% | -2% | +0% | +3% | +1% | +1% | -3% | -2% | +51% | +53% | -3% | +41% | +4% | +15% | +36% | +2% |
| blue hour | specks (A 3766) | +3% | +5% | +0% | +3% | +2% | +3% | -4% | -4% | -4% | +74% | +75% | -3% | +52% | +8% | +29% | +30% | +1% |
| all | lines (A 86786) | +1% | +2% | -0% | -0% | +1% | +0% | -1% | -1% | -1% | +52% | +53% | -2% | +43% | +1% | +17% | +36% | +1% |
| all | specks (A 15244) | +1% | +3% | +0% | +0% | +0% | +0% | -5% | -1% | -1% | +73% | +73% | +2% | +58% | -1% | +40% | +26% | -0% |

## Verdict

| Whose | Lines | Specks |
| --- | --- | --- |
| Pipeline: bloom, shadow bias, SSAO | 0 (−1 to +1%) | 0 (SSAO off adds 5%) |
| Stone's named terms: GNF, joint floor, cut marks | 0 to 2% | 0 to 3% |
| All six together | −1% | −1% |
| Stone's colour | 53% | 73% |
| … growth (moss alone; lichen alone; they overlap) | 43% (36; 17) | 58% (26; 40) |
| … rock's own colour | 1% | −1% |
| Relief (grain map) | −2% | 2% |
| Mesh alone (what `all-flat` keeps) | 48% | 27% |

**Where:** outlines (2 px around each stone) are 15% of the stone's pixels, joints 2%. The mesh alone puts 82 to 95% of its marks on outlines and half its dark lines and specks on joints. Seven in ten of its bright lines are nosings at 1 px. Without moss, tread tops' share of the dark lines falls from 49% to 6%.

**For the plan (evidence, not a change):** SN7 cuts lichen (alone 17% of lines, 40% of specks). It keeps moss ("a soft line at the back of each tread"), today's largest maker of lines; band-limiting it belongs to the shared `Growth.hlsl`. The mesh's share is what SN4's chamfers and SN5's fills address.

**Joint floor:** soil is 0.4% of pixels and 9% of the dark lines, dark because it is sunk and occluded, which only shallower fills (SN5) change. Beds, pointing and dabs (21%) lie outside the floor.

**GNF:** the look gives the sun no specular; only lamps and reflections give gloss.

## The overrides, exact

Set in memory after `LT1Stone.Stage`, restored in a `finally`, never saved. `unity/` hashed unchanged around every run, and `M_Sky.mat` was restored exactly.

- **Shadow normal bias:** 0.2 against 0.5.
- **Bloom off (upper bound):** intensity 0, not 0.15 (0.35 in low sun).
- **Bloom clamp (proxy):** 2, not 65472; threshold 1.1 kept.
- **SSAO:** feature inactive.
- **GNF:** `GeometricNormalFiltering(smoothness, normalWS, 0.1, 0.2)` after wet.
- **Joint floor:** kind 6 no darker than face L* − 6 in the same light, scene-linear.
- **Cut marks:** rust 0, hue bins 1, crumb and sand 0.5, film 0, crazing 0.
- **The arms** sit behind `LT1R0b`'s keyword `OS_R0B`; `Growth.hlsl` is untouched. Stripped, `Stone.shader` is HEAD plus L5's lines, and a baseline frame came out byte-identical (`pre-edit/`).

## Not measured

Karis averaging (URP has none); each cut mark, streaks and lost pointing alone; the look's brush, grime and haze; grey light (the floor is pre-tonemap); lines under 4 L* (broken lines count as specks).
