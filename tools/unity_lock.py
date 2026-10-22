#!/usr/bin/env python3
"""The Unity lock: one job at a time on unity/ (the unity-conventions skill, Using Unity; docs/measuring.md).

Several sessions and agents share one Unity project on one Mac, and Unity cannot open a project twice. Every command
that runs Unity on unity/, or writes into it (a Blender export's install step), goes through this lock, so no two
overlap. The lock is fcntl.flock on .locks/unity.lock (gitignored and never deleted; not in unity/Temp/, which Unity
deletes when it quits), and its holder is named in .locks/unity.json.

    tools/unity_lock.py run [--owner "<session or agent>"] [--purpose "<what>"] [--timing [--out DIR [--out-runs GLOB]]]
        [--max-wait SECONDS] -- <command...>
    tools/unity_lock.py status

run takes the lock, runs the command and releases the lock when it ends:
- It waits while the lock is held, printing the holder every 30 s. Holding is judged by the flock and the holder's pid
  (with the start time ps gives it, so a reused pid is not taken for the holder), never by a pattern over command
  lines, which can match the waiting shell itself.
- A holder that died without releasing (its pid gone) left a stale record: the lock is taken, and says so. If the
  command that holder started still runs, the run waits for it.
- It waits while a Unity outside the lock has the project open: one holding unity/Temp/UnityLockfile open (lsof), or
  one whose -projectPath is unity/. Øystein's own editor counts: it says so and waits until the editor is closed.
- On SIGTERM, SIGINT or SIGHUP the signal goes to the command's process group, which has 20 s to stop; then the lock is
  released. A command still running by then keeps its pid in the record, and the next run waits for it.
- A command that already runs under the lock (a script that takes it, started by the holder) runs at once: its
  ancestor holds the lock.
- --timing also waits until no Blender batch process, no other Unity batch run and no player built from unity/ is
  running outside this command, and records the machine's background load as machine.json: the busiest processes
  before the run and during it (sampled every 30 s), Spotlight's among them, and the load average. It goes into --out,
  or with --out-runs into every folder matching GLOB in --out that the command made. It never waits for a quiet
  machine: Spotlight's mds_stores alone takes 30 to 40% of a core all the time.
- --max-wait gives up after that many seconds, with exit code 75 (the default is $UNITY_LOCK_MAX_WAIT, or no limit).
  Otherwise the exit code is the command's (128 + the signal for one stopped by a signal).

The owner defaults to $UNITY_LOCK_OWNER, which the lock passes on to the command, so a script it runs names the same
owner. status prints the holder, or "free", then anyone waiting and any Unity outside the lock that has the project
open; it exits 0 when a run could start now, 1 otherwise.

From Python (a Blender export's install step), the same lock around a with-block, held by this process:

    import unity_lock
    with unity_lock.installing(path):        # or unity_lock.held(purpose="...")
        ...

Standard library only; runs in the system's Python 3.9 and in Blender's. For tests, UNITY_LOCK_DIR and
UNITY_LOCK_PROJECT move the lock and the project checked, and UNITY_LOCK_EVERY and UNITY_LOCK_GRACE shorten the
30 s and 20 s (tools/tests/test_unity_lock.py).
"""
import argparse
import contextlib
import datetime
import errno
import fcntl
import glob
import json
import os
import re
import secrets
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
BUSY = 75                       # EX_TEMPFAIL: the lock or the project stayed busy past --max-wait
TOP = 12                        # the busiest processes a machine record names
SPOTLIGHT = ("mds", "mds_stores", "mdworker", "mdworker_shared", "mdsync", "mdbulkimport", "corespotlightd")
SIGNALS = (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)
_HELD = []                      # the locks this process holds: a held() inside another runs at once


def _seconds(name, default):
    try:
        return float(os.environ.get(name, default))
    except ValueError:
        return float(default)


EVERY = _seconds("UNITY_LOCK_EVERY", 30)     # how often a waiter prints, and a timing run samples the machine
GRACE = _seconds("UNITY_LOCK_GRACE", 20)     # how long a signalled command has to stop before the lock is released


def lock_dir():
    return os.path.abspath(os.environ.get("UNITY_LOCK_DIR") or os.path.join(REPO, ".locks"))


def project():
    """The Unity project this lock guards: unity/, resolved."""
    return os.path.realpath(os.environ.get("UNITY_LOCK_PROJECT") or os.path.join(REPO, "unity"))


