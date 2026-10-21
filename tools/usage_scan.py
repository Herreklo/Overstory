"""Usage scan: reads this project's Claude Code transcripts and sums what each session, agent, model and kind of work used.

Transcripts: ~/.claude/projects/-Users-oystein-code-Overstory/<session>.jsonl, subagents in <session>/subagents/ with a
.meta.json each. Tokens are weighted by list price: relative weights, unverified as the plan's weights
(docs/research/working-with-claude.md). Each request is counted once, though a message is spread over several lines
and a copied session repeats its parent's messages; its output is the largest the lines report.

Only usage fields and job metadata are read: tool inputs for tool names, file paths, script names and commit subjects,
and the app's plan readings (get_usage) from tool outputs. No other tool output is read, and nothing but numbers, job
descriptions, first prompt lines, paths and commit subjects is printed. Image payloads are never parsed or held whole:
no line but an assistant's (which carries no images) is held beyond HEAD bytes, the rest streams past and is searched
only for the heads of image blocks, and a line with an image block is never parsed.

  python3 tools/usage_scan.py                      totals per session and agent (the token study's view)
  python3 tools/usage_scan.py jobs [--from 2026-10-20] [--to 2026-10-22] [--md] [--min 0.5]
        one row per job (each main session and each subagent): date, model, summary, tokens, weighted cost, kind of
        work and what it produced; then the shares by kind, unit costs, and the plan readings found in the transcripts.
        --md prints Markdown rows for docs/usage-log.md, jobs of at least --min per cent of the cost.
"""
import json, os, re, sys, glob, base64, struct, math, collections, subprocess, datetime
from zoneinfo import ZoneInfo

ROOT = os.path.expanduser('~/.claude/projects/-Users-oystein-code-Overstory')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TZ = ZoneInfo('Europe/Oslo')
HEAD = 1 << 16          # bytes of a line held at most; the rest of a longer line streams past
IDLE = 20 * 60          # a gap between requests longer than this is waiting, not work
# list price per MTok: input, 5m write, 1h write, cache read, output
PRICE = {
    'fable': (10, 12.5, 20, 0.25, 50),
    'opus': (4, 5, 8, 0.20, 20),
    'sonnet': (2, 2.5, 4, 0.10, 10),
    'haiku': (0.10, 0.125, 0.20, 0.01, 0.50),
}
KINDS = ('build', 'measure', 'review', 'research', 'docs', 'orchestration')

# Kind of a subagent's job from its description, first match wins; jobs that match none go by the tools they used.
DESC_RULES = (
    ('review', r'\b(re-?review|review|critique|judge)\b'),
    ('research', r'\b(research|survey|scout|digest|sources|reference|practitioner|primary|token facts)\b'),
    ('measure', r'\b(render|stress|golden|benchmark|contact sheet|measure the)\b'),
    ('docs', r'\b(design|draft|synthesis|consolidate|pre-mortem|register|plan|contract|options|usage log|write[- ]up)\b'),
    ('build', r'\b(build|implement|generator|port|fix)\b'),
)
# What a tool call does, from its name and input.
MEASURE_RUN = re.compile(r'-executeMethod\s+\S*?\.\w*(Frames|Views|Golden|Perf|Motion|Seasons|Variety|Render|Stills|Sheet|Check|Measure)'
                         r'|\b(stress|golden\w*|perf|mesh_hash|motion_measure|time_score|time_claims|trace_check|reach_check|crown_value'
                         r'|\w*_sheet|contact_sheet|spread|ab|info|cat|variant|validate)\.(py|sh)\b|\b(sips|magick|montage|ffmpeg)\s')
