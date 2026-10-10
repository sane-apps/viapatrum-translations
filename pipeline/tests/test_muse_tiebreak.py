"""Muse queue runner/client and the optional --muse-tiebreak lane.
python3 -m pytest pipeline/tests/test_muse_tiebreak.py"""
import json
import os
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import dual_family_review as dfr  # noqa: E402
import muse_client  # noqa: E402
import muse_runner  # noqa: E402


def _fake_muse(tmp_path: Path, answer: str) -> Path:
    exe = tmp_path / "fake_muse"
    exe.write_text("#!/bin/sh\n# args: exec --prompt-file F --reasoning-effort E --workspace W\n"
                   f"cat <<'EOT'\n{answer}\nEOT\n")
    exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
    return exe


def test_runner_roundtrip_atomic(tmp_path, monkeypatch):
    q = tmp_path / "q"
    monkeypatch.setenv("MUSE_BIN", str(_fake_muse(tmp_path, '{"verdict": "pass"}')))
    jid = muse_client.submit("hello", effort="low", q=q, tag="t")
    assert (q / "in" / f"{jid}.json").exists() and not list((q / "in").glob("*.tmp"))
    done = muse_runner.process_pending(q)
    assert [r["id"] for r in done] == [jid]
    res = muse_client.wait(jid, q=q, timeout=5, require_runner=False)
    assert res["rc"] == 0 and res["error"] is None and '"verdict": "pass"' in res["answer"]
    assert res["effort"] == "low"
    assert not list((q / "work").iterdir()) or all(p.suffix != ".json" for p in (q / "work").iterdir())


def test_runner_rejects_bad_effort_without_dying(tmp_path, monkeypatch):
    q = tmp_path / "q"
    monkeypatch.setenv("MUSE_BIN", str(_fake_muse(tmp_path, "x")))
    jid = muse_client.submit("hello", effort="bogus", q=q)
    muse_runner.process_pending(q)
    res = muse_client.wait(jid, q=q, timeout=5, require_runner=False)
    assert "bad effort" in res["error"]


def test_client_reports_dead_runner(tmp_path, monkeypatch):
    monkeypatch.setattr(muse_client, "HEARTBEAT_MAX_AGE", 0.0)
    res = muse_client.wait("nope", q=tmp_path / "q", timeout=2, poll=0.1)
    assert "not alive" in res["error"]


def test_two_family_default_unchanged():
    assert dfr.DEFAULT_PROFILE == "aligned"
    assert dfr.PROFILES["aligned"]["lanes"] == ("kimi", "glm")
    ap_defaults = dfr.main.__code__.co_consts  # flag exists and is opt-in
    assert "--muse-tiebreak" in ap_defaults


def _review(verdict="fail"):
    return {"section": "s1", "verdict": verdict, "uncertainties": ["kimi fail: x"],
            "notes": "[kimi @cf/moonshotai/kimi-k2.6] verdict=fail; failed checks: completeness; model notes: X\n"
                     "[glm @cf/zai-org/glm-5.2] verdict=pass; failed checks: none; model notes: ok",
            "lanes": [{"response_id": "r1"}, {"response_id": "r2"}]}


def test_tiebreak_is_advisory_and_cached():
    items = [{"section": "s1", "source_text": ["λόγος"], "english": ["word"],
              "source_sha256": "a", "english_sha256": "b"}]
    seen = []

    def ask(prompt, effort, timeout, tag):
        seen.append(prompt)
        return {"id": "j1", "answer": 'noise {"flags": [{"n": 1, "real": false, "why": "style"}], "verdict": "pass"}',
                "seconds": 1.0, "error": None}

    state, reviews = {}, [_review(), _review("pass") | {"section": "s1"}]
    n = dfr.apply_muse_tiebreak(items, reviews[:1], state, ask)
    r = reviews[0]
    assert n == 1 and r["verdict"] == "fail"           # never flips the verdict
    assert r["muse_tiebreak"]["advisory"] is True and r["muse_tiebreak"]["verdict"] == "pass"
    assert "1. [kimi" in seen[0] and "glm" not in seen[0].split("FLAGS:")[1]  # only failing lanes sent
    again = [_review()]
    assert dfr.apply_muse_tiebreak(items, again, state, ask) == 0  # cached by text + response ids
    assert again[0]["muse_tiebreak"]["verdict"] == "pass"
    passing = [_review("pass")]
    assert dfr.apply_muse_tiebreak(items, passing, {}, ask) == 0 and "muse_tiebreak" not in passing[0]
