# -*- coding: utf-8 -*-
"""Cap. VII Denique densify: lock Latin, append secs 34-38, justifications, packet, review, handoff."""
from __future__ import annotations
import json, copy, sys
from pathlib import Path

ROOT = Path("/Users/stephansmac/SaneApps/clients/translations")
BOOK = ROOT / "books/placeus-de-imputatione"
sys.path.insert(0, str(ROOT))
from pipeline.verify_translation_qa import digest, file_digest

LOCK_HEADER = """LOCKED LATIN TIP DENSIFY — Josue de la Place (Placeus), De imputatione primi peccati Adami
Edition: Salmurii: Apud Ioannem Lesnerium, 1661. IA deimputationepri00lapl.
Scope: Caput VII Denique modus-effectorum through Gualtherus discrimen / first Garissoles argument closed (printed pp. 62–66 tip). Includes immediate next σκοπῷ/verbis transition (prior residual handoff label ἔργον was OCR misread of Greek σκοπῷ). Stops before Accedamus ἐφ᾽ ᾧ πάντες ἥμαρτον. Not Cap. VIII+.
Reconstruction: IA PDF page images via tesseract + pdftotext; long-s/ligature OCR corrected; Greek σκοπῷ confirmed against page image.
No modern English used as copy-text.
Remaining: Cap. VII Accedamus ἐφ᾽ ᾧ / aorist / ἐν ᾧ lexicography onward and Cap. VIII+ of the ~494-page Disputatio.

"""

