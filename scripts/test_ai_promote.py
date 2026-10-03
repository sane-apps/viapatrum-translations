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

    def test_arbiter_note_checks_only_no_narrative(self):
        a = {'model': 'm-a', 'parsed': {'verdict': 'pass',
             'notes': 'A narrative with a quoted claim.',
             'checks': {'completeness': True, 'scripture': True}}}
        b = {'model': 'm-b', 'parsed': {'verdict': 'fail',
             'notes': 'B narrative: omits the giant passage.',
             'checks': {'completeness': False, 'scripture': True}}}
        note = promote.build_arbiter_note(a, b)
        self.assertIn('m-a', note)
        self.assertIn('completeness', note)
        self.assertNotIn('giant passage', note)
        self.assertNotIn('quoted claim', note)
        self.assertIn('independently', note)

    def test_arbiter_note_handles_unreadable(self):
        note = promote.build_arbiter_note({}, {'model': 'm-b'})
        self.assertIn('unreadable', note)
        self.assertIn('none', note)

    def test_gpt_oss_out_of_arbiter_defaults(self):
        self.assertNotIn('@cf/openai/gpt-oss-20b', promote.ARBITER_DEFAULTS)


    def _override_bundle_entry(self):
        bundle = {'section': 's1', 'book': 'b', 'greek': ['g1'],
                  'justification': {'draft_model': 'm-d'}, 'english_row': {}}
        good = {'model': 'm-x', 'ok': True,
                'parsed': {'verdict': 'pass', 'checks': {},
                           'pass_a_fidelity': True, 'title_is_thought': True,
                           'covered_source_paragraphs': [1], 'uncertainties': []}}
        return bundle, good

    def test_arbiter_promote_excuses_single_dissent(self):
        bundle, good = self._override_bundle_entry()
        bad = dict(good, model='m-y', ok=False)
        arb = dict(good, model='m-z', decision='PROMOTE')
        entry = {'section': 's1', 'binding': 'B', 'draft_model': 'm-d',
                 'checker_a': good, 'checker_b': bad, 'arbiter': arb}
        with patch.object(promote, 'structural_ok', return_value={'ok': True}), \
             patch.object(promote, 'bundle_binding', return_value='B'), \
             patch.object(promote, 'model_families',
                          side_effect=lambda m: {m}), \
             patch.object(promote, 'checker_verdict_ok', return_value=True):
            self.assertTrue(promote.review_is_current(bundle, entry, 'm-d'))

    def test_arbiter_hold_keeps_veto(self):
        bundle, good = self._override_bundle_entry()
        bad = dict(good, model='m-y', ok=False)
        arb = dict(good, model='m-z', ok=False, decision='HOLD')
        entry = {'section': 's1', 'binding': 'B', 'draft_model': 'm-d',
                 'checker_a': good, 'checker_b': bad, 'arbiter': arb}
        with patch.object(promote, 'structural_ok', return_value={'ok': True}), \
             patch.object(promote, 'bundle_binding', return_value='B'), \
             patch.object(promote, 'model_families',
                          side_effect=lambda m: {m}), \
             patch.object(promote, 'checker_verdict_ok', return_value=True):
            self.assertFalse(promote.review_is_current(bundle, entry, 'm-d'))

    def test_two_fails_no_override(self):
        bundle, good = self._override_bundle_entry()
        bad_a = dict(good, model='m-x', ok=False)
        bad_b = dict(good, model='m-y', ok=False)
        entry = {'section': 's1', 'binding': 'B', 'draft_model': 'm-d',
                 'checker_a': bad_a, 'checker_b': bad_b}
        with patch.object(promote, 'structural_ok', return_value={'ok': True}), \
             patch.object(promote, 'bundle_binding', return_value='B'), \
             patch.object(promote, 'model_families',
                          side_effect=lambda m: {m}), \
             patch.object(promote, 'checker_verdict_ok', return_value=True):
            self.assertFalse(promote.review_is_current(bundle, entry, 'm-d'))


ARB = 'nvidia/nemotron-3-super-120b-a12b'


def scripture_fail(reasons, notes='', fidelity=True, title=True, failed=('scripture',)):
    checks = {key: True for key in ('source_identity', 'completeness', 'negation', 'agency',
                                    'modality', 'doctrine', 'scripture')}
    for key in failed:
        checks[key] = False
    return {'verdict': 'fail', 'reviewer': 'model', 'notes': notes, 'checks': checks,
            'pass_a_fidelity': fidelity, 'title_is_thought': title,
            'covered_source_paragraphs': [1], 'uncertainties': [], 'reasons': reasons}


