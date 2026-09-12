#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass A≠B for cyril-matt-frag-a12..a15 (entries 45–60)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = json.loads((ROOT / "translations/matthew_fragments_source.json").read_text(encoding="utf-8"))
BY = {i + 1: s for i, s in enumerate(SRC["sections"])}


def clean(text: str) -> str:
    t = " ".join(text.split())
    return re.sub(r"(\S)\s+(\d{1,2})\s+(\S)", r"\1 \3", t)


def claim_for(n: int) -> str:
    if n <= 48:
        return "cyril-matt-frag-a12"
    if n <= 52:
        return "cyril-matt-frag-a13"
    if n <= 56:
        return "cyril-matt-frag-a14"
    return "cyril-matt-frag-a15"


CLEAN = {n: clean(BY[n]["greek"][0]) for n in range(45, 61)}

PASS_A = {
    45: (
        "Teaches us here the savior the punishment to escape when-sinning. The therefore "
        "after-thought upon the sins and the toward the having-been-grieved from us "
        "consolation and the of the forgiveness of the sin request both the brother heals "
        "and the God."
    ),
    46: (
        "The at-any-rate quadrans signifies the fourth of the hin measure. This according to "
        "the Hebrews' voice is two obols, which Luke having-clarified 'lepton' named. And we "
        "let-us-be-freed both of the enemy and avenger, that-is of the devil, while we are in "
        "this road, and of the of dishonor passions, which adversaries of us are; for nobody "
        "of us other adversary, unless we of ourselves through these become adversaries and "
        "not the conscience condemn us as despising of the reminder of it, lest we be-handed-"
        "over to the judge of all God by the conscience having-been-convicted; and he will-"
        "hand-over to the exactors, that-is to the punishing angels, and we will-be-demanded "
        "the upon every fault penalties, small and great."
    ),
    47: (
        "Carefully therefore the Lord here adversary names the attempting to take-away "
        "something of the belonging to us. And we are-well-disposed to him, if we keep the "
        "command of the Lord having-said 'to the wanting with you to go-to-law and the tunic "
        "of you to take, allow to him also the cloak' and upon every such matter likewise."
    ),
    48: (
        "What he says is such: before judgment be-reasonable. Since also if you are-accused "
        "and imprisoned, you are not released until you pay until an obol; for this the "
        "quadrans shows. And what he says is such: for he exhorts to be-reasonable and not "
        "to trust to the judgment; for if something happen beyond hope and you are-held by "
        "the judge, you will not be-released until you pay the last obol; for this is called "
        "quadrans."
    ),
    49: (
        "Let there be supposed someone, he says, upon one of those arranged into rule having-"
        "made some charges against you, then to those leading-away onto the court having-"
        "pointed-out he causes to be-carried-off; while therefore, he says, with him you are "
        "in the road, that-is before arriving toward the judge, give work, instead of to set "
        "every do not hesitate zeal, in order that you be-freed from him. And if this not "
        "happen, he will-hand-over you to the judge. Then when liable to the debts you are-"
        "found, you will-be-handed-over to the exactor, that-is to the collectors, and those "
        "having-shut you up will-demand also 'the last lepton'. Therefore liable on-the-one-"
        "hand to faults we are all those being upon the earth. And of each indeed adversary "
        "and accuser the satan; for enemy he is and avenger; while therefore we are in the "
        "road, that-is while not-yet toward the of the here life we have-arrived end, let-us-"
        "be-freed of him, let-us-loose the against ourselves charges, the through Christ grace "
        "let-us-seize freeing us of every debt and of judgment putting-outside of punishment "
        "and of fear, lest somehow having unwashed the stain we be-carried toward the judge "
        "and be-handed-over 'to the exactors' or to the punishers, of whom not anyone would "
        "escape the harshness. And he will-be-demanded rather the upon every fault penalties, "
        "small and great. Far from these will be those testing the of Christ's presence time "
        "and the upon it mystery not having-ignored."
    ),
    50: (
        "Perhaps there are some having-received such a gift so as not to desire. But Christ "
        "as having-strengthened the of humans nature also the beyond law he commands as now "
        "being-possible; for if even to those before Christ impossible this was, yet to the "
        "faithful easy-to-accomplish the the desires to cut-out."
    ),
    51: (
        "The having-looked-at a woman and having-desired then is judged, when appear to him "
        "the flesh of the woman toward desire beautiful and fleshly her he see and sinfully; "
        "for the through love of the pure seeing the beauty, not the flesh he considers "
        "beautiful, but the soul."
    ),
    52: (
        "Having-said if the eye of you scandalize you and the following, eye he says the "
        "thought of the desire, which he says to be-cut-out."
    ),
    53: (
        "Eye and hand is-understood the friend. For if someone thus you love as in rank of "
        "right eye and useful him you consider as in rank of right hand and he harms of you "
        "the soul, cut-off these from you and far be-separated from them; for when not each-"
        "other you save, but rather both you are-destroyed-together being together, it-"
        "profits having-been-separated at-least the one to be-saved."
    ),
    54: (
        "The the sober woman casting-out gives to her license to another to be-married, which "
        "is a form of adultery as-if not having-been-loosed the yoking; for not the divorce-"
        "papers beside God loose the marriage, but the improper deed."
    ),
    55: (
        "The you shall not swear-falsely and the following. If someone shameless bring-upon "
        "the holy ones an oath, instead of the oath will be for them the yes and the no."
    ),
    56: (
        "Through this he prevents us to swear according to the heaven and the earth, in order "
        "that we not give to the creation the beyond the creation dignity god-making it; for "
        "those swearing, he says, 'according to the greater swear' as the apostle said. And he "
        "forbids also the according to the 'Jerusalem' oath, since the earthly 'Jerusalem' of "
        "the 'above Jerusalem' type is and according to himself alone swears the God, which is "
        "of the own glory. Wherefore as surpassing us of the likeness we ought not according "
        "to ourselves or of the ourselves to swear glory; for not free we are as the God, but "
        "under the of the God we are authority."
    ),
    57: (
        "Be, says the Christ, not toward the to-receive ready, but toward the to-give; for "
        "the one separates us from God, but the other to join is-wont and especially, when the "
        "asking worthy happens-to-be and just the request."
    ),
    58: (
        "Let-us-love the enemies not insofar adulterers they are or murderers, but insofar "
        "humans; for the to-sin of activity is, not of essence; wherefore neither work of God "
        "the sin."
    ),
    59: (
        "Perhaps someone might-say, how the blessed Paul Alexander curses the smith? Toward "
        "whom we say not as own enemy, but as enemy of the gospel he cursed him teaching, that "
        "to the of God enemies always it-is-necessary to war. But perhaps someone the blessed "
        "Paul as cursing the smith Alexander bringing-forward to us might-persuade not the "
        "enemies to love; toward whom it-is to say, that not as own enemy, but as of the Christ "
        "and of the gospel curses the Paul teaching that always to such it-is-necessary to war."
    ),
    60: (
        "The through itself the good doing virtue above-world has the boast."
    ),
}