BUILD_RUN = re.compile(r'(Blender|blender)\S*\s.*?\.py\b|-executeMethod\s|\b(generators|resolver|blockouts)/\w+\.py\b|\bexport_\w+\.py\b')
RESEARCH_RUN = re.compile(r'\b(curl|wget)\s|\b(pdftext\w*|pdf2txt|pdftxt|commons_search|tc_grep)\.py\b|\bsearch\.sh\b')
DOCS_RUN = re.compile(r'\btells\.py\b')
WRITES = re.compile(r"\.write\(|\bsed\s+-i|\bperl\s+-pi|\btee\s|>\s*['\"]?[\w./~-]+\.\w+|\b(cp|mv)\s")
PATHS = re.compile(r"[\w./~-]+\.(md|py|cs|sh|shader|hlsl|compute|json|mat|unity|asset|prefab)\b")
CODE_EXT = {'.py', '.cs', '.sh', '.shader', '.hlsl', '.cginc', '.compute', '.asmdef', '.uss', '.uxml'}
ASSET_EXT = {'.mat', '.unity', '.asset', '.prefab', '.fbx', '.blend', '.controller', '.anim', '.json'}
IMAGE_EXT = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.exr', '.tif', '.tiff'}
IMG = re.compile(rb'"type":"image","source":\{"type":"base64",(?:"media_type":"[a-z/]+",)?"data":"([A-Za-z0-9+/]{44})')
SECRET = re.compile(r'\b(sk-|ghp_|gho_|ghs_|github_pat_|xox[abpr]-|AKIA|AIza)[\w-]+|[A-Za-z0-9+=]*\d[A-Za-z0-9+=]*')


def redact(s):
    """Blank anything shaped like a key or token: a known prefix, or a run of 24 or more letters and digits with a digit in it."""
    return SECRET.sub(lambda m: '[redacted]' if m.group(1) or len(m.group(0)) >= 24 else m.group(0), s or '')


def fam(model):
    m = (model or '').lower()
    for k in PRICE:
        if k in m:
            return k
    return None


def img_tokens(b64):
    """Tokens of one image from the head of its base64 (PNG only; None for other formats)."""
    try:
        raw = base64.b64decode(b64[:44])
    except Exception:
        return None, None
    if raw[:8] != b'\x89PNG\r\n\x1a\n':
        return None, None
    w, h = struct.unpack('>II', raw[16:24])
    if not w or not h:
        return None, None
    # high-res tier: long edge 2576, 4784 patches
    s = min(1.0, 2576 / max(w, h))
    w2, h2 = w * s, h * s
    t = math.ceil(w2 / 28) * math.ceil(h2 / 28)
    if t > 4784:
        s2 = math.sqrt(4784 / t)
        w2, h2 = w2 * s2, h2 * s2
        t = math.ceil(w2 / 28) * math.ceil(h2 / 28)
    return (w, h), t


def lines(path):
    """Yield (line, image heads) per transcript line. A line up to HEAD bytes comes whole. A longer one is read in
    HEAD-sized pieces and only its first piece is kept, unless it is an assistant line (which holds no images); the
    rest streams past, searched only for image blocks, of which the first 44 base64 characters are kept."""
    with open(path, 'rb') as f:
        while True:
            piece = f.readline(HEAD)
            if not piece:
                return
            user = b'"type":"user"' in piece[:2048]
            if piece.endswith(b'\n'):
                yield piece, (IMG.findall(piece) if user else [])
                continue
            asst = b'"role":"assistant"' in piece[:4096]
            head, parts = piece, [piece]
            imgs = IMG.findall(piece) if user else []
            carry = piece[-256:]
            while not piece.endswith(b'\n'):
                piece = f.readline(HEAD)
                if not piece:
                    break
                if asst:
                    parts.append(piece)
                elif user:
                    buf = carry + piece
                    imgs += [m.group(1) for m in IMG.finditer(buf) if m.end() > len(carry)]
                    carry = buf[-256:]
            yield (b''.join(parts) if asst else head), imgs


def ts_of(s):
    return datetime.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp() if s else None


def local(t, fmt='%d %b %H:%M'):
    return datetime.datetime.fromtimestamp(t, TZ).strftime(fmt)


