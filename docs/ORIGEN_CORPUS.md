# Origen corpus — what survives, what we can lock, what is next

Private-study inventory for `~/SaneApps/clients/translations`. Rank: **(1) no usable public-domain English first**, **(2) Victorian/ANF exists, new English later**. Do not copy modern English (ACW, FOTC, CWS, SC facing pages, Daly, Heine, Trigg, Scheck, Chadwick, Butterworth).

**Honesty:** “finish all Origen” is not one more book. Surviving prose is about **twelve GCS volumes** of first-edition text, plus Toura recoveries, plus catena fragments, plus the 2015 Munich Psalms (not a PD edition). Bundled the way Books 1–2 are bundled, that is on the order of **twenty Logos personal books**, not four. The Hexateuch homilies alone are 108 sermons.

Jerome’s Letter 33 to Paula is the ancient catalogue of what Origen wrote. Most of that list is lost.

## Already in this repo

| Book | Slug | Works | Rank | Status |
|------|------|-------|------|--------|
| 1 | `origen-prayer-martyrdom` | *On Prayer*; *Exhortation to Martyrdom* | 1 | Done (Logos + fathers.saneapps.com) |
| 2 | `origen-heraclides-pascha` | *Dialogue with Heraclides*; *On Pascha* | 1 | In progress. Heraclides Greek locked. Pascha: Witte page-images usable; tesseract not (see `books/origen-heraclides-pascha/sources/pascha_ocr_status.md`) |

Cross-author Tier A in `docs/WORKS_QUEUE.md` still puts **Melito, *On Pascha*** then **Irenaeus, *Demonstration*** after Origen Book 2. The sequence below is Origen-only, if the owner stays in Origen.

## How to read the tables

- **Survival:** Greek / Rufinus Latin / Jerome Latin / papyrus. “Greek” means a continuous (or near-continuous) Greek witness, not only catena crumbs.
- **GCS / PG:** first-edition GCS (1899–1930) is the lock when it exists. PG 11–17 (Migne, 1857–1862) is the PD fallback. Later GCS/SC/FOTC/OWD volumes are copyrighted — cite, do not lock.
- **ANF:** ANF 4 (Crombie) and ANF 9 American / Edinburgh 10 (Menzies, Patrick, and the Luke homilies). NPNF does not cover Origen.
- **PD English “usable”:** a complete-enough Victorian or other PD translation of that work, not a paragraph in a handbook.

US public-domain line as of 2026: publications through **1930** are PD; **1931+** are not. So GCS Orig. I–IX (through Rauer 1930) are lockable. GCS Orig. X–XII (Matt, 1933–1955) and Orig. XIII (Psalms, 2015) are not.

---

## Rank 1 — no usable PD English

These are the remaining whole works (or surviving blocks) after Prayer, Martyrdom, Heraclides, and Pascha.

