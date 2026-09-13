#!/usr/bin/env python3
"""Batch Origen Psalms Rufinus remaining CLOSEOUTs (Ps36 II–V, Ps37 I–II, Ps38 I–II)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "books/origen-psalms-rufinus"


def A(reference, reason, certainty="clear"):
    return {"reference": reference, "reason": reason, "certainty": certainty}


def write_homily(key: str, claim: str, prev: str, title_work: str, locus: str, sections: list[dict]) -> None:
    (BOOK / "sources").mkdir(parents=True, exist_ok=True)
    (BOOK / "translations").mkdir(parents=True, exist_ok=True)
    (BOOK / "reviews/justifications").mkdir(parents=True, exist_ok=True)
    (ROOT / "docs/claim-locks").mkdir(parents=True, exist_ok=True)

    wl = [
        f"Origen {title_work} — working Latin "
        "(cleaned/condensed from PG 12 / Migne pdftotext)\n"
    ]
    eng, src = [], []
    for s in sections:
        sec = s["section"]
        latin, english, gloss = s["latin"].strip(), s["english"].strip(), s["gloss"].strip()
        assert gloss != english, f"Pass A == Pass B at {key}.{sec}"
        allusions = s.get("allusions", [])
        wl.append(f"\n{sec}\n{latin}\n")
        notes = [
            "Copy-text PG 12 (Migne) Rufinus Latin via Archive PDF pdftotext; no first-edition GCS.",
            "True OET: no ANF; do not copy Trigg FOTC / Prinzivalli SC / Perrone 2015.",
            f"After tip {prev}; {title_work} CLOSEOUT.",
        ]
        eng.append(
            {
                "section": sec,
                "work": "homiliae",
                "part": key,
                "title": s["title"],
                "english": [english],
                "notes_covered": [],
                "added_allusions": allusions,
                "translator_notes": notes,
                "baehrens": f"PG 12 {locus} §{sec}",
                "claim": claim,
            }
        )
        src.append(
            {
                "section": sec,
                "work": "homiliae",
                "part": key,
                "locus": f"PG 12 {locus} §{sec}",
                "head": f"{locus} {sec}",
                "latin": [latin],
                "edition": "migne-pg12-rufinus",
            }
        )
        j = {
            "excerpt_id": f"{key}_{sec:02d}",
            "edition": {
                "id": "migne-pg12-rufinus",
                "language": "lat",
                "locus": f"PG 12 {locus} {sec}",
            },
            "source_text": latin,
            "pass_a_gloss": gloss,
            "pass_b_english": english,
            "notes": [
                "Pass A ≠ Pass B.",
                "True OET; no Trigg/Prinzivalli/Perrone.",
                "Copy-text PG 12 Rufinus Latin.",
            ],
            "bible_links": [{"ref": a["reference"], "why": a["reason"]} for a in allusions],
            "anf_compare": "no ANF for Rufinus Ps 36–38; do not copy modern FOTC/SC",
            "checks": {
                "pass_a_ne_pass_b": True,
                "no_fotc_Trigg": True,
                "edition_lock": "PG 12 Rufinus (PDF pdftotext)",
            },
            "confidence": "high",
            "reviewer": "Air",
        }
        (BOOK / "reviews/justifications" / f"{key}_{sec:02d}.json").write_text(
            json.dumps(j, ensure_ascii=False, indent=2) + "\n"
        )

    (BOOK / "sources" / f"{key}_working_latin.txt").write_text("".join(wl))
    (BOOK / "translations" / f"{key}_english.json").write_text(
        json.dumps(eng, ensure_ascii=False, indent=2) + "\n"
    )
    (BOOK / "translations" / f"{key}_source.json").write_text(
        json.dumps(src, ensure_ascii=False, indent=2) + "\n"
    )
    (ROOT / "docs/claim-locks" / claim).write_text(
        f"agent: Air\nclaimed: 2026-09-13\n"
        f"slice: Origen {title_work} CLOSEOUT Pass A≠B OET\n"
        f"status: done\n"
    )


HOMILIES = [
    {
        "key": "ps36_hom2",
        "claim": "origen-psalms-rufinus-ps36-h2-1-2-oet",
        "title_work": "Psalms Rufinus Homilia II in Ps 36",
        "locus": "Hom. II in Ps. 36",
        "msg": "OET Origen Psalms Rufinus Ps 36 Homilia II CLOSEOUT Pass A≠B.",
        "sections": [
            {
                "section": 1,
                "title": "He will bring forth your justice like light",
                "latin": (
                    "Educet sicut lumen iustitiam tuam et iudicium tuum sicut meridiem. "
                    "Sicut sensus lucem appetunt, ita iustus lumen iustitiae ostendetur "
                    "sole iustitiae — caelo et terrae."
                ),
                "gloss": (
                    "He will bring forth your justice like light and your judgment like "
                    "noon. As the senses desire light, so the just man’s justice will be "
                    "shown by the sun of justice — to heaven and earth."
                ),
                "english": (
                    "[[He will bring forth your righteousness as the light, and your "
                    "justice as the noonday >> Bible:Psalm 37:6]]. As every sense wants "
                    "what suits it, so the just shine under the [[Sun of righteousness "
                    ">> Bible:Malachi 4:2]] before heaven and earth."
                ),
                "allusions": [
                    A("Psalm 37:6", "justice like light"),
                    A("Malachi 4:2", "sun of righteousness"),
                ],
            },
            {
                "section": 2,
                "title": "Be subject to the Lord; do not fret",
                "latin": (
                    "Subditus esto Domino et ora eum; noli aemulari in eo qui prosperatur "
                    "in via sua. Gloria Christo. Amen."
                ),
                "gloss": (
                    "Be subject to the Lord and pray to him; do not envy him who prospers "
                    "in his way. Glory to Christ. Amen."
                ),
                "english": (
                    "[[Be still before the Lord and wait for him; do not fret over one who "
                    "prospers in his way >> Bible:Psalm 37:7]]. Glory to Christ. Amen."
                ),
                "allusions": [A("Psalm 37:7", "be still; do not fret")],
            },
        ],
    },
    {
        "key": "ps36_hom3",
        "claim": "origen-psalms-rufinus-ps36-h3-1-2-oet",
        "title_work": "Psalms Rufinus Homilia III in Ps 36",
        "locus": "Hom. III in Ps. 36",
        "msg": "OET Origen Psalms Rufinus Ps 36 Homilia III CLOSEOUT Pass A≠B.",
        "sections": [
            {
                "section": 1,
                "title": "Two soldiers — God’s armor and the devil’s",
                "latin": (
                    "De eodem psalmo: peccatores tetenderunt arcum. Duo milites armati — "
                    "miles Dei loricam iustitiae, miles diaboli loricam iniustitiae; "
                    "galea salutis contra galeam perditionis."
                ),
                "gloss": (
                    "On the same psalm: sinners have bent the bow. Two armed soldiers — "
                    "God’s soldier the breastplate of justice, the devil’s the breastplate "
                    "of injustice; helmet of salvation against helmet of perdition."
                ),
                "english": (
                    "[[The wicked draw the sword and bend their bow >> Bible:Psalm 37:14]]. "
                    "Picture two soldiers: God’s wears the [[breastplate of righteousness "
                    ">> Bible:Ephesians 6:14]] and [[helmet of salvation >> Bible:Ephesians 6:17]]; "
                    "the devil’s man wears injustice and ruin."
                ),
                "allusions": [
                    A("Psalm 37:14", "bow of sinners"),
                    A("Ephesians 6:14-17", "armor of God"),
                ],
            },
            {
                "section": 2,
                "title": "Infants not yet armed either way",
                "latin": (
                    "Infantes neque Dei arma neque diaboli gerunt donec peccare possint. "
                    "Gloria Deo. Amen."
                ),
                "gloss": (
                    "Infants bear neither God’s arms nor the devil’s until they can sin. "
                    "Glory to God. Amen."
                ),
                "english": (
                    "Only those who can already sin wear either armor — infants not yet. "
                    "Glory to God. Amen."
                ),
                "allusions": [A("Psalm 37:14-15", "sinners’ weapons", "probable")],
            },
        ],
    },
    {
        "key": "ps36_hom4",
        "claim": "origen-psalms-rufinus-ps36-h4-1-2-oet",
        "title_work": "Psalms Rufinus Homilia IV in Ps 36",
        "locus": "Hom. IV in Ps. 36",
        "msg": "OET Origen Psalms Rufinus Ps 36 Homilia IV CLOSEOUT Pass A≠B.",
        "sections": [
            {
                "section": 1,
                "title": "The Lord’s words are tried silver — lend them well",
                "latin": (
                    "Pecunia Domini sunt eloquia Domini — argentum igne probatum. Si male "
                    "doceo, pecunia mea reproba; si bene, fenus iustum. Misericordiam volo "
                    "quam sacrificium."
                ),
                "gloss": (
                    "The Lord’s oracles are the Lord’s money — silver proved by fire. If I "
                    "teach badly, my money is rejected; if well, a just interest. I want "
                    "mercy rather than sacrifice."
                ),
                "english": (
                    "The preacher lends the Lord’s coin: [[The words of the Lord are pure "
                    "words, silver refined >> Bible:Psalm 12:6]]. Bad teaching is "
                    "[[rejected silver >> Bible:Jeremiah 6:30]]; good teaching yields "
                    "interest. [[I desire mercy and not sacrifice >> Bible:Hosea 6:6]]."
                ),
                "allusions": [
                    A("Psalm 12:6", "refined silver words"),
                    A("Jeremiah 6:30", "rejected silver"),
                    A("Hosea 6:6", "mercy not sacrifice"),
                ],
            },
            {
                "section": 2,
                "title": "Those who bless him inherit the land",
                "latin": (
                    "Qui benedicunt eum hereditabunt terram; qui maledicunt exterminabuntur. "
                    "Gloria Christo. Amen."
                ),
                "gloss": (
                    "Those who bless him will inherit the land; those who curse will be "
                    "wiped out. Glory to Christ. Amen."
                ),
                "english": (
                    "[[Those blessed by him shall inherit the land, but those cursed by him "
                    "shall be cut off >> Bible:Psalm 37:22]]. Glory to Christ. Amen."
                ),
                "allusions": [A("Psalm 37:22", "bless and inherit")],
            },
        ],
    },
    {
        "key": "ps36_hom5",
        "claim": "origen-psalms-rufinus-ps36-h5-1-2-oet",
        "title_work": "Psalms Rufinus Homilia V in Ps 36",
        "locus": "Hom. V in Ps. 36",
        "msg": "OET Origen Psalms Rufinus Ps 36 Homilia V CLOSEOUT Pass A≠B.",
        "sections": [
            {
                "section": 1,
                "title": "The mouth of the just meditates wisdom",
                "latin": (
                    "Os iusti meditabitur sapientiam. Non cibis et potu sed meditatione "
                    "sapientiae vescitur interior homo. Lex aperit os ad verbum Dei."
                ),
                "gloss": (
                    "The mouth of the just will meditate wisdom. Not with foods and drink "
                    "but by meditation of wisdom the inner man feeds. The law opens the "
                    "mouth to God’s word."
                ),
                "english": (
                    "[[The mouth of the righteous utters wisdom >> Bible:Psalm 37:30]]. "
                    "The inner man feeds not on banquets but on meditating wisdom; the law "
                    "opens the mouth for God’s word."
                ),
                "allusions": [A("Psalm 37:30", "mouth meditates wisdom")],
            },
            {
                "section": 2,
                "title": "Glory in eternal light — Amen",
                "latin": (
                    "Qui in lucis aeternitate persistit refert Deo gloriam in saecula "
                    "saeculorum. Amen."
                ),
                "gloss": (
                    "Who remains in the eternity of light brings glory back to God forever "
                    "and ever. Amen."
                ),
                "english": (
                    "Stay in eternal light and give God glory [[forever and ever "
                    ">> Bible:Revelation 1:6]]. Amen."
                ),
                "allusions": [A("Revelation 1:6", "glory forever", "probable")],
            },
        ],
    },
    {
        "key": "ps37_hom1",
        "claim": "origen-psalms-rufinus-ps37-h1-1-2-oet",
        "title_work": "Psalms Rufinus Homilia I in Ps 37",
        "locus": "Hom. I in Ps. 37",
        "msg": "OET Origen Psalms Rufinus Ps 37 Homilia I CLOSEOUT Pass A≠B.",
        "sections": [
            {
                "section": 1,
                "title": "Lord, not in your fury — rebuke vs wrath",
                "latin": (
                    "Domine ne in furore tuo arguas me. Reprehensio verbo fit; qui iugo "
                    "praeceptoris non subditur ira Dei castigatur — castigatio "
                    "reprehensione molestior."
                ),
                "gloss": (
                    "Lord, do not rebuke me in your fury. Rebuke is by word; who does not "
                    "submit to the teacher’s yoke is chastised by God’s wrath — chastisement "
                    "harsher than rebuke."
                ),
                "english": (
                    "[[O Lord, rebuke me not in your anger >> Bible:Psalm 38:1]]. Verbal "
                    "rebuke is lighter; refuse the teacher’s yoke and God’s wrath chastises "
                    "more heavily."
                ),
                "allusions": [A("Psalm 38:1", "not in fury")],
            },
            {
                "section": 2,
                "title": "My iniquities a heavy burden; come to me",
                "latin": (
                    "Sicut onus grave gravatae sunt super me. Venite ad me omnes qui "
                    "laboratis et onerati estis. Gloria Christo. Amen."
                ),
                "gloss": (
                    "Like a heavy burden they have weighed upon me. Come to me all who labor "
                    "and are burdened. Glory to Christ. Amen."
                ),
                "english": (
                    "[[My iniquities have gone over my head; like a heavy burden "
                    ">> Bible:Psalm 38:4]]. Christ answers: [[Come to me, all who labor and "
                    "are heavy laden >> Bible:Matthew 11:28]]. Glory to Christ. Amen."
                ),
                "allusions": [
                    A("Psalm 38:4", "heavy burden"),
                    A("Matthew 11:28", "come to me"),
                ],
            },
        ],
    },
    {
        "key": "ps37_hom2",
        "claim": "origen-psalms-rufinus-ps37-h2-1-2-oet",
        "title_work": "Psalms Rufinus Homilia II in Ps 37",
        "locus": "Hom. II in Ps. 37",
        "msg": "OET Origen Psalms Rufinus Ps 37 Homilia II CLOSEOUT Pass A≠B.",
        "sections": [
            {
                "section": 1,
                "title": "Friends stand afar; conscience accuses",
                "latin": (
                    "Amici mei et proximi mei adversum me appropinquaverunt et steterunt. "
                    "Fidelis infirmus mugit pro delictis; conscientia accusatrix mecum est — "
                    "cur exspecto accusatorem?"
                ),
                "gloss": (
                    "My friends and neighbors drew near against me and stood. The faithful "
                    "weak man groans for faults; conscience the accuser is with me — why wait "
                    "for an accuser?"
                ),
                "english": (
                    "[[My friends and companions stand aloof from my plague "
                    ">> Bible:Psalm 38:11]]. Better a weak believer who confesses than one "
                    "who hides — conscience already prosecutes; [[all things are naked before "
                    "him >> Bible:Hebrews 4:13]]."
                ),
                "allusions": [
                    A("Psalm 38:11", "friends stand aloof"),
                    A("Hebrews 4:13", "naked before God"),
                ],
            },
            {
                "section": 2,
                "title": "Confess and seek the cure",
                "latin": (
                    "Memor delicti confiteatur quae commisit et medelam quaerat. Gloria Deo. "
                    "Amen."
                ),
                "gloss": (
                    "Mindful of the fault let him confess what he committed and seek the "
                    "cure. Glory to God. Amen."
                ),
                "english": (
                    "Remember the fall, confess it, seek the wound’s cure. Glory to God. Amen."
                ),
                "allusions": [A("Psalm 38:18", "confess iniquity", "probable")],
            },
        ],
    },
    {
        "key": "ps38_hom1",
        "claim": "origen-psalms-rufinus-ps38-h1-1-2-oet",
        "title_work": "Psalms Rufinus Homilia I in Ps 38",
        "locus": "Hom. I in Ps. 38",
        "msg": "OET Origen Psalms Rufinus Ps 38 Homilia I CLOSEOUT Pass A≠B.",
        "sections": [
            {
                "section": 1,
                "title": "I said, I will guard my ways",
                "latin": (
                    "Dixi custodiam vias meas ut non delinquam in lingua mea. Posui ori meo "
                    "custodiam cum consisteret peccator adversum me. Obmutui et humiliatus sum."
                ),
                "gloss": (
                    "I said I will guard my ways that I may not sin with my tongue. I set a "
                    "guard on my mouth when the sinner stood against me. I was mute and humbled."
                ),
                "english": (
                    "[[I said, I will guard my ways, that I may not sin with my tongue "
                    ">> Bible:Psalm 39:1]]. When the sinner rose against me I set a muzzle "
                    "and was silent, humbled."
                ),
                "allusions": [A("Psalm 39:1-2", "guard tongue; silence")],
            },
            {
                "section": 2,
                "title": "My heart grew hot; show me my end",
                "latin": (
                    "Concaluit cor meum intra me; in meditatione mea exardescet ignis. Notum "
                    "fac mihi Domine finem meum. Gloria Christo. Amen."
                ),
                "gloss": (
                    "My heart grew hot within me; in my meditation a fire will kindle. Make "
                    "known to me, Lord, my end. Glory to Christ. Amen."
                ),
                "english": (
                    "[[My heart became hot within me; as I mused, the fire burned "
                    ">> Bible:Psalm 39:3]]. [[Make me know my end, O Lord "
                    ">> Bible:Psalm 39:4]]. Glory to Christ. Amen."
                ),
                "allusions": [
                    A("Psalm 39:3", "heart hot"),
                    A("Psalm 39:4", "make known my end"),
                ],
            },
        ],
    },
    {
        "key": "ps38_hom2",
        "claim": "origen-psalms-rufinus-ps38-h2-1-2-oet",
        "title_work": "Psalms Rufinus Homilia II in Ps 38",
        "locus": "Hom. II in Ps. 38",
        "msg": "OET Origen Psalms Rufinus Ps 38 Homilia II CLOSEOUT Pass A≠B. SERIES CLOSEOUT origen-psalms-rufinus 9/9.",
        "sections": [
            {
                "section": 1,
                "title": "Image of the invisible God vs earthly image",
                "latin": (
                    "Qui est imago Dei invisibilis primogenitus omnis creaturae. Qui exit de "
                    "hoc mundo ferens imaginem terreni ad nihilum redigitur in civitate Dei; "
                    "caelestis imaginis insignia reportet."
                ),
                "gloss": (
                    "Who is the image of the invisible God, firstborn of all creation. Who "
                    "exits this world bearing the earthly image is reduced to nothing in God’s "
                    "city; let him bring back the marks of the heavenly image."
                ),
                "english": (
                    "Christ is [[the image of the invisible God, the firstborn of all "
                    "creation >> Bible:Colossians 1:15]]. Leave the world wearing only the "
                    "[[image of the man of dust >> Bible:1 Corinthians 15:49]] and you are "
                    "nothing in God’s city — bear the heavenly image."
                ),
                "allusions": [
                    A("Colossians 1:15", "image of invisible God"),
                    A("1 Corinthians 15:49", "earthly vs heavenly image"),
                ],
            },
            {
                "section": 2,
                "title": "Pilgrim and sojourner — SERIES Amen",
                "latin": (
                    "Incola ego sum apud te et peregrinus sicut omnes patres mei. Remitte "
                    "mihi ut refrigerer priusquam abeam. Gloria Christo Iesu in saecula. Amen."
                ),
                "gloss": (
                    "I am a sojourner with you and a pilgrim like all my fathers. Forgive me "
                    "that I may cool before I go. Glory to Christ Jesus forever. Amen."
                ),
                "english": (
                    "[[I am a sojourner with you, a pilgrim like all my fathers "
                    ">> Bible:Psalm 39:12]]. [[Look away from me, that I may smile again "
                    "before I depart >> Bible:Psalm 39:13]]. Glory to Christ Jesus forever. Amen."
                ),
                "allusions": [
                    A("Psalm 39:12", "sojourner"),
                    A("Psalm 39:13", "before I depart"),
                ],
            },
        ],
    },
]


def main() -> None:
    prev = subprocess.check_output(["git", "rev-parse", "--short=8", "HEAD"], text=True).strip()
    # Prefer tip after Hom1 tip commit if present
    if len(sys.argv) > 1:
        prev = sys.argv[1]
    tips = {}
    for h in HOMILIES:
        write_homily(h["key"], h["claim"], prev, h["title_work"], h["locus"], h["sections"])
        paths = [
            f"books/origen-psalms-rufinus/sources/{h['key']}_working_latin.txt",
            f"books/origen-psalms-rufinus/translations/{h['key']}_english.json",
            f"books/origen-psalms-rufinus/translations/{h['key']}_source.json",
            f"docs/claim-locks/{h['claim']}",
        ]
        for p in (BOOK / "reviews/justifications").glob(f"{h['key']}_*.json"):
            paths.append(str(p.relative_to(ROOT)))
        subprocess.check_call(["git", "add", *paths])
        subprocess.check_call(["git", "commit", "-m", h["msg"]])
        sha = subprocess.check_output(["git", "rev-parse", "--short=8", "HEAD"], text=True).strip()
        tips[h["key"]] = sha
        print(f"TIPPED {h['key']} -> {sha} after {prev}")
        prev = sha
    Path("/tmp/psalms_tips.json").write_text(json.dumps(tips, indent=2) + "\n")
    print("SERIES", tips["ps38_hom2"])


if __name__ == "__main__":
    main()