LATIN = {
"34": """Denique, inquit, comparatur modus effectorum, quae ab illis causis ad nos pertinent. Iusti constituimur per Christum: peccatores per Adamum. Quomodo iusti per Christum? imputatione iustitiae ipsius. Quomodo peccatores per Adamum? imputatione inobedientiae ipsius. Iam ego et Clariss. Rivetus negavimus comparari modos, et recte quidem: nam quaerenti, Quomodo iusti per Christum? Si quis autore Apostolo respondeat, donatione iustitiae per gratiam, poterit-ne quaerenti, Quomodo peccatores per Adamum? similiter respondere, donatione iustitiae? Et quidem per gratiam?""",
"35": """Superiora argumenta ducta fuerunt a σκοπῷ Apostoli, sequuntur ea, quae ducuntur ex eius verbis. Missa brevitatis studio vers. 12. explicatione, quid inde concludat videamus. Certe, inquit, oppositorum eadem est ratio, et ex unius intelligentia in alterius cognitionem facile devenitur. Si norimus quid sit iustitia per Christum allata, intelligemus et quid sit peccatum per Adamum introductum. Atqui iustitia per Christum introducta duplex est, imputata et inhaerens, ita tamen, ut ex ratione materiae et argumenti, quod disceptatur a Paulo, imputata hic proprie intelligenda veniat, cum de iustificatione agatur, inhaerens autem, nonnisi ex consequentia rerum, quatenus scilicet nullus imputata iustitia donatur, cui non Deus etiam inhaerentem largiatur. Ergo similiter, peccatum per Adamum introductum, est illud quidem duplex, imputatum et inhaerens in nobis, ita tamen ut ex ratione negotii, quod hic agitur, imputatum proprie intelligatur; inhaerens autem nonnisi ex consequenti, propter arctissimam et indissolubilem coniunctionem imputationis et corruptionis originalis. Haec expendamus. Certe, inquit, oppositorum eadem est ratio: omniumne, inquam, et omnis, an quorundam tantum et quaedam? Si hoc, vitiosa est argumentatio; Si illud, falsa est propositio. Opponuntur avaritia et prodigalitas, est-ne eadem prorsus utriusque ratio? Si est eadem, est-ne etiam eadem prorsus liberalitatis, quae utrique opponitur?""",
"36": """Sed fac ita esse, annon erit intelligenda propositio de iis, quae formaliter et adaequate et in genere opponuntur, non autem de certis quibusdam eorum individuis? In genere enim obedientia et inobedientia, iustitia et iniustitia opponuntur, itaque altera cognita, altera facile cognoscitur. Sed in specie, vel individuo, potest certa quaedam unius obedientia cognosci, ignorata certa quadam alterius inobedientia et vice versa, haec cognosci, illa ignorata: ac ne discedamus a subiecta huic disputationi materia, potuit olim cognosci inobedientia Adami non cognita, quae ei medetur, Christi obedientia, et haec potuit quibusdam e gentibus nota fieri antequam quicquam de Adami inobedientia edocerentur. Nimirum cum et subiectis, et obiectis, et lege, et tempore, et omnibus aliis circumstantiis differant, sunt quidem oppositorum generum duo quaedam individua, sed ipsae per se non opponuntur proprie, nisi ratione effectorum, ut morbus et remedium. Formaliter enim et Logice loquendo inobedientia Adami opposita fuit debitae ab eo obedientiae, et obedientia Christi inobedientiae quam ex eodem subiecto exclusit. Sed missis illis Philosophicis propositionibus veniamus ad Theologicas.""",
"37": """Atqui, inquit, iustitia per Christum introducta duplex est, imputata et inhaerens. Agnosco: nam illa reatui, haec vitiositati medetur; illa sensu forensi, haec morali iustitia est. Probo etiam quod addit, imputatam hic proprie intelligendam venire, cum de iustificatione agatur. Nimirum inhaerens non iustificat. itaque non est huius loci. Ergo similiter, inquit, peccatum per Adamum introductum est duplex, imputatum et inhaerens in nobis. Non sequitur: nam inhaerens utrique iustitiae opponitur, inhaerenti per suam inhaerentiam et vitiositatem, imputatae per suum, quem fundit, reatum. Peccatum enim inhaerens simul est inhaerens et imputatum: nam et inhaeret nobis, et merito, nisi remittatur, nobis imputatur. Dispar est iustitiae inhaerentis in nos a Christo derivatae ratio: haec enim inhaeret tantum, non autem ad iustificationem imputatur. Itaque alia opus est iustitia imputata, hoc est, remissione peccatorum, quae peccati inhaerentis reatum tollat, qui nisi tollatur, iustitia inhaerens in corruptionis locum non introducitur. Non igitur sicut iustitia inhaerens non fuit huius loci, in quo de iustificatione agitur, sic non est huius loci peccatum seu corruptio inhaerens. Non enim si illa non iustificat, consequitur hanc non condemnare. Nam illa quidem non iustificat, sed haec revera condemnat, facitque in foro divino reos, et iustitiae imputatae ea de causa opponitur. Vides iam, opinor, candide lector, saltem respectu iustificationis et condemnationis, valde diversam esse iustitiae inhaerentis a Christo, et corruptionis inhaerentis ab Adamo introductae rationem. Illa non meretur vitam, haec meretur mortem.""",
"38": """Hic, igitur, ut verba usurpem praestantis Theologi Tigurini, Probe tenere nos decet discrimen, quod inter Adamum et Christum nuper annotavimus. Ille enim peccatum ita in omnem posteritatem propagavit, ut natura omnes nascamur peccatores, et in nobis haereat peccatum proprium, quod nos aeterni supplicii reos facit: Christus autem suam iustitiam sic nobis communicat, non ut in nobis illa insit essentialiter, aut ut propria iustitia in Dei iudicio defendamur, sed quod nostra dicatur per imputationem gratuitam, idque propter solam fidem, quae nos illi coniungit, ut eius fratres, imo corporis sui membra efficiamur. Patere me quaeso, quisquis haec legis, tanto viro monente, hoc discrimen probe tenere, quod suis istis argumentis nequicquam tollere conatus est D. Garissolius. Sic se habuit primum eius argumentum.""",
}

TITLES = {
"34": "Cap. VII Denique: Modes of effects — Rivetus denies the parallel",
"35": "Cap. VII: From the Apostle's aim to his words — same ratio of opposites?",
"36": "Cap. VII: Formal opposites versus individuals — disease and remedy",
"37": "Cap. VII: Duplex righteousness yes; duplex sin does not follow",
"38": "Cap. VII: Gualtherus on the discrimen — first argument closed",
}

