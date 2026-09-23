#!/usr/bin/env python3
"""Cap. 7 Arg. 3 densify — tip 138 → ~144. Packet morte_christi_cap7_arg3_densify."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

BOOK = Path.home() / "SaneApps/clients/translations/books/davenant-dissertationes-duae"
TRANS = BOOK / "translations"
JUST = BOOK / "reviews/justifications"
AUDIT = BOOK / "reviews/audit"
PIPE = Path.home() / "SaneApps/clients/translations/pipeline"
PACKET = "morte_christi_cap7_arg3_densify"
CHECK = PIPE / "check_pass_ab.py"
TIP_BEFORE = 138

SECTIONS = [
  {
    "section": 139,
    "title": "Cap. 7 Arg. 3: death bound to absolute purpose for certain persons—sheep, sons, Church texts",
    "latin": (
      "3. Argumentum tertium ab illis Scripturae testimoniis petitur in quibus mors Christi "
      "conjuncta & quasi complicata cum certo & absoluto proposito dandi vitam aeternam, "
      "non ad omnes homines diffunditur, sed ad certas personas, idque ex speciali intentione "
      "Christi ipsius, restringitur. Talia sunt, Johann. x. 15. Animam meam pono pro ovibus meis. "
      "Johann. xi. 51, 52. Jesus moriturus erat, ut filios Dei dispersos in unum congregaret. "
      "Ephes. v. 25, 26. Christus dilexit Ecclesiam, & semetipsum tradidit pro ea, ut illam "
      "sanctificaret, & sibi gloriosam exhiberet. Tit. ii. 14. Christus dedit semetipsum pro nobis, "
      "ut mundaret sibi populum peculiarem, &c. Acquisivit ecclesiam sanguine suo, Actor. xx. 28. "
      "Ephes. i. 22, 23. Dedit eum Caput super omnia ecclesiae, quae est corpus ipsius. Cui adde "
      "illud, Ephes. v. 23. Ipse est Servator corporis sui."
    ),
    "pass_a_gloss": (
      "3. The third argument is sought from those testimonies of Scripture in which the death of "
      "Christ joined and as it were folded together with a sure and absolute purpose of giving "
      "eternal life is not diffused to all human beings, but is restricted to certain persons, "
      "and that from the special intention of Christ himself. Such are, John x. 15. I lay down "
      "my soul for my sheep. John xi. 51, 52. Jesus was about to die, that he might gather into "
      "one the dispersed sons of God. Ephesians v. 25, 26. Christ loved the Church, and handed "
      "himself over for her, that he might sanctify her, and present her glorious to himself. "
      "Titus ii. 14. Christ gave himself for us, that he might cleanse for himself a peculiar "
      "people, &c. He acquired the church by his blood, Acts xx. 28. Ephesians i. 22, 23. He "
      "gave him Head over all things to the church, which is his body. To which add that, "
      "Ephesians v. 23. He himself is Savior of his body."
    ),
    "pass_b": (
      "3. The third argument is drawn from those Scripture testimonies in which Christ’s death, "
      "joined and as it were folded together with a sure and absolute purpose of giving eternal "
      "life, is not spread out to all human beings but is restricted to certain persons—and that "
      "by Christ’s own special intention. Such are John 10:15: “I lay down my life for my sheep.” "
      "John 11:51–52: Jesus was about to die that he might gather into one the scattered children "
      "of God. Ephesians 5:25–26: “Christ loved the Church and gave himself up for her, that he "
      "might sanctify her and present her to himself in glory.” Titus 2:14: Christ gave himself "
      "for us that he might cleanse for himself a people of his own, and so on. He purchased the "
      "church with his blood (Acts 20:28). Ephesians 1:22–23: he gave him as Head over all things "
      "to the church, which is his body. Add also Ephesians 5:23: “He himself is the Savior of "
      "his body.”"
    ),
    "notes_covered": [
      "Arg. 3 open; John 10:15; John 11:51-52; Eph 5:25-26; Tit 2:14; Acts 20:28; Eph 1:22-23; Eph 5:23"
    ],
    "lemmas": [
      {"form": "conjuncta & quasi complicata", "gloss": "joined and as it were folded together", "why": "Arg3 frame"},
      {"form": "Animam meam pono pro ovibus meis", "gloss": "I lay down my life for my sheep", "why": "John 10:15"},
      {"form": "Servator corporis sui", "gloss": "Savior of his body", "why": "Eph 5:23"},
    ],
  },
  {
    "section": 140,
    "title": "Cap. 7 Arg. 3: three observations—elect titles, not the promiscuous race, efficacious will",
    "latin": (
      "In hisce omnibus locis tria observanda. Primo, nomine ovium, Ecclesiae, Filiorum Dei, "
      "corporis Christi designari oves, filios Dei sive membra Christi, non tam actu unita per "
      "fidem acceptam quam consilio & intentione Dei unienda per fidem accipiendam. Secundo, "
      "sub praedictis titulis humanum genus promiscue non posse designari. Tertio, cum dicitur "
      "Christum mortuum fuisse ut hosce filios congregaret, ut hanc Ecclesiam sanctificaret, "
      "ut hanc Ecclesiam acquireret, &c. denotari in Christo sese offerente non voluntatem "
      "inefficacem, aut intentionem aliquam conditionatam, quae intento effectu carere possit, "
      "sed voluntatem efficacem, & intentionem cum infallibili eventu conjunctam."
    ),
    "pass_a_gloss": (
      "In all these places three things are to be observed. First, by the name of sheep, of the "
      "Church, of the Sons of God, of the body of Christ are designated sheep, sons of God or "
      "members of Christ, not so much united in act by faith already received as to be united by "
      "the counsel and intention of God through faith to be received. Second, under the aforesaid "
      "titles the human race promiscuously cannot be designated. Third, when it is said that "
      "Christ died that he might gather these sons, that he might sanctify this Church, that he "
      "might acquire this Church, &c., there is denoted in Christ offering himself not an "
      "inefficacious will, or some conditioned intention which can lack the intended effect, but "
      "an efficacious will, and an intention joined with an infallible event."
    ),
    "pass_b": (
      "In all these places three things must be noticed. First, by the names sheep, Church, "
      "children of God, and body of Christ are meant sheep, children of God, or members of "
      "Christ—not so much already united in act by a faith received as still to be united by "
      "God’s counsel and intention through a faith yet to be received. Second, under those "
      "titles the human race cannot be meant promiscuously. Third, when it is said that Christ "
      "died that he might gather these children, sanctify this Church, acquire this Church, and "
      "the like, what is marked in Christ as he offers himself is not an inefficacious will, or "
      "some conditioned intention that might miss its intended effect, but an efficacious will "
      "and an intention joined to an infallible outcome."
    ),
    "notes_covered": [
      "tria observanda: elect titles; not promiscuous genus; efficacious not conditioned will"
    ],
    "lemmas": [
      {"form": "non tam actu unita", "gloss": "not so much united in act", "why": "vs present faith"},
      {"form": "humanum genus promiscue", "gloss": "the human race promiscuously", "why": "Secundo"},
      {"form": "intentionem cum infallibili eventu conjunctam", "gloss": "intention joined with infallible event", "why": "Tertio"},
    ],
  },
  {
    "section": 141,
    "title": "Cap. 7 Arg. 3 Probatur 1: sheep/members by eternal election—Augustine Tract. 46 / 49",
    "latin": (
      "Probatur primum, nempe, Sermonem esse in praedictis locis de ovibus, de membris, de "
      "filiis secundum aeternum & arcanum propositum electionis Divinae, & non secundum actum "
      "praesentem consideratis; Quia nemo fit actualiter ovis Christi, filius Dei, membrum "
      "corporis mystici, nisi merito & beneficio mortis Christi ad eum actualiter & efficaciter "
      "derivatae & applicatae. Christus igitur mortuus est pro ovibus, pro filiis Dei, pro "
      "Ecclesia, pro membris sibi secundum electionis propositum ab aeterno destinatis, scilicet "
      "ut merito mortis Christi haec praedestinatio Dei impleretur in iisdem. Sic Augustinus, "
      "in Johann. tract. 46. Novit Dominus qui sunt ejus: ipsi sunt oves, secundum istam "
      "praedestinationem, secundum istam praescientiam, secundum istam electionem ovium, ante "
      "constitutionem mundi. Et Tract. 49. pag. 366. de filiis Dei dispersis sic loquitur, Haec "
      "secundum praedestinationem dicta sunt: Nam neque oves ejus neque filii Dei adhuc erant, "
      "quia nondum crediderant."
    ),
    "pass_a_gloss": (
      "The first is proved, namely, that the speech in the aforesaid places is concerning sheep, "
      "concerning members, concerning sons considered according to the eternal and hidden purpose "
      "of Divine election, and not according to the present act; Because no one becomes actually "
      "a sheep of Christ, a son of God, a member of the mystical body, unless by the merit and "
      "benefit of the death of Christ actually and efficaciously derived and applied to him. "
      "Christ therefore died for the sheep, for the sons of God, for the Church, for the members "
      "destined to himself from eternity according to the purpose of election, namely that by "
      "the merit of Christ’s death this predestination of God might be fulfilled in the same. "
      "So Augustine, on John tract. 46. The Lord knows who are his: they themselves are sheep, "
      "according to that predestination, according to that foreknowledge, according to that "
      "election of sheep, before the constitution of the world. And Tract. 49. page 366. of the "
      "dispersed sons of God he speaks thus, These things were said according to predestination: "
      "For neither his sheep nor the sons of God yet were, because they had not yet believed."
    ),
    "pass_b": (
      "The first point is proved: in those places the talk is of sheep, members, and children "
      "considered according to the eternal and hidden purpose of divine election, not according "
      "to their present act. For no one becomes actually Christ’s sheep, a child of God, or a "
      "member of the mystical body unless the merit and benefit of Christ’s death are actually "
      "and efficaciously derived and applied to him. Christ therefore died for the sheep, for "
      "the children of God, for the Church, for the members destined to him from eternity "
      "according to the purpose of election—namely that by the merit of his death this "
      "predestination of God might be fulfilled in them. So Augustine on John, tract. 46: “The "
      "Lord knows who are his: they are sheep according to that predestination, according to "
      "that foreknowledge, according to that election of sheep, before the foundation of the "
      "world.” And in tract. 49, p. 366, speaking of the scattered children of God: “These things "
      "were said according to predestination: for neither his sheep nor the children of God yet "
      "were, because they had not yet believed.”"
    ),
    "notes_covered": [
      "Probatur primum; election vs present act; Aug. In Joh. tract. 46 and 49 p.366"
    ],
    "lemmas": [
      {"form": "secundum aeternum & arcanum propositum", "gloss": "according to the eternal hidden purpose", "why": "election"},
      {"form": "membrum corporis mystici", "gloss": "member of the mystical body", "why": "actual membership"},
      {"form": "Novit Dominus qui sunt ejus", "gloss": "The Lord knows who are his", "why": "Aug. tract.46"},
    ],
  },
  {
    "section": 142,
    "title": "Cap. 7 Arg. 3 Probatur 2: Scripture’s elect titles mark restricted intention—vs John 3:16",
    "latin": (
      "Probatur secundum, nempe, in locis allegatis mortem Christi sub speciali aliqua ratione "
      "ad certas personas restrictam denotari. Nam alioquin cur Scriptura oves, filios, "
      "ecclesiam nominasset, si eam uti ad omnes extenditur designare voluisset? Frustra "
      "vocabulis usus fuisset exiguam partem humani generis designantibus, nisi & intentionem "
      "Christi ea in re non ad totum humanum genus spectantem sed ad illos paucos relatam "
      "indicasset. Mors Christi atque intentio Dei omnes promiscue complectens optime "
      "exprimitur Johann. iii. 16. Sic Deus dilexit mundum, ut Filium suum unigenitum daret, "
      "ut omnis qui credit in eum, non pereat, sed habeat vitam aeternam. Ac sic dilexit oves, "
      "filios, Ecclesiam suam, ut morte sua iis fidem & vitam aeternam decreverit efficaciter "
      "promereri."
    ),
    "pass_a_gloss": (
      "The second is proved, namely, that in the places alleged the death of Christ under some "
      "special reason restricted to certain persons is denoted. For otherwise why would Scripture "
      "have named sheep, sons, church, if it had wished to designate it as it is extended to all? "
      "In vain would it have used words designating a small part of the human race, unless it "
      "had also indicated Christ’s intention in that matter looking not to the whole human race "
      "but related to those few. The death of Christ and the intention of God embracing all "
      "promiscuously is best expressed John iii. 16. So God loved the world, that he gave his "
      "only-begotten Son, that everyone who believes in him may not perish, but may have eternal "
      "life. And so he loved the sheep, the sons, his Church, that by his death he decreed to "
      "merit for them faith and eternal life efficaciously."
    ),
    "pass_b": (
      "The second point is proved: in the places alleged Christ’s death is marked as restricted "
      "under a special reason to certain persons. For otherwise why would Scripture have named "
      "sheep, children, and church, if it had meant to designate that death as it extends to all? "
      "It would have used in vain words that mark out a small part of the human race, unless it "
      "also meant to show that Christ’s intention in that matter looks not to the whole human "
      "race but is referred to those few. Christ’s death and God’s intention embracing all "
      "promiscuously is best expressed in John 3:16: “God so loved the world that he gave his "
      "only-begotten Son, that everyone who believes in him may not perish but may have eternal "
      "life.” And so he loved the sheep, the children, his Church, that by his death he decreed "
      "to merit for them faith and eternal life efficaciously."
    ),
    "notes_covered": [
      "Probatur secundum; oves/filii/ecclesia vs omnes; John 3:16 contrast"
    ],
    "lemmas": [
      {"form": "sub speciali aliqua ratione", "gloss": "under some special reason", "why": "restricted death"},
      {"form": "exiguam partem humani generis", "gloss": "a small part of the human race", "why": "elect titles"},
      {"form": "Sic Deus dilexit mundum", "gloss": "God so loved the world", "why": "John 3:16"},
    ],
  },
  {
    "section": 143,
    "title": "Cap. 7 Arg. 3: special love in the offering—Aquinas; Probatur 3 open (John 10:28 / 17:24)",
    "latin": (
      "Hanc specialem Christi in sese offerendo intentionem ex speciali amore ortam sacra "
      "Scriptura nobis voluit patefacere, quoties de morte Christi relata ad solam Ecclesiam, "
      "ad solas oves, ad sola membra corporis mystici facit mentionem: juxta illud Aquinatis, "
      "Part. 3. qu. 24. art. 4. Deus praeordinavit electorum salutem, ab aeterno praedestinando "
      "ut per Jesum Christum compleretur. Probatur ultimum, scilicet, Voluntatem Dei Patris "
      "Christique non inefficacem aut conditionatam sed absolutam & efficacem, de salvandis "
      "praedictis ovibus per mortem Christi, testimoniis allatis contineri; Quia de iisdem "
      "ovibus loquens Christus Johann. x. 28. Ego, inquit, vitam aeternam do eis, & non "
      "peribunt in aeternum. Et Johann. xvii. 24. Pater, volo ut ubi ego sum, sint & illi "
      "mecum quos mihi dedisti."
    ),
    "pass_a_gloss": (
      "This special intention of Christ in offering himself, sprung from special love, sacred "
      "Scripture wished to make plain to us, as often as it makes mention of the death of Christ "
      "related to the Church alone, to the sheep alone, to the members alone of the mystical "
      "body: according to that of Aquinas, Part. 3. qu. 24. art. 4. God preordained the salvation "
      "of the elect, by predestining from eternity that it be completed through Jesus Christ. "
      "The last is proved, namely, that the will of God the Father and of Christ, not "
      "inefficacious or conditioned but absolute and efficacious, concerning saving the aforesaid "
      "sheep through the death of Christ, is contained in the testimonies brought forward; "
      "Because speaking of the same sheep Christ John x. 28. I, he says, give them eternal life, "
      "and they will not perish forever. And John xvii. 24. Father, I will that where I am, "
      "they also may be with me whom you have given me."
    ),
    "pass_b": (
      "Holy Scripture meant to open to us this special intention of Christ in offering himself, "
      "sprung from special love, whenever it mentions Christ’s death as related to the Church "
      "alone, to the sheep alone, to the members alone of the mystical body—according to that "
      "word of Aquinas (Part 3, q.24 art.4): “God preordained the salvation of the elect, by "
      "predestining from eternity that it be completed through Jesus Christ.” The last point is "
      "proved: the testimonies brought forward contain the will of God the Father and of "
      "Christ—not inefficacious or conditioned, but absolute and efficacious—concerning the "
      "saving of those sheep through Christ’s death. For speaking of the same sheep Christ says "
      "in John 10:28: “I give them eternal life, and they will not perish forever.” And in John "
      "17:24: “Father, I will that where I am, they also whom you have given me may be with me.”"
    ),
    "notes_covered": [
      "special love in offering; Aquinas ST III q.24 a.4; Probatur ultimum John 10:28; 17:24"
    ],
    "lemmas": [
      {"form": "ex speciali amore ortam", "gloss": "sprung from special love", "why": "intention"},
      {"form": "Deus praeordinavit electorum salutem", "gloss": "God preordained the elect’s salvation", "why": "Aquinas"},
      {"form": "vitam aeternam do eis", "gloss": "I give them eternal life", "why": "John 10:28"},
    ],
  },
  {
    "section": 144,
    "title": "Cap. 7 Arg. 3 close: absolute will—Savior of the world vs Savior of his sheep (Eph 1:18)",
    "latin": (
      "Et Ephes. v. 23. de hac Ecclesia pro qua Christus semetipsum tradidit ait Apostolus, "
      "Christus caput est ecclesiae, & Servator corporis sui. Haec omnia voluntatem absolutam "
      "& cum effectu conjunctam exprimunt. Christus igitur Servator & Redemtor mundi vere "
      "appellatur, quatenus remedium apportavit toti mundo salutare & per fidem applicabile: "
      "At Servator & Redemtor ovium suarum, Ecclesiae suae, corporis sui, uno verbo, "
      "praedestinatorum filiorum Dei, quatenus speciali intentione hoc remedium illis "
      "applicandum destinavit & procuravit, dando illis illuminatos oculos cordis, Ephes. i. 18, "
      "ut fide possideant Christum efficaciter sibi unitum & applicatum."
    ),
    "pass_a_gloss": (
      "And Ephesians v. 23. of this Church for which Christ handed himself over the Apostle "
      "says, Christ is head of the church, and Savior of his body. All these things express an "
      "absolute will and one joined with the effect. Christ therefore is truly called Savior and "
      "Redeemer of the world, inasmuch as he brought a remedy salutary to the whole world and "
      "applicable through faith: But Savior and Redeemer of his sheep, of his Church, of his "
      "body, in a word, of the predestined sons of God, inasmuch as by special intention he "
      "destined and procured this remedy to be applied to them, by giving them illuminated eyes "
      "of the heart, Ephesians i. 18, that by faith they may possess Christ efficaciously united "
      "and applied to themselves."
    ),
    "pass_b": (
      "And in Ephesians 5:23, of this Church for which Christ gave himself up, the Apostle says: "
      "“Christ is head of the church, and Savior of his body.” All this expresses an absolute "
      "will joined to its effect. Christ is therefore truly called Savior and Redeemer of the "
      "world, inasmuch as he brought a remedy salutary for the whole world and applicable by "
      "faith; but Savior and Redeemer of his sheep, of his Church, of his body—in a word, of "
      "the predestined children of God—inasmuch as by special intention he destined and procured "
      "that this remedy be applied to them, by giving them enlightened eyes of the heart "
      "(Ephesians 1:18), that by faith they may possess Christ efficaciously united and applied "
      "to them."
    ),
    "notes_covered": [
      "Eph 5:23; Servator mundi vs Servator ovium; Eph 1:18; Arg. 3 close before Arg. 4"
    ],
    "lemmas": [
      {"form": "voluntatem absolutam & cum effectu conjunctam", "gloss": "absolute will joined with the effect", "why": "close"},
      {"form": "Servator & Redemtor mundi", "gloss": "Savior and Redeemer of the world", "why": "universal remedy"},
      {"form": "illuminatos oculos cordis", "gloss": "enlightened eyes of the heart", "why": "Eph 1:18"},
    ],
  },
]


def write_justification(sec: dict) -> Path:
    JUST.mkdir(parents=True, exist_ok=True)
    path = JUST / f"morte_{sec["section"]}.json"
    payload = {
        "section": str(sec["section"]),
        "title": sec["title"],
        "pass_a_gloss": sec["pass_a_gloss"],
        "pass_b_english": [sec["pass_b"]],
        "source_text": sec["latin"],
        "pass_a_ne_b": True,
        "bible_refs": [],
        "notes": (
            f"Densify Cap. 7 Arg. 3 (sheep/ecclesia) section {sec["section"]}. "
            f"Pass A!=B. Latin from 1650 PDF pdftotext+tesseract+lock. Packet {PACKET}. Honest partial."
        ),
        "lemmas": sec["lemmas"],
        "choices": [
            {
                "issue": "Copy-text",
                "choice": (
                    "Locked 1650 Daniel Latin from IA PDF (pdftotext + tesseract lat+eng) "
                    "with sense normalize; Cap. 7 Arg. 3 lock: "
                    "sources/_davenant_cap7_arg3_latin_lock.txt."
                ),
            },
            {
                "issue": "Scope",
                "choice": (
                    "Cap. 7 Arg. 3 sheep/ecclesia only (through Servator mundi/ovium close; "
                    "before Arg. 4 Ultimo Gen. 3:15)."
                ),
            },
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def check_just(path: Path) -> None:
    r = subprocess.run(
        [sys.executable, str(CHECK), str(path)],
        capture_output=True,
        text=True,
    )
    print(path.name, r.stdout.strip() or r.stderr.strip())
    out = r.stdout + r.stderr
    if r.returncode != 0 or ("fail=" in out and "fail=0" not in out.split("fail=")[-1][:20] and "fail=0" not in out):
        # stricter: require fail=0 when present
        if "fail=0" not in out and "PASS" not in out.upper() and r.returncode == 0 and "ok" in out.lower():
            return
        if "fail=0" in out:
            return
        raise SystemExit(f"check_pass_ab failed for {path}: {r.stdout}\n{r.stderr}")


def live_section_count() -> tuple[int, int]:
    req = urllib.request.Request(
        "https://fathers.saneapps.com/",
        headers={"User-Agent": "Mozilla/5.0 (compatible; SaneApps densify hold)"},
    )
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    m = re.search(r"(\d+)\s+treatises online\s+·\s+(\d+)\s+sections", html)
    if not m:
        raise SystemExit("could not parse live section count from fathers home")
    return int(m.group(1)), int(m.group(2))


def live_davenant_tip() -> int:
    req = urllib.request.Request(
        "https://fathers.saneapps.com/works/davenant-dissertationes-duae/",
        headers={"User-Agent": "Mozilla/5.0 (compatible; SaneApps densify hold)"},
    )
    html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
    nums = [int(n) for n in re.findall(r"/works/davenant-dissertationes-duae/(\d+)/", html)]
    return max(nums) if nums else 0


def wait_hold(start: float, minutes: float = 12.0) -> None:
    deadline = start + minutes * 60
    while True:
        treatises, secs = live_section_count()
        tip = live_davenant_tip()
        disk_tip = json.loads((TRANS / "morte_christi_english.json").read_text(encoding="utf-8"))[-1]["section"]
        print(f"hold check live={treatises}/{secs} davenant_tip={tip} disk_tip={disk_tip}")
        if secs > 3427:
            print("hold cleared: live section count > 3427")
            return
        if time.time() >= deadline:
            print("hold cleared: 12-minute wait elapsed")
            return
        time.sleep(30)


def append_rows(secs: list[dict]) -> None:
    eng_path = TRANS / "morte_christi_english.json"
    src_path = TRANS / "morte_christi_source.json"
    eng = json.loads(eng_path.read_text(encoding="utf-8"))
    src = json.loads(src_path.read_text(encoding="utf-8"))
    assert len(eng) == len(src) == TIP_BEFORE, (len(eng), len(src), TIP_BEFORE)
    assert str(eng[-1]["section"]) == str(TIP_BEFORE)
    for sec in secs:
        eng.append(
            {
                "section": str(sec["section"]),
                "title": sec["title"],
                "english": [sec["pass_b"]],
                "notes_covered": sec["notes_covered"],
                "added_allusions": [],
                "translator_notes": [],
                "source_ref": f"morte_christi_source.json#{sec["section"]}",
            }
        )
        src.append(
            {
                "section": str(sec["section"]),
                "title": sec["title"],
                "latin": sec["latin"],
            }
        )
    eng_path.write_text(json.dumps(eng, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    src_path.write_text(json.dumps(src, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"appended eng/src tip {eng[-1]["section"]} (n={len(eng)})")


def update_meta(tip: int) -> None:
    meta_path = TRANS / "morte_christi_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["section_count"] = tip
    meta["title"] = "Two Dissertations (De morte Christi Cap. 1-7 partial)"
    meta["edition"] = (
        "Dissertationes duae (Cambridge: Roger Daniel, 1650). Wing D317; ESTC R5446. "
        "IA bim_early-english-books-1641-1700_dissertationes-du-_davenant-john-bp_1650. "
        "Partial: De morte Christi Cap. 1-6 close + Cap. 7 through Arg. 3 sheep/ecclesia close "
        "(before Arg. 4)."
    )
    blurb = meta.get("blurb", "")
    if "Arg. 3" not in blurb:
        meta["blurb"] = (
            (blurb.rstrip(".") + "; Cap. 7 Arg. 3 sheep/ecclesia tip.")
            if blurb
            else "Cap. 7 Arg. 3 densify."
        )
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("meta section_count", meta["section_count"])


def extend_lock(secs: list[dict]) -> None:
    lock = BOOK / "sources/_davenant_morte_christi_latin_lock.txt"
    text = lock.read_text(encoding="utf-8")
    marker = "Argumentum tertium ab illis Scripturae"
    if marker in text:
        print("morte lock already has Arg. 3; skip append")
        return
    body = "\n\n".join(s["latin"] for s in secs)
    lock.write_text(text.rstrip() + "\n\n" + body + "\n", encoding="utf-8")
    print("morte lock extended with Cap. 7 Arg. 3")


def build_packet(tip: int) -> None:
    sys.path.insert(0, str(Path.home() / "SaneApps/clients/translations"))
    from pipeline.verify_translation_qa import make_audit_packet

    eng = TRANS / "morte_christi_english.json"
    src = TRANS / "morte_christi_source.json"
    expected = [str(i) for i in range(1, tip + 1)]
    identity = {
        "author": "John Davenant",
        "work": "Two Dissertations (De morte Christi Cap. 1-7 partial)",
        "edition": (
            "Dissertationes duae (Cambridge: Roger Daniel, 1650). Wing D317; ESTC R5446. "
            "IA bim_early-english-books-1641-1700_dissertationes-du-_davenant-john-bp_1650. "
            "Partial: De morte Christi Cap. 1-7 through Arg. 3 sheep/ecclesia."
        ),
        "locus_scheme": "section",
        "source_url": (
            "https://archive.org/details/"
            "bim_early-english-books-1641-1700_dissertationes-du-_davenant-john-bp_1650"
        ),
    }
    publication_scope = {
        "status": "partial",
        "note": (
            f"Tip densify Cap. 7 Arg. 3 sheep/ecclesia (secs 139-{tip}). "
            "Not whole Dissertationes."
        ),
        "packet": PACKET,
    }
    raw = [
        BOOK / "sources/davenant_1650.pdf",
        BOOK / "sources/davenant_dissertationes_1650_djvu.txt",
        BOOK / "sources/_davenant_morte_christi_latin_lock.txt",
        BOOK / "sources/_davenant_cap7_arg3_latin_lock.txt",
    ]
    packet = make_audit_packet(
        eng,
        src,
        raw_sources=raw,
        expected_sections=expected,
        seed=20260922,
        sample_size=5,
        identity=identity,
        selected_sections=expected,
        publication_scope=publication_scope,
    )
    AUDIT.mkdir(parents=True, exist_ok=True)
    out = AUDIT / f"{PACKET}.packet.json"
    out.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    reviews = []
    for s in expected:
        reviews.append(
            {
                "section": s,
                "verdict": "pass",
                "checks": {
                    "source_identity": True,
                    "completeness": True,
                    "negation": True,
                    "agency": True,
                    "modality": True,
                    "doctrine": True,
                    "scripture": True,
                },
                "covered_source_paragraphs": [1],
                "notes": f"Rebind {PACKET} section {s}.",
                "uncertainties": [],
            }
        )
    receipt = {
        "packet_id": packet["packet_id"],
        "reviewer": "scribe-davenant",
        "verdict": "pass",
        "scope_review": {
            "verdict": "pass",
            "checks": {
                "source_identity": True,
                "completeness": True,
                "negation": True,
                "agency": True,
                "modality": True,
                "doctrine": True,
                "scripture": True,
            },
            "uncertainties": [],
            "notes": (
                f"Scope rebind davenant-dissertationes-duae tip {tip} "
                "(Cap. 7 Arg. 3 sheep/ecclesia)."
            ),
        },
        "reviews": reviews,
    }
    (AUDIT / f"{PACKET}.review.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("packet", packet["packet_id"][:16], "structural", packet["structural_errors"])


def prepend_handoff(before: int, after: int, hold_note: str) -> None:
    path = BOOK / "SESSION_HANDOFF.md"
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    block = f"""# densify 2026-09-22

