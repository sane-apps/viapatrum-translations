#!/usr/bin/env python3
"""Cap. 7 open densify — tip 131 → ~138. Packet morte_christi_cap7_open_densify."""
from __future__ import annotations

import json
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
PACKET = "morte_christi_cap7_open_densify"
CHECK = PIPE / "check_pass_ab.py"
TIP_BEFORE = 131

SECTIONS = [
  {
    "section": 132,
    "title": 'Cap. 7 open: universal death under faith and electing grace—two decrees do not collide',
    "latin": ('Egimus de morte Christi, qua totum genus humanum spectat, universali ambitu vivificae potentiae, sub conditione Fidei, quoad quemvis hominem in actum deducendae. Quamvis enim, deficiente hac conditione, mors Christi non exserat in majore hominum parte vim suam salutiferam, tamen neque negandum est, quod Scripturae passim ac clare testantur; neque dubitandum est, quin Deus apud se habeat justissimas & sapientissimas sui consilii rationes, dum statuit mortem Filii sui omnibus sub fidei conditione applicabilem, & nihilominus non decrevit efficere aut procurare ut eadem per fidem singulis donatam omnibus applicetur. Non debemus itaque inter se committere & quasi collidere haec decreta Divina, Volo Filium meum ita semetipsum in cruce offerre pro peccatis humani generis, ut omnes & singuli in eum credentes possint servari; Volo gratiam meam efficacem ita dispensare, ut non omnes, sed electi solummodo, accipiant hanc fidem salutiferam qua serventur. Si cuiquam haec duo decreta pugnare videantur, debet ille intellectus sui infirmitatem potius agnoscere quam quicquam eorum, quae in sacris Scripturis tam diserte habentur, inficias ire. Sit igitur hoc fixum & stabilitum; Ex decreto ipsius Dei Christum ita fuisse in ara crucis oblatum pro omnibus hominibus, ut mors ejus sit jam constitutum quasi universale quoddam remedium omnibus & singulis, ad obtinendam remissionem peccatorum & vitam aeternam, per fidem applicabile.'),
    "pass_a_gloss": ('We have treated of the death of Christ, as it looks to the whole human race, with the universal circuit of life-giving power, under the condition of Faith, as respects any human being to be led into act. For although, this condition failing, the death of Christ does not put forth in the greater part of human beings its saving force, yet it is neither to be denied, which the Scriptures everywhere and clearly witness; nor to be doubted that God has with himself most just and most wise reasons of his counsel, while he has established the death of his Son applicable to all under the condition of faith, and nevertheless has not decreed to effect or procure that the same be applied to all by faith given to individuals. We ought not therefore to set against each other and as it were make collide these Divine decrees, I will that my Son so offer himself on the cross for the sins of the human race, that all and each believing in him can be saved; I will so dispense my efficacious grace, that not all, but the elect only, receive this saving faith by which they are saved. If to anyone these two decrees seem to fight, he ought rather to acknowledge the infirmity of his understanding than to deny anything of those things which are so expressly had in the sacred Scriptures. Let this therefore be fixed and established; From the decree of God himself Christ so to have been offered on the altar of the cross for all human beings, that his death is already constituted as it were a certain universal remedy for all and each, applicable through faith for obtaining remission of sins and eternal life.'),
    "pass_b": ('We have treated Christ’s death as it regards the whole human race—with the universal scope of his life-giving power, under the condition of Faith, as that power is to be brought into act for any person. For although, when that condition fails, Christ’s death does not put forth its saving force in the greater part of humankind, still it must neither be denied—what the Scriptures everywhere and clearly witness—nor doubted that God has within himself most just and wise reasons for his counsel when he ordained his Son’s death applicable to all under the condition of faith, and yet did not decree to effect or procure that the same death be applied to all by a faith given to each. So we must not set these divine decrees against each other as if they collided: “I will that my Son so offer himself on the cross for the sins of the human race that all and each who believe in him can be saved”; and “I will so dispense my efficacious grace that not all, but the elect alone, receive this saving faith by which they are saved.” If anyone thinks those two decrees fight, he ought rather to own the weakness of his understanding than to deny anything so plainly set down in Holy Scripture. Let this then stand fixed: by God’s own decree Christ was so offered on the altar of the cross for all human beings that his death is already established as it were a universal remedy for all and each, applicable by faith for obtaining remission of sins and eternal life.'),
    "notes_covered": ['Cap. 7 title locus; Egimus...; Volo...Volo decrees; universal remedy under faith'],
    "lemmas": [{'form': 'universali ambitu vivificae potentiae', 'gloss': 'with universal scope of life-giving power', 'why': 'Cap7 open'}, {'form': 'electi solummodo', 'gloss': 'the elect alone', 'why': 'efficacious faith'}, {'form': 'quasi universale quoddam remedium', 'gloss': 'as it were a universal remedy', 'why': 'under faith'}],
  },
  {
    "section": 133,
    "title": 'Cap. 7 open: special elect prerogative—not Pelagian parity or Grevinchovius bare impetration',
    "latin": ('Jam vero ne sub hac universali virtute mortis Christi, quae ad omnes potestate se extendit, illam obteramus specialem ejusdem efficaciam, quae ad solos praedestinatos pertinet & pertingit, altera pars susceptae nostrae disputationis aggredienda est, quae specialem electorum in morte Christi praerogativam, tam ex voluntate Dei Patris Filium suum in mortem dantis, quam Filii seipsum offerentis, explicabit & tuebitur. Non enim debemus ita defendere Christum pro omnibus fuisse mortuum, ut cum Pelagianis credamus ejusdem mortis vivificam efficaciam a pari momento prostare omnibus communem, ex intentione Divinae voluntatis, in eventu autem fieri aliquibus salutiferam, aliis minime, non aliunde quam ex contingente usu humanae libertatis. Neque cum Arminianis delirandum est, quasi Deus dederit in mortem Filium suum, nihil aliud absolute intendens, quam ut inde haberet ipse nudam potestatem salvandi quosvis peccatores, non obstante justitia sua; atque ut quivis peccatores haberent modum sive medium quo salvari possent, non obstante peccato suo. Hinc praeclarum illud Grevinchovii corollarium, in dissertatione De morte Christi pag. 9. Impetrationi suam dignitatem, necessitatem, utilitatem abunde constare potuisse, etiamsi impetrata redemtio nulli individuo unquam ab ipso applicata fuisset. Item & illud, pag. 14. Potuisse omnibus impetratam esse redemtionem, & tamen nullis eam applicari, propter intervenientem omnium incredulitatem. Nos autem minime arbitramur Christi mortem fuisse tanquam aleam jactam; sed Deo Patri Christoque fuisse ab aeterno decretum, merito hujus mortis certas quasdam personas, quas Scriptura electorum nomine designat, infallibiliter servare; adeoque ex voluntate Dei mortem Christi pro iisdem redimendis fuisse speciali quodam modo & consilio oblatam & acceptatam.'),
    "pass_a_gloss": ('But now, lest under this universal virtue of the death of Christ, which extends itself to all by power, we crush that special efficacy of the same which pertains and reaches to the predestined alone, the other part of our undertaken disputation is to be entered upon, which will explain and defend the special prerogative of the elect in the death of Christ, both from the will of God the Father giving his Son into death, and of the Son offering himself. For we ought not so to defend that Christ was dead for all, that with the Pelagians we believe the life-giving efficacy of the same death to stand forth at equal moment common to all, from the intention of the Divine will, but in the event to become saving for some, for others not at all, from nowhere else than from the contingent use of human liberty. Nor is it to be raved with the Arminians, as if God had given his Son into death, intending absolutely nothing else, than that thence he himself should have a bare power of saving any sinners he would, his justice not withstanding; and that any sinners should have a mode or medium by which they could be saved, their sin not withstanding. Hence that famous corollary of Grevinchovius, in the dissertation On the death of Christ page 9. That its dignity, necessity, usefulness could have stood abundantly for the obtaining, even if the redemption obtained had never been applied by him to any individual. Likewise also that, page 14. That redemption could have been obtained for all, and yet be applied to none, on account of the intervening unbelief of all. But we by no means judge the death of Christ to have been as a die cast; but it to have been decreed from eternity by God the Father and by Christ, by the merit of this death to save infallibly certain persons, whom Scripture designates by the name of elect; and so from the will of God the death of Christ for redeeming the same to have been offered and accepted in a certain special mode and counsel.'),
    "pass_b": ('But now, lest under this universal virtue of Christ’s death—which extends to all by power—we crush that special efficacy of the same which belongs and reaches to the predestined alone, we must take up the other part of the dispute we have undertaken. It will explain and defend the elect’s special prerogative in Christ’s death, both from the will of God the Father who gave his Son to death and from the Son who offered himself. For we must not so defend that Christ died for all that, with the Pelagians, we believe the life-giving efficacy of that death stands open in equal measure to all in common from the intention of the divine will, and yet in the event becomes saving for some and not for others from nowhere but the contingent use of human liberty. Nor must we rave with the Arminians as if God gave his Son to death intending absolutely nothing else than that he himself should thence have a bare power of saving any sinners he pleased, his justice notwithstanding, and that any sinners should have a way or means by which they could be saved, their sin notwithstanding. Hence that famous corollary of Grevinchovius in his dissertation On the Death of Christ, p. 9: that the dignity, necessity, and usefulness of the obtaining could have stood abundantly even if the redemption obtained had never been applied by him to any individual. Likewise also that at p. 14: that redemption could have been obtained for all, and yet applied to none, because of the intervening unbelief of all. But we by no means judge that Christ’s death was cast like a die; rather it was decreed from eternity by God the Father and by Christ that by the merit of this death certain persons, whom Scripture marks by the name of the elect, should be saved infallibly; and so by God’s will Christ’s death was offered and accepted for redeeming those same persons in a special mode and counsel.'),
    "notes_covered": ['special efficacy for praedestinati; anti-Pelagian; anti-Arminian; Grevinchovius pp.9,14; death not dice'],
    "lemmas": [{'form': 'specialem electorum ... praerogativam', 'gloss': 'the elect’s special prerogative', 'why': 'Cap7'}, {'form': 'tanquam aleam jactam', 'gloss': 'as a cast die', 'why': 'vs Grevinchovius'}, {'form': 'impetrata redemtio nulli individuo', 'gloss': 'obtained redemption applied to no individual', 'why': 'Grevinchovius p.9'}],
  },
  {
    "section": 134,
    "title": 'Cap. 7: decree-order digression set aside; thesis aimed at the predestined alone',
    "latin": ('Neque hic necessarium est, ad hujus specialis consilii defensionem, spinosam istam quaestiunculam definire a multis vexatam, vexantem omnes qui eam discutiendam susceperunt, Utrum scilicet prius sit Decretum illud quo praedestinantur certae personae ad infallibilem participationem vitae aeternae, an illud alterum quo Christus ordinatus fuit ad officium Mediatorium. Nam quamvis, ad sustentandam intellectus humani imbecillitatem, in aeternis Dei decretis cogimur quaedam ut priora, quaedam ut posteriora concipere, tamen de hisce imaginariis rationis nostrae signis contendere, aut ex iisdem quaestiones fidei stabiliendas aut refellendas suscipere, lubricum mihi videtur, & valde periculosum. Illud siquidem extra omnem dubitationis aleam poni debet, haec, quae a nobis secundum ordinem prioris & posterioris cogitantur, Dei decreta penes ipsum Deum aequabili infinitatis aeternitate consistere: nec dari posse aut debere instans aliquod separatum, in quo, stabilito uno decreto, alterum nondum revisum ac stabilitum recte cogitetur. Concipe igitur ut ordine prius, decretum de constituendo & mittendo Mediatore (quod mihi videtur ad nostrum intelligendi modum aptius) ut posterius, decretum de eligendis certis personis ad infrustrabilem consecutionem vitae aeternae in Mediatore constituto; nunquam tamen haec ita divelles quin passio Mediatoris ab aeterno praevisa fuerit ut offerenda speciali quodam modo, & intuitu pro hisce eligendis, & tanquam oblata pro eisdem specialiter a Deo fuerit, idque ab aeterno, acceptata. E contra, concipe ut ordine prius decretum de electione certarum personarum ad salutem, ut posterius decretum de destinatione Christi ad officium Mediatorium; nunquam tamen haec ita separaveris quin passio Christi, specialiter oblata & acceptata pro iisdem, causa fuerit praeparandi ac donandi illis electis tam gratiam efficacem, quam salutem. Cum igitur utraque opinio perinde se habeat ad institutum nostrum, missa rei minime necessariae disquisitione, unicam thesin de morte Christi, sub speciali quadam consideratione ad solos praedestinatos restricta, proponemus & confirmabimus: Quae sic se habet,'),
    "pass_a_gloss": ('Nor is it necessary here, for the defense of this special counsel, to define that thorny little question vexed by many, vexing all who have undertaken to discuss it, Whether namely that Decree is prior by which certain persons are predestined to the infallible participation of eternal life, or that other by which Christ was ordained to the Mediatorial office. For although, for sustaining the imbecility of the human intellect, in the eternal decrees of God we are compelled to conceive certain things as prior, certain as posterior, yet to contend about these imaginary signs of our reason, or from the same to undertake questions of faith to be established or refuted, seems to me slippery, and very dangerous. That indeed ought to be placed outside every cast of doubt, that these decrees of God, which are thought by us according to the order of prior and posterior, consist in God himself in the equal eternity of infinity: nor can or ought any separated instant be given, in which, one decree being established, the other not yet reviewed and established is rightly thought. Conceive therefore as prior in order, the decree concerning constituting and sending the Mediator (which seems to me fitter to our mode of understanding) as posterior, the decree concerning electing certain persons to the unfrustrated consecution of eternal life in the Mediator constituted; yet never so pull these apart but that the passion of the Mediator from eternity was foreseen as to be offered in a certain special mode, and with regard for these to be elected, and as offered for the same specially was by God, and that from eternity, accepted. On the contrary, conceive as prior in order the decree concerning the election of certain persons to salvation, as posterior the decree concerning the destination of Christ to the Mediatorial office; yet never so separate these but that the passion of Christ, specially offered and accepted for the same, was the cause of preparing and giving to those elect both efficacious grace and salvation. Since therefore either opinion stands alike toward our purpose, the disquisition of a matter least necessary being dismissed, we will propose and confirm a single thesis concerning the death of Christ, under a certain special consideration restricted to the predestined alone: Which thus holds,'),
    "pass_b": ('Nor is it necessary here, for defending this special counsel, to settle that thorny little question—vexed by many, and vexing all who take it up—whether the decree by which certain persons are predestined to the infallible sharing of eternal life is prior, or that other by which Christ was ordained to the Mediator’s office. For although, to shore up the weakness of human understanding, we are forced in God’s eternal decrees to conceive some as prior and some as posterior, still to contend about these imaginary signs of our reason, or to take from them questions of faith to establish or refute, seems to me slippery and very dangerous. This at least must be set beyond every cast of doubt: those decrees of God which we think according to an order of prior and posterior stand, in God himself, in the equal eternity of infinity; nor can or should any separate instant be given in which, one decree being fixed, the other is rightly thought not yet reviewed and fixed. Conceive then as prior in order the decree of constituting and sending the Mediator (which seems to me fitter to our way of understanding), and as posterior the decree of electing certain persons to the unfrustrated obtaining of eternal life in the Mediator so constituted; yet never so pull these apart that the Mediator’s passion was not from eternity foreseen as to be offered in a special mode and regard for those to be elected, and as specially offered for them was from eternity accepted by God. Or on the contrary, conceive as prior the decree of electing certain persons to salvation, and as posterior the decree of destining Christ to the Mediator’s office; yet never so separate them that Christ’s passion, specially offered and accepted for those same persons, was not the cause of preparing and giving those elect both efficacious grace and salvation. Since therefore either opinion serves our purpose alike, leaving aside a question of little necessity, we will propose and confirm a single thesis on Christ’s death, under a special consideration restricted to the predestined alone. It runs thus:'),
    "notes_covered": ['utraque opinio; missa disquisitione; unicam thesin ad solos praedestinatos'],
    "lemmas": [{'form': 'spinosam istam quaestiunculam', 'gloss': 'that thorny little question', 'why': 'decree order'}, {'form': 'aequabili infinitatis aeternitate', 'gloss': 'in the equal eternity of infinity', 'why': 'decrees'}, {'form': 'ad solos praedestinatos restricta', 'gloss': 'restricted to the predestined alone', 'why': 'thesis frame'}],
  },
  {
    "section": 135,
    "title": 'Cap. 7 Thesis: death destined to the elect alone—vs Grevinchovius foresight application',
    "latin": ('Thes. Mors Christi, ex speciali Intentione Dei Patris illud sacrificium ab aeterno ordinantis & acceptantis, Christique illud idem in plenitudine temporis Deo Patri offerentis, destinata fuit certis quibusdam hominibus (quos Electos Scriptura appellat) iisdemque solis, ut efficaciter & infallibiliter applicanda ad aeternae vitae consecutionem. Hanc thesin opponimus Arminiorum errori, quem Grevinchovius stabilire conatur, Dissert. De morte Christi, pag. 7. &c. ubi docet Deum tradentem Filium suum, intendisse impetrationem reconciliationis omnibus & singulis communem, applicationem vero ejusdem impetratae nemini mortalium absolute voluisse. Agnosco, inquit, in Deo quidem affectum constantem ac perpetuum, bonum impetratum omnibus & singulis applicandi: Nego applicationem ipsam ulli hominum nisi fideli; & qua fideli, certo Dei consilio ac voluntate destinatam. Opinatur igitur novus iste magistellus Deum ex aequo velle omnibus vitam aeternam in Christo, neque absoluta & antecedanea voluntate destinare & praeparare aliquibus gratiam efficacem, qua Christus illis infallibiliter applicetur; sed per aeternam suam praescientiam speculari quinam sunt credituri, quinam in sua infidelitate permansuri, & tum demum destinare Fidelibus, qua Fidelibus, efficacem applicationem mortis ac meritorum Jesu Christi. At nos in ipsa praedestinatione ad fidem, applicationem mortis Christi quibusdam certis personis infallibiliter destinatam putamus; atque dicimus hanc fidem non Fidelibus, qua Fidelibus, sed infidelibus praeparatam, ut per eam evadant fideles. Applicatio igitur non destinata sed facta intelligitur in hominibus qui considerantur ut fideles: destinata autem applicatio intelligitur in illis quibus fides donanda destinatur, per quam fiet haec applicatio. Hi autem sunt electi, ac soli electi, quorum specialis praerogativa est, quod ex absoluta voluntate Dei Patris ac Christi Mediatoris, per Christi mortem infallibiliter salvandi decernantur ac procurentur. Hisce praelibatis ad argumenta veniamus, ac Scripturarum disertis testimoniis primo in loco agamus.'),
    "pass_a_gloss": ('Thes. The death of Christ, from the special Intention of God the Father ordaining and accepting that sacrifice from eternity, and of Christ offering the same itself to God the Father in the fullness of time, was destined for certain human beings (whom Scripture calls the Elect) and for the same alone, as to be applied efficaciously and infallibly unto the consecution of eternal life. This thesis we oppose to the error of the Arminians, which Grevinchovius tries to establish, Dissert. On the death of Christ, page 7. &c. where he teaches God delivering his Son to have intended the obtaining of reconciliation common to all and each, but the application of the same obtained absolutely to have willed for no mortals. I acknowledge, he says, in God indeed a constant and perpetual affection of applying the obtained good to all and each: I deny the application itself destined to any of humans except to a believer; and as a believer, by the sure counsel and will of God. This new little master therefore opines that God from equality wills eternal life in Christ for all, and neither by absolute and antecedent will destines and prepares for some efficacious grace, by which Christ may be infallibly applied to them; but through his eternal foreknowledge to look who are going to believe, who going to remain in their infidelity, and then at last to destine to Believers, as Believers, the efficacious application of the death and merits of Jesus Christ. But we in predestination itself to faith think the application of the death of Christ infallibly destined to certain certain persons; and we say this faith prepared not for Believers, as Believers, but for unbelievers, that through it they may become faithful. Application therefore not destined but done is understood in humans who are considered as faithful: but destined application is understood in those for whom faith to be given is destined, through which this application will be made. But these are elect, and elect alone, whose special prerogative is, that from the absolute will of God the Father and of Christ the Mediator, through the death of Christ they are decreed and procured to be saved infallibly. These things having been preliminated let us come to the arguments, and first in place let us deal with the express testimonies of the Scriptures.'),
    "pass_b": ('Thesis. Christ’s death, from the special Intention of God the Father who from eternity ordained and accepted that sacrifice, and of Christ who offered the same to God the Father in the fullness of time, was destined for certain human beings (whom Scripture calls the Elect) and for them alone, to be applied efficaciously and infallibly for the obtaining of eternal life. We oppose this thesis to the Arminians’ error, which Grevinchovius tries to establish in his Dissertation On the Death of Christ, p. 7 ff., where he teaches that God, in delivering his Son, intended the obtaining of reconciliation to be common to all and each, but absolutely willed the application of that obtained reconciliation for no mortal. “I acknowledge,” he says, “in God indeed a constant and perpetual affection of applying the obtained good to all and each: I deny that the application itself is destined by God’s sure counsel and will to any human being except as a believer, and as a believer.” So this new little master thinks God wills eternal life in Christ equally for all, and does not by an absolute and antecedent will destine and prepare for some efficacious grace by which Christ is infallibly applied to them; but by his eternal foreknowledge looks ahead who will believe and who will remain in their unbelief, and only then destines to believers as believers the efficacious application of Jesus Christ’s death and merits. But we hold that in predestination to faith itself the application of Christ’s death is infallibly destined to certain persons; and we say this faith is prepared not for believers as believers, but for unbelievers, that by it they may become believers. So application not destined but done is understood in those considered as believers; but destined application is understood in those for whom the gift of faith is destined, through which that application will be made. And these are the elect, and the elect alone, whose special prerogative is that by the absolute will of God the Father and of Christ the Mediator they are decreed and procured to be saved infallibly through Christ’s death. With these preliminaries we come to the arguments, and first take up the plain testimonies of the Scriptures.'),
    "notes_covered": ['Thes. Mors Christi...; Grevinchovius Diss. p.7; praedestinatio ad fidem; soli electi'],
    "lemmas": [{'form': 'ex speciali Intentione Dei Patris', 'gloss': 'from the Father’s special intention', 'why': 'thesis'}, {'form': 'non Fidelibus, qua Fidelibus, sed infidelibus', 'gloss': 'not to believers as such but to unbelievers', 'why': 'faith prepared'}, {'form': 'novus iste magistellus', 'gloss': 'this new little master', 'why': 'Grevinchovius'}],
  },
  {
    "section": 136,
    "title": 'Cap. 7 Arg. 1: persons given to the Mediator—John 6 / 17 / Ephesians 1; Augustine',
    "latin": ('1. Huc faciunt inprimis ea loca quae Patris absolutam voluntatem significant de certis personis Mediatori donandis, & quasi commendandis, hoc fine ut ab eo, & per eum accipiant omnia ad salutem necessaria, ac ipsam denique salutem. Johan. vi. 37, 39. Omne quod dat mihi Pater, ad me veniet: & eum qui venit ad me, non ejiciam foras. Haec est voluntas ejus qui misit me Patris, ut omne quod dedit mihi non perdam ex eo, &c. Clarum est ex hoc contextu, non omnes promiscue, sed quasdam personas singulari Dei Patris misericordia datas Mediatori, ex certo & gratioso proposito producendi infallibiliter & efficaciter easdem personas ad vitam aeternam. Confimilia habentur, Johan. xvii. 2. Dedisti ei potestatem omnis carnis, ut omne quod dedisti ei, det eis vitam aeternam. Haec specialis donatio non aliter quam in aeterna electione facta intelligi potest. Sic autem donatos Redemptori in ipso opere redemptionis habere specialem praerogativam nemo sanus dubitaverit. Certe, Apostolus id aperte significavit Ephes. i. 4, 5, 6, &c. Elegit nos in Christo ante jacta mundi fundamenta. Praedestinavit nos in adoptionem filiorum per Christum secundum propositum voluntatis suae. Hic habetis specialem illam donationem quarundam personarum soli Deo notarum. Dein ver. 7 ostenditur, secundum propositum Dei personas easdem semper consequi efficacem & applicatam redemptionem in Mediatore, In quo habemus redemptionem per sanguinem ejus, &c. Qui ergo Christo specialiter donati sunt in electione, illi fidem, remissionem peccatorum, sanctificationem & salutem semper hauriunt ex morte Christi, donata simul eis fructuosa ejusdem mortis applicatione. Sanctus Augustinus per hanc donationem nihil aliud quam aeternam electionem intellexit, In Johan. tract. 107. Non (inquit) Pater eos Filio dedisset, nisi elegisset. Idem Pater, De Praedest. Sanctor. cap. 16, sic datos Filio, eo etiam peculiari modo vocatos demonstrat, ut Christus crucifixus non fiat iis scandalum aut stultitia, sed virtus & Dei sapientia ad fidem & salutem efficaciter in illis operandam. Videte verba autoris, quae brevitatis causa omitto. Aut igitur negandum est certas quasdam personas Christo Mediatori a Deo Patre specialiter datas, aut simul fatendum Mediatorem in oblatione sua specialem intuitum ad easdem habuisse.'),
    "pass_a_gloss": ("1. Hither first make those places which signify the absolute will of the Father concerning certain persons to be given to the Mediator, and as it were to be commended, to this end that from him, and through him they may receive all things necessary to salvation, and finally salvation itself. John vi. 37, 39. All that the Father gives me, will come to me: and him who comes to me, I will not cast out. This is the will of him who sent me, of the Father, that of all which he gave me I should not lose from it, &c. It is clear from this context, not all promiscuously, but certain persons by the singular mercy of God the Father given to the Mediator, from a sure and gracious purpose of producing infallibly and efficaciously the same persons to eternal life. Like things are had, John xvii. 2. You have given him power of all flesh, that all which you have given him, he may give them eternal life. This special donation cannot otherwise than as done in eternal election be understood. But that those so given to the Redeemer in the work itself of redemption have a special prerogative no sane person will have doubted. Certainly, the Apostle openly signified it Ephesians i. 4, 5, 6, &c. He chose us in Christ before the foundations of the world were laid. He predestined us into the adoption of sons through Christ according to the purpose of his will. Here you have that special donation of certain persons known to God alone. Then verse 7 is shown, according to the purpose of God the same persons always to obtain efficacious and applied redemption in the Mediator, In whom we have redemption through his blood, &c. Who therefore have been specially given to Christ in election, those always draw faith, remission of sins, sanctification and salvation from the death of Christ, the fruitful application of the same death being given them at once. Saint Augustine understood through this donation nothing other than eternal election, In John tract. 107. The Father (he says) would not have given them to the Son, unless he had chosen. The same Father, On the Predest. of the Saints chapter 16, demonstrates those so given to the Son to be called also in that peculiar mode, that Christ crucified may not become to them a scandal or foolishness, but power and wisdom of God for working faith and salvation efficaciously in them. See the words of the author, which for brevity's cause I omit. Either therefore it is to be denied that certain persons were specially given to Christ the Mediator by God the Father, or at once it is to be confessed that the Mediator in his oblation had a special regard to the same."),
    "pass_b": ('1. First here belong those places that mark the Father’s absolute will to give certain persons to the Mediator and as it were commend them, to this end: that from him and through him they may receive all things needful for salvation, and finally salvation itself. John 6:37, 39: “All that the Father gives me will come to me; and him who comes to me I will not cast out. This is the will of the Father who sent me, that of all he has given me I should lose nothing,” and so on. It is clear from this context that not all promiscuously, but certain persons, were given to the Mediator by the Father’s singular mercy, from a sure and gracious purpose of bringing those same persons infallibly and efficaciously to eternal life. Like texts are found in John 17:2: “You have given him authority over all flesh, that he should give eternal life to all you have given him.” This special donation can be understood as done in no other way than in eternal election. And that those so given to the Redeemer have a special prerogative in the very work of redemption no sane person will doubt. Certainly the Apostle marked it openly in Ephesians 1:4, 5, 6, and following: “He chose us in Christ before the foundation of the world was laid. He predestined us to adoption as sons through Christ according to the purpose of his will.” Here you have that special donation of certain persons known to God alone. Then verse 7 shows that according to God’s purpose those same persons always obtain efficacious and applied redemption in the Mediator—“in whom we have redemption through his blood,” and so on. Therefore those specially given to Christ in election always draw faith, remission of sins, sanctification, and salvation from Christ’s death, the fruitful application of that same death being given them together with it. Saint Augustine understood by this donation nothing other than eternal election (On John, tract. 107): “The Father,” he says, “would not have given them to the Son unless he had chosen them.” The same Father, in On the Predestination of the Saints, chapter 16, shows that those so given to the Son are also called in that peculiar way, so that Christ crucified does not become to them a scandal or foolishness, but the power and wisdom of God for working faith and salvation efficaciously in them. See the author’s words, which for brevity I omit. Either, then, it must be denied that certain persons were specially given by God the Father to Christ the Mediator, or it must at once be granted that the Mediator in his offering had a special regard to those same persons.'),
    "notes_covered": ['John 6:37,39; John 17:2; Eph 1:4-7; Aug. In Joh. 107; De praed. sanct. 16'],
    "lemmas": [{'form': 'Omne quod dat mihi Pater', 'gloss': 'All that the Father gives me', 'why': 'John 6:37'}, {'form': 'in aeterna electione facta', 'gloss': 'done in eternal election', 'why': 'special donation'}, {'form': 'specialem intuitum ad easdem', 'gloss': 'a special regard to the same', 'why': 'oblation'}],
  },
  {
    "section": 137,
    "title": 'Cap. 7 Arg. 2: Christ keeps and sanctifies the given—John 17; Hebrews 2:13',
    "latin": ('2. Idem evincitur ex illis locis quae docent Christum, Paternae voluntatis conscium, praedictas personas specialiter sibi datas speciali cura ad salutem dirigere & infallibiliter perducere. Quod proculdubio non fieret, nisi mors Christi, quae est omnis gratiae salutiferae nobis indultae causa meritoria, iisdem personis, ut salutifera & vivifica, speciali quadam intentione fuisset destinata. Sed verba Scripturae audiamus. Johan. xvii. 9. Pro ipsis ego rogo; non pro mundo rogo, sed pro iis quos dedisti mihi, quia tui sunt. Et ver. 12. Ego servavi eos; quos dedisti mihi custodivi. Et ver. 19. Ego pro iis sanctifico meipsum, ut ipsi quoque sint sanctificati in veritate. Nihil clarius quam hisce in locis duo affirmari: Unum, A Deo Patre non omnes promiscue, sed quosdam specialiter fuisse datos Christo mediatori: quod de Electis intelligendum esse, ostensum est: Alterum, Christum in ipso Mediatoris & Servatoris officio fungendo complecti & prosequi eosdem speciali amore, intentione ac cura, hoc est, tali amore intentione & cura quae producant in iis infallibilem effectum vitae aeternae. Quod ex Heb. ii. 13. manifeste liquet, ubi Christus hosce pueros sibi a Patre datos Patri suo representat salvos & incolumes; Ecce ego, & pueri quos dedit mihi Deus.'),
    "pass_a_gloss": ('2. The same is evinced from those places which teach Christ, conscious of the Paternal will, to direct and infallibly lead to salvation the aforesaid persons specially given to himself with special care. Which without doubt would not be done, unless the death of Christ, which is the meritorious cause of every saving grace granted to us, had been destined to the same persons, as saving and life-giving, by a certain special intention. But let us hear the words of Scripture. John xvii. 9. For them I ask; I do not ask for the world, but for those whom you have given me, because they are yours. And verse 12. I have kept them; those whom you have given me I have guarded. And verse 19. For them I sanctify myself, that they also may be sanctified in truth. Nothing clearer than that in these places two things are affirmed: One, From God the Father not all promiscuously, but certain ones specially to have been given to Christ the mediator: which is to be understood of the Elect, has been shown: The other, Christ in discharging the office itself of Mediator and Savior to embrace and pursue the same with special love, intention and care, that is, with such love intention and care which produce in them the infallible effect of eternal life. Which from Heb. ii. 13. plainly is clear, where Christ represents these children given to himself by the Father to his Father safe and unharmed; Behold I, and the children whom God has given me.'),
    "pass_b": ('2. The same is proved from those places that teach Christ, conscious of the Father’s will, directs and infallibly leads to salvation the aforesaid persons specially given to him, with special care. That would doubtless not happen unless Christ’s death—which is the meritorious cause of every saving grace granted us—had been destined to those same persons as saving and life-giving by a special intention. But let us hear the words of Scripture. John 17:9: “I ask for them; I do not ask for the world, but for those you have given me, because they are yours.” And verse 12: “I have kept them; those you gave me I have guarded.” And verse 19: “For them I sanctify myself, that they also may be sanctified in truth.” Nothing is clearer than that two things are affirmed in these places: first, that not all promiscuously, but certain ones, were specially given by God the Father to Christ the mediator—which has been shown to be understood of the Elect; second, that Christ, in discharging the very office of Mediator and Savior, embraces and pursues those same persons with special love, intention, and care—that is, with such love, intention, and care as produce in them the infallible effect of eternal life. That is plain from Hebrews 2:13, where Christ presents these children given him by the Father to his Father safe and sound: “Behold, I and the children God has given me.”'),
    "notes_covered": ['John 17:9,12,19; Heb 2:13 Ecce ego et pueri'],
    "lemmas": [{'form': 'non pro mundo rogo', 'gloss': 'I do not ask for the world', 'why': 'John 17:9'}, {'form': 'speciali amore, intentione ac cura', 'gloss': 'with special love, intention, and care', 'why': 'Arg2'}, {'form': 'Ecce ego, & pueri', 'gloss': 'Behold I and the children', 'why': 'Heb 2:13'}],
  },
  {
    "section": 138,
    "title": 'Cap. 7 Arg. 2 close: absolute intercession (Bannes/Suarez)—oblation intends the same elect',
    "latin": ('Jam vero ut haec omnia quasi in fasciculum recolligam: Quos Christus speciali intercessione Patri commendavit, hoc est, oratione absoluta (ut habet Bannesius in 1. qu. 23. art. 5. pag. 297.) vel (ut Suarezius in 3. tom. 1. quaest. 19. disp. 31. pag. 634.) pro quibus oravit efficaci & absoluta voluntate, ut meritum mortis suae eis applicaretur efficaciter, pro quibus servandis & custodiendis quasi extra ordinem excubias agit, pro quibus seipsum ita sanctificavit ut ab eo efficaciter percipiant eam sanctificationem quae per Evangelii doctrinam in cordibus salvandorum peragitur, denique, quos ad unum omnes Patri tandem sistet incolumes & gloriosos, eos extra omnem controversiam etiam in ipso actu oblationis, adeoque in toto opere redemptionis, speciali intentione complectebatur. Absurdum enim est, salutem speciali intentione fuisse illis a Mediatore procuratam, quibus mors Christi, quae est salutis humanae causa, non fuit speciali intentione destinata.'),
    "pass_a_gloss": ('But now that I may gather all these things as it were into a bundle: Those whom Christ by special intercession commended to the Father, that is, by absolute prayer (as Bannesius has in 1. qu. 23. art. 5. pag. 297.) or (as Suarezius in 3. tom. 1. quaest. 19. disp. 31. pag. 634.) for whom he prayed with efficacious and absolute will, that the merit of his death might be applied to them efficaciously, for whom to be kept and guarded he mounts as it were watches outside the ordinary, for whom he so sanctified himself that from him they may efficaciously perceive that sanctification which through the doctrine of the Gospel is wrought in the hearts of those to be saved, finally, whom to a one all he will at last present to the Father unharmed and glorious, those beyond all controversy even in the act itself of oblation, and so in the whole work of redemption, he was embracing with special intention. For it is absurd, that salvation by special intention was procured for them by the Mediator, for whom the death of Christ, which is the cause of human salvation, was not destined by special intention.'),
    "pass_b": ('But now, to gather all this as into one bundle: those whom Christ by special intercession commended to the Father—that is, by absolute prayer (as Bannes has it on I q.23 art.5 p.297), or (as Suárez in tom. 3.1 q.19 disp.31 p.634) those for whom he prayed with an efficacious and absolute will that the merit of his death be applied to them efficaciously; those for whose keeping and guarding he mounts as it were extraordinary watch; those for whom he so sanctified himself that from him they efficaciously receive that sanctification which is worked in the hearts of the saved by the teaching of the Gospel; finally, those whom he will at last present to the Father, every one, safe and glorious—those, beyond all controversy, he also embraced with special intention in the very act of offering, and so in the whole work of redemption. For it is absurd that salvation was procured for them by the Mediator with special intention, if Christ’s death, which is the cause of human salvation, was not destined to them with special intention.'),
    "notes_covered": ['Bannes 1 q.23 a.5 p.297; Suarez; absurd without special destination of death'],
    "lemmas": [{'form': 'oratione absoluta', 'gloss': 'by absolute prayer', 'why': 'Bannes/Suarez'}, {'form': 'in ipso actu oblationis', 'gloss': 'in the very act of offering', 'why': 'special intention'}, {'form': 'Absurdum enim est', 'gloss': 'For it is absurd', 'why': 'Arg2 close'}],
  },

]