def shown(path):
    """A path as a message names it: relative to the repo when inside it."""
    rel = os.path.relpath(path, os.path.realpath(REPO))
    return path if rel.startswith("..") else rel + "/"


def say(text):
    print("unity_lock: " + text, file=sys.stderr, flush=True)


def ago(seconds):
    s = int(max(0, seconds))
    if s < 60:
        return f"{s} s"
    if s < 3600:
        return f"{s // 60} min"
    return f"{s // 3600} h {s % 3600 // 60} min"


def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def short(text, n=110):
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[:n - 3] + "..."


# ---- processes, from ps (never pgrep -f: a pattern over command lines matches the shell that waits on it) ----

def _run(cmd, timeout=20):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=timeout,
                              env=dict(os.environ, LC_ALL="C")).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def processes():
    """Every process by pid: its parent, %CPU (of one core, ps's decaying average), %memory, executable and
    arguments."""
    procs = {}
    for line in _run(["ps", "-axww", "-o", "pid=,ppid=,pcpu=,pmem=,comm="]).splitlines():
        f = line.split(None, 4)
        if len(f) < 5:
            continue
        try:
            pid, ppid, cpu, mem = int(f[0]), int(f[1]), float(f[2]), float(f[3])
        except ValueError:
            continue
        procs[pid] = dict(pid=pid, ppid=ppid, cpu=cpu, mem=mem, exe=f[4].strip(), args="")
    for line in _run(["ps", "-axww", "-o", "pid=,args="]).splitlines():
        f = line.strip().split(None, 1)
        if f and f[0].isdigit() and int(f[0]) in procs:
            procs[int(f[0])]["args"] = f[1] if len(f) > 1 else ""
    return procs


def started(pid):
    """When the process started, as ps prints it, or None."""
    return " ".join(_run(["ps", "-o", "lstart=", "-p", str(pid)], 10).split()) or None


def alive(pid, start=None):
    """Whether pid runs (os.kill(pid, 0)) and, when its start is known, is the same process that started then."""
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        pass
    except OSError:
        return False
    if start:
        now = started(pid)
        if now and now != start:
            return False                    # the pid was reused
    return True


def ancestors(procs, pid):
    """pid and every process above it."""
    seen = set()
    while pid and pid not in seen:
        seen.add(pid)
        p = procs.get(pid)
        if p is None:
            break
        pid = p["ppid"]
    return seen


def descendants(procs, pid):
    """Every process below pid."""
    kids = {}
    for p in procs.values():
        kids.setdefault(p["ppid"], []).append(p["pid"])
    out, todo = set(), [pid]
    while todo:
        for k in kids.get(todo.pop(), ()):
            if k not in out:
                out.add(k)
                todo.append(k)
    return out


def lineage(procs, pid, depth=4):
    """The names of the processes above pid: 'zsh < claude'."""
    names, p = [], procs.get(procs.get(pid, {}).get("ppid", 0))
    while p and p["pid"] > 1 and len(names) < depth:
        names.append(name(p))
        p = procs.get(p["ppid"])
    return " < ".join(names) or "?"


def name(p):
    return os.path.basename(p["exe"]) or p["exe"]


def is_unity(p):
    return name(p) == "Unity"


def is_batch(p):
    return re.search(r"(?i)(?:^|\s)-batchmode(?:\s|$)", p["args"]) is not None


def is_blender_batch(p):
    return name(p).lower() == "blender" and re.search(r"(?:^|\s)(?:-b|--background)(?:\s|$)", p["args"]) is not None


def cwd_of(pid):
    for line in _run(["lsof", "-a", "-p", str(pid), "-d", "cwd", "-Fn"], 10).splitlines():
        if line.startswith("n"):
            return line[1:]
    return None


def opens(p, proj):
    """Whether a Unity process names proj as its project (-projectPath in any case; a relative path is resolved
    against the process's own directory)."""
    m = re.search(r"(?i)(?:^|\s)-projectpath\s+(\S+)", p["args"])
    if m:
        cand = os.path.expanduser(m.group(1).strip("\"'"))
        if not os.path.isabs(cand):
            cwd = cwd_of(p["pid"])
            cand = os.path.join(cwd, cand) if cwd else None
        if cand and os.path.realpath(cand) == proj:
            return True
    raw = os.path.abspath(os.environ.get("UNITY_LOCK_PROJECT") or os.path.join(REPO, "unity"))
    return any(re.search(r"(?:^|\s)" + re.escape(form.rstrip("/")) + r"/?(?:\s|$)", p["args"]) for form in {proj, raw})


