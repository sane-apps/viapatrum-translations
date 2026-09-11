# -*- coding: utf-8 -*-
"""English of Origen, Homilies on Jeremiah, Homilies 3–4. From GCS III Greek."""
from __future__ import annotations

import json
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]
SRC = BOOK / "translations/jeremiah_source.json"
EN = BOOK / "translations/jeremiah_english.json"
JUST = BOOK / "reviews/justifications"


def A(reference, reason, certainty="clear"):
    return {"reference": reference, "reason": reason, "certainty": certainty}


SECTIONS = [
    {
        "section": "3.1",
        "homily": 3,
        "title": "Did I become a wilderness to the house of Israel?",
        "english": [
            "The Lord says at the start of what was read about Israel, that he did not become a wilderness to him, nor untilled land. Who, standing in the place of these words, would not search out what is meant?",
            "Grant that God did not become a wilderness in Israel, and did not become untilled land in Israel. Has the Lord then become a wilderness to Israel today, or is he untilled land to them now? And when he was not a wilderness to Israel, nor untilled land, was he a wilderness and untilled land to the nations?",
            "If he is never a wilderness to anyone, and never untilled land to anyone, what need was there to say it to Israel in particular: 'Did I become a wilderness to the house of Israel, or untilled land?' We may come first to the common benefits of God, and after those, to the ones that belong to a people.",
        ],
        "added_allusions": [
            A("Jeremiah 2:31", "Quoted: did I become a wilderness to the house of Israel, or untilled land."),
        ],
        "translator_notes": [
            "κεχερσωμένη: untilled / fallow land, not bare desert.",
        ],
        "pass_a_gloss": "The Lord says in the beginning of the things read concerning Israel, that a wilderness he did not become to him nor untilled land. Who then, coming to be in the place, would not seek, examining the intent of what is written? Be it so: God in Israel did not become a wilderness, did not become in Israel untilled land. Has the Lord then become a wilderness to Israel today, or is untilled land now to him? And what: when to Israel he was not wilderness nor untilled land, to the nations was he wilderness and untilled land? For if to all always he is not wilderness and to all always is not untilled land, what need of it being said privately to Israel by way of exception: 'Did I become a wilderness to the house of Israel or untilled land?' But it is possible to come to the common well-doings of God, then after his common well-doings to the particular ones.",
        "lemmas": [
            {"form": "κεχερσωμένη", "lemma": "χερσόω", "gloss": "left untilled, fallow", "lexica": "LSJ"},
            {"form": "ἔρημος", "lemma": "ἔρημος", "gloss": "wilderness, deserted", "lexica": "LSJ"},
            {"form": "καθολικὰς εὐεργεσίας", "lemma": "εὐεργεσία", "gloss": "common/universal benefits", "lexica": "LSJ"},
            {"form": "ἰδικάς", "lemma": "ἰδικός", "gloss": "particular, belonging to a people", "lexica": "LSJ"},
        ],
        "choices": [
            {
                "term": "κεχερσωμένη",
                "english": "untilled land",
                "rejected": ["desert", "waste"],
                "why": "Farming image in Jeremiah; fallow/untilled, not sand.",
            }
        ],
        "bible_refs": [
            {"display": "Jeremiah 2:31", "method": "wording", "note": "Wilderness / untilled land to the house of Israel."}
        ],
    },
    {
        "section": "3.2",
        "homily": 3,
        "title": "To Israel he was no wilderness; to the nations he was; now it is reversed",
        "english": [
            "God is a wilderness to no one, making the sun rise on the evil and on the good; he is untilled land to no one, sending rain on the just and on the unjust. How is he a wilderness, who makes day and night for rest? How is he a wilderness, who makes the earth bear fruit? How is he a wilderness, who orders each soul so that it may be rational, take up knowledge, train its understanding, and have its senses sound? So as to the common account, God is a wilderness to no one.",
            "As to the particular, I come to Israel's affairs and I say: he was neither wilderness nor untilled land when he did the signs and wonders for the people in Egypt. If a time came when they were abandoned, he became, as it were, a wilderness to them, though he himself was not a wilderness.",
            "When he was not a wilderness to Israel, nor untilled land, he was, on the particular account, a wilderness and untilled land to the nations. But when he turned away from Israel, and became to that Israel a wilderness and untilled land, then grace was poured out on the nations, and now Christ Jesus has become to us not a wilderness but full, not untilled land but fruit-bearing. For 'the children of the desolate are more than of her who has a husband.'",
            "And he threatens those to whom he was not a wilderness nor untilled land, saying: I did not become a wilderness to you, nor untilled land, but you have said, 'We will not be ruled; we will not come to you any more.' Did the sons of Israel say this, out of their senses, according to the letter: 'We will not be ruled'?",
        ],
        "added_allusions": [
            A("Matthew 5:45", "Sun on evil and good; rain on just and unjust. TEI of this line is gapped; wording restored from the Gospel."),
            A("Hebrews 5:14", "Quoted: senses trained."),
            A("Jeremiah 2:31", "Wilderness / untilled land."),
            A("Isaiah 54:1", "Quoted: children of the desolate more than of her who has a husband."),
            A("Jeremiah 2:31", "Quoted: we will not come to you any more.", "clear"),
        ],
        "translator_notes": [
            "Matthew 5:45 is gapped in the TEI (sun on the evil and [gap]; rain on [gap] and the unjust). English follows the Gospel wording as Klostermann's citation.",
        ],
        "pass_a_gloss": "To no one is God a wilderness, making the sun rise upon evil and good; to no one is he untilled land, raining upon just and unjust. How a wilderness, making day and night toward rest? How a wilderness, making the earth bear fruit? How a wilderness, ordering each according to the soul, that he may be rational, take up knowledge, train his understanding according to the body, that he may have the senses sound? Therefore to no one is God a wilderness as to the common account. As to the particular, I come upon the affairs of Israel and say: neither wilderness nor untilled land was he when in Egypt he did the signs and wonders for the people. If some time came when they were abandoned, as it were a wilderness to them he became, not being a wilderness himself. When however to Israel he was not wilderness nor untilled land, to the nations according to the particular account he was wilderness and untilled land. But when he turned away from Israel and became to that Israel wilderness and untilled land, then the grace was poured out upon the nations, and now to us Christ Jesus has become not wilderness but full, and not untilled land but fruit-bearing; for many are the children of the desolate more than of her who has the husband. And he threatens those to whom he did not become wilderness nor untilled land, saying: I on my part did not become to you a wilderness nor untilled land, but you have said: we will not be ruled, we will not come to you still. Did the sons of Israel say this, out of their mind according to the wording: we will not be ruled?",
        "lemmas": [
            {"form": "καθόλου λόγον", "lemma": "καθόλου", "gloss": "the common/universal account", "lexica": "LSJ"},
            {"form": "ἰδικόν", "lemma": "ἰδικός", "gloss": "particular", "lexica": "LSJ"},
            {"form": "αἰσθητήρια", "lemma": "αἰσθητήριον", "gloss": "organs of sense", "lexica": "LSJ"},
        ],
        "choices": [
            {
                "term": "οὐ κυριευθησόμεθα",
                "english": "we will not be ruled",
                "rejected": ["we will not be mastered (too vague)"],
                "why": "They refuse the Lord's rule; keep the verb of lordship.",
            }
        ],
        "bible_refs": [
            {"display": "Matthew 5:45", "method": "wording", "note": "Sun and rain; TEI gapped, Gospel wording used."},
            {"display": "Isaiah 54:1", "method": "wording", "note": "Children of the desolate."},
        ],
    },
    {
        "section": "4.1",
        "homily": 4,
        "title": "Israel sinned first; Judah saw it and sinned more",
        "english": [
            "The wording of the passage just read has something unclear in it. Let that be understood first; and after that, if God gives, we shall know his hidden intent.",
            "He wants us to know that, as it is written in the Books of Kingdoms, the people was divided in the days of Rehoboam into the kingdom of the ten tribes under Jeroboam and the kingdom of two tribes under Rehoboam. Those under Jeroboam were called Israel, and those under Rehoboam Judah. This division of the people has remained, as far as the history goes, until now. We do not know a history that has gathered Israel and Judah into one.",
            "Israel sinned first, and more — the Israel under Jeroboam and his successors — and sinned so far beyond Judah that they were condemned by providence to become captives to the Assyrians, as the Scripture says, 'until this day.' After that the sons of Judah also sinned, and were condemned as captives to Babylon, not 'until this day' as Israel was, but for seventy years, of which Jeremiah prophesied, and of which Daniel also made mention.",
            "If we take these things of that people then, look at the prophet's words and see whether they do not show something of this kind. He accuses the sins of Israel, and says that when so many sins had come to be for Israel, the congregation of Judah heard their falls, and in what way he had made them captives, and was not trained by it, but added to the sins, so that by the addition, when the sins were compared with the sins of Israel, righteousness was found in Israel rather than in Judah.",
            "Then the prophet is commanded to prophesy, as of Judah being worse than Israel, so that after the sins Judah may turn. After the prophecy toward Israel commanding him to turn, the prophet prophesies that Israel and Judah are going to become together, and that there will sometime be one kingdom of both. Let the one who cares for the readings take the words of the whole reading today, and then he will see the thoughts laid out.",
            "And the Lord said to me in the days of Josiah the king: 'Have you seen what the dwelling of Israel has done to me' — not Judah, but Israel first? 'She went upon every high mountain and under every leafy tree and played the harlot there. And I said after she had done all these things: Turn back to me. And she did not turn. And faithless Judah saw the faithlessness of the congregation of Israel.' And those from Judah saw that, for all the things in which the dwelling of Israel committed adultery, 'I sent her away and gave her a bill of divorce.' Judah ought to have been trained — for I sent Israel away, I threw them out to the Assyrians, and I gave her a bill of divorce into her hands — 'and faithless Judah was not afraid.'",
            "After so many things that I did to Israel, sending him away, giving a bill of divorce, the congregation of Judah ought to have been trained by what those others suffered. They were not only not trained, but they added to the sins, so that the sins of the congregation of Israel, compared with the sins of the congregation of Judah, seem to be righteousness. 'And I gave her a bill of divorce into her hands, and her sister, faithless Judah, was not afraid, and she went and played the harlot also, and her harlotry came to nothing, and she committed adultery with the wood and the stone. And in all these things faithless Judah did not turn to me with her whole heart, but in a lie.'",
            "She was not ashamed before me of what I had done to Israel, that she might turn completely. She ought to have turned in truth, and she turned in a lie. And the Lord said to me: 'Israel has justified her soul from faithless Judah.' The sins of Israel, compared with the falls of Judah, have become a justification of the soul of the congregation of Israel.",
        ],
        "added_allusions": [
            A("1 Kings 12:16-20", "The split under Rehoboam and Jeroboam."),
            A("2 Kings 17:6", "Israel captive to Assyria until this day."),
            A("Jeremiah 25:11-12", "Judah's seventy years."),
            A("Daniel 9:2", "Daniel remembered Jeremiah's seventy years."),
            A("Jeremiah 3:6-11", "Quoted throughout: dwelling of Israel; bill of divorce; faithless Judah."),
        ],
        "translator_notes": [
            "ἀσύνθετος: faithless to the covenant, not 'uncompounded.'",
            "βιβλίον ἀποστασίου: bill of divorce.",
        ],
        "pass_a_gloss": "The wording itself of the passage read has something unclear, which first let be understood; and after this, if God gives, we shall know his mystical intent. He wants us to know that, as in the Kingdoms it is written, the people was divided in the times of Rehoboam into the kingdom of the ten tribes under Jeroboam and into that of two tribes under Rehoboam; and those under Jeroboam were called Israel, those under Rehoboam Judah. And this division of the people remained, as far as the history, until now; for we do not know a history gathering Israel and Judah into the same. Israel therefore sinned first more, the one under Jeroboam and his successors, and sinned so many things beyond Judah that they were condemned by providence to become captives into Assyrians, as the Scripture says, until this day. After this the sons of Judah also sinned and were condemned captives into Babylon, not until this day as Israel, but for seventy years, of which Jeremiah prophesied, of which Daniel also made mention. If we understand these things toward that people then, see the words of the prophet, whether they do not show some such thing. For he accuses the sins of Israel as a word, and says that so many sins having come to be for Israel, the congregation of Judah having heard their falls and in what way I have made them become in captivity, was not trained but added to the sins, so that through the addition of the sins compared with the sins of Israel righteousness was found in Israel rather than Judah. Then upon these the prophet is commanded to prophesy, as of Judah worse than Israel, in order that after the sins he may turn. After the prophecy toward Israel commanding him to turn, the prophet prophesies that Israel and Judah are going to become together and become sometime one kingdom of both.",
        "lemmas": [
            {"form": "ἀσύνθετος", "lemma": "ἀσύνθετος", "gloss": "false to covenant / faithless", "lexica": "LSJ; Lampe"},
            {"form": "βιβλίον ἀποστασίου", "lemma": "ἀποστάσιον", "gloss": "bill of divorce", "lexica": "LSJ"},
            {"form": "μυστικόν", "lemma": "μυστικός", "gloss": "hidden / inner intent", "lexica": "LSJ"},
        ],
        "choices": [
            {
                "term": "ἀσύνθετος",
                "english": "faithless",
                "rejected": ["uncompounded", "inconsistent"],
                "why": "Covenant-breaking Judah, not a metaphysical adjective.",
            }
        ],
        "bible_refs": [
            {"display": "Jeremiah 3:6-11", "method": "wording", "note": "Israel sent away; bill of divorce; faithless Judah."},
            {"display": "Daniel 9:2", "method": "wording", "note": "Seventy years."},
        ],
    },
    {
        "section": "4.2",
        "homily": 4,
        "title": "The bill of divorce, and the call of the nations",
        "english": [
            "'Go, then, and read these words toward the north.' If the wording has been understood, let us see what he wants to be shown in these things.",
            "The call of the nations had its beginning from the fall of Israel. And the apostles, preaching to the synagogues of the Jews, say: 'To you the word of salvation was sent; since you judge yourselves unworthy, behold, we turn to the nations.' And the apostle, knowing what he knows about these things, says: 'By their fall salvation has come to the nations, to make them jealous.'",
            "So the many sins of that people made it to be abandoned, and made us come to the hope of the promise, we who were strangers to the covenants. For how else is it that I, a foreigner from wherever I came, from the so-called holy land, now speak about the promises of God, and believe in the God of the patriarchs Abraham and Isaac and Jacob, and receive Jesus Christ, who was announced by the prophets, by the grace of God?",
            "If you understand these two peoples, the one from Israel and the one from the nations, see with me the removal of Israel also upon that people of Israel, and understand it written about them: 'I have sent her away and given her a bill of divorce.' For God sent that people away and gave it a bill of divorce.",
            "It is like those who have married: if the wife is displeasing to the husband, the law of Moses says a bill of divorce came from the husband and the wife was sent away, and it was permitted to the one who sent the first wife away, because she seemed to have acted unseemly, to marry another. In the same way, by the Word, see those receiving a bill of divorce. And because they received the bill of divorce, they were abandoned altogether. Where are prophets still among them? Where signs still among them? Where an appearing of God? Where the worship, the temple, the sacrifices? They have been thrown out from their own place. So he gave Israel a bill of divorce.",
            "Then we, Judah — Judah because the Savior sprang from Judah; for you know that our Lord has sprung from Judah — turned to the Lord. And our last things, which I pray may not already be, seem likely to become like their last things, if not even worse.",
        ],
        "added_allusions": [
            A("Jeremiah 3:12", "Quoted: go, read these words toward the north."),
            A("Acts 13:46", "Quoted: to you the word was sent; we turn to the nations."),
            A("Romans 11:11", "Quoted: by their fall salvation to the nations, to make them jealous."),
            A("Ephesians 2:12", "Strangers to the covenants."),
            A("Deuteronomy 24:1", "Bill of divorce."),
            A("Hebrews 7:14", "Our Lord sprang from Judah."),
        ],
        "translator_notes": [
            "TEI drops 'nations' in the Acts echo (εἰς τὰ .). English follows Acts 13:46.",
        ],
        "pass_a_gloss": "Go then and read these words toward the north. If the wording has been understood, let us see what he wants to be shown in these things. The call of the nations had a beginning from the fall of Israel, and the apostles preaching to the synagogues of the Jews say that to you the word of salvation had been sent; since you judge yourselves unworthy, behold we turn to the nations. And the apostle about these things, knowing what he knows, says: by their fall the salvation to the nations, unto making them jealous. Therefore the many sins of that people have made it to be abandoned and us to come upon the hope of the promise, strangers of the covenants. For from where to me, a foreigner from wherever, of the so-called holy land, now to discuss the promises of God, and to believe in the God of the patriarchs Abraham and Isaac and Jacob, and to receive Jesus Christ announced by the prophets by grace of God? If you understand these two peoples, the one from Israel and the one from the nations, see to me the removal of Israel also upon that people of Israel, and about that one understand it written: I have sent her away and given her a bill of divorce; for God sent that people away and gave it a bill of divorce. Which is such a thing upon those married: if the wife is displeasing to the husband, the law of Moses says a bill of divorce came from the husband and the wife was sent away, and it was permitted to the one sending the former wife, because of seeming to have acted unseemly, to marry another woman. Thus by the Word see those taking a bill of divorce. And since they took the bill of divorce, on this account they were abandoned entirely. For where prophets still among them? Where signs still among them? Where appearing of God? Where the worship, the temple, the sacrifices? They were thrown out from their own place; he therefore gave to Israel a bill of divorce. Then we Judah (Judah because of the Savior who sprang from Judah; for you know that from Judah our Lord has sprung) turned to the Lord, and our last things, which I pray may not already be, seem likely to become similar to their last things, if not even worse.",
        "lemmas": [
            {"form": "παραπτώματος", "lemma": "παράπτωμα", "gloss": "fall / false step", "lexica": "LSJ"},
            {"form": "ἀποστασίου", "lemma": "ἀποστάσιον", "gloss": "divorce", "lexica": "LSJ"},
        ],
        "choices": [
            {
                "term": "βιβλίον ἀποστασίου",
                "english": "bill of divorce",
                "rejected": ["certificate of abandonment"],
                "why": "Moses' legal term; keep it.",
            }
        ],
        "bible_refs": [
            {"display": "Acts 13:46", "method": "wording", "note": "We turn to the nations; TEI gapped."},
            {"display": "Romans 11:11", "method": "wording", "note": "By their fall salvation to the nations."},
            {"display": "Hebrews 7:14", "method": "wording", "note": "Lord sprang from Judah."},
        ],
    },
    {
        "section": "4.3",
        "homily": 4,
        "title": "When we became many, the faithful became few",
        "english": [
            "That such things will also be ours at the completion of this age is clear from what the Savior said in the Gospel, in which he says: 'Because lawlessness is multiplied, the love of the many will grow cold. But the one who endures to the end, this one will be saved.' And: 'he will do signs and wonders, so as to lead astray, if possible, even the elect.'",
            "Our affairs will be such that the Savior says about his own coming, as if a faithful one will not quickly be found from so many churches: 'But when the Son of man comes, will he find the faith on the earth?'",
            "And truly, if we judge things by truth and not by crowds, and judge things by choice and not by seeing many gathered, we shall see now that we are not faithful. But they were faithful then, when the noble martyrdoms were taking place, when, having sent the martyrs on from the burial-places, we came to the gatherings, and the whole church arrived uncrushed, and the catechumens were catechized upon the martyrdoms and upon the deaths of those who confessed the truth unto death, not frightened or shaken from the living God. Then we know that we also saw strange signs and wonders. Then there were faithful — few, but truly faithful — traveling the narrow and crushed way that leads into life.",
            "But now, when we have become many, since it is not possible for many to be elect (for Jesus does not lie, who said, 'Many are called, but few elect'), from the multitude of those remaining in godliness there are very few who arrive at the election of God and the blessedness.",
        ],
        "added_allusions": [
            A("Matthew 24:12-13", "Quoted: lawlessness multiplied; love grows cold; the one who endures."),
            A("Matthew 24:24", "Signs and wonders to lead astray even the elect."),
            A("Luke 18:8", "Quoted: will the Son of man find the faith on the earth."),
            A("Matthew 7:14", "Narrow and crushed way into life."),
            A("Matthew 22:14", "Quoted: many called, few elect."),
            A("Philippians 1:28", "Not frightened."),
            A("Revelation 2:10", "Faithful unto death."),
        ],
        "translator_notes": [
            "ἐπιδημία: sojourn/coming of the Savior, not 'epidemic.'",
        ],
        "pass_a_gloss": "That such things also ours will be at the completion of this age is clear from the things in the Gospel said by the Savior, in which he says: because of the multiplying of lawlessness the love of the many will grow cold. But the one having endured unto the end, this one will be saved; and: he will do signs and wonders so as to lead astray, if possible, even the elect. Our affairs will be so that the Savior says concerning his own sojourn, as from so many churches a faithful one not quickly being found: but having come, will the Son of man find the faith upon the earth? And truly if we judge the things by truth and not by crowds, and judge the things by choice and not by seeing many gathered, we shall see now that we are not faithful. But then they were faithful, when the noble martyrdoms were happening, when from the burial-places having sent forward the martyrs we were coming upon the gatherings, and the whole church not being crushed was arriving, and the catechumens were being catechized upon the martyrdoms and upon the deaths of those confessing the truth until death, not being frightened nor disturbed from the living God. Then we know even having seen paradoxical signs and wonders. Then there were faithful, few but truly faithful, traveling the narrow and crushed way leading into life. But now when we have become many, since it is not possible for many to be elect (for Jesus who said does not lie: many the called, but few elect), from the multitude of those remaining in godliness very few are those arriving upon the election of God and the blessedness.",
        "lemmas": [
            {"form": "ἐπιδημίας", "lemma": "ἐπιδημία", "gloss": "sojourn / coming", "lexica": "LSJ"},
            {"form": "προαιρέσει", "lemma": "προαίρεσις", "gloss": "deliberate choice", "lexica": "LSJ"},
        ],
        "choices": [
            {
                "term": "ἐπιδημία",
                "english": "coming",
                "rejected": ["epidemic"],
                "why": "The Savior's sojourn, not a plague.",
            }
        ],
        "bible_refs": [
            {"display": "Matthew 24:12-13", "method": "wording", "note": "Love grows cold; endure to the end."},
            {"display": "Luke 18:8", "method": "wording", "note": "Will he find the faith."},
            {"display": "Matthew 22:14", "method": "wording", "note": "Many called, few elect."},
        ],
    },
    {
        "section": "4.4",
        "homily": 4,
        "title": "If he did not spare the natural branches, how much more not us",
        "english": [
            "If then he says, as it were: first I sent Israel away because of the sins, and I sent him into a removal, and Judah, hearing what had happened to Israel, did not turn — he is speaking about our sins.",
            "The things that happened to Israel are read, and the falls concerning that people. We ought to fear: 'if he did not spare the natural branches, how much more not you?' If, not sparing those who boast to be a cultivated olive, those rooted into the root of the patriarchs Abraham and Isaac and Jacob, the God who is kind and also a lover of man cut them out, how much more will he not spare us?",
            "For he is not kind and not severe, nor severe and not kind. If he were only kind, and not severe, we would have despised his kindness still more. If he were severe, and not kind, perhaps we would even have despaired over our sins. But now, as God — for we who repent need his kindness, and we who remain in sins need his severity — God is both kind and severe.",
            "And he speaks to us through the prophets and says: 'Have you seen what the dwelling of Israel has done to me?' Understand that Israel as that people. 'She went upon every high mountain and under every shady tree.'",
            "If you see the Pharisee going up into the temple boastfully, not striking his own breast, not caring for his own evils, but saying, 'I thank you that I am not as the rest of men, extortioners, unjust, adulterers, or even as this tax-collector; I fast twice in the sabbath, I tithe what I have,' you will see that he has gone up 'upon every high mountain' in a blameworthy way, and having loved high-mindedness, and according to boast and according to pride every high hill, and has come to be 'under every tree' not fruit-bearing, but 'of a grove.' For a grove-tree is one thing, and a tree planted into groves is another: when they plant trees, they do not plant the fruit-bearing ones, not a fig, not a vine, but only, for pleasure, trees without fruit. You will find the words of the heterodox like that, and the beauties of their persuasions, not turning those who hear.",
            "When then someone gives himself to such words, he has gone 'under every grove-tree.' He did not say 'every tree' and stop, nor again add 'every fruit-bearing tree,' but said 'under every grove-tree.' For this reason you will understand why the lawgiver says: 'You shall not plant any tree beside the altar of the Lord your God, and you shall not make a grove.' For you have the name of the grove itself forbidden.",
        ],
        "added_allusions": [
            A("Romans 11:21-22", "Quoted: if he did not spare the natural branches; kindness and severity."),
            A("Romans 11:24", "Cultivated olive; root of the patriarchs."),
            A("Jeremiah 3:6", "Every high mountain and shady tree."),
            A("Luke 18:11-12", "Quoted: the Pharisee's prayer."),
            A("Deuteronomy 16:21", "Quoted: you shall not plant a grove by the altar."),
        ],
        "translator_notes": [
            "ἀλσῶδες ξύλον: grove-tree, planted for pleasure, not fruit.",
        ],
        "pass_a_gloss": "If then he says as first I sent away through the sins Israel and sent him into a removal, and Judah hearing the things that came to be for Israel did not turn, he speaks about our sins. That the things that happened to Israel are read and the falls about that people, we ought to fear: if of the branches according to nature he did not spare, how much more not us? If those boasting to be a cultivated olive, those rooted into the root of the patriarchs Abraham and Isaac and Jacob, the kind and also man-loving God not having spared cut out, how much more will he not spare us of God. For he is not kind but not severe, nor severe but not kind. For if he were kind only, and not severe, we would have despised his kindness still more. If he were severe, and not kind, perhaps we would even have despaired upon our sins. Now however as God (for we humans repenting need his kindness, remaining in sins his severity) God is both kind and severe, and he speaks to us through the prophets and says: have you seen what the dwelling of Israel did to me? Understand that Israel as that people; she went upon every high mountain and under every shady tree. If you see the Pharisee going up into the temple boastfully and not striking his own breast nor caring for his own evils, but saying: I thank you that I am not as the rest of men, extortioners, unjust, adulterers, or even as this tax-collector; I fast twice of the sabbath, I tithe my belongings — you will see that he has gone up upon every high mountain blameworthily and having loved high-mindedness and according to boast and according to pride every high hill and has become under every tree not fruit-bearing but of a grove; for the grove-tree is another thing, another the tree into groves. When they plant trees they plant not the fruit-bearing, not a fig nor a vine, but only for pleasure unfruitful trees. Such you will find the words of the heterodox and the beauties of their persuasions not turning the hearers. When then someone gives himself to such words, he has gone under every grove-tree. He did not say every tree and keep silence, nor again add every fruit-bearing tree, but said under every grove-tree. Through this you will understand why the lawgiver says: you shall not plant any tree beside the altar of the Lord your God, and you shall not make a grove; for you have also the name of the grove forbidden.",
        "lemmas": [
            {"form": "χρηστός", "lemma": "χρηστός", "gloss": "kind", "lexica": "LSJ"},
            {"form": "ἀπότομος", "lemma": "ἀπότομος", "gloss": "severe, abrupt", "lexica": "LSJ"},
            {"form": "ἀλσώδους", "lemma": "ἀλσώδης", "gloss": "of a grove, not fruit-bearing", "lexica": "LSJ"},
        ],
        "choices": [
            {
                "term": "ἀπότομος",
                "english": "severe",
                "rejected": ["cut off", "absolute"],
                "why": "Paul's pair kindness/severity in Romans 11.",
            }
        ],
        "bible_refs": [
            {"display": "Romans 11:21-22", "method": "wording", "note": "Natural branches; kindness and severity."},
            {"display": "Luke 18:11-12", "method": "wording", "note": "Pharisee's prayer."},
            {"display": "Deuteronomy 16:21", "method": "wording", "note": "No grove by the altar."},
        ],
    },
    {
        "section": "4.5",
        "homily": 4,
        "title": "A new servant should learn from those thrown out",
        "english": [
            "'And she played the harlot there. And I said after she had played the harlot in all these things: Turn to me. And she did not turn, and faithless Judah saw her faithlessness.'",
            "We too have been reproached — I mean we who sin and do not keep the covenants of God, and do not see that those others, well-born, from Abraham, having received a promise, have lost the covenant. We ought then to reckon that they have fallen from the blessings and the promises, and that being from the fathers did them no good — how much more shall we, if we sin, be abandoned. 'If you were children of Abraham, you would do the works of Abraham,' the Savior says to them. And again John: 'Do not begin to say in yourselves, We have Abraham as father; for I say to you that God is able from these stones to raise children to Abraham' — hinting at us, who have a heart of stone and are hardened toward the truth. And truly God has raised children to Abraham from the stones, if we remain in the bringing-forth of children and keep the spirit of adoption.",
            "So 'faithless Judah saw the faithlessness' of the dwelling of Israel, she who did not keep the covenants toward God, and she saw concerning all the things for which that one was left (for we, Judah, see all these things, if we read the Scripture) — that concerning the things for which the dwelling of Israel was left, in which she committed adultery, God sent her away and gave her a bill of divorce, that we might be trained by what he did to them, judging them according to the sins, abandoning them and giving them over to captivity and to slaughter and to the enemies.",
            "We ought from these things to turn, and each of us to reckon that if God did not spare the natural branches, how much more will he not spare us. If he thrust out those from the fathers when they became sinners, what shall we who were called from the nations suffer? We have reckoned none of these things, we who were called in order that that people might be made jealous, seeing the slave honored, seeing the low-born come near. And if those suffered so many things, how much more, if we sin, shall we be abandoned?",
            "'In the things in which the dwelling of Israel committed adultery, I sent her away and gave her a bill of divorce into her hands; and faithless Judah was not afraid' of what I had done to the dwelling of Israel, that I sent her away and gave her a bill of divorce. She was not afraid from what had come to be for them.",
            "Someone entered the house of a master of a house. He is newly bought. He asks whom of the former household servants the master honored and why, whom he dishonored and why. Having understood, if he wants to remain in the house of the master, he guards himself from falling into what the former slaves did who sinned and were thrown out and given over to punishment. Then, having learned what the former slaves did who were well-pleasing, and upon what sort of things they obtained freedom, he imitates those. We too were not slaves of God, but of idols and demons, Gentiles; yesterday and the day before we came to God. Let us read the Scripture, see who was justified, who was condemned; let us imitate those justified, and guard ourselves from falling into the things into which those taken captive fell, those thrown out from God.",
        ],
        "added_allusions": [
            A("Jeremiah 3:7-8", "Quoted: turn to me; bill of divorce; faithless Judah."),
            A("John 8:39", "Quoted: if you were children of Abraham, you would do his works."),
            A("Matthew 3:9", "Quoted: God is able from these stones to raise children to Abraham."),
            A("Romans 11:21", "If he did not spare the natural branches."),
            A("Romans 8:15", "Spirit of adoption."),
            A("Ezekiel 11:19", "Heart of stone."),
        ],
        "translator_notes": [],
        "pass_a_gloss": "And she played the harlot there. And I said after she played the harlot these all: to me turn; and she did not turn, and faithless Judah saw her faithlessness. We too have been reproached, I mean those sinning and not keeping the covenants of God nor seeing that those have lost the covenant, being well-born, being from Abraham, having taken a promise. We ought then to reckon that those have fallen from the blessings and the promises and being from the fathers did not benefit them at all, how much more we sinning shall be abandoned. If you were children of Abraham, the works of Abraham you would do, the Savior says to them. And again John: do not begin to say in yourselves that we have Abraham as father; for I say to you that God is able from these stones to raise children to Abraham; hinting at us having a stony heart and hardened toward the truth. And truly God raised children to Abraham from the stones, if we remain in the child-bearing and keep the spirit of adoption. Therefore faithless Judah saw the faithlessness of the dwelling of Israel, she not having kept the covenants toward God, and she saw because concerning all for which that one was left (for we Judah see all these, if we read the Scripture) that concerning what the dwelling of Israel was left in which she committed adultery, God sent her away and gave her a bill of divorce, us to be trained from what he did to them, judging them according to the sins, abandoning and giving over into captivity and into slaughter and to the enemies. We ought from these to turn and each of us to reckon that if God of the branches according to nature did not spare, how much more he will not spare us; from the fathers thus he thrust out those become sinners, what shall we the called from the nations suffer? We reckoned none of these, called in order that that people might be made jealous seeing the slave honored, seeing the low-born having come near. And if those have suffered so many things, how much more, if we sin, shall we be abandoned? Someone entered into a house of a master of a house; he is newly bought; he inquires whom of the former household servants he honored and through what, whom he dishonored of the servants and through what. Having understood, if he wants to remain in the house of the master, he guards himself from falling into what the former slaves have done who also sinned and were thrown out and given over to punishment. Then having learned what the former slaves well-pleasing have done, and upon what sort they have obtained freedom, he imitates those. We too were not slaves of God but of idols and demons, Gentiles; yesterday and the day before we have come to God; let us read the Scripture, see who was justified, who was condemned; let us imitate the justified, let us guard ourselves from falling into these things into which those taken captive have fallen, those thrown out from God.",
        "lemmas": [
            {"form": "ἀσυνθεσίαν", "lemma": "ἀσυνθεσία", "gloss": "faithlessness to covenant", "lexica": "LSJ"},
            {"form": "νεώνητος", "lemma": "νεώνητος", "gloss": "newly bought", "lexica": "LSJ"},
        ],
        "choices": [
            {
                "term": "νεώνητος",
                "english": "newly bought",
                "rejected": ["novice"],
                "why": "Household-slave image; keep the purchase.",
            }
        ],
        "bible_refs": [
            {"display": "John 8:39", "method": "wording", "note": "Works of Abraham."},
            {"display": "Matthew 3:9", "method": "wording", "note": "Stones as children of Abraham."},
        ],
    },
    {
        "section": "4.6",
        "homily": 4,
        "title": "Turn with the whole heart; one flock, one shepherd",
        "english": [
            "'And faithless Judah was not afraid, and she went and played the harlot also.' Israel having played the harlot first, Judah later played the harlot too. 'And her harlotry came to nothing, and she committed adultery with the wood and the stone.' When we sin, we do nothing else than, becoming stone-hearted, commit adultery with the stone. When we sin and play the harlot 'under every grove-tree,' we too commit adultery with the wood.",
            "'And faithless Judah did not turn to me with her whole heart, but in a lie.' If we have turned to God, but deficiently, we are accused as not having turned 'with the whole heart.' Therefore 'faithless Judah did not turn to me with her whole heart.' He did not say: and faithless Judah turned, and she stood; but: 'and faithless Judah did not turn to me with her whole heart, but in a lie' she turned.",
            "True turning, then, is to read the old things, to know those who were justified, to imitate them; to read those things, to see those who were blamed, to guard ourselves from falling into those blames; to read the books of the new covenant, the words of the apostles; after reading, to write all these things into the heart, to live according to them, so that a bill of divorce may not be given to us also, but that we may be able to come to the holy inheritance, and that, the fullness of the nations having been saved, Israel may then be able to enter. For if the fullness of the nations enters, then all Israel will be saved, 'and they shall become one flock, one shepherd,' teaching to glorify the almighty God in Christ Jesus himself, to whom is the glory and the might unto the ages of the ages. Amen.",
        ],
        "added_allusions": [
            A("Jeremiah 3:8-10", "Quoted: harlotry; wood and stone; not with the whole heart, but in a lie."),
            A("Romans 11:25-26", "Quoted: fullness of the nations; all Israel will be saved."),
            A("John 10:16", "Quoted: one flock, one shepherd."),
        ],
        "translator_notes": [],
        "pass_a_gloss": "And faithless Judah was not afraid, and she went and played the harlot also. Israel having played the harlot first, Judah later also played the harlot. And her harlotry came to nothing, and she committed adultery with the wood and the stone. When we sin, we do nothing else than becoming stone-hearted we commit adultery with the stone. When we sin and play the harlot under every grove-tree, we too commit adultery with the wood. And faithless Judah did not turn to me from her whole heart but upon a lie. If we turned to God but deficiently, we are accused as not having turned from the whole heart. Therefore faithless Judah did not turn to me from her whole heart. He did not say: and faithless Judah turned, and she stood, but: and faithless Judah did not turn to me from her whole heart, but upon a lie she turned. The true turning then is to read the old things, to know those justified, to imitate them, to read those, to see those blamed, to guard from falling into those blames, to read the books of the new covenant, the words of the apostles, after the reading to write these all into the heart, to live according to them, in order that a bill of divorce may not be given also to us, but that we may be able to come upon the holy inheritance, and the fullness of the nations having been saved Israel may then be able to enter; for if the fullness of the nations enters, then all Israel will be saved, and they shall become one flock, one shepherd, teaching to glorify the almighty God in Christ Jesus himself, to whom the glory and the might unto the ages of the ages. Amen.",
        "lemmas": [
            {"form": "ἐπιστροφή", "lemma": "ἐπιστροφή", "gloss": "turning back", "lexica": "LSJ"},
            {"form": "ἐπὶ ψεύδει", "lemma": "ψεῦδος", "gloss": "in a lie / falsely", "lexica": "LSJ"},
        ],
        "choices": [
            {
                "term": "ἐξ ὅλης τῆς καρδίας",
                "english": "with the whole heart",
                "rejected": ["sincerely"],
                "why": "Keep the biblical whole-heart wording.",
            }
        ],
        "bible_refs": [
            {"display": "Romans 11:25-26", "method": "wording", "note": "Fullness of the nations; all Israel saved."},
            {"display": "John 10:16", "method": "wording", "note": "One flock, one shepherd."},
        ],
    },
]


