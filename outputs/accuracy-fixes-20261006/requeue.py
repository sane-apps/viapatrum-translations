#!/usr/bin/env python3
"""Send the owner-approved accuracy corrections (red-team 2026-10-06) back
through the pipeline's own source check. The corrected English is already in
books/*/translations; each section's staged file becomes a hold whose notes
name the error, so a lane redrafts it with those notes, runs the blind
two-model check, and re-certifies the book (held_review.reopen puts it first).
Old staged files are copied next to this script. Usage: requeue.py [--apply]
"""
import json, re, shutil, sys
from pathlib import Path

T = Path.home() / "SaneApps/clients/translations"
sys.path.insert(0, str(T / "scripts"))
import os; os.chdir(T)
import work_pipeline as W  # noqa: E402
import held_review as H  # noqa: E402

APPLY = "--apply" in sys.argv
OUT = Path(__file__).resolve().parent
FIXES = [
    ("tertullian-on-idolatry", "outside are worshipped against God",
     [("mistranslation", "the very hands that outside are used to worship against God", "quae foris aduersus deum adorantur",
       "adorantur is passive: the hands themselves are worshipped outside (in the idols they make), not hands used to worship.")]),
    ("eusebius-emesa-fragmenta-galatas", "in this way I helped them",
     [("mistranslation", "and in this way I put them on", "καὶ οὕτως αὐτοῖς ἐβοήθησα", "ἐβοήθησα means 'I helped them'; only περιεθέμην is 'put on'."),
      ("mistranslation", "because I considered it most valuable", "ὅτι μάλιστα πλείστης ἠξίωμαι",
       "ἠξίωμαι is passive with a genitive: 'I have been counted worthy of the very greatest (care)'.")]),
    ("severianus-fragmenta-ephesios", "the rule not to give a certificate of divorce",
     [("omission", "the rule about giving a certificate of divorce", "τὸ μὴ διδόναι βιβλίον ἀποστασίου",
       "The English dropped μή: the rule is NOT to give a certificate of divorce; it reverses the meaning."),
      ("speaker", "so also he taught me by revelation", "οὕτω κἀμὲ κατ' ἀποκάλυψιν",
       "Inside 'Paul wants to show', 'me' has no speaker; keep it clear the Lord taught Paul himself by revelation.")]),
    ("origen-ezekiel-fragments", "with his excrement",
     [("mistranslation", "from his foreparts", "ἀπὸ τῶν προχωρημάτω(ν) αὐτοῦ",
       "προχώρημα is excrement (confirmed by σκυβαλώδης ἔκκρισις in the next clause), not 'foreparts'.")]),
    ("eustathius-de-melchisedech", "who had taken hold of the height of righteousness",
     [("mistranslation", "the line forgotten for its extreme unrighteousness", "τῷ τῆς ἄκρας ἀδικίας ἐπιλελημμένῳ γένει",
       "ἐπιλελημμένος (ἐπιλαμβάνομαι) means 'having taken hold of', not ἐπιλελησμένος 'forgotten'; same for the righteous man."),
      ("omission", "What then might someone say?", "Καὶ μετ' ὀλίγον τόπον",
       "The source marks a gap: 'And a little further on'. Keep that marker.")]),
]

receipt = {"apply": APPLY, "sections": []}
books = set()
for book, needle, findings in FIXES:
    pairs = W.load_pairs(book)
    hits = [p for p in pairs if needle in " ".join(p["english"])]
    if len(hits) != 1:
        receipt["sections"].append({"book": book, "error": f"{len(hits)} sections contain the corrected text"})
        continue
    p = hits[0]
    f = W.STAGE / book / "sections" / f"{re.sub(r'[^A-Za-z0-9_.-]', '_', p['id'])}.json"
    j = json.loads(f.read_text()) if f.exists() else {"section": p["id"]}
    new = {**j, "section": p["id"], "_status": "hold", "pass_b_english": p["english"],
           "_why": "owner-approved correction (red-team 2026-10-06): recheck this section against the source",
           "open_findings": [{"class": c, "quote": q, "source_quote": sq, "why": why} for c, q, sq, why in findings],
           "confidence": "held"}
    receipt["sections"].append({"book": book, "section": p["id"], "staged": str(f), "was": j.get("_status"),
                                "findings": len(findings)})
    if APPLY:
        if f.exists():
            shutil.copy2(f, OUT / f"{book}__{f.name}.before")
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(new, indent=1, ensure_ascii=False))
        tries = f.with_suffix(".retries")
        if tries.exists():
            tries.unlink()
    books.add(book)
if APPLY:
    H.reopen(books)
(OUT / ("receipt.json" if APPLY else "dry-run.json")).write_text(json.dumps(receipt, indent=1, ensure_ascii=False))
print(json.dumps(receipt, indent=1, ensure_ascii=False))
