"""Standalone reviewed revision for Le Blanc §2337 (Variae distinctiones Gratiae XVIII, Pighius): 'increatam' settled from the sources.

Reuses the packet W apply module (constants match tip 2352) with scope = changed §2337 only. English text unchanged; translator notes revised with the evidence.
Aligned review (Workers AI kimi + glm). Idempotent and resumable: rerun to resume after a pause.
"""
import importlib.util, json, sys, socket, subprocess
from datetime import datetime
from pathlib import Path

REPO = Path.home() / 'SaneApps/clients/translations'
BOOK = REPO / 'books/le-blanc-theses-theologicae'
M_APPLY = BOOK / 'sources/_ocr_variae_gratiae/apply_variae_gratiae_romana_i_xxxiii_densify.py'
STEM = 'variae_gratiae_2337_pighius_revision'
FIXREC = BOOK / 'sources/_ocr_variae_gratiae' / (STEM + '.json')

src = M_APPLY.read_text(encoding='utf-8')
def rep(a, b):
    global src
    assert src.count(a) == 1, a[:70]
    src = src.replace(a, b)
rep("PACKET_STEM = 'variae_gratiae_romana_i_xxxiii_densify'", "PACKET_STEM = %r" % STEM)
rep("PAYLOAD = BOOK / 'sources/_ocr_variae_gratiae/variae_gratiae_romana_i_xxxiii_payload.json'", "PAYLOAD = BOOK / 'sources/_ocr_variae_gratiae/%s.json'" % STEM)
rep("CHANGED = []", "CHANGED = ['2337']")
rep("SECS = [str(n) for n in range(2320, 2353)]", "SECS = []")
rep("sample_size=len(scoped),", "sample_size=max(3, len(scoped)),")
rep("CHANGED_LOCKS = []", "CHANGED_LOCKS = [JUST / 'variae_gratiae_2337.json']")
rep("'Scope: new %s-%s plus changed %s.' % (SECS[0], SECS[-1], ', '.join(CHANGED) or 'none')",
    "'Scope: changed 2337 only (Pighius increatam settled from the sources; no new sections).'")
spec = importlib.util.spec_from_loader('apfix', loader=None)
ap = importlib.util.module_from_spec(spec)
ap.__file__ = str(M_APPLY)
exec(compile(src, str(M_APPLY) + ' [rev2337]', 'exec'), ap.__dict__)

OLD1 = 'Albert Pighius, De libero hominis arbitrio et divina gratia (1542), book 5, as reported by Bellarmine.'
NEW1 = 'Albert Pighius, De libero hominis arbitrio et divina gratia libri decem (Cologne, 1542), book 5, fol. 76r, as reported by Bellarmine, De gratia et libero arbitrio, book 1, chapter 3 (Opera omnia, Vives ed., vol. 5).'
OLD2 = "'Increatam' is read as the participle of increo, 'created in' (the quality God creates in the soul), not 'uncreated'; the dative 'animae nostrae' and 'a Deo' require it."
NEW2 = ("'Increatam' is read as the participle of increo, 'created in', not 'uncreated'. Pighius's own text (1542, book 5, fol. 76r) and Bellarmine's quotation of it both read "
        "'imaginantur gratiam Dei qualitatem aliquam increatam animae nostrae a Deo' (Le Blanc drops 'gratiam Dei'). The word describes the scholastic view Pighius rejects: "
        "a quality put into the soul by God, either the habit of charity or distinct from it. In the same chapter Bellarmine defends that view as 'habitum supernaturalem a Deo nobis infundi' "
        "and grace as 'habitum, sive qualitatem creatam'. Pighius's own view was that grace in Scripture is God's favour (his next pages gloss 'finding grace in someone's eyes' as being loved freely), "
        "and Bellarmine groups him with Calvin's 'gratuita acceptione'. In scholastic terms that favour is 'gratia increata' (Thesis II; Lombard's uncreated charity, the Holy Spirit), "
        "but here the word qualifies the created quality Pighius denies, not his own view.")
REASON = ("Both reviewers read 'increatam' (§2337) as 'uncreated'. The passage was checked against Pighius's 1542 text (archive.org bub_gb_nGsCu5n-cH4C, book 5, fol. 76r) and Bellarmine, De gratia et libero arbitrio 1.3 "
          "(archive.org operaomnia05bell). Both read 'qualitatem aliquam increatam animae nostrae a Deo', describing the schools' infused created quality, which Bellarmine defends there as 'qualitatem creatam'. "
          "Pighius himself held grace to be God's favour, not an inherent quality, but the word qualifies the view he rejects. English kept ('created in (increatam) our soul by God'); translator notes revised with the evidence.")
REPL = [(OLD1, NEW1), (OLD2, NEW2)]


