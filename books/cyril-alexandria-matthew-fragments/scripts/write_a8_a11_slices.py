#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass A≠B for cyril-matt-frag-a8..a11 (entries 29–44)."""
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
    if n <= 32:
        return "cyril-matt-frag-a8"
    if n <= 36:
        return "cyril-matt-frag-a9"
    if n <= 40:
        return "cyril-matt-frag-a10"
    return "cyril-matt-frag-a11"


CLEAN = {n: clean(BY[n]["greek"][0]) for n in range(29, 45)}

PASS_A = {
    29: (
        "Toward love-of-glory passion wanting to drag the Satan the Christ did not say to him "
        "eat, but make a sign. And this he was doing, not in order that he be benefited, but in "
        "order that, which I said, into empty-glory he drag him; which knowing the Christ did "
        "not obey him. With this aim also to the Pharisees wanting from him a sign to see he "
        "did not nod; for not with undoubting heart they were approaching him as God, but as "
        "a human they were testing. Let be therefore this unfallen for the holy ones a rule "
        "toward unbelievers or testing-ones the not to love-glory upon nothing useful."
    ),
    30: (
        "Of teaching it is the withdrawing of Jesus. Clearly the word teaches, that it is not "
        "necessary someone onto the school to come, unless first he be baptized and obtain "
        "holy spirit and fast wholly and conquer every kind of temptation as the type of the "
        "truth in Christ began and through Christ happens."
    ),
    31: (
        "Not through cowardice did he withdraw, but us through what he was doing teaching to "
        "withdraw to the persecuting. And he withdraws from the Judea onto the nations, showing "
        "that not only whenever against him the God the Jews insult he stands-away from them, "
        "but also when against the holy prophets they sin. And light great is Christ the Lord "
        "of us and the brightness of the evangelical proclamation, not indeed the law, which "
        "to a lamp had been compared. Wherefore always in the tent a lamp was burning because "
        "of the short of the of the law gleam as-far-as only the Jewish boundaries being-able "
        "to send-out the own light. Therefore the gentiles in darkness were as not even the "
        "lamp-like having light."
    ),
    32: (
        "In some the repent is not lying. And if the same things the savior to John says, one "
        "the having-sent both God. And perhaps John on-the-one-hand as preparing for God a "
        "prepared [people] first says repent, but Jesus having-received prepared things no "
        "longer needing repentance does not say repent. And not heralding-against law and "
        "prophets, but John having-fulfilled the old he begins to herald the new, himself "
        "beginning having-become of it. Wherefore upon John it has not been written the he "
        "began; for end he was. And that the one in desert heralds, but the other in people. "
        "And the kingdom of the heavens is not in place, but in disposition; for within us it "
        "is. And see if John on-the-one-hand heralds approaching kingdom of heavens, but king "
        "Christ which he will hand-over to the God and father."
    ),
    33: (
        "And if someone asks, what the difference of disease and weakness, we answer, that "
        "weakness on-the-one-hand is the temporary irregularity of the body, but disease "
        "disproportion of the in the body elements. And it is necessary also this to note, that "
        "the inheritance of the tribe of Zebulun and Naphtali as-far-as Sidon gentile city was "
        "stretched and that mixed with the nations Jews were dwelling already. And is "
        "interpreted Zebulun on-the-one-hand good-journey and blessing, but Naphtali a stem "
        "loosened that-is a plant stretching. And have become these the into Christ having-"
        "believed; for well-journeying going of the divine blessing they were deemed-worthy "
        "and with the good all they were broadened the formerly in Galilee being, which "
        "rolling-down is interpreted, that-is the rolling-down against the pits of destruction."
    ),
    34: (
        "Peacemaker is the the to-others appearing battle of the scriptures showing-forth "
        "agreement, of olds toward news, of legal toward prophetic, of evangelical toward "
        "evangelical. Wherefore having-imitated the son of the God son he will be called in "
        "deed the spirit of the adoption having-received."
    ),
    35: (
        "And peacemakers not only the making-friends the enemies, but also the the anger and "
        "the bad desire taming, living both rightly in deed and word through faith unfailing, "
        "and also the re-teaching the unbelievers and leading toward the faith as the enemies "
        "of the God making-friends to him. Blessed the such as having-imitated the son of the "
        "God; for sons they will be called of immortality having-shared or they will co-reign "
        "with the Christ in the second of him presence."
    ),
    36: (
        "Peacemakers are also the the unbelievers persuading to believe as the formerly enemies "
        "of the God peacemaking to him. Peacemakers are called also the persuading the "
        "unbelievers to believe the God."
    ),
    37: (
        "Salt he calls the prudence, of which full is the apostolic word, which having-been-"
        "sown in the our souls the of the wisdom to us settles word, which through the tasty "
        "and graceful to this has been compared; for which manner without salt neither bread "
        "nor relish edible, thus without the apostolic understanding and teaching every soul "
        "both foolish and tasteless and not pleasant is beside the God."
    ),
    38: (
        "And the a city cannot; the upon the faith established as upon a mountain high ought "
        "not secretly or with cowardice to speak the word."
    ),
    39: (
        "And light but they according to participation having-become when you live no longer "
        "yourselves, but lives in you the light, the Christ, being-able through word also whole "
        "to illuminate the world."
    ),
    40: (
        "Instead of the fleshly worship introduced the Lord the in spirit and truth; and "
        "perhaps what things not even fleshly the Jews were doing, these also now spiritually "
        "the of Christ disciples do. Wherefore he says: one iota or one horn will not pass from "
        "the law, until all happen. Clearly not all the Jews did, or even if they did, they "
        "ceased of the doing no longer being-allowed to do them, partly on-the-one-hand through "
        "the fear of the kings, partly and the having-been-destroyed the temple, in which alone "
        "it was necessary the sacrifices to be completed."
    ),
    41: (
        "God-fighter, he says, will be called the the least of the in the law commandments "
        "setting-aside. Wherefore also he is set-aside beside God as to him opposing and "
        "counter-legislating."
    ),
    42: (
        "The setting-aside one of the of the law commandments is set-aside beside the God as "
        "God-fighter and counter-legislating to the God. And now from the evangelical law he "
        "receives the punishment, which law of old was not the having-defined. Wherefore also "
        "consistently says the Christ, that I did not come to destroy the law, but to fulfill. "
        "For what there was lacking, here he filled-up, such-as in the law it was said: from "
        "face of gray you shall rise and if you see the beast of your enemy having-fallen under "
        "the load, raise it with him. These if someone transgressed, there was not punishment "
        "defined by the law. Which filling-up the Christ says, that in the kingdom of the God "
        "the such will be set-at-nought. This therefore he calls least commandment, upon which "
        "there was not from transgression being-brought punishment."
    ),
    43: (
        "Through this also the of Moses law the split-hoof accepts, in order that through "
        "riddles us it teach through both to journey through both word and deed. And I think "
        "also the split-hoof in the law this to signify, the through word and deed to journey "
        "us and neither to act unreasonably nor word to have of deed apart. And if something "
        "from the such to be wants isolated, let deed be then and not word; for word unbridled "
        "against cliffs pushed often the possessing, but deed never."
    ),
    44: (
        "The to say if you offer the gift of you and following this makes-clear, that a manner "
        "of salvation and escape of punishment for the sinning invented the God the change-of-"
        "mind, and the of the having-been-grieved healing overturning to be of punishment he "
        "says. Since the not loving the brother of him, does not love the Lord, reasonably the "
        "being in grief of the brother he does not accept as not truly to him approaching."
    ),
}

