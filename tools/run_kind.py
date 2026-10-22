"""Run a kind's stages on one record: the one runner (schemas/stages.md).

It reads the record, its kind file (kinds/<kind>.json, validated against schemas/kind.schema.json) and its pack, and
runs the seven stages in order: facts, plan, life, geometry, bake, export, checks. Each stage's Python entry
(`file.py:function`, as the kind names it) takes a context and returns its output, a dict. Every output is hashed
(tools/hashes.py) into the chain; a stage whose key (the link before it and its inputs) has a valid cache entry is
skipped and its output read back. The runner never branches on the kind's name: everything a kind does is in its file.

It runs in whatever Python starts it, and stops at the first stage that is planned, ported or has no Python entry:

    .venv/bin/python tools/run_kind.py fixtures/records/bld-104.json --world-seed 1
    /Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13 tools/run_kind.py <record>   (numpy)
    /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python tools/run_kind.py -- <record>  (bpy)

Options:
    --world-seed N    the world seed (default: the pack's worldSeed; an error when the pack has none)
    --date YEAR       the fabric's date, for the stages that read "date" (default: the pack's showYear)
    --until STAGE     stop after this stage
    --rerun STAGE     run this stage even when its cache entry is valid (repeatable; "all" for every stage)
    --no-cache        neither read nor write the cache
    --out DIR         where the run's stage files go (default cache/runs/<record>); emptied of stage files first
    --golden          also write each stage file to fixtures/golden/<kind>/ (or --golden-dir)
    --check           compare the run's stage files with the golden ones (tools/diff_stage.py); exit 1 if they differ
    --golden-dir DIR  the golden fixtures' folder, for --golden and --check
    --kinds DIR       where kind files are read from (default kinds/)
    --packs DIR       where packs are read from (default packs/)
    --cache DIR       the cache's root (default cache/, kept out of git)
    --validate-kind FILE   only validate a kind file and print its problems (what Blender's Python calls, lacking
                      jsonschema)

Exit 0 when every stage that ran passed (and --check found no difference); 1 when a stage failed, an output said
"pass": false or a golden differs; 2 on a usage or setup error.
"""
import argparse
import array
import ast
import importlib
import json
import os
import shutil
import subprocess
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import hashes as HX  # noqa: E402
from hashes import Blob  # noqa: E402

VENV_PYTHON = os.path.join(ROOT, ".venv", "bin", "python")
RUNS = ("live", "frozen")
RUN_INPUTS = ("date",)  # words in a stage's reads that are the run's, not the pack's tables
KEEP = 3  # cache entries kept per record and stage
TOOLS = [os.path.join(HERE, "run_kind.py"), os.path.join(HERE, "hashes.py"),
         os.path.join(ROOT, "blender", "resolver", "hashing.py")]


class SetupError(Exception):
    """The run cannot start: a missing or invalid kind, pack, seed or record."""


class StageError(Exception):
    """A stage raised, or could not be loaded."""


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def rel(path):
    path = os.path.abspath(path)
    return os.path.relpath(path, ROOT).replace(os.sep, "/") if path.startswith(ROOT + os.sep) else path


def write_json(path, doc):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp-%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


# ---------------------------------------------------------------- the kind

def kind_problems(path, doc):
    """The kind file's problems against kind.schema.json: in-process where jsonschema is, else by the venv."""
    try:
        import validate_record as VR
    except ImportError:
        VR = None
    if VR is not None:
        return ["%s: %s" % ("/".join(str(p) for p in e.absolute_path) or "(top)", e.message)
                for e in VR.Contracts().schema_errors("kind.schema.json", doc)]
    if not os.path.exists(VENV_PYTHON):
        return ["cannot validate: no jsonschema in this Python and no venv at %s" % rel(VENV_PYTHON)]
    out = subprocess.run([VENV_PYTHON, os.path.join(HERE, "run_kind.py"), "--validate-kind", path],
                         capture_output=True, universal_newlines=True)
    if out.returncode == 0:
        return []
    return [line for line in out.stdout.splitlines() if line.strip()] or [out.stderr.strip() or "validation failed"]


