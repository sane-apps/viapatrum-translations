#!/usr/bin/env python3
"""Call one named Muse model directly (19 Nov 2026).

Why: the Muse runner queue (muse_runner.py, used by plan_calls.chat("muse")) names no model, so every queued job runs
on the Muse program's default, Spark 1.3. The owner upgraded the Muse plan on 19 Nov 2026 and Wonder Full
(muse-wonder-full-1.0, Meta's strongest model, only in the Muse program on the two top plans) is now served. Until
the queue learns to carry a model name, this is the one way to reach a named model. It calls the Muse program the
same way the runner does (`exec --preset empty`: no tools) plus --model.

  ask = ask_muse("muse-wonder-full-1.0", effort="high");  text = ask(prompt)     raises RuntimeError on any failure
  python3 muse_exec.py <model> [effort]      one tiny request, prints the reply

Rules kept from the runner and the 5 Nov 2026 account restriction: the topic screen is applied first
(plan_calls._screen: biomedical and harm-to-children inputs never go to Muse); an empty answer or a non-zero exit is
an error and is NEVER retried here; at most MAX_AT_ONCE calls at a time across processes."""
import fcntl, os, subprocess, sys, tempfile, time
from pathlib import Path

MUSE = os.path.expanduser("~/.local/bin/muse")
MODELS = {"muse-wonder-full-1.0", "muse-wonder-1.0", "muse-spark-1.3", "muse-ember-1.0"}   # `muse exec --list-models`, 19 Nov 2026
EFFORTS = {"minimal", "low", "medium", "high", "xhigh", "max"}
WORK = Path(os.path.expanduser("~/.cache/muse-exec"))
MAX_AT_ONCE = int(os.environ.get("MUSE_EXEC_MAX", "3"))


def _slot():
    (WORK / "slots").mkdir(parents=True, exist_ok=True)
    while True:
        for i in range(MAX_AT_ONCE):
            fh = open(WORK / "slots" / f"{i}.lock", "w")
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return fh
            except BlockingIOError:
                fh.close()
        time.sleep(2)


def final_text(events: str) -> str | None:
    """The model's final answer from `muse exec --json` output: the text of the last run_terminal event that
    completed. Plain stdout is not used: when an answer arrives in several pieces the program prints the pieces and
    then the whole answer again, with no line break between (seen 19 Nov 2026: "@@LIST .@@LIST ."), which broke
    three code-trial runs."""
    import json
    out = None
    for line in events.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            e = json.loads(line)
        except ValueError:
            continue
        pl = e.get("payload") or {}
        if isinstance(pl, dict) and pl.get("kind") == "run_terminal" and pl.get("terminal") == "completed":
            out = undouble(pl.get("text") or "")
    return out


def undouble(text: str) -> str:
    """Muse models often send a short answer twice in one turn (a first message and then the same words as the final
    one), and the program hands back both, joined with a line break or with nothing: "@@LIST .\n@@LIST ." or
    "@@LIST /a@@LIST /a" (seen in every code-trial run on 19 Nov 2026, Spark and Wonder Full alike). When a reply is
    exactly the same text twice, keep one copy. Anything else is returned untouched."""
    t = text.strip()
    n = len(t)
    if n >= 4 and n % 2 == 0 and t[:n // 2] == t[n // 2:]:
        return t[:n // 2].strip()
    if n >= 5 and n % 2 == 1 and t[n // 2] == "\n" and t[:n // 2] == t[n // 2 + 1:]:
        return t[:n // 2].strip()
    for sep in ("\n\n", "\n \n"):
        k = (n - len(sep)) // 2
        if n > len(sep) and (n - len(sep)) % 2 == 0 and t[k:k + len(sep)] == sep and t[:k] == t[k + len(sep):]:
            return t[:k].strip()
    return text


def ask_muse(model: str, effort: str = "high", timeout_s: int = 1800, screen: bool = True):
    if model not in MODELS:
        raise ValueError(f"not a Muse model we call: {model}")
    if effort not in EFFORTS:
        raise ValueError(f"bad effort: {effort}")
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    import plan_calls   # for its topic screen only

    def ask(prompt: str) -> str:
        why = plan_calls._screen("muse", "", prompt) if screen else None   # screen=False only when the router has screened already
        if why:
            raise RuntimeError(f"{model}: screened: {why}; refusing")
        ws = WORK / "ws"
        ws.mkdir(parents=True, exist_ok=True)
        fh = _slot()
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".txt", dir=WORK, delete=False) as pf:
                pf.write(prompt)
            try:
                p = subprocess.run([MUSE, "exec", "--json", "--preset", "empty", "--prompt-file", pf.name, "--model", model,
                                    "--reasoning-effort", effort, "--workspace", str(ws)], capture_output=True,
                                   text=True, timeout=timeout_s, cwd=str(ws), stdin=subprocess.DEVNULL)
            finally:
                os.unlink(pf.name)
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"{model}: timeout after {timeout_s}s") from None
        finally:
            fh.close()
        text = final_text(p.stdout)
        if p.returncode != 0 or not (text or "").strip():
            raise RuntimeError(f"{model}: muse exited {p.returncode}, final answer {'empty' if text is not None else 'missing'}: {p.stderr[-400:]}")
        return text
    return ask


if __name__ == "__main__":
    m = sys.argv[1]
    e = sys.argv[2] if len(sys.argv) > 2 else "high"
    print(ask_muse(m, e)('Reply with exactly this JSON and nothing else: {"ok": true}'))
