#!/usr/bin/env python3
"""Run model-written code in a sealed folder, so a text-only model can do work that needs code.

Why (19 Nov 2026): Google's models reach us through the vendor's command-line tool with every tool denied
(plan_calls.agy_cmd), because that tool's process holds the owner's sign-in and keychain access. So the model
stays text-only. This file is the other half: our own harness carries out the one action the model writes each
turn (write a file, run it, read or list a file), inside a macOS sandbox we control, and feeds the printed result
back on the next turn.

Two parts:
  run_sealed()  runs one command under /usr/bin/sandbox-exec with a deny-by-default profile: writes only inside
                the job folder, reads only the system, Homebrew, the job folder and the read-only folders the
                caller names, no network, no service lookups (so no keychain and no talking to other apps), and a
                list of programs that may never start. sandbox-exec is deprecated by Apple but present and
                working on this Mac (macOS 27.2); that is accepted.
  work_loop()   the turn loop: prompt = fixed instructions + task + transcript; one action per answer in a
                line-fenced format (see INSTRUCTIONS); every turn logged as one JSON line.

Service lookups (mach-lookup): the allowed list is EMPTY. Tested 19 Nov 2026 on this Mini, deny-default profile,
every lookup denied: /opt/homebrew/bin/python3, /usr/bin/python3, /bin/sh, the sz-audit-check venv with numpy,
pandas, scipy and statsmodels, and Rscript (lm, mean) all start and compute. The lookups they try and are refused
(and do fine without): com.apple.system.notification_center (notify_post at start), com.apple.system.
opendirectoryd.libinfo (getpwuid: user name lookup; HOME is set, so nothing needs it), com.apple.logd and
com.apple.diagnosticd (os_log from Apple's python shim). If a future tool needs one, add it to ALLOWED_MACH with
the error seen without it, and never any name in NEVER_MACH.

The harness's own READ, LIST and WRITE also run inside the sandbox (HELPER, a fixed script; paths go in as argv,
a file body through stdin), so links that code in the job folder makes, or swaps in mid-check, cannot steer them
outside (security review, 19 Nov 2026). Nothing in the harness opens a model-named path by name outside it.

Leftover processes: a process that calls setsid() and double-forks leaves our process group, so the end-of-run
group kill misses it. work_loop sweeps before every file action and after every run (find_strays: the kernel says
which processes run under this job folder's profile, by a per-job token) and stops with "stray_process" if one
survives the kill. Such a process stays sealed meanwhile (no network, no writes outside the job folder).
"""
from __future__ import annotations

import json
import os
import re
import secrets
import select
import shlex
import signal
import stat
import subprocess
import threading
import time
from pathlib import Path

SANDBOX_EXEC = "/usr/bin/sandbox-exec"
DEFAULT_PYTHON = "/opt/homebrew/bin/python3"
RSCRIPT = "/opt/homebrew/bin/Rscript"
HOME = os.path.realpath(os.path.expanduser("~"))

# Read-only system folders a plain Python, R or sh process needs to start. Each was added because a run failed
# without it (19 Nov 2026), except /usr, /bin, /System which every process needs.
SYSTEM_READ = [
    "/usr", "/bin", "/sbin", "/System",
    "/opt/homebrew",                  # Homebrew python3, Rscript and their libraries
    "/private/var/db/dyld",           # older dyld shared cache location
    "/private/var/db/timezone",       # time zone data behind /etc/localtime
    "/private/var/select",            # /bin/sh is a link through here; Apple's /usr/bin/python3 reads developer_dir
    "/Library/Developer/CommandLineTools",
]
SYSTEM_READ_LITERAL = [
    "/private/etc/localtime",
    # Apple's /usr/bin/python3 runs xcodebuild, which refuses to go on ("You have not agreed to the Xcode license
    # agreements") unless it can read the machine-wide record that the license was accepted.
    "/Library/Preferences/com.apple.dt.Xcode.plist",
]
# Links at the top of the disk: stat on the link itself is needed to follow it.
TOP_LINKS = ["/tmp", "/var", "/etc"]
DEV_WRITE_LITERAL = ["/dev/null", "/dev/tty", "/dev/dtracehelper"]
DEV_WRITE_SUBPATH = ["/dev/fd"]

# Programs that may never start inside the sandbox, even though the system folders are readable.
DENY_EXEC = [
    "/usr/bin/open", "/usr/bin/osascript", "/usr/bin/security", "/usr/bin/ssh", "/usr/bin/scp", "/usr/bin/sftp",
    "/usr/bin/curl", "/usr/bin/nc", "/usr/bin/sudo", "/usr/bin/su", "/usr/bin/login", "/usr/bin/screencapture",
    "/usr/bin/pbcopy", "/usr/bin/pbpaste", "/usr/bin/crontab", "/bin/launchctl", "/usr/bin/osacompile",
    "/usr/bin/defaults", "/usr/bin/shortcuts", "/usr/bin/automator", "/usr/sbin/networksetup",
]

# Service names a sandboxed process may look up. Empty on purpose (see the module docstring).
ALLOWED_MACH: list[str] = []
# Never allowed, whatever ALLOWED_MACH says; build_profile refuses them.
NEVER_MACH = ("com.apple.SecurityServer", "com.apple.securityd", "com.apple.security.", "com.apple.pasteboard.",
              "com.apple.windowserver", "com.apple.coreservices.launchservicesd", "com.apple.tccd")

# Folders that must never be a job folder or a read-only folder (nor anything inside them).
SECRET_DIRS = [os.path.join(HOME, d) for d in
               (".ssh", ".gnupg", ".config", ".gemini", ".claude", ".codex", ".sane", ".sanemaster", "Library",
                ".aws", ".docker", ".kube", ".netrc")]
