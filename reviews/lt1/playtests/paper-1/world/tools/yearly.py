"""What the town could know, year by year: public and notable local events of world 9989, re-dated, short.
Usage: python3 -I yearly.py   (prints markdown, one paragraph per year)"""
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w9989 as w  # noqa: E402

MON = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
DROP = {"want:achieved", "seize", "stepdown", "shyaway", "group:work", "thread:cost", "stayfor", "sulk", "quietword", "gaveup",
        "want:failed", "thread:chronic", "group:show", "performed", "group:joined", "group:left"}  # bands: see the Bands section
SHORT = [
    (r"^(.+) moved to the town for a job at the (.+?)(, with (.+))?\.$", lambda m: f"{m[1]} arrives for the {m[2]}" + (f" (with {m[4]})" if m[4] else "")),
    (r"^(.+) started work at the (.+)\.$", r"\1 starts at the \2"),
    (r"^Peter Lane retired after (.+) years at the Old Bank Café\.$", r"Peter Lane steps down as the Old Bank Café's owner"),
    (r"^(.+) retired after (.+) years at the (.+)\.$", r"\1 retires from the \3"),
    (r"^(.+) became (.+) at the (.+)\.$", r"\1 becomes \2 at the \3"),
    (r"^(.+) bought (.+)\.$", r"\1 buys \2"),
    (r"^(.+) was born to (.+)\.$", r"\1 born to \2"),
    (r"^(.+) died (.+)\.$", r"**\1 dies \2**"),
    (r"^(.+) and (.+) got married\.$", r"\1 and \2 marry"),
    (r"^(.+) and (.+) divorced\.$", r"\1 and \2 divorce"),
    (r"^(.+) and (.+) split up\.$", r"\1 and \2 split up"),
    (r"^(.+) was found out: (.+)\.$", r"\1 found out: \2"),
    (r"^(.+) played the Anchor's open night and (.+)\.$", r"open night: \1 \2"),
    (r"^(.+) stopped drinking\.$", r"\1 stops drinking"),
    (r"^(.+) walked out of the (.+) to start again somewhere else\.$", r"\1 walks out of the \2"),
    (r"^(.+) hung back when the others went out into the storm\.$", r"\1 hangs back in the storm"),
    (r"^(.+) went out into the storm\.$", r"\1 goes out into the storm"),
    (r"^(.+) was passed over for (.+); (.+) got the job\.$", r"\1 passed over for \2"),
    (r"^The summer festival that (.+) put on was the best night the town had had in years\.$", r"\1's festival: \"the best night the town had had in years\""),
    (r"^The summer festival that (.+) put on was a washout; (.+)\.$", r"\1's festival: \"a washout\"; \2"),
    (r"^The council said yes to (.+)\.$", r"council says yes to \1"),
    (r"^The harbour day ran like clockwork; (.+) had a list for everything\.$", r"the harbour day \"like clockwork\" (\1)"),
    (r"^The harbour day went off well enough, with (.+) running it\.$", r"the harbour day \"well enough\" (\1)"),
    (r"^The harbour day (.+)\.$", r"the harbour day \1"),
    (r"^(.+) split up after (.+?): .*$", r"\1 split up after \2"),
    (r"^(.+) joined (.+?)(,.*)?\.$", r"\1 joins \2"),
    (r"^It was known that (.+) leaned on people\..*$", r"\1 known to lean on people"),
    (r"^By now (.+) was someone who kept to (him|her)self.*$", r"\1 keeps to \2self"),
    (r"^It got back to (.+) that (.+) had been talking\.$", r"it gets back to \1 that \2 talked"),
    (r"^It came out that (.+)\.$", r"**it comes out that \1**"),
    (r"^(.+) started a band: (.+)\.$", r"\1 start a band, \2"),
    (r"^(.+) left the (.+) for a start at the (.+)\.$", r"\1 moves from the \2 to the \3"),
    (r"^(.+) left the town for the city\.(.*)$", r"\1 leaves for the city.\2"),
    (r"^(.+) left for university in the city\.$", r"\1 leaves for university"),
    (r"^(.+) came back to the town after (.+) away\.$", r"\1 comes home after \2"),
    (r"^(.+) let (.+) go from the (.+)\.$", r"\1 lets \2 go from the \3"),
    (r"^(.+) played the Anchor(.*)\.$", r"\1 at the Anchor\2"),
    (r"^(.+) was the one who shone during (.+)\.$", r"\1 shines at \2"),
    (r"^(.+) would not hear it from (.+); not after (.+)\.$", r'\1 rebuffs \2: "not after \3"'),
    (r"^(.+) and (.+) buried the hatchet, (.+)\.$", r"\1 and \2 bury the hatchet, \3"),
    (r"^(.+) had (a|another|a second) (heart attack|stroke)\.$", r"\1: \2 \3"),
    (r"^(.+) was hospitalised with pneumonia\.$", r"\1: pneumonia"),
    (r"^(.+) was diagnosed with cancer\.$", r"\1: cancer"),
    (r"^(.+) learned the cancer was back\.$", r"\1: cancer back"),
    (r"^(.+) was not picked for (.+); (.+) got the place\.$", r"\1 not picked for \2"),
    (r"^(.+) shouted at (.+) in front of everyone at the (.+)\.$", r"\1 shouts at \2 at the \3"),
    (r"^(.+) confronted (.+) about it in front of everyone at the (.+?)\..*$", r"\1 confronts \2 at the \3"),
]


def short(text):
    for pat, rep in SHORT:
        m = re.match(pat, text)
        if m:
            return (rep(m) if callable(rep) else m.expand(rep)).replace('\\"', '"')
    return text.rstrip(".")


def keep(e):
    if e["vis"] == "private" or e["type"] in DROP:
        return False
    if e["type"] in ("go", "hangback", "caught", "peace", "rebuffed", "claimsong", "group:creditrow", "betrayed", "scheme:found"):
        return True
    return (e["vis"] == "public" and e["notability"] >= 1000) or (e["vis"] == "local" and e["notability"] >= 1400)


if __name__ == "__main__":
    years = {}
    for e in w.D["events"]:
        if keep(e):
            years.setdefault(w.ty(e["at"]), []).append(e)
    for y in sorted(years):
        items = []
        for e in years[y]:
            tag = "P" if e["vis"] == "public" else "L"
            items.append(f"{MON[e['at']['month'] - 1]} {short(w.rd(e['text']))} ({tag} {e['id']})")
        print(f"**{y}.** " + "; ".join(items) + ".\n")
