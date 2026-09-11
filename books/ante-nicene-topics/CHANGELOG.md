# Changelog — Ante-Nicene Dogmatics

## 0.8.4 — 2026-09-10

- Promoted **Melito** + **Victorinus** to `source_verified` after second-model hold-unlock **PASS** (`outputs/reviews/second_model_hold_unlock_audit_2026-09-10.md`).
- MVP now **48/48** `source_verified`. Melito locked to Greek οὐσίαι (“substances”); Victorinus continuous Migne/Routh Latin (incl. *Prius enim lux*).
- Synced same Melito English into christology seed duplicates (`melito_reliquiae_*`).
- `--strict-professional` green. Professional GTG still Yes; Sellable still No.

## 0.8.3 — 2026-09-10

- Cleared Harvey **print_check** on four Irenaeus ids against IA PDF `sanctiirenaeiep00harvgoog` (Vision OCR receipts under `outputs/reviews/printchecks/`).
- Melito: locked clean Greek (PG 5 Fragmenta + Routh); English corrected to **δύο οὐσίας** (“two substances”); still `anf_mediated` pending clear stamp.
- Victorinus: PL 5 Vision OCR matches lock; Walker transposition settled via printed COMMENTARIUS; still `anf_mediated` pending clear stamp.
- Settlement report: `outputs/reviews/caveat_settlement_2026-09-10.md`. Professional GTG still Yes (46 clears); Sellable still No.

## 0.8.2 — 2026-09-10

- Second-model audit **PASS WITH CAVEATS** (`outputs/reviews/second_model_golden_set_audit_2026-09-10_v081.md`).
- Stamped all **46** `source_verified` receipts: `reviewer=second-model-2026-09-10`, `second_model_clear=pass`.
- `--strict-professional` **green**. **Professional GTG: Yes** (caveats: Irenaeus OCR `print_check` pending on 4 ids; Melito + Victorinus remain held `anf_mediated`). Sellable GTG still No.

## 0.8.1 — 2026-09-10

- Second-model v0.8.0 audit **FAIL** on Tertullian Marc. 2.5–6: removed editorial “Take away choice…”; extended CSEL lock through ch.6 `merces`/`necessitate` Latin with `[…]` abridgment.
- **Professional GTG still No** (holds Melito/Victorinus; no clear stamps).

## 0.8.0 — 2026-09-10

- Relocked Irenaeus **AH 4.37.4** and **4.37.5** from continuous Harvey vol.2 Latin; English constrained to each block (counsel stays in 4.37.5 only). MVP **46/48** `source_verified`.
- Melito + Victorinus remain `anf_mediated` (no clean Greek; print/transposition unsettled).
- Strict QA now accepts owner clear **or** named second-model clear with report path (`docs/HUMAN_CLEAR.md`).
- **Professional GTG still No** (0 clears recorded).

## 0.7.9 — 2026-09-10

- Retitled Logos/catalog book to **Ante-Nicene Dogmatics** (dropped “Soteriology and Free Will” subtitle from the volume title).
- Subtitle / cover line: **The Fathers on the Full Counsel of God**.
- Catalog description + About copy cover the full topic map; new cover art in `assets/cover.jpg`; Desktop body `AnteNicene-Dogmatics.docx`.
- Script: `scripts/update_logos_metadata.py` writes Title / Authors / Description / Copyright / CoverImage / body path.

## 0.7.8 — 2026-09-10

- Second-model re-audit **FAIL** acted on: demoted Melito (mediated Grelser Latin), Victorinus (print/transposition), Irenaeus 4.37.4/5 (OCR blocks insufficient); restored Harvey `observabit`/`observans` on AH 5.21.1.
- MVP now **44/48** `source_verified`. **Professional GTG still No.**

## 0.7.7 — 2026-09-10

- Logos PBB log cleanup: Headwords no longer contain colons (Minucius ANF “Argument:” titles shortened); comma-verse Bible links split into full attached targets; `Wisdom` → `Wisdom of Solomon` in Bible datatype targets.
- Rebuilt DOCX + Logos. PBB log no longer reports colon-ignored headwords or orphan `bible.70.*` milestones (blank Logos `[Warning]` line may still appear).

## 0.7.6 — 2026-09-10

- MVP again **48/48** `source_verified`: re-promoted Irenaeus 4.37.4/5 + Victorinus with cleaned Latin, lemmas, apparatus notes (`print_check: pending`).
- Registry expanded **33 → 83** works: all **1237** excerpt ids listed (`scripts/expand_registry.py`); seed stubs use `pending-seed-edition` (not Professional GTG).
- Glossary soft-check in `qa_professional.py` (lemma → allowed English warnings on MVP).
- Second-model **re-audit** in flight for independent clear ruling.
- DOCX + Logos rebuilt for this stamp. **Professional GTG** still **No** until clear per `docs/HUMAN_CLEAR.md` / re-audit.

