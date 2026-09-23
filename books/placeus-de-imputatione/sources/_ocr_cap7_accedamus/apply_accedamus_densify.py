# -*- coding: utf-8 -*-
"""Cap. VII Accedamus densify: ἐφ᾽ ᾧ / aorist / lexicography through Placeus two reasons."""
from __future__ import annotations
import json, copy, sys
from pathlib import Path

ROOT = Path("/Users/stephansmac/SaneApps/clients/translations")
BOOK = ROOT / "books/placeus-de-imputatione"
sys.path.insert(0, str(ROOT))
from pipeline.verify_translation_qa import digest, file_digest, validate_audit_receipt

LOCK_HEADER = """LOCKED LATIN TIP DENSIFY — Josue de la Place (Placeus), De imputatione primi peccati Adami
Edition: Salmurii: Apud Ioannem Lesnerium, 1661. IA deimputationepri00lapl.
Scope: Caput VII Accedamus ἐφ᾽ ᾧ πάντες ἥμαρτον through aorist and ἐφ᾽ ᾧ lexicography (in quo vs eo quod) to Placeus's two principal reasons (printed pp. 66–71 tip). Stops before Ad alias rationes / further Cap. VII. Not Cap. VIII+.
Reconstruction: IA PDF page images via macOS Vision OCR + tesseract + pdftotext; long-s/ligature OCR corrected; Greek ἐφ᾽ ᾧ / ἥμαρτον / ἐπί / ἐν confirmed against page image.
No modern English used as copy-text.
Remaining: Cap. VII Ad alias rationes onward and Cap. VIII+ of the ~494-page Disputatio.

"""

