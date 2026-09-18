# REVIEWS-A closeout-4 verdict: Ad Arcadiam (De recta fide)

Book: `cyril-alexandria-recta-fide-court`, treatise Ad Arcadiam Marinamque
Packet: `books/cyril-alexandria-recta-fide-court/reviews/audit/arcadia_closeout4.packet.json`
Packet sha256: `254e20b82901ca6ffc9e2df4b564ba9ab8fc1379d6ba390ceb467cc4fd377c54`
Scope: 41 at-risk sections (20, 22, 24, 27-29, 32-35, 40, 42, 45-49,
51-53, 56, 57, 59, 64, 67-69, 73, 79, 81, 83, 84, 87, 89, 90, 92-94,
96, 97) of 100.
Provenance: packet `source_text` == audit
`ad_arcadiam_marinamque_source_clean.json` for 41/41; packet `english`
== translations `ad_arcadiam_marinamque_english.json` for 41/41.
Packet reflects the post-E1-fix JSON (commit 2e10c8f97).

## Verdict: PASS (all 41 sections)

Ground truth: packet-bound `source_text` + `english`. Translation
prose is faithful everywhere sampled. All triage-listed E1 sites for
this treatise verified fixed (s22, s34; s35 E4 malformed label now
correct `Habakkuk 3:18`). No rotated-label residue found in this
packet -- the fix pass covered Arcadia completely as far as the
sweeps and reads show.

## Evidence

- Deep Greek-English reads (10 sections, every clause): s22, s34,
  s35, s64, s68, s73, s81, s83, s89, s92, s97. All PASS on prose:
  negations, subjunctives/optatives, comparatives, speaker turns,
  and Pusey-paragraph structure all faithful.
- Mechanical census: no structural errors; char ratios 0.97-1.19,
  median 1.11 -- tightest of the five notes.
- Gemini sweep: 39/41 rows fully pass (2 rows lane_error, see below).
  Scripture flags adjudicated: s81 (Heb 12:1-2 correctly labels the
  cloud-of-witnesses quote; trailing Heb 8:1-2 placement loose --
  minor); s68 (Jn 6:27; Jn 11:43-44; Rom 3:25 all at true clauses --
  flag overstrict, false positive); s89 (Rom 9:33; Lk 2:29-34;
  Rom 10:3-9 correct; Isa 28:16 placement loose -- minor).
- Jev sweep: 41 rows. All flags adjudicated FALSE POSITIVES against
  the reads: s64 neg/scripture (1 Jn 1:1-2; Jn 14:1; 1 Pet 1:21;
  Jn 6:47; 1 Jn 3:23 all at true clauses); s22/s73/s83 completeness;
  s34/s92/s97 negation. Consistent with triage E2 (sweep windowing
  fails on abbreviated refs and en-dash ranges; noisy-OCR source).
- E1-fix verification: s22 (Deut 6:5; Rom 8:38-39; Rom 14:10;
  Mt 25:31; Ps 7:11) all at true clauses; s34 (Gal 3:5; Heb 2:2 +
  Gal 3:19 doubled true refs; Gal 3:23-27) correct; s35
  (Mt 28:19; Gal 4:8-9; Gal 6:14; Hab 3:18) correct.

## Advisory minors (translation lane; non-blocking, left untouched)

1. s89: `(Isaiah 28:16)` sits after the Simeon/Luke quote while
   belonging to the opening stone-of-stumbling sentence. Loose, not
   rotated onto a foreign quote; lowest-priority cleanup.
2. s81: trailing `(Hebrews 8:1-2)` placement loose (belongs with the
   high-priest discussion two sentences up).
3. Gemini lane_error rows (no gem verdict; Jev-covered, both Jev
   clean): s35, s48. No coverage gap.

## Remainder

None for this treatise.
