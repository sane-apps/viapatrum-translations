# Judging Scripture references in Via Patrum translations (Nov 8, 2026)

Each item is one Bible reference printed in parentheses in a published English translation of a Church Father
(viapatrum.org). Decide whether the reference is right FOR AN ENGLISH READER using KJV/English Bible numbering.

You get: `printed` (as printed), `parsed_as`, `context` (the text around it; the reference sits right after the
words it refers to), `kjv_cited_and_neighbours` (KJV text of the cited verse and 2 verses each side), and for Psalms
`kjv_if_greek_numbering` (KJV text where the Greek/Septuagint Psalm numbering would land in English Bibles).

Use your own knowledge of the whole Bible, not only the verses shown. The translation is modern English from Greek or
Latin, often following the Septuagint, so wording differs from the KJV: judge meaning, not shared words.

Verdicts (exactly one):
- `correct`: the cited verse (or range) is what the words quote, paraphrase or point to. A range that contains the
  verse is correct. A pointer with no quotation is correct when the verse is what the sentence is talking about.
- `greek_numbering`: right passage, but numbered by the Greek/Latin Psalter (or another non-English versification),
  so the English reference differs. Give the English (KJV) reference.
- `near`: same passage but the wrong verse by 1-3 verses in English numbering (not explained by Greek numbering).
  Give the right verse.
- `wrong`: points to a different passage than the words are about. Give the right reference if you can find it.
  Watch attribution too: "called Elijah by the Lord" cited as Luke 1:17 is wrong (the angel says that there; the
  Lord says it in Matthew 11:14).
- `unclear`: you cannot tell (context too thin, or the words fit no verse you can identify).

For each item write one JSON line:
{"id": "...", "verdict": "...", "correct_ref": "Book C:V" or null, "confidence": 0.0-1.0, "reason": "<= 20 words"}
correct_ref uses full English book names and KJV numbering ("Psalm 79:8", "Matthew 11:14"); null when `correct`
or when you can't find it. Be careful and honest; do not guess a correct_ref you are not sure of (say so in reason
and lower confidence). Apocrypha (Wisdom, Sirach, Baruch, Tobit...) count as valid books.
