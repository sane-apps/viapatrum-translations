# Content SOPs — one row per type we ship

Every content type below names its source of truth, its required parts, the
gates that run without a human, the checks a human still does, and the ship
path. Prose describes; scripts enforce. When a miss ships, add the gate that
would have caught it — this file grows by incident.

## 1. Library web works (fathers.saneapps.com text + read-along audio)

- Source of truth: `books/<slug>/` (`book.yml`, `translations/*_english.json`,
  `intro.md`, `research.json`).
- Required parts: complete English, witness/check text, intro.md (3 paras),
  research.json, author dates entry.
- Automated gates: `check_research.py` (intros sourced, dates agree);
  `build_site.py` (refuses structural gaps); `inject_audio.py` (exact-match
  audio attach, unmatched reported, never forced); `ship.sh` (catalogue,
  research, UI, link, and live gates).
- Human checks: spot-read changed works; confirm no new `held` works ship
  unintentionally; read the ship log tail.
- Ship path: Mini only, `./scripts/ship.sh` (full) or `--skip-build` (dist
  already final). Never hand-edit `dist/`.

## 2. Logos Personal Books (text)

- Source of truth: same book dir plus `<slug>.docx`, `assets/cover.jpg|png`.
- Required parts: DOCX built by `build_pbb_docx.py` (never by hand);
  `docx:` key in `book.yml`; research gate green; cover art; intro in book
  (`logos_intro: true`); no audio-framed sections (`logos_drop_titles`).
- Automated gates: `check_research.py` (runs inside the driver);
  `verify_docx` before Build; driver warns on missing cover/intro;
  `verify_logos_db` after Build (ArticleCache sane, no pollution).
- Human checks: description accuracy audit (witness-label sweep across the
  book's source files; headnote claims traced to primary sources —
  period imprints, author's own Journal/Works, not Wikipedia);
  spot-check TOC, Bible click, TN hover after Build.
- Ship path: Mini only, `logos_build.py --book <slug>` (Sunday agent sweeps
  all). Rebuild + re-upload is cheap; never leave a known-bad upload up.
- Lessons: 2026-10-01 Wesley shipped coverless with audio-framed sections
  and a self-contradictory description; added cover/intro warnings,
  `logos_blurb`/`logos_drop_titles`/`logos_intro` keys, and this audit step.

## 3. Audiobooks (downloadable/paid editions)

- Source of truth: `outputs/audio/<work>/` (manifest + per-passage mp3s).
- Voice: see `docs/SOP.md` "Audiobook voice rule" (owner 2026-10-09): ONE
  narrator voice per work across all its chapters and parts; different works
  may use different voices; never one site-wide voice; pick per work by best
  quality, then speed, then cost; the voice is recorded in the work's manifest.
- Required parts: ONE voice across all chapters of that work; ONE container format;
  ACX-grade mastering (44.1 kHz, CBR 192k+, RMS -23..-18 dB, peaks at/below
  -3 dB, noise floor below -60 dB, head/tail room tone, one file per
  chapter under 120 min); opening + closing credit files; square cover
  (3000px); AI-narration disclosure everywhere the distributor asks.
- Automated gates: `check_audiobook.py <work>` (voice-signature and format
  uniformity; must pass before mastering); post-master measurement pass
  (every file re-measured, report kept).
- Human checks: listen to chapter starts/ends (no clipped words, tone
  present); confirm credits wording and rights-holder line; confirm the
  distributor's AI policy in writing before upload.
- Ship path: master to `outputs/audiobook/<title>/`; distributor upload is a
  deliberate human step, never chained.
- Lessons: 2026-10-01 Wesley mixed ElevenLabs (1-24) with Kokoro (25-44);
  voice uniformity is now gated, and paid-service audio is archived
  (`elliott-archive/`) instead of overwritten.

## 4. Hub articles (saneapps.com long-form)

- Source of truth: edition markdown + builder script, BOTH committed under
  the site repo (`outputs/`), never only in /tmp.
- Required parts: shell cloned from a live site page; complete body;
  scan/source links per section; guides link; sitemap entry.
- Automated gates: rebuild script asserts tag balance, note/link counts, and
  no leftover markdown; sitemap must stay valid XML.
- Human checks: read the page top to bottom once; click every distinct link
  type; verify live URL + guides card after deploy.
- Ship path: staged rsync (no `.git/.wrangler/outputs`) +
  `wrangler pages deploy --project-name saneapps-site`; verify live.
- Lessons: 2026-10-01 reboot wiped /tmp mid-ship; Tmp-durability rule now in
  `~/AGENTS.md` (durable paths as work is made).

## 5. Social/marketing

- Existing lanes: `x-post.py`, prose guard, launch-readiness gate. No change;
  this row exists so the matrix stays complete.

## Title caps policy (audit 2026-10-01, T rank-7)
- Wesley works: Title Case ("A Caution Against Bigotry", "Discourse I–XIII" roman numerals).
- Patristic works: minimal caps ("Medicine Chest against Heresies", "On the Soul against the Arians"); lowercase short words (is/in/of/against); parentheticals capitalized ("(Fragments)", "(Epitome)").
- Numerals: roman for homilies/discourses/books (Homily I/II, Book IV); arabic only where the edition uses it.
- Fragment labels: bare title when the work survives substantially ("To Florus"); "(Fragments)" when genuinely fragmentary; "Extracts in …" for excerpted witnesses.
