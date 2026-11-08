#!/usr/bin/env python3
"""Known-answer tests for the reference gate (Nov 8, 2026). Run: python3 -m unittest scripts/test_ref_gate.py"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ref_gate as G  # noqa: E402

SECS = {"u01": ["John said no; he was called Elijah by the Lord (Luke 1:17).",
                "The law is a lamp (Ps 118:106); 'Remember not our former iniquities' (Ps 103:12). "
                "'In the beginning was the Word' (John 1:1)."]}


def stub(verdicts):
    def chat(model, messages):
        items = json.loads(messages[1]["content"].split("ITEMS:\n", 1)[1])
        lines = []
        for it in items:
            v = verdicts.get(it["printed"], {"verdict": "correct", "correct_ref": None, "confidence": 0.95})
            lines.append(json.dumps({"id": it["id"], **v}))
        return {"content": "\n".join(lines)}
    return chat


class Parse(unittest.TestCase):
    def test_finds_all_refs(self):
        got = [(r[3], r[4], r[5], r[6]) for r in G.refs_in(SECS["u01"])]
        self.assertEqual(got, [("Luke 1:17", "Luke", 1, 17), ("Ps 118:106", "Psalm", 118, 106),
                               ("Ps 103:12", "Psalm", 103, 12), ("John 1:1", "John", 1, 1)])

    def test_canon(self):
        self.assertEqual(G.canon("1 Cor"), "1 Corinthians")
        self.assertEqual(G.canon("Psalms"), "Psalm")
        self.assertEqual(G.canon("Matt"), "Matthew")
        self.assertEqual(G.canon("II Kings"), "2 Kings")

    def test_greek_numbering_does_not_exist_in_english(self):
        self.assertFalse(G.exists("Psalm", 118, 106))
        self.assertTrue(G.exists("Psalm", 119, 105))

    def test_items_carry_greek_numbering_text(self):
        items, _ = G.items_for(SECS)
        ps = next(i for i in items if i["printed"] == "Ps 118:106")
        self.assertFalse(ps["exists_in_english_numbering"])
        self.assertTrue(any(x.startswith("Psalm 119:105 ") for x in ps["kjv_if_greek_numbering"]))


class Gate(unittest.TestCase):
    V = {"Luke 1:17": {"verdict": "wrong", "correct_ref": "Matthew 11:14", "confidence": 0.9},
         "Ps 118:106": {"verdict": "greek_numbering", "correct_ref": "Psalm 119:105", "confidence": 0.9},
         "Ps 103:12": {"verdict": "wrong", "correct_ref": "Psalm 79:8", "confidence": 0.9}}

    def test_fixes_are_applied_citation_only(self):
        fixed, rep = G.gate(SECS, chat=stub(self.V))
        self.assertEqual(fixed["u01"][0], "John said no; he was called Elijah by the Lord (Matthew 11:14).")
        self.assertIn("(Psalm 119:105)", fixed["u01"][1])
        self.assertIn("(Psalm 79:8)", fixed["u01"][1])
        self.assertIn("(John 1:1)", fixed["u01"][1])
        self.assertEqual(rep["replaced"], 3)

    def test_low_confidence_is_kept(self):
        v = {"Luke 1:17": {"verdict": "wrong", "correct_ref": "Matthew 11:14", "confidence": 0.5}}
        fixed, rep = G.gate(SECS, chat=stub(v))
        self.assertEqual(fixed["u01"], SECS["u01"])
        self.assertEqual(rep["kept_flagged"], 1)

    def test_wrong_without_ref_is_removed(self):
        v = {"Luke 1:17": {"verdict": "wrong", "correct_ref": None, "confidence": 0.9}}
        fixed, _ = G.gate(SECS, chat=stub(v))
        self.assertEqual(fixed["u01"][0], "John said no; he was called Elijah by the Lord.")

    def test_judge_failure_blocks(self):
        fixed, rep = G.gate(SECS, chat=lambda m, msgs: {"error": "paused"})
        self.assertIsNone(fixed)
        self.assertIn("error", rep)

    def test_partial_answer_blocks(self):
        def half(m, msgs):
            items = json.loads(msgs[1]["content"].split("ITEMS:\n", 1)[1])
            return {"content": json.dumps({"id": items[0]["id"], "verdict": "correct", "confidence": 1})}
        self.assertIsNone(G.gate(SECS, chat=half)[0])

    def test_no_refs_needs_no_judge(self):
        fixed, rep = G.gate({"a": ["No references here."]}, chat=lambda m, msgs: {"error": "should not be called"})
        self.assertEqual(fixed, {"a": ["No references here."]})


if __name__ == "__main__":
    unittest.main()
