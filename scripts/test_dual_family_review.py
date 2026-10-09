"""dual_family_review profiles: aligned (default) and legacy. No network."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import dual_family_review as D  # noqa: E402
from pipeline.verify_translation_qa import provenance_family_errors  # noqa: E402

SRC = ["Non necessitate sed voluntate. " * 40, "Deus est lux et non tenebrae."]
ENG = ["Not by necessity but by will. " * 40, "God is light and not darkness."]


def packet():
    secs = [{"section": "s1", "source_text": SRC, "english": ENG,
             "source_sha256": D.sha("\n".join(SRC)), "english_sha256": D.sha("\n".join(ENG))}]
    return {"packet_id": "pk-test", "sections": secs}


def fake_cf(defect_on_chunk=None):
    n = {"i": 0}

    def call(model, messages, key):
        n["i"] += 1
        bad = defect_on_chunk is not None and f"part {defect_on_chunk} of" in messages[1]["content"]
        body = {"gloss": "g", "english": "e", "uncertain": [], "verdict": "fail" if bad else "pass",
                "defects": [{"check": "negation", "english": "God is light", "source": "Deus est lux",
                             "problem": "negation flipped"}] if bad else []}
        return {"http_status": 200, "text": json.dumps(body), "response_model": model,
                "response_id": f"{model}-{n['i']}", "request_id": f"req-{n['i']}", "finish_reason": "stop",
                "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150, "neurons": 40}}
    return call


class DualFamilyProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.pk = self.dir / "p.packet.json"
        self.pk.write_text(json.dumps(packet()))
        self.out = self.dir / "p.review.json"
        for lane in ("kimi", "glm", "nim", "gemini"):
            D.LANES[lane]["min_interval"] = 0

    def tearDown(self):
        self.tmp.cleanup()

    def run_main(self, *extra, caller=None):
        env = {"CLOUDFLARE_API_TOKEN": "t", "NV_API_KEY": "n", "GEMINI_API_KEY": "g"}
        with mock.patch.dict(D.CALLERS, {"cf": caller or fake_cf()}), mock.patch.dict("os.environ", env):
            return D.main(["--packet", str(self.pk), "--receipt-out", str(self.out), *extra])

    def test_default_profile_is_aligned_two_families(self):
        self.assertEqual(D.DEFAULT_PROFILE, "aligned")
        self.assertEqual(self.run_main(), 0)
        rec = json.loads(self.out.read_text())
        prov = rec["review_provenance"]
        self.assertEqual(prov["profile"], "aligned")
        self.assertEqual({l["family"] for l in prov["lanes"]}, {"kimi", "glm"})
        chunks = len(D.source_chunks(SRC))
        self.assertGreater(chunks, 1)
        for lane in prov["lanes"]:
            self.assertEqual(lane["call_count"], chunks)  # one recorded call per source chunk
            self.assertGreater(lane["credit_usd"], 0)
            self.assertEqual(lane["spend_usd"], 0)
        self.assertEqual(provenance_family_errors(rec, packet()["sections"]), [])

    def test_chunk_defect_fails_section_until_adjudicated(self):
        last = len(D.source_chunks(SRC))
        self.assertEqual(self.run_main(caller=fake_cf(defect_on_chunk=last)), 1)
        rec = json.loads(self.out.read_text())
        self.assertEqual(rec["verdict"], "fail")
        errs = provenance_family_errors(rec, packet()["sections"])
        self.assertTrue(any("no adjudication" in e for e in errs), errs)
        lanes = rec["reviews"][0]["lanes"]
        adj = {"s1": [{"model": l["model"], "response_id": l["response_id"], "by": "test",
                       "resolution": "checked against the source"} for l in lanes]}
        a = self.dir / "a.json"
        a.write_text(json.dumps(adj))
        self.assertEqual(self.run_main("--adjudications", str(a), caller=fake_cf(defect_on_chunk=last)), 0)
        rec = json.loads(self.out.read_text())
        self.assertEqual(provenance_family_errors(rec, packet()["sections"]), [])

    def test_parse_aligned_defect_overrides_model_verdict(self):
        r = D.parse_aligned('noise {"verdict": "pass", "defects": [{"check": "agency", "english": "x", '
                            '"source": "y", "problem": "z"}]} tail')
        self.assertEqual(r["verdict"], "fail")
        self.assertFalse(r["checks"]["agency"])
        self.assertIsNone(D.parse_aligned("not json"))
        broken = '{"gloss": "he said "x" here", "defects": [], "verdict": "pass"}'
        self.assertEqual(D.parse_aligned(broken)["verdict"], "pass")
        broken_fail = '{"gloss": "a "b"", "defects": [{"check": "negation", "english": "q"}], "verdict": "fail"}'
        self.assertEqual(D.parse_aligned(broken_fail)["verdict"], "fail")

    def test_legacy_profile_still_nemotron_gemini(self):
        self.assertEqual(D.PROFILES["legacy"]["lanes"], ("nim", "gemini"))
        self.assertEqual(D.LANES["nim"]["model"], "nvidia/nemotron-3-super-120b-a12b")
        self.assertEqual(D.LANES["gemini"]["model"], "gemini-3.5-flash-lite")

    def test_same_family_pair_refused(self):
        self.assertEqual(self.run_main("--glm-model", "@cf/moonshotai/kimi-k2.6"), 2)


if __name__ == "__main__":
    unittest.main()