def load_parts(pack_dir):
    """Every part definition in the pack, by its path."""
    parts = {}
    root = os.path.join(pack_dir, "parts")
    for dirpath, _, files in os.walk(root):
        for f in sorted(files):
            if f.endswith(".json"):
                p = os.path.join(dirpath, f)
                parts[os.path.relpath(p, root)[:-5].replace(os.sep, "/")] = read_json(p)
    return parts


# ---------------------------------------------------------------- inputs and tables

def table_paths(pack_dir, word):
    """A pack table: packs/<pack>/<word>.json, or the folder packs/<pack>/<word>/; None when the pack has neither."""
    f = os.path.join(pack_dir, word + ".json")
    if os.path.isfile(f):
        return f
    d = os.path.join(pack_dir, word)
    if os.path.isdir(d):
        return d
    return None


def table_hash(pack_dir, word):
    p = table_paths(pack_dir, word)
    if p is None:
        return "absent"
    if os.path.isfile(p):
        return HX.file_hash(p)
    return HX.files_hash(p, ["**/*.json"])


def read_table(pack_dir, word):
    p = table_paths(pack_dir, word)
    if p is None:
        return None
    if os.path.isfile(p):
        return read_json(p)
    out = {}
    for dirpath, _, files in os.walk(p):
        for f in sorted(files):
            if f.endswith(".json"):
                q = os.path.join(dirpath, f)
                out[os.path.relpath(q, p)[:-5].replace(os.sep, "/")] = read_json(q)
    return dict((k, out[k]) for k in sorted(out))


def stage_inputs(stage, spec, record_path, date, pack_dir):
    """What a stage reads beyond the link before it: the record for facts; the date and each pack table it declares;
    bakeVersion for the bake (schemas/hashing.md, The chain)."""
    inputs = {}
    if stage == "facts":
        inputs["record"] = HX.file_hash(record_path)
    for word in spec.get("reads", []):
        if word == "date":
            inputs["date"] = int(date)
        else:
            inputs["table:" + word] = table_hash(pack_dir, word)
    if stage == "bake":
        inputs["bakeVersion"] = HX.bake_version()
    return inputs


# ---------------------------------------------------------------- the context a stage gets

class Context(object):
    """What a stage's entry is given. It reads only what its stage declares: an undeclared table or the date raises."""

    def __init__(self, stage, kind, spec, record_path, source, outputs, inputs, world_seed, pack, pack_dir, work):
        self.stage = stage
        self.kind = kind
        self.params = spec.get("params", {})
        self.record_path = record_path
        self.source = source            # the record file as read; facts turns it into the record
        self.outputs = outputs          # earlier stages' outputs, by stage (Blobs whole)
        self.inputs = inputs            # this stage's inputs as hashed
        self.world_seed = world_seed
        self.pack = pack
        self.pack_dir = pack_dir
        self.root = ROOT
        self._work = work
        self._reads = list(spec.get("reads", []))
        self._wrote = {}
        self._depends = set()
        self._log = []

    @property
    def record(self):
        """The facts stage's output."""
        return self.outputs["facts"]

    @property
    def date(self):
        if "date" not in self._reads:
            raise KeyError("stage %s reads the date without declaring it in its reads" % self.stage)
        return self.inputs["date"]

    def table(self, word):
        """A pack table the stage declares in its reads, parsed (a folder as {path: definition}); None if absent."""
        if word not in self._reads or word in RUN_INPUTS:
            raise KeyError("stage %s reads table %r without declaring it in its reads" % (self.stage, word))
        return read_table(self.pack_dir, word)

    @property
    def work(self):
        """A folder of the stage's own in the cache, one per key, for files it writes (an export): a run at another
        date writes beside it, never over it."""
        os.makedirs(self._work, exist_ok=True)
        return self._work

    def wrote(self, path):
        """Name a file the stage wrote outside the cache; its cache entry holds only while the file is unchanged."""
        st = os.stat(path)
        self._wrote[os.path.abspath(path)] = [st.st_size, st.st_mtime_ns]

    def depends(self, path):
        """Name a file (code or data) the stage's output rests on that no input or import shows."""
        self._depends.add(os.path.abspath(path))

    def log(self, text):
        self._log.append(str(text))