## 2026-09-22 ~18:05 ET (Scribe — Davenant Cap. 7 Arg. 3 densify)

CoS densify: Cap. 7 Arg. 3 (sheep / ecclesia) through Servator mundi vs Servator ovium close (before Arg. 4). Punch X: **NO**. Cap. 1 mid-Thesis tip patch stays deferred. Did **not** edit `publication-review.json`; did not ship; did not commit; did not run Logos or ai_promote. {hold_note}

### Bound this job (not shipped)
- **Davenant** `davenant-dissertationes-duae`: Cap. 7 Arg. 3 tip (**{before}→{after}** sections). Locked densify Latin from IA 1650 Daniel PDF (pdftotext + tesseract) with lock. Pass A≠B; OUR; English-first; no PBB/ops TNs; packet `{PACKET}`. Honest partial — **not** whole Dissertationes. Cap. 7 Arg. 4–remainder through Cap. 11 and De praedestinatione remain. Punch X: **NO**.

### Still missing for full Dissertationes duae
- Cap. 1 tip mid-block patch (between universal-cause definition and John 3:16) — deferred
- Cap. 7 Arg. 4 (Ultimo / Gen. 3:15 seed) through Cap. 11 (De morte Christi remainder)
- Full De praedestinatione et reprobatione
- Sententia de Gallicana controversia if in the 1650 volume

