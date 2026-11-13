"""Tests for scripts/provenance_audit.py. Run: python3 -m unittest scripts.test_provenance_audit -q"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import provenance_audit as p  # noqa: E402

TEI = """<TEI xmlns="http://www.tei-c.org/ns/1.0"><teiHeader><fileDesc><titleStmt>
<title>Against Heresies, Book I</title><author>Irenaeus of Lyons</author>
</titleStmt></fileDesc></teiHeader><text><body><div type="edition">
<div n="1" subtype="chapter" type="textpart">
<p>2EPI <del>l. Epei</del> ten aletheian 3 parapempomenoi tines, epeisagousi logous.</p>
</div>
</div></body></text></TEI>"""


class ProvenanceAuditTests(unittest.TestCase):
    def test_witness_text_strips_del_so_intake_head_matches(self):
        # intake_first1k.text_of skips <del>, so the source head is the
        # running text without the apparatus "l. Epei".
        head = "2EPI ten aletheian 3 parapempomenoi tines, epeisagousi logous."
        self.assertNotIn(p.norm(head)[:40], p.norm(TEI))
        w = p.witness_text("copy.xml", TEI)
        self.assertNotIn("Epei", w)
        self.assertIn(p.norm(head)[:40], p.norm(w))

    def test_audit_accepts_tei_with_del_and_flags_a_real_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            book = Path(td) / "zz-test-ah"
            (book / "sources").mkdir(parents=True)
            (book / "translations").mkdir()
            (book / "book.yml").write_text(
                'title: "Irenaeus: Against Heresies (Greek fragments)"\n'
                'author: "Irenaeus of Lyons"\n'
                'slug: "zz-test-ah"\n',
                encoding="utf-8",
            )
            xml_name = "tlg1447.tlg001.1st1K-grc1.xml"
            (book / "sources" / xml_name).write_text(TEI, encoding="utf-8")
            src = [{"section": "1", "greek": [
                "2EPI ten aletheian 3 parapempomenoi tines, epeisagousi logous."
            ]}]
            (book / "translations" / "zz_source.json").write_text(
                json.dumps(src), encoding="utf-8"
            )
            (book / "translations" / "zz_english.json").write_text(
                json.dumps([{"section": "1", "title": "", "english": []}]),
                encoding="utf-8",
            )
            meta = {
                "slug": "zz-test-ah",
                "title": "Irenaeus: Against Heresies (Greek fragments)",
                "author": "Irenaeus of Lyons",
                "text_history": {"witnesses": [{
                    "role": "copy-text",
                    "path": f"sources/{xml_name}",
                }]},
            }
            (book / "translations" / "zz_meta.json").write_text(
                json.dumps(meta), encoding="utf-8"
            )
            out = Path(td) / "rep.json"
            cmd = [sys.executable, str(Path(p.__file__)), "--books", td, "--out", str(out)]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rep = json.loads(out.read_text())
            flags = [f for f in rep["flags"] if f["slug"] == "zz-test-ah"]
            self.assertEqual(flags, [], flags)

            bad = [{"section": "1", "greek": [
                "This sentence was never in the witness file at all, truly."
            ]}]
            (book / "translations" / "zz_source.json").write_text(
                json.dumps(bad), encoding="utf-8"
            )
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rep = json.loads(out.read_text())
            kinds = [f["check"] for f in rep["flags"] if f["slug"] == "zz-test-ah"]
            self.assertIn("unlinked", kinds, rep["flags"])


if __name__ == "__main__":
    unittest.main()
