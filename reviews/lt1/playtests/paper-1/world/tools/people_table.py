"""The atlas's people table for world 9989, re-dated: one row per person in town at some time 1989-1999.
Usage: python3 -I people_table.py [in|out]   in: everyone in town at some time 1989-1999; out: the rest"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w9989 as w  # noqa: E402

PLACE = {"the sawmill": "sawmill", "the harbour fleet": "fleet", "the garage": "garage", "the clinic": "clinic",
         "the school": "school", "the Courier": "Courier", "the Anchor": "Anchor", "the council office": "council",
         "the Old Bank Café": "café"}
PID = {"pl-mill": "sawmill", "pl-harbour": "fleet", "pl-garage": "garage", "pl-clinic": "clinic", "pl-school": "school",
       "pl-paper": "Courier", "pl-bar": "Anchor", "pl-council": "council", "pl-cafe13": "café"}
HAB = {"is at the Anchor every Friday without fail": "Fri Anchor", "plays cards at the Anchor on Tuesdays": "Tue cards",
       "sings with the choir every Thursday": "Thu choir", "walks the shore every evening": "shore walk",
       "reads late into every night": "reads late", "is out in the garden every morning from spring to autumn": "garden",
       "spends every spare hour fixing something in the shed": "shed", "has two pints at the Anchor most evenings": "2 pints",
       "swims in the harbour every morning, whatever the weather": "swims 7am", "runs the coast road every other day": "coast run",
       "is first in at work every morning": "first in", "practises every night after the house has gone quiet": "practises",
       "has Sunday dinner with the family every week": "Sun dinner", "is out on the boat every weekend": "boat wkends",
       "rings their mother every Sunday evening": "rings mother"}
ROLE = {"head mechanic": "head mech.", "owner": "owner", "manager": "manager", "chief officer": "chief officer"}


def place_of(text):
    for k, v in PLACE.items():
        if k in text:
            return v
    return None


def work(p):
    pid = p["id"]
    moves, first = [], None
    for e in w.events_of(pid):
        t, y = w.rd(e["text"]), w.ty(e["at"])
        if e["type"] == "dismiss" and e["who"][0] != pid and pid in e["who"]:
            first = first or place_of(t)
            moves.append(f"let go {y}")
        elif e["type"] == "dismiss":
            continue
        elif e["type"] == "arrived":
            if e["who"][0] == pid:
                first = first or "arrives"
                moves.append(f"{place_of(t)} {y}")
            else:
                first = first or "arrives"
                moves.append(f"with {w.NAME[e['who'][0]]} {y}")
        elif e["type"] == "hired":
            moves.append(f"{place_of(t)} {y}")
        elif e["type"] == "moved":
            m = re.search(r"left the (.+?) for a start at the (.+?)\.", t)
            first = first or PLACE.get("the " + m[1])
            moves.append(f"{PLACE.get('the ' + m[2])} {y}")
        elif e["type"] == "startover":
            first = first or place_of(t)
            moves.append(f"out {y}")
        elif e["type"] == "retired":
            first = first or place_of(t)
            moves.append(f"retired {y}")
        elif e["type"] == "promoted":
            m = re.search(r"became (.+?) at", t)
            first = first or place_of(t)
            moves.append(f"{ROLE.get(m[1], m[1])} {y}")
        elif e["type"] == "left":
            moves.append(f"to the city {y}" if "university" not in t else f"university {y}")
        elif e["type"] == "home":
            moves.append(f"home {y}")
    j = p["job"]
    if not first and j and w.ty(j["since"]) <= 1989:
        first = PID[j["place"]] + (" (lead)" if j["lead"] and not any("owner" in m or "mech" in m or "manager" in m or "chief" in m for m in moves) else "")
    if not first:
        first = "retired" if p["retired"] else ("child" if w.ty(p["born"]) > 1971 else "–")
    if first in ("retired", "child", "–") and moves and moves[0].split()[0] in PID.values():
        first = "–"
    s = first + ("; " + ", ".join(moves) if moves else "")
    return s


def habits(p):
    out = []
    for h in p["habits"]:
        s, b = w.ty(h["since"]), w.ty(h.get("broken"))
        if b and b < 1989:
            continue
        out.append(f"{HAB[h['label']]} {s}–{str(b)[2:] if b else ''}")
    for a in p["attachments"]:
        if a["key"] != "home":
            out.append(f"{a['key']} {w.ty(a['since'])}")
    return "; ".join(out)


def kin(p):
    par = ", ".join(w.NAME[x] for x in p["parents"])
    kids = ", ".join(w.NAME[x] for x in p["kids"])
    return (f"of {par}" if par else "") + (" · " if par and kids else "") + (f"kids {kids}" if kids else "")


def partner(p):
    pa = p["partner"]
    if not pa:
        return ""
    since = w.ty(pa.get("since")) if pa.get("since") else ""
    return f"{w.NAME[pa['id']]} ({'m.' if pa['kind'] == 'married' else 'dating '}{since})"


def where(p):
    if p["status"] == "dead":
        return f"d. {w.tm(p['died'])}"
    if p["status"] == "away":
        return f"away {w.ty(p['away']['since'])} ({p['away']['kind']})"
    return "in"


def row(p):
    gs = BANDS.get(p["id"], [])
    return (f"| {p['id'][2:]} | {p['name']} | {p['sex']} | {w.ty(p['born'])} | {where(p)} | {work(p)} | {partner(p)} | "
            f"{kin(p)} | {hh(p['id'])} | {', '.join(gs)} | {habits(p)} |")


# Band members over the run, from the group: events (the export's member lists are the state in January 1999
# and lose Driftwood's members at its split, e-8374)
BANDS = {"p-21": ["Night Shift 77–"], "p-72": ["Night Shift"], "p-24": ["Night Shift"], "p-52": ["Night Shift 89–"],
         "p-55": ["Sawmill Boys 73–74", "Driftwood 90–96", "Pirate Radio 98–"], "p-41": ["Driftwood 90–94"],
         "p-17": ["Driftwood 90–96", "Pirate Radio 98"], "p-19": ["Driftwood 91–96"], "p-80": ["Driftwood 96"],
         "p-64": ["Pirate Radio 98–"], "p-31": ["Pirate Radio 98–"]}


def hh(pid):
    for h in w.D["households"]:
        if pid in h["members"] or pid in h["children"]:
            return h["id"][2:]
    shared = [h["id"][2:] for h in w.D["households"] if pid in h["childrenShared"]]
    return "/".join(shared)


def in_decade(p):
    if p["status"] == "dead":
        return w.ty(p["died"]) >= 1989
    if p["status"] == "away":
        return any(e["type"] in ("left",) for e in w.events_of(p["id"]))
    return True


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "in"
    print("| id | name | sex | born | 1999 | work 1989 → moves | partner | parents · kids | hh | band | habits (since–broken), things |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for p in w.D["people"]:
        if (which == "in") == in_decade(p):
            print(row(p))