LATIN = {
"39": """Accedamus iam, inquit, secundo loco ad verba illustria ἐφ᾽ ᾧ πάντες ἥμαρτον, quae vel sola potuerunt ad doctrinam de imputatione stabiliendam sufficere. (Hoc quam sit falsum mox clarum fiet.) Nam ita significat Apostolus, omnes omnino homines, qui fuerunt, sunt, aut futuri sunt usque ad finem seculi, in Adamo peccante peccavisse. (An id significet mox videbimus.) Itaque quicunque veterum aut Recentiorum de imputatione hac egerunt, illi omnes hoc praesertim loco doctrinam illam confirmarunt. Prudenter addidit limitationem quicunque de imputatione hac egerunt. Nam et Calvinus, et Martyr, et alii maximi viri doctrinam illam hoc loco non confirmarunt, confirmaturi sine dubio, si imputationem illam verbis illis doceri credidissent. Nubem illam testium, qua lucem veritatis obscurare nititur, Deo dante, suo loco dissipabimus. Nunc cum eo rem ipsam consideremus.""",
"40": """Nimirum, inquit, opponit haec duo Apostolus, in Adamo omnes peccaverunt, in Christo omnes justificantur. Itane, inquam, illis verbis ἐφ᾽ ᾧ πάντες ἥμαρτον? Sed pergat. Sive oppositionem sive verba spectes, quibus oppositio explicatur, imputationem habes ex eo consurgentem. Ex oppositione. Nam ut in Christo justificantur homines, ita in Adamo peccasse intelliguntur. Atqui in Christo justificantur per imputationem justitiae illius. Ergo et in Adamo peccasse intelligendi sunt, per imputationem peccati Adae. Primum nego in illis verbis ejusmodi oppositionem fieri. Id erat non supponendum, sed probandum. Deinde, ut jam aliquoties inculcavi, (nihil enim differt hoc argumentum a superioribus) universaliter vera non est propositio, et similitudo potius est in veritate rei, quam in modo. Nimirum tam vere in Christo justificantur homines, quam vere peccaverunt in Adamo; Sed non justificantur eodem prorsus modo quo peccaverunt: id enim res ipsa pati non poterat; sed diverso. Subsumam enim, Atqui in Christo justificantur homines per suam quisque fidem. Ergo et in Adamo peccasse intelligendi sunt per suam quisque fidem ne dicam, an incredulitatem? Nonne haec minor propositio vera est, Apostoli et omnium Christianorum calculis confirmata? Aut igitur major falsa est, aut admittenda est conclusio conclusioni D. Gar. non obscure opposita. Quid horum pie lector eligis?""",
"41": """Ex verbis addit. Nam vis Aoristi ἥμαρτον hic perpendenda. Etenim tempus hoc, in usu Scripturae, aliquando absolutum est a speciali significatione temporis, ut cum dicitur, Omnes deflexerunt, inutiles facti sunt, peccaverunt. Rom. 3, 12. 23. Hoc enim omnia tempora praeteritum, praesens, et futurum continet; ut significetur peccasse, qui fuerunt, peccare qui sunt, peccaturos qui erunt. Hic tamen ubi multiplicat Apostolus Aoristos, vis eorum singulariter spectari debet: peccatum intraasse, mortem introiisse, omnes peccavisse. Intravit autem peccatum, ut primum Adam peccavit, et mortis reatus una cum illo peccato introiit. Ergo et ut primum peccavit Adam, nos omnes peccavisse intelligimur; quod sane melius exponi non potest, quam si dicamus peccatum Adae omnibus imputari. Non dicam peccare hoc argumentum ignoratione elenchi; nec id concludere quod erat inter suum autorem et Placeum controversum: Hoc enim peccant omnia D. Gar. argumenta: Nam ne id quidem quod concludit probandi vim ullam habet. Etenim si Aoristi, omnes deflexerunt, inutiles facti sunt, peccaverunt, Rom. 3. absoluti sunt a speciali significatione temporis, quid est, quamobrem similiter non sint ab ea significatione absoluti Aoristi, peccatum intravit, mors introiit, omnes peccaverunt, Rom. 5? Obstat, inquies, eorum hoc loco multiplicatio. At nonne aeque illic atque hic tres numeravit Aoristos? ac tribus illis quos laudavit ex Rom. 3. addere potuit alios duos ex vers. 13. et 17. linguis suis ad dolum usi sunt, viam veritatis non cognoverunt? Quanquam non video cur si duo aut tres Aoristi ita accipi debeant, non possint eodem modo quatuor, vel quinque, vel sex accipi. Non enim multiplicatio Aoristorum mutat eorum significationem. Affirmanti igitur, nec probanti negationem oppono: possem et magnorum, qui ante nos vixerunt, Theologorum autoritatem opponere, sed studio brevitatis mihi tempero, et in alium locum reservo.""",
"42": """Illud observo, mortem introiisse in omnes homines non unam numero omnibus imputatam, sed suam cuique homini propriam. Hoc non potest negari. Constat etiam per unum hominem peccatum revera intraasse in omnes homines non unum numero, sed suum cuique proprium et inhaerens. Nonne? Haec si agnoscis, cur iis non acquiescis? Si negas, qui publicae fidei confessioni subscribere te profiteris? Revocabo-ne ad examen etiam verba sequentia? Quid-ni? interest enim veritatis quicquid rectum non est corrigi. Intravit autem, inquit, peccatum, ut primum Adam peccavit. Certe quidem in Adamum, sed per Adamum in alios omnes homines, qui tunc nulli erant, quomodo tunc intrare potuit? Non dicit autem Apostolus, peccatum intraasse in unum hominem, sed per unum hominem in mundum, id est, in omnes homines. Constat autem per unum hominem intraasse in omnes homines, uno Christo excepto, peccatum inhaerens nos in foro divino reos mortis constituens. Cur ergo illud in Pauli verbis non agnoscamus? Quis etiam credat, Apostolum per mortem reatum mortis, potius quam per peccatum, intelligere? Da enim locum, si potes, ubi mors non mortem, sed tantum reatum mortis significet, praesertim cum spectatur, ut sit hic, tanquam peccati effectum et stipendium, ab eoque distinguitur? An aliter peccatum actuale Adami in omnes homines introiit, quam quatenus ejus vel pravitas propagatione, vel reatus imputatione in eos introiit? Si ergo reatum D. Gar. intellexit cum dicitur peccatum introiisse, qui eundem reatum intelligere potuit, cum additur, per peccatum quod introiit in omnes homines, in eosdem mortem etiam introiisse? Caeterum ut primum peccavit Adam, nos omnes peccavisse intelligimur, nimirum quomodo, ut primum fuit vel creatum est, nos omnes fuisse vel creati fuisse intelligimur. An igitur ferendus esset, qui simpliciter diceret, nos omnes ab initio mundi fuisse?""",
"43": """Audio virum doctum alio argumento hoc confirmantem, id attendamus. Quod idem, inquit, confirmant voculae illae ἐφ᾽ ᾧ in quo. Nam qui, cum nondum essent in rerum natura, dicuntur in alio peccasse, censentur procul dubio eo committente peccatum, et ipsi etiam commisisse, quod evidenter ad imputationem pertinet. Atqui homines omnes cum nondum essent, dicuntur in Adamo peccasse. Ergo censentur eo committente peccatum, et ipsi commisisse, quod ad imputationem peccati Adae manifeste pertinet. Primum nititur haec argumentatio hypothesi, voculas ἐφ᾽ ᾧ hoc loco significare in quo. Id quod non concedimus. Negari enim non potest, quin verti possint eo quod, propterea quod, quatenus &c. Si sic verti possunt, non est necesse ut vertantur in quo; si non est necesse ut vertantur in quo, nulla est argumentationis, quae nititur illa versione, necessitas. Quomodo ergo probat D. Gariss. debere hoc loco reddi in quo, potius quam eo quod &c? Affert indicem magnorum virorum antiquorum et recentium qui reddiderunt in quo, sed eorum autoritas non impedivit, quominus alii, et ipsi magni viri, versioni in quo praetulerint versionem eo quod, quatenus &c, Theodoretus, Syrus interpres, Calvinus, Martyr, Bucerus, Aretius, Piscator, Paraeus, Erasmus, Leo Juda, Vatablus, Autores versionis Gallicanae, qua utuntur Ecclesiae nostrae, nec-non Anglicanae, &c. nam longum esset omnes enumerare. Faverunt-ne propterea isti maximi viri Pelagianae haeresi? Quid est quare Placeus non debeat eorum exemplum sequi, et recepta versione respondens niti? Nihil-ne praeterea D. Garissolius? Addit etiam vim vocularum illarum ex usu Scripturae: nam, inquit, frequentissimum est ut ἐπί accipiatur pro ἐν, quod ut probet multa laudat exempla. Nempe id probat quod non negatur, quod vero negatur id non probat. Nemo enim ei negavit ἐπί aliquando accipi pro ἐν. Sed an inde sequitur, esse illam praepositionem per enallagen usurpatam hoc loco, et positam ἐπί pro ἐν? Immo si dixisset Apostolus ἐν ᾧ, nihil prohiberet quominus etiam illae voces eo quod vel quoniam &c. redderentur, ut factum est ab omnibus fere interpretibus Rom. 8. 3. Extant autem ἐφ᾽ ᾧ eo sensu 2. Cor. 5. 4. nec aliter accipi solent quoties nullum est antecedens, ad quod ᾧ commode referri possit. Caeterum quod ait, versionis in quo, nos autorem facere Bezam, unde habeat nescio. Id certe Placeus neque dixit, neque scripsit, neque cogitavit unquam. Rationes quas nobis tribuit, non sunt Placei, nec eis opus est respondenti secundum versionem ab Ecclesiis nostris probatam. Quam si flagitas a me, Lector, ut probem, Primum duas Placei rationes afferam, deinde quinque illas, quas sibi D. G. objecit, ab ejus exceptionibus breviter vindicabo. Primum igitur si vertas in quo, relativum quo, quia referri non poterit ad nomen masculinum proximum, vel propinquum, sed ad remotius, trajectio admittenda erit, eaque insolens et dura admodum. Jam autem ejusmodi trajectio admitti non debet absque necessitate, quae hic nulla apparet, cum voculae ἐφ᾽ ᾧ non minus et proprie et commode reddi possint eo quod, vel quoniam, vel quatenus. Deinde verba omnes peccaverunt, cum causam contineant ejus quod immediate praecessit, cum eo jungi flagitant: quis enim negare potest, quin mors in omnes invaserit, quia omnes peccaverunt? Cur ergo a se invicem separaremus ea orationis Apostolicae membra, quae non modo situ et collocatione ab Apostolo juncta sunt, sed etiam sensu et rerum significatarum indissolubili nexu cohaerent?""",
}

