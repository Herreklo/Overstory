# Showing time passing

Ideas for showing one place across years, wide on purpose (Øystein, 22 October: "there are many cool ways to show time progressing, we should try to be very creative here"). They are ideas, not decisions. The best few are prototyped in clay on the corner through the years (`docs/experiments.md`, LT1f) and judged there: for beauty by strict review, for readability by cold readers.

## The constraints

From `docs/research/time-on-screen.md` (§7, Rules for showing time), as `NOW.md` sets them: findings that bind every idea, not the answer.

1. Every pixel difference between two dates comes from the record.
2. Hold the camera, tier, day of year, sun and weather; name any change of season.
3. A cut, dissolve, fade or time-lapse is followed by an aligned comparison at the spot. The eye finds a change only where something visibly jumps.
4. Every jump is dated, at the record's precision.
5. Point at no more than the history budget (one, two, three), from the change query, never from a picture difference.
6. No cause by juxtaposition, and no morph between unrelated things: a cut invites a cause.
7. Every year is mostly older than itself.
8. Light of the date, never a grade for the era.
9. Something recurs across every jump.
10. Absence must be true too.
11. Watched or jumped, the town draws the same.

And our style: true up close, painted from afar (`docs/visual-direction.md`). The highlight must never read as light, since every light is a fact; marks on the map, never in the painting (`docs/research/interface-and-inspection.md`).

## The ideas

Each with where it comes from: known (a game, a film, a practice) or new (no example found).

