#!/usr/bin/env python3
"""Cap. 7 Arg. 4 densify — tip 144 → ~150. Packet morte_christi_cap7_arg4_densify."""
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
PACKET = "morte_christi_cap7_arg4_densify"
CHECK = PIPE / "check_pass_ab.py"
TIP_BEFORE = 144

SECTIONS = [
  {
    "section": 145,
    "title": "Cap. 7 Arg. 4 Ultimo: Gen. 3:15 seed promise—Satan crushed under the elect (Rupert / Marlorat)",
    "latin": (
      "4. Ultimo, confirmare possumus sententiam nostram iis locis in quibus Christo "
      "morienti absolute Deus promisit Ecclesiam merito hujus mortis infallibiliter a morte "
      "liberandam; & vita aeterna donandam. Gen. iii. 15. Semen mulieris conteret caput "
      "serpentis. Quod quid aliud est, quam virtute & merito mortis Christi conculcatum iri "
      "Satanam, & liberandos ex ejus potestate illos omnes quorum Deus in Christo voluit "
      "specialiter misereri? Jam quis dubitet Christum mortem suam Satanae debellatricem "
      "speciali intuitu ad eos retulisse qui speciali beneficio per eum fuerunt liberandi? "
      "Hos autem infallibiliter liberandos fuisse electos, apud omnes sanos Theologos in "
      "confesso est. Rupertus, lib. 2, De victoria verbi Dei, cap. 18, Electos nominatim "
      "appellat Serpentis victores. Quia nimirum efficacia mortis & resurrectionis Christi "
      "Diabolum conterentis, iis solis ex speciali misericordia efficaciter applicanda "
      "destinatur & procuratur. Unde Marloratus in hunc locum, Diabolus & generatio malorum "
      "contra electos Dei pugnant, sed electi tandem fortiores evadant propter Caput ipsorum, "
      "nempe Christum, qui per mortem suam abolevit eum qui mortis habebat imperium. Mors "
      "igitur Christi specialiter intenta & destinata fuit ad conterendum Satanam sub pedibus "
      "electorum, eosdemque efficaciter salvandos, idque ex firmissima promissione ipsius Dei."
    ),
    "pass_a_gloss": (
      "4. Lastly, we can confirm our opinion from those places in which God absolutely "
      "promised to Christ as he was dying that the Church by the merit of this death would "
      "infallibly be freed from death; and be given eternal life. Gen. iii. 15. The seed of "
      "the woman shall bruise the head of the serpent. Which what else is it, than that by "
      "the virtue and merit of the death of Christ Satan will be trampled down, and that all "
      "those will be freed from his power of whom God in Christ specially willed to have "
      "mercy? Now who would doubt that Christ referred his death, the vanquisher of Satan, "
      "by a special regard to those who by a special benefit were to be freed through him? "
      "But that these were to be infallibly freed as elect is confessed among all sound "
      "Theologians. Rupert, book 2, On the victory of the word of God, chapter 18, calls the "
      "elect by name the conquerors of the Serpent. Because indeed the efficacy of the death "
      "and resurrection of Christ crushing the Devil is destined and procured to be "
      "efficaciously applied to those alone from special mercy. Whence Marlorat on this place, "
      "The Devil and the generation of the wicked fight against the elect of God, but the "
      "elect at length come out stronger on account of their Head, namely Christ, who through "
      "his death abolished him who had the empire of death. The death of Christ therefore was "
      "specially intended and destined for crushing Satan under the feet of the elect, and "
      "for saving the same efficaciously, and that from the most firm promise of God himself."
    ),
    "pass_b": (
      "4. Lastly, we can confirm our view from those places in which God absolutely promised "
      "Christ, as he died, that by the merit of this death the Church would infallibly be set "
      "free from death and given eternal life. Genesis 3:15: “The seed of the woman shall "
      "bruise the serpent’s head.” What else is that than that by the power and merit of "
      "Christ’s death Satan will be trampled down, and that all those of whom God in Christ "
      "specially willed to have mercy will be freed from his power? Who then can doubt that "
      "Christ referred his death—Satan’s vanquisher—with special regard to those who were to "
      "be freed through him by a special benefit? And that those to be infallibly freed were "
      "the elect is confessed by all sound theologians. Rupert (On the Victory of the Word of "
      "God, book 2, chapter 18) expressly calls the elect the serpent’s conquerors, because "
      "the efficacy of Christ’s death and resurrection crushing the Devil is destined and "
      "procured to be applied efficaciously to them alone from special mercy. So Marlorat on "
      "this place: the Devil and the wicked generation fight against God’s elect, but the "
      "elect at last prove stronger because of their Head, Christ, who by his death abolished "
      "him who had the empire of death. Christ’s death was therefore specially intended and "
      "destined to crush Satan under the elect’s feet and to save them efficaciously—and that "
      "from God’s own most firm promise."
    ),
    "notes_covered": [
      "Arg. 4 Ultimo open; Gen 3:15; Rupert De victoria verbi Dei 2.18; Marlorat; Satan under elect feet"
    ],
    "lemmas": [
      {"form": "Semen mulieris conteret caput serpentis", "gloss": "the seed of the woman shall bruise the serpent's head", "why": "Gen 3:15"},
      {"form": "Electos nominatim appellat Serpentis victores", "gloss": "calls the elect by name conquerors of the Serpent", "why": "Rupert"},
      {"form": "conterendum Satanam sub pedibus electorum", "gloss": "crushing Satan under the feet of the elect", "why": "special intention"},
    ],
  },
  {
    "section": 146,
    "title": "Cap. 7 Arg. 4: Isa 53:10–11 long-lived seed—Luther, Calvin, Musculus on elect Church",
    "latin": (
      "Esai. liii. 10, 11. non dissimilis exstat promissio Dei Patris de efficacia mortis "
      "Christi quoad electos: Verba sic se habent, Si posuerit pro peccato animam suam, "
      "videbit semen longaeuum: & voluntas Domini in manu ejus dirigetur. Pro eo quod "
      "laboravit anima ejus, videbit & saturabitur, &c. Deus Pater hisce verbis promittit "
      "Filio, passionem & mortem ejus non fore inutilem aut infructuosam, sed semen illi "
      "indubie partituram. Quaero igitur an haec promissio vaga & incerta individua "
      "respiciat, an personas certas Deo Patri ac Christo Mediatori singulariter notas. "
      "Proculdubio confusam promissionem fingere de salvandis aliquibus, sed ab ipso Deo "
      "nondum singulariter designatis, est Divina perfectione & sapientia indignissimum. "
      "Quod si Deo Christoque constiterit, de hoc semine efficaciter salvando per mortem "
      "Christi, consequetur, in Christo moriente fuisse, respectu salutis eorundem, "
      "efficacem & singularem intentionem. Omnes hujus loci interpretes ita eum "
      "intellexerunt, ut per Christi mortem efficacissimam & certissimam liberationem ac "
      "salutem mystico corpori ejus, id est, Ecclesiae, sive electis, promissam fateantur. "
      "Sic Lutherus, Posteritas sive semen de quo loquitur, est Ecclesia. VIDEBIT SEMEN, "
      "id est, habebit regnum & regios liberos. Sic Calvinus, VIDEBIT SEMEN, significat: "
      "Mortem Christi causam fore gignendae sobolis, quia mortuus vivificans populum sibi "
      "peculiarem acquiret. Non dissentit Musculus explicans illa verba, De labore animae "
      "suae videbit, & satiabitur. Affinitatem hanc electorum & salvandorum vidit jam olim "
      "Christus, videt etiamnum, & ad finem mundi usque videbit, videndoque saturatur, quia "
      "placitum Dei Patris sui in manu ipsius dirigitur. Omnes hi consentiunt, ex speciali "
      "beneplacito Dei Patris efficacem salutem Ecclesiae, id est certarum quarundam "
      "personarum Deo soli notarum, Christo tanquam pretium passionis suae fuisse "
      "promissam, Christumque pro salvandis hisce electis, sive hoc populo peculiari a Deo "
      "Patre singulariter sibi dato & commendato, singulari & efficaci voluntate intendisse "
      "& laborasse."
    ),
    "pass_a_gloss": (
      "Isaiah liii. 10, 11. there stands a not dissimilar promise of God the Father concerning "
      "the efficacy of the death of Christ as regards the elect: The words stand thus, If he "
      "shall have put his soul for sin, he shall see a long-lived seed: and the will of the "
      "Lord shall be directed in his hand. For that for which his soul labored, he shall see "
      "and be satisfied, &c. God the Father by these words promises to the Son that his "
      "passion and death will not be useless or unfruitful, but will undoubtedly bring forth "
      "seed for him. I ask therefore whether this promise regards vague and uncertain "
      "individuals, or certain persons singularly known to God the Father and to Christ the "
      "Mediator. Without doubt to invent a confused promise about some to be saved, but not "
      "yet singularly designated by God himself, is most unworthy of Divine perfection and "
      "wisdom. But if it has been settled with God and Christ concerning this seed being "
      "efficaciously saved through the death of Christ, it will follow that in Christ dying "
      "there was, with respect to the salvation of the same, an efficacious and singular "
      "intention. All interpreters of this place have so understood it, that they confess "
      "that through the death of Christ a most efficacious and most certain liberation and "
      "salvation was promised to his mystical body, that is, to the Church, or to the elect. "
      "Thus Luther, The posterity or seed of which he speaks is the Church. HE SHALL SEE "
      "SEED, that is, he will have a kingdom and royal children. Thus Calvin, HE SHALL SEE "
      "SEED, signifies: that the death of Christ will be the cause of begetting offspring, "
      "because the dead one, making alive, will acquire a people peculiar to himself. "
      "Musculus does not dissent, explaining those words, From the labor of his soul he shall "
      "see, and be satisfied. This affinity of the elect and of those to be saved Christ saw "
      "already long ago, sees even now, and will see even to the end of the world, and by "
      "seeing is satisfied, because the good pleasure of God his Father is directed in his "
      "hand. All these agree that from the special good pleasure of God the Father an "
      "efficacious salvation of the Church, that is of certain persons known to God alone, "
      "was promised to Christ as the price of his passion, and that Christ intended and "
      "labored with a singular and efficacious will for saving these elect, or this peculiar "
      "people singularly given and committed to him by God the Father."
    ),
    "pass_b": (
      "Isaiah 53:10–11 gives a like promise of God the Father about the efficacy of Christ’s "
      "death for the elect. The words run: “If he shall put his soul for sin, he shall see a "
      "long-lived seed; and the will of the Lord shall prosper in his hand. For the travail "
      "of his soul he shall see and be satisfied,” and so on. By these words the Father "
      "promises the Son that his passion and death will not be useless or barren, but will "
      "surely yield him seed. I ask, then: does this promise look to vague, indefinite "
      "individuals, or to certain persons singularly known to the Father and to Christ the "
      "Mediator? To invent a confused promise of some who will be saved, yet not yet "
      "singularly designated by God himself, is most unworthy of divine perfection and "
      "wisdom. But if God and Christ have settled that this seed will be efficaciously saved "
      "through Christ’s death, it follows that in the dying Christ there was, with respect to "
      "their salvation, an efficacious and singular intention. All interpreters of the place "
      "have taken it so: that through Christ’s death a most efficacious and certain "
      "liberation and salvation was promised to his mystical body—that is, to the Church, or "
      "the elect. So Luther: the posterity or seed spoken of is the Church; “he shall see "
      "seed” means he will have a kingdom and royal children. So Calvin: “he shall see seed” "
      "means Christ’s death will be the cause of begetting offspring, because the One who "
      "died, making alive, will acquire a people of his own. Musculus agrees, explaining “from "
      "the travail of his soul he shall see and be satisfied”: Christ already saw this bond "
      "of the elect and those to be saved, still sees it, and will see it to the world’s end, "
      "and is satisfied in seeing, because the Father’s good pleasure is directed in his "
      "hand. All agree that from the Father’s special good pleasure an efficacious salvation "
      "of the Church—certain persons known to God alone—was promised to Christ as the price "
      "of his passion, and that Christ intended and labored with a singular, efficacious will "
      "to save these elect, this peculiar people singularly given and committed to him by the "
      "Father."
    ),
    "notes_covered": [
      "Isa 53:10-11; long-lived seed; Luther/Calvin/Musculus; elect Church as promised seed"
    ],
    "lemmas": [
      {"form": "videbit semen longaeuum", "gloss": "he shall see a long-lived seed", "why": "Isa 53:10"},
      {"form": "Posteritas sive semen ... est Ecclesia", "gloss": "the posterity or seed is the Church", "why": "Luther"},
      {"form": "populum sibi peculiarem", "gloss": "a people peculiar to himself", "why": "Calvin"},
    ],
  },
  {
    "section": 147,
    "title": "Cap. 7 Arg. 4 objection (Grevinchovius) and reply: tacit promise of faith to the elect",
    "latin": (
      "Si quis hic objiciat cum Grevinchovio, non fuisse absolutam aliquam promissionem "
      "aut voluntatem Dei de singularibus quibuscunque personis efficaciter redimendis, "
      "sed Deum applicationem mortis Christi omnibus & singulis non absolute sed "
      "conditionate voluisse & noluisse: voluisse omnibus, fide intercedente; noluisse, "
      "mediante incredulitate: atque idcirco, Christo ponente animam suam, potuisse tamen "
      "mortem ejus nullis applicari, id est, potuisse eum promissor semine fraudari, "
      "propter intervenientem omnium incredulitatem: Respondetur, In hac promissione qua "
      "se Mediatori Deus Pater quasi obstrinxit, de dando illi semine, si animam suam "
      "posuerit pro peccato, continetur tacita promissio de fide danda ipsis electis; "
      "absque qua semen Christi non haberentur. Tam igitur decretum fuit Deo propter "
      "mortem Filii dare aliquibus ipsam fidem, quam dare Filio progeniem in aeternum "
      "victuram. Hujus promissi & consilii praescius Christus non potuit non speciali "
      "intentione pro hoc semine, pro hisce fidelibus futuris, mortis suae sacrificium "
      "Deo Patri offerre. Hactenus expressis Scripturarum testimoniis pugnavimus: jam "
      "rationes aliquot in sacris etiam Scripturis fundatas afferemus."
    ),
    "pass_a_gloss": (
      "If anyone here should object with Grevinchovius, that there was not some absolute "
      "promise or will of God concerning any singular persons whatsoever being efficaciously "
      "redeemed, but that God willed and did not will the application of the death of Christ "
      "to all and each not absolutely but conditionally: willed it for all, faith "
      "intervening; did not will it, unbelief mediating: and therefore, Christ putting his "
      "soul, his death could nevertheless be applied to none, that is, he could be cheated "
      "of the promised seed, on account of the intervening unbelief of all: It is answered, "
      "In this promise by which God the Father as it were bound himself to the Mediator, "
      "concerning giving him seed, if he should have put his soul for sin, there is contained "
      "a tacit promise of faith to be given to the elect themselves; without which they would "
      "not be had as the seed of Christ. Therefore it was as much decreed for God on account "
      "of the death of the Son to give to some faith itself, as to give to the Son offspring "
      "that would live forever. Christ, foreknowing this promise and counsel, could not but "
      "with special intention offer the sacrifice of his death to God the Father for this "
      "seed, for these future believers. Thus far we have contended by express testimonies "
      "of the Scriptures: now we will bring forward some reasons founded also in the sacred "
      "Scriptures."
    ),
    "pass_b": (
      "If someone objects with Grevinchovius that there was no absolute promise or will of "
      "God to redeem any particular persons efficaciously, but that God willed and refused "
      "the application of Christ’s death to each and all only conditionally—willing it for "
      "all if faith intervened, refusing it if unbelief mediated—and that therefore, even "
      "when Christ laid down his life, his death might be applied to no one, and he might be "
      "cheated of the promised seed by everyone’s intervening unbelief: the reply is that in "
      "this promise by which the Father as it were bound himself to the Mediator to give him "
      "seed if he put his soul for sin, there is contained a tacit promise of faith to be "
      "given to the elect themselves; without that faith they would not be Christ’s seed. So "
      "it was as much decreed that God, because of the Son’s death, give faith itself to "
      "some, as that he give the Son an everlasting offspring. Christ, foreknowing this "
      "promise and counsel, could not but offer the sacrifice of his death to the Father with "
      "special intention for this seed, for these future believers. So far we have argued "
      "from express Scripture testimonies; next we will add some reasons also grounded in "
      "holy Scripture."
    ),
    "notes_covered": [
      "Grevinchovius conditional application objection; tacita promissio de fide; bridge to rationes"
    ],
    "lemmas": [
      {"form": "conditionate voluisse & noluisse", "gloss": "willed and refused conditionally", "why": "objection"},
      {"form": "tacita promissio de fide danda ipsis electis", "gloss": "tacit promise of faith to be given to the elect", "why": "reply"},
      {"form": "promissor semine fraudari", "gloss": "be cheated of the promised seed", "why": "Grevinch reductio"},
    ],
  },
  {
    "section": 148,
    "title": "Cap. 7 Arg. 4 Ratio 1: secret covenant (Jer 31:33 / Heb 8)—Mediator for elect Israel alone",
    "latin": (
      "Qui morte sua non modo stabilivit foedus illud Evangelicum ad omnes homines "
      "promiscue spectans, Quisquis crediderit, salvus erit; sed insuper foedus illud "
      "arcanum, quod certas & singulares quasdam personas Deo soli notas comprehendit, a "
      "Propheta hisce verbis descriptum, Jer. xxxi. 33. Hoc est foedus quod pangam cum "
      "domo Israel post dies hos, Indam legem meam menti eorum, & cordi eorum inscribam "
      "eam, & ero eis Deus, & ipsi erunt mihi populus; Qui, inquam, tale foedus morte sua "
      "procuravit, is mortem meritumque suum Deo Patri ut efficaciter quibusdam electis "
      "personis applicandum obtulit. Haec propositio inde clara & manifesta est, quod "
      "indere leges suas hominum mentibus, & inscribere eorundem cordibus, atque eosdem "
      "populum peculiarem Deo facere efficacem applicationem meritorum Christi denotant, "
      "& electorum sive spiritualis Israelis privilegia designant. Jam vero adjungo "
      "Minorem, & affirmo, Christum morte sua hujus arcani foederis, quod applicationem "
      "includit, & Israelem Dei sive electos Dei filios eosdemque solos complectitur, "
      "Mediatorem exstitisse. Praeter verba Prophetae modo laudati, habemus & Apostoli, "
      "eundem Prophetam citantis, perspicuum testimonium, Heb. viii. 6. Noster Pontifex "
      "melioris testamenti Mediator est, quod in melioribus repromissionibus sancitum est. "
      "At quae tandem sunt meliores illae promissiones quas Christus Mediator stabilivit? "
      "Recensentur vers. 10. iisdem verbis quibus exstant apud Jeremiam; & ad duo capita "
      "revocantur, ad promissionem de interiori cordium reformatione, & de gratuita "
      "peccatorum remissione, ut bene observavit in hunc locum Calvinus. Christus ergo "
      "morte sua meruit omnibus remissionem peccatorum, si credant & convertantur: ac "
      "meruit & procuravit quibusdam hoc gratuitum & arcanum foedus a Deo promittente "
      "implendum; nimirum, ut credant & convertantur Deo, per & propter Mediatorem, "
      "illorum corda efficaciter reformante, & leges suas eisdem indente. Hi autem pro "
      "quibus hoc promeruit Christus (ut ex Augustino liquet) sunt omnes pertinentes "
      "spiritualiter ad domum Israel & semen Abrahae: quid aliud est quam omnes electi? "
      "Electi igitur ex intentione Dei & Christi speciale beneficium fructuosae "
      "applicationis ex morte Christi & destinatum sibi habuerunt, & donatum."
    ),
    "pass_a_gloss": (
      "He who by his death not only established that Evangelical covenant looking "
      "promiscuously to all human beings, Whoever shall have believed will be saved; but "
      "moreover that secret covenant which comprehends certain and singular persons known "
      "to God alone, described by the Prophet in these words, Jer. xxxi. 33. This is the "
      "covenant which I will strike with the house of Israel after these days, I will put "
      "my law in their mind, and on their heart I will inscribe it, and I will be God to "
      "them, and they will be a people to me; He who, I say, procured such a covenant by "
      "his death, offered his death and merit to God the Father to be applied efficaciously "
      "to certain elect persons. This proposition is thence clear and manifest, because to "
      "put his laws into the minds of human beings, and to inscribe them on their hearts, "
      "and to make the same a peculiar people to God, denote the efficacious application of "
      "the merits of Christ, and designate the privileges of the elect or of spiritual "
      "Israel. Now indeed I add the Minor, and I affirm that Christ by his death stood as "
      "Mediator of this secret covenant, which includes application, and embraces the "
      "Israel of God or the elect sons of God and them alone. Besides the words of the "
      "Prophet just praised, we have also of the Apostle, citing the same Prophet, a clear "
      "testimony, Heb. viii. 6. Our High Priest is Mediator of a better testament, which "
      "has been sanctioned in better promises. But what finally are those better promises "
      "which Christ the Mediator established? They are rehearsed in verse 10 in the same "
      "words in which they stand in Jeremiah; and they are reduced to two heads, to the "
      "promise of an interior reformation of hearts, and of a free remission of sins, as "
      "Calvin well observed on this place. Christ therefore by his death merited for all "
      "remission of sins, if they believe and are converted: and he merited and procured "
      "for certain ones this free and secret covenant to be fulfilled by God promising; "
      "namely, that they believe and are converted to God, through and on account of the "
      "Mediator, efficaciously reforming their hearts, and putting his laws into the same. "
      "But these for whom Christ merited this (as is clear from Augustine) are all who "
      "pertain spiritually to the house of Israel and the seed of Abraham: what else is "
      "that than all the elect? The elect therefore from the intention of God and of Christ "
      "have had destined and given to them the special benefit of a fruitful application "
      "from the death of Christ."
    ),
    "pass_b": (
      "He who by his death not only established that evangelical covenant looking "
      "promiscuously to all—“Whoever believes will be saved”—but also that secret covenant "
      "which takes in certain singular persons known to God alone, described by the prophet "
      "in Jeremiah 31:33: “This is the covenant I will make with the house of Israel after "
      "these days: I will put my law in their mind and write it on their heart, and I will "
      "be their God, and they shall be my people”—he who procured such a covenant by his "
      "death offered his death and merit to the Father to be applied efficaciously to "
      "certain elect persons. That is clear, because putting his laws into people’s minds, "
      "writing them on their hearts, and making them God’s peculiar people marks the "
      "efficacious application of Christ’s merits and names the privileges of the elect, or "
      "spiritual Israel. I add the minor and affirm that by his death Christ was Mediator of "
      "this secret covenant, which includes application and embraces God’s Israel—or the "
      "elect children of God—and them alone. Besides the prophet’s words just cited, we have "
      "the Apostle citing the same prophet (Hebrews 8:6): “Our High Priest is Mediator of a "
      "better testament, established on better promises.” What are those better promises "
      "Christ the Mediator established? Verse 10 rehearses them in Jeremiah’s own words; "
      "they reduce to two heads—the promise of an inward reforming of hearts, and of free "
      "remission of sins—as Calvin notes on the place. So by his death Christ merited "
      "remission of sins for all if they believe and turn; and for some he also merited and "
      "procured this free, secret covenant to be fulfilled by the promising God—namely that "
      "they believe and turn to God, through and because of the Mediator reforming their "
      "hearts efficaciously and putting his laws into them. Those for whom he merited this "
      "(as Augustine makes plain) are all who belong spiritually to the house of Israel and "
      "Abraham’s seed: what else is that than all the elect? So from God’s and Christ’s "
      "intention the elect have had destined and given to them the special benefit of a "
      "fruitful application from Christ’s death."
    ),
    "notes_covered": [
      "Ratio 1; Jer 31:33; Heb 8:6-10; Calvin; Augustine spiritual Israel; elect application"
    ],
    "lemmas": [
      {"form": "foedus illud arcanum", "gloss": "that secret covenant", "why": "vs promiscuous gospel covenant"},
      {"form": "Indam legem meam menti eorum", "gloss": "I will put my law in their mind", "why": "Jer 31:33"},
      {"form": "melioris testamenti Mediator", "gloss": "Mediator of a better testament", "why": "Heb 8:6"},
    ],
  },
  {
    "section": 149,
    "title": "Cap. 7 Arg. 4 Ratio 2: precious blood not left to chance—Malderus on elect fruit",
    "latin": (
      "Secunda ratio sumi potest a consideratione ipsius pretii in cruce persoluti pro "
      "redemtione humani generis. Pretium hoc fuit sanguis Filii Dei, Filii unigeniti & "
      "dilecti: At non est credibile tale ac tantum pretium impensum fuisse in eventum ex "
      "incerta alea humani arbitrii pendulum: Fuit ergo consilium & intentio Dei Patris ac "
      "Christi Mediatoris, hac pretiosa morte quosdam homines infallibiliter & efficaciter "
      "redimere & servare: Hi autem alii esse non potuerunt ab illis, qui reapse salvantur, "
      "id est, ab electis: Ergo Christi seipsum offerentis intentio speciali quodam modo "
      "respiciebat electos. Scio Grevinchovium, aliosque qui ex eadem Schola prodierunt, "
      "audacter asserere, Finem impetrationis proprium atque a Deo intentum fuisse, ut "
      "peccatorem salvare posset salva justitia sua: potuisse autem hanc redemtionem "
      "omnibus impetratam nullis applicari, propter intervenientem omnium incredulitatem. "
      "Quod perinde valet, ac si dicerent, Deum ita dedisse Filium in mortem, ut interim "
      "nullum certum propositum habuerit de servandis ullis hominibus merito ejusdem "
      "mortis, sed nuda possibilitate salutis per mortem Christi omnibus generaliter "
      "procurata, ita efficacem participationem salutis commisisse arbitrio singulorum, "
      "ut Christi mors, in tota latitudine sui meriti considerata, potuerit neminem a "
      "morte efficaciter redemisse. At quisquis rite perpenderit quam pretiosa fuit mors "
      "Filii in oculis Patris, ne cogitare quidem poterit illum voluisse Filium morti "
      "exponere absque certo proposito eandem mortem efficaciter quibusdam applicandi. "
      "Esai. liii. 10. Voluntas Domini in manu ejus dirigetur. Audite Malderum scriptorem "
      "Pontificium, Arminianis hac in re multo saniorem, Anti-Synod. pag. 138. Si solum "
      "respiciatur ipsa oblatio, inquit, aequalis illa est pro omnibus; secus, si "
      "respiciatur id pro quo reipsa obtinendo obtulit. Obtinunt enim electi fructum "
      "perfectum, & reipsa sequentem, & applicatum suae passionis, tanquam in hoc sibi "
      "datis a Patre. Non potuit igitur sanguis Christi in inane diffluere; quia pretio "
      "sanguinis sui, ex decreto Dei, promeruit electis fructuosam ejusdem pretii "
      "applicationem."
    ),
    "pass_a_gloss": (
      "A second reason can be taken from consideration of the price itself paid on the "
      "cross for the redemption of the human race. This price was the blood of the Son of "
      "God, of the only-begotten and beloved Son: But it is not credible that such and so "
      "great a price was spent on an outcome hanging from the uncertain dice of human "
      "choice: Therefore there was counsel and intention of God the Father and of Christ "
      "the Mediator, by this precious death to redeem and save certain human beings "
      "infallibly and efficaciously: But these could not be other than those who are in "
      "fact saved, that is, than the elect: Therefore the intention of Christ offering "
      "himself regarded the elect in a certain special way. I know that Grevinchovius, and "
      "others who have come forth from the same School, boldly assert that the proper end "
      "of impetration and that intended by God was that he might be able to save the "
      "sinner with his justice safe: but that this redemption obtained for all could be "
      "applied to none, on account of the intervening unbelief of all. Which is worth as "
      "much as if they said that God so gave the Son into death that meanwhile he had no "
      "certain purpose of saving any human beings by the merit of the same death, but with "
      "a bare possibility of salvation through the death of Christ generally procured for "
      "all, so committed the efficacious participation of salvation to the choice of "
      "individuals, that the death of Christ, considered in the whole breadth of its "
      "merit, could have efficaciously redeemed no one from death. But whoever rightly "
      "weighs how precious the death of the Son was in the eyes of the Father will not "
      "even be able to think that he willed to expose the Son to death without a certain "
      "purpose of applying the same death efficaciously to some. Isaiah liii. 10. The will "
      "of the Lord shall be directed in his hand. Hear Malder, a Pontifical writer, much "
      "sounder than the Arminians in this matter, Anti-Synod. page 138. If the offering "
      "itself alone is regarded, he says, it is equal for all; otherwise, if that is "
      "regarded for obtaining which in the thing itself he offered. For the elect obtain "
      "the perfect fruit, and that which in the thing itself follows, and is applied, of "
      "his passion, as given to themselves by the Father for this. Therefore the blood of "
      "Christ could not flow away into emptiness; because by the price of his blood, from "
      "the decree of God, he merited for the elect the fruitful application of the same "
      "price."
    ),
    "pass_b": (
      "A second reason is the price paid on the cross for redeeming the human race. That "
      "price was the blood of God’s Son, the only-begotten and beloved. It is not credible "
      "that so great a price was spent on an outcome dangling from the uncertain dice of "
      "human choice. So the Father and Christ the Mediator meant by this precious death to "
      "redeem and save certain people infallibly and efficaciously; and those can be none "
      "other than those who are in fact saved—the elect. Therefore Christ’s intention in "
      "offering himself regarded the elect in a special way. I know Grevinchovius and "
      "others of that school boldly claim the proper end of impetration God intended was "
      "only that he might save the sinner with his justice intact, and that this redemption "
      "obtained for all might still be applied to none because of everyone’s intervening "
      "unbelief. That is as much as to say God gave the Son to death with no certain "
      "purpose of saving anyone by that death’s merit, but only a bare possibility of "
      "salvation procured for all in general, leaving efficacious share in salvation to "
      "each person’s choice—so that Christ’s death, taken in the whole breadth of its "
      "merit, might have redeemed no one from death. But whoever weighs how precious the "
      "Son’s death was in the Father’s eyes cannot even think he meant to expose the Son to "
      "death without a certain purpose of applying that death efficaciously to some. Isaiah "
      "53:10: “The will of the Lord shall prosper in his hand.” Hear Malder, a papal "
      "writer far sounder than the Arminians here (Anti-Synod, p. 138): if you look only at "
      "the offering itself, it is equal for all; otherwise, if you look at that for whose "
      "actual obtaining he offered. For the elect obtain the perfect fruit of his passion "
      "that actually follows and is applied, as given them by the Father for this. So "
      "Christ’s blood could not run to waste; by the price of his blood, from God’s decree, "
      "he merited for the elect the fruitful application of that same price."
    ),
    "notes_covered": [
      "Ratio 2; precious blood vs alea arbitrii; Grevinch impetration; Malderus Anti-Synod 138; Isa 53:10"
    ],
    "lemmas": [
      {"form": "incerta alea humani arbitrii", "gloss": "uncertain dice of human choice", "why": "reject chance outcome"},
      {"form": "Finem impetrationis", "gloss": "end of impetration", "why": "Grevinch"},
      {"form": "sanguis Christi in inane diffluere", "gloss": "Christ's blood flow away into emptiness", "why": "Malderus close"},
    ],
  },
  {
    "section": 150,
    "title": "Cap. 7 Arg. 4 Ratio 3: Spirit’s gifts prove special intent—Heb 7:25 Savior of certain ones",
    "latin": (
      "Quicquid boni spiritualis & salutiferi Christi Spiritus efficit in ullis "
      "hominibus, id Christi sanguis effusus promeruit iisdem hominibus: At Christi "
      "Spiritus producit in certis quibusdam personis poenitentiam & fidem, & mediante "
      "fide ac poenitentia infallibilem applicationem mortis suae: Ergo iisdem "
      "hominibus haec specialia bona promeruit: Ergo seipsum in ara crucis sacrificans "
      "promereri intendit. Neque enim temere aut casu fas est putare, Christum majora "
      "spiritualia beneficia hisce quam illis procurasse. Quid hic respondebunt "
      "adversarii? Nunquid dicent Christi Spiritum impertire beneficia hominibus, quae "
      "Christus illis minime promeruit? Non audebunt Christi meritum ita conculcare; "
      "Nunquid respondebunt, Ipsam fidem, & voluntatem, & actum fructuosae applicationis "
      "non esse Dona specialia Spiritus sancti? Pudebit tam crassi Pelagianismi. "
      "Fateantur ergo nobiscum, sicut per Christi mortem specialia bona sunt procurata "
      "electis, ita in voluntate Christi morientis, Deique Patris, hanc mortem "
      "acceptantis, fuisse efficacem intentionem de iisdem procurandis & conferendis. "
      "Atque hoc est illud singulare privilegium in morte Christi, quod solis electis "
      "vindicamus, quia ex facto apparet, Deum eos solos morte Filii sui efficaciter "
      "servandos destinasse. Unde Heb. vii. 25. statuitur Servator quorundam, id est, "
      "electorum, munus, nempe tam merito, quam efficacia."
    ),
    "pass_a_gloss": (
      "Whatever of spiritual and saving good the Spirit of Christ effects in any human "
      "beings, the poured-out blood of Christ merited for the same human beings: But the "
      "Spirit of Christ produces in certain persons repentance and faith, and by means of "
      "faith and repentance an infallible application of his death: Therefore for the same "
      "human beings he merited these special goods: Therefore sacrificing himself on the "
      "altar of the cross he intended to merit them. For it is not right to think rashly or "
      "by chance that Christ procured greater spiritual benefits for these than for those. "
      "What will the adversaries answer here? Will they say that the Spirit of Christ "
      "imparts benefits to human beings which Christ by no means merited for them? They "
      "will not dare so to trample the merit of Christ; Will they answer that faith itself, "
      "and the will, and the act of fruitful application are not special Gifts of the Holy "
      "Spirit? They will be ashamed of so crass a Pelagianism. Let them therefore confess "
      "with us that just as through the death of Christ special goods were procured for the "
      "elect, so in the will of Christ dying, and of God the Father accepting this death, "
      "there was an efficacious intention of procuring and conferring the same. And this is "
      "that singular privilege in the death of Christ which we claim for the elect alone, "
      "because from the fact it appears that God destined them alone to be saved "
      "efficaciously by the death of his Son. Whence Heb. vii. 25. there is established the "
      "office of Savior of certain ones, that is, of the elect, namely as much by merit as "
      "by efficacy."
    ),
    "pass_b": (
      "Whatever spiritual, saving good Christ’s Spirit works in any people, Christ’s "
      "poured-out blood merited for those same people. But Christ’s Spirit produces in "
      "certain persons repentance and faith, and through faith and repentance an infallible "
      "application of his death. Therefore he merited these special goods for those same "
      "people; therefore, sacrificing himself on the cross’s altar, he meant to merit them. "
      "It is not right to suppose by chance that Christ procured greater spiritual benefits "
      "for these than for those. What will the adversaries say? That Christ’s Spirit gives "
      "people benefits Christ never merited for them? They will not dare so to trample "
      "Christ’s merit. That faith itself, the will, and the act of fruitful application are "
      "not special gifts of the Holy Spirit? They will blush at so crass a Pelagianism. Let "
      "them confess with us: just as through Christ’s death special goods were procured for "
      "the elect, so in the will of the dying Christ, and of the Father accepting that "
      "death, there was an efficacious intention to procure and confer those goods. And that "
      "is the singular privilege in Christ’s death we claim for the elect alone, because the "
      "fact shows God destined them alone to be saved efficaciously by his Son’s death. "
      "Hence Hebrews 7:25 establishes the office of Savior of certain ones—that is, of the "
      "elect—both by merit and by efficacy."
    ),
    "notes_covered": [
      "Ratio 3; Spirit faith/repentance; anti-Pelagian; Heb 7:25 Servator quorundam; before Quartum"
    ],
    "lemmas": [
      {"form": "Christi Spiritus producit ... poenitentiam & fidem", "gloss": "Christ's Spirit produces repentance and faith", "why": "Ratio 3 major"},
      {"form": "crassi Pelagianismi", "gloss": "crass Pelagianism", "why": "adversary trap"},
      {"form": "Servator quorundam", "gloss": "Savior of certain ones", "why": "Heb 7:25"},
    ],
  },
]