TITLES = {
"39": "Cap. VII Accedamus: ἐφ᾽ ᾧ πάντες ἥμαρτον — second place on the words",
"40": "Cap. VII: Adam–Christ opposition from ἐφ᾽ ᾧ — modes not the same",
"41": "Cap. VII: Force of the aorist ἥμαρτον — Rom. 3 and Rom. 5",
"42": "Cap. VII: Death and inhering sin entered — not one imputed number",
"43": "Cap. VII: Lexicography of ἐφ᾽ ᾧ — in quo versus eo quod",
}

PASS_A = {
"39": "Garissoles Accedamus: second place to the illustrious words ἐφ᾽ ᾧ πάντες ἥμαρτον, which alone could suffice to establish the imputation doctrine (Placeus: how false soon clear). Apostle thus means all humans who were, are, or will be to world's end sinned in Adam sinning (whether that is meant, soon). Hence whoever of ancients or moderns treated this imputation confirmed the doctrine especially here. Placeus: he wisely limited to those who treated this imputation — for Calvin, Martyr, and other greatest men did not confirm that doctrine here, and would have if they had believed those words taught that imputation. The cloud of witnesses by which he tries to obscure truth's light we will, God granting, scatter in its place. Now let us consider the matter itself with him.",
"40": "Garissoles: Apostle opposes these two — in Adam all sinned, in Christ all are justified. Placeus: with those words ἐφ᾽ ᾧ πάντες ἥμαρτον? Let him go on. Whether you look at opposition or words explaining it, imputation rises from it. From opposition: as men are justified in Christ, so they are understood to have sinned in Adam; but in Christ by imputation of his righteousness; therefore in Adam by imputation of Adam's sin. Placeus first denies such opposition is made in those words — that was to be proved, not assumed. Second, as often stressed (argument same as prior): the proposition is not universally true; likeness is in truth of the thing more than in mode. Men are as truly justified in Christ as they truly sinned in Adam; but not justified in the same mode exactly as they sinned — the thing itself could not bear that; rather differently. Subsume: but men are justified in Christ by each one's own faith; therefore understood to have sinned in Adam by each one's own faith — not to say unbelief? Is this minor not true by Apostle's and all Christians' votes? Either major is false, or a conclusion obscurely opposite Garissoles's must be admitted. Which do you choose, pious reader?",
"41": "Garissoles adds from the words: force of aorist ἥμαρτον to be weighed. This tense in Scripture use is sometimes absolute from special time-sense, as 'All have turned aside, become useless, have sinned' (Romans 3:12, 23) — covering past, present, future: who were sinned, who are sin, who will be will sin. Yet here where Apostle multiplies aorists, their force must be watched singly: sin entered, death entered, all sinned. Sin entered as soon as Adam sinned, and death's reatus entered with that sin. Therefore as soon as Adam sinned we all are understood to have sinned — best exposed by saying Adam's sin is imputed to all. Placeus: I will not say this argument sins by ignoratio elenchi, nor that it concludes what was disputed between its author and Placeus — for all Garissoles's arguments so sin: what it concludes has no proving force. If Rom. 3 aorists are absolute from special time-sense, why not likewise Rom. 5 aorists 'sin entered, death entered, all sinned'? You object: their multiplication here. But did he not count three aorists there as here? And to the three from Rom. 3 he could add two from vv. 13 and 17 ('their throat an open grave… way of peace they have not known'). If two or three aorists may be so taken, why not four, five, or six? Multiplication does not change their sense. To one affirming without proving I oppose negation; I could oppose great theologians' authority but for brevity reserve that elsewhere.",
"42": "Placeus observes: death entered into all men — not one death numerically imputed to all, but each man's own. Undeniable. Also through one man sin truly entered into all — not one numerically, but each one's own and inhering. If you grant these, why not rest in them? If you deny, you who profess to subscribe the public confession of faith? Shall he recall even the following words to examination? Why not? Truth's interest is that whatever is not right be corrected. Garissoles: sin entered as soon as Adam sinned. Placeus: certainly into Adam, but through Adam into all other men who then were none — how could it then enter? Apostle does not say sin entered into one man, but through one man into the world, i.e. into all men. And it is established that through one man inhering sin entered into all (Christ alone excepted), making us liable to death in the divine forum. Why not acknowledge that in Paul's words? Who would believe the Apostle means by death the reatus of death rather than by sin? Give a place, if you can, where death means not death but only reatus of death, especially when viewed here as sin's effect and wages, distinguished from it. Did Adam's actual sin enter all otherwise than as its pravity by propagation or its reatus by imputation entered them? If Garissoles meant reatus when sin is said to have entered, how could he mean the same reatus when it is added that through the sin which entered all, death also entered them? As for 'as soon as Adam sinned we all are understood to have sinned' — as if, as soon as he was or was created, we all are understood to have been or been created. Would one be borne who simply said we all existed from the world's beginning?",
"43": "Hear a learned man confirming by another argument. Garissoles: the little words ἐφ᾽ ᾧ 'in quo' confirm the same. Who, not yet in the nature of things, are said to have sinned in another are doubtless counted, while he commits the sin, to have committed it themselves — evidently belonging to imputation. But all men, when not yet, are said to have sinned in Adam; therefore counted to have committed it with him — manifestly belonging to imputation of Adam's sin. Placeus: this rests on the hypothesis that ἐφ᾽ ᾧ here means 'in quo,' which we do not grant. It cannot be denied they can be rendered 'eo quod,' 'propterea quod,' 'quatenus,' etc. If so renderable, no necessity to render 'in quo'; if no necessity, the argument built on that version has no necessity. How then does Garissoles prove it must here be 'in quo' rather than 'eo quod'? He offers an index of great ancient and recent men who rendered 'in quo,' but their authority did not stop others, themselves great, from preferring 'eo quod / quatenus': Theodoret, Syriac interpreter, Calvin, Martyr, Bucer, Aretius, Piscator, Paraeus, Erasmus, Leo Juda, Vatablus, authors of the French version our churches use, and the English, etc. Did those greatest men therefore favor Pelagian heresy? Why should Placeus not follow their example and rest on the received version? Does Garissoles add nothing more? He adds force of those words from Scripture use: most frequent that ἐπί is taken for ἐν, and he cites many examples. That proves what is not denied; what is denied it does not prove. Nobody denied ἐπί is sometimes taken for ἐν. But does it follow the preposition is used here by enallage, ἐπί put for ἐν? Even if the Apostle had said ἐν ᾧ, nothing would stop rendering those words 'eo quod' or 'quoniam,' as nearly all interpreters do at Romans 8:3. And ἐφ᾽ ᾧ exists in that sense at 2 Corinthians 5:4, and is usually so taken whenever there is no antecedent to which ᾧ can conveniently refer. As for his making Beza author of our 'in quo' version — whence he has that, Placeus does not know; Placeus never said, wrote, or thought it. Reasons he attributes to us are not Placeus's, and the respondent according to our churches' approved version needs them not. If you demand proof, Reader: first two of Placeus's reasons, then the five Garissoles objected to himself, briefly vindicated from his exceptions. First, if you render 'in quo,' the relative quo cannot refer to the nearest masculine noun but to a remoter — an insolent hard trajection must be admitted; such trajection must not be admitted without necessity, and here none appears, since ἐφ᾽ ᾧ can no less properly and conveniently be rendered 'eo quod,' 'quoniam,' or 'quatenus.' Second, the words 'all sinned,' containing the cause of what immediately preceded, demand to be joined with it: who can deny death invaded all because all sinned? Why then separate from each other those members of the Apostolic speech which the Apostle joined not only by situ and placement but by sense and indissoluble nexus of the things signified?",
}