PASS_B = {
    29: [
        (
            "Wanting to drag Christ into the passion of love of glory, Satan did not say to him, "
            "“Eat,” but, “Make a sign.” He did this not to gain any help himself, but — as I said "
            "— to pull Christ into empty glory. Knowing that, Christ did not obey him."
        ),
        (
            "With the same aim he also refused the Pharisees when they wanted to see a sign from "
            "him. They were not coming to him with an undoubting heart as to God; they were "
            "testing him as a man. So let this stand for the saints as an unfailing rule toward "
            "unbelievers or testers: do not love glory in anything useless."
        ),
    ],
    30: [
        (
            "Jesus’ withdrawal is itself a teaching. The word clearly teaches that no one should "
            "come to the school unless he is first baptized, receives the Holy Spirit, fasts "
            "completely, and conquers every kind of temptation — as the type of the truth began "
            "in Christ and happens through Christ."
        ),
    ],
    31: [
        (
            "He did not withdraw through cowardice, but by what he did he teaches us to withdraw "
            "from persecutors. He withdraws from Judea to the nations, showing that he stands "
            "away from the Jews not only when they insult God himself, but also when they sin "
            "against the holy prophets."
        ),
        (
            "Christ our Lord is a great light, and so is the brightness of the gospel "
            "proclamation — not the law, which had been compared to a lamp. That is why a lamp "
            "always burned in the tent: the law’s gleam was short, able to send its own light "
            "only as far as the Jewish boundaries. So the gentiles were in darkness, as those "
            "who did not even have lamp-light."
        ),
    ],
    32: [
        (
            "In some copies “repent” is not present. If the Savior says the same things as John, "
            "one God sent them both. Perhaps John, as one preparing a people made ready for God, "
            "first says “repent,” while Jesus, receiving what was already prepared and no longer "
            "needing repentance, does not say “repent.”"
        ),
        (
            "He is not heralding against the law and the prophets. John having finished the old, "
            "he begins to herald the new, himself becoming its beginning. That is why “he began” "
            "is not written of John — for John was an end. One heralds in the desert, the other "
            "among the people."
        ),
        (
            "The kingdom of the heavens is not in a place but in a disposition, for it is within "
            "us. See also: John heralds a kingdom of heavens that is near, while Christ is the "
            "king who will hand it over to God and Father."
        ),
    ],
    33: [
        (
            "If someone asks the difference between disease and weakness, we answer: weakness is "
            "the body’s temporary irregularity; disease is disproportion among the elements in "
            "the body."
        ),
        (
            "Note also that the inheritance of the tribe of Zebulun and Naphtali stretched as far "
            "as the gentile city Sidon, and that Jews were already living mixed with the nations. "
            "Zebulun is interpreted “good journey” and “blessing”; Naphtali, “a loosened stem,” "
            "that is, a plant stretched out."
        ),
        (
            "Those who believed in Christ became these things. Journeying well, they were counted "
            "worthy of the divine blessing and were broadened in every good — those who were "
            "formerly in Galilee, which is interpreted “rolling down,” that is, those rolling "
            "down into the pits of destruction."
        ),
    ],
    34: [
        (
            "A peacemaker is the one who shows that the battle others see in the scriptures is "
            "agreement: old with new, legal with prophetic, gospel with gospel. Having imitated "
            "the Son of God, he will be called a son, receiving in deed the spirit of adoption."
        ),
    ],
    35: [
        (
            "Peacemakers are not only those who reconcile enemies, but also those who tame anger "
            "and base desire, living rightly in deed and word through unfailing faith — and those "
            "who re-teach unbelievers and lead them to faith, making God’s enemies friends to him."
        ),
        (
            "Blessed are such people, as those who have imitated the Son of God. They will be "
            "called sons, sharing immortality, or they will reign with Christ at his second coming."
        ),
    ],
    36: [
        (
            "Peacemakers are also those who persuade unbelievers to believe, making God’s former "
            "enemies at peace with him. They are called peacemakers who persuade unbelievers to "
            "believe God."
        ),
    ],
    37: [
        (
            "He calls salt prudence, of which the apostolic word is full. Sown in our souls, it "
            "settles the word of wisdom in us, compared to salt because it is savory and graceful. "
            "Just as without salt neither bread nor relish is edible, so without apostolic "
            "understanding and teaching every soul is foolish, tasteless, and not pleasant to God."
        ),
    ],
    38: [
        (
            "“A city cannot [be hidden]”: those established on the faith as on a high mountain "
            "ought not to speak the word secretly or with cowardice."
        ),
    ],
    39: [
        (
            "Having become light by participation, when you live it is no longer you who live, "
            "but the light — Christ — lives in you, able through the word to illuminate the whole "
            "world."
        ),
    ],
    40: [
        (
            "In place of fleshly worship the Lord introduced worship “in spirit and truth.” "
            "Perhaps what the Jews were not even doing fleshly, Christ’s disciples now do "
            "spiritually. That is why he says one iota or one horn will not pass from the law "
            "until all happens."
        ),
        (
            "Clearly the Jews did not do all of it — or if they did, they stopped, no longer "
            "allowed to do those things, partly through fear of kings, and partly because the "
            "temple had been destroyed, the only place where the sacrifices had to be completed."
        ),
    ],
    41: [
        (
            "Whoever sets aside the least of the commandments in the law will be called a "
            "God-fighter, he says. That is why he is also set aside by God, as one who opposes "
            "him and legislates against him."
        ),
    ],
    42: [
        (
            "Whoever sets aside one commandment of the law is set aside by God as a God-fighter "
            "and as one who legislates against God. And now from the gospel law he receives the "
            "punishment that the old law had not defined. So Christ says consistently that he "
            "did not come to destroy the law but to fulfill it."
        ),
        (
            "What was lacking there, he filled up here. The law said, “You shall rise before a "
            "gray head,” and, “If you see your enemy’s beast fallen under its load, raise it with "
            "him.” If someone transgressed these, the law had defined no punishment. Filling that "
            "up, Christ says such a person will be set at nought in the kingdom of God. That is "
            "what he calls the least commandment: one on which no penalty was brought for "
            "transgression."
        ),
    ],
    43: [
        (
            "That is also why Moses’ law accepts the split hoof: that through riddles it may "
            "teach us to journey by both — by word and by deed. I think the split hoof in the "
            "law signifies this: that we journey by word and deed, neither acting without reason "
            "nor holding a word apart from deed."
        ),
        (
            "If something from such things wants to stand alone, let it be deed and not word. An "
            "unbridled word has often pushed those who have it over cliffs; deed never has."
        ),
    ],
    44: [
        (
            "Saying, “If you offer your gift,” and what follows, makes this clear: God invented "
            "a way of salvation and an escape from punishment for sinners — a change of mind — "
            "and he says healing the one who was grieved will overturn punishment."
        ),
        (
            "Since the one who does not love his brother does not love the Lord, he reasonably "
            "does not accept the one who approaches while his brother is in grief, as one not "
            "truly coming to him."
        ),
    ],
}