def grounding_bundle(english):
    return {'section': 's1', 'greek': ['g1'],
            'english_row': {'section': 's1', 'english': english},
            'justification': {'draft_model': DRAFT}}


def grounding_entry(fail_a, pass_b_model=B, arbiter=None):
    entry = {'section': 's1', 'binding': 'B', 'draft_model': DRAFT,
             'checker_a': {'model': A, 'ok': False, 'parsed': fail_a},
             'checker_b': {'model': pass_b_model, 'ok': True, 'parsed': verdict()}}
    if arbiter is not None:
        entry['arbiter'] = arbiter
    return entry


PASS_B_CITED = ["Man shall not live by bread alone, but by every word of God. "
                "(Deuteronomy 8:3; cf. Matthew 4:4) Unless one is born of water and spirit. "
                "(John 3:5) I am the way and the door. (John 14:6) A veil lies on their hearts. "
                "(2 corinthians 3:14)"]


class GroundingTests(unittest.TestCase):
    def test_presence_refutation_overrides(self):
        fail = scripture_fail(["The quote lacks Deuteronomy 8:3/Matthew 4:4 citation."])
        result = promote.grounding_override(grounding_entry(fail), grounding_bundle(PASS_B_CITED))
        self.assertTrue(result['override'], result)
        self.assertEqual(result['detail']['refuted_sentences'][0]['basis'], 'present-in-pass-b')

    def test_gloss_scoped_demand_refuted(self):
        fail = scripture_fail(["Missing inline scripture citations in Pass A."],
                              notes='Pass A gloss lacks citation for the bread quote.')
        result = promote.grounding_override(grounding_entry(fail), grounding_bundle(PASS_B_CITED))
        self.assertTrue(result['override'], result)
        self.assertIn('gloss-layer', result['detail']['refuted_sentences'][-1]['basis'])

    def test_genuinely_missing_citation_holds(self):
        fail = scripture_fail(["Pass B omits the John 3:5 citation for the rebirth quote."])
        bare = grounding_bundle(['Unless one is born of water and spirit, with no citation.'])
        self.assertFalse(promote.grounding_override(grounding_entry(fail), bare)['override'])

    def test_correctness_dispute_holds(self):
        fail = scripture_fail(["The (John 14:6) citation is wrong, it should be John 10:9."])
        self.assertFalse(promote.grounding_override(
            grounding_entry(fail), grounding_bundle(PASS_B_CITED))['override'])

    def test_non_scripture_fail_blocks(self):
        fail = scripture_fail(["The quote lacks John 3:5 citation."], failed=('scripture', 'completeness'))
        self.assertFalse(promote.grounding_override(
            grounding_entry(fail), grounding_bundle(PASS_B_CITED))['override'])

    def test_vague_fail_holds(self):
        fail = scripture_fail(["Scripture handling seems weak overall."])
        self.assertFalse(promote.grounding_override(
            grounding_entry(fail), grounding_bundle(PASS_B_CITED))['override'])

    def test_api_error_blocks(self):
        fail = scripture_fail(["The quote lacks John 3:5 citation."])
        entry = grounding_entry(fail)
        entry['checker_a']['api_error'] = True
        self.assertFalse(promote.grounding_override(entry, grounding_bundle(PASS_B_CITED))['override'])

    def test_bare_parsed_blocks(self):
        entry = grounding_entry(scripture_fail(['x']))
        entry['checker_a']['parsed'] = {}
        self.assertFalse(promote.grounding_override(entry, grounding_bundle(PASS_B_CITED))['override'])

    def test_praise_sentence_does_not_satisfy(self):
        fail = scripture_fail([], notes='Renders John 3:5 without error.')
        self.assertFalse(promote.grounding_override(
            grounding_entry(fail), grounding_bundle(PASS_B_CITED))['override'])

    def test_format_nit_ignored_when_claim_refuted(self):
        fail = scripture_fail(["Pass B uses incorrect citation formatting (lowercase, post-block "
                               "placement) and omits citation for John 14:6 in fourth clause."])
        result = promote.grounding_override(grounding_entry(fail), grounding_bundle(PASS_B_CITED))
        self.assertTrue(result['override'], result)

    def test_fidelity_flag_falls_with_citation_reasons(self):
        fail = scripture_fail(["Missing inline scripture citations in Pass A."], fidelity=False)
        result = promote.grounding_override(grounding_entry(fail), grounding_bundle(PASS_B_CITED))
        self.assertTrue(result['override'], result)
        self.assertIn('pass_a_fidelity', result['detail']['flags_excused'])

    def test_fidelity_flag_with_noncitation_defect_holds(self):
        fail = scripture_fail(["Missing inline citations in Pass A.", "Pass A adds a clause about giants."],
                              fidelity=False)
        self.assertFalse(promote.grounding_override(
            grounding_entry(fail), grounding_bundle(PASS_B_CITED))['override'])

    def test_mixed_clause_does_not_refute(self):
        fail = scripture_fail(["Omits the final clause of the paragraph but the John 3:5 citation is present."])
        self.assertFalse(promote.grounding_override(
            grounding_entry(fail), grounding_bundle(PASS_B_CITED))['override'])

    def test_rem_close_receipt_replay(self):
        qwen = scripture_fail(
            ["Missing inline scripture citations in Pass A (e.g., 'Man shall not live by bread alone' "
             "lacks Deuteronomy 8:3/Matthew 4:4 citation"],
            notes=("source: 'γὰρ εἴρηκεν ἁπλῶς τῶν Ἰουδαίων' (p1); English: 'For it has been said that the "
                   "Jews will be deprived of bread and water' (Pass A gloss lacks citation for 'Man shall "
                   "not live by bread alone' quote)"),
            fidelity=False)
        nemotron = scripture_fail(
            ["Missing inline citation for Matthew 4:4 / Deuteronomy 8:3 quotation in Pass A",
             "Missing inline citation for 2 Corinthians 3:14 quotation in Pass A",
             "Missing inline citation for John 3:5 quotation in Pass A",
             "Missing inline citation for John 14:6 quotation in Pass A",
             "Pass B uses incorrect citation formatting (lowercase, post-block placement) and omits "
             "citation for John 14:6 in fourth clause"],
            notes=("The source Greek contains scriptural quotations which correspond to Matthew 4:4 / "
                   "Deuteronomy 8:3, and later which is John 3:5, and which is John 14:6. Pass A renders "
                   "these quotations but omits the required inline parenthetical citations (e.g., "
                   "(Matthew 4:4), (John 3:5), (John 14:6)) beside the quoted clauses as mandated by the "
                   "standing rules. Pass B includes some citations but uses incorrect formatting: it "
                   "places them after the quotation block and uses lowercase ('cf.', '2 corinthians') and "
                   "non-standard punctuation, and omits citations for some quotes (e.g., the John 14:6 "
                   "quote in the fourth clause of Pass B lacks a citation despite being present in the "
                   "source). Furthermore, the source contains a quotation from 2 Corinthians 3:14, and "
                   "Pass A renders it but omits the citation, while Pass B includes it but with incorrect "
                   "casing ('2 corinthians 3:14') and places it after the quotation block. The standing "
                   "rules require inline parenthetical citations like (Isaiah 29:13) as REQUIRED additions "
                   "beside quoted clauses. Failure to provide correct inline citations for all scriptural "
                   "quotations constitutes a failure of the 'scripture' check."))
        arbiter = {'model': ARB, 'ok': False, 'parsed': nemotron,
                   'decision': 'HOLD', 'reason': 'split decision stands; parked, never published'}
        entry = grounding_entry(qwen, pass_b_model='@cf/zai-org/glm-4.7-flash', arbiter=arbiter)
        entry['draft_model'] = '@cf/meta/llama-3.3-70b-instruct-fp8-fast'
        bundle = grounding_bundle(PASS_B_CITED)
        bundle['justification']['draft_model'] = entry['draft_model']
        result = promote.grounding_override(entry, bundle)
        self.assertTrue(result['override'], result)
        self.assertEqual(len(result['detail']['failers']), 2)

    def test_extract_refs_aliases_and_ranges(self):
        refs = promote.extract_refs('See (Dt 8:3), 2 Cor 3:14-15, Jn 3, and Song of Sol 2:4.')
        self.assertIn(('deut', 8, 3), refs)
        self.assertIn(('2cor', 3, 14), refs)
        self.assertIn(('john', 3, None), refs)
        self.assertNotIn(('song', 2, 4), refs)  # 'Sol' is not a registered alias.
        self.assertEqual(promote.extract_refs('bare page marker 70.348 and Tome 2'), [])

    def test_review_current_honors_grounding(self):
        fail = scripture_fail(["The quote lacks John 3:5 citation."])
        entry = grounding_entry(fail)
        entry['grounding_override'] = {'overridden': True}
        bundle = grounding_bundle(PASS_B_CITED)
        with patch.object(promote, 'structural_ok', return_value={'ok': True}), \
             patch.object(promote, 'bundle_binding', return_value='B'), \
             patch.object(promote, 'checker_verdict_ok', return_value=False):
            self.assertTrue(promote.review_is_current(bundle, entry, DRAFT))

    def test_review_current_reholds_when_pass_b_changes(self):
        fail = scripture_fail(["The quote lacks John 3:5 citation."])
        entry = grounding_entry(fail)
        entry['grounding_override'] = {'overridden': True}
        bundle = grounding_bundle(['Unless one is born of water and spirit, with no citation.'])
        with patch.object(promote, 'structural_ok', return_value={'ok': True}), \
             patch.object(promote, 'bundle_binding', return_value='B'), \
             patch.object(promote, 'checker_verdict_ok', return_value=False):
            self.assertFalse(promote.review_is_current(bundle, entry, DRAFT))


