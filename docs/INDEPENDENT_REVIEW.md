# Independent review

Second-model sampling over recent audit receipts, plus reader corrections.
Runs weekly (Sundays 03:00, `com.saneapps.fathers-independent-review`).

## Method

1. Sample 5 sections from audit receipts touched in the last 7 days
   (deterministic seed = ISO week; round-robin across books).
2. Screen: NV Nemotron re-verdicts blind (same 7 semantic checks).
3. Confirm: screen hits go to CF Llama-70B (different vendor).
4. Confirmed mismatch = both say fail with at least one common disputed
   check. Single-model disputes are logged as unconfirmed, never escalated.

Screen hits are NOT findings: the screen model is noisy (observed
false-positive rate is high on OCR-damaged sources). Only dual-confirmed
mismatches route to lane owners.

## Dispositions

- agree: second verdict matches the recorded review.
- unconfirmed: one model disputes; logged, not routed.
- mismatch: both dispute; routed to the owning lane (`docs/OWNERSHIP.md`).
- escalated: mismatch unresolved when the next weekly run lands
  (resolution = any receipt in the book reworked).
- error: API/parse failure; never a finding, never filed.

## Lane-owner SLA

Triage confirmed mismatches within 7 days: re-review the section and
either correct the translation (new tip + receipt) or record why the
recorded review stands (receipt notes amendment). Untriaged mismatches
re-appear as escalated in the digest.

## Reader corrections

`scripts/corrections.py` snapshots open `correction` issues weekly for the
digest. Triage: reproduce against the locked source, fix forward with a new
tip + receipt when the reader is right, reply on the issue either way.
Accepted corrections that reveal a systematic error also update the
producing lane's SOP or checker prompt.

## Calibration (future work)

A golden set (known-good + known-bad sections) to measure reviewer
precision/recall per model. Until then, treat single-model hit rates as
uncalibrated and rely only on dual confirmation.
