# Part 2: what happened to the houses

Here are the years of the frames:

{REVEAL}

Look again at the frames as you need, now with their years.

**Task 2.** For each house (A to E) in each year, say what each part of it is, from what you can see:
- `roof`, `upper windows`, `ground floor` (its windows, doors or shopfront at street level, on any wall), `additions` (porches, bays, dormers, lean-tos, balconies and the like): one of `original` (as the house was built), `changed` (altered, replaced or added later), `neglected` (let go, damaged, boarded), `none` (the house has none) or `unsure`;
- `care`, the house as a whole: `kept`, `neglected` or `unsure`.

**Task 3.** For each pair of years (1989 to 2000, 2000 to 2010, 2010 to 2020), list what changed on the five houses: one short claim each, with the house, what changed, why you think it changed if you can tell, and your confidence. List only what you see change.

**Task 4.** For each house, what happened to it? Give two to six short claims, each one statement, with a confidence. Include what you read about its life before 1989 if you can.

**Task 5.** Between each pair of years, did the corner grow `busier`, `quieter` or stay the `same`; and was it `better kept`, `worse kept` or the `same`?

Answer with one JSON block, and nothing after it:

```json
{"parts": {"A": {"1989": {"roof": ["original", 2], "upper windows": ["original", 2], "ground floor": ["changed", 3], "additions": ["none", 1], "care": ["kept", 2]}, "2000": {...}, "2010": {...}, "2020": {...}}, "B": {...}, "C": {...}, "D": {...}, "E": {...}},
 "changes": {"1989-2000": [{"house": "A", "what": "...", "why": "...", "confidence": 2}], "2000-2010": [...], "2010-2020": [...]},
 "stories": {"A": [{"claim": "...", "confidence": 2}], "B": [...], "C": [...], "D": [...], "E": [...]},
 "direction": {"1989-2000": {"activity": "busier", "care": "worse kept"}, "2000-2010": {...}, "2010-2020": {...}}}
```