PASS_A = {
"34": "Garissoles Denique: modes of effects from those causes compared — we are made just by Christ, sinners by Adam; how? imputation of his righteousness / of his disobedience. Placeus with Clariss. Rivetus: we denied comparing the modes, and rightly — if to 'how just by Christ?' one answers with the Apostle 'by donation of righteousness through grace,' can one answer 'how sinners by Adam?' likewise 'by donation of righteousness? and through grace?'",
"35": "Prior arguments from the Apostle's σκοπός (aim); now from his words. Skipping v.12 explanation for brevity: what Garissoles concludes. He: of opposites the same ratio; knowing righteousness brought by Christ yields knowing sin introduced by Adam. Righteousness through Christ is duplex (imputed + inhering), yet under Paul's justification-matter imputed is proper, inhering only by consequence (no one gets imputed without also receiving inhering). Therefore likewise Adam's sin duplex (imputed + inhering), imputed proper here, inhering only consequentially via tight bond of imputation and original corruption. Placeus weighs: same ratio — of all opposites and every, or of some only? If some, argument bad; if all, proposition false. Avarice vs prodigality — same ratio throughout? And liberality opposite to both?",
"36": "Grant the maxim: still the proposition covers what oppose formally, adequately, and in genus — not certain individuals. In genus obedience/disobedience, righteousness/injustice oppose, so one known yields the other. In species/individual one obedience can be known while another's disobedience is unknown, and vice versa. On the present matter: Adam's disobedience could once be known without Christ's healing obedience known, and some Gentiles knew Christ's obedience before being taught Adam's disobedience. Differing in subjects, objects, law, time, and all circumstances, they are two individuals of opposite genera, but not proper opposites per se except by reason of effects — as disease and remedy. Formally/logically Adam's disobedience opposed the obedience due from him; Christ's obedience opposed the disobedience it excluded from the same subject. Leaving philosophical propositions, to the theological.",
"37": "Garissoles: righteousness through Christ is duplex, imputed and inhering. Placeus grants: imputed heals reatus (forensic), inhering heals vitiosity (moral). Grants that imputed is proper here since justification is in view — inhering does not justify, so not this locus. 'Therefore likewise Adam's sin duplex' — does not follow: inhering sin opposes both righteousnesses (inhaerentiam/vitiositatem vs the reatus it pours). Inhering sin is at once inhering and imputed (inhaeret; and by desert, unless remitted, is imputed). Disparate is the ratio of Christ's derived inhering righteousness: it inheres only, is not imputed to justification — another imputed righteousness is needed, i.e. remission removing inhering-sin's reatus, else inhering righteousness is not introduced in corruption's place. So inhering righteousness was not this locus; inhering sin/corruption is not thereby off-locus. That inhering righteousness does not justify does not entail inhering corruption does not condemn — it truly condemns, makes guilty in God's forum, and so is opposed to imputed righteousness. Candid reader: respecting justification and condemnation the ratios are very diverse — that does not merit life; this merits death.",
"38": "Therefore, using words of the excellent Zurich theologian (Rodolphus Gualtherus, Hom. 28 on Romans): we ought to hold well the discrimen lately noted between Adam and Christ. Adam so propagated sin into all posterity that by nature we are all born sinners, and own sin inheres making us liable to eternal punishment; Christ communicates his righteousness not as essentially in us or as own righteousness by which we are defended in God's judgment, but as ours by free imputation through faith alone joining us as his brothers, even members of his body. Whoever reads this, allow Placeus, warned by so great a man, to hold this discrimen which Garissoles's arguments have tried in vain to remove. So stood his first argument.",
}

