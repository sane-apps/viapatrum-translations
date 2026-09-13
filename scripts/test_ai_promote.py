#!/usr/bin/env python3
"""Offline regressions for translation promotion. Never calls an inference endpoint."""
import copy
from contextlib import ExitStack
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ai_promote as promote
import draft_claim as draft
from llm_bakeoff import score

DRAFT = '@cf/qwen/qwen3-30b-a3b-fp8'
A = '@cf/google/gemma-4-26b-a4b-it'
B = '@cf/meta/llama-3.3-70b-instruct-fp8-fast'


def bundle():
    source = ['Ὁ θεὸς οὐκ ἀδικεῖ τὸν ἄνθρωπον. Ὁ ἄνθρωπος ἑκουσίως πράττει, οὐκ ἀνάγκῃ.',
              'Διὰ τοῦτο ἔπαινος καὶ ψόγος δίκαιος. Ἀγαπᾷ τοὺς δικαίους ὁ θεός.']
    english = ['God does not wrong a person. Human beings act willingly, not under compulsion.',
               'For this reason, praise and blame are just. God loves the righteous.']
    return {'section': '6.1', 'greek': source,
            'english_row': {'section': '6.1', 'title': 'Willing action and just judgment', 'english': english},
            'justification': {'excerpt_id': 'jeremiah_6_1', 'draft_model': DRAFT,
                'source_text': ' '.join(source), 'pass_b_english': english,
                'pass_a_gloss': 'The divine agent commits no injustice toward a human. The human performs the action voluntarily rather than by necessity. On that basis commendation and censure are deserved. The righteous are objects of divine love.',
                'lemmas': [{'form': 'ἑκουσίως', 'lemma': 'ἑκουσίως', 'gloss': 'willingly'}],
                'choices': [{'term': 'ἀνάγκῃ', 'english': 'under compulsion', 'why': 'Contrasts with voluntary agency.'}],
                'edition': {'id': 'test', 'language': 'grc', 'path': __file__, 'sha256': promote.file_digest(Path(__file__)), 'locus': '6.1'}}}


def verdict():
    return {'verdict': 'pass', 'reviewer': 'model', 'notes': 'οὐκ ἀδικεῖ is rendered does not wrong; ἑκουσίως contrasts with compulsion. Both supplied paragraphs retain all clauses.',
            'checks': {key: True for key in ('source_identity', 'completeness', 'negation', 'agency', 'modality', 'doctrine', 'scripture')},
            'pass_a_fidelity': True, 'title_is_thought': True,
            'covered_source_paragraphs': [1, 2], 'uncertainties': [], 'reasons': []}


def entry(data):
    return {'section': data['section'], 'binding': promote.bundle_binding(data), 'draft_model': DRAFT,
            'checker_a': {'model': A, 'ok': True, 'parsed': verdict()},
            'checker_b': {'model': B, 'ok': True, 'parsed': verdict()}}