def rel(p):
    p = os.path.expanduser(p or '')
    if os.path.isabs(p):
        return os.path.relpath(p, REPO) if p.startswith(REPO + os.sep) else None
    return p


def ftype(p):
    e = os.path.splitext(p)[1].lower()
    if p.endswith('.meta'):
        return None
    if e in ('.md', '.txt'):
        return 'docs'
    if e in CODE_EXT:
        return 'code'
    if e in ASSET_EXT:
        return 'assets'
    if e in IMAGE_EXT:
        return 'images'
    return 'other'


def commit_subjects(cmd):
    """First lines of the commit messages a Bash command commits (heredoc or -m)."""
    out = []
    for m in re.finditer(r'git(?:\s+-C\s+\S+)?\s+commit\b([^\n]*)', cmd):
        rest = m.group(1)
        if re.search(r"<<-?\s*['\"]?\w+['\"]?", rest):
            first = cmd[m.end():].lstrip('\n').split('\n', 1)[0]
        else:
            q = re.search(r'''-\w*m\s+(?:"((?:[^"\\]|\\.)*)|'([^']*))''', cmd[m.start():m.start() + 2000])
            if not q:
                continue
            first = (q.group(1) if q.group(1) is not None else q.group(2) or '').split('\n')[0].replace('\\"', '"')
        first = ' '.join(first.split())
        if first:
            out.append(first)
    return out


def acts_of(name, inp, job):
    """The kinds of work one tool call does, and what it writes or commits (recorded on the job)."""
    inp = inp if isinstance(inp, dict) else {}
    if name in ('Write', 'Edit', 'NotebookEdit', 'MultiEdit'):
        p = inp.get('file_path') or inp.get('notebook_path') or ''
        r = rel(p)
        if r:
            job.written.add(r)
        return {'docs'} if p.endswith('.md') else {'build'}
    if name == 'Read':
        p = (inp.get('file_path') or '').lower()
        return {'review'} if os.path.splitext(p)[1] in IMAGE_EXT else {'orchestration'}
    if name in ('WebFetch', 'WebSearch') or name.startswith(('mcp__Claude_Browser__', 'mcp__claude-in-chrome__')):
        return {'research'}
    if name.startswith('mcp__Blender__'):
        return {'build'}
    if name != 'Bash':
        return {'orchestration'}
    cmd = inp.get('command') or ''
    acts = set()
    for s in commit_subjects(cmd):
        job.commits.append(s)
    if MEASURE_RUN.search(cmd):
        acts.add('measure')
    if BUILD_RUN.search(MEASURE_RUN.sub(' ', cmd)):
        acts.add('build')
    if RESEARCH_RUN.search(cmd):
        acts.add('research')
    if DOCS_RUN.search(cmd):
        acts.add('docs')
    if WRITES.search(cmd):
        for m in PATHS.finditer(cmd):
            acts.add('docs' if m.group(1) == 'md' else 'build')
    return acts or {'orchestration'}


class Job:
    def __init__(self, path, main, meta):
        self.path, self.main, self.meta = path, main, meta or {}
        base = os.path.basename(path)[:-6]
        self.id = base[:8] if main else base.replace('agent-', '')[:9]
        self.session = (base if main else os.path.basename(os.path.dirname(os.path.dirname(path))))[:8]
        self.desc = self.meta.get('description') or ''
        self.prompt = ''
        self.reqs = {}            # message id -> request record
        self.written, self.commits, self.images = set(), [], []
        self.report_words = 0
        self.last = (0, False)    # (time, synthetic) of the last message: a synthetic one is an error, such as a spent limit
        self.children = []


def first_line(content):
    if isinstance(content, list):
        content = ' '.join(c.get('text', '') for c in content if isinstance(c, dict) and c.get('type') == 'text')
    for ln in (content or '').split('\n'):
        ln = ln.strip()
        if ln:
            return ln
    return ''