def load_entry(entry):
    """The entry's function: `path/file.py:function`, the path from the repo's root. The file is imported by its
    module name with its folder first on sys.path, so its sibling imports work and one module is never loaded twice."""
    path, fn = entry.rsplit(":", 1)
    full = os.path.join(ROOT, path)
    if not os.path.isfile(full):
        raise StageError("its entry %s: no such file" % entry)
    folder, name = os.path.dirname(full), os.path.basename(full)[:-3]
    if folder not in sys.path:
        sys.path.insert(0, folder)
    try:
        mod = importlib.import_module(name)
    except ImportError as e:
        raise StageError("its entry %s cannot be imported: %s%s" % (entry, e, _hint(e)))
    if os.path.realpath(getattr(mod, "__file__", "") or "") != os.path.realpath(full):
        raise StageError("its entry %s: the module name %r is already %s; rename one of them"
                         % (entry, name, getattr(mod, "__file__", "a built-in module")))
    if not hasattr(mod, fn):
        raise StageError("its entry %s: %s has no %s" % (entry, path, fn))
    return getattr(mod, fn)


def _hint(e):
    name = getattr(e, "name", "") or ""
    if name.split(".")[0] == "bpy":
        return " (run it under Blender: Blender -b --factory-startup --python tools/run_kind.py -- <record>)"
    if name.split(".")[0] == "numpy":
        return " (run it in Blender's Python, which has numpy)"
    return ""


# ---------------------------------------------------------------- the cache

class Files(object):
    """File hashes for one run, each file hashed once while its size and time stand."""

    def __init__(self):
        self.memo = {}

    def hash(self, path):
        try:
            st = os.stat(path)
        except OSError:
            return "absent"
        k = (path, st.st_size, st.st_mtime_ns)
        if k not in self.memo:
            self.memo[k] = HX.file_hash(path)
        return self.memo[k]


def code_paths(ctx, entry_file):
    """The files a stage's output rests on beyond its inputs: the runner and hash spec, the entry, every repo module
    loaded so far (outside the venv), and what the stage named with ctx.depends."""
    paths = set(TOOLS) | {entry_file} | ctx._depends
    venv = os.path.join(ROOT, ".venv") + os.sep
    for name, m in list(sys.modules.items()):
        f = getattr(m, "__file__", None)
        if not f or name == "__main__":
            continue
        f = os.path.abspath(f)
        if f.endswith(".pyc"):
            continue
        if f.startswith(ROOT + os.sep) and not f.startswith(venv):
            paths.add(f)
    return sorted(paths)


NPY_TYPES = {"float64": ("<f8", "d", 8), "float32": ("<f4", "f", 4), "int64": ("<i8", "q", 8),
             "uint64": ("<u8", "Q", 8), "int32": ("<i4", "i", 4), "uint32": ("<u4", "I", 4), "int16": ("<i2", "h", 2),
             "uint16": ("<u2", "H", 2), "int8": ("|i1", "b", 1), "uint8": ("|u1", "B", 1), "bool": ("|b1", "B", 1)}


