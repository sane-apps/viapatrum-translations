# Beliefs map: where did this belief come from?

Owner-approved 2026-10-03. Code: `scripts/doctrine_map.py`. Data:
`websites/fathers.saneapps.com/data/explore/doctrines.json` (definitions) and
`doctrine_map.json` (results). This file is the spec; change it before
changing the method.

## Goal

For each doctrine that divides the churches, show when it first appears in
the early writings, what came before it, and who spoke against it, with every
claim tied to a quoted, linked passage. The bar is fairness that a Catholic,
an Orthodox Christian and a Baptist scholar would each accept.

## Phase one

The writers who died by 450 come first. Translation lanes run earliest writer
first: untranslated early works, then re-checks of translated early works,
then later centuries (`scripts/book_era.py`, `run-recert-lanes.sh`). A gap
inventory of every surviving early work, `docs/early-inventory.json`, shows
what the library still lacks.

## Exact meanings, not similar sounds (owner 2026-10-03)

"Real presence is a different belief shared by many, but the Catholic belief
is ultra specific... not 'sounds similar', because then anyone can claim the
Fathers agree with them." So the map is built on QUESTIONS, each with its
competing precise POSITIONS (`data/explore/doctrine_questions.json`):

- each position is defined in its own tradition's words, checked word for
  word against official texts (`doctrines.json` keeps the per-doctrine
  quotes);
- its MARK is the one thing that tells it from its neighbours;
- the question's SHARED GROUND is what several positions affirm, and it
  counts for none of them.

Example, the Eucharist: memorial, spiritual presence, sacramental union,
real change with no defined mode, transubstantiation. "This is my body"
excludes memorial and decides nothing among the other four.

## Verdicts, per passage, for every position at once

| Verdict | Meaning |
|---|---|
| states | the passage says this position's mark |
| excludes | the passage rules this position out |
| compatible | fits, or doesn't touch it, but decides nothing |
| disputed | graders could not reach a majority |

A writer counts as holding a position only through a passage that states
its mark, or that excludes every rival. Silence is never evidence.

## Method

1. **Index:** every English paragraph in the library, embedded with the same
   model as site search.
2. **Search:** for each question, the nearest passages to every phrasing
   (the question, its queries and shared ground, and each position's
   statement, mark and exclusions), then reranked. Up to 180 early and 30
   later candidates per question.
3. **Blind judging:** Kimi K2.6 and GPT-OSS-120B (labs the translation lanes do not use) see the positions only as letters,
   shuffled per passage, with no names or churches, and give every position
   a verdict with the deciding words quoted. Splits go to Nemotron; with no
   majority the verdict is disputed. (Owner exception to the translate-only
   rule, recorded in `LLM_VENDOR_API_SOP.md`.)
4. **Audit:** Claude 4.5+ subagents re-check every "states", "excludes" and
   "disputed" verdict, and every earliest statement of a position, against
   the passage and, where it decides the date, the original language. An
   audited change wins and is logged with its reason.
