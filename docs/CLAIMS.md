# Claims — who is working on what

Take the next free slice:

**Tip/SERIES closeout gate:** `python3 scripts/assert_tip_ready.py <english.json> <source.json>` must exit 0 before marking done. Scaffold (`Lemma-led` / `Rem early|mid|closeout`) or tip ops in source are refused.

```bash
python3 scripts/claims.py start --agent YourName
```

That locks the top `free` row. One slice per person. Statuses: `free` → `claimed` → `prepped` (machine crib) or `done` (human Pass B).  
If a `claimed` row is older than 48 hours with no handoff, anyone may set it back to `free`.

**Pass B scripture gate (standing, 2026-09-12):** do **not** mark a claim `done` if the Father quotes or clearly alludes to Scripture and `english[]` lacks an inline parenthetical full-name ref beside the clause. Apparatus / `added_allusions` / `bible_refs` alone fail. No new Adorations densify until the corpus upgrade pass is solid (`docs/scripture-ref-upgrade-pass.md` in the Project store). See `docs/SOP.md`, `TRANSLATION_QA.md` Bible refs, Project store `docs/scripture-refs-inline.md`.

## Open / active claims

| Claim ID | Status | Book slug | Slice (sections) | Agent | Started | Branch | Notes |
|----------|--------|-----------|------------------|-------|---------|--------|-------|
| cyril-alexandria-psalms--ps026-rem-close | free | cyril-alexandria-psalms | ps026-rem-close |  |  | wip/cyril-alexandria-psalms--ps026-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps027-open | free | cyril-alexandria-psalms | ps027-open |  |  | wip/cyril-alexandria-psalms--ps027-open | earliest scaffold |
| cyril-alexandria-psalms--ps027-rem-early | free | cyril-alexandria-psalms | ps027-rem-early |  |  | wip/cyril-alexandria-psalms--ps027-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps027-rem-mid | free | cyril-alexandria-psalms | ps027-rem-mid |  |  | wip/cyril-alexandria-psalms--ps027-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps025-rem-close | free | cyril-alexandria-psalms | ps025-rem-close |  |  | wip/cyril-alexandria-psalms--ps025-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps026-open | free | cyril-alexandria-psalms | ps026-open |  |  | wip/cyril-alexandria-psalms--ps026-open | earliest scaffold |
| cyril-alexandria-psalms--ps026-rem-early | free | cyril-alexandria-psalms | ps026-rem-early |  |  | wip/cyril-alexandria-psalms--ps026-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps026-rem-mid | free | cyril-alexandria-psalms | ps026-rem-mid |  |  | wip/cyril-alexandria-psalms--ps026-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps024-rem-close | free | cyril-alexandria-psalms | ps024-rem-close |  |  | wip/cyril-alexandria-psalms--ps024-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps025-open | free | cyril-alexandria-psalms | ps025-open |  |  | wip/cyril-alexandria-psalms--ps025-open | earliest scaffold |
| cyril-alexandria-psalms--ps025-rem-early | free | cyril-alexandria-psalms | ps025-rem-early |  |  | wip/cyril-alexandria-psalms--ps025-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps025-rem-mid | free | cyril-alexandria-psalms | ps025-rem-mid |  |  | wip/cyril-alexandria-psalms--ps025-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps023-rem-close | free | cyril-alexandria-psalms | ps023-rem-close |  |  | wip/cyril-alexandria-psalms--ps023-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps024-open | free | cyril-alexandria-psalms | ps024-open |  |  | wip/cyril-alexandria-psalms--ps024-open | earliest scaffold |
| cyril-alexandria-psalms--ps024-rem-early | free | cyril-alexandria-psalms | ps024-rem-early |  |  | wip/cyril-alexandria-psalms--ps024-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps024-rem-mid | free | cyril-alexandria-psalms | ps024-rem-mid |  |  | wip/cyril-alexandria-psalms--ps024-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps022-rem-close | free | cyril-alexandria-psalms | ps022-rem-close |  |  | wip/cyril-alexandria-psalms--ps022-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps023-open | free | cyril-alexandria-psalms | ps023-open |  |  | wip/cyril-alexandria-psalms--ps023-open | earliest scaffold |
| cyril-alexandria-psalms--ps023-rem-early | free | cyril-alexandria-psalms | ps023-rem-early |  |  | wip/cyril-alexandria-psalms--ps023-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps023-rem-mid | free | cyril-alexandria-psalms | ps023-rem-mid |  |  | wip/cyril-alexandria-psalms--ps023-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps021-rem-close | free | cyril-alexandria-psalms | ps021-rem-close |  |  | wip/cyril-alexandria-psalms--ps021-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps022-open | free | cyril-alexandria-psalms | ps022-open |  |  | wip/cyril-alexandria-psalms--ps022-open | earliest scaffold |
| cyril-alexandria-psalms--ps022-rem-early | free | cyril-alexandria-psalms | ps022-rem-early |  |  | wip/cyril-alexandria-psalms--ps022-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps022-rem-mid | free | cyril-alexandria-psalms | ps022-rem-mid |  |  | wip/cyril-alexandria-psalms--ps022-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps020-rem-close | free | cyril-alexandria-psalms | ps020-rem-close |  |  | wip/cyril-alexandria-psalms--ps020-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps021-open | free | cyril-alexandria-psalms | ps021-open |  |  | wip/cyril-alexandria-psalms--ps021-open | earliest scaffold |
| cyril-alexandria-psalms--ps021-rem-early | free | cyril-alexandria-psalms | ps021-rem-early |  |  | wip/cyril-alexandria-psalms--ps021-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps021-rem-mid | free | cyril-alexandria-psalms | ps021-rem-mid |  |  | wip/cyril-alexandria-psalms--ps021-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps019-rem-close | free | cyril-alexandria-psalms | ps019-rem-close |  |  | wip/cyril-alexandria-psalms--ps019-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps020-open | free | cyril-alexandria-psalms | ps020-open |  |  | wip/cyril-alexandria-psalms--ps020-open | earliest scaffold |
| cyril-alexandria-psalms--ps020-rem-early | free | cyril-alexandria-psalms | ps020-rem-early |  |  | wip/cyril-alexandria-psalms--ps020-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps020-rem-mid | free | cyril-alexandria-psalms | ps020-rem-mid |  |  | wip/cyril-alexandria-psalms--ps020-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps018-rem-close | free | cyril-alexandria-psalms | ps018-rem-close |  |  | wip/cyril-alexandria-psalms--ps018-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps019-open | free | cyril-alexandria-psalms | ps019-open |  |  | wip/cyril-alexandria-psalms--ps019-open | earliest scaffold |
| cyril-alexandria-psalms--ps019-rem-early | free | cyril-alexandria-psalms | ps019-rem-early |  |  | wip/cyril-alexandria-psalms--ps019-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps019-rem-mid | free | cyril-alexandria-psalms | ps019-rem-mid |  |  | wip/cyril-alexandria-psalms--ps019-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps017-rem-close | free | cyril-alexandria-psalms | ps017-rem-close |  |  | wip/cyril-alexandria-psalms--ps017-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps018-open | free | cyril-alexandria-psalms | ps018-open |  |  | wip/cyril-alexandria-psalms--ps018-open | earliest scaffold |
| cyril-alexandria-psalms--ps018-rem-early | free | cyril-alexandria-psalms | ps018-rem-early |  |  | wip/cyril-alexandria-psalms--ps018-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps018-rem-mid | free | cyril-alexandria-psalms | ps018-rem-mid |  |  | wip/cyril-alexandria-psalms--ps018-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps016-rem-close | free | cyril-alexandria-psalms | ps016-rem-close |  |  | wip/cyril-alexandria-psalms--ps016-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps017-open | free | cyril-alexandria-psalms | ps017-open |  |  | wip/cyril-alexandria-psalms--ps017-open | earliest scaffold |
| cyril-alexandria-psalms--ps017-rem-early | free | cyril-alexandria-psalms | ps017-rem-early |  |  | wip/cyril-alexandria-psalms--ps017-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps017-rem-mid | free | cyril-alexandria-psalms | ps017-rem-mid |  |  | wip/cyril-alexandria-psalms--ps017-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps015-rem-close | free | cyril-alexandria-psalms | ps015-rem-close |  |  | wip/cyril-alexandria-psalms--ps015-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps016-open | free | cyril-alexandria-psalms | ps016-open |  |  | wip/cyril-alexandria-psalms--ps016-open | earliest scaffold |
| cyril-alexandria-psalms--ps016-rem-early | free | cyril-alexandria-psalms | ps016-rem-early |  |  | wip/cyril-alexandria-psalms--ps016-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps016-rem-mid | free | cyril-alexandria-psalms | ps016-rem-mid |  |  | wip/cyril-alexandria-psalms--ps016-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps014-rem-close | free | cyril-alexandria-psalms | ps014-rem-close |  |  | wip/cyril-alexandria-psalms--ps014-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps015-open | free | cyril-alexandria-psalms | ps015-open |  |  | wip/cyril-alexandria-psalms--ps015-open | earliest scaffold |
| cyril-alexandria-psalms--ps015-rem-early | free | cyril-alexandria-psalms | ps015-rem-early |  |  | wip/cyril-alexandria-psalms--ps015-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps015-rem-mid | free | cyril-alexandria-psalms | ps015-rem-mid |  |  | wip/cyril-alexandria-psalms--ps015-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps013-rem-close | free | cyril-alexandria-psalms | ps013-rem-close |  |  | wip/cyril-alexandria-psalms--ps013-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps014-open | free | cyril-alexandria-psalms | ps014-open |  |  | wip/cyril-alexandria-psalms--ps014-open | earliest scaffold |
| cyril-alexandria-psalms--ps014-rem-early | free | cyril-alexandria-psalms | ps014-rem-early |  |  | wip/cyril-alexandria-psalms--ps014-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps014-rem-mid | free | cyril-alexandria-psalms | ps014-rem-mid |  |  | wip/cyril-alexandria-psalms--ps014-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps012-rem-close | free | cyril-alexandria-psalms | ps012-rem-close |  |  | wip/cyril-alexandria-psalms--ps012-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps013-open | free | cyril-alexandria-psalms | ps013-open |  |  | wip/cyril-alexandria-psalms--ps013-open | earliest scaffold |
| cyril-alexandria-psalms--ps013-rem-early | free | cyril-alexandria-psalms | ps013-rem-early |  |  | wip/cyril-alexandria-psalms--ps013-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps013-rem-mid | free | cyril-alexandria-psalms | ps013-rem-mid |  |  | wip/cyril-alexandria-psalms--ps013-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps011-rem-close | free | cyril-alexandria-psalms | ps011-rem-close |  |  | wip/cyril-alexandria-psalms--ps011-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps012-open | free | cyril-alexandria-psalms | ps012-open |  |  | wip/cyril-alexandria-psalms--ps012-open | earliest scaffold |
| cyril-alexandria-psalms--ps012-rem-early | free | cyril-alexandria-psalms | ps012-rem-early |  |  | wip/cyril-alexandria-psalms--ps012-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps012-rem-mid | free | cyril-alexandria-psalms | ps012-rem-mid |  |  | wip/cyril-alexandria-psalms--ps012-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps010-rem-close | free | cyril-alexandria-psalms | ps010-rem-close |  |  | wip/cyril-alexandria-psalms--ps010-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps011-open | free | cyril-alexandria-psalms | ps011-open |  |  | wip/cyril-alexandria-psalms--ps011-open | earliest scaffold |
| cyril-alexandria-psalms--ps011-rem-early | free | cyril-alexandria-psalms | ps011-rem-early |  |  | wip/cyril-alexandria-psalms--ps011-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps011-rem-mid | free | cyril-alexandria-psalms | ps011-rem-mid |  |  | wip/cyril-alexandria-psalms--ps011-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps009-rem-close | free | cyril-alexandria-psalms | ps009-rem-close |  |  | wip/cyril-alexandria-psalms--ps009-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps010-open | free | cyril-alexandria-psalms | ps010-open |  |  | wip/cyril-alexandria-psalms--ps010-open | earliest scaffold |
| cyril-alexandria-psalms--ps010-rem-early | free | cyril-alexandria-psalms | ps010-rem-early |  |  | wip/cyril-alexandria-psalms--ps010-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps010-rem-mid | free | cyril-alexandria-psalms | ps010-rem-mid |  |  | wip/cyril-alexandria-psalms--ps010-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps008-rem-close | free | cyril-alexandria-psalms | ps008-rem-close |  |  | wip/cyril-alexandria-psalms--ps008-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps009-open | free | cyril-alexandria-psalms | ps009-open |  |  | wip/cyril-alexandria-psalms--ps009-open | earliest scaffold |
| cyril-alexandria-psalms--ps009-rem-early | free | cyril-alexandria-psalms | ps009-rem-early |  |  | wip/cyril-alexandria-psalms--ps009-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps009-rem-mid | free | cyril-alexandria-psalms | ps009-rem-mid |  |  | wip/cyril-alexandria-psalms--ps009-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps007-rem-close | free | cyril-alexandria-psalms | ps007-rem-close |  |  | wip/cyril-alexandria-psalms--ps007-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps008-open | free | cyril-alexandria-psalms | ps008-open |  |  | wip/cyril-alexandria-psalms--ps008-open | earliest scaffold |
| cyril-alexandria-psalms--ps008-rem-early | free | cyril-alexandria-psalms | ps008-rem-early |  |  | wip/cyril-alexandria-psalms--ps008-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps008-rem-mid | free | cyril-alexandria-psalms | ps008-rem-mid |  |  | wip/cyril-alexandria-psalms--ps008-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps006-rem-close | free | cyril-alexandria-psalms | ps006-rem-close |  |  | wip/cyril-alexandria-psalms--ps006-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps007-open | free | cyril-alexandria-psalms | ps007-open |  |  | wip/cyril-alexandria-psalms--ps007-open | earliest scaffold |
| cyril-alexandria-psalms--ps007-rem-early | free | cyril-alexandria-psalms | ps007-rem-early |  |  | wip/cyril-alexandria-psalms--ps007-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps007-rem-mid | free | cyril-alexandria-psalms | ps007-rem-mid |  |  | wip/cyril-alexandria-psalms--ps007-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps005-rem-close | free | cyril-alexandria-psalms | ps005-rem-close |  |  | wip/cyril-alexandria-psalms--ps005-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps006-open | free | cyril-alexandria-psalms | ps006-open |  |  | wip/cyril-alexandria-psalms--ps006-open | earliest scaffold |
| cyril-alexandria-psalms--ps006-rem-early | free | cyril-alexandria-psalms | ps006-rem-early |  |  | wip/cyril-alexandria-psalms--ps006-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps006-rem-mid | free | cyril-alexandria-psalms | ps006-rem-mid |  |  | wip/cyril-alexandria-psalms--ps006-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps004-rem-close | free | cyril-alexandria-psalms | ps004-rem-close |  |  | wip/cyril-alexandria-psalms--ps004-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps005-open | free | cyril-alexandria-psalms | ps005-open |  |  | wip/cyril-alexandria-psalms--ps005-open | earliest scaffold |
| cyril-alexandria-psalms--ps005-rem-early | free | cyril-alexandria-psalms | ps005-rem-early |  |  | wip/cyril-alexandria-psalms--ps005-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps005-rem-mid | free | cyril-alexandria-psalms | ps005-rem-mid |  |  | wip/cyril-alexandria-psalms--ps005-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps003-rem-close | free | cyril-alexandria-psalms | ps003-rem-close |  |  | wip/cyril-alexandria-psalms--ps003-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps004-open | free | cyril-alexandria-psalms | ps004-open |  |  | wip/cyril-alexandria-psalms--ps004-open | earliest scaffold |
| cyril-alexandria-psalms--ps004-rem-early | free | cyril-alexandria-psalms | ps004-rem-early |  |  | wip/cyril-alexandria-psalms--ps004-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps004-rem-mid | free | cyril-alexandria-psalms | ps004-rem-mid |  |  | wip/cyril-alexandria-psalms--ps004-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps002-rem-close | free | cyril-alexandria-psalms | ps002-rem-close |  |  | wip/cyril-alexandria-psalms--ps002-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps003-open | free | cyril-alexandria-psalms | ps003-open |  |  | wip/cyril-alexandria-psalms--ps003-open | earliest scaffold |
| cyril-alexandria-psalms--ps003-rem-early | free | cyril-alexandria-psalms | ps003-rem-early |  |  | wip/cyril-alexandria-psalms--ps003-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps003-rem-mid | free | cyril-alexandria-psalms | ps003-rem-mid |  |  | wip/cyril-alexandria-psalms--ps003-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--ps001-rem-close | free | cyril-alexandria-psalms | ps001-rem-close |  |  | wip/cyril-alexandria-psalms--ps001-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps002-open | free | cyril-alexandria-psalms | ps002-open |  |  | wip/cyril-alexandria-psalms--ps002-open | earliest scaffold |
| cyril-alexandria-psalms--ps002-rem-early | free | cyril-alexandria-psalms | ps002-rem-early |  |  | wip/cyril-alexandria-psalms--ps002-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps002-rem-mid | free | cyril-alexandria-psalms | ps002-rem-mid |  |  | wip/cyril-alexandria-psalms--ps002-rem-mid | earliest scaffold |
| cyril-alexandria-psalms--prol-rem-close | free | cyril-alexandria-psalms | prol-rem-close |  |  | wip/cyril-alexandria-psalms--prol-rem-close | earliest scaffold |
| cyril-alexandria-psalms--ps001-open | free | cyril-alexandria-psalms | ps001-open |  |  | wip/cyril-alexandria-psalms--ps001-open | earliest scaffold |
| cyril-alexandria-psalms--ps001-rem-early | free | cyril-alexandria-psalms | ps001-rem-early |  |  | wip/cyril-alexandria-psalms--ps001-rem-early | earliest scaffold |
| cyril-alexandria-psalms--ps001-rem-mid | free | cyril-alexandria-psalms | ps001-rem-mid |  |  | wip/cyril-alexandria-psalms--ps001-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-in-transfigurationem--hom-open | free | cyril-alexandria-lucam-in-transfigurationem | hom-open |  |  | wip/cyril-alexandria-lucam-in-transfigurationem--hom-open | earliest scaffold |
| cyril-alexandria-lucam-in-transfigurationem--hom-rem-early | free | cyril-alexandria-lucam-in-transfigurationem | hom-rem-early |  |  | wip/cyril-alexandria-lucam-in-transfigurationem--hom-rem-early | earliest scaffold |
| cyril-alexandria-lucam-in-transfigurationem--hom-rem-mid | free | cyril-alexandria-lucam-in-transfigurationem | hom-rem-mid |  |  | wip/cyril-alexandria-lucam-in-transfigurationem--hom-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-in-transfigurationem--hom-rem-close | free | cyril-alexandria-lucam-in-transfigurationem | hom-rem-close |  |  | wip/cyril-alexandria-lucam-in-transfigurationem--hom-rem-close | earliest scaffold |
| cyril-alexandria-lucam-in-occursum--hom-open | free | cyril-alexandria-lucam-in-occursum | hom-open |  |  | wip/cyril-alexandria-lucam-in-occursum--hom-open | earliest scaffold |
| cyril-alexandria-lucam-in-occursum--hom-rem-early | free | cyril-alexandria-lucam-in-occursum | hom-rem-early |  |  | wip/cyril-alexandria-lucam-in-occursum--hom-rem-early | earliest scaffold |
| cyril-alexandria-lucam-in-occursum--hom-rem-mid | free | cyril-alexandria-lucam-in-occursum | hom-rem-mid |  |  | wip/cyril-alexandria-lucam-in-occursum--hom-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-in-occursum--hom-rem-close | free | cyril-alexandria-lucam-in-occursum | hom-rem-close |  |  | wip/cyril-alexandria-lucam-in-occursum--hom-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u40-open | free | cyril-alexandria-lucam-fragmenta | u40-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u40-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u40-rem-early | free | cyril-alexandria-lucam-fragmenta | u40-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u40-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u40-rem-mid | free | cyril-alexandria-lucam-fragmenta | u40-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u40-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u40-rem-close | free | cyril-alexandria-lucam-fragmenta | u40-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u40-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u38-open | free | cyril-alexandria-lucam-fragmenta | u38-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u38-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u38-rem-close | free | cyril-alexandria-lucam-fragmenta | u38-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u38-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u39-open | free | cyril-alexandria-lucam-fragmenta | u39-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u39-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u39-rem-close | free | cyril-alexandria-lucam-fragmenta | u39-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u39-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u37-open | free | cyril-alexandria-lucam-fragmenta | u37-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u37-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u37-rem-early | free | cyril-alexandria-lucam-fragmenta | u37-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u37-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u37-rem-mid | free | cyril-alexandria-lucam-fragmenta | u37-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u37-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u37-rem-close | free | cyril-alexandria-lucam-fragmenta | u37-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u37-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u36-open | free | cyril-alexandria-lucam-fragmenta | u36-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u36-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u36-rem-early | free | cyril-alexandria-lucam-fragmenta | u36-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u36-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u36-rem-mid | free | cyril-alexandria-lucam-fragmenta | u36-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u36-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u36-rem-close | free | cyril-alexandria-lucam-fragmenta | u36-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u36-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u35-open | free | cyril-alexandria-lucam-fragmenta | u35-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u35-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u35-rem-early | free | cyril-alexandria-lucam-fragmenta | u35-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u35-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u35-rem-mid | free | cyril-alexandria-lucam-fragmenta | u35-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u35-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u35-rem-close | free | cyril-alexandria-lucam-fragmenta | u35-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u35-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u33-rem-mid | free | cyril-alexandria-lucam-fragmenta | u33-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u33-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u33-rem-close | free | cyril-alexandria-lucam-fragmenta | u33-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u33-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u34-open | free | cyril-alexandria-lucam-fragmenta | u34-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u34-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u34-rem-close | free | cyril-alexandria-lucam-fragmenta | u34-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u34-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u31-rem-close | free | cyril-alexandria-lucam-fragmenta | u31-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u31-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u32-open | free | cyril-alexandria-lucam-fragmenta | u32-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u32-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u33-open | free | cyril-alexandria-lucam-fragmenta | u33-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u33-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u33-rem-early | free | cyril-alexandria-lucam-fragmenta | u33-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u33-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u30-rem-close | free | cyril-alexandria-lucam-fragmenta | u30-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u30-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u31-open | free | cyril-alexandria-lucam-fragmenta | u31-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u31-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u31-rem-early | free | cyril-alexandria-lucam-fragmenta | u31-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u31-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u31-rem-mid | free | cyril-alexandria-lucam-fragmenta | u31-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u31-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u29-rem-close | free | cyril-alexandria-lucam-fragmenta | u29-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u29-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u30-open | free | cyril-alexandria-lucam-fragmenta | u30-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u30-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u30-rem-early | free | cyril-alexandria-lucam-fragmenta | u30-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u30-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u30-rem-mid | free | cyril-alexandria-lucam-fragmenta | u30-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u30-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u28-rem-close | free | cyril-alexandria-lucam-fragmenta | u28-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u28-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u29-open | free | cyril-alexandria-lucam-fragmenta | u29-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u29-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u29-rem-early | free | cyril-alexandria-lucam-fragmenta | u29-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u29-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u29-rem-mid | free | cyril-alexandria-lucam-fragmenta | u29-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u29-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u27-rem-close | free | cyril-alexandria-lucam-fragmenta | u27-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u27-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u28-open | free | cyril-alexandria-lucam-fragmenta | u28-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u28-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u28-rem-early | free | cyril-alexandria-lucam-fragmenta | u28-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u28-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u28-rem-mid | free | cyril-alexandria-lucam-fragmenta | u28-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u28-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u26-rem-close | free | cyril-alexandria-lucam-fragmenta | u26-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u26-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u27-open | free | cyril-alexandria-lucam-fragmenta | u27-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u27-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u27-rem-early | free | cyril-alexandria-lucam-fragmenta | u27-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u27-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u27-rem-mid | free | cyril-alexandria-lucam-fragmenta | u27-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u27-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u25-rem-close | free | cyril-alexandria-lucam-fragmenta | u25-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u25-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u26-open | free | cyril-alexandria-lucam-fragmenta | u26-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u26-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u26-rem-early | free | cyril-alexandria-lucam-fragmenta | u26-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u26-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u26-rem-mid | free | cyril-alexandria-lucam-fragmenta | u26-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u26-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u24-rem-close | free | cyril-alexandria-lucam-fragmenta | u24-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u24-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u25-open | free | cyril-alexandria-lucam-fragmenta | u25-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u25-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u25-rem-early | free | cyril-alexandria-lucam-fragmenta | u25-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u25-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u25-rem-mid | free | cyril-alexandria-lucam-fragmenta | u25-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u25-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u23-rem-close | free | cyril-alexandria-lucam-fragmenta | u23-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u23-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u24-open | free | cyril-alexandria-lucam-fragmenta | u24-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u24-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u24-rem-early | free | cyril-alexandria-lucam-fragmenta | u24-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u24-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u24-rem-mid | free | cyril-alexandria-lucam-fragmenta | u24-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u24-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u22-rem-close | free | cyril-alexandria-lucam-fragmenta | u22-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u22-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u23-open | free | cyril-alexandria-lucam-fragmenta | u23-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u23-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u23-rem-early | free | cyril-alexandria-lucam-fragmenta | u23-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u23-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u23-rem-mid | free | cyril-alexandria-lucam-fragmenta | u23-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u23-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u21-rem-close | free | cyril-alexandria-lucam-fragmenta | u21-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u21-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u22-open | free | cyril-alexandria-lucam-fragmenta | u22-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u22-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u22-rem-early | free | cyril-alexandria-lucam-fragmenta | u22-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u22-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u22-rem-mid | free | cyril-alexandria-lucam-fragmenta | u22-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u22-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u20-open | free | cyril-alexandria-lucam-fragmenta | u20-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u20-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u21-open | free | cyril-alexandria-lucam-fragmenta | u21-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u21-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u21-rem-early | free | cyril-alexandria-lucam-fragmenta | u21-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u21-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u21-rem-mid | free | cyril-alexandria-lucam-fragmenta | u21-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u21-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u19-open | free | cyril-alexandria-lucam-fragmenta | u19-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u19-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u19-rem-early | free | cyril-alexandria-lucam-fragmenta | u19-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u19-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u19-rem-mid | free | cyril-alexandria-lucam-fragmenta | u19-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u19-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u19-rem-close | free | cyril-alexandria-lucam-fragmenta | u19-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u19-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u18-open | free | cyril-alexandria-lucam-fragmenta | u18-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u18-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u18-rem-early | free | cyril-alexandria-lucam-fragmenta | u18-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u18-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u18-rem-mid | free | cyril-alexandria-lucam-fragmenta | u18-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u18-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u18-rem-close | free | cyril-alexandria-lucam-fragmenta | u18-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u18-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u17-open | free | cyril-alexandria-lucam-fragmenta | u17-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u17-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u17-rem-early | free | cyril-alexandria-lucam-fragmenta | u17-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u17-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u17-rem-mid | free | cyril-alexandria-lucam-fragmenta | u17-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u17-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u17-rem-close | free | cyril-alexandria-lucam-fragmenta | u17-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u17-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u16-open | free | cyril-alexandria-lucam-fragmenta | u16-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u16-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u16-rem-early | free | cyril-alexandria-lucam-fragmenta | u16-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u16-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u16-rem-mid | free | cyril-alexandria-lucam-fragmenta | u16-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u16-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u16-rem-close | free | cyril-alexandria-lucam-fragmenta | u16-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u16-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u15-open | free | cyril-alexandria-lucam-fragmenta | u15-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u15-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u15-rem-early | free | cyril-alexandria-lucam-fragmenta | u15-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u15-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u15-rem-mid | free | cyril-alexandria-lucam-fragmenta | u15-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u15-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u15-rem-close | free | cyril-alexandria-lucam-fragmenta | u15-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u15-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u14-open | free | cyril-alexandria-lucam-fragmenta | u14-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u14-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u14-rem-early | free | cyril-alexandria-lucam-fragmenta | u14-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u14-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u14-rem-mid | free | cyril-alexandria-lucam-fragmenta | u14-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u14-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u14-rem-close | free | cyril-alexandria-lucam-fragmenta | u14-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u14-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u12-rem-early | free | cyril-alexandria-lucam-fragmenta | u12-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u12-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u12-rem-mid | free | cyril-alexandria-lucam-fragmenta | u12-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u12-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u12-rem-close | free | cyril-alexandria-lucam-fragmenta | u12-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u12-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u13-open | free | cyril-alexandria-lucam-fragmenta | u13-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u13-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u11-rem-early | free | cyril-alexandria-lucam-fragmenta | u11-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u11-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u11-rem-mid | free | cyril-alexandria-lucam-fragmenta | u11-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u11-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u11-rem-close | free | cyril-alexandria-lucam-fragmenta | u11-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u11-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u12-open | free | cyril-alexandria-lucam-fragmenta | u12-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u12-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u10-rem-early | free | cyril-alexandria-lucam-fragmenta | u10-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u10-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u10-rem-mid | free | cyril-alexandria-lucam-fragmenta | u10-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u10-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u10-rem-close | free | cyril-alexandria-lucam-fragmenta | u10-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u10-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u11-open | free | cyril-alexandria-lucam-fragmenta | u11-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u11-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u08-open | free | cyril-alexandria-lucam-fragmenta | u08-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u08-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u08-rem-close | free | cyril-alexandria-lucam-fragmenta | u08-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u08-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u09-open | free | cyril-alexandria-lucam-fragmenta | u09-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u09-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u10-open | free | cyril-alexandria-lucam-fragmenta | u10-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u10-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u07-open | free | cyril-alexandria-lucam-fragmenta | u07-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u07-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u07-rem-early | free | cyril-alexandria-lucam-fragmenta | u07-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u07-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u07-rem-mid | free | cyril-alexandria-lucam-fragmenta | u07-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u07-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u07-rem-close | free | cyril-alexandria-lucam-fragmenta | u07-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u07-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u05-rem-mid | free | cyril-alexandria-lucam-fragmenta | u05-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u05-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u05-rem-close | free | cyril-alexandria-lucam-fragmenta | u05-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u05-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u06-open | free | cyril-alexandria-lucam-fragmenta | u06-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u06-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u06-rem-close | free | cyril-alexandria-lucam-fragmenta | u06-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u06-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u03-rem-close | free | cyril-alexandria-lucam-fragmenta | u03-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u03-rem-close | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u04-open | free | cyril-alexandria-lucam-fragmenta | u04-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u04-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u05-open | free | cyril-alexandria-lucam-fragmenta | u05-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u05-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u05-rem-early | free | cyril-alexandria-lucam-fragmenta | u05-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u05-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u02-open | free | cyril-alexandria-lucam-fragmenta | u02-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u02-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u03-open | free | cyril-alexandria-lucam-fragmenta | u03-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u03-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u03-rem-early | free | cyril-alexandria-lucam-fragmenta | u03-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u03-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u03-rem-mid | free | cyril-alexandria-lucam-fragmenta | u03-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u03-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u01-open | free | cyril-alexandria-lucam-fragmenta | u01-open |  |  | wip/cyril-alexandria-lucam-fragmenta--u01-open | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u01-rem-early | free | cyril-alexandria-lucam-fragmenta | u01-rem-early |  |  | wip/cyril-alexandria-lucam-fragmenta--u01-rem-early | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u01-rem-mid | free | cyril-alexandria-lucam-fragmenta | u01-rem-mid |  |  | wip/cyril-alexandria-lucam-fragmenta--u01-rem-mid | earliest scaffold |
| cyril-alexandria-lucam-fragmenta--u01-rem-close | free | cyril-alexandria-lucam-fragmenta | u01-rem-close |  |  | wip/cyril-alexandria-lucam-fragmenta--u01-rem-close | earliest scaffold |
| cyril-alexandria-in-parabolam-vineae--hom-open | free | cyril-alexandria-in-parabolam-vineae | hom-open |  |  | wip/cyril-alexandria-in-parabolam-vineae--hom-open | earliest scaffold |
| cyril-alexandria-in-parabolam-vineae--hom-rem-early | free | cyril-alexandria-in-parabolam-vineae | hom-rem-early |  |  | wip/cyril-alexandria-in-parabolam-vineae--hom-rem-early | earliest scaffold |
| cyril-alexandria-in-parabolam-vineae--hom-rem-mid | free | cyril-alexandria-in-parabolam-vineae | hom-rem-mid |  |  | wip/cyril-alexandria-in-parabolam-vineae--hom-rem-mid | earliest scaffold |
| cyril-alexandria-in-parabolam-vineae--hom-rem-close | free | cyril-alexandria-in-parabolam-vineae | hom-rem-close |  |  | wip/cyril-alexandria-in-parabolam-vineae--hom-rem-close | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--sxv-open | free | cyril-alexandria-homiliarum-incertarum | sxv-open |  |  | wip/cyril-alexandria-homiliarum-incertarum--sxv-open | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--sxv-rem-early | free | cyril-alexandria-homiliarum-incertarum | sxv-rem-early |  |  | wip/cyril-alexandria-homiliarum-incertarum--sxv-rem-early | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--sxv-rem-mid | free | cyril-alexandria-homiliarum-incertarum | sxv-rem-mid |  |  | wip/cyril-alexandria-homiliarum-incertarum--sxv-rem-mid | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--sxv-rem-close | free | cyril-alexandria-homiliarum-incertarum | sxv-rem-close |  |  | wip/cyril-alexandria-homiliarum-incertarum--sxv-rem-close | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--sxiv-open | free | cyril-alexandria-homiliarum-incertarum | sxiv-open |  |  | wip/cyril-alexandria-homiliarum-incertarum--sxiv-open | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--sxiv-rem-early | free | cyril-alexandria-homiliarum-incertarum | sxiv-rem-early |  |  | wip/cyril-alexandria-homiliarum-incertarum--sxiv-rem-early | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--sxiv-rem-mid | free | cyril-alexandria-homiliarum-incertarum | sxiv-rem-mid |  |  | wip/cyril-alexandria-homiliarum-incertarum--sxiv-rem-mid | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--sxiv-rem-close | free | cyril-alexandria-homiliarum-incertarum | sxiv-rem-close |  |  | wip/cyril-alexandria-homiliarum-incertarum--sxiv-rem-close | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--sxiii-open | free | cyril-alexandria-homiliarum-incertarum | sxiii-open |  |  | wip/cyril-alexandria-homiliarum-incertarum--sxiii-open | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--sxiii-rem-early | free | cyril-alexandria-homiliarum-incertarum | sxiii-rem-early |  |  | wip/cyril-alexandria-homiliarum-incertarum--sxiii-rem-early | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--sxiii-rem-mid | free | cyril-alexandria-homiliarum-incertarum | sxiii-rem-mid |  |  | wip/cyril-alexandria-homiliarum-incertarum--sxiii-rem-mid | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--sxiii-rem-close | free | cyril-alexandria-homiliarum-incertarum | sxiii-rem-close |  |  | wip/cyril-alexandria-homiliarum-incertarum--sxiii-rem-close | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--sx-rem-close | free | cyril-alexandria-homiliarum-incertarum | sx-rem-close |  |  | wip/cyril-alexandria-homiliarum-incertarum--sx-rem-close | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--sxi-open | free | cyril-alexandria-homiliarum-incertarum | sxi-open |  |  | wip/cyril-alexandria-homiliarum-incertarum--sxi-open | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--sxii-open | free | cyril-alexandria-homiliarum-incertarum | sxii-open |  |  | wip/cyril-alexandria-homiliarum-incertarum--sxii-open | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--sxii-rem-close | free | cyril-alexandria-homiliarum-incertarum | sxii-rem-close |  |  | wip/cyril-alexandria-homiliarum-incertarum--sxii-rem-close | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--sviii-rem-close | free | cyril-alexandria-homiliarum-incertarum | sviii-rem-close |  |  | wip/cyril-alexandria-homiliarum-incertarum--sviii-rem-close | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--sx-open | free | cyril-alexandria-homiliarum-incertarum | sx-open |  |  | wip/cyril-alexandria-homiliarum-incertarum--sx-open | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--sx-rem-early | free | cyril-alexandria-homiliarum-incertarum | sx-rem-early |  |  | wip/cyril-alexandria-homiliarum-incertarum--sx-rem-early | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--sx-rem-mid | free | cyril-alexandria-homiliarum-incertarum | sx-rem-mid |  |  | wip/cyril-alexandria-homiliarum-incertarum--sx-rem-mid | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--svii-open | free | cyril-alexandria-homiliarum-incertarum | svii-open |  |  | wip/cyril-alexandria-homiliarum-incertarum--svii-open | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--sviii-open | free | cyril-alexandria-homiliarum-incertarum | sviii-open |  |  | wip/cyril-alexandria-homiliarum-incertarum--sviii-open | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--sviii-rem-early | free | cyril-alexandria-homiliarum-incertarum | sviii-rem-early |  |  | wip/cyril-alexandria-homiliarum-incertarum--sviii-rem-early | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--sviii-rem-mid | free | cyril-alexandria-homiliarum-incertarum | sviii-rem-mid |  |  | wip/cyril-alexandria-homiliarum-incertarum--sviii-rem-mid | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--svi-open | free | cyril-alexandria-homiliarum-incertarum | svi-open |  |  | wip/cyril-alexandria-homiliarum-incertarum--svi-open | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--svi-rem-early | free | cyril-alexandria-homiliarum-incertarum | svi-rem-early |  |  | wip/cyril-alexandria-homiliarum-incertarum--svi-rem-early | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--svi-rem-mid | free | cyril-alexandria-homiliarum-incertarum | svi-rem-mid |  |  | wip/cyril-alexandria-homiliarum-incertarum--svi-rem-mid | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--svi-rem-close | free | cyril-alexandria-homiliarum-incertarum | svi-rem-close |  |  | wip/cyril-alexandria-homiliarum-incertarum--svi-rem-close | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--six-open | free | cyril-alexandria-homiliarum-incertarum | six-open |  |  | wip/cyril-alexandria-homiliarum-incertarum--six-open | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--six-rem-early | free | cyril-alexandria-homiliarum-incertarum | six-rem-early |  |  | wip/cyril-alexandria-homiliarum-incertarum--six-rem-early | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--six-rem-mid | free | cyril-alexandria-homiliarum-incertarum | six-rem-mid |  |  | wip/cyril-alexandria-homiliarum-incertarum--six-rem-mid | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--six-rem-close | free | cyril-alexandria-homiliarum-incertarum | six-rem-close |  |  | wip/cyril-alexandria-homiliarum-incertarum--six-rem-close | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--pref-open | free | cyril-alexandria-homiliarum-incertarum | pref-open |  |  | wip/cyril-alexandria-homiliarum-incertarum--pref-open | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--pref-rem-early | free | cyril-alexandria-homiliarum-incertarum | pref-rem-early |  |  | wip/cyril-alexandria-homiliarum-incertarum--pref-rem-early | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--pref-rem-mid | free | cyril-alexandria-homiliarum-incertarum | pref-rem-mid |  |  | wip/cyril-alexandria-homiliarum-incertarum--pref-rem-mid | earliest scaffold |
| cyril-alexandria-homiliarum-incertarum--pref-rem-close | free | cyril-alexandria-homiliarum-incertarum | pref-rem-close |  |  | wip/cyril-alexandria-homiliarum-incertarum--pref-rem-close | earliest scaffold |
| cyril-alexandria-homilia-cyrini--hom-open | free | cyril-alexandria-homilia-cyrini | hom-open |  |  | wip/cyril-alexandria-homilia-cyrini--hom-open | earliest scaffold |
| cyril-alexandria-homilia-cyrini--hom-rem-early | free | cyril-alexandria-homilia-cyrini | hom-rem-early |  |  | wip/cyril-alexandria-homilia-cyrini--hom-rem-early | earliest scaffold |
| cyril-alexandria-homilia-cyrini--hom-rem-mid | free | cyril-alexandria-homilia-cyrini | hom-rem-mid |  |  | wip/cyril-alexandria-homilia-cyrini--hom-rem-mid | earliest scaffold |
| cyril-alexandria-homilia-cyrini--hom-rem-close | free | cyril-alexandria-homilia-cyrini | hom-rem-close |  |  | wip/cyril-alexandria-homilia-cyrini--hom-rem-close | earliest scaffold |
| cyril-alexandria-glaphyra--noah-ham-rem-close | free | cyril-alexandria-glaphyra | noah-ham-rem-close |  |  | wip/cyril-alexandria-glaphyra--noah-ham-rem-close | earliest scaffold |
| cyril-alexandria-glaphyra--num-rem-early | free | cyril-alexandria-glaphyra | num-rem-early |  |  | wip/cyril-alexandria-glaphyra--num-rem-early | earliest scaffold |
| cyril-alexandria-glaphyra--num-rem-mid | free | cyril-alexandria-glaphyra | num-rem-mid |  |  | wip/cyril-alexandria-glaphyra--num-rem-mid | earliest scaffold |
| cyril-alexandria-glaphyra--num-rem-close | free | cyril-alexandria-glaphyra | num-rem-close |  |  | wip/cyril-alexandria-glaphyra--num-rem-close | earliest scaffold |
| cyril-alexandria-glaphyra--noah-ark-rem-mid | free | cyril-alexandria-glaphyra | noah-ark-rem-mid |  |  | wip/cyril-alexandria-glaphyra--noah-ark-rem-mid | earliest scaffold |
| cyril-alexandria-glaphyra--noah-ark-rem-close | free | cyril-alexandria-glaphyra | noah-ark-rem-close |  |  | wip/cyril-alexandria-glaphyra--noah-ark-rem-close | earliest scaffold |
| cyril-alexandria-glaphyra--noah-ham-rem-early | free | cyril-alexandria-glaphyra | noah-ham-rem-early |  |  | wip/cyril-alexandria-glaphyra--noah-ham-rem-early | earliest scaffold |
| cyril-alexandria-glaphyra--noah-ham-rem-mid | free | cyril-alexandria-glaphyra | noah-ham-rem-mid |  |  | wip/cyril-alexandria-glaphyra--noah-ham-rem-mid | earliest scaffold |
| cyril-alexandria-glaphyra--lev-rem-early | free | cyril-alexandria-glaphyra | lev-rem-early |  |  | wip/cyril-alexandria-glaphyra--lev-rem-early | earliest scaffold |
| cyril-alexandria-glaphyra--lev-rem-mid | free | cyril-alexandria-glaphyra | lev-rem-mid |  |  | wip/cyril-alexandria-glaphyra--lev-rem-mid | earliest scaffold |
| cyril-alexandria-glaphyra--lev-rem-close | free | cyril-alexandria-glaphyra | lev-rem-close |  |  | wip/cyril-alexandria-glaphyra--lev-rem-close | earliest scaffold |
| cyril-alexandria-glaphyra--noah-ark-rem-early | free | cyril-alexandria-glaphyra | noah-ark-rem-early |  |  | wip/cyril-alexandria-glaphyra--noah-ark-rem-early | earliest scaffold |
| cyril-alexandria-glaphyra--gen-b6-rem-close | free | cyril-alexandria-glaphyra | gen-b6-rem-close |  |  | wip/cyril-alexandria-glaphyra--gen-b6-rem-close | earliest scaffold |
| cyril-alexandria-glaphyra--gen-b7-rem-early | free | cyril-alexandria-glaphyra | gen-b7-rem-early |  |  | wip/cyril-alexandria-glaphyra--gen-b7-rem-early | earliest scaffold |
| cyril-alexandria-glaphyra--gen-b7-rem-mid | free | cyril-alexandria-glaphyra | gen-b7-rem-mid |  |  | wip/cyril-alexandria-glaphyra--gen-b7-rem-mid | earliest scaffold |
| cyril-alexandria-glaphyra--gen-b7-rem-close | free | cyril-alexandria-glaphyra | gen-b7-rem-close |  |  | wip/cyril-alexandria-glaphyra--gen-b7-rem-close | earliest scaffold |
| cyril-alexandria-glaphyra--gen-b5-rem-mid | free | cyril-alexandria-glaphyra | gen-b5-rem-mid |  |  | wip/cyril-alexandria-glaphyra--gen-b5-rem-mid | earliest scaffold |

