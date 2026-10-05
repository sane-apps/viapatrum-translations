"""Unit tests for pipeline/work_lint.py. Run: python3 -m unittest pipeline.test_work_lint -q
(also collected by pytest if installed)."""
import unittest

from pipeline import work_lint as wl


def S(text, sid="s1"):
    return {"id": sid, "title": "", "text": text}


def rules(sections, brief=None, rule=None):
    out = wl.lint_work(sections, brief)
    return [f for f in out if rule is None or f["rule"] == rule]


GOOD = "He spoke at length about the matter. Then he left."


class WorkLintTests(unittest.TestCase):
    def test_quotes_are_substrings(self):
        secs = [S("lowercase start with [things] and (Matt 23:1) and thou art"), S(GOOD, "s2")]
        for f in wl.lint_work(secs):
            text = next(s["text"] for s in secs if s["id"] == f["section"])
            self.assertIn(f["quote"], text)

    # boundary
    def test_boundary_lowercase_start(self):
        self.assertTrue(rules([S("and then he went. Done.")], rule="boundary"))

    def test_boundary_ok_starts(self):
        for t in ("“faith” is the word. Yes.", "1 Corinthians 13 says so.", GOOD, "(Gen 1) He said."):
            self.assertFalse([f for f in rules([S(t)], rule="boundary") if "starts" in f["why"]], t)

    def test_boundary_unpunctuated_end(self):
        f = rules([S("He said that the many should be cast out and the")], rule="boundary")
        self.assertEqual(f[0]["severity"], "error")

    def test_boundary_ok_ends(self):
        for t in ("He said it.", "He said “no.”", "He asked why?", "See (Genesis 1:1)", "Done…"):
            self.assertFalse(rules([S(t)], rule="boundary"), t)

    # bracket filler
    def test_bracket_filler(self):
        self.assertTrue(rules([S("the [spoils] of war. Ok.")], rule="bracket_filler"))
        self.assertTrue(rules([S("by [one thing]. Ok.")], rule="bracket_filler"))

    def test_bracket_filler_negative(self):
        for t in ("see [Genesis 1:1]. Ok.", "He [sic] said. Ok.", "[M.] said so. Ok.", "a [very long editorial gloss here] x."):
            self.assertFalse(rules([S(t)], rule="bracket_filler"), t)

    # citation style
    def test_citation_abbrev(self):
        for t in ("as said (Matt 23:1) there.", "see (1 Cor 13", "in (Ps 22", "[1 Sam 28:13-15]"):
            self.assertTrue(rules([S(t)], rule="citation_style"), t)

    def test_citation_full_names_ok(self):
        for t in ("as said (Matthew 23:1) there.", "see (1 Corinthians 13:4)", "(Psalm 22:1)", "the Mark he made (Mark 1:1)"):
            self.assertFalse(rules([S(t)], rule="citation_style"), t)

    def test_kingdoms_titles(self):
        for t in ("the first of Kingdoms tells", "in the third of the Kingdoms", "the Fourth Book of Kingdoms"):
            self.assertTrue(rules([S(t)], rule="citation_style"), t)
        self.assertFalse(rules([S("the kingdoms of the earth fall")], rule="citation_style"))

    def test_old_titles_warn(self):
        f = rules([S("in Canticles and the Apocalypse")], rule="citation_style")
        self.assertEqual({x["severity"] for x in f}, {"warn"})

    # ancient names
    def test_ancient_names(self):
        self.assertTrue(rules([S("as Esaias said. Ok.")], rule="ancient_names"))
        self.assertTrue(rules([S("Jesus son of Nave led them.")], rule="ancient_names"))
        self.assertTrue(rules([S("in the book of Paralipomenon.")], rule="ancient_names"))

    def test_ancient_names_glossed_or_absent(self):
        self.assertFalse(rules([S("as Esaias (Isaiah) said.")], rule="ancient_names"))
        self.assertFalse(rules([S("as Isaiah said.")], rule="ancient_names"))

    # stray script
    def test_stray_script(self):
        self.assertTrue(rules([S("He wrote εὐλογία and left.")], rule="stray_script"))

    def test_stray_script_glossed(self):
        self.assertFalse(rules([S("the word εὐλογία (blessing) means praise.")], rule="stray_script"))
        self.assertFalse(rules([S("It is called εὐλογία, that is blessing.")], rule="stray_script"))

    # term drift
    def test_term_drift(self):
        secs = [S("The belly-myth spoke.", "a"), S("The belly-talker lied.", "b"), S("A belly-dancer rose.", "c")]
        f = rules(secs, rule="term_drift")
        self.assertEqual(len(f), 1)
        for v in ("belly-myth", "belly-talker", "belly-dancer"):
            self.assertIn(v, f[0]["why"])

    def test_term_drift_negative(self):
        # one variant only, or ordinary compounds
        self.assertFalse(rules([S("belly-myth a", "a"), S("belly-myth b", "b"), S("belly-myth c", "c")], rule="term_drift"))
        self.assertFalse(rules([S("well-known x", "a"), S("well-being y", "b"), S("well-fed z", "c")], rule="term_drift"))
        # variants in a single section only
        self.assertFalse(rules([S("belly-myth belly-talker belly-dancer", "a"), S("x", "b")], rule="term_drift"))

    # glossary / names
    def test_glossary_banned(self):
        brief = {"glossary": [{"source_term": "x", "english": "medium", "banned": ["belly-myth", "ventriloquist"]}]}
        f = rules([S("The Ventriloquist spoke. A medium too.")], brief, "glossary")
        self.assertEqual(len(f), 1)
        self.assertEqual(f[0]["severity"], "error")
        self.assertEqual(f[0]["quote"], "Ventriloquist")

    def test_glossary_whole_word(self):
        brief = {"glossary": [{"source_term": "x", "english": "medium", "banned": ["belly-myth"]}]}
        self.assertFalse(rules([S("the belly-mythology")], brief, "glossary"))
        self.assertFalse(rules([S("belly-myth")], None, "glossary"))

    def test_names_map(self):
        brief = {"names": {"first of Kingdoms": "1 Samuel"}}
        self.assertTrue(rules([S("in the first of Kingdoms we read")], brief, "glossary"))
        self.assertFalse(rules([S("in the first of Kingdoms (1 Samuel) we read")], brief, "glossary"))

    # scaffold / guard
    def test_scaffold(self):
        self.assertTrue(rules([S("Unit 1. Lemma-led open here.")], rule="scaffold"))
        self.assertTrue(rules([S("TODO fix this.")], rule="scaffold"))
        self.assertFalse(rules([S("A calm sentence.")], rule="scaffold"))

    def test_output_guard(self):
        self.assertTrue(rules([S("He went to the the market.")], rule="output_guard"))
        self.assertFalse(rules([S("He went to the market.")], rule="output_guard"))

    # archaic
    def test_archaic(self):
        self.assertTrue(rules([S("He said thou art holy.")], rule="archaic"))

    def test_archaic_inside_quotes_ok(self):
        self.assertFalse(rules([S("He said “thou art holy” to him.")], rule="archaic"))

    # false friend
    def test_false_friend_latin_only(self):
        s = [S("They formed a conspiracy of faith.")]
        self.assertTrue(rules(s, {"language": "Latin (Jerome)"}, "false_friend"))
        self.assertFalse(rules(s, {"language": "Greek"}, "false_friend"))
        self.assertFalse(rules(s, None, "false_friend"))

    # contract
    def test_load_work_eustathius(self):
        secs = wl.load_work("eustathius-engastrimytho")
        self.assertTrue(secs)
        self.assertEqual(set(secs[0]), {"id", "title", "text"})
        self.assertIsInstance(secs[0]["text"], str)

    def test_eustathius_expected_flags(self):
        secs = wl.load_work("eustathius-engastrimytho")
        found = wl.lint_work(secs)
        drift = [f for f in found if f["rule"] == "term_drift" and "belly-" in f["why"]]
        self.assertTrue(drift)
        quotes = " ".join(f["quote"].lower() for f in found if f["rule"] == "citation_style")
        self.assertIn("first of kingdoms", quotes)
        self.assertIn("third of the kingdoms", quotes)
        self.assertTrue([f for f in found if f["rule"] == "boundary"])



