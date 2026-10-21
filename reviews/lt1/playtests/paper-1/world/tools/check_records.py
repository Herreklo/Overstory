"""Check records-9989.md: every cited event id exists, written weekdays are right,
and each record's cited events are not later than the record's date (allowing GM notes).
Usage: python3 -I check_records.py"""
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w9989 as w

path = os.path.join(os.path.dirname(__file__), "..", "records-9989.md")
text = open(path).read()
ids = set(re.findall(r"\be-\d{4}\b", text))
missing = sorted(i for i in ids if i not in w.E)
print("cited ids:", len(ids), "missing:", missing)
# ranges like e-7769 to e-7777
for a, b in re.findall(r"(e-\d{4}) to (e-\d{4})", text):
    for n in range(int(a[2:]), int(b[2:]) + 1):
        pass
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                       "September", "October", "November", "December"], 1)}
bad = []
for wd, d, mon, y in re.findall(r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday) (\d{1,2}) (\w+) (\d{4})", text):
    real = datetime.date(int(y), MONTHS[mon], int(d)).strftime("%A")
    if real != wd:
        bad.append((wd, d, mon, y, real))
print("weekday errors:", bad)
# per record: events dated after the record (outside GM notes)
for block in re.split(r"\n(?=### |\*\*A-)", text):
    head = block.split("\n", 1)[0]
    m = re.search(r"(\w+) (\d{4})", head)
    rid = re.search(r"([CPAD]-\d\d)", head)
    if not rid:
        continue
    dm = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December) (\d{4})", head)
    if not dm:
        continue
    rec = (int(dm.group(2)), MONTHS[dm.group(1)])
    body = "\n".join(l for l in block.split("\n") if not l.startswith(">"))
    later = []
    for i in set(re.findall(r"\be-\d{4}\b", body)):
        e = w.E.get(i)
        if e and (e["at"]["year"] - 37, e["at"]["month"]) > rec:
            later.append(f"{i}@{w.tm(e['at'])}")
    if later:
        print(rid.group(1), head[:60], "-> later events outside GM note:", sorted(later))
