# Part 2: the views

Your folder also holds views of the same five houses:
- `frames/<view>-<code>-whole.png`: a whole view, at half size;
- `frames/<view>-<code>-tile1.png` to `tile4.png`: its four quarters (top left, top right, bottom left, bottom right) at the size a player sees them on screen;
- `locator-city.png`, `locator-12m.png`, `locator-street.png`, `locator-eye.png`: views with the five houses lettered (only the letters are added).

There are four views: `eye` (standing on the quay road), `street` (on the steps, a little above head height), `12m` (12 metres up over the foot of the steps) and `city` (high above). Here are the years of the frames:

{REVEAL}

Look at the locators, then at every frame: the whole view and all four tiles.

**Task 6.**
- `told_more`: which helped you understand what happened to these houses better, the views or the record? Answer `views`, `record` or `same`, and say why.
- `contradicts`: list anything the views show that the record contradicts or does not hold, with your confidence.
- `views_showed`: what did the views make clear that the record does not make obvious, if anything?
- `missing`: what in the record could you not see in the views?

Answer with one JSON block, and nothing after it:

```json
{"told_more": ["record", "..."], "contradicts": [{"claim": "...", "confidence": 2}], "views_showed": ["..."], "missing": ["..."]}
```