LEMMAS = {
    29: [
        {"form": "φιλοδοξίας", "lemma": "φιλοδοξία", "gloss": "love of glory", "lexica": "LSJ"},
        {"form": "κενοδοξίαν", "lemma": "κενοδοξία", "gloss": "empty glory", "lexica": "LSJ"},
        {"form": "κανών", "lemma": "κανών", "gloss": "rule / canon", "lexica": "patristic"},
    ],
    30: [
        {"form": "διδασκαλεῖον", "lemma": "διδασκαλεῖον", "gloss": "school", "lexica": "LSJ"},
        {"form": "τύπος τῆς ἀληθείας", "lemma": "τύπος", "gloss": "type of the truth", "lexica": "patristic"},
    ],
    31: [
        {"form": "λύχνῳ", "lemma": "λύχνος", "gloss": "lamp", "lexica": "biblical"},
        {"form": "λυχνιαῖον φῶς", "lemma": "λύχνος", "gloss": "lamp-light", "lexica": "patristic"},
    ],
    32: [
        {"form": "μετανοεῖτε", "lemma": "μετανοέω", "gloss": "repent", "lexica": "Mt 3–4"},
        {"form": "ἐντὸς ἡμῶν", "lemma": "ἐντός", "gloss": "within us", "lexica": "Luke 17:21"},
    ],
    33: [
        {"form": "μαλακία / νόσος", "lemma": "μαλακία / νόσος", "gloss": "weakness / disease", "lexica": "Mt 4:23"},
        {"form": "Ζαβουλών / Νεφθαλείμ", "lemma": "proper names", "gloss": "etymologies of the tribes", "lexica": "patristic"},
    ],
    34: [
        {"form": "εἰρηνοποιός", "lemma": "εἰρηνοποιός", "gloss": "peacemaker", "lexica": "Mt 5:9"},
        {"form": "υἱοθεσίας", "lemma": "υἱοθεσία", "gloss": "adoption", "lexica": "NT"},
    ],
    35: [
        {"form": "φιλοποιοῦντες", "lemma": "φιλοποιέω", "gloss": "make friends / reconcile", "lexica": "LSJ"},
        {"form": "συμβασιλεύσουσι", "lemma": "συμβασιλεύω", "gloss": "reign with", "lexica": "NT"},
    ],
    36: [
        {"form": "μεταπείθοντες", "lemma": "μεταπείθω", "gloss": "persuade to change", "lexica": "LSJ"},
    ],
    37: [
        {"form": "ἅλας", "lemma": "ἅλας", "gloss": "salt", "lexica": "Mt 5:13"},
        {"form": "φρόνησιν", "lemma": "φρόνησις", "gloss": "prudence", "lexica": "LSJ"},
        {"form": "ἄνοστος", "lemma": "ἄνοστος", "gloss": "tasteless", "lexica": "LSJ"},
    ],
    38: [
        {"form": "πόλις", "lemma": "πόλις", "gloss": "city", "lexica": "Mt 5:14"},
        {"form": "δειλίας", "lemma": "δειλία", "gloss": "cowardice", "lexica": "LSJ"},
    ],
    39: [
        {"form": "κατὰ μετοχήν", "lemma": "μετοχή", "gloss": "by participation", "lexica": "patristic"},
        {"form": "φωτίζειν", "lemma": "φωτίζω", "gloss": "illuminate", "lexica": "LSJ"},
    ],
    40: [
        {"form": "ἰῶτα / κεραία", "lemma": "ἰῶτα / κεραία", "gloss": "iota / horn-stroke", "lexica": "Mt 5:18"},
        {"form": "ἐν πνεύματι καὶ ἀληθείᾳ", "lemma": "πνεῦμα / ἀλήθεια", "gloss": "in spirit and truth", "lexica": "John 4:23"},
    ],
    41: [
        {"form": "θεομάχος", "lemma": "θεομάχος", "gloss": "God-fighter", "lexica": "patristic"},
        {"form": "ἀντινομοθετῶν", "lemma": "ἀντινομοθετέω", "gloss": "legislate against", "lexica": "patristic"},
    ],
    42: [
        {"form": "πληρῶσαι", "lemma": "πληρόω", "gloss": "fulfill", "lexica": "Mt 5:17"},
        {"form": "ἐλαχίστην ἐντολήν", "lemma": "ἐλάχιστος", "gloss": "least commandment", "lexica": "Mt 5:19"},
    ],
    43: [
        {"form": "διχηλοῦν", "lemma": "διχηλέω", "gloss": "split-hoofed", "lexica": "Lev dietary law"},
        {"form": "ἀχαλίνωτος λόγος", "lemma": "ἀχαλίνωτος", "gloss": "unbridled word", "lexica": "LSJ"},
    ],
    44: [
        {"form": "μετάγνωσιν", "lemma": "μετάγνωσις", "gloss": "change of mind / repentance", "lexica": "LSJ"},
        {"form": "θεραπείαν", "lemma": "θεραπεία", "gloss": "healing / tending", "lexica": "LSJ"},
    ],
}