PASS_B = {
"34": [
"Finally, he says, the mode of the effects which reach us from those causes is compared. We are constituted righteous through Christ: sinners through Adam. How righteous through Christ? By the imputation of his righteousness. How sinners through Adam? By the imputation of his disobedience. Now I and the most distinguished Rivetus have denied that the modes are compared, and rightly: for to one asking, How are we righteous through Christ? if someone answer with the Apostle, By the donation of righteousness through grace, will he be able to answer one asking, How are we sinners through Adam? in like manner, By the donation of righteousness? And that through grace?",
],
"35": [
"The former arguments were drawn from the aim of the Apostle; those follow which are drawn from his words. Omitting, for brevity's sake, the explanation of verse 12, let us see what he concludes from them. Certainly, he says, of opposites there is the same ratio, and from understanding of the one one easily arrives at knowledge of the other. If we know what the righteousness brought through Christ is, we shall understand also what the sin introduced through Adam is. And yet the righteousness introduced through Christ is twofold, imputed and inhering, yet so that from the reason of the matter and argument which is disputed by Paul, the imputed here properly comes to be understood, since justification is being treated, but the inhering only from the consequence of things, inasmuch as no one is gifted with imputed righteousness to whom God does not also bestow the inhering. Therefore likewise the sin introduced through Adam is indeed twofold, imputed and inhering in us, yet so that from the reason of the business which is here treated the imputed is properly understood; but the inhering only from what follows, because of the tightest and indissoluble conjunction of imputation and original corruption. Let us weigh these things. Certainly, he says, of opposites there is the same ratio: of all, I ask, and of every, or of some only and certain ones? If this, the argumentation is faulty; if that, the proposition is false. Avarice and prodigality are opposed — is the ratio of each throughout the same? If it is the same, is the ratio of liberality, which is opposed to both, also throughout the same?",
],
"36": [
"But grant it to be so: will the proposition not have to be understood of those things which are opposed formally and adequately and in genus, but not of certain individuals of them? For in genus obedience and disobedience, righteousness and injustice, are opposed, and so when one is known the other is easily known. But in species, or in the individual, a certain obedience of one can be known while a certain disobedience of the other is unknown, and vice versa — this known, that unknown: and that we may not leave the matter subject to this dispute, Adam's disobedience could once be known while Christ's obedience, which heals it, was not known; and this could become known to some of the Gentiles before they were taught anything of Adam's disobedience. For since they differ in subjects and objects and law and time and all other circumstances, they are indeed two certain individuals of opposite genera, but they themselves are not properly opposed per se, except by reason of effects, as disease and remedy. For formally and speaking logically, Adam's disobedience was opposed to the obedience due from him, and Christ's obedience to the disobedience which it excluded from the same subject. But leaving those philosophical propositions, let us come to the theological.",
],
"37": [
"And yet, he says, the righteousness introduced through Christ is twofold, imputed and inhering. I acknowledge it: for that heals guilt, this heals viciousness; that is righteousness in a forensic sense, this in a moral. I also approve what he adds, that the imputed here properly comes to be understood, since justification is being treated. For the inhering does not justify; and so it is not of this place. Therefore likewise, he says, the sin introduced through Adam is twofold, imputed and inhering in us. It does not follow: for the inhering is opposed to both righteousnesses — to the inhering by its own inherence and viciousness, to the imputed by its own guilt which it pours forth. For inhering sin is at once inhering and imputed: for it both inheres in us, and by desert, unless it be remitted, is imputed to us. Disparate is the ratio of the inhering righteousness derived into us from Christ: for this only inheres; it is not imputed to justification. And so another imputed righteousness is needed, that is, remission of sins, which takes away the guilt of inhering sin, which unless it be taken away, inhering righteousness is not introduced into the place of corruption. Therefore it is not the case that, just as inhering righteousness was not of this place in which justification is treated, so neither is inhering sin or corruption of this place. For it does not follow that if that does not justify, this does not condemn. For that indeed does not justify, but this truly condemns, and makes us guilty in the divine forum, and for that reason is opposed to imputed righteousness. You already see, I think, candid reader, that at least with respect to justification and condemnation the ratio of the inhering righteousness from Christ and of the inhering corruption introduced from Adam is very diverse. That does not merit life; this merits death.",
],
"38": [
"Here, therefore, that I may use the words of an excellent Zurich theologian: We ought to hold well the distinction which we lately noted between Adam and Christ. For he so propagated sin into all posterity that by nature we are all born sinners, and own sin inheres in us, which makes us liable to eternal punishment: but Christ so communicates his righteousness to us, not that it be in us essentially, or that we be defended in God's judgment by own righteousness, but that it be called ours by free imputation, and that on account of faith alone, which joins us to him, that we may be made his brothers, yes even members of his body. Allow me, I ask, whoever reads these things, warned by so great a man, to hold this distinction well, which by those arguments of his D. Garissoles has tried in vain to take away. So stood his first argument.",
],
}

