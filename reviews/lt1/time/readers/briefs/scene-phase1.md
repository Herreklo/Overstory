# Part 1: order the views

Your folder holds views of the town:
- `frames/<view>-<code>-whole.png`: a whole view, at half size;
- `frames/<view>-<code>-tile1.png` to `tile4.png`: its four quarters (top left, top right, bottom left, bottom right) at the size a player sees them on screen;
- `locator-city.png`, `locator-12m.png`, `locator-street.png`, `locator-eye.png`: views with the five houses lettered (only the letters are added).

There are four views: `eye` (standing on the quay road), `street` (on the steps, a little above head height), `12m` (12 metres up over the foot of the steps) and `city` (high above). For each view there are four frames, with codes W, X, Y and Z: the same place from exactly the same spot, in four different years. The codes are in a random order.

Look at the locators first. Then, for every frame, look at the whole view and then all four of its tiles.

**Task 1.** For each view, put its four frames in order from earliest to latest, and say in which year you think each was seen (to the nearest year you can; we score it to the decade). Say what told you, and how sure you are.

Answer with one JSON block, and nothing after it (the angle brackets stand for your answers; years as plain numbers):

```json
{"order": {"eye": {"sequence": ["<earliest code>", "<next>", "<next>", "<latest>"], "years": {"W": <year>, "X": <year>, "Y": <year>, "Z": <year>}, "confidence": <1 to 3>, "because": "..."},
           "street": {...}, "12m": {...}, "city": {...}}}
```