REFUSED_RO_ROOTS = {"/", "/Users", "/Volumes", "/private", "/System/Volumes", HOME}


class SealError(ValueError):
    """A job folder or read-only folder the sandbox refuses to use."""


def _inside(path: str, root: str) -> bool:
    return path == root or path.startswith(root.rstrip("/") + "/")


def _ancestors(path: str) -> list[str]:
    out, p = [], os.path.dirname(path)
    while p and p != "/":
        out.append(p)
        p = os.path.dirname(p)
    return out


def _quote(path: str) -> str:
    """A path as a sandbox-profile string. Refuses characters that could end the string or the rule."""
    if not path.startswith("/") or re.search(r'["\\\x00-\x1f\x7f]', path):
        raise SealError(f"path not usable in a sandbox profile: {path!r}")
    return '"' + path + '"'


def check_job_dir(job_dir) -> str:
    """The resolved job folder, or SealError: it must exist, be owned by this user, mode 0700, and not be the
    home folder, an ancestor of it, or a secret folder."""
    real = os.path.realpath(os.fspath(job_dir))
    try:
        st = os.stat(real)
    except OSError as e:
        raise SealError(f"job folder missing: {job_dir} ({e})") from None
    if not stat.S_ISDIR(st.st_mode):
        raise SealError(f"job folder is not a folder: {job_dir}")
    if st.st_uid != os.getuid():
        raise SealError(f"job folder not owned by this user: {job_dir}")
    if stat.S_IMODE(st.st_mode) != 0o700:
        raise SealError(f"job folder mode must be 0700, is {oct(stat.S_IMODE(st.st_mode))}: {job_dir}")
    if _inside(HOME, real):
        raise SealError(f"job folder is the home folder or above it: {job_dir}")
    for s in SECRET_DIRS:
        if _inside(real, s) or _inside(s, real):
            raise SealError(f"job folder touches a secret folder ({s}): {job_dir}")
    return real


def check_ro_roots(ro_roots) -> list[str]:
    out = []
    for r in ro_roots:
        real = os.path.realpath(os.path.expanduser(os.fspath(r)))
        if real in REFUSED_RO_ROOTS or _inside(HOME, real):
            raise SealError(f"read-only folder too broad: {r}")
        if os.path.dirname(real) == "/Volumes":
            raise SealError(f"read-only folder is a whole volume; name a folder on it: {r}")
        for s in SECRET_DIRS:
            if _inside(real, s) or _inside(s, real):
                raise SealError(f"read-only folder touches a secret folder ({s}): {r}")
        if not os.path.exists(real):
            raise SealError(f"read-only folder missing: {r}")
        out.append(real)
    return out


def _developer_dir() -> list[str]:
    """Apple's /usr/bin/python3 is a small program that starts the real one from the selected developer folder."""
    try:
        d = os.path.realpath("/private/var/select/developer_dir")
    except OSError:
        return []
    if not (os.path.isdir(d) and d.startswith("/Applications/")):
        return []
    # It runs xcodebuild from that folder, which loads frameworks from all over the app bundle (denied before:
    # "couldn't stat Xcode's Info.plist", DVTSystemPrerequisites "blocked by sandbox"), so the whole bundle.
    m = re.match(r"^(/Applications/[^/]+\.app)/", d + "/")
    return [m.group(1)] if m else [d]


def build_profile(job: str, ro: list[str], protect: tuple = (), token: str | None = None) -> str:
    """The sandbox profile text. In this language the LAST matching rule wins, so every deny comes after the
    allow it narrows."""
    for name in ALLOWED_MACH:
        if any(name.startswith(n) for n in NEVER_MACH):
            raise SealError(f"service name never allowed: {name}")
    read_sub = SYSTEM_READ + _developer_dir()
    meta = set(TOP_LINKS) | {"/"}
    for p in read_sub + ro + [job]:
        meta.update(_ancestors(p))
    for p in ro:  # the caller's spelling may be a link: allow stat along it too
        meta.update(_ancestors(p))
    L = ["(version 1)", "(deny default)",
         "(allow process-fork)",
         "(allow process-exec)",                     # narrowed by the deny-exec lines below
         "(allow signal (target same-sandbox))",
         "(allow sysctl-read)",
         "(allow file-read-data (literal \"/\"))",   # sh reads the top folder at start (denied: sh deny file-read-data /)
         "(allow file-read-metadata " + " ".join(f"(literal {_quote(m)})" for m in sorted(meta)) + ")",
         "(allow file-read* " + " ".join(f"(subpath {_quote(p)})" for p in read_sub)
         + " " + " ".join(f"(literal {_quote(p)})" for p in SYSTEM_READ_LITERAL) + " (subpath \"/dev\"))"]
    if ro:
        L.append("(allow file-read* " + " ".join(f"(subpath {_quote(p)})" for p in ro) + ")")
    L.append(f"(allow file-read* file-write* (subpath {_quote(job)}))")
    L.append("(allow file-write-data " + " ".join(f"(literal {_quote(p)})" for p in DEV_WRITE_LITERAL)
             + " " + " ".join(f"(subpath {_quote(p)})" for p in DEV_WRITE_SUBPATH) + ")")
    L.append("(allow file-ioctl (literal \"/dev/tty\") (subpath \"/dev/fd\"))")
    if ALLOWED_MACH:
        L.append("(allow mach-lookup " + " ".join(f'(global-name "{n}")' for n in ALLOWED_MACH) + ")")
    if token:
        # Not a real service: no program registers this name, so a lookup returns nothing. It marks this job
        # folder's sandbox, so find_strays can ask the kernel which processes run under it.
        if not re.fullmatch(r"[0-9a-f]{32}", token):
            raise SealError("bad fingerprint token")
        L.append(f'(allow mach-lookup (global-name "{token_service(token)}"))')
    # Narrowing denies, after the allows.
    for p in protect:  # files inside the job folder that code there may read but never change (the audit log)
        L.append(f"(deny file-write* (literal {_quote(p)}))")
    L.append("(deny process-exec " + " ".join(f"(literal {_quote(p)})" for p in DENY_EXEC) + ")")
    # Nothing written in the job folder may itself be started as a program: a copy of /usr/bin/security there
    # would otherwise slip past the list above. Scripts still run, because sh or python is what starts.
    L.append(f"(deny process-exec (subpath {_quote(job)}))")
    L.append("(deny network*)")
    L.append("(deny mach-lookup " + " ".join(
        f'(global-name-prefix "{n}")' for n in NEVER_MACH) + ")")
    return "\n".join(L) + "\n"


