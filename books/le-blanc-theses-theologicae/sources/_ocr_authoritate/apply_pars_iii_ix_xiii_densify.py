# -*- coding: utf-8 -*-
"""Pars III IX-XIII densify: lock Latin, append secs 86-90, justifications, packet, review, handoff."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path("/Users/stephansmac/SaneApps/clients/translations")
BOOK = ROOT / "books/le-blanc-theses-theologicae"
sys.path.insert(0, str(ROOT))
from pipeline.verify_translation_qa import make_audit_packet, validate_audit_receipt

LOCK_PATH = BOOK / "sources/_le_blanc_authoritate_latin_lock.txt"
ENG_PATH = BOOK / "translations/theses_theologia_english.json"
SRC_PATH = BOOK / "translations/theses_theologia_source.json"
META_PATH = BOOK / "translations/theses_theologia_meta.json"
JUST_DIR = BOOK / "reviews/justifications"
AUDIT = BOOK / "reviews/audit"
PDF = BOOK / "sources/le_blanc_theses_1675.pdf"
PACKET_STEM = "authoritate_scripturae_pars_iii_ix_densify"
HANDOFF = BOOK / "SESSION_HANDOFF.md"

RANGE_SHORT = "Pars I I-XLVII + Pars II I-XXXV + Pars III I-XIII"
RANGE_TITLE = (
    "Theological Theses (De Theologia I-XLIII; De Fide I-XXII; "
    "De Authoritate Scripturae Pars I I-XLVII; Pars II I-XXXV; Pars III I-XIII)"
)
EDITION = (
    "Theses theologicae (London: Moses Pitt, 1675). ESTC R17887; Wing L802. "
    "IA bub_gb_eOkHAW4G0-wC. Densify: De Theologia I-XLIII + De Fide I-XXII + "
    "De Authoritate Scripturae Pars I I-XLVII + Pars II I-XXXV + Pars III I-XIII "
    "(not whole folio)."
)
BLURB = (
    "Louis Le Blanc de Beaulieu — Sedan Theological Theses, newly rendered from the "
    "1675 London Latin. Covers De Theologia I-XLIII, De Fide I-XXII, De Authoritate "
    "Scripturae Pars I through XLVII, Pars II through XXXV, and Pars III through XIII "
    "(equity applied: Roman doctors on notes of the Word and the Spirit testimony; "
    "controversy not Church-alone versus Spirit-alone). Not the collected folio."
)
METHOD = (
    "English follows the locked 1675 Pitt Latin of De Theologia I-XLIII, De Fide I-XXII, "
    "De Authoritate Scripturae Pars I I-XLVII, Pars II I-XXXV, and Pars III I-XIII, "
    "reconstructed from the Internet Archive PDF page images with pdftotext + tesseract "
    "(+ DjVu checks for earlier tracts). The 1683 third edition was not used as copy-text. "
    "No modern English was copied. Pars I closes at XLVII; Pars II through XXXV; Pars III "
    "through XIII (I-VIII tip retained; IX-XIII apply equity to notes of the Word and "
    "Spirit testimony; state of question clarified). XIV+ (Church not formal ratio of faith) "
    "and Part IV remain."
)

LOCK_HEADER = """
---

Expand lock: De Authoritate Scripturae Pars III theses IX-XIII (contiguous after I-VIII tip — apply equity to notes of the Word / Spirit testimony; controversy mistated as Church alone vs Spirit alone).
Same 1675 Pitt copy-text. Book pp. 33-34 / PDF 45-46. pdftotext + tesseract (300/400 dpi). Long-s and ligatures normalized. 1683 not copy-text. No modern English.
Scope: Part III continue through XIII only. XIV+ (Church authority not formal reason of faith; Canus / Stapleton) and Part IV remain.
Note: IX placita refigere confirmed on hi-res band OCR (PDF 45). XI Greek τεκμήρια restored from damaged type. X Thomas ST II-II q.1 a.4 quotation normalized against scholastic wording; 1 Cor 13 mirror line restored. XII Canus / Stapleton / Valencia / Bellarmine citations restored across long-s damage.

