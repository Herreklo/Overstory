# Engine contract (draft)

The data the game reads from the engine. The engine owns the contract (EC1): its front door (`src/boundary.ts`) publishes a version, a schema and fixtures exported from real seeds, and Overstory pins to a version. This page is Overstory's side of it: what our experiments read, in the shape our fixtures use until the front door's second part (#22) lands. Keep it to what experiments actually use; add fields only when an experiment needs them, and list each new field in `engine-requests.md`.

## In short

- **EC1** The engine owns the contract: its front door publishes a version, a schema and fixtures, and Overstory pins a version. This page holds only what experiments read; a new field is added only when one needs it, and is listed in `engine-requests.md`. Evidence: the opening. Reopens: #22 landing.
- **EC2** Ids are strings typed by prefix, never reused or changed. Time is absolute (calendar year and month). Things that last carry `from` and `to` (`null` while current), and nothing starts after the snapshot's `at`. Buildings and businesses are separate. Lengths are in millimetres, amounts per mille. Evidence: Rules. Reopens: none named.
- **D3.3** Every record carries its provenance in four values, `simulated`, `generated-past`, `derived` or `authored`, at `schemaVersion` 2 (disputed). Evidence: `building-blocks-decisions.md` §4; `schemas/record.schema.json`. Reopens: none named.
- **EC3** Everything here is a fact the game may not contradict; it may elaborate it, never invent history. Evidence: Rules. Reopens: none named.

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
      "provenance": "authored",
      "events": [
        { "id": "bld-101/1", "year": 1893, "kind": "built", "params": { "era": "chalet", "storeys": 2000, "wealth": 850 }, "cause": "a herring merchant builds his house", "provenance": "authored" },
        { "id": "bld-101/13", "year": 1988, "kind": "business_opened", "params": { "business": "anchor", "kind": "bar", "name": "the Anchor" }, "cause": "Ruth opens a bar", "provenance": "authored" }
      ]
    }
  ],
  "businesses": [
    { "id": "anchor", "kind": "bar", "building": "bld-101", "from": 1988, "to": null, "owner": "p-812", "state": "struggling", "provenance": "authored" },
    { "id": "mos", "kind": "cafe", "building": "bld-101", "from": 1975, "to": 1986, "provenance": "authored" }
  ],
  "people": [
    { "id": "p-812", "name": "Ruth Hale", "born": 1931, "at": "anchor", "provenance": "authored" }
  ]
}
```

## Rules

- **Ids are strings, typed by prefix** (EC2), never reused and never changed. The engine's place ids are already strings (`'mill'`, `'harbour'`); buildings, plots, businesses, people and events follow the same rule.
- **Time is absolute.** `at` gives the calendar year and month of the snapshot. Every dated field is a calendar year (and month where it matters), never an engine-internal month index.
- **Validity intervals.** Things that exist for a time carry `from` and `to` (`to: null` while current). Nothing in a snapshot may start after the snapshot's `at`; a fixture that breaks this fails validation.
- **Buildings and businesses are separate.** A building is a physical thing with a diary; a business occupies a building for an interval.
- **Provenance on every record** (D3.3): `simulated` (decided by the engine), `authored` (written by hand for an experiment, for anything the engine does not model yet) or `generated-past` (written by the fabric pass, before the people begin). The game draws all three the same way; tests and tools can tell them apart.
- **Lengths in millimetres, chances and amounts per mille,** as in the resolver.
- **Everything here is a fact the game may not contradict** (EC3). The game may elaborate it visually, but may not invent history.