PASS_B = {
    45: [
        (
            "Here the Savior teaches us how sinners escape punishment. Afterthought over our "
            "sins, appeal to the one we grieved, and asking forgiveness of the fault heal both "
            "the brother and God."
        ),
    ],
    46: [
        (
            "The quadrans means a fourth of the hin. In Hebrew speech it is two obols, which "
            "Luke clarifies by naming it a “lepton.”"
        ),
        (
            "So let us be freed from the enemy and avenger — that is, the devil — while we are "
            "still on this road, and from the passions of dishonor, which are our adversaries. "
            "No one else is our adversary unless we make ourselves so through these things, and "
            "unless conscience condemns us for despising its reminder."
        ),
        (
            "Otherwise we will be handed over to God, the judge of all, convicted by conscience. "
            "He will hand us to the exactors — the punishing angels — and we will be charged "
            "penalties for every fault, small and great."
        ),
    ],
    47: [
        (
            "Carefully, then, the Lord here names “adversary” the one who tries to take something "
            "that belongs to us. We are well disposed toward him if we keep the Lord’s command: "
            "“To the one who wants to go to law with you and take your tunic, give him the cloak "
            "as well,” and likewise in every such matter."
        ),
    ],
    48: [
        (
            "What he means is this: be reasonable before judgment. If you are accused and jailed, "
            "you are not released until you pay down to an obol — that is what the quadrans shows."
        ),
        (
            "He exhorts us to be reasonable and not to trust the lawsuit. If something goes "
            "against hope and the judge holds you, you will not be released until you pay the "
            "last obol. That is what is called a quadrans."
        ),
    ],
    49: [
        (
            "Suppose someone, he says, brings charges against you before one set in authority, "
            "then points you out to those who lead to court and has you hauled off. While you are "
            "still with him on the road — that is, before you reach the judge — give diligence: "
            "do not hesitate to use every effort to be freed from him."
        ),
        (
            "If that does not happen, he will hand you to the judge. When you are found liable "
            "for the debts, you will be handed to the exactor — the collectors — and after "
            "shutting you up they will demand even “the last lepton.”"
        ),
        (
            "So all of us on earth are liable for faults. Each person’s adversary and accuser is "
            "Satan, for he is enemy and avenger. While we are still on the road — that is, before "
            "we reach the end of this life — let us be freed from him, loose the charges against "
            "ourselves, and seize the grace through Christ that frees us from every debt and sets "
            "us outside judgment, punishment, and fear."
        ),
        (
            "Otherwise, still carrying the stain unwashed, we may be carried to the judge and "
            "handed to “the exactors,” the punishers, whose harshness no one escapes. Then "
            "penalties will be demanded for every fault, small and great. Far from this will be "
            "those who prove the time of Christ’s coming and have not ignored the mystery in him."
        ),
    ],
    50: [
        (
            "Perhaps some have received such a gift that they do not desire. But Christ, having "
            "strengthened human nature, also commands what is beyond the law as now possible. "
            "Even if this was impossible for those before Christ, for the faithful cutting out "
            "desires is easy to accomplish."
        ),
    ],
    51: [
        (
            "The one who looks at a woman and desires is judged when her flesh appears beautiful "
            "to him for desire, and he sees her fleshly and sinfully. The one who looks at beauty "
            "through love of purity does not count the flesh beautiful, but the soul."
        ),
    ],
    52: [
        (
            "When he says, “If your eye causes you to stumble,” and what follows, by “eye” he "
            "means the thought of desire, which he says must be cut out."
        ),
    ],
    53: [
        (
            "“Eye” and “hand” are understood as the friend. If you love someone as a right eye, "
            "and count him useful as a right hand, and he harms your soul, cut them off from you "
            "and separate far from them. When you do not save each other but rather both perish "
            "together, it is better that, once separated, at least one be saved."
        ),
    ],
    54: [
        (
            "The one who casts out a chaste wife gives her leave to marry another — a form of "
            "adultery, as if the yoking were not loosed. For divorce papers do not loose marriage "
            "before God; improper deed does."
        ),
    ],
    55: [
        (
            "“You shall not swear falsely,” and what follows. If someone shamelessly lays an oath "
            "on the saints, instead of the oath they will have yes and no."
        ),
    ],
    56: [
        (
            "For this reason he forbids us to swear by heaven and earth: that we not give creation "
            "a dignity beyond creation and make it a god. Those who swear, he says, “swear by the "
            "greater,” as the apostle said."
        ),
        (
            "He also forbids the oath by “Jerusalem,” because earthly Jerusalem is a type of the "
            "Jerusalem above, and God swears by himself alone — that is, by his own glory. Since "
            "that likeness surpasses us, we ought not swear by ourselves or by our own glory. We "
            "are not free as God is; we are under God’s authority."
        ),
    ],
    57: [
        (
            "Be ready, Christ says, not to receive but to give. Receiving separates us from God; "
            "giving joins us to him — especially when the one who asks is worthy and the request "
            "is just."
        ),
    ],
    58: [
        (
            "Let us love enemies not insofar as they are adulterers or murderers, but insofar as "
            "they are human. Sinning belongs to activity, not to essence; that is why sin is not "
            "God’s work."
        ),
    ],
    59: [
        (
            "Someone may ask how blessed Paul curses Alexander the smith. We say he cursed him "
            "not as a private enemy but as an enemy of the gospel, teaching that one must always "
            "war against God’s enemies."
        ),
        (
            "Someone may bring forward blessed Paul cursing Alexander the smith to persuade us "
            "not to love enemies. To him we say: Paul curses not as against a private enemy, but "
            "as against an enemy of Christ and the gospel, teaching that one must always war "
            "against such people."
        ),
    ],
    60: [
        (
            "The one who does the good for the good itself has a boast of virtue above the world."
        ),
    ],
}