def npy_write(path, blob):
    """A Blob as a .npy file: by numpy where it holds a numpy array, else written by hand in the same format."""
    if HX._is_numpy(blob.values):
        import numpy as np
        with open(path, "wb") as f:
            np.save(f, blob.values, allow_pickle=False)
        return
    descr, code, size = NPY_TYPES[blob.dtype]
    flat = list(HX._flatten(blob.values))
    a = array.array(code, [float(x) for x in flat] if blob.dtype in HX.FLOAT_DTYPES else [int(x) for x in flat])
    if a.itemsize != size:
        raise HX.Refused("this Python's array type %s is %d bytes, not %d" % (code, a.itemsize, size))
    if sys.byteorder != "little" and size > 1:
        a.byteswap()
    shape = "(%s)" % "".join("%d," % n for n in blob.shape) if blob.shape else "()"
    header = "{'descr': '%s', 'fortran_order': False, 'shape': %s, }" % (descr, shape)
    pad = 64 - (10 + len(header) + 1) % 64
    header = (header + " " * (pad % 64) + "\n").encode("latin1")
    with open(path, "wb") as f:
        f.write(b"\x93NUMPY\x01\x00" + len(header).to_bytes(2, "little") + header)
        f.write(a.tobytes())


def npy_read(path, dtype, use_numpy=True):
    """A .npy file's values: a numpy array where numpy is (and use_numpy), else nested lists."""
    try:
        import numpy as np
    except ImportError:
        np = None
    if not use_numpy:
        np = None
    if np is not None:
        return np.load(path, allow_pickle=False)
    with open(path, "rb") as f:
        data = f.read()
    if data[:6] != b"\x93NUMPY":
        raise ValueError("%s is not a .npy file" % path)
    if data[6] == 1:
        hlen, start = int.from_bytes(data[8:10], "little"), 10
    else:
        hlen, start = int.from_bytes(data[8:12], "little"), 12
    header = ast.literal_eval(data[start:start + hlen].decode("latin1"))
    descr, code, size = NPY_TYPES[dtype]
    if header["descr"] != descr or header["fortran_order"]:
        raise ValueError("%s holds %s, not %s" % (path, header["descr"], descr))
    a = array.array(code)
    a.frombytes(data[start + hlen:])
    if sys.byteorder != "little" and size > 1:
        a.byteswap()
    flat = [bool(x) for x in a] if dtype == "bool" else a.tolist()
    shape = list(header["shape"])
    if not shape:
        return flat[0]

    def nest(items, dims):
        if len(dims) == 1:
            return list(items)
        step = len(items) // dims[0] if dims[0] else 0
        return [nest(items[i * step:(i + 1) * step], dims[1:]) for i in range(dims[0])]
    return nest(flat, shape)


def _blobs(v, found):
    if isinstance(v, Blob):
        found[HX.hex64(v.hash)] = v
    elif isinstance(v, dict):
        for x in v.values():
            _blobs(x, found)
    elif isinstance(v, list):
        for x in v:
            _blobs(x, found)
    return found


def _rehydrate(v, folder):
    if isinstance(v, dict):
        if set(v) == {"$blob"}:
            s = v["$blob"]
            b = Blob(npy_read(os.path.join(folder, s["hash"] + ".npy"), s["dtype"]), s["dtype"])
            if list(b.shape) != s["shape"]:
                raise ValueError("blob %s: shape %s, not %s" % (s["hash"], list(b.shape), s["shape"]))
            b._hash = int(s["hash"], 16)
            return b
        return dict((k, _rehydrate(x, folder)) for k, x in v.items())
    if isinstance(v, list):
        return [_rehydrate(x, folder) for x in v]
    return v


