#!/usr/bin/env python3
"""Unit tests for optional Gemini lane enable gates (no network)."""
from __future__ import annotations

import importlib
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


class GeminiLaneConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = importlib.import_module("llm_lane_config")
        for k in ("FATHERS_GEMINI_PREP", "FATHERS_ENABLE_GEMINI"):
            os.environ.pop(k, None)

    def tearDown(self) -> None:
        for k in ("FATHERS_GEMINI_PREP", "FATHERS_ENABLE_GEMINI"):
            os.environ.pop(k, None)

    def test_load_has_gemini_lane_enabled_prep_qa_only(self) -> None:
        cfg = self.mod.load_lane_config()
        self.assertIn("cf", cfg["lanes"])
        self.assertIn("nv", cfg["lanes"])
        gem = cfg["lanes"]["gemini"]
        self.assertTrue(gem.get("enabled"))
        self.assertFalse(gem.get("auto_promote"))
        self.assertEqual(gem.get("role"), "prep_qa_only")
        self.assertIn("gemini-3.5-flash-lite", gem.get("prep") or [])

    def test_gemini_enabled_force_and_env(self) -> None:
        cfg = self.mod.load_lane_config()
        self.assertTrue(self.mod.gemini_enabled(cfg))
        self.assertTrue(self.mod.gemini_enabled(cfg, force=True))
        os.environ["FATHERS_GEMINI_PREP"] = "1"
        self.assertTrue(self.mod.gemini_enabled(cfg))

    def test_cf_nv_primary_lists_unchanged_shape(self) -> None:
        cfg = self.mod.load_lane_config()
        for lane in ("cf", "nv"):
            self.assertTrue(self.mod.as_list(cfg["lanes"][lane].get("draft")))
            self.assertTrue(self.mod.as_list(cfg["lanes"][lane].get("checker_a")))
            self.assertTrue(self.mod.as_list(cfg["lanes"][lane].get("checker_b")))


if __name__ == "__main__":
    raise SystemExit(unittest.main())