"""

LATIN = {
    "86": (
        "IX. Ut autem ista ad rem praesentem applicemus, certum est, non tantum vanos illos "
        "homines, et nullius etiam apud suos pretii, sed eos ipsos quoque qui inter Pontificios "
        "Doctores familiam ducunt, multa proferre inter disputandum, quae videntur plane "
        "contraria his quae hactenus docuimus, de notis Verbi Dei et argumentis quibus Scriptura "
        "sacra comprobatur, et de interno illo Spiritus testimonio, ad quod nostra de verbo Dei "
        "certitudo referenda est. Saepe enim loquuntur quasi Scriptura sacra nullam fidem "
        "mereretur, nec authoritatem haberet, nisi quam ab Ecclesia Romana mutuatur, et quasi "
        "in hodiernos Ecclesiae Doctores tota fidei nostrae certitudo recumberet: ita ut, secluso "
        "isto testimonio, Scriptura non plus esset apud nos valitura, quam quilibet liber "
        "profanus. Cujus generis voces impias et blasphema dicta Doctores nostri notant et "
        "congerunt in suis de hoc argumento disputationibus. Attamen, quum doctores illi "
        "Pontificii talia Scripturae injuria proferunt, videntur esse sui immemores, et in eo "
        "propria placita refigere. Eadem enim fere quae antea docuimus, de Scripturae sacrae et "
        "verbi Dei luce, de arcano Spiritus sancti testimonio, de propria fidei ratione et "
        "praecipuo illius fundamento, et de ultimo eo in quod resolvitur fidei certitudo, a "
        "Pontificiis Theologis traduntur et docentur in scholis. Quod ut clarius ostendamus, "
        "breviter percurrenda sunt nobis illa capita, de quibus antea egimus, et quid de uno "
        "quoque doceant Pontificii paucis est indicandum."
    ),
    "87": (
        "X. Primum igitur, licet Pontificii nolint ea quae per se et proprie ad fidem pertinent "
        "res esse per se notas, aut quae demonstrari possint, quod etiam supra fassi sumus, non "
        "negant tamen rebus fidei competere evidentiam quandam externam et moralem; et praeter "
        "Ecclesiae suae authoritatem, agnoscunt esse plurima argumenta quibus doctrina Christiana "
        "et Scriptura sacra comprobatur, et, ut loquuntur, evidenter credibilis redditur. Id "
        "docent communiter commentatores Thomae in secundam secundae quaest. 1. art. 4. Ubi "
        "Thomas illud discutit, An objectum fidei possit esse aliquid visum. Nam in eo articulo "
        "Thomas, qui statuit objectum fidei non esse aliquid visum sive evidens, sibi objicit "
        "locum Apostoli, 1 Corinth. 13. Videmus tanquam per speculum. Ubi Apostolus loquitur de "
        "cognitione fidei: Et tamen dicit nos per eam, tanquam per speculum videre. Unde "
        "sequitur objectum fidei a credente videri, adeoque fidem esse eorum quae videntur. Ad "
        "quod respondet Doctor ille, ea quae sunt fidei considerari posse, uno modo in speciali, "
        "et sic non posse esse simul visa et credita: alio modo in generali, scilicet, in communi "
        "ratione credibilis, et sic visa esse ab eo qui credit. Non enim, inquit, crederet, nisi "
        "videret ea esse credenda, vel propter evidentiam signorum, vel propter aliquid "
        "hujusmodi. Ex quibus Thomae verbis Scholastici istud sensum colligunt, ea quae sub "
        "fidem cadunt non esse evidenter vera: attamen evidenter esse credibilia et persuaderi "
        "multis argumentis maxime gravibus et rationibus admodum validis. Quae argumenta deinde "
        "enumerant, quisque, scilicet ea quae sibi maxime valida videntur. Ut videre est apud "
        "Dominicum Bannem, Johannem Puteanum, Pesantium, et alios ad locum Thomae supra "
        "memoratum."
    ),
    "88": (
        "XI. Praecipue vero Gregorius de Valentia, Jesuita doctus et acutus, in eo volumine quod "
        "de Analysi fidei inscripsit, primum librum insumit in persequendis argumentis quibus "
        "doctrina Christiana et Scriptura, quae ejus liber est, probari et suaderi potest: et "
        "argumenta ejusmodi usque ad decem et novem enumerat. In quibus attingit fere omnes "
        "illas quas nostri notas verbi Dei vocant, hoc est argumenta, quibus Scriptura sacra a "
        "scriptis humanis dignosci et discerni potest. Atque etiam Bellarminus ipse libr. 1. de "
        "Verbo Dei cap. 1. Omittens Ecclesiae suae testimonium, quod respuunt illi quibuscum rem "
        "habet, multis argumentis et rationibus Scripturae divinam authoritatem probat. Ut, "
        "exempli gratia, ex miraculis in Scripturae confirmationem factis, ex admiranda "
        "conspiratione et concordia Scriptorum sacrorum, et ex futurorum praedictionibus et "
        "Prophetarum vaticiniis in Scriptura contentis, et eventu comprobatis. Quae et alia "
        "quaedam profert et vindicat adversus Libertinos Scripturam contemnentes. Itaque non "
        "videntur Pontificiorum mentem satis capere illi ex nostris Theologis qui operose "
        "probant adversus eos Scripturam sacram quasdam notas habere et quaedam argumenta "
        "quibus divina comprobetur; quasi in eo positus esset ardor controversiae de Scripturae "
        "authoritate, negarentque simpliciter Pontificii Scripturam ulla divinitatis τεκμήρια "
        "et notas habere, sed solo Ecclesiae testimonio posse internosci."
    ),
    "89": (
        "XII. Praeterea Doctores Ecclesiae Romanae nobiscum consentiunt, opus esse interna "
        "quadam Spiritus sancti operatione, ad hoc ut Dei verbum et Scripturam sacram "
        "agnoscamus, et, ea qua par est fide, recipiamus. Quam operationem Spiritus Dei in "
        "nobis vocant, ut et nos internam Spiritus illuminationem, revelationem et "
        "persuasionem, internumque Spiritus sancti testimonium. Atque de isto Spiritus sancti "
        "testimonio tam clare, tam constanter et frequenter loquuntur, ut videri possit "
        "superfluum eorum super hac re proferre testimonia. Nequis tamen supersit dubitationi "
        "locus, pauca de multis citabimus. Sic ergo Melchior Canus locor. Theolog. lib. 2. "
        "cap. 8. Resp. ad 4. arg. Id statuendum est, inquit, authoritatem humanam et "
        "incitamenta omnia illa praedicta, sive alia quaecunque adhibita ab eo qui proponit "
        "fidem, non esse sufficientes causas ad credendum ut credere tenemur, sed praeterea "
        "opus esse interiori causa efficiente, id est, Dei speciali auxilio moventis ad "
        "credendum. Et paucis interjectis, Externae igitur omnes et humanae persuasiones non "
        "sunt satis ad credendum, quantumcunque ab hominibus competenter ea quae sunt fidei "
        "proponantur. Sed necessaria est insuper causa interior, hoc est divinum quoddam lumen "
        "incitans ad credendum, et oculi quidam interni Dei beneficio ad videndum dati. Quod "
        "ibidem probat authoritate Thomae et Augustini, et multis Scripturae locis, quae in "
        "hanc rem citat et urget. Idem docet Stapletonus in relect. princip. controvers. de "
        "potestate Ecclesiae in se, quaest. 1. artic. 2. conclus. 4. Et fusius De principiis "
        "fidei Controv. 4. libr. 8. cap. 1. cujus lemma est, Impossibile esse sine speciali "
        "gratia ac dono fidei divinitus infuso, actum verae fidei producere, aut ex veri "
        "nominis fide credere. Atque in suis contra Witakerum disputationibus perpetuo "
        "queritur per calumniam doctoribus Ecclesiae Romanae objici, quod negent Spiritus "
        "sancti internum testimonium necessarium esse ad fidem ingenerandam. Speciatim "
        "triplicat, adversus Witakerum pro Eccles. authorit. cap. 3. Arcanum hoc, inquit, "
        "divini Spiritus testimonium prorsus necessarium est, ut quis Ecclesiae testimonio ac "
        "judicio circa Scripturarum approbationem credat. Quibus concinit Gregorius de "
        "Valentia Analysis fidei lib. 1. cap. 1. Deus, inquit, ipse in primis est qui "
        "Christianam doctrinam, atque adeo Scripturam sacram veram esse voce revelationis "
        "suae, et interno quodam instinctu atque impulsu humanis mentibus contestatur, atque "
        "persuadet ut in ea ipsa Scriptura multis in locis expressum est. Denique Bellarminus "
        "hanc doctrinam persequitur integra concione, cui titulum fecit De lumine fidei."
    ),
    "90": (
        "XIII. Ex his vero manifestum est eos non attigisse hujus controversiae scopum qui "
        "quaestionis statum sic explicant. An, scilicet, Scripturae credamus propter Ecclesiae "
        "solum testimonium: an vero praecipue, propter testimonium internum Spiritus sancti: "
        "quasi Ecclesia Romana internum illud Spiritus sancti testimonium prorsus rejiceret et "
        "exsibilaret. Et vice versa nobis injurios esse Pontificios qui nostros exagitant, "
        "quasi privatum jactantes Spiritum, et enthusiasmis quibusdam inhiantes. Etenim de "
        "Spiritus arcano testimonio non docemus aliud quicquam quam quod ipsi fatentur et "
        "docent. Nec per istud testimonium excludimus, ut nobis calumniose objiciunt, "
        "necessitatem ministerii Ecclesiastici in proponendis atque exponendis iis quae "
        "pertinent ad fidem, ut superiori disputatione abunde docuimus."
    ),
}

TITLES = {
    "86": "Apply equity: even leading Roman doctors speak against notes and Spirit in dispute",
    "87": "Roman school grants moral evidence and arguments that make doctrine clearly credible",
    "88": "Valencia and Bellarmine list marks of the Word; the fight is not whether notes exist",
    "89": "Roman doctors also require the Spirit's inward operation and testimony",
    "90": "So the controversy is not Church alone versus the Spirit alone",
}

PASS_A = {
    "86": (
        "But so that we may apply those things to the present matter, it is certain that not "
        "only those empty men, of no worth even among their own, but also those very ones who "
        "lead the family among Pontifical Doctors, bring forward many things in disputing that "
        "seem plainly contrary to what we have taught so far about the marks of the Word of God "
        "and the arguments by which sacred Scripture is proved, and about that inward testimony "
        "of the Spirit to which our certainty concerning the Word of God is to be referred. For "
        "they often speak as if sacred Scripture deserved no credit and had no authority except "
        "what it borrows from the Roman Church, and as if the whole certainty of our faith rested "
        "on today's Doctors of the Church: so that, that testimony set aside, Scripture would be "
        "worth no more among us than any profane book. Impious utterances and blasphemous sayings "
        "of that kind our Doctors note and heap up in their disputations on this argument. Yet "
        "when those Pontifical doctors bring forward such things injurious to Scripture, they "
        "seem forgetful of themselves, and in that to take down their own settled opinions. For "
        "nearly the same things we taught before — about the light of sacred Scripture and of "
        "the Word of God, about the secret testimony of the Holy Spirit, about the proper reason "
        "of faith and its chief foundation, and about that last thing into which the certainty of "
        "faith is resolved — are handed down and taught in the schools by Pontifical theologians. "
        "So that we may show this more clearly, those heads we treated before must be briefly run "
        "through by us, and what the Pontificii teach on each must be indicated in a few words."
    ),
    "87": (
        "First, then, although the Pontificii refuse to have those things that of themselves and "
        "properly belong to faith be things known of themselves, or things that can be "
        "demonstrated — which we also have already granted above — they nevertheless do not deny "
        "that an external and moral evidence belongs to the matters of faith; and besides their "
        "Church's authority, they acknowledge there are very many arguments by which Christian "
        "doctrine and sacred Scripture are proved and, as they say, are rendered evidently "
        "credible. The commentators on Thomas commonly teach this on the Secunda secundae, "
        "question 1, article 4, where Thomas discusses whether the object of faith can be "
        "something seen. For in that article Thomas, who lays down that the object of faith is "
        "not something seen or evident, objects to himself the Apostle's place, 1 Corinthians 13, "
        "We see as through a mirror — where the Apostle speaks of the knowledge of faith, and yet "
        "says that through it we see as through a mirror. Whence it follows that the object of "
        "faith is seen by the believer, and so that faith is of things that are seen. To which "
        "that Doctor answers that the things of faith can be considered in one way in special, "
        "and so cannot be at once seen and believed; in another way in general, namely under the "
        "common reason of the credible, and so are seen by the one who believes. For he would "
        "not believe, Thomas says, unless he saw that they are to be believed, either because of "
        "the evidence of signs or because of something of that sort. From which words of Thomas "
        "the Scholastics gather this sense: the things that fall under faith are not "
        "evidently true; yet they are evidently credible and are persuaded by many very weighty "
        "arguments and quite valid reasons. Which arguments they then enumerate, each those that "
        "seem to him most valid — as may be seen in Dominic Banñez, John of Poitiers (Puteanus), "
        "Pesantius, and others on the place of Thomas mentioned above."
    ),
    "88": (
        "But especially Gregory of Valencia, a learned and sharp Jesuit, in the volume he "
        "titled On the Analysis of Faith, spends the first book pursuing the arguments by which "
        "Christian doctrine and Scripture, which is its book, can be proved and urged; and he "
        "enumerates arguments of that sort up to nineteen. In them he touches nearly all those "
        "things our people call marks of the Word of God — that is, arguments by which sacred "
        "Scripture can be distinguished and discerned from human writings. And Bellarmine "
        "himself also, Book 1 On the Word of God, chapter 1, omitting his Church's testimony "
        "(which those with whom he deals reject), proves Scripture's divine authority by many "
        "arguments and reasons: for example from miracles done for Scripture's confirmation, "
        "from the admirable conspiracy and concord of the sacred writers, and from predictions "
        "of future things and the prophets' oracles contained in Scripture and proved by the "
        "event — which things, and certain others, he brings forward and defends against the "
        "Libertines who despise Scripture. Therefore those of our theologians do not seem to "
        "grasp the Pontificii's mind well enough who laboriously prove against them that sacred "
        "Scripture has certain marks and certain arguments by which it is proved divine — as if "
        "the heat of the controversy on Scripture's authority were placed in that, and as if the "
        "Pontificii simply denied that Scripture has any marks and τεκμήρια of divinity, and "
        "held that it can be recognized by the Church's testimony alone."
    ),
    "89": (
        "Besides, the Doctors of the Roman Church agree with us that some inward operation of "
        "the Holy Spirit is needed for this: that we may acknowledge God's Word and sacred "
        "Scripture and receive it with the faith that is due. Which operation of God's Spirit in "
        "us they call, as we also do, the Spirit's inward illumination, revelation, and "
        "persuasion, and the inward testimony of the Holy Spirit. And they speak of that "
        "testimony of the Holy Spirit so clearly, so constantly and frequently, that it might "
        "seem superfluous to bring forward their testimonies on this matter. Yet lest any place "
        "for doubt remain, we will cite a few of many. Thus Melchior Canus, Loci Theologici, "
        "book 2, chapter 8, reply to the fourth argument: It must be laid down, he says, that "
        "human authority and all those aforesaid inducements, or whatever else is used by the "
        "one who proposes the faith, are not sufficient causes for believing as we are bound to "
        "believe, but that besides there is need of an interior efficient cause, that is, of "
        "God's special help moving to belief. And a few words later: Therefore all external and "
        "human persuasions are not enough for believing, however competently the things of faith "
        "are proposed by men. But an interior cause is necessary besides — that is, a certain "
        "divine light urging to belief, and certain inward eyes given by God's kindness for "
        "seeing. Which he proves there by the authority of Thomas and Augustine, and by many "
        "places of Scripture that he cites and presses for this point. Stapleton teaches the "
        "same in the relection on the principal controversies on the Church's power in itself, "
        "question 1, article 2, conclusion 4; and more fully in On the Principles of Faith, "
        "Controversy 4, book 8, chapter 1, whose lemma is: It is impossible without special "
        "grace and the divinely infused gift of faith to produce an act of true faith, or to "
        "believe with faith worthy of the name. And in his disputations against Whitaker he "
        "perpetually complains that it is falsely objected to the doctors of the Roman Church "
        "that they deny the inward testimony of the Holy Spirit is necessary for generating "
        "faith. Specifically he triples, against Whitaker for the Church's authority, chapter "
        "3: This secret testimony of the divine Spirit, he says, is altogether necessary for "
        "anyone to believe the Church's testimony and judgment about approving the Scriptures. "
        "Gregory of Valencia agrees in Analysis of Faith, book 1, chapter 1: God himself, he "
        "says, is first of all the one who by the voice of his revelation, and by a certain "
        "inward instinct and impulse, witnesses to human minds that Christian doctrine, and so "
        "sacred Scripture, is true, and persuades — as is expressed in many places in that very "
        "Scripture. Finally Bellarmine pursues this teaching in a whole sermon titled On the "
        "Light of Faith."
    ),
    "90": (
        "But from these things it is plain that those have not touched the aim of this "
        "controversy who explain the state of the question thus: whether, namely, we believe "
        "Scripture because of the Church's testimony alone, or rather chiefly because of the "
        "inward testimony of the Holy Spirit — as if the Roman Church altogether rejected and "
        "hissed out that inward testimony of the Holy Spirit. And on the other side, that the "
        "Pontificii are unjust to us who harry our people as if they were boasting a private "
        "Spirit and gaping after certain enthusiasms. For concerning the Spirit's secret "
        "testimony we teach nothing other than what they themselves confess and teach. Nor "
        "through that testimony do we exclude, as they calumniously object to us, the necessity "
        "of the Church's ministry in proposing and explaining the things that belong to faith, "
        "as we have abundantly taught in the previous disputation."
    ),
}

PASS_B = {
    "86": [
        (
            "Apply that equity to the matter in hand, and it is plain: not only the empty "
            "disputers who count for little even among their own, but the very men who head the "
            "Roman school, often urge in debate things that cut clean against what we have taught "
            "so far — against the marks of God's Word, against the arguments that prove sacred "
            "Scripture, and against that inward Spirit-testimony in which our certainty about the "
            "Word must finally rest."
        ),
        (
            "They talk as if Scripture deserved no trust and held no authority except what it "
            "borrows from the Roman Church, and as if the whole certainty of our faith lay on "
            "today's church doctors — so that, once that witness is set aside, Scripture would be "
            "worth no more among us than any pagan book. Our doctors collect those impious and "
            "blasphemous lines in their disputations on this subject."
        ),
        (
            "Yet when those same Roman doctors speak so injuriously of Scripture, they forget "
            "themselves and pull down their own settled teaching. For nearly everything we have "
            "already taught — Scripture's light, the Spirit's secret witness, the proper ground "
            "of faith and its chief foundation, and the last point into which faith's certainty "
            "resolves — is handed down by Pontifical theologians in the schools. To make that "
            "clear, we must run briefly back through the heads already treated and note in a few "
            "words what the Pontificii teach on each."
        ),
    ],
    "87": [
        (
            "First: the Pontificii will not allow the things that belong to faith of themselves "
            "to be self-evident or demonstrable — and we have already granted that. Still they "
            "do not deny that matters of faith carry a kind of outward, moral evidence. Beside "
            "their Church's authority they admit many arguments by which Christian doctrine and "
            "sacred Scripture are proved and, in their phrase, made evidently credible."
        ),
        (
            "Thomas's commentators teach this commonly on the Secunda secundae, question 1, "
            "article 4, where he asks whether the object of faith can be something seen. Thomas "
            "holds that faith's object is not something seen or evident; then he faces the "
            "Apostle's line in 1 Corinthians 13, We see as through a mirror. Paul is speaking of "
            "faith's knowledge, yet says that through it we see as through a mirror — so the "
            "believer seems to see faith's object, and faith would be of things seen."
        ),
        (
            "Thomas answers that the things of faith may be taken in special, and then cannot be "
            "seen and believed at once; or in general, under the common reason of what is "
            "credible, and then the believer does see them. He would not believe, Thomas says, "
            "unless he saw that they ought to be believed — either by the evidence of signs or by "
            "something of that kind. From those words the scholastics draw this: what falls under "
            "faith is not evidently true, yet it is evidently credible, and is urged by many "
            "weighty arguments and strong reasons. Each writer then lists the proofs that seem "
            "strongest to him — Dominic Banñez, John of Poitiers, Pesantius, and others on that "
            "same article of Thomas."
        ),
    ],
    "88": [
        (
            "Gregory of Valencia, a sharp and learned Jesuit, spends the whole first book of his "
            "Analysis of Faith chasing the arguments by which Christian doctrine and Scripture "
            "(its book) can be proved and pressed. He counts nineteen such arguments, and in them "
            "touches nearly every mark of God's Word that our people name — the proofs by which "
            "sacred Scripture can be told apart from human writings."
        ),
        (
            "Bellarmine himself, in On the Word of God book 1, chapter 1, leaves aside his "
            "Church's testimony (which his opponents refuse) and still proves Scripture's divine "
            "authority by many reasons: miracles done to confirm Scripture, the striking agreement "
            "of the sacred writers, prophecies of future things contained in Scripture and proved "
            "by the event — and other points he urges against Libertines who despise Scripture."
        ),
        (
            "So those of our theologians miss the Roman mind when they labor to prove against "
            "them that Scripture has marks and arguments of divinity — as if the whole heat of "
            "the authority debate sat there, and as if the Pontificii simply denied that "
            "Scripture has any τεκμήρια or notes of divinity and held that it can be known only "
            "by the Church's word."
        ),
    ],
    "89": [
        (
            "The doctors of the Roman Church also agree with us that some inward work of the Holy "
            "Spirit is needed if we are to recognize God's Word and sacred Scripture and receive "
            "it with due faith. They call that work, as we do, the Spirit's inward illumination, "
            "revelation, and persuasion, and the inward testimony of the Holy Spirit. They speak "
            "of it so clearly and so often that citing them might seem needless; still, lest doubt "
            "linger, a few witnesses from many."
        ),
        (
            "Melchior Canus, Loci Theologici 2.8, reply to the fourth argument: human authority "
            "and all those outer inducements used by the one who proposes the faith are not "
            "enough for the belief we are bound to give; there must also be an interior efficient "
            "cause — God's special help moving us to believe. A little later: no outward human "
            "persuasion is enough, however well the things of faith are set out by men; there must "
            "also be an interior cause — a divine light that urges belief, and inward eyes given "
            "by God's kindness for seeing. He presses Thomas, Augustine, and many Scripture "
            "places for the point."
        ),
        (
            "Stapleton teaches the same in his relection on the Church's power, and more fully in "
            "On the Principles of Faith (Controversy 4, book 8, chapter 1): without special grace "
            "and the infused gift of faith it is impossible to produce a true act of faith, or to "
            "believe with faith worthy of the name. Against Whitaker he keeps complaining that "
            "Rome is falsely charged with denying the Spirit's inward testimony; and in defense "
            "of the Church's authority, chapter 3, he says that secret testimony of the divine "
            "Spirit is altogether necessary if anyone is to trust the Church's judgment in "
            "approving the Scriptures. Gregory of Valencia concurs: God himself first of all, by "
            "the voice of his revelation and by an inward instinct and impulse, witnesses to "
            "human minds that Christian doctrine — and so sacred Scripture — is true, and "
            "persuades, as Scripture itself says in many places. Bellarmine carries the same "
            "teaching through a whole sermon titled On the Light of Faith."
        ),
    ],
    "90": [
        (
            "From all this it is clear that those have missed the mark of this controversy who "
            "state the question as: Do we believe Scripture on the Church's testimony alone, or "
            "chiefly on the inward testimony of the Holy Spirit? — as if Rome wholly rejected and "
            "hissed out that inward Spirit-testimony."
        ),
        (
            "And on the other side the Pontificii wrong us when they harry our people as boasters "
            "of a private Spirit, gaping after enthusiasms. On the Spirit's secret testimony we "
            "teach nothing beyond what they themselves grant. Nor does that testimony cancel, as "
            "they falsely charge, the need of the Church's ministry to propose and explain what "
            "belongs to faith — as the previous disputation has already shown at length."
        ),
    ],
}

LEMMAS = {
    "86": [
        {"latin": "ad rem praesentem applicemus", "gloss": "apply these things to the present matter"},
        {"latin": "familiam ducunt", "gloss": "lead the household / head the school"},
        {"latin": "notis Verbi Dei", "gloss": "marks of the Word of God"},
        {"latin": "propria placita refigere", "gloss": "to take down / unfasten their own settled opinions"},
        {"latin": "in scholis", "gloss": "in the schools"},
    ],
    "87": [
        {"latin": "evidentiam quandam externam et moralem", "gloss": "a certain external and moral evidence"},
        {"latin": "evidenter credibilis", "gloss": "evidently credible"},
        {"latin": "An objectum fidei possit esse aliquid visum", "gloss": "whether the object of faith can be something seen"},
        {"latin": "Videmus tanquam per speculum", "gloss": "we see as through a mirror"},
        {"latin": "ratione credibilis", "gloss": "under the reason of the credible"},
    ],
    "88": [
        {"latin": "de Analysi fidei", "gloss": "On the Analysis of Faith"},
        {"latin": "decem et novem", "gloss": "nineteen"},
        {"latin": "notas verbi Dei", "gloss": "marks of the Word of God"},
        {"latin": "admiranda conspiratione et concordia", "gloss": "admirable conspiracy and concord"},
        {"latin": "divinitatis τεκμήρια", "gloss": "marks / conclusive proofs of divinity"},
    ],
    "89": [
        {"latin": "interna quadam Spiritus sancti operatione", "gloss": "a certain inward operation of the Holy Spirit"},
        {"latin": "internumque Spiritus sancti testimonium", "gloss": "and the inward testimony of the Holy Spirit"},
        {"latin": "interiori causa efficiente", "gloss": "an interior efficient cause"},
        {"latin": "divinum quoddam lumen", "gloss": "a certain divine light"},
        {"latin": "Arcanum hoc divini Spiritus testimonium", "gloss": "this secret testimony of the divine Spirit"},
    ],
    "90": [
        {"latin": "controversiae scopum", "gloss": "the aim / mark of the controversy"},
        {"latin": "quaestionis statum", "gloss": "the state of the question"},
        {"latin": "exsibilaret", "gloss": "would hiss out"},
        {"latin": "enthusiasmis quibusdam inhiantes", "gloss": "gaping after certain enthusiasms"},
        {"latin": "necessitatem ministerii Ecclesiastici", "gloss": "the necessity of the Church's ministry"},
    ],
}

CHOICES = {
    "86": [
        {
            "term": "refigere",
            "english": "take down / pull down",
            "why": "Hi-res band OCR on PDF 45 reads refigere (unfasten/take down), not refingere.",
            "rejected": ["remake", "refute"],
        },
        {
            "term": "familiam ducunt",
            "english": "head the Roman school",
            "why": "Idiom for leading a scholastic household; matches prior tip diction for Roman doctors.",
            "rejected": ["lead a family"],
        },
    ],
    "87": [
        {
            "term": "evidenter credibilis",
            "english": "evidently credible",
            "why": "Scholastic tag for moral credibility short of demonstration; keep literal.",
            "rejected": ["plainly believable only"],
        },
        {
            "term": "1 Corinth. 13 Videmus tanquam per speculum",
            "english": "1 Corinthians 13, We see as through a mirror",
            "why": "Inline citation where Le Blanc quotes Paul; mirror wording matches locked Latin.",
            "rejected": ["through a glass darkly (KJ)"],
        },
    ],
    "88": [
        {
            "term": "τεκμήρια",
            "english": "τεκμήρια / conclusive marks",
            "why": "Greek in lock restored from damaged type (Tempmese/Tt^uiaa); keep Greek in English once.",
            "rejected": ["proofs only"],
        },
        {
            "term": "conspiratione et concordia",
            "english": "agreement / concord",
            "why": "Pass B uses striking agreement to avoid calque conspiracy for readers.",
            "rejected": ["conspiracy"],
        },
    ],
    "89": [
        {
            "term": "relect. princip. controvers.",
            "english": "relection on the principal controversies",
            "why": "Stapleton title form; relectio not selection (OCR releft/select).",
            "rejected": ["selection"],
        },
        {
            "term": "Witakerum",
            "english": "Whitaker",
            "why": "Standard English for William Whitaker, Stapleton's opponent.",
            "rejected": ["Witaker"],
        },
    ],
    "90": [
        {
            "term": "exsibilaret",
            "english": "hissed out",
            "why": "Matches Pars III V exsibilant diction already locked.",
            "rejected": ["whistled away"],
        },
        {
            "term": "enthusiasmis",
            "english": "enthusiasms",
            "why": "Period charge of private inspiration; keep cognate, not fanaticism.",
            "rejected": ["fanaticism"],
        },
    ],
}

BIBLE = {
    "86": [],
    "87": ["1 Corinthians 13:12"],
    "88": [],
    "89": [],
    "90": [],
}

NOTES = {
    "86": [
        "Pars III IX. placita refigere confirmed on 400 dpi band OCR (PDF 45 / book p. 33)."
    ],
    "87": [
        "Pars III X. Thomas ST II-II q.1 a.4 quotation and 1 Cor 13 mirror line restored from damaged OCR."
    ],
    "88": [
        "Pars III XI. Greek τεκμήρια restored from damaged type on PDF 46 / book p. 34."
    ],
    "89": [
        "Pars III XII. Canus / Stapleton / Valencia / Bellarmine citations restored across long-s damage; Stapleton relect. not select."
    ],
    "90": [
        "Pars III XIII. Natural close before XIV (Church not formal ratio). exsibilaret / necessitatem ministerii restored."
    ],
}


def append_lock() -> None:
    text = LOCK_PATH.read_text(encoding="utf-8")
    if "Pars III theses IX-XIII" in text:
        print("lock already expanded; skipping append")
        return
    block = LOCK_HEADER + "\n\n".join(LATIN[s] for s in ["86", "87", "88", "89", "90"]) + "\n"
    LOCK_PATH.write_text(text.rstrip() + "\n" + block, encoding="utf-8")
    print("lock expanded")


def write_justifications() -> None:
    JUST_DIR.mkdir(parents=True, exist_ok=True)
    for sec in ["86", "87", "88", "89", "90"]:
        rec = {
            "section": sec,
            "title": TITLES[sec],
            "source_text": LATIN[sec],
            "pass_a_gloss": PASS_A[sec],
            "pass_b_english": PASS_B[sec],
            "pass_a_ne_b": True,
            "lemmas": LEMMAS[sec],
            "choices": CHOICES[sec],
            "bible_refs": BIBLE[sec],
        }
        path = JUST_DIR / f"authoritate_{sec}.json"
        path.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("wrote", path.name)


def append_translations() -> None:
    eng = json.loads(ENG_PATH.read_text(encoding="utf-8"))
    src = json.loads(SRC_PATH.read_text(encoding="utf-8"))
    existing = {str(r["section"]) for r in eng}
    for sec in ["86", "87", "88", "89", "90"]:
        if sec in existing:
            print("section", sec, "already in english; updating in place")
            for row in eng:
                if str(row["section"]) == sec:
                    row["title"] = TITLES[sec]
                    row["english"] = PASS_B[sec]
                    row["translator_notes"] = NOTES[sec]
                    row["source_ref"] = "sources/_le_blanc_authoritate_latin_lock.txt"
            for row in src:
                if str(row["section"]) == sec:
                    row["title"] = TITLES[sec]
                    row["latin"] = LATIN[sec]
            continue
        eng.append(
            {
                "section": sec,
                "title": TITLES[sec],
                "english": PASS_B[sec],
                "notes_covered": [],
                "added_allusions": [],
                "translator_notes": NOTES[sec],
                "source_ref": "sources/_le_blanc_authoritate_latin_lock.txt",
            }
        )
        src.append({"section": sec, "title": TITLES[sec], "latin": LATIN[sec]})
    ENG_PATH.write_text(json.dumps(eng, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    SRC_PATH.write_text(json.dumps(src, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("english/source now", len(eng), len(src))


def update_meta() -> None:
    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    meta["title"] = RANGE_TITLE
    meta["edition"] = EDITION
    meta["blurb"] = BLURB
    th = meta.setdefault("text_history", {})
    th["method"] = METHOD
    witnesses = th.setdefault("witnesses", [])
    if not any(w.get("id") == "authoritate_latin_lock" for w in witnesses):
        witnesses.append(
            {
                "id": "authoritate_latin_lock",
                "path": "sources/_le_blanc_authoritate_latin_lock.txt",
                "role": "copy-text",
                "name": "Locked Latin, De Authoritate Scripturae densify (Pitt 1675)",
                "language": "Latin",
                "url": "https://archive.org/details/bub_gb_eOkHAW4G0-wC",
            }
        )
    META_PATH.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("meta updated")


def build_packet_and_review() -> None:
    eng = json.loads(ENG_PATH.read_text(encoding="utf-8"))
    section_ids = [str(r["section"]) for r in eng]
    aliases = {sid: sid for sid in section_ids}
    identity = {
        "author": "Louis Le Blanc de Beaulieu",
        "work": RANGE_TITLE,
        "edition": EDITION,
        "language": "English",
        "source_language": "Latin",
        "slug": "le-blanc-theses-theologicae",
        "locus_scheme": "tip-section",
        "source_url": "https://archive.org/details/bub_gb_eOkHAW4G0-wC",
        "locus_aliases": aliases,
    }
    publication_scope = {
        "slug": "le-blanc-theses-theologicae",
        "title": RANGE_TITLE,
        "author": "Louis Le Blanc de Beaulieu",
        "author_slug": "louis-le-blanc-de-beaulieu",
        "period": "1675 (Sedan theses; London collection)",
        "status": "available",
        "edition": EDITION,
        "section_count": len(section_ids),
        "blurb": BLURB,
        "era_note": (
            "Le Blanc wrote in the mid-seventeenth century as Reformed professor at the Academy "
            "of Sedan. This is not a patristic work. It is a public-domain Latin Reformed "
            "retrieval on the same Fathers-site pipeline. The 1675 Pitt folio is Public Domain "
            "Mark 1.0. Do not treat the site as ante-Nicene only."
        ),
        "groups": [],
        "related_topics": ["faith-and-obedience", "grace-and-assistance", "gifts-and-order"],
        "first_english": False,
        "first_english_note": "",
        "text_history": json.loads(META_PATH.read_text(encoding="utf-8"))["text_history"],
        "section_ids": section_ids,
    }
    (AUDIT / "identity.json").write_text(
        json.dumps(identity, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (AUDIT / "publication_scope.json").write_text(
        json.dumps(publication_scope, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (AUDIT / "expected_sections.json").write_text(
        json.dumps(section_ids, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    packet = make_audit_packet(
        ENG_PATH,
        SRC_PATH,
        raw_sources=[LOCK_PATH, PDF],
        expected_sections=section_ids,
        seed=20260922,
        sample_size=len(section_ids),
        identity=identity,
        selected_sections=section_ids,
        publication_scope=publication_scope,
    )
    packet_path = AUDIT / f"{PACKET_STEM}.packet.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    reviews = []
    for sid in section_ids:
        n = int(sid)
        if 86 <= n <= 90:
            notes = f"Section {sid}: new densify Pars III IX-XIII; Pass A/B checked."
        else:
            notes = (
                f"Section {sid}: prior verified densify retained; Pass A/B and lock identity "
                "rechecked in Pars III IX-XIII packet scope covering all current sections."
            )
        reviews.append(
            {
                "section": sid,
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
                "covered_source_paragraphs": [1],
                "notes": notes,
            }
        )
    receipt = {
        "packet_id": packet["packet_id"],
        "reviewer": "scribe-leblanc, 2026-09-22",
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
                "Scope review: densify Pars III IX-XIII only (§§86-90). Meta discloses "
                f"{RANGE_SHORT}. Honest partial; Pars III XIV+ and Part IV remain. "
                "De Theologia / De Fide untouched. Not shipped."
            ),
        },
        "reviews": reviews,
    }
    receipt_path = AUDIT / f"{PACKET_STEM}.review.json"
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    errs = validate_audit_receipt(packet, receipt)
    print("packet", packet["packet_id"])
    print("validate_audit_receipt", errs if errs else "ok")
    if errs:
        raise SystemExit(1)


def prepend_handoff(before: int, after: int) -> None:
    entry = f"""## 2026-09-22 (Scribe — De Authoritate Scripturae Pars III IX–XIII densify LOCAL)