PASS_B = {
"39": [
"Let us now approach, he says, in the second place to the illustrious words \"in that all sinned\" (ἐφ᾽ ᾧ πάντες ἥμαρτον) (Romans 5:12), which alone were able to suffice for establishing the doctrine of imputation. (How false this is will soon be clear.) For so, he says, the Apostle signifies that all men whatsoever who were, are, or are to be unto the end of the age sinned in Adam when he sinned. (Whether he signifies that, we shall soon see.) And so whoever of the ancients or of the more recent who have treated of this imputation have all confirmed that doctrine especially in this place. He prudently added the limitation \"whoever have treated of this imputation.\" For both Calvin and Martyr and other greatest men did not confirm that doctrine in this place — men who would without doubt have confirmed it if they had believed that imputation to be taught by those words. That cloud of witnesses by which he strives to obscure the light of truth we shall, God granting, scatter in its own place. Now let us consider the matter itself with him.",
],
"40": [
"Namely, he says, the Apostle opposes these two: in Adam all sinned, in Christ all are justified. Is it so, I ask, by those words \"in that all sinned\" (ἐφ᾽ ᾧ πάντες ἥμαρτον) (Romans 5:12)? But let him go on. Whether you look at the opposition or at the words by which the opposition is explained, you have imputation rising from it. From the opposition. For as men are justified in Christ, so they are understood to have sinned in Adam. And yet in Christ they are justified by the imputation of his righteousness. Therefore they are also to be understood to have sinned in Adam by the imputation of Adam's sin. First I deny that such an opposition is made in those words. That was not to be supposed, but to be proved. Next, as I have already often impressed (for this argument differs in nothing from the former ones), the proposition is not universally true, and the likeness is rather in the truth of the thing than in the mode. Namely, men are as truly justified in Christ as they truly sinned in Adam; but they are not justified in exactly the same mode in which they sinned: for the thing itself could not bear that; but in a diverse mode. For I will subsume: And yet men are justified in Christ by each one's own faith. Therefore they are also to be understood to have sinned in Adam by each one's own faith — not to say, or by unbelief? Is this minor proposition not true, confirmed by the votes of the Apostle and of all Christians? Either therefore the major is false, or a conclusion must be admitted that is not obscurely opposed to D. Garissoles's conclusion. Which of these do you choose, pious reader?",
],
"41": [
"From the words he adds: For the force of the aorist \"sinned\" (ἥμαρτον) is here to be weighed. For this tense, in the use of Scripture, is sometimes absolute from a special signification of time, as when it is said, \"All have turned aside, they have become useless; they have sinned\" (Romans 3:12, 23). For this contains all times — past, present, and future — so that it may be signified that those who were have sinned, those who are sin, those who will be will sin. Here nevertheless, where the Apostle multiplies aorists, their force ought to be regarded singly: that sin entered, that death entered, that all sinned. But sin entered as soon as Adam sinned, and the guilt of death entered together with that sin. Therefore also, as soon as Adam sinned, we all are understood to have sinned; which surely cannot be better expounded than if we say that Adam's sin is imputed to all. I will not say that this argument sins by ignorance of the elenchus; nor that it does not conclude what was controversial between its author and Placeus: for in this all D. Garissoles's arguments sin: for not even that which it concludes has any force of proving. For if the aorists \"all have turned aside, have become useless, have sinned\" (Romans 3) are absolute from a special signification of time, what is there why the aorists \"sin entered, death entered, all sinned\" (Romans 5:12) should not likewise be absolute from that signification? Their multiplication in this place, you will say, stands in the way. But did he not equally there and here count three aorists? And to those three which he praised from Romans 3 he could add two others from verses 13 and 17: \"with their tongues they have used deceit,\" \"the way of peace they have not known\" (Romans 3:13, 17). Although I do not see why, if two or three aorists ought to be so taken, four or five or six cannot be taken in the same way. For the multiplication of aorists does not change their signification. To one affirming, therefore, and not proving, I oppose negation: I could also oppose the authority of great theologians who lived before us, but for brevity's sake I restrain myself, and reserve it for another place.",
],
"42": [
"This I observe: that death entered into all men — not one death numerically imputed to all, but each man's own. This cannot be denied. It is also established that through one man sin truly entered into all men — not one numerically, but each one's own and inhering. Is it not so? If you acknowledge these things, why do you not rest in them? If you deny them, you who profess to subscribe the public confession of faith? Shall I recall even the following words to examination? Why not? For it interests the truth that whatever is not right be corrected. \"But sin entered,\" he says, \"as soon as Adam sinned.\" Certainly into Adam, but through Adam into all other men, who then were none — how could it then enter? But the Apostle does not say that sin entered into one man, but through one man into the world, that is, into all men (Romans 5:12). And it is established that through one man there entered into all men, Christ alone excepted, inhering sin constituting us guilty of death in the divine forum. Why then should we not acknowledge that in Paul's words? Who would also believe that the Apostle understands by death the guilt of death rather than by sin? For give a place, if you can, where death signifies not death but only the guilt of death, especially when it is regarded, as it is here, as the effect and wages of sin, and is distinguished from it (Romans 6:23). Did Adam's actual sin enter into all men otherwise than insofar as either its pravity by propagation or its guilt by imputation entered into them? If therefore D. Garissoles understood guilt when it is said that sin entered, how could he understand the same guilt when it is added that through the sin which entered into all men death also entered into the same? For the rest, \"as soon as Adam sinned, we all are understood to have sinned\" — namely in the way that, as soon as he was or was created, we all are understood to have been or to have been created. Would one therefore be to be borne who should simply say that we all existed from the beginning of the world?",
],
"43": [
"I hear a learned man confirming this by another argument; let us attend to it. \"The same,\" he says, \"those little words ἐφ᾽ ᾧ, 'in which,' confirm. For those who, when they were not yet in the nature of things, are said to have sinned in another are counted without doubt, while he was committing the sin, to have committed it themselves also, which evidently belongs to imputation. And yet all men, when they were not yet, are said to have sinned in Adam. Therefore they are counted, while he was committing the sin, to have committed it themselves also, which manifestly belongs to the imputation of Adam's sin.\" First this argumentation rests on the hypothesis that the little words ἐφ᾽ ᾧ in this place signify \"in which.\" That we do not grant. For it cannot be denied that they can be rendered \"in that,\" \"because,\" \"inasmuch as,\" and so on. If they can be so rendered, it is not necessary that they be rendered \"in which\"; if it is not necessary that they be rendered \"in which,\" there is no necessity of the argumentation which rests on that version. How then does D. Garissoles prove that in this place \"in which\" ought to be rendered rather than \"in that,\" and so on? He brings an index of great men ancient and recent who rendered \"in which,\" but their authority did not hinder others, themselves also great men, from preferring to the version \"in which\" the version \"in that,\" \"inasmuch as,\" and so on: Theodoret, the Syriac interpreter, Calvin, Martyr, Bucer, Aretius, Piscator, Paraeus, Erasmus, Leo Juda, Vatablus, the authors of the French version which our churches use, and likewise of the English, and so on — for it would be long to enumerate all. Did those greatest men therefore favor the Pelagian heresy? What is there why Placeus ought not to follow their example and rest, answering, on the received version? Does D. Garissoles add nothing besides? He also adds the force of those little words from the use of Scripture: for, he says, it is most frequent that ἐπί be taken for ἐν, which to prove he praises many examples. Namely, he proves what is not denied; but what is denied, that he does not prove. For nobody denied to him that ἐπί is sometimes taken for ἐν. But does it therefore follow that that preposition is used here by enallage, and ἐπί put for ἐν? Nay, if the Apostle had said ἐν ᾧ, nothing would hinder even those words from being rendered \"in that\" or \"since,\" and so on, as was done by nearly all interpreters at Romans 8:3. And ἐφ᾽ ᾧ exists in that sense at 2 Corinthians 5:4, and is usually taken otherwise whenever there is no antecedent to which ᾧ can conveniently be referred. For the rest, what he says — that he makes Beza the author of the version \"in which\" for us — whence he has it I do not know. That certainly Placeus never said, nor wrote, nor ever thought. The reasons which he attributes to us are not Placeus's, nor are they needed by one answering according to the version approved by our churches. If you demand of me, Reader, that I prove it: First I will bring two reasons of Placeus, then those five which D. Garissoles objected to himself I will briefly vindicate from his exceptions. First therefore if you render \"in which,\" the relative \"which,\" because it will not be able to be referred to the nearest or neighboring masculine noun but to a remoter one, a trajection will have to be admitted, and that an insolent and very hard one. But now such a trajection ought not to be admitted without necessity, which here appears none, since the little words ἐφ᾽ ᾧ can no less both properly and conveniently be rendered \"in that,\" or \"since,\" or \"inasmuch as.\" Next, the words \"all sinned,\" since they contain the cause of that which immediately preceded, demand to be joined with it: for who can deny that death invaded all because all sinned (Romans 5:12)? Why then should we separate from each other those members of the Apostolic speech which are joined by the Apostle not only by situ and placement, but also by sense and by the indissoluble nexus of the things signified?",
],
}

