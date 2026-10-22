Not for Øystein: test 4 stays blind.

# Test 1: is the first telling a decision?

**Change, not a kill.** On both seeds the ranking of the named lines flips inside the sweep: in 7 of 24 sweeps on seed A and 10 of 24 on seed B. By the outline, that means the rule is tuned, not designed, and it is rewritten from one stated principle. Seed A's first-telling branches are flat. Seed B's are not, so the kill line (flat on both seeds) is not met.

`tools/playable/ties.py` reads only `case-spec.md`'s frozen block (sha256 `876b3185…`). Its toy cases and parsers ran first (`tools/tests/test_ties.py`, 12 of 12). Full output: `1-ties-run.txt`.

## Tie counts first

| Seed | Person | Kin | Partner | Coworkers | Liked | Disliked | Tied to |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A, December 1989 | Hannah | 1 | 0 | 0 | 1 | 0 | 2 |
| A, December 1989 | Olive | 2 | 0 | 3 | 2 | 1 | 8 |
| B, October 1998 | Trevor | 1 | 0 | 0 | 3 | 0 | 4 |
| B, October 1998 | Ben | 0 | 1 | 0 | 5 | 0 | 5 |
| B, October 1998 | Oliver | 2 | 1 | 5 | 6 | 1 | 12 |

The town has 138 tied pairs in 1989 and 243 in 1998. The events start in January 1989, so seed A's graph is thin by construction. Hannah's ties are Sid, at the sawmill all day, and Ben Reed. Olive works at the Anchor from noon, and anything she knows is said aloud there.

## Seed A (Agnes; Friday 15 December 1989)

| Pass line | Value | Holds |
| --- | --- | --- |
| Hannah-first and Olive-first branches ≥16 apart | 0 (20 and 20) | **no**; inside the kill line's 8 |
| The best line beats the page's (Sean first, −20) by ≥16 | +55 | yes |
| The best line beats Peter first (−15) by ≥16 | +50 | yes |
| Back to back (20) is not the best line (35) | | yes |
| The page's line reaches ≥6 by 18:00 | 14 | yes |
| The ranking holds across the sweep | flips at τ×½, work ±1 h, café ±1 h, Anchor staff −1 h, regulars −1 h | **no** |

The best line, Peter → Hannah → Sean → Olive, has no idea in it. Telling Peter and Sean first only delays Olive.

**The decision is when to tell, not who goes first.** The same tellings, started later (a check, not a pass line):

| Start | Hannah first | Olive first |
| --- | --- | --- |
| 11:00 | 50 | 20 |
| 12:00 to 16:00 | 50 | 50 |
| 17:00 | 60 | 65 |

Only the late lines reach the pick's 60. The 65 tells Olive at the Anchor first, then Hannah.

## Seed B (Andy; Friday 16 October 1998; run last, untuned)

**Branches:** the branches differ by 147. That is a flood, not a decision. Telling Trevor or Ben reaches 48 to 55 of 76 people by 18:00, through retired friends who are all off work, so these lines score −150 to −180.

**The best line** tells only Greta Brook (3.3); Oliver hears it from her through the family. No line passes; the best start, 17:00, gives 48.

**The page's line** scores −35 and reaches 7. The ranking flips in 10 sweeps, across τ, the telling's length, the minutes to elsewhere, two weights and four hours.

## What it means

- **The authored hours decide the ranking.** Shifting one hour of work, the café or the Anchor's staff reorders Peter first against the page's line.
- **"Both off work, so they ring" over-connects.** It floods a dense graph and leaves a thin one indifferent to order. The uncapped leak cost then dominates the score.
- **The case does have a decision:** when to tell Olive, who carries it into the Anchor. Lines told back to back from 10:00 cannot show it.

## Not done here

I did not rewrite the rule. A rule written now would be tuned on both seeds, and the only unread death is test 4's hold-out. The proposed principle: *people pass it on only to those they meet in their day, and a place says it aloud.* Reach would be the same place only, and lines could wait. Adopting it, and choosing which seed checks it, is the change's own decision.

## This rung's limits

- Numbers from the export plus our authored hours, homes and rule. They cannot say whether a player sees, feels or finds the decision.
- The player is assumed to know who visited; the 27 vantage plans only limit whom a line may tell (seed A median 35; seed B 3.3 throughout).
- One Friday; "elsewhere" a flat 10 minutes; squares crossed straight; the café's door and the Anchor (Harbour Row 22) provisional.
- Liking is the sign of seven event types; rosters are rebuilt from text (derived). The −10 for a private act is not exercised.

## Engine questions for the next bundle

1. **Ties before the events start.** Could the export carry the relationship state at `presentFrom`: friendships, dislikes, liking? Seed A's flat branches come partly from a graph half as dense as 1998's (pre-mortem must 3).
2. **Where people are in a day** (hours and homes, #59). The ranking turns on hours we authored.
