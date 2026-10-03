# Translation errors found by the beliefs-map audit (2026-10-03)

Claude 4.5+ auditors checked deciding passages against the Greek. Each line:
book, passage-id prefix (outputs/doctrine-map/corpus.jsonl), the error. Fix
the English from the source; never patch the map to hide it.

| Book | Passage | Error |
|---|---|---|
| asterius-* (Homily 10) | 10.18.6 | "entreat the martyrs to revile the Lord": δυσωπῆσαι = "implore our common Master". Serious. |
| asterius-* (Homily 10) | 10.4.3 | martyr is the go-between (πρὸς τὸν μεσίτην); means "you who suffered for Christ, intercede". |
| cyril-alexandria-* (Isaiah) | f497 | adds "which is necessary for spiritual rebirth"; not in the Greek. |
| cyril-alexandria-fragmenta-1-corinthios | 92cb | "perfected through holy baptism": τετελείωκε = "initiated". |
| cyril-alexandria-fragmenta-acta-catholicas | bd7f49 | "He is also named Theotokos": the Virgin is named Theotokos. |
| cyril-alexandria-de-adoratione (10 §18) | ac1373 | "brought forward no sacrifice for sins" inverts Heb 10:12; source Greek οὐδεμίαν likely corrupt for οὗτος δὲ μίαν. Check the witness. |
| cyril-alexandria-de-adoratione (12 §27) | b9233 | excerpt cuts the subject (the catechumen); "the victim" misread as the Eucharist. |
| cyril-alexandria-de-adoratione (3) | - | "we ourselves still exact the sentences": ἐξαιτεῖσθαι δίκας = penalties are demanded of us. |
| cyril-alexandria-de-adoratione (13) | - | "middle rank" understates μείω ("lesser"). |
| didymus-fragmenta-psalmos | 03d240 | "she was once in doubt": the doubt is the reader's, not Mary's. Produced a false verdict. |
| didymus-fragmenta-psalmos (Ps 34) | dfps u17 | adds "praying and interceding". |
| diodorus-fragmenta* | 6b705772 | splits one clause; it is about the Spirit's consubstantiality, not origin from the Son. |
| apollinaris-fragmenta-joannem | 7ef0 | garbled first clause. |
| apollinaris (Eucharist) | u05 | omits "Apollinaris makes a type of the participation accomplished in spirit" (a reporter's frame). |
| amphilochius (In natalitia) | - | "the firstborn Creator" understates "has the Creator of all as her firstborn". |
| evagrius-* (Proverbs scholion) | - | "rub ... consume" for κατατρίβουσι ... καταναλίσκουσι ("wear away ... squander"). |
| hesychius-* | 40bb9f3a | adds "remained" to an aorist. |
| hesychius-* | - | optative wish (διαφυλαχθείημεν) rendered as a statement. |
| origen-heraclides-pascha | ed15f3 | "who is sacrificed by us" comes from a restored lacuna in 1.42, not 1.41. |
| origen-philocalia (3) | b67b39 | English is a summary, not a translation ("closed, ordered library" not in the Greek). |
| origen (Exodus Hom. 8; Letter to Africanus) | - | paraphrase, not translation; Africanus OCR "Τὼβ" for Job. |
| epiphanius-epistula-ad-theodosium-imperatorem | - | "lintels of doors" should be "door curtains" (βήλοις). |
| epiphanius-index-discipulorum | - | Barnabas "first preached Christ in Rome"; "two thousand", not "thousands". |

Also noted for the library (not translation): the Didymus Tura commentaries
cite "PG 39" as edition, which does not contain them; the `cyprian.epistles`
excerpt entry in ante-nicene-topics seems to hold Hippolytus fragments.

## From audit group 3 (justification, predestination, Scripture, baptism)

| Book | Passage | Error |
|---|---|---|
| didymus (Enarratio in 1 Pet) | 52c7c68c | catena heading Ὠριγένους rendered "Originating from"; it is Origen's. |
| origen (Romans catena) | 790dcd6b | "through faith alone": no μόνη in the Greek. Invented. |
| cyril-alexandria (Romans fragment) | db58b597 | James 2:21's question rendered as a denial. |
| cyril-alexandria (James) | 29126ee3 | lemma folded into Cyril's words; "to bring about righteousness" and the "David" clause added. |
| origen (Romans catena) | b261abd0 | εὐσέβειαν rendered "security"; it is "piety". |
| asterius | 805343795 | ἀπεκλήρωσε rendered "completed"; it is "allotted". |
| severianus (Galatians) | f890c545 | ἀκουομένη rendered "the one obeying"; it is "when heard". |
| origen (Romans catena) | bd6d7d5b | "as if He arbitrarily chose some and rejected others" not in the Greek. |
| origen-principiis (praef.) | b4a35fcf | chunk runs Praef. 1 into Praef. 10; Praef. 2 (apostolic tradition) missing. |
| cyril-alexandria-de-adoratione | db7a9d30 | Bible verse labels shuffled (Gen 15:6 tagged Matthew 9:12-13). |
| didymus (Proverbs) | - | "Matt 4:4" citation should be Ps 77(78):25. |