| Work | Survival | GCS / SC / PG | PD source (GCS/PG) | ANF? | Suggested slug | Size |
|------|----------|---------------|--------------------|------|----------------|------|
| Homilies on Jeremiah (20 Greek + 2 Jerome-only) + Lamentations fragments + Homily on 1 Kingdoms 28 (Witch of Endor) | Greek (Jerome Latin overlaps 12 of the 20) | Orig. III = GCS 6, Klostermann 1901. SC 232/238 (Nautin) copyrighted. | https://archive.org/details/origeneswerke03orig | No. FOTC 97 (Smith 1998) is copyrighted. | `origen-jeremiah-samuel` | One GCS volume. Next book after Book 2. |
| Commentary on John, books 13, 19, 20, 28, 32 | Greek (9 of 32 books survive: 1, 2, 6, 10, 13, 19, 20, 28, 32) | Orig. IV = GCS 10, Preuschen 1903. SC 120 etc. copyrighted. | https://archive.org/details/origeneswerke04orig | **Partial.** ANF 9 has 1, 2, 4–6, 10 (4–5 are fragments). Books **13, 19, 20, 28, 32 have no ANF.** Heine FOTC 80/89 is copyrighted. | `origen-john-later` | Five tomoi. Same GCS volume as the ANF books; slice the later ones. |
| Commentary on the Song of Songs (4 books) + 2 homilies | Rufinus Latin (comm.); Jerome Latin (homilies). Greek lost except fragments. | Orig. VIII = GCS 33, Baehrens 1925. ACW 26 (Lawson) copyrighted. | https://archive.org/details/origeneswerkehrs08origuoft | No | `origen-song` | Medium. Complete as surviving. |
| Homilies on Genesis (16) | Rufinus Latin | Orig. VI = GCS 29, Baehrens 1920 (first part of that volume). Habermehl 2012 2nd ed. copyrighted. Heine FOTC 71 copyrighted. | https://archive.org/details/origeneswerke06orig | No | `origen-genesis-homilies` | Medium-large. Opens the Hexateuch series. |
| Homilies on Exodus (13) | Rufinus Latin | Orig. VI = GCS 29 | same Bd 6 | No | `origen-exodus-homilies` | After Genesis. |
| Homilies on Leviticus (16) | Rufinus Latin | Orig. VI = GCS 29 | same Bd 6 | No. FOTC 83 (Barkley) copyrighted. | `origen-leviticus-homilies` | After Exodus. |
| Homilies on Numbers (28) | Rufinus Latin | Orig. VII = GCS 30, Baehrens 1921 | https://archive.org/details/origeneswerke07orig | No. Scheck FOTC copyrighted. | `origen-numbers-homilies` | Large. |
| Homilies on Joshua (26) | Rufinus Latin | Orig. VII = GCS 30 | same Bd 7 | No. FOTC 105 (Bruce) copyrighted. | `origen-joshua-homilies` | Large. |
| Homilies on Judges (9) | Rufinus Latin | Orig. VII = GCS 30 | same Bd 7 | No | `origen-judges-homilies` | Short. Can pair with Judges+1 Sam Latin leftovers. |
| Homilies on Isaiah (9) | Jerome Latin | Orig. VIII = GCS 33 | https://archive.org/details/origeneswerkehrs08origuoft | No. Scheck FOTC copyrighted. | with Ezekiel, `origen-isaiah-ezekiel` | Medium as a pair. |
| Homilies on Ezekiel (14) | Jerome Latin; Greek fragments | Orig. VIII = GCS 33. PG 13. Pearse/Hooker 2014 is copyrighted. | same Bd 8 | No | `origen-isaiah-ezekiel` | Medium as a pair. |
| Homilies on Psalms 36–38 (9) | Rufinus Latin (4 of the 9 also in Munich Greek) | No first-edition GCS. PG 12. Prinzivalli 1991/SC 411 copyrighted. | PG 12 (Migne) | No | `origen-psalms-rufinus` | Short. Do **not** lock Perrone 2015 for this. |
| Commentary on Romans (Rufinus, 10 books from 15 Greek) | Rufinus Latin; Greek fragments (Philocalia, catenae, Tura III.5–V.7) | No GCS. PG 14. Hammond Bammel (Vetus Latina, 1990–98) copyrighted. Scheck FOTC 103/104 copyrighted. Scherer 1957 Tura fragment copyrighted. | PG 14 | No | `origen-romans` | Large. Weaker lock than GCS 1899–1930. |
| Commentary on Matthew, books 15–17 (Greek) + *Series commentariorum* (Latin, Matt 22:34–27) | Greek 10–17; Latin series | Orig. X–XII = GCS 40/38/41 (1933–1955) **not PD**. PG 13 is PD. Heine’s recent English is copyrighted. | PG 13 until GCS X–XII expire | **Partial.** ANF 9 has Matt 10–14 (and some early fragments). **15–17 and the Series are not in ANF.** | `origen-matthew-later` | Large. Defer the GCS lock; PG 13 is the PD text. |
| Catena / reconstructed NT commentaries (Eph, 1 Cor, Hebrews, etc.) | Fragments | Scattered (Gregg, Ramsbotham, Heine reconstructions) | PG + older fragment collections, case by case | No continuous ANF | later fragment books | Not a “complete work.” |

**Munich Psalms (29 Greek homilies, Cod. Mon. gr. 314, found 2012).** Last large Greek recovery. GCS Orig. XIII / GCS NF 19 (Perrone 2015) is **in copyright**. Trigg FOTC 2021 is copyrighted. BSB has digitized the manuscript; a future book would have to transcribe from manuscript images, not from Perrone. **Not next.**

**Tura other than Heraclides/Pascha:** selections of *Contra Celsum*, Romans III.5–V.7 (Scherer 1957), and 1 Sam 28 overlap GCS. Do not start a “Tura leftovers” book.

---

## Rank 2 — ANF/NPNF (or other PD English) exists; new English later