class JevGateTests(unittest.TestCase):
    def _entry_bundle(self):
        bundle = {'section': 's1', 'book': 'b', 'greek': ['g1'],
                  'english_row': {'english': ['x (John 3:5)']},
                  'justification': {'draft_model': DRAFT}}
        return {}, bundle

    def _cites(self, choice, conf, cf=False):
        return {'section': 's1', 'cites': [{'display': 'John 3:5', 'sentence': 's',
                'choice': choice, 'verdict': 'v', 'confidence': conf,
                'auto': True, 'cf': cf}]}

    def test_hold_fires_on_high_conf_contradicts(self):
        entry, bundle = self._entry_bundle()
        with patch.dict(promote.os.environ, {'TYPESAFE_API_KEY': 'k'}), \
             patch('jev_cite_check.check_section',
                   return_value=self._cites('contradicts', 0.97)):
            hold = promote.jev_citation_gate(entry, bundle)
        self.assertTrue(hold['held'])
        self.assertIn('John 3:5', hold['reason'])
        self.assertIn('jev_cites', entry)

    def test_cf_contradicts_does_not_hold(self):
        entry, bundle = self._entry_bundle()
        with patch.dict(promote.os.environ, {'TYPESAFE_API_KEY': 'k'}), \
             patch('jev_cite_check.check_section',
                   return_value=self._cites('contradicts', 0.97, cf=True)):
            self.assertIsNone(promote.jev_citation_gate(entry, bundle))
        self.assertIn('jev_cites', entry)

    def test_low_conf_contradicts_does_not_hold(self):
        entry, bundle = self._entry_bundle()
        with patch.dict(promote.os.environ, {'TYPESAFE_API_KEY': 'k'}), \
             patch('jev_cite_check.check_section',
                   return_value=self._cites('contradicts', 0.27)):
            self.assertIsNone(promote.jev_citation_gate(entry, bundle))

    def test_supports_never_holds(self):
        entry, bundle = self._entry_bundle()
        with patch.dict(promote.os.environ, {'TYPESAFE_API_KEY': 'k'}), \
             patch('jev_cite_check.check_section',
                   return_value=self._cites('supports', 0.99)):
            self.assertIsNone(promote.jev_citation_gate(entry, bundle))

    def test_missing_key_skips(self):
        entry, bundle = self._entry_bundle()
        with patch.dict(promote.os.environ, {'TYPESAFE_API_KEY': ''}):
            self.assertIsNone(promote.jev_citation_gate(entry, bundle))
        self.assertEqual(entry['jev_cites'], {'skipped': 'no-key'})

    def test_api_error_skips(self):
        entry, bundle = self._entry_bundle()
        with patch.dict(promote.os.environ, {'TYPESAFE_API_KEY': 'k'}), \
             patch('jev_cite_check.check_section', side_effect=TimeoutError('slow')):
            self.assertIsNone(promote.jev_citation_gate(entry, bundle))
        self.assertIn('TimeoutError', entry['jev_cites']['error'])

    def test_grounding_refuses_jev_hold(self):
        fail = scripture_fail(['The quote lacks John 3:5 citation.'])
        entry = grounding_entry(fail)
        entry['jev_hold'] = {'held': True}
        bundle = grounding_bundle(PASS_B_CITED)
        self.assertFalse(promote.grounding_override(entry, bundle)['override'])



