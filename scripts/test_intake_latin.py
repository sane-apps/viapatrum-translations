"""Latin intake in scripts/intake_first1k.py. Run: python3 -m unittest scripts.test_intake_latin -q
The live test dry-runs one known work (Cyprian, Ad Donatum, CSEL 3.1) and
skips when GitHub cannot be reached."""
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import intake_first1k as m  # noqa: E402

TEI = """<TEI xmlns="http://www.tei-c.org/ns/1.0"><teiHeader><fileDesc><sourceDesc><biblStruct><monogr>
<title>Opera</title><imprint><date>{year}</date></imprint></monogr></biblStruct></sourceDesc></fileDesc></teiHeader>
<text><body><div type="edition"><head>INCIPIT</head>
<div n="1" subtype="chapter" type="textpart"><p>Bene admones, Donate ca-<lb/>rissime: nam<note type="footnote">1 ammones WB</note> et promisisse</p></div>
<div n="2" subtype="chapter" type="textpart"><p>Ceterum quale uel quantum est</p></div>
</div></body></text></TEI>"""


class LatinIntakeTests(unittest.TestCase):
    def test_chapters_become_sections_without_notes_or_line_breaks(self):
        root = m.xml_fromstring(TEI.format(year=1868))
        self.assertTrue(m.chapters_only(root))
        secs = m.flat_units(root)[0][2]
        self.assertEqual([s for s, _ in secs], ["1", "2"])
        self.assertEqual(m.dehyphen(secs[0][1][0]), "Bene admones, Donate carissime: nam et promisisse")

    def test_edition_year_gate(self):
        self.assertEqual(m.edition_year(m.xml_fromstring(TEI.format(year=1868))), 1868)
        self.assertGreater(m.edition_year(m.xml_fromstring(TEI.format(year=1931))), m.LAST_PD_YEAR)

    def test_live_dry_run_ad_donatum(self):
        cmd = [sys.executable, str(Path(m.__file__)), "--urn", "stoa0104a.stoa001", "--slug", "zz-test-ad-donatum",
               "--author", "Cyprian of Carthage", "--title", "Cyprian: To Donatus", "--dry-run"]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if p.returncode and "no public-domain Latin edition" in (p.stdout + p.stderr):
            self.skipTest("GitHub not reachable")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("(csel): 1 units, 16 sections", p.stdout)
        self.assertIn("Hartel", p.stdout)
        self.assertIn("first: Bene admones, Donate carissime", p.stdout)
        self.assertFalse((m.BOOKS / "zz-test-ad-donatum").exists())

    def test_skip_units_drops_front_matter(self):
        root = m.xml_fromstring(TEI.format(year=1868))
        self.assertEqual([s for s, _ in m.flat_units(root, ("1",))[0][2]], ["2"])
        self.assertEqual(m.flat_units(root, ("chapter",)), [])

    def _dry(self, *args):
        p = subprocess.run([sys.executable, str(Path(m.__file__)), "--dry-run", *args],
                           capture_output=True, text=True, timeout=600)
        if p.returncode and "no Greek edition" in (p.stdout + p.stderr) and "--edition" not in args:
            self.skipTest("GitHub not reachable")
        return p

    def test_live_dry_run_greek_edition_choice(self):
        base = ["--urn", "tlg2018.tlg002", "--slug", "zz-test-eus-he", "--author", "Eusebius of Caesarea",
                "--title", "Eusebius: Church History"]
        p = self._dry(*base)  # default file is the 1926-1932 Loeb: refused
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("after 1929", p.stdout + p.stderr)
        p = self._dry(*base, "--edition", "tlg2018.tlg002.1st1K-grc2.xml", "--unit-names", "b1")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("Dindorf", p.stdout)
        self.assertIn("(1st1K): 10 units", p.stdout)
        self.assertFalse((m.BOOKS / "zz-test-eus-he").exists())

    def test_live_dry_run_greek_skip_units(self):
        base = ["--urn", "tlg2115.tlg060", "--slug", "zz-test-refutatio", "--author", "Hippolytus of Rome",
                "--title", "Hippolytus: Refutation"]
        p = self._dry(*base)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("unit MSS", p.stdout)
        p = self._dry(*base, "--skip-units", "MSS")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertNotIn("unit MSS", p.stdout)
        self.assertIn("8 units", p.stdout)


if __name__ == "__main__":
    unittest.main()
