#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Write cyril-matt-frag-a1 greek_clean + English + justifications."""
from __future__ import annotations

import json
from pathlib import Path
from reader_titles import reader_title, scholar_label

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    clean_map = {
        1: (
            "Ἰαὼ τὴν σωτηρίαν οἱ Ἑβραῖοι ἔλεγον, Χριστοῦ δὲ εἶπε διὰ τὸ τοὺς "
            "παλαιοὺς βασιλεῖς τε καὶ ἱερεῖς τῷ ἐλαίῳ χρίεσθαι διὰ τοῦ κέρατος. "
            "ὁ δὲ ἡμέτερος Ἰησοῦς Χριστὸς οὐ διὰ τὸ τῷ κέρατι χρισθῆναι "
            "προσηγορεύθη Χριστός, ἀλλὰ τὸ τῷ θείῳ πνεύματι· ἀληθῶς γὰρ καὶ "
            "κυρίως αὐτὸς εἶχε τὸ πνεῦμα τὸ ἅγιον."
        ),
        2: (
            "Μέμνηται τοῦ Ἀβραάμ, ἐπειδὴ ἐκεῖνος πρῶτος ἐγένετο τύπος τῶν δύο "
            "λαῶν τῶν μελλόντων πιστεύειν τῷ Χριστῷ· καὶ γὰρ ἐν ἀκροβυστίᾳ ὢν "
            "ἐπίστευσε καὶ μετὰ τὸ περιτμηθῆναι ἔμεινεν πάλιν πιστός. μέμνηται "
            "δὲ κατ' ἐξαίρετον καὶ τοῦ ∆αβίδ, ἐπειδὴ καὶ αὐτὸς τύπος γέγονεν "
            "τοῦ Χριστοῦ· ὥσπερ γὰρ τοῦ Σαοὺλ ἐκβληθέντος ὡς ἀδοκίμου ∆αβὶδ "
            "δεύτερος προεχειρίσθη βασιλεὺς εὐάρεστος τῷ θεῷ, οὕτως καὶ τοῦ "
            "πρώτου ἀνθρώπου, τοῦ Ἀδάμ φημι, ἐκβληθέντος διὰ τὴν παρακοὴν καὶ "
            "μηκέτι βασιλεύσαντος τῶν λοιπῶν ὅλως εἰσηνέχθη δεύτερος Ἀδάμ, ὁ "
            "Χριστὸς βασιλεὺς τῶν πάντων, ἵνα τὸ ἐν Ἀδὰμ ἀπολωλὸς διὰ Χριστοῦ "
            "τοῖς ἀνθρώποις ἐπαναληφθῇ, βασιλεὺς οὐ μόνον γῆς, ἀλλὰ καὶ "
            "οὐρανοῦ· υἱὸς δὲ ἀνθρώπου φύσει καλεῖται ὡς πάντα ἔχων, ὅσα εἶχεν "
            "ὁ Ἀδάμ, νυνὶ θεὸς ὤν. Ἀβραὰμ ἐν ἀκροβυστίᾳ ὢν ἐπίστευσε τῷ θεῷ· "
            "εἶτα δεξάμενος τὰς ὑποσχέσεις καὶ περιτμηθεὶς ἀλώβητον τὴν πίστιν "
            "διετήρησεν. εἰκότως τοίνυν ἀναχθήσεται τὸ ῥητὸν εἰς ἕτερόν τι "
            "θεώρημα περὶ τῆς τοῦ Χριστοῦ ἐκκλησίας τῆς τε ἐκ περιτομῆς καὶ "
            "τῆς ἐξ ἐθνῶν· τύπος γὰρ ἦν, ὡς εἰκός, τῶν δύο λαῶν τῶν εἰς Χριστὸν "
            "πεπιστευκότων. ἀλλ' ἐκεῖ μὲν προτέρα ἡ ἀκροβυστία τῆς περιτομῆς· "
            "φύσεως γὰρ ἔργον ἡ ἀκροβυστία, ἐντολῆς δὲ καὶ νόμου ἡ περιτομή. "
            "διὰ τοῦτο ἐκείνη ταύτης προηγήσατο καὶ μετὰ ταῦτα εἰς αὐτὴν ἡ "
            "περιτομὴ ἀνακάμπτει, ἐπεὶ καὶ βέλτιόν ἐστι φύσις ἅμα καὶ νόμος ἢ "
            "τὸ διεστηκέναι ἀπ' ἀλλήλων χωρίς. ἀλλὰ καὶ ∆αβὶδ τύπος ἦν τοῦ "
            "Χριστοῦ· τοῦ γὰρ Σαοὺλ ἐκβληθέντος ἀντεισήχθη ∆αβίδ. οὕτως καὶ "
            "τοῦ Ἀδὰμ διὰ τὴν παρακοὴν τῆς Ἐδὲμ διωχθέντος ὁ δεύτερος "
            "ἀντεισήχθη Ἀδὰμ ὡς ἂν πρὸς τὴν ἀρχαίαν τάξιν τὸν Ἀδὰμ τὸν πρῶτον "
            "ἀποκαταστήσῃ."
        ),
        3: (
            "∆ιὰ τοῦτο ἐξ ἀνδρῶν ποιεῖται τῆς γενεαλογίας τὰ ὀνόματα, ἐπειδὴ "
            '"ἡ γυνὴ δόξα ἀνδρός ἐστι", παρακολούθημα οὖσα καὶ οὐκ ἀρχὴ τοῦ '
            "ἀνδρός."
        ),
        4: (
            "Ὠικοδόμησεν ὁ Ζοροβάβελ τὸν ἀπὸ Σολομῶνος μὲν πάλαι "
            "ᾠκοδομηθέντα ναὸν ὑπὸ δὲ Βαβυλωνίων ἐμπρησθέντα. καὶ ὁ κύριος "
            "ἀληθινὸς οἰκοδόμος ἐστὶ τοῦ διαρρυέντος τοῖς παραπτώμασι λογικοῦ "
            "ναοῦ καὶ ἐμπρησθέντος ἀλλοτρίῳ πυρί, ὅπερ ἡμεῖς ἐξεκαύσαμεν οὐ "
            "μόνον τῷ σαρκικῷ φρονήματι τὸ τῆς ψυχῆς νοερὸν ἕπεσθαι δουλικῶς "
            "παρασκευάσαντες, ἀλλὰ καὶ τὴν τῶν παθῶν ὕλην ἀναιδῆ δι' ἐνεργείας "
            "ἐξάψαντες. ἀλλὰ καὶ λίθον ἔχει ὁ Ζοροβάβελ ἐν τῇ χειρὶ ἑπτὰ "
            "ὀφθαλμοῖς κοσμούμενον. ἔστι καὶ τῷ κυρίῳ λίθος ἡ εἰς αὐτὸν "
            "πίστις· ἐν τῇ χειρὶ δέ, ὅτι ἐν τῇ πράξει τῶν ἐντολῶν ἡ πίστις "
            "τοῦ Χριστοῦ διαφαίνεται. πράξεως δέ ἐστι σύμβολον προδήλως ἡ "
            "χείρ. φέρων οὖν ἐν τῇ χειρὶ τὸν λίθον ὁ κύριος ἔμπρακτον ἡμᾶς "
            "διδάσκει τὴν εἰς αὐτὸν πίστιν ἔχειν ταῖς ἑπτὰ κοσμουμένην "
            "ἐνεργείαις τοῦ πνεύματος."
        ),
    }

    pass_a = {
        1: (
            "Iao the salvation the Hebrews used to say, but of Christ he said "
            "because the ancient kings and priests were anointed with the oil "
            "through the horn. But our Jesus Christ was not named Christ "
            "because of being anointed with the horn, but [named so by] the "
            "divine Spirit; for truly and properly he himself had the Holy Spirit."
        ),
        2: (
            "He mentions Abraham, since that one first became a type of the two "
            "peoples about to believe in Christ; for also while in uncircumcision "
            "he believed and after being circumcised he remained again faithful. "
            "And he mentions especially also David, since he too became a type of "
            "Christ; for just as when Saul was cast out as unapproved David was "
            "appointed second as king well-pleasing to God, so also when the first "
            "human — Adam I mean — was cast out through disobedience and no longer "
            "ruling the rest at all, a second Adam was brought in, Christ king of "
            "all, so that what was lost in Adam might be taken up again for humans "
            "through Christ, king not only of earth but also of heaven; and he is "
            "called son of man by nature as having all that Adam had, now being God. "
            "Abraham while in uncircumcision believed God; then receiving the "
            "promises and being circumcised he kept the faith unharmed. Reasonably "
            "therefore the saying will be led up to some other contemplation about "
            "the church of Christ both from circumcision and from the nations; for "
            "he was a type, as is likely, of the two peoples who have believed in "
            "Christ. But there the uncircumcision is prior to circumcision; for "
            "uncircumcision is a work of nature, and circumcision of command and "
            "law. For this reason that preceded this and after these things "
            "circumcision turns back into it, since nature together with law is "
            "better than being separated from each other apart. But David also was "
            "a type of Christ; for when Saul was cast out David was brought in "
            "instead. Thus also when Adam through disobedience was driven from Eden "
            "the second Adam was brought in instead so that he might restore the "
            "first Adam to the ancient order."
        ),
        3: (
            "For this reason he makes the names of the genealogy from men, since "
            '"the woman is glory of man," being an accompaniment and not a '
            "beginning of the man."
        ),
        4: (
            "Zerubbabel built the temple once built of old by Solomon and burned by "
            "the Babylonians. And the Lord is true builder of the rational temple "
            "that flowed apart by transgressions and was burned by alien fire, which "
            "we kindled, not only preparing the intellective part of the soul to "
            "follow slavishly the fleshly mind, but also shamelessly kindling the "
            "matter of the passions through activity. But Zerubbabel also has a "
            "stone in the hand adorned with seven eyes. And for the Lord also a "
            "stone is the faith into him; and in the hand, because in the practice "
            "of the commandments the faith of Christ shines through. And the hand "
            "is clearly a symbol of practice. So the Lord bearing the stone in the "
            "hand teaches us to have the faith into him as practical, adorned with "
            "the seven energies of the Spirit."
        ),
    }

    pass_b = {
        1: [
            (
                "The Hebrews used to call “Iao” salvation. Matthew says “of Christ,” "
                "though, because the old kings and priests were anointed with oil "
                "from the horn."
            ),
            (
                "Our Jesus Christ was not named Christ because a horn anointed him, "
                "but because the divine Spirit did. For he truly and properly had "
                "the Holy Spirit himself."
            ),
        ],
        2: [
            (
                "Matthew names Abraham because Abraham was the first type of the two "
                "peoples who would believe in Christ. He believed while still "
                "uncircumcised, and after circumcision he remained faithful."
            ),
            (
                "Matthew names David especially because David too was a type of "
                "Christ. When Saul was cast out as rejected, David was appointed "
                "second as a king well-pleasing to God. In the same way, when the "
                "first human — Adam — was cast out through disobedience and no longer "
                "ruled the rest, a second Adam was brought in: Christ, king of all, "
                "so that what was lost in Adam might be recovered for humankind "
                "through Christ. He is king not only of earth but of heaven. He is "
                "called Son of Man by nature because he has all that Adam had, while "
                "now being God."
            ),
            (
                "Abraham believed God while uncircumcised; then, after receiving the "
                "promises and being circumcised, he kept the faith unharmed. So the "
                "verse rightly rises to another contemplation: the church of Christ "
                "from circumcision and from the nations. Abraham was a type of those "
                "two peoples who have believed in Christ."
            ),
            (
                "There uncircumcision came before circumcision. Uncircumcision is "
                "nature’s work; circumcision is command and law. That is why the "
                "former led, and afterward circumcision turns back into it — because "
                "nature together with law is better than the two standing apart."
            ),
            (
                "David too was a type of Christ. When Saul was cast out, David was "
                "brought in instead. So also, when Adam was driven from Eden through "
                "disobedience, the second Adam was brought in instead, that he might "
                "restore the first Adam to the ancient order."
            ),
        ],
        3: [
            (
                "That is why the genealogy’s names run through men: “the woman is "
                "the glory of the man,” an accompaniment, not the man’s beginning."
            ),
        ],
        4: [
            (
                "Zerubbabel rebuilt the temple Solomon had once built and the "
                "Babylonians had burned. The Lord is the true builder of the "
                "rational temple that fell apart through transgressions and burned "
                "with an alien fire — a fire we ourselves kindled, not only making "
                "the soul’s intellect follow the fleshly mind as a slave, but also "
                "shamelessly lighting the fuel of the passions by what we do."
            ),
            (
                "Zerubbabel also holds in his hand a stone adorned with seven eyes. "
                "For the Lord too the stone is faith in him; and it is “in the hand” "
                "because faith in Christ shows itself in the practice of the "
                "commandments. The hand is plainly a symbol of practice. So the "
                "Lord, bearing the stone in his hand, teaches us to hold faith in "
                "him as something done, adorned with the seven energies of the Spirit."
            ),
        ],
    }

    lemmas = {
        1: [
            {
                "form": "Ἰαὼ",
                "lemma": "Ἰαώ",
                "gloss": "Iao (divine name form)",
                "lexica": "patristic",
            },
            {
                "form": "προσηγορεύθη",
                "lemma": "προσαγορεύω",
                "gloss": "be named / addressed as",
                "lexica": "LSJ",
            },
            {
                "form": "κυρίως",
                "lemma": "κυρίως",
                "gloss": "properly / in the proper sense",
                "lexica": "LSJ",
            },
        ],
        2: [
            {"form": "τύπος", "lemma": "τύπος", "gloss": "type / figure", "lexica": "LSJ / NT"},
            {
                "form": "ἀκροβυστίᾳ",
                "lemma": "ἀκροβυστία",
                "gloss": "uncircumcision",
                "lexica": "NT",
            },
            {
                "form": "ἐπαναληφθῇ",
                "lemma": "ἐπαναλαμβάνω",
                "gloss": "be taken up again / recovered",
                "lexica": "LSJ",
            },
            {
                "form": "ἀντεισήχθη",
                "lemma": "ἀντεισάγω",
                "gloss": "be brought in instead",
                "lexica": "LSJ",
            },
        ],
        3: [
            {
                "form": "παρακολούθημα",
                "lemma": "παρακολούθημα",
                "gloss": "accompaniment / sequel",
                "lexica": "LSJ",
            },
            {"form": "δόξα", "lemma": "δόξα", "gloss": "glory", "lexica": "1 Cor 11:7"},
        ],
        4: [
            {
                "form": "διαρρυέντος",
                "lemma": "διαρρέω",
                "gloss": "flow apart / fall to pieces",
                "lexica": "LSJ",
            },
            {
                "form": "ἔμπρακτον",
                "lemma": "ἔμπρακτος",
                "gloss": "practical / put into action",
                "lexica": "LSJ",
            },
            {
                "form": "ἐνεργείαις",
                "lemma": "ἐνέργεια",
                "gloss": "energies / operations",
                "lexica": "patristic",
            },
        ],
    }

    choices = {
        1: [
            {
                "term": "Ἰαώ",
                "english": "Iao",
                "rejected": ["Yahweh (modernizing)", "Jehovah"],
                "why": "Keep the Greek form Cyril reports the Hebrews said.",
            }
        ],
        2: [
            {
                "term": "τύπος",
                "english": "type",
                "rejected": ["symbol only", "foreshadowing (too soft)"],
                "why": "Standard patristic typology word; Pass B keeps “type.”",
            }
        ],
        3: [
            {
                "term": "παρακολούθημα",
                "english": "accompaniment",
                "rejected": ["appendix", "afterthought"],
                "why": "She follows man; not an independent origin of the line.",
            }
        ],
        4: [
            {
                "term": "ἔμπρακτον … πίστιν",
                "english": "faith … as something done / practical",
                "rejected": ["active faith (vague)", "works-righteousness"],
                "why": "Stone-in-hand = faith shown in commandment practice.",
            }
        ],
    }

    allusions = {
        1: [
            {
                "reference": "Matthew 1:1",
                "reason": "Lemma of the fragment (Christ / genealogy head).",
                "certainty": "clear",
            }
        ],
        2: [
            {
                "reference": "Matthew 1:1",
                "reason": "Abraham and David named in the lemma.",
                "certainty": "clear",
            }
        ],
        3: [
            {
                "reference": "1 Corinthians 11:7",
                "reason": "Quoted: woman is glory of man.",
                "certainty": "clear",
            }
        ],
        4: [
            {
                "reference": "Matthew 1:12",
                "reason": "Zerubbabel in the genealogy lemma.",
                "certainty": "clear",
            },
            {
                "reference": "Zechariah 3:9",
                "reason": "Stone with seven eyes in Zerubbabel’s hand.",
                "certainty": "clear",
            },
            {
                "reference": "Isaiah 11:2",
                "reason": "Seven energies of the Spirit adorning faith.",
                "certainty": "possible",
            },
        ],
    }

    src = json.loads((ROOT / "translations/matthew_fragments_source.json").read_text(encoding="utf-8"))
    by = {s["section"]: s for s in src["sections"]}

    clean_sections = []
    english = []
    for n in (1, 2, 3, 4):
        a = pass_a[n]
        b = " ".join(pass_b[n])
        if a.strip() == b.strip():
            raise SystemExit(f"Pass A equals Pass B for section {n}")
        clean_sections.append(
            {
                "section": n,
                "fragment": n,
                "matthew": by[n]["matthew"],
                "locus": by[n]["locus"],
                "head": by[n]["head"],
                "greek": [clean_map[n]],
                "claim": "cyril-matt-frag-a1",
                "witness": "khazarzar-aegean-pg72-extract",
                "ocr_cleanup": "joined PDF line-break hyphenation only; no IA merge",
            }
        )
        english.append(
            {
                "section": n,
                "fragment": n,
                "matthew": by[n]["matthew"],
                "title": reader_title(by[n].get("matthew")),
                "scholar_label": scholar_label(fragment=by[n].get("fragment"), matthew=by[n].get("matthew"), existing=by[n].get("head")),
                "english": pass_b[n],
                "notes_covered": [],
                "added_allusions": allusions[n],
                "translator_notes": [
                    "Copy-text khazarzar Aegean PG 72 extract; PDF line-break hyphens joined in greek_clean_a1.",
                    "IA PG72 OCR not used as reading text.",
                ],
                "claim": "cyril-matt-frag-a1",
            }
        )
        j = {
            "excerpt_id": f"matt_frag_{n:02d}",
            "section": n,
            "fragment": n,
            "matthew": by[n]["matthew"],
            "treatise": "cpg5206_fragmenta_in_matthaeum",
            "claim": "cyril-matt-frag-a1",
            "edition": {
                "id": "khazarzar-aegean-pg72-extract",
                "language": "grc",
                "locus": by[n]["head"],
                "path": "translations/matthew_fragments_source.json",
                "greek_clean": "translations/matthew_fragments_greek_clean_a1.json",
            },
            "source_text": clean_map[n],
            "pass_a_gloss": pass_a[n],
            "pass_b_english": pass_b[n],
            "lemmas": lemmas[n],
            "choices": choices[n],
            "variants": [
                {
                    "witnesses": [
                        "khazarzar-aegean-pg72-extract",
                        "matia-aegean-pg72-extract-mirror",
                    ],
                    "note": "PDFs byte-identical; no textual disagreement.",
                },
                {
                    "witnesses": ["ia-bim-pg72-djvu-ocr"],
                    "note": "IA OCR too damaged for lemma-level check; not used as copy-text; no merge.",
                },
            ],
            "guards": {
                "pass_a_ne_pass_b": True,
                "cpg_5219_5220_closed": True,
                "melito_skipped": True,
                "no_css": True,
                "jer_h20b_preserved": True,
            },
        }
        out = ROOT / f"reviews/justifications/matt_frag_{n:02d}.json"
        out.write_text(json.dumps(j, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("wrote", out.name)

    (ROOT / "translations/matthew_fragments_greek_clean_a1.json").write_text(
        json.dumps(
            {"meta": {"claim": "cyril-matt-frag-a1", "sections": "1-4"}, "sections": clean_sections},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (ROOT / "translations/matthew_fragments_english.json").write_text(
        json.dumps(english, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("A≠B verified for fr.1–4")


if __name__ == "__main__":
    main()
