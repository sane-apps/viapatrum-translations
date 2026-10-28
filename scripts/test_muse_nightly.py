"""Muse nightly lane: one queue item end to end with a fake muse.
python3 -m pytest scripts/test_muse_nightly.py"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import muse_nightly  # noqa: E402

DRAFT = {"section": "1", "title": "Choice, Not Necessity",
         "pass_a_gloss": "Not by necessity but by willing we act in every case, and God compels no person toward the good; the will stays its own master in choosing.",
         "lemmas": [{"form": "voluntate", "lemma": "voluntas", "gloss": "by willing"}],
         "choices": [{"term": "voluntate", "english": "by choice", "why": "abl. of means", "rejected": ["by fate"]}],
         "bible_refs": [], "variants": [], "translator_notes": [],
         "english": ["We act by choice, never by necessity, in every case we face. God forces no one toward the good. The will remains master of its own choosing, free and uncompelled by any fate outside itself."]}


def _item(tmp_path, research=True):
    eng = tmp_path / "english.json"
    src = tmp_path / "source.json"
    raw = tmp_path / "witness.txt"
    raw.write_text("printed witness")
    eng.write_text(json.dumps([{"section": "1", "english": ["Old text."]}]))
    src.write_text(json.dumps([{"section": "1", "latin": ["Non necessitate sed voluntate agimus, et Deus neminem cogit ad bonum."]}]))
    item = {"english": str(eng), "source": str(src), "raw": str(raw),
            "identity": {"author": "A", "work": "W", "edition": "E", "locus_scheme": "section",
                         "source_url": "https://example.test/x"},
            "section": "1",
            "research": [{"item": "voluntate", "source": "Lexicon s.v.", "sense_relied_on": "by willing"}] if research else []}
    return item


def _ask(prompt, effort, timeout, tag):
    if tag.startswith("nightly-draft"):
        return {"id": "d1", "error": None, "answer": json.dumps(DRAFT)}
    if tag.startswith("muse-gloss"):
        return {"id": "g1", "error": None, "finished_at": "2026-10-18T18:01:00Z",
                "answer": '{"gloss": "Not by necessity but by willing we act, and God compels no one to the good.", "lemmas": [], "scripture": [], "gaps": [], "uncertainties": []}'}
    return {"id": "c1", "error": None, "finished_at": "2026-10-18T18:02:00Z",
            "answer": '{"verdict": "pass", "checks": {"source_identity": true, "completeness": true, "negation": true, "agency": true, "modality": true, "doctrine": true, "scripture": true}, "uncertainties": [], "notes": "Source: Non necessitate sed voluntate agimus, et Deus. English: We act by choice, never by necessity, in every case."}'}


def test_item_passes_end_to_end(tmp_path, monkeypatch):
    monkeypatch.setattr(muse_nightly, "ROOT", tmp_path)
    item = _item(tmp_path)
    # process_item resolves english/source under ROOT; seed copies there.
    rec = muse_nightly.process_item(item, _ask, tmp_path / "run")
    assert rec["status"] == "pass", rec
    assert rec["validate_errors"] == [] and rec["receipt_verdict"] == "pass"
    assert (tmp_path / "run" / "review.json").exists()


def test_item_without_research_stops_before_receipt(tmp_path, monkeypatch):
    monkeypatch.setattr(muse_nightly, "ROOT", tmp_path)
    rec = muse_nightly.process_item(_item(tmp_path, research=False), _ask, tmp_path / "run")
    assert rec["status"] == "needs-research"
    assert not (tmp_path / "run" / "review.json").exists()