## 0.7.5 — 2026-09-10

- Relocked Melito incarnation from Reliquiae **Grelser Latin** (Greek OCR column abandoned).
- Relocked Irenaeus AH **5.1.2** continuous Harvey Latin (legacy id `irenaeus_ah_3_18_1`).
- Owner packet: `docs/HUMAN_CLEAR.md`.
- MVP **45/48** `source_verified`; 3 held: Victorinus + Irenaeus 4.37.4/5. **Professional GTG still No** (human clear).

## 0.7.4 — 2026-09-10

Post-audit hardening toward Professional GTG (still **No**).

- Relocked Irenaeus AH 5.21.1 continuous Harvey Latin; chose *calcabit*/tread; documented *observabit* OCR variant.
- Filled empty `lemmas[]` on remaining `source_verified` receipts (auto-seeded from glossary/English — refine on human clear).
- QA: `--strict-professional` fails on pending reviewer / empty lemmas / missing `source_lock`.
- MVP **43/48** `source_verified` (5 still `anf_mediated`: Melito, Victorinus, 3 Harvey Irenaeus spans). Strict QA FAIL = honest Professional GTG block (43 pending human clear).

## 0.7.3 — 2026-09-10

Second-model audit response (Professional GTG still **No**).

- Independent audit: `outputs/reviews/second_model_golden_set_audit_2026-09-10.md` → **FAIL**.
- Fixed Theophilus 2.25 (removed 2.27 obedience/life addition); Ignatius Smyrn. 6 English; Clement Strom. 2.15 sense; Tertullian *Paen.* 2 “compotes” rendering; Arnobius glossary (“free decision”); citation/locus aliases (Arnobius 2.64, Justin 2 Apol. 6, Irenaeus 5.1.2).
- Demoted insecure locks to `anf_mediated`: Melito Reliquiae OCR, Victorinus transposition/OCR, Irenaeus Harvey OCR spans (incl. 5.21.1).
- Marked abridgments with `translation_mode=abridged` + `[…]` where mid-span cuts.
- MVP now **42/48** `source_verified` (honest after audit). Human clear still required for Professional GTG.

## 0.7.2 — 2026-09-10

MVP golden set **48/48** `source_verified`.

- Locked **Dionysius of Alexandria** *On Nature* Greek from local First1K Eusebius PE TEI (anti-Epicurus block, vign ~773–774); rematched English; justification added.
- QA: 48 justifications on disk. Second-model audit in flight. **Professional GTG still pending** that audit + human clear + OCR print-checks.

## 0.7.1 — 2026-09-10

MVP golden-set polish (still not Professional GTG).

- Locked **Gregory Thaumaturgus** creed Son clause from Schaff/Hahn Greek; dropped ANF “through him we are saved” tag absent from that clause.
- Locked **Victorinus** *De Fabrica Mundi* sixth-day Latin (Migne PL 5 OCR); rewrote English to image/likeness — removed invented “capacity to know and choose.”
- Rematched **Dionysius** to Eusebius PE 14.23–24 *On Nature* (anti-atomist); prior evil/free-creature English was the wrong locus. Still `anf_mediated` — local First1K PE TEI lacks Book 14 Greek.
- MVP now **47/48** `source_verified` (1 `anf_mediated`). Deleted Logos **FN Test Pandoc Footnotes** personal book + `/tmp/fn-test.docx`.
- Professional GTG still **No** (no human/second-model clear; OCR print-check; Dionysius Greek pending).

## 0.7.0 — 2026-09-10

Eschatology + Ethics deep mining integrated.

- Added **416** `seed_anf` excerpts (`translations/topics/eschatology_ethics.json`).
- Book now **1237** excerpts across all 10 loci / 35 filled topics. Still seed-grade for new material; MVP golden set unchanged (45/48 `source_verified`).
- Author stub: Passion of Perpetua and Felicity. Professional GTG still **No**.

## 0.6.0 — 2026-09-10

Deep corpus mining into empty systematic loci (still seed-grade).