def lockfile_users(proj):
    """The pids that have the project's Temp/UnityLockfile open (lsof), when it exists."""
    path = os.path.join(proj, "Temp", "UnityLockfile")
    if not os.path.exists(path):
        return []
    return [int(x) for x in _run(["lsof", "-t", "-w", "--", path], 15).split() if x.isdigit()]


def blockers(procs, proj, mine=(), ours=(), timing=False, lockfile=(), leftover=None):
    """What stops a run now, as (key, text) pairs: a Unity outside the lock with the project open, the last holder's
    command when it still runs and, with timing, any Blender batch process, Unity batch run or player built from the
    project. mine (this run's own ancestors and descendants) never counts; ours (the processes of the holder this run
    is nested in) may have the project open. Keyed on executables, never on a pattern over command lines."""
    skip = set(mine) | set(ours)
    found = []
    unity = {pid: p for pid, p in procs.items() if is_unity(p) and pid not in skip and opens(p, proj)}
    for pid in lockfile:
        if pid not in skip and pid not in unity:
            unity[pid] = procs.get(pid, dict(pid=pid, ppid=0, cpu=0.0, mem=0.0, exe="?", args=""))
    for pid, p in sorted(unity.items()):
        if p["ppid"] in unity:
            continue                        # an editor's import worker: the editor is named
        if is_unity(p) and not is_batch(p):
            found.append((("editor", pid), f"the Unity editor (pid {pid}) has {shown(proj)} open, most likely "
                          "Øystein's; batch mode cannot open a project that is open elsewhere, so this waits until "
                          "the editor is closed"))
        elif is_unity(p):
            found.append((("unity", pid), f"a Unity batch run outside the lock (pid {pid}) has {shown(proj)} open: "
                          + short(p["args"])))
        else:
            found.append((("lockfile", pid), f"{name(p)} (pid {pid}) has {shown(proj)}Temp/UnityLockfile open"))
    if leftover:
        found.append((("leftover", leftover[0]), leftover[1]))
    if timing:
        for pid, p in sorted(procs.items()):
            if pid in mine:
                continue
            if is_blender_batch(p):
                found.append((("blender", pid), f"a Blender batch process (pid {pid}) is running: " + short(p["args"])))
            elif is_unity(p) and is_batch(p) and pid not in unity and pid not in ours and not opens(p, proj):
                found.append((("unity-other", pid), f"a Unity batch run (pid {pid}) on another project is running: "
                              + short(p["args"])))
            elif p["exe"].startswith(proj + os.sep) and not is_unity(p):
                found.append((("player", pid), f"a player built from {shown(proj)} is running ({name(p)}, pid {pid})"))
    return found


# ---- the record: who holds the lock ----

def _record_path(d):
    return os.path.join(d, "unity.json")


def read_holder(d=None):
    try:
        with open(_record_path(d or lock_dir())) as fh:
            h = json.load(fh)
        return h if isinstance(h, dict) else None
    except (OSError, ValueError):
        return None


def _write_json(path, value):
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, "w") as fh:
        json.dump(value, fh, indent=1)
        fh.write("\n")
    os.replace(tmp, path)


def describe(h):
    if not h:
        return "an unnamed holder"
    since = h.get("since", "")
    length = f", {ago(time.time() - h['since_t'])}" if isinstance(h.get("since_t"), (int, float)) else ""
    return (f"{h.get('owner')}: {h.get('purpose')} (pid {h.get('pid')}, since {since[11:16]}{length}"
            f"{', timing' if h.get('timing') else ''})")


class Busy(Exception):
    """The lock or the project stayed busy past the longest wait."""


class Interrupted(Exception):
    def __init__(self, signum):
        super().__init__(signum)
        self.signum = signum