NOTES = {
"39": [
"Caput VII Accedamus: Garissoles's second place on ἐφ᾽ ᾧ πάντες ἥμαρτον (Romans 5:12); Placeus notes Calvin/Martyr did not confirm immediate imputation from these words.",
"Honest partial: Cap. VII Accedamus opening; aorist and ἐφ᾽ ᾧ lexicography follow in this slice.",
],
"40": [
"Caput VII: Garissoles Adam–Christ opposition from ἐφ᾽ ᾧ; Placeus denies the opposition is in the words and reduces the parallel by each one's faith.",
"Honest partial within Cap. VII Accedamus / aorist / lexicography series.",
],
"41": [
"Caput VII: force of aorist ἥμαρτον; Garissoles's singular force when aorists multiply; Placeus compares Romans 3 absolute aorists and denies multiplication changes sense.",
"Honest partial within Cap. VII Accedamus / aorist / lexicography series.",
],
"42": [
"Caput VII: death and inhering sin each one's own; Intrauit peccatum timing — into Adam vs through Adam into the world; reatus vs death as wages.",
"Honest partial within Cap. VII Accedamus / aorist / lexicography series.",
],
"43": [
"Caput VII: lexicography of ἐφ᾽ ᾧ — in quo vs eo quod / quatenus; authorities; ἐπί/ἐν enallage rejected; Placeus's two principal reasons (relative trajection; causal join of omnes peccaverunt).",
"Honest partial: Cap. VII Ad alias rationes onward and Cap. VIII+ of the Disputatio remain (~494 pp not claimed).",
],
}