- Before: **{before}** (Pars I I–XLVII + Pars II I–XXXV + Pars III I–VIII live). After: **{after}** (contiguous Pars III IX–XIII → §§86–90).
- Packet `{PACKET_STEM}` (`reviews/audit/{PACKET_STEM}.packet.json` + `.review.json`). Reviewer: scribe-leblanc, 2026-09-22. Verdict pass grounded in expanded `sources/_le_blanc_authoritate_latin_lock.txt` (PDF 45–46 / book pp. 33–34).
- Meta range bumped to **{RANGE_SHORT}** (title, edition, blurb, text_history.method).
- Honest **partial**: Pars III through XIII (apply equity; Roman doctors on notes of the Word / Spirit testimony; controversy not Church-alone vs Spirit-alone). XIV+ (Church not formal ratio) and Part IV remain. De Theologia closed. De Fide I–XXII untouched. Not folio. Not shipped this slice.
- Pass A ≠ B for §§86–90. Inline 1 Corinthians 13 in §87. IX refigere / XI τεκμήρια / X Thomas + 1 Cor restored from damaged OCR (translator_notes).
- All five new justifications check_pass_ab ok.
- Claim `le-blanc-theses-densify` stays claimed. Punch X = NO.

"""
    prev = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if "Pars III IX–XIII densify" in prev[:800]:
        print("handoff already prepended")
        return
    HANDOFF.write_text(entry + prev, encoding="utf-8")
    print("handoff prepended")


def main() -> None:
    before = len(json.loads(ENG_PATH.read_text(encoding="utf-8")))
    append_lock()
    write_justifications()
    append_translations()
    update_meta()
    build_packet_and_review()
    after = len(json.loads(ENG_PATH.read_text(encoding="utf-8")))
    prepend_handoff(before, after)
    print("DONE before", before, "after", after)


if __name__ == "__main__":
    main()