class Lock:
    """The Unity lock, held by this process from acquire() to release()."""

    def __init__(self, owner=None, purpose="", command=None, timing=False):
        self.owner = owner or os.environ.get("UNITY_LOCK_OWNER") or None
        self.purpose = purpose or short(" ".join(command or sys.argv), 200)
        self.command = list(command or sys.argv)
        self.timing = timing
        self.proj = project()
        self.dir = lock_dir()
        self.fd = None
        self.token = None
        self.record = None
        self.nested = None          # the holder's record, when this runs under the lock an ancestor holds
        self.inner = False          # True when this process already holds the lock

    def acquire(self, max_wait=None):
        if any(lk.fd is not None for lk in _HELD):
            self.inner = True
            return self
        os.makedirs(self.dir, exist_ok=True)
        procs = processes()
        self.owner = self.owner or f"unnamed (from {lineage(procs, os.getpid())})"
        self.nested = self._nested(procs)
        t0 = time.time()
        last_keys, last_t = None, 0.0
        try:
            while True:
                if self.nested:
                    found = self._blockers()
                    if not found:
                        return self
                else:
                    fd = self._flock()
                    if fd is None:
                        h = read_holder(self.dir)
                        found = [(("held", (h or {}).get("pid")), "the lock is held by " + describe(h))]
                    else:
                        self.fd = fd
                        last = read_holder(self.dir)
                        found = self._blockers(last)
                        if not found:
                            self._take(last, time.time() - t0)
                            return self
                        self.fd = None
                        os.close(fd)        # never hold the lock while waiting on others: they may need it to end
                now = time.time()
                if max_wait is not None and now - t0 >= max_wait:
                    raise Busy("; ".join(t for _, t in found))
                keys = [k for k, _ in found]
                if keys != last_keys or now - last_t >= EVERY:
                    say(f"{self.owner} waiting ({ago(now - t0)}): " + "; ".join(t for _, t in found))
                    self._waiting(found, t0)
                    last_keys, last_t = keys, now
                # the flock is cheap to try; ps and lsof, for other processes, less so
                time.sleep(1.0 if all(k[0] == "held" for k in keys) else 5.0)
        finally:
            self._unwait()

    def _nested(self, procs):
        pid_s, _, token = os.environ.get("UNITY_LOCK_HOLDER", "").partition(":")
        if not pid_s.isdigit() or not token:
            return None
        h = read_holder(self.dir)
        if not h or h.get("token") != token or h.get("pid") != int(pid_s) or h.get("released"):
            return None
        if int(pid_s) not in ancestors(procs, os.getpid()) or not alive(h["pid"], h.get("pid_start")):
            return None
        return h

    def _flock(self):
        path = os.path.join(self.dir, "unity.lock")
        fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o644)       # not inherited by the command (PEP 446)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as e:
            os.close(fd)
            if e.errno in (errno.EWOULDBLOCK, errno.EAGAIN, errno.EACCES):
                return None
            raise
        try:
            same = os.fstat(fd).st_ino == os.stat(path).st_ino
        except FileNotFoundError:
            same = False
        if not same:                        # the file was replaced while it was locked: lock the new one
            os.close(fd)
            return None
        return fd

    def _blockers(self, last=None):
        procs = processes()
        me = os.getpid()
        mine = ancestors(procs, me) | descendants(procs, me)
        ours = descendants(procs, self.nested["pid"]) if self.nested else set()
        leftover = None
        if last and not self.nested and last.get("pid") != me:
            child = last.get("child")
            if child and child not in mine and alive(child, last.get("child_start")):
                leftover = (child, f"the last holder's command still runs as pid {child} though its lock was released "
                                   f"({describe(last)})")
            elif not last.get("released") and alive(last.get("pid"), last.get("pid_start")):
                leftover = (last.get("pid"), f"the last holder still runs though the lock is free ({describe(last)})")
        return blockers(procs, self.proj, mine, ours, self.timing, lockfile_users(self.proj), leftover)

    def _take(self, last, waited):
        if last:
            say(f"taking a stale lock: its last holder is gone ({describe(last)})")
        procs = processes()
        self.token = secrets.token_hex(8)
        self.record = dict(owner=self.owner, purpose=self.purpose, pid=os.getpid(), pid_start=started(os.getpid()),
                           since=now_iso(), since_t=round(time.time(), 3), timing=self.timing,
                           command=self.command, cwd=os.getcwd(), parent=lineage(procs, os.getpid()),
                           child=None, child_start=None, token=self.token)
        _write_json(_record_path(self.dir), self.record)
        _HELD.append(self)
        if waited >= 2:
            say(f"{self.owner} has the lock, after {ago(waited)}")

    def set_child(self, pid):
        if self.fd is None:
            return
        self.record.update(child=pid, child_start=started(pid))
        _write_json(_record_path(self.dir), self.record)

    def release(self, child_alive=False):
        """Release the lock; when the command still runs, the record keeps its pid so the next run waits for it."""
        if self.fd is None:
            return
        try:
            cur = read_holder(self.dir)
            if cur and cur.get("token") == self.token:
                if child_alive:
                    _write_json(_record_path(self.dir), dict(self.record, released=now_iso()))
                else:
                    os.unlink(_record_path(self.dir))    # before the flock goes, so a new holder's record is safe
        except OSError:
            pass
        finally:
            os.close(self.fd)
            self.fd = None
            if self in _HELD:
                _HELD.remove(self)

    def child_env(self):
        env = dict(os.environ, UNITY_LOCK_OWNER=self.owner)
        if self.fd is not None:
            env["UNITY_LOCK_HOLDER"] = f"{os.getpid()}:{self.token}"
        return env

    def _waiting(self, found, t0):
        d = os.path.join(self.dir, "waiting")
        try:
            os.makedirs(d, exist_ok=True)
            _write_json(os.path.join(d, f"{os.getpid()}.json"),
                        dict(owner=self.owner, purpose=self.purpose, pid=os.getpid(), pid_start=started(os.getpid()),
                             since_t=round(t0, 3), why="; ".join(t for _, t in found)))
        except OSError:
            pass

    def _unwait(self):
        with contextlib.suppress(OSError):
            os.unlink(os.path.join(self.dir, "waiting", f"{os.getpid()}.json"))


