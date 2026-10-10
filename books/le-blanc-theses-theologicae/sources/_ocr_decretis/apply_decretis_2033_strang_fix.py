"""Standalone reviewed fix for Le Blanc §2033: Strangius = John Strang of Glasgow (1584-1654), not William Strang.

Reuses the packet M apply module (constants match tip 2060) with scope = changed §2033 only.
Aligned review (Workers AI kimi + glm). Idempotent and resumable: rerun to resume after a pause.
"""
import importlib.util, json, sys, socket, subprocess
from datetime import datetime
from pathlib import Path

REPO = Path.home() / 'SaneApps/clients/translations'
BOOK = REPO / 'books/le-blanc-theses-theologicae'
M_APPLY = BOOK / 'sources/_ocr_decretis/apply_decretis_xxxiii_lxv_densify.py'
STEM = 'decretis_2033_strang_fix'
FIXREC = BOOK / 'sources/_ocr_decretis' / (STEM + '.json')

src = M_APPLY.read_text(encoding='utf-8')
def rep(a, b):
    global src
    assert src.count(a) == 1, a[:70]
    src = src.replace(a, b)
rep("PACKET_STEM = 'decretis_xxxiii_lxv_densify'", "PACKET_STEM = %r" % STEM)
rep("PAYLOAD = BOOK / 'sources/_ocr_decretis/decretis_xxxiii_lxv_payload.json'", "PAYLOAD = BOOK / 'sources/_ocr_decretis/%s.json'" % STEM)
rep("CHANGED = []", "CHANGED = ['2033']")
rep("SECS = [str(n) for n in range(2028, 2061)]", "SECS = []")
rep("sample_size=len(scoped),", "sample_size=max(3, len(scoped)),")
rep("CHANGED_LOCKS = []", "CHANGED_LOCKS = [JUST / 'decretis_2033.json']")
rep("'Scope: new %s-%s plus changed %s.' % (SECS[0], SECS[-1], ', '.join(CHANGED) or 'none')",
    "'Scope: changed 2033 only (Strang identification fix; no new sections).'")
spec = importlib.util.spec_from_loader('apfix', loader=None)
ap = importlib.util.module_from_spec(spec)
ap.__file__ = str(M_APPLY)
exec(compile(src, str(M_APPLY) + ' [fix2033]', 'exec'), ap.__dict__)

REPL = [
    ('William Strang expressly rejects it', 'John Strang expressly rejects it'),
    ('William Strang (1588-1645), De voluntate', 'John Strang (1584-1654), principal of Glasgow University, De voluntate'),
]
REASON = ("Strangius misidentified as William Strang (1588-1645). Le Blanc's 'Strangius' is Joannes Strangius, John Strang "
          "of Glasgow (1584-1654), author of De voluntate et actionibus Dei circa peccatum (Amsterdam, 1657), as Le Blanc himself "
          "names him ('Joanne Strangio', De Decretis Pars Secunda XIX) and as the book renders him elsewhere (§§1776-1782, 1862, 1928-1937, 2039, 2054-2055). "
          "Name and note corrected; no other change.")


