# REVIEWS-A closeout-4 verdict: Matthew Fragments

Book: `cyril-alexandria-matthew-fragments`
Packet: `books/cyril-alexandria-matthew-fragments/reviews/audit/matthew_fragments_closeout4.packet.json`
Packet sha256: `5d267c23789d00162ba65c7da274673fac6856745e141c3819496f7ee89673bf`
Scope: full book, all 290 sections (loci Mt 1,1 through Mt 28,18).
Provenance: packet `source_text` == book `matthew_fragments_source.json`
Greek for 290/290; packet `english` == book
`matthew_fragments_english.json` for 290/290. Packet reflects the
post-E1-fix JSON (commit 2e10c8f97).

## Verdict: PASS (translation prose, all 290 sections)

Ground truth: packet-bound `source_text` + `english`. Fragments are
independent per-verse units, so no contiguous-prose boundary analysis
applies (unlike Adoration). Translation prose is faithful everywhere
sampled: negations, comparatives, genitive absolutes, optatives,
speaker turns, and catena asterisk/cross markers all render exactly.

## Evidence

- Deep Greek-English reads (16 sections, every clause): s4, s16, s19,
  s22, s32, s63, s71, s78, s88, s89, s95, s199, s210, s214, s235, s262.
  All PASS on prose.
- Mechanical census: no structural errors; char ratios 0.64-1.95,
  median 1.11. Extremes checked by hand: s78 (0.64) compacts a long
  ritual list without loss; s65 (1.95) is a broken scholion honestly
  completed with a bracketed supplement ("[guard]").
- Gemini sweep: 290 rows, 281 fully pass. 9 sections carry non-pass
  dimensions, all adjudicated below (label placement, not prose).
- Jev sweep: 290 rows. Scripture flags (~30) are near-all label
  placement; negation/modality/completeness flags are low-confidence
  (mostly c<0.5) and contradicted by the deep reads.

## E1 rotation adjudication (task item)

- Triage-listed sites FIXED, verified 3/3 in packet: s95 labels
  (Mt 10:2; Lev 24:5-7; Jn 6:33-35; Mt 5:13-14; 2 Cor 2:15; Ps 68:27)
  all at true clauses; s199 (Mt 20:1-16; Mt 25:1-13; 2 Pet 1:4;
  Rom 8:15) all at true clauses; s210 (Mt 21:23; Ps 110:4) at true
  clauses. E3 unfiled item confirmed as unfiled: s210
  "God-breathed scriptures" (2 Tim 3:16, Greek-confirmed) carries no
  parenthetical -- owner decision still pending, correctly untouched.
- Same-pattern RESIDUE the fix pass missed (7 sections, verified by
  hand). Each label below sits on the preceding quote while belonging
  to the following one (or to no quote in the section):
  - s40: `(Matthew 5:18)` on the John 4:24 "in spirit and truth"
    quote; `(John 4:23)` stranded at paragraph end.
  - s56: `(Matthew 5:34-35)` on the Hebrews 6:16 "swear by the
    greater" quote; `(Hebrews 6:16)` on the Mt 5:35 Jerusalem sentence.
  - s124: `(Matthew 11:25)` locus label on a Psalm quote ("Let them
    confess, Lord, your great name"); the Psalm is unlabeled.
  - s19: `(Matthew 3:8-9)` locus label on the Romans 6:4 "newness of
    life" quote; `(Romans 6:4)` stranded at paragraph end.
  - s22: `(Matthew 3:10)` locus label on the Jeremiah 23:29 "axe
    cutting rock" quote (true ref per fix-commit s21 precedent).
  - s278: cascade -- `(Matthew 27:38)` on the Isaiah 53:12 "reckoned
    with the lawless" quote; `(Isaiah 53:12)` on the Isaiah 53:5
    "by his bruise" quote; `(Isaiah 53:5)` on the John 19:15 "no king
    except Caesar" quote; `(John 19:15)` stranded at the end.
  - s282: `(Matthew 27:50)` locus label doubled with the true
    `(1 Peter 4:19)` on the 1 Pet 4:19 quote.
- Benign doubled locus+true labels (true ref present and correctly
  placed; link duplication only): s4, s16, s46, s59, s89, s192, s235,
  s262. Same class the "drop 2 duplicate links" pass reduced but did
  not eliminate (cf. pulcheria s28).
- Fix-commit-pattern sites spot-checked CLEAN: s9 (Jn 10:16), s10
  (Gen 28:12; 32:28), s15 (Isa 11:1; Song 2:1), s21 (Rom 11:17-24;
  Jer 23:29), s32, s71 (Sir 5:12; Prov 18:21; Ps 141:3 MT numbering),
  s78 (Lev 14:4-7; Acts 2:31).

## Advisory minors (translation lane; non-blocking, left untouched)

1. The 7 rotated-label sections above: reposition per the E1
   strip-identity gate, then re-sweep Matthew only (same procedure as
   2e10c8f97). Rebuild NOT blocked -- defect is pre-existing link
   placement, per triage E1 standing rule.
2. s214: verbless Greek clause bridged interpretively ("through whom
   come the priests and teachers"); meaning preserved, gem
   completeness/agency flags adjudicated false positive.
3. s63 tail renders OCR-damaged Greek ("73 Mt 7 6, 14 ...") as
   reconstruction; already carries textual_uncertainty risk, correctly.

## Remainder

None for this book. 91 sections carry non-Matthew parentheticals;
the residue screen covered the gem/jev-flagged subset plus 6
single-label spot checks (s16, s32, s59, s71, s78, s88 all clean).
A systematic label-position pass over the remaining unflagged
label-bearing sections is translation-lane follow-up, not a verdict
blocker.