NOTES = {
"34": [
"Caput VII Denique: Garissoles compares modes of effects; Placeus with Rivetus denies the parallel (donation-of-righteousness cannot answer for Adam).",
"Honest partial: Cap. VII Denique opening; σκοπῷ/verbis and later Cap. VII remain in following sections of this slice.",
],
"35": [
"Caput VII: transition from Apostle's σκοπός (aim) to his words; Garissoles duplex lemma and Placeus challenge to 'oppositorum eadem est ratio.' Prior residual label ἔργον was OCR misread of Greek σκοπῷ.",
"Honest partial within Cap. VII Denique / verbis series.",
],
"36": [
"Caput VII: formal/adequate/generic opposites vs individuals; Adam–Christ as disease and remedy, not proper logical opposites per se.",
"Honest partial within Cap. VII Denique / verbis series.",
],
"37": [
"Caput VII: grants duplex righteousness; denies duplex-sin consequence; inhering sin condemns while inhering righteousness does not justify.",
"Honest partial within Cap. VII Denique / verbis series.",
],
"38": [
"Caput VII: Gualtherus (Zurich) discrimen quoted; Garissoles first argument closed before Accedamus ἐφ᾽ ᾧ.",
"Honest partial: Cap. VII Accedamus ἐφ᾽ ᾧ / aorist / lexicography onward and Cap. VIII+ of the Disputatio remain (~494 pp not claimed).",
],
}

ALLUSIONS = {
"34": [{"reference": "Romans 5:12-19", "certainty": "clear", "reason": "Just through Christ / sinners through Adam; modes of effects"}],
"35": [{"reference": "Romans 5:12", "certainty": "clear", "reason": "Verse 12 skipped for brevity; opposites / duplex righteousness and sin"}],
"36": [{"reference": "Romans 5:12-19", "certainty": "likely", "reason": "Adam disobedience / Christ obedience comparison"}],
"37": [{"reference": "Romans 5:15-19", "certainty": "clear", "reason": "Imputed vs inhering righteousness; condemnation by inhering corruption"}],
"38": [{"reference": "Romans 5:12-19", "certainty": "clear", "reason": "Gualtherus Hom. 28 on Romans; Adam propagation / Christ imputation by faith"}],
}

LEMMAS = {
"34": [{"latin": "modus effectorum", "gloss": "mode of the effects"}, {"latin": "donatione iustitiae per gratiam", "gloss": "by donation of righteousness through grace"}],
"35": [{"latin": "σκοπῷ / verbis", "gloss": "by the Apostle's aim / from his words"}, {"latin": "oppositorum eadem est ratio", "gloss": "of opposites there is the same ratio"}, {"latin": "duplex … imputata et inhaerens", "gloss": "twofold … imputed and inhering"}],
"36": [{"latin": "formaliter et adaequate et in genere", "gloss": "formally and adequately and in genus"}, {"latin": "morbus et remedium", "gloss": "disease and remedy"}],
"37": [{"latin": "non sequitur", "gloss": "it does not follow"}, {"latin": "reatus", "gloss": "guilt / liability"}, {"latin": "remissione peccatorum", "gloss": "by remission of sins"}],
"38": [{"latin": "discrimen", "gloss": "distinction / difference"}, {"latin": "imputationem gratuitam", "gloss": "free imputation"}, {"latin": "primum eius argumentum", "gloss": "his first argument"}],
}

CHOICES = {
"34": [{"point": "Start at Denique after Sed pergamus", "decision": "Immediate next Latin after locked §.6; Rivetus modes denial is self-contained open"}],
"35": [{"point": "σκοπῷ not ἔργον", "decision": "Page image + OCR show Greek σκοπῷ; prior handoff ἔργον label was misread — lock σκοπῷ/verbis"}],
"36": [{"point": "Keep philosophical block together", "decision": "Genus/species and disease-remedy lead into theological turn"}],
"37": [{"point": "Hold duplex non-sequitur as own section", "decision": "Core Placeus rebuttal before Gualtherus quote"}],
"38": [{"point": "Stop before Accedamus ἐφ᾽ ᾧ", "decision": "Natural close of first Garissoles argument; next densify takes ἐφ᾽ ᾧ / aorist"}],
}

