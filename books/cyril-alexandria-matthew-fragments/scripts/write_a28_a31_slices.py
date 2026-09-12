#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass A≠B for cyril-matt-frag-a28..a31 (entries 109–124)."""
from __future__ import annotations

import json
import re
from pathlib import Path
from reader_titles import reader_title, scholar_label

ROOT = Path(__file__).resolve().parents[1]
SRC = json.loads((ROOT / "translations/matthew_fragments_source.json").read_text(encoding="utf-8"))
BY = {i + 1: s for i, s in enumerate(SRC["sections"])}


def clean(text: str) -> str:
    t = " ".join(text.split())
    return re.sub(r"(\S)\s+(\d{1,2})\s+(\S)", r"\1 \3", t)


def claim_for(n: int) -> str:
    if n <= 112:
        return "cyril-matt-frag-a28"
    if n <= 116:
        return "cyril-matt-frag-a29"
    if n <= 120:
        return "cyril-matt-frag-a30"
    return "cyril-matt-frag-a31"


CLEAN = {n: clean(BY[n]["greek"][0]) for n in range(109, 125)}

PASS_A = {109: 'Toward the enemies of the God and friends of the satan not it-is-necessary to-have friendship.', 110: "The the here temporary life loving, he-says, and of me preferring 'not is of me worthy'; but the of the here temporary life having-neglected and about much making me and the my commandments life he-will-find eternal.", 111: 'Of soul destruction here he-calls the from the body separation by-misuse. The having-found the soul of him, <that> is the the here temporary life preferring and as-if gaining, of death worse he-endures into indissoluble being-sent punishment and death.', 112: 'The receiving, he-says, you the the truth preaching that that receives the divinity, that is the Father and the Son and the holy Spirit; for this is, what he-says: the receiving you me receives, and the me receiving him the Father receives.', 113: 'In-order-that not someone poverty may-put-forward, he-said this wanting to-give wage to the receiving.', 114: 'Not being-ignorant him to-be the Christ he-asks or that he-was-about into Hades to-go-down, as some say; for he-knew the passion of him. Wherefore also lamb him he-named; but in-order-that still living he-may-persuade them and not after death of him they-may-be-added to another teacher.', 115: 'He-prepared the way of Lord that is he-made-ready the humans toward the to-receive the legislation of the God. He-showed on-the-one-hand also from-here—from himself then he-brings vote saying.', 116: 'By-oath he-confirms the about John. But the has-been-raised he-said through the of the worth of him great and elevated as upon king conspicuous or plant well-growing; for that also the being-prophesied he-saw and And see how by-oath he-confirms the about John; amen for he-says to-all he-made-known. I-say, that not has-been-raised greater of him. The has-been-raised he-said as about some king conspicuous or as about plant very tallest and by the virtues into height having-run-up.', 117: "Together with the others, who also before him have-become, born he-is of woman, but those indeed the faith having-accepted born on-the-one-hand no-longer they-are-called of women, but, says the most-wise evangelist, 'as-many-as received him, he-gave to them authority children of God to-become, who not from bloods nor from will of flesh nor from will of man, but from God were-born'; for we-were-reborn into adoption of God not from seed corruptible, but through word living and remaining. Better therefore beside every the born of woman those not from seed corruptible, having-been-born but rather from God. The on-the-one-hand John born was of woman, but those indeed the faith having-accepted born on-the-one-hand no-longer they-are-called of women, 'but from God were-born'. But when Christ rose-again having-spoiled the Hades, then the of the adoption is-given Spirit. But the blessed John before the to-be-given the Spirit departed, so-that even-if lesser we-are of those in law righteousness having-accomplished, yet in greater we-have-become through Christ.", 118: 'Greater he-says of John the faithful the through the washing having-been-reborn, which state he-calls kingdom of the heavens as to the faithful being-given of kingdom of heavens, of which not-yet was having-attained the Baptist. But the only having-been-baptized even if not-yet he-had virtuous life above the John is. The therefore word praise has of the holy baptism.', 119: 'Since the of the heavens kingdom is the into the Christ faith, from the preaching of John it-began, who was-pointing-out the being-preached through the baptism leading into kingdom. But those force into the kingdom of the heavens to-enter those to the of the idolatry renouncing old and empty custom and those to the letter not attending, but as-if from force some through the into Christ faith being-drawn-over. But having-said by forcers to-be-seized the kingdom the malicious he-hints of the Jews, who not only not were-believing into the Christ, but also the others were-hindering through threats and blows. And it-was-necessary firm in the mind to-be-shown those wanting through the into Christ faith to-partake of the of the heavens kingdom despising of the Jews threats. Yet also the faithful, whenever vigorously he-resists toward the bodily and psychic passions toward the to-enter into the of the heavens kingdom, this God-loving is forcer. But the until now this is until the continuous.', 120: 'The into Christ faith through the baptism the of the God kingdom is, which began from the preaching of John the pointing-out the Christ. But the forcing are those to the idolatry renouncing and to the old custom.', 121: 'Just-as of children dancing, but of others mourning not stands into one <the> will (for both they-blame to the companions not agreeing to them), such something have-suffered Jews neither the gloomy of the John nor the relaxed of the Christ having-accepted nor through one manner having-been-benefited.', 122: "For the on-the-one-hand John through ascetic life the of the flesh was-putting-to-death passions, but the Jesus as God with-authoritative law these was-putting-to-death, not indeed through ascetic toils being-helped. And the on-the-one-hand John 'preaching baptism of repentance' type was of gloom to those owing upon this to-mourn, but the Lord 'kingdom of heavens preaching' the bright in himself was-showing, through which now to the faithful he-sketches the about-to-be life and the toilless joy.", 123: "It-was-fitting to John as household-servant through the extreme austerity to-put-to-death the of the flesh passions, but to the Christ as free by-power of the divinity authoritatively the of the flesh to-put-to-death movements and the innate of the flesh law, not indeed through ascetic toils into this to-be-helped. Yet John 'baptism preaching of repentance' type himself provided to those owing to-mourn, but the Lord 'kingdom of heavens preaching' reasonably the relaxed and bright in himself was-showing, through which to the faithful he-was-sketching the inexpressible joy and the toilless life. For flute is the of the kingdom of the heavens sweetness, but dirge the of Gehenna painful-things.", 124: "The I-confess he-says according to custom human instead of the thanks I-acknowledge or I-glorify you; for custom is to the God-inspired scripture the of the confession name according to such some to-receive manner. It-has-been-written at-least that 'let-them-confess' Lord 'to the name of you the great, that fearful and holy it-is'. And again: 'I-will-confess to you, Lord, in whole heart of me'. But the having-been-twisted the mind: look, they-say, thanks he-acknowledges to the Father, then how not lesser is of him? Toward this may-say someone of those well knowing to the of the truth to-champion dogmas: and what the preventing, O best, the consubstantial Son to-accept and to-praise the of himself Father, saving through him the under heaven? But if you-think through the confession in lesser to-be him of the Father, see also the next. For Lord of the heaven and earth he-confesses and he-calls the Father. But the Son of the of the all ruling God altogether somehow with him masters of the all, not as lesser or of-other-essence, but as God from God with the equal glories being-crowned and the according to every anything equality toward him having essentially."}

