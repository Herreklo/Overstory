"""Check atlas-9989.md: every cited event id exists, and every "Name (p-N" pairs the right name with its id.
Usage: python3 -I check_atlas.py"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w9989 as w  # noqa: E402

text = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "atlas-9989.md")).read()
ids = set(re.findall(r"\be-\d{4}\b", text))
print("event ids cited:", len(ids), "missing:", sorted(i for i in ids if i not in w.E))
bad = [(n, p) for n, p in re.findall(r"\*?\*?([A-Z][a-z]+ [A-Z][a-z]+)\*?\*? \((p-\d+)", text) if w.NAME.get(p) != n]
print("name/id mismatches:", bad)