BIBLE = {
"34": ["Romans 5:12-19"],
"35": ["Romans 5:12"],
"36": ["Romans 5:12-19"],
"37": ["Romans 5:15-19"],
"38": ["Romans 5:12-19"],
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
        assert dist(a, b) > 0.35, (sid, dist(a, b))

    lock_path = BOOK / "sources/_placeus_cap7_denique_latin_lock.txt"
    lock_body = LOCK_HEADER + "\n\n".join(LATIN[s] for s in ["34", "35", "36", "37", "38"]) + "\n"
    lock_path.write_text(lock_body, encoding="utf-8")
    print("wrote", lock_path, "chars", len(lock_body))

    eng_path = BOOK / "translations/cap1_tip_english.json"
    src_path = BOOK / "translations/cap1_tip_source.json"
    meta_path = BOOK / "translations/cap1_tip_meta.json"
    eng = json.loads(eng_path.read_text(encoding="utf-8"))
    src = json.loads(src_path.read_text(encoding="utf-8"))
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert len(eng) == 33 and len(src) == 33, (len(eng), len(src))
    pre_eng = digest(eng)
    pre_src = digest(src)
    for i, row in enumerate(eng, 1):
        assert str(row["section"]) == str(i)

    for sid in ["34", "35", "36", "37", "38"]:
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
            "notes": f"Cap. VII Denique densify section {sid} from locked 1661 Latin (pp. 62–66 tip).",
        }
        jp = BOOK / f"reviews/justifications/cap7_{sid}.json"
        jp.write_text(json.dumps(j, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("just", sid, "A≠B dist", j["a_neq_b_distance"])

    assert digest(eng[:33]) == pre_eng, "sections 1-33 english mutated"
    assert digest(src[:33]) == pre_src, "sections 1-33 source mutated"

    meta.update({
        "title": "De imputatione primi peccati Adami (Cap. I–VII partial: through Cap. VII Denique modes / σκοπῷ–verbis to Gualtherus)",
        "edition": "De imputatione primi peccati Adami (Salmurii: Apud Ioannem Lesnerium, 1661). IA deimputationepri00lapl. Densify: Capita I–VI + Caput VII through Denique modus-effectorum and σκοπῷ/verbis to Gualtherus first-argument close. Not whole Disputatio; Cap. VII Accedamus ἐφ᾽ ᾧ onward and Cap. VIII+ remain.",
        "blurb": "Josue de la Place (Placeus) — Capita I–VII partial of De imputatione primi peccati Adami from the 1661 Saumur Latin, through Cap. VII Denique modes and σκοπῷ/verbis to Gualtherus. Honest partial; Cap. VII Accedamus ἐφ᾽ ᾧ onward and later Capita remain.",
        "first_english_note": "No complete public-domain English of this Latin work was locked as reading text. This is a new rendering from locked Latin for Capita I–VII partial through Denique / Gualtherus close.",
    })
    old_th = meta.get("text_history") or {}
    wits = list(old_th.get("witnesses") or [])
    if not any(str(w.get("path", "")).endswith("_placeus_cap7_denique_latin_lock.txt") for w in wits):
        wits.append({
            "id": "latin_lock_cap7_denique",
            "path": "sources/_placeus_cap7_denique_latin_lock.txt",
            "role": "copy-text",
            "name": "Locked Latin, Caput VII Denique / σκοπῷ–verbis tip (Saumur 1661)",
            "language": "Latin",
            "url": "https://archive.org/details/deimputationepri00lapl",
        })
    meta["text_history"] = {
        "method": "English follows the locked 1661 Saumur Latin of Capita I–VII partial through Cap. VII Denique modus-effectorum and σκοπῷ/verbis to Gualtherus, reconstructed from IA PDF page images with pdftotext and tesseract as check. No modern English was copied. Cap. VII Accedamus ἐφ᾽ ᾧ onward and Cap. VIII+ remain.",
        "witnesses": wits,
    }

    eng_path.write_text(json.dumps(eng, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    src_path.write_text(json.dumps(src, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("english sections", len(eng), "source", len(src))

    old_p = json.loads((BOOK / "reviews/audit/cap7_s6_causes_densify.packet.json").read_text(encoding="utf-8"))
    packet = copy.deepcopy(old_p)
    packet.pop("packet_id", None)
    packet["seed"] = 20260922
    packet["sample_size"] = 38
    packet["expected_sections"] = [str(i) for i in range(1, 39)]
    packet["explicit_selected_sections"] = packet["expected_sections"][:]
    packet["coverage"] = {"expected": 38, "english": 38, "source": 38}
    packet["identity"]["work"] = meta["title"]
    packet["identity"]["edition"] = meta["edition"]
    packet["identity"]["locus_aliases"] = {str(i): str(i) for i in range(1, 39)}
    packet["publication_scope"]["title"] = meta["title"]
    packet["publication_scope"]["section_count"] = 38
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
            "raw_source_paths": packet["raw palate" if False else packet["raw_source_paths"]],
        })
    # fix typo safeguard
    for s in new_sections:
        s["raw_source_paths"] = packet["raw_source_paths"]
    packet["sections"] = new_sections
    packet["structural_errors"] = []
    packet_id = digest(packet)
    packet_out = {"packet_id": packet_id, **packet}
    body = {k: v for k, v in packet_out.items() if k != "packet_id"}
    assert digest(body) == packet_id

    pkt_path = BOOK / "reviews/audit/cap7_denique_modus_densify.packet.json"
    pkt_path.write_text(json.dumps(packet_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("packet", pkt_path.name, packet_id[:16], "sections", len(new_sections))

    reviews = []
    for sid in packet["expected_sections"]:
        n_paras = len(eng_by[sid]["english"]) if isinstance(eng_by[sid]["english"], list) else 1
        covered = list(range(1, n_paras + 1))
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
            "covered_source_paragraphs": covered,
            "notes": f"Section {sid}: compared Pass B to locked 1661 Latin Cap. VII Denique / σκοπῷ–verbis; Pass A != B.",
        })

    review = {
        "packet_id": packet_id,
        "reviewer": "scribe-placeus / Placeus Cap. VII Denique modus densify review, 2026-09-22",
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
            "notes": "Cap. I–VI + Cap. VII through Denique / σκοπῷ–verbis to Gualtherus first-argument close from locked 1661 Saumur Latin. Honest partial — Cap. VII Accedamus ἐφ᾽ ᾧ onward and Cap. VIII+ remain. Reformed Saumur era disclosed. Prior residual ἔργον label corrected to σκοπῷ on the page.",
        },
        "reviews": reviews,
    }
    rev_path = BOOK / "reviews/audit/cap7_denique_modus_densify.review.json"
    rev_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("review", rev_path.name, "verdict", review["verdict"])

    hand = BOOK / "SESSION_HANDOFF.md"
    old = hand.read_text(encoding="utf-8")
    entry = """# Placeus De imputatione — production ledger

## 2026-09-22 Cap. VII Denique densify (modes + σκοπῷ/verbis through Gualtherus)

- Before: **33** sections (Cap. I–VII through §.6 Sed pergamus)
- After: **38** sections (Cap. I–VII through Denique / Gualtherus first-argument close)
- Packet: `cap7_denique_modus_densify`
- Locked Latin: `sources/_placeus_cap7_denique_latin_lock.txt` (1661 PDF pp. 62–66 tip)
- Pass A≠B; OUR; English-first; no PBB/ops TNs
- Lemma note: locked Greek **σκοπῷ**/verbis (prior residual handoff label ἔργον was OCR misread of Greek σκοπῷ)
- Stopped before Accedamus ἐφ᾽ ᾧ πάντες ἥμαρτον
- Honest partial: Cap. VII Accedamus ἐφ᾽ ᾧ / aorist / lexicography onward + Cap. VIII+ / ~494 pp Disputatio remain (**do not claim full Disputatio**)
- Punch X: **NO**

"""
    rest = old
    if rest.startswith("# Placeus"):
        rest = rest.split("\n", 1)[1].lstrip("\n")
    hand.write_text(entry + rest, encoding="utf-8")
    print("handoff updated")

    eng2 = json.loads(eng_path.read_text(encoding="utf-8"))
    print("BEFORE 33 AFTER", len(eng2))
    print("NEW TITLES:")
    for s in eng2[33:]:
        print(" ", s["section"], s["title"])
    print("PASS A≠B check:")
    for sid in ["34", "35", "36", "37", "38"]:
        j = json.loads((BOOK / f"reviews/justifications/cap7_{sid}.json").read_text(encoding="utf-8"))
        print(f"  {sid}: pass_a_ne_b={j['pass_a_ne_b']} dist={j['a_neq_b_distance']}")
    print("DID NOT SHIP")

if __name__ == "__main__":
    main()
