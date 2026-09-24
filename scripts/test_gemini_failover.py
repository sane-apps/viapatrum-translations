#!/usr/bin/env python3
"""Regression tests for the Gemini prep lane: 503 retry, model failover, book adapters."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import gemini_prep_lane as gpl


def test_is_retriable() -> None:
    assert gpl._is_retriable("HTTP 429") is True
    assert gpl._is_retriable("RESOURCE_EXHAUSTED quota") is True
    assert gpl._is_retriable("HTTP 503 high demand") is True
    assert gpl._is_retriable("UNAVAILABLE backend") is True
    assert gpl._is_retriable("HTTP 404 NOT_FOUND") is False
    assert gpl._is_retriable("HTTP 400 bad request") is False
    assert gpl._is_retriable("") is False


def _run_failover(script, models=("m1", "m2")):
    calls: list[str] = []
    sleeps: list[float] = []
    orig = gpl.gemini_call

    def fake(model, key, system, user):
        calls.append(model)
        return dict(script[len(calls) - 1])

    gpl.gemini_call = fake
    try:
        out = gpl.call_with_failover(list(models), "k", "s", "u", sleep=sleeps.append)
    finally:
        gpl.gemini_call = orig
    return out, calls, sleeps


def test_failover_retries_503_same_model() -> None:
    out, calls, sleeps = _run_failover(
        [{"ok": False, "error": "HTTP 503", "body": "high demand"},
         {"ok": True, "raw": "{}"}],
        models=("m1",),
    )
    assert out["ok"] is True
    assert calls == ["m1", "m1"]
    assert sleeps == [2]


def test_failover_advances_on_404() -> None:
    out, calls, _ = _run_failover(
        [{"ok": False, "error": "HTTP 404", "body": "NOT_FOUND"},
         {"ok": True, "raw": "{}"}],
    )
    assert out["ok"] is True
    assert calls == ["m1", "m2"]
    assert out["failover_from"] == "m1"


def test_failover_gives_up_and_keeps_last_error() -> None:
    out, calls, _ = _run_failover(
        [{"ok": False, "error": "HTTP 503", "body": "busy"},
         {"ok": False, "error": "HTTP 503", "body": "busy"},
         {"ok": False, "error": "HTTP 404", "body": "gone"}],
    )
    assert out["ok"] is False
    assert calls == ["m1", "m1", "m2"]
    assert out["error"] == "HTTP 404"


def test_cyril_load_fix() -> None:
    fix = gpl.load_fix("logos2-rem-close", "cyril-alexandria-isaiah")
    assert fix["section"] == "logos2-rem-close"
    assert isinstance(fix["greek"], list) and any(g.strip() for g in fix["greek"])


def test_cyril_justification_present_and_missing() -> None:
    just = gpl.load_justification("logos2-rem-close", "cyril-alexandria-isaiah")
    assert isinstance(just, dict) and just.get("pass_b_english")
    assert gpl.load_justification("logos9-nope", "cyril-alexandria-isaiah") is None


def test_pass_a_bounded_scales_with_source() -> None:
    obj = {"section": "x", "pass_a_gloss": "y" * 2754, "lemmas": ["a"]}
    assert gpl.score_prep(obj, "{}", "x", 2500)["checks"]["pass_a_bounded"] is True
    assert gpl.score_prep(obj, "{}", "x", 0)["checks"]["pass_a_bounded"] is False
    assert gpl.score_prep(obj, "{}", "x")["checks"]["pass_a_bounded"] is False


def test_jeremiah_paths_unchanged() -> None:
    just = gpl.load_justification("6.1")
    assert isinstance(just, dict)
    fix = gpl.load_fix("6.1")
    assert fix["section"] == "6.1" and fix["greek"]


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("PASS", t.__name__)
    print("all %d gemini failover tests passed" % len(tests))
