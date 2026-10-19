# Engine contract (draft)

The data the game reads from the engine. A draft: the engine does not export it yet, so fixtures in `fixtures/` follow it. Keep it to what experiments actually use; add fields only when an experiment needs them, and list each new field in `engine-requests.md`.

## A neighbourhood snapshot

```json
{
  "schemaVersion": 1,
  "rulesetVersion": "fixture",
  "worldSeed": 1989,
  "at": { "year": 1989, "month": 10 },
  "neighbourhood": { "id": "harbour-row", "name": "Harbour Row" },
  "buildings": [
    {
      "id": "bld-101",
      "plot": "plot-101",
      "provenance": "scenario-authored",
      "events": [
        { "id": "bld-101/1", "year": 1893, "kind": "built", "params": { "era": "chalet", "storeys": 2000, "wealth": 850 }, "cause": "a herring merchant builds his house", "provenance": "scenario-authored" },
        { "id": "bld-101/13", "year": 1988, "kind": "business_opened", "params": { "business": "anchor", "kind": "bar", "name": "the Anchor" }, "cause": "Ruth opens a bar", "provenance": "scenario-authored" }
      ]
    }
  ],
  "businesses": [
    { "id": "anchor", "kind": "bar", "building": "bld-101", "from": 1988, "to": null, "owner": "p-812", "state": "struggling", "provenance": "scenario-authored" },
    { "id": "mos", "kind": "cafe", "building": "bld-101", "from": 1975, "to": 1986, "provenance": "scenario-authored" }
  ],
  "people": [
    { "id": "p-812", "name": "Ruth Hale", "born": 1931, "at": "anchor", "provenance": "scenario-authored" }
  ]
}
```

## Rules

- **Ids are strings, typed by prefix,** never reused and never changed. The engine's place ids are already strings (`'mill'`, `'harbour'`); buildings, plots, businesses, people and events follow the same rule.
- **Time is absolute.** `at` gives the calendar year and month of the snapshot. Every dated field is a calendar year (and month where it matters), never an engine-internal month index.
- **Validity intervals.** Things that exist for a time carry `from` and `to` (`to: null` while current). Nothing in a snapshot may start after the snapshot's `at`; a fixture that breaks this fails validation.
- **Buildings and businesses are separate.** A building is a physical thing with a diary; a business occupies a building for an interval.
- **Provenance on every record:** `historical` (from real sources), `scenario-authored` (hand-written for an experiment), or `simulated` (decided by the engine). The game draws all three the same way; tests and tools can tell them apart.
- **Lengths in millimetres, chances and amounts per mille,** as in the resolver.
- **Everything here is a fact the game may not contradict.** The game may elaborate it visually, but may not invent history.
