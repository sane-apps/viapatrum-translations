#!/usr/bin/env python3
"""Tests for sealed_run.py. No network use, no real model: the loop tests use a scripted fake ask().

Every "cannot" test shows the forbidden thing failing INSIDE the sandbox while a control shows it would have worked
outside (or, where doing it outside is not allowed, such as network use or starting `security`, that the failure
is the sandbox's own "Operation not permitted" and that an allowed neighbour runs). Scripts print only DENIED /
LEAK / OTHER words, never the contents of a real file.

Run: /opt/homebrew/bin/python3 -m unittest scripts/test_sealed_run.py -v   (from the translations repo root)
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import uuid
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sealed_run as sr  # noqa: E402

PY = sr.DEFAULT_PYTHON
VENV_PY = os.path.expanduser("~/.venvs/sz-audit-check/bin/python")
VENV = os.path.expanduser("~/.venvs/sz-audit-check")
HOME = sr.HOME
SCRATCH = os.path.realpath(tempfile.mkdtemp(prefix="sealed-test-"))  # mode 0700, ours alone


MADE: list[str] = []  # every folder this module made, so their harness folders can be removed too


def tearDownModule():
    for p in MADE:  # only the harness folders of our own test job folders
        try:
            sd = sr.state_dir(p, create=False)
        except sr.SealError:
            sd = None
        if sd:
            shutil.rmtree(sd, ignore_errors=True)
    shutil.rmtree(SCRATCH, ignore_errors=True)  # only the folder this module made


def mkdir700(name: str) -> str:
    p = os.path.join(SCRATCH, f"{name}-{uuid.uuid4().hex[:8]}")
    os.mkdir(p, 0o700)
    MADE.append(os.path.realpath(p))
    return p


def sealed_py(job, code, ro=(), interp=PY, timeout=60, args=()):
    path = os.path.join(job, f"t-{uuid.uuid4().hex[:6]}.py")
    Path(path).write_text(code)
    return sr.run_sealed([interp, "-I", path] + list(args), job, ro, timeout_s=timeout)


def outside_py(code, interp=PY, timeout=60, args=()):
    d = mkdir700("outside")
    path = os.path.join(d, "t.py")
    Path(path).write_text(code)
    p = subprocess.run([interp, "-I", path] + list(args), capture_output=True, text=True, timeout=timeout,
                       stdin=subprocess.DEVNULL, cwd=d)
    return p.stdout + p.stderr


# Tries each (kind, path); prints one word per item, never file contents.
PROBE = r'''
import json, os, sys
for kind, p in json.loads(sys.argv[1]):
    try:
        if kind == "read":
            open(p, "rb").close()
        elif kind == "list":
            os.listdir(p)
        elif kind == "write":
            with open(p, "w") as f:
                f.write("x")
        print("LEAK", p)
    except PermissionError:
        print("DENIED", p)
    except OSError as e:
        print("OTHER", e.errno, p)
'''


def words(out: str) -> dict:
    res = {}
    for line in out.splitlines():
        bits = line.split(" ")
        if bits and bits[0] in ("LEAK", "DENIED", "OTHER", "RAN"):
            res[bits[-1]] = bits[0]
    return res


class Fake:
    """A scripted model: returns the answers in order and keeps every prompt."""

    def __init__(self, answers):
        self.answers = list(answers)
        self.prompts = []

    def __call__(self, prompt):
        self.prompts.append(prompt)
        if not self.answers:
            raise RuntimeError("fake model has no more answers")
        a = self.answers.pop(0)
        if isinstance(a, Exception):
            raise a
        return a


def log_rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines()]


def kill_exact(test, job, pid):
    """Sweep only when the stray finder names exactly the process we expect, so a wrong match kills nothing."""
    found = sr.find_strays(job)
    test.assertEqual(found, [pid], "stray finder must name exactly our stray (nothing was killed)")
    s = sr.sweep_strays(job)
    test.assertEqual(s["survivors"], [])
    gone(test, pid)


def gone(test, pid, wait=3.0):
    deadline = time.time() + wait
    while time.time() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return
        if sr._is_zombie(pid):
            return
        time.sleep(0.1)
    test.fail(f"process {pid} still alive")


class T01Basics(unittest.TestCase):
    def test_write_run_read_back(self):
        job = mkdir700("job")
        r = sealed_py(job, "open('made.txt','w').write(str(6*7))\nprint('ran')\n")
        self.assertEqual(r["rc"], 0, r["output"])
        self.assertIn("ran", r["output"])
        self.assertEqual(Path(job, "made.txt").read_text(), "42")
        self.assertFalse(r["timed_out"])
        self.assertFalse(r["truncated"])

    def test_sh_runs(self):
        job = mkdir700("job")
        Path(job, "s.sh").write_text("echo hello > h.txt\ncat h.txt\n")
        r = sr.run_sealed(["/bin/sh", os.path.join(job, "s.sh")], job)
        self.assertEqual((r["rc"], r["output"].strip()), (0, "hello"))


class T02Venv(unittest.TestCase):
    def test_numpy_pandas_statsmodels(self):
        if not os.path.exists(VENV_PY):
            self.skipTest(f"{VENV_PY} missing: cannot test the virtual environment")
        job = mkdir700("job")
        code = ("import numpy as np, pandas as pd, scipy.stats, statsmodels.api as sm\n"
                "x = np.arange(10.0); y = 2 * x + 1\n"
                "fit = sm.OLS(y, sm.add_constant(x)).fit()\n"
                "df = pd.DataFrame({'g': list('aabb'), 'v': [1, 2, 3, 4]})\n"
                "print('SLOPE %.6f' % fit.params[1], 'SUMB', df.groupby('g').v.sum()['b'])\n")
        r = sealed_py(job, code, ro=[VENV], interp=VENV_PY)
        self.assertEqual(r["rc"], 0, r["output"])
        self.assertIn("SLOPE 2.000000 SUMB 7", r["output"])


class T03NoReadOutside(unittest.TestCase):
    def test_canary_and_home(self):
        job, other = mkdir700("job"), mkdir700("other")
        canary = os.path.join(other, "canary.txt")
        Path(canary).write_text("CANARY-" + uuid.uuid4().hex)
        items = [("read", canary), ("list", other)]
        for kind, p in [("list", os.path.join(HOME, ".config")), ("list", os.path.join(HOME, "SaneApps")),
                        ("read", os.path.join(HOME, ".zsh_history")), ("list", os.path.join(HOME, ".ssh")),
                        ("list", HOME), ("list", os.path.join(HOME, "Library", "Keychains"))]:
            if os.path.exists(p):
                items.append((kind, p))
            else:
                print(f"\n  (skipped {p}: not on this Mac)")
        arg = [json.dumps(items)]
        inside = words(sealed_py(job, PROBE, args=arg)["output"])
        control = words(outside_py(PROBE, args=arg))
        for _, p in items:
            self.assertEqual(control.get(p), "LEAK", f"control: {p} should be readable outside")
            self.assertEqual(inside.get(p), "DENIED", f"{p} must be denied inside")
        # the sandboxed script also cannot print the canary's text
        r = sealed_py(job, f"print(open({canary!r}).read())")
        self.assertNotEqual(r["rc"], 0)
        self.assertNotIn("CANARY-", r["output"])

    def test_ro_root_readable_but_not_beside_it(self):
        job, ro, beside = mkdir700("job"), mkdir700("ro"), mkdir700("beside")
        Path(ro, "data.csv").write_text("a,b\n1,2\n")
        Path(beside, "x.txt").write_text("x")
        arg = [json.dumps([("read", os.path.join(ro, "data.csv")), ("read", os.path.join(beside, "x.txt"))])]
        got = words(sealed_py(job, PROBE, ro=[ro], args=arg)["output"])
        self.assertEqual(got[os.path.join(ro, "data.csv")], "LEAK")  # allowed: it is an ro_root
        self.assertEqual(got[os.path.join(beside, "x.txt")], "DENIED")


class T04NoWriteOutside(unittest.TestCase):
    def test_writes(self):
        job, other, ro = mkdir700("job"), mkdir700("other"), mkdir700("ro")
        targets = [os.path.join(other, "w.txt"), os.path.join(ro, "w.txt")]
        arg = [json.dumps([("write", t) for t in targets])]
        control = words(outside_py(PROBE, args=arg))
        for t in targets:
            self.assertEqual(control[t], "LEAK", "control: writable outside")
            os.unlink(t)  # the control's own file
        home_t = os.path.join(HOME, f".sealed-test-{uuid.uuid4().hex}")
        self.assertTrue(os.access(HOME, os.W_OK), "control: home is writable outside")
        inside = words(sealed_py(job, PROBE, ro=[ro], args=[json.dumps([("write", t) for t in targets + [home_t]])])
                       ["output"])
        for t in targets + [home_t]:
            self.assertEqual(inside[t], "DENIED", t)
            self.assertFalse(os.path.exists(t), t)


KEYCHAIN = r'''
import ctypes, uuid
sec = ctypes.CDLL("/System/Library/Frameworks/Security.framework/Security")
cf = ctypes.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
ref = ctypes.c_void_p()
print("DEFAULT", sec.SecKeychainCopyDefault(ctypes.byref(ref)))
cf.CFStringCreateWithCString.restype = ctypes.c_void_p
cf.CFStringCreateWithCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32]
cf.CFDictionaryCreate.restype = ctypes.c_void_p
cf.CFDictionaryCreate.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long,
                                  ctypes.c_void_p, ctypes.c_void_p]
svc = cf.CFStringCreateWithCString(None, ("sealed-run-test-" + uuid.uuid4().hex).encode(), 0x08000100)
keys = (ctypes.c_void_p * 2)(ctypes.c_void_p.in_dll(sec, "kSecClass").value,
                             ctypes.c_void_p.in_dll(sec, "kSecAttrService").value)
vals = (ctypes.c_void_p * 2)(ctypes.c_void_p.in_dll(sec, "kSecClassGenericPassword").value, svc)
d = cf.CFDictionaryCreate(None, keys, vals, 2,
                          ctypes.addressof(ctypes.c_char.in_dll(cf, "kCFTypeDictionaryKeyCallBacks")),
                          ctypes.addressof(ctypes.c_char.in_dll(cf, "kCFTypeDictionaryValueCallBacks")))
res = ctypes.c_void_p()
sec.SecItemCopyMatching.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
print("ITEM", sec.SecItemCopyMatching(d, ctypes.byref(res)))
'''


def codes(out):
    return {line.split()[0]: int(line.split()[1]) for line in out.splitlines()
            if line.split()[:1] in (["DEFAULT"], ["ITEM"])}


class T05NoKeychain(unittest.TestCase):
    def test_security_tool_cannot_start(self):
        job = mkdir700("job")
        self.assertTrue(os.access("/usr/bin/security", os.X_OK), "control: the tool exists here")
        # Never started outside (house rule); the control is that an allowed neighbour starts inside.
        r = sr.run_sealed(["/bin/sh", "-c", "/usr/bin/true && echo TRUE-RAN; /usr/bin/security list-keychains; "
                           "echo rc=$?"], job, timeout_s=20)
        self.assertIn("TRUE-RAN", r["output"])
        self.assertIn("Operation not permitted", r["output"])
        self.assertIn("rc=126", r["output"])
        self.assertNotIn(".keychain", r["output"])

    def test_security_framework_refused_without_dialog(self):
        job = mkdir700("job")
        control = codes(outside_py(KEYCHAIN, timeout=30))
        self.assertEqual(control.get("DEFAULT"), 0, f"control: keychain reachable outside {control}")
        self.assertEqual(control.get("ITEM"), -25300, f"control: made-up item not found outside {control}")
        r = sealed_py(job, KEYCHAIN, timeout=20)
        self.assertFalse(r["timed_out"], "a hang may mean a dialog: fail")
        inside = codes(r["output"])
        print(f"\n  keychain codes inside: {inside} (rc {r['rc']})")
        # -25300 inside would mean the keychain was actually searched; 0 would mean it answered.
        self.assertNotIn(inside.get("ITEM", 1), (0, -25300), r["output"][-500:])
        self.assertTrue(inside.get("DEFAULT", 1) != 0 or "ITEM" in inside)


NET = r'''
import socket
try:
    socket.create_connection(("1.1.1.1", 443), timeout=5).close()
    print("LEAK tcp")
except PermissionError:
    print("DENIED tcp")
except OSError as e:
    print("OTHER", e.errno, "tcp")
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(b"x", ("1.1.1.1", 53))
    print("LEAK udp")
except PermissionError:
    print("DENIED udp")
except OSError as e:
    print("OTHER", e.errno, "udp")
try:
    socket.getaddrinfo("example.com", 443)
    print("LEAK dns")
except PermissionError:
    print("DENIED dns")
except OSError as e:
    print("DENIED dns-failed", e)
'''


class T06NoNetwork(unittest.TestCase):
    def test_tcp_udp_dns(self):
        # No outside control: the brief forbids network use. EPERM ("Operation not permitted") is the
        # sandbox's own answer; a dead network gives unreachable or a timeout instead.
        job = mkdir700("job")
        r = sealed_py(job, NET, timeout=30)
        got = r["output"]
        self.assertIn("DENIED tcp", got)
        self.assertIn("DENIED udp", got)
        self.assertIn("DENIED dns", got)
        self.assertNotIn("LEAK", got)


EXEC = r'''
import json, subprocess, sys
for argv in json.loads(sys.argv[1]):
    try:
        r = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, timeout=10)
        print("RAN", r.returncode, argv[0])
    except PermissionError:
        print("DENIED", argv[0])
    except OSError as e:
        print("OTHER", e.errno, argv[0])
'''


class T07NoForbiddenPrograms(unittest.TestCase):
    def test_programs(self):
        job = mkdir700("job")
        banned = [["/usr/bin/open", "-h"], ["/usr/bin/osascript", "-e", "1"], ["/usr/bin/curl", "--version"],
                  ["/usr/bin/ssh", "-V"], ["/usr/bin/pbpaste"], ["/bin/launchctl", "version"]]
        for argv in banned:
            self.assertTrue(os.access(argv[0], os.X_OK), f"control: {argv[0]} exists and is executable")
        shutil.copy("/usr/bin/true", os.path.join(job, "mytrue"))
        argvs = [["/usr/bin/true"]] + banned + [[os.path.join(job, "mytrue")]]
        got = words(sealed_py(job, EXEC, args=[json.dumps(argvs)])["output"])
        self.assertEqual(got["/usr/bin/true"], "RAN", "control: an allowed program starts inside")
        for argv in banned:
            self.assertEqual(got[argv[0]], "DENIED", argv[0])
        # a program copied into the job folder cannot be started either
        self.assertEqual(got[os.path.join(job, "mytrue")], "DENIED")


class T08Timeout(unittest.TestCase):
    def test_killed_with_children(self):
        job = mkdir700("job")
        Path(job, "slow.sh").write_text("sleep 300 &\necho $! > kids.txt\n(sleep 300; echo) &\necho $! >> kids.txt\n"
                                        "sleep 300\n")
        t = time.time()
        r = sr.run_sealed(["/bin/sh", os.path.join(job, "slow.sh")], job, timeout_s=3)
        self.assertTrue(r["timed_out"])
        self.assertLess(time.time() - t, 30)
        kids = [int(x) for x in Path(job, "kids.txt").read_text().split()]
        self.assertEqual(len(kids), 2)
        for pid in kids:
            gone(self, pid)


class T09OutputCap(unittest.TestCase):
    def test_cut(self):
        job = mkdir700("job")
        r = sr.run_sealed([PY, "-I", "-c", "print('A' * 100000); print('END-MARK')"], job, max_output_bytes=1000)
        self.assertTrue(r["truncated"])
        self.assertIn("[cut: ", r["output"])
        self.assertIn("END-MARK", r["output"])  # the end, where errors land, is kept
        self.assertLess(len(r["output"]), 1100)


class T10Refusals(unittest.TestCase):
    def test_refuse(self):
        loose = os.path.join(SCRATCH, "loose-" + uuid.uuid4().hex[:6])
        os.mkdir(loose)
        os.chmod(loose, 0o755)
        with self.assertRaises(sr.SealError):
            sr.run_sealed(["/usr/bin/true"], loose)
        with self.assertRaises(sr.SealError):
            sr.run_sealed(["/usr/bin/true"], HOME)
        job = mkdir700("job")
        for bad in ("/Users", HOME, "/", "/Volumes", os.path.join(HOME, ".ssh"), os.path.join(HOME, "Library")):
            with self.assertRaises(sr.SealError, msg=bad):
                sr.run_sealed(["/usr/bin/true"], job, ro_roots=[bad])
        with mock.patch.object(sr, "SANDBOX_EXEC", "/nonexistent/sandbox-exec"):
            with self.assertRaises(sr.SealError):
                sr.run_sealed(["/usr/bin/true"], job)
        ssh = os.path.join(HOME, ".ssh")
        if os.path.isdir(ssh):  # 0700 and ours, so only the secret-folder rule refuses it
            with self.assertRaises(sr.SealError):
                sr.check_job_dir(ssh)


class T11Loop(unittest.TestCase):
    def loop(self, answers, **kw):
        job = kw.pop("job", None) or mkdir700("job")
        fake = Fake(answers)
        res = sr.work_loop(fake, "test task", job, timeout_s=kw.pop("timeout_s", 30), **kw)
        return job, fake, res

    def test_a_write_run_done(self):
        job, fake, res = self.loop([
            "Plan first.\n@@WRITE calc.py\nopen('out.txt','w').write(str(6*7))\nprint('ok', 6*7)\n@@END\n"
            "@@RUN python calc.py",
            "@@READ out.txt",
            "@@DONE\nThe answer is 42\n@@END"])
        self.assertEqual(res["stopped"], "done")
        self.assertEqual(res["final"], "The answer is 42")
        self.assertEqual(res["turns"], 3)
        self.assertEqual(Path(job, "out.txt").read_text(), "42")
        self.assertIn("ok 42", fake.prompts[1])
        self.assertIn("1: 42", fake.prompts[2])
        self.assertIn("# Task\ntest task", fake.prompts[0])

    def test_b_bad_write_paths(self):
        outside = os.path.join(mkdir700("other"), "abs.py")
        job, fake, res = self.loop(["@@WRITE ../x.py\nprint(1)\n@@END", f"@@WRITE {outside}\nprint(1)\n@@END",
                                    "@@DONE\nx\n@@END"])
        self.assertIn("refused", fake.prompts[1])
        self.assertIn("'..'", fake.prompts[1])
        self.assertIn("refused", fake.prompts[2].split("## Turn 2")[1])
        self.assertIn("relative", fake.prompts[2].split("## Turn 2")[1])
        self.assertFalse(os.path.exists(outside))
        self.assertFalse(os.path.exists(os.path.join(os.path.dirname(job), "x.py")))

    def test_c_bad_format(self):
        job, fake, res = self.loop(["sure, here you go", "```python\nprint(1)\n```", "@@FROB x"])
        self.assertEqual(res["stopped"], "bad_format")
        self.assertEqual(res["turns"], 3)
        self.assertIn("could not read your action", fake.prompts[1])
        self.assertIn("@@WRITE path", fake.prompts[1])

    def test_d_max_turns(self):
        job, fake, res = self.loop(["@@LIST ."] * 5, max_turns=2)
        self.assertEqual((res["stopped"], res["turns"]), ("max_turns", 2))
        self.assertIn(".home/", fake.prompts[1])

    def test_e_end_marker_inside_body(self):
        body = "s = '''\n@@END\n'''\nprint('BODY', s.strip())\n"
        job, fake, res = self.loop([f"@@WRITE m.py\n{body}@@END\n@@RUN python m.py",
                                    f"@@WRITE m.py END=EOF\n{body}@@END EOF\n@@RUN python m.py",
                                    "@@DONE\nok\n@@END"])
        # without an END word the reply is rejected whole (nothing half-written) with a hint ...
        self.assertIn("could not read your action", fake.prompts[1])
        self.assertIn("END=SOMEWORD", fake.prompts[1])
        # ... and with one, the file is written exactly and runs
        self.assertEqual(Path(job, "m.py").read_text(), body)
        self.assertIn("BODY @@END", fake.prompts[2])
        self.assertEqual(res["stopped"], "done")

    def test_f_read_outside_refused(self):
        ro = mkdir700("ro")
        Path(ro, "data.csv").write_text("a,b\n1,2\n")
        other = mkdir700("other")
        Path(other, "c.txt").write_text("CANARY-F")
        job, fake, res = self.loop(["@@READ /etc/hosts", "@@READ ../c.txt", f"@@READ {other}/c.txt",
                                    f"@@READ {ro}/data.csv", "@@DONE\nx\n@@END"], ro_roots=[ro])
        turns = fake.prompts[4].split("## Turn ")
        for n in (1, 2, 3):
            self.assertIn("refused", turns[n])
        self.assertNotIn("CANARY-F", fake.prompts[4])
        self.assertIn("2: 1,2", turns[4])

    def test_g_log_one_line_per_turn(self):
        job, fake, res = self.loop(["@@LIST .", "junk", "@@WRITE a.txt\nhi\n@@END", "@@DONE\nfin\n@@END"])
        rows = log_rows(res["transcript_path"])
        self.assertEqual(len(rows), res["turns"])
        self.assertEqual([r["turn"] for r in rows], [1, 2, 3, 4])
        for r in rows:
            self.assertIn("prompt_bytes", r)
            self.assertIn("answer", r)
            self.assertIn("result", r)

    def test_model_error(self):
        job, fake, res = self.loop([RuntimeError("plan paused")])
        self.assertEqual((res["stopped"], res["turns"]), ("model_error", 1))
        self.assertIn("plan paused", log_rows(res["transcript_path"])[0]["error"])

    def test_log_out_of_reach_of_code(self):
        job = mkdir700("job")
        log = os.path.join(sr.state_dir(job), "transcript.jsonl")
        job, fake, res = self.loop([
            f"@@WRITE evil.py\ntry:\n    open({log!r}, 'w').write('gone')\n    print('LEAK')\n"
            "except PermissionError:\n    print('DENIED')\n@@END\n@@RUN python evil.py",
            "@@WRITE transcript.jsonl\nx\n@@END",  # a file of that name in the job folder is just a file now
            "@@DONE\nx\n@@END"], job=job)
        self.assertEqual(res["transcript_path"], log)
        self.assertFalse(sr._inside(log, sr.check_job_dir(job)))
        self.assertIn("DENIED", fake.prompts[1])
        self.assertIn("wrote transcript.jsonl", fake.prompts[2])
        self.assertEqual(len(log_rows(log)), 3)

    def test_stray_that_cannot_be_killed_stops_loop(self):
        with mock.patch.object(sr, "sweep_strays", return_value={"killed": [], "survivors": [999999]}):
            job, fake, res = self.loop(["@@LIST .", "@@DONE\nx\n@@END"])
        self.assertEqual(res["stopped"], "stray_process")

    def test_prompt_trim_drops_oldest_results_first(self):
        turns = [{"acts": [{"kind": "LIST", "path": "."}], "action_text": f"@@LIST dir{n}",
                  "result": f"R{n}-" + "x" * 3000} for n in range(1, 6)]
        p = sr.build_prompt("task", [], turns, limit=len(sr.INSTRUCTIONS) + 9000)
        self.assertLessEqual(len(p.encode()), len(sr.INSTRUCTIONS) + 9000)
        for n in range(1, 6):
            self.assertIn(f"@@LIST dir{n}", p)  # every action kept
        self.assertNotIn("R1-", p)
        self.assertIn("R5-", p)
        self.assertIn("results of turns 1", p)


# --- attacks on the harness's own file actions (security review, 19 Nov 2026) ---

LINKER = r'''
import os, sys
os.symlink(sys.argv[1], sys.argv[2])
print("linked")
'''


class T12LinkAttacks(unittest.TestCase):
    def setUp(self):
        self.job, self.other = mkdir700("job"), mkdir700("other")
        self.canary = os.path.join(self.other, "canary.txt")
        self.secret = "CANARY-" + uuid.uuid4().hex
        Path(self.canary).write_text(self.secret + "\n")

    def test_a_read_through_link(self):
        r = sealed_py(self.job, LINKER, args=[self.canary, os.path.join(self.job, "l.txt")])
        self.assertIn("linked", r["output"])  # code in the sandbox can make the link ...
        self.assertIn(self.secret, Path(self.job, "l.txt").read_text(), "control: the link does lead out")
        job, ro = sr.check_job_dir(self.job), []
        out = sr.file_action(job, ro, "read", ["l.txt", 1, 10, 10000])
        self.assertNotIn(self.secret, out)  # ... but READ through it shows nothing
        self.assertTrue(out.startswith("refused"), out)
        sealed_py(self.job, LINKER, args=[self.other, os.path.join(self.job, "d")])
        out = sr.file_action(job, ro, "list", ["d", 200])
        self.assertNotIn("canary.txt", out)
        fake = Fake(["@@READ l.txt", "@@DONE\nx\n@@END"])
        sr.work_loop(fake, "t", self.job, timeout_s=30)
        self.assertNotIn(self.secret, fake.prompts[1])

    def test_b_write_through_linked_parent(self):
        sealed_py(self.job, LINKER, args=[self.other, os.path.join(self.job, "out")])
        self.assertTrue(os.path.islink(os.path.join(self.job, "out")))
        fake = Fake(["@@WRITE out/x.txt\nPLANTED\n@@END", "@@WRITE out/canary.txt\nPLANTED\n@@END",
                     "@@DONE\nx\n@@END"])
        sr.work_loop(fake, "t", self.job, timeout_s=30)
        self.assertFalse(os.path.exists(os.path.join(self.other, "x.txt")))
        self.assertEqual(Path(self.canary).read_text(), self.secret + "\n")
        self.assertIn("refused", fake.prompts[1].split("## Turn 1")[1])

    def test_c_race_link_flip(self):
        racer = os.path.join(self.job, "racer.py")
        Path(racer).write_text(
            "import os, sys, time\n"
            "canary = sys.argv[1]\n"
            "if os.fork() == 0:\n"
            "    os.setsid()\n"
            "    if os.fork() == 0:\n"
            "        open('racer.pid', 'w').write(str(os.getpid()))\n"
            "        end = time.time() + 240\n"
            "        while time.time() < end:\n"
            "            try: os.unlink('flip')\n"
            "            except OSError: pass\n"
            "            open('flip', 'w').write('SAFE\\n')\n"
            "            try: os.unlink('flip')\n"
            "            except OSError: pass\n"
            "            os.symlink(canary, 'flip')\n"
            "    os._exit(0)\n"
            "os.wait()\n")
        r = sr.run_sealed([PY, "-I", racer, self.canary], self.job, timeout_s=20)
        self.assertEqual(r["rc"], 0, r["output"])
        deadline = time.time() + 5
        while not os.path.exists(os.path.join(self.job, "racer.pid")) and time.time() < deadline:
            time.sleep(0.05)
        pid = int(Path(self.job, "racer.pid").read_text())
        try:
            # Control: a plain unsandboxed open of the same path does reach the canary while the racer runs,
            # so the race is live and a sandbox-less harness would leak.
            seen = False
            for _ in range(20000):
                try:
                    with open(os.path.join(self.job, "flip")) as f:
                        if self.secret in f.read():
                            seen = True
                            break
                except OSError:
                    pass
            self.assertTrue(seen, "control: the race should reach the canary outside the sandbox")
            job = sr.check_job_dir(self.job)
            safe = 0
            for _ in range(300):
                out = sr.file_action(job, [], "read", ["flip", 1, 5, 10000])
                self.assertNotIn(self.secret, out)
                safe += "SAFE" in out
            print(f"\n  race: 300 sandboxed reads, {safe} saw the plain file, 0 saw the canary")
        finally:
            kill_exact(self, self.job, pid)

    def test_d_setsid_stray_found_and_killed(self):
        script = ("import os, time\n"
                  "if os.fork() == 0:\n"
                  "    os.setsid()\n"
                  "    if os.fork() == 0:\n"
                  "        open('stray.pid', 'w').write(str(os.getpid()))\n"
                  "        time.sleep(200)\n"
                  "    os._exit(0)\n"
                  "os.wait()\n"
                  "time.sleep(0.3)\n"
                  "print('parent leaves')\n")
        fake = Fake([f"@@WRITE s.py\n{script}@@END\n@@RUN python s.py", "@@DONE\nx\n@@END"])
        t = time.time()
        res = sr.work_loop(fake, "t", self.job, timeout_s=30)
        self.assertLess(time.time() - t, 30, "the stray must not hold the run open")
        pid = int(Path(self.job, "stray.pid").read_text())
        gone(self, pid)
        row = log_rows(res["transcript_path"])[0]
        self.assertIn(pid, row.get("strays_killed", []))
        self.assertEqual(res["stopped"], "done")


class T13StrayFinderPrecision(unittest.TestCase):
    def test_no_false_matches(self):
        """19 Nov 2026: a file-based fingerprint matched 7 macOS services. With no run alive, nothing matches."""
        job = mkdir700("job")
        sr._token(sr.check_job_dir(job), create=True)
        self.assertEqual(sr.find_strays(job), [])
        # and a live run is found, alone
        p = subprocess.Popen([sr.SANDBOX_EXEC, "-p", sr.build_profile(sr.check_job_dir(job), [],
                                                                       sr.job_token(job)), "/bin/sleep", "30"],
                             cwd=job, stdin=subprocess.DEVNULL)
        try:
            time.sleep(0.5)
            self.assertEqual(sr.find_strays(job), [p.pid])
            other = mkdir700("job2")
            sr._token(sr.check_job_dir(other), create=True)
            self.assertEqual(sr.find_strays(other), [], "another job folder's finder must not claim it")
        finally:
            p.kill()
            p.wait()


class T15HarnessWritesOutsideJob(unittest.TestCase):
    """Second security review, 19 Nov 2026: the harness writes nothing in a job folder that code may have
    prepared (think of a second run in a job folder an earlier run touched)."""

    def setUp(self):
        self.job, self.other = mkdir700("job"), mkdir700("other")
        self.canary = os.path.join(self.other, "canary.txt")
        self.secret = "CANARY-" + uuid.uuid4().hex + "\n"
        Path(self.canary).write_text(self.secret)

    def test_a_planted_links_change_nothing(self):
        os.link(self.canary, os.path.join(self.job, "transcript.jsonl"))  # hard link to the outside canary
        canary2 = os.path.join(self.other, "canary2.txt")
        Path(canary2).write_text(self.secret)
        os.symlink(canary2, os.path.join(self.job, ".sealed-probe"))       # old fingerprint name, as a link
        outdir = mkdir700("outdir")
        os.symlink(outdir, os.path.join(self.job, ".home"))                # folder link named .home
        before = (os.stat(self.canary).st_nlink, os.stat(canary2).st_nlink)
        self.assertEqual(before[0], 2, "control: the hard link really is there")
        fake = Fake(["@@WRITE h.py\nimport os\ntry:\n    open(os.path.join(os.environ['HOME'], 'x'), 'w')\n"
                     "    print('LEAK')\nexcept PermissionError:\n    print('DENIED')\n@@END\n@@RUN python h.py",
                     "@@LIST .", "@@DONE\nx\n@@END"])
        res = sr.work_loop(fake, "t", self.job, timeout_s=30)
        self.assertEqual(res["stopped"], "done")
        self.assertIn("DENIED", fake.prompts[1])
        self.assertEqual(Path(self.canary).read_text(), self.secret)
        self.assertEqual(Path(canary2).read_text(), self.secret)
        self.assertEqual((os.stat(self.canary).st_nlink, os.stat(canary2).st_nlink), before)
        self.assertEqual(os.listdir(outdir), [])
        self.assertTrue(res["transcript_path"].startswith(sr.STATE_ROOT + "/"))
        self.assertEqual(len(log_rows(res["transcript_path"])), 3)

    def test_b_log_inside_job_or_ro_refused(self):
        ro = mkdir700("ro")
        job_link = os.path.join(SCRATCH, "joblink-" + uuid.uuid4().hex[:6])
        ro_link = os.path.join(SCRATCH, "rolink-" + uuid.uuid4().hex[:6])
        os.symlink(self.job, job_link)
        os.symlink(ro, ro_link)
        for bad in (os.path.join(self.job, "log.jsonl"), os.path.join(ro, "log.jsonl"),
                    os.path.join(job_link, "log.jsonl"), os.path.join(ro_link, "log.jsonl"),
                    os.path.join(job_link, "sub", "..", "log.jsonl")):
            with self.assertRaises(sr.SealError, msg=bad):
                sr.work_loop(Fake(["@@DONE\nx\n@@END"]), "t", self.job, ro_roots=[ro], log_path=bad)
            self.assertFalse(os.path.exists(os.path.join(self.job, "log.jsonl")))
        ok = os.path.join(self.other, "log.jsonl")  # control: outside both, accepted
        res = sr.work_loop(Fake(["@@DONE\nx\n@@END"]), "t", self.job, ro_roots=[ro], log_path=ok)
        self.assertEqual((res["stopped"], res["transcript_path"]), ("done", ok))

    def test_c_log_with_two_links_refused(self):
        log = os.path.join(self.other, "two.jsonl")
        Path(log).write_text("")
        os.link(log, os.path.join(self.other, "two-again.jsonl"))
        with self.assertRaises(sr.SealError):
            sr.work_loop(Fake(["@@DONE\nx\n@@END"]), "t", self.job, log_path=log)
        link = os.path.join(self.other, "link.jsonl")
        os.symlink(self.canary, link)
        with self.assertRaises(sr.SealError):  # a link as the last name is refused too
            sr.work_loop(Fake(["@@DONE\nx\n@@END"]), "t", self.job, log_path=link)
        self.assertEqual(Path(self.canary).read_text(), self.secret)

    def test_d_state_folder_out_of_sight(self):
        sr.run_sealed(["/usr/bin/true"], self.job)  # makes the token
        sd = sr.state_dir(self.job)
        token_file = os.path.join(sd, "token")
        self.assertTrue(os.path.isfile(token_file))
        self.assertFalse(os.path.exists(os.path.join(self.job, ".sealed-probe")))
        items = [("list", sd), ("read", token_file), ("list", sr.STATE_ROOT), ("write", os.path.join(sd, "w"))]
        control = words(outside_py(PROBE, args=[json.dumps(items[:3])]))
        for _, p in items[:3]:
            self.assertEqual(control[p], "LEAK", f"control: {p} readable outside")
        inside = words(sealed_py(self.job, PROBE, args=[json.dumps(items)])["output"])
        for _, p in items:
            self.assertEqual(inside[p], "DENIED", p)
        self.assertFalse(os.path.exists(os.path.join(sd, "w")))

    def test_e_stray_found_by_token_in_state_folder(self):
        script = ("import os, time\n"
                  "if os.fork() == 0:\n"
                  "    os.setsid()\n"
                  "    if os.fork() == 0:\n"
                  "        open('stray.pid', 'w').write(str(os.getpid()))\n"
                  "        time.sleep(200)\n"
                  "    os._exit(0)\n"
                  "os.wait()\n")
        r = sr.run_sealed([PY, "-I", "-c", script], self.job, timeout_s=20)
        self.assertEqual(r["rc"], 0, r["output"])
        deadline = time.time() + 5
        while not os.path.exists(os.path.join(self.job, "stray.pid")) and time.time() < deadline:
            time.sleep(0.05)
        pid = int(Path(self.job, "stray.pid").read_text())
        # as if the harness had restarted: nothing in memory, only the token in the harness folder
        self.assertIsNotNone(sr.job_token(self.job))
        kill_exact(self, self.job, pid)


class T14Parser(unittest.TestCase):
    def test_write_then_run_other_file_refused(self):
        with self.assertRaises(sr.ActionError):
            sr.parse_action("@@WRITE a.py\nx\n@@END\n@@RUN python b.py")

    def test_look_only_actions_may_be_batched(self):
        acts = sr.parse_action("@@LIST .\n@@READ a.txt")
        self.assertEqual([a["kind"] for a in acts], ["LIST", "READ"])
        self.assertEqual(len(sr.parse_action("@@LIST .\n@@LIST ws\n@@READ a.txt 1 9\n@@READ b.txt")), 4)

    def test_mixed_or_too_many_actions_refused(self):
        for bad in ("@@LIST .\n@@RUN python x.py", "@@RUN python x.py\n@@LIST .", "@@READ a.txt\n@@DONE\nok\n@@END",
                    "@@LIST a\n@@LIST b\n@@LIST c\n@@LIST d\n@@LIST e"):
            with self.assertRaises(sr.ActionError, msg=bad):
                sr.parse_action(bad)

    def test_code_fence_wrapping_tolerated(self):
        acts = sr.parse_action("```\n@@READ a.txt 2 5\n```")
        self.assertEqual(acts[0], {"kind": "READ", "path": "a.txt", "first": 2, "last": 5})


if __name__ == "__main__":
    unittest.main()