LEMMAS = {
    45: [
        {"form": "μετάγνωσις", "lemma": "μετάγνωσις", "gloss": "afterthought / repentance", "lexica": "LSJ"},
        {"form": "παράκλησις", "lemma": "παράκλησις", "gloss": "appeal / consolation", "lexica": "LSJ"},
    ],
    46: [
        {"form": "κοδράντης", "lemma": "κοδράντης", "gloss": "quadrans", "lexica": "Mt 5:26"},
        {"form": "ἀντίδικος", "lemma": "ἀντίδικος", "gloss": "adversary", "lexica": "Mt 5:25"},
        {"form": "πράκτορσιν", "lemma": "πράκτωρ", "gloss": "exactors / collectors", "lexica": "LSJ"},
    ],
    47: [
        {"form": "εὐνοοῦμεν", "lemma": "εὐνοέω", "gloss": "be well disposed", "lexica": "Mt 5:25"},
        {"form": "χιτῶνα / ἱμάτιον", "lemma": "χιτών / ἱμάτιον", "gloss": "tunic / cloak", "lexica": "Mt 5:40"},
    ],
    48: [
        {"form": "εὐγνωμονεῖν", "lemma": "εὐγνωμονέω", "gloss": "be reasonable / fair", "lexica": "LSJ"},
        {"form": "ὀβολοῦ", "lemma": "ὀβολός", "gloss": "obol", "lexica": "LSJ"},
    ],
    49: [
        {"form": "ἔσχατον λεπτόν", "lemma": "λεπτόν", "gloss": "last lepton", "lexica": "Luke 12:59"},
        {"form": "ἀναπόνιπτον … μολυσμόν", "lemma": "μολυσμός", "gloss": "unwashed stain", "lexica": "LSJ"},
    ],
    50: [
        {"form": "ὑπὲρ νόμον", "lemma": "νόμος", "gloss": "beyond the law", "lexica": "patristic"},
        {"form": "εὐκατόρθωτον", "lemma": "εὐκατόρθωτος", "gloss": "easy to accomplish", "lexica": "LSJ"},
    ],
    51: [
        {"form": "ἐμβλέψας", "lemma": "ἐμβλέπω", "gloss": "look intently at", "lexica": "Mt 5:28"},
        {"form": "σαρκικῶς / ἁμαρτητικῶς", "lemma": "σαρκικός", "gloss": "fleshly / sinfully", "lexica": "patristic"},
    ],
    52: [
        {"form": "λογισμὸν τῆς ἐπιθυμίας", "lemma": "λογισμός / ἐπιθυμία", "gloss": "thought of desire", "lexica": "patristic"},
    ],
    53: [
        {"form": "ὀφθαλμὸς καὶ χεὶρ", "lemma": "ὀφθαλμός / χείρ", "gloss": "eye and hand = friend", "lexica": "allegory"},
        {"form": "προσαπολλύησθε", "lemma": "προσαπόλλυμι", "gloss": "perish together", "lexica": "LSJ"},
    ],
    54: [
        {"form": "ῥεπούδια", "lemma": "ῥεπούδιον", "gloss": "divorce certificate", "lexica": "Latin loan"},
        {"form": "εἶδος μοιχείας", "lemma": "μοιχεία", "gloss": "form of adultery", "lexica": "Mt 5:32"},
    ],
    55: [
        {"form": "οὐκ ἐπιορκήσεις", "lemma": "ἐπιορκέω", "gloss": "you shall not swear falsely", "lexica": "Mt 5:33"},
        {"form": "τὸ ναὶ καὶ τὸ οὔ", "lemma": "ναί / οὔ", "gloss": "yes and no", "lexica": "Mt 5:37"},
    ],
    56: [
        {"form": "θεοποιοῦντες", "lemma": "θεοποιέω", "gloss": "make into a god", "lexica": "patristic"},
        {"form": "ἄνω Ἰερουσαλήμ", "lemma": "Ἰερουσαλήμ", "gloss": "Jerusalem above", "lexica": "Gal 4:26"},
    ],
    57: [
        {"form": "πρὸς τὸ διδόναι", "lemma": "δίδωμι", "gloss": "toward giving", "lexica": "Mt 5:42"},
    ],
    58: [
        {"form": "ἐνεργείας … οὐκ οὐσίας", "lemma": "ἐνέργεια / οὐσία", "gloss": "activity not essence", "lexica": "patristic"},
    ],
    59: [
        {"form": "Ἀλέξανδρον τὸν χαλκέα", "lemma": "proper name", "gloss": "Alexander the smith", "lexica": "2 Tim 4:14"},
        {"form": "κατηράσατο", "lemma": "καταράομαι", "gloss": "cursed", "lexica": "LSJ"},
    ],
    60: [
        {"form": "δι' αὐτὸ τὸ καλόν", "lemma": "καλόν", "gloss": "for the good itself", "lexica": "ethics"},
        {"form": "ὑπερκόσμιον", "lemma": "ὑπερκόσμιος", "gloss": "above the world", "lexica": "patristic"},
    ],
}