CHOICES = {
    29: [{"term": "φιλοδοξίας / κενοδοξίαν", "english": "love of glory / empty glory", "rejected": ["ambition (vague)"], "why": "Keep the vain-glory bait explicit."}],
    30: [{"term": "διδασκαλεῖον", "english": "school", "rejected": ["classroom (modern)"], "why": "Teaching office / school of Christ."}],
    31: [{"term": "λυχνιαῖον φῶς", "english": "lamp-light", "rejected": ["candlight"], "why": "Law as tent-lamp vs gospel sun."}],
    32: [{"term": "ἐν διαθέσει", "english": "in a disposition", "rejected": ["in an attitude only"], "why": "Kingdom as inward state, not locale."}],
    33: [{"term": "μαλακία vs νόσος", "english": "weakness vs disease", "rejected": ["sickness for both"], "why": "Cyril’s medical distinction."}],
    34: [{"term": "εἰρηνοποιός", "english": "peacemaker", "rejected": ["peacekeeper"], "why": "Beatitude term; scriptural harmony."}],
    35: [{"term": "φιλοποιοῦντες", "english": "making friends / reconciling", "rejected": ["being friendly"], "why": "Active reconciliation to God."}],
    36: [{"term": "μεταπείθοντες", "english": "persuading to change / believe", "rejected": ["convincing casually"], "why": "Evangelistic persuasion."}],
    37: [{"term": "φρόνησιν", "english": "prudence", "rejected": ["intelligence only"], "why": "Moral-intellectual savor of apostolic teaching."}],
    38: [{"term": "μετὰ δειλίας", "english": "with cowardice", "rejected": ["timidly (soft)"], "why": "Fearful secrecy vs public word."}],
    39: [{"term": "κατὰ μετοχήν", "english": "by participation", "rejected": ["by sharing vaguely"], "why": "Christological participation language."}],
    40: [{"term": "ἰῶτα / κεραία", "english": "iota / horn", "rejected": ["jot / tittle only"], "why": "Keep Greek letter-stroke terms."}],
    41: [{"term": "θεομάχος", "english": "God-fighter", "rejected": ["enemy of God (soft)"], "why": "Strong Cyril label for antinomian repeal."}],
    42: [{"term": "ἐλαχίστην ἐντολήν", "english": "least commandment", "rejected": ["smallest rule"], "why": "Mt 5:19 lemma Cyril defines by missing penalty."}],
    43: [{"term": "διχηλοῦν", "english": "split hoof", "rejected": ["cloven foot only"], "why": "Levitical riddle for word+deed."}],
    44: [{"term": "μετάγνωσιν", "english": "change of mind", "rejected": ["regret only"], "why": "Salvific repentance that heals the brother."}],
}