PASS_B = {109: ['One must not keep friendship with the enemies of God and friends of Satan.'], 110: ['“The one who loves this temporary life here,” he says, “and prefers it to me ‘is not worthy of me.’ But the one who neglects this temporary life here and counts me and my commandments as much will find eternal life.”'], 111: ['Here he calls “loss of soul,” by a stretched use of the word, separation from the body. The one who “finds” his soul — that is, who prefers this temporary life here and seems to gain it — endures something worse than death: he is sent into undying punishment and death.'], 112: ['“The one who receives you,” he says, “who preach the truth, receives that divinity itself — that is, the Father and the Son and the Holy Spirit. For this is what he means: the one who receives you receives me, and the one who receives me receives the Father himself.”'], 113: ['He said this so that no one would plead poverty as an excuse, wanting to give a reward to those who receive them.'], 114: ['John does not ask because he does not know him to be the Christ, or because he was about to go down into Hades, as some say — for he knew his passion. That is why he also named him Lamb. He asks so that, while he himself is still alive, he may persuade them, and they may not attach themselves to another teacher after his death.'], 115: ['He prepared the Lord’s way — that is, he made people ready to receive God’s legislation. He also showed this from here — from himself he then brings a verdict, saying…'], 116: ['He confirms what concerns John with an oath. He said “has been raised” because of John’s great and lofty worth, as of a conspicuous king or a thriving plant — for he also saw the one prophesied. And see how he confirms what concerns John with an oath: “Amen,” he says, making it known to all. “I say that no one greater than he has been raised.” He said “has been raised” as about some conspicuous king, or as about a plant grown very tall and run up into height by the virtues.'], 117: ['Together with the others who came before him, he is born of a woman. But those who have accepted the faith are no longer called born of women. As the most wise evangelist says, “As many as received him, he gave them authority to become children of God, who were born not of bloods, nor of the will of the flesh, nor of the will of a man, but of God.” For we were reborn into God’s adoption not from corruptible seed, but through a living and abiding word. So those born not from corruptible seed but rather from God are better than everyone born of a woman.', 'John was born of a woman; but those who accepted the faith are no longer called born of women — “but they were born of God.” When Christ rose again after spoiling Hades, then the Spirit of adoption is given. Blessed John departed before the Spirit was given. So even if we are lesser than those who accomplished righteousness under the law, we have still come into greater things through Christ.'], 118: ['He calls greater than John the believer reborn through the washing — a state he names “kingdom of heaven,” since the kingdom of heaven is given to the faithful, which the Baptist had not yet attained. Even the one only baptized, if he does not yet have a virtuous life, is above John. So the saying is praise of holy baptism.'], 119: ['Since the kingdom of heaven is faith in Christ, it began from John’s preaching, who was pointing out the one being preached as leading through baptism into the kingdom. Those who force their way into the kingdom of heaven are the ones who renounce the old, empty custom of idolatry, and those who do not cling to the letter but are drawn over, as by a kind of force, through faith in Christ.', 'By saying the kingdom is seized by forcers he also hints at the malice of the Jews, who not only did not believe in Christ but also hindered others by threats and blows. Those who want to share the kingdom of heaven through faith in Christ had to prove firm in mind, despising the Jews’ threats. And the believer too, whenever he resists bodily and soul passions vigorously in order to enter the kingdom of heaven, is a God-loving forcer. “Until now” means until the ongoing time.'], 120: ['Faith in Christ through baptism is the kingdom of God, which began from the preaching of John, who pointed out Christ. The ones who force are those who renounce idolatry and the old custom.'], 121: ['Just as when some children dance and others mourn, their will does not settle into one thing (for both blame companions who do not agree with them), something like that happened to the Jews: they accepted neither John’s gloom nor Christ’s ease, and were helped by neither manner.'], 122: ['John was putting the passions of the flesh to death through an ascetic life; Jesus, as God, was putting them to death by an authoritative law, not helped by ascetic toils. John, “preaching a baptism of repentance,” was a type of gloom for those who ought to mourn for that; the Lord, “preaching the kingdom of heaven,” was showing brightness in himself, through which he now sketches for the faithful the life to come and toilless joy.'], 123: ['It was fitting for John, as a household servant, to put the flesh’s passions to death through extreme austerity; but for Christ, as free, to put to death the flesh’s movements and its innate law by the power of divinity with authority — not to be helped into this by ascetic toils. Still, John, “preaching a baptism of repentance,” offered himself as a type to those who ought to mourn; the Lord, “preaching the kingdom of heaven,” reasonably showed ease and brightness in himself, through which he was sketching for the faithful inexpressible joy and toilless life. For the flute is the sweetness of the kingdom of heaven; the dirge is the pains of Gehenna.'], 124: ['“I confess,” he says, in the human custom, for “I give thanks” or “I glorify you.” God-inspired scripture is accustomed to take the name “confession” in such a sense. It is written, “Let them confess, Lord, your great name, for it is fearful and holy,” and again, “I will confess you, Lord, with my whole heart.”', 'But those with a twisted mind say, “Look, he gives thanks to the Father — then how is he not lesser than him?” To this someone who knows how to champion the dogmas of truth would say: And what prevents you, my good people, from accepting that the consubstantial Son receives and praises his own Father, who saves the world under heaven through him?', 'If you think the confession puts him in a lesser place than the Father, look also at what follows. He confesses and calls the Father Lord of heaven and earth. And the Son of the God who rules all things surely masters all things with him — not as lesser or of another essence, but as God from God, crowned with equal glories and having equality with him in every respect essentially.']}