CHOICES = {
    45: [{"term": "μετάγνωσις", "english": "afterthought / repentance", "rejected": ["mere regret"], "why": "Active turn that heals brother and God."}],
    46: [{"term": "πράκτορσιν", "english": "exactors", "rejected": ["bailiffs only"], "why": "Punishing angels collecting the debt."}],
    47: [{"term": "εὐνοεῖν", "english": "be well disposed", "rejected": ["be nice"], "why": "Mt 5:25 lemma with cloak/tunic."}],
    48: [{"term": "εὐγνωμονεῖν", "english": "be reasonable", "rejected": ["be grateful only"], "why": "Settle before court."}],
    49: [{"term": "ἔσχατον λεπτόν", "english": "last lepton", "rejected": ["last penny only"], "why": "Keep Gospel coin term."}],
    50: [{"term": "ὑπὲρ νόμον", "english": "beyond the law", "rejected": ["against the law"], "why": "Christ raises the command above Torah minimum."}],
    51: [{"term": "σαρκικῶς καὶ ἁμαρτητικῶς", "english": "fleshly and sinfully", "rejected": ["lustfully only"], "why": "Judgment turns on sinful mode of seeing."}],
    52: [{"term": "λογισμὸν τῆς ἐπιθυμίας", "english": "thought of desire", "rejected": ["eyeball literally"], "why": "Eye = desire’s thought to cut out."}],
    53: [{"term": "ὀφθαλμὸς καὶ χείρ", "english": "friend as eye/hand", "rejected": ["body parts only"], "why": "Allegory of harmful intimate friend."}],
    54: [{"term": "ῥεπούδια", "english": "divorce papers", "rejected": ["repudiation vaguely"], "why": "Certificate does not dissolve before God."}],
    55: [{"term": "ναὶ καὶ οὔ", "english": "yes and no", "rejected": ["simple speech only"], "why": "Oath-substitute for the saints."}],
    56: [{"term": "θεοποιοῦντες", "english": "making it a god", "rejected": ["honoring creation"], "why": "Swearing by creatures elevates them wrongly."}],
    57: [{"term": "πρὸς τὸ διδόναι", "english": "ready to give", "rejected": ["generous mood"], "why": "Orientation that joins to God."}],
    58: [{"term": "ἐνεργείας οὐκ οὐσίας", "english": "activity not essence", "rejected": ["behavior not being (jargon dump)"], "why": "Love the human; hate the act."}],
    59: [{"term": "ὡς ἐχθρὸν τοῦ εὐαγγελίου", "english": "as enemy of the gospel", "rejected": ["personal feud"], "why": "Paul’s curse is ecclesial warfare, not private hate."}],
    60: [{"term": "δι' αὐτὸ τὸ καλόν", "english": "for the good itself", "rejected": ["for virtue’s sake (loop)"], "why": "Motive above worldly boast."}],
}