class ClauseOverrideTests(unittest.TestCase):
    def _entry(self, reasons, pass_b_ok=True):
        fail = {'verdict': 'fail', 'reasons': reasons, 'notes': '', 'checks': {'completeness': False}}
        entry = {
            'section': 's1', 'binding': 'B', 'draft_model': DRAFT,
            'checker_a': {'model': A, 'ok': False, 'parsed': fail},
            'checker_b': {'model': B, 'ok': pass_b_ok, 'parsed': verdict() if pass_b_ok else fail},
        }
        return entry

    def test_present_omission_overrides(self):
        gloss = 'since He was about to rebuke Israel and make the charge known'
        entry = self._entry(["Pass A omitted the clause 'since He was about to rebuke Israel' from the reading."])
        bundle = {
            'section': 's1', 'greek': ['Ἐπειδὴ γὰρ ἔμελλε τὰς κατὰ τοῦ Ἰσραὴλ'],
            'justification': {'draft_model': DRAFT, 'pass_a_gloss': gloss},
            'english_row': {'english': [gloss]},
        }
        result = promote.clause_override(entry, bundle)
        self.assertTrue(result['override'], result)

    def test_mistranslation_blocks_clause_override(self):
        gloss = 'since He was about to rebuke Israel'
        entry = self._entry([
            "Pass A omitted the clause 'since He was about to rebuke Israel' from the reading.",
            "Mistranslated 'πεπονηκότων' as 'those involved in the labor' rather than those who had toiled.",
        ])
        bundle = {
            'section': 's1',
            'greek': ['Ἐπειδὴ γὰρ ἔμελλε πεπονηκότων'],
            'justification': {'draft_model': DRAFT, 'pass_a_gloss': gloss},
            'english_row': {'english': [gloss + ' and all those involved in the labor']},
        }
        self.assertFalse(promote.clause_override(entry, bundle)['override'])

    def test_arbiter_promote_holds_unsupported_sentence(self):
        quote = 'As they ascend, they will experience the perfection and blamelessness that come from being in Christ'
        bundle = {
            'section': 's1', 'book': 'b', 'binding': 'B',
            'greek': ['ἣ καὶ ἀληθῶς ἐστι τελεία καὶ ἄμωμος'],
            'justification': {
                'draft_model': 'm-d',
                'pass_a_gloss': 'The intelligible Jerusalem, which is truly perfect and blameless, is the Church.',
            },
            'english_row': {'english': [quote + '.']},
        }
        bad = {
            'model': 'm-y', 'ok': False,
            'parsed': {'verdict': 'fail', 'reasons': ["Pass B adds the sentence '%s'." % quote]},
        }
        good = {'model': 'm-x', 'ok': True, 'parsed': {'verdict': 'pass'}}
        arb = {'model': 'm-z', 'ok': True, 'decision': 'PROMOTE', 'parsed': {'verdict': 'pass'}}
        entry = {
            'section': 's1', 'binding': 'B', 'draft_model': 'm-d',
            'checker_a': good, 'checker_b': bad, 'arbiter': arb,
        }
        with patch.object(promote, 'structural_ok', return_value={'ok': True}), \
             patch.object(promote, 'bundle_binding', return_value='B'), \
             patch.object(promote, 'model_families', side_effect=lambda model: {model}), \
             patch.object(promote, 'checker_verdict_ok', return_value=True):
            self.assertFalse(promote.review_is_current(bundle, entry, 'm-d'))

    def test_review_current_honors_clause_override(self):
        gloss = 'since He was about to rebuke Israel and make the charge known'
        entry = self._entry(["Pass A omitted the clause 'since He was about to rebuke Israel' from the reading."])
        entry['clause_override'] = {'overridden': True}
        entry['binding'] = 'B'
        bundle = {
            'section': 's1', 'greek': ['Ἐπειδὴ γὰρ ἔμελλε τὰς κατὰ τοῦ Ἰσραὴλ'],
            'justification': {'draft_model': DRAFT, 'pass_a_gloss': gloss},
            'english_row': {'english': [gloss]},
        }
        with patch.object(promote, 'structural_ok', return_value={'ok': True}), \
             patch.object(promote, 'bundle_binding', return_value='B'), \
             patch.object(promote, 'checker_verdict_ok', return_value=False):
            self.assertTrue(promote.review_is_current(bundle, entry, DRAFT))



if __name__ == '__main__':
    unittest.main()
