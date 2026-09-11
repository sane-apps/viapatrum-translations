# Professional bar — what else to bake in

Not GTG for “original-language, sellable, Logos-native” until these are normal parts of the workflow. The Soteriology/Free Will DOCX is a **structure pilot**; professional translation upgrades ride on this checklist.

## Gaps people usually miss

1. **What “original language” means per work**  
   - Justin, Athenagoras, many Greeks: Greek.  
   - Tertullian, Cyprian, Minucius, Arnobius, Lactantius: Latin.  
   - **Irenaeus *Against Heresies***: mostly **Latin** survival; Greek often fragmentary. Translating “from Greek” for AH 4.37 is often impossible — translate the Latin and footnote Greek fragments when they exist.  
   - Some items: Syriac / Coptic / Armenian only — either specialist lane or exclude with honesty.

2. **Edition lock, not “the Greek”**  
   Name the edition (First1K / Otto / SC / CCSL / CSEL / Migne PL/PG with year). Different editions punctuate differently; punctuation can change free-will arguments.

3. **Authenticity and recensions**  
   Longer/shorter Ignatius, Hermas layers, Pseudo-*, contested Barnabas. Flag `authenticity: accepted | contested | spurious` on each work.

4. **One canonical English per locus**  
   Same Methodius paragraph under two topics must not drift into two wordings. Registry keyed by `author/work/locus`.

5. **Project glossary**  
   *αὐτεξούσιον / liberum arbitrium / προαίρεσις* → agreed English + when to transliterate. Consistency is professional; silent synonym-hopping looks like hallucination.

6. **Scripture form of the Father**  
   They quote LXX, Old Latin, or paraphrase. Do **not** “correct” to NA28/ESV. Tag the form they used; note modern parallel.

7. **Justification layer (required for `source_verified`)**  
   Every non-obvious choice: lemma, contemporary/patristic usage (LSJ / Lampe / Blaise), rejected alternatives, why ANF wording was left. Lives in `reviews/justifications/<id>.json`.

8. **Apparatus / variants**  
   When Latin ≠ Greek or MSS disagree: note it. Never pick silently.

9. **Legal source access**  
   No paywalled TLG scrape. Owner-provided exports OK. Prefer CC/PD CTS (First1KGreek, Latin Library where genuine, Documenta, Tertullian Project).

10. **Versioning**  
    Translations will change. Semver the book; changelog; Logos rebuild after upgrades; keep receipts.

11. **Independent check**  
    Same model cannot certify itself. Second model and/or human golden set.

12. **Sellable extras**  
    Clear About/legal, correction channel, no overclaim (“complete critical edition”), Faithlife rights packet later.

## Gate: when are we GTG?

| Gate | Meaning |
|------|---------|
| **Structure GTG** | Encyclopedia DOCX, Headwords, Bible links, broad authors — **done for MVP** |
| **Professional GTG** | Golden set `source_verified` with edition lock + justifications + glossary + variant notes + **human and/or second-model clear** — **Yes (2026-09-10)** via second-model PASS WITH CAVEATS (`outputs/reviews/second_model_golden_set_audit_2026-09-10_v081.md`) plus hold-unlock PASS (`outputs/reviews/second_model_hold_unlock_audit_2026-09-10.md`); **48/48** receipts stamped; Harvey print-check cleared; `--strict-professional` green. |
| **Sellable GTG** | Professional GTG + human spot-check + legal review — **not yet** |

Default customer About copy: private study edition — no confidence labels, no GTG jargon. Confidence stays in JSON/QA until Professional GTG.