1. **The toggle in place.** The view flips between two years with nothing between, as the astronomer's blink comparator and the rephotographer's flicker do. Known (rephotography, Rensink's flicker studies).
2. **The years strip.** Three or four dates of one view side by side, in order, each dated. Known (Third View, Vergara).
3. **The swipe.** A seam the player drags across one view: one year on each side. Known (then-and-now sliders on news sites).
4. **A window into another year.** A pane held over the scene, the other year inside it, aligned to the pixel, which the player moves like a loupe. Known as insets in comics (McGuire's *Here*); as a free loupe in a game, new.
5. **The photograph held at its spot.** An archive photograph, or one the player took earlier, held up where it was taken, filling part of the view; lowered, it shows now. Known (*Dear Photograph*, Klett's insets).
6. **Repainted, stroke by stroke, in the order things happened.** The view of one year is repainted into the next: each recorded change is brushed in where it happened, in date order, with its date, as a painter lays a new state over an old canvas. New.
7. **Pentimento.** The earlier year shows through the paint where the record changed something, faint, as a painter's corrections show through old canvases; the player rubs a place to bring it up. New in games.
8. **The ghost line.** What is gone is drawn as a faint pencil line over the present: the outline of a shopfront taken out, a demolished neighbour. Known as the dashed line of conservation phase plans; in a painted world, new.
9. **The phase plan.** Each part tinted by the decade it was put in, one colour a period, the undated left plain. Known (English Heritage phase plans). A study mode, map-like.
10. **The time-lapse.** The years run past in seconds: trees grow, coats fade, works come and go. Known (films, *SimCity*'s history replays).
11. **The cut with a date card.** A chapter jump. Known (*Pentiment*, *Mafia II*).
12. **The dissolve.** One year fades into the next. Known (film).
13. **The page turned.** The view as a plate in a book, the year on its edge; turning the page is a toggle with a hand in it. Known in print; in a game, new.
14. **Tracing paper.** The earlier year on a translucent sheet laid over the present and slid off, as an archivist overlays survey drawings. New.
15. **The light table.** Archive negatives of the spot laid over each other on a light table, the old one's dark where things have gone. New.
16. **Age rings.** Every part edged with faint rings, one for each time it was changed, like a tree's rings: the more rings, the more the part has been through. New.
17. **The record's highlight.** Everything dims a little except what the change query says changed between the two dates; the changed parts keep their full value, as a painter loses edges away from the focus. Known as change highlights; from the record, not a picture difference, new.
18. **A walk through time.** The year follows the camera along a path: walking up the lane walks from 1989 to 2020, one house at a time. New. Breaks "hold everything but the year" inside one frame.
19. **The sketchbook.** The earlier year drawn as a quick ink sketch beside, or over, the painted present: the past as a record, the present as paint. New.
20. **A person who stays.** One person recurs across every jump, older each time, standing where they stood. Known (*Cinema Paradiso*'s fountain man, *Pentiment*'s townsfolk).
21. **Shadows of the past.** At low sun, gone things cast their old shadows on the present. New. Violates "light of the date": a shadow is a claim about light.
22. **Weather as the passage.** A shower passes over the view and leaves the next year behind it. New. Claims weather the record does not hold.
23. **The newspaper on the wall.** A dated clipping pinned at the place (perceived information, which may be wrong), opening the comparison. Known as diegetic records (*Return of the Obra Dinn*'s book, *Pentiment*'s manuscripts).
24. **Sound first.** A change heard before it is seen: a hammer for works, a shop bell, a door boarded. New in this use; not visual alone.
25. **The flipbook in the margin.** A small flipbook of the view in a corner of the screen while the world stays put. Weak; listed for range.

## Ranked

Scored against the constraints that bite hardest (3: the jump visible; 5: the budget; 6: no false cause; 8: light of the date) and the style, then for what each buys: criterion 1 (reads right), 3 (a consequence) and 4 (preferred, not misled). Strong, fair, weak.

| Rank | Idea | Change found (3) | Budget, cause (5, 6) | Style | Criteria | Cost in clay | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Toggle in place | strong: the jump itself | strong if dated | neutral: the painting is untouched | 1, 3, 4 | low | prototype |
| 2 | Repainted, stroke by stroke | strong: each change is brushed in where it happened, one at a time | strong: one change at a time, each dated, from the record | ours: paint laying a new state | 1, 3, 4, and beauty | medium | prototype |
| 3 | A window into another year | strong at the pane's edge, where one part is split between years | fair: the player picks the place | fair: a pane is interface; as a photograph, diegetic | 1, 3 | medium | prototype, with the photograph as its diegetic form |
| 4 | The photograph held at its spot | strong | strong | ours: a dated object in the world | 1, 3, 4 | medium | folded into 3 |
| 5 | Years strip | strong for order, slow for small changes | strong | neutral | 1, 4 | low | the readers' material; the archive's view |
| 6 | Record's highlight | strongest | strong if from the change query | fair: risks reading as light | 1, 3 | low | later, with the change query |
| 7 | Pentimento | fair | strong | ours | 1, 3 | medium | later, as 2's still form |
| 8 | Ghost line | fair | strong (gone things only) | fair | 1 | low | later: after the window, for what is gone |
| 9 | Swipe | fair: strong at the seam, a part split by the seam misleads | fair | neutral | 1 | low | covered by 3 |
| 10 | Tracing paper, light table, page turned | as the toggle, with a gesture | strong | ours where diegetic | 1, 4 | medium | an archivist game's form of the toggle |
| 11 | Phase plan | strong for dates | strong | weak: colours the painting | 1 | medium | study mode on the map, never in the painting |
| 12 | Age rings | fair | strong | weak: a pattern over the picture | 1 | medium | no |
| 13 | A person who stays | needs people | strong | ours | 3, 9 | high (people) | with the people (plan step 5) |
| 14 | Newspaper, sound first | as a cue | fair: perceived information | ours | 3 | medium | with play |
| 15 | Time-lapse | weak for discrete changes | weak: years synthesised | ours for slow things | 3 | high | a passage only, then a toggle |
| 16 | Sketchbook | fair | fair | ours | 1 | medium | maybe, as the journal's form |
| 17 | Cut with a date card, dissolve | weak | weak: invites a cause | neutral | | low | a passage only |
| 18 | A walk through time | weak: two years in one frame | breaks rule 2 | | | medium | no |
| 19 | Shadows of the past, weather as the passage | | break rule 8: light and weather are facts | | | | no |
| 20 | Flipbook in the margin | weak | | | | low | no |

## The three prototyped (LT1f)

- **The toggle in place:** the evidence's answer, and the control the other two are measured against.
- **Repainted, stroke by stroke:** the one idea that is ours: it uses the painted style itself as the passage, keeps the budget by showing one change at a time in date order, dates each, and points only where the record changed something.
- **A window into another year:** the pane the player holds over a place, the other year inside it; and the same pane as a photograph held at its spot, the diegetic form.

What each showed, and how the readers and the review judged it, is in `docs/experiments.md` (LT1f).

**Taken forward (Øystein, 21 October):** repainted stroke by stroke leads, and the toggle is the baseline it must beat. Both go into the greybox as a switch (`docs/plan.md`, 1g). The window's photograph held at its spot is kept for close views. The rest of this list stays open for the creative exploration.
