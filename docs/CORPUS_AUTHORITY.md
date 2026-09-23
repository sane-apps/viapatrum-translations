# Corpus Authority Report

Generated 2026-09-23 16:34 UTC by scripts/build_corpus_authority.py. Cross-checks the repo corpus against outside authorities: CCEL's ANF/NPNF (prior English), Migne PG/PL volume citations, and Wikidata datings. Re-run after corpus or crosswalk changes.

## Method in one paragraph

CCEL's 38 Schaff volumes were harvested (authors + works + volumes) and hand-mapped to repo authors, calling out same-name different-person cases (Antioch/Alexandria, Urbanus/Amasea, Caesarea/Emesa, Massilia/Constantinople). Missing authors are dated from Wikidata claims, falling back to standard datings where entities were absent or conflicted; provenance per row. PG/PL coverage counts direct volume citations in book.yml files (alternate editions like GCS undercount true coverage - see caveats).

## A. Authors with CCEL English but zero repo books (62, oldest first)

This is the charter queue: oldest first, each with dated prior English to beat.

| Year | Author | Dates | CCEL English |
|---|---|---|---|
| 100 | Didache (Teaching of the Twelve Apostles) | c.100 (work) (standard) | anf07 |
| 100 | Clement of Rome | d.c.100 (wikidata-Q42887) | anf01, anf07, anf08 |
| 108 | Ignatius of Antioch | d.c.108 (wikidata-Q44170) | anf01 |
| 140 | Aristides of Athens | fl.c.140 (standard) | anf09 |
| 140 | Hermas (Shepherd) | c.140 (work) (standard) | anf02 |
| 150 | Papias of Hierapolis | c.70-c.150 (wikidata-Q273053) | anf01 |
| 150 | Mathetes (Epistle to Diognetus) | c.150 (work) (standard) | anf01 |
| 155 | Polycarp of Smyrna | 69-155 (wikidata-Q192371) | anf01 |
| 165 | Justin Martyr | c.100-165 (wikidata-Q185117) | anf01 |
| 177 | Athenagoras of Athens | fl.c.177 (wikidata-Q309772-desc) | anf02 |
| 180 | Tatian | c.120-c.180 (standard) | anf02, anf09 |
| 180 | Theophilus of Antioch | fl.c.180 (wikidata-Q220787) | anf02 |
| 180 | Scillitan Martyrs (Passion) | 180 (work) (standard) | anf09 |
| 200 | Minucius Felix | fl.c.200 (disputed) (wikidata-Q319423) | anf04 |
| 200 | Caius (Gaius) of Rome | fl.c.200 (standard) | anf05 |
| 215 | Clement of Alexandria | c.150-c.215 (wikidata-Q188883) | anf02, anf09 |
| 220 | Tertullian | c.150-c.220 (wikidata-Q174929) | anf03, anf04 |
| 230 | Asterius Urbanus | fl.c.230 (standard) | anf07 |
| 235 | Hippolytus of Rome | c.170-c.235 (wikidata-Q207113-desc) | anf05 |
| 250 | Commodianus | fl.c.250 (disputed) (wikidata-Q1115768) | anf04 |
| 251 | Alexander of Cappadocia (of Jerusalem) | d.250/251 (standard) | anf06 |
| 258 | Cyprian of Carthage | c.210-258 (wikidata-Q190240-desc) | anf05 |
| 258 | Novatian | c.220-258 (wikidata-Q222890) | anf05 |
| 265 | Dionysius of Alexandria | d.265 (wikidata-Q328736) | anf06, anf07 |
| 270 | Malchion of Antioch | fl.270 (standard) | anf06 |
| 280 | Theognostus of Alexandria | fl.c.280 (standard) | anf06 |
| 283 | Anatolius of Laodicea | d.283 (wikidata-Q2524557) | anf06 |
| 300 | Pierius of Alexandria | fl.c.300 (wikidata-Q2335606) | anf06 |
| 300 | Theonas of Alexandria | d.c.300 (standard) | anf06 |
| 300 | Alexander of Lycopolis | fl.c.300 (wikidata-Q2094745) | anf06 |
| 300 | Archelaus (Acts of Disputation) | c.300 (work; quasi-fictional) (standard) | anf06 |
| 303 | Victorinus of Pettau | d.303/304 (wikidata-Q469199) | anf07 |
| 307 | Phileas of Thmuis | d.307 (wikidata-Q2348355) | anf06 |
| 309 | Pamphilus of Caesarea | d.309 (wikidata-Q1855156) | anf06 |
| 311 | Methodius of Olympus | d.311 (wikidata-Q518300) | anf06 |
| 311 | Peter of Alexandria | d.311 (wikidata-Q365927) | anf06 |
| 317 | Lactantius | c.240-c.317 (wikidata-Q209102) | anf07 |
| 326 | Alexander of Alexandria | d.326 (wikidata-Q44794) | anf06 |
| 327 | Arnobius of Sicca | c.255-c.327 (wikidata-Q342416) | anf06 |
| 339 | Eusebius of Caesarea | c.265-339 (wikidata-Q142999) | npnf201 |
| 346 | Aphrahat | c.270-346 (wikidata-Q434222) | npnf213 |
| 367 | Hilary of Poitiers | c.315-367 (wikidata-Q44344) | npnf209 |
| 373 | Athanasius of Alexandria | 296-373 (wikidata-Q44024) | npnf204 |
| 373 | Ephrem the Syrian | c.306-373 (wikidata-Q200608) | npnf213 |
| 379 | Basil of Caesarea | 329-379 (wikidata-Q44258) | npnf208 |
| 390 | Gregory of Nazianzus | 329-c.390 (wikidata-Q44011) | npnf207 |
| 395 | Gregory of Nyssa | c.335-395 (wikidata-Q191734) | npnf205 |
| 397 | Ambrose of Milan | c.340-397 (wikidata-Q43689-desc) | npnf210 |
| 407 | John Chrysostom | 349-407 (wikidata-Q43706) | npnf109, npnf110, npnf111, npnf112, npnf113, npnf114 |
| 411 | Rufinus of Aquileia | c.345-411 (wikidata-Q365835) | npnf203 |
| 420 | Jerome | c.345-420 (wikidata-Q44248) | npnf203, npnf206 |
| 420 | Sulpitius Severus | c.360-c.420 (wikidata-Q336704) | npnf211 |
| 430 | Augustine of Hippo | 354-430 (wikidata-Q8018) | npnf101, npnf102, npnf103, npnf104, npnf105, npnf106, npnf107, npnf108 |
| 435 | John Cassian | c.360-435 (wikidata-Q313795) | npnf211 |
| 440 | Socrates of Constantinople | c.380-c.440 (wikidata-Q336198) | npnf202 |
| 445 | Vincent of Lerins | d.445 (wikidata-Q644057) | npnf211 |
| 450 | Sozomen | c.400-c.450 (wikidata-Q354350) | npnf202 |
| 457 | Theodoret of Cyrrhus | c.393-457 (wikidata-Q317029) | npnf203 |
| 461 | Leo the Great | 390-461 (wikidata-Q43954) | npnf212 |
| 496 | Gennadius of Massilia | d.496 (wikidata-Q373675) | npnf203 |
| 604 | Gregory the Great | 540-604 (wikidata-Q42827) | npnf212, npnf213 |
| ? | Venantius (On Easter) | undated (CCEL ANF07 as given) (ccel-only) | anf07 |