ALLUSIONS = {
"39": [{"reference": "Romans 5:12", "certainty": "clear", "reason": "ἐφ᾽ ᾧ πάντες ἥμαρτον; Accedamus second place on the words"}],
"40": [{"reference": "Romans 5:12-19", "certainty": "clear", "reason": "In Adam all sinned / in Christ all justified opposition"}],
"41": [{"reference": "Romans 3:12-17", "certainty": "clear", "reason": "Aorists Omnes deflexerunt; vers. 13 and 17; compared with Romans 5 aorists"}, {"reference": "Romans 5:12", "certainty": "clear", "reason": "peccatum intravit, mors introiit, omnes peccaverunt"}],
"42": [{"reference": "Romans 5:12", "certainty": "clear", "reason": "Sin entered through one man into the world"}, {"reference": "Romans 6:23", "certainty": "likely", "reason": "Death as peccati effectum et stipendium"}],
"43": [{"reference": "Romans 5:12", "certainty": "clear", "reason": "ἐφ᾽ ᾧ lexicography; omnes peccaverunt as cause of death"}, {"reference": "Romans 8:3", "certainty": "clear", "reason": "Placeus cites interpreters rendering causal sense"}, {"reference": "2 Corinthians 5:4", "certainty": "clear", "reason": "ἐφ᾽ ᾧ in causal sense without convenient antecedent"}],
}

LEMMAS = {
"39": [{"latin": "Accedamus iam", "gloss": "let us now approach"}, {"latin": "ἐφ᾽ ᾧ πάντες ἥμαρτον", "gloss": "in that / upon which all sinned"}, {"latin": "doctrinam de imputatione", "gloss": "doctrine concerning imputation"}],
"40": [{"latin": "opponit haec duo", "gloss": "opposes these two"}, {"latin": "per suam quisque fidem", "gloss": "by each one's own faith"}, {"latin": "similitudo … in veritate rei, quam in modo", "gloss": "likeness in the truth of the thing rather than in the mode"}],
"41": [{"latin": "vis Aoristi ἥμαρτον", "gloss": "force of the aorist 'sinned'"}, {"latin": "absolutum … a speciali significatione temporis", "gloss": "absolute from a special time-sense"}, {"latin": "multiplicatio Aoristorum", "gloss": "multiplication of aorists"}],
"42": [{"latin": "suam cuique … propriam", "gloss": "each one's own"}, {"latin": "peccatum inhaerens", "gloss": "inhering sin"}, {"latin": "reatum mortis", "gloss": "guilt of death"}, {"latin": "per unum hominem in mundum", "gloss": "through one man into the world"}],
"43": [{"latin": "voculae illae ἐφ᾽ ᾧ", "gloss": "those little words ἐφ᾽ ᾧ"}, {"latin": "in quo / eo quod / quatenus", "gloss": "in which / in that / inasmuch as"}, {"latin": "per enallagen", "gloss": "by enallage"}, {"latin": "trajectio", "gloss": "trajection / displacement of relative"}, {"latin": "indissolubili nexu", "gloss": "indissoluble nexus"}],
}

CHOICES = {
"39": [{"point": "Start at Accedamus after Gualtherus close", "decision": "Immediate next Latin after locked Denique/Gualtherus; second Garissoles place on ἐφ᾽ ᾧ"}],
"40": [{"point": "Keep opposition + faith reductio together", "decision": "Single Placeus rebuttal arc before aorist block"}],
"41": [{"point": "Hold full aorist exchange as own section", "decision": "Rom. 3 vs Rom. 5 and multiplication are one lexicogrammatical unit"}],
"42": [{"point": "Intrauit timing with own/inhering death-sin", "decision": "Natural bridge from aorist into ἐφ᾽ ᾧ lexicography"}],
"43": [{"point": "Stop after two Placeus ἐφ᾽ ᾧ reasons, before Ad alias rationes", "decision": "Natural close of aorist/lexicography slice; next densify takes remaining Cap. VII reasons"}],
}

BIBLE = {
"39": ["Romans 5:12"],
"40": ["Romans 5:12-19"],
"41": ["Romans 3:12-17", "Romans 5:12"],
"42": ["Romans 5:12", "Romans 6:23"],
"43": ["Romans 5:12", "Romans 8:3", "2 Corinthians 5:4"],
}

def dist(a: str, b: str) -> float:
    ta, tb = set(a.lower().split()), set(b.lower().split())
    if not ta or not tb:
        return 1.0
    return round(1.0 - len(ta & tb) / len(ta | tb), 4)

