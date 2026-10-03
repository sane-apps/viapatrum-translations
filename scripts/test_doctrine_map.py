#!/usr/bin/env python3
"""Offline tests for doctrine_map: candidate slots, broker-only grading,
audit locus carry. No network, no inference calls."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import doctrine_map as D  # noqa: E402


def row(i, year, book="b", text="t", section="1", para=0):
    return {"id": f"id{i}", "book": book, "file": "f_english", "section": section, "para": para,
            "year": year, "text": text}


class SlotTests(unittest.TestCase):
    def test_undated_and_late_take_no_slots(self):
        rows = [row(0, None), row(1, 900), row(2, 300), row(3, 600), row(4, 800), row(5, 801), row(6, 450)]
        early, later = D.split_candidates(list(range(7)), rows, {})
        self.assertEqual(early, [2, 6])
        self.assertEqual(later, [3, 4])

    def test_attribution_year_and_spurious(self):
        rows = [row(0, 900, book="moved"), row(1, 300, book="fake"), row(2, None, book="p")]
        att = {"books": {"moved": {"work_year": 700}, "fake": {"status": "spurious"}},
               "passages": {"id2": {"work_year": 400}}}
        early, later = D.split_candidates([0, 1, 2], rows, att)
        self.assertEqual(early, [2])
        self.assertEqual(later, [0])

    def test_later_cap_fills_with_451_800(self):
        rows = [row(i, None if i % 2 else 600) for i in range(200)]
        _, later = D.split_candidates(list(range(200)), rows, {})
        self.assertEqual(len(later), D.KEEP_LATER)
        self.assertTrue(all(rows[i]["year"] == 600 for i in later))


class BrokerTests(unittest.TestCase):
    def test_payload_kimi_and_gpt_oss(self):
        p = D.broker_payload("@cf/moonshotai/kimi-k2.6", "s", "u", 3000)
        self.assertEqual(p["max_completion_tokens"], 3000)
        self.assertEqual(p["reasoning_effort"], "none")
        self.assertEqual(p["chat_template_kwargs"], {"enable_thinking": False})
        g = D.broker_payload("@cf/openai/gpt-oss-120b", "s", "u", 3000)
        self.assertEqual(g["max_tokens"], 3000)
        self.assertEqual(g["messages"][1], {"role": "user", "content": "u"})
        self.assertIsNone(D.broker_payload("nvidia/nemotron-3-ultra-550b-a55b", "s", "u", 3000))

    def test_broker_only_when_up(self):
        res = {"result": {"response": '{"on_question": true, "verdicts": {}}'}}
        with mock.patch.object(D.LB, "_broker_up", return_value=True), \
                mock.patch.object(D.LB, "_broker_run", return_value=res) as br, \
                mock.patch.object(D.W, "call") as direct:
            self.assertEqual(D.grade_call("@cf/moonshotai/kimi-k2.6", "s", "u"),
                             {"on_question": True, "verdicts": {}})
            br.assert_called_once()
            direct.assert_not_called()

    def test_falls_back_direct(self):
        with mock.patch.object(D.LB, "_broker_up", return_value=False), \
                mock.patch.object(D.W, "call", return_value={"x": 1}) as direct:
            self.assertEqual(D.grade_call("@cf/moonshotai/kimi-k2.6", "s", "u"), {"x": 1})
            direct.assert_called_once()
        with mock.patch.object(D.LB, "_broker_up", return_value=True), \
                mock.patch.object(D.LB, "_broker_run", return_value={"error": "boom"}) as br, \
                mock.patch.object(D.time, "sleep"), \
                mock.patch.object(D.W, "call", return_value={"x": 2}) as direct:
            self.assertEqual(D.grade_call("@cf/openai/gpt-oss-120b", "s", "u"), {"x": 2})
            self.assertEqual(br.call_count, 3)
            direct.assert_called_once()
        with mock.patch.object(D.LB, "_broker_run") as br, \
                mock.patch.object(D.W, "call", return_value={"x": 3}):
            D.grade_call("nvidia/nemotron-3-ultra-550b-a55b", "s", "u")   # referee: never the broker
            br.assert_not_called()


TEXT = ("And so the bread which is blessed is no longer common bread but the body of the Lord, "
        "as the apostle teaches when he speaks of the cup of blessing which we bless. ") * 6


class AuditCarryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name)
        (self.out / "audit").mkdir()
        self.old = row(1, 300, text=TEXT)
        (self.out / "corpus.jsonl").write_text(json.dumps(self.old) + "\n")
        (self.out / "audit" / "g.json").write_text(json.dumps(
            [{"passage": "id1", "question": "q", "position": "real", "grader": "states", "verdict": "compatible",
              "reason": "r"}]))
        self.patches = [mock.patch.object(D, "OUT", self.out), mock.patch.object(D, "AUDIT", self.out / "audit")]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def test_backfill_then_carry_light_edit_only(self):
        self.assertEqual(D.audit_backfill(), 1)
        self.assertEqual(D.audit_backfill(), 0)           # idempotent
        r = json.loads((self.out / "audit" / "g.json").read_text())[0]
        self.assertEqual(r["locus"], "b|f_english|1|0")
        self.assertEqual(r["text"], TEXT)
        light = dict(self.old, id="new1", text=TEXT.replace("common bread", "ordinary bread", 1))
        heavy = dict(self.old, id="new2", text=TEXT[: len(TEXT) // 2] + "Something else entirely. " * 20)
        elsewhere = dict(light, id="new3", para=1)
        exact, by_locus = D.load_audit({x["id"]: x for x in (light, heavy, elsewhere)})
        self.assertIn(("id1", "real"), exact)
        cache = {}
        self.assertEqual(D.carried_audit(light, "real", by_locus, cache),
                         {"verdict": "compatible", "audited": "r", "carried": True})
        self.assertIsNone(D.carried_audit(light, "symbolic", by_locus, cache))
        self.assertIsNone(D.carried_audit(heavy, "real", by_locus, cache))
        self.assertIsNone(D.carried_audit(elsewhere, "real", by_locus, cache))

    def test_no_carry_while_audited_id_still_exists(self):
        D.audit_backfill()
        _, by_locus = D.load_audit({"id1": self.old})
        self.assertEqual(by_locus, {})

    def test_report_carries_only_when_graders_agree(self):
        D.audit_backfill()                                # stamp while id1 still resolves
        light = dict(self.old, id="new1", author="A", text=TEXT.replace("common bread", "ordinary bread", 1))
        q = {"id": "q", "question": "Q?", "positions": [{"id": "real"}, {"id": "symbolic"}]}
        (self.out / "q.json").write_text(json.dumps([q]))
        (self.out / "q-grades").mkdir()
        site = self.out / "site.json"
        for grader in ("compatible", "states"):
            (self.out / "q-grades" / "q.json").write_text(json.dumps({"new1": {"on_question": True, "positions": {
                "real": {"verdict": grader}, "symbolic": {"verdict": "excludes"}}}}))
            with mock.patch.object(D, "load_corpus", return_value=([light], None)), \
                    mock.patch.object(D, "QUESTIONS", self.out / "q.json"), \
                    mock.patch.object(D, "ATTRIBUTION", self.out / "none.json"), \
                    mock.patch.object(D, "SITE_DATA", site):
                D.q_report()
            real = json.loads(site.read_text())["questions"][0]["passages"][0]["positions"].get("real")
            if grader == "compatible":   # graders agree with the old audit: it carries; compatible decides nothing
                self.assertIsNone(real)
            else:                        # graders now say "states": the old audit neither overrides nor certifies
                self.assertEqual(real["verdict"], "states")
                self.assertFalse(real["reviewed"])
                self.assertNotIn("carried", real)


if __name__ == "__main__":
    unittest.main()
