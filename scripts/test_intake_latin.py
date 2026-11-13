"""Latin intake in scripts/intake_first1k.py. Run: python3 -m unittest scripts.test_intake_latin -q
The live tests dry-run known works from GitHub, so they change with GitHub and the network. They run only with
TRANSLATIONS_LIVE_TESTS=1, and skip when GitHub cannot be reached."""
import os
import subprocess
import tempfile
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import intake_first1k as m  # noqa: E402

live = unittest.skipUnless(os.environ.get("TRANSLATIONS_LIVE_TESTS"), "live: reads GitHub; set TRANSLATIONS_LIVE_TESTS=1")

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

    @live
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

    @live
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

    @live
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

    def test_html_entity_mdash_parses_and_leaves_bytes_alone(self):
        raw = (
            TEI.format(year=1911)
            .replace(
                "<p>Bene admones, Donate ca-<lb/>rissime: nam<note type=\"footnote\">1 ammones WB</note> et promisisse</p>",
                "<p>Fides &mdash; spes, caritas &ndash; pax</p>",
            )
            .encode("utf-8")
        )
        self.assertIn(b"&mdash;", raw)
        self.assertIn(b"&ndash;", raw)
        with self.assertRaises(Exception):
            m._et_fromstring(raw)
        kept = bytes(raw)
        root = m.xml_fromstring(raw)
        self.assertEqual(raw, kept)
        self.assertIn("&mdash;", raw.decode("utf-8"))
        secs = m.flat_units(root)[0][2]
        self.assertEqual(secs[0][1][0], "Fides \u2014 spes, caritas \u2013 pax")

    def test_unnumbered_preface_and_toc_get_unique_ids(self):
        tei = (
            "<TEI xmlns=\"http://www.tei-c.org/ns/1.0\"><teiHeader><fileDesc><sourceDesc>"
            "<biblStruct><monogr><title>Opera</title><imprint><date>1900</date></imprint>"
            "</monogr></biblStruct></sourceDesc></fileDesc></teiHeader><text><body><div type=\"edition\">"
            "<div n=\"1\" subtype=\"book\" type=\"textpart\">"
            "<div subtype=\"preface\" type=\"textpart\"><p>Praefatio libri primi.</p></div>"
            "<div n=\"1\" subtype=\"chapter\" type=\"textpart\"><p>Caput primum textus.</p></div>"
            "<div n=\"2\" subtype=\"chapter\" type=\"textpart\"><p>Caput secundum textus.</p></div>"
            "</div>"
            "<div subtype=\"toc\" type=\"textpart\"><p>Capitula libri.</p></div>"
            "<div n=\"2\" subtype=\"book\" type=\"textpart\">"
            "<div subtype=\"toc\" type=\"textpart\"><p>Index epistulae.</p></div>"
            "<div n=\"pr\" subtype=\"chapter\" type=\"textpart\"><p>Praefatio epistulae.</p></div>"
            "<div n=\"1\" subtype=\"chapter\" type=\"textpart\"><p>Caput unum.</p></div>"
            "</div></div></body></text></TEI>"
        )
        root = m.xml_fromstring(tei)
        parts = m.units(root)
        self.assertEqual([n for n, _, _ in parts], ["1", "toc", "2"])
        self.assertEqual([sn for sn, _ in parts[0][2]], ["preface", "1", "2"])
        self.assertEqual([sn for sn, _ in parts[2][2]], ["toc", "pr", "1"])
        ids = [f"{n}.{sn}" for n, _, secs in parts for sn, _ in secs]
        self.assertEqual(len(ids), len(set(ids)))
        skipped = m.units(root, skip=("toc",))
        self.assertEqual([n for n, _, _ in skipped], ["1", "2"])
        # Mirror-like flat list: preface beside chapter 1 at the top level
        flat_tei = (
            "<TEI xmlns=\"http://www.tei-c.org/ns/1.0\"><teiHeader><fileDesc><sourceDesc>"
            "<biblStruct><monogr><title>Speculum</title><imprint><date>1887</date></imprint>"
            "</monogr></biblStruct></sourceDesc></fileDesc></teiHeader><text><body><div type=\"edition\">"
            "<div subtype=\"preface\" type=\"textpart\"><p>Praefatio speculi.</p></div>"
            "<div n=\"1\" subtype=\"chapter\" type=\"textpart\"><p>Caput primum.</p></div>"
            "</div></body></text></TEI>"
        )
        flat_ids = [sn for sn, _ in m.flat_units(m.xml_fromstring(flat_tei))[0][2]]
        self.assertEqual(flat_ids, ["preface", "1"])

    def test_empty_unnumbered_sibling_does_not_steal_chapter_id(self):
        tei = (
            "<TEI xmlns=\"http://www.tei-c.org/ns/1.0\"><teiHeader><fileDesc><sourceDesc>"
            "<biblStruct><monogr><title>Opera</title><imprint><date>1900</date></imprint>"
            "</monogr></biblStruct></sourceDesc></fileDesc></teiHeader><text><body><div type=\"edition\">"
            "<div n=\"4\" subtype=\"book\" type=\"textpart\">"
            "<div subtype=\"chapter\" type=\"textpart\"><p></p></div>"
            "<div n=\"21\" subtype=\"chapter\" type=\"textpart\"><p>Caput XXI. Has deas non ueritas.</p></div>"
            "</div></div></body></text></TEI>"
        )
        secs = m.units(m.xml_fromstring(tei))[0][2]
        self.assertEqual([sn for sn, _ in secs], ["21"])
        self.assertIn("Has deas", secs[0][1][0])

    def test_tei_file_dry_run_keeps_mdash_bytes_and_unique_ids(self):
        tei = (
            "<TEI xmlns=\"http://www.tei-c.org/ns/1.0\"><teiHeader><fileDesc><sourceDesc>"
            "<biblStruct><monogr><title>Opera</title><author>Augustine</author>"
            "<imprint><publisher>Tempsky</publisher><date>1911</date></imprint>"
            "</monogr></biblStruct></sourceDesc></fileDesc></teiHeader>"
            "<text><body><div type=\"edition\">"
            "<div n=\"1\" subtype=\"book\" type=\"textpart\"><head>Liber I</head>"
            "<div subtype=\"preface\" type=\"textpart\"><p>Praefatio &mdash; initium.</p></div>"
            "<div n=\"1\" subtype=\"chapter\" type=\"textpart\"><p>Caput primum textus.</p></div>"
            "</div></div></body></text></TEI>"
        )
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "stoa0040.stoa011.opp-lat2.xml"
            path.write_text(tei, encoding="utf-8")
            self.assertIn(b"&mdash;", path.read_bytes())
            p = self._dry(
                "--urn", "stoa0040.stoa011",
                "--slug", "zz-test-letters-mdash",
                "--author", "Augustine of Hippo",
                "--title", "Augustine: Letters",
                "--tei-file", str(path),
                "--source-url", "https://example.invalid/stoa0040.stoa011.opp-lat2.xml",
            )
            self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
            self.assertIn("(local): 1 units, 2 sections", p.stdout)
            self.assertIn("Praefatio", p.stdout)
            self.assertIn(b"&mdash;", path.read_bytes())
            self.assertFalse((m.BOOKS / "zz-test-letters-mdash").exists())


if __name__ == "__main__":
    unittest.main()