class PromotionTests(unittest.TestCase):
    def test_valid_review(self):
        data = bundle()
        self.assertTrue(promote.structural_ok(data)['ok'], promote.structural_ok(data))
        self.assertTrue(promote.review_is_current(data, entry(data), DRAFT))

    def test_false_missing_or_malformed_flags_fail(self):
        for field in verdict()['checks']:
            for value in (False, 'true', None, 1):
                obj = verdict()
                obj['checks'][field] = value
                self.assertFalse(promote.checker_verdict_ok(obj, 2), (field, value))
        for field in ('checks', 'uncertainties', 'covered_source_paragraphs', 'pass_a_fidelity'):
            obj = verdict()
            del obj[field]
            self.assertFalse(promote.checker_verdict_ok(obj, 2), field)
        obj = verdict()
        obj['uncertainties'] = ['An unread clause may reverse the agency.']
        self.assertFalse(promote.checker_verdict_ok(obj, 2))

    def test_omitted_source_paragraph_fails(self):
        obj = verdict()
        obj['covered_source_paragraphs'] = [1]
        self.assertFalse(promote.checker_verdict_ok(obj, 2))
        obj = verdict()
        obj['checks']['completeness'] = False
        self.assertFalse(promote.checker_verdict_ok(obj, 2))

    def test_current_hashes_required(self):
        original = bundle()
        receipt = entry(original)
        for target, field, value in (
            ('english_row', 'english', ['God wrongs a person.']),
            ('english_row', 'title', 'A changed title'),
            ('justification', 'pass_a_gloss', 'A different reading of the text.'),
        ):
            changed = copy.deepcopy(original)
            changed[target][field] = value
            self.assertFalse(promote.review_is_current(changed, receipt, DRAFT))
        changed = copy.deepcopy(original)
        changed['greek'][0] += ' οὐ'
        self.assertFalse(promote.review_is_current(changed, receipt, DRAFT))
        changed = copy.deepcopy(original)
        changed['justification']['reviewer'] = 'ai-crosscheck:a+b'
        self.assertTrue(promote.review_is_current(changed, receipt, DRAFT))

    def test_wrong_source_or_pass_b_fails_structural(self):
        for field, replacement in [('source_text', 'Ἄλλος λόγος.'), ('pass_b_english', ['Another English reading.'])]:
            data = bundle()
            data['justification'][field] = replacement
            self.assertFalse(promote.structural_ok(data)['ok'])

    def test_same_checker_family_fails(self):
        data = bundle()
        for model in (A, '@cf/google/gemma-3-27b', DRAFT, 'unidentified-model'):
            receipt = entry(data)
            receipt['checker_b']['model'] = model
            self.assertFalse(promote.review_is_current(data, receipt, DRAFT), model)

    def test_missing_or_changed_raw_source_fails(self):
        data = bundle()
        data['justification']['edition']['sha256'] = 'old-hash'
        self.assertFalse(promote.structural_ok(data)['ok'])
        data['justification']['edition']['path'] = '/nonexistent/source.xml'
        self.assertFalse(promote.structural_ok(data)['ok'])

    def test_no_provenance_fails(self):
        data = bundle()
        data['justification'].pop('draft_model')
        self.assertFalse(promote.structural_ok(data)['ok'])

    def test_mocked_checker_false_without_reasons_rejected(self):
        obj = verdict()
        obj['pass_a_fidelity'] = False
        with patch.object(promote, 'vendor_call', return_value={'content': json.dumps(obj)}):
            self.assertFalse(promote.run_checker(A, bundle())['ok'])

    def test_content_fail_does_not_shop_for_pass(self):
        with patch.object(promote, 'run_checker', return_value={'ok': False, 'api_error': False}) as run:
            promote.run_checker_chain([A, B], bundle(), draft_model=DRAFT)
            self.assertEqual(run.call_count, 1)
        with patch.object(promote, 'run_checker') as run:
            result = promote.run_checker_chain([A], bundle(), draft_model=DRAFT, prior_models=(A,))
            self.assertFalse(result['ok'])
            run.assert_not_called()

    def test_wrong_book_and_reversed_slice_rejected(self):
        for row in ({'Book slug': 'augustine', 'Claim ID': 'jer-h6'},
                    {'Book slug': 'origen-jeremiah-samuel', 'Claim ID': 'sam-h6'}):
            with self.assertRaises(SystemExit):
                promote.require_supported_claim(row)
        with self.assertRaises(SystemExit):
            promote.sections_from_slice('§§6.3–6.1')

    def test_gross_omission_and_bad_paragraph_type(self):
        data = bundle()
        obj = dict(data['english_row'], pass_a_gloss=data['justification']['pass_a_gloss'], lemmas=data['justification']['lemmas'])
        self.assertFalse(score(obj, json.dumps(obj), '6.1', source=data['greek'] * 20)['ok'])
        obj['english'] = [42]
        self.assertFalse(score(obj, json.dumps(obj), '6.1')['ok'])

    def test_main_refuses_changed_inputs_after_checking(self):
        original = bundle()
        changed = copy.deepcopy(original)
        changed['english_row']['title'] = 'Changed while a checker was running'
        row = {'Claim ID': 'jer-h6', 'Book slug': 'origen-jeremiah-samuel', 'Status': 'claimed', 'Slice (sections)': '§§6.1–6.1'}
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            stack.enter_context(patch.object(promote, 'OUT', Path(tmp)))
            stack.enter_context(patch.object(promote.sys, 'argv', ['ai_promote.py', '--claim', 'jer-h6', '--agent', 'test', '--no-mark-done']))
            stack.enter_context(patch.dict(promote.os.environ, {'CF_TOKEN': 'offline-test', 'SANE_FATHERS_NESTED': '0'}))
            for name in ('acquire_global', 'acquire_claim', 'install_wall_deadline', 'clear_wall_deadline', 'release_all'):
                stack.enter_context(patch.object(promote, name, return_value=True))
            stack.enter_context(patch.object(promote, 'load_lane_config', return_value={}))
            stack.enter_context(patch.object(promote, 'parse_claim_row', return_value=row))
            stack.enter_context(patch.object(promote, 'load_section_bundle', side_effect=[original, changed]))
            stack.enter_context(patch.object(promote.time, 'sleep'))
            stack.enter_context(patch.object(promote, 'run_checker_chain', side_effect=[entry(original)['checker_a'], entry(original)['checker_b']]))
            marked = stack.enter_context(patch.object(promote, 'mark_claim_done'))
            self.assertEqual(promote.main(), 1)
            summary = json.loads(next(Path(tmp).glob('*/summary.json')).read_text())
            self.assertFalse(summary['ok'])
            marked.assert_not_called()

    def test_canonical_writer_preserves_evidence_and_rejects_missing_choices(self):
        fixture = bundle()
        obj = dict(fixture['english_row'], pass_a_gloss=fixture['justification']['pass_a_gloss'],
                   lemmas=fixture['justification']['lemmas'], choices=fixture['justification']['choices'])
        fix = {'section': '6.1', 'homily': 6, 'greek': fixture['greek'], 'klostermann': 'Hom.6.1'}
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            root = Path(tmp)
            book = root / 'books/origen-jeremiah-samuel'
            raw = book / 'sources/first1k/tlg2042.tlg009.opp-grc1.xml'
            raw.parent.mkdir(parents=True)
            raw.write_text(' '.join(fixture['greek']))
            manifest = raw.parent.parent / 'manifest.json'
            manifest.write_text(json.dumps({'files': {'first1k/tlg2042.tlg009.opp-grc1.xml': {'sha256': promote.file_digest(raw)}}}))
            english = book / 'translations/jeremiah_english.json'
            english.parent.mkdir()
            english.write_text('[]')
            just_dir = book / 'reviews/justifications'
            just_dir.mkdir(parents=True)
            for name, value in (('ENG', english), ('JUST_DIR', just_dir), ('RAW_SOURCE', raw), ('XML_SOURCE', raw), ('SOURCE_MANIFEST', manifest)):
                stack.enter_context(patch.object(draft, name, value))
            stack.enter_context(patch.object(promote, 'ROOT', root))
            stack.enter_context(patch.object(draft, 'load_fixture', side_effect=lambda _s: copy.deepcopy(fix)))
            call = stack.enter_context(patch.object(draft, 'vendor_call', return_value={'content': json.dumps(obj)}))
            result = draft.draft_section('6.1', DRAFT, '', '', '', 'offline-test')
            self.assertTrue(result['ok'], result)
            current = json.loads(english.read_text())[0]
            just_path = just_dir / 'jeremiah_6_1.json'
            just = json.loads(just_path.read_text())
            self.assertEqual(just['choices'], obj['choices'])
            self.assertEqual(just['source_text'], ' '.join(fix['greek']))
            self.assertEqual(just['pass_b_english'], current['english'])
            self.assertNotIn('lexica', just['lemmas'][0])
            self.assertTrue(promote.structural_ok({'section': '6.1', 'greek': fix['greek'], 'english_row': current, 'justification': just})['ok'])
            prior = (english.read_bytes(), just_path.read_bytes())
            bad = dict(obj, choices=[])
            call.return_value = {'content': json.dumps(bad)}
            self.assertEqual(draft.draft_section('6.1', DRAFT, '', '', '', 'offline-test')['error'], 'missing_draft_evidence')
            self.assertEqual((english.read_bytes(), just_path.read_bytes()), prior)
            call.reset_mock()
            result = draft.draft_section('6.1', DRAFT, '', '', '', 'offline-test', prep=True)
            self.assertFalse(result['ok'])
            call.assert_not_called()
            raw.write_text('Changed witness')
            self.assertEqual(draft.draft_section('6.1', DRAFT, '', '', '', 'offline-test')['error'], 'raw_source_does_not_match_locked_manifest')
            call.assert_not_called()

    def test_configured_cf_drafts_have_two_independent_checkers(self):
        config = json.loads((Path(__file__).resolve().parents[1] / 'docs/LLM_LANE_CONFIG.json').read_text())['lanes']['cf']
        for model in config['draft']:
            draft_family = promote.model_families(model)
            self.assertTrue(draft_family, model)
            first = [m for m in config['checker_a'] if promote.model_families(m) and not promote.model_families(m) & draft_family]
            self.assertTrue(first, f'No independent checker A for {model}')
            used = draft_family | promote.model_families(first[0])
            second = [m for m in config['checker_b'] if promote.model_families(m) and not promote.model_families(m) & used]
            self.assertTrue(second, f'No independent checker B after {model} -> {first[0]}')

    def test_atomic_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'summary.json'
            path.write_text('old')
            promote.atomic_text(path, '{"ok":false}\n')
            self.assertEqual(json.loads(path.read_text()), {'ok': False})
            self.assertEqual(list(Path(tmp).iterdir()), [path])


if __name__ == '__main__':
    unittest.main()
