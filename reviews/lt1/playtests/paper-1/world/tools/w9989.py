"""Read-only helpers over world 9989 for the game masters' atlas.

Usage: python3 w9989.py <command> [args]
  person <id|name>      the person, re-dated, with every event they are in
  jobs <id|name>        their work moves in the run, and the job held in January 1999
  events <type>         every event of a type
  year <town year>      public and local notable events of that town year
  find <text>           events whose text contains <text>
  chain <event id>      the event and its cause tree, back through event causes

Re-dating: town year = engine year - 37. Engine 2026-2036 is the town's 1989-1999.
The export's reads are the truth, never what a player could know.
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 6))
RUN = os.path.join(ROOT, "fixtures", "engine", "understory-world-9989.json")
SHIFT = -37

D = json.load(open(RUN))
P = {p["id"]: p for p in D["people"]}
E = {e["id"]: e for e in D["events"]}
PL = {p["id"]: p for p in D["places"]}
NAME = {p["id"]: p["name"] for p in D["people"]}
BYNAME = {p["name"].lower(): p["id"] for p in D["people"]}


def ty(at):
    """Town year of an engine date."""
    return at["year"] + SHIFT if at else None


def tm(at):
    """Town date as YYYY-MM."""
    return f"{at['year'] + SHIFT}-{at['month']:02d}" if at else ""


import re

_YEAR = re.compile(r"\b(19\d\d|20[0-4]\d)\b")


def rd(text):
    """Re-date every engine year written in a line ("since 2014" -> "since 1977")."""
    return _YEAR.sub(lambda m: str(int(m.group(1)) + SHIFT), text)


def events_of(pid):
    return [e for e in D["events"] if pid in e["who"]]


def household_of(pid):
    for h in D["households"]:
        if pid in h["members"] or pid in h.get("children", []):
            return h["id"]
    return None


def fmt_event(e, causes=True):
    s = f"{e['id']} {tm(e['at'])} [{e['type']}|{e['vis']}|{e['notability']}] {rd(e['text'])}"
    if causes and e["causes"]:
        cs = "; ".join(
            f"{c['kind']}:{rd(c['label'])}({c['weight']})" + (f"->{c['event']}" if c.get("event") else "")
            for c in e["causes"]
        )
        s += f"\n      <- {cs}"
    return s


def resolve(arg):
    if arg in P:
        return arg
    return BYNAME[arg.lower()]


def cmd_person(arg):
    pid = resolve(arg)
    p = P[pid]
    print(json.dumps(p, indent=1))
    print("household:", household_of(pid))
    for e in events_of(pid):
        print(fmt_event(e))


def cmd_events(t):
    for e in D["events"]:
        if e["type"] == t:
            print(fmt_event(e))


def cmd_year(y):
    y = int(y)
    for e in D["events"]:
        if ty(e["at"]) == y and e["vis"] in ("public", "local") and e["notability"] >= 900:
            print(fmt_event(e, causes=False))


def cmd_find(text):
    for e in D["events"]:
        if text.lower() in e["text"].lower():
            print(fmt_event(e))


def cmd_chain(eid, depth=0, seen=None):
    seen = seen or set()
    if eid in seen or eid not in E:
        if eid not in E:
            print("  " * depth + f"{eid} (before the export)")
        return
    seen.add(eid)
    print("  " * depth + fmt_event(E[eid], causes=False))
    for c in E[eid]["causes"]:
        if c.get("event"):
            cmd_chain(c["event"], depth + 1, seen)


WORKTYPES = ("hired", "moved", "arrived", "startover", "retired", "dismiss", "promoted", "left", "home", "take", "stepdown")


def jobs(pid):
    """Work moves in the run, re-dated, plus the job held at the export (January 1999)."""
    out = []
    for e in events_of(pid):
        if e["type"] in WORKTYPES or (e["type"] == "dismiss" and pid in e["who"]):
            out.append(f"{tm(e['at'])} {rd(e['text'])} ({e['id']})")
    j = P[pid]["job"]
    if j:
        out.append(f"at export: {PL[j['place']]['name']}{' (lead)' if j['lead'] else ''} since {tm(j['since'])}")
    return out


def cmd_jobs(arg):
    for line in jobs(resolve(arg)):
        print(line)


if __name__ == "__main__":
    cmd, *args = sys.argv[1:]
    {"person": cmd_person, "events": cmd_events, "year": cmd_year, "find": cmd_find, "chain": cmd_chain, "jobs": cmd_jobs}[cmd](
        " ".join(args)
    )