def cache_load(folder, key, files):
    """The cached output under key, or None when there is none or it no longer holds: a code or data file it rests on
    has changed, or a file it wrote is gone or changed."""
    entry = os.path.join(folder, key)
    try:
        meta = read_json(os.path.join(entry, "meta.json"))
        if meta.get("key") != key:
            return None
        for p, h in meta["code"].items():
            if files.hash(os.path.join(ROOT, p) if not os.path.isabs(p) else p) != h:
                return None
        for p, (size, mtime) in meta["wrote"].items():
            st = os.stat(os.path.join(ROOT, p) if not os.path.isabs(p) else p)
            if st.st_size != size or st.st_mtime_ns != mtime:
                return None
        output = _rehydrate(read_json(os.path.join(entry, "output.json")), os.path.join(entry, "blobs"))
    except (OSError, ValueError, KeyError, TypeError):
        return None
    os.utime(os.path.join(entry, "meta.json"))  # (kept as recently used)
    return output, meta["output"]


def cache_store(folder, key, output, meta):
    """Write an entry atomically (a temporary folder renamed into place) and keep the stage's KEEP latest."""
    os.makedirs(folder, exist_ok=True)
    tmp = os.path.join(folder, ".tmp-%d-%s" % (os.getpid(), key))
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(os.path.join(tmp, "blobs"))
    for h, b in sorted(_blobs(output, {}).items()):
        npy_write(os.path.join(tmp, "blobs", h + ".npy"), b)
    write_json(os.path.join(tmp, "output.json"), HX.plain(output))
    write_json(os.path.join(tmp, "meta.json"), meta)
    final = os.path.join(folder, key)
    shutil.rmtree(final, ignore_errors=True)
    os.replace(tmp, final)
    entries = []
    for name in os.listdir(folder):
        m = os.path.join(folder, name, "meta.json")
        if name not in ("files",) and not name.startswith(".") and os.path.exists(m):
            entries.append((os.stat(m).st_mtime_ns, name))
    for _, name in sorted(entries, reverse=True)[KEEP:]:
        if name != key:
            shutil.rmtree(os.path.join(folder, name), ignore_errors=True)
            shutil.rmtree(os.path.join(folder, "files", name), ignore_errors=True)


# ---------------------------------------------------------------- the run

def stage_file(stage, rid, kind, schema_version, chain, output):
    return {"what": "the %s stage's output for %s, kind %s (tools/run_kind.py; schemas/stages.md)" % (stage, rid, kind),
            "schemaVersion": schema_version, "record": rid, "kind": kind, "stage": stage, "chain": chain,
            "output": HX.plain(output)}


