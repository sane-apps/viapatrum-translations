"""Hyphen-gloss gate: catch interlinear cribs, not a repeated ordinary compound."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_pass_ab import _hyphen_gloss  # noqa: E402


class HyphenGlossTests(unittest.TestCase):
    def test_repeated_compound_is_prose(self):
        text = " ".join(["Exercise self-control from evil, and do not do it; this is self-control."] * 12)
        self.assertFalse(_hyphen_gloss(text, text.split()))

    def test_interlinear_crib_is_caught(self):
        crib = ("God-beloved church-of-the-Philippians grace-to-you peace-from-God through-Jesus-Christ "
                "Lord-our we-rejoiced with-you greatly in-the-Lord having-received the-examples love-of-truth")
        self.assertTrue(_hyphen_gloss(crib, crib.split()))


if __name__ == "__main__":
    unittest.main()
