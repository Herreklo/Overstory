Not for Øystein: test 4 stays blind.

# The case, frozen for the ladder: "Before Friday"

**In short.** This is the case the ladder tests (`outline.md` §3). It holds the spread rule, the score, the authored hours, the homes and the sightings in one JSON block. `tools/playable/ties.py` reads that block and refuses to run unless its sha256 matches the hash frozen in the script. A change after any result is a new case. It carries the pre-mortem's fixes for the ladder (`premortem.md` §4), test 5's routed facts (`ladder/5-facts.md`), Øystein's choice of the player's place, and the hold-out for test 4. Every value is labelled: *simulated* (the export's own field), *derived* (read from the export's event text by `tools/playable/facts.py`), or *authored* (ours, for play).

## The case

**Seed A** (the case). Agnes Fielding of house E dies after a long illness in December 1989 (e-6557, public). Two people visited her that November, and nobody else knew:
- Hannah Tanner came every week (e-6531, private);
- Olive Shaw kept turning up with something or other (e-6532, private).

On the Friday, 15 December 1989, the player has heard of the death and has the hours from 10:00 to 18:00. At 18:00 the Anchor says it aloud to everyone there. The goal: each of the two hears it from the player before then, and as few others as possible hear it early.

**Seed B** (run last; nothing is tuned on it). Andy Shaw of the Low Terrace dies after a long illness in October 1998 (e-8899). Three visitors came that September: Trevor Lane, Ben Reed and Oliver Brook of house B (e-8881 to e-8883, private). His three visitors share the 80 points equally. The Friday is 16 October 1998.

## The player

