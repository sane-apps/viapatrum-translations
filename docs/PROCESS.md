# How the translations are made

This is the process behind [viapatrum.org](https://viapatrum.org). You may read it, reuse it or copy it under the [MIT license](../LICENSE). The reader-facing version is at [viapatrum.org/methodology](https://viapatrum.org/methodology/).

## The idea

Older tools checked one section at a time, so a work could pass every check and still render a key term five ways or lose track of who was speaking. This process treats the whole work as the unit, and no model checks its own draft.

## The stages

All of this lives in [`scripts/work_pipeline.py`](../scripts/work_pipeline.py).

| Stage | What happens |
|---|---|
| Brief | One model reads the whole Greek or Latin and writes a guide: occasion, argument, outline, who speaks, a fixed glossary and a map of ancient names. A second model checks each claim against the source. Unsupported claims are removed or redone. |
| Draft | Each section is drafted twice, with the brief and the neighbouring text in view: first a close gloss (Pass A), then readable English (Pass B). Automatic gates reject near-copies, glossary breaks and other known faults. |
| Check | Two models from different makers each read only the source and Pass B, without seeing Pass A. They report omissions, additions, reversed negation, wrong agency, wrong speaker and wrong Scripture references, with exact quotes. A finding counts when both report it, or when one reports it and the other upholds it on review. Quotes that are not in the text are dropped. |
| Repair | Confirmed findings are fixed and the section is checked again. After the set number of rounds, a section that still fails is held back, not published. |
| Read | Two models read the whole work in English, as first-time readers, looking for drifting terms, garbled sentences and wrong references. |
| Intro | A three-paragraph introduction is written from the checked brief, then checked sentence by sentence. |
| Apply | The work is copied into its book folder with a receipt bound to a SHA-256 hash of every source and English section, so any later change needs a new check. |

Nothing changes in the book folder until `apply`. Work in progress stays under `outputs/work-pipeline/<slug>/`.

## Run it

The repository is over 10 GB. Use the partial clone in [START_HERE.md](START_HERE.md) and add only the book you want.

```bash
pip install -r requirements.txt
python3 scripts/work_pipeline.py run --slug <book-slug>
python3 scripts/work_pipeline.py status --slug <book-slug>
python3 scripts/work_pipeline.py apply --slug <book-slug>
```

The script reads `CLOUDFLARE_API_TOKEN` and `NV_API_KEY` from the environment. Choose your own models with `WP_DRAFTER`, `WP_CHECKERS`, `WP_JUDGES`, `WP_FALLBACK` and `WP_REFEREE`. The checker and judge defaults today are Kimi K2.6 and GLM-5.2. Keep the drafter and the checkers from different makers.

**This is working code, not a packaged tool.** It was built for one setup. Before a run it checks for a model research receipt (`receipts_ok` in the script) and a spending limit ([`scripts/spend_guard.py`](../scripts/spend_guard.py)). Expect to adapt both.

## Where to look

| Path | What it is |
|---|---|
| `scripts/work_pipeline.py` | The pipeline above |
| `scripts/work_read.py` | The whole-work reader |
| `pipeline/work_lint.py` | Automatic checks on the English |
| `pipeline/check_pass_ab.py` | Checks on each section's two drafts |
| `docs/SCHEMAS.md` | File formats for translation JSON |
| `docs/AI_CROSSCHECK.md` | Rules for the checkers, including the older section-level path |
| `books/<slug>/` | Locked sources, English, receipts and reviews for one work |

`docs/SOP.md` covers building Logos Personal Books. It is not the translation process.

## Limits

These are AI checks, not a scholar's line-by-line review, and not every work has been through every stage yet. Two dated audits show what the checks missed when they were run and why the process changed: [the October 2 red team](REDTEAM_2026-10-02.md) and [the October 5 quality audit](QUALITY_AUDIT_20261005.md).

Found an error? [Send a correction](https://github.com/sane-apps/viapatrum-translations/issues/new?template=correction.yml).