| cyril-alexandria-glaphyra--gen-b6-rem-mid | free | cyril-alexandria-glaphyra | gen-b6-rem-mid |  |  | wip/cyril-alexandria-glaphyra--gen-b6-rem-mid | earliest scaffold |

| cyril-alexandria-glaphyra--gen-b4-rem-mid | free | cyril-alexandria-glaphyra | gen-b4-rem-mid |  |  | wip/cyril-alexandria-glaphyra--gen-b4-rem-mid | earliest scaffold |

| cyril-alexandria-glaphyra--gen-b3-rem-early | free | cyril-alexandria-glaphyra | gen-b3-rem-early |  |  | wip/cyril-alexandria-glaphyra--gen-b3-rem-early | earliest scaffold |

| cyril-alexandria-glaphyra--exod-b3-rem-early | free | cyril-alexandria-glaphyra | exod-b3-rem-early |  |  | wip/cyril-alexandria-glaphyra--exod-b3-rem-early | earliest scaffold |

| cyril-alexandria-glaphyra--exod-b1-rem-early | free | cyril-alexandria-glaphyra | exod-b1-rem-early |  |  | wip/cyril-alexandria-glaphyra--exod-b1-rem-early | earliest scaffold |

| cyril-alexandria-glaphyra--book1-cain-abel-rem-close | free | cyril-alexandria-glaphyra | book1-cain-abel-rem-close |  |  | wip/cyril-alexandria-glaphyra--book1-cain-abel-rem-close | earliest scaffold |
| cyril-alexandria-glaphyra--deut-rem-early | free | cyril-alexandria-glaphyra | deut-rem-early |  |  | wip/cyril-alexandria-glaphyra--deut-rem-early | earliest scaffold |
| cyril-alexandria-glaphyra--deut-rem-mid | free | cyril-alexandria-glaphyra | deut-rem-mid |  |  | wip/cyril-alexandria-glaphyra--deut-rem-mid | earliest scaffold |
| cyril-alexandria-glaphyra--deut-rem-close | free | cyril-alexandria-glaphyra | deut-rem-close |  |  | wip/cyril-alexandria-glaphyra--deut-rem-close | earliest scaffold |
| cyril-alexandria-glaphyra--book1-adam-rem-mid | free | cyril-alexandria-glaphyra | book1-adam-rem-mid |  |  | wip/cyril-alexandria-glaphyra--book1-adam-rem-mid | earliest scaffold |
| cyril-alexandria-glaphyra--book1-adam-rem-close | free | cyril-alexandria-glaphyra | book1-adam-rem-close |  |  | wip/cyril-alexandria-glaphyra--book1-adam-rem-close | earliest scaffold |

