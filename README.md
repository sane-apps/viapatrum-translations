# Church Fathers Translation Project

New English from locked public-domain Greek and Latin for private study and for the free public library at [fathers.saneapps.com](https://fathers.saneapps.com).

**License:** [MIT](LICENSE).

## How to use

- Browse the public library: [fathers.saneapps.com](https://fathers.saneapps.com)
- Clone this repo to inspect sources, translation JSON, claims, and tooling
- Point an AI at a claim slice via [docs/START_HERE.md](docs/START_HERE.md)
- Spot-check Greek/Latin and open a correction: [new issue](https://github.com/sane-apps/translations/issues/new?template=correction.yml)

This repo does **not** claim every treatise is complete. It is **not** permission to copy modern copyrighted English (FOTC, ACW, etc.) or to paste ANF/NPNF as the reading text. Those are usage notes about source text, not license restrictions.

## Help

This library is free. Pick one. None of these is required to read. Same list: https://fathers.saneapps.com/contribute/

1. [Donate](https://github.com/sponsors/MrSaneApps)
2. [Buy a Mac app](https://saneapps.com) — one-time purchase, no subscription
3. [Point an AI at a slice](docs/START_HERE.md) — copy that file into your AI
4. [Spot-check the Greek or Latin](https://github.com/sane-apps/translations/issues/new?template=correction.yml)

## Layout

```
docs/           START_HERE, CLAIMS, SOP, schemas
books/<slug>/   sources (PDFs usually gitignored), translations JSON, reviews
pipeline/       DOCX + verify tools
scripts/        claims.py, …
```

Heavy edition PDFs are gitignored. Locked Greek/Latin lives in `books/*/translations/*_source.json` (and local PDFs via each book’s `sources/manifest.json`).

## Legal stance (usage notes)

Private study by default. New English from allowed public-domain / permitted source text. Public mirror: fathers.saneapps.com. No paywall on the library; support via [GitHub Sponsors](https://github.com/sponsors/MrSaneApps).

## Fathers site UX gate

When shipping books to fathers.saneapps.com, agents must read `websites/fathers.saneapps.com/AGENTS.md` → Standing UX rules and acknowledge them before UI/tip work.
