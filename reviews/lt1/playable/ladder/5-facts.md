Not for Øystein: test 4 stays blind.

# Test 5: do the facts agree?

**Pass, with fixes. No kill.** Our authored layer settles every contradiction. None needs a home or a job the export rules out.

**The check.** `tools/playable/facts.py`, with tests in `tools/tests/test_facts.py` (24 of 24 pass), makes 1,020 checks in 94 classes:
- every diary field, each given a class;
- the diaries' claims, and every house resolved at the seeds' months;
- 154 claims in the case's strings: roles, jobs, kin, ages, deaths, labels, weekdays, hours, businesses at corner houses, presence, and each cited event's month, year and visibility.

Anything parsed from text is labelled derived. On the old diaries it finds all eleven faults; on the fixed, none. It exits 0: every other finding has a routed fix.

## Contradictions, fixes, costs

**1. A's 1988 café** (diary A event 6, Appendix A, the pitch's "You run the café at house A" and "the café window", the atlas, `heart_layout.py`). The export's only café is the Old Bank Café (pl-cafe13, v-13, 1979); the engine owns openings after S.
- *Applied:* A's shop stands empty from 1974. New owners paint it in 1996. The café opens in 2000, after the export ends. Both events keep their ids, so the colour of the 1996 coat is unchanged.
- *Cost:* at 1989 A loses its café (the ironmonger's ghost stays); at 2000 the shopfront's era moves to recent.

**2. B's 1997 bakery in seed B's 1998.** The engine's only ventures are cafés and festivals.
- *Applied:* the bakery opens in 2000.
- *Cost:* B has no shop in 1998. Nothing changes at 1989.

**3. D: "the owner dies; the heirs live in Oslo" (1986).** Tom Vaughan died in November 1985. His sons live in the town: Ken has led the Courier since 1976, and Jonah works at the council office until e-7478. "The heirs cannot agree" has no event behind it (FC3).
- *Applied:* "the owner died at the end of 1985; the house is shut up and boarded"; "still empty, and the roof lets in water".
- *Cost:* wording only.

**4. E: "the last owner dies" (1993).** Agnes died in December 1989 (e-6557) and has no living kin.
- *Applied:* "empty since its last owner died in December 1989; nobody takes it on, and it is let go" (still 1993).
- *Cost:* wording only.

**5. The pitch's "its lead Evan Newman".** Sean Hale leads the Anchor until he walks out (e-7079, November 1991). Evan becomes manager after that (e-7097). This lead is derived.
- *Routed to the case spec:* in 1989 the page's answer is Sean.

**6. "Tell Peter Lane at house C", between 10:00 and 18:00.** In 1989 he owns the café (derived from e-6908).
- *Routed:* the hours table places him at the café.
- *Cost:* "Peter first" costs the walk to the square, 3.5 minutes each way.

**7. Two fixes to sources and labels, both routed:**
- The outline cites e-6545 for Peter's ownership; the source is e-6908.
- The pitch calls Olive's job "canonical"; it is derived from e-8736 ("after ten years"), with no hire event.

**8. Copies of the old lines.** The atlas's diary column and its lit "A's café" are routed to new wording. `corner_fixture.py`, `lt1-corner.json` and `bld-104.json` still carry the old lines.

## The player's place at A

- **H, live at A with no trade.** This touches no engine fact. The player watches from A's empty shop window. Una Waller has the attic from November.
- **W, work at Peter's café.** An authored coworker joins Peter Lane, Lisa Myers and Eddie Lane in the month of their owner race (e-6545 to e-6547), where the engine could later contradict it. "Peter first" becomes cheap; the free Friday and the vantage at A must be rewritten.

On the facts alone, H is cleaner. The choice itself is a play question.

## Not covered

Form fields (the engine has no buildings), years before S, homes, pitches other than C3.1, and the shuffled arm (false by design). The frozen hours: `case-spec.md` does not exist yet, and the check will read it as the case, with no routes. New phrasings: the parsers are heuristics, tested on the case's sentences.

## Engine questions for the next bundle

1. **Unshifted years:** 136 event texts and 479 cause labels (279 unique, 424 events) carry engine years, 1985 to 2035 ("every week (2024)", e-6400). Structured dates, or the setting's start year (#23)?
2. **Job history:** no hire events before 1989, no place field. Each place's lead by month?
3. **Shops of unmodelled kinds** (bakeries, ironmongers): the engine's or ours?
4. **Heirs (request 31):** Tom Vaughan's widow Olive Shaw is kin; the casting omits her.
5. **Homes (#59).**

## For W1

- At 1989 the only resolved change is to house A: it now has no business. B, C, D and E are unchanged.
- In `heart_layout.py`, line 752 lights A as `shop="open"`; it should be `"empty"`. Line 465 names A as "café 1988". Neither was edited here.
- Do not rerun `time_key.py` until its sources are fixed: it would undo these fixes.