| cyril-alexandria-glaphyra--abraham-melchizedek-rem-early | free | cyril-alexandria-glaphyra | abraham-melchizedek-rem-early |  |  | wip/cyril-alexandria-glaphyra--abraham-melchizedek-rem-early | earliest scaffold |
| cyril-alexandria-glaphyra--abraham-melchizedek-rem-mid | free | cyril-alexandria-glaphyra | abraham-melchizedek-rem-mid |  |  | wip/cyril-alexandria-glaphyra--abraham-melchizedek-rem-mid | earliest scaffold |
| cyril-alexandria-glaphyra--abraham-melchizedek-rem-close | free | cyril-alexandria-glaphyra | abraham-melchizedek-rem-close |  |  | wip/cyril-alexandria-glaphyra--abraham-melchizedek-rem-close | earliest scaffold |
| cyril-alexandria-glaphyra--book1-adam-rem-early | free | cyril-alexandria-glaphyra | book1-adam-rem-early |  |  | wip/cyril-alexandria-glaphyra--book1-adam-rem-early | earliest scaffold |
| cyril-alexandria-fragmentum-psalmum--frag-open | free | cyril-alexandria-fragmentum-psalmum | frag-open |  |  | wip/cyril-alexandria-fragmentum-psalmum--frag-open | earliest scaffold |
| cyril-alexandria-fragmentum-psalmum--frag-rem-early | free | cyril-alexandria-fragmentum-psalmum | frag-rem-early |  |  | wip/cyril-alexandria-fragmentum-psalmum--frag-rem-early | earliest scaffold |
| cyril-alexandria-fragmentum-psalmum--frag-rem-mid | free | cyril-alexandria-fragmentum-psalmum | frag-rem-mid |  |  | wip/cyril-alexandria-fragmentum-psalmum--frag-rem-mid | earliest scaffold |
| cyril-alexandria-fragmentum-psalmum--frag-rem-close | free | cyril-alexandria-fragmentum-psalmum | frag-rem-close |  |  | wip/cyril-alexandria-fragmentum-psalmum--frag-rem-close | earliest scaffold |
| cyril-alexandria-fragmentum-papyraceum--frag-open | free | cyril-alexandria-fragmentum-papyraceum | frag-open |  |  | wip/cyril-alexandria-fragmentum-papyraceum--frag-open | earliest scaffold |
| cyril-alexandria-fragmentum-papyraceum--frag-rem-early | free | cyril-alexandria-fragmentum-papyraceum | frag-rem-early |  |  | wip/cyril-alexandria-fragmentum-papyraceum--frag-rem-early | earliest scaffold |
| cyril-alexandria-fragmentum-papyraceum--frag-rem-mid | free | cyril-alexandria-fragmentum-papyraceum | frag-rem-mid |  |  | wip/cyril-alexandria-fragmentum-papyraceum--frag-rem-mid | earliest scaffold |
| cyril-alexandria-fragmentum-papyraceum--frag-rem-close | free | cyril-alexandria-fragmentum-papyraceum | frag-rem-close |  |  | wip/cyril-alexandria-fragmentum-papyraceum--frag-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u11-open | free | cyril-alexandria-fragmenta-romanos | u11-open |  |  | wip/cyril-alexandria-fragmenta-romanos--u11-open | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u11-rem-early | free | cyril-alexandria-fragmenta-romanos | u11-rem-early |  |  | wip/cyril-alexandria-fragmenta-romanos--u11-rem-early | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u11-rem-mid | free | cyril-alexandria-fragmenta-romanos | u11-rem-mid |  |  | wip/cyril-alexandria-fragmenta-romanos--u11-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u11-rem-close | free | cyril-alexandria-fragmenta-romanos | u11-rem-close |  |  | wip/cyril-alexandria-fragmenta-romanos--u11-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u10-open | free | cyril-alexandria-fragmenta-romanos | u10-open |  |  | wip/cyril-alexandria-fragmenta-romanos--u10-open | earliest scaffold |

| cyril-alexandria-fragmenta-romanos--u10-rem-mid | free | cyril-alexandria-fragmenta-romanos | u10-rem-mid |  |  | wip/cyril-alexandria-fragmenta-romanos--u10-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u10-rem-close | free | cyril-alexandria-fragmenta-romanos | u10-rem-close |  |  | wip/cyril-alexandria-fragmenta-romanos--u10-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u09-open | free | cyril-alexandria-fragmenta-romanos | u09-open |  |  | wip/cyril-alexandria-fragmenta-romanos--u09-open | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u09-rem-early | free | cyril-alexandria-fragmenta-romanos | u09-rem-early |  |  | wip/cyril-alexandria-fragmenta-romanos--u09-rem-early | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u09-rem-mid | free | cyril-alexandria-fragmenta-romanos | u09-rem-mid |  |  | wip/cyril-alexandria-fragmenta-romanos--u09-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u09-rem-close | free | cyril-alexandria-fragmenta-romanos | u09-rem-close |  |  | wip/cyril-alexandria-fragmenta-romanos--u09-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u08-open | free | cyril-alexandria-fragmenta-romanos | u08-open |  |  | wip/cyril-alexandria-fragmenta-romanos--u08-open | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u08-rem-early | free | cyril-alexandria-fragmenta-romanos | u08-rem-early |  |  | wip/cyril-alexandria-fragmenta-romanos--u08-rem-early | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u08-rem-mid | free | cyril-alexandria-fragmenta-romanos | u08-rem-mid |  |  | wip/cyril-alexandria-fragmenta-romanos--u08-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u08-rem-close | free | cyril-alexandria-fragmenta-romanos | u08-rem-close |  |  | wip/cyril-alexandria-fragmenta-romanos--u08-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u07-open | free | cyril-alexandria-fragmenta-romanos | u07-open |  |  | wip/cyril-alexandria-fragmenta-romanos--u07-open | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u07-rem-early | free | cyril-alexandria-fragmenta-romanos | u07-rem-early |  |  | wip/cyril-alexandria-fragmenta-romanos--u07-rem-early | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u07-rem-mid | free | cyril-alexandria-fragmenta-romanos | u07-rem-mid |  |  | wip/cyril-alexandria-fragmenta-romanos--u07-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u07-rem-close | free | cyril-alexandria-fragmenta-romanos | u07-rem-close |  |  | wip/cyril-alexandria-fragmenta-romanos--u07-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u06-open | free | cyril-alexandria-fragmenta-romanos | u06-open |  |  | wip/cyril-alexandria-fragmenta-romanos--u06-open | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u06-rem-early | free | cyril-alexandria-fragmenta-romanos | u06-rem-early |  |  | wip/cyril-alexandria-fragmenta-romanos--u06-rem-early | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u06-rem-mid | free | cyril-alexandria-fragmenta-romanos | u06-rem-mid |  |  | wip/cyril-alexandria-fragmenta-romanos--u06-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u06-rem-close | free | cyril-alexandria-fragmenta-romanos | u06-rem-close |  |  | wip/cyril-alexandria-fragmenta-romanos--u06-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u05-open | free | cyril-alexandria-fragmenta-romanos | u05-open |  |  | wip/cyril-alexandria-fragmenta-romanos--u05-open | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u05-rem-early | free | cyril-alexandria-fragmenta-romanos | u05-rem-early |  |  | wip/cyril-alexandria-fragmenta-romanos--u05-rem-early | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u05-rem-mid | free | cyril-alexandria-fragmenta-romanos | u05-rem-mid |  |  | wip/cyril-alexandria-fragmenta-romanos--u05-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u05-rem-close | free | cyril-alexandria-fragmenta-romanos | u05-rem-close |  |  | wip/cyril-alexandria-fragmenta-romanos--u05-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u04-open | free | cyril-alexandria-fragmenta-romanos | u04-open |  |  | wip/cyril-alexandria-fragmenta-romanos--u04-open | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u04-rem-early | free | cyril-alexandria-fragmenta-romanos | u04-rem-early |  |  | wip/cyril-alexandria-fragmenta-romanos--u04-rem-early | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u04-rem-mid | free | cyril-alexandria-fragmenta-romanos | u04-rem-mid |  |  | wip/cyril-alexandria-fragmenta-romanos--u04-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u04-rem-close | free | cyril-alexandria-fragmenta-romanos | u04-rem-close |  |  | wip/cyril-alexandria-fragmenta-romanos--u04-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u03-open | free | cyril-alexandria-fragmenta-romanos | u03-open |  |  | wip/cyril-alexandria-fragmenta-romanos--u03-open | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u03-rem-early | free | cyril-alexandria-fragmenta-romanos | u03-rem-early |  |  | wip/cyril-alexandria-fragmenta-romanos--u03-rem-early | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u03-rem-mid | free | cyril-alexandria-fragmenta-romanos | u03-rem-mid |  |  | wip/cyril-alexandria-fragmenta-romanos--u03-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u03-rem-close | free | cyril-alexandria-fragmenta-romanos | u03-rem-close |  |  | wip/cyril-alexandria-fragmenta-romanos--u03-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u02-open | free | cyril-alexandria-fragmenta-romanos | u02-open |  |  | wip/cyril-alexandria-fragmenta-romanos--u02-open | earliest scaffold |

| cyril-alexandria-fragmenta-romanos--u02-rem-mid | free | cyril-alexandria-fragmenta-romanos | u02-rem-mid |  |  | wip/cyril-alexandria-fragmenta-romanos--u02-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u02-rem-close | free | cyril-alexandria-fragmenta-romanos | u02-rem-close |  |  | wip/cyril-alexandria-fragmenta-romanos--u02-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u01-open | free | cyril-alexandria-fragmenta-romanos | u01-open |  |  | wip/cyril-alexandria-fragmenta-romanos--u01-open | earliest scaffold |
| cyril-alexandria-fragmenta-romanos--u01-rem-early | free | cyril-alexandria-fragmenta-romanos | u01-rem-early |  |  | wip/cyril-alexandria-fragmenta-romanos--u01-rem-early | earliest scaffold |

| cyril-alexandria-fragmenta-regum--b03-rem-early | free | cyril-alexandria-fragmenta-regum | b03-rem-early |  |  | wip/cyril-alexandria-fragmenta-regum--b03-rem-early | earliest scaffold |

| cyril-alexandria-fragmenta-regum--b02-open | free | cyril-alexandria-fragmenta-regum | b02-open |  |  | wip/cyril-alexandria-fragmenta-regum--b02-open | earliest scaffold |
| cyril-alexandria-fragmenta-regum--b02-rem-early | free | cyril-alexandria-fragmenta-regum | b02-rem-early |  |  | wip/cyril-alexandria-fragmenta-regum--b02-rem-early | earliest scaffold |
| cyril-alexandria-fragmenta-regum--b02-rem-mid | free | cyril-alexandria-fragmenta-regum | b02-rem-mid |  |  | wip/cyril-alexandria-fragmenta-regum--b02-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-regum--b02-rem-close | free | cyril-alexandria-fragmenta-regum | b02-rem-close |  |  | wip/cyril-alexandria-fragmenta-regum--b02-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-regum--b01-open | free | cyril-alexandria-fragmenta-regum | b01-open |  |  | wip/cyril-alexandria-fragmenta-regum--b01-open | earliest scaffold |
| cyril-alexandria-fragmenta-regum--b01-rem-early | free | cyril-alexandria-fragmenta-regum | b01-rem-early |  |  | wip/cyril-alexandria-fragmenta-regum--b01-rem-early | earliest scaffold |
| cyril-alexandria-fragmenta-regum--b01-rem-mid | free | cyril-alexandria-fragmenta-regum | b01-rem-mid |  |  | wip/cyril-alexandria-fragmenta-regum--b01-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-regum--b01-rem-close | free | cyril-alexandria-fragmenta-regum | b01-rem-close |  |  | wip/cyril-alexandria-fragmenta-regum--b01-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-numeros--frag-open | free | cyril-alexandria-fragmenta-numeros | frag-open |  |  | wip/cyril-alexandria-fragmenta-numeros--frag-open | earliest scaffold |

| cyril-alexandria-fragmenta-numeros--frag-rem-mid | free | cyril-alexandria-fragmenta-numeros | frag-rem-mid |  |  | wip/cyril-alexandria-fragmenta-numeros--frag-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-numeros--frag-rem-close | free | cyril-alexandria-fragmenta-numeros | frag-rem-close |  |  | wip/cyril-alexandria-fragmenta-numeros--frag-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-jeremiam--frag-open | free | cyril-alexandria-fragmenta-jeremiam | frag-open |  |  | wip/cyril-alexandria-fragmenta-jeremiam--frag-open | earliest scaffold |
| cyril-alexandria-fragmenta-jeremiam--frag-rem-early | free | cyril-alexandria-fragmenta-jeremiam | frag-rem-early |  |  | wip/cyril-alexandria-fragmenta-jeremiam--frag-rem-early | earliest scaffold |
| cyril-alexandria-fragmenta-jeremiam--frag-rem-mid | free | cyril-alexandria-fragmenta-jeremiam | frag-rem-mid |  |  | wip/cyril-alexandria-fragmenta-jeremiam--frag-rem-mid | earliest scaffold |

| cyril-alexandria-fragmenta-homiliae-unus--frag-open | free | cyril-alexandria-fragmenta-homiliae-unus | frag-open |  |  | wip/cyril-alexandria-fragmenta-homiliae-unus--frag-open | earliest scaffold |
| cyril-alexandria-fragmenta-homiliae-unus--frag-rem-early | free | cyril-alexandria-fragmenta-homiliae-unus | frag-rem-early |  |  | wip/cyril-alexandria-fragmenta-homiliae-unus--frag-rem-early | earliest scaffold |
| cyril-alexandria-fragmenta-homiliae-unus--frag-rem-mid | free | cyril-alexandria-fragmenta-homiliae-unus | frag-rem-mid |  |  | wip/cyril-alexandria-fragmenta-homiliae-unus--frag-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-homiliae-unus--frag-rem-close | free | cyril-alexandria-fragmenta-homiliae-unus | frag-rem-close |  |  | wip/cyril-alexandria-fragmenta-homiliae-unus--frag-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-hebraeos--u08-open | free | cyril-alexandria-fragmenta-hebraeos | u08-open |  |  | wip/cyril-alexandria-fragmenta-hebraeos--u08-open | earliest scaffold |

| cyril-alexandria-fragmenta-hebraeos--u07-rem-mid | free | cyril-alexandria-fragmenta-hebraeos | u07-rem-mid |  |  | wip/cyril-alexandria-fragmenta-hebraeos--u07-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-hebraeos--u07-rem-close | free | cyril-alexandria-fragmenta-hebraeos | u07-rem-close |  |  | wip/cyril-alexandria-fragmenta-hebraeos--u07-rem-close | earliest scaffold |

| cyril-alexandria-fragmenta-hebraeos--u06-rem-mid | free | cyril-alexandria-fragmenta-hebraeos | u06-rem-mid |  |  | wip/cyril-alexandria-fragmenta-hebraeos--u06-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-hebraeos--u06-rem-close | free | cyril-alexandria-fragmenta-hebraeos | u06-rem-close |  |  | wip/cyril-alexandria-fragmenta-hebraeos--u06-rem-close | earliest scaffold |

| cyril-alexandria-fragmenta-hebraeos--u05-rem-early | free | cyril-alexandria-fragmenta-hebraeos | u05-rem-early |  |  | wip/cyril-alexandria-fragmenta-hebraeos--u05-rem-early | earliest scaffold |