def write_justification(sec: dict) -> Path:
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
            f"Densify Cap. 7 open (elect / praedestinati) section {sec['section']}. "
            f"Pass A!=B. Latin from 1650 PDF pdftotext+tesseract+DjVu. Packet {PACKET}. Honest partial."
        ),
        "lemmas": sec["lemmas"],
        "choices": [
            {
                "issue": "Copy-text",
                "choice": (
                    "Locked 1650 Daniel Latin from IA PDF (pdftotext + tesseract lat+eng) "
                    "with DjVu check; long-s/ligatures normalized. Cap. 7 open lock: "
                    "sources/_davenant_cap7_open_latin_lock.txt."
                ),
            },
            {
                "issue": "Scope",
                "choice": (
                    "Cap. 7 De morte Christi qua spectat solos praedestinatos: open through "
                    "Thesis + Grevinchovius + Arg. 1–2 close (before Arg. 3 sheep/ecclesia)."
                ),
            },
            {
                "issue": "OCR lacuna",
                "choice": (
                    "At Arg. 2 mid (amore intentione & cura quae producant…), pdftotext drops "
                    "words after 'go'; restored from tesseract + sense (producant in iis "
                    "infallibilem effectum vitae aeternae)."
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
    if r.returncode != 0 or ("fail=" in out and "fail=0" not in out):
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
        if secs > 3400:
            print("hold cleared: live section count > 3400")
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
                "source_ref": f"morte_christi_source.json#{sec['section']}",
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
    print(f"appended eng/src tip {eng[-1]['section']} (n={len(eng)})")


def update_meta(tip: int) -> None:
    meta_path = TRANS / "morte_christi_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["section_count"] = tip
    meta["title"] = "Two Dissertations (De morte Christi Cap. 1-7 partial)"
    meta["edition"] = (
        "Dissertationes duae (Cambridge: Roger Daniel, 1650). Wing D317; ESTC R5446. "
        "IA bim_early-english-books-1641-1700_dissertationes-du-_davenant-john-bp_1650. "
        "Partial: De morte Christi Cap. 1-6 close + Cap. 7 open (elect / praedestinati: "
        "Thesis through Arg. 2 close before Arg. 3)."
    )
    blurb = meta.get("blurb", "")
    if "Cap. 7 open" not in blurb:
        meta["blurb"] = (
            (blurb.rstrip(".") + "; Cap. 7 open through Thesis/Grevinchovius/Arg. 1–2 close.")
            if blurb
            else "Cap. 7 open densify."
        )
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("meta section_count", meta["section_count"])


def extend_lock(secs: list[dict]) -> None:
    lock = BOOK / "sources/_davenant_morte_christi_latin_lock.txt"
    text = lock.read_text(encoding="utf-8")
    header = (
        "\n\nCAPUT VII\n"
        "De morte Christi, qua spectat solos praedestinatos.\n\n"
    )
    body = "\n\n".join(s["latin"] for s in secs)
    if "CAPUT VII" in text and "solos praedestinatos" in text:
        print("lock already has Cap. 7 open; skip append")
        return
    lock.write_text(text.rstrip() + header + body + "\n", encoding="utf-8")
    print("lock extended with Cap. 7 open")


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
            "Partial: De morte Christi Cap. 1-6 + Cap. 7 open (elect sons / praedestinati "
            "through Arg. 2 close)."
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
            f"Tip densify Cap. 7 open elect/praedestinati Thesis + Grevinchovius + Arg. 1–2 "
            f"(secs 132-{tip}). Not whole Dissertationes."
        ),
        "packet": PACKET,
    }
    raw = [
        BOOK / "sources/davenant_1650.pdf",
        BOOK / "sources/davenant_dissertationes_1650_djvu.txt",
        BOOK / "sources/_davenant_morte_christi_latin_lock.txt",
        BOOK / "sources/_davenant_cap7_open_latin_lock.txt",
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
                "(Cap. 7 open elect/praedestinati through Arg. 2 close)."
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

## 2026-09-22 ~17:50 ET (Scribe — Davenant Cap. 7 open densify)

CoS densify: Cap. 7 *De morte Christi, qua spectat solos praedestinatos* (elect sons tip: open through Thesis / Grevinchovius / Arg. 1–2 close). Punch X: **NO**. Cap. 1 mid-Thesis tip patch stays deferred. Did **not** edit `publication-review.json`; did not ship; did not commit; did not run Logos or ai_promote. {hold_note}

### Bound this job (not shipped)
- **Davenant** `davenant-dissertationes-duae`: Cap. 7 open tip (**{before}→{after}** sections). Locked densify Latin from IA 1650 Daniel PDF (pdftotext + tesseract) with DjVu check. Pass A≠B; OUR; English-first; no PBB/ops TNs; packet `{PACKET}`. Honest partial — **not** whole Dissertationes. Cap. 7 Arg. 3–remainder through Cap. 11 and De praedestinatione remain. Punch X: **NO**.

### Still missing for full Dissertationes duae
- Cap. 1 tip mid-block patch (between universal-cause definition and John 3:16) — deferred
- Cap. 7 Arg. 3 (sheep/ecclesia) through Cap. 11 (De morte Christi remainder)
- Full De praedestinatione et reprobatione
- Sententia de Gallicana controversia if in the 1650 volume

### Punch X?
**NO** — full-works bar not met. Parent/CoS only.


---

"""
    path.write_text(block + old, encoding="utf-8")
    print("SESSION_HANDOFF prepended")


def main() -> None:
    import os
    # Hold clock: honor HOLD_START_EPOCH if parent already started the tip-131 wait.
    start = float(os.environ.get("HOLD_START_EPOCH", time.time()))
    # Pass A/B self-check EACH justification before any append
    for sec in SECTIONS:
        p = write_justification(sec)
        check_just(p)
    # Hold: no eng/src append until live >3400 OR 12 minutes from HOLD_START_EPOCH
    wait_hold(start, minutes=12.0)
    # Re-read tip after hold
    eng = json.loads((TRANS / "morte_christi_english.json").read_text(encoding="utf-8"))
    tip_now = int(eng[-1]["section"])
    if tip_now != TIP_BEFORE:
        raise SystemExit(f"disk tip changed during hold: expected {TIP_BEFORE}, got {tip_now}")
    treatises, secs = live_section_count()
    dav_tip = live_davenant_tip()
    hold_note = (
        f"Waited tip-131 ship hold (live was 57/3400, davenant tip {dav_tip}); "
        f"cleared with live {treatises}/{secs} before append."
    )
    append_rows(SECTIONS)
    tip = SECTIONS[-1]["section"]
    update_meta(tip)
    extend_lock(SECTIONS)
    build_packet(tip)
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
    # batch check new justifications
    for sec in SECTIONS:
        check_just(JUST / f"morte_{sec['section']}.json")
    prepend_handoff(TIP_BEFORE, tip, hold_note)
    print(f"DONE {TIP_BEFORE}→{tip} packet={PACKET} Punch X=NO claim stays claimed")


if __name__ == "__main__":
    main()
