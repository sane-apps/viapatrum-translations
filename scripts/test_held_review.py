#!/usr/bin/env python3
"""Tests for scripts/held_review.py (weekly Claude review of held sections)."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import held_review as H  # noqa: E402


def finding(book, sec, i, quote="bad words"):
    return {"id": f"{book}/{sec}#{i}", "book": book, "section": sec, "source": "src", "english": "eng", "quote": quote}


class ParseTests(unittest.TestCase):
    def test_parse_keeps_known_ids_and_verdicts_only(self):
        text = "\n".join(['Here you go:', '{"id": "b/1#0", "verdict": "real", "correct_fix": "x"}',
                          '{"id": "b/1#1", "verdict": "maybe"}', '{"id": "zz#0", "verdict": "noise"}', 'not json {'])
        got = H.parse_lines(text, {"b/1#0", "b/1#1"})
        self.assertEqual(list(got), ["b/1#0"])

    def test_unruled_holds_are_reviewed(self):
        # 2026-10-06: work_pipeline names holds with no ruling apart from confirmed ones.
        self.assertTrue(H.reviewable({"_why": "2 problems without a ruling after 3 repairs"}))
        self.assertTrue(H.reviewable({"_why": "1 confirmed problems after 3 repairs (+1 without a ruling)"}))
        self.assertFalse(H.reviewable({"_why": "gate: near-copies"}))
        self.assertFalse(H.reviewable({"_why": "no locked source"}))

    def test_chunks_keep_sections_whole(self):
        fs = [finding("b", "1", i) for i in range(10)] + [finding("b", "2", i) for i in range(10)]
        cs = H.chunks(fs)
        self.assertEqual([len(c) for c in cs], [10, 10])
        self.assertTrue(all(len({f["section"] for f in c}) == 1 for c in cs))


class ApplyTests(unittest.TestCase):
    def setup(self, d, verdicts, english=("The bad words stay here.",)):
        root = Path(d)
        stage = root / "outputs/work-pipeline"
        sec = stage / "bk/sections/1.json"
        sec.parent.mkdir(parents=True)
        sec.write_text(json.dumps({"section": "1", "_status": "hold", "_why": "1 confirmed problems after 3 repairs",
                                   "pass_b_english": list(english),
                                   "open_findings": [{"class": "mistranslation", "quote": "bad words", "why": "w"}]}))
        rev = root / "outputs/held-review/x"
        rev.mkdir(parents=True)
        (rev / "confirmed_holds.txt").write_text("outputs/work-pipeline/bk/sections/1.json")
        (rev / "findings.jsonl").write_text(json.dumps(finding("bk", "1", 0)) + "\n")
        (rev / "verdicts.jsonl").write_text("".join(json.dumps(v) + "\n" for v in verdicts))
        return root, stage, sec, rev

    def run_apply(self, root, stage, rev, gate=()):
        with mock.patch.object(H, "ROOT", root), mock.patch.object(H.W, "STAGE", stage), \
                mock.patch.object(H.W, "QUEUE_LOG", stage / "queue.json"), \
                mock.patch.object(H.W, "update_log", return_value={}), \
                mock.patch.object(H, "load_brief", return_value={}), \
                mock.patch.object(H.W, "section_gate", return_value=list(gate)):
            return H.apply(rev, dry_run=False)

    def test_real_fix_applied_and_released(self):
        with tempfile.TemporaryDirectory() as d:
            root, stage, sec, rev = self.setup(d, [{"id": "bk/1#0", "verdict": "real", "correct_fix": "good words"}])
            st = self.run_apply(root, stage, rev)
            j = json.loads(sec.read_text())
            self.assertTrue((rev / "archive/bk/1.json").exists())
        self.assertEqual(st["released_fixed"], 1)
        self.assertEqual(j["_status"], "pass")
        self.assertEqual(j["pass_b_english"], ["The good words stay here."])
        self.assertEqual(j["sweep"]["fixed"][0]["fix"], "good words")

    def test_unsure_stays_held(self):
        with tempfile.TemporaryDirectory() as d:
            root, stage, sec, rev = self.setup(d, [{"id": "bk/1#0", "verdict": "unsure", "note": "corrupt"}])
            st = self.run_apply(root, stage, rev)
            self.assertEqual(json.loads(sec.read_text())["_status"], "hold")
        self.assertEqual(st["kept_unsure"], 1)

    def test_gate_failure_stays_held(self):
        with tempfile.TemporaryDirectory() as d:
            root, stage, sec, rev = self.setup(d, [{"id": "bk/1#0", "verdict": "real", "correct_fix": "but but"}])
            st = self.run_apply(root, stage, rev, gate=["doubled word"])
            self.assertEqual(json.loads(sec.read_text())["_status"], "hold")
        self.assertEqual(st["kept_gate"], 1)

    def test_quote_missing_stays_held(self):
        with tempfile.TemporaryDirectory() as d:
            root, stage, sec, rev = self.setup(d, [{"id": "bk/1#0", "verdict": "real", "correct_fix": "x"}],
                                               english=("Already changed.",))
            st = self.run_apply(root, stage, rev)
        self.assertEqual(st["kept_quote"], 1)

    def test_redone_section_not_matched_to_old_verdict(self):
        with tempfile.TemporaryDirectory() as d:
            root, stage, sec, rev = self.setup(d, [{"id": "bk/1#0", "verdict": "noise"}])
            j = json.loads(sec.read_text())
            j["open_findings"][0]["quote"] = "a new finding"
            sec.write_text(json.dumps(j))
            st = self.run_apply(root, stage, rev)
        self.assertEqual(st["kept_unjudged"], 1)


class ImportTests(unittest.TestCase):
    def run_import(self, d, english, gate=(), published=None, stage_english=("Old.",), extra=None):
        root = Path(d)
        stage = root / "outputs/work-pipeline"
        sec = stage / "bk/sections/1.json"
        sec.parent.mkdir(parents=True)
        sec.write_text(json.dumps({"section": "1", "_status": "hold", "_why": "corrupt",
                                   "pass_b_english": list(stage_english)}))
        merged = json.dumps({"book": "bk", "section": "1", "english": english, **(extra or {})})
        first = json.dumps({"book": "bk", "section": "1", "english": published if published is not None else ["Old."]})

        def git(*args):
            if args[0] == "ls-tree":
                return "held/README.md\nheld/bk/1.json\n"
            if args[0] == "show":
                return first if args[1].startswith("add000:") else merged
            if args[0] == "log" and "--diff-filter=A" in args:
                return "add000\n"
            if args[0] == "log":
                return "abc123 A Contributor\n"
            return ""
        with mock.patch.object(H, "ROOT", root), mock.patch.object(H.W, "STAGE", stage), \
                mock.patch.object(H.W, "QUEUE_LOG", stage / "queue.json"), \
                mock.patch.object(H.W, "update_log", return_value={}), mock.patch.object(H, "git", side_effect=git), \
                mock.patch.object(H, "load_brief", return_value={}), \
                mock.patch.object(H.W, "section_gate", return_value=list(gate)):
            st = H.import_held()
        return st, json.loads(sec.read_text())

    def test_changed_english_released(self):
        with tempfile.TemporaryDirectory() as d:
            st, j = self.run_import(d, ["New [perhaps: reading]."])
        self.assertEqual(st["imported"], 1)
        self.assertEqual(j["_status"], "pass")
        self.assertEqual(j["pass_b_english"], ["New [perhaps: reading]."])
        self.assertEqual(j["sweep"]["previous_english"], ["Old."])
        self.assertIn("abc123", j["sweep"]["by"])

    def test_unchanged_english_left_held(self):
        with tempfile.TemporaryDirectory() as d:
            st, j = self.run_import(d, ["Old."])
        self.assertEqual(st["unchanged"], 1)
        self.assertEqual(j["_status"], "hold")

    def test_publish_snapshot_not_imported_after_later_repair(self):
        # 2026-10-09: the section was repaired after publish wrote held/, so the
        # stage English differs from the file. The file is still the snapshot,
        # not a contributor fix, and must not put the old English back.
        with tempfile.TemporaryDirectory() as d:
            st, j = self.run_import(d, ["Snapshot with the bad words."], published=["Snapshot with the bad words."],
                                    stage_english=("Repaired later.",))
        self.assertEqual(st["imported"], 0)
        self.assertEqual(st["snapshot"], 1)
        self.assertEqual(j["_status"], "hold")
        self.assertEqual(j["pass_b_english"], ["Repaired later."])

    def test_recorded_published_english_not_imported(self):
        with tempfile.TemporaryDirectory() as d:
            st, j = self.run_import(d, ["Snapshot."], published=["Something else."], stage_english=("Repaired.",),
                                    extra={"published_english": ["Snapshot."]})
        self.assertEqual(st["imported"], 0)
        self.assertEqual(j["_status"], "hold")

    def test_contributor_edit_after_later_repair_still_imported(self):
        with tempfile.TemporaryDirectory() as d:
            st, j = self.run_import(d, ["Contributor fix."], published=["Snapshot."], stage_english=("Repaired.",))
        self.assertEqual(st["imported"], 1)
        self.assertEqual(j["pass_b_english"], ["Contributor fix."])

    def test_gate_failure_left_held(self):
        with tempfile.TemporaryDirectory() as d:
            st, j = self.run_import(d, ["and and"], gate=["doubled word"])
        self.assertEqual(st["gate"], 1)
        self.assertEqual(j["_status"], "hold")


if __name__ == "__main__":
    unittest.main()