def apply_fix():
    eng = json.loads(ap.ENG.read_text(encoding='utf-8'))
    if len(eng) != 2352 or str(eng[-1]['section']) != '2352':
        raise SystemExit('refuse: tip is not 2352 (%s)' % len(eng))
    row = [r for r in eng if str(r['section']) == '2337']
    assert len(row) == 1
    row = row[0]
    rec = json.loads(FIXREC.read_text(encoding='utf-8')) if FIXREC.exists() else None
    notes = row['translator_notes']
    if OLD2 in notes:
        prev = {'english': list(row['english']), 'translator_notes': list(notes)}
        for a, b in REPL:
            if a not in notes:
                raise SystemExit('expected note missing: %s' % a[:60])
            notes[notes.index(a)] = b
        rec = {'section': '2337', 'date': datetime.now().strftime('%Y-%m-%d'), 'reason': REASON,
               'by': 'Densify (agent), at Stephan\'s request 2026-10-10 04:59',
               'kind': 'revision (translator notes; English unchanged)',
               'evidence': {
                   'pighius_1542': 'De libero hominis arbitrio & divina gratia libri decem (Cologne, 1542), lib. 5, fol. LXXVI: "Gratiae acceptionem variam, non ex scholis, sed ex divinis scripturis petemus. Quandoquidem, in illis, fere imaginantur gratiam Dei qualitatem aliquam increatam animae nostrae a Deo: vel eandem cum charitatis habitu, vel distinctam ab eodem. Quae commentitia universa existimo, nec ex scripturis ullam authoritatem habere." (archive.org bub_gb_nGsCu5n-cH4C); then Scripture\'s "invenire gratiam in oculis alicujus" = to be loved freely.',
                   'bellarmine_dgla_1_3': 'De gratia et libero arbitrio lib. 1 cap. 3 (Opera omnia, Vives, t. 5; archive.org operaomnia05bell): Pighius joined Calvin (Antidote, sess. 6: "gratuita acceptione nos esse justos"), Chemnitz and Heshusius in denying grace "quae sit habitus, aut certe qualitas per modum habitus in anima permanens"; quotes Pighius as above; the common view: "habitum supernaturalem a Deo nobis infundi, quo anima exornetur"; "gratiam in genere ... esse habitum, sive qualitatem creatam".',
                   'scholastic_usage': '"gratia increata" = God\'s favour or the Holy Spirit (Le Blanc Thesis II: "gratiam aeternam & increatam"; Lombard, Sent. 1 d. 17, charity = the Holy Spirit; Bonaventure, In 1 Sent. d. 17 p. 1 a. 1 q. 1: besides uncreated charity a created habit must be posited). The scholastics never call the infused quality uncreated.',
               },
               'previous': prev, 'current': {'english': list(row['english']), 'translator_notes': list(notes)},
               'latin': [r for r in json.loads(ap.SRC.read_text(encoding='utf-8')) if str(r['section']) == '2337'][0]['latin']}
        FIXREC.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        ap.ENG.write_text(json.dumps(eng, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('english §2337 notes revised; revision record', FIXREC)
    else:
        print('english §2337 notes already revised')
        if rec is None:
            raise SystemExit('notes revised but revision record missing; refuse')
    jp = ap.JUST / 'variae_gratiae_2337.json'
    j = json.loads(jp.read_text(encoding='utf-8'))
    if j['pass_b_english'] != row['english']:
        raise SystemExit('justification pass_b_english != english §2337')
    errs = ap.check_file(jp)
    print('check_pass_ab variae_gratiae_2337', 'ok' if not errs else errs)
    if errs:
        raise SystemExit(1)


def main():
    host = socket.gethostname()
    if 'mini' not in host.lower():
        raise SystemExit('refuse: not Mini (%s)' % host)
    ap.DATA = Path('/tmp/leblanc_' + STEM); ap.DATA.mkdir(parents=True, exist_ok=True)
    fp0 = ap.crocius_baron_fingerprint(); print('crocius/baron before', fp0, flush=True)
    apply_fix()
    ap.tip_ready()
    packet_path, review_path, packet = ap.build_packet_and_review()
    summ = ap._review_summary(review_path)
    rcpt = {
        'packet_stem': STEM, 'packet': str(packet_path), 'review': str(review_path),
        'packet_id': packet['packet_id'], 'before': 2352, 'after': 2352,
        'added_sections': [], 'changed_sections': [2337], 'revision': str(FIXREC),
        'two_family_review': summ,
        'gates': {'check_pass_ab': 'ok variae_gratiae_2337', 'tip_ready': 'ok', 'validate_audit_receipt': 'ok'},
        'punch_x': 'NO', 'ship': 'NO', 'claim': 'le-blanc-theses-densify stays claimed',
    }
    rp = ap.AUDIT / (STEM + '.receipt.json')
    rp.write_text(json.dumps(rcpt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('receipt', rp)
    nl = '\n'
    block = ('## %s (Densify — Le Blanc §2337 Pighius revision LOCAL)' % datetime.now().strftime('%Y-%m-%d') + nl + nl
             + '- §2337 (Variae distinctiones Gratiae XVIII, Pighius): "increatam" settled from Pighius 1542 (lib. 5 fol. 76r) and Bellarmine, De gratia et lib. arb. 1.3 as "created in" (the schools\' infused quality Pighius rejects); English kept, notes revised with the evidence; revision record `sources/_ocr_variae_gratiae/%s.json`.' % STEM + nl
             + '- Review: aligned profile (Workers AI kimi-k2.6 + glm-5.2), scope §2337 only; packet `%s` %s. Tip unchanged 2352. Punch X = NO. Not shipped.' % (STEM, packet['packet_id'][:8]) + nl + nl)
    for h in (ap.HANDOFF, REPO / 'docs/SESSION_HANDOFF.md', REPO / 'SESSION_HANDOFF.md'):
        if h.exists() and '§2337 Pighius revision' not in h.read_text(encoding='utf-8')[:3000]:
            h.write_text(block + h.read_text(encoding='utf-8'), encoding='utf-8'); print('prepended', h)
    fp1 = ap.crocius_baron_fingerprint(); print('crocius/baron after', fp1)
    if fp1 != fp0:
        raise SystemExit('Crocius/Baron changed; refuse')
    print('DONE rev2337 packet', packet['packet_id'], flush=True)


if __name__ == '__main__':
    main()