| cyril-alexandria-fragmenta-hebraeos--u04-rem-early | free | cyril-alexandria-fragmenta-hebraeos | u04-rem-early |  |  | wip/cyril-alexandria-fragmenta-hebraeos--u04-rem-early | earliest scaffold |
| cyril-alexandria-fragmenta-hebraeos--u04-rem-mid | free | cyril-alexandria-fragmenta-hebraeos | u04-rem-mid |  |  | wip/cyril-alexandria-fragmenta-hebraeos--u04-rem-mid | earliest scaffold |

| cyril-alexandria-fragmenta-hebraeos--u02-rem-mid | free | cyril-alexandria-fragmenta-hebraeos | u02-rem-mid |  |  | wip/cyril-alexandria-fragmenta-hebraeos--u02-rem-mid | earliest scaffold |

| didymus-commentarii-octateuchum--u01-rem-mid | free | didymus-commentarii-octateuchum | u01-rem-mid |  |  | wip/didymus-commentarii-octateuchum--u01-rem-mid | earliest scaffold |

| cyril-alexandria-fragmenta-ezechielem--frag-rem-mid | free | cyril-alexandria-fragmenta-ezechielem | frag-rem-mid |  |  | wip/cyril-alexandria-fragmenta-ezechielem--frag-rem-mid | earliest scaffold |

| cyril-alexandria-fragmenta-de-uno-filio--frag-rem-mid | free | cyril-alexandria-fragmenta-de-uno-filio | frag-rem-mid |  |  | wip/cyril-alexandria-fragmenta-de-uno-filio--frag-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-de-uno-filio--frag-rem-close | free | cyril-alexandria-fragmenta-de-uno-filio | frag-rem-close |  |  | wip/cyril-alexandria-fragmenta-de-uno-filio--frag-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-ezechielem--frag-open | free | cyril-alexandria-fragmenta-ezechielem | frag-open |  |  | wip/cyril-alexandria-fragmenta-ezechielem--frag-open | earliest scaffold |
| cyril-alexandria-fragmenta-ezechielem--frag-rem-early | free | cyril-alexandria-fragmenta-ezechielem | frag-rem-early |  |  | wip/cyril-alexandria-fragmenta-ezechielem--frag-rem-early | earliest scaffold |
| cyril-alexandria-fragmenta-danielem--frag-open | free | cyril-alexandria-fragmenta-danielem | frag-open |  |  | wip/cyril-alexandria-fragmenta-danielem--frag-open | earliest scaffold |
| cyril-alexandria-fragmenta-danielem--frag-rem-close | free | cyril-alexandria-fragmenta-danielem | frag-rem-close |  |  | wip/cyril-alexandria-fragmenta-danielem--frag-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-de-uno-filio--frag-open | free | cyril-alexandria-fragmenta-de-uno-filio | frag-open |  |  | wip/cyril-alexandria-fragmenta-de-uno-filio--frag-open | earliest scaffold |
| cyril-alexandria-fragmenta-de-uno-filio--frag-rem-early | free | cyril-alexandria-fragmenta-de-uno-filio | frag-rem-early |  |  | wip/cyril-alexandria-fragmenta-de-uno-filio--frag-rem-early | earliest scaffold |
| cyril-alexandria-fragmenta-cyri-joannis--frag-open | free | cyril-alexandria-fragmenta-cyri-joannis | frag-open |  |  | wip/cyril-alexandria-fragmenta-cyri-joannis--frag-open | earliest scaffold |
| cyril-alexandria-fragmenta-cyri-joannis--frag-rem-early | free | cyril-alexandria-fragmenta-cyri-joannis | frag-rem-early |  |  | wip/cyril-alexandria-fragmenta-cyri-joannis--frag-rem-early | earliest scaffold |
| cyril-alexandria-fragmenta-cyri-joannis--frag-rem-mid | free | cyril-alexandria-fragmenta-cyri-joannis | frag-rem-mid |  |  | wip/cyril-alexandria-fragmenta-cyri-joannis--frag-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-cyri-joannis--frag-rem-close | free | cyril-alexandria-fragmenta-cyri-joannis | frag-rem-close |  |  | wip/cyril-alexandria-fragmenta-cyri-joannis--frag-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-contra-theodorum-2--frag-rem-mid | free | cyril-alexandria-fragmenta-contra-theodorum-2 | frag-rem-mid |  |  | wip/cyril-alexandria-fragmenta-contra-theodorum-2--frag-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-contra-theodorum-2--frag-rem-close | free | cyril-alexandria-fragmenta-contra-theodorum-2 | frag-rem-close |  |  | wip/cyril-alexandria-fragmenta-contra-theodorum-2--frag-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-contra-theodorum-3--frag-open | free | cyril-alexandria-fragmenta-contra-theodorum-3 | frag-open |  |  | wip/cyril-alexandria-fragmenta-contra-theodorum-3--frag-open | earliest scaffold |
| cyril-alexandria-fragmenta-contra-theodorum-3--frag-rem-close | free | cyril-alexandria-fragmenta-contra-theodorum-3 | frag-rem-close |  |  | wip/cyril-alexandria-fragmenta-contra-theodorum-3--frag-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-contra-diodorum--frag-rem-mid | free | cyril-alexandria-fragmenta-contra-diodorum | frag-rem-mid |  |  | wip/cyril-alexandria-fragmenta-contra-diodorum--frag-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-contra-diodorum--frag-rem-close | free | cyril-alexandria-fragmenta-contra-diodorum | frag-rem-close |  |  | wip/cyril-alexandria-fragmenta-contra-diodorum--frag-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-contra-theodorum-2--frag-open | free | cyril-alexandria-fragmenta-contra-theodorum-2 | frag-open |  |  | wip/cyril-alexandria-fragmenta-contra-theodorum-2--frag-open | earliest scaffold |
| cyril-alexandria-fragmenta-contra-theodorum-2--frag-rem-early | free | cyril-alexandria-fragmenta-contra-theodorum-2 | frag-rem-early |  |  | wip/cyril-alexandria-fragmenta-contra-theodorum-2--frag-rem-early | earliest scaffold |
| cyril-alexandria-fragmenta-canticum--u03-rem-mid | free | cyril-alexandria-fragmenta-canticum | u03-rem-mid |  |  | wip/cyril-alexandria-fragmenta-canticum--u03-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-canticum--u03-rem-close | free | cyril-alexandria-fragmenta-canticum | u03-rem-close |  |  | wip/cyril-alexandria-fragmenta-canticum--u03-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-contra-diodorum--frag-open | free | cyril-alexandria-fragmenta-contra-diodorum | frag-open |  |  | wip/cyril-alexandria-fragmenta-contra-diodorum--frag-open | earliest scaffold |

| cyril-alexandria-fragmenta-canticum--u02-rem-close | free | cyril-alexandria-fragmenta-canticum | u02-rem-close |  |  | wip/cyril-alexandria-fragmenta-canticum--u02-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-canticum--u03-open | free | cyril-alexandria-fragmenta-canticum | u03-open |  |  | wip/cyril-alexandria-fragmenta-canticum--u03-open | earliest scaffold |
| cyril-alexandria-fragmenta-canticum--u03-rem-early | free | cyril-alexandria-fragmenta-canticum | u03-rem-early |  |  | wip/cyril-alexandria-fragmenta-canticum--u03-rem-early | earliest scaffold |

| cyril-alexandria-fragmenta-canticum--u01-rem-close | free | cyril-alexandria-fragmenta-canticum | u01-rem-close |  |  | wip/cyril-alexandria-fragmenta-canticum--u01-rem-close | earliest scaffold |

| cyril-alexandria-fragmenta-acta-catholicas--u04-rem-mid | free | cyril-alexandria-fragmenta-acta-catholicas | u04-rem-mid |  |  | wip/cyril-alexandria-fragmenta-acta-catholicas--u04-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-acta-catholicas--u04-rem-close | free | cyril-alexandria-fragmenta-acta-catholicas | u04-rem-close |  |  | wip/cyril-alexandria-fragmenta-acta-catholicas--u04-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-canticum--u01-open | free | cyril-alexandria-fragmenta-canticum | u01-open |  |  | wip/cyril-alexandria-fragmenta-canticum--u01-open | earliest scaffold |

| cyril-alexandria-fragmenta-acta-catholicas--u03-rem-close | free | cyril-alexandria-fragmenta-acta-catholicas | u03-rem-close |  |  | wip/cyril-alexandria-fragmenta-acta-catholicas--u03-rem-close | earliest scaffold |

| cyril-alexandria-fragmenta-acta-catholicas--u04-rem-early | free | cyril-alexandria-fragmenta-acta-catholicas | u04-rem-early |  |  | wip/cyril-alexandria-fragmenta-acta-catholicas--u04-rem-early | earliest scaffold |

| cyril-alexandria-fragmenta-acta-catholicas--u01-rem-mid | free | cyril-alexandria-fragmenta-acta-catholicas | u01-rem-mid |  |  | wip/cyril-alexandria-fragmenta-acta-catholicas--u01-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-acta-catholicas--u01-rem-close | free | cyril-alexandria-fragmenta-acta-catholicas | u01-rem-close |  |  | wip/cyril-alexandria-fragmenta-acta-catholicas--u01-rem-close | earliest scaffold |

| cyril-alexandria-fragmenta-2-corinthios--u05-rem-mid | free | cyril-alexandria-fragmenta-2-corinthios | u05-rem-mid |  |  | wip/cyril-alexandria-fragmenta-2-corinthios--u05-rem-mid | earliest scaffold |

| cyril-alexandria-fragmenta-2-corinthios--u04-rem-mid | free | cyril-alexandria-fragmenta-2-corinthios | u04-rem-mid |  |  | wip/cyril-alexandria-fragmenta-2-corinthios--u04-rem-mid | earliest scaffold |

| cyril-alexandria-fragmenta-2-corinthios--u05-open | free | cyril-alexandria-fragmenta-2-corinthios | u05-open |  |  | wip/cyril-alexandria-fragmenta-2-corinthios--u05-open | earliest scaffold |
| cyril-alexandria-fragmenta-2-corinthios--u05-rem-early | free | cyril-alexandria-fragmenta-2-corinthios | u05-rem-early |  |  | wip/cyril-alexandria-fragmenta-2-corinthios--u05-rem-early | earliest scaffold |

| cyril-alexandria-fragmenta-2-corinthios--u04-open | free | cyril-alexandria-fragmenta-2-corinthios | u04-open |  |  | wip/cyril-alexandria-fragmenta-2-corinthios--u04-open | earliest scaffold |

| cyril-alexandria-fragmenta-2-corinthios--u02-rem-mid | free | cyril-alexandria-fragmenta-2-corinthios | u02-rem-mid |  |  | wip/cyril-alexandria-fragmenta-2-corinthios--u02-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-2-corinthios--u02-rem-close | free | cyril-alexandria-fragmenta-2-corinthios | u02-rem-close |  |  | wip/cyril-alexandria-fragmenta-2-corinthios--u02-rem-close | earliest scaffold |

| cyril-alexandria-fragmenta-2-corinthios--u03-rem-early | free | cyril-alexandria-fragmenta-2-corinthios | u03-rem-early |  |  | wip/cyril-alexandria-fragmenta-2-corinthios--u03-rem-early | earliest scaffold |
| cyril-alexandria-fragmenta-2-corinthios--u01-rem-mid | free | cyril-alexandria-fragmenta-2-corinthios | u01-rem-mid |  |  | wip/cyril-alexandria-fragmenta-2-corinthios--u01-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-2-corinthios--u01-rem-close | free | cyril-alexandria-fragmenta-2-corinthios | u01-rem-close |  |  | wip/cyril-alexandria-fragmenta-2-corinthios--u01-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-2-corinthios--u02-open | free | cyril-alexandria-fragmenta-2-corinthios | u02-open |  |  | wip/cyril-alexandria-fragmenta-2-corinthios--u02-open | earliest scaffold |
| cyril-alexandria-fragmenta-2-corinthios--u02-rem-early | free | cyril-alexandria-fragmenta-2-corinthios | u02-rem-early |  |  | wip/cyril-alexandria-fragmenta-2-corinthios--u02-rem-early | earliest scaffold |
| cyril-alexandria-fragmenta-1-corinthios--u08-rem-mid | free | cyril-alexandria-fragmenta-1-corinthios | u08-rem-mid |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u08-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-1-corinthios--u08-rem-close | free | cyril-alexandria-fragmenta-1-corinthios | u08-rem-close |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u08-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-2-corinthios--u01-open | free | cyril-alexandria-fragmenta-2-corinthios | u01-open |  |  | wip/cyril-alexandria-fragmenta-2-corinthios--u01-open | earliest scaffold |
| cyril-alexandria-fragmenta-2-corinthios--u01-rem-early | free | cyril-alexandria-fragmenta-2-corinthios | u01-rem-early |  |  | wip/cyril-alexandria-fragmenta-2-corinthios--u01-rem-early | earliest scaffold |

| cyril-alexandria-fragmenta-1-corinthios--u08-open | free | cyril-alexandria-fragmenta-1-corinthios | u08-open |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u08-open | earliest scaffold |
| cyril-alexandria-fragmenta-1-corinthios--u08-rem-early | free | cyril-alexandria-fragmenta-1-corinthios | u08-rem-early |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u08-rem-early | earliest scaffold |

| cyril-alexandria-fragmenta-1-corinthios--u06-rem-close | free | cyril-alexandria-fragmenta-1-corinthios | u06-rem-close |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u06-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-1-corinthios--u07-open | free | cyril-alexandria-fragmenta-1-corinthios | u07-open |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u07-open | earliest scaffold |
| cyril-alexandria-fragmenta-1-corinthios--u07-rem-early | free | cyril-alexandria-fragmenta-1-corinthios | u07-rem-early |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u07-rem-early | earliest scaffold |
| cyril-alexandria-fragmenta-1-corinthios--u05-rem-mid | free | cyril-alexandria-fragmenta-1-corinthios | u05-rem-mid |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u05-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-1-corinthios--u05-rem-close | free | cyril-alexandria-fragmenta-1-corinthios | u05-rem-close |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u05-rem-close | earliest scaffold |

| cyril-alexandria-fragmenta-1-corinthios--u06-rem-early | free | cyril-alexandria-fragmenta-1-corinthios | u06-rem-early |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u06-rem-early | earliest scaffold |
| cyril-alexandria-fragmenta-1-corinthios--u04-rem-mid | free | cyril-alexandria-fragmenta-1-corinthios | u04-rem-mid |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u04-rem-mid | earliest scaffold |

| cyril-alexandria-fragmenta-1-corinthios--u05-open | free | cyril-alexandria-fragmenta-1-corinthios | u05-open |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u05-open | earliest scaffold |
| cyril-alexandria-fragmenta-1-corinthios--u05-rem-early | free | cyril-alexandria-fragmenta-1-corinthios | u05-rem-early |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u05-rem-early | earliest scaffold |

| cyril-alexandria-fragmenta-1-corinthios--u03-rem-close | free | cyril-alexandria-fragmenta-1-corinthios | u03-rem-close |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u03-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-1-corinthios--u04-open | free | cyril-alexandria-fragmenta-1-corinthios | u04-open |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u04-open | earliest scaffold |
| cyril-alexandria-fragmenta-1-corinthios--u04-rem-early | free | cyril-alexandria-fragmenta-1-corinthios | u04-rem-early |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u04-rem-early | earliest scaffold |
| cyril-alexandria-fragmenta-1-corinthios--u02-rem-mid | free | cyril-alexandria-fragmenta-1-corinthios | u02-rem-mid |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u02-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-1-corinthios--u02-rem-close | free | cyril-alexandria-fragmenta-1-corinthios | u02-rem-close |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u02-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-1-corinthios--u03-open | free | cyril-alexandria-fragmenta-1-corinthios | u03-open |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u03-open | earliest scaffold |
| cyril-alexandria-fragmenta-1-corinthios--u03-rem-early | free | cyril-alexandria-fragmenta-1-corinthios | u03-rem-early |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u03-rem-early | earliest scaffold |
| cyril-alexandria-fragmenta-1-corinthios--u01-rem-mid | free | cyril-alexandria-fragmenta-1-corinthios | u01-rem-mid |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u01-rem-mid | earliest scaffold |
| cyril-alexandria-fragmenta-1-corinthios--u01-rem-close | free | cyril-alexandria-fragmenta-1-corinthios | u01-rem-close |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u01-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-1-corinthios--u02-open | free | cyril-alexandria-fragmenta-1-corinthios | u02-open |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u02-open | earliest scaffold |
| cyril-alexandria-fragmenta-1-corinthios--u02-rem-early | free | cyril-alexandria-fragmenta-1-corinthios | u02-rem-early |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u02-rem-early | earliest scaffold |
| cyril-alexandria-festal-letters--logos30-rem-mid | free | cyril-alexandria-festal-letters | logos30-rem-mid |  |  | wip/cyril-alexandria-festal-letters--logos30-rem-mid | earliest scaffold |
| cyril-alexandria-festal-letters--logos30-rem-close | free | cyril-alexandria-festal-letters | logos30-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos30-rem-close | earliest scaffold |
| cyril-alexandria-fragmenta-1-corinthios--u01-open | free | cyril-alexandria-fragmenta-1-corinthios | u01-open |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u01-open | earliest scaffold |
| cyril-alexandria-fragmenta-1-corinthios--u01-rem-early | free | cyril-alexandria-fragmenta-1-corinthios | u01-rem-early |  |  | wip/cyril-alexandria-fragmenta-1-corinthios--u01-rem-early | earliest scaffold |
| cyril-alexandria-festal-letters--logos29-rem-early | free | cyril-alexandria-festal-letters | logos29-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos29-rem-early | earliest scaffold |
| cyril-alexandria-festal-letters--logos29-rem-mid | free | cyril-alexandria-festal-letters | logos29-rem-mid |  |  | wip/cyril-alexandria-festal-letters--logos29-rem-mid | earliest scaffold |
| cyril-alexandria-festal-letters--logos29-rem-close | free | cyril-alexandria-festal-letters | logos29-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos29-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos30-rem-early | free | cyril-alexandria-festal-letters | logos30-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos30-rem-early | earliest scaffold |
| cyril-alexandria-festal-letters--logos27-rem-close | free | cyril-alexandria-festal-letters | logos27-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos27-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos28-rem-early | free | cyril-alexandria-festal-letters | logos28-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos28-rem-early | earliest scaffold |
| cyril-alexandria-festal-letters--logos28-rem-mid | free | cyril-alexandria-festal-letters | logos28-rem-mid |  |  | wip/cyril-alexandria-festal-letters--logos28-rem-mid | earliest scaffold |
| cyril-alexandria-festal-letters--logos28-rem-close | free | cyril-alexandria-festal-letters | logos28-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos28-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos26-rem-mid | free | cyril-alexandria-festal-letters | logos26-rem-mid |  |  | wip/cyril-alexandria-festal-letters--logos26-rem-mid | earliest scaffold |
| cyril-alexandria-festal-letters--logos26-rem-close | free | cyril-alexandria-festal-letters | logos26-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos26-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos27-rem-early | free | cyril-alexandria-festal-letters | logos27-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos27-rem-early | earliest scaffold |
| cyril-alexandria-festal-letters--logos27-rem-mid | free | cyril-alexandria-festal-letters | logos27-rem-mid |  |  | wip/cyril-alexandria-festal-letters--logos27-rem-mid | earliest scaffold |
| cyril-alexandria-festal-letters--logos25-rem-early | free | cyril-alexandria-festal-letters | logos25-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos25-rem-early | earliest scaffold |
| cyril-alexandria-festal-letters--logos25-rem-mid | free | cyril-alexandria-festal-letters | logos25-rem-mid |  |  | wip/cyril-alexandria-festal-letters--logos25-rem-mid | earliest scaffold |
| cyril-alexandria-festal-letters--logos25-rem-close | free | cyril-alexandria-festal-letters | logos25-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos25-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos26-rem-early | free | cyril-alexandria-festal-letters | logos26-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos26-rem-early | earliest scaffold |
| cyril-alexandria-festal-letters--logos23-rem-close | free | cyril-alexandria-festal-letters | logos23-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos23-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos24-rem-early | free | cyril-alexandria-festal-letters | logos24-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos24-rem-early | earliest scaffold |
| cyril-alexandria-festal-letters--logos24-rem-mid | free | cyril-alexandria-festal-letters | logos24-rem-mid |  |  | wip/cyril-alexandria-festal-letters--logos24-rem-mid | earliest scaffold |
| cyril-alexandria-festal-letters--logos24-rem-close | free | cyril-alexandria-festal-letters | logos24-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos24-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos22-rem-mid | free | cyril-alexandria-festal-letters | logos22-rem-mid |  |  | wip/cyril-alexandria-festal-letters--logos22-rem-mid | earliest scaffold |
| cyril-alexandria-festal-letters--logos22-rem-close | free | cyril-alexandria-festal-letters | logos22-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos22-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos23-rem-early | free | cyril-alexandria-festal-letters | logos23-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos23-rem-early | earliest scaffold |
| cyril-alexandria-festal-letters--logos23-rem-mid | free | cyril-alexandria-festal-letters | logos23-rem-mid |  |  | wip/cyril-alexandria-festal-letters--logos23-rem-mid | earliest scaffold |
| cyril-alexandria-festal-letters--logos21-rem-early | free | cyril-alexandria-festal-letters | logos21-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos21-rem-early | earliest scaffold |
| cyril-alexandria-festal-letters--logos21-rem-mid | free | cyril-alexandria-festal-letters | logos21-rem-mid |  |  | wip/cyril-alexandria-festal-letters--logos21-rem-mid | earliest scaffold |
| cyril-alexandria-festal-letters--logos21-rem-close | free | cyril-alexandria-festal-letters | logos21-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos21-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos22-rem-early | free | cyril-alexandria-festal-letters | logos22-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos22-rem-early | earliest scaffold |
| cyril-alexandria-festal-letters--logos19-rem-close | free | cyril-alexandria-festal-letters | logos19-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos19-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos20-rem-early | free | cyril-alexandria-festal-letters | logos20-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos20-rem-early | earliest scaffold |
| cyril-alexandria-festal-letters--logos20-rem-mid | free | cyril-alexandria-festal-letters | logos20-rem-mid |  |  | wip/cyril-alexandria-festal-letters--logos20-rem-mid | earliest scaffold |
| cyril-alexandria-festal-letters--logos20-rem-close | free | cyril-alexandria-festal-letters | logos20-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos20-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos18-rem-mid | free | cyril-alexandria-festal-letters | logos18-rem-mid |  |  | wip/cyril-alexandria-festal-letters--logos18-rem-mid | earliest scaffold |
| cyril-alexandria-festal-letters--logos18-rem-close | free | cyril-alexandria-festal-letters | logos18-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos18-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos19-rem-early | free | cyril-alexandria-festal-letters | logos19-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos19-rem-early | earliest scaffold |
| cyril-alexandria-festal-letters--logos19-rem-mid | free | cyril-alexandria-festal-letters | logos19-rem-mid |  |  | wip/cyril-alexandria-festal-letters--logos19-rem-mid | earliest scaffold |
| cyril-alexandria-festal-letters--logos17-rem-early | free | cyril-alexandria-festal-letters | logos17-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos17-rem-early | earliest scaffold |
| cyril-alexandria-festal-letters--logos17-rem-mid | free | cyril-alexandria-festal-letters | logos17-rem-mid |  |  | wip/cyril-alexandria-festal-letters--logos17-rem-mid | earliest scaffold |
| cyril-alexandria-festal-letters--logos17-rem-close | free | cyril-alexandria-festal-letters | logos17-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos17-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos18-rem-early | free | cyril-alexandria-festal-letters | logos18-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos18-rem-early | earliest scaffold |
| cyril-alexandria-festal-letters--logos15-rem-close | free | cyril-alexandria-festal-letters | logos15-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos15-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos16-rem-early | free | cyril-alexandria-festal-letters | logos16-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos16-rem-early | earliest scaffold |
| cyril-alexandria-festal-letters--logos16-rem-mid | free | cyril-alexandria-festal-letters | logos16-rem-mid |  |  | wip/cyril-alexandria-festal-letters--logos16-rem-mid | earliest scaffold |
| cyril-alexandria-festal-letters--logos16-rem-close | free | cyril-alexandria-festal-letters | logos16-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos16-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos14-rem-mid | free | cyril-alexandria-festal-letters | logos14-rem-mid |  |  | wip/cyril-alexandria-festal-letters--logos14-rem-mid | earliest scaffold |