## B. Shared authors: repo AND CCEL (complementarity)

| Repo author | CCEL has | Relationship |
|---|---|---|
| Gregory Thaumaturgus | anf06 | Acknowledged + dubious writings; OVERLAP LIKELY with repo Gregory Thaumaturgus books (nee... |
| Irenaeus of Lyons | anf01 | CCEL has Against Heresies I-V + fragments; repo has Demonstration -> COMPLEMENTARY, no ov... |
| Julius Africanus | anf06 | CCEL has Epistle to Aristides + Chronography fragments; repo has Cesti body -> COMPLEMENT... |
| Cyril of Jerusalem | npnf207 | CCEL has Catechetical Lectures; repo has Epistula + 3 homilies -> COMPLEMENTARY, no overl... |
| John of Damascus | npnf209 | CCEL has Exposition of the Orthodox Faith; repo has 42-book Damascene corpus -> repo larg... |
| Origen | anf04, anf09 | Celsus, Matthew commentary, misc; repo Origen corpus far broader -> repo largely compleme... |

## C. Repo authors with no CCEL English (61, first-English territory)

`Agathias Scholasticus`, `Alexander Monachus`, `Ammonius`, `Amphilochius of Iconium`, `Apollinaris of Laodicea`, `Arethas of Caesarea`, `Asterius of Amasea`, `Chronicon Paschale`, `Cosmas Indicopleustes`, `Cyril of Alexandria`, `Didymus the Blind`, `Diodorus of Tarsus`, `Epiphanius of Salamis`, `Eudocia Augusta`, `Eusebius of Emesa`, `Eustathius of Antioch`, `Eustathius of Thessalonica`, `Evagrius Ponticus`, `Gennadius of Constantinople`, `Georges Pisides`, `Georgius Cedrenus`, `Georgius Peccator`, `Georgius Syncellus`, `Hesychius of Jerusalem`, `John Davenant`, `John Malalas`, `John of Antioch`, `Josué de la Place (Placeus)`, `Julian of Eclanum`, `Louis Le Blanc de Beaulieu`, `Ludwig Crocius`, `Macarius the Egyptian`, `Marcellus of Ancyra`, `Maximus Confessor`, `Nemesius of Emesa`, `Nicephorus Bryennius`, `Nicephorus Phokas`, `Nicephorus of Constantinople`, `Nonnos of Panopolis`, `Oecumenius`, `Olympiodorus of Alexandria`, `Origen (anthology by Basil & Gregory)`, `Origen of Alexandria`, `Paulus Silentarius`, `Philostorgius`, `Photius of Constantinople`, `Procopius of Gaza`, `Robert Baron`, `Samuel Strimesius`, `Serapion of Antioch`, `Severianus of Gabala`, `Symeon Magister`, `Symeon Metaphrastes`, `Symeon the New Theologian`, `Theodore the Studite`, `Theodorus (PG 86a)`, `Theodorus of Heraclea`, `Theophanes Confessor`, `Theophanes Kerameus`, `Theophilus of Alexandria`, `Theophylact Simocatta`

## D. PG volume triage (cited 59/161 volumes)

Gap volumes with archive.org scan-title cues; bare/UNVERIFIED rows need the scan's own table of contents before claiming contents.

| PG vol | Repo cites | Scan-title cue |
|---|---|---|
| 1 | 0 | UNVERIFIED (no scan title) |
| 2 | 0 | Clementina |
| 3 | 0 | Dionysius the Areopagite |
| 4 | 0 | Dionysius the Areopagite |
| 5 | 0 | Ignatius and other writers |
| 6 | 0 | Justin and others |
| 7 | 0 | Irenaeus - Tomus Unicus |
| 8 | 0 | Clemens Alexandrinus - Tomus Prior |
| 9 | 0 | Clemens Alexandrinus - Tomus Secundus |
| 15 | 0 | Origen 5 |
| 16 | 0 | c - Origen 6c |
| 19 | 0 | Eusebius 1 |
| 20 | 0 | Eusebius 2 |
| 21 | 0 | Eusebius 3 |
| 22 | 0 | Eusebius 4 |
| 23 | 0 | Eusebius 5 |
| 24 | 0 | Eusebius 6 |
| 25 | 0 | Athanasius 1 |
| 26 | 0 | Athanasius 2 |
| 27 | 0 | Athanasius 3 |
| 28 | 0 | Athanasius 4 |
| 29 | 0 | Basil 1 |
| 30 | 0 | UNVERIFIED (no scan title) |
| 31 | 0 | Basil 3 |
| 32 | 0 | Basil 4 |
| 35 | 0 | Gregory of Nazianzus 1 |
| 36 | 0 | Gregory of Nazianzus 2 |
| 37 | 0 | Gregory of Nazianzus 3 |
| 38 | 0 | Gregory of Nazianzus 4 |
| 42 | 0 | UNVERIFIED (no scan title) |
| 44 | 0 | UNVERIFIED (no scan title) |
| 45 | 0 | UNVERIFIED (no scan title) |
| 46 | 0 | UNVERIFIED (no scan title) |
| 47 | 0 | UNVERIFIED (no scan title) |
| 48 | 0 | UNVERIFIED (no scan title) |
| 49 | 0 | UNVERIFIED (no scan title) |
| 50 | 0 | UNVERIFIED (no scan title) |
| 51 | 0 | UNVERIFIED (no scan title) |
| 52 | 0 | UNVERIFIED (no scan title) |
| 53 | 0 | UNVERIFIED (no scan title) |
| 54 | 0 | UNVERIFIED (no scan title) |
| 55 | 0 | UNVERIFIED (no scan title) |
| 56 | 0 | UNVERIFIED (no scan title) |
| 57 | 0 | Chrysostom on Matthew (1) |
| 58 | 0 | Chrysostom on Matthew (2) |
| 59 | 0 | UNVERIFIED (no scan title) |
| 60 | 0 | UNVERIFIED (no scan title) |
| 61 | 0 | UNVERIFIED (no scan title) |
| 62 | 0 | UNVERIFIED (no scan title) |
| 63 | 0 | UNVERIFIED (no scan title) |
| 64 | 0 | UNVERIFIED (no scan title) |
| 67 | 0 | UNVERIFIED (no scan title) |
| 73 | 0 | UNVERIFIED (no scan title) |
| 78 | 0 | UNVERIFIED (no scan title) |
| 79 | 0 | UNVERIFIED (no scan title) |
| 80 | 0 | UNVERIFIED (no scan title) |
| 81 | 0 | UNVERIFIED (no scan title) |
| 82 | 0 | UNVERIFIED (no scan title) |
| 83 | 0 | UNVERIFIED (no scan title) |
| 84 | 0 | UNVERIFIED (no scan title) |
| 89 | 0 | UNVERIFIED (no scan title) |
| 95 | 0 | UNVERIFIED (no scan title) |
| 96 | 0 | UNVERIFIED (no scan title) |
| 102 | 0 | UNVERIFIED (no scan title) |
| 103 | 0 | UNVERIFIED (no scan title) |
| 104 | 0 | UNVERIFIED (no scan title) |
| 105 | 0 | UNVERIFIED (no scan title) |
| 107 | 0 | UNVERIFIED (no scan title) |
| 108 | 0 | UNVERIFIED (no scan title) |
| 109 | 0 | UNVERIFIED (no scan title) |
| 111 | 0 | UNVERIFIED (no scan title) |
| 112 | 0 | UNVERIFIED (no scan title) |
| 113 | 0 | UNVERIFIED (no scan title) |
| 114 | 0 | UNVERIFIED (no scan title) |
| 115 | 0 | UNVERIFIED (no scan title) |
| 116 | 0 | UNVERIFIED (no scan title) |
| 117 | 0 | UNVERIFIED (no scan title) |
| 119 | 0 | UNVERIFIED (no scan title) |
| 122 | 0 | UNVERIFIED (no scan title) |
| 123 | 0 | UNVERIFIED (no scan title) |
| 124 | 0 | UNVERIFIED (no scan title) |
| 125 | 0 | UNVERIFIED (no scan title) |
| 126 | 0 | UNVERIFIED (no scan title) |
| 127 | 0 | UNVERIFIED (no scan title) |
| 128 | 0 | UNVERIFIED (no scan title) |
| 129 | 0 | UNVERIFIED (no scan title) |
| 130 | 0 | UNVERIFIED (no scan title) |
| 131 | 0 | UNVERIFIED (no scan title) |
| 132 | 0 | UNVERIFIED (no scan title) |
| 133 | 0 | UNVERIFIED (no scan title) |
| 134 | 0 | UNVERIFIED (no scan title) |
| 135 | 0 | UNVERIFIED (no scan title) |
| 136 | 0 | UNVERIFIED (no scan title) |
| 137 | 0 | UNVERIFIED (no scan title) |
| 138 | 0 | UNVERIFIED (no scan title) |
| 139 | 0 | UNVERIFIED (no scan title) |
| 140 | 0 | UNVERIFIED (no scan title) |
| 141 | 0 | UNVERIFIED (no scan title) |
| 142 | 0 | UNVERIFIED (no scan title) |
| 143 | 0 | UNVERIFIED (no scan title) |
| 144 | 0 | UNVERIFIED (no scan title) |
| 145 | 0 | UNVERIFIED (no scan title) |
| 146 | 0 | UNVERIFIED (no scan title) |
| 147 | 0 | UNVERIFIED (no scan title) |
| 148 | 0 | UNVERIFIED (no scan title) |
| 149 | 0 | UNVERIFIED (no scan title) |
| 150 | 0 | UNVERIFIED (no scan title) |
| 151 | 0 | UNVERIFIED (no scan title) |
| 152 | 0 | UNVERIFIED (no scan title) |
| 153 | 0 | UNVERIFIED (no scan title) |
| 154 | 0 | UNVERIFIED (no scan title) |
| 155 | 0 | UNVERIFIED (no scan title) |
| 156 | 0 | UNVERIFIED (no scan title) |
| 157 | 0 | UNVERIFIED (no scan title) |
| 158 | 0 | UNVERIFIED (no scan title) |
| 159 | 0 | UNVERIFIED (no scan title) |
| 160 | 0 | UNVERIFIED (no scan title) |
| 161 | 0 | UNVERIFIED (no scan title) |

Covered volumes: 10, 11, 12, 13, 14, 17, 18, 33, 34, 39, 40, 41, 43, 65, 66, 68, 69, 70, 71, 72, 74, 75, 76, 77, 85, 86, 87, 88, 90, 91, 92, 93, 94, 97, 98, 99, 100, 101, 106, 110, 118, 120, 121, 5201, 5202, 5203, 5204, 5206, 5215, 5216, 5219, 5228, 5230, 5231, 5232, 5233, 5240, 5378, 5379

## E. PL volume triage (cited 0/217 volumes)

ZERO Latin Father coverage by Migne citation. The missing Latin authors from table A (Tertullian, Cyprian, Minucius, Novatian, Lactantius, Arnobius, Commodianus, Victorinus, Ambrose, Jerome, Augustine, Hilary, Sulpitius, Vincent, Cassian, Leo, Gregory I) confirm it: the Latin corpus is unstarted.

## F. Scope questions for the owner

- Excerpts of Theodotus (ANF08): Valentinian Gnostic fragments via Clement - heretical corpus, owner call
- Narrative of Zosimus + Testament of Abraham (ANF09): OT pseudepigrapha, not patristic - owner call
- Seven Ecumenical Councils (NPNF214): conciliar documents, not authored works - owner call
- NT Apocrypha bundle (ANF08/09: Peter, Diatessaron, Testaments, Apocalypses): apocrypha - owner call whether in charter scope

## Caveats

- Book-level granularity: an author marked present may still lack individual works (work-level CPG/CPL cross-check is future work).
- PG citations undercount coverage where books use GCS/SC/OCT instead of Migne.
- Missing-author years are ordering-grade, not critical datings.