LEMMAS = {109: [], 110: [], 111: [{'form': 'καταχρηστικῶς', 'lemma': 'καταχρηστικός', 'gloss': 'by stretched use', 'lexica': 'LSJ'}], 112: [], 113: [], 114: [{'form': 'ἀμνόν', 'lemma': 'ἀμνός', 'gloss': 'lamb', 'lexica': 'NT'}], 115: [], 116: [], 117: [{'form': 'υἱοθεσίας', 'lemma': 'υἱοθεσία', 'gloss': 'adoption', 'lexica': 'NT'}], 118: [], 119: [{'form': 'βιασταί', 'lemma': 'βιαστής', 'gloss': 'forcer', 'lexica': 'NT'}], 120: [], 121: [], 122: [], 123: [], 124: [{'form': 'ὁμοούσιον', 'lemma': 'ὁμοούσιος', 'gloss': 'consubstantial', 'lexica': 'patristic'}]}

CHOICES = {109: [], 110: [], 111: [{'term': "<τοῦτ'>", 'english': 'that is', 'rejected': ['silent omit'], 'why': 'Angle brackets mark editor-supplied stretch; disclose, invent no Greek.'}], 112: [], 113: [], 114: [], 115: [{'term': 'ἔδειξε…λέγων', 'english': 'he showed…saying (breaks)', 'rejected': ['invented continuation'], 'why': 'Copy-text trails into the next lemma; disclose, invent no Greek.'}], 116: [], 117: [], 118: [], 119: [], 120: [], 121: [{'term': '<τό>', 'english': 'the (will)', 'rejected': ['silent omit'], 'why': 'Editor-supplied article; disclose.'}], 122: [], 123: [], 124: [{'term': 'ἐξομολογοῦμαι', 'english': 'I confess / give thanks / glorify', 'rejected': ['confess sins only'], 'why': 'Thanksgiving/praise to the Father, not penitential confession.'}]}