| cyril-alexandria-festal-letters--logos15-rem-early | free | cyril-alexandria-festal-letters | logos15-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos15-rem-early | earliest scaffold |
| cyril-alexandria-festal-letters--logos15-rem-mid | free | cyril-alexandria-festal-letters | logos15-rem-mid |  |  | wip/cyril-alexandria-festal-letters--logos15-rem-mid | earliest scaffold |
| cyril-alexandria-festal-letters--logos13-rem-early | free | cyril-alexandria-festal-letters | logos13-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos13-rem-early | earliest scaffold |

| cyril-alexandria-festal-letters--logos14-rem-early | free | cyril-alexandria-festal-letters | logos14-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos14-rem-early | earliest scaffold |
| cyril-alexandria-festal-letters--logos11-rem-close | free | cyril-alexandria-festal-letters | logos11-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos11-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos12-rem-early | free | cyril-alexandria-festal-letters | logos12-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos12-rem-early | earliest scaffold |

| cyril-alexandria-festal-letters--logos12-rem-close | free | cyril-alexandria-festal-letters | logos12-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos12-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos10-rem-mid | free | cyril-alexandria-festal-letters | logos10-rem-mid |  |  | wip/cyril-alexandria-festal-letters--logos10-rem-mid | earliest scaffold |
| cyril-alexandria-festal-letters--logos10-rem-close | free | cyril-alexandria-festal-letters | logos10-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos10-rem-close | earliest scaffold |

| cyril-alexandria-festal-letters--logos11-rem-mid | free | cyril-alexandria-festal-letters | logos11-rem-mid |  |  | wip/cyril-alexandria-festal-letters--logos11-rem-mid | earliest scaffold |
| cyril-alexandria-festal-letters--logos09-rem-early | free | cyril-alexandria-festal-letters | logos09-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos09-rem-early | earliest scaffold |

| cyril-alexandria-festal-letters--logos10-rem-early | free | cyril-alexandria-festal-letters | logos10-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos10-rem-early | earliest scaffold |
| cyril-alexandria-festal-letters--logos07-rem-close | free | cyril-alexandria-festal-letters | logos07-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos07-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos08-rem-early | free | cyril-alexandria-festal-letters | logos08-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos08-rem-early | earliest scaffold |

| cyril-alexandria-festal-letters--logos08-rem-close | free | cyril-alexandria-festal-letters | logos08-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos08-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos06-rem-mid | free | cyril-alexandria-festal-letters | logos06-rem-mid |  |  | wip/cyril-alexandria-festal-letters--logos06-rem-mid | earliest scaffold |
| cyril-alexandria-festal-letters--logos06-rem-close | free | cyril-alexandria-festal-letters | logos06-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos06-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos07-rem-early | free | cyril-alexandria-festal-letters | logos07-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos07-rem-early | earliest scaffold |

| cyril-alexandria-festal-letters--logos05-rem-mid | free | cyril-alexandria-festal-letters | logos05-rem-mid |  |  | wip/cyril-alexandria-festal-letters--logos05-rem-mid | earliest scaffold |
| cyril-alexandria-festal-letters--logos05-rem-close | free | cyril-alexandria-festal-letters | logos05-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos05-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos06-rem-early | free | cyril-alexandria-festal-letters | logos06-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos06-rem-early | earliest scaffold |
| cyril-alexandria-festal-letters--logos02-rem-close | free | cyril-alexandria-festal-letters | logos02-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos02-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos04-rem-early | free | cyril-alexandria-festal-letters | logos04-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos04-rem-early | earliest scaffold |
| cyril-alexandria-festal-letters--logos04-rem-mid | free | cyril-alexandria-festal-letters | logos04-rem-mid |  |  | wip/cyril-alexandria-festal-letters--logos04-rem-mid | earliest scaffold |
| cyril-alexandria-festal-letters--logos04-rem-close | free | cyril-alexandria-festal-letters | logos04-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos04-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos01-rem-mid | free | cyril-alexandria-festal-letters | logos01-rem-mid |  |  | wip/cyril-alexandria-festal-letters--logos01-rem-mid | earliest scaffold |
| cyril-alexandria-festal-letters--logos01-rem-close | free | cyril-alexandria-festal-letters | logos01-rem-close |  |  | wip/cyril-alexandria-festal-letters--logos01-rem-close | earliest scaffold |
| cyril-alexandria-festal-letters--logos02-rem-early | free | cyril-alexandria-festal-letters | logos02-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos02-rem-early | earliest scaffold |

| cyril-alexandria-epistula-domnum--ep-rem-close | free | cyril-alexandria-epistula-domnum | ep-rem-close |  |  | wip/cyril-alexandria-epistula-domnum--ep-rem-close | earliest scaffold |

| cyril-alexandria-festal-letters--logos01-rem-early | free | cyril-alexandria-festal-letters | logos01-rem-early |  |  | wip/cyril-alexandria-festal-letters--logos01-rem-early | earliest scaffold |
| cyril-alexandria-encomium-maria--enc-rem-mid | free | cyril-alexandria-encomium-maria | enc-rem-mid |  |  | wip/cyril-alexandria-encomium-maria--enc-rem-mid | earliest scaffold |
| cyril-alexandria-encomium-maria--enc-rem-close | free | cyril-alexandria-encomium-maria | enc-rem-close |  |  | wip/cyril-alexandria-encomium-maria--enc-rem-close | earliest scaffold |
| cyril-alexandria-epistula-domnum--ep-open | free | cyril-alexandria-epistula-domnum | ep-open |  |  | wip/cyril-alexandria-epistula-domnum--ep-open | earliest scaffold |

| cyril-alexandria-dialogus-nestorio--dial-rem-mid | free | cyril-alexandria-dialogus-nestorio | dial-rem-mid |  |  | wip/cyril-alexandria-dialogus-nestorio--dial-rem-mid | earliest scaffold |

| cyril-alexandria-encomium-maria--enc-open | free | cyril-alexandria-encomium-maria | enc-open |  |  | wip/cyril-alexandria-encomium-maria--enc-open | earliest scaffold |
| cyril-alexandria-encomium-maria--enc-rem-early | free | cyril-alexandria-encomium-maria | enc-rem-early |  |  | wip/cyril-alexandria-encomium-maria--enc-rem-early | earliest scaffold |
| cyril-alexandria-contra-julianum--prol-rem-mid | free | cyril-alexandria-contra-julianum | prol-rem-mid |  |  | wip/cyril-alexandria-contra-julianum--prol-rem-mid | earliest scaffold |
| cyril-alexandria-contra-julianum--prol-rem-close | free | cyril-alexandria-contra-julianum | prol-rem-close |  |  | wip/cyril-alexandria-contra-julianum--prol-rem-close | earliest scaffold |

| cyril-alexandria-dialogus-nestorio--dial-rem-early | free | cyril-alexandria-dialogus-nestorio | dial-rem-early |  |  | wip/cyril-alexandria-dialogus-nestorio--dial-rem-early | earliest scaffold |
| cyril-alexandria-contra-julianum--book7-rem-close | free | cyril-alexandria-contra-julianum | book7-rem-close |  |  | wip/cyril-alexandria-contra-julianum--book7-rem-close | earliest scaffold |
| cyril-alexandria-contra-julianum--book8-rem-mid | free | cyril-alexandria-contra-julianum | book8-rem-mid |  |  | wip/cyril-alexandria-contra-julianum--book8-rem-mid | earliest scaffold |
| cyril-alexandria-contra-julianum--book9-rem-early | free | cyril-alexandria-contra-julianum | book9-rem-early |  |  | wip/cyril-alexandria-contra-julianum--book9-rem-early | earliest scaffold |
| cyril-alexandria-contra-julianum--prol-rem-early | free | cyril-alexandria-contra-julianum | prol-rem-early |  |  | wip/cyril-alexandria-contra-julianum--prol-rem-early | earliest scaffold |

| cyril-alexandria-contra-julianum--book6-rem-mid | free | cyril-alexandria-contra-julianum | book6-rem-mid |  |  | wip/cyril-alexandria-contra-julianum--book6-rem-mid | earliest scaffold |
| cyril-alexandria-contra-julianum--book7-rem-early | free | cyril-alexandria-contra-julianum | book7-rem-early |  |  | wip/cyril-alexandria-contra-julianum--book7-rem-early | earliest scaffold |

| cyril-alexandria-contra-julianum--book4-rem-early | free | cyril-alexandria-contra-julianum | book4-rem-early |  |  | wip/cyril-alexandria-contra-julianum--book4-rem-early | earliest scaffold |
| cyril-alexandria-contra-julianum--book4-rem-mid | free | cyril-alexandria-contra-julianum | book4-rem-mid |  |  | wip/cyril-alexandria-contra-julianum--book4-rem-mid | earliest scaffold |

| cyril-alexandria-contra-julianum--book2-rem-close | free | cyril-alexandria-contra-julianum | book2-rem-close |  |  | wip/cyril-alexandria-contra-julianum--book2-rem-close | earliest scaffold |
| cyril-alexandria-ad-optimum--ep-rem-mid | free | cyril-alexandria-ad-optimum | ep-rem-mid |  |  | wip/cyril-alexandria-ad-optimum--ep-rem-mid | earliest scaffold |

| cyril-alexandria-contra-julianum--book1-rem-mid | free | cyril-alexandria-contra-julianum | book1-rem-mid |  |  | wip/cyril-alexandria-contra-julianum--book1-rem-mid | earliest scaffold |
| cyril-alexandria-ad-episcopos-libyae--ep-rem-mid | free | cyril-alexandria-ad-episcopos-libyae | ep-rem-mid |  |  | wip/cyril-alexandria-ad-episcopos-libyae--ep-rem-mid | earliest scaffold |

| cyril-alexandria-ad-optimum--ep-open | free | cyril-alexandria-ad-optimum | ep-open |  |  | wip/cyril-alexandria-ad-optimum--ep-open | earliest scaffold |
| cyril-alexandria-ad-optimum--ep-rem-early | free | cyril-alexandria-ad-optimum | ep-rem-early |  |  | wip/cyril-alexandria-ad-optimum--ep-rem-early | earliest scaffold |
| cyril-alexandria-ad-calosyrium--ep-rem-mid | free | cyril-alexandria-ad-calosyrium | ep-rem-mid |  |  | wip/cyril-alexandria-ad-calosyrium--ep-rem-mid | earliest scaffold |
| cyril-alexandria-ad-calosyrium--ep-rem-close | free | cyril-alexandria-ad-calosyrium | ep-rem-close |  |  | wip/cyril-alexandria-ad-calosyrium--ep-rem-close | earliest scaffold |
| cyril-alexandria-ad-episcopos-libyae--ep-open | free | cyril-alexandria-ad-episcopos-libyae | ep-open |  |  | wip/cyril-alexandria-ad-episcopos-libyae--ep-open | earliest scaffold |
| cyril-alexandria-ad-episcopos-libyae--ep-rem-early | free | cyril-alexandria-ad-episcopos-libyae | ep-rem-early |  |  | wip/cyril-alexandria-ad-episcopos-libyae--ep-rem-early | earliest scaffold |
| hesychius-in-stephanum--u02-rem-mid | free | hesychius-in-stephanum | u02-rem-mid |  |  | wip/hesychius-in-stephanum--u02-rem-mid | earliest scaffold |
| hesychius-in-stephanum--u02-rem-close | claimed | hesychius-in-stephanum | u02-rem-close | overnight-mini-nv | 2026-10-03 | wip/hesychius-in-stephanum--u02-rem-close | earliest scaffold |

| cyril-alexandria-ad-calosyrium--ep-rem-early | free | cyril-alexandria-ad-calosyrium | ep-rem-early |  |  | wip/cyril-alexandria-ad-calosyrium--ep-rem-early | earliest scaffold |

| hesychius-in-stephanum--u02-open | free | hesychius-in-stephanum | u02-open |  |  | wip/hesychius-in-stephanum--u02-open | earliest scaffold |

| hesychius-in-stephanum--u01-open | free | hesychius-in-stephanum | u01-open |  |  | wip/hesychius-in-stephanum--u01-open | earliest scaffold |
| hesychius-in-stephanum--u01-rem-early | free | hesychius-in-stephanum | u01-rem-early |  |  | wip/hesychius-in-stephanum--u01-rem-early | earliest scaffold |

| hesychius-in-sanctos-martyres--u01-open | free | hesychius-in-sanctos-martyres | u01-open |  |  | wip/hesychius-in-sanctos-martyres--u01-open | earliest scaffold |

| hesychius-in-lazarum-ramos--u02-rem-early | free | hesychius-in-lazarum-ramos | u02-rem-early |  |  | wip/hesychius-in-lazarum-ramos--u02-rem-early | earliest scaffold |

| hesychius-in-conceptionem-praecursoris--u01-open | free | hesychius-in-conceptionem-praecursoris | u01-open |  |  | wip/hesychius-in-conceptionem-praecursoris--u01-open | earliest scaffold |

| hesychius-in-andream--u02-rem-close | free | hesychius-in-andream | u02-rem-close |  |  | wip/hesychius-in-andream--u02-rem-close | earliest scaffold |

| hesychius-in-andream--u02-rem-early | free | hesychius-in-andream | u02-rem-early |  |  | wip/hesychius-in-andream--u02-rem-early | earliest scaffold |

| hesychius-homilia-ii-pascha--u01-rem-close | free | hesychius-homilia-ii-pascha | u01-rem-close |  |  | wip/hesychius-homilia-ii-pascha--u01-rem-close | earliest scaffold |

| hesychius-homilia-jejunio--u01-rem-early | free | hesychius-homilia-jejunio | u01-rem-early |  |  | wip/hesychius-homilia-jejunio--u01-rem-early | earliest scaffold |

| hesychius-homilia-i-pascha--u01-rem-mid | free | hesychius-homilia-i-pascha | u01-rem-mid |  |  | wip/hesychius-homilia-i-pascha--u01-rem-mid | earliest scaffold |
| hesychius-homilia-i-pascha--u01-rem-close | free | hesychius-homilia-i-pascha | u01-rem-close |  |  | wip/hesychius-homilia-i-pascha--u01-rem-close | earliest scaffold |

| hesychius-homilia-i-pascha--u01-rem-early | free | hesychius-homilia-i-pascha | u01-rem-early |  |  | wip/hesychius-homilia-i-pascha--u01-rem-early | earliest scaffold |

| epiphanius-tractatus-de-numerorum-mysteriis--u01-open | free | epiphanius-tractatus-de-numerorum-mysteriis | u01-open |  |  | wip/epiphanius-tractatus-de-numerorum-mysteriis--u01-open | earliest scaffold |

| epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u02-open | free | epiphanius-testimonia-ex-divinis-et-sacris-scripturis | u02-open |  |  | wip/epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u02-open | earliest scaffold |

| epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u01-open | free | epiphanius-testimonia-ex-divinis-et-sacris-scripturis | u01-open |  |  | wip/epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u01-open | earliest scaffold |

| epiphanius-testamentum-ad-cives--u01-open | claimed | epiphanius-testamentum-ad-cives | u01-open | overnight-mini-cf | 2026-10-03 | wip/epiphanius-testamentum-ad-cives--u01-open | earliest scaffold |

| cyr-isa-logos3-rem-early | free | cyril-alexandria-isaiah | logos3-rem-early |  |  | wip/cyr-isa-logos3-rem-early | repair scaffold closeout |

| cyr-isa-book5-part2-rem-mid | free | cyril-alexandria-isaiah | book5-part2-rem-mid |  |  | wip/cyr-isa-book5-part2-rem-mid | source is betacode; do not publish |

| cyr-isa-book4-logos2-rem-early | free | cyril-alexandria-isaiah | book4-logos2-rem-early |  |  | wip/cyr-isa-book4-logos2-rem-early | repair scaffold closeout |

| cyr-isa-book3-tomos4-rem-early | free | cyril-alexandria-isaiah | book3-tomos4-rem-early |  |  | wip/cyr-isa-book3-tomos4-rem-early | repair scaffold closeout |

| cyr-isa-book5-part2-rem-close | free | cyril-alexandria-isaiah | book5-part2-rem-close |  |  | wip/cyr-isa-book5-part2-rem-close | source is betacode; do not publish |