def _max_wait(value=None):
    if value is not None:
        return value
    v = os.environ.get("UNITY_LOCK_MAX_WAIT")
    try:
        return float(v) if v else None
    except ValueError:
        return None


@contextlib.contextmanager
def held(owner=None, purpose="", timing=False, max_wait=None):
    """The Unity lock around a with-block, held by this process (a Blender export's install step). Raises Busy when
    max_wait (or $UNITY_LOCK_MAX_WAIT) seconds pass first. Inside a run that already holds it, it runs at once."""
    lk = Lock(owner, purpose, sys.argv, timing)
    lk.acquire(_max_wait(max_wait))
    try:
        yield lk
    finally:
        lk.release()


def installing(path):
    """held() for an install step that writes path into the project (a Blender export's FBX, sidecar and manifest)."""
    rel = os.path.relpath(os.path.abspath(path), REPO)
    return held(purpose="install " + (os.path.abspath(path) if rel.startswith("..") else rel))


# ---- the machine's background load, for timing runs ----

class Machine:
    """The busiest processes before a timing run and while it runs, by name only (no arguments: the record is kept
    beside the run's results in git)."""

    def __init__(self, proj):
        self.proj = proj
        self.t0 = time.time()
        self.started = now_iso()
        procs = processes()
        run = self._run(procs)
        self.before = self._snapshot(procs, run)
        self.open = sorted({self._note(p) for p in procs.values() if p["pid"] not in run and self._note(p)})
        self.cpu = {}               # (name, pid, part of the run) -> summed %CPU
        self.peak = {}
        self.loads = []
        self.samples = 0

    def _run(self, procs):
        me = os.getpid()
        return ({me} | descendants(procs, me)
                | {pid for pid, p in procs.items() if p["exe"].startswith(self.proj + os.sep)})

    def _note(self, p):
        if is_unity(p) and not is_batch(p):
            return "a Unity editor" + ("" if opens(p, self.proj) else " on another project")
        if name(p).lower() == "blender" and not is_blender_batch(p):
            return "Blender, interactive"
        return None

    @staticmethod
    def _row(p):
        return dict(name=name(p), pid=p["pid"], cpu=round(p["cpu"], 1), mem=round(p["mem"], 1))

    def _snapshot(self, procs, run):
        others = [p for pid, p in procs.items() if pid not in run]
        spot = [p for p in others if name(p) in SPOTLIGHT and p["cpu"] > 0]
        return dict(load=[round(x, 2) for x in os.getloadavg()],
                    top=[self._row(p) for p in sorted(others, key=lambda p: -p["cpu"])[:TOP]],
                    spotlight=[self._row(p) for p in sorted(spot, key=lambda p: -p["cpu"])],
                    spotlight_cpu=round(sum(p["cpu"] for p in spot), 1))

    def sample(self):
        procs = processes()
        run = self._run(procs)
        self.samples += 1
        self.loads.append(os.getloadavg()[0])
        for pid, p in procs.items():
            key = (name(p), pid, pid in run)
            self.cpu[key] = self.cpu.get(key, 0.0) + p["cpu"]
            self.peak[key] = max(self.peak.get(key, 0.0), p["cpu"])

    def result(self, lk, code):
        n = self.samples
        rows = sorted(((k, v / n) for k, v in self.cpu.items()), key=lambda kv: -kv[1]) if n else []

        def row(k, mean):
            return dict(name=k[0], pid=k[1], cpu_mean=round(mean, 1), cpu_max=round(self.peak[k], 1))
        during = dict(samples=n, every_s=EVERY)
        if n:
            during.update(load=dict(min=round(min(self.loads), 2), mean=round(sum(self.loads) / n, 2),
                                    max=round(max(self.loads), 2)),
                          top=[row(k, m) for k, m in rows if not k[2]][:TOP],
                          spotlight_cpu_mean=round(sum(m for k, m in rows if not k[2] and k[0] in SPOTLIGHT), 1),
                          run=[row(k, m) for k, m in rows if k[2]][:5])
        return dict(what="the machine's background load around a timing run (tools/unity_lock.py --timing): the "
                         "busiest processes by ps's %CPU (of one core), before the run and sampled during it, the "
                         "run's own processes apart",
                    owner=lk.owner, purpose=lk.purpose, command=lk.command, started=self.started, ended=now_iso(),
                    seconds=round(time.time() - self.t0), exit=code, cpus=os.cpu_count(),
                    memory_gb=_memory_gb(),
                    open=self.open, before=self.before, during=during)