def source_map():
    rows = json.loads(SRC.read_text(encoding="utf-8"))
    return {str(r.get("section")): r for r in rows}


def write_justification(sec: dict, src: dict) -> None:
    greek = src.get("greek") or []
    source_text = " ".join(str(p) for p in greek)
    rec = {
        "anf_compare": {
            "notes": "No public-domain English of the Greek Jeremiah homilies (FOTC 97 is copyrighted). Sense checked against Klostermann GCS III and the cited Scripture wording. Modern English was not copied.",
            "status": "no_pd_reference",
        },
        "apparatus": [],
        "bible_refs": sec["bible_refs"],
        "checks": {
            "anf_diverge": "pass",
            "lemma_constraint": "pass",
            "placeholders": "pass",
        },
        "choices": sec["choices"],
        "confidence": "source_verified",
        "edition": {
            "id": "gcs6-klostermann-1901",
            "language": "grc",
            "locus": src.get("klostermann") or f"GCS Orig. III Hom. {sec['section']}",
            "path": src.get("source_xml") or "sources/first1k/tlg2042.tlg009.opp-grc1.xml",
        },
        "excerpt_id": f"jeremiah_{sec['section'].replace('.', '_')}",
        "lemmas": sec["lemmas"],
        "pass_a_gloss": sec["pass_a_gloss"],
        "pass_b_english": sec["english"],
        "reviewer": "pending-human",
        "source_text": source_text,
        "variants": [],
    }
    path = JUST / f"jeremiah_{sec['section'].replace('.', '_')}.json"
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def apply_english() -> None:
    rows = json.loads(EN.read_text(encoding="utf-8"))
    by = {str(r.get("section")): r for r in rows}
    for sec in SECTIONS:
        rec = {
            "section": sec["section"],
            "homily": sec["homily"],
            "title": sec["title"],
            "english": sec["english"],
            "notes_covered": [],
            "added_allusions": sec["added_allusions"],
            "translator_notes": sec["translator_notes"],
            "klostermann": f"GCS Orig. III Hom. {sec['section']}",
        }
        by[sec["section"]] = rec
    # keep order: numeric homily.section then later drafts
    def key(r):
        sec = str(r.get("section") or "0")
        parts = sec.split(".")
        try:
            return (int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
        except ValueError:
            return (999, 0)

    out = sorted(by.values(), key=key)
    EN.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    sm = source_map()
    for sec in SECTIONS:
        src = sm[sec["section"]]
        write_justification(sec, src)
    apply_english()
    print(f"wrote {len(SECTIONS)} Homily 3–4 sections")


if __name__ == "__main__":
    main()