def scan_job(job, claimed, readings):
    own = set()
    for line, imgs in lines(job.path):
        job.images += imgs
        if b'"role":"assistant"' in line[:4096]:
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get('type') != 'assistant':
                continue
            msg = d.get('message') or {}
            mid, u = msg.get('id'), msg.get('usage')
            t = ts_of(d.get('timestamp')) or 0
            if t >= job.last[0]:
                job.last = (t, msg.get('model') == '<synthetic>')
            if not mid or not u:
                continue
            if mid in claimed and mid not in own:
                continue
            claimed.add(mid); own.add(mid)
            r = job.reqs.get(mid)
            if r is None:
                cc = u.get('cache_creation') or {}
                w1h = cc.get('ephemeral_1h_input_tokens', 0) or 0
                w5m = cc.get('ephemeral_5m_input_tokens', 0) or 0
                if not (w1h or w5m):
                    w5m = u.get('cache_creation_input_tokens', 0) or 0
                r = job.reqs[mid] = dict(t=ts_of(d.get('timestamp')), fam=fam(msg.get('model')),
                                         inp=u.get('input_tokens', 0) or 0, read=u.get('cache_read_input_tokens', 0) or 0,
                                         w5m=w5m, w1h=w1h, out=0, acts=collections.Counter())
            r['out'] = max(r['out'], u.get('output_tokens', 0) or 0)
            for c in msg.get('content') or []:
                if not isinstance(c, dict):
                    continue
                if c.get('type') == 'tool_use':
                    for a in acts_of(c.get('name', ''), c.get('input'), job):
                        r['acts'][a] += 1
                    if c.get('name') == 'SubagentHandback':
                        job.report_words = len(str((c.get('input') or {}).get('message', '')).split())
                elif c.get('type') == 'text' and c.get('text', '').strip():
                    job.report_words = len(c['text'].split())
            continue
        if b'"type":"user"' not in line[:2048] or b'"type":"image"' in line:
            continue
        if b'percentUsed' in line and b'Weekly' in line:
            readings.extend(plan_readings(line))
        if not job.prompt:
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get('isMeta') or d.get('isCompactSummary'):
                continue
            content = (d.get('message') or {}).get('content')
            if isinstance(content, list) and any(isinstance(c, dict) and c.get('type') == 'tool_result' for c in content):
                continue
            fl = first_line(content)
            if fl and not fl.startswith('<'):
                job.prompt = fl[:120]


def plan_readings(line):
    """The app's plan bars from a get_usage result: (time, weekly %, Fable %, 5-hour %, week ends)."""
    out = []
    try:
        d = json.loads(line)
    except Exception:
        return out
    for c in (d.get('message') or {}).get('content') or []:
        if not (isinstance(c, dict) and c.get('type') == 'tool_result'):
            continue
        txt = c.get('content')
        if isinstance(txt, list):
            txt = ''.join(x.get('text', '') for x in txt if isinstance(x, dict))
        try:
            plan = json.loads(txt).get('plan') or {}
        except Exception:
            continue
        w = {x.get('label', ''): x for x in plan.get('windows') or []}
        week = w.get('Weekly · all models')
        if not week:
            continue
        out.append((ts_of(d.get('timestamp')), week.get('percentUsed'), (w.get('Weekly · Fable') or {}).get('percentUsed'),
                    (w.get('5-hour limit') or {}).get('percentUsed'), ts_of(week.get('resetsAt'))))
    return out


def cost_of(r):
    if not r['fam']:
        return 0.0
    p = PRICE[r['fam']]
    return (r['inp'] * p[0] + r['w5m'] * p[1] + r['w1h'] * p[2] + r['read'] * p[3] + r['out'] * p[4]) / 1e6