def _memory_gb():
    v = _run(["sysctl", "-n", "hw.memsize"], 5).strip()
    return round(int(v) / 2 ** 30, 1) if v.isdigit() else None


def _targets(out, runs, before):
    if not runs:
        return [out]
    return [d for d in sorted(glob.glob(os.path.join(out, runs))) if os.path.isdir(d) and d not in before]


# ---- the commands ----

def cmd_run(a, command):
    if not command:
        say("run: give the command after --")
        return 2
    lk = Lock(a.owner, a.purpose, command, a.timing)
    received, state = [], dict(child=None, starting=False)

    def on_signal(signum, frame):
        received.append(signum)
        child = state["child"]
        if child is not None:
            with contextlib.suppress(OSError):
                os.killpg(child.pid, signum)
        elif not state["starting"]:
            raise Interrupted(signum)

    for s in SIGNALS:
        signal.signal(s, on_signal)
    machine, child, code, before = None, None, 0, set()
    out = os.path.abspath(a.out) if a.out else None
    t0 = time.time()
    try:
        lk.acquire(_max_wait(a.max_wait))
        if a.timing:
            machine = Machine(lk.proj)
            if out and a.out_runs:
                before = set(glob.glob(os.path.join(out, a.out_runs)))
            b = machine.before
            say("timing: load {} ({} cpus); busiest {}; Spotlight {}% of a core".format(
                b["load"][0], os.cpu_count(), ", ".join(f"{r['name']} {r['cpu']}%" for r in b["top"][:3]),
                b["spotlight_cpu"]))
        state["starting"] = True
        try:
            child = subprocess.Popen(command, env=lk.child_env(), start_new_session=True)
        except OSError as e:
            say(f"cannot run {command[0]}: {e}")
            code = 127
            return code
        state["child"], state["starting"] = child, False
        if received:
            with contextlib.suppress(OSError):
                os.killpg(child.pid, received[-1])
        lk.set_child(child.pid)
        code = _wait(child, machine, received)
    except Busy as e:
        say(f"gave up after {ago(time.time() - t0)}: {e}")
        code = BUSY
    except Interrupted as e:
        code = 128 + e.signum
    finally:
        for s in SIGNALS:
            signal.signal(s, signal.SIG_IGN)            # the clean-up is short: let it finish
        still = child is not None and child.poll() is None
        lk.release(child_alive=still)
        if machine and out:
            dirs = _targets(out, a.out_runs, before)
            for d in dirs:
                os.makedirs(d, exist_ok=True)
                _write_json(os.path.join(d, "machine.json"), machine.result(lk, code))
            if not dirs:
                say(f"no folder matching {a.out_runs} was made in {out}: no machine.json written")
    return code


