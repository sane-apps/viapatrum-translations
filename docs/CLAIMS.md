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
| crocius-syntagma-densify | claimed | crocius-syntagma | Full work densify (Syntagma 4 books; 1636 Latin) | OpenCode | 2026-09-16 | wip/crocius-syntagma-densify | Reformed lane; SLUB Villerian 1636 PD Latin; new English from Latin |
| davenant-dissertationes-densify | free | davenant-dissertationes-duae | Full work densify (Dissertationes duae; 1650 Latin) |  |  |  | Reformed lane; Daniel 1650 PD Latin; new English from Latin |
| baron-philosophia-densify | free | baron-philosophia-theologiae-ancillans | Full work densify (Philosophia theologiae ancillans; 1658 Latin) |  |  |  | Reformed lane; Oxford 1658 PD Latin; new English from Latin |
| placeus-de-imputatione-densify | free | placeus-de-imputatione | Full work densify (De imputatione; 1661 Latin) |  |  |  | Reformed lane; Lesnerius 1661 PD Latin; new English from Latin |
| le-blanc-theses-densify | free | le-blanc-theses-theologicae | Full work densify (Theses theologicae; 1675 Latin) |  |  |  | Reformed lane; Pitt 1675 PD Latin; new English from Latin |
| strimesius-in-controversias-densify | free | strimesius-in-controversias-evangelicorum | Full work densify (In controversias evangelicorum; 1708 Latin) |  |  |  | Reformed lane; Francofurti ad Viadrum 1708 PD Latin; new English from Latin |

## How to claim

```bash
python3 scripts/claims.py start --agent YourName
```

Then do only that slice. Finish with `python3 scripts/ai_promote.py --claim <id> --agent YourName`.

## Done / closed

Archived: older done rows now live in `docs/CLAIMS_ARCHIVE.md` (1871 rows, full commit history preserved). Do not read the archive for routine work.
Keep this file lean: when a claim closes, move its row to the archive instead of letting this section grow.

## Do not claim these (owner / blocked)

- Website deploy / Cloudflare Pages / edits under `websites/fathers.saneapps.com`
- Logos Personal Book compile; `build_book.py` unless owner asked
- Inventing a new book slug without `docs/WORKS_QUEUE.md` + charter
- Any modern or ANF English as the reading text
- Changing Slice columns or merging/splitting claim rows (ask owner)