| nemesius-de-natura-hominis-densify | prepped | nemesius-de-natura-hominis | Full work densify (Wither 1636 PD English) | Owner | 2026-09-14 | wip/nemesius-de-natura-hominis-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| macarius-spiritual-homilies-densify | prepped | macarius-spiritual-homilies | Full work densify (PD English exists) | Owner | 2026-09-14 | wip/macarius-spiritual-homilies-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| philostorgius-he-densify | prepped | philostorgius-he | Full work densify (Walford PD English) | Owner | 2026-09-15 | wip/philostorgius-he-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| greg-thaum-fide-xii-densify | prepped | gregory-thaumaturgus-de-fide-xii | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/greg-thaum-fide-xii-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| greg-thaum-ad-tatianum-densify | prepped | gregory-thaumaturgus-ad-tatianum-de-anima | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/greg-thaum-ad-tatianum-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| greg-thaum-annuntiationem-densify | prepped | gregory-thaumaturgus-in-annuntiationem | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/greg-thaum-annuntiationem-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| greg-thaum-sermo-omnes-densify | prepped | gregory-thaumaturgus-sermo-in-omnes-sanctos | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/greg-thaum-sermo-omnes-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| greg-thaum-panegyricus-densify | prepped | gregory-thaumaturgus-panegyricus | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/greg-thaum-panegyricus-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| greg-thaum-eccl-metaphrase-densify | prepped | gregory-thaumaturgus-ecclesiastes-metaphrase | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/greg-thaum-eccl-metaphrase-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| greg-thaum-epistula-can-densify | prepped | gregory-thaumaturgus-epistula-canonica | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/greg-thaum-epistula-can-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| serapion-fragmenta-densify | prepped | serapion-antioch-fragmenta | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/serapion-fragmenta-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| epiphanius-ancoratus-densify | prepped | epiphanius-ancoratus | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/epiphanius-ancoratus-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| epiphanius-panarion-densify | prepped | epiphanius-panarion | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/epiphanius-panarion-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| epiphanius-anaceph-densify | prepped | epiphanius-anacephalaeosis | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/epiphanius-anaceph-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| epiphanius-de-mensuris-densify | prepped | epiphanius-de-mensuris | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/epiphanius-de-mensuris-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| photius-bibliotheca-densify | prepped | photius-bibliotheca | Full work densify (Freese PD English) | OpenCode | 2026-09-15 | wip/photius-bibliotheca-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| cosmas-topographia-densify | prepped | cosmas-topographia | Full work densify (McCrindle 1897 PD English) | OpenCode | 2026-09-15 | wip/cosmas-topographia-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| paulus-silentarius-sophia-densify | prepped | paulus-silentarius-sophia | Full work densify (Lethaby PD English) | OpenCode | 2026-09-15 | wip/paulus-silentarius-sophia-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| paulus-silentarius-ambonis-densify | prepped | paulus-silentarius-ambonis | Full work densify (Lethaby/Swainson PD English) | OpenCode | 2026-09-15 | wip/paulus-silentarius-ambonis-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| crocius-syntagma-densify | ready-for-review | crocius-syntagma | Liber I-IV COMPLETE densify CLOSED FINIS PHYS 1363; Cap.15-22 secs 5/5/4/5/4/4/4/5 (=36); Index Authorum ~1370-1372 not densified as treatise body; claim ready for review / free | Densify | 2026-09-29 | wip/crocius-syntagma-densify | Reformed lane; Liber I-III CLOSED; Liber IV Cap.1-22 COMPLETE PHYS 1005-1363 FINIS; Syntagma densify CLOSED (english on disk; no ship/promote/mixed commit) |
| davenant-dissertationes-densify | claimed | davenant-dissertationes-duae | Full work densify (Dissertationes duae; 1650 Latin) | scribe-davenant | 2026-09-22 | wip/davenant-dissertationes-densify | Reformed lane; Daniel 1650 PD Latin; new English from Latin |
| baron-philosophia-densify | ready-for-review | baron-philosophia-theologiae-ancillans | Exercitatio Tertia Art. I–XXX densify COMPLETE (secs 28→57; Prima 1–12 + Secunda 13–27 PRESERVED); Tertia FINIS; Philosophia three Exercitationes CLOSED; claim ready for review / free | Densify | 2026-09-29 | wip/baron-philosophia-densify | Reformed lane; Oxford 1658 PD Latin; Prima+Secunda+Tertia COMPLETE on disk; Crocius untouched; no ship/promote/mixed commit |
| placeus-de-imputatione-densify | claimed | placeus-de-imputatione | Full work densify (De imputatione; 1661 Latin) | scribe-placeus | 2026-09-22 | wip/placeus-de-imputatione-densify | Reformed lane; Lesnerius 1661 PD Latin; new English from Latin |
| le-blanc-theses-densify | claimed | le-blanc-theses-theologicae | Sanctorum Cultu Pars Secunda Reformata I-XL densify DONE tip 1557→1597; tip-1557 PRESERVED; Pars Secunda NOT closed; next XLI–fin (~CI); book densify NOT closed; not ship | Densify | 2026-09-29 | wip/le-blanc-theses-densify | Reformed lane; Pitt 1675; packet sanctorum_cultu_pars_secunda_i_xl_densify; sister lock EXTEND sanctorum_cultu Pars Secunda I-XL; Punch X=NO; Crocius/Baron CLOSED untouched this slice |
| strimesius-in-controversias-densify | claimed | strimesius-in-controversias-evangelicorum | Full work densify (In controversias evangelicorum; 1708 Latin) | scribe-strimesius | 2026-09-22 | wip/strimesius-in-controversias-densify | Reformed lane; Francofurti ad Viadrum 1708 PD Latin; new English from Latin |

## How to claim

```bash
python3 scripts/claims.py start --agent YourName
```

Then do only that slice. Finish with `python3 scripts/ai_promote.py --claim <id> --agent YourName`.

## Done / closed

Archived: older done rows now live in `docs/CLAIMS_ARCHIVE.md` (1871 rows, full commit history preserved). Do not read the archive for routine work.
Keep this file lean: when a claim closes, move its row to the archive instead of letting this section grow.

| cyr-isa-tomos2-open | done | book2-tomos2-open | 2026-09-22 | AI cross-check (verify); @cf/google/gemma-4-26b-a4b-it+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260923T034046048669Z-cyr-isa-tomos2-open |
## Do not claim these (owner / blocked)