def _descendants(root_pid: int) -> list[int]:
    try:
        out = subprocess.run(["/bin/ps", "-axo", "pid=,ppid="], capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    kids: dict[int, list[int]] = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 2:
            kids.setdefault(int(parts[1]), []).append(int(parts[0]))
    seen, todo = [], [root_pid]
    while todo:
        p = todo.pop()
        for c in kids.get(p, []):
            if c not in seen:
                seen.append(c)
                todo.append(c)
    return seen


def _kill_all(proc: subprocess.Popen) -> None:
    pids = _descendants(proc.pid)
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except OSError:
        pass
    for p in pids:
        try:
            os.kill(p, signal.SIGKILL)
        except OSError:
            pass


def cut_marker(n: int) -> str:
    return f"\n[cut: {n} more bytes]\n"


PROBE_NAME = ".sealed-probe"  # fingerprint file in every job folder; see find_strays


def _prepare_job(job: str) -> str:
    """Make the fingerprint file and the .home/.tmp folders without ever following a link (code from an earlier
    run may have left links in the job folder). Returns the fingerprint path."""
    dfd = os.open(job, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for d in (".home", ".tmp"):
            try:
                os.mkdir(d, 0o700, dir_fd=dfd)
            except FileExistsError:
                pass  # a link or a file there only hurts that run's own code; it is still sealed
        try:
            fd = os.open(PROBE_NAME, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600, dir_fd=dfd)
        except OSError as e:
            raise SealError(f"fingerprint file in the job folder is not a plain file: {e}") from None
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise SealError("fingerprint file in the job folder is not a plain file")
            token = os.read(fd, 64).decode("ascii", "replace").strip()
            if not re.fullmatch(r"[0-9a-f]{32}", token):
                if token:
                    raise SealError("fingerprint file in the job folder was changed")
                token = secrets.token_hex(16)
                os.write(fd, token.encode())
        finally:
            os.close(fd)
    finally:
        os.close(dfd)
    return token


def job_token(job_dir) -> str | None:
    """This job folder's fingerprint token, read by descriptor (None when there is none yet)."""
    try:
        fd = os.open(os.path.join(os.path.realpath(os.fspath(job_dir)), PROBE_NAME), os.O_RDONLY | os.O_NOFOLLOW)
    except OSError:
        return None
    try:
        token = os.read(fd, 64).decode("ascii", "replace").strip()
    finally:
        os.close(fd)
    return token if re.fullmatch(r"[0-9a-f]{32}", token) else None


def token_service(token: str) -> str:
    return f"com.saneapps.sealed-run.{token}"


def run_sealed(argv, job_dir, ro_roots=(), timeout_s=300, max_output_bytes=60000, protect=(),
               stdin_bytes: bytes | None = None, on_start=None) -> dict:
    """Run argv in the sandbox with cwd = job_dir. Returns {"rc", "output", "timed_out", "truncated", "pgid"}.
    Output is stdout and stderr together; past max_output_bytes the middle is cut (the start and the end, where
    errors land, are kept). stdin is closed (/dev/null) unless stdin_bytes is given, which is then fed through a
    pipe. on_start(pgid) is called once the process exists. Raises SealError for an unsafe job folder or
    read-only folder."""
    if not os.access(SANDBOX_EXEC, os.X_OK):
        raise SealError(f"{SANDBOX_EXEC} missing: refusing to run code unsealed")
    job = check_job_dir(job_dir)
    ro = check_ro_roots(ro_roots)
    token = _prepare_job(job)
    prot = tuple(os.path.join(job, os.path.relpath(os.path.abspath(p), job)) for p in protect)
    prot += (os.path.join(job, PROBE_NAME),)
    profile = build_profile(job, ro, prot, token)
    home, tmp = os.path.join(job, ".home"), os.path.join(job, ".tmp")
    env = {"PATH": "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin", "LANG": "en_US.UTF-8", "HOME": home,
           "TMPDIR": tmp + "/", "MPLBACKEND": "Agg"}
    proc = subprocess.Popen([SANDBOX_EXEC, "-p", profile] + [os.fspath(a) for a in argv], cwd=job, env=env,
                            stdin=subprocess.DEVNULL if stdin_bytes is None else subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            start_new_session=True, close_fds=True)
    if on_start:
        on_start(proc.pid)
    if stdin_bytes is not None:
        def feed():
            try:
                proc.stdin.write(stdin_bytes)
            except OSError:
                pass
            finally:
                try:
                    proc.stdin.close()
                except OSError:
                    pass
        threading.Thread(target=feed, daemon=True).start()
    head_cap = max_output_bytes // 2
    tail_cap = max_output_bytes - head_cap
    head, tail = bytearray(), bytearray()
    total = [0]

    fd = proc.stdout.fileno()
    stop = threading.Event()

    def take(chunk: bytes):
        total[0] += len(chunk)
        room = head_cap - len(head)
        if room > 0:
            head.extend(chunk[:room])
            chunk = chunk[room:]
        if chunk:
            tail.extend(chunk)
            if len(tail) > tail_cap:
                del tail[:len(tail) - tail_cap]

    def reader():
        # select with a short wait, never a blocking read: a leftover process that keeps the pipe open (one that
        # called setsid, say) must not hold this call open after the run ends (seen 19 Nov 2026: 120 s).
        while True:
            ready, _, _ = select.select([fd], [], [], 0.2)
            if ready:
                chunk = os.read(fd, 65536)
                if not chunk:
                    break
                take(chunk)
            elif stop.is_set():
                break

    t = threading.Thread(target=reader, daemon=True)
    t.start()
    timed_out = False
    try:
        proc.wait(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        timed_out = True
    # Kill the whole group either way: a finished script may have left children behind.
    _kill_all(proc)
    proc.wait()
    stop.set()  # the reader drains what is waiting, then stops at the first quiet 0.2 s
    t.join(timeout=10)
    try:
        proc.stdout.close()
    except OSError:
        pass
    truncated = total[0] > max_output_bytes
    if truncated:
        out = bytes(head) + cut_marker(total[0] - len(head) - len(tail)).encode() + bytes(tail)
    else:
        out = bytes(head) + bytes(tail)
    return {"rc": proc.returncode, "output": out.decode("utf-8", errors="replace"), "timed_out": timed_out,
            "truncated": truncated, "pgid": proc.pid}


# ---------------------------------------------------------------------------------------------------------------
# Finding processes left over from a run.
#
# macOS `ps` shows 0 for every session, and a process that calls setsid() leaves our process group, so groups
# alone miss it. The kernel can tell us instead: sandbox_check(pid, op, filter, value) answers whether that
# process's sandbox allows op. Each job folder has a random token (in .sealed-probe, which code in the job may read
# but not change), and its profile allows a lookup of the made-up service name built from it. See find_strays.
# A first version (19 Nov 2026) used "may read a file in the job folder, may not read the home folder" instead;
# in its first real run it matched and killed 7 macOS user services (cfprefsd, sharingd, CoreDeviceService,
# callservicesd and others; launchd restarted them), because their sandboxes read temp folders and not the home
# folder. Never go back to a file-based fingerprint.
#
# Calling sandbox_check from ctypes: it is variadic, and on Apple Silicon variadic arguments go on the stack while
# ctypes puts every argument in a register (tested 19 Nov 2026: the plain call returns -1 for every question). So
# five dummy integers fill the registers x3-x7 and the path goes ninth, onto the stack where the function reads
# its first variadic argument. Checked against known answers: unsandboxed self -> 0 for /usr/bin/true and
# ~/.zshrc; a process under our profile -> 0 for /usr/bin/true and 1 for ~/.zshrc.

_SANDBOX_FILTER_PATH = 1
_SANDBOX_FILTER_GLOBAL_NAME = 2
_SANDBOX_CHECK_NO_REPORT = 0x40000000


_SC = []


def _sandbox_check(pid: int, op: str | None = None, arg: str | None = None, kind: int = _SANDBOX_FILTER_PATH) -> int:
    """0 allowed, 1 denied, -1 error. kind: _SANDBOX_FILTER_PATH or _SANDBOX_FILTER_GLOBAL_NAME."""
    import ctypes
    if not _SC:
        _SC.append(ctypes.CDLL("/usr/lib/libSystem.B.dylib").sandbox_check)
    f = _SC[0]
    f.restype = ctypes.c_int
    if op is None:
        return f(ctypes.c_int(pid), None, ctypes.c_int(0))
    z = ctypes.c_long(0)
    return f(ctypes.c_int(pid), op.encode(), ctypes.c_int(kind | _SANDBOX_CHECK_NO_REPORT),
             z, z, z, z, z, ctypes.c_char_p(arg.encode()))


def _process_table() -> list[tuple[int, int, int, int]]:
    """(pid, ppid, pgid, uid) for every process."""
    try:
        out = subprocess.run(["/bin/ps", "-axo", "pid=,ppid=,pgid=,uid="], capture_output=True, text=True,
                             timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    rows = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 4 and all(p.lstrip("-").isdigit() for p in parts):
            rows.append(tuple(int(p) for p in parts))
    return rows


def find_strays(job_dir, pgids=()) -> list[int]:
    """Live processes from runs in this job folder, found by the kernel: sandboxed, and their sandbox allows a
    lookup of this job's token service name (random, so no other profile names it) while it refuses
    com.apple.system.notification_center (which nearly every other sandbox allows, including any that allow
    every name). pgids (the groups our runs started) is kept for the log; it never decides a kill on its own:
    numbers are reused, and an unrelated program must never be killed."""
    token = job_token(job_dir)
    if not token:
        return []
    name = token_service(token)
    me, uid = os.getpid(), os.getuid()
    out = []
    for pid, _ppid, _pgid, puid in _process_table():
        if pid in (me, 0, 1) or puid != uid or _sandbox_check(pid) != 1:
            continue
        # 19 Nov 2026 dry run, nothing killed: of 237 sandboxed processes of this user, 7 allowed the random name
        # (their sandboxes allow every name); all 7 also allowed the notification service; only the stray from our
        # run matched all four tests.
        if (_sandbox_check(pid, "mach-lookup", name, _SANDBOX_FILTER_GLOBAL_NAME) == 0
                and _sandbox_check(pid, "mach-lookup", "com.apple.system.notification_center",
                                   _SANDBOX_FILTER_GLOBAL_NAME) == 1
                and _sandbox_check(pid, "mach-lookup", "com.apple.cfprefsd.agent", _SANDBOX_FILTER_GLOBAL_NAME) == 1
                and _sandbox_check(pid, "file-read-data", HOME) == 1):
            out.append(pid)
    return out


def sweep_strays(job_dir, pgids=(), wait_s: float = 2.0) -> dict:
    """Kill every leftover process from this job folder. {"killed": [pids], "survivors": [pids]}."""
    found = find_strays(job_dir, pgids)
    for pid in found:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    deadline = time.time() + wait_s
    left = find_strays(job_dir, pgids)
    while left and time.time() < deadline:
        time.sleep(0.1)
        left = [p for p in find_strays(job_dir, pgids)]
    # A killed child of ours that is not yet reaped shows as a zombie; zombies do nothing, so they do not count.
    left = [p for p in left if not _is_zombie(p)]
    return {"killed": found, "survivors": left}


def _is_zombie(pid: int) -> bool:
    try:
        st = subprocess.run(["/bin/ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True,
                            timeout=5).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return False
    return st == "" or st.startswith("Z")


# ---------------------------------------------------------------------------------------------------------------
# The action loop.

INSTRUCTIONS = """You are working on a task on a computer you control only through actions written as text.
Each reply must contain exactly ONE action in the format below. Our harness carries it out in a sealed work
folder and shows you the result next turn. The folder has no network. Your code can read the files of the task
and the read-only folders named below, and write only inside the work folder.

Actions (each marker starts at the beginning of its own line):

@@WRITE relative/path.py
...the whole file...
@@END
    Writes a file in the work folder (relative path only; no "..", no absolute path). If the file itself contains
    a line that is exactly @@END, give your own end word: "@@WRITE path END=SOMEWORD" and close with
    "@@END SOMEWORD". A WRITE may be followed in the same reply by one RUN of that same file.

@@RUN python relative/script.py [args]
@@RUN sh relative/script.sh [args]
@@RUN R relative/script.R [args]
    Runs the script in the work folder. Python runs isolated (-I): the script's folder is not on sys.path, so put
    helpers in the same file or add the folder to sys.path yourself. Output is shown cut to its start and end.

@@READ path [first_line last_line]
    Shows lines of a file in the work folder or a read-only folder (default: the first 400 lines).

@@LIST path
    Lists names and sizes in a folder (at most 200 entries).

@@DONE
...your final answer...
@@END
    Ends the task. Same END=SOMEWORD rule as WRITE.

Write nothing after the action. Text before the first @@ line is ignored."""

FORMAT_REMINDER = ("Your reply must hold exactly one action: @@WRITE path ... @@END (optionally followed by one "
                   "@@RUN of that file), @@RUN python|sh|R path [args], @@READ path [first last], @@LIST path, or "
                   "@@DONE ... @@END. Use END=SOMEWORD on the opening line when the body has a line '@@END'.")

PROMPT_LIMIT = 700_000
READ_DEFAULT_LINES = 400
LIST_CAP = 200


class ActionError(ValueError):
    """The model's reply could not be read as one action."""


_OPEN = re.compile(r"^@@(WRITE|DONE)(?:[ \t]+(.*?))?[ \t]*$")


def _fenced(lines: list[str], i: int, kind: str, rest: str) -> tuple[dict, int]:
    """Parse a WRITE or DONE block that opens at lines[i]; return (action, index after the closing line)."""
    word = None
    path = None
    if kind == "WRITE":
        bits = rest.split() if rest else []
        if bits and bits[-1].startswith("END="):
            word = bits.pop()[4:]
        if len(bits) != 1:
            raise ActionError("@@WRITE needs exactly one path (spaces in paths are not allowed)")
        path = bits[0]
    else:
        if rest:
            if not rest.startswith("END=") or " " in rest:
                raise ActionError("@@DONE takes nothing on its line except END=SOMEWORD")
            word = rest[4:]
    if word is not None and not re.fullmatch(r"[A-Za-z0-9_]{1,40}", word):
        raise ActionError("END= word must be 1-40 letters, digits or _")
    close = "@@END" + (" " + word if word else "")
    for j in range(i + 1, len(lines)):
        if lines[j].rstrip() == close:
            body = "\n".join(lines[i + 1:j])
            if kind == "WRITE":
                body += "\n"
            return {"kind": kind, "path": path, "body": body}, j + 1
    raise ActionError(f"no closing line '{close}' found")


def _simple(line: str) -> dict:
    m = re.match(r"^@@(RUN|READ|LIST)[ \t]+(.*?)[ \t]*$", line)
    if not m:
        raise ActionError(f"unknown action line: {line[:80]!r}")
    kind, rest = m.groups()
    try:
        bits = shlex.split(rest)
    except ValueError as e:
        raise ActionError(f"could not split the {kind} line: {e}") from None
    if kind == "RUN":
        if len(bits) < 2 or bits[0] not in ("python", "sh", "R"):
            raise ActionError("@@RUN needs: python|sh|R relative/script [args]")
        return {"kind": "RUN", "lang": bits[0], "path": bits[1], "args": bits[2:]}
    if kind == "READ":
        if len(bits) == 1:
            return {"kind": "READ", "path": bits[0], "first": 1, "last": READ_DEFAULT_LINES}
        if len(bits) == 3 and bits[1].isdigit() and bits[2].isdigit() and 1 <= int(bits[1]) <= int(bits[2]):
            return {"kind": "READ", "path": bits[0], "first": int(bits[1]), "last": int(bits[2])}
        raise ActionError("@@READ needs: path [first_line last_line]")
    if len(bits) != 1:
        raise ActionError("@@LIST needs exactly one path")
    return {"kind": "LIST", "path": bits[0]}


def parse_action(text: str) -> list[dict]:
    """One action (or WRITE then RUN of the same file) from a reply, or ActionError.

    A WRITE body that contains a line exactly '@@END' without an END= word ends the file early; the leftover
    lines then make the reply fail as 'text after the action', so it is rejected, never half-written."""
    lines = (text or "").replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(lines) and not lines[i].startswith("@@"):
        i += 1
    if i == len(lines):
        raise ActionError("no line starting with @@ found")
    m = _OPEN.match(lines[i])
    if m:
        act, i = _fenced(lines, i, m.group(1), (m.group(2) or "").strip())
        acts = [act]
    else:
        acts, i = [_simple(lines[i])], i + 1
    # After a WRITE, one RUN of the same file is allowed.
    rest = [(k, l) for k, l in enumerate(lines[i:], start=i) if l.strip() and l.strip() not in ("```",)]
    if acts[0]["kind"] == "WRITE" and rest and rest[0][1].startswith("@@RUN"):
        run = _simple(rest[0][1])
        if os.path.normpath(run["path"]) != os.path.normpath(acts[0]["path"]):
            raise ActionError("a RUN after a WRITE must run the file just written")
        acts.append(run)
        rest = rest[1:]
    if rest:
        raise ActionError(f"text after the action (line {rest[0][0] + 1}: {rest[0][1][:60]!r}); if your file has a "
                          "line '@@END', use END=SOMEWORD")
    return acts


def _rel_path(rel: str) -> str:
    """A cleaned relative path inside the job folder, or ActionError. Lexical checks only: the kernel enforces
    the folder rule when the helper opens the path inside the sandbox, whatever links lie on the way."""
    if not rel or os.path.isabs(rel) or rel.startswith("~"):
        raise ActionError(f"path must be relative to the work folder: {rel!r}")
    if ".." in Path(rel).parts:
        raise ActionError(f"'..' is not allowed in paths: {rel!r}")
    if re.search(r"[\x00-\x1f]", rel):
        raise ActionError("control characters in path")
    norm = os.path.normpath(rel)
    if norm in (".", ""):
        raise ActionError(f"path names the work folder itself: {rel!r}")
    return norm


def _view_arg(job: str, ro: list[str], p: str) -> str:
    """The path to hand the helper for READ/LIST: relative to the job folder, or absolute inside a read-only
    folder (lexically). The helper checks again after following links, inside the sandbox."""
    if not p or re.search(r"[\x00-\x1f]", p):
        raise ActionError("empty path or control characters in path")
    if not os.path.isabs(p):
        if ".." in Path(p).parts:
            raise ActionError(f"'..' is not allowed in paths: {p!r}")
        return os.path.normpath(p)
    norm = os.path.normpath(p)
    if any(_inside(norm, r) for r in [job] + ro):
        return norm
    raise ActionError(f"refused: {p!r} is outside the work folder and the read-only folders")


# The harness's own file actions run INSIDE the sandbox through this fixed helper, so a link that code in the job
# folder made (or swaps in while we look) can never send a read or a write outside: the kernel refuses it. The
# model's text never becomes code here: paths arrive as argv, a file body as stdin.
# argv: mode job n_ro ro... then for read: path first last cap; list: path cap; write: relpath
HELPER = r'''
import os, stat, sys
mode, job, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
ro = sys.argv[4:4 + n]
args = sys.argv[4 + n:]
def inside(p, r):
    return p == r or p.startswith(r.rstrip("/") + "/")
def refuse(msg):
    sys.stdout.write("refused: " + msg)
    sys.exit(3)
def allowed(p):
    real = os.path.realpath(p)
    if not any(inside(real, r) for r in [job] + ro):
        refuse(repr(args[0]) + " is outside the work folder and the read-only folders")
    return real
try:
    if mode == "write":
        rel = args[0]
        full = os.path.join(job, rel)
        try:
            os.makedirs(os.path.dirname(full), mode=0o700, exist_ok=True)
        except FileExistsError:  # a link on the way that leads where this process may not look
            refuse("a folder on the way to " + repr(rel) + " is not a folder inside the work folder")
        allowed(os.path.dirname(full))
        fd = os.open(full, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            refuse("not a plain file: " + rel)
        data = sys.stdin.buffer.read()
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        sys.stdout.write("wrote %s (%d bytes)" % (rel, len(data)))
    elif mode == "read":
        p, first, last, cap = args[0], int(args[1]), int(args[2]), int(args[3])
        real = allowed(p if os.path.isabs(p) else os.path.join(job, p))
        fd = os.open(real, os.O_RDONLY | os.O_NOFOLLOW)
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            refuse("not a file: " + p)
        out, size = [], 0
        with os.fdopen(fd, "rb") as f:
            for i, raw in enumerate(f, start=1):
                if i > last or size > cap:
                    break
                if i >= first:
                    line = "%d: %s" % (i, raw.decode("utf-8", "replace").rstrip("\n"))
                    out.append(line)
                    size += len(line) + 1
        sys.stdout.write("\n".join(out) if out else "(no lines in that range)")
    elif mode == "list":
        p, cap = args[0], int(args[1])
        real = allowed(p if os.path.isabs(p) else os.path.join(job, p))
        st = os.stat(real)
        if stat.S_ISREG(st.st_mode):
            sys.stdout.write("%s  %d bytes (a file)" % (p, st.st_size))
            sys.exit(0)
        if not stat.S_ISDIR(st.st_mode):
            refuse("no such folder: " + p)
        names = sorted(os.listdir(real))
        rows = []
        for name in names[:cap]:
            try:
                s = os.lstat(os.path.join(real, name))
            except OSError:
                continue
            kind = "/" if stat.S_ISDIR(s.st_mode) else ("@" if stat.S_ISLNK(s.st_mode) else "")
            rows.append("%s%s  %d" % (name, kind, s.st_size))
        if len(names) > cap:
            rows.append("[%d more entries not shown]" % (len(names) - cap))
        sys.stdout.write("\n".join(rows) if rows else "(empty folder)")
    else:
        refuse("unknown mode")
except PermissionError as e:
    sys.stdout.write("refused by the sandbox: " + str(e))
    sys.exit(4)
except OSError as e:
    sys.stdout.write("failed: " + str(e))
    sys.exit(5)
'''


def file_action(job: str, ro: list[str], mode: str, args: list[str], body: bytes | None = None,
                cap: int = 60000, protect=(), on_start=None) -> str:
    """Carry out READ, LIST or WRITE through HELPER inside the sandbox. Returns the text to show the model."""
    argv = [DEFAULT_PYTHON, "-I", "-S", "-c", HELPER, mode, job, str(len(ro))] + list(ro) + [str(a) for a in args]
    r = run_sealed(argv, job, ro, timeout_s=60, max_output_bytes=cap, protect=protect,
                   stdin_bytes=body if mode == "write" else None, on_start=on_start)
    text = r["output"] or "(no output)"
    if r["timed_out"]:
        return "failed: the file action took too long"
    return text


def _cap(text: str, cap: int) -> str:
    b = text.encode("utf-8")
    if len(b) <= cap:
        return text
    return b[:cap].decode("utf-8", errors="ignore") + cut_marker(len(b) - cap)


def _run_args(job, act, interpreter) -> list[str]:
    script = os.path.join(job, _rel_path(act["path"]))  # opened by the sandboxed interpreter, never by us
    if act["lang"] == "python":
        return [interpreter, "-I", script]
    if act["lang"] == "sh":
        return ["/bin/sh", script]
    if not os.access(RSCRIPT, os.X_OK):
        raise ActionError("R is not installed here")
    return [RSCRIPT, "--vanilla", script]


def _action_text(acts: list[dict], body_note: str | None = None) -> str:
    """The action as shown back in the transcript."""
    out = []
    for a in acts:
        if a["kind"] == "WRITE":
            body = body_note if body_note is not None else a["body"].rstrip("\n")
            out.append(f"@@WRITE {a['path']}\n{body}\n@@END")
        elif a["kind"] == "RUN":
            out.append("@@RUN " + " ".join(shlex.quote(x) for x in [a["lang"], a["path"]] + a["args"]))
        elif a["kind"] == "READ":
            out.append(f"@@READ {a['path']} {a['first']} {a['last']}")
        elif a["kind"] == "LIST":
            out.append(f"@@LIST {a['path']}")
        else:
            out.append("@@DONE ...")
    return "\n".join(out)


def build_prompt(task: str, ro: list[str], turns: list[dict], limit: int = PROMPT_LIMIT) -> str:
    """Instructions + task + transcript. Over the limit, the oldest results go first (actions stay, with a
    one-line note), then the oldest file bodies."""
    ro_line = ("Read-only folders: " + ", ".join(ro)) if ro else "Read-only folders: none"
    head = f"{INSTRUCTIONS}\n\n{ro_line}\n\n# Task\n{task}\n\n# Transcript so far\n"
    shown = [{"result": t["result"]} for t in turns]
    dropped_results: list[int] = []
    dropped_bodies: list[int] = []

    def render():
        parts = [head]
        if dropped_results:
            parts.append(f"[results of turns {_ranges(dropped_results)} dropped to keep this prompt short]\n")
        if dropped_bodies:
            parts.append(f"[file bodies of turns {_ranges(dropped_bodies)} dropped to keep this prompt short]\n")
        if not shown:
            parts.append("(nothing yet: this is your first turn)\n")
        for n, t in enumerate(shown, start=1):
            parts.append(f"\n## Turn {n}\nYour action:\n{t['action_text']}\nResult:\n{t['result']}\n")
        parts.append("\n# Your next action\n")
        return "".join(parts)

    for n, t in enumerate(shown):
        t["action_text"] = turns[n]["action_text"]
    text = render()
    n = 0
    while len(text.encode()) > limit and n < len(shown):
        if shown[n]["result"] != "[dropped]":
            shown[n]["result"] = "[dropped]"
            dropped_results.append(n + 1)
            text = render()
        n += 1
    n = 0
    while len(text.encode()) > limit and n < len(shown):
        acts = turns[n].get("acts") or []
        if any(a["kind"] == "WRITE" for a in acts):
            shown[n]["action_text"] = _action_text(acts, "[file body dropped]")
            dropped_bodies.append(n + 1)
            text = render()
        n += 1
    return text


def _ranges(nums: list[int]) -> str:
    out, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        out.append(str(nums[i]) if i == j else f"{nums[i]}-{nums[j]}")
        i = j + 1
    return ", ".join(out)


def _open_log(path: str):
    """The audit log, opened once by descriptor: never through a link a run may have left."""
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    if not stat.S_ISREG(os.fstat(fd).st_mode):
        os.close(fd)
        raise SealError(f"log path is not a plain file: {path}")
    return os.fdopen(fd, "a", encoding="utf-8")


def work_loop(ask, task: str, job_dir, ro_roots=(), max_turns: int = 40, interpreter: str | None = None,
              log_path=None, timeout_s: int = 300, max_output_bytes: int = 60000) -> dict:
    """Turn loop. ask(prompt) -> reply text. Returns {"final", "turns", "stopped", "transcript_path"}; stopped is
    "done", "max_turns", "model_error", "bad_format" (three unreadable replies in a row) or "stray_process" (a
    process from a run could not be killed)."""
    job = check_job_dir(job_dir)
    ro = check_ro_roots(ro_roots)
    interpreter = interpreter or DEFAULT_PYTHON
    log = os.path.abspath(os.fspath(log_path)) if log_path else os.path.join(job, "transcript.jsonl")
    # Code in the job folder must not rewrite the audit log (the profile denies writes to it) and a WRITE must not
    # name it.
    protect = (log,) if _inside(log, job) else ()
    reserved = {os.path.relpath(log, job)} if protect else set()
    pgids: list[int] = []  # every process group any run of this loop started
    turns: list[dict] = []
    bad_streak = 0
    final = None
    stopped = "max_turns"
    count = 0
    _prepare_job(job)
    with _open_log(log) as lf:
        def record(row):
            lf.write(json.dumps(row, ensure_ascii=False) + "\n")
            lf.flush()
            os.fsync(lf.fileno())

        def sweep(row) -> bool:
            s = sweep_strays(job, pgids)
            if s["killed"]:
                row.setdefault("strays_killed", []).extend(s["killed"])
            if s["survivors"]:
                row["strays_alive"] = s["survivors"]
                return False
            return True

        for turn in range(1, max_turns + 1):
            count = turn
            prompt = build_prompt(task, ro, turns)
            row = {"turn": turn, "at": time.time(), "prompt_bytes": len(prompt.encode())}
            try:
                answer = ask(prompt)
                if not isinstance(answer, str):
                    raise TypeError(f"ask() returned {type(answer).__name__}, not text")
            except Exception as e:  # noqa: BLE001  any model failure ends the run, logged
                row.update({"answer": None, "error": f"{type(e).__name__}: {e}"})
                record(row)
                stopped = "model_error"
                break
            row["answer"] = answer
            try:
                acts = parse_action(answer)
            except ActionError as e:
                bad_streak += 1
                result = f"could not read your action: {e}\n{FORMAT_REMINDER}"
                row.update({"action": None, "result": result, "bad_streak": bad_streak})
                record(row)
                turns.append({"acts": None, "action_text": "(unreadable reply)", "result": result})
                if bad_streak >= 3:
                    stopped = "bad_format"
                    break
                continue
            bad_streak = 0
            if acts[0]["kind"] == "DONE":
                final = acts[0]["body"]
                row.update({"action": acts, "result": "done"})
                record(row)
                turns.append({"acts": acts, "action_text": "@@DONE", "result": "done"})
                stopped = "done"
                break
            results = []
            stray = False
            for a in acts:
                if not sweep(row):  # nothing from an earlier run may be alive while we act
                    stray = True
                    results.append("stopped: a process from an earlier run could not be killed")
                    break
                try:
                    if a["kind"] == "WRITE":
                        rel = _rel_path(a["path"])
                        if rel in reserved:
                            raise ActionError(f"refused: {a['path']} is kept by the harness")
                        results.append(file_action(job, ro, "write", [rel], a["body"].encode("utf-8"),
                                                   max_output_bytes, protect, pgids.append))
                    elif a["kind"] == "RUN":
                        r = run_sealed(_run_args(job, a, interpreter) + a["args"], job, ro, timeout_s=timeout_s,
                                       max_output_bytes=max_output_bytes, protect=protect, on_start=pgids.append)
                        results.append(f"exit code {r['rc']}"
                                       + (f"; stopped: ran past {timeout_s} s" if r["timed_out"] else "")
                                       + "\n" + (r["output"] or "(no output)"))
                    elif a["kind"] == "READ":
                        results.append(file_action(job, ro, "read", [_view_arg(job, ro, a["path"]), a["first"],
                                                   a["last"], max_output_bytes], None, max_output_bytes, protect,
                                                   pgids.append))
                    else:
                        results.append(file_action(job, ro, "list", [_view_arg(job, ro, a["path"]), LIST_CAP],
                                                   None, max_output_bytes, protect, pgids.append))
                except ActionError as e:
                    results.append(str(e) if str(e).startswith("refused") else f"refused: {e}")
                    break
                except SealError as e:
                    results.append(f"refused by the sandbox: {e}")
                    break
                if results[-1].startswith(("refused", "failed")):
                    break
            if not stray and not sweep(row):  # after every run, nothing it started may stay alive
                stray = True
                results.append("stopped: a process this run started could not be killed")
            result = _cap("\n".join(results), max_output_bytes)
            row.update({"action": acts, "result": result})
            record(row)
            turns.append({"acts": acts, "action_text": _action_text(acts), "result": result})
            if stray:
                stopped = "stray_process"
                break
    return {"final": final, "turns": count, "stopped": stopped, "transcript_path": log}


def ask_plan_calls(model: str):
    """An ask() that sends the prompt to one plan model through plan_calls.chat and raises on an error reply."""
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    import plan_calls  # imported only when used: it reads plan state at import

    def ask(prompt: str) -> str:
        r = plan_calls.chat(model, [{"role": "user", "content": prompt}])
        if "error" in r:
            raise RuntimeError(f"{model}: {r['error']}")
        return r.get("content") or ""

    return ask