| Work | Survival | GCS / PG | PD English | Notes |
|------|----------|----------|------------|-------|
| *Contra Celsum* (8 books) | Greek, complete | Orig. I–II = GCS 2–3 (Koetschau 1899). SC Borret copyrighted. Chadwick 1953 copyrighted. | ANF 4 (Crombie). IA: https://archive.org/details/origeneswerke01orig and `origeneswerke02orig` (also the Book 1 locks `origenes-werke.-bd-1-1899` / `bd-2-1899`) | Huge. WORKS_QUEUE already defers it. |
| *De Principiis / Peri Archon* (4 books) | Rufinus Latin; Greek in Philocalia + Justinian excerpts | Orig. V = GCS 22 (Koetschau 1913). SC 252/253 copyrighted. Butterworth 1936 copyrighted. | ANF 4 (Crombie). IA: https://archive.org/details/origeneswerke05orig (Wikisource). PG 11. | Huge. Rufinus is a paraphrase; disclose that. Koetschau’s reconstructed “Greek” from hostile witnesses is not Origen’s running text — do not treat it as such. |
| Commentary on John, books 1, 2, 6, 10 | Greek | Orig. IV = GCS 10 | ANF 9 (Menzies), incomplete even for these books vs Preuschen | Refresh after Rank 1 John-later, or skip if ANF is enough for private study. |
| Commentary on Matthew, books 10–14 | Greek | Orig. X not PD; PG 13 | ANF 9 (Patrick) | Same. |
| Homilies on Luke (39) | Jerome Latin; Greek fragments | Orig. IX = GCS 35, Rauer 1930 (**PD in 2026**). IA: https://archive.org/details/origenes-werke.-bd.-9-1930 | ANF 9 | First-edition Rauer is now lockable. Still Rank 2 because ANF exists. |
| Letter to Africanus (Susanna) | Greek | PG 11; often with the letters | ANF 4 | Short. Can ride with a letters/Philocalia book. |
| Letter to Gregory (Thaumaturgus) | Greek (Philocalia 13) | Philocalia | ANF 4 | Same. |
| *Philocalia* (Basil + Gregory’s anthology) | Greek | J. A. Robinson, Cambridge 1893 (PD), not GCS | George Lewis 1911 (PD) | Rank 2. Useful as a source of Greek fragments of lost commentaries. |
| Hexapla remains | Fragments / columns | Field 1875 (PD) | Not a prose book | Apparatus, not a Logos reading text. |

---

## GCS first-edition lock table

Origenes Werke band ≠ GCS series number. Lock **first editions**.

| Orig. Bd | GCS | Year | Editor | Contents | Archive.org (verified 2026-09-10 unless noted) |
|----------|-----|------|--------|----------|-----------------------------------------------|
| I | 2 | 1899 | Koetschau | Martyrdom; C. Cels. I–IV | https://archive.org/details/origeneswerke01orig and Book 1 lock `origenes-werke.-bd-1-1899` |
| II | 3 | 1899 | Koetschau | C. Cels. V–VIII; *De oratione* | https://archive.org/details/origeneswerke02orig and `origenes-werke.-bd-2-1899` |
| III | 6 | 1901 | Klostermann | Hom. Jeremiah; Lamentations fr.; 1 Kingdoms | https://archive.org/details/origeneswerke03orig |
| IV | 10 | 1903 | Preuschen | Comm. John | https://archive.org/details/origeneswerke04orig |
| V | 22 | 1913 | Koetschau | *De principiis* | https://archive.org/details/origeneswerke05orig (Wikisource) |
| VI | 29 | 1920 | Baehrens | Hom. Gen, Ex, Lev (Rufinus) | https://archive.org/details/origeneswerke06orig |
| VII | 30 | 1921 | Baehrens | Hom. Num, Josh, Judg (Rufinus) | https://archive.org/details/origeneswerke07orig |
| VIII | 33 | 1925 | Baehrens | Hom. 1 Sam (Lat.); Cant. hom. + comm.; Isa; Jer (Lat.); Ezek | https://archive.org/details/origeneswerkehrs08origuoft |
| IX | 35 | 1930 | Rauer | Hom. Luke (Jerome) + Greek fragments | https://archive.org/details/origenes-werke.-bd.-9-1930 |
| X | 40 | 1935 | Klostermann | Comm. Matt Greek 10–17 | Not PD. Use PG 13. |
| XI | 38 | 1933 | Klostermann | Matt *Series* (Latin) | Not PD. Use PG 13. |
| XII | 41 | 1941/55 | Klostermann | Matt fragments / indices | Not PD. |
| XIII | NF 19 | 2015 | Perrone | Munich Psalms | Not PD. Not a lock. |