def load(lo=None, hi=None):
    """All jobs, each request counted once. lo/hi bound request times (epoch seconds)."""
    mains = sorted(glob.glob(os.path.join(ROOT, '*.jsonl')), key=lambda p: (-os.path.getsize(p), p))
    subs = sorted(glob.glob(os.path.join(ROOT, '*', 'subagents', '*.jsonl')),
                  key=lambda p: (not os.path.exists(p[:-6] + '.meta.json'), p))
    claimed, readings, jobs, allreq = set(), [], [], []
    for p in mains + subs:
        main = p in mains
        meta = None
        if not main and os.path.exists(p[:-6] + '.meta.json'):
            with open(p[:-6] + '.meta.json') as f:
                meta = json.load(f)
        job = Job(p, main, meta)
        if main:
            tf = os.path.join(p[:-6], 'custom-title.json')
            if os.path.exists(tf):
                with open(tf) as f:
                    job.desc = json.load(f).get('customTitle', '')
        scan_job(job, claimed, readings)
        for r in job.reqs.values():
            r['cost'] = cost_of(r)
            if r['t'] is not None:
                allreq.append((r['t'], r['cost']))
        for mid in [m for m, r in job.reqs.items() if r['t'] is None or (lo and r['t'] < lo) or (hi and r['t'] >= hi)]:
            del job.reqs[mid]
        if job.reqs:
            jobs.append(job)
    for job in jobs:
        rs = sorted(job.reqs.values(), key=lambda r: r['t'])
        for a, b in zip(rs, rs[1:] + [None]):
            gap = (b['t'] - a['t']) if b else 0
            a['dt'] = gap if gap <= IDLE else 0
        job.rs = rs
        job.t0, job.t1 = rs[0]['t'], rs[-1]['t']
        job.cost = sum(r['cost'] for r in rs)
        job.tok = {k: sum(r[k] for r in rs) for k in ('inp', 'read', 'w5m', 'w1h', 'out')}
        job.active = sum(r['dt'] for r in rs)
        fams = collections.Counter()
        for r in rs:
            fams[r['fam']] += r['cost']
        job.model = fams.most_common(1)[0][0] or '-'
        job.maxctx = max(r['inp'] + r['read'] + r['w5m'] + r['w1h'] for r in rs)
        job.acts = collections.Counter()
        for r in rs:
            job.acts.update(r['acts'])
    byid = {os.path.basename(j.path)[:-6].replace('agent-', ''): j for j in jobs if not j.main}
    for j in jobs:
        pa = j.meta.get('parentAgentId')
        j.parent = byid.get(pa) if pa else None
        if j.parent:
            j.parent.children.append(j)
    return jobs, sorted(set(readings)), sorted(allreq)


def classify(job):
    if job.main:
        return 'orchestration'
    d = job.desc.lower()
    kind = next((k for k, rx in DESC_RULES if re.search(rx, d)), None)
    a = job.acts
    if kind == 'build' and not a['build'] and a['docs']:
        kind = 'docs'
    if kind is None:
        kind = ('research' if a['research'] >= 3 else 'build' if a['build'] else 'measure' if a['measure']
                else 'review' if a['review'] >= 3 else 'docs' if a['docs'] else 'orchestration')
    return kind


def git_commits(since):
    """Commit subject -> files, from the repo's history since a time."""
    try:
        out = subprocess.run(['git', '-C', REPO, 'log', '--all', '--since=' + datetime.datetime.fromtimestamp(since, TZ).isoformat(),
                              '--format=%x01%s', '--name-only'],
                             capture_output=True, text=True, timeout=60).stdout
    except Exception:
        return {}
    subj = collections.defaultdict(set)
    for block in out.split('\x01')[1:]:
        lines_ = block.split('\n')
        key = ' '.join(lines_[0].split())[:60]
        subj[key].update(l for l in lines_[1:] if l.strip())
    return subj


def family(job):
    out = [job]
    for c in job.children:
        out += family(c)
    return out


def fmt(n):
    return f'{n/1e9:.2f}B' if n >= 1e9 else f'{n/1e6:.1f}M' if n >= 1e6 else f'{n/1e3:.0f}k'


