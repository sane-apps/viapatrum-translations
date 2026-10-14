"""question_priority(): listed books sort first, in file order; a bad file is ignored."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import work_pipeline as W  # noqa: E402


class QuestionPriorityTest(unittest.TestCase):
    def setUp(self):
        self.old = W.QUESTION_PRIORITY, W.EXCERPT_PRIORITY
        d = Path(tempfile.mkdtemp())
        self.tmp, self.excerpts = d / "question-priority.json", d / "excerpt-priority.json"
        W.QUESTION_PRIORITY, W.EXCERPT_PRIORITY = self.tmp, self.excerpts

    def tearDown(self):
        W.QUESTION_PRIORITY, W.EXCERPT_PRIORITY = self.old

    def test_excerpt_works_follow_the_question_books(self):
        self.tmp.write_text(json.dumps({"books": ["q1", "shared"]}))
        self.excerpts.write_text(json.dumps({"books": ["shared", "x1"]}))
        self.assertEqual(W.question_priority(), {"q1": 0, "shared": 1, "x1": 2})

    def test_order_and_duplicates(self):
        self.tmp.write_text(json.dumps({"books": ["b", "a", "b", 3]}))
        self.assertEqual(W.question_priority(), {"b": 0, "a": 1})

    def test_missing_or_broken_file(self):
        self.assertEqual(W.question_priority(), {})
        self.tmp.write_text("{not json")
        self.assertEqual(W.question_priority(), {})
        self.tmp.write_text("[1, 2]")
        self.assertEqual(W.question_priority(), {})

    def test_sorts_listed_books_first(self):
        self.tmp.write_text(json.dumps({"books": ["late-book"]}))
        prio = W.question_priority()
        listed = [(10, "early-book"), (5, "late-book"), (1, "other")]
        order = [b for _, b in sorted(listed, key=lambda wb: (prio.get(wb[1], len(prio)), wb[0]))]
        self.assertEqual(order[0], "late-book")


if __name__ == "__main__":
    unittest.main()
