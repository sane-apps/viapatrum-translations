"""PG intake in scripts/intake_first1k.py (--pg-khazarzar/--pg-scan).
Run: python3 -m unittest scripts.test_intake_pg -q  (offline)"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import intake_first1k as m  # noqa: E402

MIGNE = """Epistula ad Maximum
ΤΟΥ ΕΝ ΑΓΙΟΙΣ ΠΑΤΡΟΣ ΗΜΩΝ ΑΘΑΝΑΣΙΟΥ ΠΡΟΣ ΜΑΞΙΜΟΝ.
Ἐντυχὼν τοῖς γραφεῖσι, τὴν μὲν σὴν εὐλάβειαν ἀπεδεξάμην, καὶ οὐκ ἀπεκρίνατο ὁ Κύριος,
ἀλλὰ μᾶλλον ἐχρημάτιζε (Corderius.) τῇ γυναικὶ, ἵνα μὴ ἐν λόγῳ. Τὸν Πατέρα καὶ τὸν Υἱὸν,
ὡς εἴρηται, 26.1088 ἀεὶ ὁμολογοῦμεν, καὶ πάλιν τὸν Λόγον, καὶ τὴν σάρκα, καὶ τὴν ἀλήθειαν.
ΕΠΙΣΤΟΛΗ ΤΟΥ ΑΥΤΟΥ ΠΡΟΣ ΤΟΝ ΑΥΤΟΝ.
ΤΟΥ ΣΩΜΑΤΟΣ ΜΕΤΑΛΑΜΒΑΝΟΜΕΝ. Πάλιν γράφω σοι, ἀδελφέ.
"""
CRITICAL = "Ἀκούω Λεόντιον. ὅτι δή, ζητούμενος ἀναιρεθῆναι, οὐκ ἔκδοτον ἐμαυτόν. καὶ τοῦτό φησι, ὅτι οὐ, " * 3


class PGIntakeTests(unittest.TestCase):
    def test_print_gate_tells_migne_from_a_critical_edition(self):
        self.assertTrue(m.migne_print(MIGNE)[0])
        self.assertFalse(m.migne_print(CRITICAL)[0])

    def test_units_keep_headings_and_text_and_take_column_loci(self):
        units = m.pg_sections(MIGNE, {"26"})
        self.assertEqual(len(units), 2)  # a second ΕΠΙΣΤΟΛΗ title opens a unit
        first = units[0][2][0]
        self.assertTrue(first[1][0].startswith("ΤΟΥ ΕΝ ΑΓΙΟΙΣ"))  # heading stays in the Greek
        self.assertNotIn("Corderius", first[1][0])
        self.assertNotIn("26.1088", first[1][0])
        self.assertEqual(first[2], "PG 26.1087–1088")
        # a capital line that is text, not a title, is kept, not dropped
        self.assertIn("ΤΟΥ ΣΩΜΑΤΟΣ ΜΕΤΑΛΑΜΒΑΝΟΜΕΝ.", units[1][2][0][1][0])

    def test_lowercase_numeral_heading_opens_a_unit(self):
        body = "Μακάριοι οἱ ἐλεήμονες, ὅτι αὐτοὶ ἐλεηθήσονται. " * 10  # a unit, not a title page
        text = f"x\nΛΟΓΟΣ Εʹ.\n{body}\nΛΟΓΟΣ ς ʹ.\n{body}\n"
        self.assertEqual([u[1] for u in m.pg_sections(text, set())], ["ΛΟΓΟΣ Εʹ.", "ΛΟΓΟΣ ς ʹ."])

    def test_excerpt_cuts_between_anchor_words(self):
        cut = m.excerpt("Ἀρχή. Εἷς Θεὸς Πατὴρ Λόγου ζῶντος, σοφίας. Τριὰς ἀεί. Τέλος.", "Εἷς Θεὸς|Τριὰς ἀεί")
        self.assertEqual(cut.split("\n", 1)[1], "Εἷς Θεὸς Πατὴρ Λόγου ζῶντος, σοφίας. Τριὰς ἀεί.")

    def test_latin_rubrics_go_greek_stays(self):
        self.assertEqual(m.strip_latin("ἀρχή. EX COMMENTARIO IN JOB. Cap. I, v. 1. Τό γε μὴν λέγειν"),
                         "ἀρχή. Τό γε μὴν λέγειν")
        self.assertEqual(m.strip_latin("ὁ μέγας Βασίλειος, etc. . Ἀθανάσιος. Διὰ τί"), "ὁ μέγας Βασίλειος. Ἀθανάσιος. Διὰ τί")
        self.assertEqual(m.strip_latin("λόγοι ιβʹ. Ἐγώ"), "λόγοι ιβʹ. Ἐγώ")
        # numerals typed with Latin look-alikes become Greek, not stripped
        self.assertEqual(m.strip_latin(m.greek_numerals("ΨΑΛΜΟΣ ΡΙS ʹ. Δαυΐδ")), "ΨΑΛΜΟΣ ΡΙϚ ʹ. Δαυΐδ")

    def test_split_words_rejoin_only_into_known_words(self):
        m._VOCAB.update({"κρατουντεσ", "οι"})
        self.assertEqual(m.join_splits("οἱ κρα τοῦντες".split(), set()), ["οἱ", "κρατοῦντες"])
        self.assertEqual(m.join_splits("οἱ λόγοι".split(), set()), ["οἱ", "λόγοι"])


if __name__ == "__main__":
    unittest.main()