def totals_report():
    """The token study's view: per main session, the largest subagents, and the totals."""
    jobs = load()[0]
    G = collections.Counter(); GC = collections.Counter()
    print('MAIN SESSIONS')
    for j in [j for j in jobs if j.main]:
        c = collections.Counter()
        for r in j.rs:
            p = PRICE.get(r['fam'])
            if p:
                c['input'] += r['inp'] * p[0] / 1e6; c['w5m'] += r['w5m'] * p[1] / 1e6; c['w1h'] += r['w1h'] * p[2] / 1e6
                c['read'] += r['read'] * p[3] / 1e6; c['out'] += r['out'] * p[4] / 1e6
        ct = sum(c.values()) or 1
        G.update(j.tok); GC.update(c)
        imgs = [img_tokens(b.decode())[1] for b in j.images]
        print(f"{j.id} reqs={len(j.rs)} models={dict(collections.Counter(r['fam'] for r in j.rs))} maxctx={fmt(j.maxctx)} "
              f"read={fmt(j.tok['read'])} w1h={fmt(j.tok['w1h'])} w5m={fmt(j.tok['w5m'])} out={fmt(j.tok['out'])} "
              f"$={ct:.0f} shares read/write/out={c['read']/ct:.0%}/{(c['w1h']+c['w5m']+c['input'])/ct:.0%}/{c['out']/ct:.0%} "
              f"images={len(j.images)} imgtok~{fmt(sum(t for t in imgs if t))}")
    print('\nSUBAGENTS')
    SG = collections.Counter(); SGC = 0.0; dims = collections.Counter(); itot = 0; n_img = 0
    subs = sorted([j for j in jobs if not j.main], key=lambda j: -j.cost)
    for j in subs:
        SG.update(j.tok); SGC += j.cost
        for b in j.images:
            dm, t = img_tokens(b.decode())
            if dm:
                dims[dm] += 1; itot += t; n_img += 1
    print('n agents', len(subs))
    for j in subs[:12]:
        print(f"$={j.cost:.0f} reqs={len(j.rs)} maxctx={fmt(j.maxctx)} rawtokens={fmt(sum(j.tok.values()))} "
              f"images={len(j.images)} model={j.model} parent={j.session} {redact(j.desc)[:50]}")
    print('subagent PNG images', n_img, 'est tokens (first sight)', fmt(itot), 'top dims', dims.most_common(6))
    for name, T, C in (('MAIN', G, sum(GC.values())), ('SUB', SG, SGC)):
        print(f"\n{name} totals raw: " + ' '.join(f"{k}={fmt(v)}" for k, v in T.items()) + f"  list$={C:.0f}")