def _wait(child, machine, received):
    deadline, next_sample = None, time.time() + EVERY
    while child.poll() is None:
        time.sleep(0.5)
        now = time.time()
        if received and deadline is None:
            deadline = now + GRACE
        if deadline is not None and now >= deadline and child.poll() is None:
            say(f"the command (pid {child.pid}) did not stop within {GRACE:.0f} s of the signal: the lock is "
                "released, and its record keeps the pid, so the next run waits for it")
            return 128 + received[0]
        if machine and now >= next_sample:
            machine.sample()
            next_sample = now + EVERY
    if received:
        return 128 + received[0]
    rc = child.returncode
    return rc if rc >= 0 else 128 - rc


def _probe(d):
    """True when someone holds the flock (a shared lock is refused)."""
    path = os.path.join(d, "unity.lock")
    if not os.path.exists(path):
        return False
    fd = os.open(path, os.O_RDONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
        fcntl.flock(fd, fcntl.LOCK_UN)
        return False
    except OSError:
        return True
    finally:
        os.close(fd)


def cmd_status(a):
    d, proj = lock_dir(), project()
    busy = _probe(d)
    h = read_holder(d)
    if busy and h is None:
        time.sleep(0.3)
        h = read_holder(d)
    free = False
    if busy:
        print("held by " + describe(h) if h else "held (its holder is not named yet)")
        if h:
            print(f"  command: {short(' '.join(h.get('command', [])), 200)}")
            print(f"  from: {h.get('parent')}, in {h.get('cwd')}")
    elif h and h.get("child") and alive(h["child"], h.get("child_start")):
        print(f"held: the last holder released the lock, but its command still runs as pid {h['child']}; runs wait "
              f"for it ({describe(h)})")
    elif h and not h.get("released") and alive(h.get("pid"), h.get("pid_start")):
        print(f"held: the last holder still runs though the lock is free; runs wait for it ({describe(h)})")
    else:
        free = True
        print("free")
        if h:
            print(f"  (a stale record from {describe(h)}: its pid is gone, so the next run takes it)")
    for f in sorted(glob.glob(os.path.join(d, "waiting", "*.json"))):
        try:
            with open(f) as fh:
                w = json.load(fh)
        except (OSError, ValueError):
            continue
        if not alive(w.get("pid"), w.get("pid_start")):
            with contextlib.suppress(OSError):
                os.unlink(f)
            continue
        print(f"waiting: {w.get('owner')}: {w.get('purpose')} (pid {w.get('pid')}, "
              f"for {ago(time.time() - w.get('since_t', time.time()))}): {w.get('why')}")
    procs = processes()
    ours = descendants(procs, h["pid"]) | {h["pid"]} if busy and h and isinstance(h.get("pid"), int) else set()
    for _, text in blockers(procs, proj, ancestors(procs, os.getpid()), ours, lockfile=lockfile_users(proj)):
        print("outside the lock: " + text)
        free = False
    return 0 if free else 1


def main(argv):
    opts, command = (argv[:argv.index("--")], argv[argv.index("--") + 1:]) if "--" in argv else (argv, [])
    p = argparse.ArgumentParser(prog="unity_lock.py", description="One job at a time on unity/.")
    sub = p.add_subparsers(dest="what")
    r = sub.add_parser("run", help="take the lock and run the command after --")
    r.add_argument("--owner", help="the session or agent (default: $UNITY_LOCK_OWNER)")
    r.add_argument("--purpose", help="what the run is for (default: the command)")
    r.add_argument("--timing", action="store_true",
                   help="also wait for no Blender batch, Unity batch or player of ours; record machine.json")
    r.add_argument("--out", help="the folder machine.json goes into (with --timing)")
    r.add_argument("--out-runs", help="instead: every folder matching this glob in --out that the command made")
    r.add_argument("--max-wait", type=float, help="give up after this many seconds (exit 75)")
    sub.add_parser("status", help="print the holder, or free")
    a = p.parse_args(opts)
    if a.what == "run":
        return cmd_run(a, command)
    if a.what == "status":
        return cmd_status(a)
    p.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