class LacunaRuleTests(unittest.TestCase):
    """2026-10-05 audit: a gap the source marks mid-text was filled with invented English."""

    def _run(self, source, text):
        return [f for f in wl.lint_work([{"id": "1", "text": text, "source": source}]) if f["rule"] == "lacuna"]

    def test_gap_dropped_is_warned(self):
        f = self._run("καὶ τίς αὐτοῦ τὴν παρουσίαν ὑποστήσεται; ... .. παραβαλλομένους θηρίοις.",
                      "And who will endure his coming? Do you not see those thrown to wild beasts.")
        self.assertEqual(len(f), 1)
        self.assertEqual(f[0]["severity"], "warn", "a warning, never a hard gate")

    def test_gap_kept_is_fine(self):
        self.assertEqual(self._run("καὶ τίς αὐτοῦ τὴν παρουσίαν ὑποστήσεται; ... παραβαλλομένους θηρίοις.",
                                   "And who will endure his coming? […] those thrown to wild beasts."), [])

    def test_marks_at_the_edges_are_not_gaps(self):
        self.assertEqual(self._run("... τὴν παρουσίαν ὑποστήσεται παραβαλλομένους θηρίοις ...",
                                   "who will endure his coming, thrown to wild beasts."), [])

if __name__ == "__main__":
    unittest.main()
