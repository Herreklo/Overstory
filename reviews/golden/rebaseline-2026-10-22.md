# Gully stairs, A against B: strict review

Method: each pair at frame size, then a pixel diff to find where they differ (01/02/06/07: 11 to 19 % of pixels, almost all stone-position shifts of a pixel or two; 03/04/05: 1 to 3 %), then 2x zooms of every pair and 4x/8x zooms of the suspect spots. Coordinates are in the 1280x720 crops.

## Per pair

**01, foot of the steps, low sun.** Stones sit a pixel or two apart; the same stones, the same faces. A has olive moss lines at the foot of the second and fourth risers (y≈505 and ≈680, x 100-500); B has them faintly. Both sit in the inside corner where water stands, so both are plausible. No fault in either. Equal.

**02, on the steps, low sun.** A carries a moss band along the foot of the big right-hand riser (y≈330-345, x 800-1280) and the one below (y≈490-500); B has none there and shows a lichen field instead (x 805-870, y 472-505). Lichen rosettes shift by a few pixels, nothing more. Equal.

**03, street stop.** Identical in form; the diff is confined to the lower flight's shading. Both show moss lines at riser feet here, B slightly more. Equal.

**04, 12 m up.** The landing flags, their joints and the dark wet patch are the same in both. Equal.

**05, city camera.** Indistinguishable at the size a player sees it. Equal.

**06, on the steps, drizzle.** Form is identical in grey light: same wobble inside each stone, same edges on the grid, no floating or interpenetrating stones. A's moss band (y≈310-345, x 640-1280) is the only read-level difference; B is drier on this step. Equal.

**07, foot of the steps, drizzle.** As 01 in grey light. Cheek walls identical course for course, including the chipped coping end (x≈85-100, y≈130-150). Equal.

## Faults, all shared by A and B, none exclusive to either

1. **Left cheek wall's low end, street stop (03, x≈780-815, y≈530-640).** At 8x the wall's end is thin tan slabs with the pavement's blue showing between them and a blue wedge below; it reads as a see-through end, not a built pier or quoin. Visible at native size as a stripy wall foot. The same thing darkens to a black band between the wall's inner face and the tread ends in 04 (x≈640-690, y≈540-600). Check the mesh: it looks like the wall's skins have no end cap.
2. **Joint slits (02/06: x≈100-115, y≈195-325; x≈350-360, y≈85-180; x≈568-575, y≈190-330; x≈640-650, y≈325-480; x≈540-560, y≈485-650).** Where a stone's end stands proud of its neighbour, the gap is a flat pure-black bar with no end face in it. It reads as a hole rather than a shadowed end, and at the street stop the flight is striped with dark ticks. Shade the end face or narrow the stagger.
3. **Lichen reads as decals under grey light (06/07).** Fields carry a uniform bright rim and the young rosettes are coin-round discs of one size. The bar's merged fields with rosettes between are there, but the rosettes need size and edge variation before they read as growth.
4. **Fine bedding lines catching the wet gloss (02, the big riser at x 240-1130, y≈200 and ≈300).** One-pixel bright lines; shimmer-prone in motion.
5. **Nosing gloss.** The wet film on every tread's front arris is strong but does not mirror; acceptable.

## Verdict

Neither build is worse than the other in any way a player would see. The differences are the generator's noise: stone positions, which face kind lands where, where the moss falls. Each outcome is as plausible as the other and none contradicts a cause. Both are fit to be the reference, and the choice can be made on other grounds (the leaner cheek wall, or the newer build). The five faults above are frozen into whichever is chosen and should be logged against it as known defects, so that fixing them is a deliberate change to the reference, not a regression.

## The key (unblinded after the verdict)

The build from today's generators (now the reference) is A in pairs 01, 02, 04, 06 and 07 and B in 03 and 05; the other is the gully committed at `200d596`. Crops are 1280 by 720 at native size from the 2560 by 1440 golden frames, placed where the two differ most: 01 low sun eye-foot (x 600, y 720), 02 low sun eye-on (720, 720), 03 low sun street (320, 680), 04 low sun into12 (320, 320), 05 low sun high (80, 640), 06 drizzle eye-on (720, 720), 07 drizzle eye-foot (600, 720). Reviewer: Fable 5.1, a fresh agent given only the crops and the bar, 22 October.
