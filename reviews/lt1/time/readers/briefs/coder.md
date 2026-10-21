# Coding claims against a record

You are coding short claims that readers made about five houses (A to E) on a lane in a harbour town, against the town's record for those houses. You do not know who made each claim or what they were shown, and you do not need to.

Read only the files in your folder: {FOLDER}. Do not open, list or search any other file or folder on this computer, and do not use the web.

Files:
- `record.json`: for each house, every dated event (`id`, `year`, what happened, its cause), and for each pair of years (1989-2000, 2000-2010, 2010-2020) the ids of the events that fall between them.
- `claims.json`: the claims. Each has a `cid`, the `house` it is about, the `pair` of years it is said to fall between (or none: a claim about the house's whole life), the claim's `text` and the reader's `confidence`.

For every claim, give one code:
- `fact`: the record holds what the claim says (for a claim with a pair, the event falls between those years). List the event ids it matches.
- `fair`: a fair reading of facts in the record that the record does not state in so many words (for example, "the shop did not do well" where a shop closed). List the event ids it rests on.
- `texture`: a claim about the house's history that the record does not hold at all (for example, "the roof was replaced" when no event touches the roof, or "an extension was added" when none was). These are false histories.
- `contradiction`: a claim the record contradicts (for example, "boarded up in 2000" for a house the record has lived in and kept then; or the right change put on the wrong house or between the wrong years).
- `vague`: no history to check ("it looks old", "it is a nice house"), or only a statement about the present look.

Be strict and literal: a change named for the wrong house, or between the wrong pair of years, is a `contradiction`, not a `fact`. Repaints are in the record; the readers may not have been able to see colour, so a claim of a repaint is coded like any other.

Answer with one JSON block, and nothing after it:

```json
[{"cid": "c0001", "code": "fact", "matches": ["A7"]}, {"cid": "c0002", "code": "texture", "matches": []}]
```
