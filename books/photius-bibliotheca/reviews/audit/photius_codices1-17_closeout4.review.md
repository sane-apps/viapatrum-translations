# REVIEWS-A closeout-4 verdict: Photius Bibliotheca, scope + packets (codices 1-17)

Book: `photius-bibliotheca`
Packets: `books/photius-bibliotheca/reviews/audit/bibl_codex_{1..17}_closeout4.packet.json`
Scope: one single-row packet per codex; packet N has locus N,
expected [N], coverage 1/1, and names codex N's work in identity.
Provenance: all 17 packet `source_text` == book `bibl_codex_N_source.json`
Greek; all 17 packet `english` == book `bibl_codex_N_english.json`
row 1 English. No packet carries another codex's text.

## Verdict: CONDITIONAL -- 9 PASS, 8 lock-depth FLAG (see table)

## Packet-scope adjudication (task item a)

The flagged scope artifact is REAL but is a lock-DEPTH gap, not a
mis-scoping: every packet scopes its named codex (locus, identity,
and subject all agree -- e.g. packet 8 is Origen De Principiis,
packet 14 is Apollinarius, packet 16 is Ephesus). NO cross-codex
mismatch found in any of the 17. What the sweeps caught is English
rendering the fuller Bekker codex text while the locked Greek
(`sources/photius_bibliotheca_greek_lock.txt`, header: "New English
from this Greek only") carries an abbreviated excerpt. Char ratios
make the split exact: the 8 flagged codices sit at 1.59-27.66, the 9
clean ones at 0.93-1.54. Lock-hygiene notes: CODEX 6/7/8/9/10 blocks
appear twice in the lock file (verified byte-identical -- harmless);
cod. 14 Greek has mixed-script OCR noise (`Ἀntonείνου`, source lane).

## Per-codex verdicts

| Cod. | Subject | Ratio | Verdict | Note |
|------|---------|-------|---------|------|
| 1 | Theodore presb. / Dionysius | 1.33 | PASS | "shortly before his death" small expansion -- minor |
| 2 | Hadrian Isagoge | 0.93 | PASS | one-liner, exact |
| 3 | Nonnosus History | 27.66 | FLAG (lock-depth) | Greek 1 sentence; English full ethnographic narrative (Caisus, Axumis, elephants, islanders). Subject correct; needs lock expansion + Freese-originality check (lock: Freese "reference only -- do not copy") before ship |
| 4 | Theodore Mops. / Eunomius | 1.59 | FLAG (lock-depth) | extra "bishop of Mopsuestia" identification is genuine Photius, absent from lock excerpt only |
| 5 | Sophronius / Eunomius | 1.78 | FLAG (lock-depth) | aphoristic-style remarks genuine, absent from lock excerpt only |
| 6 | Nyssa / Eunomius (1) | 2.37 | FLAG (lock-depth) | enthymeme + superiority sentences genuine, absent from lock excerpt only |
| 7 | Nyssa / Eunomius (2) | 1.54 | PASS | "storms the tottering ramparts" vivid but defensible |
| 8 | Origen De Principiis | 2.53 | FLAG (lock-depth) | migration of souls, living stars, incarnation/soul/punishment, created-perishable world all genuine cod. 8 content; lock excerpt drops them |
| 9 | Eusebius PE | 2.08 | FLAG (lock-depth) | "beginning and end" of book 15 overstates (end only); purpose sentence beyond lock |
| 10 | Eusebius DE | 0.98 | PASS | exact |
| 11 | Eusebius PE eccl. (lost) | 1.15 | PASS | exact |
| 12 | Eusebius DE eccl. (lost) | 1.04 | PASS | exact |
| 13 | Eusebius Ref./Def. | 1.28 | PASS | exact |
| 14 | Apollinarius | 2.85 | FLAG (lock-depth) | "Marcus Antoninus Verus", style praise, unread-works sentences beyond lock excerpt; plus `Ἀntonείνου` OCR noise in lock |
| 15 | Gelasius Nicaea | 2.04 | FLAG (lock-depth) | style slam + detailed-account sentences genuine cod. 15, absent from lock excerpt |
| 16 | Ephesus | 0.96 | PASS | typo nits: "Cyrils", "mans" lack apostrophes -- minor |
| 17 | Chalcedon | 1.19 | PASS | exact |

## Evidence

- Full Greek-English read of all 17 codex rows: PASS on codex
  fidelity for 16 (content matches the named Bekker codex throughout);
  cod. 3's narrative is subject-correct but unverifiable
  clause-by-clause against the one-sentence lock excerpt.
- Gemini sweep: 17 rows. 9 fully pass. The 8 non-pass rows
  (3,4,5,6,8,9,14,15 -- source_identity/completeness/doctrine) each
  cite English-beyond-locked-Greek, confirming the depth gap rather
  than mistranslation.
- Jev sweep: 17 rows. Clean for 1,2,7,10,11,12,13,16,17. Flags on
  3,4,5,6,8,9,15 (source_identity/completeness, c0.09-0.96) confirm
  the same gap; no flag contradicts the reads.
- Mechanical census: no structural errors in any packet.

## Loader-relevant finding (SHIP lane; NO site code touched -- site/ and dist/ live outside this repo)

Section ids are 1:1 with codex numbers (section "8" == codex 8) in
every packet, source file, and english file (rows carry explicit
`"codex": N`). A section-keyed loader therefore resolves correctly
TODAY, but only by this coincidence: nothing in the row record shape
forces section == codex, and the flagged codices' English already
spans content far beyond what a section-scoped lock excerpt suggests.
If the loader ever ingests multi-row-per-codex splits (or the lock
expansions below add rows), section keys will collide across codices.
Recommend the SHIP lane key photius loader rows on the explicit
`codex` field (present in english rows) rather than `section`.
Also: `books/photius-bibliotheca/book.yml` description still says
"Codices 1-15 ... Codices 16-279 are not in this volume" while the
book now holds 16 and 17 -- stale metadata the loader may surface.

## Remainder / lane action (translation lane owns; review blocks nothing already live)

Photius is pre-ship (site 404 per closeout brief), so unlike the
Cyril books there is no "already live" tolerance to lean on: expand
the 8 lock excerpts to full Bekker Greek, re-sweep the 8 codices
(gem + jev), and correct the book.yml description + cod. 16 typos +
cod. 14 OCR noise in the same pass. Cod. 3 additionally needs the
Freese-originality check. Re-review after that pass before SHIP
registers photius.