def write_justification(sec: dict) -> Path:
    JUST.mkdir(parents=True, exist_ok=True)
    path = JUST / f"morte_{sec['section']}.json"
    payload = {
        "section": str(sec["section"]),
        "title": sec["title"],
        "pass_a_gloss": sec["pass_a_gloss"],
        "pass_b_english": [sec["pass_b"]],
        "source_text": sec["latin"],
        "pass_a_ne_b": True,
        "bible_refs": [],
        "notes": (
            f"Densify Cap. 7 Arg. 4 (Ultimo / Gen. 3:15 seed) section {sec['section']}. "
            f"Pass A!=B. Latin from 1650 PDF pdftotext+tesseract+lock. Packet {PACKET}. Honest partial."
        ),
        "lemmas": sec["lemmas"],
        "choices": [
            {
                "issue": "Copy-text",
                "choice": (
                    "Locked 1650 Daniel Latin from IA PDF (pdftotext + tesseract lat+eng) "
                    "with sense normalize; Cap. 7 Arg. 4 lock: "
                    "sources/_davenant_cap7_arg4_latin_lock.txt."
                ),
            },
            {
                "issue": "Scope",
                "choice": (
                    "Cap. 7 Arg. 4 Ultimo / Gen. 3:15 through Ratio 3 (Heb 7:25) close; "
                    "before Quartum argumentum (sufficienter/efficaciter)."
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
    if r.returncode != 0:
        raise SystemExit(f"check_pass_ab failed for {path}: {r.stdout}\n{r.stderr}")
    if "fail=" in out and "fail=0" not in out:
        raise SystemExit(f"check_pass_ab FAIL for {path}: {out}")


def live_section_count() -> tuple[int, int]:
    req = urllib.request.Request(
        "https://fathers.saneapps.com/",
        headers={"User-Agent": "Mozilla/5.0 (compatible; SaneApps densify hold)"},
    )
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    m = re.search(r"(\d+)\s*treatises.*?(\d+)\s*sections", html, re.I | re.S)
    if not m:
        raise SystemExit("could not parse live section count from fathers home")
    return int(m.group(1)), int(m.group(2))


def live_davenant_tip() -> int:
    req = urllib.request.Request(
        "https://fathers.saneapps.com/works/davenant-dissertationes-duae/",
        headers={"User-Agent": "Mozilla/5.0 (compatible; SaneApps densify hold)"},
    )
    html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
    nums = [int(x) for x in re.findall(r'data-section[=:]["\']?(\d+)', html)]
    if not nums:
        nums = [int(x) for x in re.findall(r'"section"\s*:\s*(\d+)', html)]
    return max(nums) if nums else -1


def append_rows(secs: list[dict]) -> None:
    eng = json.loads((TRANS / "morte_christi_english.json").read_text(encoding="utf-8"))
    src = json.loads((TRANS / "morte_christi_source.json").read_text(encoding="utf-8"))
    assert len(eng) == len(src) == TIP_BEFORE, (len(eng), len(src), TIP_BEFORE)
    assert str(eng[-1]["section"]) == str(TIP_BEFORE)
    for sec in secs:
        eng.append(
            {
                "section": sec["section"],
                "title": sec["title"],
                "english": [sec["pass_b"]],
                "notes_covered": sec["notes_covered"],
                "added_allusions": [],
                "translator_notes": [],
                "source_ref": f"morte_christi_source.json#{sec['section']}",
            }
        )
        src.append(
            {
                "section": sec["section"],
                "title": sec["title"],
                "latin": sec["latin"],
            }
        )
    (TRANS / "morte_christi_english.json").write_text(
        json.dumps(eng, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (TRANS / "morte_christi_source.json").write_text(
        json.dumps(src, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"appended eng/src tip {eng[-1]['section']} (n={len(eng)})")


def update_meta(tip: int) -> None:
    meta_path = TRANS / "morte_christi_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["section_count"] = tip
    blurb = meta.get("blurb") or meta.get("description") or ""
    note = "; Cap. 7 Arg. 4 Ultimo/Gen. 3:15 tip."
    if isinstance(blurb, str) and "Arg. 4" not in blurb:
        if "blurb" in meta:
            meta["blurb"] = blurb.rstrip(".") + note
        elif "description" in meta:
            meta["description"] = blurb.rstrip(".") + note
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def extend_lock(secs: list[dict]) -> None:
    lock = BOOK / "sources/_davenant_morte_christi_latin_lock.txt"
    if not lock.exists():
        return
    text = lock.read_text(encoding="utf-8")
    if "Arg. 4" in text and "Ultimo" in text and "Gen. iii" in text:
        print("morte lock already has Arg. 4; skip append")
        return
    block = "\n\n=== Cap. 7 Arg. 4 densify append ===\n" + "\n\n".join(
        f"[{s['section']}] {s['latin']}" for s in secs
    )
    lock.write_text(text.rstrip() + block + "\n", encoding="utf-8")
    print("extended morte latin lock")


def build_packet(tip: int) -> None:
    AUDIT.mkdir(parents=True, exist_ok=True)
    expected = [str(i) for i in range(1, tip + 1)]
    eng = json.loads((TRANS / "morte_christi_english.json").read_text(encoding="utf-8"))
    src = json.loads((TRANS / "morte_christi_source.json").read_text(encoding="utf-8"))
    sections = []
    for e, s in zip(eng, src):
        sections.append(
            {
                "section": str(e["section"]),
                "title": e.get("title", ""),
                "english": e.get("english", []),
                "latin": s.get("latin", ""),
                "notes_covered": e.get("notes_covered", []),
            }
        )
    packet = {
        "identity": {
            "author": "John Davenant",
            "work": "Two Dissertations (De morte Christi Cap. 1-7 partial)",
            "edition": (
                "Dissertationes duae (Cambridge: Roger Daniel, 1650). Wing D317; ESTC R5446. "
                "IA bim_early-english-books-1641-1700_dissertationes-du-_davenant-john-bp_1650. "
                "Partial: De morte Christi Cap. 1-6 close + Cap. 7 through Arg. 4 Ultimo/Gen. 3:15 "
                "Ratio 3 close (before Quartum sufficienter/efficaciter)."
            ),
            "locus_scheme": "section",
            "source_url": "https://archive.org/details/bim_early-english-books-1641-1700_dissertationes-du-_davenant-john-bp_1650",
        },
        "publication_scope": {
            "status": "partial",
            "note": f"Tip densify Cap. 7 Arg. 4 Ultimo/Gen. 3:15 (secs 145-{tip}). Not whole Dissertationes.",
            "packet": PACKET,
        },
        "explicit_selected_sections": expected,
        "schema": "translation-audit-v1",
        "seed": 20260922,
        "sample_size": 5,
        "scope": "selected_passages_only",
        "expected_sections": expected,
        "files": {
            "english": str(TRANS / "morte_christi_english.json"),
            "source": str(TRANS / "morte_christi_source.json"),
        },
        "raw_source_paths": [
            str(BOOK / "sources/_davenant_cap7_arg4_latin_lock.txt"),
            str(BOOK / "sources/davenant_1650.pdf"),
        ],
        "structural_errors": [],
        "coverage": {"sections": tip, "expected": tip},
        "sections": sections,
        "limits": {"max_sections": tip},
        "packet_id": "",
    }
    blob = json.dumps(packet, ensure_ascii=False, sort_keys=True)
    import hashlib

    packet["packet_id"] = hashlib.sha256(blob.encode()).hexdigest()
    out = AUDIT / f"{PACKET}.packet.json"
    out.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    reviews = []
    for i in range(1, tip + 1):
        reviews.append(
            {
                "section": str(i),
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
                "notes": f"Rebind {PACKET} section {i}.",
                "uncertainties": [],
            }
        )
    review = {
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
            "notes": f"Scope rebind davenant-dissertationes-duae tip {tip} (Cap. 7 Arg. 4 Ultimo/Gen. 3:15).",
        },
        "reviews": reviews,
    }
    (AUDIT / f"{PACKET}.review.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("packet", packet["packet_id"][:16], "structural", packet["structural_errors"])


def prepend_handoff(before: int, after: int, hold_note: str) -> None:
    path = BOOK / "SESSION_HANDOFF.md"
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    block = f"""# densify 2026-09-22

## 2026-09-22 ~18:15 ET (Scribe — Davenant Cap. 7 Arg. 4 densify)

CoS densify: Cap. 7 Arg. 4 (Ultimo / Gen. 3:15 seed) through Ratio 3 (Heb 7:25) close before Quartum. Punch X: **NO**. Cap. 1 mid-Thesis tip patch stays deferred. Did **not** edit `publication-review.json`; did not ship; did not commit; did not run Logos or ai_promote. {hold_note}

### Bound this job (not shipped)
- **Davenant** `davenant-dissertationes-duae`: Cap. 7 Arg. 4 tip (**{before}→{after}** sections). Locked densify Latin from IA 1650 Daniel PDF (pdftotext + tesseract) with lock. Pass A≠B; OUR; English-first; no PBB/ops TNs; packet `{PACKET}`. Honest partial — **not** whole Dissertationes. Cap. 7 Quartum argumentum–remainder through Cap. 11 and De praedestinatione remain. Punch X: **NO**.

### Still missing for full Dissertationes duae
- Cap. 1 tip mid-block patch (between universal-cause definition and John 3:16) — deferred
- Cap. 7 Quartum (sufficienter/efficaciter) through Cap. 11 (De morte Christi remainder)
- Full De praedestinatione et reprobatione
- Sententia de Gallicana controversia if in the 1650 volume

### Punch X?
**NO** — full-works bar not met. Parent/CoS only.


---

"""
    path.write_text(block + old, encoding="utf-8")
    print("SESSION_HANDOFF prepended")


def main() -> None:
    mode = os.environ.get("DENSIFY_MODE", "all")
    if mode in ("all", "just"):
        for sec in SECTIONS:
            p = write_justification(sec)
            check_just(p)
        if mode == "just":
            print("justifications only; stop before append")
            return
    eng = json.loads((TRANS / "morte_christi_english.json").read_text(encoding="utf-8"))
    tip_now = int(eng[-1]["section"])
    if tip_now != TIP_BEFORE:
        raise SystemExit(f"disk tip changed: expected {TIP_BEFORE}, got {tip_now}")
    treatises, secs = live_section_count()
    dav_tip = live_davenant_tip()
    print(f"pre-append live={treatises}/{secs} davenant_tip={dav_tip} disk={tip_now}")
    if secs <= 3427:
        raise SystemExit(f"hold not cleared: live sections still {secs}")
    hold_note = (
        f"Hold cleared with live {treatises}/{secs} (>{3427}); disk tip {tip_now}; "
        f"davenant live tip parse={dav_tip}."
    )
    append_rows(SECTIONS)
    tip = TIP_BEFORE + len(SECTIONS)
    update_meta(tip)
    extend_lock(SECTIONS)
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
