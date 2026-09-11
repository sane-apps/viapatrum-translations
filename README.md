# Church Fathers Translation Project

New English from locked public-domain Greek and Latin for private study and for the free public library at [fathers.saneapps.com](https://fathers.saneapps.com).

This is **100% Transparent Code** under [PolyForm Shield](LICENSE). It is **not** a claim that every treatise is complete, and it is **not** permission to copy modern copyrighted English (FOTC, ACW, etc.) or to paste ANF/NPNF as the reading text.

## Help

This library is free. If you want to help it keep growing, pick one. None of these is required to read. Same list on the site: https://fathers.saneapps.com/contribute/

### 1. Donate

[GitHub Sponsors](https://github.com/sponsors/MrSaneApps)

### 2. Buy a Mac app

If you use a Mac, the SaneApps utilities are a one-time purchase with no subscription. They run on your machine. Buying one also supports this library.

[SaneApps](https://saneapps.com)

### 3. Point an AI at a slice

Clone this repo. Point your AI at [`docs/START_HERE.md`](docs/START_HERE.md), then paste:

```bash
python3 scripts/claims.py start --agent YourName
```

Use your name, not YourName. One slice at a time. Do not copy modern English.

### 4. Spot-check the Greek or Latin

If you read the original language and a line of English looks wrong, [submit a correction](https://github.com/sane-apps/translations/issues/new?template=correction.yml). Name the work, the section, and what you think it should say.

## Layout

```
docs/           START_HERE, CLAIMS, SOP, schemas
books/<slug>/   sources (PDFs usually gitignored), translations JSON, reviews
pipeline/       DOCX + verify tools (Logos Personal Books on the owner’s Mac)
scripts/        claims.py, …
```

Heavy edition PDFs are gitignored. Locked Greek/Latin lives in `books/*/translations/*_source.json` (and local PDFs via each book’s `sources/manifest.json`).

## Legal stance

Private study by default. New English from allowed public-domain / permitted source text. Public mirror: fathers.saneapps.com. No paywall on the library; support via [GitHub Sponsors](https://github.com/sponsors/MrSaneApps).

## Owner notes

Canonical checkout: `~/SaneApps/clients/translations` on Air and Mini. Logos compile: Air only. Site build/deploy: Mini-first → Cloudflare Pages `fathers-site`.
