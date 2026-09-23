# Contributing

Same four ways as https://fathers.saneapps.com/contribute/

1. [Donate](https://github.com/sponsors/MrSaneApps)
2. [Buy a Mac app](https://saneapps.com) — one-time purchase, no subscription
3. [Point an AI at a slice](docs/START_HERE.md) — copy that file into your AI
4. [Spot-check the Greek or Latin](https://github.com/sane-apps/translations/issues/new?template=correction.yml)

## Research SOP (intros, bios, dates)

No author bio, work intro, or date ships without a receipt. This is
plain-English nonfiction presented as fact; every checkable claim
must trace to a source a stranger could open.

Per book (`books/<slug>/`):

- `intro.md`: exactly 3 paragraphs — author / context / contents.
- `research.json`: `{"slug", "checked": "YYYY-MM-DD", "claims": [...]}`
  with one entry per checkable claim: `{"claim", "kind", "sources"}`.
  - `kind=fact` (author/work history): at least one `http(s)` source.
    Two independent sources when they disagree or the fact is obscure.
  - `kind=scope` (what this volume holds): `repo:` paths are fine.
  - `kind=repo` (rosters, counts): `repo:` paths are fine.
- Dates in the intro must also appear in the claims, the book's
  `book.yml`, or the site's `author-dates.json` — and the intro's
  author-date line must agree with `author-dates.json` for that author.

Enforcement (automatic, not advisory):

- `python3 scripts/check_research.py` fails the site ship
  (`websites/fathers.saneapps.com scripts/ship.sh`) and the Logos
  driver preflight (`scripts/logos_build.py`) on any violation:
  missing/unsourced files, unsourced dates, or intro/dates drift.
- When sources conflict (it happens — Le Blanc's birth year was wrong
  in our own data until ESTC corrected it), record the stronger source
  and fix every consumer, not just the file in front of you.
