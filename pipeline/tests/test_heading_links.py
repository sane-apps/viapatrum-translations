from pipeline.bible_links import link_heading_verses


def test_heading_markup_stripped_to_plain_dot_form():
    # PBB Logs 2026-09-17: [[D >> Bible:T]] in a Heading warns
    # (=d~bible… not attached to anything); raw dot-form does not.
    assert (
        link_heading_verses("Homilies on [[Jeremiah 1.1 >> Bible:Jeremiah 1:1]] — x", None)
        == "Homilies on Jeremiah 1.1 — x"
    )
    assert (
        link_heading_verses("On Pascha 1.9 — [[Exodus 12:1–2 >> Bible:Exodus 12:1-2]]", None)
        == "On Pascha 1.9 — Exodus 12:1–2"
    )


def test_heading_plain_text_untouched():
    assert (
        link_heading_verses("Homily on 1 Samuel 28 (the witch of Endor)", None)
        == "Homily on 1 Samuel 28 (the witch of Endor)"
    )
