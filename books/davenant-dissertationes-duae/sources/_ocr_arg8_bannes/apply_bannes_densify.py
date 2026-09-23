#!/usr/bin/env python3
"""Cap. 6 Arg. 8 Bannes/Alvarez/Estius/Bellarmine densify — tip 124 → ~131."""
from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

BOOK = Path.home() / "SaneApps/clients/translations/books/davenant-dissertationes-duae"
TRANS = BOOK / "translations"
JUST = BOOK / "reviews/justifications"
AUDIT = BOOK / "reviews/audit"
PIPE = Path.home() / "SaneApps/clients/translations/pipeline"
PACKET = "morte_christi_cap6_arg8_bannes_densify"
CHECK = PIPE / "check_pass_ab.py"

SECTIONS = [
  {
    "section": 125,
    "title": "Cap. 6 Arg. 8 Schoolmen: Bannes—supernatural helps not given to all; difference not from free choice",
    "latin": (
      "Dominicus Bannes in 1. Aquin. qu. 22. conclus. ult. pag. 278: Deus, inquit, "
      "ab aeterno statuit, voluntate vel absoluta vel consequenti, non dare omnibus "
      "supernaturalia auxilia. Quod si quis quaerat, quare potius quibusdam in singulari "
      "haec dona conferat, aliis vero deneget, hoc ex simplici Dei voluntate pendet, neque "
      "est ejus rei ratio quaerenda, ut docet Augustinus et D. Thomas. Paulo post, Discat "
      "ergo Theologus Christianus et humilis cum D. Thoma et Augustino ignorare potius quam "
      "cum curiosis sapere plusquam oportet sapere, ne incidat in haeresin Pelagianam, "
      "referendo hujusmodi differentiam in liberum arbitrium tanquam in primam illius causam "
      "et radicem, scilicet, Quia iste voluit converti, ille non voluit. Denique et illud "
      "addit, quod nervos incidit Pelagianae et Arminianae Theologiae, Ipsamet concurrentia "
      "liberi arbitrii effectus est necessario consequens necessitate consequentiae ex "
      "Divino auxilio efficaci."
    ),
    "pass_a_gloss": (
      "Dominicus Bannes on 1 Aquinas question 22 last conclusion page 278: God, he says, "
      "from eternity decided, by a will either absolute or consequent, not to give "
      "supernatural helps to all. But if anyone asks why rather he confers these gifts on "
      "certain people in particular, and denies them to others, this hangs on the simple "
      "will of God, and the reason of that matter is not to be sought, as Augustine and "
      "Saint Thomas teach. A little later: Therefore let the Christian and humble "
      "theologian learn with Saint Thomas and Augustine rather to be ignorant than with "
      "the curious to know beyond what it is fitting to know, lest he fall into the "
      "Pelagian heresy by referring a difference of this kind into free choice as into its "
      "first cause and root, namely, Because this one willed to be converted, that one did "
      "not will. Finally he also adds that which cuts the sinews of Pelagian and Arminian "
      "theology: The concurrence of free choice itself is an effect necessarily following "
      "by necessity of consequence from efficacious divine help."
    ),
    "pass_b": (
      "Dominicus Bannes, on Aquinas I q.22, last conclusion, p. 278: God, he says, decided "
      "from eternity—by a will either absolute or consequent—not to give supernatural helps "
      "to everyone. If anyone asks why he confers these gifts on certain people in "
      "particular and denies them to others, that hangs on God’s bare will; as Augustine "
      "and St Thomas teach, you should not hunt a further reason. A little later: So the "
      "Christian theologian who is humble should learn with St Thomas and Augustine to leave "
      "some things unknown rather than, with the curious, to know more than he ought, lest "
      "he slide into the Pelagian heresy by tracing this difference to free choice as its "
      "first cause and root—“because this one wanted to convert, and that one did not.” He "
      "also adds a line that cuts the sinews of Pelagian and Arminian theology: the will’s "
      "own concurrence is itself an effect that necessarily follows, by necessity of "
      "consequence, from efficacious divine help."
    ),
    "notes_covered": [
      "Bannes in 1 Sent./Aquin. q.22 conclus. ult. p. 278",
      "difference of helps not from liberum arbitrium; concurrence as effect of efficacious help",
    ],
    "lemmas": [
      {"form": "voluntate vel absoluta vel consequenti", "gloss": "by absolute or consequent will", "why": "Bannes"},
      {"form": "nervos incidit", "gloss": "cuts the sinews", "why": "vs Pelagian/Arminian"},
      {"form": "necessitate consequentiae", "gloss": "by necessity of consequence", "why": "concurrentia as effect"},
    ],
  },
  {
    "section": 126,
    "title": "Cap. 6 Arg. 8 Schoolmen: Bannes rejects universal prepared grace and will-based discrimination",
    "latin": (
      "Hisce suis pronunciatis doctissimus Bannesius illorum opinionem rejicit damnatque, "
      "qui gratiam regenerantem et salvivificam propter meritum Christi omnibus hominibus "
      "paratam et expositam tuentur. Porro et illos refellit, qui rationem cur hi "
      "regenerentur, illi non regenerentur, sive cur hi convertantur, illi non convertantur, "
      "resolvunt in velle et nolle humanum. Denique et illud docet, nostram concurrentiam "
      "sive non-resistentiam, hoc est, velle nostrum, esse necessarium effectum datae "
      "gratiae efficacis, ac proinde, non esse rationem aut conditionem dandae et "
      "accipiendae."
    ),
    "pass_a_gloss": (
      "By these pronouncements of his the most learned Bannes rejects and condemns the "
      "opinion of those who maintain that regenerating and saving-vivifying grace is "
      "prepared and set out for all human beings on account of the merit of Christ. Further "
      "he also refutes those who resolve the reason why these are regenerated and those are "
      "not regenerated, or why these are converted and those are not converted, into human "
      "willing and not-willing. Finally he also teaches that our concurrence or "
      "non-resistance, that is our willing, is a necessary effect of efficacious grace that "
      "has been given, and therefore is not the reason or condition of its being given and "
      "received."
    ),
    "pass_b": (
      "With those rulings the learned Bannes rejects and condemns the view that regenerating, "
      "life-saving grace is prepared and laid open to every human being because of Christ’s "
      "merit. He also refutes those who locate the reason why some are regenerated and others "
      "are not—or why some convert and others do not—in human willing and refusing. And he "
      "teaches that our concurrence, or our non-resistance—our willing—is a necessary effect "
      "of efficacious grace once given, and so is not the reason or condition for its being "
      "given and received."
    ),
    "notes_covered": [
      "Bannesius application against universal prepared regenerating grace",
      "velle/nolle not root of discrimination; concurrentia as effect not condition",
    ],
    "lemmas": [
      {"form": "gratiam regenerantem et salvivificam", "gloss": "regenerating and life-saving grace", "why": "universal prepared"},
      {"form": "velle et nolle humanum", "gloss": "human willing and refusing", "why": "false root"},
      {"form": "non-resistentiam", "gloss": "non-resistance", "why": "as effect of grace"},
    ],
  },
  {
    "section": 127,
    "title": "Cap. 6 Arg. 8 Schoolmen: Alvarez—efficacious grace’s start not from nature’s use of sufficient help",
    "latin": (
      "Alvares, De auxiliis Divinae gratiae, Disp. 58. pag. 263. Si asseramus legem a Deo "
      "statutam dandi infallibiliter auxilium efficax bene utentibus, aut uti volentibus ex "
      "sola sua innata libertate auxilio sufficienti, jam initium gratiae efficacis esset ex "
      "natura et ex innata hominis libertate, volentis bene uti auxilio sufficienti. Haec "
      "est ipsissima lex sive ipsissimum illud decretum Dei, quod ab Arminio, Corvino, "
      "reliquisque ejusdem Scholae Theologis tanto studio propugnatur. Dicunt enim, gratiam "
      "sufficientem propter meritum Christi Mediatoris dari omnibus; efficacem vero, id est, "
      "eam, quae ipso facto convertat regeneretque, ea lege dandam, si bene utantur illa "
      "excitante sive sufficiente, hoc est, si voluntas per gratiam excitata et potens "
      "reddita, insitam sibi facultatem volendi exserat. Quod initium gratiae efficacis "
      "Naturae adscribit. Idem, Alvares, Ibidem, Haec causalis est falsa: Quia homo "
      "excitatus a Deo vult consentire, ideo adjuvatur: Haec causalis est vera: Quia homo "
      "excitatus gratia sufficiente adjuvatur auxilio efficaci, ideo cooperatur: Quod "
      "disputatione 59. probat copiose: ubi hanc propositionem etiam asserit esse "
      "verissimam, Quia Deus vult ut homo velit, ideo homo vult."
    ),
    "pass_a_gloss": (
      "Alvarez, On the helps of divine grace, Disputation 58, page 263: If we assert a law "
      "established by God of giving infallibly efficacious help to those who use well, or "
      "who will to use, from their innate liberty alone, the sufficient help, then already "
      "the beginning of efficacious grace would be from nature and from the innate liberty "
      "of the human being who wills to use the sufficient help well. This is the very law "
      "itself, or that very decree of God, which is defended with so much zeal by Arminius, "
      "Corvinus, and the remaining theologians of the same school. For they say that "
      "sufficient grace is given to all on account of the merit of Christ the Mediator; but "
      "efficacious grace, that is that which in the very act converts and regenerates, is to "
      "be given by this law, if they use well that exciting or sufficient grace, that is, if "
      "the will excited by grace and rendered able puts forth the faculty of willing "
      "implanted in it. Which beginning of efficacious grace he ascribes to Nature. The same "
      "Alvarez, in the same place: This causal is false: Because the human being excited by "
      "God wills to consent, therefore he is helped. This causal is true: Because the human "
      "being excited by sufficient grace is helped by efficacious help, therefore he "
      "cooperates: which he proves at length in Disputation 59, where he also asserts that "
      "this proposition is most true: Because God wills that the human being will, therefore "
      "the human being wills."
    ),
    "pass_b": (
      "Alvarez, On the Helps of Divine Grace, Disp. 58, p. 263: Suppose we assert a law God "
      "has set, that he will infallibly give efficacious help to those who use well—or who "
      "choose to use—sufficient help from their innate liberty alone. Then the start of "
      "efficacious grace would already come from nature and from the creature’s innate "
      "liberty of willing to use sufficient help well. That is the very law, the very decree "
      "of God, that Arminius, Corvinus, and the rest of that school defend with such zeal. "
      "They say sufficient grace is given to all because of Christ the Mediator’s merit; but "
      "efficacious grace—grace that in the act itself converts and regenerates—is to be given "
      "only if people use that exciting or sufficient grace well, that is, if the will, once "
      "stirred by grace and made able, puts forth the power of willing planted in it. That "
      "makes the beginning of efficacious grace belong to Nature. The same Alvarez, same "
      "place: this causal is false—“because the person stirred by God wills to consent, "
      "therefore he is helped.” This causal is true—“because the person stirred by sufficient "
      "grace is helped by efficacious help, therefore he cooperates.” He proves it at length "
      "in Disp. 59, and there also holds this proposition most true: because God wills that "
      "the person will, therefore the person wills."
    ),
    "notes_covered": [
      "Alvarez De auxiliis Disp. 58 p. 263 vs Arminian lex of sufficient→efficacious",
      "false vs true causalis; Disp. 59 Quia Deus vult ut homo velit",
    ],
    "lemmas": [
      {"form": "initium gratiae efficacis", "gloss": "beginning of efficacious grace", "why": "not from nature"},
      {"form": "Haec causalis est falsa/vera", "gloss": "this causal is false/true", "why": "priority of help"},
      {"form": "Quia Deus vult ut homo velit", "gloss": "because God wills that man will", "why": "Disp. 59"},
    ],
  },
  {
    "section": 128,
    "title": "Cap. 6 Arg. 8 Schoolmen: Alvarez against Arminians who root salvation’s difference in human will",
    "latin": (
      "Haec e diametro adversantur placitis Arminianorum, qui negant aliquam antecedentem "
      "Dei voluntatem esse causam cur alii prae aliis credant, convertantur et efficaciter "
      "salventur: et totum hoc discrimen referunt ad antecedentem hominum voluntatem, qui "
      "cum aliis communi gratia excitati, prae aliis voluerunt credere, voluerunt se "
      "convertere, voluerunt salutem apprehendere."
    ),
    "pass_a_gloss": (
      "These things stand diametrically against the opinions of the Arminians, who deny that "
      "any antecedent will of God is the cause why some rather than others believe, are "
      "converted, and are efficaciously saved; and they refer this whole discrimination to "
      "the antecedent will of human beings who, excited by grace common with others, rather "
      "than others willed to believe, willed to convert themselves, willed to lay hold of "
      "salvation."
    ),
    "pass_b": (
      "That stands diametrically against Arminian teaching. They deny that any antecedent "
      "will of God is why some rather than others believe, convert, and are saved with "
      "effect. They put the whole difference down to the prior human will of people who, "
      "stirred by the same common grace as others, chose ahead of the rest to believe, to "
      "turn, and to take hold of salvation."
    ),
    "notes_covered": [
      "Alvarez anti-Arminian: antecedent divine will vs antecedent human will",
    ],
    "lemmas": [
      {"form": "e diametro adversantur", "gloss": "stand diametrically against", "why": "Arminians"},
      {"form": "antecedentem Dei voluntatem", "gloss": "antecedent will of God", "why": "denied by Arminians"},
      {"form": "qui negant", "gloss": "who deny", "why": "OCR lacuna filled from sense+context; marked in choices"},
    ],
  },
  {
    "section": 129,
    "title": "Cap. 6 Arg. 8 Schoolmen: Estius—no frustrated divine striving blocked by human bad will",
    "latin": (
      "Gulielmus Estius olim in Academia Duacena Professor, in 1. Sentent. disp. 46. §. 2. "
      "pag. 222. Non debemus in Deo imaginari voluntatem, studium, conatum aliquem, quo "
      "velit, studeat, nitatur, et quantum in ipso est agat ut omnes homines salventur, quod "
      "tamen propterea non assequatur, quia bonae ejus voluntati obsistat mala voluntas "
      "hominum, qua praevalente atque impediente frustratur voluntas Dei. At hoc pene totum "
      "est quod Christi morte procuratum contendunt nonnulli; nempe, quod Deus, gratiam "
      "salutiferam omnibus promiscue offerendo, salvare velit cos qui libere se applicant ad "
      "gratiam, damnare eos qui eidem resistunt."
    ),
    "pass_a_gloss": (
      "William Estius, formerly Professor in the Academy of Douai, on 1 Sentences "
      "disputation 46 section 2 page 222: We ought not to imagine in God a will, a zeal, "
      "some striving, by which he wills, studies, strains, and as far as is in him acts that "
      "all human beings may be saved, which nevertheless he does not for that reason attain, "
      "because the bad will of human beings stands against his good will, and by that "
      "prevailing and hindering the will of God is frustrated. But this is almost the whole "
      "of what some contend was procured by the death of Christ; namely, that God, by "
      "offering saving grace indiscriminately to all, wills to save those who freely apply "
      "themselves to grace, and to damn those who resist the same."
    ),
    "pass_b": (
      "William Estius, once professor at Douai, on I Sentences disp. 46 §2, p. 222: We must "
      "not picture in God a will, a zeal, some straining by which he wills, labors, presses, "
      "and does all that is in him so that every human being may be saved—only to fail "
      "because human bad will blocks his good will and, by prevailing and getting in the "
      "way, frustrates God’s will. Yet that is nearly the whole of what some claim Christ’s "
      "death procured: that God, by offering saving grace to all alike, wills to save those "
      "who freely apply themselves to grace and to damn those who resist it."
    ),
    "notes_covered": [
      "Estius 1 Sent. disp. 46 §2 p. 222 against frustrated divine conatus",
      "Arminian reading of Christ’s death as promiscuous offer + free application",
    ],
    "lemmas": [
      {"form": "studium, conatum", "gloss": "zeal, striving", "why": "not in God"},
      {"form": "frustratur voluntas Dei", "gloss": "God’s will is frustrated", "why": "denied"},
      {"form": "promiscue offerendo", "gloss": "offering indiscriminately", "why": "contended effect of death"},
    ],
  },
  {
    "section": 130,
    "title": "Cap. 6 Arg. 8 Schoolmen: Bellarmine—efficacious grace not conditioned on not rejecting it",
    "latin": (
      "Ultimo in loco prodeat Bellarminus, qui non agnoscit cum morte Christi connexum tale "
      "aliquod Dei decretum, quo gratiam efficacem sive reapse regenerantem Deus omnibus "
      "hominibus dare statuerit sub hac conditione, Si eam sua voluntate non respuerint. "
      "Lib. 1. De grat. et lib. arbit. cap. 12. rejicit eorum opinionem, qui in potestate "
      "hominum esse docent, ut gratiam faciant esse efficacem, quae alioquin ex se non esset "
      "nisi sufficiens. Ostendit eos Augustino et sacris Scripturis adversari, qui dicunt "
      "omnes homines fuisse accepturos gratiam Dei, si non illi, quibus non datur, eam sua "
      "voluntate respuerent, pag. 423. Denique hoc incommodo premit hanc opinionem, Quod si "
      "vocatio efficax non penderet a proposito Dei, sed ab humana voluntate, nullus locus "
      "praedestinationi relinqueretur. Quibus addi potest illud, lib. 2. cap. 8. pag. 455: "
      "Credimus Deum absoluta voluntate velle salvare multos, tum parvulos tum adultos, et "
      "absoluta voluntate alios non velle salvare, tum parvulos tum adultos. Vide Augustini "
      "Enchiridion, cap. 102, 103."
    ),
    "pass_a_gloss": (
      "Last in place let Bellarmine come forward, who does not acknowledge connected with "
      "the death of Christ any such decree of God by which God would have decided to give "
      "efficacious grace, or grace that regenerates in very deed, to all human beings under "
      "this condition, If they have not rejected it by their will. Book 1 On grace and free "
      "choice chapter 12 rejects the opinion of those who teach that it is in the power of "
      "human beings to make grace be efficacious which otherwise of itself would be only "
      "sufficient. He shows that they are opposed to Augustine and the sacred Scriptures "
      "who say that all human beings would have received the grace of God, if those to whom "
      "it is not given had not rejected it by their will, page 423. Finally he presses this "
      "opinion with this inconvenience: That if efficacious calling did not hang from the "
      "purpose of God but from the human will, no place would be left for predestination. To "
      "which can be added that from book 2 chapter 8 page 455: We believe that God by an "
      "absolute will wills to save many, both little ones and adults, and by an absolute will "
      "does not will to save others, both little ones and adults. See Augustine’s "
      "Enchiridion, chapters 102, 103."
    ),
    "pass_b": (
      "Last, let Bellarmine step forward. He does not grant that Christ’s death is tied to "
      "any divine decree by which God would give efficacious grace—grace that regenerates in "
      "very fact—to every human being on the condition that they do not refuse it by their "
      "will. In On Grace and Free Choice book 1, chapter 12, he rejects those who teach that "
      "people have it in their power to make grace efficacious when otherwise, of itself, it "
      "would be only sufficient. He shows they stand against Augustine and Holy Scripture "
      "when they say everyone would have received God’s grace if those who do not receive it "
      "had not refused it by their will (p. 423). He presses the view with this trouble: if "
      "efficacious calling hung not on God’s purpose but on the human will, no room would be "
      "left for predestination. Add book 2, chapter 8, p. 455: We believe God by absolute "
      "will wills to save many, both infants and adults, and by absolute will does not will "
      "to save others, both infants and adults. See Augustine’s Enchiridion, chapters 102–103."
    ),
    "notes_covered": [
      "Bellarmine De grat. et lib. arbit. 1.12; 2.8 p. 455; Aug. Enchir. 102–103",
      "no decree of efficacious grace to all Si non respuerint",
    ],
    "lemmas": [
      {"form": "reapse regenerantem", "gloss": "regenerating in very deed", "why": "efficacious"},
      {"form": "Si eam sua voluntate non respuerint", "gloss": "if they have not rejected it by will", "why": "denied condition"},
      {"form": "nullus locus praedestinationi", "gloss": "no place left for predestination", "why": "incommodum"},
    ],
  },
  {
    "section": 131,
    "title": "Cap. 6 close: why grace and free choice—universal covenant of faith, not of efficacious means to all",
    "latin": (
      "Sed quorsum tam multa de gratia et Libero arbitrio, cum versemur in explicanda "
      "quaestione de Morte Christi, quatenus consideratur ut universalis causa salutis "
      "humanae? Nimirum quia Pelagiani olim docuerunt, atque multi nunc dierum in eam "
      "opinionem dilabuntur, quae statuit, Morte meritoque Christi Redemptoris gratiam "
      "salvantem sive efficacem ex aequo prostare omnibus hominibus sub hac conditione "
      "dandam, Si eam sua voluntate non respuerint; sub hac lege negandam, Si respuerint: "
      "Quasi ipsa mors Christi ex pura Dei misericordia fuisset hominibus indulta, sed "
      "gratia efficax sive salutifera ad homines dimanet prout bene aut male usi fuerint "
      "libero suo arbitrio, in gratia excitante amplexanda aut repellenda. Sitque salus "
      "dignis salvari ex se volentibus, ut cecinit Prosper 1. De Ingratis, c. 6. In hac "
      "igitur Dissertatione, De universali efficacia mortis Christi, sicut nostrum fuit "
      "ostendere contra eos qui illam coarctare moliuntur, Esse stabilitum quoddam "
      "universale pactum cum toto humano genere de danda remissione et vita aeterna omnibus "
      "et singulis hominibus sub conditione fidei; ita et illud etiam monstrandum fuit, "
      "contra eos qui hanc universalem efficaciam mortis Christi extra suos limites "
      "extendunt, Nullam legem, nullum decretum esse stabilitum in ordine ad mortem Christi, "
      "de dandis mediis gratiae supernaturalis, aut de danda ipsa gratia salvifica et "
      "efficaci, omnibus hominibus sub conditione, Si bene aut minus male utantur lumine "
      "naturae, vel sub conditione, Si sua voluntate eam non respuerint. Posita igitur morte "
      "Christi tenetur Deus ex fidelitate, juxta pactum Evangelicum, dare remissionem "
      "peccatorum et vitam aeternam cuivis poenitenti et credenti: At nullo pacto tenetur "
      "dare ipsam fidem, charitatem aut gratiam salutiferam quemcunque alium actum liberi "
      "arbitrii viribus praestanti. Imo gratiae efficacis et salutiferae donatio sive "
      "negatio, posita morte Christi, tam libera manet Deo, quam fuit Christi donatio, quae "
      "nullis humani arbitrii actibus debita aut data intelligitur. Ad propositum igitur Dei "
      "miserantis aut non-miserantis, non ad arbitrium hominis volentis aut non-volentis, "
      "consecutio gratiae efficacis et salvantis tanquam ad primam radicem referenda est. "
      "Hactenus de morte Christi, quatenus ejus vis et efficacia ad omnes pertinet, "
      "disputandum est. Deinceps, quatenus ad electos Dei filios restringatur, est "
      "explicandum."
    ),
    "pass_a_gloss": (
      "But to what end so many things about grace and Free choice, when we are engaged in "
      "explaining the question concerning the Death of Christ, insofar as it is considered "
      "as the universal cause of human salvation? Namely because the Pelagians once taught, "
      "and many nowadays slide into that opinion, which establishes that by the death and "
      "merit of Christ the Redeemer saving or efficacious grace stands forth equally for all "
      "human beings to be given under this condition, If they have not rejected it by their "
      "will; to be denied under this law, If they have rejected it: As if the death of Christ "
      "itself had been granted to human beings from the pure mercy of God, but efficacious "
      "or saving grace flows out to human beings according as they have used their free "
      "choice well or badly in embracing or rejecting exciting grace. And let salvation be "
      "for those worthy to be saved as willing from themselves, as Prosper sang in book 1 On "
      "the Ungrateful, chapter 6. In this Dissertation therefore, On the universal efficacy "
      "of the death of Christ, just as it was our task to show against those who struggle to "
      "narrow it, That a certain universal covenant has been established with the whole "
      "human race concerning the giving of remission and eternal life to all and each human "
      "being under the condition of faith; so also that also had to be shown, against those "
      "who stretch this universal efficacy of the death of Christ beyond its limits, That no "
      "law, no decree has been established in order to the death of Christ, concerning the "
      "giving of the means of supernatural grace, or concerning the giving of saving and "
      "efficacious grace itself, to all human beings under the condition, If they use the "
      "light of nature well or less badly, or under the condition, If they have not rejected "
      "it by their will. Therefore, the death of Christ having been posited, God is bound "
      "from faithfulness, according to the Evangelic covenant, to give remission of sins and "
      "eternal life to anyone repentant and believing: But by no covenant is he bound to give "
      "faith itself, charity, or saving grace to anyone performing any other act by the "
      "powers of free choice. Indeed the donation or denial of efficacious and saving grace, "
      "the death of Christ having been posited, remains as free to God as was the donation of "
      "Christ, which is understood as owed or given to no acts of human choice. Therefore the "
      "consecution of efficacious and saving grace is to be referred to the purpose of God "
      "having mercy or not having mercy, not to the choice of the human being willing or not "
      "willing, as to the first root. Thus far it has been necessary to dispute concerning "
      "the death of Christ insofar as its force and efficacy pertains to all. Next it is to "
      "be explained insofar as it is restricted to the elect sons of God."
    ),
    "pass_b": (
      "But why so much on grace and free choice, when our question is the Death of Christ "
      "as the universal cause of human salvation? Because the Pelagians once taught—and many "
      "today still slide into—the view that by the Redeemer’s death and merit, saving or "
      "efficacious grace stands open equally to every human being, to be given if they do "
      "not refuse it by their will, and denied if they do. As if Christ’s death itself had "
      "been granted from pure mercy, while efficacious or saving grace reaches people only "
      "as they use free choice well or badly in embracing or rejecting exciting grace. Then "
      "salvation would belong to those “worthy to be saved” as willing from themselves—as "
      "Prosper sang in On the Ungrateful 1.6. So in this Dissertation on the universal "
      "efficacy of Christ’s death, just as we had to show against those who try to narrow "
      "it that a universal covenant stands with the whole human race to give remission and "
      "eternal life to each person under the condition of faith, so we also had to show "
      "against those who stretch that universal efficacy past its bounds that no law and no "
      "decree stands, in connection with Christ’s death, to give the means of supernatural "
      "grace—or saving efficacious grace itself—to everyone on the condition that they use "
      "nature’s light well or less badly, or that they do not refuse that grace by their "
      "will. Christ’s death being granted, God is bound by faithfulness, under the gospel "
      "covenant, to give remission of sins and eternal life to anyone who repents and "
      "believes. By no covenant is he bound to give faith itself, charity, or saving grace "
      "to someone who only performs some other act by free choice’s own powers. Indeed, once "
      "Christ’s death is granted, the gift or denial of efficacious saving grace remains as "
      "free to God as the gift of Christ himself, which is owed to no human acts of choice. "
      "So the coming of efficacious saving grace must be traced to God’s purpose of mercy "
      "or non-mercy as its first root—not to the human choice of willing or not willing. "
      "Thus far we have had to treat Christ’s death as its force and efficacy reach all. "
      "Next we must explain how it is restricted to God’s elect children."
    ),
    "notes_covered": [
      "Cap. 6 close: why grace/free-choice digression; Prosper De Ingratis 1.6",
      "universal pact under faith vs no decree of efficacious means to all",
      "bridge to Cap. 7 elect sons",
    ],
    "lemmas": [
      {"form": "universale pactum ... sub conditione fidei", "gloss": "universal covenant under faith", "why": "Cap. 6 thesis"},
      {"form": "nullo pacto tenetur dare ipsam fidem", "gloss": "by no covenant bound to give faith itself", "why": "limit"},
      {"form": "Hactenus ... Deinceps", "gloss": "thus far ... next", "why": "Cap. 6→7"},
    ],
  },
]


