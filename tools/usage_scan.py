"""Usage scan: reads this project's Claude Code transcripts (~/.claude/projects/...) and sums tokens per session, agent and model, weighted by list price (relative weights; unverified). From the token study, docs/research/working-with-claude.md."""
import json, os, sys, glob, base64, struct, math, collections

ROOT = os.path.expanduser('~/.claude/projects/-Users-oystein-code-Overstory')
# list price per MTok: input, 5m write, 1h write, cache read, output
PRICE = {
    'fable': (10, 12.5, 20, 0.25, 50),
    'opus': (4, 5, 8, 0.20, 20),
    'sonnet': (2, 2.5, 4, 0.10, 10),
    'haiku': (0.10, 0.125, 0.20, 0.01, 0.50),
}

def fam(model):
    m = (model or '').lower()
    for k in PRICE:
        if k in m:
            return k
    return None

def img_tokens(b64):
    try:
        raw = base64.b64decode(b64[:200] + '=' * (-len(b64[:200]) % 4))
    except Exception:
        return None, None
    w = h = None
    if raw[:8] == b'\x89PNG\r\n\x1a\n':
        w, h = struct.unpack('>II', raw[16:24])
    if not w:
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

def walk_images(content, out):
    if isinstance(content, list):
        for c in content:
            if isinstance(c, dict):
                if c.get('type') == 'image':
                    src = c.get('source', {})
                    dims, t = img_tokens(src.get('data', '')) if src.get('type') == 'base64' else (None, None)
                    out.append((dims, t))
                elif 'content' in c:
                    walk_images(c['content'], out)

def scan(path):
    seen = set()
    tot = collections.Counter()
    cost = collections.Counter()
    models = collections.Counter()
    maxctx = 0
    misses = []
    images = []
    reqs = 0
    with open(path, errors='ignore') as f:
        for line in f:
            try:
                d = json.loads(line)
            except Exception:
                continue
            msg = d.get('message') or {}
            if d.get('type') == 'user':
                walk_images(msg.get('content'), images)
                continue
            if d.get('type') != 'assistant':
                continue
            mid = msg.get('id')
            u = msg.get('usage')
            if not u or mid in seen:
                continue
            seen.add(mid)
            reqs += 1
            model = msg.get('model', '')
            fm = fam(model)
            models[fm] += 1
            inp = u.get('input_tokens', 0) or 0
            cr = u.get('cache_read_input_tokens', 0) or 0
            cw = u.get('cache_creation_input_tokens', 0) or 0
            out = u.get('output_tokens', 0) or 0
            cc = u.get('cache_creation') or {}
            w1h = cc.get('ephemeral_1h_input_tokens', 0) or 0
            w5m = cc.get('ephemeral_5m_input_tokens', 0) or 0
            if not (w1h or w5m):
                w5m = cw
            tot['input'] += inp; tot['read'] += cr; tot['w1h'] += w1h; tot['w5m'] += w5m; tot['out'] += out
            ctx = inp + cr + cw
            maxctx = max(maxctx, ctx)
            if cw > 40000:
                misses.append(cw)
            if fm:
                p = PRICE[fm]
                cost['input'] += inp * p[0] / 1e6
                cost['w5m'] += w5m * p[1] / 1e6
                cost['w1h'] += w1h * p[2] / 1e6
                cost['read'] += cr * p[3] / 1e6
                cost['out'] += out * p[4] / 1e6
    return dict(reqs=reqs, tot=tot, cost=cost, models=models, maxctx=maxctx, misses=misses, images=images)

def fmt(n):
    return f'{n/1e6:.1f}M' if n >= 1e6 else f'{n/1e3:.0f}k'

mains = sorted(glob.glob(os.path.join(ROOT, '*.jsonl')), key=os.path.getmtime)
subs = sorted(glob.glob(os.path.join(ROOT, '*', 'subagents', '*.jsonl')), key=os.path.getmtime)

G = collections.Counter(); GC = collections.Counter()
print('MAIN SESSIONS')
for p in mains:
    r = scan(p)
    if not r['reqs']:
        continue
    c = r['cost']; ct = sum(c.values())
    G.update(r['tot']); GC.update(c)
    imgs = [t for _, t in r['images'] if t]
    print(f"{os.path.basename(p)[:8]} reqs={r['reqs']} models={dict(r['models'])} maxctx={fmt(r['maxctx'])} "
          f"read={fmt(r['tot']['read'])} w1h={fmt(r['tot']['w1h'])} w5m={fmt(r['tot']['w5m'])} out={fmt(r['tot']['out'])} "
          f"$={ct:.0f} shares read/write/out={c['read']/ct:.0%}/{(c['w1h']+c['w5m']+c['input'])/ct:.0%}/{c['out']/ct:.0%} "
          f"bigwrites>40k={len(r['misses'])} ({fmt(sum(r['misses']))}) images={len(r['images'])} imgtok~{fmt(sum(imgs))}")

print('\nSUBAGENTS')
SG = collections.Counter(); SGC = collections.Counter(); sizes = []
dims_counter = collections.Counter(); img_total = 0; img_n = 0
for p in subs:
    r = scan(p)
    if not r['reqs']:
        continue
    ct = sum(r['cost'].values())
    SG.update(r['tot']); SGC.update(r['cost'])
    sizes.append((ct, r['reqs'], r['maxctx'], sum(r['tot'].values()), len(r['images']), dict(r['models']), os.path.basename(os.path.dirname(os.path.dirname(p)))[:8]))
    for dims, t in r['images']:
        if dims:
            dims_counter[dims] += 1; img_total += t; img_n += 1
sizes.sort(reverse=True)
print('n agents', len(sizes))
for s in sizes[:12]:
    print(f"$={s[0]:.0f} reqs={s[1]} maxctx={fmt(s[2])} rawtokens={fmt(s[3])} images={s[4]} models={s[5]} parent={s[6]}")
print('subagent images', img_n, 'est tokens each (first-sight)', fmt(img_total), 'top dims', dims_counter.most_common(6))

for name, T, C in (('MAIN', G, GC), ('SUB', SG, SGC)):
    ct = sum(C.values())
    print(f"\n{name} totals raw: " + ' '.join(f"{k}={fmt(v)}" for k, v in T.items()) + f"  list$={ct:.0f}  " +
          ' '.join(f"{k}={v/ct:.0%}" for k, v in C.items()))
