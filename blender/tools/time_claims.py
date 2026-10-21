"""The claims and the records for the blind coder (docs/experiments.md, LT1f).

    python3 blender/tools/time_claims.py [reviews/lt1/time/readers]

Gathers every free-text claim the readers made (tasks 3 and 4, and the misled list of task 6) from answers/, under
neutral ids in a shuffled order, with no reader, arm or role (claims/claims.json, for the coder), and keeps the
mapping apart (claims/claims-map.json, for the scorer). Writes the records the coder codes against
(claims/record-real.json and claims/record-shuffled.json): each house's dated events with ids such as A7, and the
ids that fall between each pair of years.
"""

import json
import os
import random
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
YEARS = (1989, 2000, 2010, 2020)


def record(diaries):
    out = {}
    for letter, d in diaries.items():
        evs = sorted(d["events"], key=lambda e: (e["year"], e["id"]))
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from time_key import event_words
        out[letter] = dict(
            events=[dict(id=f"{letter}{e['id']}", year=e["year"], what=event_words(e, d), cause=e.get("cause", "")) for e in evs],
            pairs={f"{a}-{b}": [f"{letter}{e['id']}" for e in evs if a < e["year"] <= b] for a, b in zip(YEARS, YEARS[1:])})
    return out


def main(argv):
    base = os.path.join(ROOT, argv[0] if argv else "reviews/lt1/time/readers")
    ds = json.load(open(os.path.join(base, "diaries.json")))
    os.makedirs(os.path.join(base, "claims"), exist_ok=True)
    for arm in ("real", "shuffled"):
        with open(os.path.join(base, "claims", f"record-{arm}.json"), "w") as f:
            json.dump(record(ds[arm]), f, indent=1, ensure_ascii=False)
    readers = json.load(open(os.path.join(base, "readers.json")))
    claims = []
    for r in readers:
        phase = "2" if r["arm"] in ("scene", "shuffled") else "1"
        a = json.load(open(os.path.join(base, "answers", f"{r['id']}-{phase}.json")))
        for pair, items in (a.get("changes") or {}).items():
            for it in items:
                text = it.get("what", "") + (f" (why: {it['why']})" if it.get("why") else "")
                claims.append(dict(reader=r["id"], task="changes", pair=pair, house=it.get("house"), text=text, confidence=it.get("confidence")))
        for house, items in (a.get("stories") or {}).items():
            for it in items:
                claims.append(dict(reader=r["id"], task="stories", pair=None, house=house, text=it.get("claim", ""), confidence=it.get("confidence")))
    rng = random.Random(1989)
    rng.shuffle(claims)
    for i, c in enumerate(claims):
        c["cid"] = f"c{i + 1:04d}"
    with open(os.path.join(base, "claims", "claims-map.json"), "w") as f:
        json.dump(claims, f, indent=1, ensure_ascii=False)
    with open(os.path.join(base, "claims", "claims.json"), "w") as f:
        json.dump([dict(cid=c["cid"], house=c["house"], pair=c["pair"], text=c["text"], confidence=c["confidence"]) for c in claims], f, indent=1, ensure_ascii=False)
    print(len(claims), "claims")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