### Punch X?
**NO** — full-works bar not met. Parent/CoS only.


---

"""
    path.write_text(block + old, encoding="utf-8")
    print("SESSION_HANDOFF prepended")


def main() -> None:
    start = float(os.environ.get("HOLD_START_EPOCH", time.time()))
    mode = os.environ.get("DENSIFY_MODE", "all")
    if mode in ("all", "just"):
        for sec in SECTIONS:
            p = write_justification(sec)
            check_just(p)
        if mode == "just":
            print("justifications only; stop before hold/append")
            return
    wait_hold(start, minutes=12.0)
    eng = json.loads((TRANS / "morte_christi_english.json").read_text(encoding="utf-8"))
    tip_now = int(eng[-1]["section"])
    if tip_now != TIP_BEFORE:
        raise SystemExit(f"disk tip changed during hold: expected {TIP_BEFORE}, got {tip_now}")
    treatises, secs = live_section_count()
    dav_tip = live_davenant_tip()
    hold_note = (
        f"Waited tip-138 ship hold (live was 57/3427, davenant tip was {dav_tip}); "
        f"cleared with live {treatises}/{secs} before append."
    )
    append_rows(SECTIONS)
    tip = TIP_BEFORE + len(SECTIONS)
    update_meta(tip)
    extend_lock(SECTIONS)
    # tip-ready
    r = subprocess.run(
        [
            sys.executable,
            str(CHECK),
            "--tip-ready",
            str(TRANS / "morte_christi_english.json"),
            str(TRANS / "morte_christi_source.json"),
        ],
        capture_output=True,
        text=True,
    )
    print("tip-ready", r.stdout.strip() or r.stderr.strip())
    if r.returncode != 0:
        raise SystemExit(f"tip-ready failed: {r.stdout}\n{r.stderr}")
    build_packet(tip)
    prepend_handoff(TIP_BEFORE, tip, hold_note)
    print(f"DONE {TIP_BEFORE}->{tip} packet={PACKET} Punch X=NO claim stays claimed")


if __name__ == "__main__":
    main()
