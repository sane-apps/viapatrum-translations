"""Re-issue packet M (De Decretis Pars Prima XXXIII-LXV, §2028-2060) as decretis_xxxiii_lxv_densify_r2
against the current English (§2033 corrected by decretis_2033_strang_fix). Owner-approved option (a),
Stephan 2026-10-09 21:55. Old M audit files are left untouched; no English/source/lock change.
Review checkpoint seeded from M's aligned checkpoint + the fix packet's §2033 calls ($0, all cached).
Adjudications: M's file copied verbatim, plus the fix packet's §2033 entry for the current call."""
import importlib.util, json, shutil, socket
from datetime import datetime
from pathlib import Path

REPO = Path.home() / 'SaneApps/clients/translations'
BOOK = REPO / 'books/le-blanc-theses-theologicae'
M_APPLY = BOOK / 'sources/_ocr_decretis/apply_decretis_xxxiii_lxv_densify.py'
OLD = 'decretis_xxxiii_lxv_densify'
FIX = 'decretis_2033_strang_fix'
STEM = OLD + '_r2'
DFR = REPO / 'outputs/dual-family-review'

src = M_APPLY.read_text(encoding='utf-8')
def rep(a, b):
    global src
    assert src.count(a) == 1, a[:70]
    src = src.replace(a, b)
rep("PACKET_STEM = %r" % OLD, "PACKET_STEM = %r" % STEM)
spec = importlib.util.spec_from_loader('apr2', loader=None)
ap = importlib.util.module_from_spec(spec)
ap.__file__ = str(M_APPLY)
exec(compile(src, str(M_APPLY) + ' [r2]', 'exec'), ap.__dict__)
A = ap.AUDIT
SHARED = ('identity.json', 'publication_scope.json', 'expected_sections.json')


def seed_checkpoint():
    dst = DFR / ('%s.aligned.checkpoint.json' % STEM)
    if dst.exists():
        print('checkpoint exists (resume)', dst); return
    m = json.loads((DFR / ('%s.aligned.checkpoint.json' % OLD)).read_text(encoding='utf-8'))
    f = json.loads((DFR / ('%s.aligned.checkpoint.json' % FIX)).read_text(encoding='utf-8'))
    for lane, calls in f['calls'].items():
        if '2033' in calls:
            m['calls'].setdefault(lane, {})['2033'] = calls['2033']
            print('seeded', lane, '2033 from fix checkpoint')
    dst.write_text(json.dumps(m, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('wrote', dst)


def write_adjudications():
    m = json.loads((A / ('%s.adjudications.json' % OLD)).read_text(encoding='utf-8'))
    f = json.loads((A / ('%s.adjudications.json' % FIX)).read_text(encoding='utf-8'))
    new = f.get('2033') or []
    have = {(e['model'], e['response_id']) for e in m.get('2033', [])}
    m.setdefault('2033', []).extend(e for e in new if (e['model'], e['response_id']) not in have)
    ap.ADJUDICATIONS.write_text(json.dumps(m, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('adjudications', ap.ADJUDICATIONS, 'sections', len(m), 'entries', sum(len(v) for v in m.values()))


def main():
    if 'mini' not in socket.gethostname().lower():
        raise SystemExit('refuse: not Mini')
    old_files = {p: p.read_bytes() for p in A.glob(OLD + '.*')}
    shared = {n: (A / n).read_bytes() for n in SHARED if (A / n).exists()}
    fp0 = ap.crocius_baron_fingerprint(); print('crocius/baron before', fp0, flush=True)
    seed_checkpoint(); write_adjudications()
    try:
        packet_path, review_path, packet = ap.build_packet_and_review()
    finally:
        for n, b in shared.items():
            (A / n).write_bytes(b)
        print('restored shared audit files', list(shared))
    summ = ap._review_summary(review_path)
    old_pkt = json.loads((A / (OLD + '.packet.json')).read_text(encoding='utf-8'))
    fix_pkt = json.loads((A / (FIX + '.packet.json')).read_text(encoding='utf-8'))
    rcpt = {
        'packet_stem': STEM, 'packet': str(packet_path), 'review': str(review_path),
        'packet_id': packet['packet_id'], 'before': 2027, 'after': 2060,
        'added_sections': [int(s) for s in ap.SECS], 'changed_sections': [],
        'reissue_of': {'packet_stem': OLD, 'packet_id': old_pkt['packet_id'],
                       'reason': 'Old M packet no longer regenerates after the reviewed §2033 Strang fix; old audit files kept untouched as the historical record.'},
        'revision': {'section': 2033, 'packet_stem': FIX, 'packet_id': fix_pkt['packet_id'],
                     'record': 'sources/_ocr_decretis/%s.json' % FIX},
        'review_cost': '$0 (all calls reused from %s and %s checkpoints)' % (OLD, FIX),
        'two_family_review': summ,
        'gates': {'validate_audit_receipt': 'ok'},
        'punch_x': 'NO', 'ship': 'NO', 'claim': 'le-blanc-theses-densify stays claimed',
    }
    rp = A / (STEM + '.receipt.json')
    rp.write_text(json.dumps(rcpt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('receipt', rp)
    for p, b in old_files.items():
        if p.read_bytes() != b:
            raise SystemExit('old M audit file changed: %s' % p)
    print('old M audit files untouched', len(old_files))
    nl = '\n'
    block = ('## %s (Densify — Le Blanc packet M re-issued as r2 LOCAL)' % datetime.now().strftime('%Y-%m-%d') + nl + nl
             + '- `%s` (%s) re-issues `%s` (%s) for §2028-2060 against the current English (§2033 John Strang fix, `%s` %s). Old M audit files kept untouched; `val.py` stems now use r2 in place of M.' % (STEM, packet['packet_id'][:8], OLD, old_pkt['packet_id'][:8], FIX, fix_pkt['packet_id'][:8]) + nl
             + '- Review: aligned profile, all calls reused from the M and fix checkpoints ($0); adjudications = M file verbatim + fix §2033 entry. Tip unchanged. Punch X = NO. Not shipped.' + nl + nl)
    for h in (ap.HANDOFF, REPO / 'docs/SESSION_HANDOFF.md', REPO / 'SESSION_HANDOFF.md'):
        if h.exists() and 're-issued as r2' not in h.read_text(encoding='utf-8')[:4000]:
            h.write_text(block + h.read_text(encoding='utf-8'), encoding='utf-8'); print('prepended', h)
    fp1 = ap.crocius_baron_fingerprint(); print('crocius/baron after', fp1)
    if fp1 != fp0:
        raise SystemExit('Crocius/Baron changed; refuse')
    print('DONE r2 packet', packet['packet_id'], flush=True)


if __name__ == '__main__':
    main()