- Website deploy / Cloudflare Pages / edits under `websites/fathers.saneapps.com`
- Logos Personal Book compile; `build_book.py` unless owner asked
- Inventing a new book slug without `docs/WORKS_QUEUE.md` + charter
- Any modern or ANF English as the reading text
- Changing Slice columns or merging/splitting claim rows (ask owner)
| cyr-isa-logos1-rem-mid | done | logos1-rem-mid | 2026-09-23 | AI cross-check (golive5-cf); @cf/qwen/qwen3-30b-a3b-fp8+@cf/zai-org/glm-4.7-flash; receipt 20260923T054356295735Z-cyr-isa-logos1-rem-mid |
| cyr-isa-book2-open | done | book2-open | 2026-09-24 | AI cross-check (overnight-mini-cf); +@cf/meta/llama-3.3-70b-instruct-fp8-fast+arb:@cf/zai-org/glm-4.7-flash; receipt 20260925T012514135741Z-cyr-isa-book2-open |
| cyr-isa-logos1-open | done | logos1-open | 2026-09-25 | AI cross-check (fix-logos); +@cf/meta/llama-3.3-70b-instruct-fp8-fast+arb:nvidia/nemotron-3-super-120b-a12b; receipt 20260925T193753960270Z-cyr-isa-logos1-open |
| cyr-isa-prologue | done | prologue | 2026-09-25 | AI cross-check (fix-logos); @cf/qwen/qwen3-30b-a3b-fp8+@cf/google/gemma-4-26b-a4b-it; receipt 20260925T194050808121Z-cyr-isa-prologue |
| cyr-isa-logos1-rem-close | done | logos1-rem-close | 2026-09-25 | AI cross-check (fix-logos); @cf/qwen/qwen3-30b-a3b-fp8+@cf/zai-org/glm-4.7-flash; receipt 20260925T194121496372Z-cyr-isa-logos1-rem-close |
| cyr-isa-book5-part1-open | done | book5-part1-open | 2026-09-25 | AI cross-check (draft-book5); +@cf/meta/llama-3.3-70b-instruct-fp8-fast+arb:@cf/zai-org/glm-4.7-flash; receipt 20260925T194252012436Z-cyr-isa-book5-part1-open |
| cyr-isa-book4-logos1-open | done | book4-logos1-open | 2026-09-25 | AI cross-check (holds-resolver-book4); mistralai/mistral-nemotron+@cf/google/gemma-4-26b-a4b-it; receipt 20260925T181337539427Z-cyr-isa-book4-logos1-open (verified-mark, no re-burn) |
| cyr-isa-book4-logos2-open | done | book4-logos2-open | 2026-09-25 | AI cross-check (holds-resolver-book4); mistralai/mistral-nemotron+@cf/zai-org/glm-4.7-flash; receipt 20260925T190814028725Z-cyr-isa-book4-logos2-open (verified-mark, no re-burn) |
| cyr-isa-book4-logos3-open | done | book4-logos3-open | 2026-09-25 | AI cross-check (holds-resolver-book4); @cf/google/gemma-4-26b-a4b-it+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260925T190024261858Z-cyr-isa-book4-logos3-open (verified-mark, no re-burn) |
| cyr-isa-book4-logos4-open | done | book4-logos4-open | 2026-09-25 | AI cross-check (holds-resolver-book4); @cf/google/gemma-4-26b-a4b-it+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260925T194012163418Z-cyr-isa-book4-logos4-open (verified-mark, no re-burn) |
| cyr-isa-book4-logos5-open | done | book4-logos5-open | 2026-09-25 | AI cross-check (holds-resolver-book4); @cf/google/gemma-4-26b-a4b-it+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260925T194059399209Z-cyr-isa-book4-logos5-open (verified-mark, no re-burn) |
| cyr-isa-book3-tomos1-open | done | book3-tomos1-open | 2026-09-25 | AI cross-check (fix-book3); +@cf/meta/llama-3.3-70b-instruct-fp8-fast+arb:@cf/google/gemma-4-26b-a4b-it; receipt 20260925T201853142687Z-cyr-isa-book3-tomos1-open |
| cyr-isa-book2-tomos3-open | done | book2-tomos3-open | 2026-09-25 | AI cross-check (fix-book2); @cf/qwen/qwen3-30b-a3b-fp8+@cf/google/gemma-4-26b-a4b-it; receipt 20260925T201916849546Z-cyr-isa-book2-tomos3-open |
| cyr-isa-book3-tomos2-open | done | book3-tomos2-open | 2026-09-25 | AI cross-check (fix-book3); +@cf/meta/llama-3.3-70b-instruct-fp8-fast+arb:@cf/google/gemma-4-26b-a4b-it; receipt 20260925T202123048754Z-cyr-isa-book3-tomos2-open |
| cyr-isa-book3-tomos3-open | done | book3-tomos3-open | 2026-09-25 | AI cross-check (fix-book3); @cf/qwen/qwen3-30b-a3b-fp8+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260925T202437049249Z-cyr-isa-book3-tomos3-open |
| cyr-isa-book3-tomos4-open | done | book3-tomos4-open | 2026-09-25 | AI cross-check (fix-book3); +@cf/meta/llama-3.3-70b-instruct-fp8-fast+arb:@cf/google/gemma-4-26b-a4b-it; receipt 20260925T202816665289Z-cyr-isa-book3-tomos4-open |
| cyr-isa-logos3-open | done | logos3-open | 2026-09-25 | AI cross-check (fix-logos); @cf/google/gemma-4-26b-a4b-it+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260925T203148871267Z-cyr-isa-logos3-open |
| cyr-isa-book3-tomos5-open | done | book3-tomos5-open | 2026-09-25 | AI cross-check (fix-book3); @cf/qwen/qwen3-30b-a3b-fp8+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260925T203626702632Z-cyr-isa-book3-tomos5-open |
| cyr-isa-book2-tomos4-open | done | book2-tomos4-open | 2026-09-25 | AI cross-check (fix-book2); @cf/qwen/qwen3-30b-a3b-fp8+@cf/google/gemma-4-26b-a4b-it; receipt 20260925T210245605900Z-cyr-isa-book2-tomos4-open |
| cyr-isa-logos4-open | done | logos4-open | 2026-09-25 | AI cross-check (fix-logos); @cf/qwen/qwen3-30b-a3b-fp8+@cf/google/gemma-4-26b-a4b-it; receipt 20260925T210634248004Z-cyr-isa-logos4-open |
| cyr-isa-logos5-open | done | logos5-open | 2026-09-25 | AI cross-check (fix-logos); @cf/qwen/qwen3-30b-a3b-fp8+@cf/google/gemma-4-26b-a4b-it; receipt 20260925T212310338343Z-cyr-isa-logos5-open |
| cyr-isa-book2-tomos5-open | done | book2-tomos5-open | 2026-09-25 | AI cross-check (fix-book2); +@cf/google/gemma-4-26b-a4b-it+arb:@cf/zai-org/glm-4.7-flash; receipt 20260925T213738980023Z-cyr-isa-book2-tomos5-open |
| cyr-isa-book5-part2-open | done | book5-part2-open | 2026-09-25 | AI cross-check (finish-book5); @cf/google/gemma-4-26b-a4b-it+@cf/zai-org/glm-4.7-flash; receipt 20260925T220437556321Z-cyr-isa-book5-part2-open |
| cyr-isa-book5-part2-rem-early | done | book5-part2-rem-early | 2026-09-26 | AI cross-check (overnight-mini-nv); @cf/qwen/qwen3-30b-a3b-fp8+@cf/meta/llama-3.3-70b-instruct-fp8-fast; receipt 20260927T011341239453Z-cyr-isa-book5-part2-rem-early |
| cyr-isa-logos2-open | done | logos2-open | 2026-09-28 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T004027390316Z-cyr-isa-logos2-open |
| cyr-isa-book2-rem-early | done | book2-rem-early | 2026-09-28 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T010817218819Z-cyr-isa-book2-rem-early |
| cyr-isa-book2-tomos2-rem-close | done | book2-tomos2-rem-close | 2026-09-28 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T011105204073Z-cyr-isa-book2-tomos2-rem-close |
| cyr-isa-book2-tomos3-rem-close | done | book2-tomos3-rem-close | 2026-09-28 | AI cross-check (overnight-mini-cf); accept-current+clause; receipt 20260929T013453618936Z-cyr-isa-book2-tomos3-rem-close |
| cyr-isa-book2-rem-close | done | book2-rem-close | 2026-09-28 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T013702005597Z-cyr-isa-book2-rem-close |
| cyr-isa-book2-tomos4-rem-close | done | book2-tomos4-rem-close | 2026-09-28 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T014447045986Z-cyr-isa-book2-tomos4-rem-close |
| cyr-isa-book2-tomos4-rem-mid | done | book2-tomos4-rem-mid | 2026-09-28 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T015351038688Z-cyr-isa-book2-tomos4-rem-mid |
| cyr-isa-book2-tomos2-rem-early | done | book2-tomos2-rem-early | 2026-09-28 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T015532435697Z-cyr-isa-book2-tomos2-rem-early |
| cyr-isa-book2-tomos5-rem-early | done | book2-tomos5-rem-early | 2026-09-28 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T021535598152Z-cyr-isa-book2-tomos5-rem-early |
| cyr-isa-book3-tomos1-rem-close | done | book3-tomos1-rem-close | 2026-09-28 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T021848896907Z-cyr-isa-book3-tomos1-rem-close |
| cyr-isa-book2-tomos2-rem-mid | done | book2-tomos2-rem-mid | 2026-09-28 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T022515137549Z-cyr-isa-book2-tomos2-rem-mid |
| cyr-isa-book2-tomos5-rem-close | done | book2-tomos5-rem-close | 2026-09-28 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T024630706894Z-cyr-isa-book2-tomos5-rem-close |
| cyr-isa-book3-tomos3-rem-early | done | book3-tomos3-rem-early | 2026-09-28 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T030540451497Z-cyr-isa-book3-tomos3-rem-early |
| cyr-isa-book3-tomos1-rem-early | done | book3-tomos1-rem-early | 2026-09-28 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T030839390330Z-cyr-isa-book3-tomos1-rem-early |
| cyr-isa-book3-tomos2-rem-close | done | book3-tomos2-rem-close | 2026-09-28 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T031251190190Z-cyr-isa-book3-tomos2-rem-close |
| cyr-isa-book3-tomos4-rem-close | done | book3-tomos4-rem-close | 2026-09-28 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T032640630533Z-cyr-isa-book3-tomos4-rem-close |
| cyr-isa-book3-tomos4-rem-mid | done | book3-tomos4-rem-mid | 2026-09-28 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T032807296570Z-cyr-isa-book3-tomos4-rem-mid |
| cyr-isa-logos1-rem-early | done | logos1-rem-early | 2026-09-28 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T033320758746Z-cyr-isa-logos1-rem-early |
| cyr-isa-book3-tomos3-rem-mid | done | book3-tomos3-rem-mid | 2026-09-28 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T033600791484Z-cyr-isa-book3-tomos3-rem-mid |
| cyr-isa-book3-tomos3-rem-close | done | book3-tomos3-rem-close | 2026-09-28 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T033928944251Z-cyr-isa-book3-tomos3-rem-close |
| cyr-isa-book3-tomos2-rem-early | done | book3-tomos2-rem-early | 2026-09-28 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T034212517706Z-cyr-isa-book3-tomos2-rem-early |
| cyr-isa-book2-tomos5-rem-mid | done | book2-tomos5-rem-mid | 2026-09-28 | AI cross-check (overnight-mini-cf); accept-current+clause; receipt 20260929T034452028676Z-cyr-isa-book2-tomos5-rem-mid |
| cyr-isa-book2-tomos3-rem-early | done | book2-tomos3-rem-early | 2026-09-28 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T034549945181Z-cyr-isa-book2-tomos3-rem-early |
| cyr-isa-book2-rem-mid | done | book2-rem-mid | 2026-09-28 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T034805746006Z-cyr-isa-book2-rem-mid |
| cyr-isa-book3-tomos5-rem-early | done | book3-tomos5-rem-early | 2026-09-28 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T035834061385Z-cyr-isa-book3-tomos5-rem-early |
| cyr-isa-book4-logos2-rem-close | done | book4-logos2-rem-close | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T043551559209Z-cyr-isa-book4-logos2-rem-close |
| cyr-isa-book4-logos2-rem-mid | done | book4-logos2-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T044439374369Z-cyr-isa-book4-logos2-rem-mid |
| cyr-isa-book4-logos1-rem-close | done | book4-logos1-rem-close | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T045127112543Z-cyr-isa-book4-logos1-rem-close |
| cyr-isa-book3-tomos5-rem-close | done | book3-tomos5-rem-close | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T045154921473Z-cyr-isa-book3-tomos5-rem-close |
| cyr-isa-book3-tomos2-rem-mid | done | book3-tomos2-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current+clause; receipt 20260929T045326460690Z-cyr-isa-book3-tomos2-rem-mid |
| cyr-isa-book4-logos1-rem-early | done | book4-logos1-rem-early | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T045415119877Z-cyr-isa-book4-logos1-rem-early |
| cyr-isa-book4-logos3-rem-mid | done | book4-logos3-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T051859085089Z-cyr-isa-book4-logos3-rem-mid |
| cyr-isa-book4-logos1-rem-mid | done | book4-logos1-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T052043162956Z-cyr-isa-book4-logos1-rem-mid |
| cyr-isa-book4-logos4-rem-early | done | book4-logos4-rem-early | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T054236422706Z-cyr-isa-book4-logos4-rem-early |
| cyr-isa-book4-logos3-rem-close | done | book4-logos3-rem-close | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T055325812257Z-cyr-isa-book4-logos3-rem-close |
| cyr-isa-book4-logos5-rem-close | done | book4-logos5-rem-close | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T055541564060Z-cyr-isa-book4-logos5-rem-close |
| cyr-isa-book4-logos3-rem-early | done | book4-logos3-rem-early | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T055555885386Z-cyr-isa-book4-logos3-rem-early |
| cyr-isa-book5-part1-rem-early | done | book5-part1-rem-early | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T062542274194Z-cyr-isa-book5-part1-rem-early |
| cyr-isa-book4-logos4-rem-close | done | book4-logos4-rem-close | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T063608639131Z-cyr-isa-book4-logos4-rem-close |
| cyr-isa-book3-tomos1-rem-mid | done | book3-tomos1-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current+clause; receipt 20260929T063733218155Z-cyr-isa-book3-tomos1-rem-mid |
| cyr-isa-logos2-rem-close | done | logos2-rem-close | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T064438128001Z-cyr-isa-logos2-rem-close |
| cyr-isa-book4-logos5-rem-mid | done | book4-logos5-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T064820173556Z-cyr-isa-book4-logos5-rem-mid |
| cyr-isa-book5-part1-rem-mid | done | book5-part1-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T065241331040Z-cyr-isa-book5-part1-rem-mid |
| cyr-isa-logos4-rem-close | done | logos4-rem-close | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T073127295492Z-cyr-isa-logos4-rem-close |
| cyr-isa-logos4-rem-mid | done | logos4-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T080028092724Z-cyr-isa-logos4-rem-mid |
| cyr-isa-logos3-rem-close | done | logos3-rem-close | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T081956034046Z-cyr-isa-logos3-rem-close |
| cyr-isa-book5-part1-rem-close | done | book5-part1-rem-close | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T083033584716Z-cyr-isa-book5-part1-rem-close |
| cyr-isa-book4-logos4-rem-mid | done | book4-logos4-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T083132467360Z-cyr-isa-book4-logos4-rem-mid |
| cyr-isa-logos4-rem-early | done | logos4-rem-early | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T085251269111Z-cyr-isa-logos4-rem-early |
| cyr-isa-logos2-rem-early | done | logos2-rem-early | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T090657426153Z-cyr-isa-logos2-rem-early |
| cyr-isa-book2-tomos3-rem-mid | done | book2-tomos3-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T091037261063Z-cyr-isa-book2-tomos3-rem-mid |
| cyr-isa-logos5-rem-early | done | logos5-rem-early | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T093544166799Z-cyr-isa-logos5-rem-early |
| cyr-isa-logos5-rem-close | done | logos5-rem-close | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T095038317654Z-cyr-isa-logos5-rem-close |
| cyr-isa-logos5-rem-mid | done | logos5-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current+clause; receipt 20260929T100249776220Z-cyr-isa-logos5-rem-mid |
| cyr-isa-logos3-rem-mid | done | logos3-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T100708460303Z-cyr-isa-logos3-rem-mid |
| cyr-isa-logos2-rem-mid | done | logos2-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T111153415666Z-cyr-isa-logos2-rem-mid |
| cyr-isa-book4-logos5-rem-early | done | book4-logos5-rem-early | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current+clause; receipt 20260929T122559324371Z-cyr-isa-book4-logos5-rem-early |
ceipt 20260929T124640969768Z-cyr-isa-book3-tomos5-rem-mid |
| cyr-isa-book2-tomos4-rem-early | done | book2-tomos4-rem-early | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current+clause; receipt 20260929T022441768738Z-cyr-isa-book2-tomos4-rem-early |
| cyr-isa-book3-tomos5-rem-mid | done | book3-tomos5-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T124640969768Z-cyr-isa-book3-tomos5-rem-mid |
| epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u01-rem-close | done | u01-rem-close | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current+clause; receipt 20260929T162256571546Z-epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u01-rem-close |
| epiphanius-testamentum-ad-cives--u01-rem-mid | done | u01-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T165231125120Z-epiphanius-testamentum-ad-cives--u01-rem-mid |
| epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u03-rem-close | done | u03-rem-close | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T165839291782Z-epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u03-rem-close |
| epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u02-rem-close | done | u02-rem-close | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T170730366358Z-epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u02-rem-close |
| epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u03-rem-early | done | u03-rem-early | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current+clause; receipt 20260929T172304858976Z-epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u03-rem-early |
| epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u01-rem-mid | done | u01-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T171935632855Z-epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u01-rem-mid |
| epiphanius-tractatus-de-numerorum-mysteriis--u01-rem-early | done | u01-rem-early | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T175134825290Z-epiphanius-tractatus-de-numerorum-mysteriis--u01-rem-early |
| epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u03-open | done | u03-open | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current+clause; receipt 20260929T175546923830Z-epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u03-open |
| epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u01-rem-early | done | u01-rem-early | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T181309121858Z-epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u01-rem-early |
| severianus-fragmentum-philemonem--u01-open | done | u01-open | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T182857729292Z-severianus-fragmentum-philemonem--u01-open |
| epiphanius-testamentum-ad-cives--u01-rem-close | done | u01-rem-close | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current+clause; receipt 20260929T190007780293Z-epiphanius-testamentum-ad-cives--u01-rem-close |
| epiphanius-fragmenta-precationis-et-exorcismi--u01-open | done | u01-open | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current+clause; receipt 20260929T190041022202Z-epiphanius-fragmenta-precationis-et-exorcismi--u01-open |
| theophilus-alex-fragmenta-joannem--u01-rem-close | done | u01-rem-close | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T192921631314Z-theophilus-alex-fragmenta-joannem--u01-rem-close |
| theophilus-alex-fragmenta-matthaeum--u01-rem-early | done | u01-rem-early | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T193251367024Z-theophilus-alex-fragmenta-matthaeum--u01-rem-early |
| theophilus-alex-fragmenta-joannem--u01-rem-mid | done | u01-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T193446027091Z-theophilus-alex-fragmenta-joannem--u01-rem-mid |
| epiphanius-tractatus-de-numerorum-mysteriis--u01-rem-close | done | u01-rem-close | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T194127665376Z-epiphanius-tractatus-de-numerorum-mysteriis--u01-rem-close |
| epiphanius-tractatus-de-numerorum-mysteriis--u01-rem-mid | done | u01-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T194915120393Z-epiphanius-tractatus-de-numerorum-mysteriis--u01-rem-mid |
| epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u02-rem-early | done | u02-rem-early | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T195937548848Z-epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u02-rem-early |
| theophilus-alex-fragmenta-matthaeum--u01-rem-mid | done | u01-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T200257532213Z-theophilus-alex-fragmenta-matthaeum--u01-rem-mid |
| theophilus-alex-fragmenta-matthaeum--u01-rem-close | done | u01-rem-close | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T200850544522Z-theophilus-alex-fragmenta-matthaeum--u01-rem-close |
| theophilus-alex-fragmenta-joannem--u01-rem-early | done | u01-rem-early | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T201241124500Z-theophilus-alex-fragmenta-joannem--u01-rem-early |
| hesychius-homilia-i-hypapante--u01-rem-early | done | u01-rem-early | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T201636794902Z-hesychius-homilia-i-hypapante--u01-rem-early |
| hesychius-homilia-i-hypapante--u01-rem-close | done | u01-rem-close | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T204100216075Z-hesychius-homilia-i-hypapante--u01-rem-close |
| epiphanius-tractatus-contra-eos-qui-imagines-faciunt--u01-open | done | u01-open | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T205703573616Z-epiphanius-tractatus-contra-eos-qui-imagines-faciunt--u01-open |
| hesychius-homilia-i-longinum--u01-open | done | u01-open | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T210554098133Z-hesychius-homilia-i-longinum--u01-open |
| hesychius-homilia-i-longinum--u01-rem-early | done | u01-rem-early | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T211302350394Z-hesychius-homilia-i-longinum--u01-rem-early |
| hesychius-homilia-i-lazarum--u01-rem-early | done | u01-rem-early | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T211921406964Z-hesychius-homilia-i-lazarum--u01-rem-early |
| epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u03-rem-mid | done | u03-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current+clause; receipt 20260929T212301764278Z-epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u03-rem-mid |
| hesychius-homilia-i-longinum--u01-rem-mid | done | u01-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T213506771381Z-hesychius-homilia-i-longinum--u01-rem-mid |
| hesychius-homilia-i-lazarum--u01-open | done | u01-open | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current+clause; receipt 20260929T214849562501Z-hesychius-homilia-i-lazarum--u01-open |
| hesychius-homilia-i-maria-deipara--u01-open | done | u01-open | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T220224867298Z-hesychius-homilia-i-maria-deipara--u01-open |
| hesychius-homilia-i-maria-deipara--u01-rem-early | done | u01-rem-early | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T220729638151Z-hesychius-homilia-i-maria-deipara--u01-rem-early |
| hesychius-homilia-i-lazarum--u01-rem-mid | done | u01-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T221019675127Z-hesychius-homilia-i-lazarum--u01-rem-mid |
| hesychius-homilia-i-hypapante--u01-rem-mid | done | u01-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T221446012320Z-hesychius-homilia-i-hypapante--u01-rem-mid |
| hesychius-homilia-i-maria-deipara--u01-rem-close | done | u01-rem-close | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T223302672625Z-hesychius-homilia-i-maria-deipara--u01-rem-close |
| hesychius-homilia-i-longinum--u02-rem-mid | done | u02-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T223822166937Z-hesychius-homilia-i-longinum--u02-rem-mid |
| hesychius-homilia-i-longinum--u01-rem-close | done | u01-rem-close | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T224034532400Z-hesychius-homilia-i-longinum--u01-rem-close |
| epiphanius-tractatus-contra-eos-qui-imagines-faciunt--u01-rem-close | done | u01-rem-close | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T224941991464Z-epiphanius-tractatus-contra-eos-qui-imagines-faciunt--u01-rem-close |
| hesychius-homilia-i-maria-deipara--u01-rem-mid | done | u01-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T231223670791Z-hesychius-homilia-i-maria-deipara--u01-rem-mid |
| hesychius-homilia-ii-hypapante--u01-rem-early | done | u01-rem-early | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T231307189833Z-hesychius-homilia-ii-hypapante--u01-rem-early |
| hesychius-homilia-i-hypapante--u01-open | done | u01-open | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T231932359401Z-hesychius-homilia-i-hypapante--u01-open |
| hesychius-homilia-ii-hypapante--u01-rem-mid | done | u01-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T232856298131Z-hesychius-homilia-ii-hypapante--u01-rem-mid |
| hesychius-homilia-ii-hypapante--u01-rem-close | done | u01-rem-close | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current+clause; receipt 20260929T233055963151Z-hesychius-homilia-ii-hypapante--u01-rem-close |
| hesychius-homilia-ii-hypapante--u01-open | done | u01-open | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260929T233939564125Z-hesychius-homilia-ii-hypapante--u01-open |
| hesychius-homilia-i-longinum--u02-rem-early | done | u02-rem-early | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260929T234928652445Z-hesychius-homilia-i-longinum--u02-rem-early |
| hesychius-homilia-ii-lazarum--u01-rem-close | done | u01-rem-close | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T000429439587Z-hesychius-homilia-ii-lazarum--u01-rem-close |
| hesychius-homilia-ii-longinum--u01-rem-early | done | u01-rem-early | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T001119304854Z-hesychius-homilia-ii-longinum--u01-rem-early |
| hesychius-homilia-ii-longinum--u01-open | done | u01-open | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T001301200213Z-hesychius-homilia-ii-longinum--u01-open |
| hesychius-homilia-i-pascha--u01-open | done | u01-open | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T002217930285Z-hesychius-homilia-i-pascha--u01-open |
| hesychius-homilia-i-longinum--u02-rem-close | done | u02-rem-close | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T002535048651Z-hesychius-homilia-i-longinum--u02-rem-close |
| hesychius-homilia-ii-longinum--u02-rem-early | done | u02-rem-early | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T004618996522Z-hesychius-homilia-ii-longinum--u02-rem-early |
| hesychius-homilia-ii-lazarum--u01-open | done | u01-open | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current+clause; receipt 20260930T005407662333Z-hesychius-homilia-ii-lazarum--u01-open |
| hesychius-homilia-ii-maria-deipara--u01-rem-early | done | u01-rem-early | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T012244047899Z-hesychius-homilia-ii-maria-deipara--u01-rem-early |
| hesychius-homilia-ii-longinum--u01-rem-close | done | u01-rem-close | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current+clause; receipt 20260930T012423675030Z-hesychius-homilia-ii-longinum--u01-rem-close |
| hesychius-homilia-ii-lazarum--u01-rem-mid | done | u01-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T013433923044Z-hesychius-homilia-ii-lazarum--u01-rem-mid |
| hesychius-homilia-ii-lazarum--u01-rem-early | done | u01-rem-early | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T013559320914Z-hesychius-homilia-ii-lazarum--u01-rem-early |
| theophilus-alex-fragmenta-matthaeum--u01-open | done | u01-open | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T015457454906Z-theophilus-alex-fragmenta-matthaeum--u01-open |
| hesychius-homilia-ii-maria-deipara--u01-open | done | u01-open | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T021524802231Z-hesychius-homilia-ii-maria-deipara--u01-open |
| epiphanius-tractatus-contra-eos-qui-imagines-faciunt--u01-rem-mid | done | u01-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T023517909867Z-epiphanius-tractatus-contra-eos-qui-imagines-faciunt--u01-rem-mid |
| hesychius-homilia-ii-longinum--u02-rem-mid | done | u02-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T025811663740Z-hesychius-homilia-ii-longinum--u02-rem-mid |
| hesychius-in-andream--u01-open | done | u01-open | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T032725775035Z-hesychius-in-andream--u01-open |
| hesychius-homilia-ii-maria-deipara--u01-rem-mid | done | u01-rem-mid | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T034001569828Z-hesychius-homilia-ii-maria-deipara--u01-rem-mid |
| hesychius-homilia-ii-maria-deipara--u01-rem-close | done | u01-rem-close | 2026-09-29 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T034056499570Z-hesychius-homilia-ii-maria-deipara--u01-rem-close |
| epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u02-rem-mid | done | u02-rem-mid | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current+clause; receipt 20260930T040632147591Z-epiphanius-testimonia-ex-divinis-et-sacris-scripturis--u02-rem-mid |
| hesychius-homilia-jejunio--u01-rem-mid | done | u01-rem-mid | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T042342717872Z-hesychius-homilia-jejunio--u01-rem-mid |
| hesychius-homilia-jejunio--u01-open | done | u01-open | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T042924890354Z-hesychius-homilia-jejunio--u01-open |
| hesychius-homilia-ii-longinum--u01-rem-mid | done | u01-rem-mid | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T044052317778Z-hesychius-homilia-ii-longinum--u01-rem-mid |
| hesychius-in-andream--u01-rem-early | done | u01-rem-early | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T050824559051Z-hesychius-in-andream--u01-rem-early |
| hesychius-in-andream--u01-rem-close | done | u01-rem-close | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T051443171771Z-hesychius-in-andream--u01-rem-close |
| hesychius-homilia-jejunio--u01-rem-close | done | u01-rem-close | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T051557738044Z-hesychius-homilia-jejunio--u01-rem-close |
| hesychius-in-conceptionem-praecursoris--u01-rem-mid | done | u01-rem-mid | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T064909260365Z-hesychius-in-conceptionem-praecursoris--u01-rem-mid |
| hesychius-in-conceptionem-praecursoris--u02-open | done | u02-open | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T065618280360Z-hesychius-in-conceptionem-praecursoris--u02-open |
| hesychius-in-conceptionem-praecursoris--u02-rem-early | done | u02-rem-early | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T065618341238Z-hesychius-in-conceptionem-praecursoris--u02-rem-early |
| hesychius-in-antonium--u01-rem-mid | done | u01-rem-mid | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T065807700471Z-hesychius-in-antonium--u01-rem-mid |
| hesychius-in-andream--u01-rem-mid | done | u01-rem-mid | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T071354625943Z-hesychius-in-andream--u01-rem-mid |
| hesychius-in-conceptionem-praecursoris--u02-rem-close | done | u02-rem-close | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T075716927437Z-hesychius-in-conceptionem-praecursoris--u02-rem-close |
| hesychius-in-lazarum-ramos--u01-open | done | u01-open | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T075834620620Z-hesychius-in-lazarum-ramos--u01-open |
| hesychius-in-conceptionem-praecursoris--u01-rem-close | done | u01-rem-close | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T080013846656Z-hesychius-in-conceptionem-praecursoris--u01-rem-close |
| hesychius-in-antonium--u01-rem-close | done | u01-rem-close | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T080056969205Z-hesychius-in-antonium--u01-rem-close |
| hesychius-in-antonium--u01-open | done | u01-open | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T080831606031Z-hesychius-in-antonium--u01-open |
| hesychius-in-antonium--u01-rem-early | done | u01-rem-early | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current+clause; receipt 20260930T080949495591Z-hesychius-in-antonium--u01-rem-early |
| hesychius-homilia-ii-longinum--u02-rem-close | done | u02-rem-close | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T082259041578Z-hesychius-homilia-ii-longinum--u02-rem-close |
| hesychius-in-lazarum-ramos--u02-open | done | u02-open | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T084725661271Z-hesychius-in-lazarum-ramos--u02-open |
| hesychius-in-lazarum-ramos--u01-rem-early | done | u01-rem-early | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T090157151874Z-hesychius-in-lazarum-ramos--u01-rem-early |
| hesychius-in-conceptionem-praecursoris--u01-rem-early | done | u01-rem-early | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T090702056823Z-hesychius-in-conceptionem-praecursoris--u01-rem-early |
| hesychius-in-lazarum-ramos--u02-rem-mid | done | u02-rem-mid | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T090947106159Z-hesychius-in-lazarum-ramos--u02-rem-mid |
| hesychius-in-lucam--u01-open | done | u01-open | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current+clause; receipt 20260930T091846124711Z-hesychius-in-lucam--u01-open |
| hesychius-in-andream--u02-rem-mid | done | u02-rem-mid | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T093439966869Z-hesychius-in-andream--u02-rem-mid |
| theophilus-alex-fragmenta-joannem--u01-open | done | u01-open | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T095833858601Z-theophilus-alex-fragmenta-joannem--u01-open |
| hesychius-in-lucam--u01-rem-mid | done | u01-rem-mid | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T100244589350Z-hesychius-in-lucam--u01-rem-mid |
| hesychius-in-lucam--u01-rem-close | done | u01-rem-close | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T100522909703Z-hesychius-in-lucam--u01-rem-close |
| hesychius-in-petrum-paulum--u01-rem-early | done | u01-rem-early | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current+clause; receipt 20260930T101014555960Z-hesychius-in-petrum-paulum--u01-rem-early |
| epiphanius-tractatus-contra-eos-qui-imagines-faciunt--u01-rem-early | done | u01-rem-early | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T104525648254Z-epiphanius-tractatus-contra-eos-qui-imagines-faciunt--u01-rem-early |
| hesychius-in-petrum-paulum--u01-rem-mid | done | u01-rem-mid | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T105156685995Z-hesychius-in-petrum-paulum--u01-rem-mid |
| hesychius-in-petrum-paulum--u01-rem-close | done | u01-rem-close | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T105051345481Z-hesychius-in-petrum-paulum--u01-rem-close |
| hesychius-in-procopium--u01-rem-early | done | u01-rem-early | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T110329573037Z-hesychius-in-procopium--u01-rem-early |
| hesychius-in-lazarum-ramos--u01-rem-mid | done | u01-rem-mid | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T111942453063Z-hesychius-in-lazarum-ramos--u01-rem-mid |
| hesychius-in-procopium--u01-rem-mid | done | u01-rem-mid | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T120101647276Z-hesychius-in-procopium--u01-rem-mid |
| hesychius-in-lucam--u01-rem-early | done | u01-rem-early | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T134143473358Z-hesychius-in-lucam--u01-rem-early |
| hesychius-in-stephanum--u01-rem-mid | done | u01-rem-mid | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T142445444586Z-hesychius-in-stephanum--u01-rem-mid |
| hesychius-in-stephanum--u01-rem-close | done | u01-rem-close | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T142755292666Z-hesychius-in-stephanum--u01-rem-close |
| hesychius-in-sanctos-martyres--u01-rem-early | done | u01-rem-early | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T144003643081Z-hesychius-in-sanctos-martyres--u01-rem-early |
| hesychius-in-conceptionem-praecursoris--u02-rem-mid | done | u02-rem-mid | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T145729718546Z-hesychius-in-conceptionem-praecursoris--u02-rem-mid |
| hesychius-in-procopium--u01-rem-close | done | u01-rem-close | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T153053540669Z-hesychius-in-procopium--u01-rem-close |
| hesychius-in-procopium--u01-open | done | u01-open | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current+clause; receipt 20260930T153726482020Z-hesychius-in-procopium--u01-open |
| hesychius-in-petrum-paulum--u01-open | done | u01-open | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T153755111153Z-hesychius-in-petrum-paulum--u01-open |
| hesychius-homilia-ii-pascha--u01-rem-early | done | u01-rem-early | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T163525323975Z-hesychius-homilia-ii-pascha--u01-rem-early |
| hesychius-homilia-ii-longinum--u02-open | done | u02-open | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T164040410603Z-hesychius-homilia-ii-longinum--u02-open |
| hesychius-in-lazarum-ramos--u01-rem-close | done | u01-rem-close | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T170805858001Z-hesychius-in-lazarum-ramos--u01-rem-close |
| cyril-alexandria-contra-julianum--book1-rem-early | done | book1-rem-early | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current+clause; receipt 20260930T183541470355Z-cyril-alexandria-contra-julianum--book1-rem-early |
| cyril-alexandria-contra-julianum--book1-rem-close | done | book1-rem-close | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T194529316073Z-cyril-alexandria-contra-julianum--book1-rem-close |
| cyril-alexandria-ad-episcopos-libyae--ep-rem-close | done | ep-rem-close | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current; receipt 20260930T202316203647Z-cyril-alexandria-ad-episcopos-libyae--ep-rem-close |
| cyril-alexandria-ad-calosyrium--ep-open | done | ep-open | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T203058882877Z-cyril-alexandria-ad-calosyrium--ep-open |
| cyril-alexandria-ad-optimum--ep-rem-close | done | ep-rem-close | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T215319215572Z-cyril-alexandria-ad-optimum--ep-rem-close |
| cyril-alexandria-contra-julianum--book2-rem-early | done | book2-rem-early | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T235344322429Z-cyril-alexandria-contra-julianum--book2-rem-early |
| cyril-alexandria-contra-julianum--book5-rem-early | done | book5-rem-early | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20260930T235803811447Z-cyril-alexandria-contra-julianum--book5-rem-early |
| cyril-alexandria-contra-julianum--book2-rem-mid | done | book2-rem-mid | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261001T000341302905Z-cyril-alexandria-contra-julianum--book2-rem-mid |
| cyril-alexandria-dialogus-nestorio--dial-open | done | dial-open | 2026-09-30 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261001T023432939775Z-cyril-alexandria-dialogus-nestorio--dial-open |
| hesychius-homilia-i-lazarum--u01-rem-close | done | u01-rem-close | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261001T032925482665Z-hesychius-homilia-i-lazarum--u01-rem-close |
| cyril-alexandria-contra-julianum--book7-rem-mid | done | book7-rem-mid | 2026-09-30 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261001T033755020186Z-cyril-alexandria-contra-julianum--book7-rem-mid |
| cyril-alexandria-epistula-photium--ep-open | done | ep-open | 2026-10-01 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261001T060522666226Z-cyril-alexandria-epistula-photium--ep-open |
| cyril-alexandria-epistula-domnum--ep-rem-early | done | ep-rem-early | 2026-10-01 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261001T061229459312Z-cyril-alexandria-epistula-domnum--ep-rem-early |
| cyril-alexandria-contra-julianum--book6-rem-early | done | book6-rem-early | 2026-10-01 | AI cross-check (overnight-mini-nv); accept-current+clause; receipt 20261001T063802864201Z-cyril-alexandria-contra-julianum--book6-rem-early |
| cyril-alexandria-contra-julianum--book3-rem-early | done | book3-rem-early | 2026-10-01 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261001T064716527831Z-cyril-alexandria-contra-julianum--book3-rem-early |
| cyril-alexandria-epistula-domnum--ep-rem-mid | done | ep-rem-mid | 2026-10-01 | AI cross-check (overnight-mini-nv); accept-current+clause; receipt 20261001T080224458033Z-cyril-alexandria-epistula-domnum--ep-rem-mid |
| cyril-alexandria-festal-letters--logos02-rem-mid | done | logos02-rem-mid | 2026-10-01 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261001T080344289670Z-cyril-alexandria-festal-letters--logos02-rem-mid |
| cyril-alexandria-dialogus-nestorio--dial-rem-close | done | dial-rem-close | 2026-10-01 | AI cross-check (overnight-mini-cf); accept-current+clause; receipt 20261001T081229587720Z-cyril-alexandria-dialogus-nestorio--dial-rem-close |
| cyril-alexandria-festal-letters--logos12-rem-mid | done | logos12-rem-mid | 2026-10-01 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261001T131942084009Z-cyril-alexandria-festal-letters--logos12-rem-mid |
| cyril-alexandria-festal-letters--logos09-rem-close | done | logos09-rem-close | 2026-10-01 | AI cross-check (overnight-mini-cf); accept-current+clause; receipt 20261001T141600302121Z-cyril-alexandria-festal-letters--logos09-rem-close |
| cyril-alexandria-festal-letters--logos13-rem-close | done | logos13-rem-close | 2026-10-01 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261001T160918947861Z-cyril-alexandria-festal-letters--logos13-rem-close |
| cyril-alexandria-festal-letters--logos13-rem-mid | done | logos13-rem-mid | 2026-10-01 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261001T161435414402Z-cyril-alexandria-festal-letters--logos13-rem-mid |
| cyril-alexandria-festal-letters--logos11-rem-early | done | logos11-rem-early | 2026-10-01 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261001T164514773894Z-cyril-alexandria-festal-letters--logos11-rem-early |
| cyril-alexandria-festal-letters--logos09-rem-mid | done | logos09-rem-mid | 2026-10-01 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261001T165816126797Z-cyril-alexandria-festal-letters--logos09-rem-mid |
| cyril-alexandria-festal-letters--logos08-rem-mid | done | logos08-rem-mid | 2026-10-01 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261001T170340218595Z-cyril-alexandria-festal-letters--logos08-rem-mid |
| cyril-alexandria-festal-letters--logos07-rem-mid | done | logos07-rem-mid | 2026-10-01 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261001T173635844599Z-cyril-alexandria-festal-letters--logos07-rem-mid |
| cyril-alexandria-festal-letters--logos05-rem-early | done | logos05-rem-early | 2026-10-01 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261001T174325076384Z-cyril-alexandria-festal-letters--logos05-rem-early |
| cyril-alexandria-festal-letters--logos14-rem-close | done | logos14-rem-close | 2026-10-01 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261001T185859158916Z-cyril-alexandria-festal-letters--logos14-rem-close |
| hesychius-in-lazarum-ramos--u02-rem-close | done | u02-rem-close | 2026-10-01 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261001T233331395954Z-hesychius-in-lazarum-ramos--u02-rem-close |
| hesychius-homilia-i-longinum--u02-open | done | u02-open | 2026-10-01 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T005218594010Z-hesychius-homilia-i-longinum--u02-open |
| cyril-alexandria-fragmenta-contra-diodorum--frag-rem-early | done | frag-rem-early | 2026-10-01 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T010350489316Z-cyril-alexandria-fragmenta-contra-diodorum--frag-rem-early |
| cyril-alexandria-fragmenta-canticum--u02-rem-mid | done | u02-rem-mid | 2026-10-01 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T010824409773Z-cyril-alexandria-fragmenta-canticum--u02-rem-mid |
| hesychius-in-andream--u02-open | done | u02-open | 2026-10-01 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T033245199038Z-hesychius-in-andream--u02-open |
| cyril-alexandria-fragmenta-hebraeos--u01-open | done | u01-open | 2026-10-01 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T034634001122Z-cyril-alexandria-fragmenta-hebraeos--u01-open |
| cyril-alexandria-fragmenta-canticum--u01-rem-mid | done | u01-rem-mid | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T040247770348Z-cyril-alexandria-fragmenta-canticum--u01-rem-mid |
| cyril-alexandria-fragmenta-canticum--u02-rem-early | done | u02-rem-early | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T040636175077Z-cyril-alexandria-fragmenta-canticum--u02-rem-early |
| cyril-alexandria-fragmenta-canticum--u02-open | done | u02-open | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T040931638902Z-cyril-alexandria-fragmenta-canticum--u02-open |
| cyril-alexandria-fragmenta-canticum--u01-rem-early | done | u01-rem-early | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current+clause; receipt 20261002T042030573897Z-cyril-alexandria-fragmenta-canticum--u01-rem-early |
| cyril-alexandria-fragmenta-acta-catholicas--u04-open | done | u04-open | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T042847534407Z-cyril-alexandria-fragmenta-acta-catholicas--u04-open |
| cyril-alexandria-fragmenta-acta-catholicas--u02-rem-mid | done | u02-rem-mid | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T043021388154Z-cyril-alexandria-fragmenta-acta-catholicas--u02-rem-mid |
| cyril-alexandria-fragmenta-acta-catholicas--u02-rem-close | done | u02-rem-close | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current+clause; receipt 20261002T043638823836Z-cyril-alexandria-fragmenta-acta-catholicas--u02-rem-close |
| cyril-alexandria-fragmenta-acta-catholicas--u03-rem-early | done | u03-rem-early | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T044155172728Z-cyril-alexandria-fragmenta-acta-catholicas--u03-rem-early |
| cyril-alexandria-fragmenta-hebraeos--u01-rem-mid | done | u01-rem-mid | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T052122972773Z-cyril-alexandria-fragmenta-hebraeos--u01-rem-mid |
| cyril-alexandria-fragmenta-hebraeos--u01-rem-close | done | u01-rem-close | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T052407909515Z-cyril-alexandria-fragmenta-hebraeos--u01-rem-close |
| cyril-alexandria-fragmenta-ezechielem--frag-rem-close | done | frag-rem-close | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T052448353718Z-cyril-alexandria-fragmenta-ezechielem--frag-rem-close |
| cyril-alexandria-fragmenta-hebraeos--u01-rem-early | done | u01-rem-early | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T052539918555Z-cyril-alexandria-fragmenta-hebraeos--u01-rem-early |
| cyril-alexandria-fragmenta-acta-catholicas--u03-open | done | u03-open | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T043710356111Z-cyril-alexandria-fragmenta-acta-catholicas--u03-open |
| cyril-alexandria-fragmenta-acta-catholicas--u03-rem-mid | done | u03-rem-mid | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current+clause; receipt 20261002T053642233645Z-cyril-alexandria-fragmenta-acta-catholicas--u03-rem-mid |
| cyril-alexandria-fragmenta-acta-catholicas--u02-rem-early | done | u02-rem-early | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T055053173942Z-cyril-alexandria-fragmenta-acta-catholicas--u02-rem-early |
| cyril-alexandria-fragmenta-2-corinthios--u05-rem-close | done | u05-rem-close | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T055145545116Z-cyril-alexandria-fragmenta-2-corinthios--u05-rem-close |
| cyril-alexandria-fragmenta-acta-catholicas--u01-rem-early | done | u01-rem-early | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T055419620435Z-cyril-alexandria-fragmenta-acta-catholicas--u01-rem-early |
| cyril-alexandria-fragmenta-2-corinthios--u03-open | done | u03-open | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T060455418559Z-cyril-alexandria-fragmenta-2-corinthios--u03-open |
| cyril-alexandria-fragmenta-2-corinthios--u04-rem-close | done | u04-rem-close | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T060720100645Z-cyril-alexandria-fragmenta-2-corinthios--u04-rem-close |
| cyril-alexandria-fragmenta-2-corinthios--u03-rem-mid | done | u03-rem-mid | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T061156969091Z-cyril-alexandria-fragmenta-2-corinthios--u03-rem-mid |
| cyril-alexandria-fragmenta-2-corinthios--u03-rem-close | done | u03-rem-close | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T061538955653Z-cyril-alexandria-fragmenta-2-corinthios--u03-rem-close |
| cyril-alexandria-fragmenta-2-corinthios--u04-rem-early | done | u04-rem-early | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T062242300980Z-cyril-alexandria-fragmenta-2-corinthios--u04-rem-early |
| hesychius-in-sanctos-martyres--u01-rem-mid | done | u01-rem-mid | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T073356669253Z-hesychius-in-sanctos-martyres--u01-rem-mid |
| epiphanius-testamentum-ad-cives--u01-rem-early | done | u01-rem-early | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T074345342485Z-epiphanius-testamentum-ad-cives--u01-rem-early |
| didymus-commentarii-job--u10-rem-mid | done | u10-rem-mid | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current+clause; receipt 20261002T075954413359Z-didymus-commentarii-job--u10-rem-mid |
| cyril-alexandria-fragmenta-hebraeos--u08-rem-early | done | u08-rem-early | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T101503592027Z-cyril-alexandria-fragmenta-hebraeos--u08-rem-early |
| cyril-alexandria-fragmenta-numeros--frag-rem-early | done | frag-rem-early | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T105208915783Z-cyril-alexandria-fragmenta-numeros--frag-rem-early |
| cyril-alexandria-fragmenta-jeremiam--frag-rem-close | done | frag-rem-close | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T112825400089Z-cyril-alexandria-fragmenta-jeremiam--frag-rem-close |
| cyril-alexandria-fragmenta-hebraeos--u08-rem-mid | done | u08-rem-mid | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T122133905844Z-cyril-alexandria-fragmenta-hebraeos--u08-rem-mid |
| cyril-alexandria-fragmenta-hebraeos--u08-rem-close | done | u08-rem-close | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T122431879434Z-cyril-alexandria-fragmenta-hebraeos--u08-rem-close |
| cyril-alexandria-fragmenta-hebraeos--u07-rem-early | done | u07-rem-early | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T122723912418Z-cyril-alexandria-fragmenta-hebraeos--u07-rem-early |
| cyril-alexandria-fragmenta-hebraeos--u07-open | done | u07-open | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T122721947703Z-cyril-alexandria-fragmenta-hebraeos--u07-open |
| cyril-alexandria-fragmenta-hebraeos--u06-rem-early | done | u06-rem-early | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T123554539587Z-cyril-alexandria-fragmenta-hebraeos--u06-rem-early |
| cyril-alexandria-fragmenta-hebraeos--u06-open | done | u06-open | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T123532050842Z-cyril-alexandria-fragmenta-hebraeos--u06-open |
| cyril-alexandria-fragmenta-regum--b03-open | done | b03-open | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T131016059206Z-cyril-alexandria-fragmenta-regum--b03-open |
| cyril-alexandria-fragmenta-regum--b03-rem-mid | done | b03-rem-mid | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T131408327253Z-cyril-alexandria-fragmenta-regum--b03-rem-mid |
| cyril-alexandria-fragmenta-regum--b03-rem-close | done | b03-rem-close | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T131751694322Z-cyril-alexandria-fragmenta-regum--b03-rem-close |
| cyril-alexandria-fragmenta-hebraeos--u05-open | done | u05-open | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T132500059144Z-cyril-alexandria-fragmenta-hebraeos--u05-open |
| cyril-alexandria-fragmenta-hebraeos--u05-rem-mid | done | u05-rem-mid | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T132911332493Z-cyril-alexandria-fragmenta-hebraeos--u05-rem-mid |
| cyril-alexandria-fragmenta-hebraeos--u04-open | done | u04-open | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T133221078578Z-cyril-alexandria-fragmenta-hebraeos--u04-open |
| cyril-alexandria-fragmenta-hebraeos--u05-rem-close | done | u05-rem-close | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T133524484624Z-cyril-alexandria-fragmenta-hebraeos--u05-rem-close |
| cyril-alexandria-fragmenta-hebraeos--u03-open | done | u03-open | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T135252220740Z-cyril-alexandria-fragmenta-hebraeos--u03-open |
| cyril-alexandria-fragmenta-hebraeos--u04-rem-close | done | u04-rem-close | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T135252735144Z-cyril-alexandria-fragmenta-hebraeos--u04-rem-close |
| cyril-alexandria-fragmenta-hebraeos--u03-rem-early | done | u03-rem-early | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T135404022738Z-cyril-alexandria-fragmenta-hebraeos--u03-rem-early |
| cyril-alexandria-fragmenta-hebraeos--u03-rem-mid | done | u03-rem-mid | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T135653316402Z-cyril-alexandria-fragmenta-hebraeos--u03-rem-mid |
| cyril-alexandria-fragmenta-hebraeos--u03-rem-close | done | u03-rem-close | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T135818883878Z-cyril-alexandria-fragmenta-hebraeos--u03-rem-close |
| cyril-alexandria-fragmenta-hebraeos--u02-rem-early | done | u02-rem-early | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T140002034740Z-cyril-alexandria-fragmenta-hebraeos--u02-rem-early |
| cyril-alexandria-fragmenta-hebraeos--u02-open | done | u02-open | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T140235558568Z-cyril-alexandria-fragmenta-hebraeos--u02-open |
| cyril-alexandria-fragmenta-hebraeos--u02-rem-close | done | u02-rem-close | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T140455794325Z-cyril-alexandria-fragmenta-hebraeos--u02-rem-close |
| cyril-alexandria-fragmenta-acta-catholicas--u02-open | done | u02-open | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T141102255306Z-cyril-alexandria-fragmenta-acta-catholicas--u02-open |
| cyril-alexandria-fragmenta-acta-catholicas--u01-open | done | u01-open | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T141422129543Z-cyril-alexandria-fragmenta-acta-catholicas--u01-open |
| cyril-alexandria-fragmenta-1-corinthios--u07-rem-mid | done | u07-rem-mid | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T143438505953Z-cyril-alexandria-fragmenta-1-corinthios--u07-rem-mid |
| cyril-alexandria-fragmenta-1-corinthios--u07-rem-close | done | u07-rem-close | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T144034560965Z-cyril-alexandria-fragmenta-1-corinthios--u07-rem-close |
| cyril-alexandria-fragmenta-1-corinthios--u06-rem-mid | done | u06-rem-mid | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T144325093304Z-cyril-alexandria-fragmenta-1-corinthios--u06-rem-mid |
| cyril-alexandria-fragmenta-1-corinthios--u06-open | done | u06-open | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T150614115605Z-cyril-alexandria-fragmenta-1-corinthios--u06-open |
| cyril-alexandria-fragmenta-1-corinthios--u04-rem-close | done | u04-rem-close | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T152002825626Z-cyril-alexandria-fragmenta-1-corinthios--u04-rem-close |
| cyril-alexandria-fragmenta-1-corinthios--u03-rem-mid | done | u03-rem-mid | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T154712866879Z-cyril-alexandria-fragmenta-1-corinthios--u03-rem-mid |
| hesychius-in-stephanum--u02-rem-early | done | u02-rem-early | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current+clause; receipt 20261002T161226766451Z-hesychius-in-stephanum--u02-rem-early |
| cyril-alexandria-fragmenta-romanos--u01-rem-mid | done | u01-rem-mid | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T163529105736Z-cyril-alexandria-fragmenta-romanos--u01-rem-mid |
| cyril-alexandria-fragmenta-romanos--u01-rem-close | done | u01-rem-close | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T163849970336Z-cyril-alexandria-fragmenta-romanos--u01-rem-close |
| cyril-alexandria-fragmenta-romanos--u02-rem-early | done | u02-rem-early | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T170015602709Z-cyril-alexandria-fragmenta-romanos--u02-rem-early |
| hesychius-homilia-ii-pascha--u01-open | done | u01-open | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T180035152647Z-hesychius-homilia-ii-pascha--u01-open |
| cyril-alexandria-glaphyra--book1-cain-abel-rem-early | done | book1-cain-abel-rem-early | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T203424072807Z-cyril-alexandria-glaphyra--book1-cain-abel-rem-early |
| cyril-alexandria-glaphyra--gen-b5-rem-early | done | gen-b5-rem-early | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T221508999330Z-cyril-alexandria-glaphyra--gen-b5-rem-early |
| cyril-alexandria-glaphyra--gen-b4-rem-close | done | gen-b4-rem-close | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T221626427382Z-cyril-alexandria-glaphyra--gen-b4-rem-close |
| cyril-alexandria-glaphyra--gen-b3-rem-mid | done | gen-b3-rem-mid | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T222919850719Z-cyril-alexandria-glaphyra--gen-b3-rem-mid |
| cyril-alexandria-glaphyra--exod-b2-rem-mid | done | exod-b2-rem-mid | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T223334713318Z-cyril-alexandria-glaphyra--exod-b2-rem-mid |
| cyril-alexandria-glaphyra--exod-b2-rem-close | done | exod-b2-rem-close | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T223356769902Z-cyril-alexandria-glaphyra--exod-b2-rem-close |
| cyril-alexandria-glaphyra--exod-b3-rem-mid | done | exod-b3-rem-mid | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T223611110869Z-cyril-alexandria-glaphyra--exod-b3-rem-mid |
| cyril-alexandria-glaphyra--exod-b1-rem-mid | done | exod-b1-rem-mid | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T224332231821Z-cyril-alexandria-glaphyra--exod-b1-rem-mid |
| cyril-alexandria-glaphyra--exod-b1-rem-close | done | exod-b1-rem-close | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T224511295312Z-cyril-alexandria-glaphyra--exod-b1-rem-close |
| cyril-alexandria-glaphyra--gen-b5-rem-close | done | gen-b5-rem-close | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T231856495802Z-cyril-alexandria-glaphyra--gen-b5-rem-close |
| cyril-alexandria-glaphyra--gen-b6-rem-early | done | gen-b6-rem-early | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current+clause; receipt 20261002T232320425425Z-cyril-alexandria-glaphyra--gen-b6-rem-early |
| cyril-alexandria-glaphyra--gen-b4-rem-early | done | gen-b4-rem-early | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T232716074542Z-cyril-alexandria-glaphyra--gen-b4-rem-early |
| cyril-alexandria-glaphyra--exod-b3-rem-close | done | exod-b3-rem-close | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T233001346203Z-cyril-alexandria-glaphyra--exod-b3-rem-close |
| cyril-alexandria-glaphyra--gen-b3-rem-close | done | gen-b3-rem-close | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T233047200484Z-cyril-alexandria-glaphyra--gen-b3-rem-close |
| cyril-alexandria-glaphyra--exod-b2-rem-early | done | exod-b2-rem-early | 2026-10-02 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261002T233817581522Z-cyril-alexandria-glaphyra--exod-b2-rem-early |
| cyril-alexandria-glaphyra--book1-cain-abel-rem-mid | done | book1-cain-abel-rem-mid | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261002T234920827358Z-cyril-alexandria-glaphyra--book1-cain-abel-rem-mid |
| cyril-alexandria-fragmenta-romanos--u10-rem-early | done | u10-rem-early | 2026-10-02 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261003T002139305889Z-cyril-alexandria-fragmenta-romanos--u10-rem-early |
| hesychius-in-sanctos-martyres--u01-rem-close | done | u01-rem-close | 2026-10-03 | AI cross-check (overnight-mini-nv); accept-current; receipt 20261003T064840948399Z-hesychius-in-sanctos-martyres--u01-rem-close |
| hesychius-homilia-ii-pascha--u01-rem-mid | done | u01-rem-mid | 2026-10-03 | AI cross-check (overnight-mini-cf); accept-current; receipt 20261003T073023274534Z-hesychius-homilia-ii-pascha--u01-rem-mid |