def run(record_path, world_seed=None, date=None, until=None, rerun=(), use_cache=True, out=None, golden_dir=None,
        kinds_dir=None, packs_dir=None, cache_dir=None, say=print):
    """Run a record's kind through its stages. Returns the run's summary (also written as run.json in out)."""
    record_path = os.path.abspath(record_path)
    kinds_dir = os.path.abspath(kinds_dir or os.path.join(ROOT, "kinds"))
    packs_dir = os.path.abspath(packs_dir or os.path.join(ROOT, "packs"))
    cache_dir = os.path.abspath(cache_dir or os.path.join(ROOT, "cache"))
    try:
        source = read_json(record_path)
    except (OSError, ValueError) as e:
        raise SetupError("the record %s cannot be read: %s" % (rel(record_path), e))
    for k in ("id", "kind", "pack", "schemaVersion"):
        if k not in source:
            raise SetupError("the record %s has no %s" % (rel(record_path), k))
    rid, kind_name = source["id"], source["kind"]
    kind_path = os.path.join(kinds_dir, kind_name + ".json")
    if not os.path.exists(kind_path):
        raise SetupError("no kind file %s" % rel(kind_path))
    kind = read_json(kind_path)
    problems = kind_problems(kind_path, kind)
    if problems:
        raise SetupError("%s does not validate:\n  %s" % (rel(kind_path), "\n  ".join(problems)))
    if kind["kind"] != kind_name:
        raise SetupError("%s names kind %r" % (rel(kind_path), kind["kind"]))
    if source["schemaVersion"] != kind["schemaVersion"]:
        raise SetupError("the record is at schemaVersion %r and its kind at %r: migrate first (tools/migrate.py)"
                         % (source["schemaVersion"], kind["schemaVersion"]))
    pack_dir = os.path.join(packs_dir, source["pack"])
    if not os.path.exists(os.path.join(pack_dir, "pack.json")):
        raise SetupError("no pack %s" % rel(pack_dir))
    pack = read_json(os.path.join(pack_dir, "pack.json"))
    if world_seed is None:
        world_seed = pack.get("worldSeed")
    if world_seed is None:
        raise SetupError("pack %s names no worldSeed: pass --world-seed" % source["pack"])
    if date is None:
        date = pack.get("showYear")
    unknown = [s for s in list(rerun) + ([until] if until else []) if s not in HX.STAGES and s != "all"]
    if unknown:
        raise SetupError("no such stage: %s (the stages are %s)" % (", ".join(unknown), ", ".join(HX.STAGES)))

    ruleset = HX.ruleset_version(kind, HX.admitted_parts(kind, load_parts(pack_dir)))
    head = HX.head(kind["schemaVersion"], ruleset, int(world_seed))
    after = HX.head_hash(head)
    out = os.path.abspath(out or os.path.join(cache_dir, "runs", rid))
    os.makedirs(out, exist_ok=True)
    for st in HX.STAGES:
        if os.path.exists(os.path.join(out, st + ".json")):
            os.remove(os.path.join(out, st + ".json"))
    summary = {"what": "a run of tools/run_kind.py: what ran, what was skipped, the chain (machine-local: keys and "
                       "times)", "record": rid, "recordFile": rel(record_path), "kind": kind_name, "head": head,
               "headHash": after, "worldSeed": int(world_seed), "date": date, "python": sys.version.split()[0],
               "stages": [], "stopped": None, "ok": True}
    say("%s  kind %s  ruleset %s  world seed %d  date %s  head %s" % (rid, kind_name, ruleset, int(world_seed), date,
                                                                      after))
    files = Files()
    outputs = {}
    for stage in HX.STAGES:
        spec = kind["stages"][stage]
        if spec["status"] not in RUNS or not spec.get("python"):
            summary["stopped"] = "%s is %s" % (stage, spec["status"] if spec["status"] not in RUNS
                                               else "live without a Python entry")
            break
        inputs = stage_inputs(stage, spec, record_path, date, pack_dir)
        key = HX.stage_key(stage, after, inputs)
        folder = os.path.join(cache_dir, "stages", rid, stage)
        t0 = time.time()
        hit = None
        if use_cache and stage not in rerun and "all" not in rerun:
            hit = cache_load(folder, key, files)
        log = []
        if hit is not None:
            output, content = hit
        else:
            entry_file = os.path.join(ROOT, spec["python"].rsplit(":", 1)[0])
            ctx = Context(stage, kind, spec, record_path, source, outputs, inputs, int(world_seed), pack, pack_dir,
                          os.path.join(folder, "files", key))
            try:
                fn = load_entry(spec["python"])
                output = fn(ctx)
                if not isinstance(output, dict):
                    raise StageError("its entry returned a %s, not a dict" % type(output).__name__)
                output = HX.plain(output, "$", blobs=True)
                content = HX.hash_hex(output)
            except Exception as e:  # a stage's failure is reported, never cached
                say("%-9s FAILED  %s" % (stage, e))
                if not isinstance(e, StageError):
                    say(traceback.format_exc().rstrip())
                summary["stages"].append({"stage": stage, "key": key, "failed": str(e)})
                summary["ok"] = False
                summary["stopped"] = "%s failed" % stage
                break
            log = ctx._log
            if use_cache:
                code = dict((rel(p), files.hash(p)) for p in code_paths(ctx, entry_file))
                cache_store(folder, key, output, {
                    "stage": stage, "key": key, "after": after, "inputs": inputs, "output": content,
                    "code": code, "wrote": dict((rel(p), v) for p, v in ctx._wrote.items()),
                    "seconds": round(time.time() - t0, 3), "python": sys.version.split()[0]})
        ln = HX.link(stage, after, inputs, content)
        chain = {"after": after, "inputs": inputs, "output": content, "link": ln}
        if stage == "facts":
            chain = dict(chain, head=head)
        write_json(os.path.join(out, stage + ".json"),
                   stage_file(stage, rid, kind_name, kind["schemaVersion"], chain, output))
        passed = output.get("pass") is not False
        floats = HX.count_floats(HX.plain(output))
        summary["stages"].append({"stage": stage, "key": key, "link": ln, "output": content,
                                  "skipped": hit is not None, "seconds": round(time.time() - t0, 3),
                                  "floats": floats, "pass": passed, "log": log})
        say("%-9s %-4s  %6.2fs  output %s  link %s%s" % (stage, "skip" if hit is not None else "ran",
                                                         time.time() - t0, content, ln, "" if passed else "  FAILED"))
        for line in log:
            say("          " + line)
        outputs[stage] = output
        after = ln
        if not passed:
            summary["ok"] = False
            summary["stopped"] = "%s did not pass" % stage
            for p in output.get("problems", [])[:20]:
                say("          " + str(p))
            break
        if stage == until:
            summary["stopped"] = "until %s" % stage
            break
    if summary["stopped"]:
        say("stopped: %s" % summary["stopped"])
    summary["outputs"] = outputs  # (for a caller in-process; never written)
    write_json(os.path.join(out, "run.json"), dict((k, v) for k, v in summary.items() if k != "outputs"))
    if golden_dir and summary["ok"]:
        golden_dir = os.path.abspath(golden_dir)
        for s in summary["stages"]:
            shutil.copyfile(os.path.join(out, s["stage"] + ".json"), os.path.join(_mkdir(golden_dir),
                                                                                 s["stage"] + ".json"))
        say("golden: wrote %d stage files to %s" % (len(summary["stages"]), rel(golden_dir)))
    summary["out"] = out
    return summary


