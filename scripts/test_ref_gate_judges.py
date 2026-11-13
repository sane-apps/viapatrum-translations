#!/usr/bin/env python3
"""Known-answer tests for ref_gate's model override and two-judge agreement (12 Nov 2026).
Run: python3 -m unittest scripts/test_ref_gate_judges.py"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ref_gate as G  # noqa: E402

SECS = {"u01": ["John said no; he was called Elijah by the Lord (Luke 1:17).",
                "'In the beginning was the Word' (John 1:1)."]}
WRONG = {"verdict": "wrong", "correct_ref": "Matthew 11:14", "confidence": 0.9}
OK = {"verdict": "correct", "correct_ref": None, "confidence": 0.95}


def by_model(table, seen):
    """table: {model: {printed: verdict}}; unknown printed -> correct. Records which models were asked."""
    def chat(model, messages):
        seen.append(model)
        items = json.loads(messages[1]["content"].split("ITEMS:\n", 1)[1])
        return {"content": "\n".join(json.dumps({"id": it["id"], **table.get(model, {}).get(it["printed"], OK)})
                                     for it in items)}
    return chat


class Override(unittest.TestCase):
    def setUp(self):
        self.model, self.second = G.MODEL, G.SECOND

    def tearDown(self):
        G.MODEL, G.SECOND = self.model, self.second

    def test_default_model_is_opus(self):
        self.assertEqual(self.model if not __import__("os").environ.get("REF_GATE_MODEL") else "claude-opus-5-5",
                         "claude-opus-5-5")

    def test_named_model_is_the_one_asked(self):
        G.MODEL, G.SECOND, seen = "agy/gemini-4-argon-high", None, []
        G.gate(SECS, chat=by_model({}, seen))
        self.assertEqual(set(seen), {"agy/gemini-4-argon-high"})

    def test_two_judges_agree_text_changes(self):
        G.MODEL, G.SECOND, seen = "a", "b", []
        fixed, rep = G.gate(SECS, chat=by_model({"a": {"Luke 1:17": WRONG}, "b": {"Luke 1:17": WRONG}}, seen))
        self.assertIn("(Matthew 11:14)", fixed["u01"][0])
        self.assertEqual(set(seen), {"a", "b"})

    def test_two_judges_disagree_text_stays(self):
        G.MODEL, G.SECOND, seen = "a", "b", []
        fixed, _ = G.gate(SECS, chat=by_model({"a": {"Luke 1:17": WRONG}}, seen))
        self.assertIn("(Luke 1:17)", fixed["u01"][0])

    def test_disagreement_is_unclear_not_correct(self):
        G.MODEL, G.SECOND, seen = "a", "b", []
        items, _ = G.items_for(SECS)
        v = G.judge(items, chat=by_model({"a": {"Luke 1:17": WRONG}}, seen))
        luke = [x for x in items if x["printed"] == "Luke 1:17"][0]["id"]
        self.assertEqual(v[luke]["verdict"], "unclear")

    def test_second_judge_failing_fails_the_gate(self):
        G.MODEL, G.SECOND = "a", "b"

        def chat(model, messages):
            if model == "b":
                return {"error": "paused"}
            return by_model({}, [])(model, messages)
        self.assertIsNone(G.gate(SECS, chat=chat)[0])


if __name__ == "__main__":
    unittest.main()