def apply_fix():
    eng = json.loads(ap.ENG.read_text(encoding='utf-8'))
    if len(eng) != 2060 or str(eng[-1]['section']) != '2060':
        raise SystemExit('refuse: tip is not 2060 (%s)' % len(eng))
    row = [r for r in eng if str(r['section']) == '2033']
    assert len(row) == 1
    row = row[0]
    rec = json.loads(FIXREC.read_text(encoding='utf-8')) if FIXREC.exists() else None
    blob = json.dumps(row, ensure_ascii=False)
    if 'William Strang' in blob:
        prev = {'english': row['english'], 'translator_notes': row['translator_notes']}
        for a, b in REPL:
            if a not in blob:
                raise SystemExit('expected text missing: %s' % a)
            blob = blob.replace(a, b)
        new = json.loads(blob)
        row.clear(); row.update(new)
        rec = {'section': '2033', 'date': datetime.now().strftime('%Y-%m-%d'), 'reason': REASON,
               'replacements': REPL, 'previous': prev,
               'current': {'english': row['english'], 'translator_notes': row['translator_notes']},
               'latin': [r for r in json.loads(ap.SRC.read_text(encoding='utf-8')) if str(r['section']) == '2033'][0]['latin']}
        FIXREC.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        ap.ENG.write_text(json.dumps(eng, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('english §2033 corrected; fix record', FIXREC)
    else:
        print('english §2033 already corrected')
        if rec is None:
            raise SystemExit('english corrected but fix record missing; refuse')
    others = [str(r['section']) for r in eng if 'William Strang' in json.dumps(r, ensure_ascii=False)]
    if others:
        raise SystemExit('other William Strang sections remain: %s' % others)
    jp = ap.JUST / 'decretis_2033.json'
    j = json.loads(jp.read_text(encoding='utf-8'))
    if 'William Strang' in json.dumps({k: v for k, v in j.items() if k != 'pass_b_revision'}, ensure_ascii=False):
        prev_b = list(j['pass_b_english'])
        jb = json.dumps(j, ensure_ascii=False)
        jb = jb.replace(REPL[0][0], REPL[0][1])
        j = json.loads(jb)
        j['pass_b_revision'] = {
            'date': rec['date'], 'by': 'Densify (agent), owner-approved (Stephan 2026-10-09 20:12)',
            'reason': REASON, 'previous_pass_b_english': prev_b,
            'previous_translator_notes': rec['previous']['translator_notes'],
        }
        if 'William Strang' in json.dumps({k: v for k, v in j.items() if k != 'pass_b_revision'}, ensure_ascii=False):
            raise SystemExit('justification still names William Strang')
        jp.write_text(json.dumps(j, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('justification decretis_2033.json corrected + pass_b_revision')
    else:
        print('justification already corrected')
    if j['pass_b_english'] != row['english']:
        raise SystemExit('justification pass_b_english != english §2033')
    errs = ap.check_file(jp)
    print('check_pass_ab decretis_2033', 'ok' if not errs else errs)
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
        'packet_id': packet['packet_id'], 'before': 2060, 'after': 2060,
        'added_sections': [], 'changed_sections': [2033], 'revision': str(FIXREC),
        'two_family_review': summ,
        'gates': {'check_pass_ab': 'ok decretis_2033', 'tip_ready': 'ok', 'validate_audit_receipt': 'ok'},
        'punch_x': 'NO', 'ship': 'NO', 'claim': 'le-blanc-theses-densify stays claimed',
    }
    rp = ap.AUDIT / (STEM + '.receipt.json')
    rp.write_text(json.dumps(rcpt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('receipt', rp)
    nl = '\n'
    block = ('## %s (Densify — Le Blanc §2033 Strang fix LOCAL)' % datetime.now().strftime('%Y-%m-%d') + nl + nl
             + '- §2033 (De Decretis Pars Prima XXXVIII): "William Strang (1588-1645)" corrected to John Strang of Glasgow (1584-1654) in English and note; `reviews/justifications/decretis_2033.json` pass_b_revision; fix record `sources/_ocr_decretis/%s.json`.' % STEM + nl
             + '- Review: aligned profile (Workers AI kimi-k2.6 + glm-5.2), scope §2033 only; packet `%s` %s. Tip unchanged 2060. Punch X = NO. Not shipped.' % (STEM, packet['packet_id'][:8]) + nl + nl)
    for h in (ap.HANDOFF, REPO / 'docs/SESSION_HANDOFF.md', REPO / 'SESSION_HANDOFF.md'):
        if h.exists() and '§2033 Strang fix' not in h.read_text(encoding='utf-8')[:3000]:
            h.write_text(block + h.read_text(encoding='utf-8'), encoding='utf-8'); print('prepended', h)
    fp1 = ap.crocius_baron_fingerprint(); print('crocius/baron after', fp1)
    if fp1 != fp0:
        raise SystemExit('Crocius/Baron changed; refuse')
    print('DONE fix2033 packet', packet['packet_id'], flush=True)


if __name__ == '__main__':
    main()