**Øystein's choice (22 October): the player lives at A, with no trade.** It touches no engine fact. A's shop has stood empty since 1974 (diary A, after test 5's fix), so the player watches from A's windows: the empty shopfront facing the quay, and the right-hand and back windows over the Gully Steps. Una Waller has the attic from November 1989 (e-6528). The player has no job, so no hours bind them; every telling starts from A.

## Test 5's facts, which bind the case

- The Anchor's lead in December 1989 is **Sean Hale** (derived: e-7079, e-7097); Evan Newman is bar staff then. The page's line therefore tells Sean first. In October 1998 Evan leads the Anchor (derived: e-7097).
- **Peter Lane** owns the Old Bank Café in 1989 (derived from e-6908) and is at the café from 10:00 to 18:00. He lives at C, so "Peter first" costs the walk to the square.
- Olive's work at the Anchor is **derived** (e-8736, "after ten years"; no hire event).
- Peter Lane has left the town by October 1998 (derived), so seed B has no "Peter first".

## The rule (authored, one principle)

**A person tells what they know to the closest person they can reach.**
- **Closeness** between two people is 3 for kin (parents and children, simulated), 3 for partners at the month (the export's partner with its date, simulated; or a split, divorce or couple event that dates the pair, derived), 1 for coworkers at the month (derived), and the sum of the signs of their pair events up to the month (derived: friends, confide and keep +1; cold, coolto, dislike and contempt −1). The export has no liking field; this is a reading of those events. A hearer is anyone with closeness above zero. A stranger is nobody's hearer.
- **Reach:** two people at the same place, or two people who are both off work (they go round or ring).
- **The clock:** half an hour after hearing, and every half hour after that, each person tells their closest reachable hearer who has not heard (ties by id). Someone at the Anchor says it aloud instead: everyone there hears it, and so does anyone who comes in later. A person whose close hearers have all heard stops.
- **The player** tells one person at a time, 15 minutes a telling, walking at 1.4 m/s (55% of that on flights and steep lanes) over `heart_layout`'s lanes. Anyone who lives or works outside the corner is 10 minutes away. A line is an order of up to four tellings, back to back from 10:00.

## The score (the pick's rule)

For each visitor: the full share (40 of 80 on seed A) if they heard it from the player; half if they heard it from someone else outside the Anchor; nothing if they heard it at the Anchor, or not at all. Minus 5 for every other person who has heard it before 18:00, however they heard. Minus 10 for each private act said aloud (not exercised by test 1: the player says only the death). Pass at 60 of 80.

## The hours and homes (authored)

- Workers are at their place 09:00 to 17:00; the café is open 10:00 to 18:00 and its people are there then. The Anchor's lead is in from 11:00, its staff from 12:00, both until closing.
- Everyone whose habits take them to the Anchor on a Friday evening (derived: "at the Anchor every Friday" or "two pints at the Anchor most evenings", running at the month) is there from 18:00.
- Everyone else is at home. The corner's homes are in the block; anyone else lives outside the corner.
- The Anchor stands provisionally in Harbour Row 22, the Row house that holds the old blockout's Anchor; W3 casts it.
- The sightings: Hannah climbs to E every Wednesday at 16:30; Olive comes along the Row from the Anchor at 15:30 on the first and third of the three Wednesdays. From the window at A both climbs are in view (test 2a checks this); from the Row only Olive turning up the steps; from the Anchor's door nobody at E. Seed B mirrors it on September's three Wednesdays: Trevor and Ben every week, Oliver on the first and third; Ben and Oliver come along the Row.

## The hold-out for test 4

**Ellie Holmes, who dies in June 1992 (e-7261).** Øystein has read her only in passing lines, and no pitch or plan builds on her. She is kept out of every ladder report, and her case's config is written at test 4. Its limit: her death is sudden and her son John is on the page, so she has neither the long illness nor the private visitors of seed A. She tests the reading of ties and the order of tellings, not the steps' clue.

## The pre-mortem's fixes, and where each lands

- **Must 1:** the hold-out above.
- **Must 3:** `ties.py` reports tie counts first, runs its toy cases (`tools/tests/test_ties.py`) before it referees, and sweeps every authored hour an hour either side as well as every rule value at ½ and 1½ times. A fail caused by thin ties goes to Øystein as an engine question.
- **Should:** rosters are parsed from text, with tests, and labelled derived; 2a adds the birch at (44.5, 28.0), the stone walls and A's real windows, and is checked against a 2b still.
- **Stories 1 and 2:** the stills' limits are 2b's; the export's thinness and the hours are test 1's, reported with every result.

## The frozen block

Times are minutes after midnight on the Friday. Places are the export's ids; people are ids.

```json
{
 "rule": {"w_kin": 3, "w_partner": 3, "w_cowork": 1, "w_like": 1, "tau": 30, "tell": 15, "elsewhere": 10,
          "speed": 1.4, "flight": 0.55, "max_tellings": 4},
 "score": {"points": 80, "spread_share": 0.5, "leak": 5, "exposure": 10, "pass": 60},
 "hours": {"day": [600, 1080], "deadline": 1080, "work": [540, 1020], "place_hours": {"pl-cafe13": [600, 1080]},
           "bar_lead": 660, "bar_staff": 720, "regulars": 1080},
 "anchor_habits": ["at the Anchor every Friday", "two pints at the Anchor most evenings"],
 "sweep": {"rule": ["tau", "tell", "elsewhere", "w_kin", "w_partner", "w_cowork", "w_like"],
           "hours": ["work", "place_hours", "bar_lead", "bar_staff", "regulars"]},
 "points": {"A": "A", "B": "B", "C": "C", "E": "E", "row22": "Harbour Row 22", "row23": "Harbour Row 23",
            "ltd9": "Low Terrace down 9", "ltu18": "Low Terrace up 18", "htu21": "High Terrace up 21",
            "cafe": [384.0, -138.6]},
 "place_points": {"pl-bar": "row22", "pl-cafe13": "cafe"},
 "vantages": ["window", "row", "anchor"],
 "seeds": {
  "A": {"month": [1989, 12], "death": "e-6557", "day": "15 December 1989", "dead": "p-36",
        "visitors": ["p-2", "p-37"], "page": "p-31", "peter": "p-41", "player_home": "A",
        "homes": {"p-99": "A", "p-55": "B", "p-63": "C", "p-41": "C", "p-17": "ltd9", "p-2": "ltu18",
                  "p-4": "htu21", "p-37": "row23"},
        "evenings": [{"date": "15 November 1989", "sightings": {"window": ["p-2", "p-37"], "row": ["p-37"], "anchor": []}},
                     {"date": "22 November 1989", "sightings": {"window": ["p-2"], "row": [], "anchor": []}},
                     {"date": "29 November 1989", "sightings": {"window": ["p-2", "p-37"], "row": ["p-37"], "anchor": []}}]},
  "B": {"month": [1998, 10], "death": "e-8899", "day": "16 October 1998", "dead": "p-17",
        "visitors": ["p-38", "p-72", "p-55"], "page": "p-81", "peter": null, "player_home": "A",
        "homes": {"p-99": "A", "p-55": "B", "p-63": "C", "p-2": "ltu18", "p-4": "htu21", "p-37": "row23",
                  "p-72": "row23", "p-17": "ltd9"},
        "evenings": [{"date": "9 September 1998", "sightings": {"window": ["p-38", "p-72", "p-55"], "row": ["p-72", "p-55"], "anchor": []}},
                     {"date": "16 September 1998", "sightings": {"window": ["p-38", "p-72"], "row": ["p-72"], "anchor": []}},
                     {"date": "23 September 1998", "sightings": {"window": ["p-38", "p-72", "p-55"], "row": ["p-72", "p-55"], "anchor": []}}]}
 }
}
```