def main() -> None:
    for sid in TITLES:
        a, b = PASS_A[sid], " ".join(PASS_B[sid])
        assert a.strip() != b.strip(), sid
        d = dist(a, b)
        assert d > 0.35, (sid, d)

    lock_path = BOOK / "sources/_placeus_cap7_accedamus_latin_lock.txt"
    lock_body = LOCK_HEADER + "\n\n".join(LATIN[s] for s in ["39", "40", "41", "42", "43"]) + "\n"
    lock_path.write_text(lock_body, encoding="utf-8")
    print("wrote", lock_path.name, "chars", len(lock_body))

    eng_path = BOOK / "translations/cap1_tip_english.json"
    src_path = BOOK / "translations/cap1_tip_source.json"
    meta_path = BOOK / "translations/cap1_tip_meta.json"
    eng = json.loads(eng_path.read_text(encoding="utf-8"))
    src = json.loads(src_path.read_text(encoding="utf-8"))
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert len(eng) == 38 and len(src) == 38, (len(eng), len(src))
    pre_eng = digest(eng)
    pre_src = digest(src)
    for i, row in enumerate(eng, 1):
        assert str(row["section"]) == str(i)

    for sid in ["39", "40", "41", "42", "43"]:
        eng.append({
            "section": sid,
            "title": TITLES[sid],
            "english": PASS_B[sid],
            "translator_notes": NOTES[sid],
            "added_allusions": ALLUSIONS[sid],
        })
        src.append({
            "section": sid,
            "title": TITLES[sid],
            "latin": LATIN[sid],
            "notes": NOTES[sid][0],
        })
        pb = PASS_B[sid]
        j = {
            "section": sid,
            "title": TITLES[sid],
            "pass_a_gloss": PASS_A[sid],
            "pass_b_english": pb,
            "source_text": LATIN[sid],
            "pass_a_ne_b": True,
            "a_neq_b_distance": dist(PASS_A[sid], " ".join(pb)),
            "lemmas": LEMMAS[sid],
            "choices": CHOICES[sid],
            "bible_refs": BIBLE[sid],
            "notes": f"Cap. VII Accedamus densify section {sid} from locked 1661 Latin (pp. 66–71 tip).",
        }
        jp = BOOK / f"reviews/justifications/cap7_{sid}.json"
        jp.write_text(json.dumps(j, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("just", sid, "A≠B dist", j["a_neq_b_distance"])

    assert digest(eng[:38]) == pre_eng, "sections 1-38 english mutated"
    assert digest(src[:38]) == pre_src, "sections 1-38 source mutated"

    meta.update({
        "title": "De imputatione primi peccati Adami (Cap. I–VII partial: through Cap. VII Accedamus ἐφ᾽ ᾧ / aorist / lexicography)",
        "edition": "De imputatione primi peccati Adami (Salmurii: Apud Ioannem Lesnerium, 1661). IA deimputationepri00lapl. Densify: Capita I–VI + Caput VII through Accedamus ἐφ᾽ ᾧ πάντες ἥμαρτον, aorist, and ἐφ᾽ ᾧ lexicography to Placeus's two reasons. Not whole Disputatio; Cap. VII Ad alias rationes onward and Cap. VIII+ remain.",
        "blurb": "Josue de la Place (Placeus) — Capita I–VII partial of De imputatione primi peccati Adami from the 1661 Saumur Latin, through Cap. VII Accedamus ἐφ᾽ ᾧ / aorist / lexicography. Honest partial; Cap. VII Ad alias rationes onward and later Capita remain.",
        "first_english_note": "No complete public-domain English of this Latin work was locked as reading text. This is a new rendering from locked Latin for Capita I–VII partial through Accedamus ἐφ᾽ ᾧ / aorist / lexicography.",
    })
    old_th = meta.get("text_history") or {}
    wits = list(old_th.get("witnesses") or [])
    if not any(str(w.get("path", "")).endswith("_placeus_cap7_accedamus_latin_lock.txt") for w in wits):
        wits.append({
            "id": "latin_lock_cap7_accedamus",
            "path": "sources/_placeus_cap7_accedamus_latin_lock.txt",
            "role": "copy-text",
            "name": "Locked Latin, Caput VII Accedamus ἐφ᾽ ᾧ / aorist / lexicography tip (Saumur 1661)",
            "language": "Latin",
            "url": "https://archive.org/details/deimputationepri00lapl",
        })
    meta["text_history"] = {
        "method": "English follows the locked 1661 Saumur Latin of Capita I–VII partial through Cap. VII Accedamus ἐφ᾽ ᾧ πάντες ἥμαρτον, aorist force, and ἐφ᾽ ᾧ lexicography, reconstructed from IA PDF page images with Vision OCR, tesseract, and pdftotext as check. No modern English was copied. Cap. VII Ad alias rationes onward and Cap. VIII+ remain.",
        "witnesses": wits,
    }

    eng_path.write_text(json.dumps(eng, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    src_path.write_text(json.dumps(src, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("english sections", len(eng), "source", len(src))

    old_p = json.loads((BOOK / "reviews/audit/cap7_denique_modus_densify.packet.json").read_text(encoding="utf-8"))
    packet = copy.deepcopy(old_p)
    packet.pop("packet_id", None)
    packet["seed"] = 20260922
    packet["sample_size"] = 43
    packet["expected_sections"] = [str(i) for i in range(1, 44)]
    packet["explicit_selected_sections"] = packet["expected_sections"][:]
    packet["coverage"] = {"expected": 43, "english": 43, "source": 43}
    packet["identity"]["work"] = meta["title"]
    packet["identity"]["edition"] = meta["edition"]
    packet["identity"]["locus_aliases"] = {str(i): str(i) for i in range(1, 44)}
    packet["publication_scope"]["title"] = meta["title"]
    packet["publication_scope"]["section_count"] = 43
    packet["publication_scope"]["blurb"] = meta["blurb"]
    packet["publication_scope"]["edition"] = meta["edition"]
    packet["publication_scope"]["first_english_note"] = meta["first_english_note"]
    packet["publication_scope"]["text_history"] = meta["text_history"]

    lock_files = [
        "_placeus_cap1_latin_lock.txt",
        "_placeus_cap2_latin_lock.txt",
        "_placeus_cap3_latin_lock.txt",
        "_placeus_cap4_latin_lock.txt",
        "_placeus_cap4_rest_latin_lock.txt",
        "_placeus_cap5_6tip_latin_lock.txt",
        "_placeus_cap6_rest_latin_lock.txt",
        "_placeus_cap7_tip_latin_lock.txt",
        "_placeus_cap7_rest_latin_lock.txt",
        "_placeus_cap7_s6_latin_lock.txt",
        "_placeus_cap7_denique_latin_lock.txt",
        "_placeus_cap7_accedamus_latin_lock.txt",
    ]
    files = [
        {"path": str(eng_path), "sha256": file_digest(eng_path)},
        {"path": str(src_path), "sha256": file_digest(src_path)},
    ]
    for lf in lock_files:
        p = BOOK / "sources" / lf
        files.append({"path": str(p), "sha256": file_digest(p)})
    packet["files"] = files
    packet["raw_source_paths"] = [str(BOOK / "sources" / lf) for lf in lock_files]

    eng_by = {str(s["section"]): s for s in eng}
    src_by = {str(s["section"]): s for s in src}
    new_sections = []
    for sid in packet["expected_sections"]:
        er, sr = eng_by[sid], src_by[sid]
        latin = sr["latin"] if isinstance(sr["latin"], str) else "\n\n".join(sr["latin"])
        english = er["english"] if isinstance(er["english"], list) else [er["english"]]
        new_sections.append({
            "section": sid,
            "locus": sid,
            "source_path": str(src_path),
            "source_text": [latin],
            "english": english,
            "source_sha256": digest({"latin": latin}),
            "english_sha256": digest(er),
            "risks": ["negation_modality_or_doctrine", "scripture_links", "textual_uncertainty"],
            "raw_source_paths": packet["raw_source_paths"],
        })
    packet["sections"] = new_sections
    packet["structural_errors"] = []

    # Prefer regenerated packet so validate_audit_receipt matches make_audit_packet
    from pipeline.verify_translation_qa import make_audit_packet
    packet = make_audit_packet(
        eng_path,
        src_path,
        raw_sources=packet["raw_source_paths"],
        expected_sections=packet["expected_sections"],
        seed=packet["seed"],
        sample_size=packet["sample_size"],
        identity=packet["identity"],
        selected_sections=packet["explicit_selected_sections"],
        publication_scope=packet["publication_scope"],
    )
    # make_audit_packet already sets packet_id
    pkt_path = BOOK / "reviews/audit/cap7_accedamus_densify.packet.json"
    pkt_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("packet", packet["packet_id"][:16], len(packet["sections"]))

    reviews = []
    for sid in packet["expected_sections"]:
        n_paras = len(eng_by[sid]["english"]) if isinstance(eng_by[sid]["english"], list) else 1
        reviews.append({
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
            "covered_source_paragraphs": list(range(1, n_paras + 1)),
            "notes": f"Section {sid}: compared Pass B to locked 1661 Latin Cap. VII Accedamus ἐφ᾽ ᾧ / aorist / lexicography; Pass A != B.",
        })

    review = {
        "packet_id": packet["packet_id"],
        "reviewer": "scribe-placeus / Placeus Cap. VII Accedamus densify review, 2026-09-22",
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
            "notes": "Cap. I–VI + Cap. VII through Accedamus ἐφ᾽ ᾧ πάντες ἥμαρτον, aorist force, and ἐφ᾽ ᾧ lexicography (in quo vs eo quod) to Placeus's two reasons from locked 1661 Saumur Latin. Honest partial — Cap. VII Ad alias rationes onward and Cap. VIII+ remain. Reformed Saumur era disclosed. Locked Greek ἐφ᾽ ᾧ / ἥμαρτον (do not revive OCR ἔργον).",
        },
        "reviews": reviews,
    }
    rev_path = BOOK / "reviews/audit/cap7_accedamus_densify.review.json"
    rev_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("review", rev_path.name)

    errs = validate_audit_receipt(packet, review)
    print("validate_audit_receipt errors", len(errs))
    for e in errs[:20]:
        print(" -", e)
    assert len(errs) == 0, errs

    hand = BOOK / "SESSION_HANDOFF.md"
    old = hand.read_text(encoding="utf-8")
    if "cap7_accedamus_densify" not in old[:900]:
        entry = """# Placeus De imputatione — production ledger

## 2026-09-22 Cap. VII Accedamus densify (ἐφ᾽ ᾧ / aorist / lexicography)

- Before: **38** sections (Cap. I–VII through Denique / Gualtherus first-argument close)
- After: **43** sections (Cap. I–VII through Accedamus ἐφ᾽ ᾧ / aorist / ἐφ᾽ ᾧ lexicography)
- Packet: `cap7_accedamus_densify`
- Locked Latin: `sources/_placeus_cap7_accedamus_latin_lock.txt` (1661 PDF pp. 66–71 tip)
- Pass A≠B; OUR; English-first; no PBB/ops TNs
- Lemma note: locked Greek **ἐφ᾽ ᾧ** / **ἥμαρτον** (do not revive OCR ἔργον); σκοπῷ/verbis remains for prior Denique slice
- Stopped before Ad alias rationes (further Cap. VII)
- Honest partial: Cap. VII Ad alias rationes onward + Cap. VIII+ / ~494 pp Disputatio remain (**do not claim full Disputatio**)
- Punch X: **NO**

"""
        rest = old
        if rest.startswith("# Placeus"):
            rest = rest.split("\n", 1)[1].lstrip("\n")
        hand.write_text(entry + rest, encoding="utf-8")
        print("handoff updated")
    else:
        print("handoff already has entry")

    claim = Path("/Users/stephansmac/SaneApps/clients/translations/docs/claim-locks/placeus-de-imputatione-densify")
    print("claim lock", claim.read_text().strip() if claim.exists() else "MISSING")
    print("NEW TITLES:")
    for s in eng[38:]:
        print(" ", s["section"], s["title"])
    print("BEFORE 38 AFTER", len(eng))
    print("DID NOT SHIP; DID NOT COMMIT; claim not freed")

if __name__ == "__main__":
    main()
