#!/usr/bin/env python3
"""Regression tests for the constrained Pass B redrafter (offline checks only)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import redraft_b as rb


def test_lossless_split() -> None:
    assert rb.verify_lossless_split(["a b", "c d"], "a b c d") is True
    assert rb.verify_lossless_split(["a  b", "c d"], "a b\nc d") is True
    assert rb.verify_lossless_split(["a b"], "a b c d") is False
    assert rb.verify_lossless_split(["c d", "a b"], "a b c d") is False
    assert rb.verify_lossless_split([], "a b") is False
    assert rb.verify_lossless_split([""], "a b") is False


def test_numbered_sequence() -> None:
    ok, out = rb.verify_numbered_sequence(["1. one", "2. two", "3. three"], 3)
    assert ok is True and out == ["one", "two", "three"]
    assert rb.verify_numbered_sequence(["1. one", "3. three"], 3)[0] is False
    assert rb.verify_numbered_sequence(["1. one", "2. two"], 3)[0] is False
    assert rb.verify_numbered_sequence(["1. one", "2. "], 2)[0] is False
    assert rb.verify_numbered_sequence(["one", "two"], 2)[0] is False


def test_citation_extraction() -> None:
    assert rb.extract_citations("see Matthew 4:4 here") == [("matthew", 4, 4, 4)]
    assert rb.extract_citations("cf. 1 Timothy 1:9") == [("1 timothy", 1, 9, 9)]
    assert rb.extract_citations("Song of Solomon 2:1") == [("song of solomon", 2, 1, 1)]
    assert rb.extract_citations("Romans 11:25-26") == [("romans", 11, 25, 26)]
    assert rb.extract_citations("no refs here") == []


def test_citation_allowlist_with_ranges() -> None:
    allow = [("romans", 11, 25, 26)]
    assert rb.citation_allowed(("romans", 11, 25, 25), allow) is True
    assert rb.citation_allowed(("romans", 11, 25, 26), allow) is True
    assert rb.citation_allowed(("romans", 11, 27, 27), allow) is False
    assert rb.citation_allowed(("romans", 12, 25, 25), allow) is False
    assert rb.citation_allowed(("matthew", 4, 4, 4), allow) is False


def test_invented_verse_rejected() -> None:
    # Tonight's live failure: model cited Romans 11:25-26 for a 2 Cor 3 quote.
    allow = [("2 corinthians", 3, 14, 16)]
    bad = rb.check_citations(["a veil lies (Romans 11:25-26)."], allow)
    assert bad == ["Romans 11:25-26"]
    good = rb.check_citations(["a veil lies (2 Corinthians 3:14-16)."], allow)
    assert good == []


def test_citations_case_insensitive() -> None:
    assert rb.extract_citations("born of water (john 3:5)") == [("john", 3, 5, 5)]
    assert rb.check_citations(["x (john 3:5)."], [("john", 3, 5, 5)]) == []
    assert rb.check_citations(["x (john 3:5)."], [("matthew", 4, 4, 4)]) == ["john 3:5"]


def test_book_walk_left() -> None:
    assert rb.extract_citations("see Matthew 4:4 here") == [("matthew", 4, 4, 4)]
    assert rb.extract_citations("meet 3:30 tomorrow") == []
    assert rb.extract_citations("Song of Solomon 2:1") == [("song of solomon", 2, 1, 1)]
    assert rb.extract_citations("cf. 1 Timothy 1:9.") == [("1 timothy", 1, 9, 9)]


def test_greek_and_bracket_detection() -> None:
    assert rb.has_greek("plain english") is False
    assert rb.has_greek("with logos") is False
    assert rb.has_greek("with λόγος mixed") is True
    assert rb.has_bracket_tags("see [n1] here") is True
    assert rb.has_bracket_tags("see (note 1) here") is False


def test_length_ratio_bounds() -> None:
    anchor = "x" * 1000
    assert rb.length_ratio_ok("y" * 1100, anchor) is True
    assert rb.length_ratio_ok("y" * 300, anchor) is False
    assert rb.length_ratio_ok("y" * 3100, anchor) is False
    assert rb.length_ratio_ok("y" * 100, "") is False


def test_assemble_paragraphs() -> None:
    paras = rb.assemble_paragraphs(["aaa", "bbb", "ccc"], width=8)
    assert paras == ["aaa bbb", "ccc"]
    assert rb.assemble_paragraphs([]) == []


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("PASS", t.__name__)
    print("all %d redraft_b tests passed" % len(tests))
