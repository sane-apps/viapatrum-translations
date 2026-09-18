# Photius, Codices 1–17 — Closeout-4b re-review (PHOTIUSRR lane, Mini, 2026-09-18)

Scope: the 10 gate-failing rows (1, 3, 4, 5, 6, 7, 8, 9, 14, 15) were re-rendered
from genuine Bekker Greek; the other 7 rows are untouched. This note does NOT
alter the closeout-4 note (photius_codices1-17_closeout4.review.md).

## What was wrong

The in-repo lock excerpts for the 10 failing codices were composed summaries,
not Bekker's text (Ἀνέγνων for Bekker's Ἀνεγνώσθη; one-line stands-ins for
multi-page codices; modern glosses incl. Latin words, e.g. cod. 9
"Demonstratio Evangelica", cod. 15 "φλωρ. 475"; fabricated bekker_page 1:1
with codex number). The English rows had been expanded from Freese 1920
(reference-only) instead of the Greek. The lock file also carried duplicate
sections (6, 7, 8, 9, 10 twice); deduplicated in this pass.

## Greek witness (all transcribed, pp. cited)

- Bekker 1824 item bibliothecaexrec00photuoft ("Bibliotheca. Ex recensione
  Immanuelis Bekkeri"), direct HTTPS download of the exact item file
  bibliothecaexrec00photuoft_djvu.txt (3,225,614 bytes, sha256
  e9c0461bb810fb58ed17f80f9a0b24debdca2d639dadaac35fb985c1fec6982f):
  ZERO Greek characters — IA OCR mapped the Greek to Latin lookalikes.
  Unusable; documented, not committed.
- Firecrawl: CLI present (v1.23.3 via npx) but "Not authenticated ... Run
  'firecrawl login' to authenticate" — no API key on this machine, and a
  markdown-scrape lane cannot deliver a 3 MB raw text faithfully anyway.
  Fell back to direct HTTPS per lane brief.
- Working Greek: Hoeschel 1653 Google OCR (archive.org item
  bub_gb_ZW0dhUNjuQoC, 2.48M Greek chars) as reading aid; decisive witness is
  Bekker 1824 page images (leaves n12–n16 = prefatory leaf + pp. 1–5),
  read directly, with enlarged crops for 8 cruxes.
- Lock sections replaced (Bekker loci): 1 → pp. 1–2; 3 → pp. 2–3; 4, 5, 6,
  7 → p. 3; 8 → pp. 3–4; 9, 14, 15 → p. 4. Apparatus/sigla omitted.
- Scan-ambiguous readings kept as printed, flagged here: §3 πελάζειν-clause
  (ἔδει τῶν ἐγχωρίων parsed as genitive of the party concerned; οὐδὲ εἴργειν
  τῆς νομῆς; προσεγίνετο); §3 μετρεῖ παρατείνων; §4 πιστωθὲν (neuter,
  concord-anomaly kept as printed); §5 ἐξ ἀκρισίας; §6 ἡδονῆς ἄξιον;
  §8 κατὰ τὰς γραφάς (grammar disambiguates); §14 λέγεται/οὔπω;
  §15 ὑπάρχον, εὐτελὲς. None affects the English beyond the noted clauses.
- DEFERRED (not this lane): lock excerpts for the 7 passing codices
  (2, 10, 11, 12, 13, 16, 17) are still short composed summaries. Their
  English passes the originality gate, so no lock violation reaches the
  deliverable, but a Phase C should transcribe them from Bekker pp. 2–5.

## Cod. 3 Freese comparison (originality evidence)

Same content, new translation throughout. Sample — Saracen assembly:
- Freese: "The greater part of the Saracens, both those in Phoenicon and
  those beyond Phoenicon and the so-called Taurenian mountains, regard a
  certain place as sacred, where they believe a god was ... and here they
  assemble twice a year..."
- 4b: "Most of the Saracens — those at Phoenicon and those beyond Phoenicon
  and the so-called Taurene mountains — hold a certain place sacred, where,
  as they hold, a god was set free; and there they gather twice each year."
Structure, diction, and sentence breaks differ in every paragraph (Ἀνεγνώσθη
rendered "has been read by me" throughout, ὅτι-clauses as independent
sentences, island ethnography in fresh syntax). Gate confirms: longest
verbatim run under threshold on all rows (see below).

## Reference-originality gate (all 17, quoted)

Command per codex N:
PYTHONPATH=. python3 pipeline/verify_translation_qa.py --english
books/photius-bibliotheca/translations/bibl_codex_N_english.json --source
books/photius-bibliotheca/translations/bibl_codex_N_source.json
--identity /tmp/phx-identity.json --raw-source
books/photius-bibliotheca/sources/photius_bibliotheca_greek_lock.txt
--reference-only books/photius-bibliotheca/sources/freese_1920_full.txt

Baseline (pre-render): FAIL verbatim runs on 1 (51w), 3 (206w), 4 (64w),
5 (51w), 6 (41w), 7 (48w), 8 (130w), 9 (67w), 14 (28w), 15 (21w); clean on
2, 10, 11, 12, 13, 16, 17 — exactly the expected split.

Post-render: all 17 print
"OK structural/current-snapshot checks; no automatic fidelity certification"
with zero FAIL lines (packets 0694c30d…, 2bb3075e…, 294b8890…, 9edaf6ab…,
8a209068…, 79db1b01…, 901ee109…, 1d0fc7af…, a6eaf698…, 07586c6c…, plus
unchanged-row packets). Tip-ready gate (check_pass_ab.py --tip-ready): ok on
all 10 re-rendered pairs.

## Semantic sweeps (/tmp/phx3-gem.jsonl, /tmp/phx3-jev.jsonl)

Same prompts/models/chunking as the 0918 sibling harnesses, reading the fresh
row files (stale closeout-4 packets still bind the old English).
- Gemini (models gemini-3.5/3.1-flash-lite): 10/10 all-pass, 7 dimensions.
  (One 429-driven retry on cod. 3; filed verdict all-pass.)
- Jev (TYPESAFE_API_KEY lane): 8/10 all-pass; negation=fail on cod. 1
  (conf 0.01, re-probe 0.06) and cod. 3 (conf 0.10, re-probe 0.16).
  Adjudication: clause-by-clause audit finds every Greek negation rendered
  (cod. 1: οὐκ ἐμνήσθησαν → "none did"; οὐδεμίαν μνήμην → "no mention";
  cod. 3: οὐκ ὀλίγον, οὐ μόνον…ἀλλά, οὐδὲν (×3), οὐδὲ — all rendered; οὐ μὴν
  ἀλλά correctly treated as transitional). Reproducible but ~0.1-confidence
  model artifact; recorded, translations unchanged (re-wording to chase it
  would require re-gating for no fidelity gain).

## Per-codex verdicts

- 1: PASS (gate OK; gem all-pass; jev 6/7 + adjudicated negation).
- 3: PASS (gate OK; gem all-pass; jev 6/7 + adjudicated negation).
- 4, 5, 6, 7, 8, 9, 14, 15: PASS (gate OK; gem all-pass; jev 7/7).
- 2, 10, 11, 12, 13, 16, 17: PASS, untouched (gate OK as before).
- Cod. 15 translator note corrected: the genuine Greek offers the book as
  minutes (πρακτικόν) rather than history — the old note said the reverse.

## SHIP-REGISTRATION verdict: GO

All 17 rows clear the reference-originality gate with zero errors; both
semantic lanes are effectively clear (Gemini 10/10; Jev flags adjudicated
with audit trail above). No packet/receipt was regenerated in this lane
(reviews/audit packets still bind pre-4b rows — registration should cut
fresh packets from the 4b rows). Deferred Phase C: transcribe lock Greek
for codices 2, 10, 11, 12, 13, 16, 17.