5. **Report:** `doctrine_map.py report` writes the site data, including how
   many writers were searched in each century, so readers can see how deep the
   evidence goes. A graded passage whose English has changed since the index
   is left out until the next index and grade see the new words, and the site
   build also leaves out any passage its own work page no longer says
   (`beliefs_page._on_page`). A quote never outlives its words. The report
   keeps a new verdict with `reviewed: false`; the site shows only reviewed
   verdicts (`beliefs_page._deciding`), so a verdict stays off the site until
   the audit passes it.
   Passage ids hash the words as the reader sees them (`speak_text.read_text`;
   owner 2026-10-06: no pin to the legacy cleaner). A graded passage whose id
   leaves the corpus is logged by the report, not dropped in silence.
   Topic-page excerpts marked `source_verified` (and not `needs_recert`) are
   searched too and link to `/e/<id>/`; seed ANF excerpts never are.
   The nightly runner skips the report when an earlier step failed, so a failed
   or skipped grade never rewrites the site map. The page date is the last full
   grade (`outputs/doctrine-map/graded-at.json`), not the day the report ran.
   Owner decision (made by Claude at the owner's request, 2026-10-07): only
   audited deciding verdicts publish (`_deciding`, reviewed-only). The audit is
   a Claude review of `reviewed: false` verdicts, run in a working session; the
   page says how many verdicts wait for it.
   A passage that fails to grade is logged and retried the next night; one vote
   or none is never stored as "disputed".

## Fairness rules

- Graders never see a position's name or which church holds it.
- Silence is never evidence.
- Words both sides claim ("through the Son", "faith alone", "sacrifice",
  "this is my body") are shared ground and decide nothing.
- The same rules apply to every doctrine, whichever church holds it.
- Every grade on the page shows its quote and links to the full passage.
- Commentary is written by the orchestrating agent from the graded evidence
  and verified sources, never by the grading models.

## The page

- A page per question: each position as a timeline row (100 to 800), marking
  passages that state it or exclude it, with its earliest statement called
  out, plus a band for the shared ground.
- A filter by tradition.
- Every deciding passage in date order, with what it decides and what it
  leaves open.
- Tapping a mark opens the passage.
- Rebuilt by every ship; re-graded incrementally as new works are certified.

## Churches and questions (owner 2026-10-06)

- Eleven churches, in chip order: Catholic, Orthodox, Oriental Orthodox,
  Church of the East, Lutheran, Reformed, Anglican, Methodist, Baptist,
  Anabaptist, Pentecostal. 23 questions: the first 19 plus spiritual gifts,
  sanctification, Christ's natures and the millennium.
- `doctrine_questions.json` decides which questions and positions show and
  which churches hold (`traditions`) or reject (`rejected_by`) each;
  `beliefs_page.load` overlays the graded map on it. A new question or church
  shows at the next build, with "no early passage yet" until the nightly job
  searches and grades it. No change to this script was needed for new
  questions; at most 8 positions per question (grader letters A-H).
- The page has no "divided" state. A church that is divided, or has no
  settled text, is left unplaced and named in `tradition_notes` (one short
  line under the chips); `public_note` holds a line the whole question needs.
  `rejected_by_sources` keeps the quote behind each new rejection.
- Oriental Orthodox placements rest mainly on Coptic and Ethiopian texts; the
  page says so on every question that places them.
- Changing a position's statement, mark or excluded_by, or adding a position,
  changes the grading key and re-grades the whole question. Church lists,
  names, quotes and notes do not.
- The research, review and merge script live in the site repo under
  `outputs/beliefs-expansion-20261006/` (`apply_review.py`).

## Hard boundaries the audit checks first

From the definitions research (2026-10-03). These marks are close in early
texts; every "states" or "excludes" verdict on them gets an audit.

- Eucharist presence: Cyril of Jerusalem's "what seems bread is not bread"
  (near the transubstantiation mark); Theodoret and Gelasius "the nature of
  bread remains" (states sacramental union, excludes real change); Augustine's
  figure language beside his realist language; "transformed" against the
  Lutheran mark.
- Eucharist sacrifice: "offering" only excludes no-sacrifice; propitiatory
  needs a stated purpose (sins, the dead) or Christ named as victim.
- Rome: Ignatius "presides in love", Irenaeus "more powerful origin" fit both
  honour and jurisdiction.
- Mary: "spotless", "all-holy" state personal sinlessness at most; a bodily
  taking-up states Dormition and Assumption alike unless her death is
  addressed.
- After death: the Orthodox defining text itself speaks of punishment in
  Hades; its line with purgatory is thin.
- Justification: theosis has no defining text and overlaps infused
  righteousness.
- Scripture: only a claim about the final norm decides; praise is shared
  ground.
- Predestination: only passages about those passed by decide single vs double.
- Church order: Jerome's "bishop and presbyter were once the same" states the
  presbyterian mark only if he denies the bishop's present authority.
- Attribution: works of uncertain authorship (e.g. the "Anaphora of
  Epiphanius") carry their uncertainty onto the page instead of a firm date.

## Known limits

- Evidence is only as deep as what the library has translated; the page says
  so.
- English translations are graded, not the originals. A disputed or
  first-explicit passage is checked against the source language in the audit.