ALLUSIONS = {
    29: [{"reference": "Matthew 4:3-4", "reason": "Stones-to-bread / sign temptation.", "certainty": "clear"}],
    30: [{"reference": "Matthew 4:12", "reason": "Jesus withdraws after John’s arrest.", "certainty": "clear"}],
    31: [
        {"reference": "Matthew 4:12-16", "reason": "Withdrawal to Galilee / great light.", "certainty": "clear"},
        {"reference": "Isaiah 9:1-2", "reason": "Light to Zebulun/Naphtali.", "certainty": "clear"},
    ],
    32: [
        {"reference": "Matthew 4:17", "reason": "Repent / kingdom near.", "certainty": "clear"},
        {"reference": "Luke 17:21", "reason": "Kingdom within.", "certainty": "clear"},
        {"reference": "1 Corinthians 15:24", "reason": "Hand over the kingdom to the Father.", "certainty": "possible"},
    ],
    33: [{"reference": "Matthew 4:23", "reason": "Disease and weakness lemma.", "certainty": "clear"}],
    34: [{"reference": "Matthew 5:9", "reason": "Blessed are the peacemakers.", "certainty": "clear"}],
    35: [{"reference": "Matthew 5:9", "reason": "Peacemakers / sons of God.", "certainty": "clear"}],
    36: [{"reference": "Matthew 5:9", "reason": "Peacemakers.", "certainty": "clear"}],
    37: [{"reference": "Matthew 5:13", "reason": "Salt of the earth.", "certainty": "clear"}],
    38: [{"reference": "Matthew 5:14", "reason": "City on a hill.", "certainty": "clear"}],
    39: [{"reference": "Matthew 5:14", "reason": "You are the light.", "certainty": "clear"}, {"reference": "Galatians 2:20", "reason": "Christ lives in you.", "certainty": "possible"}],
    40: [
        {"reference": "Matthew 5:18", "reason": "Iota and horn will not pass.", "certainty": "clear"},
        {"reference": "John 4:23", "reason": "Worship in spirit and truth.", "certainty": "clear"},
    ],
    41: [{"reference": "Matthew 5:19", "reason": "Least commandment.", "certainty": "clear"}],
    42: [
        {"reference": "Matthew 5:17-19", "reason": "Fulfill the law; least commandment.", "certainty": "clear"},
        {"reference": "Leviticus 19:32", "reason": "Rise before gray head.", "certainty": "possible"},
        {"reference": "Exodus 23:5", "reason": "Raise enemy’s beast.", "certainty": "possible"},
    ],
    43: [{"reference": "Leviticus 11:3", "reason": "Split hoof clean animals.", "certainty": "clear"}],
    44: [
        {"reference": "Matthew 5:23-24", "reason": "Leave gift; first be reconciled.", "certainty": "clear"},
        {"reference": "1 John 4:20", "reason": "Not loving brother / not loving God.", "certainty": "possible"},
    ],
}


def main() -> None:
    eng_path = ROOT / "translations/matthew_fragments_english.json"
    english = json.loads(eng_path.read_text(encoding="utf-8"))
    english = [e for e in english if e.get("section") not in CLEAN]
    cleans = []
    for n in range(29, 45):
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
                "greek_clean": "translations/matthew_fragments_greek_clean_a8a11.json",
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

    (ROOT / "translations/matthew_fragments_greek_clean_a8a11.json").write_text(
        json.dumps(
            {
                "meta": {
                    "claims": [
                        "cyril-matt-frag-a8",
                        "cyril-matt-frag-a9",
                        "cyril-matt-frag-a10",
                        "cyril-matt-frag-a11",
                    ],
                    "sections": "29-44",
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