ALLUSIONS = {109: [{'reference': 'Matthew 10:34-35', 'reason': 'Not peace but a sword.', 'certainty': 'clear'}], 110: [{'reference': 'Matthew 10:37-39', 'reason': 'Worthy of me; find/lose life.', 'certainty': 'clear'}], 111: [{'reference': 'Matthew 10:39', 'reason': 'Find/lose the soul.', 'certainty': 'clear'}], 112: [{'reference': 'Matthew 10:40', 'reason': 'Receives you / me / Father.', 'certainty': 'clear'}], 113: [{'reference': 'Matthew 10:40-42', 'reason': 'Reward for receiving.', 'certainty': 'clear'}], 114: [{'reference': 'Matthew 11:3', 'reason': 'Are you the coming one?', 'certainty': 'clear'}], 115: [{'reference': 'Matthew 11:10', 'reason': 'Messenger prepares the way.', 'certainty': 'clear'}], 116: [{'reference': 'Matthew 11:11', 'reason': 'None greater than John raised.', 'certainty': 'clear'}], 117: [{'reference': 'Matthew 11:11', 'reason': 'Least in kingdom greater than John.', 'certainty': 'clear'}, {'reference': 'John 1:12-13', 'reason': 'Born of God.', 'certainty': 'clear'}, {'reference': '1 Peter 1:23', 'reason': 'Reborn through living word.', 'certainty': 'possible'}], 118: [{'reference': 'Matthew 11:11', 'reason': 'Baptism / kingdom greater than John.', 'certainty': 'clear'}], 119: [{'reference': 'Matthew 11:12', 'reason': 'Kingdom seized by forcers.', 'certainty': 'clear'}], 120: [{'reference': 'Matthew 11:12', 'reason': 'Forcers leave idolatry.', 'certainty': 'clear'}], 121: [{'reference': 'Matthew 11:16-17', 'reason': 'Children; flute and dirge.', 'certainty': 'clear'}], 122: [{'reference': 'Matthew 11:18-19', 'reason': 'John vs Son of Man.', 'certainty': 'clear'}], 123: [{'reference': 'Matthew 11:18-19', 'reason': 'Ascetic gloom vs bright kingdom.', 'certainty': 'clear'}], 124: [{'reference': 'Matthew 11:25', 'reason': 'I thank/confess you, Father.', 'certainty': 'clear'}, {'reference': 'Psalm 99:3', 'reason': 'Confess the great name.', 'certainty': 'possible'}, {'reference': 'Psalm 9:1', 'reason': 'Confess with whole heart.', 'certainty': 'possible'}]}