def _mkdir(path):
    os.makedirs(path, exist_ok=True)
    return path


def _argv(argv):
    """Blender passes its own arguments first; ours follow --."""
    return argv[argv.index("--") + 1:] if "--" in argv else argv[1:]


def main(argv):
    args = _argv(argv)
    if args[:1] == ["--validate-kind"]:
        problems = []
        for p in args[1:]:
            problems += kind_problems(p, read_json(p))
        for line in problems:
            print(line)
        return 1 if problems else 0
    ap = argparse.ArgumentParser(prog="run_kind.py", description="Run a record's kind through its stages.")
    ap.add_argument("record")
    ap.add_argument("--world-seed", type=int)
    ap.add_argument("--date", type=int)
    ap.add_argument("--until")
    ap.add_argument("--rerun", action="append", default=[])
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--golden", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--golden-dir")
    ap.add_argument("--kinds")
    ap.add_argument("--packs")
    ap.add_argument("--cache")
    a = ap.parse_args(args)
    kind_name = None
    try:
        kind_name = read_json(a.record).get("kind")
    except (OSError, ValueError):
        pass
    golden_dir = a.golden_dir or os.path.join(ROOT, "fixtures", "golden", kind_name or "unknown")
    try:
        s = run(a.record, world_seed=a.world_seed, date=a.date, until=a.until, rerun=a.rerun, use_cache=not a.no_cache,
                out=a.out, golden_dir=golden_dir if a.golden else None, kinds_dir=a.kinds, packs_dir=a.packs,
                cache_dir=a.cache)
    except SetupError as e:
        print("run_kind: %s" % e)
        return 2
    status = 0 if s["ok"] else 1
    if a.check:
        import diff_stage
        report = diff_stage.diff_runs(golden_dir, s["out"], stages=[x["stage"] for x in s["stages"]])
        diff_stage.show(report, "golden", "run")
        if report["differ"]:
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv))  # (Blender -b exits with it too)