- Integrated **773** mined excerpts across Theology Proper, Christology, Bibliology, Pneumatology, Ecclesiology, Sacraments (`translations/topics/{theology_christology,bibliology_pneumatology,ecclesiology_sacraments}.json`).
- Book now **821** excerpts total (48 MVP anthropology/soteriology + 773 seeds). Confidence is `seed_anf` / `seed_edition` only for new material — **not** `source_verified`.
- Authors added: Clement of Rome, Firmilian of Caesarea, Eusebius of Caesarea (secondary).
- Eschatology + Ethics mining still pending. Professional GTG still **No**.

## 0.5.0 — 2026-09-10

One-book systematic map + Wave 0 remainder locks.

- **One book:** title **Ante-Nicene Dogmatics**; `topics.yml` filled (~47 topics across 10 loci); `docs/TOPIC_MAP.md`; builder reads taxonomy and all `translations/topics/*.json`.
- Customer About updated for one growing book (no Confidence / GTG jargon).
- Golden set: Methodius FW2 remapped to tlg002 ch.11 Greek; Melito remapped to Reliquiae incarnation fragment. Gregory / Victorinus / Dionysius parked (anf_mediated / uncertain).
- `source_verified` **45/48**. Professional GTG still **No**.

## 0.4.1 — 2026-09-10

Customer surface cleanup: internal QA metadata no longer printed in the book.

- Removed per-excerpt **Confidence** captions from DOCX/Logos builder.
- About / How to read: dropped source_verified counts, GTG jargon, and “confidence labeled” copy.
- STYLE + PROFESSIONAL_BAR: confidence / notes / justifications are internal-only; customer gets citation, English, TN wording notes, attribution, Scripture allusions.
- Soft-removed nested stale `books/ante-nicene-topics/build_book.py` (still printed Confidence).

## 0.4.0 — 2026-09-10

Open-edition locks expanded; free-will golden set largely closed from Greek/Latin.

- `source_verified` now **43/48** (was ~35); justification receipts match.
- Origen *De Principiis*: Philocalia 21 Greek locked for 3.1.1 and remapped “3.1.6”→**3.1.18**; Rufinus Latin OCR locked for Preface free-choice rule.
- Irenaeus: blood/Spirit English remapped **3.18.1→5.1.2**; 5.21.1 locked from Harvey OCR.
- Clement Strom. 1.17 rewritten from real Greek (causation / μὴ κωλῦον); Cyprian Unity 6 + Novatian Trin. 1/9 locked from Latin.
- Registry expanded (Philocalia, Rufinus Princ, Cyprian, Novatian). Glossary QA still green.
- Remaining anf_mediated/uncertain: Melito, Gregory Thaumaturgus, Victorinus, Methodius foreknowledge illustration, Dionysius fragment.
- **Not Professional GTG** — human/second-model clear and print-check on OCR still required.

## 0.3.0 — 2026-09-10

Aggressive open-edition download + golden-set expansion (still not Professional GTG).

- Downloaded First1K/Perseus Greek for Athenagoras, Clement Stromata+Paedagogus, Didache, Barnabas, Diognetus, Ignatius, Hippolytus Refutatio, Origen Celsum, Justin 2 Apology, Irenaeus AH Greek file.
- `source_verified` now **23/48** with justification receipts (was 6).
- Free-will topic: Athenagoras 24 + Clement Strom. 2.15 locked from Greek; Lactantius Inst 2.17 kept anf_mediated (English did not match CSEL 2.17).
- Spot-check corrected Tatian 11, Origen Cels. 8.72, Hippolytus 10.33 English to match Greek; Justin 2 Apol “7” downgraded pending rematch.
- Glossary QA still green. Human/second-model clear still required for Professional GTG.

## 0.2.0 — 2026-09-10

Professional-track polish on the structure pilot (not Professional GTG yet).

- Golden set `source_verified` now **6/48**: Justin 1Apol 43, Tatian Address 7, Theophilus Autol. 2.27, Methodius Free Will 1, Hermas Mand 12, Tertullian Marc 2.5–6.
- Hermas Greek (First1K) + Tertullian Latin (CSEL) locked; English rewritten from those editions; justification receipts added.
- All 48 excerpts carry `authenticity` + `source_language`.
- Glossary: customer English avoids bare “free will”; prefer free choice / decision / self-determining power.
- `works/registry.json` expanded for every work in this topic; Methodius/Hermas/Tertullian edition paths corrected; Lactantius CSEL file noted but Inst 2.17 still anf_mediated.
- Added `scripts/qa_professional.py`, `VERSION`, this changelog.
- About copy updated for v0.2 honesty (mixed confidence; private study).

## 0.1.0 — 2026-09-09

Structure pilot: encyclopedia DOCX, Headword TN notes, chronological authors with dates, Bible datatype links, Logos Personal Book compile path proven on Air.