ALLUSIONS = {
    45: [{"reference": "Matthew 5:23-24", "reason": "Gift at altar; first be reconciled.", "certainty": "clear"}],
    46: [
        {"reference": "Matthew 5:25-26", "reason": "Adversary; prison; last quadrans.", "certainty": "clear"},
        {"reference": "Luke 12:59", "reason": "Lepton clarification.", "certainty": "clear"},
    ],
    47: [
        {"reference": "Matthew 5:25", "reason": "Make friends with adversary.", "certainty": "clear"},
        {"reference": "Matthew 5:40", "reason": "Tunic and cloak.", "certainty": "clear"},
    ],
    48: [{"reference": "Matthew 5:25-26", "reason": "Pay the last quadrans.", "certainty": "clear"}],
    49: [
        {"reference": "Matthew 5:25-26", "reason": "Road to judge; exactors; last lepton.", "certainty": "clear"},
        {"reference": "Luke 12:58-59", "reason": "Parallel court image.", "certainty": "possible"},
    ],
    50: [{"reference": "Matthew 5:28-30", "reason": "Desire / cut off eye or hand.", "certainty": "clear"}],
    51: [{"reference": "Matthew 5:28", "reason": "Looking to lust.", "certainty": "clear"}],
    52: [{"reference": "Matthew 5:29-30", "reason": "Eye causing stumble.", "certainty": "clear"}],
    53: [{"reference": "Matthew 5:29-30", "reason": "Eye and hand cut off.", "certainty": "clear"}],
    54: [{"reference": "Matthew 5:31-32", "reason": "Certificate of divorce / adultery.", "certainty": "clear"}],
    55: [{"reference": "Matthew 5:33-37", "reason": "Oaths; yes and no.", "certainty": "clear"}],
    56: [
        {"reference": "Matthew 5:34-35", "reason": "Swear not by heaven, earth, Jerusalem.", "certainty": "clear"},
        {"reference": "Hebrews 6:13", "reason": "God swears by himself.", "certainty": "possible"},
        {"reference": "Hebrews 6:16", "reason": "Swear by the greater.", "certainty": "clear"},
    ],
    57: [{"reference": "Matthew 5:42", "reason": "Give to the one who asks.", "certainty": "clear"}],
    58: [{"reference": "Matthew 5:44", "reason": "Love your enemies.", "certainty": "clear"}],
    59: [
        {"reference": "Matthew 5:44", "reason": "Love enemies.", "certainty": "clear"},
        {"reference": "2 Timothy 4:14", "reason": "Alexander the smith.", "certainty": "clear"},
    ],
    60: [{"reference": "Matthew 6:1", "reason": "Practice righteousness not for show.", "certainty": "clear"}],
}


def main() -> None:
    eng_path = ROOT / "translations/matthew_fragments_english.json"
    english = json.loads(eng_path.read_text(encoding="utf-8"))
    english = [e for e in english if e.get("section") not in CLEAN]
    cleans = []
    for n in range(45, 61):
        src = BY[n]
        a = PASS_A[n]
        b = " ".join(PASS_B[n])
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
                "title": src["head"],
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
                "greek_clean": "translations/matthew_fragments_greek_clean_a12a15.json",
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

    (ROOT / "translations/matthew_fragments_greek_clean_a12a15.json").write_text(
        json.dumps(
            {
                "meta": {
                    "claims": [
                        "cyril-matt-frag-a12",
                        "cyril-matt-frag-a13",
                        "cyril-matt-frag-a14",
                        "cyril-matt-frag-a15",
                    ],
                    "sections": "45-60",
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
