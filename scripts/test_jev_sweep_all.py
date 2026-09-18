#!/usr/bin/env python3
"""Unit tests for jev_sweep_all --glob remainder filter (no network).

Guards the resume path: a remainder sweep with --glob must touch only
matching slugs, so already-swept slugs are never duplicated on append.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import scripts.jev_sweep_all as sweep  # noqa: E402


def _book(tmp: str, slug: str, ref: str = "Genesis 1:1") -> None:
    d = Path(tmp) / "books" / slug / "translations"
    d.mkdir(parents=True)
    (d / "t_english.json").write_text(
        json.dumps(
            [
                {
                    "section": 1,
                    "english": ["In the beginning God created the heaven and the earth."],
                    "added_allusions": [{"reference": ref, "certainty": "clear"}],
                }
            ]
        ),
        encoding="utf-8",
    )


def _stub_jev(state, questions):
    return {
        "answers": {"certainty": {"choice": "clear", "confidence": 0.9}},
        "usage": {"input_tokens": 1, "output_tokens": 1},
    }


class GlobFilterTests(unittest.TestCase):
    def test_iter_no_pattern_yields_all(self) -> None:
        with TemporaryDirectory() as tmp:
            for slug in ("aaa-book", "mmm-book", "zzz-book"):
                _book(tmp, slug)
            got = sorted(s for _, s in sweep.iter_english_files(tmp))
            self.assertEqual(got, ["aaa-book", "mmm-book", "zzz-book"])

    def test_iter_glob_selects_remainder(self) -> None:
        with TemporaryDirectory() as tmp:
            for slug in ("aaa-book", "mmm-book", "zzz-book"):
                _book(tmp, slug)
            got = sorted(s for _, s in sweep.iter_english_files(tmp, "[k-z]*"))
            self.assertEqual(got, ["mmm-book", "zzz-book"])
            got = [s for _, s in sweep.iter_english_files(tmp, "mmm-book")]
            self.assertEqual(got, ["mmm-book"])

    def test_main_glob_appends_without_duplicating_other_slugs(self) -> None:
        with TemporaryDirectory() as tmp:
            for slug in ("aaa-book", "mmm-book", "zzz-book"):
                _book(tmp, slug)
            out = str(Path(tmp) / "sweep.jsonl")
            with mock.patch.object(sweep, "jev", _stub_jev), mock.patch.object(
                sweep, "ROOT", Path(tmp)
            ):
                sweep.main(["prog", "--out", out, "--glob", "[k-z]*"])
                sweep.main(["prog", "--out", out, "--glob", "aaa-book"])
            lines = [
                json.loads(ln)
                for ln in Path(out).read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(len(lines), 3)
            self.assertEqual(
                sorted(ln["book"] for ln in lines),
                ["aaa-book", "mmm-book", "zzz-book"],
            )


if __name__ == "__main__":
    unittest.main()
