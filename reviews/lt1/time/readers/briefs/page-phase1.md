# Part 1: the record

Your folder holds `page.md`: the town's record for these five houses, every dated event with its cause. Read it.

Then answer Tasks 2 to 5 below from the record, as if you were looking at the houses in 1989, 2000, 2010 and 2020.

**Task 2.** For each house (A to E) in each year (1989, 2000, 2010, 2020), say what each part of it is:
- `roof`, `upper windows`, `ground floor` (its windows, doors or shopfront at street level, on any wall), `additions` (porches, bays, dormers, lean-tos, balconies and the like): one of `original` (as the house was built), `changed` (altered, replaced or added later), `neglected` (let go, damaged, boarded), `none` (the house has none) or `unsure`;
- `care`, the house as a whole: `kept`, `neglected` or `unsure`.

**Task 3.** For each pair of years (1989 to 2000, 2000 to 2010, 2010 to 2020), list what changed on the five houses that someone looking at them would see: one short claim each, with the house, what changed, why, and your confidence.

**Task 4.** For each house, what happened to it? Give two to six short claims, each one statement, with a confidence.

**Task 5.** Between each pair of years, did the corner grow `busier`, `quieter` or stay the `same`; and was it `better kept`, `worse kept` or the `same`?

Answer with one JSON block, and nothing after it, in this form (the angle brackets stand for your answers; confidences as plain numbers):

```json
{"parts": {"A": {"1989": {"roof": ["<state>", <confidence>], "upper windows": ["<state>", <confidence>], "ground floor": ["<state>", <confidence>], "additions": ["<state>", <confidence>], "care": ["<kept, neglected or unsure>", <confidence>]}, "2000": {...}, "2010": {...}, "2020": {...}}, "B": {...}, "C": {...}, "D": {...}, "E": {...}},
 "changes": {"1989-2000": [{"house": "<letter>", "what": "...", "why": "...", "confidence": <1 to 3>}], "2000-2010": [...], "2010-2020": [...]},
 "stories": {"A": [{"claim": "...", "confidence": <1 to 3>}], "B": [...], "C": [...], "D": [...], "E": [...]},
 "direction": {"1989-2000": {"activity": "<busier, quieter or same>", "care": "<better kept, worse kept or same>"}, "2000-2010": {...}, "2010-2020": {...}}}
```