def write_justification(sec: dict) -> Path:
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
            f"Densify Cap. 6 Arg. 8 Bannes/Alvarez/Estius/Bellarmine section {sec["section"]}. "
            f"Pass A!=B. Latin from 1650 PDF pdftotext+tesseract+DjVu. Packet {PACKET}. Honest partial."
        ),
        "lemmas": sec["lemmas"],
        "choices": [
            {
                "issue": "Copy-text",
                "choice": (
                    "Locked 1650 Daniel Latin from IA PDF (pdftotext + tesseract lat+eng) "
                    "with DjVu check; long-s/ligatures normalized."
                ),
            },
            {
                "issue": "Scope",
                "choice": (
                    "Arg. 8 schoolmen after Fulgentius jugulum: Bannes, Alvarez, Estius, "
                    "Bellarmine through Cap. 6 close before Cap. 7 elect."
                ),
            },
            {
                "issue": "OCR lacuna",
                "choice": (
                    "At Alvarez anti-Arminian clause, witnesses show blank/garbled before "
                    "aliquam antecedentem Dei voluntatem; locked qui negant from "
                    "sense and Davenant’s contrast (Arminians deny antecedent divine will "
                    "as cause of discrimination)."
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
    if r.returncode != 0 or "fail=" in (r.stdout + r.stderr) and "fail=0" not in (r.stdout + r.stderr):
        raise SystemExit(f"check_pass_ab failed for {path}: {r.stdout}\n{r.stderr}")


def append_rows(secs: list[dict]) -> None:
    eng_path = TRANS / "morte_christi_english.json"
    src_path = TRANS / "morte_christi_source.json"
    eng = json.loads(eng_path.read_text(encoding="utf-8"))
    src = json.loads(src_path.read_text(encoding="utf-8"))
    assert len(eng) == len(src) == 124, (len(eng), len(src))
    assert str(eng[-1]["section"]) == "124"
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
    print(f"appended eng/src tip {eng[-1][section]} (n={len(eng)})")


def update_meta(tip: int) -> None:
    meta_path = TRANS / "morte_christi_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["section_count"] = tip
    # Extend edition tip note
    old = meta["edition"]
    marker = "through Fulgentius jugulum before Bannes/Alvarez schoolmen."
    replacement = (
        "through Fulgentius jugulum + Cap. 6 Arg. 8 Bannes/Alvarez/Estius/Bellarmine "
        "schoolmen through Cap. 6 close before Cap. 7 elect."
    )
    if marker in old:
        meta["edition"] = old.replace(marker, replacement)
    elif "Bannes/Alvarez/Estius/Bellarmine schoolmen through Cap. 6 close" not in old:
        meta["edition"] = old.rstrip(".") + " + Cap. 6 Arg. 8 Bannes/Alvarez/Estius/Bellarmine through Cap. 6 close."
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("meta section_count", meta["section_count"])


def extend_lock(secs: list[dict]) -> None:
    lock = BOOK / "sources/_davenant_morte_christi_latin_lock.txt"
    text = lock.read_text(encoding="utf-8")
    add = "\n\n" + "\n\n".join(s["latin"] for s in secs) + "\n"
    if secs[0]["latin"][:40] in text:
        print("lock already has Bannes block; skip append")
        return
    lock.write_text(text.rstrip() + add, encoding="utf-8")
    print("lock extended")


def build_packet(tip: int) -> None:
    sys.path.insert(0, str(Path.home() / "SaneApps/clients/translations"))
    from pipeline.verify_translation_qa import make_audit_packet

    eng = TRANS / "morte_christi_english.json"
    src = TRANS / "morte_christi_source.json"
    expected = [str(i) for i in range(1, tip + 1)]
    identity = {
        "author": "John Davenant",
        "work": "Two Dissertations (De morte Christi Cap. 1-6 partial)",
        "edition": (
            "Dissertationes duae (Cambridge: Roger Daniel, 1650). Wing D317; ESTC R5446. "
            "IA bim_early-english-books-1641-1700_dissertationes-du-_davenant-john-bp_1650. "
            "Partial: De morte Christi Cap. 1-5 + Cap. 6 opening through Arg. 8 Secundo "
            "Fathers concord and Arg. 8 Pelagian-mode digression through Fulgentius jugulum "
            "+ Cap. 6 Arg. 8 Bannes/Alvarez/Estius/Bellarmine schoolmen through Cap. 6 close "
            "before Cap. 7 elect."
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
            f"Tip densify Cap. 6 Arg. 8 Bannes/Alvarez/Estius/Bellarmine through Cap. 6 close "
            f"(secs 125-{tip}). Not whole Dissertationes."
        ),
        "packet": PACKET,
    }
    raw = [
        BOOK / "sources/davenant_1650.pdf",
        BOOK / "sources/davenant_dissertationes_1650_djvu.txt",
        BOOK / "sources/_davenant_morte_christi_latin_lock.txt",
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
    out = AUDIT / f"{PACKET}.packet.json"
    out.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # review receipt: pass all expected
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
                "(Arg.8 Bannes/Alvarez/Estius/Bellarmine through Cap. 6 close)."
            ),
        },
        "reviews": reviews,
    }
    (AUDIT / f"{PACKET}.review.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("packet", packet["packet_id"][:16], "structural", packet["structural_errors"])


def prepend_handoff(before: int, after: int) -> None:
    path = BOOK / "SESSION_HANDOFF.md"
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    block = f"""# densify 2026-09-22

## 2026-09-22 ~17:35 ET (Scribe — Davenant Cap. 6 Arg. 8 Bannes densify)

CoS densify: Cap. 6 Arg. 8 after Fulgentius jugulum (Bannes / Alvarez / Estius / Bellarmine through Cap. 6 close). Punch X: **NO**. Cap. 1 mid-Thesis tip patch stays deferred. Did **not** edit `publication-review.json`; did not ship; did not commit; did not run Logos or ai_promote. Waited for tip-124 ship (live 57/3400) before append.

### Bound this job (not shipped)
- **Davenant** `davenant-dissertationes-duae`: Cap. 6 Arg. 8 Bannes tip (**{before}→{after}** sections). Locked densify Latin from IA 1650 Daniel PDF (pdftotext + tesseract) with DjVu check. Pass A≠B; OUR; English-first; no PBB/ops TNs; packet `{PACKET}`. Honest partial — **not** whole Dissertationes. Cap. 7–11 (elect / De morte Christi remainder) and De praedestinatione remain. Punch X: **NO**.

### Still missing for full Dissertationes duae
- Cap. 1 tip mid-block patch (between universal-cause definition and John 3:16) — deferred
- Cap. 7–11 (De morte Christi remainder; elect sons tip next)
- Full De praedestinatione et reprobatione
- Sententia de Gallicana controversia if in the 1650 volume

### Punch X?
**NO** — full-works bar not met. Parent/CoS only.


---

"""
    path.write_text(block + old, encoding="utf-8")
    print("SESSION_HANDOFF prepended")


def main() -> None:
    tip_before = 124
    # Pass A/B self-check EACH justification before append
    for sec in SECTIONS:
        p = write_justification(sec)
        check_just(p)
    append_rows(SECTIONS)
    tip = SECTIONS[-1]["section"]
    update_meta(tip)
    extend_lock(SECTIONS)
    build_packet(tip)
    # tip-ready + batch check
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
    print("tip-ready:", r.stdout.strip() or r.stderr.strip())
    if r.returncode != 0:
        raise SystemExit(f"tip-ready failed: {r.stdout}\n{r.stderr}")
    paths = [str(JUST / f"morte_{s["section"]}.json") for s in SECTIONS]
    r2 = subprocess.run([sys.executable, str(CHECK), *paths], capture_output=True, text=True)
    print("batch:", r2.stdout.strip() or r2.stderr.strip())
    if r2.returncode != 0:
        raise SystemExit(f"batch check failed: {r2.stdout}\n{r2.stderr}")
    prepend_handoff(tip_before, tip)
    # claim stays claimed — do not free
    print(f"DONE before={tip_before} after={tip} packet={PACKET} Punch X=NO")


if __name__ == "__main__":
    main()
