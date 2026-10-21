"""Causal chains in world 9989: connected groups of events linked by event causes (within the export).
Usage: python3 -I chains.py [min_size]   prints each chain's size, kinds, people, span and ids, richest first."""
import os
import collections
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w9989 as w  # noqa: E402

adj = collections.defaultdict(set)
for e in w.D["events"]:
    for c in e["causes"]:
        t = c.get("event")
        if t and t in w.E:
            adj[e["id"]].add(t)
            adj[t].add(e["id"])
seen, groups = set(), []
for e in w.D["events"]:
    if e["id"] in seen or e["id"] not in adj:
        continue
    stack, comp = [e["id"]], []
    while stack:
        x = stack.pop()
        if x in seen:
            continue
        seen.add(x)
        comp.append(x)
        stack.extend(adj[x] - seen)
    groups.append(comp)


def score(comp):
    evs = [w.E[i] for i in comp]
    kinds = {e["type"] for e in evs}
    people = {p for e in evs for p in e["who"]}
    years = {w.ty(e["at"]) for e in evs}
    return len(kinds) * 3 + len(people) + len(years) * 2 + sum(e["notability"] for e in evs) / 1000


if __name__ == "__main__":
    mn = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    for comp in sorted(groups, key=score, reverse=True):
        if len(comp) < mn:
            continue
        evs = sorted((w.E[i] for i in comp), key=lambda e: (e["at"]["year"], e["at"]["month"]))
        people = collections.Counter(p for e in evs for p in e["who"])
        print(f"== {len(comp)} events, {len({e['type'] for e in evs})} kinds, {w.tm(evs[0]['at'])}..{w.tm(evs[-1]['at'])}, score {score(comp):.0f}")
        print("   people:", ", ".join(f"{w.NAME[p]}({n})" for p, n in people.most_common(8)))
        for e in evs:
            print("   ", e["id"], w.tm(e["at"]), e["type"], e["vis"][:3], w.rd(e["text"])[:110])
