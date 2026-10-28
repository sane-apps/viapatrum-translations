"""Muse-only review adapter: receipt shape the QA gate accepts.
python3 -m pytest scripts/test_muse_review.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import muse_review  # noqa: E402
from pipeline.verify_translation_qa import muse_provenance_errors  # noqa: E402

SRC = ["Non necessitate sed voluntate agimus, et Deus neminem cogit ad bonum."]
ENG = ["We act by choice, not necessity, and God forces no one toward the good."]
PACKET = {"packet_id": "p1", "sections": [{
    "section": "1", "source_text": SRC, "english": ENG,
    "source_sha256": "s" * 64, "english_sha256": "e" * 64}]}
RESEARCH = {"1": [{"item": "voluntate", "source": "Test lexicon s.v. voluntas",
                   "sense_relied_on": "by willing, not by force"}]}


def fake_ask_factory(compare_verdict="pass"):
    seen = []

    def ask(prompt, effort, timeout, tag):
        seen.append(tag)
        if tag.startswith("muse-gloss"):
            return {"id": "q-gloss-1", "error": None, "finished_at": "2026-10-18T18:01:00Z",
                    "answer": '{"gloss": "Not by necessity but by willing we act, and God compels no one to the good.", "lemmas": [], "scripture": [], "gaps": [], "uncertainties": []}'}
        return {"id": "q-compare-1", "error": None, "finished_at": "2026-10-18T18:02:00Z",
                "answer": ('{"verdict": "' + compare_verdict + '", "checks": {"source_identity": true, '
                           '"completeness": true, "negation": true, "agency": true, "modality": true, '
                           '"doctrine": true, "scripture": true}, "uncertainties": [], '
                           '"notes": "Source: Non necessitate sed voluntate agimus. English: We act by choice, not necessity."}')}

    ask.seen = seen
    return ask


def test_receipt_shape_passes_muse_gate():
    ask = fake_ask_factory()
    receipt, hard = muse_review.build_receipt(PACKET, RESEARCH, ask)
    assert hard == [] and receipt["verdict"] == "pass"
    assert ask.seen == ["muse-gloss-1", "muse-compare-1"]  # gloss runs before compare
    assert receipt["review_provenance"]["schema"] == "review-provenance-muse-v1"
    assert muse_provenance_errors(receipt, PACKET["sections"]) == []
    lanes = {lane["role"] for lane in receipt["review_provenance"]["lanes"]}
    assert lanes == {"blind-gloss", "compare"}


def test_research_is_filtered_to_selected_sections():
    extra = {**RESEARCH, "99": [{"item": "x", "source": "Lexicon", "sense_relied_on": "y"}]}
    receipt, hard = muse_review.build_receipt(PACKET, extra, fake_ask_factory())
    assert hard == []
    assert {e["section"] for e in receipt["review_provenance"]["research"]} == {"1"}


def test_parse_prefers_verdict_object_over_schema_echo():
    echo = '{"verdict": "pass or fail", "checks": {}} garbage {"verdict": "pass", "checks": {"source_identity": true}}'
    assert muse_review.parse_answer(echo)["checks"] == {"source_identity": True}
    assert muse_review.parse_answer("no json here") is None


def test_compare_fail_and_missing_research_fail_closed():
    receipt, hard = muse_review.build_receipt(PACKET, RESEARCH, fake_ask_factory("fail"))
    assert hard == [] and receipt["verdict"] == "fail"
    assert muse_provenance_errors(receipt, PACKET["sections"])  # fail call, no adjudication
    no_research, hard = muse_review.build_receipt(PACKET, {}, fake_ask_factory())
    assert hard == [] and no_research["verdict"] == "pass"
    errors = muse_provenance_errors(no_research, PACKET["sections"])
    assert any("research" in e for e in errors)


def test_runner_error_is_hard_and_no_receipt_claimed():
    def dead_ask(prompt, effort, timeout, tag):
        return {"id": None, "error": "muse runner not alive", "answer": ""}

    receipt, hard = muse_review.build_receipt(PACKET, RESEARCH, dead_ask)
    assert receipt == {} and hard and "blind-gloss" in hard[0]