PG 11–17: Migne 1857–1862, PD. Use when GCS is missing or still in copyright.

Toura / other:

| Work | Edition to lock | Notes |
|------|-----------------|-------|
| *Dialogue with Heraclides* | Scherer tradition; SC 67 (1960) is copyrighted. Repo: DCO/Aegean text in `heraclides_greek.txt`. | Book 2. |
| *On Pascha* | **Witte 1993** continuous Greek (charter). First edition: Guéraud–Nautin 1979, *Origène, Sur la Pâque* (Christianisme antique 2, Beauchesne) — papyrus diplomatic edition, not the GCS-style running text. | Book 2. Daly ACW 54 (1992) is copyrighted English from Guéraud–Nautin. Do not copy. |

---

## Lost or not a book

Lost except fragments (do not advertise as surviving works): *Stromateis*; *De resurrectione*; commentaries on Genesis, the Twelve Prophets, Isaiah and Ezekiel as commentaries (homilies survive); most of the 32-book John and 25-book Matthew; Greek of *De principiis* as a running text; almost all of the 400+ homilies Jerome listed.

Not Origen’s own book: Pamphilus, *Apology for Origen* (Rufinus Latin); Eusebius HE 6; Gregory Thaumaturgus’s *Address*.

---

## Next four Origen books after Heraclides + Pascha

Stay in Rank 1. Prefer lockable first-edition GCS, then remaining **Greek** without ANF, then complete-as-surviving Latin without ANF. Do not start Munich Psalms or GCS X–XII.

| # | Slug | What | Why this order |
|---|------|------|----------------|
| **3** | `origen-jeremiah-samuel` | GCS Orig. III: 20 Greek Jeremiah homilies, 2 Jerome-only, Lamentations fragments, Homily on 1 Kingdoms 28. **Homily 1 English on the site 2026-09-11.** | Last large pre-Munich **Greek homily** set. No ANF. One PD volume, same lock pattern as Book 1. Prophecy / testing-prophets overlap with `gifts-and-order` is a bonus, not the reason. |
| **4** | `origen-john-later` | GCS Orig. IV slice: John **13, 19, 20, 28, 32** | Remaining **Greek commentary** with no ANF. Preuschen 1903 is PD. Heine is the copyrighted complete English. |
| **5** | `origen-song` | GCS Orig. VIII slice: Rufinus *Comm. in Cant.* (4 books) + Jerome’s 2 homilies | No ANF. Complete as surviving. Best literary Latin block before the Hexateuch grind. |
| **6** | `origen-genesis-homilies` | GCS Orig. VI slice: 16 Genesis homilies | No ANF. Starts 108 Hexateuch+Judges homilies, which then want their own books (Exodus, Leviticus, Numbers, Joshua, Judges). |

After those four, Rank 1 still has: Exodus, Leviticus, Numbers, Joshua, Judges, Isaiah+Ezekiel, Rufinus Psalms 36–38, Romans, Matthew 15–17 + Series (PG 13), and fragment volumes. Rank 2 still has Celsum, *De principiis*, Luke, and ANF refreshes.

**Do not** treat Book 6 as “the rest of Origen.”

If the owner instead follows `WORKS_QUEUE.md` after Book 2, insert **Melito *On Pascha*** then **Irenaeus *Demonstration*** before any of the slugs above.

---

## Sources used for this inventory

- This repo: `docs/WORKS_QUEUE.md`; Book 1–2 charters and GCS locks.
- Wikisource *Origenes* (GCS band list + IA links): https://de.wikisource.org/wiki/Origenes
- Archive.org items fetched 2026-09-10: `origeneswerke03orig`, `origeneswerke04orig`, `origeneswerke06orig`, `origeneswerke07orig`, `origeneswerkehrs08origuoft`; Bd 9 via search hit `origenes-werke.-bd.-9-1930`.
- Crouzel’s surviving-homily counts as summarized by Poulos (2012) and the English Wikipedia “Origen” homily list (Gen 16, Ex 13, Lev 16, Num 28, Josh 26, Judg 9, etc.) — they agree with GCS VI–IX contents.
- ANF 4 / ANF 9 contents: Crombie (Princ, Celsum, two letters); Menzies/Patrick (John partial, Matt partial, Luke homilies).
- Pascha editions: Witte 1993 IA `Witte02OrigenesUeberDasPassaK` (locked); Guéraud–Nautin 1979 described in Witte’s own preface and in the ACW 54 catalogue note (edition history only — not Daly’s English).
