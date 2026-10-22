"""Tests for the Unity lock (tools/unity_lock.py). A plain script; it never starts Unity or Blender (the commands run
under the lock are sleep, true and small Pythons), and it moves the lock and the project checked into a temporary
folder, so a real editor or run on unity/ neither blocks it nor is touched by it:

    python3 tools/tests/test_unity_lock.py

Exit 0 when every test passes.
"""
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
LOCK = os.path.join(TOOLS, "unity_lock.py")
sys.path.insert(0, TOOLS)
import unity_lock as UL  # noqa: E402

TMP = tempfile.mkdtemp(prefix="unity-lock-test-")
PROJ = os.path.realpath(os.path.join(TMP, "proj"))
LOCKS = os.path.join(TMP, "locks")
ENV = dict(os.environ, UNITY_LOCK_DIR=LOCKS, UNITY_LOCK_PROJECT=PROJ, UNITY_LOCK_EVERY="1", UNITY_LOCK_GRACE="3")
for k in ("UNITY_LOCK_HOLDER", "UNITY_LOCK_REEXEC", "UNITY_LOCK_OWNER", "UNITY_LOCK_MAX_WAIT"):
    ENV.pop(k, None)
os.makedirs(PROJ)


def lock(*args, wait=True, timeout=60):
    """unity_lock.py with args: (exit code, stdout, stderr), or the Popen when not waited for."""
    p = subprocess.Popen([sys.executable, LOCK, *args], env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True)
    if not wait:
        return p
    out, err = p.communicate(timeout=timeout)
    return p.returncode, out, err


def status():
    code, out, _ = lock("status")
    return code, out


def until(test, timeout=15, what="the condition"):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if test():
            return
        time.sleep(0.1)
    raise AssertionError(f"timed out waiting for {what}")


def holder():
    try:
        with open(os.path.join(LOCKS, "unity.json")) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def stamp(log):
    """A command that writes its start and end times to log, sleeping 0.8 s between."""
    return [sys.executable, "-c", "import sys, time\n"
            f"f = open({log!r}, 'a'); f.write('start %r\\n' % time.time()); f.flush()\n"
            "time.sleep(0.8)\n"
            "f.write('end %r\\n' % time.time()); f.close()"]


def dead_pid():
    p = subprocess.Popen(["true"])
    p.wait()
    return p.pid


# ---- the tests ----

def test_status_free():
    code, out = status()
    assert code == 0 and out.splitlines()[0] == "free", out


def test_concurrent_runs_serialise():
    logs = [os.path.join(TMP, f"serial-{i}.log") for i in range(3)]
    runs = [lock("run", "--owner", f"run {i}", "--purpose", "serialise", "--", *stamp(logs[i]), wait=False)
            for i in range(3)]
    errs = [p.communicate(timeout=60)[1] for p in runs]
    assert all(p.returncode == 0 for p in runs), [p.returncode for p in runs]
    spans = []
    for log in logs:
        with open(log) as fh:
            t = dict(line.split() for line in fh)
        spans.append((float(t["start"]), float(t["end"])))
    spans.sort()
    for (s0, e0), (s1, e1) in zip(spans, spans[1:]):
        assert s1 >= e0, f"overlap: {spans}"
    assert sum("waiting" in e and "held by run" in e for e in errs) >= 2, errs


def test_status_names_holder():
    p = lock("run", "--owner", "status test", "--purpose", "holding", "--", "sleep", "2", wait=False)
    until(lambda: holder() is not None, what="the holder's record")
    code, out = status()
    first = out.splitlines()[0]
    assert code == 1 and first.startswith("held by status test: holding (pid "), out
    assert "command: sleep 2" in out, out
    p.communicate(timeout=30)
    code, out = status()
    assert code == 0 and out.splitlines() == ["free"], out
    assert holder() is None


def test_stale_lock_taken():
    # a holder that died without releasing: its record stays, naming a pid that is gone
    UL._write_json(os.path.join(LOCKS, "unity.json"),
                   dict(owner="ghost", purpose="died", pid=dead_pid(), since="2026-10-22T09:00:00+02:00",
                        since_t=time.time() - 600, token="feedface", child=None))
    code, out = status()
    assert code == 0 and out.splitlines()[0] == "free" and "stale record from ghost" in out, out
    code, out, err = lock("run", "--owner", "taker", "--max-wait", "5", "--", "true")
    assert code == 0, (code, err)
    assert "taking a stale lock" in err and "ghost" in err, err
    assert holder() is None and status() == (0, "free\n")
    # a pid reused by another process (here, this test's own) is not the holder: its start time differs
    UL._write_json(os.path.join(LOCKS, "unity.json"),
                   dict(owner="reused", purpose="died", pid=os.getpid(), pid_start="Mon Jan  1 00:00:00 2001",
                        token="feedface", child=None))
    code, out, err = lock("run", "--owner", "taker", "--max-wait", "5", "--", "true")
    assert code == 0 and "taking a stale lock" in err and "reused" in err, (code, err)


