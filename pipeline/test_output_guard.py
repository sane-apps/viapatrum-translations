"""Save-time output guard: python3 -m pytest pipeline/test_output_guard.py"""
from pipeline.check_pass_ab import output_guard_errors


def test_clean_prose_passes():
    assert output_guard_errors(["Holy, holy, holy is the Lord. That that is true, he had had no doubt."]) == []


def test_glued_stutter_rejected():
    assert output_guard_errors(["They were many.many.many in number."])


def test_word_run_rejected():
    assert output_guard_errors(["and and and and so it went."])


def test_doubled_function_word_rejected():
    assert output_guard_errors(["He went to the the city."])


def test_cut_off_paragraph_rejected_when_required():
    assert output_guard_errors(["He spoke, and because the Spirit"], require_full_stop=True)
    assert output_guard_errors(["He spoke, and because the Spirit"]) == []  # chunked slices may end mid-clause


def test_scripture_repeats_and_ref_lists_ok():
    assert output_guard_errors(["Lord, Lord, open to us (Matthew 7:22). Amen, amen. See Genesis 1:1; Genesis 2:3; Genesis 3:1; Genesis 4:1."]) == []


def test_quote_and_ref_endings_ok():
    assert output_guard_errors(['He said, "Come."', "See this (John 3:16)."], require_full_stop=True) == []
