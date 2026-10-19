# Engine contract (draft)

The data the game reads from the engine. A draft: the engine does not export it yet, so fixtures in `fixtures/` follow it. Keep it to what experiments actually use; add fields only when an experiment needs them, and list each new field in `engine-requests.md`.

## A neighbourhood snapshot

```json
{
  "worldSeed": 1234,
  "month": 372,
  "neighbourhood": { "id": 7, "name": "Harbour Row" },
  "buildings": [
    {
      "id": 101,
      "version": 3,
      "footprint": { "x": 0, "y": 0, "w": 3, "d": 2 },
      "storeys": 2,
      "built": 1931,
      "extensions": [{ "year": 1978, "side": "back", "storeys": 1 }],
      "condition": 0.4,
      "business": {
        "id": 55,
        "kind": "bar",
        "name": "the Anchor",
        "owner": 812,
        "opened": 2031,
        "state": "struggling"
      },
      "past": [{ "kind": "cafe", "name": "Mo's", "from": 2012, "to": 2029 }]
    }
  ],
  "people": [
    { "id": 812, "name": "Ruth Hale", "age": 58, "at": 101, "mood": -0.3 }
  ]
}
```

## Rules

- Ids never change and are never reused.
- `version` increases whenever the building's look should change (a new business, a renovation, an extension, a closure).
- `condition` runs from 0 (falling apart) to 1 (as new).
- Everything here is a fact the engine decided. The game may not fill a gap with its own invention, except in fixtures, where each such field is marked in `engine-requests.md`.