def test_no_self_match():
    # The waiter's own command line names the lock file, the project and Unity and Blender in batch mode, and a log
    # watcher tails the lock file, as `until ! pgrep -f ...` loops met them: the waiter must still go once it is free.
    lockfile = os.path.join(LOCKS, "unity.lock")
    words = f"until ! pgrep -f {lockfile}; Unity -batchmode -projectPath {PROJ}; Blender -b"
    watcher = subprocess.Popen(["tail", "-f", lockfile], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        h = lock("run", "--owner", "first", "--", "sleep", "1.5", wait=False)
        until(lambda: holder() is not None, what="the first holder")
        t0 = time.time()
        code, out, err = lock("run", "--owner", "waiter", "--purpose", words, "--max-wait", "20", "--",
                              "sh", "-c", f"echo '{words}'", timeout=40)
        h.communicate(timeout=30)
        assert code == 0 and words in out, (code, out, err)
        assert "held by first" in err and time.time() - t0 < 10, err
    finally:
        watcher.kill()
        watcher.wait()


def test_blockers_count_executables_not_command_lines():
    me = 900
    unity = "/Applications/Unity/Hub/Editor/6000.6.6f1/Unity.app/Contents/MacOS/Unity"
    procs = {p["pid"]: dict(cpu=0.0, mem=0.0, **p) for p in [
        dict(pid=100, ppid=1, exe=unity, args=f"{unity} -projectpath {PROJ} -useHub -hubIPC"),
        dict(pid=101, ppid=100, exe=unity, args=f"{unity} -batchMode -name AssetImportWorker0 -projectPath {PROJ}"),
        dict(pid=200, ppid=1, exe="/bin/zsh",
             args=f"zsh -c until ! pgrep -f 'Unity -batchmode -projectPath {PROJ}'; do sleep 5; done; Blender -b"),
        dict(pid=201, ppid=1, exe="/usr/bin/tail", args=f"tail -f {PROJ}/Builds/Perf/build.log"),
        dict(pid=300, ppid=1, exe="/Applications/Blender.app/Contents/MacOS/Blender",
             args="/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python stone.py"),
        dict(pid=301, ppid=1, exe="/Applications/Blender.app/Contents/MacOS/Blender",
             args="/Applications/Blender.app/Contents/MacOS/Blender"),
        dict(pid=400, ppid=1, exe="/System/Library/Frameworks/CoreServices.framework/Frameworks/Metadata.framework/"
                                  "Versions/A/Support/mds_stores", args="mds_stores"),
        dict(pid=500, ppid=1, exe=unity, args=f"{unity} -batchmode -quit -projectPath {PROJ}"),
        dict(pid=me, ppid=500, exe="/usr/bin/python3", args=f"python3 unity_lock.py run -- Unity -projectPath {PROJ}"),
        dict(pid=600, ppid=1, exe=f"{PROJ}/Builds/Perf/Overstory.app/Contents/MacOS/Overstory", args="Overstory"),
    ]}
    mine = UL.ancestors(procs, me)
    plain = UL.blockers(procs, PROJ, mine)
    assert [k for k, _ in plain] == [("editor", 100)], plain
    assert "Unity editor (pid 100)" in plain[0][1] and "Øystein" in plain[0][1], plain
    timing = [k for k, _ in UL.blockers(procs, PROJ, mine, timing=True)]
    assert timing == [("editor", 100), ("blender", 300), ("player", 600)], timing
    # the editor is the holder's own (a nested run): it is not counted
    assert UL.blockers(procs, PROJ, mine, ours={100, 101}) == []


def test_unity_lockfile_open_blocks():
    temp = os.path.join(PROJ, "Temp")
    os.makedirs(temp, exist_ok=True)
    path = os.path.join(temp, "UnityLockfile")
    open(path, "w").close()
    keeper = subprocess.Popen([sys.executable, "-c", f"import time; f = open({path!r}); time.sleep(60)"])
    try:
        until(lambda: keeper.pid in UL.lockfile_users(PROJ), what="lsof to see the open UnityLockfile")
        code, _, err = lock("run", "--owner", "blocked", "--max-wait", "2", "--", "true")
        assert code == UL.BUSY and "Temp/UnityLockfile open" in err, (code, err)
    finally:
        keeper.kill()
        keeper.wait()
    # a UnityLockfile no process has open is what a crashed Unity leaves: it does not block
    code, _, err = lock("run", "--owner", "after", "--max-wait", "5", "--", "true")
    assert code == 0, (code, err)
    shutil.rmtree(temp)


def test_sigterm_releases():
    p = lock("run", "--owner", "signalled", "--", "sleep", "30", wait=False)
    until(lambda: (holder() or {}).get("child"), what="the command's pid in the record")
    child = holder()["child"]
    t0 = time.time()
    p.send_signal(signal.SIGTERM)
    p.communicate(timeout=20)
    assert p.returncode == 128 + signal.SIGTERM, p.returncode
    assert time.time() - t0 < 5, "the signal was not passed on to the command"
    assert not UL.alive(child), "the command survived the signal"
    assert holder() is None and status() == (0, "free\n")
    code, _, err = lock("run", "--owner", "next", "--max-wait", "0", "--", "true")
    assert code == 0, (code, err)


def test_sigterm_while_waiting():
    h = lock("run", "--owner", "first", "--", "sleep", "3", wait=False)
    until(lambda: holder() is not None, what="the first holder")
    w = lock("run", "--owner", "waiter", "--", "true", wait=False)
    until(lambda: os.path.exists(os.path.join(LOCKS, "waiting", f"{w.pid}.json")), what="the waiter's note")
    w.send_signal(signal.SIGTERM)
    w.communicate(timeout=10)
    assert w.returncode == 128 + signal.SIGTERM, w.returncode
    assert not os.path.exists(os.path.join(LOCKS, "waiting", f"{w.pid}.json"))
    h.communicate(timeout=30)
    assert status() == (0, "free\n")


def test_nested_run_goes_at_once():
    inner = [sys.executable, LOCK, "run", "--owner", "inner", "--max-wait", "2", "--", "sh", "-c",
             "echo inner ran as $UNITY_LOCK_OWNER"]
    code, out, err = lock("run", "--owner", "outer", "--", *inner)
    assert code == 0 and "inner ran as inner" in out, (code, out, err)
    # the same command line, not under the holder, waits
    h = lock("run", "--owner", "holder", "--", "sleep", "3", wait=False)
    until(lambda: holder() is not None, what="the holder")
    p = subprocess.run(inner, env=dict(ENV, UNITY_LOCK_HOLDER=f"{h.pid}:not-its-token"), capture_output=True,
                       text=True, timeout=30)
    assert p.returncode == UL.BUSY and "held by holder" in p.stderr, (p.returncode, p.stderr)
    h.communicate(timeout=30)


def test_timing_writes_machine_json():
    out = os.path.join(TMP, "perf")
    os.makedirs(os.path.join(out, "run-1"))
    code, _, err = lock("run", "--owner", "timing", "--timing", "--out", out, "--out-runs", "run-*", "--max-wait",
                        "3", "--", "sh", "-c", f"sleep 1.5; mkdir {out}/run-2")
    if code == UL.BUSY and "Blender batch" in err:
        print("  (skipped: a Blender batch process is running on this machine, and timing runs wait for it)")
        return
    assert code == 0, (code, err)
    assert not os.path.exists(os.path.join(out, "run-1", "machine.json")), "an earlier run's folder was written"
    with open(os.path.join(out, "run-2", "machine.json")) as fh:
        m = json.load(fh)
    assert m["owner"] == "timing" and m["exit"] == 0 and m["before"]["top"], m
    assert {"load", "top", "spotlight", "spotlight_cpu"} <= set(m["before"]) and m["during"]["samples"] >= 1, m
    assert all(set(r) == {"name", "pid", "cpu", "mem"} for r in m["before"]["top"]), "a record names more than names"


def test_script_header_reruns_under_the_lock():
    # tools/perf.sh's own header (up to its first fi), with a body that makes a run folder: run directly, and by a
    # holder of the lock (it must nest, and still take its own timing wrapper)
    rep = os.path.join(TMP, "rep")
    os.makedirs(os.path.join(rep, "tools"))
    shutil.copy(LOCK, os.path.join(rep, "tools"))
    with open(os.path.join(TOOLS, "perf.sh")) as fh:
        lines = fh.read().splitlines()
    head = lines[:next(i for i, line in enumerate(lines) if line == "fi") + 1]
    script = os.path.join(rep, "tools", "perf.sh")
    with open(script, "w") as fh:
        fh.write("\n".join(head) + '\necho "body as $UNITY_LOCK_OWNER"\nmkdir -p $R/reviews/perf/t/run-1\n')
    for outer in ([], [sys.executable, LOCK, "run", "--owner", "outer", "--max-wait", "5", "--"]):
        shutil.rmtree(os.path.join(rep, "reviews"), ignore_errors=True)
        p = subprocess.run(outer + ["zsh", script, "-out", "reviews/perf/t"], env=dict(ENV, UNITY_LOCK_OWNER="direct"),
                           capture_output=True, text=True, timeout=60)
        if p.returncode == UL.BUSY and "Blender batch" in p.stderr:
            print("  (skipped: a Blender batch process is running on this machine, and timing runs wait for it)")
            return
        assert p.returncode == 0 and "timing: load" in p.stderr, (p.returncode, p.stderr)
        assert f"body as {'outer' if outer else 'direct'}" in p.stdout, p.stdout
        assert os.path.exists(os.path.join(rep, "reviews", "perf", "t", "run-1", "machine.json"))


def main():
    tests = [(k, v) for k, v in globals().items() if k.startswith("test_") and callable(v)]
    failed = 0
    try:
        for k, fn in tests:
            try:
                fn()
                print("PASS", k)
            except Exception:
                failed += 1
                print("FAIL", k)
                traceback.print_exc()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print(f"{len(tests) - failed} of {len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
