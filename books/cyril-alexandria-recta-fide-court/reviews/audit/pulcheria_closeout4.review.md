# REVIEWS-A closeout-4 verdict: Ad Pulcheriam (De recta fide)

Book: `cyril-alexandria-recta-fide-court`, treatise Ad Pulcheriam Eudociamque
Packet: `books/cyril-alexandria-recta-fide-court/reviews/audit/pulcheria_closeout4.packet.json`
Packet sha256: `7c285e0f9a87833fcbc7c507ff7cdfd86805977cad7f12a2882100e28036cf50`
Scope: 41 at-risk sections (3-11, 13-15, 18-28, 30, 31, 33-47) of 48.
Provenance: packet `source_text` == audit
`ad_pulcheriam_eudociamque_source_clean.json` for 41/41; packet
`english` == translations `ad_pulcheriam_eudociamque_english.json`
for 41/41. Packet reflects the post-E1-fix JSON (commit 2e10c8f97).

## Verdict: PASS (all 41 sections)

Ground truth: packet-bound `source_text` + `english`. Translation
prose is faithful everywhere sampled. No rotated-label residue found
in this packet. E3 unfiled item confirmed in its recorded state
(see below) -- owner decision, correctly untouched.

## Evidence

- Deep Greek-English reads (8 sections, every clause): s3, s8, s20,
  s23, s24, s28, s31. All PASS on prose: negations, participles,
  purpose/result clauses, and Hebrews-catena quotation chains all
  faithful. Psalm numbering MT-consistent (s20 Ps 77:6).
- Mechanical census: no structural errors; char ratios 0.99-1.25,
  median 1.12.
- Gemini sweep: 39/41 rows fully pass (2 rows lane_error, see below).
  Scripture flags adjudicated: s8 (Heb 2:16-18; Phil 2:7; Heb 10:14
  at true clauses; Heb 7:23-25 placement loose -- minor); s31
  (Lk 2:14; Jn 1:32-34 at true clauses -- flag overstrict, false
  positive). Agency flag s23 (Phil 2:6-8; Heb 3:1-6 at true clauses;
  Word-as-subject preserved throughout) adjudicated false positive.
- Jev sweep: 41 rows, only 4 flags, all low-confidence and all
  contradicted by the reads: s3/s8/s28 scripture (Joel 2:28;
  Ps 68:11; Heb 2:16-18; Wis 1:13-14 verified at true clauses),
  s24 negation (c0.03).
- E3 verification: s20 "summing up all things in Christ" carries its
  `(Ephesians 1:10)` parenthetical in-text and is filed in
  `notes_covered`, but has no `added_allusions` certainty entry --
  exactly the recorded "unfiled" state. Owner decides whether to
  file; review takes no position.

## Advisory minors (translation lane; non-blocking, left untouched)

1. s28: `(Wisdom 1:13-14; 2:24) (Wisdom 2:24)` -- true ref doubled
   with a redundant second label. Same duplicate-link class the
   2c23e10d2 pass reduced elsewhere; drop the trailing duplicate
   if the lane re-touches this treatise.
2. Gemini lane_error rows (no gem verdict; Jev-covered, both Jev
   clean): s45, s47. No coverage gap.

## Remainder

None for this treatise.
