# REG-SHIP registration review: Photius Bibliotheca codices 1–17 (Mini, 2026-09-18)

Book: `photius-bibliotheca`
Packets: `books/photius-bibliotheca/reviews/audit/bibl_codex_{1..17}_regship.packet.json`
Receipts: `books/photius-bibliotheca/reviews/audit/bibl_codex_{1..17}_regship.review.json`
Scope: one single-row packet per codex, cut fresh from the 4b rows
(seed 20260918, explicit section N); codex-1 packet additionally carries
`publication_scope` == the built site work scope. Provenance: all 17
packet `source_text` == book `bibl_codex_N_source.json` Greek; all 17
packet `english` == book `bibl_codex_N_english.json` row English
(mechanically verified, 8/8 checks x17). Section ids are codex numbers
(rows carry explicit `"codex": N` plus a `"section": N` key added in this
lane; no English or Greek token changed — tracked diff is 34 one-line
`+section` insertions only).

## Verdict: PASS, all 17 (ship-blocking defects: none)

## Packet-scope adjudication

No cross-codex mismatch in any of the 17: locus, identity subject, Greek
names, and English subject agree throughout (packet 8 is Origen De
Principiis; 14 Apollinarius of Hierapolis in Asia; 16 Ephesus; 17
Chalcedon with 15 sessions). The closeout-4 lock-depth flags are
resolved: the 4b lane replaced the 10 abbreviated lock excerpts with
genuine Bekker Greek (loci: 1→pp.1–2; 3→pp.2–3; 4,5,6,7→p.3; 8→pp.3–4;
9,14,15→p.4), and the packets bind that Greek. The 7 composed-summary
locks (2, 10, 11, 12, 13, 16, 17) remain short but pass the
reference-originality gate and are rendered exactly; Phase C
transcription stays deferred, non-blocking.

## Clause reads (this lane; full Greek-vs-English read of all 17)

- 1: four objections complete; negations rendered (οὐκ ἐμνήσθησαν→"none
  did"; οὐδεμίαν μνήμην→"no mention"); Acts appeal carries the Acts 17:34
  allusion (clear); ἀπίθανον/κακόπλαστον→"implausible ... fabrication".
- 2: one-liner exact.
- 3: embassy narrative complete — persons (Arethas, Caïsus, Abrames,
  Alamandarus, Timostratus, John, Mavias hostage, Elesbaas), places
  (Phoenicon, Taurene mountains, Auxumis metropolis, Adulis 15 days,
  Aue), numbers (~5000 elephants, whole-month + two-month festivals,
  mid-spring Taurus, post-solstice), climate reversal with zodiac pairs,
  Nile flood, islanders (stature/skin/hair, oyster-fish diet, unknown
  dialect). Negations rendered (οὐκ ὀλίγον→"not small"); οὐ μὴν ἀλλὰ
  transitional; πελάζειν-clause per the 4b parsing. The 4b Jev
  negation flags (conf 0.01–0.16) were adjudicated model artifact after
  clause audit; the text is unchanged since, so the adjudication stands.
- 4: οὐ πάνυ λαμπρός→"not altogether brilliant"; πιστωθὲν kept neuter;
  Mopsuestia identification hedged with οἶμαι→"I believe".
- 5: comparatives rendered; ἀφοριστικῷ→"aphoristic"; ἐξ ἀκρισίας litotes
  →"not from want of judgment".
- 6: ῥήτορος→"an orator if ever there was one"; ἡδονῆς ἄξιον→"what gives
  delight"; two-way superiority sentence kept.
- 7: σαθρώσας→"rotting away" (undermine); σύγκρατος→"well-tempered".
- 8: all four books inventoried; hostile βλασφημεῖ frame preserved, not
  softened; μεμυθολογημένος→"mythologized account"; κατὰ τὰς
  γραφάς→"according to the Scriptures"; γενητὸς καὶ φθαρτὸς→"created
  and perishable".
- 9: ἀρχῇ + τέλει both rendered (genuine Greek resolves the old
  end-only flag); ἔλεγχος/βεβαίωσις contrast kept.
- 10, 11, 12: short notices exact, incl. the "ten extant" parenthesis
  and ἀπώλετο→"has perished" (twice).
- 13: second edition differs-and-agrees rendered.
- 14: clean Greek (OCR noise gone); λέγεται/οὔπω→"said to exist ...
  not yet come upon".
- 15: πρακτικόν→"minutes" (not history); ὑπάρχον→"offered as";
  εὐτελὲς→"paltry".
- 16: Ephesus; Cyril letters + Nestorius replies; apostrophes present.
- 17: 15 sessions; Dioscorus/Eutyches condemned; Nestorius
  ἀφωρίσθη→"excommunicated"; Flavian vindicated posthumously with
  Eusebius of Dorylaeum, Theodoret, Ibas.

## Evidence

- Fresh-packet gates (this lane, all 17): structural OK; tip-ready ok;
  reference-originality zero FAIL (Freese 1920 reference-only).
- Binding semantic evidence, still current: 4b Gemini 10/10 all-pass;
  4b Jev 8/10 + 2 adjudicated; closeout-4 reads on the 7 untouched rows.
  No English/Greek token changed since those sweeps (tracked diff
  proves it); live model keys are absent on this machine, so no
  duplicate sweep was run — recorded, not worked around.
- Scope: built work is slug photius-bibliotheca, title Bibliotheca,
  author Photius of Constantinople, Bekker 1824 edition, sections
  1–17 ordered; blurb discloses the 1–17 extent and the 18–279
  exclusion; no first-English claim anywhere (Freese 1920 PD English
  exists and is disclosed).

## Loader note (data-side fix, no site code touched)

The tip loader keyed rows on absent `section` and collapsed all 17
codices into one "Origen" work with a single section "None", silently
dropping 16 codices. Fixed data-side: `"section": N` on all 34 row
files + one identical `bibl_codex_N_meta.json` per stem (slug, title
Bibliotheca, Photius author, Bekker edition, 9th-century era_note
overriding the wrong first-three-centuries default). Identity
author/work/edition now matches the packet identity exactly. Known
cosmetic defect (NOT fixed — needs a loader-sort or zero-pad rename
with Logos-lane coordination, both out of lane scope): the tip merge
appends stems in filename-glob order, so the reader lists sections
10–17 then 1–9 instead of 1–17. Content is complete (all 17 codices,
correct heads) and the bound scope is gate-consistent; only display
order is off.

## Remainder

Deferred Phase C (lock transcription for codices 2, 10–13, 16, 17)
unchanged. No ship-blocker found: registration GO.
