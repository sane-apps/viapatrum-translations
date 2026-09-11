from pipeline.check_pbb_guards import check_build_scripts
from pipeline.bible_links import index_book_heading, sort_ref_key


def test_guards_clean():
    assert check_build_scripts() == []


def test_wisdom_alias_heading():
    assert index_book_heading("Wisdom of Solomon 2:24") == "Wisdom of Solomon"
    assert index_book_heading("Romans 5:12") == "Romans"
    assert sort_ref_key("Wisdom of Solomon 2:24")[0] < 999