def main() -> None:
    eng_path = ROOT / "translations/matthew_fragments_english.json"
    english = json.loads(eng_path.read_text(encoding="utf-8"))
    english = [e for e in english if e.get("section") not in CLEAN]
    cleans = []
    for n in range(109, 125):
        src = BY[n]
        a, b = PASS_A[n], " ".join(PASS_B[n])
        if a.strip() == b.strip():
            raise SystemExit(f"A==B at {n}")
        claim = claim_for(n)
        ed = src["fragment"]
        cleans.append(
            {
                "section": n,
                "edition_fragment": ed,
                "matthew": src["matthew"],
                "locus": src["locus"],
                "head": src["head"],
                "greek": [CLEAN[n]],
                "claim": claim,
                "witness": "khazarzar-aegean-pg72-extract",
                "ocr_cleanup": "whitespace + stray digits; no IA merge",
            }
        )
        english.append(
            {
                "section": n,
                "edition_fragment": ed,
                "matthew": src["matthew"],
                "title": reader_title(src.get("matthew")),
                "scholar_label": scholar_label(fragment=src.get("fragment"), matthew=src.get("matthew"), existing=src.get("head")),
                "english": PASS_B[n],
                "notes_covered": [],
                "added_allusions": ALLUSIONS[n],
                "translator_notes": [
                    "Copy-text khazarzar Aegean PG 72 extract.",
                    "Section id = source array order (1-based).",
                    "IA OCR not reading text.",
                ],
                "claim": claim,
            }
        )
        j = {
            "excerpt_id": f"matt_frag_{n:02d}",
            "section": n,
            "edition_fragment": ed,
            "matthew": src["matthew"],
            "treatise": "cpg5206_fragmenta_in_matthaeum",
            "claim": claim,
            "edition": {
                "id": "khazarzar-aegean-pg72-extract",
                "language": "grc",
                "locus": src["head"],
                "path": "translations/matthew_fragments_source.json",
                "greek_clean": "translations/matthew_fragments_greek_clean_a28a31.json",
            },
            "source_text": CLEAN[n],
            "pass_a_gloss": PASS_A[n],
            "pass_b_english": PASS_B[n],
            "lemmas": LEMMAS[n],
            "choices": CHOICES[n],
            "variants": [
                {
                    "witnesses": [
                        "khazarzar-aegean-pg72-extract",
                        "matia-aegean-pg72-extract-mirror",
                    ],
                    "note": "PDFs byte-identical.",
                },
                {"witnesses": ["ia-bim-pg72-djvu-ocr"], "note": "Not copy-text; no merge."},
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
        print("wrote", out.name, claim, "ed_fr", ed)

    (ROOT / "translations/matthew_fragments_greek_clean_a28a31.json").write_text(
        json.dumps(
            {
                "meta": {
                    "claims": [
                        "cyril-matt-frag-a28",
                        "cyril-matt-frag-a29",
                        "cyril-matt-frag-a30",
                        "cyril-matt-frag-a31",
                    ],
                    "sections": "109-124",
                },
                "sections": cleans,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    english.sort(key=lambda e: e["section"])
    eng_path.write_text(json.dumps(english, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("english", [e["section"] for e in english])


if __name__ == "__main__":
    main()