def jobs_report(lo, hi, md, min_share):
    jobs, readings, allreq = load(lo, hi)
    if not jobs:
        print('no requests in the window'); return
    commits = git_commits(min(j.t0 for j in jobs) - 86400)
    total = sum(j.cost for j in jobs)
    latest = max(j.t1 for j in jobs)
    for j in jobs:
        j.kind = classify(j)
        # done, running, or cut off (its last message an error, such as a spent limit)
        j.status = ('' if j.main else 'cut' if j.last[1] else 'done' if j.meta.get('finished')
                    else 'running' if j.t1 > latest - 1800 else 'done')
        files = set(j.written)
        j.n_commits = 0
        for s in j.commits:
            hit = commits.get(s[:60])
            if hit is not None:
                j.n_commits += 1
                files |= hit
        j.files = sorted(f for f in files if ftype(f))
        j.fcount = collections.Counter(ftype(f) for f in j.files)
        j.fam_cost = sum(x.cost for x in family(j))

    def produced(j):
        parts = [f'{j.n_commits} commits'] if j.n_commits else []
        parts += [f'{n} {t}' for t, n in sorted(j.fcount.items(), key=lambda x: -x[1])]
        if not j.main and j.files:
            parts.append(', '.join(j.files[:2]) + (f' (+{len(j.files) - 2})' if len(j.files) > 2 else ''))
        if not j.main and j.report_words and j.status == 'done':
            parts.append(f'report {j.report_words} words')
        if j.status in ('cut', 'running'):
            parts.append('cut off' if j.status == 'cut' else 'still running')
        return '; '.join(parts) or '-'

    jobs.sort(key=lambda j: (j.t0, j.id))
    if not md:
        print(f"{'start':12} {'job':9} {'d':1} {'status':7} {'kind':13} {'model':6} {'reqs':>5} {'act h':>5} {'input':>6} {'read':>7} "
              f"{'write':>6} {'out':>6} {'w$':>6} {'fam w$':>6} {'share':>5}  summary | produced")
    for j in jobs:
        tw = j.tok['w5m'] + j.tok['w1h']
        summary = redact(j.desc if not j.main else f"{j.desc}: {j.prompt}")[:70]
        if md:
            if 100 * j.cost / total >= min_share:
                print(f"| {local(j.t0, '%d %b')} | {summary} | {j.kind} | {j.model.capitalize()} | {fmt(j.tok['inp'])} / {fmt(j.tok['read'])} / "
                      f"{fmt(tw)} / {fmt(j.tok['out'])} | {j.cost:.0f} ({100*j.cost/total:.1f}%) | {redact(produced(j))} |")
            continue
        print(f"{local(j.t0):12} {j.id:9} {j.meta.get('spawnDepth', 0)} {j.status:7} {j.kind:13} {j.model:6} {len(j.rs):5} {j.active/3600:5.1f} "
              f"{fmt(j.tok['inp']):>6} {fmt(j.tok['read']):>7} {fmt(tw):>6} {fmt(j.tok['out']):>6} {j.cost:6.0f} {j.fam_cost:6.0f} "
              f"{100*j.cost/total:4.1f}%  {summary} | {redact(produced(j))}")

    # shares by kind: by job (the main sessions as orchestration), and by request (the main sessions' requests by what they did)
    by_job = collections.Counter(); by_req = collections.Counter(); tok_job = collections.Counter(); hours = collections.Counter()
    main_split = collections.Counter(); main_hours = collections.Counter(); main_tok = collections.Counter()
    for j in jobs:
        by_job[j.kind] += j.cost
        tok_job[j.kind] += sum(j.tok.values())
        if not j.main:
            by_req[j.kind] += j.cost
            hours[j.kind] += j.active
            continue
        for r in j.rs:
            a = [k for k in r['acts'] if k != 'orchestration'] or ['orchestration']
            n = r['inp'] + r['read'] + r['w5m'] + r['w1h'] + r['out']
            for k in a:
                by_req[k] += r['cost'] / len(a); main_split[k] += r['cost'] / len(a); main_hours[k] += r['dt'] / len(a)
                main_tok[k] += n / len(a)
    print(f"\nSHARES BY KIND ({local(min(j.t0 for j in jobs))} to {local(max(j.t1 for j in jobs))}, {len(jobs)} jobs, "
          f"weighted ${total:.0f})")
    print(f"{'kind':14} {'jobs':>5} {'by job':>7} {'tokens':>8} {'by request':>11} {'main-session share':>19} {'main h':>7} {'agent h':>8}")
    msum = sum(main_split.values()) or 1
    njobs = collections.Counter(j.kind for j in jobs)
    for k in KINDS:
        print(f"{k:14} {njobs[k]:5} {100*by_job[k]/total:6.1f}% {fmt(tok_job[k]):>8} {100*by_req[k]/total:10.1f}% {100*main_split[k]/msum:18.1f}% "
              f"{main_hours[k]/3600:7.1f} {hours[k]/3600:8.1f}")

    # unit costs
    print('\nUNIT COSTS (weighted $; tokens processed = input + cache reads + cache writes + output)')
    studies = [j for j in jobs if not j.main and j.kind == 'research' and not j.parent and j.status == 'done'
               and any(f.startswith('docs/research/') for x in family(j) for f in x.files)]
    digests = [j for j in studies if j.desc.lower().startswith('digest')]
    studies = [j for j in studies if j not in digests]
    def stats(name, xs, cost, toks):
        if not xs:
            print(f'{name}: none'); return
        cs = sorted(cost(x) for x in xs); ts = sorted(toks(x) for x in xs)
        print(f"{name}: n={len(xs)} median ${cs[len(cs)//2]:.0f} (range {cs[0]:.0f} to {cs[-1]:.0f}), "
              f"tokens median {fmt(ts[len(ts)//2])} (range {fmt(ts[0])} to {fmt(ts[-1])}), total ${sum(cs):.0f}")
    ftok = lambda j: sum(sum(x.tok.values()) for x in family(j))
    for j in studies:
        print(f"  study {local(j.t0)}  ${j.fam_cost:5.1f}  {fmt(ftok(j)):>6}  helpers {len(family(j)) - 1}  {redact(j.desc)[:60]}")
    stats('finished study (wrote docs/research), with its helpers', studies, lambda j: j.fam_cost, ftok)
    stats('digest of studies', digests, lambda j: j.fam_cost, ftok)
    reviews = [j for j in jobs if not j.main and j.kind == 'review' and j.status == 'done']
    for m in sorted({j.model for j in reviews}):
        stats(f'strict review on {m}', [j for j in reviews if j.model == m], lambda j: j.cost, lambda j: sum(j.tok.values()))
    bjobs = [j for j in jobs if not j.main and j.kind == 'build']
    bh = sum(j.active for j in bjobs) / 3600; bc = sum(j.cost for j in bjobs); bt = sum(sum(j.tok.values()) for j in bjobs)
    mh = main_hours['build'] / 3600; mc = main_split['build']; mt = main_tok['build']
    for name, h, c, t in (('in build agents', bh, bc, bt), ('in the main sessions', mh, mc, mt), ('all', bh + mh, bc + mc, bt + mt)):
        if h:
            print(f'hour of building, {name}: {h:.1f} h active, ${c:.0f}, ${c/h:.0f} and {fmt(t/h)} tokens per hour')

    # the plan meter against the weights
    if readings:
        print('\nPLAN READINGS (app, get_usage) against the weighted cost since the week began')
        first = prev = None
        for t, wk, fb, h5, end in readings:
            start = end - 7 * 86400
            c = sum(x[1] for x in allreq if start <= x[0] <= t)
            line = f"{local(t)}  weekly {wk}%  Fable {fb}%  5-hour {h5}%  weighted ${c:.0f} since {local(start)}  ${c/max(wk,1):.1f} per point"
            if prev and wk != prev[1]:
                line += f"  (${(c - prev[2])/(wk - prev[1]):.1f} per point since the last change)"
            print(line)
            if not prev or wk != prev[1]:
                prev = (t, wk, c)
            first = first or (t, wk, c)
        if prev[1] != first[1]:
            print(f"from {local(first[0])} to {local(prev[0])}: ${(prev[2] - first[2]) / (prev[1] - first[1]):.1f} per point "
                  f"(over the whole week: ${prev[2] / prev[1]:.1f})")


def main(argv):
    if not argv or argv[0] != 'jobs':
        totals_report(); return
    a = argv[1:]
    def opt(name, default=None):
        return a[a.index(name) + 1] if name in a else default
    lo = opt('--from'); hi = opt('--to')
    lo = datetime.datetime.fromisoformat(lo).replace(tzinfo=TZ).timestamp() if lo else None
    hi = (datetime.datetime.fromisoformat(hi).replace(tzinfo=TZ) + datetime.timedelta(days=1)).timestamp() if hi else None
    jobs_report(lo, hi, '--md' in a, float(opt('--min', 0.5)))


if __name__ == '__main__':
    main(sys.argv[1:])
