# Church Fathers Translation Project

New English from locked public-domain Greek and Latin for private study and for the free public library at [fathers.saneapps.com](https://fathers.saneapps.com).

This is **100% Transparent Code** under [PolyForm Shield](LICENSE). It is **not** a claim that every treatise is complete, and it is **not** permission to copy modern copyrighted English (FOTC, ACW, etc.) or to paste ANF/NPNF as the reading text.

## Contribute (humans + LLMs)

1. Read **[`docs/START_HERE.md`](docs/START_HERE.md)** — paste that file into your AI first.
2. List free slices: `python3 scripts/claims.py free`
3. Take one: `python3 scripts/claims.py take <claim-id> --agent YourName`
4. Branch `wip/<claim-id>`, two-pass translation, justifications, then `python3 scripts/ai_promote.py --claim <id> --agent YourName` → `done` (AI cross-check; see `docs/AI_CROSSCHECK.md`).
5. Do **not** deploy the website or run Logos/`build_book.py` unless the owner asked.

Site: https://fathers.saneapps.com/contribute/

## Layout

```
docs/           START_HERE, CLAIMS, SOP, schemas, LLM candidate notes
books/<slug>/   sources (PDFs usually gitignored), translations JSON, reviews
pipeline/       DOCX + verify tools (Logos Personal Books on the owner’s Mac)
scripts/        claims.py, llm_bakeoff.py, …
```

Heavy edition PDFs are gitignored. Locked Greek/Latin lives in `books/*/translations/*_source.json` (and local PDFs via each book’s `sources/manifest.json`).

## Legal stance

Private study by default. New English from allowed public-domain / permitted source text. Public mirror: fathers.saneapps.com. No paywall on the library; support via [GitHub Sponsors](https://github.com/sponsors/MrSaneApps).

## Owner notes

Canonical checkout: `~/SaneApps/clients/translations` on Air and Mini. Logos compile: Air only. Site build/deploy: Mini-first → Cloudflare Pages `fathers-site`.
