"""Assemble atlas-9989.md from its hand-written parts and the generated tables (people_table.py, yearly.py).
Usage: python3 -I build_atlas.py <parts dir>   (the hand-written parts atlas_head.md, arcs_short.md, atlas_story.md and
atlas_tail.md were kept outside the repo; after the first build, atlas-9989.md itself is the source to edit)"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
parts = sys.argv[1]
run = lambda *a: subprocess.run([sys.executable, "-I", os.path.join(HERE, a[0]), *a[1:]], capture_output=True, text=True, check=True).stdout

people = run("people_table.py", "in")
fixes = {
    "| café; retired 1992, to the city 1994 |": "| café (owner); steps down 1992, to the city 1994 |",
    "| –; to the city 1996, Courier 1998 |": "| sawmill? (by coworker links only); to the city 1996 to 1998, Courier 1998 |",
}
for a, b in fixes.items():
    assert a in people, a
    people = people.replace(a, b)


def strip_role(line):
    """'- **Name** (p-N, years; role): arc' -> '- **Name** (p-N): arc'; the table holds years and roles."""
    m = re.match(r"- \*\*(.+?)\*\* \(", line)
    if not m:
        return line
    i, depth = m.end() - 1, 0
    for j in range(i, len(line)):
        depth += {"(": 1, ")": -1}.get(line[j], 0)
        if depth == 0:
            break
    pid = re.match(r"\((p-\d+)", line[i:]).group(1)
    return f"- **{m.group(1)}** ({pid}){line[j + 1:]}"


arcs_file = os.path.join(parts, "arcs_short.md")
if not os.path.exists(arcs_file):
    arcs_file = os.path.join(parts, "arcs.md")
arcs = [strip_role(l) for l in open(arcs_file).read().splitlines() if l.strip()]
arcs = "\n".join(arcs)
for a, b in {"keeps Hannah Tanner's confidences four times (private)": "keeps Hannah Tanner's confidences three times (private)",
             "tells Ben Reed something nobody knew four times (private)": "tells Ben Reed something nobody knew three times (private)"}.items():
    arcs = arcs.replace(a, b)
assert "four times (private)" not in arcs

yearly = run("yearly.py").strip().replace(". (P ", " (P ").replace(". (L ", " (L ")
yearly += ("\n\n**1999 (January, where the run ends).** Neil Lyons walks out of the sawmill after the cover-up came out (L e-8982); "
           "Gary Myers takes the credit for Alex Myers's year, Evan Newman for Agnes Tanner's, Lily Lyons for Ellen Vaughan's "
           "(L e-9001 to e-9003); John Holmes no longer talks of a house of his own (L e-8990); Oliver Brook's \"A Window for "
           "Saturday\" does not come to much (L e-8995).")

head = open(os.path.join(parts, "atlas_head.md")).read().replace("{{PEOPLE_IN}}", people.strip())
out = (head.rstrip() + "\n\n## Arcs\n\nEveryone with five events or more (72), most events first: years, kin and work are in the "
       "table above. Truth level: (private) marks what no witness saw.\n\n" + arcs + "\n\n"
       + open(os.path.join(parts, "atlas_story.md")).read().rstrip() + "\n\n"
       "## What the town could know, 1989 to January 1999\n\nPublic (P) and notable local (L) events, month by month: "
       "deaths, illness, arrivals and departures, work, money spent, marriages, the festivals and harbour days, bands "
       "formed and split (their shows and the open nights are under Bands), what came out. A local event reaches partners, coworkers and, by chance, people whose work is with "
       "people; the rest of the town hears it only through them. Made by `tools/yearly.py` (public with notability 1,000 "
       "or more, local 1,400 or more, plus the storm, the findings-out and the old café's feud).\n\n" + yearly + "\n\n"
       + open(os.path.join(parts, "atlas_tail.md")).read().rstrip() + "\n")
dest = os.path.join(HERE, "..", "atlas-9989.md")
open(dest, "w").write(out)
print(dest, len(out.split()), "words")
